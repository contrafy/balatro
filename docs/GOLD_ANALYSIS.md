# Gold Stake analysis: why runs die and what to do instead

Snapshot 2026-10-14: 46 player runs on Black Deck / Gold Stake (39 finished, 0 wins; 21 Sonnet, 18 Opus, 7 Fable).
Source: every step of `data/trajectories/**` (stake 8, no `test-*`/replay agents, no `FUZZ*` seeds). Regenerate all
tables with `cd python && python -m balatro_env.analysis.gold_stats [--out FILE]`; numbers move as runs finish.
Sample sizes are small, so treat differences under ~15 points on n < 15 as noise. Rounds and rent belong to the
ante of their blind; shop spending belongs to the ante the shop serves (the shop after an ante-A boss is in ante A+1).
"r/g xMult" means a reliable or growing xMult joker (Cavendish, Card Sharp, Photograph, Triboulet, Baron, Ramen,
The Duo/Trio/Family/Order/Tribe when they fit the main hand, Hologram, Constellation, Campfire, Lucky Cat, Vampire,
Glass/Steel Joker, Obelisk, Yorick, Canio...; a polychrome edition counts too). "Conditional" xMults are Acrobat, The
Idol, Baseball Card, Loyalty Card, Bloodstone, Ancient, Flower Pot, Seeing Double, Driver's License, Stencil,
Blackboard.

## 1. Death profile

| died at ante | runs | Small / Big / Boss | median scored/needed |
|---|---|---|---|
| 1 | 5 | 0 / 2 / 3 | 0.69 |
| 2 | 7 | 1 / 1 / 5 | 0.55 |
| 3 | 10 | 2 / 1 / 7 | 0.68 |
| 4 | 7 | 1 / 4 / 2 | 0.39 |
| 5 | 8 | 1 / 4 / 3 | 0.65 |
| 6 | 1 | Big | 0.97 |
| 8 | 1 | Crimson Heart | 0.40 |

- Deaths are spread over antes 1-5. **15 of 39 were blowouts (<50% of the target) and only 9 near misses (>=85%).**
  Runs mostly die under-scaled; bad luck in the last hand is not the main cause.
- Loss rate per blind played rises from 5-8% at ante 1 to 15-29% at the ante 2-3 bosses, then 17-27% at ante 4 and
  44-60% at the ante 5 Big Blind and boss.
- Bosses: The House lost 4 of 7 (median 0.38 of the target), The Water 2 of 2, The Mouth 2 of 7. Those House losses
  were builds that were already under-scaled (e.g. 3 x ~2.3k Pairs against 18k at ante 4, 0 xMult), so the boss was
  not the real cause. Every Flush/Straight-main run died by ante 3: no Flush or Straight main reached ante 4 (0 of 6),
  against 17 of 28 (61%) pair-family mains.

Ante-start state, runs that died in that ante vs runs that cleared it (medians, xMult = means):

| ante | fate | n | $ | jokers | r/g xMult | any xMult | main level | total levels |
|---|---|---|---|---|---|---|---|---|
| 3 | died | 10 | 0.5 | 3 | 0.40 | 0.70 | 1 | 0.5 |
| 3 | cleared | 17 | 3 | 4 | 0.41 | 0.71 | 1 | 1 |
| 4 | died | 7 | 2 | 4 | 0.14 | 0.71 | 1 | 2 |
| 4 | cleared | 10 | 3.5 | 6 | 0.60 | 0.90 | 2.5 | 2.5 |
| 5 | died | 8 | 2 | 6 | 0.62 | 1.12 | 3 | 3.5 |
| 5 | cleared | 2 | 8.5 | 7 | 1.50 | 2.00 | 3.5 | 7 |

- **Everyone is broke**: the median money at any ante start is $0.5-4. Runs that cleared ante 4 had a full joker row
  (6 vs 4), more than four times as many r/g xMults per run (0.60 vs 0.14) and main hand L2-3 instead of L1. Runs with
  6+ jokers at ante 4 averaged a final ante of 5.6, against 4.3 with fewer.
- First r/g xMult bought at ante 1-2: 5 of 13 runs reached ante 5 (one reached ante 8). Never bought one: 4 of 19
  reached ante 5, and none got further.

