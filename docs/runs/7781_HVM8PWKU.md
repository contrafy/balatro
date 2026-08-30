# Run HVM8PWKU (port 7781) - LOSS at ante 2 boss (The Arm)

## Stake 1 (White)

Ante 1: blind_select boss=The Head, tags Small=Rare Big=Investment. Start $4, no jokers.
Ante 1 Small (300): straight A2345 est220 actual220, pair Ax2 est60/64 filler -> scored 340. Cash $7. Bought Buffoon Pack ($4), picked Bloodstone (1/2 chance x1.5 per Heart, $3 sell) over Scholar. Shop had nothing else worth buying at $3, endshop.
Ante 1 Big (450): trips 9 -> discarded into Full House 99933 est292, actual 438 (Bloodstone x1.5 proc, +50%>20% diff, expected variance not a bug) -> scored 534 total with pair-Ace filler hand (est64 actual96, again Bloodstone proc). Cash $8. Shop: Faceless Joker (util, not scoring) only option, shopadvise said LEAVE, endshop with $8.
Ante 1 Boss The Head (600, hearts debuffed): discarded down to trips Q + pair 2, drew 4th Q for QUADS Q est630 actual630 (exact match) -> scored 630, blind cleared in one hand. Cash $16.

Ante 2: boss The Arm. Bought 2x Jumbo Celestial Pack ($6+$6) both Earth -> Full House L3 (90x8). Bought Hanged Man tarot ($3, unused/NOUSE in shop). $16->$0 spent this shop but shopadvise kept recommending packs since no scoring joker was on offer.
Ante 2 Small (800): trips4+pair2 dealt naturally -> FULLHOUSE L3 est848 actual848 (exact) -> cleared in 1 hand. Cash $6.
Shop: bought Temperance tarot ($3) then immediately used it (gave back $3, net $0, freed cons slot) - minor no-op buy, note for playbook: shopadvise should skip Temperance when joker sell value is trivial.
Ante 2 Big (1200): natural quads-of-4 -> discarded to keep trips4, drew pair K -> FULLHOUSE 444KK L3 est976 actual1464 (+50%, Bloodstone double-proc, expected variance) -> cleared in 1 hand, way over. Cash $13.
Shop: bought Wily Joker $4 (+100 chips if Three of a Kind, fires on Full House) -> 2/6 jokers. Ordered jokers (Wily left, Bloodstone/xMult right) per shopadvise. Bought Celestial Pack $4, no Earth offered, picked Jupiter (Flush L2, synergizes with Bloodstone's per-Heart chance since a Heart flush would proc it 5x). $5 left, shopadvise LEAVE, endshop.

Ante 2 Boss The Arm (need 1600, only 2 jokers: Wily +100chips/3oak, Bloodstone 1/2 x1.5/Heart): dealt JJ TT (two pair). `advise` repeatedly recommended discarding to draw around/improve a flat Two Pair (est 100-120) rather than steering toward a Three of a Kind that could become Full House L3 (90x8, would have scored 800+). Used all 3 discards chasing marginal two-pair improvements (drew a 3rd pair 77 instead of trips), then was forced to play Two Pair(120) -> Straight(340 total, A-5 filler) -> Two Pair(490 total) across the 3 hands with 0 discards left on the final two. Lost 490/1600. Final jokers: Wily Joker, Bloodstone. Money $5.

## Post-mortem

Binding constraint: misplay, not money/scaling/luck. I had Full House leveled to L3 (90x8) and Wily Joker (+100 chips on any hand containing Three of a Kind, which fires on Full House) — the correct highest-EV play against The Arm's 1600 target was to discard toward forming a Three of a Kind (keep one pair, discard the other two pairs, hope to pair up a third of that rank) to unlock a Full House worth an estimated 800-1200+, even after The Arm's -1 level penalty (L3->L2 still huge). Instead I (and `advise`, which only evaluates hands literally present/reachable by keeping current pairs) chased incremental Two Pair improvements each discard, capping the ceiling at ~120/hand and guaranteeing the loss. The one decision I would change: on the first hand of The Arm's round, discard down to a single made pair and actively chase trips instead of following `advise`'s "keep Two Pair, draw around it" suggestion — `advise` does not appear to search for a higher-tier hand reachable by discarding a made lower-tier hand when a leveled joker-synergized hand (Full House + Wily) is not currently on the board.

Bridge issues: none — every command executed as expected, no `ACTION FAILED` retries needed this run.

Playbook suggestions:
1. Add an explicit rule under section 4/6 (Boss notes) for The Arm: "if you hold 2+ pairs of different ranks and your leveled main hand is Full House, discard extra pairs and chase Three of a Kind instead of stacking Two Pair — a delevel from L3 to L2 is still far better than a maxed-out unleveled Two Pair."
2. `advise`'s DISCARD recommendation only optimizes the hand class already visible in hand; it should also weigh "discard toward a higher class my joker/level setup rewards" (e.g. abandon a safe two-pair to chase the trips needed for a leveled Full House) when the safe hand's est is far below need and hands/discards remain.
3. Note for shopadvise: recommending "buy $3 tarot, then use it for $3 back" (Temperance with only 1 cheap joker) is a net no-op that wastes a shop turn; add a floor (e.g. only buy Temperance when total joker sell value >= 2x its cost) so it isn't suggested as pure busywork.

Bridge/est calibration: two hands differed from actual by >20% (both explained by Bloodstone's 50% x1.5 chance, correctly flagged by the CLI's "notes: Bloodstone ... not counted" annotation, not an `advise`/`hands` bug):
- Ante1 Big Blind Full House: est 292 -> actual 438 (+50%).
- Ante2 Big Blind Full House 444KK: est 976 -> actual 1464 (+50%, double Bloodstone proc).
