# Run IWSHA9WB (port 7777) - LOSS at ante 1 Big Blind

Stake 1 (White). Boss ante 1: The Head. Small Blind tag=Foil, Big Blind tag=Holographic.

Ante 1 Small Blind (need 300): no jokers. Discarded twice per `advise` to build 22266 Full House
(2,2,2,6,6). Played FULLHOUSE idx[6,7,8,4,5] est 232 -> actual 232 (exact match). Then TWOPAIR 9,7
est 104, actual 104 (filler card 8). Total 336/300. Cleared with 1 hand, 1 discard unused. Cashed
out to $8.

Shop ante 1 (round 1): shopadvise recommended Buffoon Pack ($4) over Faceless Joker ($4, UTIL: $5 if
3+ faces discarded) and To Do List ($4, UTIL: $4 if listed hand played) since neither adds direct
mult/chips and jokers were 0/6. Opened pack: choice of Rough Gem (economy: $ per Diamond scored) vs
Swashbuckler (+mult = sell value of OTHER jokers). Picked Swashbuckler as the more "scoring" pick per
playbook's "adds mult" rule -- in hindsight this was a mistake: with 0 other jokers all game, its
mult bonus was permanently 0. Left with $4, shopadvise said LEAVE (nothing buyable at $4 worth it
over ending shop) -- did not buy Faceless Joker or To Do List even though $4 was affordable, because
advisor weighted both as UTIL not scoring.

Ante 1 Big Blind (need 450): Hand had 4 spades early; `advise` correctly chased the flush (EV 151-252
vs made two-pair 68-80). Played FLUSH est 252 -> actual 252 (exact). Then TWOPAIR 6,2 est 72 -> actual
72 (advisor chose to play this weak two pair now rather than discard, to bank guaranteed points and
save the last discard for the final hand -- reasonable sequencing, matched playbook rule ordering in
spirit even if not literally "discard while discards remain"). Scored 324/450, 1 hand + 1 discard left,
need 126. Discarded to keep QQ99 two-pair-face (est 116), best achievable target. Final hand (forced,
0 discards left): TWOPAIR Q9 est 116 -> actual 116 (exact match again). Total 440/450 -- LOST by
exactly 10 points.

Post-mortem: binding constraint was scaling/luck combined -- this was an extremely tight loss (440 vs
450 need, 97.8% of target) on the very first Big Blind, with only Swashbuckler (a joker that requires
OTHER jokers to do anything, and never got any) as the sole joker all game. Every `est` this run was
EXACT (not off by any %) versus actual score, so the CLI's estimator is trustworthy here -- the loss
was a shop-building mistake, not an estimation or execution error.
  One decision I would change: in the ante-1 shop, buy Faceless Joker or To Do List (both $4, both
  affordable with the remaining $4 after the pack) instead of leaving with $4 unspent. To Do List
  gives $4 (rerolls to a random target hand) which at minimum is money; Faceless Joker gives $5 if 3+
  faces are discarded in a hand, plausible given how often 3+ non-scoring faces get discarded while
  chasing flushes/pairs. Either would have been strictly better than banking $4 with a Swashbuckler
  that could never activate (only 1 joker slot filled all game). More importantly, I should not have
  picked Swashbuckler from the Buffoon Pack at all when it was the ONLY joker -- Rough Gem (guaranteed
  $1 per Diamond scored, an economy joker) would have funded buying a second, scoring joker sooner,
  which is what Swashbuckler actually needed to do anything.
  Bridge/CLI issues: none. Every command succeeded on the first try; `advise`'s `est` matched actual
  score exactly on all 4 played hands this run (no >20% deviation to flag).
  Playbook suggestions:
  1. Section 5 ante 1-2 guidance says "buy the FIRST affordable joker that adds mult or chips" but
     does not cover the Buffoon-Pack-with-only-non-scoring-choices case (Rough Gem vs Swashbuckler):
     neither is a flat +mult/+chips joker. Add an explicit rule: with 0 jokers owned, prefer an
     unconditional economy joker (Rough Gem, Golden Joker, etc.) over a joker whose bonus depends on
     OTHER jokers existing (Swashbuckler, Abstract Joker, Baseball Card) -- the latter are worth 0
     until a second joker is bought, so they should never be the FIRST joker.
  2. shopadvise's UTIL-vs-scoring weighting caused it to say LEAVE at $4 in ante 1 rather than buying
     a $4 UTIL joker (Faceless/To Do List) to fill the second slot. When jokers are 0/6 or 1/6 (as
     opposed to full), consider recommending an affordable UTIL joker over ending the shop with idle
     money, since ante-1 income is scarce and an empty joker slot is pure opportunity cost.
  3. No `est` deviations to report this run -- all 4 hands matched actual score exactly. Worth noting
     as a positive data point for the estimator's accuracy in un-bossed, no-special-card rounds.
