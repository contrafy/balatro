# Run N5BDCVFH (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The House (3535/6400)

Ante 1 (Uncommon/Foil/The Goad 600, $4): Small: Straight 2-6 200 + 2P KK88 112. Shop $5: Buffoon -> Scary Face{PERISH} (Blue Joker eternal rental passed). Big: FH AAA77 348 + 2P QQ55 220. Shop $6: Celestial -> Jupiter (SIM 0.29 vs Mercury 0.15; Baron $8 unaffordable). Goad: solver discards, Pair KK 180, dig 4 non-hearts, Flush H 690 -> 875.
Ante 2 (Buffoon/Coupon/The Fish 2000, $7): shop nothing (EMERGENCY, $7 kept). Skipped Small for Buffoon tag -> Mega Buffoon: Even Steven + Scholar{ETERNAL} (Walkie rental passed). Big 1500: 2P JJ44 1080 + FH QQQAA 2664. Shop $13: Throwback{RENTAL} $1 (x1.25). Fish: disc 3, FH KKKJJ 1200, disc 5 face-down, FH 99988 1245 -> 2445.
Ante 3 (Rare/Coupon/The House 6400, $16): EMERGENCY 0.23 (75th pct ~1400 vs boss/2 3200). Reroll $5 (nothing), Jupiter $3 (Flush L3, SIM +0.04), kept Throwback against SELL FIRST. Skipped Small (Rare) and Big (Coupon): Throwback x1.75, Scary (1 round left) kept alive. House: all 8 face-down -> disc 5, disc 3 face-down + 9D 6H, 2P AAQQ 2835, Pair 66 385 (solver p 0.20, kept TC 9C 5C), drew 4D/4C no flush, High AD 315 -> 3535/6400. GAME OVER.

## Post-mortem

Binding constraint: SCALING at the ante 2 -> 3 step. Entering ante 3 the build was Scary Face{PERISH, 1 round left} + Even
Steven + Scholar{ETERNAL} + Throwback{RENTAL} x1.25 with 2 empty slots, no levels on a pair-family hand (only Flush L3) and
$16. Eight shop views (ante 1-3) offered exactly one real xMult (Baron $8 at ante 1 with $6) and zero +mult jokers; the
Buffoon/Mega Buffoon picks gave Scary, Even Steven and Scholar. 75th-pct hand ~1400 vs 3200 = boss/2: the run was already
in the "84% die by next ante" band, and the ante-3 SIM gave 0.06-0.10 for clearing Small+Big+Boss.

Decisions I would change:
1. Ante 3: the skip-skip into The House was a gamble below the playbook threshold (Throwback line wants rounds that beat the
   boss by 1.3x; I was at ~0.9x: 1960/hand at x1.75 vs 2133 needed). It was still probably the best of bad options (three
   rounds at x1.25 with Scary dying after the first), but The House made it worse: its face-down first deal cost a discard,
   leaving 1 discard for 6400. A boss that eats the first deal (House, Fish) is the wrong boss to one-shot at 0.9x.
2. Ante 3 shop: the $5 reroll + $3 Jupiter. Flush L3 never got played at the boss; $8 more would not have bought anything
   either, but a Celestial pack for a pair-family level would at least have helped the 2P AAQQ / Pair hands I actually played.
3. Ante 1 Celestial pack ($4) -> Jupiter: it won The Goad (Flush 690), so fine, but it started a Flush-level habit that made
   Jupiter look like "my best level" again at ante 3. Levels should go to the pair family once 2 scorers exist.

Reusable rules (if-then):
- IF you hold Throwback below 1.3x of the boss AND the boss is The House or The Fish, THEN do not skip both blinds to one-shot
  it: The House's face-down first deal costs a discard (or a blind hand), so you fight 6400 with ~2 real hands + 1 discard.
- IF The House deals 8 face-down cards, THEN the discard-5 opener leaves 3 face-down cards that cost the second discard too;
  budget both discards for unmasking and plan to win with 3 visible hands (need 1.0x per hand, no slack).
- IF a perishable scorer has 1 round left at blind select, THEN skipping Small and Big keeps it alive for the boss (skips do
  not tick perish or rent) - a real reason to skip when the boss is the only reachable blind.
- IF you enter ante 3 with 2+ empty joker slots and no +mult joker offered in 3 shops, THEN the run is below the curve: spend
  ante-2 money on Buffoon packs over Celestial/planets for non-core hands (Scary/Steven/Scholar all came from packs here).

Advisor/CLI defects:
- shopadvise at ante 3 (twice) printed `SELL FIRST: b sell 4 (Throwback{RENTAL} is a flat RENTAL ...)` while the same output
  classed it `XMULT(growth: Throwback x1.25 now)`; rental-selling logic treats a growth xMult as flat.
- `advise` face-down handling: at The Fish it advised `disc 1 4 5 6 7` (throws visible even 8D, keeps face-down idx 8); at
  The House `disc 3 4 5 6 7` (throws visible TC 9D 6H, keeps face-down idx 8). It should discard every face-down card first.
- SOLVER p overconfident early: Goad 0.97 -> 0.76 one draw later; ante 2 Big 0.98 with Pair 180 vs 1500; useful only as a
  ranking, not as an absolute probability.
- `s` at ante 3 blind select said "do not skip" with Throwback owned and no consideration of the perishable tick saved.
Bridge issues: none (48 steps, no rejects).
