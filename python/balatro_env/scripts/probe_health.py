#!/usr/bin/env python3
"""Probe the Balatro RL Bridge health endpoint.

Usage:
    python -m balatro_env.scripts.probe_health [--host HOST] [--port PORT]

Returns exit code 0 if healthy, 1 otherwise.
"""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from balatro_env.client import BalatroClient, BalatroConnectionError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Probe Balatro RL Bridge health")
    parser.add_argument("--host", default="127.0.0.1", help="Bridge host address")
    parser.add_argument("--port", type=int, default=7777, help="Bridge port number")
    parser.add_argument("--timeout", type=float, default=5.0, help="Connection timeout")
    args = parser.parse_args()

    console.print(f"Connecting to Balatro RL Bridge at {args.host}:{args.port}...")

    try:
        client = BalatroClient(host=args.host, port=args.port, timeout=args.timeout)
        health = client.health()

        console.print(Panel.fit(
            f"[bold green]Status:[/bold green] {health.status}\n"
            f"[bold]Version:[/bold] {health.version}\n"
            f"[bold]Uptime:[/bold] {health.uptime_ms / 1000:.1f}s\n"
            f"[bold]Requests:[/bold] {health.request_count}\n"
            f"[bold]Errors:[/bold] {health.error_count}",
            title="[green]Bridge Health[/green]",
            border_style="green"
        ))

        if health.last_error:
            console.print(f"[yellow]Last Error:[/yellow] {health.last_error}")

        client.close()
        sys.exit(0)

    except BalatroConnectionError as e:
        console.print(Panel.fit(
            f"[bold red]Connection Failed[/bold red]\n\n{e}",
            title="[red]Error[/red]",
            border_style="red"
        ))
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Is Balatro running with the RL Bridge mod?")
        console.print("2. Check terminal output for mod loading messages")
        console.print("3. Try: curl http://127.0.0.1:7777/health")
        sys.exit(1)


if __name__ == "__main__":
    main()
