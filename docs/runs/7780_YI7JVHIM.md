# Run YI7JVHIM (port 7780) - LOSS at ante 2 boss (The Water)

Stake 1 (White), Black Deck.

Ante 1: jokers [] -> [Supernova], levels none. Small Blind 300: Trips 6 (144) then Flush S (280) = 424, won.
  Big Blind 450: Straight 6-high (250) + Two Pair AT (186) + Flush C (480, overkill for 14 needed) = 916, won.
  Shop after Small: bought Supernova $5 (+mult = times hand played), $8->$3.
  Boss The Hook 600: discarded chasing straight, Hook randomly removed 2 cards from discard, drew into
  AAA TT (full house) instead: Full House AAATT est 1023, won at 1023/600.
  Shop after Big: bought Greedy Joker $5 (+3 mult/diamond), $7->$2 (below the $4 buffer, but no other
  scoring joker on offer and shopadvise still recommended it).

Ante 2: jokers [Supernova, Greedy Joker], levels {Straight L2 (60x7) via Jumbo Celestial pick of Saturn
  fallback, no Full House/Earth offered}.
  Shop before Small: nothing bought (LEAVE, $9 too low for anything worthwhile).
  Small Blind 800: Full House 888JJ (756) + Pair 3 (48) = 804, won by 4.
  Shop after Small: bought Grabber voucher $10 (+1 hand/round), $14->$4. Left rest (Troubadour/Mars/packs) per LEAVE.
  Big Blind 1200: Full House 99933 (730) + Straight 8-high (360, new Straight L2 from the pack) +
  Two Pair AQ (620, overkill) = 1710, won by 510.
  Shop after Big: bought Jumbo Celestial Pack $6, no Earth (Full House planet) offered; picked Saturn
  (Straight) as best fallback since Straight had already scored twice this ante. $9->$3.
  Boss The Water (no discards) 1600: forced to build from whatever was dealt across 4 hands (Grabber's
  extra hand helped). Two Pair 93 (220) + Two Pair K4 (432) + Two Pair T6 (676) = 1328 after 3 hands,
  272 short with 1 forced hand left. Final hand: A,K,J,9,8,5,4,3 all different ranks and only 4 clubs
  (no flush, no straight, no pair) -- no consumables held to rescue it (never bought a tarot/planet that
  goes to a consumable slot). Played High Card A (32), final 1360/1600. LOSS.

Post-mortem: binding constraint was the boss (The Water, no discards) combined with having zero
  card-targeting consumables in reserve and no xMult joker by ante 2. The two jokers (Supernova, Greedy
  Joker) are both conditional/growth types, not flat +mult/+chips, so the engine had thin, streaky
  scoring (Two Pair on random ranks) rather than a reliable made-hand floor. The decision I would
  change: at the ante-2 shop before The Water, buy an Arcana pack or hold cash for one instead of the
  second Jumbo Celestial pack, specifically to bank one card-targeting tarot (Death/Strength/Justice)
  as boss insurance per playbook 4.8 -- with The Water disabling discards, a rescue tarot for the final
  forced hand was the single highest-value purchase available and none was ever acquired.

Bridge issues: none. Every `advise`/`shopadvise`/`play`/`disc`/`buy`/`pack`/`pick`/`cash`/`endshop`/`blind`
  call returned cleanly; no `ACTION FAILED` or retry needed the whole run.

Est vs actual: no case where `est` differed from actual score by more than 20% (checked scoring lines
  above; est values matched or were within a few chips/percent every play, e.g. Full House est 1023
  exact match, Two Pair est 676 exact match).

Playbook suggestions:
  1. Ante 1-2: explicitly flag "no consumable held" as a risk once a suit/no-discard boss (The Water,
     The Serpent, The Hook) is the upcoming boss -- shopadvise currently only warns about joker-disabling
     bosses, not no-discard bosses that make a bad final hand unrecoverable. A short reminder to buy/keep
     one Arcana pack card-targeting tarot before such a boss would have caught this loss.
  2. When a Jumbo Celestial pack does not offer the main hand's planet (Earth for Full House here) and a
     secondary hand (Straight) has already scored twice that ante, taking that secondary planet is
     reasonable -- worth stating explicitly as accepted practice rather than only "fallback is worth
     little," since it did convert into a needed 360 chips at the very next Big Blind.
