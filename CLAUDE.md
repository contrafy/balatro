# Balatro RL Harness - Developer Guide

## Process Management

**Agents must autonomously manage the Balatro process while developing, debugging, and testing.**
Do not ask the user to restart the game — kill and relaunch it yourself whenever changes need to be tested.

Harness instances never run from the real `%APPDATA%/Balatro` (the user's saves). The bridge unlocks everything on the profile it boots and starting a run overwrites `save.jkr`. Each instance lives in `C:/Users/contrafy/balatro-instances/<port>`; see `game_mod/install.md` (Windows section).

Use dash switches for `taskkill`/`tasklist`. They work from Git Bash, cmd and PowerShell; `/F` breaks under Git Bash path conversion and `//F` breaks everywhere else.

### Kill Balatro
Several instances (and other agents' instances) may be running: kill by PID, never by image name.
```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='Balatro.exe'\" | Select ProcessId,CommandLine | Format-List"
taskkill -F -PID <pid>   # the CommandLine's --mod-dir ...\balatro-instances\<port>\... identifies the port
```

### Launch Balatro (also deploys the bridge)
```bash
powershell -NoProfile -ExecutionPolicy Bypass -File game_mod/windows/launch_instance.ps1 -Port 7777
# -> "Balatro PID <pid> on port 7777 ..."
```
The script copies `game_mod/BalatroRLBridge` (main.lua + lovely.toml) into the instance's `Mods` (removing anything else there, e.g. Steamodded: the bridge is Lovely-only so game logic stays vanilla), then starts `Balatro.exe` directly with `APPDATA=<instance>`, `BALATRO_RL_PORT=<port>`, `BALATRO_RL_DATA_DIR=<repo>/data`, `--mod-dir <instance>/Balatro/Mods`. There is no separate deploy step. Do not use `steam.exe -applaunch 2379780`: it stalls in Steam's launch flow on this machine and can't set per-instance env. `-DebugEval` enables a test-only Lua eval endpoint that taints trajectories; never use it for data collection.

### Full dev cycle
```bash
taskkill -F -PID <pid of your instance>
powershell -NoProfile -ExecutionPolicy Bypass -File game_mod/windows/launch_instance.ps1 -Port 7777
sleep 5 && curl -s http://127.0.0.1:7777/health
```

### Crash Detection

**The game can appear to be running (process exists) but have crashed** — the bridge goes offline while `Balatro.exe` still shows in the task list. Always check BOTH:

```bash
# 1. Is the process alive?
tasklist -FI "IMAGENAME eq Balatro.exe"

# 2. Is the bridge responding?
curl -s -m 3 http://127.0.0.1:7777/health || echo OFFLINE
```

If process exists but bridge is offline after 5+ seconds:
1. **Check the log** — newest file in `C:/Users/contrafy/balatro-instances/<port>/Balatro/Mods/lovely/log/`; grep it for `ERROR` to see the crash cause
2. **Kill and relaunch** with the commands above

The bridge answers about 4 seconds after launch.

### Subagent / Background Task Strategy

Use background Bash tasks (`run_in_background: true`) for long-running waits so the main context stays free for decision-making:

- **Waiting for bridge**: Run the poll loop in background; check output file once it completes
- **Running the agent (play_agent.py)**: Always background so you can monitor and intervene
- **Log analysis after crash**: Quick foreground read — do this immediately when bridge goes offline
- **Process/health checks**: Quick foreground, not background

```bash
# Good: background poll loop
for i in $(seq 1 30); do
  curl -s -m 2 http://127.0.0.1:7777/health >/dev/null && echo "READY" && break
  sleep 2
done
```

Use `Task` with `subagent_type=Bash` (background) for the agent run so you can observe output and intervene without blocking main context.

## Logs

Per instance (`<I>` = `C:/Users/contrafy/balatro-instances/<port>/Balatro`):
- Lovely log (latest run): `<I>/Mods/lovely/log/` (most recent file)
- Mod source (runtime): `<I>/Mods/BalatroRLBridge/main.lua`
- Lovely dump (patched game source): `<I>/Mods/lovely/dump/`

## Project Structure

```
game_mod/BalatroRLBridge/main.lua   ← Lua mod (edit here; launch_instance.ps1 deploys it)
game_mod/windows/launch_instance.ps1 ← Windows instance launcher
python/balatro_env/                  ← Python RL harness
  schemas.py                         ← Pydantic models for game state/actions
  env.py                             ← Gymnasium environment
  scripts/
    do_smoke_actions.py              ← Smoke tests / autopilot
    interactive_shell.py             ← Interactive REPL for manual testing
python/.venv/                        ← Python virtualenv
```

## Running Tests

```bash
cd python && .venv/Scripts/python -m pytest
```
Live tests use the bridge on 7777. `test_health.py` expects nothing to be listening on port 7778, so stop any 7778 instance first.

## Interactive Shell

```bash
cd python && .venv/Scripts/python balatro_env/scripts/interactive_shell.py
```

Commands: `state`, `legal`, `play`, `discard`, `reroll`, `endshop`, `buy`, `sell`, `blind`, `skip`, `cashout`

## LLM Swarm

Orchestrator runbook (instances, seeds, player prompt, trajectory validation): `docs/SWARM.md`. Players use
`bash python/balatro_env/scripts/b.sh <port> <cmd> --why "..."` and follow `docs/PLAYBOOK.md`.
