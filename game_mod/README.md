# Balatro RL Bridge - Game Mod

This directory contains the Lua mod that runs inside Balatro to expose game state and accept actions via HTTP.

## Contents

- `install.md` - Detailed installation instructions for macOS
- `BalatroRLBridge/` - The mod files
  - `mod.json` - Mod metadata for Steamodded
  - `main.lua` - HTTP server and game interface

## Quick Install

1. Install Lovely Injector and Steamodded (see `install.md`)
2. Copy `BalatroRLBridge/` to `~/Library/Application Support/Balatro/Mods/`
3. Launch Balatro via `./run_lovely_macos.sh`
4. Test with `curl http://127.0.0.1:7777/health`

## API

The bridge exposes these HTTP endpoints on `127.0.0.1:7777`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/state` | GET | Current game state |
| `/legal` | GET | Legal actions |
| `/action` | POST | Execute action |
| `/reset` | POST | Reset game |
| `/config` | POST | Update config |

## Configuration

Edit `CONFIG` table in `main.lua` to change:

```lua
local CONFIG = {
    host = "127.0.0.1",  -- Bind address
    port = 7777,          -- HTTP port
    max_request_size = 65536,
    schema_version = "1.0.0",
}
```

## Development

The mod hooks into Balatro's game loop via `love.update()` to process HTTP requests without blocking. State extraction accesses Balatro's global `G` table which contains all game data.

Key globals:
- `G.GAME` - Current run state
- `G.hand` - Cards in hand
- `G.jokers` - Owned jokers
- `G.shop` - Shop state
- `G.STATE` - Current game phase
- `G.FUNCS` - Game action functions
