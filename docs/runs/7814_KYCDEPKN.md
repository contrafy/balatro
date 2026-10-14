# Run KYCDEPKN (port 7814, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Small (2929/3200)

## Per-ante log
- Ante 1: Small 300 cleared (Two Pair finish). Shop: Abstract Joker{ETERNAL} $4. Big 450 cleared (Flush). Shop: Hanging Chad{PERISHABLE,RENTAL} $1. Boss The Head 600 cleared (Two Pair, then Flush). Left at $8.
- Ante 2: Shop: swapped Hanging Chad for Fibonacci{RENTAL} $1. Small 1000 cleared (Straight). Big 1500 cleared (Two Pair, then Pair). Declined Riff-raff, Crazy Joker, Celestial. Boss The Mouth 2000 cleared: Flush locked type, Flush 1898 then Flush 1638. Left at $11 after cash-out to $15.
- Ante 3: Shop at $15: bought Director's Cut voucher $10, leaving $5 (could not afford the $10 Wall reroll). Small 3200 failed: High Card and Two Pair draws only; a late Flush hit 2689 with 1 hand left, then 240 on the final hand = 2929. Game over.

## Binding constraint
- Score scaling. The jokers held (Abstract ETERNAL +3 mult per joker, Fibonacci rental) never built past about 1500 per hand. Ante 3 Small 3200 needs about 2x the best hand. A Flush-main build at 1.5-2k/hand could not keep pace with the 3200 / 4800 / 12800 ladder.
- Economy. With only 2 jokers and a $3/round rental drain, cash was $5-$15 across ante 2-3. There was no spare money to buy a multiplier.

## Decisions I would change
1. Director's Cut purchase at ante 3 ($15 -> $5). The $10 boss reroll had to be afforded at the boss blind select, and the purchase left $5. The reroll was therefore unusable, and the $10 spent was dead money. Better: keep $10 for the reroll, or do not buy the voucher unless $10 remains after the buy.
2. Ante 2 floor-holding at $8-$11. Holding cash over a 1000-2000 scaling ladder meant no xMult or main-hand planet was ever bought. The 3200 Small at ante 3 then could not be cleared.
3. Two rentals early (Hanging Chad, Fibonacci) cost $3/round and produced little.
4. Main-hand build was Flush by accident (draws). At ante 3 the shopadvise BUILD line said to shift to Pair/Two Pair/Trips, but I had no Pair-family joker to build toward.

## If-then rules
- If the boss reroll voucher (Director's Cut) costs $10 and you hold less than $20 at the shop, then do NOT buy it: you will not afford the reroll at blind select.
- If the next ante's Small blind is more than 2x your best hand and you hold 0 xMult, then take the highest-ranked multiplier the shop offers, even below the money floor, before the Small blind.
- If The Mouth boss is up and your first played hand locks the type, then lock a type that scores in a single hand (Flush at 1638+) rather than a pair (240). Pair lock = certain loss at ante 2+.
- If a rental costs $3/round and is not in your top-2 scorers by ante 2, then sell it instead of holding it.
- If the Small blind is 3200+ and your best hand is under 1500, then expect a loss unless a reroll or xMult is affordable this shop.

## Advisor / CLI defects
- shopadvise (ante 3, $15): ranked Director's Cut as BUY "keep $10 for rerollboss" while the purchase left $5. The advice did not check that the reroll was affordable after the buy. Example: "BUY -> b vouch 1" at $15, then "keep $10 for rerollboss" at $5.
- shopadvise (ante 2): BUY Riff-raff $6 and BUY Crazy Joker $4 while the header said "money floor $8". The floor rule and BUY advice conflicted.
- blind select ADVICE (ante 2, Small 1000): recommended Economy Tag skip ($8 money). Playbook only allows Small skips at ante 1 for joker/pack tags.
- advise (Mouth boss): correctly identified the one-type lock and the flush route. Estimated 1898 for a Flush at ante 2 turned out accurate (scored 1898), so the hand estimates were reliable.
- advise (Small 3200): the last hand's estimate (240) was correct; the run was lost by the scoring gap, not by estimate error.

## Bridge
- No offline events or timeouts. Commands ran about 1-13 s each. No illegal-action refusals.

## Playbook suggestions
- Add: "Director's Cut costs $10 plus a reroll of $10 at boss select: count it as $20 of commitment before buying."
- Add: "Mouth boss: lock a single-hand Flush/Straight if available; never lock a Pair-type to clear 2000 with 3 hands."
- Add: "At ante 3 with best hand under 1500 and no xMult held, skipping money-floor rules to buy the one multiplier is the only path (Gold ante 3 Small 3200)."
