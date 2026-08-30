# Run 4CPFRIGX (port 7782) - stake 3 (Green Stake) - LOSS at ante 3 boss The Wall (9416/10400)

Ante 1: Small Blind tag=Polychrome (not joker/pack tag, zero jokers) -> played per ADVICE (b blind).
  Small Blind 360/300 (Full House 252 + Two Pair 108). Shop: bought Buffoon Pack -> Green Joker (+1 mult/hand, -1/disc).
  Big Blind 531/450: overrode ADVICE on 2nd-to-last hand (it proposed discarding the only made J-pair + Q/T straight
  material, keeping disconnected 6/5/4/2 junk) -> instead discarded the junk, kept Q/J/J/T, drew A-K to complete a
  A-K-Q-J-T straight (est 405, actual 531 incl. boss carryover). Shop: bought Banner (+30 chips/disc remaining, $5).
  Boss The Club (600) cleared 624/600: Pair J -> High Card(152, followed ADVICE despite 2 discards left, since Green
  Joker/Banner both penalize/reward discard count so playing was correctly favored) -> Two Pair JT(after discarding
  debuffed TC) played as Pair J 180 (kept 1 disc for final hand per playbook) -> final hand Two Pair K3 292 (K,K,3,3).
Ante 2 shop: Cloud 9/Bloodstone $7 (2 scoring jokers already, no xMult offered), Grabber $10 voucher, Standard/Celestial
  packs $4, upcoming boss The Goad.
Ante 2: LEAVE shop 1 (nothing affordable). Small Blind: Flush D 1113/900 (1 hand, 2 unused hands banked $2 at cashout).
  Shop 2: overrode ADVICE (The Order $8, x3 mult if Straight -- does not fit our Two Pair main hand at ante 2, not yet
  ante 4+ where any xMult counts) -> bought Celestial Pack instead -> Uranus (Two Pair L2). Big Blind: Two Pair 86 (768)
  + Two Pair KT (980) = 1748/1350. Shop 3: bought Scary Face ($4, +30 chips/face) -> Celestial Pack ($4) offered no
  Uranus (Pluto/Neptune/Jupiter only); picked Pluto (High Card level) as least-wasted option -- minor misplay, all three
  planets on offer were off our main hand so the $4 mostly wasted; note for playbook: shopadvise should flag this pack
  as low-value BEFORE buying when no main-hand planet is possible, not just after. Boss The Goad (spades debuffed):
  Straight K-Q-J-T-9 est 2331 cleared 1800 in one hand (deck naturally had a straight in hand, no spade dependency).
Ante 3 shop (upcoming boss The Wall, x2 requirement -> 10400): bought Arcana Pack $4 -> The Chariot, sel'd JC (a main
  pair rank), Steel enhancement applied to JC. LEAVE (Mars/Earth $3 planets don't fit Two Pair; Paint Brush voucher $10
  unaffordable). Small Blind 2600: Pair A(644) + Two Pair K9(2079) = 2723/2600.
  Shop: LEAVE ($4, Celestial Pack ranked highest but demoted by the ante-3 no-xMult $5 cash floor rule -- correct per
  playbook "CASH FLOOR WITH NO MULTIPLIER"). Big Blind 3900: Two Pair KQ(2340) + Two Pair A6(936) + Two Pair JT(1700)
  = 4976/3900.
  Shop (last before The Wall): bought Jumbo Buffoon Pack $6 -> picked Mad Joker (+10 mult if Two Pair, fits main hand)
  over Scholar/Wily/Popcorn(decaying, avoided per playbook). LEAVE at $2 (nothing affordable).
