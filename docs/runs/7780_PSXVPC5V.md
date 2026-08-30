# Run PSXVPC5V (port 7780) - LOSS at ante 2 boss (The Pillar, 1600 need, scored 816)

Stake 1 (White), Black Deck.

Ante 1: boss The Head (Hearts debuffed). Small Blind 300 (tag Boss Tag), Big 450 (tag Voucher Tag).
Bought Wee Joker $8 (+8 chips/2 scored, permanent) after Small blind. No other jokers seen affordable ($0 left after buy).
Small: flush S est288 actual scored 288, then pair -> 332/300 win. Big: flush C 288 + straight A-5 est220 actual 284 (>20% diff, logged) -> 604/450 win.
Boss (The Head): drew around pairs/flush in clubs avoiding hearts; flush C 272 + two pair (debuffed cards) est58 actual90 (>20% diff, logged) + straight K-high 276(1 debuff card) -> 766/600 win.
End ante 1: $5, jokers [Wee Joker], no hand leveled yet.
Shop after ante1 boss: $11, bought Golden Joker $6 (+$4/round, ECON) -> $5.

Ante 2: boss The Pillar (cards played in Small/Big get debuffed at boss). Small 800 (tag Ethereal), Big 1200 (tag Rare).
Shop before Small: bought The Duo $8 (xMult, x2 mult if hand contains Pair) -> $5; bought To the Moon $5 (ECON, +1 interest/$5) -> $0.
Small blind: chased two-pair/full-house draws hard (4 pairs seen, 4-of-3-of-a-kind style rebuilds), ended up playing Full House QQQ77 est336 actual~400+ (Duo now doubling mult), then Trips 6 est144 actual192 (33% diff, logged), then Trips K est180 actual228 (27% diff, logged) -> cleared 820/800, very close.
Shop: reordered jokers so The Duo (xMult) is rightmost (`order 1 2 4 3`). Opened Jumbo Celestial Pack $6, picked Earth -> Full House now L2 (65x6). Bought Egg $4 (ECON, +$3 sell value/round) -> $0.
Big blind: dealt QQQQ (Four of a Kind) immediately after one discard; est1400 actual1624 -> cleared entire 1200 blind in a single hand.
Shop: $10 -> bought pack Jumbo Celestial (Earth) $6, then Egg... (see above order) -- money spent down to $0 before boss.
Boss (The Pillar): by this point most Queens/9s/7s/Aces/Kings had ALREADY been played as cards during Small and Big blind (we ran deep two-pair/full-house/flush/quad chases touching 20-30 distinct cards across those two rounds). Nearly every card drawn in the boss round showed (DEBUFF): K, Q, 7, 3, 8, 6 all debuffed at various points. Could only ever assemble Flush(264, one card debuffed), Two Pair(180, one card debuffed), Two Pair(180, one card debuffed) = 816 total vs need 1600. Last hand est180 vs actual244 (36% diff, logged). No discards were left by the final hand (all 3 used chasing draws in earlier hands of this same blind) so nothing could be done to route around the debuffs.
LOSS: 816/1600 against The Pillar, ante 2 boss.

Final jokers: Wee Joker (+8 chips/2 scored, permanent, small effect), Golden Joker (+$4/round), To the Moon (+1 interest/$5), The Duo (x2 mult if Pair, rightmost), Egg (+$3 sell value/round). Full House leveled to L2. Money at loss: $0.

Post-mortem: binding constraint was the boss mechanic (The Pillar) interacting badly with our aggressive draw-chasing style, not money or scaling -- money and jokers were actually in good shape (xMult The Duo secured by ante 2, Full House leveled, $10-13 cash outs). The decision I would change: during Small/Big blind of an ante whose upcoming boss is The Pillar (shown in shop and at blind select from the start of the ante), stop chasing multi-discard draws to maximize a single hand's score and instead play the smallest/cheapest hand that clears the remaining need, using as few distinct cards as possible, to keep a reservoir of un-debuffed cards for the boss round. We ignored this playbook guidance (section 6) because the shop advisor and hand advisor do not currently factor in "upcoming boss is The Pillar" when recommending discards/plays in Small/Big -- they only optimize the current blind's need.

Bridge issues: none. All `advise`/`shopadvise`/`play`/`disc` calls worked as documented; no ACTION FAILED or connection issues encountered this run.

Playbook suggestions:
1. `advise` (the hand advisor) should detect "upcoming boss is The Pillar" (visible in state from blind-select time) and bias its DISCARD/PLAY recommendations during Small/Big toward fewer distinct cards per hand, even at the cost of a lower single-hand score, rather than only optimizing est vs current need.
2. Add explicit numeric guidance to section 6's Pillar note: with 3 hands x up to 5 discards/draws per round across Small+Big, a two-round chase can touch 20-30+ of the deck's 52 cards, which can debuff nearly every rank by the boss; recommend a hard cap (e.g. "touch no more than ~10-12 distinct cards total across Small+Big when Pillar is upcoming").
3. The est-vs-actual calibration gap was consistently on the side of actual > est (est never over-predicted) by 20-55% across 5 logged instances this run, all involving Wee Joker (permanent, growing) and/or debuffed cards in the scoring set -- worth checking whether `advise`'s est formula undercounts Wee Joker's per-scored-2 growth or systematically underestimates hands containing partially-debuffed cards (since those hands still beat estimate despite the debuff notes).
