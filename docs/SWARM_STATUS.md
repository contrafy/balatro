# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 02:01:29 by `balatro-data status` (edits inside this block are overwritten). Player runs: 96 (89 finished, 7 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (7)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | QRM4RTHQ | 8 | ROUND_EVAL | 2 | 4 | -6 | Big Blind (1500) | CASH_OUT | Big Blind won 4930/1500 | 1s |
| 7802 | port-7802 | claude-fable-5-1 | 3IDYS1SA | 8 | SELECTING_HAND | 1 | 2 | 1 | Big Blind 0/450 | DISCARD {"card_indices":[1,6,8]} | Keep QH TS 9S 8H 6D: 8 outs (4 J -> QJT98 est 432, 4 sevens -> T9876 est 528 with Odd Todd on 9+7) … | 3s |
| 7803 | port-7803 | claude-opus-5-5 | PZ67LB31 | 8 | SELECTING_HAND | 5 | 10 | 14 | Big Blind 0/37500 | DISCARD {"card_indices":[1,2,5]} | no pair, High K 9010 paces 24k < 37500; solver: discard KS 9S 5S keeping evens 6H(red seal)/2D + 7H… | 2s |
| 7804 | port-7804 | claude-opus-5-5 | MS7VJ1WX | 8 | BLIND_SELECT | 2 | 3 | 0 | Big Blind (1500) | SELECT_BLIND | Big 1500 | 3s |
| 7806 | port-7806 | claude-opus-5-5 | 7M2J3E3P | 8 | BLIND_SELECT | 1 | 0 | 4 | Small Blind (300) | SELECT_BLIND | ante 1 small, Voucher tag not worth skipping with no jokers | 12s |
| 7807 | port-7807 | claude-opus-5-5 | 3WSFNWWA | 8 | SHOP | 4 | 9 | 13 | Small Blind (9000) | SHOP_BUY {"slot":1} | Jolly +8 mult on every pair-family hand: Pair mult 17->25 (+47%) before Ramen x1.92; eternal is fin… | 6s |
| 7809 | port-7809 | claude-opus-5-5 | 96G8IPB1 | 8 | SELECTING_HAND | 2 | 5 | 3 | Big Blind 0/1500 | PLAY_HAND {"card_indices":[1,2,3,5,6]} | Broadway straight est ~1296 of 1500, leaves ~204 for 2 hands | 5s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 11 | 0 | 11 | 0 | 0 | 3.55 | 7 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 43 | 0 | 43 | 0 | 0 | 3.56 | 7 |
| claude-sonnet-5-5 | 8 | Black | 29 | 0 | 28 | 0 | 1 | 2.97 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | YJGGELMB | claude-opus-5-5 | 8 | Black | loss | 7 | The Manacle 25312/220000 | [7806_YJGGELMB.md](runs/7806_YJGGELMB.md) |
| 3 | MKHAVQ6W | claude-fable-5-1 | 8 | Black | loss | 7 | The Eye 37553/220000 | [7802_MKHAVQ6W.md](runs/7802_MKHAVQ6W.md) |
| 4 | 26ARMPG1 | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 48586/90000 | [7807_26ARMPG1.md](runs/7807_26ARMPG1.md) |
| 5 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 6 | 76GDJXLS | claude-opus-5-5 | 8 | Black | loss | 6 | The Mouth 80352/120000 | [7809_76GDJXLS.md](runs/7809_76GDJXLS.md) |
| 7 | M5SRCH3B | claude-sonnet-5-5 | 8 | Black | loss | 5 | The Mark 29380/50000 | [7810_M5SRCH3B.md](runs/7810_M5SRCH3B.md) |
| 8 | AJAKNU2C | claude-fable-5-1 | 8 | Black | loss | 5 | The Eye 14823/50000 | [7801_AJAKNU2C.md](runs/7801_AJAKNU2C.md) |
| 9 | NW9TXZPC | claude-opus-5-5 | 8 | Black | loss | 5 | The Wheel 49868/50000 | [7805_NW9TXZPC.md](runs/7805_NW9TXZPC.md) |
| 10 | HLJ9A59I | claude-opus-5-5 | 8 | Black | loss | 5 | The Fish 29532/50000 | [7803_HLJ9A59I.md](runs/7803_HLJ9A59I.md) |

### Data validity

