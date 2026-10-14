# Swarm status

## Morning summary

_Updated 07:50._

**Headline: 191 Gold Stake runs on Black Deck, 1 win.**

- **The win:** Opus, seed `9IIGB2FF` (port 7807), beat the ante-8 boss Crimson Heart 402199/400000.
  - Trajectory `data/trajectories/2026-10-14/9IIGB2FF_7807_1791965962567.jsonl.gz`: 121 steps, 0 rejects, validated.
  - Replay-verified on both the headless engine and a live GUI instance: 121/121 steps plus the final state.
  - Build: flat chips/mult (Clever, Stuntman, Abstract, Even Steven) plus foil Obelisk (x3.6) and Throwback (x3.75).
  - Line: from ante 5 it skipped every Small and Big blind (9 skips) and fought only bosses.
  - Post-mortem: `docs/runs/7807_9IIGB2FF.md`. Its rules now open PLAYBOOK section 2a.
- **Antes reached:** 1: 24, 2: 27, 3: 35, 4: 37, 5: 41, 6: 15, 7: 7, 8: 5. Of the five ante-8 runs, one won; the
  losses were Crimson Heart x2 and Amber Acorn x2.
- **By model:**

  | model | runs | mean ante | reached ante 6+ | reached ante 8 | wins |
  |---|---|---|---|---|---|
  | Opus 5.5 | 127 | 3.87 | 21 | 4 | 1 |
  | Fable 5.1 | 22 | 3.86 | 3 | 0 | 0 |
  | Sonnet 5.5 | 42 | 3.31 | 3 | 1 | 0 |

  Fable was no better than Opus and took about 3x longer per run, so it went from 2 ports to 1 at 05:30. Sonnet
  improved as the advisor improved: its first 10 runs averaged ante 2.2, its last 10 averaged 3.9.
- **Data:** 204 player trajectories, all schema-valid. 193 are replay-verified (headless and/or GUI), 0 replays
  failed, 0 quarantined, and the rest are live or awaiting replay. `dataops` now verifies headlessly with a live
  spot-check on about 1 run in 10.
- **Tooling built overnight (all live in `cli.py`):**
  - Sticker-aware Gold advisor.
  - Monte Carlo play/discard solver with calibrated p_clear (`solver.py`).
  - Shop simulator that ranks shop options by the chance of clearing the next 3 blinds (`shop_sim.py`, now the primary
    shop ranking).
  - Data analysis in `docs/GOLD_ANALYSIS.md`.
- **Why runs die:** under-scaled at antes 3-5 (no lasting xMult), broke from Gold rent plus the $0 Small Blind, and
  boss counters at ante 7-8 (The Eye, Crimson Heart, Amber Acorn).
- **Incidents:**
  - Two account-wide 429 rate limits (about 23:05 and 03:30). The first killed every agent; I revived the
    interrupted runs mid-game. The second was absorbed by `retry.waitForUsageReset`.
  - One recorded junk action: run `XRWKX6AS`, step 117 (a stray sell), noted in `data/swarm_results.jsonl`
    under `junk_steps`.
- **The "pre-action state" reports were client-side, not the bridge.** SwarmOps checked about 48k tight-loop reads:
  0 stale reads and 0 stale actions accepted. The cause was players running two `b.sh` commands in parallel on one
  port. Fixes: a per-port CLI lock (GoldAdvisor) and an explicit rule in the player definitions. No data impact.
