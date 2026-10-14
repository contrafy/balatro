# Balatro RL Python Harness

Python package for driving Balatro through the in-game bridge: HTTP client, schemas, advisor CLI, a Gymnasium-compatible environment, and a rule-based baseline agent. The Gymnasium env is existing tooling; model training will run in a headless engine (see [../docs/TRAINING_PLAN.md](../docs/TRAINING_PLAN.md)).

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install the package
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Prerequisites

The Balatro game must be running with the RL Bridge mod loaded. See `../game_mod/install.md` for setup instructions.

## Quick Start

### 1. Verify Connection

```bash
# Check if bridge is running
python -m balatro_env.scripts.probe_health
```

### 2. Explore Game State

```bash
# Dump current state
python -m balatro_env.scripts.dump_state

# List legal actions
python -m balatro_env.scripts.list_legal_actions
```

### 3. Interactive Shell

```bash
# Start interactive session
python -m balatro_env.scripts.interactive_shell
```

Commands:
- `state` / `s` - Show current game state
- `legal` / `l` - Show legal actions
- `play 1 2 3` - Play cards at indices 1, 2, 3
- `discard 1` - Discard card at index 1
- `reroll` - Reroll shop
- `endshop` - Leave shop
- `quit` / `q` - Exit

### 4. Smoke Test

```bash
# Execute safe test actions
python -m balatro_env.scripts.do_smoke_actions
```

## Using the Environment

```python
import gymnasium as gym
from balatro_env import BalatroEnv

# Create environment
env = BalatroEnv(host="127.0.0.1", port=7777)

# Reset and get initial observation
obs, info = env.reset()

# Get action mask for legal actions
action_mask = env.get_action_mask()

# Sample a legal action
action = env.sample_legal_action()

# Take a step
obs, reward, terminated, truncated, info = env.step(action)

# Render state (optional)
env.render()

# Clean up
env.close()
```

## Using the Client Directly

```python
from balatro_env import BalatroClient
from balatro_env.schemas import ActionRequest, ActionType

# Create client
client = BalatroClient()

# Check health
health = client.health()
print(f"Bridge version: {health.version}")

# Get state
state = client.get_state()
print(f"Phase: {state.phase}, Money: ${state.money}")

# Get legal actions
legal = client.get_legal_actions()
for action in legal.actions:
    print(f"  {action.type}: {action.description}")

# Execute an action
action = ActionRequest(
    type=ActionType.PLAY_HAND,
    params={"card_indices": [1, 2, 3]}
)
result = client.execute_action(action)
if result.ok:
    print("Action succeeded!")
```

## Project Structure

```
python/
├── balatro_env/
│   ├── __init__.py       # Package exports
│   ├── client.py         # HTTP client for bridge
│   ├── env.py            # Gymnasium environment
│   ├── schemas.py        # Pydantic data models
│   ├── action_space.py   # Action encoding/decoding
│   ├── obs_tokenizer.py  # State to tensor conversion
│   ├── vocab.py          # Stable id vocabularies (center keys) for the tokenizer
│   ├── util.py           # Display utilities
│   ├── data/             # Trajectory tooling: `balatro-data` CLI (see below)
│   │   └── eval_seeds.txt  # 500 held-out eval seeds: never play them for data
│   └── scripts/
│       ├── probe_health.py
│       ├── dump_state.py
│       ├── list_legal_actions.py
│       ├── do_smoke_actions.py
│       └── interactive_shell.py
├── tests/
│   ├── fixtures/trajectories/  # hand-written trajectory fixtures
│   ├── test_data_tooling.py    # offline: validator, manifest, legality, seeds
│   ├── test_health.py
│   ├── test_state_schema.py
│   └── test_legal_actions.py
├── pyproject.toml
└── README.md
```

## Trajectory Data Tooling

Recorded runs (format in [../docs/DATA_CONTRACT.md](../docs/DATA_CONTRACT.md)) are checked with
`balatro-data` (data root: `--data-dir`, else `$BALATRO_RL_DATA_DIR`, else `./data`):

```bash
balatro-data validate                    # schema + legality + hidden-info check of every trajectory
balatro-data manifest                    # rewrite data/manifest.jsonl
balatro-data replay <file> --port 7779 --update-manifest   # live replay verification (idle instance)
balatro-data fuzz --port 7779 --runs 5 --steps 400         # live legality fuzzer on FUZZ* seeds
balatro-data seeds --count 10            # training seeds (never eval or fuzz seeds)
```

## Running Tests

```bash
# Run all tests (requires Balatro running)
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py -v
```

## API Reference

### BalatroClient

| Method | Description |
|--------|-------------|
| `health()` | Check bridge health |
| `get_state()` | Get current game state |
| `get_legal_actions()` | Get available actions |
| `execute_action(action)` | Execute an action |
| `reset(seed)` | Reset game (may require manual intervention) |

### BalatroEnv (Gymnasium)

| Method | Description |
|--------|-------------|
| `reset()` | Reset environment |
| `step(action)` | Execute action, return (obs, reward, term, trunc, info) |
| `render()` | Display current state |
| `get_action_mask()` | Get boolean mask of legal actions |
| `sample_legal_action()` | Sample a random legal action |

### Game Phases

- `MENU` - Main menu
- `SELECTING_HAND` - Choosing cards to play/discard
- `HAND_PLAYED` - Hand being scored
- `SHOP` - In the shop between rounds
- `BLIND_SELECT` - Choosing which blind to play
- `PACK_OPENING` - Selecting cards from a booster pack

### Action Types

Each `/legal` entry is `{type, description?, params, info}`: `params` maps every parameter
to its domain (`one_of`, `subset`, `permutation`, `seed`), `info` carries cost/name/key.
See `docs/DATA_CONTRACT.md` for the full contract.

- `START_RUN` - Start a run (`deck`, `stake`, optional `seed`)
- `SELECT_BLIND` / `SKIP_BLIND` / `REROLL_BOSS` - Blind selection
- `PLAY_HAND` - Play cards (`card_indices`)
- `DISCARD` - Discard cards (`card_indices`)
- `REORDER` - Reorder `hand`, `jokers` or `consumables` (`area`, `order`)
- `SORT_HAND` - Sort hand (`mode`)
- `USE_CONSUMABLE` - Use a consumable (`index`, `targets` for targeted tarots/spectrals)
- `SELL_JOKER` / `SELL_CONSUMABLE` - Sell a joker/consumable (`index`)
- `CASH_OUT` - Collect round rewards
- `SHOP_BUY` / `SHOP_BUY_AND_USE` - Buy (and use) a shop card (`slot`)
- `SHOP_BUY_VOUCHER` / `SHOP_BUY_BOOSTER` - Buy a voucher/booster (`slot`)
- `SHOP_REROLL` - Reroll shop
- `SHOP_END` - Leave shop
- `SELECT_PACK_CARD` - Choose pack card (`index`, `targets` when it needs hand cards)
- `SKIP_PACK` - Skip pack selection
