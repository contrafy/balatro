# Run H6YHXLVU (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Needle (420/1000)

Ante 1 (Holo/Economy/The Manacle 600, $4): Small: Straight A-5 220 + Two Pair TT99 116 = 336/300. Shop $5: Scholar $4 (+20c +4m per Ace; single Ace High Card est 180, Pair AA 720). Big 450: Two Pair QQ22 88 + Flush 304 + Two Pair AATT 1020. Shop $5: Celestial -> Mercury (Pair L2). Manacle (hand size 7): Pair 99 129, Pair QQ 135, wheel Straight A-5 600 = 1 of 600.
Ante 2 (Coupon/Negative/The Needle 1000, $6): shop 1 had no joker; left with $6 (+$1 interest). Small 1000: Flush 288 + Pair AA 957 (hand 2). Shop $8: Swashbuckler{PERISHABLE} $4 (+2 mult; only +mult on offer). Big 1500: Two Pair AA99 1200 + Pair 66 185 + Two Pair AAQQ 1224 (cleared with 1 hand spare). Shop $8: Buffoon pack $4 -> Constellation{ETERNAL} (vs Drunkard rental); no other joker affordable. Needle (ONE hand, needs 1000, no Ace): disc 5 -> AC kept, disc 5 -> AC KC KD QH QD TD 9C 7D, best Two Pair KKQQ 420. LOSS 420/1000.

## Post-mortem

Binding constraint: scaling/luck at ante 2. One scorer (Scholar, only fires on Aces) + one +2 mult bridge; no hand without an Ace came near 1000 and The Needle gives ONE hand. The SCORE CHECK said "The Needle 1000 vs your round under its rule ~760-950" at both ante-2 shops; I treated it as noise because the previous two blinds were beaten by Ace luck.

Decisions I would change:
1. Ante 1 shop 1: Scholar ($4, Ace-gated) over a Buffoon pack. It worked at ante 1-2 only because Aces appeared; a non-Ace-gated joker (Jolly, Joker) would have made Needle a 1-hand ~600+ every deal. Ace-gated Scholar est 957 with Ace but only ~360 without.
2. Ante 2 shop 1 ($6): I left with $6 because rerolling left $1. Better: buy the Spectral/Standard? No; real error was the earlier ante-1 shop 2 spending $4 on a Mercury pack instead of keeping $5 (+$1 interest) for a reroll/joker. I entered ante 2 with 1 scorer and $6.
3. Ante 2 Needle: knowing Needle was the boss since ante 2 shop 1 (BOSS PREP printed it), I should have spent the Big-shop $8 on rerolls for a flat +mult joker (Jolly/Joker/Half Joker) instead of Buffoon pack -> Constellation (eternal, 0 planets in hand, +0 now). The pack gave no immediate score; Constellation needs planets I never held. Taking the Drunkard rental (+1 discard) would have given an extra dig (3 discards) for the Needle: P(clear) 53% after 2 discards -> maybe ~70% with 3.
4. Ante 2 Big shop: I did not buy the Jumbo Arcana / planets to feed Constellation; it is a dead slot at x1.0.

Reusable rules (if-then):
- IF the ante-2 boss is The Needle (1 hand, 1000) AND your 1-hand est without luck is < 1000, THEN before the Small/Big shops keep money for a +discard (Drunkard rental/eternal is acceptable here) or a flat +mult joker; digging with 3 discards is the only way.
- IF your only scorer is rank-gated (Scholar: Ace, Even Steven, Scary Face), THEN every Needle/one-hand boss is a coin flip; buy a second scorer that fires on any Pair BEFORE the boss shop.
- IF a growth xMult (Constellation) is offered in a Buffoon pack at ante 2 with 0 planets and $4, THEN it adds +0.0 now: with an Emergency ratio below 0.4 prefer the pack option that scores or digs now (Drunkard +1 discard) unless planets are in hand.
- IF The Manacle (hand size -1) is the ante-1 boss with an Ace-gated joker, THEN keep Ace pair draws: the winning hand was a wheel Straight A-5 (600) because Scholar fires on any scoring Ace.

Advisor/CLI defects:
- Pack advisor ranked Constellation{ETERNAL} (80) over a rental +discard even though the SCORE CHECK was EMERGENCY and Constellation adds nothing without planets; with The Needle ahead (1 hand) the +discard had higher value for the boss, which BOSS PREP flagged but pick ranking ignored.
- shopadvise printed "BOSS PREP: The Needle counters this build" and still ranked To Do List/Erosion/LEAVE; no concrete Needle plan (reroll for flat +mult, keep $5+) was offered.
- `advise` PACE "0 later hands" at Needle is correct, but SOLVER p 0.28 -> 0.53 shows the best action early was to keep an Ace and dig; consistent. No wrong estimates observed (est matched actual on 9 of 9 plays).
Bridge issues: none.
