# Run JJAUEH8M (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (4587/4800)

Ante 1 (D6/Foil/The Hook 600, $4): Small: disc 4 for spade flush draw, Flush AKT.. 288 + Two Pair 64. Shop $5: only ETERNAL+RENTAL jokers (Onyx Agate, Clever) -> Buffoon pack $4 offered Runner{R}/Red Card{R} (both rentals, junk) -> skipped; $1 left, no other scorer affordable -> took Onyx Agate{ETERNAL,RENTAL} $1 (+7 mult/club) under the "0 scorers" exception (SIM 0.88 vs 0.01). Big: Two Pair KKJJ (JC) 540 one-shot. Shop $3: passed Mercury. Hook: FH 300 + Straight QJT98 (3 clubs) 1925.
Ante 2 (Economy/Charm/The Pillar 2000, $6): shop nothing (planets only). Small 1000: disc x2, Two Pair 504 + Trips 171 + club Straight 2025 (cleared). Shop $3: Greedy $5 unaffordable, Photograph{E,R} barred. Big 1500: Straight 660 + FH 1012. Shop $5: Buffoon pack -> Sly Joker (over Shoot the Moon perishable); Blackboard{R} $1 barred (2nd rental). Pillar: 2P 990 + Straight 605 + 2P AC/66 1488 (cleared with 405 to spare, last hand 51% line).
Ante 3 (Economy/Double/The Wall 12800, $3): shop $3 nothing (Ride the Bus $6, Jumbo Buffoon $6). Skipped Small 3200 (Economy tag $3->$6, avoids rent; round est ~2970 < 3200). Big 4800: disc, disc for club flush draw: Flush AC TC 8C 7C 6C 3003, junk dig 16, final Two Pair QQ44 1568 = 4587/4800 (short 213).

## Post-mortem

Binding constraint: money and a single rental scorer. Gold's $0 Small and $3/round rent on an unsellable Eternal rental kept me at $0-6 every shop; in 4 shops I could never afford a $6 Buffoon pack or $5 joker. Result: two scorers (Onyx Agate +7 mult/club, Sly +50 chips) at ante 3, no xMult, ~1100-1600 per ordinary hand vs 4800.

Decisions I would change:
1. Ante 1 shop 1 ($5): bought a $4 Buffoon pack that offered only two junk rentals; with $5 a reroll ($5) or keeping $5 for the next shop was no better, but the pack left me at $1 and forced the Onyx Agate Eternal Rental. Onyx was run-saving for ante 1-2 (clubs flush/straight 2000+ twice) but the rent (-$3 x 6 rounds = $18) is exactly the Buffoon/joker budget I lacked later.
2. Ante 3: should have skipped the Big too? No: Wall 12800 unbeatable either way. The real loss was ante 3 Big by 213; skipping Small was right (it saved $3 rent and gave $3) but then I had no shop before the Big. Playing the Small for 3200 would have cost rent for a $0-money shop.
3. Ante 3 Big hand 2: after the flush (3003) I dug with a 5-card junk play. Playing 4 junk cards and keeping AH-high or the clubs 4C/2C changes nothing; the 213 shortfall came from hand 1 choice: I discarded a made Two Pair 87 (est 1600) for a flush draw (3003 realized): that was right. Hand 2 junk dig cost one hand; no better line existed.

Reusable rules (if-then):
- IF the first shop offers only ETERNAL+RENTAL jokers and you own 0 scorers with $5, THEN buy the $1 rental scorer FIRST (keeps $4 for a Buffoon pack); do not spend the $4 pack first and then buy it with $1 left: the order of those two buys gave the same result here but kept $0 afterward.
- IF Onyx Agate (+7 mult/Club) is owned, THEN discard hard toward clubs: club Flush 3003, club Straight 1925/2025, one-club Two Pair 540 cleared Big/Small one-shot at ante 1-2. Beyond ante 3 it is far too small (no xMult).
- IF Pillar is the ante boss, THEN Small/Big hands debuff only the cards played (~14 cards); est stays fine because the deck is 52 cards, 3 hands still found 405 extra.
- IF an eternal rental drains $3/round and you hold < $6 at every shop at ante 3, THEN skip Small blinds (Economy tag doubles the money and avoids a rent tick) and fight only Big + boss.

Advisor/CLI defects:
- shopadvise: "Buffoon Pack $4" ranked first at $5 although the first-shop jokers were all Eternal Rentals and the pack's 2 offered jokers were both rentals; no warning that a pack can be all rentals (30% each).
- SOLVER at ante 3 Big first hand recommended keeping QH JS + pair draw (p 0.26) and later flush draw 0.45 vs 0.40: the solver's p values near 0.4 were accurate (final 213 short).
- advise "play HIGH 1 3 4 5 8" last-but-one hand: p 0.03 - the 5-card junk dig discarded a 2C club while keeping QH; no better line existed, defect not clear.
