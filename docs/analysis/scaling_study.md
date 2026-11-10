# Scaling at Black Deck Gold Stake (stake 8): which ante 2-4 decisions predict getting past ante 5

Generated 2026-10-14 from `data/manifest.jsonl` + trajectories (read-only analysis, same run filter as
`docs/analysis/rental_study.md`).

## Method

- **Runs:** manifest entries with deck `b_black`, stake 8, outcome `loss`/`win`, not quarantined, recorded by a swarm
  player (`agent` = `port-78xx`): 494 runs, each matched to `data/swarm_results.jsonl` by (seed, port) for its model.
  **Cohort = runs that reached ante 4: N = 291** (Opus 163, Sonnet 97, Fable 24, Haiku 7).
  Groups: **died at ante 4** (N=112), **died at ante 5** (N=107), **reached ante 6+** (N=72, incl. 4 wins).
  Final ante = ante the run died in; wins = 9. Every seed was played once (no seed repeats), so seed luck is not controlled.
- **Snapshot ("start of ante 5 or death"):** the first observation with ante >= 5 (always the ROUND_EVAL right after the
  ante-4 boss, i.e. the build that beat ante 4, before the ante-5 shop), or the final observation for runs that died at
  ante 4. Face-down jokers (Amber Acorn) are replaced by the last face-up joker list.
  A second snapshot at **ante-4 entry** (first observation with ante >= 4) is defined for all 291 runs.
- **Always-on xMult** (applies to every hand once owned): Cavendish, Ramen, Campfire; Stencil, Throwback, Hologram,
  Constellation, Madness, Vampire, Lucky Cat, Glass Joker, Caino, Yorick only when their current `ability.x_mult` > 1;
  Steel Joker only with >= 1 Steel card; Duo/Trio/Family/Order/Tribe only when the run's main hand contains that hand
  (Duo: Pair, Two Pair, 3oak, Full House, 4oak...; Tribe: Flush family; Order: Straight family); any **polychrome joker**
  (X1.5); **Blueprint/Brainstorm** when the copied joker is an always-on xMult (Blueprint = right neighbour,
  Brainstorm = leftmost). Debuffed jokers do not count.
- **Conditional xMult:** Card Sharp (2nd+ hand of a type in a round), Acrobat (last hand), Photograph (first face card),
  Seeing Double, Obelisk (resets), Blackboard, Loyalty Card, Ancient, Baron, Bloodstone, Baseball Card, Flower Pot,
  Idol, Triboulet, Driver's License, Hit the Road; plus hand-type xMults not matching the main hand, scaling xMults
  still at X1, and Blueprint/Brainstorm copying one of these.
- **Main hand** = hand with the most `played` in `hand_levels` (ties: higher level); its level is the main-hand level.
- **Permanent +mult** = owned +mult joker (Joker, Jolly/Zany/Mad/Crazy/Droll, suit jokers, Half, Summit, Misprint,
  Gros Michel, Abstract, Even Steven, Smiley, Walkie Talkie, Shoot the Moon, Popcorn, Fibonacci, Onyx, Raised Fist,
  Ride the Bus, Supernova, Green, Trousers, Red Card, Swashbuckler, Bootstraps, Scholar, ...) with neither rental nor
  perishable sticker (same definition as the rental study).
- **Spending window "antes 2-4"** = every shop whose observation shows ante 2, 3 or 4 (the shop after the ante-1 boss
  through the shop before the ante-4 boss). Cost is read from the item (`shop.jokers[slot].cost`,
  `shop.boosters[slot].cost`, `shop.reroll_cost`, voucher cost) at the buy action. Pack contents chosen from
  Arcana/Spectral/Celestial packs are counted as uses. **Shop exit $** = `money` at the `SHOP_END` action.
- **Sightings:** a joker card id shown in a shop row or an opened Buffoon pack at ante 2-4 that the run did not own
  yet, deduplicated by card id. "Bought" = that id appears in the owned jokers at any later point. "Unaffordable" =
  cost > money at every observation where it was on offer.
