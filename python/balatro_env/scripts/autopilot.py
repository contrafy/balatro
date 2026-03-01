#!/usr/bin/env python3
"""Balatro Autopilot — deterministic strategy bot with live Rich dashboard.

Usage:
    python -m balatro_env.scripts.autopilot [--host HOST] [--port PORT] [--delay SECS]

Plays Balatro automatically using rule-based strategy. Shows a live dashboard
with current game state, decisions, and run statistics.
"""

import argparse
import sys
import time
from collections import deque
from dataclasses import dataclass, field

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import ActionRequest, GamePhase, GameState, LegalActions
from balatro_env.strategy import Decision, card_label, decide

console = Console()

# ---------------------------------------------------------------------------
# Run statistics
# ---------------------------------------------------------------------------

@dataclass
class RunStats:
    """Statistics for a single run."""
    run_id: str = ""
    rounds_survived: int = 0
    max_ante: int = 0
    max_money: int = 0
    hands_played: int = 0
    blinds_beaten: int = 0
    jokers_bought: int = 0
    won: bool = False

    def summary_line(self) -> str:
        result = "WON" if self.won else f"Lost"
        return (
            f"Run {self.run_id}: {result} | "
            f"Ante {self.max_ante} Round {self.rounds_survived} | "
            f"${self.max_money} peak | "
            f"{self.hands_played} hands"
        )


@dataclass
class SessionStats:
    """Statistics across all runs in this session."""
    runs_completed: int = 0
    total_rounds: int = 0
    total_hands: int = 0
    best_ante: int = 0
    wins: int = 0
    run_history: list[RunStats] = field(default_factory=list)
    current_run: RunStats = field(default_factory=RunStats)

    def finish_run(self, won: bool = False):
        self.current_run.won = won
        self.run_history.append(self.current_run)
        self.runs_completed += 1
        self.total_rounds += self.current_run.rounds_survived
        self.total_hands += self.current_run.hands_played
        if self.current_run.max_ante > self.best_ante:
            self.best_ante = self.current_run.max_ante
        if won:
            self.wins += 1
        self.current_run = RunStats()

    def new_run(self, run_id: str):
        self.current_run = RunStats(run_id=run_id)


# ---------------------------------------------------------------------------
# Dashboard rendering
# ---------------------------------------------------------------------------

LOG_MAX = 30


def build_dashboard(
    state: GameState | None,
    legal: LegalActions | None,
    last_decision: Decision | None,
    session: SessionStats,
    log_lines: deque[str],
    status_msg: str = "",
) -> Layout:
    """Build the Rich Layout for the live dashboard."""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=5),
    )

    # Header
    phase_str = state.phase.value if state else "Connecting..."
    run_id = state.run_id or "N/A" if state else "N/A"
    header_text = Text.from_markup(
        f"  [bold cyan]BALATRO AUTOPILOT[/]  |  "
        f"Phase: [bold yellow]{phase_str}[/]  |  "
        f"Run: {run_id}  |  "
        f"Runs: {session.runs_completed} ({session.wins}W)  |  "
        f"Best Ante: {session.best_ante}"
    )
    layout["header"].update(Panel(header_text, style="blue"))

    # Body: split into left (game state) and right (log)
    layout["body"].split_row(
        Layout(name="state_panel", ratio=2),
        Layout(name="log_panel", ratio=1),
    )

    # State panel
    state_content = build_state_panel(state, legal, last_decision, session)
    layout["state_panel"].update(state_content)

    # Log panel
    log_text = "\n".join(log_lines) if log_lines else "[dim]No actions yet[/dim]"
    layout["log_panel"].update(
        Panel(Text.from_markup(log_text), title="Action Log", border_style="dim")
    )

    # Footer — current decision
    if status_msg:
        footer_text = Text.from_markup(status_msg)
    elif last_decision:
        footer_text = Text.from_markup(
            f"[bold green]>>> {last_decision.reason}[/]\n"
            f"    {last_decision.cards_label}"
        )
    else:
        footer_text = Text.from_markup("[dim]Waiting...[/dim]")
    layout["footer"].update(Panel(footer_text, title="Decision", border_style="green"))

    return layout


