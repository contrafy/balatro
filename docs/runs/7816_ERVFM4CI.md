# Run ERVFM4CI (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Arm (894/2000)

Ante 1 (Rare/Double/The Window 600, $4): Small: dealt Flush QJ765H 292 + High AD 16 = 308/300. Shop $5: The Idol $6 / Jupiter / Buffoon pack $4 -> bought the pack ($1 left): Chaos the Clown vs Photograph{RENTAL}; took Photograph (only scorer). Big 450: two discards for AS KS JS flush (missed), Two Pair AAKK 248 + High 30 + Two Pair JJ33 184 = 462/450 (rent took me to $-2, $2 after cash out). Shop $2: Joker Stencil $8 (x5!), Devious $4, Jumbo Buffoon $6, nothing affordable. Window (diamonds debuffed): 2 discards for flush (missed), junk dig, Straight K-9 552 (KD debuffed), Two Pair QQ77 176 = 733/600. Cash $4.
Ante 2 (Skip/Investment/The Arm 2000, $4): SCORE CHECK 0.11 EMERGENCY. Shop: Celestial pack $4 -> Saturn (Straight L2). Rent made money $0. Skipped Small (Skip Tag +$5, no rent) and Big (Investment tag $25 after boss) to fight only the Arm. Arm: discard x2 for straight, dig play, Flush KS 584, Straight at L1 280 (Arm lowers the level BEFORE scoring and permanently) = 894/2000. LOSS.

## Post-mortem

Binding constraint: zero scoring jokers at ante 1-2 (Photograph alone is x2 on a face with base mult 2-4, so it adds nothing to non-face hands) and money $0-5 the whole run. Photograph{RENTAL} cost -$3/round on a $1-5 wallet, so every shop had $2-4 and Stencil ($8, x5 with 5 empty slots), Devious ($4) and the Jumbo Buffoon ($6) were all out of reach. Then The Arm at 2000 with a build whose only 500+ hands are 5-card flush/straight.

Decisions I would change:
1. Ante 1 shop 1 ($5): Buffoon pack with a rental Photograph in it. With $5 I could have bought The Idol ($6, no) - the real alternative was keeping $5 and taking Chaos the Clown (free utility, no rent), reaching ante-1 shop 2 with $5+3 = ~$8 for Joker Stencil x5 (it would have been x5 with an empty board: 300-600 hands). Rule: a rental scorer whose rent exceeds the income of the next 2 rounds leaves you unable to buy the better joker you will see next shop.
2. Ante 2 shop ($4): Saturn (Straight L2) was wasted by The Arm (L2 played as L1, level lost). Hindsight: The Arm was shown in the shop; I should have sold Photograph ($1, stop rent) + kept $5 for a reroll to look for a $4 scorer, or simply not bought a level for a hand the boss resets. The score check said EMERGENCY (0.11); a planet cannot fix that.
3. Skipping both blinds at ante 2 was right given the numbers (no rent, +$5 now, +$25 later), but it left only the boss with no jokers; it couldn't change the outcome.

Reusable rules (if-then):
- IF the only joker you can get at ante 1 is a rental xMult that needs faces (Photograph) and you have <$6, THEN prefer a free non-rental joker or keep cash: a face-gated x2 on mult 2-4 gives ~+30-60 per hand, less than the $3/round it costs.
- IF the boss is The Arm, THEN played hand types score at one level lower and lose that level permanently; Straight L2 est 280 not 700. Do not buy planets for the types you will play at The Arm.
- IF Joker Stencil is in the shop with 0-1 jokers owned (x5-x6 mult), THEN it is the best flat multiplier available; hold $8 for it (a reroll/pack bought one shop earlier made me miss it by $6).
- IF rent drives money negative at round end (state showed $-2 / $-1), THEN the shop after cash out has only ~$2-4: skip the next $0 Small to avoid a round of rent.

Advisor/CLI defects:
- Pack advice scored Photograph{RENTAL} +100% round est and "NEEDED NOW" without modeling that rent would block the Stencil buy one shop later ($2 vs $8).
- shopadvise at the Arm shop bought a Celestial pack (Saturn) for Straight although The Arm's -1 level cancels the new level for that boss; the pick text said "NOT your main hand" correctly but ADVICE was still BUY.
- Solver p 0.98/0.99 at ante 1 Window/Big was optimistic: 3 of 4 draws missed; the rule pick and solver tied but solver p values were not close to the realized hit rate.
