# Run 9JRMLNZG (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Mouth (1695/2000)

Ante 1 (300 Voucher / 450 D6 / The Window 600, $4): Small: dealt FH KKK33 304 one-shot. Shop $6: Buffoon $4 -> Bloodstone (override: advisor picked Hanging Chad{ETERNAL,RENTAL}). Big: heart Flush est 296, actual 666 (Bloodstone). Shop $8: Photograph{ETERNAL} $5. Window: club Flush 268, disc 4 keeping 4 hearts, heart Flush with KH est 560 actual 1260.
Ante 2 (1000 Voucher / 1500 Polychrome / The Mouth 2000, $9): Buffoon -> Sly{ETERNAL}; Buffoon -> Campfire; Hiker{RENTAL} bought $1 and sold $1 at once (free Campfire x1.25). Small: Two Pair QQ77 520 + JJ99 540. Shop $2: nothing. Big: sold Bloodstone (+$3, Campfire x1.5), disc 3 -> Broadway 972, J-high Straight 888. Shop $11: Buffoon (Hologram{ETERNAL,RENTAL} / Scholar{ETERNAL}) skipped, Lusty{ETERNAL} $5. Mouth (Pair lock): Pair AA (AH) 615, disc 5 -> Pair TT (TH) 600, Pair JJ 480 = 1695/2000. GAME OVER.

## Post-mortem
Binding constraint: SCALING. No +mult joker until the last shop of ante 2; base mult stayed 2 (5 with a heart pair), so a face pair with Photograph and Campfire x1.5 made 480 and The Mouth needed ~670 per Pair. Money was never above $11 (Small Blind $0, four $4 Buffoon packs in two antes produced Bloodstone, Sly, Campfire, and one skip).

Decisions I would change:
- Ante 1 pack: I overrode `advise` and took Bloodstone over Hanging Chad{ETERNAL,RENTAL}. One shop later Photograph appeared. Hanging Chad retriggers the first scoring card twice, and Photograph fires on each retrigger: x2 becomes x8 on a face pair. With that pair, every Mouth hand would have been ~2000+, so the rent ($3 per round) would have paid for itself. Even without Photograph, Chad triples every card-trigger effect (Lusty, Scary, Smiley, Bloodstone). I counted it as "+20 chips" and that was wrong.
- Ante 2 Big shop: I skipped Hologram{ETERNAL,RENTAL}. That was probably right at $7 with no way to feed it, but I spent the $5 on Lusty{ETERNAL} instead of holding money. Lusty added +3 mult on 2 of the 3 Mouth hands (~+40%), so it was not the mistake. The mistake was the ante-1 pick.

## Reusable rules (if-then)
- IF a pack or shop offers Hanging Chad (or any first-card retrigger) AND you own or are likely to buy Photograph / Scary / Smiley / Lusty-style card-trigger jokers, THEN take it even with ETERNAL+RENTAL at ante 1-2. Retriggers multiply card-trigger xMult (Photograph x2 -> x8 on a face pair).
- IF you own Campfire and the shop sells a RENTAL joker at $1, THEN buy it and sell it right away for $1. It costs $0 net, no rent is charged before round end, and Campfire gets +0.25 for the ante.
- IF the boss is The Mouth and you have no +mult joker, THEN the Pair lock needs ~boss/3 per Pair. Count your best Pair before the boss (face pair + Photograph + Campfire x1.5 = 480 here). If it is below boss/3, spend the last shop on the biggest +mult offered, not on Buffoon odds.
- IF The Mouth locks Pair and you hold a three-of-a-kind, THEN play only 2 of the cards (3 cards make Trips, which scores 0).

## Advisor/CLI defects
- Pack `advise` labels Hanging Chad "PLUS(retrigger: retrigger first card 2x)" with no note that it multiplies Photograph/Lusty/Scary. Its rank should rise when one of those is owned or common.
- `shopadvise` ranked Lusty Joker{ETERNAL} at 92 with "ETERNAL: fine, a core joker you would keep anyway". A one-suit +3 mult is not core, so that sticker note is wrong for suit-gated jokers.
- SCORE CHECK printed "one Pair (KK) ~480" while I owned Lusty. Heart pairs made 600-615, so the check ignores suit +mult.
- `est` leaves out Bloodstone (it prints "50% x1.5 not counted"): est 296 vs actual 666, est 560 vs 1260 on heart flushes. An expected-value est (x1.25 per heart) would fit better.
Bridge issues: none; 44 steps, no rejects.
