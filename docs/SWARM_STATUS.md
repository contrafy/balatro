# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 00:04:56 by `balatro-data status` (edits inside this block are overwritten). Player runs: 32 (32 finished, 0 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (0)

No live runs.

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 4 | 0 | 2 | 0 | 2 | 2.75 | 4 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 8 | 0 | 5 | 0 | 3 | 3.62 | 5 |
| claude-sonnet-5-5 | 8 | Black | 14 | 0 | 10 | 0 | 4 | 2.57 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | unfinished | 8 | Crimson Heart 15640/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | C1A5EUKS | claude-sonnet-5-5 | 8 | Black | loss | 5 | Small Blind 20982/25000 | [7807_C1A5EUKS.md](runs/7807_C1A5EUKS.md) |
| 3 | 9W4KUCWA | claude-opus-5-5 | 8 | Black | loss | 5 | The House 18927/50000 | [7804_9W4KUCWA.md](runs/7804_9W4KUCWA.md) |
| 4 | A5D7B521 | claude-opus-5-5 | 8 | Black | loss | 5 | The Head 35995/50000 | [7806_A5D7B521.md](runs/7806_A5D7B521.md) |
| 5 | NP2SKU6Q | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 21457/37500 | [7803_NP2SKU6Q.md](runs/7803_NP2SKU6Q.md) |
| 6 | UQ4UCR7Z | claude-fable-5-1 | 8 | Black | loss | 4 | The House 7029/18000 | [7802_UQ4UCR7Z.md](runs/7802_UQ4UCR7Z.md) |
| 7 | 943PYVF7 | claude-opus-4 | 1 | Black | unfinished | 4 | Big Blind (7500) | - |
| 8 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | unfinished | 4 | Small Blind (9000) | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 9 | W9HRFGMW | claude-opus-5-5 | 8 | Black | loss | 4 | Big Blind 13347/13500 | [7805_W9HRFGMW.md](runs/7805_W9HRFGMW.md) |
| 10 | 47XLSLSM | claude-sonnet-5-5 | 8 | Black | loss | 3 | The Mark 4854/6400 | [7808_47XLSLSM.md](runs/7808_47XLSLSM.md) |

### Data validity

- Player runs: 32 files in manifest; schema_ok 32, schema invalid 0; replay_ok 19, replay failed 0, awaiting replay 3, open/unended 10; quarantined 0; not yet in manifest 0.
- All files (incl. fuzz + replays): 121; schema_ok 119; replay_ok 25; replay failed 0; awaiting replay 83; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 84 |
| port-7802 | 0 | 0 | 87 |
| port-7803 | 0 | 0 | 145 |
| port-7804 | 0 | 0 | 129 |
| port-7805 | 0 | 0 | 123 |
| port-7806 | 0 | 0 | 179 |
| port-7807 | 0 | 0 | 185 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 139 |
| port-7810 | 0 | 0 | 183 |
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

