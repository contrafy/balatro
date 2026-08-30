# Run BEYQ2DYI (port 7781) - stake 2 (Red Stake) - LOSS at ante 4 Boss (The Mark)

Ante 1: Small 320/300 (Straight then Two Pair), Big 500/450 (Two Pair x2), Boss The Club 792/600 (Two Pair, one card debuffed).
  Bought: Blue Joker ($4 Buffoon pack, over Crazy Joker which is single-hand-type/Straight-only per playbook rule - not counted
  as a scoring joker), Joker +4 mult ($2), Wheel of Fortune tarot ($3, used, no edition hit). Main hand: Two Pair. End $1.

Ante 2: Small 816/800 (Two Pair), Big 1992/1200 (Flush, chased per advise - est cleared with fewest cards), Boss The Mouth
  1600 need -> scored 2814 (Two Pair only, final hand est 1974 but actual 2814, +43% - Mystic Summit's +15 mult at 0
  discards seems undercounted by `advise`/`hands` est). Bought: Walkie Talkie (Buffoon pack, picked over Devious Joker
  which is also single-hand-type/Straight-only), Mystic Summit ($5, +15 mult at 0 discards), Satellite ($6 economy).
  5/6 joker slots filled. End $2.

Ante 3: Small 2706/2000 (Trips then Straight - no Two Pair available at start), Big 3040/3000 (Two Pair x2, second hand
  used Stone-card filler for +50 chips: est 696 -> actual 996, +43%), Boss The Psychic 4704/4000 (Two Pair/Straight mix,
  5-card-exact rule; final hand est 624 -> actual 924, +48% again from Stone-card filler contributing beyond the est
  preview). Bought: The Tower tarot + The Fool tarot from a Mega Arcana Pack ($8, only non-flush-suit picks available:
  Sun/Moon/Lovers pushed suits, skipped) - converted a junk 2D to a Stone Card (now a reusable +50-chip filler); Fool
  banked a spare copy of The Tower (unused, NOUSE - needs a hand to target). No joker or planet bought all ante (money
  too tight after the Mega pack, shopadvise said LEAVE both remaining shops). Main hand still L1 Two Pair, 0 xMult.
  End $6, 5/6 jokers.

Ante 4: Small 5474/5000 (chased a diamond flush per advise EV, then a low-straight EV chase failed to connect, final
  forced hand cleared 636->2058 est via Mystic Summit's 0-discard bonus - won by the skin of our teeth). Big 7540/7500
  (Straight L2 mid-round, final Two Pair cleared 1920 est vs 1880 need - also razor thin). Bought: Photograph ($5,
  our first and only xMult all run - fires on first scoring FACE card, which our Two-Pair-of-numeric-ranks build rarely
  includes), Celestial Pack ($4) -> Uranus (Two Pair now L2), Arcana Pack ($4) -> The Empress on both 5s in the deck
  (+4 mult each, permanent enhancement), Pluto ($3, used - levels High Card, marginal but only affordable option and
  feeds Satellite's per-planet income). Boss The Mark (faces face-down, need 10000): first hand Two Pair 2610, second
  hand played 4 face-down cards blind (guaranteed pair, scored only 784 - well under the ~1176 estimate), third/final
  hand (0 discards, Mystic Summit active) best Two Pair 9-5 (using one Empress 5) est/actual 3068. Total 6462/10000 -
  LOST. Consumable The Tower (banked spare, NOUSE except when a card was highlighted) was evaluated for the final hand
  but skipped: it only adds +50 chips (~+150 after L2 x3 mult), nowhere near the ~3538 shortfall.

Post-mortem: binding constraint = SCALING. By ante 4 we still had only 1 xMult joker (Photograph) which barely ever
  fired (needs a face card in the scoring Two Pair; our engine is built on numeric-rank pairs), main hand was only
  L2, and no card enhancements beyond 2 flat-mult 5s. The playbook's ante 3-5 "is there an xMult joker" check was
  followed every shop, but only one ever appeared (Photograph) and it was the wrong shape for a numeric pair-based
  Two Pair engine - a joker like The Duo (fires on any Pair, not conditioned on suit/face) would have been much
  stronger. Money was also perpetually near $0 (spent to $0 or $1 in 4 of 5 shops), leaving zero cushion for reroll
  or a second xMult when one appeared.
  The ONE decision I would change: at ante 1, when Blue Joker (chip-scaling, no mult) and Joker (+4 mult) were our
  first two jokers, I should have prioritized finding a THIRD scoring joker or an early xMult more aggressively
  instead of buying Satellite (pure economy, ante 2) and Wheel of Fortune (low-value gamble, ante 1) - both were
  shopadvise-endorsed but neither added mult/chips/xMult. With 6 joker slots filled by ante 4 (5 of them non-xMult),
  there was no room left to pick up a second/better xMult when Photograph turned out to be a weak fit.
Bridge issues: none. All commands behaved as documented. The `play 1 2 3 4` (no TYPE word) syntax for a
  guaranteed-but-unknown face-down hand type worked as advertised.
Playbook suggestions:
  1. Section 5's "buy the first affordable joker with mult/chips" rule should also weigh whether the joker's
     trigger condition (face card, specific rank) matches the player's already-established main hand composition -
     Photograph was "the first xMult" but its face-card condition almost never fired against a numeric-rank
     Two Pair build. Suggest: prefer The Duo/other Pair-triggered xMult over a condition-mismatched one even if
     the mismatched one appears first.
  2. Add an explicit note that `est` for a fully-face-down forced hand (playbook 4.7, "any 4 face-downs always
     contain a pair") can undershoot noticeably (this run: est ~1176, actual 784, -33%) since the estimator cannot
     see the real ranks/suits - treat that estimate as a rough floor, not a number to bank pacing on.
  3. Consider tightening the ante 1-2 shop rule to say "a scoring joker OR bank the money" more strongly when only
     economy/tarot options are available with 2+ scoring jokers already owned - this run spent down to $0-1 five
     times in a row (ante 1 through ante 4), leaving no reroll cushion when a real xMult (Photograph) or better
     fit was needed.

