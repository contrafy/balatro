# Run JEMI6XIF (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (436/1500)

Ante 1 (Holo/Foil/The Hook 600, $4): Small 300: disc, disc, 2 solver digs (High Card), spade Flush AKQJ9 340 -> 371. Shop $4: Buffoon -> Hiker (overrode advisor's Ride the Bus{ETERNAL,RENTAL}), $0. Big 450: disc to JT98, Trips 999 171, Straight A-T 324. Shop $5: Odd Todd{PERISH,RENTAL} $1 (SIM 0.18 vs 0.00). Hook: Straight K-9 480, 2 disc, Pair JJ 70, spade Flush 556. $1 after rent.
Ante 2 (Polychrome/Charm/The Flint 2000, $6): SCORE CHECK 0.21 EMERGENCY. Sold Odd Todd, The Trio{RENTAL} $1 (score check fell to 0.09), Jumbo Buffoon $6 (Dusk/Banner perishable, Mime/Crazy eternal) -> Banner{PERISH}; passed Lusty{PERISH} $5 (SIM 0.31). $0. Skipped Small (rent-broke, Poly tag; overrode `s`). Big 1500: Pair JJ+3 fillers 190, High JD dig 80, disc to TT77 (drew QD 9D 3S 3D: diamond flush 456 only), disc 5 keeping QD TH TD (solver p0.43) -> no trips, 2P T9 166. 436/1500. GAME OVER.

## Post-mortem

Binding constraint: NO +MULT SOURCE. After ante 1 my jokers were chips-only (Hiker, Odd Todd, Banner) on a base mult of 2-4,
and the one multiplier (The Trio x3) needs a Three of a Kind in the hand, which Black Deck's 2 discards produce maybe once a
round. Money was $0-6 the whole run (Small pays $0, $4 start), so every shop bought exactly one thing.

Decisions I would change:
1. Ante 2 shop ($6): I sold Odd Todd (chips on every odd pair) to buy The Trio{RENTAL} and then spent $6 on a Jumbo Buffoon
   instead of Lusty Joker{PERISH} $5 (SIM p_next 0.31; it was 0.56 with Odd Todd kept). The score check fell from 0.21
   to 0.09 right after the swap: a hand-gated xMult with no flat mult under it is worth less than the chips it replaced.
   The pack offered only perishables/eternal junk. Best line was probably keep Odd Todd + Lusty (advisor's first ADVICE).
2. Ante 2 Small skip with $0 and a 0.09 score check: the skip was the rent-broke rule (Small pays $0, its shop could buy
   nothing), but it sent a ~450-per-round build straight to 1500. The Small (1000) was also very likely lost, so the
   real mistake was the shop before it, not the skip.
3. Ante 1 first shop ($4): Buffoon -> Hiker (chips-only growth). Crafty{RENTAL} $1 was worse; the pack was right but its
   result (chips, no mult) set up the chips-only problem. Next shop with a scorer choice should have bought +mult.

Reusable rules (if-then):
- IF you own no +mult joker, THEN do not trade a working scorer for a hand-gated xMult (Trio/Order/Duo-for-trips): x3 on
  a 2-3 base mult that fires once a round is smaller than +31-62 chips on every hand. Buy the flat +mult first, the
  gated xMult second.
- IF at ante 2 EMERGENCY with $5-6 and the shop has a concrete scorer the SIM rates (p_next 0.3+) next to a Jumbo
  Buffoon, THEN buy the scorer: the pack can whiff (this one: 2 perishables, 2 eternal off-type) and leaves $0.
- IF Banner is a main chip source, THEN every discard costs 30 chips on the final hand: a Full House that clears with
  1 discard left (TTT77 = 1368) does not clear after using it (1008). Count Banner's loss before a last-hand discard.
- IF Buffoon pack offers an ETERNAL+RENTAL joker, THEN never take it at ante 1 (-$69 unsellable); advisor still ranks it first.

Advisor/CLI defects:
- Pack advise ranked Ride the Bus{ETERNAL,RENTAL} 65 over Hiker 60 at ante 1 (it even prints "-$69 ... never sellable").
  Same class of bug as 7807's Raised Fist{ETERNAL,RENTAL}.
- Final Big Blind decision (1 hand, 1 discard, need 1230, jokers Hiker/Trio/Banner): SOLVER said DISCARD 4 5 6 7 8 keeping
  QD TH TD p 0.43, but Trips TTT scores ~540 and FH TTTQQ ~1080 with Banner at 0 discards; only Quads (2%) cleared.
  The solver appears to keep Banner's +30/discard after the discard is spent (or overrates the trips draw).
- Big Blind hand 2: solver PLAY HIGH (dig) p 0.78 vs rule 0.73 -> the line needed FH+Banner; actual result: no clear.
  Calibration looks too optimistic for Banner/Trio lines.
- shopadvise after selling Odd Todd/buying Trio printed score check 0.09 (from 0.21) but still ranked Jumbo Buffoon 95
  over Lusty 90 by rules (SIM overrode to Lusty); the rule ranking should not prefer a $6 pack that leaves $0 under rent.
Bridge issues: none; 36 steps, no rejects.
