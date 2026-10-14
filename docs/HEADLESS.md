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

### Linux on this machine (WSL2)

Validated on Ubuntu 24.04 under WSL2 (Python 3.12.3, lupa 2.8), with its own venv (never the Windows
`python/.venv`) and its own source cache extracted from the Windows install through `/mnt/c`:

```bash
wsl                                                    # Ubuntu shell
python3 -m venv ~/venvs/balatro-headless
~/venvs/balatro-headless/bin/pip install --upgrade pip
# torch is a package dependency (balatro_env/__init__ imports it); the CPU wheel avoids the CUDA download
~/venvs/balatro-headless/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
~/venvs/balatro-headless/bin/pip install -e "/mnt/c/Users/contrafy/git/balatro/python[dev,headless]"

export BALATRO_EXE="/mnt/c/Program Files (x86)/Steam/steamapps/common/Balatro/Balatro.exe"
export BALATRO_HEADLESS_CACHE=$HOME/balatro-headless-cache   # Linux-side cache, not headless/.cache on /mnt/c
cd /mnt/c/Users/contrafy/git/balatro                         # data/manifest.jsonl is resolved from ./data
~/venvs/balatro-headless/bin/balatro-headless extract
~/venvs/balatro-headless/bin/balatro-headless replay --manifest --workers 3
~/venvs/balatro-headless/bin/balatro-headless bench --workers 4 --steps 8000
(cd python && ~/venvs/balatro-headless/bin/python -m pytest tests/test_headless.py -q)
```

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
    # asynchronous: pool.send(i, "step", action); for i in pool.ready(): result = pool.recv(i)
```

- `obs` is the bridge's `/state` without the envelope keys (`settled`, `settle_reason`, `timestamp_ms`, `step`,
  `trajectory`), i.e. exactly a recorded `step.obs`; `legal` is the `/legal` body.
- `done` is true at `GAME_OVER` or as soon as `G.GAME.won` is set (the data contract's `win`).
- Recording: `HeadlessEnv(record_dir=..., agent="...")` makes the bridge recorder write
  `<record_dir>/trajectories/<date>/<seed>_<port>_<ms>.jsonl.gz` in the DATA_CONTRACT format. The header is the
  bridge's own plus `"host": "headless"`; `lovely_version` is `headless-<version>` (the loader that replaces
  Lovely; `headless-1.1.0` since the fast path, with `+fastpath=<names|none>` appended when the engine runs a
  non-default fast-path set). Use an `agent` starting with `test-` for anything that is not training data.

### CLI

```bash
balatro-headless replay data/trajectories/2026-10-13/X.jsonl.gz ...   # files or directories
balatro-headless replay --manifest --workers 4                        # every replay_ok row of data/manifest.jsonl
balatro-headless bench --workers 4 --steps 4000                       # random legal policy throughput
balatro-headless bench --fastpath none                                # A/B: vanilla game source (or a name list)
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
- `headless/lua/fastpath.lua`: the fast path (next section), on by default: load-time source patches of the
  game modules plus runtime hooks that skip rendering-only work.
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

## Fast path

On by default (`Engine(fastpath=True)`, CLI `--fastpath all`); `fastpath=False` / `--fastpath none` runs the
unmodified game source, and a comma list enables single optimizations for A/B attribution. Implementation and
the per-item argument from the game source: `headless/lua/fastpath.lua`. Source patches are exact text
replacements applied when a game module is `require`d (like Lovely patches) and must match exactly once, so a
game update that changes patched code fails at boot instead of running unpatched.

What the game source guarantees (the basis for every skip):

