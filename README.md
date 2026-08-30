# Balatro RL Harness

A reinforcement learning harness for the game **Balatro**, providing true game state extraction and action execution via an in-game HTTP bridge. Works on **Windows** and **macOS**.

## Overview

This project enables RL agents to play Balatro by:

1. **In-game Lua mod** (`game_mod/`) — Injects into Balatro via Lovely Injector to expose game state over HTTP
2. **Python harness** (`python/`) — Gymnasium-compatible environment, HTTP client, and a rule-based agent
3. **Advisor CLI + playbook** (`python/balatro_env/scripts/cli.py`, `docs/`) — a joker-aware scoring estimator and shop/play advisor that LLM player agents drive the game through, plus the strategy playbook and per-run post-mortems they learn from

The harness extracts true game state (no OCR) including:
- Current hand, jokers, consumables
- Shop inventory and prices
- Blind requirements and progress
- Legal action masks for each decision point

## Quick Start

### 1. Install the Mod

See [game_mod/install.md](game_mod/install.md) for detailed platform-specific instructions.

**Windows (summary):**
```powershell
# Download Lovely Injector (version.dll) → Balatro install dir
# Install Steamodded → %APPDATA%\Balatro\Mods\Steamodded
# Copy BalatroRLBridge → %APPDATA%\Balatro\Mods\BalatroRLBridge
```

**macOS (summary):**
```bash
# Download Lovely Injector (liblovely.dylib) → Balatro install dir
# Install Steamodded → ~/Library/Application Support/Balatro/Mods/Steamodded
# Copy BalatroRLBridge → ~/Library/Application Support/Balatro/Mods/BalatroRLBridge
```

### 2. Launch Balatro

```bash
# Windows (via Steam)
steam -applaunch 2379780

# macOS (via launch script)
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
./run_lovely_macos.sh
```

### 3. Verify Bridge

```bash
curl http://127.0.0.1:7777/health
# → {"status":"ok","version":"1.0.0","uptime_ms":12345}
```

### 4. Install Python Package

```bash
cd python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 5. Run the Agent

```bash
# Plain console output
python -m balatro_env.scripts.play_agent

# Rich TUI dashboard (fullscreen)
python -m balatro_env.scripts.play_agent --tui

# With custom delay between decisions
python -m balatro_env.scripts.play_agent --tui --delay 1.2
```

The agent auto-starts runs, plays hands, shops, and restarts on game over.

## Agent Strategy

The built-in agent (`play_agent.py`) uses a deterministic rule-based strategy optimized for Red Deck on White Stake:

| Component | Approach |
|-----------|----------|
| **Hand play** | Flush-first: aggressively discard off-suit cards to build flushes. Falls back to straights, then best available (full house, three of a kind, pairs). |
| **Smeared Joker** | When owned, treats Hearts/Diamonds as "Red" and Clubs/Spades as "Black" for flush detection and discard decisions. |
| **Planet priorities** | Buys/picks Jupiter (Flush) with highest priority. Deprioritizes Mars (Four of a Kind) and Neptune (Straight Flush) — hands the agent rarely completes. |
| **Joker buying** | Prioritizes Droll Joker, Four Fingers, Smeared Joker, and xMult jokers. Sells weakest joker when a significantly better one appears in the shop. |
| **Tarot cards** | Uses no-select tarots (Hermit, Judgement) immediately. Targets suit-changers and enhancements on hand cards with proper SELECT_CARDS → USE_CONSUMABLE flow. |
| **Pack opening** | Waits for flip animations before selecting. Picks one card at a time with confirmation polling. |

## LLM Agent Swarm

Beyond the rule-based agent, the repo supports a swarm of LLM player agents (Claude subagents) that each play a full run on their own game instance, coordinated by an orchestrator that patches the harness between runs.

### Parallel game instances

Each instance gets its own `HOME` (with its own `Library/Application Support/Balatro/Mods` copy) and its own bridge port via `BALATRO_RL_PORT`:

```bash
# macOS: six instances on ports 7777-7782
HOME=~/balatro-homes/h1 BALATRO_RL_PORT=7777 ./run_lovely_macos.sh &
HOME=~/balatro-homes/h2 BALATRO_RL_PORT=7778 ./run_lovely_macos.sh &
# ...
```

A six-instance swarm runs comfortably on an M-series Mac (~650MB and a fraction of a core each).

### The advisor CLI

Player agents never do scoring arithmetic themselves — they drive the game through `cli.py`, which asks the bridge for state and prints estimates and advice:

```bash
export BALATRO_RL_PORT=7778
python balatro_env/scripts/cli.py s                    # compact state + blind-select advice
python balatro_env/scripts/cli.py hands                # candidate hands with joker-aware est
python balatro_env/scripts/cli.py advise               # play/discard advice for this hand
python balatro_env/scripts/cli.py shopadvise           # ranked shop advice (buy/sell/reroll)
python balatro_env/scripts/cli.py play TWOPAIR 1 2 5 6 # aborts if the game preview disagrees
python balatro_env/scripts/cli.py start Black Deck 3   # new run at a given stake
```

The estimator models scoring order, retriggers, enhancements, editions, held-card effects, joker copies (Blueprint/Brainstorm), growth jokers, and boss effects. Every played hand logs `est` vs actual to `docs/runs/est_log.tsv`; misses over 20% get diagnosed and fixed in the estimator, so accuracy improves run over run.

### The learning loop

1. Each player agent reads `docs/PLAYBOOK.md` before its run and follows the CLI's advice plus its own judgment.
2. On game over it writes a post-mortem to `docs/runs/<port>_<run_id>.md` (build, money curve, the one decision it would change, CLI issues).
3. The orchestrator folds those findings back into `cli.py` and the playbook, then relaunches the port.

### Progress

| Milestone | Status |
|-----------|--------|
| Black Deck, White Stake (1) | **Beaten** — run `7779_E19RBJB8`: Two Pair L8, Spare Trousers, Yorick x4, Photograph+Pareidolia, 153664/100000 vs Verdant Leaf |
| Black Deck, Red Stake (2) | **Beaten** — run `7777_YYA2GKBR`: Two Pair L12, Space Joker, Photograph + foil Cavendish x3, 108480/100000 vs Cerulean Bell |
| Black Deck, Green Stake (3) | In progress — deepest so far ante 6 Big Blind (`7778_HFZL5GR2`); the faster blind scaling punishes slow starts, so most fixes target ante 1-3 economy |

## Scripts

```bash
# Run the agent
python -m balatro_env.scripts.play_agent [--tui] [--delay SECS]

