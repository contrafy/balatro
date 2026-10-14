# Swarm status

## Morning summary

_Updated 17:00._

**Headline: 482 Gold Stake runs on Black Deck, 4 wins (two Opus, one Sonnet, one Fable).**

- **Win 1:** Opus, seed `9IIGB2FF` (port 7807), beat the ante-8 boss Crimson Heart 402199/400000.
  - Trajectory `data/trajectories/2026-10-14/9IIGB2FF_7807_1791965962567.jsonl.gz`: 121 steps, 0 rejects, validated.
  - Replay-verified on both the headless engine and a live GUI instance: 121/121 steps plus the final state.
  - Build: flat chips/mult (Clever, Stuntman, Abstract, Even Steven) plus foil Obelisk (x3.6) and Throwback (x3.75).
  - Line: from ante 5 it skipped every Small and Big blind (9 skips) and fought only bosses.
  - Post-mortem: `docs/runs/7807_9IIGB2FF.md`. Its rules now open PLAYBOOK section 2a.
- **Win 2:** Sonnet 5.5, seed `2WEJC1IS` (port 7807), beat the ante-8 boss Cerulean Bell 431900/400000 with 4 hands
  left.
  - Trajectory `data/trajectories/2026-10-14/2WEJC1IS_7807_1791996446805.jsonl.gz`: 110 steps; the end record
    reads `outcome: win`, stake 8, bridge `cd4ee1e6`. Replay verification is queued in `dataops`.
  - Build: Blueprint + Half Joker at ante 1-2, so even 1-card hands scored. Throwback bought at ante 5 on the 4th
    reroll, with Blueprint copying it. Brainstorm copied Stuntman (+250 chips).
  - Line: it skipped the Small and Big from ante 3 on. Skip and Economy tags paid about $135, which funded the
    rerolls. One-card High Cards then scored 90-150k.
  - Post-mortem: `docs/runs/7807_2WEJC1IS.md`.
  - This was a goal for the night: the learnings, formalized as PLAYBOOK 2b plus the advisor, let a Sonnet-tier
    model win Gold.
- **Win 3:** Opus, seed `IFYMR9UX` (port 7802), beat the ante-8 boss Cerulean Bell 460120/400000.
  - Trajectory `data/trajectories/2026-10-14/IFYMR9UX_7802_1791997592383.jsonl.gz`: 192 steps; the end record
    reads `outcome: win`, stake 8, bridge `cd4ee1e6`.
  - Engine: Acrobat leftmost, with Blueprint directly left of Brainstorm. Blueprint copies Brainstorm, which copies
    Acrobat, for x27 on the last hand of every round. Hands 1-2 dig for that hand.
  - The advisor counted this copy chain as x9 and called the winning round UNWINNABLE. A fix is assigned to
    GoldAdvisor.
  - Post-mortem: `docs/runs/7802_IFYMR9UX.md`.
- **Win 4:** Fable 5.1, seed `7RFNYICY` (port 7801), beat the ante-8 boss Cerulean Bell 493996/400000.
  - Trajectory `data/trajectories/2026-10-14/7RFNYICY_7801_1792009663611.jsonl.gz`: 214 steps, 0 rejects.
  - Engine: Burglar (6 hands, 0 discards) + Card Sharp x3 on 4-5 repeated Pairs per round, foil Supernova (+1 mult
    per Pair played, +26 -> +61) and holo Bull (+2 chips per $). No joker-row xMult ever appeared that beat Burglar.
  - Line: money as score. It held $25+ for interest and skipped the Small for two Handy Tags (+$25 at ante 4, +$76
    at ante 8), which took the Bell from ~0.67x to 1.2x projected.
  - Advisor gaps found: it BARRED the eternal Walkie Talkie that became a core scorer, and its skip and SCORE CHECK
    logic did not price Bull's money-to-chips. Forwarded to GoldAdvisor.
  - Post-mortem: `docs/runs/7801_7RFNYICY.md`.
- **Antes reached (482 runs):** 1: 39, 2: 66, 3: 95, 4: 110, 5: 100, 6: 48, 7: 14, 8: 10. Wins: 1 in the first 191
  runs (by 07:50), 3 in the 291 runs since.