- Rendering state: a moveable's visible transform `VT` and the easing that drives it (velocity, `STATIONARY`,
  juice, pinch, `sprite_facing`), UI layout (UIBox/UIElement/DynaText transforms, text metrics), particles and
  sprite animation frames. The game reads `VT` outside draw/move code only at: the shop and round-eval slide-in
  gates (`game.lua:3090,3326`, on `G.shop`/`G.round_eval`), the booster gate on `G.pack_cards.VT.y`
  (`card.lua:1787`), `Card:update`'s flip (`VT.w`, sets `sprite_facing`/`pinch`, both rendering-only),
  `blind_choice_handler` (UI styling) and the initial position of card popups/buttons (UI).
- Positions (`T`) reach game state only through cards: `CardArea:align_cards` sorts `area.cards` by `T.x`,
  which includes `card.shadow_parrallax.x/30` (computed by the card's own move). Cursor collision never happens
  headless: `G.DRAW_HASH` is filled only by draw functions, so `Controller:get_cursor_collision` returns at its
  `not G.DRAW_HASH[1]` guard, and there is no input.
- The bridge reads no transform, no UI button state (it computes legality itself) and no display-text fields.

| name | what it does | why the game state is unchanged |
|---|---|---|
| `nojit` | `jit.off()`: LuaJIT 2.0 as a pure interpreter | The hot code is `pairs` loops and closures (ITERN/FNEW are NYI in 2.0), so traces abort and are retried forever; interpreter and JIT compute the same IEEE doubles |
| `moves` | The per-frame move pass visits a maintained list (in `G.MOVEABLES` order) of Cards, CardAreas, `Card_Character` and the two gate UIBoxes; sprites, card shadows, UI elements/boxes/text, blinds and particles are no longer moved. The update pass visits a maintained list without classes whose `update` is the empty `Node.update` | Skipped moves only write rendering state; a kept object whose `role.major` is skipped still moves it on demand (`Moveable.move`), so `G.pack_cards` and every card/area transform is computed as before. The move pass creates/removes nothing, so the sublist walk equals the stock walk; if an update removes moveables, the update pass resumes as the stock `pairs` loop would, from the key reconstructed from a removal log |
| `cardmove` | A Major card's move without `move_juice/xy/r/scale/wh` | Those only write `VT`, velocity, `STATIONARY`, juice; the frame bookkeeping, `align_to_major`, `calculate_parrallax` (same expression) and `lr_clamp` still run |
| `uiupdate` | No `DynaText:update`, `Particles:update`, sprite animation, background-spin easing; `UIElement:update` only for elements whose `func` is not in an audited rendering-only list (17 HUD/button funcs) | Text metrics, particles, animation frames and the spin are rendering; the listed funcs write UI config, UI boxes, display-only `*_text` fields, `G.GAME.blind.states.visible`, flame shader state; unlisted funcs still run |
| `cardupdate` | One name lookup guards `Card:update`'s run of `if self.ability.name == ...` blocks | The guarded names are extracted from the patched source at load, which also checks that every top-level statement of the run is such a name test |
| `remove` | Instance-list removal searches from the end; `G.STAGE_OBJECTS` keeps a membership hint | The lists are dense arrays with each object at most once, so the match is the stock index; the hint is a superset (fixes the O(n^2) `remove_all` at every run reset) |
| `gc` | `nuGC` = full collection above 64 MB instead of ~3 incremental steps per frame | No weak tables or finalizers in the game or bridge |

Known differences from the unmodified source (none observable through the bridge): rendering state is stale;
UI objects that only rendering-only funcs create or remove (the HUD flame sprite, high-score alerts) are not
created/removed, so `G.MOVEABLES` holds slightly different UI objects; trajectories record the same `obs`,
`/legal`, `hidden` and `refs` (replay gate, `test_fastpath_matches_vanilla`).

## Results (2026-10-14, game 1.0.1o-FULL, bridge_hash cd4ee1e6…)

Fidelity:

- `balatro-headless replay --manifest` (fast path on): **100%** of `replay_ok` trajectories match at every step
  (obs, `/legal`, final obs, and the replay's own recording incl. `hidden`/`refs`): 65/65 (4220 steps; fuzzer,
  rule agent and swarm runs) on Windows and 66/66 (4338 steps) on Linux (WSL2) on the final code. The gate was
  re-run after every optimization (31 -> 66 files as the swarm added runs) and never dropped below 100%.
- Before the fast path: all 123 manifest rows (`--manifest-all`, including runs never live-replayed): 121/123
  match. The two misses are `tainted` bridge test runs that used `/debug/eval` state surgery (`schema_ok=false`,
  non-replayable by design).
- Reverse direction: runs recorded headless (`host:"headless"`) pass `balatro-data validate` and replay with
  `REPLAY_OK` on a live GUI instance through `balatro-data replay` (3/3, 25-81 steps, shops and packs).
- Root-caused divergence found during bring-up: Brainstorm's `ability.blueprint_compat` after a joker
  `REORDER` (computed in `Card:update`). Fix: every settle runs at least one frame (see Determinism).

Throughput (`balatro-headless bench`, random legal policy incl. resets, `dt=0.1`, Ryzen 7 9700X 8C/16T with the
10-instance GUI swarm running on the same machine, so absolute numbers are noisy by ~±5%). One worker, each row
adds one optimization (`--fastpath` list), Windows:

| fast path | steps/s | frames/step | frames/s |
|---|---|---|---|
| none (unmodified source, JIT on) | 46.3 | 24.0 | 1111 |
| `nojit` | 52.6 | 24.0 | 1262 |
| + `moves` | 91.7 | 23.9 | 2193 |
| + `cardmove` | 101.0 | 23.9 | 2414 |
| + `uiupdate` | 157.5 | 23.9 | 3764 |
| + `cardupdate` | 160.4 | 23.9 | 3834 |
| + `remove` | 163.5 | 23.9 | 3908 |
| + `gc` (= all, default) | 176.9 | 23.9 | 4229 |

Before/after, steps/s total (per worker):

| host | workers | none | all |
|---|---|---|---|
| Windows 11 | 1 | 46.3 | 176.9 |
| Windows 11 | 4 | 187.2 (46.8) | 705.9 (176.5) |
| WSL2 Ubuntu 24.04 | 1 | 36.5 | 143.7 |
| WSL2 Ubuntu 24.04 | 4 | 105.0 (26.2) | 438.2 (109.5) |

With the JIT on, the fast path reaches only ~136 steps/s (one worker): `nojit` matters more once the frame is
cheap. The 300 steps/s per core target is not reached (~3.8x over the unmodified source). Where a step goes now
(one worker, ~5 ms):

- ~3.7 ms in ~24 frames (~0.15 ms each). Per frame the largest items are the event queue itself (the game
  logic plus the UI it builds: `UIBox` construction and layout inside events, ~30%), the ~52 deck cards
  (`CardArea:align_cards` positions and flips them every frame, `Card:update`, the card move; ~25%), and GC
  (~10%). These are game semantics or feed card order, so they stay.
- ~0.85 ms in `/state` (the bridge's `build_obs` + its Lua JSON encoder, ~8 KB per step; frozen code), ~0.25 ms
  in `/action` and `/legal`, ~0.2 ms in Python.
- Frames per decision cannot drop without changing event semantics. Over 12.7k frames of random play, 55%
  complete a blocking event; most others are the second frame of a `before`/`after` event: `EventManager:update`
  sets `blocked` after handling any blocking event, completed or not, so an event that waits on its timer holds
  the queue for the frame in which it completes. A clock-skipping prototype (after an observed inert frame,
  advance every timer exactly as the skipped `Game:update` calls would, up to the frame in which the first
  waiting event is due) passed the replay gate but skipped 49 of 12.7k frames (0.4%): at GAMESPEED 4,
  `TIMERS.TOTAL` advances 0.4 s per 0.1 s frame, so almost every wait is due on the next frame, and the long
  waits (the 1.2 s run-start screenwipe) overlap with easing and polling events. It was removed.
