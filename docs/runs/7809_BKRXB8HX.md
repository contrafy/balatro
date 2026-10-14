# Run BKRXB8HX (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Small (4568/9000)

Ante 1 (D6/Polychrome/The Head, $4): Small Straight K-high 316. Shop $6: foil Blue Joker{RENTAL} $1 (+154 chips). Big: 2P AA44 360 + JJ 300. Shop $7: Card Sharp{PERISH 5} $6 ($1 left). Head: Pair KK 316 + QQ x3 888.
Ante 2 (Ethereal/Meteor/The Pillar, $4): skipped Small (Ethereal -> Cryptid on KS, 6 kings). Big: QQ 344, 88 x3 984, TT x3 984. Shop $5: Even Steven $4 (Ramen $6 unaffordable by $1). Pillar: Flush D 2544 one-shot.
Ante 3 (Juggle/Polychrome/The Goad, $5): skipped Small (override: keep Card Sharp alive 2 more rounds, save $3 rent, Juggle +3 hand size). Big: Straight 1720, disc, Straight x3 6156. Shop $7: Buffoon -> Matador (mistake: The Goad never sets blind.triggered). Goad: 22 1560, disc, 66 x3 4320, 88 x3 -> clear. Card Sharp perished. $0.
Ante 4 (Boss/Holo/The Mark, $5): SCORE CHECK 0.16 (EMERGENCY). Sold dead Card Sharp ($8). Clever{RENTAL} $1, Arcana (Hanged Man/Lovers/World, skipped). $3. Small 9000: disc faces, disc for straight (missed), dig Pair 99 304, Straight 8-4 2784, Straight A-high 1480 -> 4568/9000. GAME OVER.

## Post-mortem

Binding constraint: money -> no permanent multiplier. Every shop from ante 1 on was entered with $4-8 and left at $0-3.
The run's only xMult was a perishable Card Sharp (dead after ante 3); the foil Blue Joker rental ate $3 every round
(~$18 over 6 rounds), so no interest ever accrued and the one r/g xMult offered (Ramen $6, ante 2) was $1 out of reach.
At ante 4 the deck-wide 75th-pct hand was ~2.7k vs a 9000 Small: lost in the first blind of the ante.

Decisions I would change:
1. Ante 2 shop ($5, Ramen $6 + Even Steven $4): I bought Even Steven. Selling Card Sharp ($3, 3 rounds left) for Ramen
   (permanent x2) would have left the ante-2 boss weaker but given a multiplier that survives ante 4. The Card Sharp
   bridge carried antes 2-3 beautifully and then left nothing behind. Perishable xMults must be replaced while alive.
2. Ante 1 Card Sharp buy to $1 (with a rental already ticking): correct for survival, but together with Blue's rent it
   locked the run at $0-5 for three antes. A rental scorer + a perishable xMult at ante 1 = no economy at all.
3. Ante 3 Buffoon pick Matador over Square Joker: Matador pays only when the boss sets `blind.triggered` (The Hook,
   Tooth, Flint, Psychic/Eye/Mouth/Arm/Ox violations, Crimson Heart, debuff-hand bosses). Suit bosses (Goad/Club/Head/
   Window), The Mark, Wall, Plant, Pillar never trigger it. It earned $0.

Reusable rules (if-then):
- IF you hold a perishable xMult with <=2 rounds left AND the Small Blind pays $0, THEN skip the Small: it keeps the
  xMult alive for Big+Boss, skips one rent charge, and costs only a shop you cannot afford anyway (did this at ante 3:
  Card Sharp then carried Big 4800 and Goad 6400).
- IF Card Sharp is owned, THEN register the type with a cheap 2-card hand and pass even-rank/high cards as fillers you
  keep; with Even Steven the x3 even pairs (66, 88) made 4320 each at L1.
- IF Matador is offered, THEN check the upcoming boss: it pays only for Hook/Tooth/Flint/Psychic/Eye/Mouth/Arm/Ox/
  Crimson Heart (and Psychic-style hand rules). Never take it for a suit boss, The Mark, The Wall, The Pillar.
- IF a r/g xMult (Ramen, etc.) is $1-3 out of reach and you own a perishable xMult with <=3 rounds left, THEN sell the
  perishable to buy the permanent one.
- IF you hold a rental scorer at ante 1-2, THEN do not let a second purchase leave you at $0-1: the rent pushes you
  negative and every following shop is dead.

Advisor/CLI defects:
- Pack advise ranked Matador UTIL ("$8 if boss ability triggers") without checking the upcoming boss (The Goad never
  triggers it); it should score Matador 0 for bosses that never set `blind.triggered`.
- Ante 3 blind select said "do not skip: Juggle Tag not worth a shop visit" while Card Sharp had 2 rounds left; the skip
  kept the run's only xMult alive for the boss (PLAYBOOK 7809_1S259TVC rule). Skip advice should weigh perishable xMults.
- Ante 2 shopadvise listed Ramen as "passed over: costs $6, you have $5" without proposing sell-perishable-then-buy.
- shopadvise state printed $5 in the header and "Shop advisor: ante 4, $8" in the same output (counted the dead Card
  Sharp sale before it happened) - confusing, not harmful.
