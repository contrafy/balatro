# Swarm status

## Morning summary

_Interim, 02:45 (updated as the night goes on)._

- 103 Gold Stake runs finished on Black Deck, 0 wins.
- Antes reached: 1: 15, 2: 15, 3: 26, 4: 19, 5: 21, 6: 4, 7: 2, 8: 1.
- Deepest run: Sonnet `ZY6GJXIG` lost the ante-8 boss Crimson Heart with a face-Pair engine. Next were Fable
  `MKHAVQ6W` (ante 7, The Eye) and Opus `YJGGELMB` (ante 7, The Manacle).
- Mean ante: Opus 3.5 (60 runs), Fable 3.6 (12), Sonnet 3.1 (31). The tiers are close; Fable is ~3x slower per run.
- Data: 270 trajectories recorded, 87 replay-verified so far; the backlog is being moved to headless replay.
- Why runs die: under-scaled by ante 3-5, broke from Gold rent and $0 Small Blinds, and reliable xMults are rare.
  See `docs/GOLD_ANALYSIS.md`.
- ~03:30: a second account-wide 429 rate limit (retry-after ~90 min) hit. With `retry.waitForUsageReset` on, agents
  paused and resumed instead of dying, so some runs show 1.5-2.5 h durations. The account rate limit, not this
  machine, now bounds throughput.