- **Bias control.** Died-at-4 runs have a truncated ante-4 window and a death-time snapshot, so ante 2-4 tables mix
  exposure with outcome. Each decision is therefore also tested on **landmark cohorts**: ante 2-3 behaviour among
  all 291 runs that reached ante 4 (outcome P(reach 5), P(reach 6)), and the ante-5-entry build among the 179 runs
  that reached ante 5 (outcome P(reach 6)). **Model-stratified diff** = per-model difference weighted by
  n_a*n_b/(n_a+n_b). p-values are two-proportion z-tests (unstratified). Money is partly an *outcome* of a strong
  build (more hands left, interest, economy jokers), so money effects are upper bounds on what banking alone buys.

## Headline

| comparison (cohort) | rates | model-strat. diff |
|---|---|---|
| >=1 always-on xMult at ante-5 entry vs 0 (reached 5) -> P(6) | 38/76 vs 34/103, p=0.022 | +16 pts |
| 2+ always-on xMult vs 0 (reached 5) -> P(6) | 11/14 vs 34/103, p=0.001 | +47 pts |
| main-hand level >=5 vs <5 at ante-5 entry -> P(6) | 12/17 vs 60/162, p=0.007 | +38 pts |
| >=1 always-on xMult at ante-4 entry vs 0 (reached 4) -> P(5) | 50/69 vs 129/222, p=0.032 | +14 pts |
| >=1 always-on xMult at ante-4 entry vs 0 (reached 4) -> P(6) | 26/69 vs 46/222, p=0.004 | +17 pts |
| never left an a2-3 shop under $5 vs did (reached 4) -> P(5) | 51/61 vs 128/230, p=0.000 | +28 pts |
| never left an a2-3 shop under $5 vs did (reached 4) -> P(6) | 26/61 vs 46/230, p=0.000 | +24 pts |
| rerolled but kept $>=5 vs rerolled below $5 -> P(6) | 26/76 vs 13/76, p=0.016 | +16 pts |
| Buffoon pack bought a2-3 vs none -> P(6) | 34/149 vs 38/142, p=0.436 | -4 pts |
| Arcana pack a2-3 keeping $>=5 vs leaving <$5 -> P(6) | 18/44 vs 1/20, p=0.004 | +36 pts |
| used Hermit/Temperance a2-4 vs not -> P(6) | 30/80 vs 42/211, p=0.002 | +17 pts |
| used Glass/Steel tarot a2-4 vs not -> P(6) | 13/41 vs 59/250, p=0.265 | +6 pts |
| reached $25 at an a2-3 exit vs max <$10 -> P(6) | 9/17 vs 25/145, p=0.001 | +33 pts |

## 1. Build at the start of ante 5 (or death)

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| always-on xMult (jokers + polychrome jokers), mean | 0.17 | 0.38 | 0.27 | 0.71 | +0.44 |
| >=1 always-on xMult | 18/112 = 16% | 38/107 = 36% | 56/219 = 26% | 38/72 = 53% | +27 pts |
| >=2 always-on xMult | 1/112 = 1% | 3/107 = 3% | 4/219 = 2% | 11/72 = 15% | +14 pts |
|   of which polychrome jokers, mean | 0.04 | 0.10 | 0.07 | 0.07 | +0.00 |
| conditional xMult jokers, mean | 0.51 | 0.59 | 0.55 | 0.78 | +0.23 |
| any xMult (always-on or conditional) | 53/112 = 47% | 72/107 = 67% | 125/219 = 57% | 62/72 = 86% | +29 pts |
| no xMult of any kind | 59/112 = 53% | 35/107 = 33% | 94/219 = 43% | 10/72 = 14% | -29 pts |
| Glass cards in deck, mean | 0.11 | 0.11 | 0.11 | 0.17 | +0.05 |
| Steel cards, mean | 0.08 | 0.06 | 0.07 | 0.07 | -0.00 |
| Polychrome cards, mean | 0.00 | 0.02 | 0.01 | 0.00 | -0.01 |
| any Glass/Steel/Poly card | 18/112 = 16% | 17/107 = 16% | 35/219 = 16% | 15/72 = 21% | +4 pts |
| enhanced cards (any), mean | 0.92 | 0.93 | 0.92 | 1.06 | +0.15 |
| main-hand level, mean | 1.87 | 2.06 | 1.96 | 2.62 | +0.66 |
| main-hand level >= 5 | 0/112 = 0% | 5/107 = 5% | 5/219 = 2% | 12/72 = 17% | +15 pts |
| main-hand level >= 4 | 8/112 = 7% | 14/107 = 13% | 22/219 = 10% | 19/72 = 26% | +17 pts |
| permanent (non-rental, non-perishable) +mult jokers, mean | 1.80 | 1.92 | 1.86 | 1.81 | -0.10 |
| >=2 permanent +mult | 66/112 = 59% | 72/107 = 67% | 138/219 = 63% | 41/72 = 57% | -8 pts |
| +mult jokers (any sticker), mean | 2.45 | 2.63 | 2.53 | 2.29 | -0.30 |
| jokers owned, mean | 4.87 | 5.56 | 5.21 | 5.71 | +0.48 |
| $ held at snapshot, mean | 3.25 | 7.03 | 5.10 | 14.26 | +9.27 |

