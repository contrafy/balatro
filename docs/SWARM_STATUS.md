# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-13 22:37:48 by `balatro-data status` (edits inside this block are overwritten). Player runs: 25 (15 finished, 10 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (10)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | XDLNJ8SC | 8 | SELECTING_HAND | 1 | 1 | 4 | Small Blind 0/300 | DISCARD {"card_indices":[1,6,7,8]} | No pair; best High Card est 15 vs need 300. Keep J987 open-ended straight draw (T or 6-5, ~35%) and… | 12s |
| 7802 | port-7802 | claude-fable-5-1 | UQ4UCR7Z | 8 | PACK_OPENING | 4 | 9 | 3 | Big Blind (13500) | SELECT_PACK_CARD {"index":3} | Mercury: Pair L1->L2 (25x3), my most-played hand; pair est 2880 -> ~3900 | 17s |
| 7803 | port-7803 | claude-opus-5-5 | NP2SKU6Q | 8 | SELECTING_HAND | 5 | 11 | 0 | Big Blind 0/37500 | DISCARD {"card_indices":[2,5,6,7,8]} | Pair 8 est 1322 vs 37500; keep 88 + QD (Photograph), draw 5 for Two Pair/Full House | 16s |
| 7804 | port-7804 | claude-opus-5-5 | 9W4KUCWA | 8 | SHOP | 4 | 9 | 23 | Small Blind (9000) | SHOP_BUY_BOOSTER {"slot":1} | Celestial another shot at Mercury/Uranus; ante 5 needs ~3x my current output; 3 -> 9 | 7s |
| 7805 | port-7805 | claude-opus-5-5 | 5C3G7R9C | 8 | SELECTING_HAND | 1 | 1 | 4 | Small Blind 0/300 | DISCARD {"card_indices":[4,6,7,8]} | Two pair est 84 x3 hands < 300; keep AD KD TD 7D, ~61% per discard to hit flush (~320 clears alone) | 7s |
| 7806 | port-7806 | claude-opus-5-5 | A5D7B521 | 8 | SHOP | 5 | 11 | 21 | Big Blind (37500) | SHOP_REROLL | No xMult yet; 1 -> 5 | 8s |
| 7807 | port-7807 | claude-sonnet-5-5 | C1A5EUKS | 8 | BLIND_SELECT | 5 | 12 | 1 | Small Blind (25000) | SELECT_BLIND | Play Small 25000 | 12s |
| 7808 | port-7808 | claude-sonnet-5-5 | 47XLSLSM | 8 | SHOP | 2 | 4 | 3 | Small Blind (1000) | SHOP_END | Nothing affordable | 5s |
| 7809 | port-7809 | claude-sonnet-5-5 | FE8A3BTS | 8 | ROUND_EVAL | 2 | 3 | 1 | The Window (2000) | CASH_OUT | Cash out boss | 23s |
| 7810 | port-7810 | claude-sonnet-5-5 | ZY6GJXIG | 8 | PACK_OPENING | 6 | 13 | 13 | Big Blind (90000) | SELECT_PACK_CARD {"index":3} | Another plain face card (QS) raises odds of a face pair; stone Q would not be a face | 11s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 1 | 0 | 1 | 0 | 0 | 3.0 | 3 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 1 | 0 | 1 | 0 | 0 | 4.0 | 4 |
| claude-sonnet-5-5 | 8 | Black | 7 | 0 | 7 | 0 | 0 | 1.71 | 3 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | 943PYVF7 | claude-opus-4 | 1 | Black | unfinished | 4 | Big Blind (7500) | - |
| 2 | W9HRFGMW | claude-opus-5-5 | 8 | Black | loss | 4 | Big Blind 13347/13500 | [7805_W9HRFGMW.md](runs/7805_W9HRFGMW.md) |
| 3 | ZIBZ3PEK | claude-sonnet-5-5 | 8 | Black | loss | 3 | Small Blind 938/3200 | [7809_ZIBZ3PEK.md](runs/7809_ZIBZ3PEK.md) |
| 4 | JN677MSZ | claude-sonnet-5-5 | 8 | Black | loss | 3 | Small Blind 2084/3200 | [7807_JN677MSZ.md](runs/7807_JN677MSZ.md) |
| 5 | 6X58CJ4E | claude-fable-5-1 | 8 | Black | loss | 3 | Big Blind 4312/4800 | [7801_6X58CJ4E.md](runs/7801_6X58CJ4E.md) |
| 6 | YTZCKRK2 | claude-sonnet-5-5 | 8 | Black | loss | 2 | The Water 428/2000 | [7808_YTZCKRK2.md](runs/7808_YTZCKRK2.md) |
| 7 | A1VMIHLQ | (unknown) | 1 | Red | loss | 2 | The Club 1344/1600 | - |
| 8 | ANTE0001 | (unknown) | 1 | Red | loss | 2 | Small Blind 664/800 | - |
| 9 | FL4ZGVC1 | claude-sonnet-5-5 | 8 | Black | loss | 1 | The Head 249/600 | [7809_FL4ZGVC1.md](runs/7809_FL4ZGVC1.md) |
| 10 | 866JGCIT | claude-sonnet-5-5 | 8 | Black | loss | 1 | The Club 413/600 | [7808_866JGCIT.md](runs/7808_866JGCIT.md) |

### Data validity

- Player runs: 25 files in manifest; schema_ok 25, schema invalid 0; replay_ok 8, replay failed 0, awaiting replay 6, open/unended 11; quarantined 0; not yet in manifest 0.
- All files (incl. fuzz + replays): 102; schema_ok 100; replay_ok 14; replay failed 0; awaiting replay 74; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 43 |
| port-7802 | 0 | 0 | 63 |
| port-7803 | 0 | 0 | 99 |
| port-7804 | 0 | 0 | 86 |
| port-7805 | 0 | 0 | 67 |
| port-7806 | 0 | 0 | 120 |
| port-7807 | 0 | 0 | 125 |
| port-7808 | 0 | 0 | 93 |
| port-7809 | 0 | 0 | 94 |
| port-7810 | 0 | 0 | 134 |
<!-- AUTO:END -->

## Orchestrator log

