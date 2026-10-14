# Run SDRXSM5R (port 7811, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Club (21272/50000)

Ante 1 (Holo/Juggle/The Hook 600, $4): Small FH TTT88 344 after 2 discards. Shop $5: Popcorn $5 (+20 mult, -4/round) -> $0. Big Two Pair 924 one-shot. Hook: Straight 9-high 1300 one-shot.
Ante 2 (Fish 2000, $14): Abstract $4, passed eternal Bloodstone, Scholar{perishable} $4 (Ace pair = 1944). Small/Big Two Pair, Fish Straight 1343 + 2P 450 + 2P 840. Passed eternal-rental Blue Joker.
Ante 3 (Goad 6400, $23): Popcorn gone, ratio 0.05 EMERGENCY. Buffoon -> Wrathful (mistake: Goad debuffs spades), reroll -> Gros Michel + foil Credit Card, reroll -> Seeing Double{rental} (sold Wrathful: swap). Skipped Small for Rare Tag -> free eternal Ancient Joker. Big Straight 7140 one-shot; Goad Straight K-high 9546 one-shot (Seeing Double makes Straights huge).
Ante 4 (Manacle 18000, $-4 on Credit Card): Gros Michel died. Rerolled -> Blackboard x3 + Joker +4 (sold Scholar). Skipped Small (broke, Holo tag -> Ice Cream rental, barred). Big 2P 13800 one-shot; Manacle 2P 17490 (Blackboard) + Straight 8804.
Ante 5 (Club 50000, debt -$20): Uranus x2 (Two Pair L4 80x5), Jupiter, Mercury bought on Credit Card up to its -$20 limit. Small 25000: Pair JJ 11520 + Pair 88 5700 + 2P 18600 (Blackboard by playing a red filler so held cards are black). Big 37500: 2P 22152 + 2P 19968. Club boss: SD dead (clubs debuffed), Blackboard still on (debuffed clubs count as black); best hand ~13.8k x 3 hands = 21272 vs 50000. LOSS.

## Post-mortem

Binding constraint: scaling/boss. The build was two conditional xMults (Blackboard x3 held-black, Seeing Double x2 club+other suit, Ancient x1.5/card) on flat +mult; it made 13-22k per hand at ante 4-5 but The Club (clubs debuffed) turned off Seeing Double and cut hands to ~14k; 3 hands could not reach 50k. No reliable xMult, no money (Credit Card debt -$20) to react at the ante-5 shop, and 6 joker slots filled with a +4 Joker, Credit Card and an eternal.

Decisions I would change:
1. Ante 3 Buffoon pick: Wrathful (spade mult) with The Goad as that ante's boss (the shop said so). Golden Joker would have given $4/round and 3 jokers for Abstract; the money would have bought a normal slot of mult later. Check the boss against suit jokers before picking.
2. Ante 5 shop: I spent into debt on 4 Celestial packs (Uranus x2) at -$20; income was nil afterwards, so no Director's Cut/reroll/xMult shop was possible at ante 5. Better to have kept the +$4/round Golden Joker economy and skipped rent.
3. Seeing Double is club-dependent: the Club boss at ante 5 turns it off. A boss check on suit-conditional jokers should be done in the shop BEFORE the boss (shopadvise warns for Goad/Wrathful but did not warn for Club vs Seeing Double + Blackboard).

Reusable rules (if-then):
- IF you own Blackboard (x3 held all Spades/Clubs): play a red card as FILLER in the 5-card play so the 3 held cards are black; `advise` lists the Blackboard est in the `play` line. Debuffed clubs still count as black for Blackboard.
- IF Ancient Joker is owned: `raw` -> ancient_card.suit shows this round's suit; pairs score max 1 heart each, only a flush stacks x1.5^5.
- IF Credit Card is owned and money is negative: planets/packs can be bought to -$20 but the next shops are dead; treat -$20 as a one-shot bridge, not a plan.
- IF a boss debuffs a suit that your xMult jokers need (Club vs Seeing Double), THEN the ante's SCORE CHECK must be recomputed without them; hunt a suit-free xMult first.

Advisor/CLI defects:
- `shopadvise` SCORE CHECK for ante 5 projected ~34k for the round but the boss estimate under The Club was ~17k/hand; it does not say the 3-hand total (~41k) fell short of 50000 in time to act.
- `advise` "SOLVER PLAY ... p>=0.99" lines at ante 5 relied on Blackboard held-black fillers; the plain candidate list (Two Pair est 7130) hides this until you add a red filler. The `hands` listing should show the filler variant first.
- In the Celestial packs `advise` printed only "pick 3 ... Mars" without noting Jupiter (flush) was better for Ancient/Blackboard; minor.