## 2. Economy

Mean $ per run per ante (income ~$12-16 a ante at antes 1-5):

| ante | blind | interest | hands left | jokers/tags at cash-out | other in | spent: jokers | packs | rerolls | rent |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 7.5 | 0.2 | 3.1 | 0.6 | 0.2 | 2.1 | 3.4 | 0.4 | 1.5 |
| 2 | 7.2 | 0.7 | 2.9 | 1.6 | 1.8 | 3.4 | 3.2 | 3.4 | 4.0 |
| 3 | 6.3 | 1.5 | 1.6 | 1.6 | 4.7 | 3.8 | 7.6 | 2.9 | 3.8 |
| 4 | 5.5 | 1.5 | 1.0 | 0.7 | 5.9 | 3.0 | 7.4 | 4.5 | 2.5 |
| 5 | 3.0 | 1.2 | 0.3 | 2.9 | 6.4 | 0.9 | 7.0 | 4.3 | 2.1 |

- Income across all runs was $1913. Blind rewards gave 48% (Small pays $0), hands left 16%, Hermit/Temperance 10%,
  Golden Joker/Investment 9%, interest only 7%.
- Spending was $1962. **Packs took 37%, rent 20%, rerolls 18% and jokers only 20%.** By pack kind: Buffoon $244,
  Celestial $242, Arcana $152, Spectral $56, Standard $32.
- **Interest was earned in 22% of cash-outs and hit the $5 cap in 1% (2 of 274).** The 5 runs that earned $12-27 of
  interest all reached ante 5+, including the two deepest. None of the runs that died by ante 4 earned more than $2.
  Longer runs also get more cash-outs, so this is a correlation, not proof.
- **Rent: $393 in total.** 41 rentals were bought for ~$1 each and then paid $9-10 of rent each (3.4 rounds held on
  average). That makes their effective price $10-11, against $4 for a clean joker. Only 9 of the 41 were xMults;
  most were Sly, Misprint, Gros Michel, Mystic Summit, Ice Cream and the like, kept until the run died.
- Perishables: 18 of 54 perished while held.

## 3. Supply: what the shop and packs actually offer

| ante | shop views | any xMult | r/g xMult | r/g without rental/perishable | E[rerolls] for r/g | r/g median $ | main-hand planet | Celestial pack | Buffoon pack |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 80 | 22% | 15% | 6% | 5.7 | 5.5 | 4% | 36% | 61% |
| 2 | 103 | 14% | 8% | 5% | 11.9 | 6.5 | 3% | 49% | 8% |
| 3 | 77 | 14% | 8% | 6% | 11.8 | 6 | 6% | 44% | 19% |
| 4 | 47 | 15% | 2% | 2% | 46 | 5 | 0% | 28% | 9% |
| 5 | 27 | 4% | 4% | 4% | 26 | - | 7% | 56% | 11% |

- 67% of shop jokers carry a sticker (perishable 18%, eternal 18%, rental 16%, eternal+rental 8%, perishable+rental 7%).
- **Cost of seeing a r/g xMult: ~$91 by rerolling (6% per reroll) against ~$24 with a bought Buffoon pack (18% per
  pack).** At ante 3-5 only 2 of 41 rerolled views showed one. Counting conditional xMults: $33 per reroll sighting,
  $20 per Buffoon pack.
- Celestial packs show the main-hand planet 37% of the time (3-card 38%, 5-card 33%). The main-hand planet was taken
  from 15 of the 55 Celestial packs bought, about $16 per level, against $3 for a shop planet. A shop planet for the
  main hand appears in only 0-7% of shop views, though, so packs are the main source of levels.
- Arcana packs offered Justice 29% of the time (10 of 35). Justice showed up in 1 of ~340 shop views.
- **Every r/g xMult a run saw (39 sightings): 19 bought, 12 passed, 8 unaffordable.** In the unaffordable cases the
  run had $-1 to $6 against prices of $6-9. Every shop r/g xMult bought by runs that reached ante 5+ was bought with
  $11-22 in hand. Only 10 of the 17 runs that reached ante 4 had even seen one by ante 3.

## 4. Decision impact (correlations; confounded by run strength)

