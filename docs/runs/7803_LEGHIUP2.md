# Run LEGHIUP2 (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Window (4347/6400)

Ante 1 (Boss/Holo/The Goad 600, $4): Small: 2P KKTT 120 + heart Flush 276. Shop $5: passed Scholar{ETERNAL,RENTAL} (advisor BUY), Buffoon -> Mime (over Hack{RENTAL}). Big 450: 2P 7766 92, Trips 222 108, FH QQQJJ 360. Shop $5: Abstract{PERISH,RENTAL} $1. Goad: disc 4, heart Flush 810 one-shot.
Ante 2 (Voucher/Coupon/The Pillar 2000, $8): EMERGENCY 0.23: Supernova{PERISH,RENTAL} $1 (2nd rental), Celestial -> Venus (Trips L2). Skipped Small (Voucher; shop would be broke). Big 1500: 2P 6622 504 + Straight Q-8 1078. Shop $2 (rent -$6/round): nothing. Pillar: disc 2 for straight/flush, heart Flush 1120 + Trips KKK 1280.
Ante 3 (Orbital(2P)/Buffoon/The Window 6400, $2): Skipped Small for Orbital (Two Pair L1->L4) and Big for Buffoon tag -> Mega Buffoon: Even Steven{ETERNAL} + Swashbuckler (passed Mystic Summit{PERISH,RENTAL}, To Do List{E}). Window: disc 5 (kept KC JC 9C), disc 3 (broke debuffed-T Straight 1984 per solver p 0.82), dig High 115, 2P KKTT 3400, forced Pair 88 832 = 4347/6400. LOSS.

## Post-mortem

Binding constraint: money. Start $4, Small Blinds pay $0, the ante-1 Buffoon pack offered only Mime/Hack{RENTAL}, and
from ante 2 I carried two rentals (-$6/round) that ate my whole income: every shop from ante 2 Big on was entered with
$2-3, so no joker, planet or pack could be bought for three shops. The run reached the ante-3 boss with 5 flat jokers
(two of them perishing) and zero xMult; best hand ~3400 vs 6400 boss (ratio 0.53).

Decisions I would change:
1. Ante 2 shop 1: buying Supernova{PERISH,RENTAL} as the SECOND rental. It added ~+4 mult but turned income negative;
   the ante-2 and ante-3 shops were then unusable. With one rental I would have had ~$8-10 in the Big-Blind shop.
2. Ante 3: skipping BOTH Small and Big. The Orbital skip (+3 Two Pair levels now) was right; the Buffoon skip gave two
   jokers but sent me into a 6400 boss with no shop and no discard-proof plan. Playing Big 4800 with 2P L4 (~3.4k) and
   the $5 + shop would at least have tested the build before the boss. Close call; I would still skip Small.
3. Window: the 2nd discard broke a made Straight (1984, debuffed T) for a two-pair draw on the solver's p 0.82; the
   draw half-missed. Playing the Straight first and keeping the last discard was the safer line for a 3-hand need.

Reusable rules (if-then):
- IF you already own one rental and income per round (blind $ + interest + hands) is under $8, THEN do not buy a second
  rental even in EMERGENCY: -$6/round makes every following shop unaffordable, which is worse than the +mult it adds.
- IF the ante-3 Small Blind tag is Orbital for your main pair-family hand (Two Pair/Pair/Trips), THEN skip it: +3 levels
  now beats a $0 Small Blind shop when you hold under $5.
- IF a Mega Buffoon (Buffoon tag) would be your only shop-like access before a boss, THEN pick no-rent scorers
  (Even Steven, Swashbuckler) over a third rental, even when the rental shows the bigger round est.
- IF a pair-family build owns Even Steven, THEN on a no-made-hand discard keep the even cards (T/8/6/4/2), not K/J/9.

Advisor/CLI defects:
- shopadvise ante 1 ranked Scholar{ETERNAL,RENTAL} BUY 128 ("NEEDED NOW") again: an eternal rental (-$69 unsellable)
  should never be a buy (same defect as 7807_9IIGB2FF).
- Blind select at ante 3 said "do not skip ... take the shop" for an Orbital tag (3 levels NOW) while I held $2 and the
  shop would have been broke after -$6 rent; it should value immediate tags (Orbital/Buffoon) and the rent saved.
- SOLVER at The Window: discard advice p 0.81/0.82 (n=100) twice, then 0.57 dig, outcome 4347/6400; the "calibrated"
  p at n=100 under a suit-debuff boss looks optimistic. The first discard kept KC JC 9C (odd cards) with Even Steven owned.
- shopadvise SIM printed baseline p_next 0.00 at ante 1 (known defect, no ranking signal).
Bridge issues: none; 45 steps, no rejects.
