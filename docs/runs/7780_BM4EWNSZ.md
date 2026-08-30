# Run BM4EWNSZ (port 7780) - LOSS at ante 3, Big Blind (need 3000, scored 2623)

Stake 1 (White), Black Deck.

Ante 1: jokers [Bloodstone (1/2 x1.5/Heart), Arrowhead (+50 chips/Spade)], $10 end of ante, levels {none leveled yet}.
  Small Blind (300): Full House 222KK est 264, actual 264; then Trips JJJ est 180 -> total 444. WIN.
  Big Blind (450): Full House 777KK est 324, actual 486 (Bloodstone hit both hearts, +50%, >20% diff logged). WIN.
  Boss The Head (600, hearts debuffed): Straight 9-high est 1028 actual 1028. WIN.
  Shop buys: Buffoon Pack -> Bloodstone; Arrowhead $7. Bought no planets yet (hand type undecided).

Ante 2: jokers +Wrathful Joker (+3mult/spade), +Egg (econ), main hand settled on Full House. Levels: Straight L2, Two Pair L2.
  Small Blind (800): Two Pair 74 est64 -> discarded to Full House 444QQ est 1720 actual 1720. WIN.
  Big Blind (1200): Full House QQQ55 est 910 actual 1170 (+29%, Bloodstone hit, >20% logged); + Pair 7 filler est48 actual48. total 1218. WIN.
  Boss The Club (1600, clubs debuffed): Quads TTTT (TC debuffed, scored 0 for that card) est 1400 actual 1400; + Pair 6 filler est360 actual360. total 1760. WIN.
  Shop: Celestial->Uranus (Two Pair L2, no Earth offered); bought The Trio $8 (x3 mult if Three of a Kind - fires every Full House, our first reliable xMult) at start of ante 3 shop.


Ante 3: jokers +The Trio (x3 mult if Three of a Kind - reliable xMult, fires on every Full House), 5/6 slots filled.
  Levels stayed: Full House L1 (never leveled - no Earth planet ever offered), Two Pair L2, Straight L2 (both dead
  weight since main hand is Full House).
  Small Blind (2000): Full House KKK33 est 2646 actual 3969 (+50%, Bloodstone double-triggered, >20% logged). WIN.
  Shop: bought The Trio $8 (only affordable scoring item).
  Big Blind (3000, Buffoon Tag - played per rule, tag not in always-skip list):
    Hand 1: Full House 33322 est 2163 actual 2163 (scored 2163, need 837 more, 2 hands + 1 disc left).
    Hand 2: advise played PAIR QQ + fillers est 400 actual 400 (scored 2563, need 437, 1 hand + 1 disc left) --
      advise's own numbers already showed best case (two pair 234, or straight-draw EV 389) both < need 437: this
      blind was arithmetically very unlikely to close from this point, regardless of the choice made here.
    Hand 3 (final, 0 discards): discarded toward an inside straight per advise (EV 389), missed the card (no Ten
      drawn); final hand only PAIR QQ est 60 actual 60. Total 2623 < 3000. LOSS. Run over.

Post-mortem:
  Binding constraint: scaling. Full House (our committed main hand) was never leveled past L1 all game -- no Earth
  planet ever appeared in any Celestial Pack (got Mercury/Pluto/Uranus/Saturn instead), so a base Full House capped
  around 40x4 base + jokers, while Big Blind needed 3000 by ante 3. Two Pair and Straight got leveled to L2 instead,
  which was wasted since we rarely played them as primary hands. Luck also played a role (missing the last straight
  draw), but the deeper issue was going into ante 3 with only one true (if reliable) xMult source and a still-L1
  main hand.
  Decision I would change: at 2163/3000 with 2 hands + 1 discard left (need 837 more), the advise line (play the
  weak Two-Pair-fallback hand now, save the discard for last) left the final hand needing an EV-389 inside-straight
  draw to clear a 437 gap that the tool itself flagged as short even in the best case. In hindsight, with a Full
  House main hand and Bloodstone (hearts) + Arrowhead/Wrathful (spades) as our only scoring jokers, it may have been
  better to discard immediately for a second full-house shot (there were still several pairs live in the remaining
  deck) rather than committing to the Two-Pair fallback + straight draw, since our jokers do nothing for straights
  specifically. This is judged in hindsight; the advise engine's own EV was already below the requirement, so the
  round may have been unwinnable regardless once the Big Blind scaled to 3000 without a leveled main hand.
  Broader lesson: should have prioritized rerolling/opening for an Earth planet (or any planet at all matching the
  main hand) once Full House was locked in as the main line at ante 2, instead of taking whichever planet a
  Celestial Pack happened to offer.

Bridge issues: none. No ACTION FAILED, no retries needed, no crashes, no connection issues the entire run.

Playbook suggestions:
  1. Section 5 (leveling): explicitly say "if a Celestial Pack does not offer your main hand's planet, still take
     one, but treat the ante as still needing scaling" -- right now the guidance to "take Earth if offered" doesn't
     say what to do about money/reroll priority when it's NOT offered repeatedly across multiple shops.
  2. Section 4 step 4 (out of discards / final hand math): when the tool's own EV for every candidate line (made
     hand and draw-EV) is below `need`, flag this explicitly as "this blind is likely lost" in the advise output so
     the agent logs it as a known-bad spot rather than only discovering it after the fact.
  3. Track "main hand level" in shopadvise's per-ante summary (e.g. "Full House L1, 2 antes since last level") to
     make chronic under-leveling more visible turn over turn, since it was the actual root cause here.
