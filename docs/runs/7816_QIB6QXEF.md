# Run QIB6QXEF (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 boss The Flint (1995/2000)

Ante 1 (Foil/Rare/The Pillar 600, $4): Small: Full House 888 77 est 312 one-shot (300). Shop $6: Buffoon pack -> Blue Joker (+2 chips per deck card) over Fortune Teller (Green Joker $4 was the alternative; $2 left). Big: Flush 648 one-shot. Shop $8: Supernova $5 (+mult = times hand played). Pillar 600: disc 4 for spade draw (missed), Pair TT 330 + fillers, then Full House 222 99 804.
Ante 2 (Investment/Investment/The Flint 2000, $9): shop: Hanging Chad{E}, Wrathful{PERISH}: rerolled once ($4 left): Drunkard{PERISH}, Uranus: left with $4. Small 1000: Pair 99 464 + Flush 900. Shop $5: Jupiter (Flush L2, $2 left). Big 1500: Straight 690 + Flush 1377. Shop $7: Crafty Joker{PERISH} $4 (+80 chips Flush; Throwback{PERISH} $6 passed). Flint 2000 (base chips/mult halved): hand AA KQJT-ish; disc 3 (kept AA + JC TC), disc 3 (kept AA KD JC TC, drew QC TS = Broadway straight 560 only), played High Card AH KD TS 5D = 176 as a "dig" (solver p 0.60, same as Pair AA 404 + fillers), drew a 5-club Flush 1519, last hand best was Pair 77 = 300 vs 305 needed. Final 1995/2000. GAME OVER.

## Post-mortem

Binding constraint: scale, and a 5-point miss at the end. Three scorers all at ante 2 (Blue Joker chips, Supernova mult growth, perishable Crafty) and no xMult; Flint halves base chips/mult so my per-hand value dropped to ~300-560 for non-flush hands.

Decisions I would change:
1. THE decisive mistake: Flint hand 1 (0 discards left, 3 hands, need 2000). The solver gave "PLAY 1 3 6 8 (High Card AH KD TS 5D, 176) dig, p 0.60" and "PLAY 1 2 6 8 (Pair AA 404 + fillers 5D TS, draws 4) p 0.60" as an exact tie. I took the High Card dig for its higher exp (1999 vs 1817). The Pair play banks +228 more score at the same p and I lost by 5. IF two plays tie on p, THEN play the one that banks more score now (the dig hand scoring ~170 is never a tie).
2. Flint hand 1 alt: Straight A-K-Q-J-T was ready (560) and scored more than the High Card dig; the dig only keeps a 4-club draw (0.69). Could have played the Pair AA with fillers AND kept QC JC TC.
3. Ante 2 first shop ($9): I rerolled for $5 and bought nothing; $4 left unspent at endshop. A Celestial pack / Uranus ($3) / Wrathful ($5 perishable) would have added a few % to hands. In hindsight 5 chips would have been bought by almost anything (Jupiter at $3 would not have helped, but Mercury/Uranus or Wrathful +3 mult on a spade scored pair, or holding Hanging Chad (retrigger first card) all add >5). IF a boss is a ~1.0x-ratio check (score check ratio 1.08, TIGHT), THEN spend all money on any scoring add, including a $4 pack, before the boss shop.
4. Discard 2 (disc 6 7 8, keeping AA): fine in hindsight; I drew the Broadway straight.

Reusable rules (if-then):
- IF The Flint is the boss, THEN `est` is exact for Pair/Flush (halving is exact) but floors odd base chips (High Card est 174 actual 176): never plan on a pair that is within ~10 of the need; every kicker-less pair is ~300-460 at ante 2 with Blue Joker + Supernova, so bank 2 pairs plus a flush, not a high-card dig.
- IF a solver dig and a banking play tie on p (within 0.02), THEN pick the banking play (higher score now), not the one with higher `exp`.
- IF last hand needs X and the best est is within 2% below X, THEN there is nothing to do; the mistake was earlier (rows above): always keep >= 5% score margin in the plan from hand 1.
- Blue Joker: +2 chips per card REMAINING in deck (88 at start, 56 late in the round); its value falls through the round, so early hands score more: play the strongest hand FIRST on boss rounds when the deck is full.

Advisor/CLI defects:
- advise on Flint hand 1 ranked the 176-point High Card dig above the 404-point Pair play at equal p (0.60 vs 0.60) by `exp`; should break ties by banked score.
- `hands` est floors Flint-halved odd chips (High Card est 174, actual 176): minor.
- shopadvise at ante 2 Small shop: SIM said buy nothing >= buy anything (noise) and rule said LEAVE; with TIGHT 1.08x it should have said spend the $4 on a pack/planet (floor OFF).
