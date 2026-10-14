# Run F1NGCDKQ (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (26537/37500)
Ante 1 (300/450/Head 600): Small jokerless: drew a Diamond flush AD KD QD 9D 2D (est 308 vs 300) with 1 discard. Shop $6: Buffoon pack -> eternal Joker (+4 mult); bought perishable-rental Riff-raff $1 (made Even Steven + Drunkard on Big select, Egg + To Do List on boss select). Big: Full House 2016 (Even Steven +4/even card is huge at pair-family L1). Boss Head: trips 280 + FH 1152.
Ante 2 (1000/1500/Wall 4000): sold To Do List/Riff-raff. Small two pair 1988 (Blue Joker), Big FH 1176 + pair 576. Rerolled once at $17: Mad Joker + Clever Joker (perishable $4 each) -> Wall Two Pair AAKK 3680 + Pair 6s 1400.
Ante 3 (3200/4800/Wheel 6400): skipped Small for Meteor tag (Mega Celestial: Uranus + Earth). Big: two pair 3638 + pair 1575. Wheel: all-even Two Pair TT88 7788 in one hand.
Ante 4 (9000/13500/Eye 18000): sold Egg ($20) for liquidity, Jumbo Celestial -> Uranus, bought Misprint $4 (eternal), Uranus $3 (Two Pair L4). Small Two Pair QQ66 (est 8976, cleared 9000). Big: Two Pair 12496 + 10255 (holo Ice Cream bought, replaced Blue Joker). Mad/Clever perished after Big. Eye: Gros Michel from Buffoon pack; FH 11136 + Two Pair AAQQ (est 8280) cleared 18000.
Ante 5 (25000/37500/House 50000): Uranus again (Two Pair L5). Small: Two Pair 10486 + Two Pair 13115 + Pair ~3.4k cleared 25000. Bought Loyalty Card rental $1 (x4 every 6 hands). Big 37500: Two Pair 12261 + 9776 + Pair JJ ~4.5k = 26537. LOST. Needed ~12.5k per hand at ante 5 and had ~10k.

## Post-mortem
Binding constraint: SCALING. Zero r/g xMult all run. Build was Two Pair L5 + five flat +mult/+chips jokers (+4 Joker, Even Steven, Misprint, holo Ice Cream, Gros Michel) = ~10k/hand; ante 5 Big needs 12.5k/hand x3. Best 3-hand sum 26.5k vs 37.5k.
What went right: Even Steven (+4 mult per even scoring card) was a monster at L1-L5 (a TT88 two pair = 7788 at ante 3, 12k at ante 4). Skipping Small at ante 3 for a Meteor tag (2 planets) was fine. Riff-raff at ante 1 gave 4 jokers for ~$1+$3 rent.
Decisions I would change:
1. Ante 4 shop: I spent $37 on 2 rerolls + Celestial packs and only found Misprint; Hologram ($7, growth xMult) was on offer and I passed because it needs card additions. A Standard/Arcana plan to feed it was never going to beat x1.0, but nothing else was xMult. If a growth xMult is offered at ante 4 with no other xMult, take it and buy Standard packs.
2. The Loyalty Card (x4 every 6 hands) bought at ante 5 arrived too late to land on a blind that mattered (it fires on the 6th hand: 3 hands/round means every other round). Buy it BEFORE a boss and count hands so the 6th hand is the final hand of a blind you need.
3. Ante 5 Big: I played Two Pair first on every hand. Nothing different would have worked; the shortfall was ~11k with Misprint averaging.
Reusable rules:
- IF you own Even Steven (or any per-even-card joker), THEN build the Two Pair from 2/4/6/8/10 ranks: all-even Two Pair is ~+16% over face pairs (+16 mult vs +8). Keep T/8/6/4 pairs over J/Q/K pairs when choosing what to play.
- IF Riff-raff is offered at ante 1 for $1 (rental+perishable) and you have free slots, THEN buy it; each blind select makes 2 clean Common jokers (stickers do not apply to created jokers). Free slots are required, so sell junk first; sell Riff-raff when slots are full.
- IF The Eye is the boss, THEN each hand type scores once: Two Pair + Full House + Pair all in one round are worth ~25k at L5; fish with discards first (Pair is always a fallback hand) and play the hand type that is hardest to redraw first.
- IF perishable jokers (Mad+Clever) are your whole engine, THEN plan the replacement the shop before they expire: they died after the ante-4 Big and ante-5 Small dropped from ~12k to ~8k per hand.
- IF the last hand of a blind needs more than the best possible hand (check Misprint range in `hands` notes), THEN it was decided earlier: re-check pace after hand 1, not hand 3.
Advisor/CLI defects:
- `hands` Loyalty note wording is confusing ("fired on the LAST hand: x4 again in 6 hands" on the first hand after purchase); the ab text "5 remaining" never updates (static config string).
- `shopadvise` ranked Even Steven weakest and recommended selling it ("SELL then BUY Ice Cream") although Even Steven was worth +16-32 mult on my even pairs; the advisor does not model Even Steven's per-card value (its listing says only "+4 mult per even card").
- `shopadvise` listed Egg as "dead weight" at ante 4 even though it sold for $20 (it is a bank): fine to sell for liquidity but the advice text should say so.
- `advise` at ante 5 Small kept suggesting "discard toward a bigger hand" with Trips Q while Two Pair QQ77 (8774) beat Full House (7749); FH is not always the best type at Two Pair L5/FH L2.
Bridge issues: none (one race: I chained `endshop` and `blind` in parallel tool calls and the second was refused with NOT LEGAL, nothing sent).
