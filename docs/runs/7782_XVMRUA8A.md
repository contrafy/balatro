# Run XVMRUA8A (port 7782) - stake 3 (Green Stake) - LOSS at ante 4 Boss (The Eye), 15270/16000

Ante 1: jokers [Raised Fist $5], $1->$3 after shop 1, buys: Raised Fist (shop1), Juggler foil from Buffoon pack (shop2, over Mail-In Rebate).
  Small 300: Quads 3s 504 (1 hand). Big 450: Two Pair 5/4 836 (1 hand, filler drew). Boss The Goad (Spades debuff) 600:
  Full House 2/6 2592 (1 hand, discarded debuffed Spades first). All 3 blinds cleared in 1 hand each, 2 discards left each round.

Ante 2: bought Space Joker $5 (1/4 level-up), Onyx Agate $7 (+7 mult/Club, overriding "no single-suit joker" per shopadvise's top rank).
  Small 900 (tag Voucher, no joker/pack so played per ADVICE): Straight T-high L1 est 1200 actual 1950 (Space Joker leveled Straight to L2,
    est diff +63%, logged). Big 1350: Two Pair J/5 est 2000 actual 2200. Boss The Water (0 discards) 1800: forced Pair 4s est 1292 actual 1292,
    then Pair T est 640 actual 855 (Space Joker leveled Pair to L2, est diff +34%, logged); total 2147/1800. No discards used both hands.

Ante 3: bought Celestial Pack (Mercury->Pair L3), Celestial Pack (Uranus->Two Pair L2), Arcana Pack (Justice->Glass on AD).
  Small 2600 (tag Handy, no joker): Straight K-high est 3180 actual 3180. Big 3900 (tag Ethereal): Two Pair K7 est 2852 actual
  2852 (pacing play, discards kept), then Two Pair 5/3 est 2438 actual 5876 (Space Joker leveled Two Pair to L3, +141% est diff,
  logged) total 5876/3900. Boss The Head (Hearts debuff) 5200: Straight A-high (4 clubs+1 diamond, Onyx Agate fired on 4 clubs)
  est 8211 actual 5635 (-31% est diff, logged) clears comfortably. Jokers by end of ante 3: Raised Fist, Juggler(foil), Space
  Joker, Onyx Agate. Levels: Straight L2, Two Pair L3, Pair L3. One Glass Ace (AD). Still zero real xMult joker.

Ante 4: sold weak Faceless Joker to open a slot ($8), rerolled once hunting xMult (none found; Wily/Green Joker offered,
  both left on the shelf per shopadvise LEAVE). Skipped Small Blind (tag Top-up: gave 2 free jokers, filled slots to 6/6:
  Faceless Joker later sold, Crazy Joker (+12 mult if Straight) kept). Big 12000 (tag Skip): chased a 4-club flush after
  discarding the Ace pair (est 6157 actual 6157), then Straight (Crazy Joker fired) est 6020 actual 12177 total clearing
  12000. The Fool tarot (ante 4 first shop pack) copied the last-used Justice, banking a rescue Glass tarot.
  Boss The Eye (16000, no repeat hand types all round) - LOSS:
    hand1 Two Pair Q/3 est 2040 actual 2040 (registers Two Pair, now dead for the round)
    hand2 Flush (clubs, Onyx Agate +7/club) est 5547 actual 8520 (Space Joker leveled Flush to L2, +54% est diff, logged)
        running total 8520/16000, need 7480 more, 1 hand + 1 discard left
    hand3 (final, forced, 0 discards after): Straight A-2-3-4-5 est 5805; used banked Justice tarot on the Ace (sel 1, use 1)
        to make it Glass before playing (playbook 4.8 last-hand-check) -> est rose to 6750; played, actual 6750.
        FINAL SCORE 15270/16000 - lost by 730 chips.

Post-mortem: binding constraint was money/scaling, not misplay. Zero xMult joker the entire run (Space Joker's random
  level-ups were the only "multiplier," and they are not guaranteed); the flat-joker/level-only build (Raised Fist,
  Juggler, Space Joker, Onyx Agate, Crazy Joker) scaled roughly linearly while The Eye's 16000 needed 3 DIFFERENT hand
  types in one round, which is much harder for a two-pair-family deck than a flat blind of the same size (no repeats
  allowed meant our best-scoring type, Two Pair, could only be used once). The one decision I would change: at the
  ante-4 shop before The Eye, I would have kept rerolling past the $8 stopping point (shopadvise said LEAVE) to hunt
  harder for any xMult, even a conditional one, since a 3-type no-repeat boss punishes a build with no multiplier far
  more than a flat boss of equal chip requirement - flat/level-only builds cap out fast once your best type is spent.
  Using the banked Justice on the final Ace only added +945 (est), not enough; with hindsight, applying it to a lower
  card in the straight or to a card that would also matter for a future hand would not have changed the outcome here
  (this was the last hand of the run either way), but confirms Glass's flat x2-on-one-card is a modest boost, not a
  reliable rescue when short by more than ~15%.
Bridge issues: none. All actions succeeded on the first try; no retries needed the entire run.
Playbook suggestions:
  1. Add explicit guidance for The Eye: with a pair-family main hand, plan which 2-3 DISTINCT types you can reliably
     produce (Pair, Two Pair, Flush/Straight backups) BEFORE round start, and bank the highest-value type for last
     since only your undealt cards constrain it - do not spend the strongest type (here Two Pair L3) on the first
     hand of the round when a weaker type (Pair) could have opened instead, saving Two Pair for later scoring need.
  2. When `shopadvise` says LEAVE while 0 xMult exists at ante 4+ and the upcoming boss is a multi-type boss (Eye/Arm),
     consider a lower reroll floor than $4-8: a multi-type boss punishes flat/level-only builds more than a flat-chip
     boss of the same requirement, so the EV of one more reroll is higher than shopadvise's generic floor assumes.
  3. Confirm whether Justice on a Glass card's mult is additive or multiplicative in `est`/actual - the observed
     jump (5805 est -> 6750 est, +16%) was much smaller than a true x2-mult would produce, suggesting the base
     mult before Glass was already large enough that x2 on one card's local contribution is diluted; document this in
     the RESCUE TAROT section so future agents do not expect Glass alone to double a shortfall exceeding ~15%.
