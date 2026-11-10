# Run F4VCTBZQ (port 7818, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The House (boss, 2948/6400)

## Per-ante lines
- Ante 1: Small 300 and Big 450 cleared, Boss The Pillar 600 cleared. Shop 1: Buffoon pack, took Cartomancer (Loyalty Card barred as ETERNAL+RENTAL). Shop 2: sold Cartomancer, bought Green Joker{ETERNAL} (+1 mult/hand).
- Ante 2: Small 1000 (Pair 9s, then Straight 3-7 for 1100) and Big 1500 (Straight 4-8 1260, then Three Aces 567) cleared. Bought Crazy Joker{ETERNAL} (+12 mult on Straight) per ADVICE. Buffoon pack gave Acrobat{RENTAL} (x3 on final hand, my one allowed xMult rental). Boss The Wheel 2000 cleared on the final hand (Two Pair 504, then Jack Pair with discards; Heart Flush 2541 with Acrobat x3). Cash $5.
- Ante 3: Small 3200 cleared (Two Pair 480, then Straight 4125 on final hand with Acrobat x3). Big 4800 cleared on the final hand (Straight 6-10 est 5460 with Acrobat x3, 3 discards used, $3 after rent). Boss The House 6400 LOST: scored 682 (Two Pair AQ), 2372 (Straight 5-9), 2948 (High Card final hand); cash $3.

## Post-mortem

**Result:** Loss on The House (ante 3, boss, 2948/6400). Shop 3 (before the Big blind) had $2-$3, nothing affordable. Jokers: Green Joker{ETERNAL}, Crazy Joker{ETERNAL}, Acrobat{RENTAL}. Only 3 jokers, no xMult besides Acrobat, no scaling chips/mult beyond Green Joker's +1 per hand.

**Binding constraint:** economy plus scoring. Money sat at $2-$5 from ante 2 onward, so no shop could buy scorers, and Acrobat rent ($3/round) drained the rest. Scoring stayed on Straight/Two Pair/Pair at roughly 1-5k per round, far below the ante-3 boss target of 6400 and the ante-4 target of 9000.

**Decisions I would change:**
1. Ante 2-3 cash: I spent $4 on Crazy Joker (ETERNAL, conditional on Straight) at $8 cash, then had almost no money for the next 3 shops. Prefer the unconditional scorer or keep $8 when a conditional is the only option.
2. Buffoon pack Acrobat at ante 2 cost $3/round for the rest of the run. Its x3 carried the ante-2 and ante-3 final hands, but it made every later shop unaffordable. Under the one-xMult-rental rule it was allowed; I would still weigh it against rent per round.
3. The House (ante 3 boss) requires 6400 and hides cards face down. The mid-hand discards were spent blind. With 3 jokers and no scaling xMult, the boss was not beatable on the draws I got.

**Reusable rules (if-then):**
- If your shop money is under $5 at ante 2 with fewer than 4 jokers, then do not buy conditional or ETERNAL scorers that consume the last $4; keep cash for the xMult or scorer shop next ante.
- If you hold an xMult rental (Acrobat-type) with rent $3/round, then count its rent in your floor: money after each round-end must stay at least $8 before buying a conditional joker.
- If the boss is The House (face-down cards), then discard face-down cards only when the advisor's visible hand estimates are below the target; the advisor's "keep 3 highest" discard already draws visible cards.
- If the advisor's SCORE CHECK ratio is below 0.9 at the boss (e.g., 0.82 here), then the run needs an xMult or a planet before the boss, not a conditional joker.

**Advisor / CLI defects:**
- The Straight 5-9 hand scored 2372 vs est 1690 (large underestimate); the final-hand estimate for High Card AS (est 576) scored 2948 total, so both were underestimated, which flattered the lines and misstated the pace.
- The advisor listed "PLAY 1 2 5" at solver p 0.29 above the advised Straight at p 0.12 for the House second hand, but kept the rule pick under its own low-confidence switch rule (lead 0.17 < 0.20). The advised line lost the chance to bank the dig; the top-listed line is the better reading of the playbook rule.
- For The House, the advisor's SOLVER lines all showed p < 0.5 on the first hand, and the advised discards carried the blind into an UNWINNABLE final hand with no visible path; this is correct but gives no early warning to change the shop plan.