Per joker (snapshot), with P(reach ante 6) for holders that reached ante 5. "Conditional" here also includes scaling
xMults still at X1 and hand xMults not matching the main hand:

| joker at snapshot | class | runs holding: died 4-5 (N=219) | runs holding: 6+ (N=72) | among reached-5 holders: P(reach 6) |
|---|---|---|---|---|
| ramen | always-on | 14 | 9 | 9/19 |
| polychrome joker | always-on | 14 | 5 | 5/15 |
| duo | always-on | 7 | 8 | 8/12 |
| stencil | always-on | 8 | 6 | 6/13 |
| hologram | always-on | 4 | 6 | 6/8 |
| throwback | always-on | 4 | 4 | 4/6 |
| constellation | always-on | 3 | 4 | 4/5 |
| campfire | always-on | 2 | 3 | 3/4 |
| madness | always-on | 2 | 1 | 1/3 |
| cavendish | always-on | 0 | 2 | 2/2 |
| blueprint>ramen | always-on | 0 | 2 | 2/2 |
| blueprint>duo | always-on | 1 | 0 | 0/1 |
| order | always-on | 0 | 1 | 1/1 |
| photograph | conditional | 27 | 8 | 8/22 |
| acrobat | conditional | 16 | 7 | 7/18 |
| seeing_double | conditional | 11 | 7 | 7/15 |
| card_sharp | conditional | 10 | 7 | 7/12 |
| obelisk | conditional | 8 | 3 | 3/10 |
| blackboard | conditional | 4 | 5 | 5/8 |
| loyalty_card | conditional | 8 | 1 | 1/5 |
| trio | conditional | 4 | 3 | 3/6 |
| order | conditional | 4 | 3 | 3/4 |
| ancient | conditional | 5 | 0 | 0/1 |
| baseball | conditional | 3 | 1 | 1/1 |
| bloodstone | conditional | 3 | 1 | 1/2 |
| duo | conditional | 3 | 0 | 0/1 |
| tribe | conditional | 1 | 2 | 2/2 |
| blueprint>card_sharp | conditional | 1 | 2 | 2/2 |
| baron | conditional | 2 | 0 | 0/1 |
| blueprint>photograph | conditional | 2 | 0 | 0/1 |
| yorick | conditional | 1 | 0 | 0/0 |
| brainstorm>stencil | conditional | 1 | 0 | 0/1 |
| stencil | conditional | 1 | 0 | 0/1 |
| blueprint>flower_pot | conditional | 1 | 0 | 0/0 |
| flower_pot | conditional | 1 | 0 | 0/0 |
| brainstorm>photograph | conditional | 0 | 1 | 1/1 |
| constellation | conditional | 0 | 1 | 1/1 |
| brainstorm>acrobat | conditional | 0 | 1 | 1/1 |
| blueprint>trio | conditional | 0 | 1 | 1/1 |
| triboulet | conditional | 1 | 0 | 0/0 |
| drivers_license | conditional | 0 | 1 | 1/1 |
| idol | conditional | 1 | 0 | 0/0 |
| vampire | conditional | 0 | 1 | 1/1 |

Reached-ante-5 cohort (N=179), build at ante-5 entry:

