# Rental / perishable jokers at Black Deck Gold Stake (stake 8)

Generated 2026-10-14 from `data/manifest.jsonl` + trajectories (read-only analysis).

## Method

- **Runs:** manifest entries with deck `b_black`, stake 8, outcome `loss`/`win`, not quarantined, recorded by a swarm
  player (`agent` = `port-78xx`). Replays (`agent=replay`), fuzzer, abandoned and other decks/stakes are excluded.
  N = 470 runs (Opus 243, Sonnet 169, Fable 32, Haiku 26; 3 wins). Each was matched by (seed, port) to
  `data/swarm_results.jsonl` for its model (470/470 matched).
- **Final ante:** the ante the run died in; wins count as 9. "Reach ante k" = final ante >= k.
- **Acquisition:** a joker id that appears in `obs.jokers` for the first time; its ante is the ante of the observation
  before the action that added it. Sticker flags (`rental`, `perishable`, `eternal`) are read from the owned card.
  Rentals at ante 1-2 came from 235 shop buys and 90 Buffoon-pack picks (Riff-raff/tag jokers carry no rental).
- **Classes (by key):** xMult (Trio/Duo/Family/Order/Tribe, Cavendish, Photograph, Stencil, Throwback, Obelisk,
  Hologram, Acrobat, Card Sharp, Baron, Ramen, ...), +mult (Joker, Jolly/Zany/Mad/Crazy/Droll, suit jokers, Half,
  Summit, Misprint, Gros Michel, Abstract, Even Steven, Smiley, Walkie Talkie, Shoot the Moon, Popcorn, ...),
  +chips (Sly/Wily/Clever/..., Banner, Scary Face, Odd Todd, Blue, Ice Cream, Stuntman, ...). "Scorer" = any of the three.
  Rentals bought at ante 1-2 by class: +mult 172, +chips 68, xMult 31, other 54.
- **Permanent +mult at end of ante 2:** owned +mult jokers with neither `rental` nor `perishable` in the first
  observation at ante 3 (defined only for runs that reached ante 3).
- **Money:** mean `money` at the first observation of each SHOP visit in antes 2-3.
- **Bias control.** Buying at ante 2 needs the run to reach ante 2, so "rental vs none over all runs" flatters the
  rental group (runs that died at ante 1 land in "none"). Each comparison is therefore also shown on a **landmark
  cohort**: runs that already reached the ante after the exposure window (ante 3 for ante 1-2 exposures, ante 2 for
  ante-1 exposures, ante 4 for ante-3 exposures). Both groups then had the same chance to buy. **Model-stratified
  difference** = per-model difference weighted by n_a*n_b/(n_a+n_b); "model x era" adds the start time in thirds
  (advisor versions changed during the day).
- Observational data: buying a rental also signals a thin shop. Comparison (b) partly controls for that.

## Headline

