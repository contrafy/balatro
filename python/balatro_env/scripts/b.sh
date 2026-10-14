#!/usr/bin/env bash
# Swarm wrapper for cli.py: b.sh <port> <cmd> [args...] [--why "one-line rationale"]
#   bash python/balatro_env/scripts/b.sh 7778 s
#   bash python/balatro_env/scripts/b.sh 7778 play PAIR 2 5 1 3 4 --why "Pair of Kings + fillers, est 340 > 300"
# Agent identity for the trajectory meta comes from BALATRO_AGENT_ID / BALATRO_AGENT_MODEL (default agent: port-<port>).
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
port="$1"
case "$port" in
  '' | *[!0-9]*) echo 'usage: b.sh <port> <cmd> [args...] [--why "..."]' >&2; exit 1 ;;
esac
shift
py="$root/python/.venv/Scripts/python.exe"
cli="$here/cli.py"
if command -v cygpath >/dev/null 2>&1; then
  cli="$(cygpath -w "$cli")"                       # Git Bash / MSYS
elif command -v wslpath >/dev/null 2>&1 && [ -x "$py" ]; then
  cli="$(wslpath -w "$cli")"                       # WSL bash driving the Windows venv
  export WSLENV="BALATRO_RL_PORT:BALATRO_AGENT_ID:BALATRO_AGENT_MODEL:PYTHONIOENCODING${WSLENV:+:$WSLENV}"
fi
[ -x "$py" ] || py="$root/python/.venv/bin/python"
export BALATRO_RL_PORT="$port" PYTHONIOENCODING=utf-8
exec "$py" "$cli" "$@"
