# Balatro RL Bridge - Game Mod

Lua mod that runs inside Balatro (Lovely only, no Steamodded) to expose game state, strictly validated
actions, and a per-run trajectory recorder over HTTP.

## Contents

- `install.md` - installation (Windows and macOS)
- `BalatroRLBridge/`
  - `lovely.toml` - Lovely loader: registers `main.lua` as module `balatro_rl_bridge` and calls it every frame
  - `main.lua` - HTTP server, observation, `/legal` domains, validation, execution, recorder
- `windows/launch_instance.ps1` - per-port isolated instance launcher (deploys the bridge on every launch)

## API

Endpoints on `127.0.0.1:$BALATRO_RL_PORT` (default 7777). The exact shapes are specified in
`docs/DATA_CONTRACT.md`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Versions, bridge hash, recorder status, current trajectory path |
| `/state` | GET | Policy-visible observation + `settled` |
| `/legal` | GET | Legal action types with exact parameter domains (empty unless settled) |
| `/action` | POST | Validate against `/legal`, execute, record a step (or a reject line) |
| `/preview` | POST | Read-only poker-hand preview for hand positions |
| `/debug` | GET | Read-only engine status (locks, event queue) |
| `/debug/eval` | POST | Test-only Lua eval; only with `BALATRO_RL_DEBUG=1`, taints the trajectory |
