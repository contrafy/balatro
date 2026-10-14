# Headless Engine

The real, unmodified Balatro game source runs headless under an embedded LuaJIT, with the frozen RL bridge
(`game_mod/BalatroRLBridge/main.lua`) as the only interface: the obs, `/legal`, validation, execution,
settled predicate and trajectory recorder are the bridge's own code, so headless observations are
byte-compatible with live GUI data (`docs/DATA_CONTRACT.md`). No display, audio or Steam is needed, and it runs
on Windows and Linux.

## Legal note

The game source is **user-supplied**: it is read at runtime from your own copy of `Balatro.exe` (a fused LOVE
executable, i.e. a zip archive) and extracted to a gitignored cache (`headless/.cache/`). It is never
committed, packaged or redistributed. Do not copy the cache directory anywhere public.

## Setup

Requirements: Python 3.10+, the repo's venv, `lupa` (ships LuaJIT 2.0 and 2.1 builds as wheels), and a copy of
Balatro (Steam, version `1.0.1o-FULL` was used for validation).

```bash
pip install -e "python[dev,headless]"      # adds lupa; run from the repo root
```

### Windows

The default Steam location `C:\Program Files (x86)\Steam\steamapps\common\Balatro\Balatro.exe` is found
automatically. Otherwise set `BALATRO_EXE`.

```bash
python/.venv/Scripts/balatro-headless extract     # optional: extract + print the cache dir
```

### Linux (cloud)

Copy `Balatro.exe` from your own install (the Windows build is fine; only its zip payload is read) to the
machine and point `BALATRO_EXE` at it. Steam for Linux/Proton installs under
`~/.steam/steam/steamapps/common/Balatro/` are also searched automatically.

```bash
export BALATRO_EXE=/path/to/Balatro.exe
python -m venv .venv && .venv/bin/pip install -e "python[dev,headless]"
.venv/bin/balatro-headless bench --workers 4 --steps 4000
```

`BALATRO_HEADLESS_CACHE` overrides the cache directory (default `headless/.cache`). Cache entries are keyed by
the exe's sha256, so a game update extracts into a new directory.

## Usage

```python
from balatro_env.headless import HeadlessEnv, HeadlessPool, random_legal_action

env = HeadlessEnv()                                   # boots to the unlocked main menu (~2.5 s)
obs, legal = env.reset(seed="7K3P9QXA", deck="b_black", stake=1)
obs, legal, done, info = env.step({"type": "SELECT_BLIND", "params": {}})
# illegal actions are rejected by the bridge without changing the game: info["ok"] False, info["error"]

with HeadlessPool(4) as pool:                         # one engine per process
    out = pool.reset([{"seed": s, "deck": "b_red", "stake": 1} for s in seeds])
    out = pool.step(actions)                          # [(obs, legal, done, info)] stepped in parallel
```

- `obs` is the bridge's `/state` without the envelope keys (`settled`, `settle_reason`, `timestamp_ms`, `step`,
  `trajectory`), i.e. exactly a recorded `step.obs`; `legal` is the `/legal` body.
- `done` is true at `GAME_OVER` or as soon as `G.GAME.won` is set (the data contract's `win`).
- Recording: `HeadlessEnv(record_dir=..., agent="...")` makes the bridge recorder write
  `<record_dir>/trajectories/<date>/<seed>_<port>_<ms>.jsonl.gz` in the DATA_CONTRACT format. The header is the
  bridge's own plus `"host": "headless"`; `lovely_version` is `headless-<version>` (the loader that replaces
  Lovely). Use an `agent` starting with `test-` for anything that is not training data.

### CLI

```bash
balatro-headless replay data/trajectories/2026-10-13/X.jsonl.gz ...   # files or directories
balatro-headless replay --manifest --workers 4                        # every replay_ok row of data/manifest.jsonl
balatro-headless bench --workers 4 --steps 4000                       # random legal policy throughput
```

`replay` runs the same comparison as `balatro-data replay` (it reuses `balatro_env.data.replay`'s diff code:
volatile keys dropped, entity ids relabeled by first appearance): at every step the headless obs and `/legal` must
equal the recorded ones, the recorded action must be accepted, the final obs must match, and the replay's own
recording must match the original step for step including `hidden` (draw order, face-down cards) and `refs`.
It prints `REPLAY_OK` or the first divergence with a JSON diff. Replay recordings go to a temp dir and are deleted.

