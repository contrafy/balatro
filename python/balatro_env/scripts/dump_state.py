#!/usr/bin/env python3
"""Dump the current Balatro game state.

Usage:
    python -m balatro_env.scripts.dump_state [--host HOST] [--port PORT] [--output DIR]

Fetches the current game state, validates it, prints a summary, and saves to JSON.
"""

import argparse
import sys

from rich.console import Console

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.util import print_state_summary, save_state_artifact

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Dump Balatro game state")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host address")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port number")
    parser.add_argument("--output", default="artifacts", help="Output directory for JSON")
    parser.add_argument("--json-only", action="store_true", help="Only output JSON, no summary")
    args = parser.parse_args()

    try:
        client = BalatroClient(host=args.host, port=args.port)
        console.print(f"Fetching state from {args.host}:{args.port}...")

        state = client.get_state()

        if state.error:
            console.print(f"[yellow]Warning:[/yellow] State has error: {state.error}")

        if not args.json_only:
            print_state_summary(state)

        # Save artifact
        filepath = save_state_artifact(state, args.output)
        console.print(f"\n[green]State saved to:[/green] {filepath}")

        # Validation summary
        console.print(f"\n[bold]Validation:[/bold]")
        console.print(f"  Schema version: {state.schema_version}")
        console.print(f"  Phase: {state.phase.value}")
        console.print(f"  Hand cards: {len(state.hand)}")
        console.print(f"  Jokers: {len(state.jokers)}")
        console.print(f"  Consumables: {len(state.consumables)}")
        console.print(f"  Is decision point: {state.is_decision_point()}")

        client.close()
        sys.exit(0)

    except BalatroConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