- **By model:**

  | model | runs | mean ante | reached ante 6+ | reached ante 8 | wins |
  |---|---|---|---|---|---|
  | Opus 5.5 | 246 | 4.09 | 49 | 6 | 2 |
  | Fable 5.1 | 33 | 4.24 | 7 | 1 | 1 |
  | Sonnet 5.5 | 176 | 3.61 | 16 | 3 | 1 |
  | Haiku 5.5 | 27 | 2.96 | 0 | 0 | 0 |

  - Fable (1 port since 05:30) takes about 3x longer per run than Opus; mean ante 4.24 and 1 win in 33 runs.
  - Sonnet improved steadily: its first 10 runs averaged ante 2.2, and its 10 runs before 11:00 averaged 5.3.
  - At 11:40 the swarm scaled to 18 players. Since 12:15, Haiku runs on 2 ports (7814, 7818): 27 runs, mean ante
    2.96, best ante 5. PLAYBOOK 2b plus the advisor have not yet carried Haiku past the ante 3-4 scaling wall.
  - 16:45: a 470-run study (`docs/analysis/rental_study.md`) found that flat rentals at antes 1-2 cut P(reach ante 5)
    from 57% to 38% (among runs reaching ante 3). Player agent definitions now hard-bar them.
- **Data:** 308 player trajectories, all schema-valid. 286 are replay-verified (headless and/or GUI); 0 replays
  failed and 0 were quarantined. The rest are live (19) or awaiting replay. `dataops` verifies headlessly, with a
  live spot-check on about 1 run in 10.
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
_Generated 2026-10-14 17:10:39 by `balatro-data status` (edits inside this block are overwritten). Player runs: 512 (495 finished, 17 live); fuzz seeds, `test-*` agents and replays excluded._

### Live runs (17)

