# Run SWIHHDDP (port 7780) - LOSS at ante 1, Small Blind (stake 2)

Ante 1, Small Blind (need 300, $4 start, no jokers yet):
- Blind select: Small tag = Holographic Tag. `s` ADVICE said `b blind` (play, not skip) - followed.
- Hand 1: dealt JD TC 9S 7C 5S 5H 3H 2S (pair of 5s available). `advise` said DISCARD toward a straight
  (best made hand Pair est 40 << need 300; straight-draw EV 99 projected higher). Followed: disc 5 6 7 8.
- Hand 2: dealt AS AH KD JD TC 9S 7C 2C (pair of A, straight draw K-J-T-9 with gaps at Q). `advise` said
  DISCARD again toward straight (EV 116 vs Pair est 64). Followed: disc 2 6 7 8.
- Hand 3 (last discard): dealt AS KS KD JD TC 8D 7S 4D (pair of K, 4 diamonds toward flush). `advise` said
  DISCARD keeping the King pair as a floor while chasing flush: disc 1 5 7. This spent the last discard.
- Result of last discard: KS KD QC JD 8H 8D 4C 4D - THREE pairs (K,8,4), no flush/straight completed.
- Play 1: `advise`/`hands` -> best TWOPAIR K8 est 112. Played `play TWOPAIR 1 2 5 6 7` (filler 4C). Scored 112/300.
- Play 2: remaining hand still had JJ + 44 pair. `advise` -> TWOPAIR J4 est 96. Played `play TWOPAIR 3 4 7 8 6`.
  Scored 96 more (208/300 total). This consumed BOTH remaining pairs (K8 pair used in play 1, J4/44 pair used
  in play 2) leaving zero pairs for the final hand.
- Play 3 (forced, 0 discards, 0 consumables, no jokers): dealt AD KC QC TD 9C 7H 6D 2D - no pair, no 4-flush
  (max 4 diamonds short by one), no straight (K-Q gap at J, T-9 gap to Q). Only legal candidate: HIGH CARD
  Ace, est 16. `advise` confirmed this was the only playable option and flagged it would leave the blind
  76 short. Played `play HIGH 1 8 7 6 5` (only legal action, 0 discards/hands/consumables remained).
- Final: scored 224/300. Small Blind lost. RUN OVER at ante 1, first blind, $4 in hand, zero jokers ever bought
  (game over occurred before any shop visit was reached).

Post-mortem:
- Binding constraint: pure misplay/plan sequencing, not money or bosses (never even reached a shop). The
  chosen line (discard-discard-discard chasing straight/flush across all 3 discards, then playing BOTH made
  pairs across hands 1-2) guaranteed hand 3 would have zero pairs left, since all three pair-ranks
  (K/8/4 and J/4) discovered by the last discard were split across only two hands, exhausting the only two
  scoring resources before the forced final hand. With three pair-ranks in hand (K,K / 8,8 / 4,4) after
  the last discard, a Full House was reachable in principle only with a third card of one rank (never drawn),
  so Two Pair was the ceiling either way - but the SEQUENCING (which two pairs to bank in which hand) left
  the worst residual (a pure high-card hand) for the last, unavoidable hand.
- Decision I would change: on hand 1 with 3 pairs already made after the last discard (K8, K4, or 84 as
  Two Pair options plus a leftover single pair), the priority should have been to make sure hand 3 is never a
  guaranteed dead high-card hand. Concretely: play 1 should have used only ONE pair-rank + filler (not two
  pair-ranks as Two Pair) to preserve a pair for hand 3, e.g. `play PAIR K` (K,K + fillers) in hand 1,
  `play PAIR 8` in hand 2, leaving `PAIR 4` (idx 4,4) guaranteed available for hand 3 - trading lower per-hand
  score (Pair ~60 each vs Two Pair ~100+) for a guaranteed non-zero final hand. Rough math: 60+60+ (Pair4
  ~36-40) = ~156-160, which is WORSE than the 208 actually banked by hands 1-2 combined - so purely on total
  score this run's actual line (208 after two hands) was ahead of pace; the real failure was that Two Pair in
  hand 2 used BOTH remaining pair ranks (J and 4) instead of one, when a single-pair play (`PAIR J` + fillers,
  leaving the 4,4 pair intact) would have banked less in hand 2 but guaranteed a Pair-est-36+ hand 3 instead
  of a High-Card-16 hand 3. Estimated alternative: 112 (hand1 TwoPair K8) + ~60 (hand2 Pair J, keeping 44) +
  ~36 (hand3 Pair 4) = ~208, statistically similar to the realized 224, and STILL likely short of 300 - so
  this specific instance may have been unwinnable regardless of sequencing once the last discard whiffed the
  flush/straight and only left three pair-ranks with no way to reach Full House/Trips. The deeper issue is one
  ante earlier: `advise` sent all 3 discards chasing a straight/flush from hand 1 rather than ever stabilizing
  on a pair-family hand early, when Black Deck at stake 2 with $4 and zero jokers has very little margin
  for a whiffed draw at the Small Blind (which unlike other stakes still costs a shop visit if lost, but
  here ended the run entirely).
- No bridge/CLI errors encountered. All commands returned `ok:` or the expected `ADVICE:`/`Legal:` lines;
  `advise` and `hands` outputs matched (`est` was accurate versus actual scored deltas, no >20% divergence
  logged - only 3 hands played this run, none diverged: 112 est/112 actual, 96 est/96 actual, 16 est/16 actual).
- Playbook suggestions:
  1. `advise`'s discard-toward-a-straight/flush heuristic (comparing "made hands project to X" vs a
     straight/flush EV) does not appear to account for the case where the straight/flush chase fails and
     leaves MULTIPLE small pairs that must then be split across exactly 2 of the 3 remaining hands, guaranteeing
     the 3rd hand has nothing. When 0 discards remain and >=2 independent pair-ranks are held, `advise` should
     warn explicitly that any Two Pair play consumes 2 of the pair-ranks and prefers a plan that reserves one
     single-pair-rank untouched for the final hand, UNLESS the total across all hands beats the reserve-plan
     total by enough margin to still clear the blind (neither did here, so it's moot, but the general case
     needs the warning).
  2. Consider flagging explicitly, at the point a discard is about to be the LAST discard, if the resulting
     hand (after best-case draw) still cannot reach `need` even with ideal remaining plays - so an agent can at
     least understand a loss may already be structurally likely before committing the final discard action.
  3. This run never reached a single shop (lost at ante 1 Small Blind, hand 3 of round 1) - no scaling/economy
     data to add this time.
