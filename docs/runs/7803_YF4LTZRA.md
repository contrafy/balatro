# Run YF4LTZRA (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big (34698/37500)

Ante 1 (300 Skip / 450 Holo / The Pillar 600, $4): Small jokerless: Straight 2-6 200 + 2P QQTT 120. Shop $5: Buffoon -> holo Cloud 9{RENTAL} (override Erosion: +0 on a 52-card deck; holo +10 mult, $4/round covers rent). Big: Pair 55 240, Pair 88 312 (2-card plays for Pillar). Shop $7: Scholar $4. Pillar: 2P 8833 372 + Pair JJ 360.
Ante 2 (1000 Polychrome / 1500 Buffoon / The Wheel 2000, $10): reroll (override LEAVE, ratio 0.39) -> Dusk{ETERNAL} $5, $0. Skipped Small (Polychrome tag; $0 shop useless). Big: Straight K-high 1106 + Pair 88 312 + 2P 4433. Shop $5: polychrome Drunkard{PERISH,RENTAL} $0 (x1.5 + 1 discard; override LEAVE). Wheel: Trips 555 877 + Trips 777 994 + 2P.
Ante 3 (3200 Standard / 4800 Uncommon / The Goad 6400, $8): EMERGENCY ratio 0.32 -> Acrobat{ETERNAL} $6 (x3 final hand, pairs with Dusk). Skipped Small (Standard tag) -> Mega Standard: Gold 9S gold seal + Steel 6H. Big: High AD 810 + High 7D 198 + final spade Flush 8001 est. Shop $11: Uranus (2P L2). Goad (spades debuffed): Pair 44 351 + High KC 258 + final FH 666QQ 7308 est.
Ante 4 (9000 Buffoon / 13500 Ethereal / The Tooth 18000, $12): Half Joker{PERISH} $5 (override Celestial: it wanted Pluto). Skipped Small (Buffoon tag, Mega Buffoon: Lusty/Droll/Mail-In/Raised Fist, skipped). Big: Pair TT 1485, 3 discards digging, throwaway, final Pair AA 34371 est. Shop $13: sold Drunkard (1 round left), Hanging Chad $4. Tooth: singles QH/KS ~1100 each, final Pair AA 40572 est.
Ante 5 (25000 Foil / 37500 Economy / The Mouth 50000, $13): Buffoon $4 (Photograph{RENTAL}/Jolly{ETERNAL}, skipped), Arcana $4 -> Hanged Man (destroyed 4C 2D). Skipped Small (override: $5 shop, non-Ace finals 7-21k). Big 37500: 2P 9977 dig 1170, 2 discards found AS AD, Pair JJ dig 600, final Pair AA 32928 est (no steel/3rd Ace drawn) -> 34698/37500. GAME OVER.

## Post-mortem

Binding constraint: SCALING on a single-card engine. From ante 3 on every blind was cleared by ONE final hand
(Acrobat x3 + Dusk retrigger + Hanging Chad on a Scholar Ace pair: ~33-40k), with Pair still at L1 and zero other
xMult. That engine needs two Aces (4 of 52) every round; ante 5 Big needed 37500 and the drawn AA made 32928 + 1770 of
digging. Money was the second constraint: two rentals (Cloud 9 + Drunkard) took $6/round at antes 2-4, so every shop
had $5-13.

Decisions I would change:
1. Pair level. I never bought a Mercury/Celestial. Pair L2 (+15 chips, +1 mult) on the final AA = 211 x 171 = 36081,
   +1770 = 37851 > 37500: one $4 Celestial at ante 4 (passed twice, partly because the advisor targeted Pluto) wins
   the blind. The Acrobat final is the main hand; level ITS type.
2. Ante 5 Small skip. Saved a risky 25000 blind, but cost a shop visit where a Mercury/xMult could appear, and money.
   With a single-card engine, more shops beat fewer blinds from ante 5.
3. Ante 5 shop: $8 on a Buffoon pack (nothing usable) + Arcana (Hanged Man, thinning 2 cards). Better: Celestial-type
   spending or keeping $13 for interest + the next shop.
4. Drunkard{RENTAL} poly at ante 2 was right for the Wheel (x1.5 + discard), but holding it through ante 3 cost $9 rent.

Reusable rules (if-then):
- IF Acrobat is your xMult, THEN your "main hand" is whatever you play LAST: buy that type's planet every shop (each
  level is ~+8-10% on the round because the x3 applies to it), and play cheap 1-3 card throwaways (with Half Joker)
  before it.
- IF your finals depend on a specific rank (Scholar Aces, Hanging Chad first card), THEN add copies of that rank
  (Death/Strength from SHOP tarots, Standard packs); a deck with 4 Aces gives AA in ~55% of rounds only after digging
  with 2 discards and 2 five-card plays.
- IF you hold a Steel card, THEN never play it (advisor sometimes picks it as a throwaway/pair card): it multiplies the
  base mult only while held.
- IF Dusk + Acrobat are owned, THEN dig with 5-card plays and both discards first, and keep the best <=3-card hand
  for the last hand; the 1st/2nd hands' score is noise next to the x3 final.
- IF Mail-In/Erosion/econ jokers compete with a holo/foil/poly edition joker in a pack, THEN count the edition:
  holo Cloud 9 (+10 mult, $4/round covering rent) carried ante 1-2.

Advisor/CLI defects:
- Main-hand detection counts Acrobat throwaway plays: after ante 3 shopadvise said "main hand High Card" and ranked
  Celestial packs as "take Pluto", while every round was won by a Pair/FH final.
- Final-hand estimate in ADVICE text ignores Dusk: "Flush ~4221 as the last hand" when `hands` on the final hand
  showed est 8001; "Pair AA ~14580 as the last hand" vs final est 34371.
- Ante 4 Big: ADVICE "play PAIR 5 6" used the Steel 6H as the throwaway pair (losing its held x1.5); the Goad's first
  ADVICE discard kept 6S 6H(steel) 2D as a pair to play.
- Pack advise ranked Erosion (adds 0 on a 52-card deck) over holo Cloud 9 at ante 1.
- Solver printed `p >=0.99 (calibrated)` for every option at antes 1-4 (e.g. ante-2 Big at 360 vs 1500, ante-4 Big),
  so it gave no ranking signal until ante 5, where it produced real values (0.68 / 0.88 / 0.63).
- My own error: I sent `sell` and `buy` in parallel tool calls; the buy was checked before the sell landed ("NOT
  LEGAL NOW ... Nothing was sent"), no reject recorded. Bridge: no offline, no rejects.
