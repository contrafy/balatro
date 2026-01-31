#!/usr/bin/env python3
"""List legal actions available in the current game state.

Usage:
    python -m balatro_env.scripts.list_legal_actions [--host HOST] [--port PORT]

Fetches and displays all legal actions with their parameters.
"""

import argparse
import sys

from rich.console import Console

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.util import print_legal_actions, save_legal_artifact

console = Console()


def main():
    parser = argparse.ArgumentParser(description="List legal actions in Balatro")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host address")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port number")
    parser.add_argument("--output", default="artifacts", help="Output directory for JSON")
    args = parser.parse_args()

    try:
        client = BalatroClient(host=args.host, port=args.port)
        console.print(f"Fetching legal actions from {args.host}:{args.port}...")

        legal = client.get_legal_actions()

        if legal.error:
            console.print(f"[yellow]Warning:[/yellow] {legal.error}")

        print_legal_actions(legal)

        # Save artifact
        filepath = save_legal_artifact(legal, args.output)
        console.print(f"\n[green]Legal actions saved to:[/green] {filepath}")

        # Summary by type
        console.print(f"\n[bold]Action Type Summary:[/bold]")
        action_types = {}
        for action in legal.actions:
            t = action.type.value
            action_types[t] = action_types.get(t, 0) + 1

        for t, count in sorted(action_types.items()):
            console.print(f"  {t}: {count}")

        console.print(f"\n[bold]Total legal actions:[/bold] {len(legal.actions)}")

        client.close()
        sys.exit(0)

    except BalatroConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
