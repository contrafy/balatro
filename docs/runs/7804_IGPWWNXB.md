# Run IGPWWNXB (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (14185/60000)

Ante 1 (Economy/Voucher/The Window 600, $4): Small: disc, 2P AA88 116 + Straight 3-7 220. Shop $5: Buffoon -> Greedy (over Hallucination{E,R}). Big: 2P JJ77 270 + 2P TT66 260. Shop $6: Smiley $4. Window: disc 9D 6D, Straight K-9 1501 one-shot.
Ante 2 (Rare/Negative/The Hook 2000, $9): Mega Buffoon $8 -> polychrome Clever{RENTAL} + Odd Todd{PERISH}. Skipped Small (rent-broke $1, Rare tag). Big: 2P AA22 564 + 2P QQ77 4410. Shop: Rare tag = Campfire{ETERNAL} $0, Credit Card{PERISH} $1. Hook: disc, 2P JJ33 3384 one-shot.
Ante 3 (Uncommon/D6/The Fish 6400, $6): EMERGENCY 0.31. Reroll ($1), sold Credit Card, flipped $1 rentals Wily + Blue (bought+sold same shop) -> Campfire x1.75 for $0 net. Skipped Small (Uncommon tag, broke). Big: Flush spades 5108 one-shot. Shop: Uncommon tag = Bootstraps $0, flipped (+$3, Campfire x2). Fish: disc, Flush hearts 6006, discard 5 (face-down + low) -> face-up JJ, Pair 1350.
Ante 4 (Garbage/Foil/The Goad 18000, $12): EMERGENCY 0.11. Flipped Shortcut{P,R} + Egg{R} ($1 rentals) -> Campfire x1.5 after a $5 reroll. Skipped Small (override: 9000 vs est 8.4k, Garbage tag +$9, kept Odd Todd alive). Big 13500: 2P QQ44 3456, 2P 6655 3312, disc, final 2P KK99 6750 (needed 6732). Shop $19: sold perished Odd Todd, Justice $3, Diet Cola $6, reroll, Green $4; sold Diet Cola (Double Tag) -> Campfire x2. Goad: Justice -> glass QD (last scoring card), 2P KKQQ 20580 one-shot.
Ante 5 (Juggle/Rare/The Tooth 50000, $10): Acrobat $6, flipped Neptune (Campfire x1.25). Skipped Small (override: Double Tag -> 2 Juggle tags = 14-card hand for the Big). Big 37500: sold Green (Campfire x1.5), junk Straight 2-6 787, disc -> KKK JJ, non-final FH 99922 3397, final FH KKKJJ 36720 (Acrobat). Shop $5: Chariot $3. Tooth: Chariot -> steel 2C (held), 2 discards -> QS QD JS JD, junk pair 55 135, pair JJ 1518, final 2P KKQQ glass QD last + steel held + Acrobat 59535. $-11 after.
Ante 6 (Foil/Handy/The Serpent 120000, $-6): shop had Gros Michel/Blue{E} at $5, unaffordable at $-6. Sold Greedy (Campfire x1.25). Small 60000: disc, Pair TT cycle 168, disc, junk High 45, final 2P QQ99 13972 (Acrobat, steel held). No glass QD or third face drawn. LOSS.

## Post-mortem

Binding constraint: scaling plus money, from ante 2 on. I never owned a permanent xMult except Acrobat (ante 5) and a
polychrome Clever (x1.5). Every blind from ante 3 to 5 was cleared by temporary multipliers: Campfire fed by selling
$1 rentals and free tag jokers (x1.5-2.0 per ante, reset after each boss), a Justice glass QD, a Chariot steel 2C held
in hand, and Acrobat's x3 on the final hand. That stack beat the Goad (20580/18000), the ante-5 Big (40904/37500) and the
Tooth (61188/50000), but always by a thin margin and only when the right faces showed up. Clever's rent (-$3 every
round from ante 2) and the Tooth's -$1 per card left me at $-6 for the ante-6 shop, so I could not buy the Gros Michel
(+15 mult) on offer. At ante 6 Campfire had reset to x1, Greedy was sold, and a normal round made ~14k against 60k.

Decisions I would change:
1. Ante 2 Mega Buffoon: I picked polychrome Clever{RENTAL}. Its x1.5 and +80 chips carried antes 2-5, but the rent
   came to ~$27 by ante 6, which was the money I needed for ante-5/6 xMults. A non-rental scorer from the same pack
   (Odd Todd/Devious) costs nothing per round. By ante 4 Campfire was carrying Clever, so I should have sold it then.
2. Ante 4 shop ($21 after selling Odd Todd): I spent it on Justice + Diet Cola + reroll + Green Joker. That cleared the
   Goad, but Green (sold a round later) and the reroll were waste. Keeping $10 would have left me ~$5 at the ante-6
   shop instead of $-6.
3. The Tooth: I played 3 + 3 + 4 cards (-$10). A 1-card cycle on hand 2 would have saved $2 but lowered the FH chance.

Reusable rules (if-then):
- IF you own Campfire, THEN every $1 rental in the shop is a free +x0.25: buy it and sell it in the same shop (sell
  value $1 = cost). The same goes for free tag jokers (Uncommon/Rare tag): flipping Bootstraps gave +$3 AND +x0.25.
  Perished jokers still sell for +x0.25. Campfire resets after the boss, so feed it in the first shop of each ante.
- IF a Double Tag is pending at ante 5 AND the Small offers a Juggle Tag, THEN skip: two Juggle tags = a 14-card hand
  for the Big, which made KKK JJ + 999 22 in one round (40.9k vs 37.5k).
- IF Acrobat is owned, THEN treat hands 1-2 as cycles: play junk (pairs of low cards, a junk straight) to draw new cards,
  hold the made face Two Pair/FH for the final. The solver found these lines (p 0.94 vs 0.80 rule pick).
- IF your +mult is all card-phase (Smiley, Greedy, suit jokers) THEN Glass and Steel are real multipliers, not +10%:
  put the Glass face LAST in hand order (glass doubles the mult the earlier cards built: KKQQ 12180 -> 20580) and Steel
  a junk card you always hold (x1.5 on the whole card-phase mult). This is the opposite of the 9IIGB2FF Steel note,
  which applies to joker-phase +mult builds.
- IF you are broke at The Fish, THEN discard the face-down cards: discard draws come face up (a 5-card discard found JJ).

Advisor/CLI defects:
- shopadvise SIM listed "flip Credit Card $1 (Campfire)" and "flip Wily Joker $4 (Campfire)" for ETERNAL jokers, which
  cannot be sold (ante 4 shop 1, ante 5 shop 2).
- shopadvise SCORE CHECK and `s` ignore the held Campfire x and Acrobat's final-hand x3 (ratio 0.17 before a 61k Tooth
  clear; after selling Greedy, `s` round est went DOWN 13608 -> 10479 although Campfire went x1 -> x1.25).
- advise rule picks repeatedly chose straight/flush draws (Hook: "drawing to a straight" over keeping 22 + faces) while
  the solver lines were pair-family; rule pick p was 0.10-0.20 below the solver in ~6 spots and the rule was kept
  because the solver was "low confidence".
- advise under The Tooth: it gives no plan for spending hands 1-2 as cycles when Acrobat is owned; the solver did.
