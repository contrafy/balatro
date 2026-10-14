# Run YY2DXIBD (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 boss The Head (16212/18000)

Ante 1 (Skip/Double/The Goad 600, $4): Small: Full House 333KK 276 + Straight 296. Shop $5: Buffoon -> Half Joker{ETERNAL} over Misprint ($1 left). Big: Pair JJ 660 one-shot (Half Joker +20 mult: even a 1-card High Card ~315). Shop $7: Celestial pack -> Uranus (no Mercury). Goad: Pair 7 374 + High QC 315.
Ante 2 (Boss Tag/Orbital/The House 2000, $9): EMERGENCY 0.33 -> reroll found Joker Stencil{RENTAL} $1 (x5 with 2 jokers, 6 slots): single Ace 1680, Pair 2200-3300. Played Small 1000 (Boss Tag could reroll House into Psychic/Wall), Big 1500, House 2000 (disc 5 face-down, Pair TT 3300). Buffoon pack at $5: Droll{P}/Joker{E}, skipped. Money $-2..$5 all ante: rent $3 vs $0-5 income.
Ante 3 (Polychrome/Negative/The Needle 3200, $5): Celestial -> Uranus again. Skipped Small (Polychrome tag, saves rent): free polychrome Ride the Bus + Pluto (High Card L2) at $3. Big 4800: Pair QQ + JJ 6600. Needle: Trips AAA 9072 one-shot.
Ante 4 (D6/Boss Tag/The Head 18000, $2): skipped Small 9000 (D6: 2 free-ish rerolls, only Constellation{R}/Chaos/Credit Card seen, $2 could buy nothing). Big 13500: Trips JJJ 8280 + High A 3588 + High A 3744 = 15612 (cleared with 2 to spare). Head: 3 hands = Trips KKK 6900 + Pair 77 3312 + Trips 555 6000 = 16212/18000, 0 discards left after chasing trips (2 discards spent on a 0.29 solver line).

## Post-mortem

Binding constraint: scaling + money. Half Joker + Joker Stencil gave a huge early boost (one card = 1680, ante 3 Trips AAA 9072) but that is a flat per-hand ceiling (~4k pair / ~9k trips at L1) with no leveling: I never saw Mercury (3 Celestial packs: Uranus, Uranus-2nd, Saturn/Mars/Jupiter/Neptune) and never had spare money. The rental Stencil cost $3 every round while Small pays $0, so I held $0-5 at every shop (all of ante 2-4 shops: nothing purchasable but one $3 planet). Ante 4 boss needed 18000 = two trips plus a good third hand; I had one 6-9k hand per round.

Decisions I would change:
1. Ante 2 Jumbo Celestial was $6 vs $5 held; I took the Buffoon pack instead (two junk jokers). In hindsight, buying nothing and reaching the Jumbo Celestial/Arcana next shop would not have helped either; the real miss was never owning a growth/level source. With a Stencil build (x5) every planet for the main hand is worth ~+50% (Pair +15 chips on ~22 mult): prioritize planets over everything at ante 2-3 and keep money for them.
2. Ante 4 Head: I discarded twice to chase trips (0.29 solver) and drew K K K: Trips 6900 + two small hands. With Aces 4416/3744 per card it was never going to reach 18000: the shop before it (ante 4 reroll hunt with D6 tag) had $3 and nothing to buy; skipping the Small for a D6 tag with no money to spend it was weak. Better: play Small (9000 = Trips + High Card) for the extra $-income? Small pays $0 though, so honestly neither fixes it.
3. Taking an Eternal Half Joker was fine early but it capped me at <=3-card hands (no Two Pair/Flush/Full House scaling, Uranus x2 wasted).

Reusable rules (if-then):
- IF you own Half Joker (+20 mult at <=3 cards) THEN a single high card is a real hand (est 315 at ante 1, 1680 with a x5 Stencil): play the best single non-face card and keep hands unspent for $1 each; levels for Pair/High Card/Trips are the only scaling, so buy Mercury/Pluto/Venus whenever offered.
- IF Joker Stencil is a $1 rental at ante 2 with 2 jokers (x5) THEN buy it (first xMult), but do not add jokers (each = -x1) and expect to be at $0-5 for the whole run: rent -$3 with Small $0. Skip Small whenever its tag is free value (saves $3 rent).
- IF the D6 tag is owned THEN the shop rerolls cost $0,$1,$2: only useful with $4+ to buy what it reveals; at $2-3 it found nothing buyable (Chaos/Constellation{R}/Credit Card). Credit Card ($1) would have enabled -$20 debt purchases, and I passed it because of the Stencil slot cost: consider it when broke with a planet/xMult in the shop.
- IF The Needle is the ante-3 boss THEN it is only 3200 (x1 base): trips/pair of Aces clears it with 1 hand.
- IF The Head (ante 4, 18000) and best hand is ~9k trips THEN the run needs two big hands + a decent third; tag skips do not fix it, only levels/xMult do.

Advisor/CLI defects:
- shopadvise/Score check warned EMERGENCY 0.31 at ante 4 but the only affordable action ($2-3) was nothing; the SIM never considered selling Ride the Bus ($5) to fund a planet (none was offered, so moot).
- `advise` Head discard lines: the solver's keep set ("KS 9C 8H", 8H debuffed) kept a debuffed card; the line "SOLVER DISCARD ... keep KS KH 7S 7C" kept a debuffed KH (est 6900 correct, though).
- Pack advise after Celestial packs offered only off-hand planets; `pick` echoes "NOT your main hand" correctly.
