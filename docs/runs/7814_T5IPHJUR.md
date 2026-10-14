# Run T5IPHJUR (port 7814, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Small 1000

## Ante log
- Ante 1 Small 300: WON. Discard 1 toward flush, then Flush 5 clubs est 276, then Two Pair 88 to clear. Cash $4 -> $5.
- Ante 1 shop: bought Droll Joker ($4, +10 mult if Flush). $1 left. Left shop.
- Ante 1 Big 450: WON with Flush (est 1008, Droll included). Cash $1 -> $7.
- Ante 1 shop: bought Banner (rental, +30 chips per discard left) for $1 (the one rental allowed). Opened Celestial pack for $4, took Jupiter (Flush L2). Left with $2.
- Ante 1 Boss The Club 600: WON over 3 hands (Two Pair 232 with 7C debuffed, Two Pair 198, Three Kings 330). Banner rent took money to $-1 at round end. Cash out -> $4.
- Ante 2 shop: $4, nothing affordable worth buying (Gluttonous $5, Misprint would be a second rental). Left at $4.
- Ante 2 Small 1000: LOST. Hand was Pair/Two Pair only (est 184 at best, no 5th diamond). Discarded to draw toward a diamond flush, the flush never came. Scored 163 total. Run over.

## Post-mortem

**Binding constraint:** Ante 2 Small Blind (1000) needed a real scorer. I had two jokers, one of them a flush-only +10 mult (Droll) and the other a +30 chips per discard rental (Banner). The Pair/Two Pair hands from this deck scored est 120-240 each, so 1000 in three hands was out of reach. No xMult was bought by end of ante 1 or 2 (GOLD CHECK target: 1 xMult by end of ante 2; I had 0).

**Decisions I would change:**
1. Ante 1 shop, $7: Banner rental + Celestial pack ($4) left $2. That $4 was the only money that could have bought the ante-2 scorer (Gluttonous $5 eternal was passed at $4). Better: skip the Celestial pack, keep $6-7 for the next shop.
2. Banner rent at $2: rent (-$3) took money to $-1 with no income until the boss reward. When a rental would push money negative, sell it first (or sell Banner the moment money is below $3 and no scorer is buying).
3. Ante 1 Droll pick: flush-only +mult was the first joker. Flush was my only big hand in ante 1 and it was also the main hand, but Flush-main runs die early at Gold (advisor BUILD line). Consider Pair-family jokers first when offered at similar cost.
4. Ante 2 shop: SCORE CHECK said EMERGENCY (ratio 0.16, buy cheapest multiplier through the money floor), yet ADVICE said LEAVE and passed Misprint (rental). With a rental already owned, the only non-rental xMult/mult option was Gluttonous at $5, and I had $4. The lesson is about money, not the emergency rule.

**Concrete if-then rules (for weaker models):**
- If you buy a rental (Banner/Stencil/Misprint) and money would drop below $3, sell the rental before round end or do not buy it.
- If the next blind is 2x the current one (ante 1 boss 600 -> ante 2 small 1000), you need 2 scorers or an xMult before leaving ante 1; Droll + Banner is not enough.
- If your main hand is Flush and the deck has fewer than 5 cards of one suit left in hand, do not plan a flush draw for the final hand; take the best Pair/Two Pair line.
- If the advisor says LEAVE with EMERGENCY SCORE CHECK, spend the money you have on the cheapest non-rental multiplier, even a pack, before ending the shop.
- If two scorers exist and money is under $5 after a rental, do not open a planet pack (it removed my only $4 for the ante-2 joker).

**Advisor/CLI defects:**
- Solver p 0.95 (calibrated) for "PAIR AS AC est 64" vs need 1000 at ante 2 Small; the solver's clear probability is inconsistent with the est (p should be near 0). The "PLAY HIGH 1 4 5 8" advice showed p 0.72 vs est 15 and need 936.
- Shopadvise showed SCORE CHECK EMERGENCY and then ADVICE: LEAVE; the two lines disagree on whether to spend.
- Banner rent drove money negative ($-1) with no warning in the blind-select or shop state; the sell-to-stop-rent option only appeared as a SIM line.
