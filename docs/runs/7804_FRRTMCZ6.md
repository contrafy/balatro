# Run FRRTMCZ6 (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind Big Blind (352/450)

Ante 1 (Juggle/Uncommon/The Manacle 600, $4): Small 300: 2P KK88 112 (overrode solver redraw, margin 0.06), disc 4, disc 3 -> diamond Flush 284 = 396. Shop $5 (Uranus, Fool, Buffoon, Arcana, Planet Merchant): Buffoon -> Card Sharp{ETERNAL} (SIM 0.72 vs Wily 0.33), $1 left. Big 450: broke Pair 44 on solver (0.89 vs 0.72) -> drew AA99; 2P AA99 120 (register); disc 5 4 3 keeping QD JC TD 8H 8C (solver p 0.98) -> drew KD 5D 2C (no 9 for the straight, no pair); Pair 88 52 (solver 0.85, keep KD QD TD 5D for 2P x3 / Flush) -> drew QH JS 8S 7S; forced Pair QQ x3 180. 352/450. LOSS.

## Post-mortem

Binding constraint: no flat scorer. The only joker was Card Sharp (x3 on a repeated type) on L1 hands, which multiplies almost
nothing at ante 1: Pair x3 tops out at (10+22)x2x3 = 192 (AA), so the 450 Big needed a registered Two Pair (~120) PLUS a
second Two Pair x3 (~300-360) within 2 hands and 1 discard. Two made Two Pairs in one 3-hand round failed here. The
$4 start and $0 Small payout left exactly one buy (Buffoon pack); the pack offered only Card Sharp{E} or Wily.

Decisions I would change:
1. Big Blind hand 3 (after missing): nothing better existed; the miss was at hand 2's discard. Keeping QJT + 88 drew 3 cards
   for a pair of Q/J/T (9 outs) - solver said 98% clear, the real chance of 2P-then-2P-x3 was far lower. Breaking 88 and
   keeping QD JC TD (p 0.97) would not have been better: any Two Pair still needed both pairs.
2. Small Blind: fine (396/300). Shop: the Buffoon pack was the only scorer route; with hindsight Wily (+100 chips on Trips,
   also Full House) is not better. Nothing to change with $5.
3. The real alternative was at the Big's first decision: Card Sharp makes a FLUSH repeat too strong to ignore? No - two
   flushes in one round are rarer than two Two Pairs. The run was decided by the deal; the structural lesson is below.

Reusable rules (if-then):
- IF Card Sharp is your only joker at ante 1, THEN only Two Pair (or better) repeats can reach the 450 Big: Pair x3 caps at
  ~192. Register Two Pair with the first one you make; keep every pair in hand; never register Pair unless the blind is
  already within one Pair x3 (~150-190).
- IF the solver's p comes from a 2-step plan (make Two Pair, THEN make another Two Pair x3), THEN treat a p above ~0.85 at
  ante 1 as overconfident: the two-pair draw itself printed p=0.62 in the same line.
- IF the Big Blind shop leaves you $1 with a lone Card Sharp, THEN the ante-1 boss would also need 600 from repeated types;
  a flat +mult joker is the first buy in the next shop, before any planet or pack.

Advisor/CLI defects:
- advise SOLVER (Big 450, need 330, 2 hands, 1 discard): "DISCARD 6 7 8 p 0.98 (calibrated) ... two pair draw p=0.62" -
  overall clear probability printed far above the probability of its own first step; it lost. Next hand "rule pick p 0.85"
  also lost. Solver calibration at ante 1 with Card Sharp (needs two specific made hands) is badly overconfident.
- shopadvise pack SIM: "take Card Sharp: P(clear all next 3 blinds) 0.72" - overstated for a lone x3-on-repeat joker on L1
  hands at 450/600; it should cap Card Sharp's value by the realistic chance of two same-type made hands per round.
