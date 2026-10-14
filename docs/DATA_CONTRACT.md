# Trajectory Data Contract

Every game played through the bridge (LLM swarm, rule agent, fuzzer, future model) produces a trajectory
that must be usable later for behavior cloning, simulator validation, and evaluation. This file is the
contract between the bridge (`game_mod/BalatroRLBridge`), the clients (`cli.py`, tooling), and training code.
Change it only together with `format_version`.

## Invariants

1. **Vanilla game logic.** The bridge loads through Lovely only; no Steamodded. The mod's only Lovely patches are
   its loader (`lovely.toml`: register `main.lua` as a module, call it from `love.update`); none touch game rules.
2. **Every recorded action was legal.** The bridge validates each `/action` against `get_legal_actions()` for the
   current decision point (type *and* params) and against the game's own `can_*` checks before executing.
   Anything else is rejected and recorded as a `reject` line, never executed.
3. **Actions only at decision points.** An action is accepted only when the game is *settled*: phase is a
   decision phase, `G.STATE_COMPLETE`, no blocking events pending, controller not locked. Otherwise
   `{ok:false, retry:true}`. The `obs` recorded with a step is therefore a stable decision state.
4. **Replayable.** `(game_version, bridge_hash, seed, deck_key, stake, action sequence)` fully determines the
   trajectory. The replay verifier must reproduce every `obs` exactly; runs that fail replay are quarantined.
5. **Full unlocks.** Harness profiles are fully unlocked/discovered; the header records a check (count of locked
   or undiscovered centers = 0). Runs without it are invalid.
6. **No hidden information in `obs`.** Draw-pile order, face-down card/joker identities, seed, and future RNG go in
   `hidden`, never in `obs`.

## Action API (`POST /action`)

```json
{"type": "PLAY_HAND", "params": {"card_indices": [1, 3, 4]},
 "meta": {"why": "Two Pair, est 412 > 300 needed", "agent": "swarm-7778", "model": "claude-...", "client": "cli.py@<sha>"}}
```

`meta` is opaque to the game and stored verbatim on the step. `meta.why` is required by `cli.py` for every
state-changing command. Indices are 1-based positions in the current area, left to right.