# Interactive REPL
python -m balatro_env.scripts.interactive_shell

# Smoke tests
python -m balatro_env.scripts.do_smoke_actions probe_health
python -m balatro_env.scripts.do_smoke_actions dump_state
python -m balatro_env.scripts.do_smoke_actions list_legal_actions

# Advisor CLI (used by the LLM agent swarm; BALATRO_RL_PORT selects the instance)
python balatro_env/scripts/cli.py s
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Balatro (LÖVE2D)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              BalatroRLBridge (Lua mod)                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │ State       │  │ Legal       │  │ Action       │  │  │
│  │  │ Extractor   │  │ Actions     │  │ Executor     │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │  │
│  │         └────────────────┴────────────────┘           │  │
│  │                          │                            │  │
│  │              ┌───────────┴───────────┐                │  │
│  │              │    HTTP Server        │                │  │
│  │              │  127.0.0.1:7777       │                │  │
│  │              └───────────────────────┘                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP (JSON)
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Python Harness                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │BalatroClient│  │BalatroEnv   │  │ play_agent.py        │ │
│  │ (HTTP)      │  │ (Gymnasium) │  │ (rule-based + TUI)   │ │
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
  "phase": "SELECTING_HAND",
  "money": 4,
  "ante": 1,
  "hands_remaining": 4,
  "discards_remaining": 3,
  "hand": [
    {"id": "1", "rank": "King", "suit": "Hearts"}
  ],
  "jokers": [],
  "blind": {"name": "Small Blind", "chips_needed": 300}
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
│   ├── install.md              # Installation guide (Windows + macOS)
│   └── BalatroRLBridge/
│       ├── mod.json            # Mod metadata
│       └── main.lua            # Bridge implementation
├── python/
│   ├── balatro_env/            # Python package
│   │   ├── client.py           # HTTP client
│   │   ├── env.py              # Gymnasium environment
│   │   ├── schemas.py          # Pydantic data models
│   │   ├── strategy.py         # Shared decision logic
│   │   ├── action_space.py     # Action encoding
│   │   ├── obs_tokenizer.py    # State tokenization
│   │   └── scripts/
│   │       ├── play_agent.py   # Rule-based agent (with TUI)
│   │       ├── cli.py          # Advisor CLI for the LLM agent swarm
│   │       ├── interactive_shell.py
│   │       └── do_smoke_actions.py
│   ├── tests/
│   └── pyproject.toml
├── docs/
│   ├── PLAYBOOK.md             # Living strategy playbook the LLM agents follow
│   └── runs/                   # Per-run post-mortems + est/shop calibration logs
└── README.md
```

## Requirements

- **Windows 10+** or **macOS** (Apple Silicon M1/M2/M3/M4)
- Balatro via Steam
- Python 3.10+

## Troubleshooting

### Bridge not responding

1. Ensure Balatro is running with mods loaded
2. Check terminal/log output for `[BalatroRLBridge] HTTP server started`
3. Verify port 7777 is not in use: `curl http://127.0.0.1:7777/health`

### Windows: Mod not loading

1. Verify `version.dll` (Lovely Injector) is in the Balatro install directory
2. Ensure Steamodded is in `%APPDATA%\Balatro\Mods\Steamodded\`
3. Launch via Steam (Lovely hooks in automatically)
4. Check logs in `%APPDATA%\Balatro\Mods\lovely\log\`

### macOS: Mod not loading

1. Verify Lovely Injector files are in Balatro directory
2. Launch via `./run_lovely_macos.sh`, not Steam
3. If Gatekeeper blocks files: `xattr -d com.apple.quarantine liblovely.dylib`

### Game appears running but bridge is offline

The game process can survive a Lua crash. Check both:
```bash
# 1. Is process alive?
tasklist /FI "IMAGENAME eq Balatro.exe"     # Windows
pgrep -l Balatro                             # macOS

# 2. Is bridge responding?
curl http://127.0.0.1:7777/health
```

If process exists but bridge is offline, check the latest log in the lovely log directory for errors, then kill and relaunch the game.

## License

MIT
