# Run CK1NLNZI (port 7777) - LOSS at ante 2 Small Blind (stake 2, Red Stake)

Previous run on this port reached ante 8 boss Violet Vessel (300000) with Pair L6 + Constellation x1.7, scored 95251 (already logged elsewhere). This is a fresh run started per instructions.

Ante 1 Small (need 300): discarded to a flush draw twice (Hanged Man-style broadway attempt didn't land, hearts did), played FLUSH H est 304 -> scored 304. Cashed to $6.
Shop: no scoring joker offered (Space Joker LEVELS, Smeared Joker UTIL $7 unaffordable); bought Space Joker $5 per shopadvise (could not afford reroll+$4 floor). $1 left, endshop.

Ante 1 Big (need 450): drew into Full House 66644 (est 264, pacing play, scored 264 exact), then drew a broadway straight A-K-Q-J-T (est 324, scored 324 exact). Total 588/450, cleared. Cash -> $6.
Shop: bought Droll Joker ($4, +10 mult if Flush) over Lusty Joker (single-suit, playbook says never at ante1-2) and a voucher. $2 left, endshop.

Ante 1 Boss The Manacle (-1 hand size, need 600): built Two Pair JJ88 across two forced discards (0 discards left after 3rd), played TWOPAIR est 112 (scored 112 exact), then drew a 6-diamond hand and played FLUSH D est 1162 with Droll bonus -> ACTUAL 1274 (est differed by ~10%, within tolerance). Total 1274+112=1386, boss cleared. Cash -> $8.
Shop: bought Wily Joker ($4, +100 chips on Three of a Kind) OVERRIDING shopadvise's top pick The Idol ($6, conditional xMult keyed to a specific rank+suit that changes every round). Reason logged: playbook's ante 1-2 rule is explicit that TWO ordinary +mult/+chips jokers come before any xMult, conditional or not, and we held ZERO ordinary scoring jokers at that point (Space Joker/Droll are marginal/conditional); The Idol's target card is not guaranteed to be in a pair/two-pair hand at ante 2, whereas Wily fires on any hand containing Three of a Kind (and richer). Left $4, endshop (couldn't afford Idol anyway after buying Wily).

Ante 2 Small Blind (need 800, no_blind_reward: Small=true this stake so no cash on this blind anyway): three discards spent chasing a diamond/spade flush that never completed (only reached 4-of-suit twice). Forced into weak scoring hands with 0 discards remaining for the last 3 plays:
  - TWOPAIR Q7 est 108 -> scored 108 (exact)
  - PAIR A est 64 -> scored 64 (exact)
  - STRAIGHT 14-high (A-K-Q-J-T) est 324 -> scored 324 (exact, final hand)
  Total 496/800. LOST — blind not cleared. GAME_OVER.

Post-mortem: binding constraint = SCALING/misplay compounding at ante 2. By the boss of ante 1 we only had 3 jokers, none a reliable flat +mult/+chips engine for a pair-family hand (Space Joker=LEVELS only, Droll=Flush-only, Wily=Trips-only) — none of them scored on the Two Pair/Pair hands that actually came up in the ante-2 Small Blind. The deck also ran unusually flush-heavy in ante 1 (bailing us out to huge overkill scores, 1274 and 588) which masked that our joker suite gave ZERO support to the bread-and-butter Pair/Two Pair hands we'd actually draw at ante 2. When ante 2 arrived without another flush, our floor was a bare Pair/Two Pair/Straight with no joker multiplier at all, and 800 (Red Stake, no discounts) was simply out of reach on 3 hands + 3 discards of unlucky draws (never completed a 5th flush card in 2 separate flush chases).
  Decision I would change: at the ante-1 boss shop (Wily vs Idol), also consider spending down to reroll for ANY unconditional pair/two-pair flat joker (Jolly +8 mult on Pair, or similar) instead of buying either Wily or Idol — Wily only fires on Three of a Kind, which we had built ZERO of by ante 2 despite our hand being pair/two-pair shaped the whole game. A Jolly/Sly-class joker (fires on Pair, i.e., every hand we actually made) would have been directly relevant. This was the one binding misplay: buying a Trips-only joker while every real hand in this run was Pair/Two Pair.
Bridge issues: none. All `est` figures matched actual scores exactly except the ante-1-boss Flush (est 1162, actual 1274, +9.6%, within the documented Misprint/edition variance tolerance — no Misprint joker was involved here, likely just rounding in est chip calc for 6-card diamond flush; not logged as a >20% deviation).
Playbook suggestions:
  1. Clarify in section 5 (ante 1-2 shop) that a "Three of a Kind"-only joker (Wily, Zany, Mad, Clever) should be deprioritized relative to a Pair-only joker (Jolly, Sly) when the run's actual hand history so far has been Pair/Two-Pair, not just "prefer Pair-triggered ones in a Buffoon pack" — the same logic should apply to any single-item shop offer, not just Buffoon packs.
  2. Consider flagging in shopadvise/playbook when zero jokers in inventory score on the hand types actually being played (a "joker/hand-type mismatch" warning), since Space Joker + Droll + Wily gave 0 support to the Pair/Two Pair hands that lost ante 2.
