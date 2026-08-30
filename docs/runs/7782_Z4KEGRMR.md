# Run Z4KEGRMR (port 7782) - LOSS at ante 1 Small Blind

## Stake 1 (White)

Boss preview at ante 1: The Pillar (600). Small blind tag=Double Tag, Big blind tag=Investment Tag.

Ante 1 Small Blind (need 300): No jokers, no consumables (start of run). Dealt K K 9 8 4 3 3 2 (D-heavy).
`advise` chased a flush (4 diamonds held after first discard: KD 9D 8D 2D), discarded twice trying to complete it
(EV 167 then EV 179) — never hit the 5th diamond both times. Forced to play made hands as discards ran out:
TwoPair 9/2 (est 84, actual 84) -> Pair K (est 60, actual 60, discard-chase to a straight A-K-J-T missed the Q) ->
forced final hand Pair A (est 64, actual 64, no discards left, no consumables to rescue). Total scored 208 < need 300.
Run ended before any shop visit — zero jokers ever purchased.

Post-mortem: binding constraint = luck (two consecutive flush/straight draws both whiffed) compounded by
starting with zero jokers per playbook 5's "no joker before shop 1" reality — ante 1 hand values with no jokers are
inherently marginal (Pair ~50-64, Two Pair ~84-92) against a 300 need over 3 hands. The one decision I would change:
after the FIRST discard whiffed the flush (still 4 diamonds, no 5th), I would not have discarded a second time
chasing another low-probability draw with only 1 discard left before the shop-critical blind; instead bank the
made Two Pair (est 84) or Pair immediately and use the saved discard to optimize the final forced hand instead of
having zero discards for it. `est` matched `scored` exactly on every hand played here (no >20% deviation).

Bridge issues: none — every command behaved as documented, no `ACTION FAILED` or retries needed.

Playbook suggestions:
1. Section 4/`advise`: when only 1 discard remains and a flush/straight chase already failed once, consider adding
   a rule to prefer banking a made hand (Pair/Two Pair) over a second low-probability chase, since a whiffed second
   chase leaves zero discards for the forced final hand.
2. Confirm the known ante-1 fact from section 7 ("Big Blind (450) with 3 hands and no jokers... needs a
   flush/straight/full house or a +mult joker") applies just as hard to the Small Blind (300): with zero jokers,
   300 over 3 hands is already a coin-flip without a made straight/flush/full-house landing. Might be worth flagging
   this explicitly as a known-marginal spot rather than something `advise` can reliably solve.