| decision | evidence | reading |
|---|---|---|
| Skip Small at ante 1 | 2 of 6 skippers died at the ante-1 Big (448/450 after a Polychrome tag, 328/450 after a Rare tag, both jokerless); both Coupon-tag skippers reached ante 5; 3 of 33 players died in ante 1 | skip only for a tag that gives a joker before the Big Blind |
| Skip Small at ante 2 | died that ante: skip 3/20 (15%), play 4/14 (29%) | no harm detected |
| Skip Small at ante 3-4 | died that ante: skip 6/15 and 6/13 (40-46%), play 4/12 and 1/4 (25-33%) | weak sign of harm; skipping gives up one of ~3 shop views per ante |
| Skip Small at ante 5 | 5 of 6 skippers died that ante (3 of 4 players) | never skip |
| Rerolls vs planets, ante 3-5 | rerolls > planets: n=8, mean final ante 4.2; planets >= rerolls: n=19, 4.1 | no gain from rerolling; A5D7B521 spent $53 on rerolls for 1 xMult |
| Rental jokers | $9-10 rent each, mostly flat jokers held to death; rent made up 20% of all spending | rentals are bridges, not keepers |
| Buffoon pack vs single | $4.69 vs $3.24 per joker; xMult share 16% vs 19%; stickered 63% vs 61% | singles are cheaper per joker, but packs are the cheapest way to *find* an xMult |

## 5. Score requirement model

Per-hand need = Gold boss / 3 hands (base 300, 1000, 3200, 9000, 25000, 60000, 110000, 200000; Big x1.5, Boss x2):

| ante | boss | boss/3 | needed growth | median best hand | runs >= boss/3 | runs >= boss/2 |
|---|---|---|---|---|---|---|
| 1 | 600 | 200 | | 664 | 98% | 93% |
| 2 | 2.0k | 667 | x3.3 | 2.2k | 97% | 97% |
| 3 | 6.4k | 2.1k | x3.2 | 4.4k | 89% | 70% |
| 4 | 18k | 6.0k | x2.8 | 11.6k | 76% | 59% |
| 5 | 50k | 16.7k | x2.8 | 18.7k | 50% | 40% |
| 6 | 120k | 40k | x2.4 | 64k (n=2) | | |
| 7 | 220k | 73k | x1.8 | 412k (n=1, Acrobat final hand) | | |
| 8 | 400k | 133k | x1.8 | 142k (n=1) | | |

- **The ante's best single hand predicts survival.** When it was below boss/3, the run died that ante 15 of 15 times.
  Between boss/3 and boss/2: 8 of 10 died. At boss/2 or more: 16 of 106 died.
- The target grows about x3 per ante through ante 5. A run's best hand grew a median **x3.0 (a1->a2), x1.9, x1.4,
  x1.2 (a4->a5)**. Scaling stalls from ante 3, which is exactly where the deaths cluster.
- Median best hand per round by build (pair-family main):

| r/g xMult | a3 | a4 | a5 | a6 | a7 |
|---|---|---|---|---|---|
| 0 | 3.0k | 8.5k | 10.1k | - | - |
| 1 | 4.9k | 12.3k | 27.9k | 31.5k | - |
| 2+ | 13.2k | 13.8k | 31.3k | 93.8k | 362k |

  With 0 xMult a build reaches ante 5 below boss/3 (10k < 16.7k). One xMult clears ante 5 (28k) but not ante 6
  (31k < 40k). Ante 6-7 took 2+ xMults plus Pair L5 / Trips L7 (7810_ZY6GJXIG: 5.0k, 17k, 94k, 94k, 412k from
  ante 3 to 7). Ante 8 needs ~200k per hand under Crimson Heart, which means a growing xMult on top of that.
- So the winning curve is **best hand >= boss/2 of the current ante, and >= boss/3 of the next ante before leaving
  its last shop**: ~3.2k by the end of ante 2, 9k by ante 3, 25k by ante 4, 60k by ante 5, 110k by ante 6, 200k
  by ante 7. On average every ante from 3 on needs one new multiplicative source (an xMult, or about 2 main-hand
  levels plus a +mult joker).

## Gold policy (priority order)

