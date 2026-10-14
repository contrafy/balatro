# Run DTAAHW9T (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 Big Blind (1113/1500)

Ante 1 (Investment/Uncommon/The Club 600, $4): Small 300: Straight 10-high 280 + Trips 333 117. Shop $5: Ramen{PERISHABLE} $6 unaffordable by $1; Buffoon pack $4 -> only Certificate{ETERNAL} / Supernova{RENTAL}: took Supernova ($1 left). Big 450: kept JJ22, drew TTT -> Full House TTTJJ 450 exactly (Supernova +mult = plays of that type, est exact). Rent put me at -$2, cash-out $4. Shop $4: Onyx Agate $7 (+7 mult/club) unaffordable; Mega packs $8; left. Club 600: Two Pair 144, then A-K-Q-J-T straight (AC debuffed) 420, Full House 408 = clear.
Ante 2 (Garbage/Juggle/The Fish 2000, $6): SCORE CHECK 0.13 EMERGENCY, shop had only Runner $5 (+15 chips/Straight), Splash rental, Arcana $4, Jumbo Celestial $6. Bought Jumbo Celestial -> Earth (Full House L2 65x6) ($0 left). Skipped Small 1000 (rent-broke, est ~765/round; Garbage tag +$2). Big 1500: disc to QQ, got KKQQ+flush; dug with junk High Card 30 keeping KKQQ, drew QQQKK Full House 1035, last hand 8 junk cards (no pair), best High Card 48 -> 1113/1500.

## Post-mortem

Binding constraint: Supernova (+1 mult per play of a hand type) was my only scorer for two antes; with ~$0-6 and a $3/round rent I never afforded a second joker (Onyx Agate $7 and Ramen $6 were each 1-3 dollars out of reach at the exact shop that showed them). A jokerless-ish ante 2 needs ~750 per hand; I made 300-420 hands except when a Full House landed.

Decisions I would change:
1. Ante 1 shop 1: I had $5 and Ramen was $6 (1 short). The $4 Buffoon pack gave a rental Supernova as the only scorer; rent then charged $3 at the Big round-end, so the second shop had $4 (Onyx Agate $7 out of reach). A rental bought with $1 left makes every later shop $3 poorer.
2. Ante 2 shop: I spent $6 on a Jumbo Celestial (Earth, +25% on FH only). A Full House appeared twice in the Big and carried 1035, but I still missed the last 435 with 8 non-pair cards. Alternative Runner ($5) would not have changed it either.
3. Big 1500: after KKQQ appeared with a diamond flush (KD QD TD 6D 5D est 380), I dug for FH. That worked (1035), but the last hand had no discards to fix a junk draw. Keeping one discard for the last hand (by not discarding 5 cards on the first discard) was impossible with 2 discards used before the dig.

Reusable rules (if-then):
- IF the only scorer you can get at ante 1 is a rental and buying it leaves <= $1, THEN expect to afford only $4 items in the next shop (rent $3/round); a skipped Small saves one rent tick.
- IF Supernova is your scorer, THEN commit to ONE hand type every play so its +mult grows by 1 per play; do not alternate types (my Straight/Trips/FH/Two Pair spread gave only +1..+3).
- IF a shop shows a +mult joker you are $1-3 short of and you hold a rental, THEN selling the rental ($1) rarely closes the gap; avoid taking a $4 pack that can only yield a rental when it leaves you under $3.

Advisor/CLI defects:
- `advise` at the Big (hand 3, 0 discards, KKQQ + flush) gave solver p 0.03-0.04 for every option and recommended Flush 380; the dig-for-FH line actually produced 1035. No defect, just low p.
- shopadvise said LEAVE at ante 1 shop 2 ($4, Onyx Agate $7): correct; but it did not suggest selling Supernova (+$1) nor rerolling; neither would have reached $7.
