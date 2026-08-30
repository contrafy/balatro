# Run HYH5NQHL (port 7779) - LOSS at ante 1 Small Blind

Stake 1 (White), Black Deck. No shop was ever reached (lost first blind of the run).

Ante 1: Small Blind tag=Rare, Big tag=Voucher, Boss=The Head (a suit debuffed). Starting $4, no jokers (pre-shop).
Dealt KD 9D 8C 8D 7D 4H 3C 2C (Pair 8 est 52, need 300). `advise` chased a 4-diamond flush draw (EV 178) over
the made Pair (est 52); followed advise and discarded the non-diamonds. Redraws kept landing 4 diamonds + junk
(never the 5th diamond) across all 3 discards:
  - Disc 1: kept K9D 8D7D(4 diamonds), drew AC KD QH QC 9D 8D 7D 3S -> still 4 diamonds, disc'd non-diamonds again.
  - Disc 2: kept KD 9D 8D 7D again, drew KD QS 9D 8D 7S 7D 6S 2S -> 4 diamonds + a loose Pair-7 (7S/7D) appeared
    (est 48) but advise still chased the flush (EV 206) over banking the pair.
  - Disc 3 (last discard): discarded the Pair-7's off-diamond half (7S) and other non-diamonds to keep the same
    4 diamonds; final draw AD KD JD TH 8S 7H 5S 3D had NO pair and 4 (not 5) diamonds - a dead hand.
Forced play sequence (0 discards remaining for hands 2-3, no better option ever appeared):
  - Hand 1: TWOPAIR 98 (idx 2 3 4 5, filler 8) est 108, actual 108. Running total 108/300.
  - Hand 2: PAIR J (idx 3 4, fillers 8 7 6) est 60, actual 60. Running total 168/300.
  - Hand 3 (forced, no discards, no pair/flush available): HIGH CARD AD, est 16, actual 16. Final 184/300. LOST.

Post-mortem: binding constraint was scaling/luck, not money or boss. This was a pure bad-draw run: the flush
chase never completed (needed a 5th diamond across 3 redraws and never got one), and by using all 3 discards
purely chasing diamonds, the final forced hand had zero pair/flush backup and was a guaranteed-loss high card.
No shop was ever reached, so no joker/economy decisions were possible - the run was decided entirely by card luck
on the very first blind, before any purchase existed to change the outcome.
The one decision I would change: on the THIRD (last) discard of the round, when a made Pair (7S/7D, est 48) was
available alongside the flush draw, bank information about how many hands/discards remain - with 0 discards left
after this and 2 hands still to play, keeping the pair as a guaranteed floor (even if not played that turn) would
have been safer than discarding it away for a flush that, if it whiffed, leaves the final hand with literally no
made hand of any kind. `advise`'s EV math (206 vs 48) is correct in isolation but does not account for "this is the
last discard before a forced play of whatever is left" - variance matters more than EV when there is no way to
recover from a miss.
Bridge issues: none. All commands (start, blind, disc, hands, advise, play) worked as documented; `est` matched
actual score exactly on both played hands (108/108, 60/60).
Playbook suggestions:
  1. On the LAST discard remaining in a round, if a made hand (even a weak Pair) exists alongside a drawing hand,
     weight variance/floor more heavily than raw EV - a whiffed draw with 0 discards left can produce a completely
     dead final hand (no pair, no flush), which is strictly worse than banking a mediocre made hand.
  2. Consider having `advise` flag explicitly when a candidate discard, if it misses, would leave zero viable made
     hand for a subsequent forced play (i.e., "floor risk" warning), not just the EV of the intended draw.