| type | params | phases |
|---|---|---|
| `START_RUN` | `deck` (key or name), `stake` 1-8, `seed` (optional; if absent the bridge generates one and still starts a *seeded* run so originals and replays take the identical code path) | MENU, GAME_OVER, WIN (see below for mid-run) |
| `SELECT_BLIND` | none (selects the blind on deck) | BLIND_SELECT |
| `SKIP_BLIND` | none (Small/Big only) | BLIND_SELECT |
| `REROLL_BOSS` | none (Director's Cut once per ante / Retcon; $10 vs `money - bankrupt_at`) | BLIND_SELECT |
| `PLAY_HAND` | `card_indices` (1..min(5, highlight limit), must include a Cerulean Bell forced card) | SELECTING_HAND |
| `DISCARD` | `card_indices` (1..highlight limit, forced card included; only while discards remain) | SELECTING_HAND |
| `REORDER` | `area` = `hand`/`jokers`/`consumables`, `order` = permutation of current positions (`order[k]` = old position of the card that ends up at position k) | jokers/consumables: every in-run decision phase (≥2 cards); hand: SELECTING_HAND and packs that show the hand |
| `SORT_HAND` | `mode` = `rank`/`suit` | SELECTING_HAND |
| `USE_CONSUMABLE` | `index`, `targets` (hand positions; count within the card's min..max) | every in-run decision phase where `can_use_consumeable` passes |
| `SELL_JOKER` | `index` (`can_sell_card`: not eternal) | every in-run decision phase |
| `SELL_CONSUMABLE` | `index` | every in-run decision phase |
| `CASH_OUT` | none | ROUND_EVAL |
| `SHOP_BUY` | `slot` (shop_jokers area: jokers, consumables, playing cards; needs buy space) | SHOP |
| `SHOP_BUY_AND_USE` | `slot`, `targets` (consumables only; no slot needed; `can_use_consumeable`) | SHOP |
| `SHOP_BUY_VOUCHER` | `slot` | SHOP |
| `SHOP_BUY_BOOSTER` | `slot` | SHOP |
| `SHOP_REROLL` | none | SHOP |
| `SHOP_END` | none | SHOP |
| `SELECT_PACK_CARD` | `index`, `targets` (consumables: `can_use_consumeable`; jokers: free slot or negative) | PACK_OPENING |
| `SKIP_PACK` | none (Arcana/Spectral only once the hand is drawn) | PACK_OPENING |

In-run decision phases: BLIND_SELECT, SELECTING_HAND, SHOP, PACK_OPENING, ROUND_EVAL. Other phase names
(`HAND_PLAYED`, `DRAW_TO_HAND`, `NEW_ROUND`, `PLAY_TAROT`, `SPLASH`, `STATE_<n>`) are transitional. `WIN` is the
win overlay after the ante-8 (`win_ante`) boss.

Affordability uses `money - bankrupt_at` (Credit Card). `UNLOCK_ALL` and other debug/admin calls are not
actions: they are never legal, never recorded, and only run at instance setup (the bridge unlocks/discovers
everything and marks the tutorial done once per boot, before the menu reports settled). Highlighting cards is
not an action: targets are params of the action that consumes them.

**START_RUN mid-run.** START_RUN is listed in `/legal` only at MENU, GAME_OVER and WIN. At any other *settled*
point it is accepted as an admin restart: the open trajectory gets `end` with `outcome:"abandoned"` and a new one
starts. START_RUN is never a step line; its canonical params and meta are the new file's `start_params` /
`start_meta`. Canonicalization: `deck` name → key (`"Black Deck"` → `"b_black"`, default `b_red`), `stake`
default 1, `seed` upper-cased or generated (8 chars of `1-9A-NP-Z`). The bridge sets
`G.GAME.viewed_back = Back(P_CENTERS[deck])` (vanilla `start_run` reads the deck from there) and runs the same
steps as `G.FUNCS.start_run(nil, {stake, seed})`, plus `G.sort_id = 0` right before `G:start_run` so entity ids
are per-run and identical between an original and its replay. Seeded runs skip vanilla career stats/unlocks only.

Response: `{ok, error?, retry?, step?}` (`step` = index of the recorded step; START_RUN returns
`{ok, params, trajectory_path, recorder_ok}`). `retry:true` only for "not settled"; the action was not executed.
Clients poll `/state` until `settled == true` before deciding again.

## `GET /legal`

```json
{"schema_version":"2.0.0", "phase":"SELECTING_HAND", "settled":true, "settle_reason":null,
 "actions":[
  {"type":"PLAY_HAND", "params":{"card_indices":{"subset":{"of":[1,2,3,4,5,6,7,8],"min":1,"max":5,"must_include":[8]}}}},
  {"type":"USE_CONSUMABLE", "params":{"index":{"one_of":[1]}, "targets":{"subset":{"of":[1,2,3,4,5,6,7,8],"min":2,"max":2}}},
   "info":{"key":"c_death","name":"Death"}},
  {"type":"REORDER", "params":{"area":{"one_of":["hand"]}, "order":{"permutation":8}}},
  {"type":"SELL_JOKER", "params":{"index":{"one_of":[2]}}, "info":{"key":"j_golden","name":"Golden Joker","sell_value":3}}]}
```

- When not settled: `settled:false`, `settle_reason` set, `actions:[]`.
- `params` maps each param name to exactly one domain kind:
  - `{"one_of":[v...]}`: scalar from the set (indices are 1-based ints).
  - `{"subset":{"of":[i...],"min":a,"max":b,"must_include":[i...]?}}`: list of distinct ints from `of`, length in
    `[a,b]`, containing every `must_include` (Cerulean Bell forced card).
  - `{"permutation":n}`: list that is a permutation of `1..n`.
  - `{"seed":true}`: 1-8 chars `[0-9A-Z]`.
  - Any domain may carry `"optional":true` (only START_RUN `seed`).
- A type may appear in several entries. Indexed actions (SELL_*, USE_CONSUMABLE, SHOP_*, SELECT_PACK_CARD)
  get one entry per legal index; REORDER one entry per area. Nullary actions have `params:{}`.
- An action is legal iff it matches **any** entry of its type: every listed param matches its domain (or is
  optional and absent), and every param not listed is absent (an empty list counts as absent).
- `info` is advisory (key, name, cost, sell_value, blind, dollars); never validated. Face-down cards show only
  `{facing:"back"}` in `info`.
- Targets: cards with `max_highlighted` use `min_highlighted or 1 .. mod_num` over all hand positions; Aura is
  exactly 1 over hand cards without an edition. Targeted cards are only usable while the hand is out
  (SELECTING_HAND, Arcana/Spectral/Celestial pack states), as in vanilla.
- Validation runs against this list built at the moment the action arrives; after validation the executor
  also re-checks `can_use_consumeable()` with the targets highlighted, and rejects (not executes) on failure.

## Settled

`settled` (in `/state` and `/legal`) is true iff, for phase:

- MENU: profile unlock done, `G.MAIN_MENU_UI` present, no screen wipe.
- GAME_OVER: `G.STATE_COMPLETE` and the game-over overlay is up, no screen wipe. WIN: win overlay up.
- In-run decision phases: `G.STATE_COMPLETE`; no screen wipe, no overlay, not paused; no truthy
  `G.CONTROLLER.locks.*`; `G.GAME.STOP_USE == 0`; `G.play` empty; no `G.TAROT_INTERRUPT`; no event in
  `G.E_MANAGER.queues.base` with `blocking and not complete`; and the phase UI exists (BLIND_SELECT:
  `G.blind_select` + `blind_on_deck`; SELECTING_HAND: `G.buttons`, hand non-empty, boss `block_play` cleared;
  SHOP: shop areas; ROUND_EVAL: `G.round_eval`; PACK_OPENING: `G.booster_pack`, pack cards all face-up and not
  flipping, Arcana/Spectral hand drawn).

These mirror the vanilla button guards (`can_use_consumeable`, `can_sell_card`, controller locks), so anything a
human could click at that moment is in `/legal`, and nothing fires mid-animation. `settle_reason` names the
first failing condition (e.g. `events_pending`, `lock:use`, `stop_use`).

## `GET /state` (obs)

`/state` = obs + envelope keys `settled`, `settle_reason`, `timestamp_ms`, `step` (next step index of the open
trajectory), `trajectory` (current or last file). `step.obs` = `/state` minus those keys. Absent key = null.
All entities carry a stable `id` (= `sort_id`) and their 1-based `index`; face-down entities (`facing:"back"`)
carry only `index`/`facing` (hand cards also `highlighted`/`forced`): no identity and no `id`.

- Run: `phase, schema_version, deck_key, deck_name, deck_config, stake, won, win_ante, round, ante, money,
  chips` (this round's score, still set in ROUND_EVAL), `hands_remaining, discards_remaining, hands_per_round,
  discards_per_round, hand_size, highlight_limit, joker_slots, consumable_slots, interest_amount, interest_cap,
  no_interest, modifiers, starting_params, shop_rates, used_vouchers[], tags[{key,name,orbital_hand}]`.
- `run`: `skips, hands_played_total, round_hands_played, discards_used, unused_discards,
  consumeable_usage_total, last_tarot_planet, starting_deck_size, bankrupt_at, free_rerolls, reroll_cost,
  boss_rerolled, round_dollars` (cash-out total), `previous_round_dollars, jokers_purchased, inflation,
  discount_percent, probabilities_normal, most_played_poker_hand, idol_card{rank,suit}, mail_card{rank},
  ancient_card{suit}, castle_card{suit}, joker_buffer, ecto_minus`.
- `blind` (while a blind is set): `key, name, boss, chips_needed, chips_scored, dollars, disabled,
  effect_text` (`get_loc_debuff_text()`), `hands_used` (The Eye), `only_hand` (The Mouth), `target_hand` (The Ox).
- `blind_select` (every in-run phase): `on_deck, boss_rerolled, choices.{Small,Big,Boss}:{key, name, boss,
  chips, dollars, state, tag_key, tag, orbital_hand}`.
- `hand[]`: `index, facing, highlighted, forced, id, rank, suit, enhancement` (center key, e.g. `m_glass`),
  `edition` (`foil|holo|polychrome|negative`), `seal, perma_bonus, debuff`.
- `jokers[]`: `index, facing, id, key, name, rarity, edition, sell_cost, debuff, eternal, perishable,
  perish_tally, rental, pinned, ability{...}`. `consumables[]`: `index, facing, id, key, name, set, edition,
  sell_cost, debuff, ability{...}`.
- `shop` (SHOP): `{jokers[], vouchers[], boosters[], reroll_cost}`; item = `index, cost, facing, id, key, name,
  set, edition` + playing cards `rank, suit, enhancement, seal, perma_bonus`; jokers `rarity, sell_cost, ability`,
  stickers; boosters `kind, size, choose`; consumables `ability`.
- `pack` (PACK_OPENING): `{kind (Arcana|Celestial|Spectral|Standard|Buffoon), size, choices_remaining, cards[]}`
  (item shape without `cost`).
- `deck` (View Deck): `total, draw_pile, discard_pile, remaining, remaining_by_suit, remaining_by_rank,
  remaining_face_cards, cards[{id, rank, suit, enhancement, edition, seal, perma_bonus, remaining}]` sorted by id.
  `remaining` follows vanilla's "Remaining" view: in the draw pile, or face-down in hand (`wheel_flipped`).
- `hand_levels`: `{<hand>: {level, chips, mult, played, played_this_round, visible}}`.

`hidden` (trajectory only): `seed`, `draw_order` (ids, next-drawn first), `face_down[{area, index, id, key, set,
name, rank, suit, edition, seal}]` for face-down cards in hand/jokers/consumables/pack/shop.

## `POST /preview`

`{card_indices:[1..5 distinct hand positions]}` → `{ok, hand, display, scoring[], level, chips, mult,
blind_debuffed}`: `hand` = `G.FUNCS.get_poker_hand_info` hand name (`display` e.g. "Royal Flush"), `scoring` =
hand positions that score (Stone cards and Splash included as in `evaluate_play`), `level/chips/mult` = that
hand's current level values (no jokers), `blind_debuffed` = the boss would not score it. If a face-down card is
selected: `{ok:true, hand:null, hidden:true}` (vanilla shows `????`). Never mutates game state (blind
`triggered` and `G.boss_throw_hand` are restored), never recorded.

## `GET /health`

`status, version, bridge_version, bridge_hash, game_version, lovely_version, git_sha, port, uptime_ms,
request_count, error_count, last_error, unlocked, data_dir, recorder_ok, recorder_error, recorder_error_count,
trajectory_open, trajectory_path, trajectory_steps`. Recorder failures (cannot open/write/gzip, data dir unset)
never stop the game; they set `recorder_ok:false` and `recorder_error`.

## Files

One JSONL file per run: `<BALATRO_RL_DATA_DIR>/trajectories/<YYYY-MM-DD>/<seed>_<port>_<epoch_ms>.jsonl`.
`BALATRO_RL_DATA_DIR` is the data root (`launch_instance.ps1` sets `<repo>\data`, gitignored); if unset the bridge
records nothing and `/health` shows `recorder_ok:false`. The recorder lives in the bridge: every line is written
and flushed immediately (a crash loses at most the in-flight step). When the run ends the bridge gzips the file in
place (`love.data.compress("string","gzip")` → `<name>.jsonl.gz`, then deletes the `.jsonl`); if that fails the
`.jsonl` stays and `recorder_error` says why. A `.jsonl` without an `end` line is a crashed/interrupted run.
JSON objects are written with sorted keys; integers without exponent. Line types:

```text
{"t":"header", "format_version":1, "schema_version", "bridge_version", "bridge_hash", "git_sha", "game_version",
 "lovely_version", "seed", "deck_key", "stake", "start_params":{"deck","stake","seed"}, "start_meta":{...},
 "unlocks": {"locked":0, "undiscovered":0}, "port", "started_at_ms"}
{"t":"step", "i", "ts_ms", "obs":{...}, "hidden":{...}, "legal":{...}, "action":{"type","params"},
 "refs":{...}, "meta":{...}, "result":{"ok":true}}
{"t":"reject", "i", "ts_ms", "phase", "action":{"type","params"}, "meta":{...}, "error":"...", "retry"?:true}
{"t":"debug", "i", "ts_ms", "lua", "ok"}
{"t":"end", "outcome":"win|loss|abandoned", "ante", "round", "steps", "tainted"?:true, "final_obs":{...}, "ts_ms"}
```

- `i` on a step is contiguous from 0; on `reject`/`debug` it is the index the next step will get.
- `obs`, `legal`, `hidden` are captured at the settled decision point, before the action executes; `legal` is
  exactly the `/legal` body the action was validated against. `action.params` are canonical (what was executed).
- `refs`: stable ids (`sort_id`) for indexed params: `card_indices`/`targets` (hand), `index` (jokers,
  consumables or pack, by action type), `slot` (shop area by action type), `order` (ids in the new order).
- `result.ok:false` on a step means the game function threw after validation (bridge bug): quarantine the run.
  Refusals by the game's own re-check are `reject` lines, not steps.
- `bridge_hash` = hex sha256 of the deployed `main.lua` bytes followed by `lovely.toml` bytes (as in the repo,
  CRLF included). `git_sha` comes from `BALATRO_RL_GIT_SHA` (launcher: `git rev-parse HEAD`, `-dirty` suffix if
  the tree has changes). `lovely_version` from `require("lovely").version`, `game_version` = `G.VERSION`.
- `unlocks` counts `unlocked == false` / `discovered == false` over P_CENTERS, P_BLINDS, P_TAGS, P_SEALS.
- Outcomes: `loss` when the state becomes GAME_OVER; `win` as soon as `G.GAME.won` is set (ante-`win_ante` boss
  beaten; `final_obs` may be mid-transition); `abandoned` when START_RUN arrives mid-run. Continuing into Endless
  is not supported (no action) and not part of the training target.
- `debug` lines and `tainted:true` come only from `POST /debug/eval`, which exists only on instances launched
  with `-DebugEval` (`BALATRO_RL_DEBUG=1`) for bridge tests. Tainted runs are never training data.

## Validity pipeline

`data/manifest.jsonl` has one row per trajectory: path, seed, deck, stake, outcome, steps, `bridge_hash`,
`schema_ok`, `replay_ok`, `quarantined_reason`. Only rows with `schema_ok && replay_ok` feed training.

## Dataset tooling

`python/balatro_env/data/` implements the checks above; CLI `balatro-data` (or `python -m balatro_env.data`),
data root `--data-dir`, else `$BALATRO_RL_DATA_DIR`, else `./data`.

| command | what it does |
|---|---|
| `balatro-data validate [paths...]` | Schema + legality check per file: header first with versions, seed and `unlocks` all 0; `step.i` contiguous, `ts_ms` monotonic; every step has `result.ok`, a settled `legal`, and an action inside that `legal` (domain check re-implemented in `data/legality.py`); no hidden keys (`seed`, `run_id`, `draw_order`, `face_down`, ...), no seed string, no identity on `facing:"back"` entities anywhere in `obs`/`final_obs`; `end.steps` matches; nothing after `end`. A truncated last line is an error; a missing `end` line only marks the run `abandoned`. Exit 1 on any invalid file. |
| `balatro-data manifest` | Rewrites `<data>/manifest.jsonl` (one row per run under `<data>/trajectories/`, keyed by `run_key` = file name without `.jsonl[.gz]`). Extra columns: `run_key`, `ante`, `rejects`, `format_version`, `bridge_version`, `game_version`, `agent` and `replay_of` (from `start_meta`), `schema_error`, `schema_warnings`, `replay_detail`, `file_size`/`file_mtime_ns` (lets `dataops` skip re-validating unchanged files). Replay verdicts from earlier runs are kept while `bridge_hash` and `steps` are unchanged. |
| `balatro-data replay <paths...> --port P [--update-manifest]` | On an idle instance: `START_RUN` with `header.start_params` and `meta.replay_of = <run_key>`, then at every step waits for `settled`, diffs live `/state` and `/legal` against the recorded `obs`/`legal` (drops `timestamp_ms`/`ts_ms`/`settled`/`step`/`trajectory`; entity ids compared after relabeling by first appearance), resends the recorded action, and finally compares `final_obs`. When the replay's own recording is closed it also diffs it step by step against the original, including `hidden`. Prints `REPLAY_OK` or the first divergence with a JSON diff. |
| `balatro-data fuzz --port P --runs N --steps M` | Legality fuzzer on `FUZZ*` seeds: at each settled point sends up to 6 illegal probes (each must be rejected without changing `/state` or `/legal`; `START_RUN` is never probed since mid-run it is an admin restart), then one action sampled from the full legal domain that must be accepted. Light bias so runs reach shops and later antes: type weights, 85% greedy best poker hand (or a flush/pair-seeking discard when the hand is too weak) when `PLAY_HAND` is legal, 60% joker buy in the shop when one is legal, half the runs at the lowest stake. Watches `/health` `error_count`, liveness, settle timeouts (`stuck`), and the instance's Lovely log for `ERROR`. Report JSON in `<data>/fuzz/`. |
| `balatro-data compress [--include-superseded] [--include-unfinished --min-age-s S]` | Gzips finished `.jsonl` files (verified line count, then removes the original). `--include-superseded` also closes end-less files whose port already has a newer trajectory (crashed/interrupted runs; the bridge keeps one open file per instance). |
| `balatro-data seeds --count N` / `--check SEED` | Fresh training seeds / reserved-seed check. |
| `balatro-data status [--print]` | Regenerates the block between `<!-- AUTO:BEGIN -->` / `<!-- AUTO:END -->` in `docs/SWARM_STATUS.md` (everything outside is kept; the file is created with *Morning summary* / *Orchestrator log* sections if missing): live runs, results per model x stake x deck (runs, wins, mean/max ante), 10 deepest runs with post-mortem links (`docs/runs/<port>_<seed>.md`), manifest validity counts and quarantine reasons, rejects per agent. Model = `meta.model` of the steps (post-mortem title as fallback). Excludes `FUZZ*` seeds, `test-*` agents, replays and debug-tainted runs. A run is *live* while it is its port's newest file, has no `end` line and was written in the last 30 min. Per-file summaries are cached in `<data>/.status_cache.json` (by size + mtime). |
| `balatro-data dashboard [--port 8765]` | Stdlib-only local web page (auto-refresh, no external assets): live runs (phase, ante, round, money, blind progress, jokers, last action + why, idle time), results, wins, ante histogram per model (inline SVG), validity counts, post-mortems (served at `/runs/<file>`); `/status.json` has the same data. Open files are read incrementally (only appended bytes). |
| `balatro-data dataops --replay-port P [--interval 300] [--once]` | Unattended loop, logging to `<data>/dataops.log`: `compress --include-superseded`, validate + manifest (changed files only), replay (one at a time, oldest first) every closed `schema_ok` player run without a verdict whose `bridge_hash` matches the replay instance, then `status`. If port P's `/health` is down it launches an instance there with `launch_instance.ps1`; a crashed/hung replay instance is killed by the PID whose command line names `balatro-instances\<P>`. Bridge-level replay failures are retried (3 attempts) before the verdict is stored. Never touches other ports. |

Seed ranges are disjoint: the 500 held-out eval seeds in `python/balatro_env/data/eval_seeds.txt` are never
played by any data producer (swarm, rule agents, fuzzer); `FUZZ????` seeds belong to the fuzzer; training runs
use `balatro-data seeds`. Replays and fuzz runs are recorded too; filter them with the manifest's `replay_of`
and `agent` columns.
