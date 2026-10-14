# Run XUABICDD (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big (4491/4800)

Ante 1 (Uncommon/Polychrome/The Window 600, $4): Small 300: Two Pair 99/44 92, 2 discards chasing a heart flush, drew FH QQQ88 344 one-shot. Shop $5: Buffoon pack -> Golden Joker (vs To the Moon; no mult offered), then Sly{PERISHABLE,RENTAL} $1 (0 scorers). Big 450: FH 77722 460 (est 460) one-shot. Shop $7: Jolly $3 (vs Raised Fist $5). Window 600: Pair QQ 800 (avoided debuffed diamond).
Ante 2 (Polychrome/Polychrome/The Needle 1000, $12): Smiley Face $4 + Celestial pack -> Mercury (Pair L2). Skipped Small (Polychrome tag, 3 scorers, $4). Big 1500: Quads 6666 2010 one-shot. Shop $11: FREE polychrome Mad Joker (tag) + Buffoon pack (Midas Mask / 8 Ball rental, skipped). Needle: Trips 222 1419 one-shot.
Ante 3 (Polychrome/Ethereal/The Eye 6400, $13): shop: Mercury (Pair L3), reroll found only planets, Uranus (Two Pair L2), $2 left. Small 3200: Pair 99 1944 then Two Pair QQ22 5301 (est exact). Sly perished, sold. Shop $5: nothing (Certificate{E}, Saturn, Jumbo Arcana $6). Big 4800: disc x2 (kept QS 44 then KD QS 9D 44) drew nothing, Pair 44 864, Pair 99 +fillers 1044 (solver p0.52, kept KD QS JD), last hand Two Pair AATT 2583 -> 4491/4800. LOST by 309 with $5 unspent and zero xMult beyond polychrome.

## Post-mortem

Binding constraint: scaling at ante 3. Build was flat +mult (Jolly 8, Smiley 5/face, Mad 10 Two Pair) + one polychrome x1.5, Pair L3 / Two Pair L2; a normal hand was ~1000-2600 and only a face Two Pair reached 5300. Big 4800 over 3 hands needs ~1600 per hand with no variance; the draws gave Pair 44 (864), Pair 99 (1044) and AATT (2583).

Decisions I would change:
1. Ante 3 Big, hand 2 (need 3936 left, hand KD QS JD TS 9C 9D 6H 4H): solver said Pair 99 + fillers p0.52 vs Straight KQJT9 (est 2251) p0.41. The straight would have left 1685 for the last hand, and the next draw produced Two Pair AATT 2583 which would then have cleared. When a made hand banks > half the remaining need and later hands are only needed at ~1700, bank it; the solver's 0.52 line banked only 1044.
2. Ante 3 Big, discards 1-2: I discarded 5 cards to keep QS 44 (p 0.93 line) and then 3 more; both draws were duds; hand 1 Pair 44 only 864. A Straight 7-high (330) was no use either; the real gap was no xMult / low base chips.
3. Ante 3 shop 1 ($13): Mercury + reroll + Uranus = $11 for ~+20% each on hands that were not enough. A Jumbo Arcana / Standard pack for Glass/Mult cards, or holding $13 for a reroll-hunt in the Big shop, might have found an xMult; I never saw a Buffoon pack in ante 3. Money did not score: $5 unspent at death.
4. Ante 1 Buffoon pick: Golden Joker (+$4) was the only non-junk option; fine, but it never converted into score (Golden pays $4 and the rental paid out only in rent).

Reusable rules (if-then):
- IF a polychrome/holo/foil edition tag is available at ante 2 with 3 scorers, THEN skip the Small: the next shop joker is FREE and edition-boosted (polychrome Mad Joker = x1.5 always, even with a mult condition that is often false).
- IF a Pair engine at ante 3 has no xMult, THEN the Big 4800 is a coin flip (~50%): before leaving the ante-3 Small shop spend ALL money on score (packs for jokers), not planets for a second hand type.
- IF a hand on a mid-round turn banks >= half the remaining need, THEN bank it over a slightly higher-p solver line that only banks ~1000 (the solver's 0.52 vs 0.41 gap was within noise for the last-hand distribution).
- The Window debuffs a suit: a debuffed card still makes the pair but score 0; play the clean pair (QQ) instead of Two Pair with the debuffed card (est already handled it).
- est is exact here: Pair 864/1044/1944 and Two Pair 2583 matched actual to the chip, so a "still short" last hand is truly lost; decide at hand 2.

Advisor/CLI defects:
- shopadvise at ante 3 Small shop said LEAVE with $5 while ratio 0.39 and TIGHT vs a 4800 Big; it had no buy that added score, so the problem was the lack of any affordable scoring item (only an eternal Certificate).
- Solver's "round p" at the ante-3 Big (0.93 on the first discard) was optimistic: the three lines all depended on 31-56% draws and the actual outcome was a loss.
