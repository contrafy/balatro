#!/usr/bin/env python3
"""Execute smoke test actions in Balatro.

Usage:
    python -m balatro_env.scripts.do_smoke_actions [--host HOST] [--port PORT]

Performs safe actions based on current game phase to verify action execution:
- SHOP: reroll (if affordable), then end shop
- SELECTING_HAND: play simplest legal hand or discard one card
- PACK_OPENING: select first item or skip
"""

import argparse
import sys
import time

from rich.console import Console
from rich.panel import Panel

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import ActionRequest, ActionType, GamePhase

console = Console()


def execute_and_report(client: BalatroClient, action: ActionRequest, description: str) -> bool:
    """Execute an action and report the result."""
    console.print(f"\n[bold]Executing:[/bold] {description}")
    console.print(f"  Action: {action.type.value}")
    console.print(f"  Params: {action.params}")

    try:
        result = client.execute_action(action)

        if result.ok:
            console.print("[green]  Result: SUCCESS[/green]")
            if result.state:
                console.print(f"  New phase: {result.state.phase.value}")
                console.print(f"  Money: ${result.state.money}")
            return True
        else:
            console.print(f"[red]  Result: FAILED - {result.error}[/red]")
            return False

    except BalatroConnectionError as e:
        console.print(f"[red]  Connection error: {e}[/red]")
        return False


def smoke_shop(client: BalatroClient, state, legal) -> int:
    """Perform smoke actions in shop phase."""
    actions_taken = 0

    # Try to reroll if affordable
    for action in legal.actions:
        if action.type == ActionType.SHOP_REROLL:
            cost = action.params.cost if action.params else 5
            if state.money >= cost:
                if execute_and_report(client, ActionRequest(type=ActionType.SHOP_REROLL), "Reroll shop"):
                    actions_taken += 1
                    time.sleep(0.5)  # Brief delay
                break

    # End shop
    for action in legal.actions:
        if action.type == ActionType.SHOP_END:
            if execute_and_report(client, ActionRequest(type=ActionType.SHOP_END), "Leave shop"):
                actions_taken += 1
            break

    return actions_taken


def smoke_hand_play(client: BalatroClient, state, legal) -> int:
    """Perform smoke actions in hand selection phase."""
    actions_taken = 0

    # Try to play a hand first
    for action in legal.actions:
        if action.type == ActionType.PLAY_HAND and action.params:
            params = action.params
            if params.card_indices:
                available = params.card_indices.get("available", [])
                if available:
                    # Play just one card (simplest)
                    card_to_play = [available[0]]
                    req = ActionRequest(
                        type=ActionType.PLAY_HAND,
                        params={"card_indices": card_to_play}
                    )
                    if execute_and_report(client, req, f"Play single card (index {card_to_play[0]})"):
                        actions_taken += 1
                    return actions_taken

    # If no play available, try discard
    for action in legal.actions:
        if action.type == ActionType.DISCARD and action.params:
            params = action.params
            if params.card_indices:
                available = params.card_indices.get("available", [])
                if available:
                    card_to_discard = [available[0]]
                    req = ActionRequest(
                        type=ActionType.DISCARD,
                        params={"card_indices": card_to_discard}
                    )
                    if execute_and_report(client, req, f"Discard card (index {card_to_discard[0]})"):
                        actions_taken += 1
                    return actions_taken

    console.print("[yellow]No play or discard actions available[/yellow]")
    return actions_taken


def smoke_pack(client: BalatroClient, state, legal) -> int:
    """Perform smoke actions in pack opening phase."""
    actions_taken = 0

    # Try to select first pack item
    for action in legal.actions:
        if action.type == ActionType.SELECT_PACK_ITEM and action.params:
            choice_idx = action.params.choice_index
            req = ActionRequest(
                type=ActionType.SELECT_PACK_ITEM,
                params={"choice_index": choice_idx}
            )
            if execute_and_report(client, req, f"Select pack item {choice_idx}"):
                actions_taken += 1
            return actions_taken

    # Skip pack if can't select
    for action in legal.actions:
        if action.type == ActionType.SKIP_PACK:
            if execute_and_report(client, ActionRequest(type=ActionType.SKIP_PACK), "Skip pack"):
                actions_taken += 1
            return actions_taken

    return actions_taken


def main():
    parser = argparse.ArgumentParser(description="Execute smoke test actions in Balatro")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host address")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port number")
    parser.add_argument("--max-actions", type=int, default=5, help="Maximum actions to take")
    args = parser.parse_args()

    try:
        client = BalatroClient(host=args.host, port=args.port)

        total_actions = 0

        for iteration in range(args.max_actions):
            console.print(Panel.fit(f"Iteration {iteration + 1}", border_style="blue"))

            # Get current state
            state = client.get_state()
            legal = client.get_legal_actions()

            console.print(f"[bold]Phase:[/bold] {state.phase.value}")
            console.print(f"[bold]Available actions:[/bold] {len(legal.actions)}")

            if state.error:
                console.print(f"[red]State error:[/red] {state.error}")
                break

            if legal.error:
                console.print(f"[red]Legal actions error:[/red] {legal.error}")
                break

            if not legal.actions:
                console.print("[yellow]No actions available - game may be in transition[/yellow]")
                time.sleep(1)
                continue

            # Execute phase-appropriate actions
            actions_taken = 0

            if state.phase == GamePhase.SHOP:
                actions_taken = smoke_shop(client, state, legal)
            elif state.phase == GamePhase.SELECTING_HAND:
                actions_taken = smoke_hand_play(client, state, legal)
            elif state.phase == GamePhase.PACK_OPENING:
                actions_taken = smoke_pack(client, state, legal)
            elif state.phase == GamePhase.BLIND_SELECT:
                # Just observe for now
                console.print("[cyan]In blind select - observing only[/cyan]")
            else:
                console.print(f"[yellow]Unknown phase {state.phase.value} - observing only[/yellow]")

            total_actions += actions_taken

            if actions_taken == 0:
                console.print("[yellow]No actions taken this iteration[/yellow]")
                time.sleep(0.5)

        console.print(Panel.fit(
            f"[bold]Total actions executed:[/bold] {total_actions}",
            title="[green]Smoke Test Complete[/green]",
            border_style="green"
        ))

        client.close()
        sys.exit(0)

    except BalatroConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
