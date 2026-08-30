# Run MCBMZ8ED (port 7781) - stake 3 (Green Stake) - LOSS at ante 2 Small Blind (572/900)

Ante 1: jokers [Red Card (util, dead early)], $0->$5, no scoring joker all ante (rerolled to $0 for one, none appeared).
  Small 300: Straight 8-high 260 + Pair 6 56 = 316. Big 450: FH 44422 224 + Trips A 189 + Pair 9 56 = 469.
  Boss The Head (debuffs hearts) 600: FH 333-88 260 + Flush S 280 (drew into 6 spades) + Two Pair J7 74 (both debuffed) = 614.
  Cleared all 3 blinds jokerless via aggressive discard-to-full-house/flush chasing; pacing sanity check overridden
  advise's first-hand "pacing" PLAY on the Big Blind (est 126 Trips vs need 450 over 3 hands was infeasible) by discarding
  instead, which produced a Full House worth 224 instead of the 126 Trips.

Ante 2: jokers [Red Card, still not scoring], $5->$0->$0. Two rerolls this ante both burned the shop's only scoring
  joker: shop 1 rerolled from $5 to $0 with no scorer appearing (shopadvise ADVICE: REROLL, per the "0 scoring jokers:
  reroll to $0" rule); shop 2 rerolled again and the reroll itself replaced a visible affordable Sly Joker ($3, PLUS on
  Pair) with a new row, then shopadvise showed Sly Joker $3 unaffordable at $0 and LEFT with nothing bought.
  Small Blind 900 (Small Blind pays $0 at stake 2+, no way to skip into money): built up via three pair-shaped hands
  chasing full house/two pair (Full House 999-JJ 348, Two Pair AK 124, Two Pair Q5 100 forced final) = 572/900. LOSS.
  Zero scoring jokers the entire run: max single-hand output was a jokerless Full House (~260-350), and ante-2's 900
  requirement needs ~3 hands averaging 300 each with zero margin for a weak final hand - which is exactly what happened
  (forced final hand only found three low pairs, no full house).

Post-mortem: binding constraint was SCALING/LUCK, not misplay - the run never drew a scoring joker despite two ante-1
  rerolls and two ante-2 rerolls (all four rerolls following shopadvise's own REROLL-to-$0 rule), and the very shop that
  DID show a buyable joker (Sly Joker $3, ante 2 shop 2) was the shop I had just rerolled INTO with $0 in hand - the
  reroll cost consumed the money needed to buy the joker it then revealed.
  The one decision I would change: at ante 1 shop 2 ($5, no scorer, Mystic Summit-tier item not present), instead of
  rerolling all the way to $0 on shopadvise's say-so, I would have rerolled ONCE ($5->$1) and then stopped with $1 in
  hand rather than rerolling again to $0 - so that if the following ante-2 shop's opening row (before any reroll) showed
  an affordable joker, I would have had a few dollars of buffer. In practice the loss came from ante-2 shop 2's reroll
  landing Sly Joker into an already-empty wallet; holding back even $3-4 through the ante-1/2 rerolls would likely have
  let me buy it. This suggests the REROLL-to-$0 rule is too aggressive when it is the SECOND consecutive reroll-to-$0
  in as many shops with no scorer found either time - the marginal value of one more $1-2 reroll attempt should be
  weighed against needing that exact $1-3 to buy whatever the next shop shows without another reroll.
Bridge issues: none. All commands (start, blind, advise, disc, play, cash, shopadvise, reroll, pack, pick, endshop)
  returned clean, expected output every time; no ACTION FAILED, no retries needed, no Connection refused.
Playbook suggestions:
  1. When a shop's REROLL both fails to find a scoring joker AND spends the money needed to buy one that WAS visible
     before the reroll (i.e. rerolling away an affordable Sly/Jolly/Joker+4/etc. that was on offer), shopadvise should
     warn "an affordable scoring joker is on the table right now - buying it beats rerolling" even under the
     0-scoring-joker REROLL-to-$0 rule. This run rerolled away a $3 Sly Joker at ante 1 shop 2's row before ever seeing
     it, then rerolled AGAIN at ante 2 shop 2 straight into a fresh, still-unaffordable Sly Joker.
  2. Add a data point: two consecutive shops (ante 1 shop 2, ante 2 shop 1) rerolling to $0 with zero scoring jokers
     found in either compounds into a THIRD shop starting at $0-5, i.e. a jokerless deck can spiral through 2-3 shops
     without ever being able to afford the very joker it needs when it finally appears. Consider capping "reroll to $0"
     at one shop per ante-pair rather than repeating it every shop while jokerless.
  3. STAKE 3 DATA POINT for section 7a: a fully jokerless deck (Red Card util joker only) cleared ante 1 (Small 316/300,
     Big 469/450, boss The Head 614/600) purely on full-house/flush chases built via aggressive mid-round discarding,
     but died at the ante 2 Small Blind (572/900) - confirms the existing "ante-2 Small Blind 900 cannot be cleared by
     a jokerless pair engine (~135-150/hand)" note; a Full House-heavy jokerless engine tops out around 260-350/hand,
     still short of 900/3.
