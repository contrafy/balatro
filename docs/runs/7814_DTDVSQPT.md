# Run DTDVSQPT (port 7814, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Wall (36000)

Ante 1 (Small 300 / Big 450 / Goad 600): cleared all three. Bought Raised Fist ($5) and Jolly Joker ($3). Declined Blackboard (second rental) and Buffoon at $4.
Ante 2 (Small 1000 / Big 1500 / Club 2000): cleared all three with Pair/Two Pair/Trips. Bought Wily Joker ETERNAL $4 (overrode advisor Ice Cream, decaying rental). Jumbo Celestial $6 -> Earth (no Mercury). Declined Vampire (x1 with 0 enhanced cards).
Ante 3 (Small 3200 / Big 4800 / The Mark 6400): Grabber voucher $10 (+1 hand). Small cleared with Two Pair/Pair chain. Bought Mr. Bones $5 (run-saver, SIM +0.21 vs Shoot the Moon +0.12). Big 4800 cleared with Full House AAA88 (est 6848). Bought Brainstorm $10 copying leftmost Raised Fist. The Mark 6400 LOST (face cards face-down; scored 2374 + 1320 final Two Pair). Mr. Bones fired at 25% of blind and was consumed; run survived.
Ante 4 (Small 9000 / Big 13500 / The Wall 36000): Shop at $1: LEAVE. Small 9000 cleared (8562 after Trips 9s, then Pair KK + fillers est 1140 for the last 438). Shop at $2: LEAVE (advisor; Jupiter $3 unaffordable, Shoot the Moon banned as ETERNAL+RENTAL before ante 7). Reordered jokers (Wily leftmost so Brainstorm copies +100 chips on Trips). Big 13500 cleared (Trips 5s est 7105, then Trips 9s est 7967 with 1 discard left). Shop at $8: bought Smiley Face (only rental, SIM 0.35 vs 0.29) and Jumbo Arcana $6 -> Empress (+4 mult on 2 cards). Left at $1. The Wall 36000 LOST: best hand Pair/Flush est ~1000, scored 2896 in 4 hands. GAME_OVER.

## Post-mortem

**Binding constraint:** Scoring power at ante 4. Build had 0 xMult (Raised Fist and Brainstorm copies are the only multiplicative effects; Smiley Face and Empress are additive mult). Best hands were Pair/Trips/Full House at est 500-8000 on Small/Big, but The Wall (36000) needs ~4x the Big. Money was $1-$2 for most of ante 4, so no xMult could be afforded in the shop before The Wall. Score ratio vs The Wall was 0.21-0.27 at shop time.

**Decisions I would change:**
- Ante 3 Grabber voucher ($10) gave +1 hand but no scoring. Spending $10 on a scorer or xMult (or saving for one) would have left more money for ante 4 shops. Rule: at ante 3, if no xMult owned, prefer xMult/scorer over +1 hand voucher.
- Ante 3 Brainstorm ($10) copying Raised Fist gave little beyond Raised Fist itself. Rule: buy Brainstorm only when the leftmost joker is a strong xMult.
- Ante 4 shops at $1-$2 were forced LEAVE. The Small-blind clear used the last of the reserve. Rule: enter ante 4 with at least $8 spare or one xMult already owned.
- The Mark (ante 3) cost the Mr. Bones save and a full-blind loss. The face-down rule is punishing: when The Mark is the boss, buy a Mark counter or skip into a high-chip build before the boss.

**Concrete reusable rules:**
- If you own 0 xMult jokers at ante 4 and The Wall is the boss, the run is already at ratio < 0.3; expect a loss unless a rare xMult is found. Buy the cheapest xMult in every shop from ante 3 onward.
- If Mr. Bones is owned and the boss is The Mark, expect it to fire at 25% of blind; do not rely on it to clear the blind.
- If a rental is the only option and no rental is owned, buying one rental before ante 5 is allowed; don't use it as a substitute for an xMult.
- Reorder jokers only when the advisor's ORDER line measures a round-est gain.

**Advisor / CLI defects:**
- Recommended Wrathful Joker rental at ante 3 (SIM -0.02 to +0.03).
- Recommended Vampire (x1, no enhanced cards) with neutral SIM at ante 2.
- Rule advice recommended Ice Cream (decaying perishable rental) over Wily Joker at ante 2.
- `advise` est can differ sharply from `sel` preview (TWOPAIR est 350 vs 770); check `sel` when suspicious.
- The Mark: advisor's face-down "guaranteed pair" est (~1260) was far below the 6400 need, but the advice still recommended playing out.
- The Wall: solver reports UNWINNABLE from the start (p 0.11 at best), yet the shop advisor kept recommending BUY/LEAVE with no xMult counter-plan shown beyond "buy Luchador/Chicot/Mr. Bones/Director's Cut".
- `order` (reorder jokers) is not in the free-command list but is accepted and recorded; the ORDER line est (19840 -> 21840) was accurate in direction.
