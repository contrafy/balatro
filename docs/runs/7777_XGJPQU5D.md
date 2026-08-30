# Run XGJPQU5D (port 7777) - LOSS at ante 1 Big Blind

Stake 1 (White). Boss ante 1: The Goad (never reached - lost at Big Blind before the boss).

Ante 1:
- Jokers at start: none. Shop 1 (after Small Blind win): Runner $5 (PLUS weak/conditional, +15 chips per Straight),
  Swashbuckler $4 (AVOID), Buffoon Pack $4, Standard Pack $4, Paint Brush voucher $10. No scoring (+mult/+chips)
  joker was on offer.
- `shopadvise` recommended the Buffoon Pack first (no scoring joker in shop). Opened it: choice of Cloud 9
  (economy, +$1 per 9 in deck/round) or Hallucination (slow/conditional tarot-on-pack-open). Picked Cloud 9
  per playbook 5 ("economy > slow scaling" when the pack whiffs on a scoring joker).
- `shopadvise` then recommended buying Runner ($5, conditional +15 chips/Straight) as the only remaining joker
  option (Swashbuckler is AVOID). Bought it, leaving $0. Ended shop with 2 non-scoring/weak jokers
  (Cloud 9 economy, Runner conditional-on-straight) and no flat +mult/+chips joker.
- Small Blind (need 300): advise->discard to keep Pair J, drew a 3rd Jack + pair of 3s -> Full House JJJ33,
  est 304, played, actual scored 304. Cleared (304 >= 300). est matched actual exactly.
- Big Blind (need 450): hand never contained anything better than Two Pair (best est 120, using A9/KT pairs) -
  no straight ever formed for Runner to fire, no pair reached three-of-a-kind. Followed `advise`/`hands` each
  turn (2 discards to hunt for trips/full house, none arrived). Final tally: 120 + 120 + 60 = 300 vs need 450.
  GAME_OVER. est for every individual hand matched the actual scored amount exactly (no est/actual divergence
  >20% this run - the deltas were all in the cards dealt, not in the estimator).

Post-mortem:
- Binding constraint: bad luck compounded by build. The ante-1 shop offered zero scoring (+mult/+chips) jokers
  at all (only a conditional-straight joker and an AVOID joker), and the only booster pack available (Buffoon)
  whiffed on a scoring joker too (Cloud 9/Hallucination, neither adds mult or chips). Per playbook 5, ante 1-2
  guidance assumes a scoring joker is reachable via one Buffoon pack; this run is a counter-example where the
  pack pool itself had no scoring option, and the shop's only "joker" slot options were also non-scoring.
  With Two Pair capping at ~120/hand with plain Jacks/Kings/Aces and no jokers boosting it, 3 hands could not
  reach 450 (max realistic ~360).
- Decision I would change: none of the individual plays deviate from advise/playbook - Full House on Small
  Blind was optimal, discards on Big Blind chased the best realistic upgrade (three of a kind/full house) each
  time and none arrived. The one lever not used: at $5 after buying Cloud 9, playbook says do not reroll under
  $10 in ante 1-2, so rerolling for a better joker was correctly avoided per rule, but with Runner being the
  only non-AVOID joker left, buying it used the last $5 rather than banking it - either choice loses this hand
  in hindsight since Runner never fired (no straight was ever drawn). Banking the $5 would not have changed
  the Big Blind outcome (still capped at Two Pair) but would have left $5 more for whatever came next had the
  hand cleared - moot here since the blind was lost regardless.
- Bridge issues: none. No `ACTION FAILED`, no retries needed, no odd errors. All commands behaved as documented.
- Playbook suggestions:
  1. Section 5 (ante 1-2) should note explicitly: if the Buffoon Pack ALSO whiffs (no scoring joker inside),
     and the shop's card slots are AVOID/weak-conditional only, there is no good ante-1 purchase available;
     this is a low-probability but real dead-end the current text does not cover (it only covers "pack whiffs,
     buy scoring joker next shop" assuming one exists next shop - here the run ended before a "next shop").
  2. Confirms 7a's data point: `est` was exact against actual scored value in every single hand this run
     (0% divergence), reinforcing that the estimator is reliable; the loss was entirely a card/shop supply
     problem, not an estimation or decision problem.
