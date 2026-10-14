# Run S5XFPLXV (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Club (10942/18000)

Ante 1 (Double/Double/The Head 600, $4): Small: Flush clubs 256 + Pair AA 64 = 320. Shop $5: Buffoon pack -> Odd Todd{PERISH,RENTAL} (Runner alt). Big: Heart Flush 420 + Trips QQQ 180. Shop $3: bought Gluttonous{PERISH,RENTAL} $1 (override advisor LEAVE; SIM +0.51). Head: Full House 888 99 952 one-shot. Money -4 after double rent.
Ante 2 (Buffoon/Negative/The Needle 1000, $3): sold both rentals ($1 each) to afford Mystic Summit{ETERNAL} $5 (+15 mult at 0 discards) - the run's engine: burn both discards, then even a lone High Card = 1000. Skipped Small for Buffoon tag: Seance{foil, +50 chips} + Clever{ETERNAL}. Big 1500: FH AAAQQ 4237. Shop $6: left (Walkie Talkie rental, Bootstraps). Needle: Two Pair JJ66 3094.
Ante 3 (Skip/Orbital/The Mouth 6400, $12): Grabber $10 (+1 hand). Small 3200: Two Pair QQ99 3196 (4 short!) + High A 1056. Shop $4: Ramen{RENTAL} $1 (x2, first xMult). Big 4800: FH AAAQQ 8135. Mouth: FH 99955 7236. Seance perished.
Ante 4 (Double/Ethereal/The Club 18000, $12): SCORE CHECK 0.33 EMERGENCY; Jumbo Celestial -> Earth (FH L2), reroll found nothing. Small 9000: Two Pair 3710 + High 422 + Two Pair 4188 + Trips 1520 = 9840. $2 shop nothing. Skipped Big 13500 for Ethereal tag (pack: Cryptid -> 2 QS). Club: dug for FH, FH QQQAA 6950, then ran out of hands: 10942/18000.

## Post-mortem

Binding constraint: scaling. Final engine was Summit (+15 mult at 0 discards) + Clever + Ramen x1.7, all Pair-family hands at L1 (FH L2). ~4000 per two pair / ~7000 per FH, with 4 hands, against 18000. No planets, no second xMult, money $2-12 all run (two early rentals ate the ante-1/2 budget: -$3 per round each).

Decisions I would change:
1. Ante 1: bought Gluttonous (club-only) on top of Odd Todd, ran money to -$4 and had to sell both rentals at ante 2 just to buy Summit with exactly $5. The two rentals cost ~$9 net and a whole shop. Better: sell Odd Todd right after the Big and keep one rental.
2. Ante 3 shop with $12: bought Grabber ($10). Grabber paid off (extra hands) but left $2 for ante 3-4 shops, so Photograph/Droll/Celestial packs were all unaffordable and I entered ante 4 at $12 with no planet history. A $4 Celestial + $8 floor might have been better.
3. Ante 4 Big skip took the Ethereal tag but yielded Cryptid (weak). The right fix was earlier: more xMult/levels in ante 3.

Reusable rules (if-then):
- IF you own Mystic Summit THEN burn BOTH discards every round on junk (keep the pair/two-pair core) before the first play: even a lone High Card scores ~1000-2000 at ante 2-3 and a Full House 7-8k; `advise` prints the 0-discard est.
- IF you own Summit + chips jokers THEN every +chips joker is worth ~17-35x its chips (Clever +80, foil +50): prefer flat +chips jokers/foil over club/diamond-only +mult jokers.
- IF you hold 2 rentals with <$6 THEN sell the weaker one before the next boss; double rent cannot be covered by ante 1 income ($0 Small).
- IF a hand lands 4 short of the blind (3196/3200) THEN a 1-card High Card at 0 discards still clears (Summit): do not panic, but fillers to cycle cards are only legal up to 5 cards.
- IF you have 0 discards and 4 hands (Grabber + Summit) THEN dig with a High Card play that keeps the pair core (solver p 0.79 vs 0.74) - it found two pair and FH twice.
- IF the boss is The Club THEN debuffed clubs still form the hand type; choose FH combos that avoid the debuffed card (QQQAA 6950 over AAAQQ 6597).

Advisor/CLI defects:
- SCORE CHECK ignores discards, so with Summit it printed 0.33-0.52 (EMERGENCY) while real hands were 4-8k; it also undervalues the Summit engine at ante 1-2 (Summit was ranked 125 NEEDED NOW but flagged ETERNAL fine).
- shopadvise ante 1: LEAVE with a hard "2nd rental" rule although SIM said P(clear 3 blinds) 0.20 -> 0.83 for a $1 rental (I overrode it).
- advise at the Club final hands: "UNWINNABLE" with 2 hands left was correct, but earlier at 0 discards it didn't flag that 4 hands x ~4k < 18000 until 2 hands remained, so the shop-phase warning (ratio 0.33) was the only signal.
- play with 7 cards rejected ("1-5 of [1..8]") - help text suggests fillers but max is 5 cards; wasted an attempt (not recorded).
