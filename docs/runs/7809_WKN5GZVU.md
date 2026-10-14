# Run WKN5GZVU (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Small Blind (692/1000)

Ante 1 (Rare/Uncommon/The Manacle 600, $4): jokerless. Small: disc to Flush draw (solver 0.95 vs 0.81), Flush clubs 296 + Two Pair AATT 124 = cleared. Shop $5: offered Burnt Joker $8, Zany{ETERNAL} $4, Buffoon pack $4. Took Buffoon: Runner{ETERNAL} / Certificate only -> Certificate. Big 450: FH 336 + 2P 92 + Pair 40. Shop $5: Hiker{E,R} $1 (rejected), reroll $5 -> Raised Fist $5 appeared with only $0 (+$3 Certificate), unaffordable. Manacle 600 (7 cards): FH JJJQQ 400 + FH AAA22 316 = cleared.
Ante 2 (Economy/Juggle/The Mark 2000, $6 after boss): still ZERO scorers. EMERGENCY 0.08. Shop: Business Card{P,R}, To Do List{R}, no scorer; rerolled ($5) -> Throwback $6 + Judgement $3. Sold Certificate, bought Judgement -> Chaos the Clown (useless). Free Chaos reroll nothing. Small 1000 jokerless: FH TTTQQ 360 + FH AAA33 316 + dead High Card = 692/1000. Dead.

## Post-mortem

Binding constraint: zero scoring jokers through ante 1 and into ante 2 (shops offered Burnt Joker, Zany{E}, Runner{E}, Certificate, Hiker{E,R}, Delayed Gratification{E,R}, Business Card, To Do List - not one unconditional scorer at <= $5). Jokerless L1 Full Houses (~320-400) just barely cleared 450 and 600 but cannot do 1000. Luck of the shop, but two decisions were mine:

Decisions I would change:
1. Ante 1 Big-shop: I rerolled ($5 -> $0) to hunt a <=$3 scorer (advisor said LEAVE); it revealed Raised Fist $5, unaffordable even after selling Certificate ($0+$3). A reroll at cost $5 with $5 can never leave money for a $4-5 scorer. Better: the Arcana pack, or no reroll.
2. Ante 1 Buffoon pick: Certificate vs Runner{ETERNAL}. Neither scored. Zany{ETERNAL} $4 (+12 mult on Trips) would have fired on 2 of my ~8 hands (FH contains Three of a Kind: JJJQQ, AAA22, TTTQQ, AAA33, 888TT - 5 of my 7 scoring plays were Full Houses!). Zany's +12 mult at mult 4 = x4 on the FH, so est would have been ~3x higher (FH 360 -> ~1000+). I misjudged "trips-only" as rare; on Black Deck with 8-card hands and discards, Full House/Trips plays occurred in ~70% of scoring hands. LESSON: Zany/Trio-gated jokers fire on Full House; a Trips-gated +12 mult joker is a real first scorer when you reach FH most rounds.

Reusable rules (if-then):
- IF you own 0 scorers at ante 1 and the shop sells Zany/Wily-type (Three of a Kind +mult) even {ETERNAL}, THEN count how many of your last plays were Full House/Trips: if >= half, BUY it (FH contains Trips, so it fires). Eternal costs nothing with 6 free slots at ante 1.
- IF a reroll would leave you < the cheapest scorer's price after selling your only joker, THEN don't reroll; buy the pack/planet instead.
- IF Judgement is in the shop with a free slot and you are jokerless, it is a legal emergency buy ($3, random sticker-free joker), but expect junk (got Chaos the Clown).
- Jokerless Full House L1 = 320-400 per hand: clears 300/450/600 only; ante 2 Small (1000) needs a scorer by then.

Advisor/CLI defects:
- shopadvise listed Zany{ETERNAL} as "adds ~0 now" (PLUS weak/conditional) although my last 5 of 7 plays were Full Houses which contain Three of a Kind; Trips-gated jokers should be valued by FH frequency (main hand was literally "Full House" in the ante-2 shop header).
- SIM said Zany +0.32 vs buying nothing and recommended it while the rule score (28) and text told me to avoid it; the text contradicted the SIM and I followed the text. SIM was right (+0.32 > +0.15 rule from the playbook: follow SIM at gain >= +0.15).
- After the ante-1 Small, advisor suggested Buffoon pack over Zany; rule line and SIM disagreed and SIM was closer to correct.
