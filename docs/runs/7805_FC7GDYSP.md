# Run FC7GDYSP (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind Small Blind (192/300)

Ante 1 (Small 300 Economy tag / Big 450 Coupon tag / The Pillar 600, $4): played Small jokerless (Economy tag gives no
joker, ADVICE b blind). Dealt QD TS TC 9S 9D 8C 7H 2S. Disc QD 2S (keep TT99+87: J/6 straight, T/9 full house, 12
outs) -> drew AD 3S, miss. Disc AD 3S again (same 12 outs) -> QC 3D, miss. Played Two Pair TT99 + 3D filler 116. Hand
AH KD QC 8C 7H 6H 5D 3C: dumped AKQ3 as High Card 16 to dig the 8765 open straight (8 outs, 4 cards, ~66%) -> drew
JC JD TD 3H, miss. Final Pair J 60. Total 192/300. GAME OVER.

## Post-mortem

Binding constraint: luck on a jokerless ante-1 Small Blind, made worse by drawing too few fresh cards. With no joker
the only hands that reach 300 in 3 tries are Straight/Flush/Full House (~260-350) or three Two Pairs (116 each). Three
draws toward a 12-out and an 8-out target all missed (~25% x 34%).

Decisions I would change:
- Both discards were 2-card discards (keep TT99 87). That saw only 4 new cards before the first play. The alternative
  "play Two Pair first while holding both discards" banks 116 and keeps 2 discards for the remaining 184 with a fresh
  4-card draw; the alternative "discard 4 (Q 8 7 2) keeping TT99" draws 4 cards for the Full House plus new pairs. I
  think the line was close to correct on odds (~75% to hit by the second discard), but it gave the round no second
  plan: after both misses I held 0 discards and a hand that needed two more Two Pairs.
- Nothing in the shop/skip layer to change: the run never reached a shop.

Reusable if-then rules:
- IF ante 1 jokerless and you hold Two Pair plus a 4-card open straight draw with 2 discards, THEN count total cards
  seen: two 2-card discards see 4 cards; prefer one 2-card discard and, if it misses, PLAY the Two Pair (116) with
  fillers to draw 5, keeping the last discard for the 184 that remains.
- IF the final two hands need 150+ with no discards and no pair, THEN dump the non-draw cards as High Card to dig a
  straight (that is what I did; 66% shot, missed) - it is the only line, so play it, but avoid reaching that state.
- IF the ante-1 Small Blind tag is a joker/pack tag, skip it (playbook); with an Economy/Coupon-only pair of tags you
  must play it jokerless and it is roughly a 60-70% blind - accept it, but do not burn both discards on thin draws.

Advisor/CLI defects:
- `advise` PACE line is inverted: "PACE: Two Pair est 116 x 3 hand(s) = 348 < need 300: discard toward a bigger hand"
  (348 is not < 300). The intent (Two Pair is not repeatable three times without discards) is right, but the printed
  comparison is wrong; it should say the repeatable-hand estimate, or compare est x hands against need correctly.
- `advise` recommended the identical 2-card discard twice (keep Two Pair floor + straight draw) without weighing
  playing the Two Pair first to see more cards; a cards-seen / plan-B check would help jokerless ante-1 blinds.
Bridge issues: none; 6 steps, all settled first try.