| group at ante-5 entry | N | P(reach ante 6) | P(reach ante 7) | mean final ante |
|---|---|---|---|---|
| 0 always-on xMult | 103 | 34/103 = 33% | 14/103 = 14% | 5.54 |
| 1 always-on xMult | 62 | 27/62 = 44% | 7/62 = 11% | 5.61 |
| 2+ always-on xMult | 14 | 11/14 = 79% | 3/14 = 21% | 6.14 |
| no xMult at all | 45 | 10/45 = 22% | 3/45 = 7% | 5.33 |
| conditional only | 58 | 24/58 = 41% | 11/58 = 19% | 5.71 |
| main-hand level 1-2 | 117 | 45/117 = 38% | 17/117 = 15% | 5.63 |
| main-hand level 3-4 | 45 | 15/45 = 33% | 5/45 = 11% | 5.47 |
| main-hand level 5+ | 17 | 12/17 = 71% | 2/17 = 12% | 5.88 |
| $ <5 at ante-5 entry | 71 | 19/71 = 27% | 4/71 = 6% | 5.32 |
| $5-14 | 56 | 23/56 = 41% | 8/56 = 14% | 5.68 |
| $15+ | 52 | 30/52 = 58% | 12/52 = 23% | 5.94 |

Build at ante-4 entry (all 291 runs reached it):

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| $ at ante-4 entry (after ante-3 boss) | 2.79 | 8.08 | 5.37 | 10.33 | +4.98 |
| always-on xMult at ante-4 entry | 0.19 | 0.23 | 0.21 | 0.46 | +0.26 |
| >=1 always-on xMult at ante-4 entry | 19/112 = 17% | 24/107 = 22% | 43/219 = 20% | 26/72 = 36% | +17 pts |
| main-hand level at ante-4 entry | 1.59 | 1.59 | 1.59 | 2.00 | +0.41 |

| build at ante-4 entry | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| 0 always-on xMult at ante-4 entry | 222 | 129/222 = 58% | 46/222 = 21% | 4.92 |
| >=1 always-on xMult | 69 | 50/69 = 72% | 26/69 = 38% | 5.23 |
| 0 xMult of any kind | 131 | 68/131 = 52% | 20/131 = 15% | 4.73 |
| only conditional xMult | 91 | 61/91 = 67% | 26/91 = 29% | 5.19 |

Always-on and conditional xMult are the clearest build-side separator: 43% of died-4-5 runs had no xMult of any kind at
the snapshot vs 14% of 6+ runs. Permanent +mult count does not separate the groups (1.86 vs 1.81): a flat build of
2-3 +mult jokers is what both groups have; the xMult is what is missing. Glass/Steel/polychrome cards are rare in both
groups (16% vs 21% of runs own any).

## 2. Money spent in antes 2-4, by category (mean $ per run)

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| $ jokers (shop) | 11.32 | 14.21 | 12.73 | 14.99 | +2.10 |
| $ Buffoon packs | 3.95 | 5.46 | 4.68 | 4.28 | -0.33 |
| $ Arcana packs | 2.27 | 2.73 | 2.49 | 4.06 | +1.54 |
| $ Celestial packs | 4.21 | 5.44 | 4.81 | 5.94 | +1.25 |
| $ Spectral packs | 0.38 | 0.58 | 0.47 | 0.47 | -0.04 |
| $ Standard packs | 0.12 | 0.28 | 0.20 | 0.89 | +0.68 |
| $ rerolls | 5.86 | 10.36 | 8.06 | 14.24 | +5.85 |
| $ vouchers | 0.18 | 1.31 | 0.73 | 1.39 | +0.71 |
| $ planets bought directly | 0.72 | 0.81 | 0.77 | 1.33 | +0.55 |
| $ tarots bought directly | 0.91 | 1.09 | 1.00 | 1.83 | +0.74 |
| $ total spent | 29.92 | 42.27 | 35.95 | 49.42 | +13.05 |

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| any Buffoon pack bought | 62/112 = 55% | 78/107 = 73% | 140/219 = 64% | 47/72 = 65% | +2 pts |
| any reroll | 63/112 = 56% | 84/107 = 79% | 147/219 = 67% | 55/72 = 76% | +9 pts |
| any Arcana pack | 41/112 = 37% | 38/107 = 36% | 79/219 = 36% | 31/72 = 43% | +7 pts |
| any Celestial pack | 62/112 = 55% | 61/107 = 57% | 123/219 = 56% | 43/72 = 60% | +5 pts |
| any voucher | 2/112 = 2% | 14/107 = 13% | 16/219 = 7% | 9/72 = 12% | +6 pts |
| shop exits (count) | 6.30 | 6.72 | 6.51 | 6.44 | -0.02 |
| $ at shop exit, mean over exits | 4.34 | 7.58 | 5.92 | 10.36 | +4.37 |
| share of exits with $>=25 | 0.00 | 0.03 | 0.02 | 0.08 | +0.06 |
| share of exits with $>=10 | 0.12 | 0.32 | 0.22 | 0.43 | +0.20 |
| share of exits with $<5 (no interest) | 0.59 | 0.37 | 0.48 | 0.26 | -0.23 |
| interest $ implied by exits (sum min(floor($/5),5)) | 3.29 | 8.05 | 5.61 | 10.53 | +4.81 |