| comparison (landmark cohort) | N (A / B) | mean final ante A vs B | P(reach 5) A vs B | stratified diff (mean ante, P5) |
|---|---|---|---|---|
| (a) rental ante 1-2 vs none, reached ante 3 | 232 / 136 | 4.34 vs 4.75 | 38% vs 57% | model (-0.43, -20), model x era (-0.44, -19) |
| (a') rental ante 1 vs none, reached ante 2 | 163 / 269 | 3.81 vs 4.31 | 29% vs 44% | model (-0.45, -13), model x era (-0.45, -13) |
| (b) same as (a), first ante-1 shop offered 0 non-rental scorers | 123 / 52 | see (b) | see (b) | model (-0.39, -22), model x era (-0.39, -23) |

Ante-1 rentals do buy short-term survival: among runs with an ante-1 shop, P(reach ante 2) is
163/166 = 98% with an ante-1 rental vs
269/291 = 92% without
(model-stratified +6 pts; partly exposure bias, since a later ante-1 buy implies surviving to that shop).
Over all runs with an ante-1 shop the net is still negative: P(reach ante 5) 48/166 = 29% vs
119/291 = 41%.

## (a) Rental acquired at ante 1-2 vs none

### All runs with an ante-1 shop (exposure-biased toward rentals)

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 272 | 3.98 | 4 | 232/272 = 85% | 89/272 = 33% | 11/272 = 4% | 7.3 (n=269) |
| no rental ante 1-2 | 185 | 3.90 | 4 | 136/185 = 74% | 78/185 = 42% | 12/185 = 6% | 10.5 (n=163) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: rental acquired ante 1-2 | 142 | 4.23 | 4 | 124/142 = 87% | 58/142 = 41% | 8/142 = 6% | 7.7 (n=139) |
| Opus: no rental ante 1-2 | 96 | 4.04 | 4 | 70/96 = 73% | 44/96 = 46% | 11/96 = 11% | 11.1 (n=83) |
| Sonnet: rental acquired ante 1-2 | 95 | 3.73 | 4 | 78/95 = 82% | 22/95 = 23% | 2/95 = 2% | 6.8 (n=95) |
| Sonnet: no rental ante 1-2 | 69 | 3.72 | 4 | 49/69 = 71% | 28/69 = 41% | 1/69 = 1% | 10.0 (n=61) |
| Fable: rental acquired ante 1-2 | 19 | 4.42 | 4 | 18/19 = 95% | 9/19 = 47% | 1/19 = 5% | 8.3 (n=19) |
| Fable: no rental ante 1-2 | 11 | 4.18 | 4 | 9/11 = 82% | 5/11 = 45% | 0/11 = 0% | 10.5 (n=10) |
| Haiku: rental acquired ante 1-2 | 16 | 2.81 | 3 | 12/16 = 75% | 0/16 = 0% | 0/16 = 0% | 4.5 (n=16) |
| Haiku: no rental ante 1-2 | 9 | 3.44 | 3 | 8/9 = 89% | 1/9 = 11% | 0/9 = 0% | 8.9 (n=9) |

Model-stratified difference (rental acquired ante 1-2 minus no rental ante 1-2): mean final ante +0.08, P(ante 5) -9 pts, P(ante 7) -2 pts.


### Landmark: runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 232 | 4.34 | 4 | 232/232 = 100% | 89/232 = 38% | 11/232 = 5% | 7.7 (n=232) |
| no rental ante 1-2 | 136 | 4.75 | 5 | 136/136 = 100% | 78/136 = 57% | 12/136 = 9% | 11.1 (n=136) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: rental acquired ante 1-2 | 124 | 4.57 | 4 | 124/124 = 100% | 58/124 = 47% | 8/124 = 6% | 8.1 (n=124) |
| Opus: no rental ante 1-2 | 70 | 4.99 | 5 | 70/70 = 100% | 44/70 = 63% | 11/70 = 16% | 11.9 (n=70) |
| Sonnet: rental acquired ante 1-2 | 78 | 4.10 | 4 | 78/78 = 100% | 22/78 = 28% | 2/78 = 3% | 7.3 (n=78) |
| Sonnet: no rental ante 1-2 | 49 | 4.59 | 5 | 49/49 = 100% | 28/49 = 57% | 1/49 = 2% | 10.5 (n=49) |
| Fable: rental acquired ante 1-2 | 18 | 4.56 | 4.5 | 18/18 = 100% | 9/18 = 50% | 1/18 = 6% | 8.6 (n=18) |
| Fable: no rental ante 1-2 | 9 | 4.78 | 5 | 9/9 = 100% | 5/9 = 56% | 0/9 = 0% | 10.5 (n=9) |
| Haiku: rental acquired ante 1-2 | 12 | 3.08 | 3 | 12/12 = 100% | 0/12 = 0% | 0/12 = 0% | 4.9 (n=12) |
| Haiku: no rental ante 1-2 | 8 | 3.62 | 3.5 | 8/8 = 100% | 1/8 = 12% | 0/8 = 0% | 9.0 (n=8) |

Model-stratified difference (rental acquired ante 1-2 minus no rental ante 1-2): mean final ante -0.43, P(ante 5) -20 pts, P(ante 7) -4 pts.


### Ante-1 rental, landmark: runs that reached ante 2

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1 | 163 | 3.81 | 4 | 132/163 = 81% | 48/163 = 29% | 6/163 = 4% | 6.3 (n=163) |
| no rental ante 1 | 269 | 4.31 | 4 | 236/269 = 88% | 119/269 = 44% | 17/269 = 6% | 9.8 (n=269) |

### Timing and count, runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental at ante 1 only | 106 | 4.25 | 4 | 106/106 = 100% | 38/106 = 36% | 5/106 = 5% | 7.0 (n=106) |
| rental at ante 2 only | 100 | 4.47 | 4 | 100/100 = 100% | 41/100 = 41% | 5/100 = 5% | 8.8 (n=100) |
| rentals at ante 1 and 2 | 26 | 4.19 | 4 | 26/26 = 100% | 10/26 = 38% | 1/26 = 4% | 6.0 (n=26) |
| no rental ante 1-2 | 136 | 4.75 | 5 | 136/136 = 100% | 78/136 = 57% | 12/136 = 9% | 11.1 (n=136) |

### Number of rentals acquired at ante 1-2, runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| 0 | 136 | 4.75 | 5 | 136/136 = 100% | 78/136 = 57% | 12/136 = 9% | 11.1 (n=136) |
| 1 | 189 | 4.39 | 4 | 189/189 = 100% | 75/189 = 40% | 9/189 = 5% | 7.9 (n=189) |
| 2+ | 43 | 4.12 | 4 | 43/43 = 100% | 14/43 = 33% | 2/43 = 5% | 6.5 (n=43) |

## (b) Runs whose first ante-1 shop offered no non-rental scorer

The first ante-1 shop's initial joker row (before rerolls) held 0 scorers without a rental sticker in 219 of
457 runs (none of the 457 runs owned a scorer at that point, so "0 scorers owned" is every run).

### All such runs

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 146 | 3.90 | 4 | 123/146 = 84% | 43/146 = 29% | 5/146 = 3% | 7.1 (n=145) |
| no rental ante 1-2 | 73 | 3.78 | 4 | 52/73 = 71% | 30/73 = 41% | 4/73 = 5% | 10.7 (n=63) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: rental acquired ante 1-2 | 76 | 4.25 | 4 | 66/76 = 87% | 28/76 = 37% | 5/76 = 7% | 7.8 (n=75) |
| Opus: no rental ante 1-2 | 41 | 4.02 | 5 | 30/41 = 73% | 21/41 = 51% | 4/41 = 10% | 11.3 (n=34) |
| Sonnet: rental acquired ante 1-2 | 48 | 3.50 | 3 | 37/48 = 77% | 10/48 = 21% | 0/48 = 0% | 6.9 (n=48) |
| Sonnet: no rental ante 1-2 | 26 | 3.50 | 3.5 | 18/26 = 69% | 8/26 = 31% | 0/26 = 0% | 9.9 (n=24) |
| Fable: rental acquired ante 1-2 | 12 | 4.17 | 4 | 12/12 = 100% | 5/12 = 42% | 0/12 = 0% | 5.8 (n=12) |
| Fable: no rental ante 1-2 | 4 | 3.25 | 3 | 2/4 = 50% | 1/4 = 25% | 0/4 = 0% | 11.5 (n=3) |
| Haiku: rental acquired ante 1-2 | 10 | 2.90 | 3 | 8/10 = 80% | 0/10 = 0% | 0/10 = 0% | 4.5 (n=10) |
| Haiku: no rental ante 1-2 | 2 | 3.50 | 3.5 | 2/2 = 100% | 0/2 = 0% | 0/2 = 0% | 7.3 (n=2) |

Model-stratified difference (rental acquired ante 1-2 minus no rental ante 1-2): mean final ante +0.16, P(ante 5) -10 pts, P(ante 7) -2 pts.


### Landmark: such runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 123 | 4.27 | 4 | 123/123 = 100% | 43/123 = 35% | 5/123 = 4% | 7.6 (n=123) |
| no rental ante 1-2 | 52 | 4.69 | 5 | 52/52 = 100% | 30/52 = 58% | 4/52 = 8% | 11.6 (n=52) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: rental acquired ante 1-2 | 66 | 4.61 | 4 | 66/66 = 100% | 28/66 = 42% | 5/66 = 8% | 8.2 (n=66) |
| Opus: no rental ante 1-2 | 30 | 5.00 | 5 | 30/30 = 100% | 21/30 = 70% | 4/30 = 13% | 12.2 (n=30) |
| Sonnet: rental acquired ante 1-2 | 37 | 3.95 | 4 | 37/37 = 100% | 10/37 = 27% | 0/37 = 0% | 7.6 (n=37) |
| Sonnet: no rental ante 1-2 | 18 | 4.28 | 4 | 18/18 = 100% | 8/18 = 44% | 0/18 = 0% | 11.1 (n=18) |
| Fable: rental acquired ante 1-2 | 12 | 4.17 | 4 | 12/12 = 100% | 5/12 = 42% | 0/12 = 0% | 5.8 (n=12) |
| Fable: no rental ante 1-2 | 2 | 5.00 | 5 | 2/2 = 100% | 1/2 = 50% | 0/2 = 0% | 12.3 (n=2) |
| Haiku: rental acquired ante 1-2 | 8 | 3.12 | 3 | 8/8 = 100% | 0/8 = 0% | 0/8 = 0% | 4.5 (n=8) |
| Haiku: no rental ante 1-2 | 2 | 3.50 | 3.5 | 2/2 = 100% | 0/2 = 0% | 0/2 = 0% | 7.3 (n=2) |

Model-stratified difference (rental acquired ante 1-2 minus no rental ante 1-2): mean final ante -0.39, P(ante 5) -22 pts, P(ante 7) -3 pts.


### Subset where that shop did offer a rental scorer (the actual decision), all such runs

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 61 | 3.79 | 4 | 50/61 = 82% | 17/61 = 28% | 4/61 = 7% | 7.1 (n=60) |
| no rental ante 1-2 | 17 | 4.00 | 4 | 13/17 = 76% | 7/17 = 41% | 1/17 = 6% | 10.3 (n=17) |

### (same subset) reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental acquired ante 1-2 | 50 | 4.20 | 4 | 50/50 = 100% | 17/50 = 34% | 4/50 = 8% | 7.5 (n=50) |
| no rental ante 1-2 | 13 | 4.62 | 5 | 13/13 = 100% | 7/13 = 54% | 1/13 = 8% | 11.5 (n=13) |

### Type of the first scorer acquired at ante 1-2 (all runs with an ante-1 shop)

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| first ante 1-2 scorer was a rental | 99 | 3.70 | 3 | 78/99 = 79% | 26/99 = 26% | 5/99 = 5% | 5.9 (n=98) |
| ... a perishable (non-rental) | 81 | 3.99 | 4 | 73/81 = 90% | 26/81 = 32% | 4/81 = 5% | 8.3 (n=79) |
| ... clean/eternal | 260 | 4.18 | 4 | 216/260 = 83% | 114/260 = 44% | 14/260 = 5% | 9.6 (n=246) |
| no scorer acquired ante 1-2 | 17 | 1.71 | 2 | 1/17 = 6% | 1/17 = 6% | 0/17 = 0% | 7.1 (n=9) |

### Same, runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| first ante 1-2 scorer was a rental | 78 | 4.17 | 4 | 78/78 = 100% | 26/78 = 33% | 5/78 = 6% | 6.3 (n=78) |
| ... a perishable (non-rental) | 73 | 4.23 | 4 | 73/73 = 100% | 26/73 = 36% | 4/73 = 5% | 8.3 (n=73) |
| ... clean/eternal | 216 | 4.69 | 5 | 216/216 = 100% | 114/216 = 53% | 14/216 = 6% | 10.1 (n=216) |

## (c) xMult rental vs non-xMult rental (ante 1-2)

### All runs with an ante-1 shop

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| xMult rental ante 1-2 | 30 | 3.63 | 3.5 | 21/30 = 70% | 10/30 = 33% | 0/30 = 0% | 7.8 (n=30) |
| non-xMult rental(s) only | 242 | 4.02 | 4 | 211/242 = 87% | 79/242 = 33% | 11/242 = 5% | 7.2 (n=239) |
| no rental ante 1-2 | 185 | 3.90 | 4 | 136/185 = 74% | 78/185 = 42% | 12/185 = 6% | 10.5 (n=163) |

### Landmark: runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| xMult rental ante 1-2 | 21 | 4.33 | 4 | 21/21 = 100% | 10/21 = 48% | 0/21 = 0% | 9.1 (n=21) |
| non-xMult rental(s) only | 211 | 4.34 | 4 | 211/211 = 100% | 79/211 = 37% | 11/211 = 5% | 7.5 (n=211) |
| no rental ante 1-2 | 136 | 4.75 | 5 | 136/136 = 100% | 78/136 = 57% | 12/136 = 9% | 11.1 (n=136) |

Small N for xMult rentals (21 in the landmark cohort): no reliable difference from flat
rentals on mean ante; P(reach 5) 48% sits between flat rentals and no rental. Eternal rentals at ante 1-2: 13 runs.

## (d) Perishable acquired at ante 1-2 vs none

### All runs with an ante-1 shop

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| perishable acquired ante 1-2 | 289 | 4.17 | 4 | 251/289 = 87% | 114/289 = 39% | 19/289 = 7% | 8.4 (n=283) |
| none | 168 | 3.57 | 4 | 117/168 = 70% | 53/168 = 32% | 4/168 = 2% | 8.7 (n=149) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: perishable acquired ante 1-2 | 146 | 4.51 | 4 | 131/146 = 90% | 70/146 = 48% | 16/146 = 11% | 9.0 (n=143) |
| Opus: none | 92 | 3.58 | 4 | 63/92 = 68% | 32/92 = 35% | 3/92 = 3% | 9.0 (n=79) |
| Sonnet: perishable acquired ante 1-2 | 106 | 3.85 | 4 | 86/106 = 81% | 33/106 = 31% | 3/106 = 3% | 8.2 (n=104) |
| Sonnet: none | 58 | 3.50 | 3.5 | 41/58 = 71% | 17/58 = 29% | 0/58 = 0% | 7.9 (n=52) |
| Fable: perishable acquired ante 1-2 | 19 | 4.37 | 5 | 18/19 = 95% | 10/19 = 53% | 0/19 = 0% | 7.9 (n=18) |
| Fable: none | 11 | 4.27 | 4 | 9/11 = 82% | 4/11 = 36% | 1/11 = 9% | 11.0 (n=11) |
| Haiku: perishable acquired ante 1-2 | 18 | 3.11 | 3 | 16/18 = 89% | 1/18 = 6% | 0/18 = 0% | 5.6 (n=18) |
| Haiku: none | 7 | 2.86 | 3 | 4/7 = 57% | 0/7 = 0% | 0/7 = 0% | 7.2 (n=7) |

Model-stratified difference (perishable acquired ante 1-2 minus none): mean final ante +0.64, P(ante 5) +9 pts, P(ante 7) +5 pts.


### Landmark: runs that reached ante 3

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| perishable acquired ante 1-2 | 251 | 4.53 | 4 | 251/251 = 100% | 114/251 = 45% | 19/251 = 8% | 8.7 (n=251) |
| none | 117 | 4.41 | 4 | 117/117 = 100% | 53/117 = 45% | 4/117 = 3% | 9.5 (n=117) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: perishable acquired ante 1-2 | 131 | 4.82 | 5 | 131/131 = 100% | 70/131 = 53% | 16/131 = 12% | 9.4 (n=131) |
| Opus: none | 63 | 4.51 | 5 | 63/63 = 100% | 32/63 = 51% | 3/63 = 5% | 9.6 (n=63) |
| Sonnet: perishable acquired ante 1-2 | 86 | 4.30 | 4 | 86/86 = 100% | 33/86 = 38% | 3/86 = 3% | 8.4 (n=86) |
| Sonnet: none | 41 | 4.27 | 4 | 41/41 = 100% | 17/41 = 41% | 0/41 = 0% | 8.8 (n=41) |
| Fable: perishable acquired ante 1-2 | 18 | 4.56 | 5 | 18/18 = 100% | 10/18 = 56% | 0/18 = 0% | 7.9 (n=18) |
| Fable: none | 9 | 4.78 | 4 | 9/9 = 100% | 4/9 = 44% | 1/9 = 11% | 11.9 (n=9) |
| Haiku: perishable acquired ante 1-2 | 16 | 3.25 | 3 | 16/16 = 100% | 1/16 = 6% | 0/16 = 0% | 6.0 (n=16) |
| Haiku: none | 4 | 3.50 | 3.5 | 4/4 = 100% | 0/4 = 0% | 0/4 = 0% | 8.8 (n=4) |

Model-stratified difference (perishable acquired ante 1-2 minus none): mean final ante +0.15, P(ante 5) +1 pts, P(ante 7) +4 pts.


## (e) Permanent non-rental +mult jokers at the end of ante 2 (runs that reached ante 3)

### >=2 vs fewer

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| >=2 permanent non-rental +mult at end of ante 2 | 119 | 4.71 | 5 | 119/119 = 100% | 65/119 = 55% | 8/119 = 7% | 11.1 (n=119) |
| 0-1 | 249 | 4.39 | 4 | 249/249 = 100% | 102/249 = 41% | 15/249 = 6% | 7.9 (n=249) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: >=2 permanent non-rental +mult at end of ante 2 | 71 | 4.83 | 5 | 71/71 = 100% | 41/71 = 58% | 7/71 = 10% | 11.3 (n=71) |
| Opus: 0-1 | 123 | 4.66 | 4 | 123/123 = 100% | 61/123 = 50% | 12/123 = 10% | 8.3 (n=123) |
| Sonnet: >=2 permanent non-rental +mult at end of ante 2 | 33 | 4.48 | 5 | 33/33 = 100% | 17/33 = 52% | 0/33 = 0% | 10.6 (n=33) |
| Sonnet: 0-1 | 94 | 4.22 | 4 | 94/94 = 100% | 33/94 = 35% | 3/94 = 3% | 7.8 (n=94) |
| Fable: >=2 permanent non-rental +mult at end of ante 2 | 10 | 5.00 | 5 | 10/10 = 100% | 6/10 = 60% | 1/10 = 10% | 12.2 (n=10) |
| Fable: 0-1 | 17 | 4.41 | 4 | 17/17 = 100% | 8/17 = 47% | 0/17 = 0% | 7.5 (n=17) |
| Haiku: >=2 permanent non-rental +mult at end of ante 2 | 5 | 3.80 | 4 | 5/5 = 100% | 1/5 = 20% | 0/5 = 0% | 9.1 (n=5) |
| Haiku: 0-1 | 15 | 3.13 | 3 | 15/15 = 100% | 0/15 = 0% | 0/15 = 0% | 5.7 (n=15) |

Model-stratified difference (>=2 permanent non-rental +mult at end of ante 2 minus 0-1): mean final ante +0.26, P(ante 5) +12 pts, P(ante 7) -0 pts.


### Crossed with rental at ante 1-2

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| >=2 perm +mult, no rental a1-2 | 63 | 4.87 | 5 | 63/63 = 100% | 40/63 = 63% | 5/63 = 8% | 12.5 (n=63) |
| >=2 perm +mult, rental a1-2 | 56 | 4.52 | 4 | 56/56 = 100% | 25/56 = 45% | 3/56 = 5% | 9.5 (n=56) |
| 0-1 perm +mult, no rental | 73 | 4.64 | 5 | 73/73 = 100% | 38/73 = 52% | 7/73 = 10% | 9.9 (n=73) |
| 0-1 perm +mult, rental | 176 | 4.28 | 4 | 176/176 = 100% | 64/176 = 36% | 8/176 = 5% | 7.1 (n=176) |

Model-stratified rental effect inside each stratum (mean ante, P5 pts): with >=2 permanent +mult
(-0.39, -21),
with 0-1 (-0.4, -17).

## Later rentals (ante 3-4)

Rental at ante 3-4 among runs that reached ante 3 looks positive, but that is exposure bias (an ante-4 buy needs the run
to reach ante 4). The fair landmark, ante-3 rental among runs that reached ante 4, is flat:

### Rental at ante 3, landmark: runs that reached ante 4

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental at ante 3 | 77 | 4.96 | 5 | 77/77 = 100% | 48/77 = 62% | 5/77 = 6% | 9.9 (n=77) |
| no rental at ante 3 | 199 | 4.99 | 5 | 199/199 = 100% | 119/199 = 60% | 18/199 = 9% | 10.0 (n=199) |

By model:

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| Opus: rental at ante 3 | 43 | 5.02 | 5 | 43/43 = 100% | 30/43 = 70% | 3/43 = 7% | 9.8 (n=43) |
| Opus: no rental at ante 3 | 114 | 5.17 | 5 | 114/114 = 100% | 72/114 = 63% | 16/114 = 14% | 10.3 (n=114) |
| Sonnet: rental at ante 3 | 24 | 4.92 | 5 | 24/24 = 100% | 14/24 = 58% | 1/24 = 4% | 9.3 (n=24) |
| Sonnet: no rental at ante 3 | 67 | 4.76 | 5 | 67/67 = 100% | 36/67 = 54% | 2/67 = 3% | 9.7 (n=67) |
| Fable: rental at ante 3 | 9 | 4.89 | 4 | 9/9 = 100% | 4/9 = 44% | 1/9 = 11% | 12.3 (n=9) |
| Fable: no rental at ante 3 | 14 | 4.93 | 5 | 14/14 = 100% | 10/14 = 71% | 0/14 = 0% | 8.9 (n=14) |
| Haiku: rental at ante 3 | 1 | 4.00 | 4 | 1/1 = 100% | 0/1 = 0% | 0/1 = 0% | 7.0 (n=1) |
| Haiku: no rental at ante 3 | 4 | 4.25 | 4 | 4/4 = 100% | 1/4 = 25% | 0/4 = 0% | 8.9 (n=4) |

Model-stratified difference (rental at ante 3 minus no rental at ante 3): mean final ante -0.04, P(ante 5) +2 pts, P(ante 7) -3 pts.


### Rental at ante 3-4, runs that reached ante 5 (P7 only)

| group | N | mean final ante | median | P(reach ante 3) | P(reach ante 5) | P(reach ante 7) | mean $ at ante 2-3 shop entries |
|---|---|---|---|---|---|---|---|
| rental ante 3-4 | 86 | 5.60 | 5 | 86/86 = 100% | 86/86 = 100% | 11/86 = 13% | 11.2 (n=86) |
| none ante 3-4 | 81 | 5.65 | 5 | 81/81 = 100% | 81/81 = 100% | 12/81 = 15% | 11.7 (n=81) |

## Recommendation (player HARD RULE)

1. **Ante 1-2: no flat (+mult/+chips/utility) rental, even at 0 scorers.** In the landmark cohort, an ante 1-2 rental
   goes with about 20 pts lower P(reach ante 5) (model x era stratified) and ~$3.5 less at ante 2-3 shops. That holds
   in the 0-clean-scorer shop subset too. At 0 scorers, a perishable or a Buffoon pack beats a rental as the first
   scorer (P5 32% vs 26%).
2. The xMult exception can stay (N=21 landmark runs, P5 48% vs 57% no rental: not clearly harmful). Sell any held rental in the first shop
   where a clean scorer is bought. Never take 2 rentals before ante 3 (2+: P5 33%).
3. Target **>=2 permanent non-rental +mult by the end of ante 2** (+12 pts P5, stratified). Perishables at ante 1-2 are
   neutral to slightly positive and are the preferred bridge. Leave the ante 3+ rental rule as is (ante-3 landmark: no effect).