- **Decisions for you:**
  - An optional 2-frame post-action guard for the bridge (the patch is in SwarmOps' report). It changes `bridge_hash`.
  - Whether to keep Sonnet on Gold or move it down a stake.
  - Whether to persist the session settings changed overnight.

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 12:10:43 by `balatro-data status` (edits inside this block are overwritten). Player runs: 308 (290 finished, 18 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (18)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | YRXUVUPU | 8 | SELECTING_HAND | 1 | 3 | 2 | The Pillar 0/600 | DISCARD {"card_indices":[3,6,7,8]} | Still Two Pair 116 vs 600; last discard: keep AA88 and draw 4 again for the FH (p 0.36), solver p 0… | 55s |
| 7802 | port-7802 | claude-opus-5-5 | IFYMR9UX | 8 | BLIND_SELECT | 2 | 3 | 3 | Big Blind (1500) | SELECT_BLIND | Big 1500, never skip Big | 13s |
| 7803 | port-7803 | claude-opus-5-5 | 6UYKULXZ | 8 | SELECTING_HAND | 6 | 13 | 1 | Big Blind 4340/90000 | PLAY_HAND {"card_indices":[1,2,4,5]} | solver: no line clears 85660 (best exp ~41k); Two Pair AA66 est 2912 registers Two Pair for Card Sh… | 7s |
| 7804 | port-7804 | claude-opus-5-5 | N6ILXWVS | 8 | SHOP | 5 | 10 | 20 | Small Blind (25000) | SELL_JOKER {"index":5} | sell Scholar (fires only on Aces) for Supernova: +14 mult now on Pair (14 plays), growing; ratio 0.… | 3s |
| 7805 | port-7805 | claude-opus-5-5 | PANHN5IE | 8 | ROUND_EVAL | 1 | 1 | 4 | Small Blind (300) | CASH_OUT | small cleared 316/300, collect | 7s |
| 7806 | port-7806 | claude-opus-5-5 | 1VG6CJBW | 8 | SELECTING_HAND | 3 | 8 | 13 | The Fish 0/6400 | PLAY_HAND {"card_indices":[1,2,6,7,8]} | Two Pair KK55 est 3200 = half of 6400, keep QJ + 2 discards (discard draws come face up under Fish)… | 7s |
| 7807 | port-7807 | claude-sonnet-5-5 | 2WEJC1IS | 8 | ROUND_EVAL | 8 | 10 | 92 | The Window (400000) | CASH_OUT | cash out Window | 9s |
| 7808 | port-7808 | claude-sonnet-5-5 | NK1V53BU | 8 | SHOP | 3 | 5 | 4 | Big Blind (4800) | SHOP_BUY_BOOSTER {"slot":1} | Free Jumbo Arcana pack (Coupon): pick 2 of 5, hoping Hermit/Strength/Justice; /bin/bash | 7s |
| 7809 | port-7809 | claude-sonnet-5-5 | ZSI1CNNI | 8 | SELECTING_HAND | 2 | 4 | 3 | Big Blind 0/1500 | PLAY_HAND {"card_indices":[1,2,5,6,8]} | Heart Flush est 1242 of 1500; remaining 258 over 2 hands with a discard left | 12s |
| 7810 | port-7810 | claude-sonnet-5-5 | 74UKW6TD | 8 | SELECTING_HAND | 3 | 8 | 4 | The Window 832/6400 | PLAY_HAND {"card_indices":[2,3,7,8]} | Need 5568, 2 hands, 0 discards: dig play KC JD 6D 3C (junk), keep AH TH TC 8H for two pair/trips/FH… | 7s |
| 7811 | port-7811 | claude-sonnet-5-5 | SH1F9PV5 | 8 | SELECTING_HAND | 5 | 15 | -5 | The Wall 0/100000 | DISCARD {"card_indices":[1,2,4,6]} | Wall 100000 unwinnable by sim (best ~54k); maximize score: keep TC 4C (even, 10) and dig for pairs … | 2s |
| 7812 | port-7812 | claude-sonnet-5-5 | IJF5DIGF | 8 | ROUND_EVAL | 4 | 8 | 8 | The Club (18000) | CASH_OUT | cash out Club | 13s |
| 7813 | port-7813 | claude-sonnet-5-5 | 3YR6XX1M | 8 | SELECTING_HAND | 3 | 6 | -3 | Big Blind 0/4800 | PLAY_HAND {"card_indices":[1,2,8,7,6]} | Pair QQ est 3760 vs need 4800; fillers 2H 4H 6D, keep 4H... later hands + 2 discards, p>=0.99 | 7s |
| 7814 | port-7814 | claude-opus-5-5 | UZSEX8F5 | 8 | SHOP | 3 | 6 | 5 | Big Blind (4800) | SELL_JOKER {"index":3} | sell rental Shoot the Moon: Stencil goes x3->x4 (equal avg score w/o Queen dependence) and saves /r… | 20s |
| 7815 | port-7815 | claude-sonnet-5-5 | GX6IX2TY | 8 | SELECTING_HAND | 2 | 6 | 4 | The Arm 0/2000 | PLAY_HAND {"card_indices":[1,2,3,4,5]} | Flush hearts est 1344 of 2000; remaining 656 via two L1 hands (pair ~624 + other), 1 discard kept | 2s |
| 7816 | port-7816 | claude-sonnet-5-5 | FVPWB9XC | 8 | SELECTING_HAND | 1 | 2 | 1 | Big Blind 112/450 | PLAY_HAND {"card_indices":[3,4,5,7]} | dig: keep AS QS 7S 3S (4 spades), draw 4 for flush p 0.60; then Chariot steel on spare card x1.5 ma… | 7s |
| 7817 | port-7817 | claude-opus-5-5 | D5DGN1SY | 8 | ROUND_EVAL | 1 | 1 | 4 | Small Blind (300) | CASH_OUT | cash out Small | 5s |
| 7818 | port-7818 | claude-opus-5-5 | INVVBG6M | 8 | SHOP | 4 | 7 | 18 | Big Blind (13500) | SHOP_BUY_BOOSTER {"slot":1} | Mega Buffoon -> 0, SIM +0.29: replace Arrowhead (perishes after this ante) with a permanent scorer/… | 30s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 28 | 0 | 28 | 0 | 0 | 4.11 | 7 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 191 | 1 | 190 | 0 | 0 | 3.94 | 8 |
| claude-sonnet-5-5 | 8 | Black | 65 | 0 | 65 | 0 | 0 | 3.49 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | 9IIGB2FF | claude-opus-5-5 | 8 | Black | win | 8 | Crimson Heart 402199/400000 | [7807_9IIGB2FF.md](runs/7807_9IIGB2FF.md) |
| 2 | B6KZC39M | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 207920/400000 | [7807_B6KZC39M.md](runs/7807_B6KZC39M.md) |
| 3 | E57ZB14D | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 249600/400000 | [7805_E57ZB14D.md](runs/7805_E57ZB14D.md) |
| 4 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 5 | A5LJXXMW | claude-opus-5-5 | 8 | Black | loss | 8 | Crimson Heart 275896/400000 | [7804_A5LJXXMW.md](runs/7804_A5LJXXMW.md) |
| 6 | CLA5SVN7 | claude-opus-5-5 | 8 | Black | loss | 7 | The Ox 79619/220000 | [7803_CLA5SVN7.md](runs/7803_CLA5SVN7.md) |
| 7 | YJGGELMB | claude-opus-5-5 | 8 | Black | loss | 7 | The Manacle 25312/220000 | [7806_YJGGELMB.md](runs/7806_YJGGELMB.md) |
| 8 | X5MG1LC2 | claude-opus-5-5 | 8 | Black | loss | 7 | Big Blind 158968/165000 | [7802_X5MG1LC2.md](runs/7802_X5MG1LC2.md) |
| 9 | I9RJP8E5 | claude-opus-5-5 | 8 | Black | loss | 7 | The Flint 157176/220000 | [7806_I9RJP8E5.md](runs/7806_I9RJP8E5.md) |
| 10 | Z6ZJWRC4 | claude-opus-5-5 | 8 | Black | loss | 7 | Big Blind 146453/165000 | [7809_Z6ZJWRC4.md](runs/7809_Z6ZJWRC4.md) |

### Data validity

- Player runs: 308 files in manifest; schema_ok 308, schema invalid 0; replay_ok 286, replay failed 0, awaiting replay 3, open/unended 19; quarantined 0; not yet in manifest 0.
- Player-run replay verdicts by host: headless ok 192 / failed 0; gui (live) ok 119 / failed 0; cross-checked by both 25, disagreeing 0.
- All files (incl. fuzz + replays): 501; schema_ok 499; replay_ok 292 (headless 192, gui 125); replay failed 0; awaiting replay 187; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7805 | 2 | 2 | 2380 |
| port-7778 | 1 | 1 | 0 |
| port-7802 | 1 | 1 | 2039 |
| port-7803 | 1 | 1 | 2440 |
| port-7804 | 1 | 1 | 2093 |
| port-7807 | 1 | 1 | 2600 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 1482 |
| port-7806 | 0 | 0 | 2510 |
| port-7808 | 0 | 0 | 375 |
| port-7809 | 0 | 0 | 2387 |
| port-7810 | 0 | 0 | 2764 |
| port-7811 | 0 | 0 | 109 |
| port-7812 | 0 | 0 | 112 |
| port-7813 | 0 | 0 | 110 |
| port-7814 | 0 | 0 | 85 |
| port-7815 | 0 | 0 | 112 |
| port-7816 | 0 | 0 | 84 |
| port-7817 | 0 | 0 | 81 |
| port-7818 | 0 | 0 | 93 |
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
- 06:03-08:19 GoldAdvisor cli.py f1cf73e0 -> d0ff7593 -> 8d140a11 -> 34c70949 -> 5215167a -> c197340f -> c1da2274 -> 695b8716: winning-run fixes (eternal rentals capped, Obelisk growth xMult + strict-reset throwaway guard, Throwback skip plan Small+Big, WINNING LINE in PLAYBOOK 2a, reading list item in player agents); hard main-hand invariants (2x plays / +3 levels) + run-keyed hysteresis + 3-play minimum; SIM PRIMARY for jokers/planets/cards/packs in shopadvise and pack advise (rule score breaks SIM ties, decides packs-without-sim/vouchers/tarots/counters; hard money/sticker rules kept; LEAVE only when the SIM says the pick hurts; gain >= 0.10 never LEAVE); per-port CLI lock + id-based retry rebuild (overlapping commands caused the stale reads); pack pick index = current listing (cache remap reverted 08:19); Joker Stencil / Baseball / Seeing Double(Wild) / Abstract(disabled) in est; Chad/Photograph REORDER (est index order fixed); Arcana pack advice; Mail-In, Idol, To Do targets shown; Credit Card debt/$0 items; Mark/Crimson/Mouth/Psychic fixes. Tests 98.
- 02:42 GoldAdvisor cli.py fd6e518e: wait_settled needs two identical settled reads 150 ms apart (pre-action state after an action; bridge analysis in local://bridge_patch_settle.md); type xMults never sold as "flat rentals" (7805 Trio); discards keep held Shoot the Moon Queens / Baron Kings; The Mark face-down held cards count as expected faces in est; every flat shop joker valued by its real deck gain (ante-1 Bootstraps/Ride the Bus/Supernova "adds ~0 now"); Celestial picks pair-family planets while the main hand is undecided. Tests 77.
- 03:16 GoldAdvisor cli.py 1ab1c6bf: solver ADVICE re-enabled on calibrated p (+0.05 over the rule pick; PLAY that clears now on p_model +0.03 or tied +$1); High Card always a candidate (Half Joker/Chad); joker_share also on deck deals (Half Joker carrier kept); scorer count by share >= 15% (Gluttonous/Stencil); Riff-raff 70 with free slots; core-gain rentals not crushed (Ramen x2); TIGHT keeps the $8 floor for Spectral/Standard; skip the Small when rent-broke; The Mark face-downs kept on discards.
- 03:30 GoldAdvisor cli.py 88b8a734: Amber Acorn: face-up jokers cached per port (data/.cli_cache), est under Acorn uses them, order range shown, 1-card probe + order inference from the score, then `b order`; Mystic Summit valued with discards burned; Steel/Gold/Blue-seal never fillers; pack: Swashbuckler valued with jokers owned, decaying jokers taken into free slots, rental under $7 penalized (rent blocks the next joker).
- 05:19 GoldAdvisor cli.py 84764033: last-action guard (data/.cli_cache/<port>_last_action.json: every command waits up to 5 s until the previous action's effect is visible); Joker Stencil modeled in est (x(empty+Stencils), only with an empty slot; card.lua) so slot-fillers show AVOID(-N%); ORDER FIRST verified by est over whole orders (Blueprint/Brainstorm copy targets); perished joker sold FIRST without hiding the ranking; SIM section in `b shopadvise` (shop_sim deltas, tie-break within 5 points, "SIM disagrees"); Throwback skip rule; Standard packs feed Hologram; Crimson Heart throwaway whenever the disabled joker is worth 1.5x; Acrobat final-hand est via est (Dusk); High Card throwaways excluded from main hand with Acrobat/Dusk; held-value cards never throwaways; solver low_n never drives ADVICE. Tests 82.
- 09:14-09:20 GoldAdvisor cli.py 695b8716 -> dec92399 -> 70db0a0b: slot-command name guard (`buy Clever` / `buy 1 --expect Clever`, target always echoed); shop SIM ranked by rent-adjusted p_adj (delta_adj, dead later shops shown); BUY yields to SIM when its best is nothing; permanent beats perishable/rental on SIM ties; Credit Card debt spendable for survival rerolls, 0-scorer reroll keeps $5; growth xMults never "flat rentals"; face-down cards discarded first; Throwback skip needs 1.6x on handicap bosses; perishable-carrier and broke skips; early planets discouraged with 0-1 scorers; Stencil/Wraith penalties; Madness/Dagger now SIM-modelled.
- 09:39 GoldAdvisor cli.py 70db0a0b -> d088f3c4: sell waits until the sold card leaves its area (it lingers while dissolving after money changes; 7805 stale-after-sell), `buy` re-polls /legal 4 s, slot-full rejections retried; test sell->buy race (fails on old, passes); Blueprint/Brainstorm copy target + ORDER FIRST; Obelisk tie warning; Raised Fist filler-aware est; The Arm prefers an L1/non-main clearing hand; Fool = its copy; cash-tag+rent skip; rental sells need share < 0.2; Riff-raff/Burglar/grown Obelisk kept; Burglar +3 hands in SCORE CHECK; Swashbuckler from ability.mult; eternal Troubadour/2nd eternal utility barred; SIM SATURATED -> rules decide. Tests 99.
- 10:15-10:36 GoldAdvisor cli.py d088f3c4 -> fac63418 -> b87ce459: shop/pack SIM ranked by DrawSolver's terminal value (delta_value); pack picks follow the SIM (tie 0.01), a free sticker-free joker is never skipped, sticker bars yield to +0.15 rent-adjusted; rental SELL FIRST simulated; 2nd permanent rental needs both xMult or a bundled sell; pair-family main-hand dominance (score-weighted); face-down EV line + rank intervals (House/Fish/Wheel); The Hook held discount; Blackboard x3 in SCORE CHECK; Misprint range fixed; Fool/Wheel/Hermit/Immolate/Wasteful values; Mr. Bones kept below SCORE CHECK 1.5; broke skip at ante 3-4; D6 note. Tests 99.
- 10:44-11:14 GoldAdvisor cli.py b87ce459 -> af77f098 -> e01d9f34 -> ee02206f -> e172b4f4 -> 50160a8f: boss-aware TIGHT (Water median deal x hands, Needle dug best x 1 hand; 1.25x before a boss); perishable/type-conditional buys need +0.07..0.12 SIM; Trio/Family engine overrides the play-count main hand; advise/shopadvise route by reached phase; +0.10 solver margin to break a made pair-family hand; Splash/Blackboard in SCORE CHECK; Campfire feed and Diet Cola Double-Tag flips; Director's Cut on Throwback plans; Death targets, Hermit/Wheel/Seed Money values; Flower Pot debuff bypass (card.lua), Seeing Double without; copier counts as xMult for the eternal-rental exception. Tests 99.
- 11:20 GoldAdvisor cli.py 50160a8f -> 410b6284: Obelisk-safe clearing plays + planets for the played (non-max) types; Throwback/Stencil classified as xMults (Throwback was still "useless, we never skip"); non-cash skips need best x hands >= the ante's boss; TIGHT 0-scorer reroll to $1 at stake 8; Manacle projection at hand size -1. Tests 99.
- 11:00 Model mix change: Sonnet's last 10 runs average ante 5.3 (7 of 10 reached ante 6), against Opus's last 30
  at 4.0 and Fable's last 8 at 4.5. Sonnet improved as the advisor and the PLAYBOOK 2b checklist matured, so
  7807 and 7809 move back to Sonnet as their runs finish, and idle 7808 restarts as Sonnet (no 429 since 03:30).
  That gives 10 players: 1 Fable (7801), 5 Opus (7802-7806), 4 Sonnet (7807-7810). Sonnet also costs less
  against the account rate limit.
- 11:40 Scaled up at the user's request (desktop apps closed): 8 new players on 7811-7818 (Sonnet 7811-7813,
  7815-7816; Opus 7814, 7817-7818). Total is 18 players: 1 Fable, 8 Opus, 9 Sonnet, plus the 7820 replay instance.
  At 19 instances: GPU 67%, 6.1 GB VRAM, 50 C; ~8.5 GB RAM free; CPU at 100%, with the Balatro instances using
  about 10 of 16 logical cores. CPU is the binding limit, so the swarm stays at 18. All instances now run at
  BelowNormal priority (`launch_instance.ps1` sets it) so the desktop stays responsive. Sweeps are capped at 3
  workers.

