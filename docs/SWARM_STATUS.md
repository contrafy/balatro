# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 00:45:46 by `balatro-data status` (edits inside this block are overwritten). Player runs: 55 (49 finished, 6 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (6)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | TIEL478W | 8 | SELECTING_HAND | 1 | 2 | 0 | The Club 0/600 | PLAY_HAND {"card_indices":[1,2,5,6,8]} | Two Pair AA66 est 540 of 600 (Even Steven +8 on the 6s); filler 3D keeps 4D (even) for a later pair… | 3s |
| 7802 | port-7802 | claude-fable-5-1 | DHIP8EMJ | 8 | SELECTING_HAND | 1 | 1 | 4 | Small Blind 0/300 | PLAY_HAND {"card_indices":[5,6,7,8]} | Bank Two Pair 44/22 est 64 (300 needed, 0 discards). No filler: keep 9 8 7 5 open-ended straight dr… | 27s |
| 7803 | port-7803 | claude-opus-5-5 | WJANAAZU | 8 | ROUND_EVAL | 2 | 4 | 2 | Big Blind (1500) | CASH_OUT | Big Blind won | 27s |
| 7805 | port-7805 | claude-opus-5-5 | 71JNH7LN | 8 | SELECTING_HAND | 1 | 1 | 4 | Small Blind 0/300 | PLAY_HAND {"card_indices":[3,4,7,8,1]} | Two Pair 8s2s est 80 banks 80/300 keeping both discards; Q as filler keeps 9-6-5 for a straight draw | 18s |
| 7806 | port-7806 | claude-opus-5-5 | JDM76YSJ | 8 | SHOP | 2 | 3 | 9 | Small Blind (1000) | SHOP_REROLL | no scorer in shop (Gluttonous perishable club-only); ->, need a pair/unconditional joker for 1000+ … | 2s |
| 7810 | port-7810 | claude-sonnet-5-5 | 6L83T6KZ | 8 | ROUND_EVAL | 3 | 6 | -2 | Big Blind (4800) | CASH_OUT | Cash out Big Blind | 12s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 6 | 0 | 6 | 0 | 0 | 3.17 | 4 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 17 | 0 | 17 | 0 | 0 | 3.65 | 6 |
| claude-sonnet-5-5 | 8 | Black | 20 | 0 | 19 | 0 | 1 | 2.85 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 3 | C1A5EUKS | claude-sonnet-5-5 | 8 | Black | loss | 5 | Small Blind 20982/25000 | [7807_C1A5EUKS.md](runs/7807_C1A5EUKS.md) |
| 4 | 9W4KUCWA | claude-opus-5-5 | 8 | Black | loss | 5 | The House 18927/50000 | [7804_9W4KUCWA.md](runs/7804_9W4KUCWA.md) |
| 5 | A5D7B521 | claude-opus-5-5 | 8 | Black | loss | 5 | The Head 35995/50000 | [7806_A5D7B521.md](runs/7806_A5D7B521.md) |
| 6 | IG1YQG43 | claude-sonnet-5-5 | 8 | Black | loss | 5 | Big Blind 14124/37500 | [7807_IG1YQG43.md](runs/7807_IG1YQG43.md) |
| 7 | HGM3CNYK | claude-opus-5-5 | 8 | Black | loss | 5 | The Hook 46987/50000 | [7805_HGM3CNYK.md](runs/7805_HGM3CNYK.md) |
| 8 | NP2SKU6Q | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 21457/37500 | [7803_NP2SKU6Q.md](runs/7803_NP2SKU6Q.md) |
| 9 | BKBSWK32 | claude-sonnet-5-5 | 8 | Black | loss | 5 | Big Blind 28980/37500 | [7810_BKBSWK32.md](runs/7810_BKBSWK32.md) |
| 10 | RJYRHSF9 | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 11394/37500 | [7809_RJYRHSF9.md](runs/7809_RJYRHSF9.md) |

### Data validity

- Player runs: 47 files in manifest; schema_ok 47, schema invalid 0; replay_ok 31, replay failed 0, awaiting replay 7, open/unended 9; quarantined 0; not yet in manifest 8.
- All files (incl. fuzz + replays): 145; schema_ok 143; replay_ok 37; replay failed 0; awaiting replay 96; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 172 |
| port-7802 | 0 | 0 | 183 |
| port-7803 | 0 | 0 | 307 |
| port-7804 | 0 | 0 | 129 |
| port-7805 | 0 | 0 | 284 |
| port-7806 | 0 | 0 | 383 |
| port-7807 | 0 | 0 | 389 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 295 |
| port-7810 | 0 | 0 | 408 |
<!-- AUTO:END -->

## Orchestrator log

- 2026-10-13 22:20: launched 10 Gold Stake players (7801-7802 Fable 5.1, 7803-7806 Opus 5.5, 7807-7810 Sonnet 5.5),
  plus HeadlessEngine, SwarmOps and GoldAdvisor workers. Load test beforehand: 12 instances = ~30% CPU, 4.3 GB RAM,
  57% GPU, so the GPU caps this box at about 18 instances.
- 22:25-23:00: 17 runs finished, all losses (Sonnet mean ante 2.2, Fable 3.5, Opus 4.2; deepest ante 5). GoldAdvisor
  hot-swapped 4 rounds of cli.py fixes from the post-mortems: skip-tag payout timing, sticker pricing, perishable
  planning, ORDER noise, est bugs, main-hand detection.
- ~23:05: an account-wide API rate limit (429, retry-after ~82 min) killed every agent at the same moment. The game
  states survived. 00:05: turned on `retry.waitForUsageReset` so agents wait instead of dying, and revived 6
  interrupted players (7801, 7803, 7806, 7807, 7809, and 7810, which is at the ante 8 boss) plus HeadlessEngine and
  GoldAdvisor. Ports 7802, 7804, 7805 and 7808 stay idle to keep concurrency at 8 agents.
- 00:16 GoldAdvisor cli.py 8dbf6b03: debuffed jokers dropped from est + `{DEBUFFED}` in `s` + Crimson Heart throwaway re-roll; Mouth/Eye locks read from blind state (`only_hand`, `hands_used`), est 0 for debuffed types; Ramen = decaying xMult, Judgement scored and `buyuse`d.
- 00:22 GoldAdvisor cli.py 46c98d9f: Mouth opening lock steered to a repeatable type, locked High Card playable (1 card), Burglar warning before The Mouth; slot pre-checks are notes only (trust /legal: Negative jokers, Buffoon packs); ORDER only for +mult vs xMult; Splash fillers chosen by est; draw outs from the real remaining deck; no "floor" for hands under half the per-hand need; Constellation planets `buyuse` ranked above rerolls; rental money jokers ~$0; debuffed cards lose suit for Seeing Double/Flower Pot.
- 00:33 GoldAdvisor cli.py 9ece1230: owned-joker keep/sell uses real contribution (est of a typical main hand with vs without the joker), so a Gros Michel/Swashbuckler that carries the build is never sold as AVOID/dead weight (shop, pack, Verdant Leaf); Blackboard plays red fillers so held cards stay black.
- 00:38 GoldAdvisor cli.py fdab97d3: 4+ plays of one type set the main hand at ante 1-2 (six Flushes no longer "undecided"; Celestial pack note/pick use most-played hand); Joker Stencil scored by empty slots (x5 with 1 joker, not AVOID); Spectral packs get pick advice with a target card.

