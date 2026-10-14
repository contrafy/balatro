# Run AUGH7GDH (port 7818, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Flint

- Ante 1 Small (300): cleared with Three of a Kind 180, Two Pair 88, Flush 280 (3 hands, 1 discard used). Cash $4.
- Ante 1 Shop: Buffoon Pack $4 -> Popcorn (+20 mult, RENTAL). Ante 1 Big (450): Pair AA est 704 cleared it. Cash $3 after rent.
- Ante 1 Shop 2: sold Popcorn ($1), bought Joker Stencil (xMult x6 on 5 empty slots, PERISHABLE 5 rounds, RENTAL). Still one rental.
- Ante 1 Boss The Hook (600): Two Pair 408 banked, then Flush 1848 cleared it (overrode advisor Pair 384). Cash $6.
- Ante 2 Shop: Onyx Agate {ETERNAL} $7 unaffordable at $6; Bull/Blueprint/To Do List were second rentals. Left with $6.
- Ante 2 Small (1000): Pair AA 384, then Heart Flush 1632 cleared it. Cash $4.
- Ante 2 Shop: Bull (rental) and Celestial pack rejected. Left with $5.
- Ante 2 Big (1500): Two Pair 504, then Two Pair 648, then Two Pair 480 cleared it (1152 + 480). Cash $5.
- Ante 2 Boss The Flint (2000; base chips and mult halved): Two Pair 228 -> discards -> Full House 624 -> Straight 708 -> High Card 72. Scored 1410, 0 hands left. GAME OVER.

## Post-mortem

**Binding constraint:** Zero permanent scorers. The run had one rental (Popcorn then Stencil) from ante 1 through ante 2. The Flint at ante 2 halves base chips and mult, so a hand-only build (Pair/Two Pair/Flush at roughly 200-700) could not reach 2000 with 3 hands. Stencil was perishable (5 rounds), so by the ante-2 boss it had only 1-2 rounds left and its x6 was about to vanish.

**Decisions I would change:**
1. Ante 1 Buffoon pack: I took Popcorn (rental, decaying +20 mult). The Raised Fist (perishable, no rent) was a safer bridge. With rent and decay, Popcorn was worth roughly $3/round for 4 rounds of +16 mult. Paying rent from $0 left me at $-3 at the first round end.
2. Ante 1 Shop 2: I swapped Popcorn for Stencil, which was allowed (one rental kept). But Stencil was perishable, so the swap bought only about 5 rounds of xMult. I should have weighed a permanent scorer over a perishable xMult before ante 2.
3. Ante 2 Shop: Onyx Agate ETERNAL +7 mult per Club cost $7; I had $6. Keeping $7 at the ante-1 Big shop (skipping the Stencil buy, which cost $1) would have bought it. Rule: at ante 1-2, keep $7 for a known permanent scorer when one is visible.
4. Boss The Flint at ante 2 was reachable only by a flush or straight built around a scorer. I did not plan a flush deck in ante 1. Rule: if a boss halves chips/mult (Flint), plan for 2 xMult sources or skip nothing; do not expect hand-only builds.

**If-then rules (for weaker models):**
- If the shop shows a permanent +mult joker at $7 and you have $6, do not spend on rentals or packs; keep the $7 floor for it.
- If a rental xMult is perishable (<=5 rounds), treat it as a bridge only and buy a permanent scorer before the next boss.
- If the boss is The Flint (base chips and mult halved), expect hand scores around half normal; need 2 scorers or a flush/straight with a permanent xMult before ante 2's boss.
- If a rental's rent is due at ROUND_EVAL and money is $0, expect $-3 immediately; keep at least $3 in hand before choosing a rental.
- If the solver shows UNWINNABLE with no discards left, play the best made hand and end the blind; do not waste calls.

**Advisor/CLI defects:**
- Shop advisor recommended "SELL then BUY" for Joker Stencil (x5 xMult) at $3 cash without warning the stencil perishes in 5 rounds. Its SIM showed value 0.70, but perishing was only flagged later as WARNING.
- Hand advisor for The Hook recommended Pair 384 (ADVICE: PLAY PAIR) over Flush 1848 with "the hand you are leveling" reasoning; the flush was a certain clear. I overrode it.
- At ROUND_EVAL the status line shows money after rent ($-3) before cash-out; this is confusing when reading "$".
