# Run K3HGDAGZ (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Water (4070/6400)

Ante 1 (Foil/Investment/The Club 600, $4): Small: made spade Flush 300/300 one-shot. Shop $6: Buffoon pack -> Raised Fist{RENTAL} (other pick Ancient{E,R}; Bootstraps{P,R} passed). Big: Trips 888 + 2 low fillers 810 (Fist doubles held 6). Shop $5: Green Joker foil $6 unaffordable, left. Club: Quad 4s 1224 one-shot.
Ante 2 (Standard/Garbage/The Window 2000, $9): EMERGENCY 0.34. Passed The Tribe{P,R} $1 (2nd rental, hard rule) and Devious{P} (straight-only chips); rerolled $5 -> Superposition{P,R}/Strength, nothing. Rent-broke ($4, $3 rent) -> skipped Small for Standard tag: gold red-seal 9C + glass 8C. Big 1500: Straight 3-7 1320 + 2P AA88 1276. Shop $6: Hanging Chad{E} $4 (SIM 0.20 vs 0.02). Window: 2P TT44 1044 + Straight 4-8 1430.
Ante 3 (Skip/Top-up/The Water 6400, $5): SCORE CHECK 0.19 EMERGENCY. Passed Blue Joker{RENTAL} $1 (advisor BUY, SIM 0.48 vs 0.05; 2nd rental = hard rule); Driver's License{E} $10 unaffordable. Skipped Small (Skip tag +$10 -> $15) and Big (Top-up -> Mad Joker + Banner). Water (0 discards): Pair 99 1210, Pair JJ 900, 2P TT55 1960 = 4070/6400. Died holding $15.

## Post-mortem

Binding constraint: SCALING from economy. Only $4-9 per shop through ante 2 (Small pays $0, Raised Fist rent $3/round),
so the whole run bought one Buffoon pack and one $4 joker. Entering ante 3 the only scorer was Raised Fist (+~16-20
mult) plus Hanging Chad (card retrigger, not a multiplier): 75th-pct hand ~1100 vs a 6400 boss. Every shop offered
mostly stickered jokers (Bootstraps{P,R}, Tribe{P,R}, Scholar{P,R}, Superposition{P,R}, Blue{R}, Driver's{E} $10).

Decisions I would change:
1. Ante 3 skip-both line: I skipped Small (Skip tag +$10) and Big (Top-up) and reached The Water with $15 I could
   not spend. Playing the Big (4.3x my hand) looked worse, so the run was effectively lost at the ante-3 shop; but no
   shop exists between a Small skip and the boss when the Big is skipped too, so that money never became score.
2. Ante 2 first shop: the $5 reroll whiffed and left $4; that $5 plus the later $4 would have bought the Jumbo
   Standard/Celestial levels or kept me able to afford a $6 joker. With 1 scorer at ante 2, a reroll at $9 is a coin flip.
3. Ante 1 Big shop: Green Joker foil $6 was $1 short. Buying the ante-1 Buffoon pack ($4 of $6) instead of keeping $6
   was right (it produced the only scorer), but it shows that the first two shops decide Gold runs.

Reusable rules (if-then):
- IF you skip BOTH Small and Big without Throwback, THEN the tag money is unusable until after the boss: only do it
  when the boss is already beatable with your current hand (>= boss/3 per hand), never as a rescue for a 0.2 ratio.
- IF the boss is The Water and Top-up/Buffoon gives Banner, THEN Banner is +0 there (0 discards); do not count it.
- IF your only mult source is Raised Fist, THEN keep high cards held and play low fillers (Big: Trips 888 + 2 low
  fillers went 378 -> 810 est); `advise` already pads correctly.
- IF Hanging Chad is owned with a Glass card, THEN `move hand` the Glass card first in a pair of its rank: x2 three
  times on base mult (only base mult, so it matters mainly before +mult jokers stack).

Advisor/CLI defects:
- shopadvise ante 3 ADVICE was `buy 2` Blue Joker{RENTAL} as a SECOND rental before ante 5 (SIM +0.44); the hard rule
  forbids it; the advisor's own text said "a second rental before ante 5 drains the run to $0" but still chose it.
- shopadvise ante 2 rule pick ranked The Tribe{PERISHABLE,RENTAL} "NEEDED NOW" (x2 if Flush, ~x1 on the deck) as a
  2nd rental; SIM correctly preferred others.
- Standard pack opened from a Standard Tag has no `advise` ("No pack advice for this pack type").
- `s` at the ante-3 Big select says "never skip the Big" without weighing Top-up (2 free jokers) vs a 4.3x Big.
