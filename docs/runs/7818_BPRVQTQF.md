# Run BPRVQTQF (port 7818, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Wall (boss)

- Ante 1: Small 300 won (Straight). Bought Mad Joker{ETERNAL} $4 (+10 mult on Two Pair). Declined Gros Michel{PERISHABLE,RENTAL} $1 (first-buy rule). Big 450 won (Two Pair). Boss The Manacle 600 won (Two Pair).
- Ante 2: Shop had no scorer, rerolled once ($5). Bought Greedy Joker{holo} $8. Skipped Small 1000 for Skip Tag ($5). Big 1500 won (club flush + Two Pair). Bought Onyx Agate{ETERNAL} $7 (per ADVICE). Boss The Flint 2000 won (club flush after one discard).
- Ante 3: Shop $15, boss The Wall 12800. Bought Popcorn{PERISHABLE} $5 (EMERGENCY score check overrode ADVICE Golden Joker) and Golden Joker{PERISHABLE} $6. Small 3200 won (Two Pair 2450 + 2912). Bought The Duo{ETERNAL} $8 (x2 on Pair, SIM/ADVICE). Big 4800 won (Two Pair KK JJ 5760). Shop: Jumbo Celestial, took Earth (Uranus not offered), $5 kept. Boss The Wall 12800: hands 3 disc 2 with a flush/straight/pair plan, two discards and a High Card dig; final Full House 11936 < 12800. GAME_OVER.

## Post-mortem

**Binding constraint:** the Wall boss (12800) at ante 3, with only 6 joker slots filled by mostly chips-light or perishable scorers. Projected round was ~11159 (ratio 0.87) with 1 xMult alive; the Duo arrived too late (bought at $8 in the ante 3 small-blind shop), and Popcorn/Golden were perishing (3 rounds left at the Wall). The shortfall was about 864 points on the final hand.

**Decisions I would change:**
1. Spend the $8 on The Duo (x2 Pair) earlier, or keep money for it: in the ante 2 shop I bought Onyx Agate ($7) per ADVICE; The Duo was not visible until ante 3. Prefer the xMult over a second 7-mult Eternal when Pair/Two Pair is the main hand.
2. At the Wall, I discarded 2 times toward draws (solver 0.73 and 0.80) and then played a High Card dig twice (solver 0.55, then 0.13). The last two high-card digs (896 total) added almost nothing; the solver's dig probabilities were optimistic. When the solver's best p is below 0.20 with 2 hands left, play the best made hand instead (Two Pair 5640 was never reached).
3. Planets: I took Earth (Full House) after Uranus was missing; Full House was not my main hand (Two Pair). Venus was the rule fallback. Took the ADVICE/SIM line, which was not a good fit for the main hand.

**If-then rules:**
- If the next boss is >= 2.5x your best hand and you have 0 xMult, buy an xMult at the first chance even at $8 (money floor off), and stop buying pair-family flat-mult jokers.
- If you have 2 hands left and the solver's best dig p < 0.20 while a made hand scores more than 50% of need, play the made hand (do not dig with High Card).
- If Popcorn/Golden Joker has <= 3 rounds left before a boss, count them as dead for boss planning.

**Advisor/CLI defects:**
- ADVICE (Golden Joker) contradicted EMERGENCY score check and SIM (Popcorn) at ante 3 shop; the rule line and ADVICE line diverged.
- ADVICE suggested Gros Michel{PERISHABLE,RENTAL} at ante 1 with 1 scorer owned, contrary to the first-buy rule.
- The advisor labelled holo Greedy Joker as "suit-only", while holo gives an any-hand +10 mult; a rule ambiguity.
- Solver dig recommendations at the Wall (p 0.55 and 0.13 for High Card digs) did not hold; the dig outcomes were 896 total. Treat solver dig p as optimistic.
- Pack advice: "pick 3 (Earth)" was ADVICE while the rule line said Venus; the planet for the main hand was not in the pack, so this was a fallback choice.
