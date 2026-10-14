# Run L6YYVEJD (port 7817, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (1294/4800)

Ante 1 (Voucher/Juggle/The Hook 600, $4): Small: disc, Flush D 272 + Pair KK. Shop $5: Acrobat $6 unaffordable -> Buffoon -> Credit Card{E} (over Square), Acrobat on credit ($-5), reroll (whiff). Big: 2 spare plays, held Flush D x3 = 864. Shop: reroll -> Wrathful{P} $5 ($-16). Hook: Straight 2-6 500 + 2P JJ33 230.
Ante 2 (Juggle/Polychrome/The Arm 2000, $-10): Buffoon -> Marble. Skipped Small (Juggle, broke). Big (11 cards): 8S+stone 252, spare, FH KKK33 x3 1596. Passed Celestial (Arm). Arm: 2 discards, solver digs (KK, AH+stone) -> spade Flush KQT96 final x3 est 4560, cleared.
Ante 3 (Ethereal/Holo/The Mouth 6400, $-5): EMERGENCY 0.10. Two rerolls on credit ($-16): nothing scoring (Trousers{E}, Shortcut{E}, Reserved Parking{P}). Skipped Small (broke, Ethereal -> Hex/Ankh, skipped: both destroy Wrathful). Big 4800: 2P 8844+stone est 752 / actual 470 (stone counted as a spade), Pair 66 dig 44, 2 discards for a 5th spade (got 4), High JS+stone x3 780. 1294/4800. GAME OVER.

## Post-mortem

Binding constraint: scaling, caused by money. After ante 1 I never owned a flat +mult joker that fires on every
hand: Acrobat (x3 on the final hand) multiplied a base Pair/Two Pair of 2-5 mult, and the only +mult was a perishable
spade-gated Wrathful. Credit Card bought Acrobat, but every later shop was spent in debt ($-16 at the end) with no
interest, so ante 3 had $4 of credit and two whiffed rerolls. A x3 final hand on a jokerless base tops ~1.5-2.5k;
ante 3 Big is 4800.

Decisions I would change:
1. Ante 1 first shop: Credit Card{E} to afford Acrobat. The x3 carried ante 1-2 (Big 864, FH 1596, Arm 4560), but it
   is a multiplier with nothing to multiply, and the eternal Credit Card plus $16 of debt meant 0 interest and no
   buying power at ante 3. Square Joker (permanent, grows) + $1 left would not have been better; the real problem
   was spending the credit on 3 rerolls ($16 of $20) that found nothing. Rerolls on credit at ante 1-3 were waste.
2. Ante 3 first shop: I rerolled twice instead of buying Spare Trousers{E} ($6, permanent +2 mult per Two Pair) or a
   Celestial. Neither would have saved the 4800 Big, but the rerolls bought nothing at all.
3. Ante 3 Big, hand 1: played Two Pair 8844+stone (solver 0.43, est 752) instead of holding it for x3. The est was
   wrong (actual 470: stone counted as a spade for Wrathful), so all solver p values in this round were inflated.

Reusable rules (if-then):
- IF you take Credit Card to buy an xMult, THEN the remaining credit buys only scorers that add mult (never
  rerolls): debt earns no interest and every later shop starts from the same hole.
- IF your only xMult is Acrobat (or any final-hand multiplier), THEN the next buy must be a flat +mult/+chips joker
  that fires on any hand: x3 of a base Pair (~60) is 180; it needs +10-20 flat mult to clear ante 3 (4800).
- IF a perishable suit joker (Wrathful/Greedy/...) is your only +mult, THEN plan the final hand as a 5-card flush of
  that suit with HIGH cards: 4 low spades (JS TS 4S 2S + x) top at ~4100 on x3 and do not clear 4800.
- IF you are broke at ante 3 with ratio < 0.3, THEN skipping the Small only moves the death to the Big: the skip is
  right only if a tag pays score now (the Ethereal pack offered Hex/Ankh, both destroying the build).

Advisor/CLI defects:
- est/solver count a Stone card as a Spade for Wrathful Joker (+3 mult per spade): "2S(stone)" est 752 vs actual
  470 on Two Pair 8844+stone (94 x 8 vs 94 x 5); "HIGH 8S+stone est 441" also included it. Stone cards have no
  suit; every Wrathful/suit-joker est with a stone in the play is inflated.
- shopadvise ante 1 (after Credit Card was owned): ranked Acrobat 90 but ADVICE said REROLL ("no scoring joker in
  this shop"), which would have thrown the Acrobat away; Acrobat should count as the xMult buy when affordable on
  Credit Card debt.
- s at ante 3 blind select said "do not skip: take the shop" while I held $-16 / $4 of credit (a shop that could buy
  nothing); the broke-skip rule should apply to Credit Card debt too.
Bridge issues: none (50 steps, no rejects).
