# Run ISNYLLW6 (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Arm (8780/50000)

Ante 1 (300/450/Manacle 600): Small with no jokers: 2P 108 + FH 300. Shop $5: Mystic Summit (passed on an eternal rental Shoot the Moon). Big: used both discards, club Flush 1463. Manacle: 2P 510 + High K 240. $6 -> $13.
Ante 2 (1000/1500/House 2000): Spare Trousers $6. Small: 2P 798 + Pair J (chose 2P over a flush that cleared, to grow Trousers). Big: FH 333QQ 1587. Rerolled $5 -> nothing. House: discarded the face-down cards, Trips 7 1122 + Straight 9-5 1495. $19.
Ante 3 (3200/4800/Club 6400): rerolled -> Supernova{ETERNAL} $5. Small: 2P 1242 + Pair K 750 + 2P 1620. Buffoon $4 -> Card Sharp{PERISHABLE,RENTAL}. Big: registered Pair 33 208, Pair J x3 2610, Pair K x3 2700. Misprint $4. Club: Pair 33 455, Pair Q x3 2700, Pair J x3 3510. $0.
Ante 4 (9000/13500/Tooth 18000): skipped Small for an Orbital Tag (Pair L1 -> L4) and saved a Card Sharp tick. Big: Pair 44 1512, Pair A x3 ~12000. Jumbo Buffoon $6 -> Popcorn (the pack had no scorer). Tooth: Pair K 4425, Pair A x3 15246. Money -$6.
Ante 5 (25000/37500/Arm 50000): $0 shop. Skipped Small for a Meteor Tag (no Mercury: took Uranus and Earth), which kept Card Sharp alive for Big. Big: Pair Q 5925 + Pair A x3 15939 + Pair K x3 cleared (Misprint rolled high). Card Sharp perished; sold it and Trousers for a $4 Buffoon (Zany). The Arm: 4080 + 2600 + 2100 = 8780/50000.

## Post-mortem
Binding constraint: SCALING + MONEY. The only multiplier all run was Card Sharp x3, a perishable rental picked at ante 3 and dead after ante 5 Big. No permanent xMult was ever offered in a shop I could afford. Money was $0-7 from ante 3 on (rent $3/round, The Tooth -$7, no Small Blind income), so there was never a reroll budget. Without Card Sharp the best hand was ~5k against a 50k boss.

Decisions I would change:
- Ante 2: I picked Spare Trousers and played Two Pair, then switched to Pair once Card Sharp arrived. That stopped Trousers' growth and split the planets: the Meteor pack had Uranus, which no longer helped. Pick one family by ante 3. With Card Sharp, Pair is the easiest type to repeat.
- Ante 3 Club shop: Misprint for $4 left me at $0-3 for the whole of ante 4. A $4 Celestial (38% Mercury) or keeping the interest probably mattered more. A flat +11 mult on ~45 mult is only +25%.
- Ante 4 Big shop: I took the Jumbo Buffoon ($6 -> $1) and got Popcorn. Holding the money for interest would have given ~$8 at ante 5 instead of $0. It would not have bought an xMult either.
- The Orbital Tag skip (Pair +3 levels) was the best decision of the run. Without it, the ante-4 Big is lost.

What worked:
- Card Sharp sequencing: register a cheap Pair on hand 1 while keeping both discards, then dig with the discards so Summit's +15 is active for the two x3 Pairs. Clear every blind at ante 3-5 Big this way.
- Keep the other pair out of the fillers. Twice `advise` used a card of the pair I needed for the next x3 hand as a filler; I dropped it from the filler list.
- Skip the Small Blind to save a perishable xMult's last tick when Small pays $0 and the tag pays now (Meteor/Orbital).

Reusable rules (if-then):
- IF the Small Blind tag is Orbital for your main hand, THEN skip at any ante: +3 levels now is worth more than the $0 Small Blind shop.
- IF your only xMult is perishable with N rounds left and the Small Blind pays $0 with a tag that pays now, THEN skip the Small Blind so the xMult lasts through Big. A perished joker scores nothing, so plan the boss without it.
- IF you own Card Sharp + Mystic Summit, THEN hand 1 = cheapest Pair with 2-3 junk fillers and both discards kept; then discard twice for pairs; hands 2-3 = Pair x3 with +15. Never fill with a card from a second pair you still need.
- IF Spare Trousers is owned but your x3 engine is Pair, THEN sell Trousers early (it stops growing) and buy Mercury, not Uranus.
- IF you are at ante 4+ with only a perishable xMult and <$5, THEN accept that the run ends when it perishes. The fix is earlier: keep $8+ from ante 3 instead of buying flat +mult jokers (Misprint/Popcorn).

Advisor/CLI defects:
- Main hand switches between Full House / Two Pair / Pair depending on the last play (ante 2-3: "main hand Full House" after one FH while Two Pair had been played 6 times). As a result, the Celestial advice targeted Earth.
- `advise` filler choice breaks pairs needed for the next Card Sharp x3 hand: ante 3 Big "play PAIR 3 4 8 6 2" used 9S from the 99 I needed next; ante 4 Big "play PAIR 1 2 8 6 5" used 7S from 77.
- `advise` right after a discard printed a stale state (ante 4 Tooth: said 1 discard left and advised a discard when 0 remained). `shopadvise` right after a buy also printed the pre-buy shop once. Rerunning after 1-2 s fixed both.
- SCORE CHECK leaves out Mystic Summit (ante 2: "Two Pair ~348" when the real hand was ~1000), so the EMERGENCY label fires too early.
- Blind select said "do not skip" for the Orbital Tag (Pair +3) and the Meteor Tag at ante 4-5. Both skips were clearly right: the tags pay now and they saved a perishable's tick.
- Pack `advise` said SKIP on Riff-raff/DNA/Greedy/Popcorn with a free slot. Popcorn +20 was the only thing that raised the Tooth score.
Bridge issues: none.
