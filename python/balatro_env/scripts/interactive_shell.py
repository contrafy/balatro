#!/usr/bin/env python3
"""Interactive shell for controlling Balatro.

Usage:
    python -m balatro_env.scripts.interactive_shell [--host HOST] [--port PORT]

Provides a REPL to:
- View current state and legal actions
- Execute actions by typing JSON
- Test the RL environment interface
"""

import argparse
import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import ActionRequest, ActionType
from balatro_env.util import print_legal_actions, print_state_summary

console = Console()

HELP_TEXT = """
[bold]Available Commands:[/bold]

  [cyan]state[/cyan], [cyan]s[/cyan]      - Show current game state
  [cyan]legal[/cyan], [cyan]l[/cyan]      - Show legal actions
  [cyan]health[/cyan], [cyan]h[/cyan]     - Check bridge health
  [cyan]action[/cyan] <json> - Execute an action (JSON format)
  [cyan]play[/cyan] <indices> - Play cards (e.g., 'play 1 2 3')
  [cyan]discard[/cyan] <indices> - Discard cards (e.g., 'discard 1 2')
  [cyan]reroll[/cyan]       - Reroll shop
  [cyan]endshop[/cyan]      - Leave shop
  [cyan]sort[/cyan] <mode>  - Sort hand (rank/suit)
  [cyan]buy[/cyan] <slot>   - Buy from shop slot
  [cyan]sell[/cyan] <index> - Sell joker
  [cyan]help[/cyan], [cyan]?[/cyan]       - Show this help
  [cyan]quit[/cyan], [cyan]q[/cyan]       - Exit

[bold]Action JSON Format:[/bold]
  {"type": "PLAY_HAND", "params": {"card_indices": [1, 2, 3]}}
  {"type": "SHOP_REROLL"}
  {"type": "SHOP_BUY", "params": {"slot": 1}}
"""


def parse_indices(args: list[str]) -> list[int]:
    """Parse card indices from command arguments."""
    indices = []
    for arg in args:
        try:
            indices.append(int(arg))
        except ValueError:
            pass
    return indices


def execute_action(client: BalatroClient, action: ActionRequest):
    """Execute an action and display the result."""
    console.print(f"\n[bold]Executing:[/bold] {action.type.value}")
    if action.params:
        console.print(f"[bold]Params:[/bold] {action.params}")

    try:
        result = client.execute_action(action)

        if result.ok:
            console.print("[green]SUCCESS[/green]")
            if result.state:
                console.print(f"  Phase: {result.state.phase.value}")
                console.print(f"  Money: ${result.state.money}")
                console.print(f"  Hands: {result.state.hands_remaining}")
        else:
            console.print(f"[red]FAILED:[/red] {result.error}")

    except BalatroConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")


def main():
    parser = argparse.ArgumentParser(description="Interactive Balatro shell")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host address")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port number")
    args = parser.parse_args()

    console.print(Panel.fit(
        f"Connecting to Balatro at {args.host}:{args.port}\n"
        "Type 'help' for available commands",
        title="[bold blue]Balatro Interactive Shell[/bold blue]",
        border_style="blue"
    ))

    try:
        client = BalatroClient(host=args.host, port=args.port)

        # Verify connection
        health = client.health()
        console.print(f"[green]Connected![/green] Bridge version: {health.version}")

    except BalatroConnectionError as e:
        console.print(f"[red]Failed to connect:[/red] {e}")
        sys.exit(1)

    # REPL loop
    while True:
        try:
            cmd_input = Prompt.ask("\n[bold cyan]balatro>[/bold cyan]")
            cmd_parts = cmd_input.strip().split()

            if not cmd_parts:
                continue

            cmd = cmd_parts[0].lower()
            cmd_args = cmd_parts[1:]

            if cmd in ("quit", "q", "exit"):
                console.print("[yellow]Goodbye![/yellow]")
                break

            elif cmd in ("help", "?"):
                console.print(HELP_TEXT)

            elif cmd in ("state", "s"):
                state = client.get_state()
                print_state_summary(state)

            elif cmd in ("legal", "l"):
                legal = client.get_legal_actions()
                print_legal_actions(legal)

            elif cmd in ("health", "h"):
                health = client.health()
                console.print(f"Status: {health.status}")
                console.print(f"Uptime: {health.uptime_ms / 1000:.1f}s")
                console.print(f"Requests: {health.request_count}")

            elif cmd == "action":
                if not cmd_args:
                    console.print("[yellow]Usage: action <json>[/yellow]")
                    continue
                try:
                    json_str = " ".join(cmd_args)
                    data = json.loads(json_str)
                    action = ActionRequest(
                        type=ActionType(data["type"]),
                        params=data.get("params", {})
                    )
                    execute_action(client, action)
                except json.JSONDecodeError as e:
                    console.print(f"[red]Invalid JSON:[/red] {e}")
                except (KeyError, ValueError) as e:
                    console.print(f"[red]Invalid action:[/red] {e}")

            elif cmd == "play":
                indices = parse_indices(cmd_args)
                if not indices:
                    console.print("[yellow]Usage: play <index1> <index2> ...[/yellow]")
                    continue
                action = ActionRequest(
                    type=ActionType.PLAY_HAND,
                    params={"card_indices": indices}
                )
                execute_action(client, action)

            elif cmd == "discard":
                indices = parse_indices(cmd_args)
                if not indices:
                    console.print("[yellow]Usage: discard <index1> <index2> ...[/yellow]")
                    continue
                action = ActionRequest(
                    type=ActionType.DISCARD,
                    params={"card_indices": indices}
                )
                execute_action(client, action)

            elif cmd == "reroll":
                execute_action(client, ActionRequest(type=ActionType.SHOP_REROLL))

            elif cmd == "endshop":
                execute_action(client, ActionRequest(type=ActionType.SHOP_END))

            elif cmd == "sort":
                mode = cmd_args[0] if cmd_args else "rank"
                action = ActionRequest(
                    type=ActionType.SORT_HAND,
                    params={"mode": mode}
                )
                execute_action(client, action)

            elif cmd == "buy":
                if not cmd_args:
                    console.print("[yellow]Usage: buy <slot>[/yellow]")
                    continue
                try:
                    slot = int(cmd_args[0])
                    action = ActionRequest(
                        type=ActionType.SHOP_BUY,
                        params={"slot": slot}
                    )
                    execute_action(client, action)
                except ValueError:
                    console.print("[red]Invalid slot number[/red]")

            elif cmd == "sell":
                if not cmd_args:
                    console.print("[yellow]Usage: sell <joker_index>[/yellow]")
                    continue
                try:
                    idx = int(cmd_args[0])
                    action = ActionRequest(
                        type=ActionType.SHOP_SELL_JOKER,
                        params={"joker_index": idx}
                    )
                    execute_action(client, action)
                except ValueError:
                    console.print("[red]Invalid joker index[/red]")

            else:
                console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
                console.print("Type 'help' for available commands")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except EOFError:
            break

    client.close()


if __name__ == "__main__":
    main()