- Player runs: 83 files in manifest; schema_ok 83, schema invalid 0; replay_ok 66, replay failed 0, awaiting replay 6, open/unended 11; quarantined 0; not yet in manifest 13.
- All files (incl. fuzz + replays): 209; schema_ok 207; replay_ok 72; replay failed 0; awaiting replay 123; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| port-7805 | 1 | 1 | 624 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 373 |
| port-7802 | 0 | 0 | 420 |
| port-7803 | 0 | 0 | 703 |
| port-7804 | 0 | 0 | 370 |
| port-7806 | 0 | 0 | 772 |
| port-7807 | 0 | 0 | 783 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 634 |
| port-7810 | 0 | 0 | 832 |
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
- 01:24 GoldAdvisor cli.py a3b18b9c: main hand re-anchors only when the richer type was played >= half as often (10 Pair vs 3 Two Pair stays Pair); state-dependent flat jokers (Erosion, Bull, Bootstraps, Spare Trousers...) valued by what they add NOW (~0 -> not a scorer, no NEEDED NOW); Throwback = x(1+0.25*skips); $0 shop items may replace a weak joker; no flush chase in the boss-debuffed suit; with 0-1 scorers at ante 1-2 any current scorer outranks every utility/LEVELS/ECON joker in shop and packs (7805 Astronomer over Walkie Talkie). ORDER direction verified (b order lists old positions; +mult goes left). Tests 54/54.
- 01:28 GoldAdvisor cli.py 7784153c: ORDER keeps a holo xMult with the xMults (7803 Summit right of holo Tribe); card-trigger xMults (Photograph, Triboulet) no longer count toward the xMult targets (they multiply before joker-main +mult); "no Pair floor" warning respects jokers that carry the est (Gros Michel) and Smiley/main-hand jokers; Half Joker = core scorer for Pair/Trips mains; retrigger jokers (Seltzer, Hanging Chad, Sock and Buskin, Dusk, Hack) are scorers; Walkie Talkie common; Mr. Bones a run-saver (72 when under-scaled), not AVOID; Raised Fist plays low fillers (no 2/3 protection); The Tooth no longer blocks buys in an EMERGENCY; PACE counts later hands at 60%. Tests 56/56.
- 01:30 GoldAdvisor cli.py 99dbd2cf: main hand = argmax(typical est with jokers/levels x frequency you can make it), containment-aware (Two Pair/Trips/FH plays count for Pair; >=2 plays, >=3 for Quads); rerolls keep the rent due at round end ($3 per rental).
- 01:33 GoldAdvisor cli.py f8edc21b: BOSS PREP (boss known at ante start): Eye/Mouth vs Card Sharp/Supernova, Plant vs face engines, Psychic vs Half Joker, suit bosses vs Flush, Wall/Violet/Needle/Flint/Arm vs a too-small hand -> counters (Luchador, Chicot, Mr. Bones, Director's Cut) ranked first, keep $10 if Director's Cut owned; every shop joker valued by its marginal est (+20%+ = keep/buy, +30% = core for stickers); Card Sharp counted in the typical est; Driver's License capped below 12 enhanced cards; Riff-raff described; PACE fixed: later hands at 85% (shown), and banking is preferred once a discard was used (7805 192/300 regression).
- 01:51 GoldAdvisor cli.py a5939a5a: ADVICE walks the printed (final, post-reweight) ranking and lists every higher-ranked option it passes over with the reason (test over fixtures; 0 unexplained of 1783 recorded shops); reroll never passes an affordable 60+ joker (Ice Cream 88 case); SCORE CHECK = best hand of a round with Summit/Acrobat/Card Sharp active, calibrated on 1042 recorded Gold shops (ratio to next boss/3: <0.35 died 80%, <0.7 60%, <1 43%, else 28%; printed); EMERGENCY only below 0.35 (was firing in 89% of ante-2+ shops), scoring jokers may break the money floor below 0.7; marginal joker value on the round total (Acrobat rental x3 bought); Buffoon packs no longer held back for planets.
- 01:55 GoldAdvisor cli.py 022bc814: `advise` checks its rule pick against DrawSolver (balatro_env/solver.py, Monte-Carlo p_clear over the public remaining deck): prints SOLVER top 3 + the rule pick's p_clear, and switches the ADVICE to the solver's best first action when it clears >3 points more often (old advice shown); special cases (non play/discard advice, Crimson Heart, Verdant Leaf, face-down cards) untouched. 60 recorded Gold hands: 10 overrides, 0 errors, median 1.8 s, max 5.1 s.

