# Run 4ULAHSJL (port 7816, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Small (3200)

- Ante 1: Small 300 won (flush). Shop 1: bought Turtle Bean $6 (ADVICE; left $0). Big 450 won (straight 324 + full house 344). Shop 2: bought Half Joker $5. Boss The Head 600 won (pairs; hearts debuffed).
- Ante 2: Small 1000 won (trips + pair). Shop 4: Jumbo Buffoon, picked Scholar (perishable). Big 1500 won (trips + high). Shop $7: left (Midas Mask ETERNAL, Jupiter). Boss The Flint 2000 won: 850 + 850 + 525 pair (Flint halves base chips/mult). Turtle Bean expired.
- Ante 3: Shop $13: Arcana pack (Hermit $9 to $18), Director's Cut voucher ($10, ADVICE EMERGENCY), reroll ($5, nothing affordable: Popcorn $5 with $3 left). Small Blind 3200 LOST: Trips JJJ 1380, then Pair KK 660 path failed; dig play of 4 cards (Half Joker disabled at >3 cards) scored only 60. Final High Card 900. Scored 2340 of 3200 at GAME_OVER.

## Post-mortem

**Binding constraint:** Scoring power. Only 2 jokers (Half Joker +20 mult, Scholar perishable) and a Pair-level hand economy (all hands at L1) by ante 3. Ante 3 Small (3200) needed roughly 3x what the hand could produce with 3 hands and 2 discards. Ante 2 cleared only with an expiring Turtle Bean and a planet-free build. No xMult was ever acquired; the Gold check (0 xMult by ante 3) was failing from ante 2 onward.

**Decisions I would change:**
1. Turtle Bean at $6 (ante 1, shop 1) over Lusty Joker (perishable +3 mult per Heart). Turtle Bean is not a scorer. After it, I entered Big with $0 and no scorer. Prefer the scorer when the tier-1 "+mult" option is a close SIM call.
2. Shop 3 at ante 2 ($6): LEAVE was right (only rentals), but no fallback scorer was bought there either. A cheap scorer at $6 would have helped.
3. Ante 2 Flint: I played the Flint boss with a weak hand, then the final dig play was a 4-card play. The Half Joker only works on hands of 3 or fewer cards. The dig play cost ~600 points and lost the blind chance in ante 3, not ante 2. Do not play 4+ cards while Half Joker is the scorer.
4. Ante 3 shop with $13: Arcana pack (Hermit doubled money) followed by Director's Cut at $10 left $8 and then a reroll. Better: keep $13 and buy Drunkard $4 / Popcorn $5 (+20 mult, perishable) at once; both were available and affordable at the start of the shop. The Hermit route turned $9 into $18 but the advisor then spent it on a voucher with no scorer value.

**Concrete if-then rules:**
- If a Half Joker (or any "<=3 cards" joker) is owned, then the final/dig hand must be 3 or fewer cards. Do not add fillers to a dig play.
- If the blind needs more than 2x the best current hand over the remaining hands, then play the highest-est single hand (High Card AD est 900) only after confirming the solver p is not 0; otherwise the dig play is worse than the printed estimate.
- If the shop offers a perishable +mult joker (Popcorn $5) and you have $13 at ante 3 start, then buy it before any voucher or reroll.
- If you have 0 scorers after the boss, then buy the cheapest +mult joker before any Arcana/Hermit pack.

**Advisor/CLI defects:**
- DISCARD SOLVER and PLAY SOLVER lines showed "p >=0.99" for every line on the Flint and final-hand states, so the p values did not discriminate.
- The dig play `play PAIR 2 3 5 8` (4 cards) was recommended as a solver line with exp 1520, but Half Joker (<=3 cards) was ignored: it scored 60 instead of 660. The estimator does not model the "<=3 cards" condition on the played set.
- The `--why` I wrote for the ante 1 Big discard was inaccurate (said I kept the 7s; I actually discarded them). Keep --why aligned with the actual cards.
- `hands` once hit a 5 s ReadTimeout; `s` recovered it.
- ADVICE "pack 1 Arcana" at $13 ranked Arcana above Drunkard/Popcorn; the SIM showed Drunkard as the best-ratio option (0.69) and the advisor's EMERGENCY text said "buy the cheapest multiplier", which Arcana does not satisfy.