Per ante (shop-exit money and spending):

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| mean $ at ante-2 shop exits | 4.68 | 5.65 | 5.15 | 5.85 | +0.71 |
| mean $ at ante-3 shop exits | 4.59 | 8.31 | 6.41 | 10.58 | +4.08 |
| mean $ at ante-4 shop exits | 3.42 | 8.85 | 6.07 | 14.12 | +7.97 |
| share of ante-2 exits under $5 | 0.54 | 0.43 | 0.48 | 0.37 | -0.12 |
| share of ante-3 exits under $5 | 0.60 | 0.35 | 0.48 | 0.25 | -0.24 |
| share of ante-4 exits under $5 | 0.67 | 0.32 | 0.50 | 0.18 | -0.32 |
| $ spent at ante 2 (all categories) | 9.34 | 10.31 | 9.81 | 9.29 | -0.55 |
| $ spent at ante 3 (all categories) | 11.33 | 14.99 | 13.12 | 16.08 | +2.95 |
| $ spent at ante 4 (all categories) | 9.25 | 16.97 | 13.02 | 24.04 | +10.66 |

Died-4-5 and 6+ runs spend the same at ante 2 ($9.8 vs $9.3); the 6+ runs then spend *and* hold more at antes 3-4
because they earn more. The shop-exit floor is the separating habit: in 6+ runs only 25% of ante-3 exits and 18% of
ante-4 exits were under $5 (no interest), vs 48% and 50% in runs that died at 4-5. The $25 interest cap is almost
never reached: 23 of 1312 ante 2-3 shop exits (2%).

### Landmark: ante 2-3 shop behaviour among runs that reached ante 4 (N=291)

Mean shop-exit $ at antes 2-3, split by tertile of mean shop-entry $ (controls for income):

| entry-$ tertile | exit $ < 5 | exit $ 5-9 | exit $ 10+ |
|---|---|---|---|
| low (mean entry <= $7.8) | N=87: P5 38%, P6 11% | N=9: P5 78%, P6 22% | - |
| mid ($7.8-12.2) | N=31: P5 48%, P6 13% | N=64: P5 70%, P6 31% | N=1: P5 0%, P6 0% |
| high (> $12.2) | N=1: P5 0%, P6 0% | N=43: P5 74%, P6 23% | N=52: P5 85%, P6 46% |

Within the middle income tertile, leaving with $5-9 instead of under $5 goes with P(reach 5) 70% vs 48% and
P(reach 6) 31% vs 13%.

| ante 2-3 shop exits | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| never <$5 | 61 | 51/61 = 84% | 26/61 = 43% | 5.48 |
| <$5 only in shops that added an xMult | 4 | 4/4 = 100% | 1/4 = 25% | 5.25 |
| <$5 in a shop without adding xMult | 226 | 124/226 = 55% | 45/226 = 20% | 4.86 |

| interest banking (a2-3) | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| max a2-3 exit $ < 10 | 145 | 67/145 = 46% | 25/145 = 17% | 4.68 |
| max $10-19 | 107 | 78/107 = 73% | 31/107 = 29% | 5.23 |
| max $20-24 | 22 | 17/22 = 77% | 7/22 = 32% | 5.23 |
| reached $25 cap at an a2-3 exit | 17 | 17/17 = 100% | 9/17 = 53% | 5.82 |

**Rerolls** (spend the reroll, but where does it leave you):