- 03:00-05:10: three Opus runs lost at the ante-8 boss: Amber Acorn x2 and Crimson Heart x1. They came after the
  solver, shop-sim and advisor upgrades. A Sonnet run had lost to Crimson Heart earlier in the night.

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 05:17:51 by `balatro-data status` (edits inside this block are overwritten). Player runs: 142 (133 finished, 9 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (9)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | UX7FJYS3 | 8 | SELECTING_HAND | 2 | 6 | 10 | The Pillar 0/2000 | DISCARD {"card_indices":[1,5,6,7,8]} | No pair, need 2000; dump both debuffed cards and the low junk, keep clean JH TH 9D (straight/pair d… | 22s |
| 7802 | port-7802 | claude-fable-5-1 | KGP6GZRV | 8 | BLIND_SELECT | 4 | 7 | 4 | Big Blind (13500) | SELECT_BLIND | Big Blind 13500: Two Pair ~7590 at 0 discards, FH ~14600 | 3s |
| 7803 | port-7803 | claude-opus-5-5 | Q5Z3IQVH | 8 | BLIND_SELECT | 1 | 2 | 7 | The Goad (600) | SELECT_BLIND | boss The Goad 600, cannot skip | 10s |
| 7804 | port-7804 | claude-opus-5-5 | GZN3NGM7 | 8 | SELECTING_HAND | 1 | 2 | 1 | Big Blind 0/450 | DISCARD {"card_indices":[1,6,7,8]} | Two Pair 9988 est 108, pace 291 < 450; draw 4 for full house (4 outs) or better two pair | 30s |
| 7805 | port-7805 | claude-opus-5-5 | 7YW86UJN | 8 | BLIND_SELECT | 4 | 8 | 18 | Big Blind (13500) | SELECT_BLIND | Big 13500 | 2s |
| 7806 | port-7806 | claude-opus-5-5 | I9RJP8E5 | 8 | SELECTING_HAND | 7 | 15 | 14 | Small Blind 0/110000 | PLAY_HAND {"card_indices":[1,2,4,7,8]} | Pair KK (lucky KS first) + red fillers JD 5H 4H, held JC TS 7S all black -> x3 est 40752 (> Two Pai… | 26s |
| 7807 | port-7807 | claude-opus-5-5 | 9IIGB2FF | 8 | SELECTING_HAND | 8 | 13 | 39 | Crimson Heart 166500/400000 | PLAY_HAND {"card_indices":[2,3,5,6,8]} | Two Pair KKJJ est 95k (+steel 3H held x1.5), disabled Even Steven is irrelevant for KKJJ; need 2335… | 44s |
| 7809 | port-7809 | claude-opus-5-5 | H8E931PC | 8 | BLIND_SELECT | 1 | 2 | 1 | The Goad (600) | SELECT_BLIND | boss The Goad 600, spades debuffed; Half Joker pairs ~500-900 | 8s |
| 7810 | port-7810 | claude-sonnet-5-5 | CCLZQ4S8 | 8 | SHOP | 3 | 5 | 13 | Small Blind (3200) | SHOP_BUY_BOOSTER {"slot":1} | Celestial pack leaves (floor ); Mercury levels Pair main hand (+15 chips on ~28) | 6s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 17 | 0 | 17 | 0 | 0 | 3.71 | 7 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 74 | 0 | 74 | 0 | 0 | 3.7 | 8 |
| claude-sonnet-5-5 | 8 | Black | 36 | 0 | 35 | 0 | 1 | 3.08 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | B6KZC39M | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 207920/400000 | [7807_B6KZC39M.md](runs/7807_B6KZC39M.md) |
| 2 | E57ZB14D | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 249600/400000 | [7805_E57ZB14D.md](runs/7805_E57ZB14D.md) |
| 3 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 4 | A5LJXXMW | claude-opus-5-5 | 8 | Black | loss | 8 | Crimson Heart 275896/400000 | [7804_A5LJXXMW.md](runs/7804_A5LJXXMW.md) |
| 5 | YJGGELMB | claude-opus-5-5 | 8 | Black | loss | 7 | The Manacle 25312/220000 | [7806_YJGGELMB.md](runs/7806_YJGGELMB.md) |
| 6 | Z6ZJWRC4 | claude-opus-5-5 | 8 | Black | loss | 7 | Big Blind 146453/165000 | [7809_Z6ZJWRC4.md](runs/7809_Z6ZJWRC4.md) |
| 7 | MKHAVQ6W | claude-fable-5-1 | 8 | Black | loss | 7 | The Eye 37553/220000 | [7802_MKHAVQ6W.md](runs/7802_MKHAVQ6W.md) |
| 8 | 3IDYS1SA | claude-fable-5-1 | 8 | Black | loss | 6 | Big Blind 87529/90000 | [7802_3IDYS1SA.md](runs/7802_3IDYS1SA.md) |
| 9 | 26ARMPG1 | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 48586/90000 | [7807_26ARMPG1.md](runs/7807_26ARMPG1.md) |
| 10 | ZJZ9YLCM | claude-opus-5-5 | 8 | Black | loss | 6 | Big Blind 87251/90000 | [7806_ZJZ9YLCM.md](runs/7806_ZJZ9YLCM.md) |

### Data validity

- Player runs: 142 files in manifest; schema_ok 142, schema invalid 0; replay_ok 128, replay failed 0, awaiting replay 3, open/unended 11; quarantined 0; not yet in manifest 0.
- Player-run replay verdicts by host: headless ok 34 / failed 0; gui (live) ok 99 / failed 0; cross-checked by both 5, disagreeing 0.
- All files (incl. fuzz + replays): 314; schema_ok 312; replay_ok 134 (headless 34, gui 105); replay failed 0; awaiting replay 166; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7778 | 1 | 1 | 0 |
| port-7805 | 1 | 1 | 1061 |
| port-7807 | 1 | 1 | 1256 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 608 |
| port-7802 | 0 | 0 | 700 |
| port-7803 | 0 | 0 | 1138 |
| port-7804 | 0 | 0 | 790 |
| port-7806 | 0 | 0 | 1226 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 1041 |
| port-7810 | 0 | 0 | 1314 |
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
- 02:42 GoldAdvisor cli.py fd6e518e: wait_settled needs two identical settled reads 150 ms apart (pre-action state after an action; bridge analysis in local://bridge_patch_settle.md); type xMults never sold as "flat rentals" (7805 Trio); discards keep held Shoot the Moon Queens / Baron Kings; The Mark face-down held cards count as expected faces in est; every flat shop joker valued by its real deck gain (ante-1 Bootstraps/Ride the Bus/Supernova "adds ~0 now"); Celestial picks pair-family planets while the main hand is undecided. Tests 77.

