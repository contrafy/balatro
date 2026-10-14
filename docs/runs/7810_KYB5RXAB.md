# Run KYB5RXAB (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Mark (990/2000)

Ante 1 (Investment/Investment/The Window 600, $4): Small: disc x2 for FH draw, 2P 5533 72 then FH 777 22 260 -> 332/300. Shop $5: Buffoon pack $4 -> forced pick Lusty{PERISHABLE,RENTAL} vs Fortune Teller{ETERNAL}; took Lusty (+3/Heart). Rent put me at $-2 after Big. Big: disc, hearts Flush KH 8H 7H 6H 2H 1292. Shop $4: nothing buyable (Credit Card{E}, Faceless{R}). Window: 2P KK22 352 + FH AA444 740 -> $7.
Ante 2 (Coupon/Garbage/The Mark 2000, $7): EMERGENCY ratio 0.15. Buffoon pack $4 -> Drunkard (+1 discard, perishable) over Madness. Skipped Small (Coupon, broke at $3). Big 1500: hearts Flush 1368 + FH 630. Coupon shop: free Jupiter (Flush L3), free Celestial -> Jupiter, free Arcana -> Justice on KH (glass). Mark: bad deal (no heart pairs), discards gave AATT 310, then 5 face-downs; FH-of-faces never came; 590, 990 vs 2000. $5, 2 jokers, 0 xMult.

## Post-mortem

Binding constraint: scaling. At ante 2 boss I had NO real scorer: Lusty (+3 per Heart, hearts-only) and Drunkard (+1 discard). Typical non-flush hand ~310-460 vs 2000. Only a hearts Flush (~1400-1800) cleared anything; Mark face-down faces killed the pair engine (4 face-downs = pair only, ~150).

Decisions I would change:
1. Ante 1 first Buffoon pack gave only Lusty/Fortune Teller; nothing else was buyable ($5). Wasting the first shop on a pack that rolled a rental perishable suit-joker forced me to $-2 after Big (rent). An alternative was To Do List $4? Not much better. Honest conclusion: bad luck + $4 start.
2. Ante 2 second Buffoon pack at $4 (all my money, $7) yielded Drunkard/Madness. Free Coupon shop (after Big) arrived too late to help the Big, only the planets/Arcana: Justice on a single card is weak. Should have taken Hierophant/Magician? Not offered.
3. At the Mark, after first Two Pair 310 I still needed 1690 in 2 hands; the only out was a hearts flush (10%). Better: at the start, with 3 discards, I discarded 5 and kept TH 4H + facedown; no alternative then either.

Reusable rules (if-then):
- IF the boss is The Mark and your only scorers are suit/flush based with a Pair engine, THEN faces are hidden: count only non-face cards (their suit/rank is visible) and expect ~150 from a face pair; do not plan on face-down pairs.
- IF `sort suit` is used under The Mark, THEN face-down cards sort among the visible ones by suit order (spades, hearts, clubs, diamonds) and by rank (faces rank above 10): a face-down sitting before a visible TS is a spade face; between TS and 6H is a heart face. This reveals the suits of face-downs (idx order only).
- IF the ante-1 shop has $5 and no joker, a Buffoon pack roll can contain only a rental/perishable joker; a rental forces rent debt ($-2 after the Big at $1): take it only if hearts-flush style hands can clear Big by 1.2x.
- IF Coupon Tag is available at ante 2, THEN the free shop comes after the next beaten blind: skip Small only if the Big (1500) is clearable by the current jokers; I cleared Big with a hearts Flush 1368 + FH.

Advisor/CLI defects:
- `advise` under The Mark did not show an est for the face-down cards but suggested keeping 3 facedowns as "face cards"; no solver line was printed, so p(clear) was unknown. A SOLVER p for face-down hands would have shown ~0 and suggested a different line earlier.
- shopadvise labeled Jupiter $0 (flush planet) as "BUY +89" while the main hand "Full House (L1)"; the Flush was actually the only hand clearing blinds. The Lusty-based main hand (Flush) was not recognized as main hand ("main hand undecided"/"Full House").
- After Coupon free shop, `shopadvise` ranked Splash{ETERNAL,RENTAL} at -135, correct.