| group | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| no reroll in a2-3 shops | 139 | 77/139 = 55% | 33/139 = 24% | 4.92 |
| rerolled, always left shop with $>=5 | 76 | 58/76 = 76% | 26/76 = 34% | 5.26 |
| rerolled down to <$5 in some a2-3 shop | 76 | 44/76 = 58% | 13/76 = 17% | 4.86 |

**Buffoon packs:**

| ante 2-3 behaviour | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| no Buffoon pack in a2-3 | 142 | 85/142 = 60% | 38/142 = 27% | 5.02 |
| Buffoon pack, every such shop left with $>=5 | 68 | 48/68 = 71% | 17/68 = 25% | 5.09 |
| Buffoon pack in a shop left under $5 | 81 | 46/81 = 57% | 17/81 = 21% | 4.86 |

**Celestial packs:**

| ante 2-3 behaviour | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| no Celestial pack in a2-3 | 154 | 97/154 = 63% | 35/154 = 23% | 5.01 |
| Celestial pack, every such shop left with $>=5 | 84 | 57/84 = 68% | 23/84 = 27% | 5.07 |
| Celestial pack in a shop left under $5 | 53 | 25/53 = 47% | 14/53 = 26% | 4.81 |

**Arcana packs:**

| ante 2-3 behaviour | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| no Arcana pack in a2-3 | 227 | 135/227 = 59% | 53/227 = 23% | 4.93 |
| Arcana pack, every such shop left with $>=5 | 44 | 37/44 = 84% | 18/44 = 41% | 5.61 |
| Arcana pack in a shop left under $5 | 20 | 7/20 = 35% | 1/20 = 5% | 4.40 |

**Shop jokers:**

| ante 2-3 behaviour | N | P(reach ante 5) | P(reach ante 6) | mean final ante |
|---|---|---|---|---|
| no shop joker in a2-3 | 9 | 5/9 = 56% | 2/9 = 22% | 4.78 |
| shop joker, every such shop left with $>=5 | 84 | 67/84 = 80% | 33/84 = 39% | 5.43 |
| shop joker in a shop left under $5 | 198 | 107/198 = 54% | 37/198 = 19% | 4.82 |

Buffoon spending itself does not predict anything (any Buffoon pack at a2-3: P(reach 6) 23% vs 27% without,
stratified -4 pts, p=0.44). Rerolling helps only when the run can afford it: rerolling while staying at >= $5 is
+16 pts P(reach 6) over rerolling into poverty, which is no better than never rerolling. Arcana packs bought into
poverty are the worst single pattern (1/20 reached ante 6).

## 3. xMult availability: seen vs bought (antes 2-4)

Always-on xMult *candidates* = Cavendish, Stencil, Ramen, Steel Joker, Throwback, Hologram, Constellation, Campfire,
Madness, Vampire, Lucky Cat, Glass Joker, Caino, Yorick, Duo/Trio/Family/Order/Tribe (all counted at sight, before
knowing whether they fit the build).

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| always-on xMult candidates SEEN a2-4 (shop+Buffoon), mean | 0.59 | 0.61 | 0.60 | 1.08 | +0.51 |
| runs that saw >=1 | 48/112 = 43% | 46/107 = 43% | 94/219 = 43% | 51/72 = 71% | +30 pts |
|   ... seen in shop, mean | 0.50 | 0.46 | 0.48 | 0.82 | +0.36 |
|   ... seen in Buffoon pack, mean | 0.09 | 0.15 | 0.12 | 0.26 | +0.15 |
| always-on xMult candidates BOUGHT/picked a2-4, mean | 0.21 | 0.25 | 0.23 | 0.68 | +0.44 |
| runs that took >=1 | 23/112 = 21% | 26/107 = 24% | 49/219 = 22% | 41/72 = 57% | +35 pts |
| take rate among runs that saw >=1 | 23/48 = 48% | 26/46 = 57% | 49/94 = 52% | 41/51 = 80% | +26 pts |
| conditional xMult SEEN, mean | 0.86 | 1.04 | 0.95 | 1.12 | +0.18 |
| conditional xMult taken, mean | 0.34 | 0.46 | 0.40 | 0.54 | +0.15 |
| polychrome (non-xMult) joker seen, mean | 0.04 | 0.13 | 0.08 | 0.08 | +0.00 |
| Blueprint/Brainstorm seen, mean | 0.07 | 0.13 | 0.10 | 0.21 | +0.13 |

