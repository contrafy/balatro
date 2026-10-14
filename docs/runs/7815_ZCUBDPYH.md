# Run ZCUBDPYH (port 7815, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Mouth (212/2000)

Ante 1 (Economy/Coupon/The Window 600, $4): Small Trips 888 162 + flush draw hit (KH QH TH 7H 3H) 300 = 462/300. Shop $5: Buffoon pack -> only Madness{RENTAL} / Showman{PERISH}; took Showman (kept as $2 of sell value). Big 450: Two Pair AA55 104, Trips draw -> FH 888 66 304, Two Pair KK33 92 = 500. Shop $5: Wily{ETERNAL} $4 + Blueprint{RENTAL} $1 (Blueprint left of Wily = +200 chips on Trips/FH). Window: kept 7C 7D 6S 6D, three pairs, played 2-card junk twice digging for trips, then FH 555 66 1024 (est exact) = cleared.
Ante 2 (Standard/Ethereal/The Mouth 2000, $2 after rent): shop had only Satellite{E}, Runner{E}: sold Showman -> Celestial pack -> Earth (FH L2 65x6). Skipped Small (Standard tag: lucky foil KC + stone 9D) and Big (Ethereal tag: Talisman gold seal on AS) to dodge $3 rent ticks with $0. The Mouth: 2 discards keeping AA QQ for A/Q missed twice (31% each); 0 discards left, forced to lock Two Pair: 124 + 0 + 88 = 212/2000. LOSS.

## Post-mortem

Binding constraint: no real scorer; the whole build was Wily{ETERNAL} + Blueprint copy = a Trips/Full House-only engine (+200 chips) with no unconditional scorer. It was fine at ante 1 (FH 1024 vs Window 600) but ante 2's Mouth (2000, one locked hand type) needed a Full House that I had ~45% to make once and then repeat. Also money: Small pays $0 and Blueprint rent was $3/round, so I was at $0-2 for the whole run and saw 3 shops with nothing affordable (Satellite{E}, Runner{E}, Astronomer).

Decisions I would change:
1. Ante 1 shop 2 (the $5 purchase): Wily{ETERNAL} + Blueprint left $0 and a rent bill, for a hand-type-gated engine. A conditional engine under a one-type boss (The Mouth/Eye/Needle) is a coin flip. Alternative would have been keeping $5 and rerolling/buying the pair-triggered joker next shop; I judged the 3 FH/Trips plays of ante 1 as proof the engine would repeat, but a 2000 lock needs a FH on the first hand every time.
2. The Mouth lock: with 2 discards I kept AA QQ (draw 4 for A/Q, 31%) twice; a Two Pair-locked fallback cannot clear 2000 at all. In hindsight I should not have skipped Big/Small blindly: the Standard/Ethereal tag picks (stone, foil lucky K, gold seal) added nothing that helped before the boss. Playing the Big (1500 with FH L2) might have found gold-seal/lucky money, but it was not the cause of the loss.
3. Showman pick at the ante-1 Buffoon pack was nothing; the pack was a $4 gamble at $5 that yielded no scorer (Madness{RENTAL}/Showman{PERISH}). With 0 scorers and $5 the right call was probably to keep $5 and see the next shop (Wily/Blueprint appeared anyway after Big).

Reusable rules (if-then):
- IF the ante boss is The Mouth/The Eye/The Needle and your only engine is a hand-type-gated joker (Wily on Trips, Clever on Two Pair), THEN the round is one coin flip per locked type; do not enter it at ante 2 with <1 unconditional +mult joker: spend the earlier shops on a scorer that fires on Pair/High Card.
- IF the first hand under The Mouth cannot be your gated hand and discards are gone, THEN you are dead (any play locks the type): spend BOTH discards digging for the strongest type BEFORE the first play, and keep at least a made 2-pair floor... a 2-pair floor cannot beat 2000 without xMult.
- IF a rental (Blueprint) copies a gated joker, THEN its $3 rent is paid every round whether or not the gate fires; with $0 income (Small $0) it consumes the whole ante's money.
- IF you hold $0-2 and the shop has only Eternal junk (Satellite, Runner), THEN skipping Small and Big for tags is correct only if a tag gives a scorer; Standard/Ethereal tags gave nothing usable.

Advisor/CLI defects:
- shopadvise "buy nothing" at the ante-1 $5 shop was right per SIM noise rules but it never evaluated Blueprint copying Wily (+0.00); my Blueprint+Wily play was hand-modelled correctly in `hands` (est 1024 vs actual FH 1024).
- advise at The Mouth with 3 pairs (AA 88 / 66 55 33) correctly listed the solver as low-n noisy; the p=0.89 line on The Window (keep 7C 7D 6S 6D) did not materialize a FH in 2 discards (35% quoted), outcome luck.
- Showman pick: pack advise ranked Madness{RENTAL} +0.36 (SIM) over Showman although Madness destroys a joker every blind (known SIM blind spot).