def build_state_panel(
    state: GameState | None,
    legal: LegalActions | None,
    last_decision: Decision | None,
    session: SessionStats,
) -> Panel:
    """Build the game state display panel."""
    if not state:
        return Panel("[dim]No state yet[/dim]", title="Game State")

    parts: list[str] = []

    # Resources
    chips_scored = state.blind.chips_scored if state.blind else 0
    chips_needed = state.blind.chips_needed or 0 if state.blind else 0
    blind_name = state.blind.name if state.blind else "?"
    boss = " [red]BOSS[/]" if state.blind and state.blind.boss else ""

    parts.append(
        f"[bold]Ante {state.ante} | Round {state.round}[/] | "
        f"Blind: {blind_name}{boss}"
    )
    parts.append(
        f"Score: [bold]{chips_scored:,}[/] / {chips_needed:,} | "
        f"Money: [green]${state.money}[/] | "
        f"Hands: {state.hands_remaining} | "
        f"Discards: {state.discards_remaining}"
    )
    parts.append(
        f"Deck: {state.deck_counts.deck_size} | "
        f"Discard pile: {state.deck_counts.discard_size}"
    )
    parts.append("")

    # Hand
    if state.hand:
        hand_str = "  ".join(
            f"[{'bold yellow' if c.highlighted else 'white'}]{card_label(c)}[/]"
            for c in state.hand
        )
        parts.append(f"[cyan]Hand ({len(state.hand)}):[/] {hand_str}")

    # Jokers
    if state.jokers:
        joker_strs = []
        for j in state.jokers:
            name = j.name or j.key or "?"
            joker_strs.append(f"{name}")
        parts.append(f"[magenta]Jokers ({len(state.jokers)}):[/] {', '.join(joker_strs)}")

    # Consumables
    if state.consumables:
        cons_strs = []
        for c in state.consumables:
            name = c.name or c.key or "?"
            usable = "*" if c.can_use else ""
            cons_strs.append(f"{name}{usable}")
        parts.append(f"[magenta]Consumables:[/] {', '.join(cons_strs)}")

    # Shop
    if state.shop:
        shop = state.shop
        parts.append("")
        if shop.jokers:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.jokers]
            parts.append(f"[yellow]Shop Jokers:[/] {' | '.join(items)}")
        if shop.vouchers:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.vouchers]
            parts.append(f"[yellow]Vouchers:[/] {' | '.join(items)}")
        if shop.boosters:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.boosters]
            parts.append(f"[yellow]Boosters:[/] {' | '.join(items)}")
        parts.append(f"Reroll: ${shop.reroll_cost}")

    # Pack
    if state.pack and state.pack.cards:
        pack_items = []
        for c in state.pack.cards:
            name = c.get("name", "?")
            if c.get("suit") and c.get("rank"):
                name = f"{c['rank']}{c['suit'][0]}"
            pack_items.append(name)
        parts.append(
            f"[yellow]Pack ({state.pack.choices_remaining} choices):[/] "
            f"{' | '.join(pack_items)}"
        )

    # Legal action summary
    if legal and legal.actions:
        action_types = {}
        for a in legal.actions:
            t = a.type.value
            action_types[t] = action_types.get(t, 0) + 1
        summary = ", ".join(f"{t}({n})" for t, n in action_types.items())
        parts.append(f"\n[dim]Legal: {summary}[/]")

    content = "\n".join(parts)
    return Panel(Text.from_markup(content), title="Game State", border_style="cyan")


# ---------------------------------------------------------------------------
# Main autopilot loop
# ---------------------------------------------------------------------------

TRANSITION_PHASES = {
    "HAND_PLAYED", "DRAW_TO_HAND", "NEW_ROUND",
    "PLAY_TAROT", "SPLASH",
    # STATE_N fallbacks when mod hasn't been reloaded
    "STATE_2", "STATE_3", "STATE_6", "STATE_13", "STATE_19",
}


