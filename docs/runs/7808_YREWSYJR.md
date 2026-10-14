# Run YREWSYJR (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind Big Blind (432/450)

Ante 1 (Investment/Foil/The Pillar 600, $4): Small 300: Pair 66 (44), disc 4 keeping pair 88, drew a 5-spade Flush 300 -> cleared with 1 hand left. Shop $5: no joker in the shop (Uranus, The Fool, Reroll Surplus); Buffoon pack $4 -> Juggler (+1 hand size) over Cloud 9{ETERNAL}; $1 left, no scorer. Big 450: Two Pair KK55 100, discarded twice keeping KK55 + AH KH QH 5H for a flush (blanked), Two Pair TT88 112, then wheel Straight 432. Lost by 18.

## Post-mortem

Binding constraint: zero scoring jokers at ante 1 Big (450 needed, base hands are ~100 each). The only joker taken was Juggler (+1 hand size), which scores nothing; total 432 = Two Pair 100 + 112 + Straight 220.

Decisions I would change:
1. Pack pick: Juggler (SIM +0.07) vs Cloud 9{ETERNAL} (+$4/round with 4 nines). Neither scores; the run needed a scorer, and the shop had none. Cloud 9 would at least have funded a $9-10 shop after the Big. Possibly I should have skipped the Small Blind... no: the Investment tag pays after a boss only.
2. Big Blind hand 1: with KK55 + 4 hearts I discarded twice (6 cards drawn, nothing) instead of playing the Two Pair 100 first. With no jokers the three-hand budget is ~100+112+220; the second discard (draw 3 for a heart) cost a 3rd 100-ish hand. Banking Two Pair on hand 1 and keeping both discards for hands 2-3 would give a similar total; the real loss was starting the Big with no scorer.
3. Small Blind: Flush 300 made it with a 5-spade lucky draw, the Small should not be a "free" blind when jokerless; the extra 'flush' outs were rare.

Reusable rules (if-then):
- IF ante 1 and you own 0 scoring jokers when the Big (450) starts, THEN expect ~300-430 from 3 hands: take any +chips/+mult joker over utility (Juggler) even at Cloud 9-style economy cost; a pack with only utility/economy jokers should still take the one that gives money (Cloud 9 +$4/round) since $1 buys nothing next shop.
- IF the wheel (A-2-3-4-5) is in hand at the last hand, check chips: it scored 220 (30x4 + 25 chips ... est exact), so a 238 gap is unreachable; plan 2 hands earlier so a Straight/Flush lands as hand 2, not hand 3.
- IF holding Two Pair at Big with 2 discards, a flush draw 4/5 (p~0.5-0.66 each) failed twice; at 0.88-0.90 solver it still lost: jokerless ante 1 solver p of 0.9 is a ~1-in-4 tail here (this run).

Advisor/CLI defects:
- Shop at ante 1 round 1 offered no joker; shopadvise (BUY Buffoon pack, SIM 0.34) was right to push the pack, but pack advise preferred Cloud 9 (rule 60) while the SIM preferred Juggler (0.07 vs 0.03), both tiny: when every option is under 0.15 the pick is noise.
- Solver on the Big: first discard 'rule pick' p 0.90 but actual outcome after two discards left 3 hands with 0 flush; solver p for the first decision was not materially calibrated on jokerless runs.
