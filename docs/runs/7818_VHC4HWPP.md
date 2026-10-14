# Run VHC4HWPP (port 7818, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (4800)

- Ante 1: Small 300 won (Full House 264 + Two Pair 116). Shop: $5, bought Buffoon pack, took Ice Cream (rental+perishable, +100 chips). Left shop at $1 (advisor Celestial and second rental Vampire refused). Big 450 won with Flush 696. Boss The Goad 600 won with Trips 399 + Pair 224. Ended ante 1 with $4 and 1 joker (Ice Cream).
- Ante 2: Shop at $7: bought The Idol (only xMult, x2 per matching card) to $1. Skipped Small 1000 for Meteor tag (Mega Celestial: took Venus, Jupiter). Big 1500 won with Straight 1328 + Two Pair 256. Shop at $3: left (nothing affordable). Boss The Psychic 2000 won with Trips 655 (set-up L2), Flush 924, Flush 930 (1579 + 930 = 2509).
- Ante 3: Shop at $5: Arcana pack, Judgement -> Scholar (+4 mult per Ace), $1 left. Skipped Small 3200 for Double Tag (no round end, perish/rent avoided). Big 4800: 0 jokers that score on my hands; Flush/Straight draws failed. Plays: 75, 1899 (flush), 2329 total at the final hand. LOSS at Big Blind 4800 (scored 2329).

## Post-mortem

**Binding constraint:** Score scaling. At ante 2 the run had 2 jokers, neither a reliable scorer (Ice Cream was a perishable chips bridge, Idol was conditional xMult with a 5-round perish). No xMult stayed alive into ante 3 (The Idol perished, Ice Cream perished). Ante 3 Big 4800 needed ~2x what the hand could reach with one Ace-only +4 mult joker. The run never had a second scaling source: money stayed at $1-$7 after every shop, so no buys beyond one joker per shop.

**Decisions I would change:**
1. Ante 1 shop: I bought Ice Cream (rental+perishable) as the only scorer on offer. It cost $3 per round and perished at ante 2 with no replacement bought. Better: take the Ice Cream only if the next shop is expected to have a $4-5 permanent scorer; otherwise leave the pack with $5 to buy a shop scorer.
2. Ante 2 shop at $7: buying The Idol left $1. The next shop saw $3 and could buy nothing. Better: keep $4+ so the Idol-like xMult and a permanent $4 joker can both be bought within 1 shop.
3. Ante 2 Small 1000 skip for a Meteor tag was fine for money (no rent tick) but it also removed a round that could have banked score. Acceptable.
4. Ante 3 Small 3200 skip for Double Tag: no round end means no rent/perish tick, which is good; but it left Big 4800 with zero permanent scorers. The fix is upstream: no skip without a permanent scorer alive.

**Concrete reusable rules (if-then):**
- If the shop offers only a perishable or rental scorer at ante 1 with $5, buy it only if you can still keep $4 for the next shop; otherwise prefer a permanent $3-4 joker or leave.
- If you hold 1 scoring joker entering ante 2 and it perishes before ante 3, then at ante 2 shop buy the cheapest PERMANENT scorer and keep $4 afterwards; do not spend to $1 on a conditional xMult that perishes in 5 rounds.
- If the Big blind after a skip is 4800 at ante 3 and you own no permanent scorer, do not skip the Small: a skip only helps when it pays a tag you will still use.
- If the solver says p <= 0.10 for a Big/Boss and the hand is High Card-only, the run is effectively lost: spend the remaining shop money before the next blind, not after.

**Advisor / CLI defects observed:**
- shopadvise at ante 1 ($4 with Ice Cream held) ranked Celestial Pack 15 with "value 0.27 vs 0.14"; after taking the pack the simulated scorer count still said 1 scorer, which made the rule "no planets at 1 scorer" conflict with the SIM. The rule line should win when the scorer is perishing.
- advise at Psychic boss: `play` must be exactly 5 cards; the advice line included fillers. Correct, but the hand list shows 8 cards so a weak model may type 3 cards and get refused. Consider printing "need exactly 5" in the state line.
- `discard` is not a command (only `disc`); the error listed commands but the advisor text used "DISCARD -> b disc ..." so the mismatch cost one round-trip.
- Ice Cream displayed "PERISHED: scores nothing" only at GAME_OVER; the state line at ROUND_EVAL still showed PERISHABLE(1 rounds left). Minor.
- Idol's "(this round: 10 of Spades)" changes each round; the SIM did not model the per-round rank change, so Idol was valued too high at ante 2.
