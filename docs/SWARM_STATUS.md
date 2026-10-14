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
- **Decisions for you** (see the chat report):
  - Bridge v2.0.1: a post-action settle guard (players sometimes saw the pre-action state) and the To Do List check.
    This changes `bridge_hash`.
  - Whether to keep Sonnet on Gold or move it down a stake.
  - Whether to persist the session settings changed overnight.

## Auto-generated status

<!-- AUTO:BEGIN -->
_Generated 2026-10-14 07:45:45 by `balatro-data status` (edits inside this block are overwritten). Player runs: 204 (198 finished, 6 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (6)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | QS3DEH89 | 8 | PACK_OPENING | 4 | 7 | 3 | Big Blind (13500) | SELECT_PACK_CARD {"index":1} | Mercury: Pair L2, the repeatable type I lock/bank with (SIM +0.03, best remaining); indices re-read… | 26s |
| 7803 | port-7803 | claude-opus-5-5 | XDYYYR1Y | 8 | BLIND_SELECT | 4 | 9 | 3 | Small Blind (9000) | SELECT_BLIND | typical hand < boss/2, take Small 9000 and the shop | 2s |
| 7804 | port-7804 | claude-opus-5-5 | U6G7N65N | 8 | SHOP | 4 | 9 | 15 | Small Blind (9000) | SHOP_REROLL | EMERGENCY 0.27, 0 xMult, 2 free slots; shop has no scorer (Strength/Cloud9 do not add score): one r… | 18s |
| 7805 | port-7805 | claude-opus-5-5 | RNVA7G3B | 8 | SHOP | 4 | 9 | 1 | Small Blind (9000) | SHOP_END | left | 17s |
| 7809 | port-7809 | claude-opus-5-5 | BKRXB8HX | 8 | SHOP | 1 | 1 | 6 | Small Blind (300) | SHOP_BUY {"slot":1} | foil Blue Joker = +154 chips on any hand; SIM p_next 1.00 vs 0.01; rental bridge, sell once 2 score… | 14s |
| 7810 | port-7810 | claude-sonnet-5-5 | 6XN584I7 | 8 | SELECTING_HAND | 4 | 10 | 4 | The Psychic 8874/18000 | PLAY_HAND {"card_indices":[1,2,4,5,8]} | Two Pair AATT + 2S filler est 9349 >= 9126 needed (previous est 8568 came in at 8874); 1 more hand … | 11s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 22 | 0 | 22 | 0 | 0 | 3.86 | 7 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 127 | 1 | 126 | 0 | 0 | 3.87 | 8 |
| claude-sonnet-5-5 | 8 | Black | 43 | 0 | 42 | 0 | 1 | 3.26 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | 9IIGB2FF | claude-opus-5-5 | 8 | Black | win | 8 | Crimson Heart 402199/400000 | [7807_9IIGB2FF.md](runs/7807_9IIGB2FF.md) |
| 2 | B6KZC39M | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 207920/400000 | [7807_B6KZC39M.md](runs/7807_B6KZC39M.md) |
| 3 | E57ZB14D | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 249600/400000 | [7805_E57ZB14D.md](runs/7805_E57ZB14D.md) |
| 4 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 5 | A5LJXXMW | claude-opus-5-5 | 8 | Black | loss | 8 | Crimson Heart 275896/400000 | [7804_A5LJXXMW.md](runs/7804_A5LJXXMW.md) |
| 6 | YJGGELMB | claude-opus-5-5 | 8 | Black | loss | 7 | The Manacle 25312/220000 | [7806_YJGGELMB.md](runs/7806_YJGGELMB.md) |
| 7 | X5MG1LC2 | claude-opus-5-5 | 8 | Black | loss | 7 | Big Blind 158968/165000 | [7802_X5MG1LC2.md](runs/7802_X5MG1LC2.md) |
| 8 | I9RJP8E5 | claude-opus-5-5 | 8 | Black | loss | 7 | The Flint 157176/220000 | [7806_I9RJP8E5.md](runs/7806_I9RJP8E5.md) |
| 9 | Z6ZJWRC4 | claude-opus-5-5 | 8 | Black | loss | 7 | Big Blind 146453/165000 | [7809_Z6ZJWRC4.md](runs/7809_Z6ZJWRC4.md) |
| 10 | MKHAVQ6W | claude-fable-5-1 | 8 | Black | loss | 7 | The Eye 37553/220000 | [7802_MKHAVQ6W.md](runs/7802_MKHAVQ6W.md) |

### Data validity

- Player runs: 204 files in manifest; schema_ok 204, schema invalid 0; replay_ok 193, replay failed 0, awaiting replay 3, open/unended 8; quarantined 0; not yet in manifest 0.
- Player-run replay verdicts by host: headless ok 99 / failed 0; gui (live) ok 107 / failed 0; cross-checked by both 13, disagreeing 0.
- All files (incl. fuzz + replays): 385; schema_ok 383; replay_ok 199 (headless 99, gui 113); replay failed 0; awaiting replay 175; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7805 | 2 | 2 | 1659 |
| port-7778 | 1 | 1 | 0 |
| port-7802 | 1 | 1 | 1303 |
| port-7803 | 1 | 1 | 1740 |
| port-7804 | 1 | 1 | 1372 |
| port-7807 | 1 | 1 | 1808 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 989 |
| port-7806 | 0 | 0 | 1760 |
| port-7808 | 0 | 0 | 145 |
| port-7809 | 0 | 0 | 1599 |
| port-7810 | 0 | 0 | 1941 |
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
- 03:16 GoldAdvisor cli.py 1ab1c6bf: solver ADVICE re-enabled on calibrated p (+0.05 over the rule pick; PLAY that clears now on p_model +0.03 or tied +$1); High Card always a candidate (Half Joker/Chad); joker_share also on deck deals (Half Joker carrier kept); scorer count by share >= 15% (Gluttonous/Stencil); Riff-raff 70 with free slots; core-gain rentals not crushed (Ramen x2); TIGHT keeps the $8 floor for Spectral/Standard; skip the Small when rent-broke; The Mark face-downs kept on discards.
- 03:30 GoldAdvisor cli.py 88b8a734: Amber Acorn: face-up jokers cached per port (data/.cli_cache), est under Acorn uses them, order range shown, 1-card probe + order inference from the score, then `b order`; Mystic Summit valued with discards burned; Steel/Gold/Blue-seal never fillers; pack: Swashbuckler valued with jokers owned, decaying jokers taken into free slots, rental under $7 penalized (rent blocks the next joker).
- 05:19 GoldAdvisor cli.py 84764033: last-action guard (data/.cli_cache/<port>_last_action.json: every command waits up to 5 s until the previous action's effect is visible); Joker Stencil modeled in est (x(empty+Stencils), only with an empty slot; card.lua) so slot-fillers show AVOID(-N%); ORDER FIRST verified by est over whole orders (Blueprint/Brainstorm copy targets); perished joker sold FIRST without hiding the ranking; SIM section in `b shopadvise` (shop_sim deltas, tie-break within 5 points, "SIM disagrees"); Throwback skip rule; Standard packs feed Hologram; Crimson Heart throwaway whenever the disabled joker is worth 1.5x; Acrobat final-hand est via est (Dusk); High Card throwaways excluded from main hand with Acrobat/Dusk; held-value cards never throwaways; solver low_n never drives ADVICE. Tests 82.

