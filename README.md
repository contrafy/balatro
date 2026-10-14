# Balatro RL

Training a from-scratch model to win Balatro runs (Black Deck, Gold Stake) using the full vanilla action space. The current work is the data pipeline: an in-game HTTP bridge, a Python harness, and a swarm of LLM agents that play through it to produce replayable trajectories and a written strategy playbook. Works on **Windows** and **macOS**.

## Goal

An entity transformer policy with autoregressive pointer-head action decoding and a value head, trained with behavior cloning on swarm trajectories and then PPO in a headless copy of the real game engine (unmodified Lua source, rendering removed). Target: win Black Deck / Gold Stake (8) runs. Full plan: [docs/TRAINING_PLAN.md](docs/TRAINING_PLAN.md).

## Roadmap

1. **Data-ready bridge** (in progress): strict legality checks, a per-step trajectory recorder, and replay verification, per [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md).
2. **Swarm data collection**: LLM agents play full runs through the bridge, recording step-level trajectories with a one-line rationale per action, and distilling strategy into [docs/PLAYBOOK.md](docs/PLAYBOOK.md) and per-run post-mortems in `docs/runs/`.
3. **Headless engine**: the game source under LuaJIT with a batched step API; must replay every verified trajectory exactly.
4. **Behavior cloning** on trajectories that pass schema and replay validation.
5. **PPO** in the headless engine, with a White-to-Gold stake curriculum.
6. **Evaluation** on held-out seeds: win rate per stake versus the swarm.

## Components

1. **In-game Lua mod** (`game_mod/`): injects into Balatro via Lovely Injector and exposes game state, legal actions, and action execution over HTTP. The same state/legality/action code is the interface the model will see.
2. **Python harness** (`python/`): HTTP client, schemas, a Gymnasium environment and a rule-based baseline agent (existing tooling, not the training setup).
3. **Advisor CLI + playbook** (`python/balatro_env/scripts/cli.py`, `docs/`): a joker-aware scoring estimator and shop/play advisor that the LLM agents drive the game through, plus the strategy playbook and post-mortems they learn from.

State is read directly from the game (no OCR): hand, jokers, consumables, shop inventory and prices, blind requirements, and legal actions at each decision point.

## Quick Start

### 1. Install the Mod

See [game_mod/install.md](game_mod/install.md) for detailed platform-specific instructions.

**Windows (summary):**
```powershell
# Download Lovely Injector v0.9.0 (version.dll) → Balatro install dir
# No Steamodded: the bridge loads through Lovely only so game logic stays vanilla.
# Each instance gets its own save/mod dir under %USERPROFILE%\balatro-instances\<port>; the launcher deploys the bridge.
```

**macOS (summary):**
```bash
# Download Lovely Injector (liblovely.dylib) → Balatro install dir
# Copy BalatroRLBridge → ~/Library/Application Support/Balatro/Mods/BalatroRLBridge (no Steamodded)
```

### 2. Launch Balatro

```bash
# Windows: isolated instance on its own port (prints the PID)
powershell -NoProfile -ExecutionPolicy Bypass -File game_mod/windows/launch_instance.ps1 -Port 7777

# macOS (via launch script)
cd ~/Library/Application\ Support/Steam/steamapps/common/Balatro
./run_lovely_macos.sh
```

### 3. Verify Bridge

```bash
curl http://127.0.0.1:7777/health
```

### 4. Install Python Package

```bash
cd python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 5. Drive the Game

```bash
# Check state and legal actions
python -m balatro_env.scripts.do_smoke_actions dump_state
python -m balatro_env.scripts.do_smoke_actions list_legal_actions

