# Run VGGMFBGY (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Small Blind (941/1000)

Ante 1 (300 Holo tag / 450 Skip tag / The Club 600, $4): Small jokerless: 2 discards for a KKQQ Full House missed, two High Card digs (15+15) kept 4 clubs, club Flush 284 -> 314. Shop $4: Buffoon -> Spare Trousers (over Square Joker), $0. Big: Two Pair QQTT 240 + Trips 6 240 = 480. Shop $5: declined Abstract {ETERNAL,RENTAL} $1 (advisor BUY) and Lusty {ETERNAL}, left. Club: dealt K-9 Straight 414 + Two Pair 7766 276 = 690. Trousers +4.
Ante 2 (1000 Rare tag / 1500 Double tag / The Needle 1000, $12): shop: Flash Card rental + Juggler -> advisor REROLL $5 -> Oops/Faceless, left $7. Played Small (Rare tag pays after Big): 2 discards on a 4-spade flush draw both missed (9 outs, 4 draws each), forced Two Pair 9922 336, High Card dig 105 keeping T987 for J/6 (72%) missed, final Two Pair 8877 500 -> 941/1000. GAME OVER.

## Post-mortem
Binding constraint: SCALING at ante 2 with a single joker. Spare Trousers (+2 mult per Two Pair, +4 -> +8 during the round) was the only scorer; every hand was L1. The ante-2 Small (1000 = 333/hand) needed either a Flush/Straight hit or three Two Pairs. Luck was also bad (two 61-66% flush digs and a 72% straight dig all missed), but the plan needed luck because the shops gave only one scorer in 4 visits (Buffoon pack: Trousers/Square; shops: Stencil $8 unaffordable, Abstract eternal+rental, Lusty eternal, Flash Card rental, Juggler, Oops eternal, Faceless).

Decisions I would change:
- Ante 1 Big-Blind shop ($5): I refused Abstract Joker {ETERNAL,RENTAL} $1. With Trousers it is +6 mult (x2 jokers), growing +3 per later joker. The losing hands would have been 9922 42x14 = 588 and 8877 50x16 = 800 instead of 336 and 500: the blind clears by ~700. The -$3/round is real, but losing at ante 2 costs everything. Survival beat economy here; the advisor's BUY was right.
- Ante 2 Small hand 1: I spent both discards chasing a 4-spade flush (~85% combined, missed both). Keeping the Pair 66 and digging for Two Pair would have grown Trousers (+2 mult per Two Pair) on every play: with a growth +mult joker for Two Pair, play toward Two Pair, not flushes.
- Ante 2 shop: the $5 reroll found nothing; at $12 a Standard pack or holding $12 changes nothing for the next hand, so this one is neutral.

Reusable rules (if-then):
- IF you own 0-1 scoring jokers at ante 1-2 and the only +mult joker offered is an Eternal/Rental $1 (Abstract, Joker, Jolly...), THEN buy it: -$3/round is ~$9/ante, while the ante-2 Small Blind (1000) is out of reach of one flat joker on L1 hands.
- IF you own Spare Trousers (or another per-type growth joker), THEN discard toward its type (keep pairs, dig for a second pair) instead of chasing a Flush/Straight: every Two Pair played adds +2 mult to all later hands, a missed flush adds nothing.
- IF you hold 4 to a straight/flush with 2 hands left and no discards, THEN a 4-card High Card dig keeping the draw is right only when the hit alone clears; compute the exact remaining need first (here the T-high straight cleared by 1 point, so the dig was correct but fragile).
- IF a made Full House/Straight draw needs 1 card and you have 3 hands and no jokers at the ante-1 Small, THEN High Card digs that keep the draw (4 cards played = 4 draws) beat playing a weak Two Pair: they cleared 300 here with 314.

Advisor/CLI defects:
- shopadvise rated Abstract {ETERNAL,RENTAL} $1 at 25 and said BUY while printing "-$66 for the rest of the run", with no comparison against the ante-2 requirement; the advice was right but the score/explanation contradicts itself (it rated the eternal Lusty -17). Make the reason explicit: "only +mult available, ante-2 Small needs 333/hand".
- advise at ante 2 Small with Spare Trousers chased a 4-spade flush twice (EV 353/377) over keeping Pair 66 for Two Pair; the EV does not count Trousers growth (+2 mult per Two Pair for the rest of the run).
Bridge issues: none.