Boss The Wall (10400, double of 5200): Two Pair 85(3276 via Full House 888JJ actually -- see below)... precise
  sequence: Full House 888JJ (est 4284, scored) -> Full House 55577 (est 2079; OVERRODE ADVICE which proposed
  discarding our LAST remaining discard on card idx8, a spare 3C not part of the made hand, leaving 0 discards for
  the remaining 2 hands of the round -- played the full house instead, preserving 1 discard for the true final hand,
  per the run's established "keep one discard for final hand" discipline) -> running total 6363/10400, 1 hand + 1
  disc left, need 4037.
  Final hand: discarded 4 non-pair cards (kept A,A,K,K) per ADVICE (this correctly used the last discard on the
  actual final hand) -> drew Q,J(Steel),T,7 giving Two Pair AK (est 3053) AND a straight A-K-Q-J-T (est 1881, lower).
  No held rescue tarot (never bought one this run -- shopadvise never surfaced money to spare for it once we chose
  Mad Joker over other options). Played Two Pair AK (3053, only/best option, 0 discards left) -> total 9416/10400.
  LOST by 984 chips (9.5% short).

Post-mortem: binding constraint = SCALING. We entered the ante-3 Wall boss with zero xMult (only 4 flat/PLUS jokers:
  Green, Banner, Scary Face, Mad) and Two Pair only at L2. Flat/level scoring alone tops out around 3000-4300 per
  hand at this point, and The Wall's doubled 10400 needed roughly 3 average hands at that level, which we only just
  missed. The one decision I would change: at the ante-3 shop before The Wall (the "$8, bought Jumbo Buffoon Pack"
  visit), I picked Mad Joker over nothing else scoring-relevant was offered (Scholar/Wily/Popcorn were the other 3),
  so that pick itself was fine -- the real miss was two shops earlier passing on The Order ($8, x3 mult if Straight)
  at ante 2. I overrode ADVICE there because it didn't fit our Two Pair main hand, and I stand by that call for a
  pure pair-family build, but in hindsight, given how rare xMult is (~2% of shops per playbook data) and that this
  run naturally produced TWO straights already (ante-1 Big Blind, ante-2 boss) from dealt cards, The Order might have
  fired often enough to be worth the slot as a secondary scaling path. Given the choice again with the same
  information, I would still avoid it as the ONLY multiplier for a Two Pair build, but if a second copy of it or a
  fitting xMult never appeared afterward (a real risk per the 2% rate), that reroll/pack money should have gone
  toward hunting an xMult that fits Two Pair specifically (Duo/Photograph-style) rather than another flat +chips/mult
  joker, which is what actually happened (Scary Face, then Mad Joker) -- both good picks individually but leaving us
  at 0 xMult by the Wall boss, which the playbook explicitly flags as fatal at ante 3-4.
Bridge issues: none. Every `play`/`disc`/`pick`/`sel`/`buy`/`pack`/`blind`/`cash`/`endshop` call succeeded on the
  first try; no `ACTION FAILED ... retry` or connection errors encountered this run.
`est` vs actual accuracy: every `est` shown at play time matched the actual scored delta exactly (e.g. Full House
  888JJ est 4284 -> scored delta 4284; Two Pair AK est 3053 -> scored delta 3053), so no >20% est/actual divergence
  to report this run.
Playbook suggestions:
  1. When a Celestial/Jumbo Celestial pack cannot possibly contain the main hand's planet mid-pick (all offered
     planets are for hands you don't build toward), shopadvise's pre-purchase pack description should say so (e.g.
     "no Uranus possible" is only knowable after opening); consider having shopadvise downrank ambiguous Celestial
     packs at ante 2-3 more aggressively when the main hand's planet has already appeared 0/2 times recently, or add
     a warning line before the buy rather than only a post-hoc note.
  2. Add an explicit rule: "at the last shop before a known The Wall boss, if zero xMult is held and a conditional
     xMult (even one that doesn't perfectly fit, e.g. Straight-only on a Two Pair build) is available and affordable,
     take it as a backup scaling path rather than a second/third flat +mult joker" -- this run had exactly that
     choice (The Order at ante 2) and passed on it, then lost the Wall boss narrowly (984 short) with zero xMult.
