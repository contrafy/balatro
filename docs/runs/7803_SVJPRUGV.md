# Run SVJPRUGV (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (1168/1500)

Ante 1 (D6/Uncommon/The Goad 600, $4): Small: 2 discards + 2 dig plays to a spade Flush 288 -> 336/300. Shop $4: Buffoon -> Golden Joker{PERISH,RENTAL} (advisor SKIP; other option Swashbuckler{ETERNAL}). Big: Flush 320 + Flush 284. Shop $6: Red Card $5, Square{ETERNAL} $4, Standard, Jumbo Arcana; left with $6 (advisor said sell Golden). Goad: heart Flush 300, disc 4 -> club Flush 320 = 620/600.
Ante 2 (Handy/Rare/The Wall 4000, $13): EMERGENCY 0.07. Buffoon -> Red Card{ETERNAL} (other: Credit Card), Spectral (Ankh/Aura) skipped -> Red Card +3. Small 1000: Flush 539 + dig High J 60 + Flush 525 = 1124. Shop $6: Standard pack bought and skipped (Red Card +6). Big 1500: disc 5 keep JJ 9D, solver disc 1 5 6 7 8 (broke 2P JJ66 416, p 0.66 vs 0.47), drew junk: Pair 99 224, 2P AAJJ 496, 2P TT88 448 = 1168/1500. LOSS.

## Post-mortem

Binding constraint: no scoring joker offered. 4 shops + 2 Buffoon packs showed Swashbuckler{E}, Golden{P,R}, Red Card,
Square{E}, Dusk{R}, Oops All 6s{P}, Red Card{E}, Credit Card, Hack{E,R}: not one +mult/+chips/xMult joker. The whole run was
base-level flushes (L1 35x4) plus Red Card +6 mult, ~500 per hand vs a 1500 Big Blind (and The Wall 4000 behind it).

Decisions I would change:
1. Ante 1 shop 2 ($6): I left with $6 to "save for a real scorer". The ante-2 shops then offered no scorer at all, and I
   ended up taking an ETERNAL Red Card from a pack anyway. The non-eternal Red Card $5 there plus the ante-2 packs bought to
   skip ($4 = +3 mult each) would have been ~+3-6 mult more by the ante-2 Big (Two Pair 448 -> ~600, flush 525 -> ~700).
2. Ante 2 shop 1 ($13): I spent $4 on a Spectral pack (skipped, +3 mult). A $5 reroll for a $4-5 scorer was the other
   option; with zero scorers a reroll that shows 2 jokers was probably better than a pack whose only value was the skip.
3. Ante 2 Big: the solver (n=100) told me to break a made Two Pair JJ66 (416) holding JD TS 9D; the next 8 cards were junk.
   With n=100 and the alternatives within 0.06, keeping the 416 floor was equally good; no clear mistake but worth noting.

Reusable rules (if-then):
- IF you own Red Card and a $4 pack offers nothing that scores now, THEN buy and skip it: +3 mult permanently for $4 is
  the cheapest scaling in an ante-1/2 shop without scoring jokers (flush 35x4 -> 35x10 after two skips).
- IF a Spectral/Standard pack shows only Ankh/Aura/plain-ish cards while Red Card is owned, THEN skip it for the +3.
- IF you own 0 scoring jokers after the ante-1 Big Blind, THEN spend the shop money on any non-eternal mult source now
  (Red Card, a +mult joker): saving $6 for interest bought nothing because the next two shops had no scorer either.
- IF a Golden Joker{PERISHABLE,RENTAL} is offered in a pack with free slots, THEN taking it nets +$1 per round (+$4 vs -$3
  rent) until it perishes; sell it the round it perishes (a perished rental still charges rent).

Advisor/CLI defects:
- shopadvise (3 shops) said `ADVICE: SELL -> b sell 1` for Golden Joker{PERISHABLE,RENTAL}: "costs $3 every round ... about
  $60-66 if kept to the end". It ignores Golden's +$4 per round (net +$1) and that it perishes after 5 rounds; correct
  advice is keep until it perishes, then sell.
- Pack advise said SKIP for Golden Joker{PERISH,RENTAL} vs Swashbuckler{ETERNAL} with 6 free slots and $0; Golden paid +$3
  net over 3 rounds. Same missing income term.
- shopadvise SIM printed p_next 0.00 for every option (baseline included) at ante 1-2, so it gave no ranking signal.
- Small skip advice at ante 2 (Handy Tag, $1 per hand played = $7 now) said "not worth a shop visit"; probably right here,
  but the Handy/Garbage tags' immediate cash value is not shown.
Bridge issues: none; 41 steps, no rejects.
