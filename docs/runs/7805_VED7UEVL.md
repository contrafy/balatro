# Run VED7UEVL (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (4774/4800)

Ante 1 (300 Economy / 450 Economy / The Head 600, $4): Small: solver disc (took the 0.95 line, ADVICE printed the 0.91 one) -> Straight 260 + Two Pair 124. Shop $5: Buffoon -> Crafty (over Mail-In Rebate{ETERNAL}), $1. Big: Straight 220 + Full House 296. Shop $6: Ice Cream{RENTAL} $1 (only scorer). Head: Pair A 264 + disc to spades, Flush 984.
Ante 2 (1000 Meteor / 1500 Handy / The Needle 1000, $8): shop before: nothing (Fortune Teller{ETERNAL}, Arcana). Small: Pair K 240 + Straight 636 + Pair 3 192. Shop $6: Green Joker $4. Big: Trips 8 516 + FH 666QQ 740 + Two Pair 476 = 1732. Shop $3: Jolly $3 -> $0. Needle: Two Pair JJ99 1534/1000 one hand.
Ante 3 (3200 D6 / 4800 Skip / The Psychic 6400, $2 after $3 rent): shop $2: Mr. Bones $5 / Jumbo Arcana unaffordable. Skipped Small for D6 (override of advice). Big: Two Pair KK77 1526, Two Pair AAQQ 1680, disc 5, disc 3, forced club Flush 1568 vs 1594 needed -> 4774/4800, lost by 26.

## Post-mortem

Binding constraint: MONEY -> SCALING. The run never had more than $8; Ice Cream{RENTAL} was the main chip source from ante 1
to the end and its $3 rent ate 4 of my ~$20 income over 4 rounds ($12), exactly the price of one more joker / Mr. Bones. The
shops offered no xMult in 6 visits (Certificate, Fortune Teller, Runner eternals; Green, Jolly, Devious, Mr. Bones). The
ante-2 -> ante-3 jump (1500 -> 4800) found a flat build (Jolly +8, Green +3..5, Ice Cream +45 chips, all hands L1) at ~1500
per hand vs 1600 needed.

Decisions I would change:
1. Ante 3 Small skip (my override of `b blind`). I reasoned the post-Small shop would be worth $0 after rent and the Small
   (3200) itself was a ~35% loss risk. But skipping forfeited 3 Green Joker plays (+3 mult on every later hand): the final
   Flush would have been 196 x 11 = 2156 instead of 1568, and both Two Pairs ~+300 each. With a growth +mult joker owned,
   playing a blind is also an investment. Rule below.
2. Final-hand discards in the Big Blind: the solver's p_clear did not charge Green Joker -1 mult for the discard itself
   (0.69 for the club-flush line; the made flush then came out 1568 vs 1594, it would have been 1764 with Green unchanged).
   With 1 hand left and a discard-penalised joker, compute the post-discard score by hand.
3. Ice Cream{RENTAL} at ante 1: it carried the Head and the Needle (Needle 1534 included +60 chips x13), so the buy itself was
   right, but I should have sold it at the ante-3 shop ($1 back, $3 rent saved) only if a replacement existed - it did not.
   The real miss was ante 2 shop 1 ($8): Fortune Teller/Arcana only; no fix.

Reusable if-then rules:
- IF you own a growth joker that scales per hand played (Green Joker, Ride the Bus, Supernova, Spare Trousers, Runner on its
  hand) and are considering a Small Blind skip, THEN count the lost growth (3 plays) as a cost: +3 mult on every later hand
  of the ante is ~+20% score at ante 3 and decided this run by 26 chips. Skip only for a tag that pays more than that.
- IF you own Green Joker and are on your final hand with a discard left, THEN the discard costs -1 mult on the made hand you
  are drawing to: recompute est for the target hand with Green -1 before trusting the draw (and prefer one discard, not two).
- IF the only affordable scorer at ante 1 is a rental decaying joker (Ice Cream), THEN buy it (it carried 2 boss blinds), but
  plan its exit: the first shop with $5+ spare buys a permanent scorer and sells it.

Advisor/CLI defects:
- ADVICE did not pick the best solver line: ante 1 Small opening hand listed `DISCARD 2 3 7 8 p_clear 0.95` but ADVICE printed
  `disc 4 5 6 7 8 (solver: clears 91%)` (twice, deterministic). It seems to take the first solver line, not the max.
- Solver crashed mid-run: `(solver unavailable: AttributeError: 'RoundSolver' object has no attribute 'growth_j')` on the
  ante-3 Big opener (advisor was being updated).
- Solver discard p_clear ignores Green Joker's -1 mult per discard: ante 3 Big final hand, `DISCARD 4 5 8 p_clear 0.69` with
  Green at 4; after the discard Green was 3 and the made club Flush was est 1568 vs 1594 needed (would have been 1764).
  The first discard (`DISCARD 4 5 6 7 8 p_clear 0.91`) had the same issue.
- Blind-select skip ADVICE does not value owned per-hand growth jokers (Green Joker) when weighing a Small skip.
Bridge issues: none; 45 steps, no rejects; est matched actual on every hand.