| always-on xMult candidates seen a2-4 (pooled sightings) | died 4-5 (N=219 runs) | 6+ (N=72 runs) |
|---|---|---|
| seen (shop + Buffoon pack) | 131 | 78 |
|   in shop | 105 | 59 |
|   in shop, bought | 37 | 38 |
|   in Buffoon pack | 26 | 19 |
|   in pack, picked | 14 | 11 |
| take rate (all sightings) | 51/131 = 39% | 49/78 = 63% |
| mean shop price (rentals cost $1) | $4.4 | $4.6 |
| sightings with rental / perishable / eternal sticker | 48 / 26 / 36 | 15 / 9 / 28 |
| missed shop sightings | 68 | 21 |
|   unaffordable at every sighting | 9 | 3 |
|   unaffordable at first sighting | 11 | 4 |
|   affordable but joker slots full every time | 9 | 6 |
|   affordable, free slot, skipped | 50 | 12 |
| missed shop sightings that were unaffordable | 9/68 = 13% | 3/21 = 14% |
| missed Buffoon-pack sightings (free pick, slot free) | 12 | 8 |

- Hit rate per source (all 291 runs): a shop view (shop entry or reroll; 2485 views) shows an always-on xMult
  candidate 6.6% of the time (164 sightings); an opened Buffoon pack (346 opened, 279 bought for $4.78 avg) shows one
  13% of the time (45). A reroll averaged $4.68. Per dollar a Buffoon pack surfaces about twice as many xMult
  candidates as a reroll, and the pick is then free, while a shop xMult costs another $6-8 (clean) or $1 (rental).
- Clean always-on xMults in shops cost $6-8 (median money at first sight $12); rentals $1.
- **Missing an xMult is rarely about money.** Of 68 shop sightings missed by died-4-5 runs, 9 (13%) were unaffordable
  at every sighting, 9 had full slots every time, and 50 (74%) were affordable with a free slot and skipped. The skipped
  keys: Madness 8, Vampire 8, Family 7, Constellation 5, Hologram 5, Tribe 4, Campfire 4, Throwback 4, Order 3,
  Stencil 1, Trio 1. 12 of 26 Buffoon-pack xMult offers were also passed over with a free slot. 6+ runs took 80% of
  runs-with-a-sighting vs 52% (+26 pts stratified).
- 6+ runs also *saw* more candidates (1.08 vs 0.60 per run): 9.0% vs 5.7% per shop view and 23% vs 10% per Buffoon
  pack, i.e. part of the gap is seed luck that a spending policy cannot fix.

## 4. Arcana, Spectral and planet usage (antes 2-4)

| metric | died at 4 (N=112) | died at 5 (N=107) | died 4-5 (N=219) | reached 6+ (N=72) | model-strat. diff (6+ minus 4-5) |
|---|---|---|---|---|---|
| Arcana packs opened a2-4 (incl. tag packs), mean | 0.71 | 0.69 | 0.70 | 1.04 | +0.33 |
| tarots used a2-4, mean | 1.49 | 1.31 | 1.40 | 2.17 | +0.73 |
| used any enhancement tarot | 43/112 = 38% | 25/107 = 23% | 68/219 = 31% | 27/72 = 38% | +6 pts |
| used Glass/Steel tarot (Justice/Chariot) | 16/112 = 14% | 12/107 = 11% | 28/219 = 13% | 13/72 = 18% | +4 pts |
| used Mult/Bonus tarot (Empress/Hierophant) | 19/112 = 17% | 12/107 = 11% | 31/219 = 14% | 8/72 = 11% | -2 pts |
| used Hermit/Temperance (money) | 21/112 = 19% | 29/107 = 27% | 50/219 = 23% | 30/72 = 42% | +19 pts |
| used Emperor/Priestess/Fool/Judgement | 31/112 = 28% | 28/107 = 26% | 59/219 = 27% | 30/72 = 42% | +15 pts |
| used Wheel of Fortune | 7/112 = 6% | 5/107 = 5% | 12/219 = 5% | 4/72 = 6% | +1 pts |
| used suit converter (Star/Moon/Sun/World) | 10/112 = 9% | 9/107 = 8% | 19/219 = 9% | 4/72 = 6% | -3 pts |
| used any Spectral | 15/112 = 13% | 23/107 = 21% | 38/219 = 17% | 7/72 = 10% | -8 pts |
| Celestial packs opened a2-4, mean | 1.14 | 1.31 | 1.22 | 1.53 | +0.36 |
| planets used a2-4, mean | 1.79 | 1.89 | 1.84 | 2.32 | +0.53 |
| planets used >= 4 | 20/112 = 18% | 14/107 = 13% | 34/219 = 16% | 18/72 = 25% | +11 pts |