## Architecture

```text
python (lupa)                          LuaJIT 2.0 state (one per process)
-------------                          -----------------------------------------------------------
HeadlessEnv / HeadlessPool             headless/lua/runtime.lua
  Engine.request("POST","/action") --> socket_stub: queue raw HTTP request
                                       bridge.update(dt) -> bridge server_tick: parse, route, handler,
                                                            json_encode, send  (unchanged bridge code)
  Engine.settle()                  --> love.update(dt) per frame (game main.lua + Lovely patch line)
                                       until the bridge's own settle_status() is true
```

- `headless/lua/love_stub.lua`: inert `love.graphics/window/audio/mouse/joystick/event` (objects are tables whose
  methods are no-ops), `love.thread` channels that drop messages (no save/sound threads), `love.filesystem` that
  reads the extracted source and keeps the save directory in memory, `love.data` (gzip/deflate/sha256 provided
  by Python), and `love.timer` as a virtual clock.
- `headless/lua/socket_stub.lua`: in-memory LuaSocket replacement. The bridge's server loop is fed raw HTTP
  requests and its responses are collected, so the bridge file runs verbatim (it is loaded from
  `game_mod/BalatroRLBridge/main.lua`; `bridge_hash` in headless headers equals the live one).
- `headless/lua/runtime.lua`: boot (`conf.lua`, `main.lua` with the exact `lovely.toml` patch applied, then
  `love.load`), fixed-dt frames, settle loop, request injection, and the header stamp `"host":"headless"`.
- `luasteam` is a stub (achievements are skipped anyway because the profile is `all_unlocked`).
- Profile: in-memory `settings.jkr` like the swarm instance template (GAMESPEED 4, tutorial complete,
  `skip_splash`); the bridge's own boot step unlocks and discovers everything, exactly as on live instances.

### Why lupa (embedded) rather than a LuaJIT binary over pipes

- Throughput: a request is a Lua function call plus one `json.loads`, with no pipe round trip, no process
  boundary per step and no second JSON parse. Per-step overhead is a small fraction of the game frames.
- Portability: `lupa` wheels bundle LuaJIT 2.0 and 2.1 for Windows, Linux and macOS (x86-64 and arm64), so
  `pip install` is the whole setup. A standalone LuaJIT binary would need building per platform plus
  bindings for zlib and sha256.
- Parallelism: one engine per process (`HeadlessPool`, `multiprocessing` pipes); the GIL is not a factor.

### Determinism

- The game ships **LuaJIT 2.0.5** (`lua51.dll`), and the headless default is lupa's `luajit20`. Balatro's
  `pseudorandom` reseeds `math.random` from `pseudohash`/`pseudoseed` (pure double arithmetic and `%.13f`
  formatting) before every logic draw. LuaJIT 2.0's `math.random` (Tausworthe) and string hashing (which decides
  `pairs` order) are what the live game uses. `lupa.luajit21` can be selected with `Engine(lua="luajit21")` but
  is not the validated configuration, and it measured slower on this codebase.
- Frame timing does not affect game logic: replays match at fixed `dt` from 1/60 s up to 0.1 s even though the
  live runs were recorded at variable real frame times. `dt` must stay <= 0.1 s (LOVE clamps its smoothed `dt`
  to 0.1). Larger steps make UI easing overshoot so the round-eval/shop slide-ins never converge (observed: stuck
  with `stop_use` at ROUND_EVAL with `dt=0.25`).
- Every settle runs at least one frame before the decision point is read, as on a live instance where every
  request is served after a full `G:update`. Per-frame derived state (Card:update: Blueprint/Brainstorm
  compatibility, Stone/Cloud 9 tallies, ...) is otherwise stale after actions that queue no events (REORDER).
- `love.timer.getTime` is a virtual clock (used only by `nuGC`'s per-frame GC budget and perf checkpoints).
  Garbage collection has no effect on game state (no weak tables or finalizers in the game).

## Validation status and performance

See the final section of this file (`Results`), updated whenever the engine changes.