def run_autopilot(client: BalatroClient, delay: float = 0.8):
    """Main autopilot loop with Rich Live dashboard."""
    session = SessionStats()
    log_lines: deque[str] = deque(maxlen=LOG_MAX)
    last_decision: Decision | None = None
    state: GameState | None = None
    legal: LegalActions | None = None
    status_msg = "[yellow]Starting...[/]"

    prev_phase = ""
    wait_count = 0
    MAX_WAIT = 30  # max iterations to wait for transition

    def log(msg: str):
        log_lines.append(msg)

    try:
        with Live(
            build_dashboard(state, legal, last_decision, session, log_lines, status_msg),
            console=console,
            refresh_per_second=4,
            screen=True,
        ) as live:
            while True:
                try:
                    # Fetch state
                    state = client.get_state()
                    phase = state.phase_raw or state.phase.value

                    # Track run stats
                    if state.run_id and state.run_id != session.current_run.run_id:
                        if session.current_run.run_id:
                            session.finish_run()
                            log(f"[red]Run ended: {session.run_history[-1].summary_line()}[/]")
                        session.new_run(str(state.run_id))

                    run = session.current_run
                    run.rounds_survived = max(run.rounds_survived, state.round)
                    run.max_ante = max(run.max_ante, state.ante)
                    run.max_money = max(run.max_money, state.money)

                    # Handle transition phases — just wait
                    if phase in TRANSITION_PHASES or phase.startswith("STATE_"):
                        wait_count += 1
                        status_msg = f"[dim]Waiting for {phase}... ({wait_count})[/]"
                        live.update(build_dashboard(
                            state, legal, last_decision, session, log_lines, status_msg
                        ))
                        if wait_count > MAX_WAIT:
                            log(f"[yellow]Stuck in {phase} for {MAX_WAIT} ticks[/]")
                            wait_count = 0
                        time.sleep(0.3)
                        continue

                    wait_count = 0

                    # Log phase transitions
                    if phase != prev_phase:
                        log(f"[cyan]Phase: {phase}[/]")
                        prev_phase = phase

                    # Get legal actions
                    legal = client.get_legal_actions()

                    # Make decision
                    decision = decide(state, legal)

                    if decision is None:
                        status_msg = f"[dim]No action for phase {phase}[/]"
                        live.update(build_dashboard(
                            state, legal, last_decision, session, log_lines, status_msg
                        ))
                        time.sleep(0.5)
                        continue

                    last_decision = decision
                    status_msg = f"[green]>>> {decision.reason}[/]"
                    live.update(build_dashboard(
                        state, legal, last_decision, session, log_lines, status_msg
                    ))

                    # Brief pause so user can see the decision
                    time.sleep(delay)

                    # Execute the action
                    action_type = decision.action.type.value
                    result = client.execute_action(decision.action)

                    if result.ok:
                        short = decision.reason[:60]
                        log(f"[green]OK[/] {action_type}: {short}")
                        run.hands_played += 1 if action_type == "PLAY_HAND" else 0
                        # After starting a run, wait for the game to transition out of MENU
                        # before polling again — prevents duplicate START_RUN calls.
                        if action_type == "START_RUN":
                            time.sleep(2.0)

                        # Update state from result if available
                        if result.state:
                            state = result.state
                        if result.legal:
                            legal = result.legal
                    else:
                        log(f"[red]FAIL[/] {action_type}: {result.error}")

                    # Handle game over
                    if phase == "GAME_OVER":
                        log(f"[red]GAME OVER[/] Ante {run.max_ante} Round {run.rounds_survived}")
                        session.finish_run(won=False)
                        time.sleep(2)  # Pause to show stats

                    live.update(build_dashboard(
                        state, legal, last_decision, session, log_lines, status_msg
                    ))

                    time.sleep(delay * 0.5)

                except BalatroConnectionError as e:
                    status_msg = f"[red]Connection error: {e}[/]"
                    live.update(build_dashboard(
                        state, legal, last_decision, session, log_lines, status_msg
                    ))
                    log(f"[red]Connection lost, retrying...[/]")
                    time.sleep(2)

    except KeyboardInterrupt:
        pass

    # Final stats
    if session.current_run.run_id:
        session.finish_run()

    console.print()
    console.print(Panel.fit(
        f"[bold]Session Summary[/]\n"
        f"Runs: {session.runs_completed} ({session.wins} wins)\n"
        f"Best Ante: {session.best_ante}\n"
        f"Total Rounds: {session.total_rounds}\n"
        f"Total Hands: {session.total_hands}",
        title="[bold blue]Autopilot Finished[/]",
        border_style="blue",
    ))

    if session.run_history:
        history_table = Table(title="Run History")
        history_table.add_column("#", style="dim")
        history_table.add_column("Run ID")
        history_table.add_column("Result", style="bold")
        history_table.add_column("Ante")
        history_table.add_column("Round")
        history_table.add_column("Hands")
        history_table.add_column("Peak $")
        for i, run in enumerate(session.run_history, 1):
            result_style = "green" if run.won else "red"
            history_table.add_row(
                str(i),
                run.run_id[:8],
                f"[{result_style}]{'WIN' if run.won else 'LOSS'}[/]",
                str(run.max_ante),
                str(run.rounds_survived),
                str(run.hands_played),
                f"${run.max_money}",
            )
        console.print(history_table)


def main():
    parser = argparse.ArgumentParser(description="Balatro Autopilot")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port")
    parser.add_argument("--delay", type=float, default=0.8,
                        help="Delay between decisions in seconds (default: 0.8)")
    args = parser.parse_args()

    console.print(Panel.fit(
        f"Connecting to Balatro at {args.host}:{args.port}...\n"
        f"Decision delay: {args.delay}s\n"
        "Press Ctrl+C to stop",
        title="[bold blue]Balatro Autopilot[/]",
        border_style="blue",
    ))

    try:
        client = BalatroClient(host=args.host, port=args.port)
        health = client.health()
        console.print(f"[green]Connected![/] Bridge v{health.version}, uptime {health.uptime_ms/1000:.0f}s")
        time.sleep(1)
    except BalatroConnectionError as e:
        console.print(f"[red]Failed to connect:[/] {e}")
        sys.exit(1)

    run_autopilot(client, delay=args.delay)
    client.close()


if __name__ == "__main__":
    main()
