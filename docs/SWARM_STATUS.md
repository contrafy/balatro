# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 01:13:47 by `balatro-data status` (edits inside this block are overwritten). Player runs: 69 (61 finished, 8 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (8)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | AJAKNU2C | 8 | SELECTING_HAND | 2 | 5 | 0 | Big Blind 0/1500 | PLAY_HAND {"card_indices":[3,4,1,2,8]} | Pair 7 (7D diamond) est 534 >= 500/hand pace for 1500. Fillers A 8 2; keep 4D + 33 (diamonds add +3… | 52s |
| 7802 | port-7802 | claude-fable-5-1 | MKHAVQ6W | 8 | SHOP | 5 | 11 | 24 | Small Blind (25000) | SHOP_BUY_BOOSTER {"slot":2} | Celestial (0 after): Uranus (Two Pair L2) or Mercury (Pair L3) adds ~9% to the Card Sharp repeat ha… | 10s |
| 7803 | port-7803 | claude-opus-5-5 | KTTHZFZI | 8 | SHOP | 5 | 10 | 10 | Small Blind (25000) | SHOP_END | no chip/xMult joker; keep 0 to buy one next shop | 6s |
| 7804 | port-7804 | claude-opus-5-5 | GXQ1C3QV | 8 | SELECTING_HAND | 3 | 6 | 6 | Small Blind 0/3200 | DISCARD {"card_indices":[4,5,6,7,8]} | need 3200, no faces in hand (best 160); Smiley+Chad need face pairs, discard 5 to dig for faces kee… | 10s |
| 7806 | port-7806 | claude-opus-5-5 | ISNYLLW6 | 8 | SELECTING_HAND | 5 | 13 | 1 | The Arm 4080/50000 | PLAY_HAND {"card_indices":[2,3,4,5,1]} | Arm unreachable (45920 left); Two Pair T6 est 2132 keeps Pair level from dropping again, 1 hand left | 5s |
| 7807 | port-7807 | claude-opus-5-5 | 26ARMPG1 | 8 | BLIND_SELECT | 3 | 5 | 28 | Small Blind (3200) | SELECT_BLIND | Small 3200, Boss Tag not worth the skip; need the shop for an xMult | 6s |
| 7809 | port-7809 | claude-opus-5-5 | 76GDJXLS | 8 | SELECTING_HAND | 6 | 13 | 4 | The Mouth 0/120000 | PLAY_HAND {"card_indices":[5,6,7,8,4]} | Mouth lock: Pair caps ~28k x4 < 120000, only Two Pair L2 (face two pair ~35k) can reach it; 7733 es… | 15s |
| 7810 | port-7810 | claude-sonnet-5-5 | F1NGCDKQ | 8 | SELECTING_HAND | 2 | 5 | 10 | Big Blind 0/1500 | PLAY_HAND {"card_indices":[6,7,8,2,3]} | Full house 333JJ est 1176 of 1500 needed; leaves ~324 for 2 hands + 2 discards | 9s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 8 | 0 | 8 | 0 | 0 | 3.0 | 4 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 21 | 0 | 21 | 0 | 0 | 3.67 | 6 |
| claude-sonnet-5-5 | 8 | Black | 26 | 0 | 25 | 0 | 1 | 2.85 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 3 | C1A5EUKS | claude-sonnet-5-5 | 8 | Black | loss | 5 | Small Blind 20982/25000 | [7807_C1A5EUKS.md](runs/7807_C1A5EUKS.md) |
| 4 | 9W4KUCWA | claude-opus-5-5 | 8 | Black | loss | 5 | The House 18927/50000 | [7804_9W4KUCWA.md](runs/7804_9W4KUCWA.md) |
| 5 | A5D7B521 | claude-opus-5-5 | 8 | Black | loss | 5 | The Head 35995/50000 | [7806_A5D7B521.md](runs/7806_A5D7B521.md) |
| 6 | WJANAAZU | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 21884/37500 | [7803_WJANAAZU.md](runs/7803_WJANAAZU.md) |
| 7 | IG1YQG43 | claude-sonnet-5-5 | 8 | Black | loss | 5 | Big Blind 14124/37500 | [7807_IG1YQG43.md](runs/7807_IG1YQG43.md) |
| 8 | HGM3CNYK | claude-opus-5-5 | 8 | Black | loss | 5 | The Hook 46987/50000 | [7805_HGM3CNYK.md](runs/7805_HGM3CNYK.md) |
| 9 | NP2SKU6Q | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 21457/37500 | [7803_NP2SKU6Q.md](runs/7803_NP2SKU6Q.md) |
| 10 | BKBSWK32 | claude-sonnet-5-5 | 8 | Black | loss | 5 | Big Blind 28980/37500 | [7810_BKBSWK32.md](runs/7810_BKBSWK32.md) |

