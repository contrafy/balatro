# Run GEJ9QVYY (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 Big Blind (11510/13500)

Ante 1 (Polychrome/Rare/The Hook 600, $4): Small: Trips 777 153 + 2P KK99 116 + Pair TT 60 = 329. Shop $4: Buffoon pack -> The Idol (over Red Card). Big: Flush 300 + 2P TT33 92 + Trips 222 108 (kept pair 22 over a 0.97 flush break, worked). Shop: sold Idol (+$3) for Half Joker $5. Hook: Trips 555 + Half Joker 1035 one-shot.
Ante 2 (Garbage/D6/The Manacle 2000, $9): Venus $3 (Trips L2), Zany $4, Sly{RENTAL} $1 (+50 chips on any Pair/Trips). Small: Trips 444 1550. Big: Pair QQ 660 x2 + Pair 22 308. Manacle: Pair QQ 1760 + Pair 99 1716.
Ante 3 (Juggle/Standard/The Club 6400, $13): Celestial -> Mercury (Pair L2), Even Steven $4. Small: Trips 777 4477 one-shot. Big: Pair TT 2945 + Pair JJ 2185 (4800). Club: Trips TTT 5400 + Pair 33 1863. Shop money was $0-5 all ante (Sly rent -$3/round, Small pays $0).
Ante 4 (Voucher/Ethereal/The Flint 18000, $5): Small 9000: Trips TTT 6370 + Pair 88 2821 = 9191. Shop $3: sold Even Steven for Gros Michel $5 (+15 mult). Big 13500: no pair from 2 discards, Pair TT 3610 + Trips QQQ 6760 = 10370, last hand 8 fresh cards had NO pair (needed 3130, ~88% by my count): Straight 1140 -> 11510/13500. LOSS.

## Post-mortem

Binding constraint: no multiplier. 4 flat jokers (Half Joker +20, Zany +12, Sly +50 chips, Gros +15) and Pair/Trips at L2 topped at ~3.6k (pair) and ~6.7k (trips) per hand, exactly the "flat builds cap ~5-8k at ante 4" line. Half Joker at ante 1-3 was brilliant (every <=3-card hand = 1000-5000) but is flat: it does not scale into ante 4 (13500 Big = 4500/hand with 3 hands needs trips twice). Money was the second constraint: $0-5 the whole run, the Sly rental (-$3 per round, Small pays $0) ate every payout, so I never held the $6-10 for an xMult or a Buffoon pack; Photograph ($5) was the only xMult-shaped item seen in 8 shops and was passed (card phase, +10%).

Decisions I would change:
1. Ante 3 shop 1 ($13): bought Celestial pack + Even Steven ($8). A Mega/Buffoon route or holding $13 for the next shop's xMult would have been better; Even Steven (+4 per even card) added ~3 mult on average and was sold a shop later for $2.
2. Ante 3 Buffoon pack ($4, to $0) offered only Crafty{E}/Reserved Parking{R}: with rent draining $3 a round, a $4 gamble at $4 total money left no buffer. Rule: with a rental owned and < $8, do not spend the last $4 on a pack.
3. Sly rental kept for 6 rounds (-$18) as the biggest chip source (+50 chips ~ +1500 per hand); selling it earlier would not have cleared ante 3, so I think it was right, but it prevented any saving. A Small Blind skip (Juggle/Voucher tag) never paid because tags pay after a shop I could not afford.
4. Ante 4 Big: with Trips QQQ + A K 7 6 4 in hand the better last-hand set-up was unclear; I took trips first (est 6760). No alternative cleared, so the loss was the 12% draw (no pair among 3 new cards) on top of a no-xMult build.

Reusable rules (if-then):
- IF Half Joker is your first joker, THEN every Pair/Trips + <=1 filler (<=3 cards) is est 400-1000 at ante 1 and 1700-4500 by ante 3 with Sly (+50 chips) and Zany: ante 1-3 clear in 1-2 hands. But from ante 4 (9000/13500/18000) it needs an xMult: spend ante 3 money ($13) on rerolls/Buffoon packs for it, not on Even Steven/Mercury.
- IF you own a rental and money is under $8, THEN every shop is rent-limited: one rental scorer is fine, but do not also spend on packs; payouts per round are ~$5 (Big/boss) minus $3 rent.
- IF a hand is a made Trips with 2 hands left and no discards, THEN count outs for the last hand before playing: Trips (3 cards) draws 3 new cards, so the last hand's pair odds come from only 5 old ranks + 3 draws (I estimated 88%, lost the 12%).
- IF a boss like The Club debuffs 3 cards, THEN Trips with 1 debuffed card still scored 5400 (est exact): debuffed cards keep the hand type, only lose their chips.

Advisor/CLI defects:
- The solver treats future draws as visible: at the ante 4 Big it gave p 0.53 for a discard (keep AC QD TD) and p 0.50 -> real outcome was 10370/13500 after trips + pair. It also preferred breaking a made Pair 44 (p .50 vs .23) which cost nothing here but p values at need 13500 were far too optimistic with 3 flat hands.
- shopadvise ranked Photograph BUY 83 [XMULT] although it is a card-phase x2 (multiplies base mult only); SIM correctly showed 0.66 vs 0.66 baseline.
- Mercury pick note: "NOT your main hand Three of a Kind" while Pair was actually played more often (7 of the 13 plays were Pair): main hand label stayed Trips; harmless.
- `pick N` for Celestial printed that the level was wasted, but Pair was played about as often as Trips.
