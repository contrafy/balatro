# Swarm status

## Morning summary

_Orchestrator: summarize the night here._

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 02:30:41 by `balatro-data status` (edits inside this block are overwritten). Player runs: 113 (104 finished, 9 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (9)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | RM2XKW5G | 8 | SHOP | 3 | 5 | 7 | Small Blind (3200) | SHOP_END | left; Venus (trips) and Arcana do not lift the flush; keep money for the next shop (Jupiter/scorers… | 53s |
| 7802 | port-7802 | claude-fable-5-1 | 3IDYS1SA | 8 | SHOP | 6 | 12 | 44 | Small Blind (60000) | SELL_CONSUMABLE {"index":1} | Sell Jupiter: +, Campfire x1.5 | 2s |
| 7803 | port-7803 | claude-opus-5-5 | 9J8GXWMG | 8 | SELECTING_HAND | 2 | 4 | 6 | Big Blind 0/1500 | PLAY_HAND {"card_indices":[5,6,7,3]} | Trips 4 est 1728 >= 1500 (Walkie x3 + spade); 2 hands backup | 8s |
| 7804 | port-7804 | claude-opus-5-5 | U4HS5KQK | 8 | SHOP | 2 | 3 | 1 | Small Blind (1000) | SHOP_END | left, nothing affordable | 8s |
| 7805 | port-7805 | claude-opus-5-5 | 5G8855KD | 8 | BLIND_SELECT | 4 | 9 | 1 | The Flint (18000) | SELECT_BLIND | The Flint 18000 boss | 9s |
| 7806 | port-7806 | claude-opus-5-5 | NBBEN6W1 | 8 | ROUND_EVAL | 5 | 11 | -5 | Small Blind (25000) | CASH_OUT | Small cleared 25000+, cash out | 2s |
| 7807 | port-7807 | claude-opus-5-5 | B6KZC39M | 8 | BLIND_SELECT | 3 | 6 | 10 | Small Blind (3200) | SKIP_BLIND | Charm tag = free Mega Arcana now; best hand ~6000 >= boss/2 1600; saves a Popcorn tick for the Big … | 4s |
| 7809 | port-7809 | claude-opus-5-5 | Z6ZJWRC4 | 8 | SELECTING_HAND | 1 | 3 | 8 | The Window 0/600 | DISCARD {"card_indices":[8]} | burn last discard on debuffed 9D; activates Summit so Two Pair QT = 60x17 ~1020 vs 600 | 4s |
| 7810 | port-7810 | claude-sonnet-5-5 | GF13YRTQ | 8 | SELECTING_HAND | 3 | 7 | 4 | The Goad 0/6400 | DISCARD {"card_indices":[2,3,5,6,8]} | Goad 6400 needs ~2100/hand; best Pair est ~1250. Keep AC 7C 4C for club flush (Gluttonous +3/club, … | 14s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 12 | 0 | 12 | 0 | 0 | 3.58 | 7 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 55 | 0 | 55 | 0 | 0 | 3.53 | 7 |
| claude-sonnet-5-5 | 8 | Black | 31 | 0 | 30 | 0 | 1 | 3.0 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 2 | YJGGELMB | claude-opus-5-5 | 8 | Black | loss | 7 | The Manacle 25312/220000 | [7806_YJGGELMB.md](runs/7806_YJGGELMB.md) |
| 3 | MKHAVQ6W | claude-fable-5-1 | 8 | Black | loss | 7 | The Eye 37553/220000 | [7802_MKHAVQ6W.md](runs/7802_MKHAVQ6W.md) |
| 4 | 26ARMPG1 | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 48586/90000 | [7807_26ARMPG1.md](runs/7807_26ARMPG1.md) |
| 5 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |
| 6 | 76GDJXLS | claude-opus-5-5 | 8 | Black | loss | 6 | The Mouth 80352/120000 | [7809_76GDJXLS.md](runs/7809_76GDJXLS.md) |
| 7 | PZ67LB31 | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 28434/90000 | [7803_PZ67LB31.md](runs/7803_PZ67LB31.md) |
| 8 | M5SRCH3B | claude-sonnet-5-5 | 8 | Black | loss | 5 | The Mark 29380/50000 | [7810_M5SRCH3B.md](runs/7810_M5SRCH3B.md) |
| 9 | AJAKNU2C | claude-fable-5-1 | 8 | Black | loss | 5 | The Eye 14823/50000 | [7801_AJAKNU2C.md](runs/7801_AJAKNU2C.md) |
| 10 | 3WSFNWWA | claude-opus-5-5 | 8 | Black | loss | 5 | Big Blind 23529/37500 | [7807_3WSFNWWA.md](runs/7807_3WSFNWWA.md) |

### Data validity

- Player runs: 98 files in manifest; schema_ok 98, schema invalid 0; replay_ok 76, replay failed 0, awaiting replay 11, open/unended 11; quarantined 0; not yet in manifest 15.
- All files (incl. fuzz + replays): 237; schema_ok 235; replay_ok 82; replay failed 0; awaiting replay 141; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| port-7805 | 1 | 1 | 760 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 446 |
| port-7802 | 0 | 0 | 532 |
| port-7803 | 0 | 0 | 844 |
| port-7804 | 0 | 0 | 502 |
| port-7806 | 0 | 0 | 920 |
| port-7807 | 0 | 0 | 935 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 754 |
| port-7810 | 0 | 0 | 983 |
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
- 02:20 GoldAdvisor cli.py 4fc5eba8: BOSS PREP facts checked in blind.lua (Eye/Needle kill Card Sharp incl. Blueprint/Brainstorm copies; Mouth does not; Water kills Banner only, Summit always on); TIGHT: next blind's projected round < 1.2x need -> money floor off (recorded: 13-40% lost vs <=6%; 7805 lost a boss by 132 holding $12); SCORE CHECK from 40 deals of the real deck (AUC 0.77 vs 0.74 synthetic; bands printed); joker values (shop + pack) = marginal round est on deals from your deck (Walkie/Scholar/Shoot the Moon visible; pack ties never by slot order; bridges must score now: Erosion 0); joker shares count Summit/Acrobat (final hand); main hand anchored by owned hand-gated jokers (Half Joker -> Pair, 7809); solver lines show n/$/growth, ADVICE also follows a same-p solver line worth $1+ more; Psychic plays always padded to 5; Credit Card -$20 for must-buys; eternal rental on a +30% joker priced like a core; Immolate 60 when poor; Riff-raff classified; no pre-emptive "sell for an xMult not in the shop"; skip reason "no free slot" only when true. Tests 71.
- 02:29 GoldAdvisor cli.py 6f832f0a: solver ADVISORY ONLY (orchestrator): ADVICE follows it only for a PLAY that clears the blind now; fillers never spend a held pair, Square Joker plays exactly 4; rental sells never take a carrier (share >= 25%), the only r/g xMult or Mr. Bones; card-trigger xMults capped by their real gain (Photograph 130 case); Mr. Bones bought in EMERGENCY. Tests 74.

