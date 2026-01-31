# Balatro RL Harness

A reinforcement learning harness for the game Balatro, providing true game state extraction and action execution via an in-game HTTP bridge.

## Overview

This project enables RL agents to play Balatro by:

1. **In-game Lua mod** (`game_mod/`) - Injects into Balatro to expose game state via HTTP
2. **Python harness** (`python/`) - Gymnasium-compatible environment for RL training

The harness extracts true game state (no OCR) including:
- Current hand, jokers, consumables
- Shop inventory and prices
- Blind requirements and progress
- Legal action masks for each decision point

## Quick Start

### 1. Install the Mod

See [game_mod/install.md](game_mod/install.md) for detailed instructions.

```bash
# Download Lovely Injector for Apple Silicon
curl -L -o lovely.tar.gz https://github.com/ethangreen-dev/lovely-injector/releases/latest/download/lovely-aarch64-apple-darwin.tar.gz

# Extract to Balatro directory
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
tar -xzf ~/Downloads/lovely.tar.gz
chmod +x run_lovely_macos.sh

# Install Steamodded
mkdir -p ~/Library/Application\ Support/Balatro/Mods
cd ~/Library/Application\ Support/Balatro/Mods
git clone https://github.com/Steamodded/smods.git Steamodded

# Copy RL Bridge mod (from this repo)
cp -r /path/to/this/repo/game_mod/BalatroRLBridge ~/Library/Application\ Support/Balatro/Mods/
```

### 2. Launch Balatro

```bash
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
./run_lovely_macos.sh
```

### 3. Verify Bridge

```bash
# Test connection
curl http://127.0.0.1:7777/health
```

### 4. Install Python Package

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 5. Run Tests

```bash
# Probe health
python -m balatro_env.scripts.probe_health

# Dump state
python -m balatro_env.scripts.dump_state

# List legal actions
python -m balatro_env.scripts.list_legal_actions

# Interactive shell
python -m balatro_env.scripts.interactive_shell
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Balatro (LÖVE2D)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              BalatroRLBridge (Lua mod)                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │  │
│  │  │ State       │  │ Legal       │  │ Action       │   │  │
│  │  │ Extractor   │  │ Actions     │  │ Executor     │   │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │  │
│  │         │                │                │           │  │
│  │         └────────────────┴────────────────┘           │  │
│  │                          │                            │  │
│  │              ┌───────────┴───────────┐                │  │
│  │              │    HTTP Server        │                │  │
│  │              │  127.0.0.1:7777       │                │  │
│  │              └───────────────────────┘                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Python Harness                           │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │BalatroClient│  │BalatroEnv   │  │ Action Encoder       │ │
│  │ (HTTP)      │  │ (Gymnasium) │  │ Obs Tokenizer        │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## HTTP API

The in-game bridge exposes these endpoints on `http://127.0.0.1:7777`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with version and uptime |
| `/state` | GET | Full game state as JSON |
| `/legal` | GET | Legal actions for current phase |
| `/action` | POST | Execute an action |
| `/reset` | POST | Reset game (best effort) |
| `/config` | POST | Update bridge configuration |

### Example: Get State

```bash
curl http://127.0.0.1:7777/state | jq .
```

```json
{
  "schema_version": "1.0.0",
  "timestamp_ms": 1234567890,
  "phase": "SELECTING_HAND",
  "money": 4,
  "ante": 1,
  "hands_remaining": 4,
  "discards_remaining": 3,
  "hand": [
    {"id": "1", "rank": "King", "suit": "Hearts", ...},
    ...
  ],
  "jokers": [...],
  "blind": {"name": "Small Blind", "chips_needed": 300, ...}
}
```

### Example: Execute Action

```bash
curl -X POST http://127.0.0.1:7777/action \
  -H "Content-Type: application/json" \
  -d '{"type": "PLAY_HAND", "params": {"card_indices": [1, 2, 3, 4, 5]}}'
```

## Project Structure

```
balatro/
├── game_mod/
│   ├── install.md              # Installation guide
│   ├── BalatroRLBridge/
│   │   ├── mod.json            # Mod metadata
│   │   └── main.lua            # Bridge implementation
│   └── README.md
├── python/
│   ├── balatro_env/            # Python package
│   │   ├── client.py           # HTTP client
│   │   ├── env.py              # Gymnasium env
│   │   ├── schemas.py          # Data models
│   │   ├── action_space.py     # Action encoding
│   │   ├── obs_tokenizer.py    # State tokenization
│   │   └── scripts/            # CLI tools
│   ├── tests/                  # Integration tests
│   └── pyproject.toml
└── README.md
```

## Requirements

- macOS on Apple Silicon (M1/M2/M3)
- Balatro via Steam
- Python 3.10+
- PyTorch 2.0+

## Troubleshooting

### Bridge not responding

1. Check terminal output when launching Balatro
2. Look for `[BalatroRLBridge] HTTP server started` message
3. Ensure port 7777 is not in use

### Mod not loading

1. Verify Lovely Injector files are in Balatro directory
2. Check Steamodded is installed in Mods folder
3. Launch via `./run_lovely_macos.sh`, not Steam

### macOS Gatekeeper blocks files

```bash
xattr -d com.apple.quarantine liblovely.dylib
```

Or allow in System Settings → Privacy & Security.

## License

MIT
