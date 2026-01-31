"""Utility functions for the Balatro RL environment."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from balatro_env.schemas import CardData, GamePhase, GameState, JokerData, LegalActions


console = Console()


def format_card(card: CardData) -> str:
    """Format a card for display.

    Args:
        card: Card data

    Returns:
        Formatted card string
    """
    suit_symbols = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
    suit = suit_symbols.get(card.suit, card.suit or "?")
    rank = card.rank or "?"

    parts = [f"{rank}{suit}"]

    if card.edition:
        parts.append(f"[{card.edition}]")
    if card.enhancement:
        parts.append(f"({card.enhancement})")
    if card.seal:
        parts.append(f"<{card.seal}>")
    if card.debuffed:
        parts.append("DEBUFFED")
    if card.highlighted:
        parts.append("*")

    return " ".join(parts)


def format_joker(joker: JokerData) -> str:
    """Format a joker for display.

    Args:
        joker: Joker data

    Returns:
        Formatted joker string
    """
    name = joker.name or joker.key or "Unknown"
    parts = [name]

    if joker.edition:
        parts.append(f"[edition]")
    if joker.sell_cost:
        parts.append(f"(sell: ${joker.sell_cost})")

    return " ".join(parts)


def print_state_summary(state: GameState):
    """Print a nicely formatted state summary.

    Args:
        state: Game state to display
    """
    # Phase and run info
    console.print(Panel.fit(
        f"[bold]Phase:[/bold] {state.phase.value}\n"
        f"[bold]Run ID:[/bold] {state.run_id or 'N/A'}\n"
        f"[bold]Ante:[/bold] {state.ante}  [bold]Round:[/bold] {state.round}",
        title="Game State"
    ))

    # Resources table
    resources = Table(title="Resources", show_header=False)
    resources.add_column("Stat", style="cyan")
    resources.add_column("Value", style="green")
    resources.add_row("Money", f"${state.money}")
    resources.add_row("Hands Left", str(state.hands_remaining))
    resources.add_row("Discards Left", str(state.discards_remaining))
    resources.add_row("Deck Size", str(state.deck_counts.deck_size))
    resources.add_row("Discard Pile", str(state.deck_counts.discard_size))
    console.print(resources)

    # Blind info
    if state.blind:
        blind_table = Table(title="Current Blind", show_header=False)
        blind_table.add_column("Stat", style="cyan")
        blind_table.add_column("Value", style="yellow")
        blind_table.add_row("Name", state.blind.name or "Unknown")
        blind_table.add_row("Chips Needed", f"{state.blind.chips_needed:,}" if state.blind.chips_needed else "N/A")
        blind_table.add_row("Chips Scored", f"{state.blind.chips_scored:,}")
        if state.blind.boss:
            blind_table.add_row("Boss Effect", state.blind.debuff_text or "Yes")
        console.print(blind_table)

    # Hand
    if state.hand:
        hand_table = Table(title=f"Hand ({len(state.hand)} cards)")
        hand_table.add_column("Idx", style="dim")
        hand_table.add_column("Card", style="bold")
        hand_table.add_column("Extras", style="cyan")
        for card in state.hand:
            extras = []
            if card.edition:
                extras.append(card.edition)
            if card.enhancement:
                extras.append(card.enhancement)
            if card.seal:
                extras.append(card.seal)
            hand_table.add_row(
                str(card.hand_index or "?"),
                format_card(card),
                ", ".join(extras) if extras else "-"
            )
        console.print(hand_table)

    # Jokers
    if state.jokers:
        joker_table = Table(title=f"Jokers ({len(state.jokers)})")
        joker_table.add_column("Idx", style="dim")
        joker_table.add_column("Joker", style="bold magenta")
        joker_table.add_column("Sell Value", style="green")
        for joker in state.jokers:
            joker_table.add_row(
                str(joker.joker_index or "?"),
                joker.name or joker.key or "Unknown",
                f"${joker.sell_cost}"
            )
        console.print(joker_table)

    # Shop
    if state.shop and state.shop.items:
        shop_table = Table(title=f"Shop (Reroll: ${state.shop.reroll_cost})")
        shop_table.add_column("Slot", style="dim")
        shop_table.add_column("Item", style="bold")
        shop_table.add_column("Cost", style="green")
        shop_table.add_column("Type", style="cyan")
        for item in state.shop.items:
            affordable = "✓" if item.cost <= state.money else "✗"
            shop_table.add_row(
                str(item.slot),
                item.name or "Unknown",
                f"${item.cost} {affordable}",
                item.type
            )
        console.print(shop_table)

    # Pack
    if state.pack and state.pack.cards:
        pack_table = Table(title="Pack Cards")
        pack_table.add_column("Idx", style="dim")
        pack_table.add_column("Card", style="bold yellow")
        for i, card in enumerate(state.pack.cards):
            pack_table.add_row(str(i + 1), card.get("name", "Unknown"))
        console.print(pack_table)


def print_legal_actions(legal: LegalActions):
    """Print a nicely formatted legal actions summary.

    Args:
        legal: Legal actions to display
    """
    console.print(Panel.fit(
        f"[bold]Phase:[/bold] {legal.phase.value}\n"
        f"[bold]Actions Available:[/bold] {len(legal.actions)}",
        title="Legal Actions"
    ))

    # Group actions by type
    by_type: dict[str, list] = {}
    for action in legal.actions:
        action_type = action.type.value
        if action_type not in by_type:
            by_type[action_type] = []
        by_type[action_type].append(action)

    for action_type, actions in by_type.items():
        action_table = Table(title=action_type)
        action_table.add_column("Description", style="cyan")
        action_table.add_column("Params", style="yellow")

        for action in actions[:5]:  # Limit display
            params_str = ""
            if action.params:
                params_dict = action.params.model_dump(exclude_none=True)
                if params_dict:
                    params_str = json.dumps(params_dict, default=str)[:50]

            action_table.add_row(action.description, params_str)

        if len(actions) > 5:
            action_table.add_row(f"... and {len(actions) - 5} more", "")

        console.print(action_table)


def save_state_artifact(state: GameState, output_dir: Path | str = "artifacts") -> Path:
    """Save game state to a JSON artifact file.

    Args:
        state: Game state to save
        output_dir: Directory to save artifacts

    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"state_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(state.model_dump(), f, indent=2, default=str)

    return filepath


def save_legal_artifact(legal: LegalActions, output_dir: Path | str = "artifacts") -> Path:
    """Save legal actions to a JSON artifact file.

    Args:
        legal: Legal actions to save
        output_dir: Directory to save artifacts

    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"legal_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(legal.model_dump(), f, indent=2, default=str)

    return filepath
