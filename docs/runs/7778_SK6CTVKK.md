# Run SK6CTVKK (port 7778) - stake 2 - LOSS at ante 1 boss The Goad

Ante 1: skipped Small Blind (Juggle Tag, ADVICE: b skip, $0 reward blind, +3 hand size next round via tag).
  Big Blind 450: discarded toward a flush per advise (disc 2 4 6 7 9), drew a 5-club flush (est 260, actual 260),
  then a 5-spade flush (est 308, actual 308) with the +3 tag hand size. Cleared 568/450. Cashed out, $4 -> $9.
  Shop: pack 1 (Buffoon Pack $4) per shopadvise. Pack offered Delayed Gratification (economy, $2/discard if
  none used) vs Wrathful Joker (suit-gated Spade joker, banned at ante 1-2 per playbook 5). Picked Delayed
  Gratification (no scoring joker on offer; avoided the banned single-suit joker). Then shopadvise ADVICE
  bought To the Moon $5 (ECON, +1 interest/$5), leaving $0. Jokers after shop: Delayed Gratification, To the
  Moon -- NEITHER is a scoring joker (no Pair/Trips/Two-Pair trigger, no flat +mult/+chips). endshop per
  shopadvise (nothing else affordable).
  Boss The Goad (Spade suit debuffed) 600: dealt QS/9S/7S debuffed among a 4x3 + 8x2 hand. advise correctly
  discarded debuffed spades each turn and chased Full House -> played FULLHOUSE est 272 actual 272 (272/600).
  Ran out of pair-family draws; final two hands were bare Pairs (est 48 actual 48, then est 64 actual 64) with
  zero discards left and zero consumables held (rescue tarot never bought - stake 2 ante 1 has none available
  from the card row yet per playbook 7b, which only applies from ante 3). Final score 384/600. LOSS.

Post-mortem: binding constraint = SCALING (zero scoring jokers). The two joker buys this run (Delayed
  Gratification, To the Moon) were both economy/utility, not scoring jokers — shopadvise's own WARNING said so
  ("none of your jokers scores on a plain Pair") but its ADVICE line still directed spending the only $5 on
  To the Moon (econ) rather than holding cash for a scoring joker at the next shop (there was no next shop
  before the boss — Small was skipped, so the ante-1 shop after Big Blind was the ONLY shop before the ante-1
  boss). The pack itself offered no scoring joker (Delayed Gratification / Wrathful Joker), so by the boss we
  had a flat, jokerless build facing a debuffed-suit boss that removed 3 of 8 cards from play each hand.
  The decision I would change: with only one Buffoon pack card being non-suit-banned and non-scoring, and the
  ADVICE line spending the remaining $5 on an economy joker instead of banking it, I should have overridden
  shopadvise and kept the $5 (or asked whether skipping the Small Blind at ante 1 is safe when it removes the
  ONLY extra shop visit before the boss — with no scoring joker in hand yet, the extra shop from playing the
  Small Blind might have been worth more than its $0 payout, since it doubles shop chances for a floor joker
  before an unknown boss). I followed shopadvise as instructed since I had no concrete rule-based reason to
  override at the time (its own warning did flag the gap but the ADVICE line proceeded anyway) — flagging this
  as a possible playbook/shopadvise gap below.

Bridge issues: none. All CLI commands worked as documented; ACTION FAILED / retries were never encountered.
  `advise` and `hands` `est` values matched actual scores exactly on every hand this run (Flush 260/260,
  Flush 308/308, Full House 272/272, Pair 48/48, Pair 64/64) — no >20% est/actual divergence to report.

Playbook suggestions:
  1. shopadvise's ADVICE line spent the last $5 on an economy joker (To the Moon) even while its own WARNING
     said zero jokers score on a Pair. Suggest: when jokers 0-1/6 are all non-scoring and the shop offers no
     scoring joker, ADVICE should say REROLL or HOLD CASH rather than buying pure economy, especially at ante 1
     stake 2 where skipping the Small Blind means the post-Big-Blind shop is the ONLY shop before the boss.
  2. Consider flagging in the stake-2 Small-Blind-skip rule (playbook 5) that skipping ante-1 Small Blind
     costs not just "$0 income" but also a full shop visit's WORTH of pack/reroll chances at finding the
     first scoring joker before the ante-1 boss — this run's loss traces directly to reaching the boss with
     zero scoring jokers because the only pre-boss shop was spent on economy, and there was no second shop to
     course-correct in.
