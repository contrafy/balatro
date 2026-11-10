# Run N8XYWGFC (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (7287/13500)

Ante 1 (Coupon/D6/The Pillar 600, $4): Small: 2P 99 77 104, 2P 88 55 92, drew Broadway 324. Shop $4 (Banner{E} $5, Ancient{E} $8 unaffordable): Buffoon -> Scary Face{P} (vs Constellation{E}). Big: Straight 280 + Pair QQ 180. Shop $5: Saturn $3 (SIM +0.09). Pillar: Straight L2 K-9 1050 one-shot.
Ante 2 (Coupon/D6/The Flint 2000, $9): EMERGENCY 0.12; reroll (Chariot/Sun), left $4. Small 1000: Flush 388, Flush 404, FH 540. Shop $4: sold Scary (2 rounds left) -> Photograph{P} $5. Big 1500: Straight Q-8 1498 (2 short!) + Pair 22. Shop $6: Acrobat{RENTAL} $1 (xMult rental allowed), Celestial -> Jupiter. Flint: dig, Pair JJ 50, drew TS -> Broadway final x3 = 1944 (est 1458: advisor rounds Flint mult 7/2 down) = 2009/2000.
Ante 3 (Meteor/Handy/The House 6400, $3): skipped Small for Meteor (Mega Celestial: Jupiter + Venus; Small shop would have had ~$1 after rent). Big 4800: disc to 7 clubs, Pair 33 32, High 30, held club Flush final x3 5136. Shop $4: Jupiter (Flush L4) $3. House: disc 5 face-down, disc 5, Trips KKK 800, Pair 33, spade Flush final x3 7440 = 8272/6400.
Ante 4 (Ethereal/Coupon/The Window 18000, $3): shop $3 (Green Joker $4, Crafty{E,R}); kept Photograph (1 round left). Skipped Small for Ethereal -> Cryptid on 3H. Big 13500: solver UNWINNABLE from the first deal (max round ~9500); dig, discards, diamond Flush final x3 7260 -> 7287/13500. LOSS.

## Post-mortem

Binding constraint: money -> joker supply. Gold Small Blinds pay $0 and from ante 2 the Acrobat rent took $3 of every
~$5-7 round income, so every shop from ante 2 on opened with $1-4. In 9 shop views I saw exactly one permanent any-hand
+mult joker I could have used (Spare Trousers $6 at $3) and never owned a single permanent scorer. The run lived on
Acrobat x3 + a perishable Photograph + Flush L4/Straight L2 planets: final-hand flush ~7300 max, which cleared antes
1-3 (2009/2000, 5198/4800, 8272/6400) and could not reach the ante-4 Big (13500).

Decisions I would change:
1. Ante 2 first shop ($9): a $5 reroll showed two tarots. Holding $9 would have bought Photograph AND kept $4 at the
   next shop (or Spare Trousers at ante 3 with the rent paid). At ante 2 with < $10, a reroll that leaves $4 cannot
   pay for the $5-6 jokers the next shop shows.
2. Ante 1 pack: Constellation{ETERNAL} vs Scary Face{P}. Scary was right for survival, but I then bought 4 planets
   (Saturn, Jupiter x2, Venus + Celestial picks) that would have made Constellation x1.4-1.5 permanently. With a
   planet-heavy line (no jokers affordable), an eternal Constellation is the better pick at ante 1 if the next
   blind is beatable without it.
3. Ante 3/4: nothing to change with $1-4; the Meteor and Ethereal skips were right (saved $6 rent, kept Photograph
   alive, two free packs).

Reusable rules (if-then):
- IF you own Acrobat (x3 on the final hand) THEN dig with hands 1-2 (spare cards + fillers, keep discards) and hold
  the made Flush/Straight for hand 3: it cleared the Flint, the ante-3 Big and The House here.
- IF the Small Blind tag pays NOW (Meteor, Ethereal, Buffoon, Charm) AND the Small shop would open with < $5 after
  rent, THEN skip the Small even at ante 3-4: a $0 shop buys nothing, while the skip saves the rent and a perish tick.
- IF a rental xMult is your only multiplier at ante 2-3 AND income per round <= $6, THEN plan for zero joker buys
  until it is sold: put every dollar into the carry hand's planets (they stack with Acrobat's x3) instead of rerolls.
- IF The Flint and the hand's mult is odd, THEN the game rounds the halved mult UP (7 -> 4): the advisor's est is
  low by up to 33% (Straight L2: est 1458, actual 1944).

Advisor/CLI defects:
- The Flint: est/solver round the halved mult down (Straight L2 60x7 -> est 1458, actual 1944, i.e. the game uses
  floor(x/2 + 0.5)); the solver rated the winning Broadway line p 0.01-0.04 and nearly steered me off it.
- shopadvise kept calling my main hand "Straight (L2, 5 plays)" and flagged Jupiter as "planet for another hand"
  while Flush (L3-L4) was my most-played big hand and the one that carried Acrobat finals; Celestial advice said
  "take Saturn" and the pack advice picked Mars/Venus over the SIM's Jupiter.
- shopadvise ante 4 ADVICE "sell Photograph (1 round left) for Green Joker $4": Photograph's last round doubles the
  next final hand (x2 on ~7000), Green Joker adds +1-3 mult.
- `s` at ante 3/4 blind select said "do not skip" for Meteor/Ethereal (pack now) when the Small shop would open with
  ~$1 after rent; the skip gate should count the money available in the forgone shop.
Bridge issues: none (73 steps, no rejects).
