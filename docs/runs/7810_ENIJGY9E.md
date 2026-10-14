# Run ENIJGY9E (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Wheel (3392/6400)
Ante 1 (300/450/Window 600): Small jokerless: AA pair 64 + spade flush 244 = 308 (drew into it with 2 discards). Bought perishable Gros Michel $5 (override of AVOID; +15 mult): Big pair 340+510, Window flush 1444 one-shot. Skipped Investment/Coupon tags (never skip rules).
Ante 2 (1000/1500/Hook 2000): Gros Michel destroyed (1/6) at the first round-end of ante 2. Shop $13: holo Scholar $7 + holo rental Sly $1 (each +10 mult holo; pair est ~1760-2600). Small FH 2592, Big two pair 2156 (Buffoon pack -> Fibonacci), Hook pair 5s 2660. Money $0 or negative all ante.
Ante 3 (3200/4800/Wheel 6400): bought perishable Smiley Face $4. Small trips K 4180, Big trips J 4180 + pair K 2560. Scholar/Sly perished after Big (sold). $8 shop: Half Joker $5. Wheel 6400: best hands trips 2s 1692 + pair 6 484 + pair A 1216 = 3392. Lost.

## Post-mortem
Binding constraint: SCALING (zero xMult, Pair L1, money $0-8 all run). Every scorer was a perishable/rental/flat +mult joker; the ante-3 boss (6400) needs ~2100/hand and my best hand was ~1700-2500 only with trips, pairs were ~500-1200.
Decisions I would change:
1. Ante 2 shop at $13 (after boss 1): holo Scholar+Sly were right to buy, but money was then $0 for the whole of ante 2-3 so no Buffoon/xMult could ever be bought at the ante-3 shops (shops showed Half Joker/Smiley/Earth/Celestial only). Hard to avoid: rent -$3/round + $0 Small Blind.
2. Wheel boss: I discarded A (a Fibonacci/Scholar card) twice for trips fishing and drew 2-pair. EV-wise nothing could reach 6400 with flat jokers; the loss was decided in ante 2-3 shops, not in the hand.
3. Should have kept the Small-blind perish clock in mind: skipping Small at ante 3 would have saved a Scholar/Sly round for the Big+boss. Not obviously better.
Reusable rules:
- IF a flat build (no xMult, Pair L1) reaches the ante-3 Small with <$10, THEN expect to lose to the ante-3 boss (6400): needs 2100/hand with 3 hands. Buy an xMult/Buffoon pack at the ante-2 shops even at the cost of rentals.
- IF a holo/polychrome edition is on a cheap joker at ante 2, THEN buy it: holo adds +10 mult, which at Pair L1 (x2 base mult) is 6x the base mult. Two holo jokers turned Pair 60 into ~2000.
- IF Half Joker is owned, THEN only 3-card hands count: Trips (3 cards) is the best play (est 1692 on 2s vs Pair 500).
- IF Gros Michel (rental or perishable) is the only mult source at ante 1, THEN buy it anyway (it carried Big + boss 1) but expect the 1/6 destroy at round ends; buy the next scorer in the following shop.
Advisor/CLI defects:
- shopadvise at ante 1 rated perishable Gros Michel -5 (AVOID) with 0 jokers and the Buffoon pack at 78; GM at $5 was clearly better (flush est 1444 on the boss). Same defect as the previous run's note: AVOID for a +15 mult joker when it is the only scorer.
- shopadvise at ante 3 after the Big (2 scorers alive, $8) ranked Half Joker only 28 and said LEAVE despite 'EMERGENCY'; Half Joker was the only mult available and I bought it anyway.
- The Wheel advise: kept Pair 6 est 484 and discarded the Ace; no concept that nothing in the hand could reach 6400 (a chase for trips would have been better flagged).
Bridge issues: none.
