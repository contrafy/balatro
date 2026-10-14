# Run QLNFFQB1 (port 7814, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Small 3200

- Ante 1: Small 300 won (Two Pair then Flush 416; overrode advisor disc 1 4 6 8 that broke pair 66 at margin +0.00). Shop $5: bought Droll Joker (perishable, rental, +10 mult on Flush; the one allowed rental). Declined Buffoon at $4 (would leave $0 before rent).
- Ante 1: Big 450 won (Flush QC TC 9C 6C 4C est 1036). Shop $7: bought Square Joker $4 (advisor ADVICE, chips-only). Left $3.
- Ante 1: Boss The Club 600 won (clubs debuffed; discarded to hearts; heart Flush AH JH 9H 3H 2H est 980).
- Ante 2: Small 1000 won (Diamond Flush AD KD JD 8D 5D est 1106 after kept-pair overrides). Shop $7 (EMERGENCY/TIGHT, floor off): Arcana pack $4, took Temperance; left $6.
- Ante 2: Big 1500 won (Two Pair kept, dig to heart Flush AH KH QH 6H 4H est 2240). Money went to -2 at round end from Droll rent before payout. Shop $5: bought Crafty Joker (+80 chips on Flush, perishable) over advisor's Clever Joker (SIM 0.74 vs 0.58). Left $2.
- Ante 2: Boss The Arm 2000 won (heart Flush QH 9H 7H 3H 2H est 2100 vs 2000, after pair-keep discard override). Droll perished at boss end.
- Ante 3: Shop $7. Sold perished Droll ($1). Reroll $5: Hanging Chad (eternal, $4) / To Do List ($4), both unaffordable at $2. Left at $2 with no shop scorer.
- Ante 3: Small Blind 3200 LOST. Hand 1 (AS TH TC 9D 8S 5C 4H 2D): discarded for pair TT, no useful draw. Hand 2: Full House TTT22 kept (disc JD 8D 4C), then Full House TTT33 est 320. Hand 3: Two Pair est 88 (scored 88, total 408). Hand 4: Straight est 356 (total 764). GAME_OVER with 764 of 3200.

## Post-mortem

**Binding constraint:** Money and scorers collapsed at the ante 2 to 3 boundary. Droll (rental, -$3/round) drained cash during ante 2 (money fell to -2 and -1 at round ends), so I could not buy a permanent scorer at ante 2's last shop ($2 after the Crafty buy). From ante 3 I had only Crafty (perishable, 3 rounds) and Square (+4 chips), with no xMult or +mult. The 3200 Small needed ~10x the score my build could make in 4 hands (best made hands ~320-410).

**Decisions I would change:**
1. Ante 2 shop at $5: I bought Crafty (+80 chips, perishable 5 rounds) over the advisor's Clever (eternal, +80 chips on Two Pair). Crafty perished before ante 3 and left me with no scorer. Clever would have stayed. Prefer the eternal scorer when the two are close in SIM.
2. Ante 2 Big Blind: spending $3 on the Arcana pack at $7 (floor off) left me at $6 instead of keeping cash for a $4 joker next shop. The Temperance pick gave only ~$3 back. Do not take a pack at ante 2 with 1 scorer unless it adds a scorer.
3. Ante 1: I bought Droll (rental, -$3/round). It drained more money than it scored. Under the Gold rule it was legal (one rental before ante 5), but the rent cost was the reason I could not afford ante 2-3 jokers. Prefer Square/Crafty-type non-rentals at $5.

**Concrete reusable rules (if-then):**
- If you own a rental joker and money is under $8, then sell or ignore the rental before buying a $4 scorer; rent costs ~$9/ante.
- If a perishable scorer is the only scorer, then buy an eternal scorer of equal value before ante 3 (perishables leave you with 0 scorers).
- If the next blind needs >5x your best made hand, then take a flush/full-house draw line, but expect a loss; do not spend the last $2 on the reroll (reroll $5 showed no affordable scorer).
- If the advisor's SIM says a blind is UNWINNABLE, then the run is effectively lost; still play it out, but flag the earlier shop decisions as the cause.

**Advisor / CLI defects:**
- Shop ADVICE "Clever Joker" at ante 2 ($5) lost to Crafty in SIM (0.74 vs 0.58) but was still ADVICE; the advisor did not reconcile eternal vs perishable durability in its ranking.
- Advise at Small Blind (ante 1) suggested disc 1 4 6 8 that broke pair 66 at solver margin +0.00; the rule pick kept pair (correct), but the ADVICE line did not match the "keep made pair" rule.
- Pace line "discard toward a bigger hand" kept firing when made hands (112, 320) could not clear, while the solver said p 0.00 for every line at ante 3 Small. Ante 3 advise gave ADVICE lines that the solver marked UNWINNABLE with no alternative, which is not actionable.
- Shop advisor at ante 3 said "SELL FIRST ... then reroll" and the reroll revealed only $4 jokers, so the advice assumed money that did not exist after the sell.