# Rule-based baseline agent (console or --tui dashboard)
python -m balatro_env.scripts.play_agent --tui --delay 1.2
```

## Rule-based Baseline

`play_agent.py` is a deterministic, flush-first strategy (planet, joker, tarot and pack heuristics) tuned for Red Deck on White Stake. It is a harness smoke test and baseline, not part of the training pipeline.

## LLM Agent Swarm

The swarm is the current data source. LLM player agents (Claude subagents) each play full runs on their own game instance, coordinated by an orchestrator that patches the harness between runs. Their runs feed two things: step-level trajectories for behavior cloning (format in [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)) and written strategy in `docs/PLAYBOOK.md` and `docs/runs/`.

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

Player agents never do scoring arithmetic themselves — they drive the game through `cli.py` (via the `b.sh <port>` wrapper), which asks the bridge for state and prints estimates and advice. State-changing commands require `--why`; the orchestrator runbook is [docs/SWARM.md](docs/SWARM.md).

```bash
B="bash python/balatro_env/scripts/b.sh 7778"
$B s                                                       # compact state + blind-select advice
$B hands                                                   # candidate hands with joker-aware est
$B advise                                                  # play/discard advice for this hand
$B shopadvise                                              # ranked shop advice (buy/sell/reroll)
$B play TWOPAIR 1 2 5 6 --why "Two Pair est 412 > 300"     # aborts if the game preview disagrees
$B start Black Deck 3 --seed 7K3P9QXA --why "assigned seed" # new seeded run at a given stake
```

The estimator models scoring order, retriggers, enhancements, editions, held-card effects, joker copies (Blueprint/Brainstorm), growth jokers, and boss effects. Every played hand logs `est` vs actual to `docs/runs/est_log.tsv`; misses over 20% get diagnosed and fixed in the estimator, so accuracy improves run over run.

### The learning loop

1. Each player agent reads `docs/PLAYBOOK.md` before its run and follows the CLI's advice plus its own judgment, giving a one-line `--why` for each action.
2. On game over it writes a post-mortem to `docs/runs/<port>_<run_id>.md` (build, money curve, the one decision it would change, CLI issues).
3. The orchestrator folds those findings back into `cli.py` and the playbook, then relaunches the port.
4. Recorded trajectories count as training data only after they pass schema and replay verification.

### Swarm progress

Earlier macOS swarm runs (not recorded under the data contract; used as strategy knowledge only):

| Milestone | Status |
|-----------|--------|
| Black Deck, White Stake (1) | **Beaten** — run `7779_E19RBJB8`: Two Pair L8, Spare Trousers, Yorick x4, Photograph+Pareidolia, 153664/100000 vs Verdant Leaf |
| Black Deck, Red Stake (2) | **Beaten** — run `7777_YYA2GKBR`: Two Pair L12, Space Joker, Photograph + foil Cavendish x3, 108480/100000 vs Cerulean Bell |
| Black Deck, Green Stake (3) | In progress — deepest so far ante 6 Big Blind (`7778_HFZL5GR2`); the faster blind scaling punishes slow starts, so most fixes target ante 1-3 economy |

## Scripts

```bash
# Interactive REPL
python -m balatro_env.scripts.interactive_shell

# Smoke tests
python -m balatro_env.scripts.do_smoke_actions probe_health
python -m balatro_env.scripts.do_smoke_actions dump_state
python -m balatro_env.scripts.do_smoke_actions list_legal_actions
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

The in-game bridge exposes these endpoints on `http://127.0.0.1:<port>` (default 7777). Full spec (action types,
`/legal` parameter domains, settled rule, observation fields, trajectory files): [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health, versions, recorder status |
| `/state` | GET | Policy-visible game state plus `settled` |
| `/legal` | GET | Legal action types with exact parameter domains (empty while not settled) |
| `/action` | POST | Validate against `/legal`, execute, and record a legal action; illegal ones are rejected and recorded as `reject` |
| `/preview` | POST | Read-only poker-hand reading for a hypothetical card selection |

```bash
curl -X POST http://127.0.0.1:7777/action \
  -H "Content-Type: application/json" \
  -d '{"type": "PLAY_HAND", "params": {"card_indices": [1, 2, 3]}, "meta": {"why": "pair of kings clears 300"}}'
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
│   ├── TRAINING_PLAN.md        # Model, headless engine, and training stages
│   ├── DATA_CONTRACT.md        # Trajectory format and validity rules
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
2. Launch with `game_mod/windows/launch_instance.ps1` (not Steam), which sets `--mod-dir` and `APPDATA` per instance
3. Check logs in `%USERPROFILE%\balatro-instances\<port>\Balatro\Mods\lovely\log\`

### macOS: Mod not loading

1. Verify Lovely Injector files are in Balatro directory
2. Launch via `./run_lovely_macos.sh`, not Steam
3. If Gatekeeper blocks files: `xattr -d com.apple.quarantine liblovely.dylib`

### Game appears running but bridge is offline

The game process can survive a Lua crash. Check both:
```bash
# 1. Is process alive?
tasklist -FI "IMAGENAME eq Balatro.exe"     # Windows
pgrep -l Balatro                             # macOS

# 2. Is bridge responding?
curl http://127.0.0.1:7777/health
```

If process exists but bridge is offline, check the latest log in the lovely log directory for errors, then kill and relaunch the game.

## License

MIT