1. **Pair-family only.** Main hand Pair, Two Pair or Trips (Full House as a bonus). Never build around Flush or
   Straight on Black Deck Gold: 0 of 6 such runs reached ante 4. Flush/Straight-gated jokers and planets are not core.
2. **Score check every shop.** Let B = est of your best hand. If B < boss/3 of the next ante, go into emergency mode:
   every dollar goes to the cheapest multiplier on offer (r/g xMult > conditional xMult > Buffoon pack > main-hand
   planet), and floors and interest are ignored. A run below boss/3 died 15 of 15 times.
3. **Cash floor $8 from ante 2.** Only an xMult, a main-hand planet, or a Buffoon pack while you own fewer than 2
   r/g xMults may take you below $8. Rerolls, Arcana/Spectral/Standard packs, vouchers and non-rescue tarots never do,
   even when you are under-scaled. Reason: r/g xMults cost $6-9, and 8 of 20 missed ones were unaffordable.
4. **Buy a r/g xMult on sight**, eternal or perishable included, once you own 1+ scoring joker. Sell the weakest flat
   joker to afford it or make room. 12 of 39 sightings were passed. Growth xMults (Hologram, Vampire, Campfire...)
   at ante 1 need a feeding plan; from ante 2 they are buys.
5. **Conditional xMult from ante 3** (not 4) when you own 0 r/g xMults: Acrobat, The Idol, Baseball Card, Loyalty
   Card. Any xMult is offered in 14-15% of views at ante 2-4, a r/g one in only 2-8%.
6. **Buffoon pack before rerolls.** With fewer than 2 r/g xMults and a free (or sellable flat) slot at ante 2-5, a
   Buffoon pack ranks above Celestial, Arcana and rerolls. It costs ~$24 per r/g xMult seen; rerolling costs ~$91.
7. **Rerolls are a luxury.** Reroll only when $20+ remains after the reroll, the shop holds nothing on rules 4-6,
   and at most 2 per shop. Never reroll at ante 3-5 just because you own 0 xMults while poor: 2 of 41 such rerolls
   showed one.
8. **Rentals are bridges.** Effective price = cost + $3 x rounds you will hold it (~$10 on average). Buy one only if
   (a) it is a r/g xMult, or (b) you own 0 scoring jokers at ante 1-2. Sell a flat rental in the first shop where
   you hold 2 other scorers that are alive next ante. Never hold 2 rentals before ante 6. From ante 7 ignore rent.
9. **Levels: 3-card Celestial ($4, 38% main-hand planet) only while main level < ante and you keep the $8 floor.**
   Always buy the main-hand shop planet ($3) once you own 2 scorers. Arcana is worth it only for a Glass/Steel
   plan (Justice 29% per pack) or to feed Vampire. Spectral and Standard packs only with $15+ left after.
10. **Interest is the default sink.** From ante 3, when nothing qualifies under rules 2-9, leave the shop with the
    money: each $5 held returns $1 per round (20%), far better than a $16-per-level Celestial gamble or a $91 reroll
    hunt. Aim for $10-15 at ante 3-5, which also pays for the next xMult.
11. **Fill 6 joker slots by ante 4** (6+ jokers at ante 4: mean final ante 5.6; fewer: 4.3), with flat +mult filling
    slots that are not xMults yet.
12. **Small Blind.** Ante 1: skip only for a tag that gives a joker now (Buffoon, Top-up). Rare and Polychrome tags
    pay after the Big Blind, and 2 of the 3 jokerless runs that skipped for them lost the ante-1 Big. Ante 2: skip
    only for a tag that pays now, or with 2+ scorers. Ante 3-4: skip only for a tag that pays now *and* only if B >=
    boss/2 of this ante (skippers died 40-46% vs 25-33%). Ante 5+: never.
13. **xMult targets.** At least 1 r/g xMult by the end of ante 2, 2 by ante 5, 3 including a growing one by ante 7
    (Crimson Heart disables one joker per hand). 0 xMult tops out at ~10k per hand at ante 5; 1 xMult tops out at
    ~31k at ante 6.
14. **Bosses.** Treat The House, The Water, The Mouth and The Eye as checks of whether you are scaled: with
    B >= boss/2 they were cleared. Below that, apply rule 2 in the shop before them; do not plan a boss-specific fix.
