# Run PHIIHH8E (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (12303/37500)

Ante 1 (Uncommon/Charm/The Window 600, $4): Small 2P JJ77 108 + Straight Q-8 308 (300). Shop $5: Buffoon pack -> Gluttonous{PERISH} (Burglar{ETERNAL} passed). Big: disc to 5 clubs, Flush 1273 (Gluttonous +3/club). Shop $7: Judgement -> Bull. Window: Flush clubs 1463.
Ante 2 (Meteor/Buffoon/The Mouth 2000, $11): Lusty{ETERNAL} $5. Skipped Small (Meteor: Mercury+Uranus). Big: 2P 828 + Trips 396 + Straight 890. Blue Joker{RENTAL,PERISH} $1 (+2 chips/card left in deck). Mouth: FH AAA66 3088 one-shot.
Ante 3 (Polychrome/Skip/The Water 6400, $15): Photograph $5. Small: Straight 1780 + Flush 1240 + Trips 1260. Shop: Buffoon pack -> Acrobat{E} (x3 final hand). Big: hearts Flush 5472 one-shot. Water (0 disc): Straight 1197 + High 109 + 2P QQ77 5904 (7H first so Lusty +3 lands before Photograph x2).
Ante 4 (Top-up/Double/The Goad 18000, $12): Saturn. Skipped Small (Top-up -> To Do List junk) and Big (Double tag) to keep Blue alive for the boss. Goad: pair 726 + pair 654 as digs, hearts Flush (KH last) 17328 on Acrobat final hand vs 16620 (sold To Do List so Bull +4 chips). Sold perished Blue.
Ante 5 (Investment/Boss/The Serpent 50000, $14 -> reroll): Gros Michel $5 + Crafty $4 ($0 left), Acrobat rightmost. Small 25000: spare pair digs, hearts Flush 24150 on the final hand vs 23800 needed (Gros Michel then died). Shop with $0: sold Bull, Misprint rental $1. Big 37500: best line was ~17-28k; 5 hearts + digs, final Straight K-high 11281 (actual 12303). LOSS.

## Post-mortem

Binding constraint: scaling. At ante 5 I had one real multiplier (Acrobat x3 on the final hand, one flush per round) and flat stuff; a good round was ~17-24k against 25k/37.5k/50k and I had $0. Every blind from ante 3 was cleared by a single heart-flush final hand, which cannot be repeated three times a round.

Decisions I would change:
1. Ante 4: skipped Small+Big with a 5k typical hand. It worked for the boss (17328 vs 16620) but it cost two shops and ~$11 of income, so I entered ante 5 with $14 and no joker slots upgraded. With Acrobat as the only xMult, skipping Small AND Big at ante 4 skipped the only places to find a second xMult.
2. Ante 3 shop ($10 after Photograph): I kept $10 instead of buying the Arcana packs; the real mistake was earlier - the ante 2 Buffoon Tag on the Big (13.5k later) / ante 4 Big skip never produced a pack. I never found a growth xMult (Throwback/Obelisk) or a second flat +mult.
3. Ante 5: I spent the whole $14 on Gros Michel + Crafty and was at $0; Gros Michel died the same round (1/6). The next shop had Popcorn/Misprint I could not afford. A single reroll earlier (ante 4 shop $12, bought a Celestial pack for Saturn instead) might have found Gros/Crafty a shop earlier.

Reusable rules (if-then):
- IF Acrobat is the only xMult, THEN the final hand is the whole round: spend hands 1-2 on spare cards (not the flush cards), keep discards for the 5th flush card, and order flush cards so Lusty/suit +mult cards score BEFORE the first face card (Photograph x2 multiplies the accumulated mult): est rose 4959 -> 5985 / 5776 -> 5890 on reorders; `order hand` is free of cost to the score.
- IF a suit-mult joker (Lusty/Gluttonous) is owned, THEN flushes in that suit are 4-5x a normal flush (1273-1463 at ante 1, 5472 at ante 3, 24150 final at ante 5): discard toward that suit first, other suits' flushes are ~4x weaker (1240 vs 5472 same ante).
- IF a Bull/To Do List-type junk joker is owned and the round is within ~5% of clearing, THEN selling it adds sell $ to Bull's chips (+4 chips = +700 on the final flush).
- IF money is $0 at ante 5 with a 1.5x deficit, THEN the run is dead; the real fix is at ante 3-4: skip Small only for a tag that pays a joker now, play the shops (rerolls with $15+).
- IF The Water (0 discards) is the boss and Acrobat is owned, THEN play the biggest made hand first, a junk hand second (dig), and the Two Pair/Flush last: 1197 + 109 + 5904 = 7210 beat 6400.

Advisor/CLI defects:
- `advise` rule pick at the ante-4 Goad kept Two Pair for a straight draw; the solver's flush-draw line (p 0.67 vs 0.42) was right and was the winning line; the CLI keeps preferring the rule pick unless n >= 300.
- `advise` solver (n=64) at the ante-5 Small proposed "play KH KC KD + fillers" (round p 0.98) which broke my 4-heart flush and ignores that the Acrobat final hand is the only scorer; my own line (spare pair dig, keep hearts) worked.
- `hands`/`advise` est for the Acrobat final hand is not explained: the flush est jumps x3 only on the last hand; the est label should say "final hand x3".
- shopadvise rated Odd Todd/Delayed Gratification (eternal) options on the ante 1 shop with no scorer; fine. Mr. Bones{RENTAL} $1 was shown at ante 3 (hard rule: second rental) and correctly marked -50.
- The Serpent/Boss Tag: BOSS WARNING said "round reaches ~16446 vs 50000" but SCORE CHECK at ante 4 said 0.08; both said I was dead and neither recommended any concrete rerolls with the $14.
