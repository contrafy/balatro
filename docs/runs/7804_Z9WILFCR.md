# Run Z9WILFCR (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Water (10171/18000)

Ante 1 (Polychrome/Holo/The Window 600, $4): Small: disc to diamonds, Pair TT 60 + Flush 288. Shop $5: Buffoon -> Mad{ETERNAL} (overrode SIM Smiley{PERISH} 0.86 vs 0.78). Big: disc, 2P QQJJ 720. Shop $7: Green Joker{ETERNAL} $4. Window: 2P TT33 429 + Straight Q-8 462.
Ante 2 (Juggle/Handy/The Flint 2000, $9): Buffoon -> Bloodstone{ETERNAL}. Small: disc, Pair AA 128, 2P JJ66 780, FH QQQ99. Shop $6: Buffoon -> foil Ride the Bus{RENTAL} (SIM 0.98 vs 0.43). Skipped Big (override: Handy tag +$8, no rent tick). Flint: disc, High AC 384, 2P 7722 1404, FH 44466 -> cleared. $13.
Ante 3 (Voucher/Skip/The Hook 6400, $13): EMERGENCY 0.33 -> Popcorn $5. Small 3200: Pair 44 2244 + Pair AA. Shop $7: left. Skipped Big (Skip tag +$10, no rent/Popcorn tick). Hook: Pair 33 2112, Pair 99 2574, FH TTT55 -> cleared. $21.
Ante 4 (Top-up/Handy/The Water 18000, $21): EMERGENCY 0.22 -> The Order{PERISH} $8 (only xMult), Celestial -> Uranus. Small 9000: disc, FH JJJ22 4216 (reset Ride the Bus 8 -> 0), disc 2, wheel Straight A-5 x3 ~7900. Shop $8: sold Popcorn -> Sly{RENTAL} $1, Arcana -> High Priestess (Mercury + Earth used). Skipped Big (Handy +$18, Big projected 0.89x with a $5 shop after it). Water (0 discards): 2P TT22 3936, dig High KC 715 (solver line, kept 9-8-7-6), Straight 9-5 5520 (no Bloodstone hit) -> 10171/18000. GAME OVER.

## Post-mortem

Binding constraint: SCALING, caused by the ante 1-2 joker picks. Three of my six slots went to Eternal jokers that do not
scale: Mad (+10 on Two Pair), Green Joker (+1/hand, -1/discard; reached only +11 by ante 4) and Bloodstone (card-phase
x1.5 per Heart: multiplies only the hand's base mult, so ~+5% on a flat build, and it never fired when it mattered). The
two flexible slots held rentals (Ride the Bus, Sly), -$6/round, and the only multiplier was a perishable Straight-gated
Order. Best hand at ante 4 was ~4-5.5k per hand against the Water's 6k-per-hand requirement with no discards. Score check
ratio was 0.22-0.33 from ante 3 on; no reliable/growth xMult was ever offered in 5 shops (none rerolled: money never
reached $20 after a reroll).

Decisions I would change:
1. Ante 2 Buffoon: took Bloodstone{ETERNAL} (SIM 0.55) over Red Card / skipping. An eternal card-phase suit xMult on a
   pair build is a permanently dead slot; skipping the pack would have kept the slot for Popcorn/Sly without a sale.
2. Ante 1 Green Joker{ETERNAL} $4: it grows slower than the blinds (+1 per hand, -1 per discard and The Hook's forced
   discards also subtract). A $4 hold would have bought a better scorer or a Buffoon pack one shop later.
3. Ante 4 Small: Full House JJJ22 reset Ride the Bus from +8 to 0 (faces). A faceless Two Pair/Pair lines would have kept
   +8 to +10 mult for the Water; with Ride the Bus owned, avoid scoring faces unless the face hand is needed to clear.
4. Skips (Big at ante 2, 3, 4) were right on money (+$37 tags, $15 rent saved) but the money never turned into an xMult
   because none was offered; that was supply luck, not the skip.

Reusable rules (if-then):
- IF a Buffoon/shop joker is Eternal AND it is a card-phase xMult (Bloodstone, Photograph-type) or a slow +1 growth joker
  (Green Joker) AND you own no xMult, THEN skip it: it multiplies only the base mult / grows slower than the ante curve,
  and it can never be sold to make room for the xMult you need at ante 3-4.
- IF you own Ride the Bus at +6 or more, THEN play faceless hands (number pairs, wheel straights) whenever they clear
  pace; a face-card Full House cost 8 mult for the rest of the ante.
- IF the Big Blind's tag pays now (Handy, Skip) AND the Big's shop would have <$8 after rent, THEN skipping it is free
  value: +$8-19 now, no rent/perish/Popcorn tick, one fewer blind to lose.
- IF The Water is the ante-4 boss AND your best hand is under boss/3 (6000), THEN the Small/Big shops must buy a flat
  +mult/+chips scorer that fires on every pair (Sly/Jolly/Popcorn) rather than a Straight-gated xMult: 0 discards make
  gated hands unreliable.

Advisor/CLI defects:
- SOLVER at The Water (hand 2): "dig KC QS JH 7C ... p 0.29" vs real chance ~2%: the dig's straight scored 5520 (est
  matched exactly) against 13349 needed. The solver appears to apply Bloodstone's 1/2 x1.5 per Heart to the whole mult
  (joker phase), while `est` (and the game) apply it at card scoring before the +mult jokers. Its Pair 99 est at The
  Hook (3315 = 2652 x1.25) shows the same full-score scaling.
- SOLVER p is ">=0.99 (calibrated)" for almost every line at ante 1-4 Small/Big (e.g. ante 1 Big with zero pairs: 0.99),
  so it does not discriminate between lines; "calibrated" looks overconfident at low ante.
- Pack advise ranked Bloodstone{ETERNAL} (SIM +0.32) as the pick on a Two Pair build; its own shop rule text says
  "rarely fires outside a Flush build". Eternal card-phase suit xMults should be AVOID on pair builds.
- `s` at blind select said "never skip the Big" while the Big tag (Handy +$18, Skip +$10) paid more than the Big's shop
  could use; it should compare the tag's money + rent saved to the shop's buying power.
Bridge issues: none (71 steps, no rejects).
