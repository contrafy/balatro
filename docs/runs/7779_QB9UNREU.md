# Run QB9UNREU (port 7779) - LOSS at ante 2 Big Blind (stake 3, Green Stake)

Ante 1: skipped Small Blind (Double Tag tag, $0 reward, per ADVICE) - no jokers yet.
  Big Blind: Full House x2 (33344 est228, 99966 est316) = 544/450, cleared in 2 hands.
  Shop: bought Erosion $6 (+4 mult per card below 52 in deck) - only $9, no other scorer affordable, shopadvise BUY.
  Rerolled shop ($5->$4) hunting a second joker: Supernova $5 offered but unaffordable at $4. shopadvise LEAVE.
  Boss The Hook (2 random discards/hand): Full House AAAKK (est372) then Flush S (est328) = 700/600, cleared in 2 hands with 1 discard to spare.

Ante 2: shop after ante-1 boss cash-out: $4, nothing affordable (Saturn $3 planet for Straight - not main hand;
  Joker Stencil $8 AVOID). shopadvise LEAVE, still only 1 joker (Erosion).
  Small Blind (900): Full House 66677 (est288) + Straight 14-high (est324) + Straight 11-high (est296, drew into it
  on the last hand with 0 discards) = 908/900, cleared with 0 margin to spare in 3 hands.
  Shop: $4, nothing affordable, LEAVE.
  Big Blind (1350): Flush D (est292) + Two Pair J3 (est92) + Two Pair KT (est120, forced final hand) = 504/1350.
  Lost - the single Erosion joker plus card-level hands could not project past ~900-1000 total across 3 hands
  even with ideal draws; the deficit was structural, not a misplay.

Post-mortem: binding constraint was MONEY, not scaling knowledge or misplay. We never got past 1 scoring joker
  (Erosion) into ante 2 despite following shopadvise exactly: the ante-1 shop had only $9 after the Big Blind win,
  spending $6 on the only offered scorer left $3, and the reroll that followed ($5) surfaced a second joker
  (Supernova, $5) exactly $1 out of reach. Every subsequent shop before the ante-2 Big Blind had $3-4 available and
  nothing affordable, so the run entered the 1350 Big Blind with a single, non-scaling joker (Erosion tops out around
  +4*20-30 = +80-120 mult on a full round, not enough against Green Stake's faster curve).
  Decision I would change: at the ante-1 shop with $9 and Erosion+reroll both on the table, reroll FIRST (before
  buying Erosion) to see if a cheaper or better second option appeared, since Erosion's ceiling is modest and a
  same-price alternative might have synergized better with the Full House/Straight hands actually being drawn -
  or accept Erosion but skip the $5 reroll immediately after (which left us $1 short of Supernova) and instead bank
  the $4 toward next shop's $5 joker. Both are marginal; the deeper issue is stake-3's $0 Small Blind plus $4-9
  ante-1 shop budgets structurally struggle to reach 2 scoring jokers by ante 2, matching the playbook's own
  "STAKE 3 ANTE 1-2" note about runs dying jokerless.
  Bridge issues: none. Every `advise`/`shopadvise`/`play`/`disc` call behaved as documented; no retries needed.
  Playbook suggestions:
  1. When shopadvise recommends BUY on a lone affordable joker at ante 1 with $8-9 in hand, consider printing
     whether a reroll BEFORE that buy (same money) might surface something better, since post-buy money is often
     too low to reroll meaningfully afterward.
  2. Add explicit guidance for the case "1 scoring joker, $3-4 available, ante 2 Big Blind next": current advice is
     correctly LEAVE (nothing affordable), but the playbook could flag this state ante-1-exit as high risk so the
     player prioritizes the Small Blind's shop tag differently (e.g. only skip Small Blind tags that give money or a
     joker outright, not just any non-Boss tag, once already down to 1 joker).
  3. Confirm whether Erosion should count as a "floor joker" per section 5 step 1 - it fired at ~+4*(cards missing
     from deck), which scaled with round length rather than being a flat per-hand bonus; it did keep pace early
     (est228->372 across Full Houses) but plateaued by ante 2 Big Blind. Worth verified numbers in section 7 for its
     typical ante-2 ceiling so shopadvise can compare it against Jolly/Sly/Smiley-class buys more precisely.
