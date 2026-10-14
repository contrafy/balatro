# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 00:28:12 by `balatro-data status` (edits inside this block are overwritten). Player runs: 42 (34 finished, 8 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (8)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | 1QAUCRHI | 8 | BLIND_SELECT | 2 | 3 | 5 | Small Blind (1000) | SKIP_BLIND | Override: Small 1000 vs ~220/hand (Splash+Banner, 0 mult jokers) is ~25% to clear; Handy tag pays n… | 6s |
| 7802 | port-7802 | claude-fable-5-1 | 7D8XNH58 | 8 | PACK_OPENING | 2 | 5 | 0 | Big Blind (1500) | SELECT_PACK_CARD {"index":1} | Jupiter: Flush L2 pairs with Crafty +80 (Flush with Q held 2635 -> 3060), my biggest one-hand clear… | 3s |
| 7803 | port-7803 | claude-opus-5-5 | T4WWHFJ8 | 8 | SELECTING_HAND | 3 | 8 | 1 | The Head 3200/6400 | PLAY_HAND {"card_indices":[1,2,5,4,8]} | Two Pair AT est 3128 of 3200; last hand needs 72 and even High Card scores ~300 with Trousers 20; D… | 2s |
| 7805 | port-7805 | claude-opus-5-5 | 9MRSNKY7 | 8 | SELECTING_HAND | 1 | 1 | 4 | Small Blind 0/300 | PLAY_HAND {"card_indices":[1,2,4,5,6]} | spade flush est 308 vs 300 need, clears in one hand | 4s |
| 7806 | port-7806 | claude-opus-5-5 | T7BAW3E8 | 8 | BLIND_SELECT | 4 | 8 | 3 | Big Blind (13500) | SELECT_BLIND | Big 13500 with Two Pair L4, never skip | 11s |
| 7807 | port-7807 | claude-sonnet-5-5 | IG1YQG43 | 8 | ROUND_EVAL | 5 | 9 | 3 | The Goad (50000) | CASH_OUT | cash out Goad | 4s |
| 7809 | port-7809 | claude-opus-5-5 | RJYRHSF9 | 8 | SELECTING_HAND | 5 | 9 | 3 | Big Blind 2574/37500 | PLAY_HAND {"card_indices":[2,3,8,7,4]} | Pair QQ est 3060, 34926 needed in 2 hands: out of reach, cycle fillers 3H 4C TD hoping last draw gi… | 15s |
| 7810 | port-7810 | claude-sonnet-5-5 | K8AC6G9T | 8 | ROUND_EVAL | 3 | 5 | -3 | The Needle (3200) | CASH_OUT | cash out ante 2 boss | 5s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 4 | 0 | 4 | 0 | 0 | 3.0 | 4 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 8 | 0 | 8 | 0 | 0 | 4.38 | 6 |
| claude-sonnet-5-5 | 8 | Black | 16 | 0 | 15 | 0 | 1 | 2.69 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 3 | C1A5EUKS | claude-sonnet-5-5 | 8 | Black | loss | 5 | Small Blind 20982/25000 | [7807_C1A5EUKS.md](runs/7807_C1A5EUKS.md) |
| 4 | 9W4KUCWA | claude-opus-5-5 | 8 | Black | loss | 5 | The House 18927/50000 | [7804_9W4KUCWA.md](runs/7804_9W4KUCWA.md) |
| 5 | A5D7B521 | claude-opus-5-5 | 8 | Black | loss | 5 | The Head 35995/50000 | [7806_A5D7B521.md](runs/7806_A5D7B521.md) |
| 6 | HGM3CNYK | claude-opus-5-5 | 8 | Black | loss | 5 | The Hook 46987/50000 | [7805_HGM3CNYK.md](runs/7805_HGM3CNYK.md) |
| 7 | NP2SKU6Q | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 21457/37500 | [7803_NP2SKU6Q.md](runs/7803_NP2SKU6Q.md) |
| 8 | BKBSWK32 | claude-sonnet-5-5 | 8 | Black | loss | 5 | Big Blind 28980/37500 | [7810_BKBSWK32.md](runs/7810_BKBSWK32.md) |
| 9 | UQ4UCR7Z | claude-fable-5-1 | 8 | Black | loss | 4 | The House 7029/18000 | [7802_UQ4UCR7Z.md](runs/7802_UQ4UCR7Z.md) |
| 10 | 943PYVF7 | claude-opus-4 | 1 | Black | unfinished | 4 | Big Blind (7500) | - |

### Data validity

- Player runs: 40 files in manifest; schema_ok 40, schema invalid 0; replay_ok 25, replay failed 0, awaiting replay 6, open/unended 9; quarantined 0; not yet in manifest 2.
- All files (incl. fuzz + replays): 133; schema_ok 131; replay_ok 31; replay failed 0; awaiting replay 90; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 124 |
| port-7802 | 0 | 0 | 139 |
| port-7803 | 0 | 0 | 235 |
| port-7804 | 0 | 0 | 129 |
| port-7805 | 0 | 0 | 197 |
| port-7806 | 0 | 0 | 297 |
| port-7807 | 0 | 0 | 311 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 236 |
| port-7810 | 0 | 0 | 307 |
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

