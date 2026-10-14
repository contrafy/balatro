# Run KLHEEA8D (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (12158/13500)

Ante 1 (D6/Polychrome/The Pillar 600, $4): Small 2P 8866 + Straight K-9. Shop $5: Buffoon -> Popcorn (over Clever; SIM 1.00 vs 0.34). Big: Pair AA 2 cards (Pillar). Shop $7: Gros Michel $5. Pillar: Pair TT one-shot; Gros Michel destroyed the same round.
Ante 2 (Handy/Top-up/The Flint 2000, $9): foil Misprint{E} $6. Skipped Small (Handy +$4, broke $3, Popcorn does not decay on a skip). Big: Pair 77 + 2P KKJJ. Shop $13: reroll -> Even Steven{PERISH,RENTAL} $1. Flint: 2P AA22 3440 one-shot.
Ante 3 (Handy/Double/The Goad 6400, $11): Mercury, sold Popcorn(4). Small: disc 4, Pair 88 + 2P TT77. Shop $9 EMERGENCY 0.34: holo Trading Card{RENTAL} $1 (+10 mult; 1-card first discard pays $3 = rent), Celestial -> Mercury (Pair L3). Big: TC disc, Straight 6-high 2900 + Pair 99. Shop: sold Even Steven, Popcorn #2 $5. Goad: TC disc 2D, Pair 66 4794 + Pair KK.
Ante 4 (Foil/Rare/The Club 18000, $8): EMERGENCY 0.27: Loyalty Card{E} $5 (only multiplier offered). Small 9000: TC disc, Pair KK 5060 + Pair JJ. Shop $4: nothing (Even Steven{E,RENTAL}, Hallucination{E}). Big 13500 (projected 10560): disc 5 + disc 4 keeping 666 (Trips L1 < Pair L3), Pair 66 3468 + Pair QQ 4620 + Pair TT 4070 = 12158/13500. Final hand was unwinnable even at a Misprint 23 roll (110 x 49 = 5390 vs 5412). Loyalty Card never fired (6th hand after purchase = the boss).

## Post-mortem

Binding constraint: no permanent scaling. Entering ante 4 I owned one permanent scorer (foil Misprint) plus a holo
rental (Trading Card), Pair L3 and no xMult; every hand capped at ~4-5k against a 4.5k/hand Big Blind. The money that
should have bought permanent jokers went to bridges: Gros Michel $5 (destroyed after 1 round), Even Steven
{PERISH,RENTAL} $1 + $5 reroll + $6 rent (2 rounds), Popcorn #2 $5. ~$22 of bridges in antes 1-3, $0-4 left in most
shops, so ante 3-4 shops could never afford an offer and the Rare tag on the ante-4 Big was out of reach.

Decisions I would change:
1. Ante 1 Buffoon: Popcorn over Clever (SIM 1.00 vs 0.34 over 3 blinds). The SIM horizon loves a +20 that is gone in 5
   rounds; Clever (+80 chips on Two Pair, permanent) plus a later +mult joker would have been worth more at ante 3-4.
2. Ante 1 Big shop: Gros Michel $5 with $7 (it died the next round). Ante 1 was already clearing 2x with Popcorn; the $5
   + interest would have bought the ante-2 Misprint AND kept a reroll.
3. Ante 4 Big: I spent both discards keeping 666. At Pair L3 / Trips L1, trips score LESS than a high pair, so the set
   only had value as a Full House/Quads draw. The solver's top line (break 666, keep A/Q for a high pair) was right in
   principle; the loss margin was 1342.
4. Loyalty Card at ante 4: it fires on the 6th hand after purchase; with 3 hands/round that was the boss. It added
   nothing to the blind I actually needed. Buy it only when its fire hand lands on the blind you are short on.

What worked: Trading Card (holo, rental) with a 1-card first discard each round is rent-neutral (+$3 vs -$3) and gives
+10 mult while thinning 2s/3s; skipping the ante-2 Small when broke ($3) for Handy (+$4) cost nothing.

Reusable rules (if-then):
- IF a Buffoon pick is between a decaying bridge (Popcorn, Gros Michel, Ice Cream) and a permanent scorer at ante 1
  AND the bridge's SIM edge comes only from the next 3 blinds, THEN take the permanent scorer unless ante 1 is otherwise
  lost: by ante 3 the bridge is gone and you have paid twice.
- IF you already clear ante-1 blinds by 2x+, THEN do not buy a second bridge (Gros Michel) - bank the money for ante 2-3.
- IF your main hand is Pair at L3+ and Trips is L1, THEN a made trips is worth less than a high pair; keep trips only
  as a Full House/Quads draw, otherwise break it for high-card pairs.
- IF you own Loyalty Card, THEN read raw `loyalty_remaining` (the joker's `extra.remaining` string is stale): it fires on
  the hand where (every-1 - (hands_played - hands_played_at_create)) mod (every+1) == every, i.e. the 6th, 12th... hand
  after purchase. Count which blind that lands on before buying/skipping.
- IF you own Trading Card, THEN make the first discard of every round a single junk card (2/3/4): +$3 pays its rent.

Advisor/CLI defects:
- Loyalty Card: right after purchase `advise` said "Loyalty Card fired on the LAST hand: x4 again in 6 hands" (no hand
  had been played since purchase); `s` shows `"remaining":"5 remaining"` forever (stale init string), while raw
  `loyalty_remaining` was 3. From the second hand on the note was right ("x4 in 5 hands (this one counts)").
- shopadvise ADVICE BUY Loyalty Card{ETERNAL} at ante 4 although its own SIM showed 0.85 vs 0.85 (no gain): the x4 could
  not fire until the boss. The rule score should check where the next fire lands.
- Buffoon pack SIM (ante 1) picked Popcorn 1.00 over Clever 0.34; the 3-blind horizon systematically prefers decaying
  bridges over permanent scorers (same family as the Troubadour/eternal SIM defect in 7806_AUZQFYQE).
- advise `Misprint range` note in the candidate list ("roll 0 -> 5, roll 23 -> ~1461") does not match the play line for
  the same hand ("roll 0 -> 1800, roll 23 -> ~10080"); the advise one looks computed for a High Card.
- Early-round SOLVER p values were ">=0.99" for every line (saturated), so they could not rank discards.
Bridge issues: two "advise only works while selecting a hand" right after `blind` (state not yet settled); a 2 s wait fixed it. 67 steps, no rejects.