| port | agent | model | seed | stake | phase | ante | round | $ | blind | last action | why | idle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7801 | port-7801 | claude-fable-5-1 | 8Q27ATWC | 8 | ROUND_EVAL | 2 | 4 | 1 | Small Blind (1000) | CASH_OUT | Small cleared 2914/1000 | 33s |
| 7802 | port-7802 | claude-opus-5-5 | V2HDUG4F | 8 | SELECTING_HAND | 2 | 6 | 0 | The Window 0/2000 | PLAY_HAND {"card_indices":[2,3,4,7,8]} | Full House KKK77 est 888, solver best p0.32 of 2000 | 4s |
| 7803 | port-7803 | claude-opus-5-5 | AF96E3ER | 8 | SHOP | 1 | 1 | 4 | Small Blind (300) | SHOP_BUY_BOOSTER {"slot":1} | Buffoon -> /bin/bash; 0 scorers, Smiley is a flat rental (hard-barred at ante 1-2); SIM 0.25 vs 0.1… | 3s |
| 7804 | port-7804 | claude-opus-5-5 | NPMBQNI1 | 8 | ROUND_EVAL | 1 | 1 | 4 | Small Blind (300) | CASH_OUT | small cleared, cash out | 4s |
| 7805 | port-7805 | claude-opus-5-5 | 455ESHT5 | 8 | BLIND_SELECT | 3 | 6 | 6 | Big Blind (4800) | SELECT_BLIND | play Big 4800; need the post-Big shop (Uncommon tag joker) before The Mouth | 6s |
| 7806 | port-7806 | claude-opus-5-5 | T7PPVCEX | 8 | PACK_OPENING | 5 | 10 | 18 | Small Blind (25000) | SELECT_PACK_CARD {"index":1} | no Mercury/Pluto; Uranus levels Two Pair (Clever +80), my third type for The Eye | 33s |
| 7808 | port-7808 | claude-sonnet-5-5 | AHX6JJ6F | 8 | BLIND_SELECT | 2 | 5 | 1 | The Mark (2000) | SELECT_BLIND | boss The Mark 2000; Riff-raff triggers | 9s |
| 7809 | port-7809 | (unknown) | LATY9V82 | 8 | BLIND_SELECT | 5 | 14 | 1 | The Needle (25000) | SELECT_BLIND | play boss The Needle 25000 (one hand) | 78s |
| 7810 | port-7810 | claude-sonnet-5-5 | PBATS6ST | 8 | SELECTING_HAND | 3 | 9 | 0 | The Mouth 0/6400 | DISCARD {"card_indices":[3,5,6,7,8]} | solver p 0.49 vs 0.28 rule: keep QC TD 8D (face + even ranks, 11 outs to Two Pair worth ~3-4k); Mou… | 18s |
| 7811 | port-7811 | claude-sonnet-5-5 | V7M2DYH4 | 8 | ROUND_EVAL | 4 | 8 | 13 | The Pillar (18000) | CASH_OUT | cash out Pillar | 2m |
| 7812 | port-7812 | claude-sonnet-5-5 | DI1851LB | 8 | ROUND_EVAL | 2 | 4 | 4 | Small Blind (1000) | CASH_OUT | cash out Small ante 2 | 25s |
| 7813 | port-7813 | claude-sonnet-5-5 | M5VQEKU4 | 8 | ROUND_EVAL | 4 | 10 | -1 | Big Blind (13500) | CASH_OUT | cash out ante 4 Big | 24s |
| 7814 | port-7814 | claude-haiku-5-5 | AJQQDHL9 | 8 | SELECTING_HAND | 2 | 5 | 0 | Big Blind 0/1500 | DISCARD {"card_indices":[5,8]} | Pair 4s est 306 vs need 1500: keep the pair plus QC JC 9D 8H for a draw, discard 7C and 2S (advice … | 8s |
| 7815 | port-7815 | claude-sonnet-5-5 | FPKFX7AQ | 8 | SELECTING_HAND | 4 | 12 | 2 | The Wheel 0/18000 | PLAY_HAND {"card_indices":[2,3,5,6,7]} | solver top p 0.49: Pair 66 est 3718 + fillers TD 9C 7C draw 5 new cards, keep QH 8H 4H and the disc… | 2s |
| 7816 | port-7816 | claude-sonnet-5-5 | YKQMDZUK | 8 | SHOP | 6 | 12 | 10 | Big Blind (90000) | SHOP_BUY_BOOSTER {"slot":1} | Celestial for Mercury (Pair L5); 0 -> ; next-ante ratio 0.72 so levels matter | 10s |
| 7817 | port-7817 | claude-opus-5-5 | E9S54C11 | 8 | SELECTING_HAND | 5 | 11 | 2 | Big Blind 0/37500 | DISCARD {"card_indices":[1,2,3,5,8]} | need 37500; solver best p 0.20: keep 9S 55, dig 5 for Queens/trips (also arms Summit) | 8s |
| 7818 | port-7818 | claude-haiku-5-5 | EJS7KI8Y | 8 | BLIND_SELECT | 4 | 10 | 0 | Big Blind (13500) | SELECT_BLIND | Big Blind 13500 (ante 4): never skip; /bin/bash money, 4 jokers, Two Pair L2 and Pair L2; final-han… | 0s |

### Results by model x stake x deck

| model | stake | deck | runs | wins | losses | abandoned | unfinished | mean ante | max ante |
|---|---|---|---|---|---|---|---|---|---|
| (unknown) | 1 | Red | 5 | 0 | 3 | 1 | 1 | 1.4 | 2 |
| claude-fable-5-1 | 8 | Black | 33 | 1 | 32 | 0 | 0 | 4.24 | 8 |
| claude-haiku-5-5 | 8 | Black | 28 | 0 | 28 | 0 | 0 | 3.04 | 5 |
| claude-opus-4 | 1 | Black | 1 | 0 | 0 | 0 | 1 | 4.0 | 4 |
| claude-opus-5-5 | 8 | Black | 249 | 2 | 247 | 0 | 0 | 4.08 | 8 |
| claude-sonnet-5-5 | 8 | Black | 179 | 1 | 178 | 0 | 0 | 3.64 | 8 |

### Deepest runs

| # | seed | model | stake | deck | outcome | ante | blind | post-mortem |
|---|---|---|---|---|---|---|---|---|
| 1 | 7RFNYICY | claude-fable-5-1 | 8 | Black | win | 8 | Cerulean Bell 493996/400000 | [7801_7RFNYICY.md](runs/7801_7RFNYICY.md) |
| 2 | IFYMR9UX | claude-opus-5-5 | 8 | Black | win | 8 | Cerulean Bell 460120/400000 | [7802_IFYMR9UX.md](runs/7802_IFYMR9UX.md) |
| 3 | 9IIGB2FF | claude-opus-5-5 | 8 | Black | win | 8 | Crimson Heart 402199/400000 | [7807_9IIGB2FF.md](runs/7807_9IIGB2FF.md) |
| 4 | 2WEJC1IS | claude-sonnet-5-5 | 8 | Black | win | 8 | Cerulean Bell 431900/400000 | [7807_2WEJC1IS.md](runs/7807_2WEJC1IS.md) |
| 5 | B6KZC39M | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 207920/400000 | [7807_B6KZC39M.md](runs/7807_B6KZC39M.md) |
| 6 | E57ZB14D | claude-opus-5-5 | 8 | Black | loss | 8 | Amber Acorn 249600/400000 | [7805_E57ZB14D.md](runs/7805_E57ZB14D.md) |
| 7 | ME9AMTUQ | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 152568/400000 | [7812_ME9AMTUQ.md](runs/7812_ME9AMTUQ.md) |
| 8 | ZY6GJXIG | claude-sonnet-5-5 | 8 | Black | loss | 8 | Crimson Heart 158620/400000 | [7810_ZY6GJXIG.md](runs/7810_ZY6GJXIG.md) |
| 9 | A5LJXXMW | claude-opus-5-5 | 8 | Black | loss | 8 | Crimson Heart 275896/400000 | [7804_A5LJXXMW.md](runs/7804_A5LJXXMW.md) |
| 10 | FWWIECQF | claude-opus-5-5 | 8 | Black | loss | 8 | Verdant Leaf 224688/400000 | [7805_FWWIECQF.md](runs/7805_FWWIECQF.md) |

### Data validity

- Player runs: 512 files in manifest; schema_ok 512, schema invalid 0; replay_ok 491, replay failed 0, awaiting replay 3, open/unended 18; quarantined 0; not yet in manifest 0.
- Player-run replay verdicts by host: headless ok 397 / failed 0; gui (live) ok 139 / failed 0; cross-checked by both 45, disagreeing 0.
- All files (incl. fuzz + replays): 725; schema_ok 723; replay_ok 497 (headless 397, gui 145); replay failed 0; awaiting replay 207; quarantined 2.

### Rejects per agent

| agent | rejects | runs with rejects | steps |
|---|---|---|---|
| BridgeCore | 3 | 1 | 63 |
| port-7805 | 2 | 2 | 3164 |
| port-7778 | 1 | 1 | 0 |
| port-7802 | 1 | 1 | 2823 |
| port-7803 | 1 | 1 | 3253 |
| port-7804 | 1 | 1 | 2914 |
| port-7807 | 1 | 1 | 3523 |
| ? | 0 | 0 | 60 |
| CliSwarm | 0 | 0 | 107 |
| port-7801 | 0 | 0 | 2006 |
| port-7806 | 0 | 0 | 3308 |
| port-7808 | 0 | 0 | 1198 |
| port-7809 | 0 | 0 | 3319 |
| port-7810 | 0 | 0 | 3684 |
| port-7811 | 0 | 0 | 929 |
| port-7812 | 0 | 0 | 982 |
| port-7813 | 0 | 0 | 944 |
| port-7814 | 0 | 0 | 954 |
| port-7815 | 0 | 0 | 962 |
| port-7816 | 0 | 0 | 981 |
| port-7817 | 0 | 0 | 862 |
| port-7818 | 0 | 0 | 965 |
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
- 11:29-12:19 GoldAdvisor cli.py 410b6284 -> b2ef5a12 -> 43fd94f6 -> 81b98e61 -> 88851418 -> 2b37cc29 -> 7c5eec8c: ships gated (tests + sweep + SIM smoke, abort on mid-check edits). Any 2nd rental before ante 6 barred unless both xMult / bundled sell (combo SIM rows) / +0.30 with money path >= 0; negative money paths barred; swaps need +0.10, never into off-hand or permanent-xMult->perishable; SIM NOISE regime; EMERGENCY floor off; early made-hand-at-pace PLAY + 0.10/n>=300 break margin; phase-change waits after blind/endshop/cash/pack and played-card waits after play/discard; Loyalty from counters (calibrated); Cerulean Bell forced card; name guard tiers; order hill-climb; face-down bounds cache; WINNING LINE 2 in PLAYBOOK. Tests 101.
- 12:24-12:43 GoldAdvisor cli.py 7c5eec8c -> 8cc93546 -> c57e377e -> 295a2619: 2nd rental before ante 5 only bundled with selling a rental (shop + packs; regression tests per path), ante 5 needs both-xMult or SIM +0.15 with money path >= 0; SCORE CHECK / TIGHT from DrawSolver's round_score_quantiles (discards, boss constraints); low-confidence solver leads switch at +0.20 with n >= 300 (Acrobat); PACE counts Acrobat; EMERGENCY ranks joker views over non-joker packs; Buffoon-tag skip at ante 4-6 with 0 xMult; reroll keeps $5-6; Big-skip names its 2b exception. Tests 103.
- 12:49-15:46 GoldAdvisor cli.py 295a2619 -> ... -> 75a9765b -> 660ed0b9 -> d1aa6420 -> 5e015925 -> 0ef7f82a -> 6648f1d9 -> 5a316d6c (+ next): `buy pack N`/`sell joker N`/`use tarot N` area words remapped, word next to a slot = name guard; `order ... --expect "A,B,C"` refuses on a changed joker row (PKWI29QQ); SCORE CHECK prints THIS ANTE (real boss chips incl. Wall/Violet, current jokers, boss rule via rsq boss=) and NEXT ANTE ratios; est: Baseball ignores copies of Uncommons (L28P5GTT), Stone cards have no rank/suit, Mime/Red-seal held retriggers; Pillar ante plays the fewest/lowest clearing cards + played-card ids tracked for rsq debuff_ids; Death prints MOVE then PICK with post-move indices; eternal rental allowed at 0 scorers ante 1-2; 2nd-eternal bar lifts at SIM +0.15 / est +50%; Red Card pack skips; Director's Cut needs $10 left; boss-dead offers (Half Joker vs Psychic, faces vs Plant, suit tarots vs suit bosses) lose NEEDED NOW. Tests 109.
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
- 12:15 Second Gold win: Sonnet, `2WEJC1IS`. Following the plan of "Sonnet/Haiku win Gold, then switch decks",
  7814 becomes a Haiku 5.5 port, to test whether PLAYBOOK 2b plus the advisor carry the weakest tier. Gold
  continues on all ports until Haiku has a meaningful sample. The deck switch waits for the user's call.
- 13:55-15:00 A third account-wide 429 rate-limit episode hit with 18 players plus 2 workers.
  `retry.waitForUsageReset` absorbed it: every agent paused and resumed, so some runs show 75-85 min durations. The
  account limit, not the machine, bounds throughput at this concurrency. The machine held steady: 9+ GB RAM free,
  GPU 75-92%.
- 15:46-16:14 GoldAdvisor cli.py 5a316d6c -> f2e87e2b: skips for non-score tags (Coupon/Economy/Investment/D6/Juggle)
  only when this ante's boss round simulates >= 1.25x its chips (3 runs in 15 min died to economy-tag skips while
  TIGHT); EMERGENCY with $4+ never prints a bare LEAVE; NEEDED NOW needs SIM +0.10; 2nd-eternal bars lift at
  SIM +0.15 / est +50% (they had barred eternal Abstract, Half Joker and Smeared on the best pick); made-hand guard is
  a 2-standard-error test with a 400-sample re-measure (the flat n >= 300 rule failed both ways: IX9HA65T, 3IW3CJIZ);
  boss-aware NEEDED NOW from the first shop of the ante (Half Joker vs The Psychic); Pillar plays the fewest cards;
  Fortune Teller, Blue Joker (half the draw pile), Gros Michel / Popcorn / Ice Cream caps. Tests 109.
  DrawSolver: Obelisk-aware round policy (don't reset it mid-round), `boss=` and `debuff_ids=` in
  round_score_quantiles; Card Sharp/Acrobat repeat lines already modelled (95k/126k/137k vs 126-135k real).
  PlaybookCurator refreshed 2b from runs 271-437 and compacted it to 136 lines (skip gates, rental sell trigger,
  reroll floor, boss known at ante start, copier order from both new wins, Card Sharp repeats, Verdant Leaf).
  Stats at 16:14: Opus 236 runs / 2 wins / mean ante 4.09; Sonnet 157 / 1 / 3.64; Fable 32 / 0 / 4.12;
  Haiku 22 / 0 / 3.00 (max 5). Latest ante-8 loss: FWWIECQF (Opus, Verdant Leaf 224688/400000).