### Data validity

- Player runs: 60 files in manifest; schema_ok 60, schema invalid 0; replay_ok 47, replay failed 0, awaiting replay 3, open/unended 10; quarantined 0; not yet in manifest 9.
- All files (incl. fuzz + replays): 165; schema_ok 163; replay_ok 53; replay failed 0; awaiting replay 99; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| port-7805 | 1 | 1 | 411 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 256 |
| port-7802 | 0 | 0 | 293 |
| port-7803 | 0 | 0 | 464 |
| port-7804 | 0 | 0 | 167 |
| port-7806 | 0 | 0 | 528 |
| port-7807 | 0 | 0 | 557 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 423 |
| port-7810 | 0 | 0 | 588 |
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
- 00:48 GoldAdvisor cli.py dc6a75cb: ante 1-2 with 0 scorers: an unstickered +mult joker (incl. one-suit) floors at 85 above the Buffoon pack (78); stickered scorers bought to survive ante 1-2 lead their text with "NEEDED NOW" instead of the rent total; rentals otherwise accepted only for reliable/growth xMults (GoldStrategist data); straight draws compare every window (open-ended over gutshot). Checked vs previous cli.py on 702 recorded ante 1-2 shops: 91 changed, mostly text.
- 00:56 GoldAdvisor cli.py d9217589: GoldStrategist rules 1-10 (GOLD_ANALYSIS.md): $8 money floor from ante 2 (not suspended), reroll only with $20+ left (max 2/shop, never over a Buffoon), Buffoon 80 at ante 2-5 with <2 reliable/growth xMults, Arcana/Spectral 45 without a Vampire/Glass plan, flat rentals sold once 2 non-rental scorers carry, SCORE CHECK/EMERGENCY line, conditional xMult boost from ante 3, ante-1 skips only for joker-now tags (ante 3-4 need hand >= boss/2), Flush/Straight non-core, GOLD CHECK xMult targets 1/2/3; Acrobat = reliable xMult. Diff vs previous on 1633 recorded Gold shops: 400 changed (mostly floor LEAVEs and flat-rental SELLs).
- 01:01 GoldAdvisor cli.py 37a94c4b: Gros Michel/Popcorn/Ice Cream bought by marginal est on the main hand (Gros discounted 1/6, not AVOID); Vampire/Lucky Cat/Glass/Steel Joker capped at 45 with nothing in the deck to feed them; editions count as scorers when you own <2; sell a dying perishable / flat rental to fund a 70+ item before LEAVE; est: held cards scored per card in hand order (Steel x1.5 before that card's Shoot the Moon; Baron per card), Sly/Jolly etc. fire on a Flush/Straight that contains a pair, Splash candidates judged with their fillers; debuffed cards that hold the kept hand are not discarded; planet picks prefer an owned type-xMult's hand, then pair-family fallbacks; cash/Orbital skip tags valued in $ / levels.
- 01:05 GoldAdvisor cli.py 30a281d0: pack picks treat the pack price as sunk (perishable cost capped, eternal harmless with 2+ free slots, rent penalty capped, scorers into free slots floored when <2 scorers); a perishable rental's rent is bounded (no "drains the run" refusal); Celestial pick uses an owned type-xMult only when it fits the main hand (no Saturn over Uranus); est notes Misprint's roll-0..23 range; 4 recorded-obs regression tests (tests/fixtures/advisor). On 464 recorded packs: 28 SKIPs became PICKs.
- 01:09 GoldAdvisor cli.py aaaa8081: shop INVARIANT: in an EMERGENCY or with <2 scorers at ante <= 3, never LEAVE/REROLL while an affordable scorer is offered (no weak Eternals, flat rentals or growth xMults); shop perishable cost 5 when under-scaled; advise PACE rule: if best est x hands left < need, discard toward a bigger hand before banking one (7810 lost 216/300). Tests 50/50.