Enhancement tarots barely separate the groups (Glass/Steel +4 pts, Mult/Bonus -2 pts; Glass/Steel users reach ante 6
32% vs 24%, p=0.27); Glass/Steel cards were owned by only 16-21% of runs at ante 5. The tarots that do separate are
the economy/generation ones: Hermit/Temperance (42% vs 23% of runs, P(reach 6) 38% vs 20%, +17 pts stratified) and
Emperor/High Priestess/Fool/Judgement (+15 pts). Spectral use leans negative (-8 pts).

Planets: main-hand level >= 5 at ante 5 is rare (17/291 runs) but strong: 12/17 = 71% reached ante 6 vs 60/162 = 37%
(+38 pts stratified, p=0.007). Level 3-4 shows no gain over level 1-2 (33% vs 38%), so planets pay only when
concentrated into one hand.

## 5. What differs most between 6+ and died-at-4-5 (model-stratified, 6+ minus 4-5)

| factor | died 4-5 | 6+ | diff |
|---|---|---|---|
| >=1 always-on xMult at snapshot | 26% | 53% | +27 pts |
| any xMult (always-on or conditional) | 57% | 86% | +29 pts |
| took >=1 always-on xMult candidate at a2-4 | 22% | 57% | +35 pts |
| take rate when one was seen | 52% | 80% | +26 pts |
| share of a2-4 shop exits under $5 | 48% | 26% | -23 pts |
| mean $ at a2-4 shop exits | $5.9 | $10.4 | +$4.4 |
| main-hand level >= 5 at snapshot | 2% | 17% | +15 pts |
| used Hermit/Temperance | 23% | 42% | +19 pts |
| $ rerolls a2-4 | $8.1 | $14.2 | +$5.9 (only above the $5 floor, see section 2) |
| $ Buffoon packs a2-4 | $4.7 | $4.3 | -$0.3 (no effect) |
| $ Arcana packs a2-4 | $2.5 | $4.1 | +$1.5 (only above the $5 floor) |
| reached $25 cap at an a2-3 exit | 2% of exits | 8% of exits | +6 pts |
| Glass/Steel/Poly card owned | 16% | 21% | +4 pts (not significant) |
| permanent +mult jokers | 1.86 | 1.81 | -0.10 (no effect) |

## Ante 2-4 spending policy (recommendation)

1. **xMult first:** at antes 2-4, buy any always-on xMult that fits the build (Ramen, Duo/Trio matching the main hand,
   Stencil with a free slot, Hologram, Constellation, Campfire, Throwback, Cavendish), clean or eternal at $6-8 or rental
   at $1, even if it drops you below $5; sell a flat +mult joker to make room. 74% of missed xMults were affordable.
2. **$5 floor:** otherwise never leave an ante 2-3 shop under $5 (never-under-$5 runs: P(reach 6) 43% vs 20%).
3. **Rerolls** only while you own no always-on xMult and only with money >= reroll cost + $5; stop at the floor.
4. **Buffoon pack over reroll** when hunting xMult (13% vs 6.6% xMult per open/view at ~$4.7 each), but only above the
   $5 floor; Buffoon spending for flat jokers does not help.
5. **Arcana / Celestial** only with >= $5 left after the buy; take Hermit/Temperance and Emperor/Priestess picks;
   do not rely on Glass/Steel tarots to replace an xMult joker.
6. **Planets into one hand:** every Celestial pick and planet buy goes to the main hand; aim for level 5 by ante 5.
7. **Interest:** with no xMult on offer, bank toward $10-25 (runs that hit $25 at an ante 2-3 exit: 9/17 reached
   ante 6 vs 25/145 for runs that never held $10).
