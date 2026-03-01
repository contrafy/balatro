# Balatro RL Harness - Developer Guide

## Process Management

**Agents must autonomously manage the Balatro process while developing, debugging, and testing.**
Do not ask the user to restart the game — kill and relaunch it yourself whenever changes need to be tested.

### Kill Balatro
```bash
taskkill //F //IM Balatro.exe
```
Note: bash requires `//F` and `//IM` (double slash), not single `/F /IM`.

### Launch Balatro (Steam)
```bash
# Launch via Steam (allows Steamodded/Lovely to load properly)
"/c/Program Files (x86)/Steam/steam.exe" -applaunch 2379780 &
```
Wait ~5 seconds after launch before making HTTP requests to the bridge.

### Deploy mod changes
After editing `game_mod/BalatroRLBridge/main.lua`, deploy to the live mods folder:
```bash
cp "C:/Users/contrafy/git/balatro/game_mod/BalatroRLBridge/main.lua" \
   "C:/Users/contrafy/AppData/Roaming/Balatro/Mods/BalatroRLBridge/main.lua"
```

### Full dev cycle
```bash
# 1. Kill game
taskkill //F //IM Balatro.exe

# 2. Deploy mod
cp "C:/Users/contrafy/git/balatro/game_mod/BalatroRLBridge/main.lua" \
   "C:/Users/contrafy/AppData/Roaming/Balatro/Mods/BalatroRLBridge/main.lua"

# 3. Launch game
"/c/Program Files (x86)/Steam/steam.exe" -applaunch 2379780 &

# 4. Wait for game to load (~20 seconds), then verify bridge
sleep 20 && python python/balatro_env/scripts/do_smoke_actions.py probe_health
```

### Crash Detection

**The game can appear to be running (process exists) but have crashed** — the bridge goes offline while `Balatro.exe` still shows in the task list. Always check BOTH:

```bash
# 1. Is the process alive?
tasklist //FI "IMAGENAME eq Balatro.exe"

# 2. Is the bridge responding?
python -c "
import requests, sys
try:
    r = requests.get('http://127.0.0.1:7777/health', timeout=3)
    print('healthy:', r.json().get('version'))
except Exception as e:
    print('OFFLINE:', e)
    sys.exit(1)
"
```

If process exists but bridge is offline after 5+ seconds:
1. **Check the log** — find the latest lovely log in `%APPDATA%/Balatro/Mods/lovely/log/` and grep for `ERROR` to see the crash cause
2. **Kill and relaunch** — `taskkill //F //IM Balatro.exe && sleep 2 && "/c/Program Files (x86)/Steam/steam.exe" -applaunch 2379780 &`
3. **Wait 20 seconds** before retrying the bridge

**The bridge needs ~15-20 seconds after launch to become available** (not 5s as previously noted).

### Subagent / Background Task Strategy

Use background Bash tasks (`run_in_background: true`) for long-running waits so the main context stays free for decision-making:

- **Waiting for bridge**: Run the poll loop in background; check output file once it completes
- **Running the agent (play_agent.py)**: Always background so you can monitor and intervene
- **Log analysis after crash**: Quick foreground read — do this immediately when bridge goes offline
- **Process/health checks**: Quick foreground, not background

```bash
# Good: background poll loop
for i in $(seq 1 30); do
  health=$(python -c "import requests; r=requests.get('http://127.0.0.1:7777/health',timeout=2); print('ok')" 2>/dev/null)
  [ "$health" = "ok" ] && echo "READY" && break
  sleep 2
done
```

Use `Task` with `subagent_type=Bash` (background) for the agent run so you can observe output and intervene without blocking main context.

## Logs

- Lovely log (latest run): `C:/Users/contrafy/AppData/Roaming/Balatro/Mods/lovely/log/` (most recent file)
- Mod source (runtime): `C:/Users/contrafy/AppData/Roaming/Balatro/Mods/BalatroRLBridge/main.lua`
- Lovely dump (patched game source): `C:/Users/contrafy/AppData/Roaming/Balatro/Mods/lovely/dump/`

## Project Structure

```
game_mod/BalatroRLBridge/main.lua   ← Lua mod (edit here, then deploy)
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
cd python && python -m pytest
```

## Interactive Shell

```bash
cd python && python balatro_env/scripts/interactive_shell.py
```

Commands: `state`, `legal`, `play`, `discard`, `reroll`, `endshop`, `buy`, `sell`, `blind`, `skip`, `cashout`
