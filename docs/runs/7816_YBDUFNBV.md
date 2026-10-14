# Run YBDUFNBV (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 boss The Mouth (1560/18000)

Ante 1 (Boss/Skip tags, The Head 600, $4): Small: discard to 4-diamond draw, Flush 316. Shop $6: Buffoon pack -> Half Joker{PERISHABLE} (+20 mult on <=3 cards; 1-card High Card = 336). Big: High A 336 + Pair QQ 660. Shop $7: Sly Joker $3. Boss Head: two 1-card High Cards 315+315.
Ante 2 (Double/Investment/The Psychic 2000, $10): Jumbo Buffoon -> Joker{PERISHABLE} +4 (alt Walkie Talkie{E}, Banner{R}). Small Pair QQ 2080. Shop: Mr. Bones $5 (Psychic counter; refused Photograph{E,R} $1). Big Pair 66 1872. Buffoon -> Vagabond (free tarots at <=$4). Psychic (5 cards): Flush 648 + FH 912 + 2P 660 = 2220.
Ante 3 (Charm/Polychrome/The Window 6400, $8): Half Joker perished. Arcana -> Temperance ($10), reroll -> Gros Michel{PERISHABLE} $5 (+15 mult), Wily{E} $4. Skipped Small (Charm -> Mega Arcana: Wheel, Death). Big 4800: Strength A->2 made FH 222QQ 6118 one-shot (Gros Michel then died, 1/6). Window 6400: FH KKKJJ 2320 + 2P 948 + Pair 792 = 3268; Mr. Bones saved the blind at >=1600.
Ante 4 (Buffoon/Voucher/The Mouth 18000, $3): shop had Photograph $5 / Brainstorm{E} $10, only $3. Arcana -> Strength. Skipped Small (Buffoon: Chad, Drunkard) and Big. Mouth: Trips 840 + 720, then 0. 1560/18000.

## Post-mortem

Binding constraint: NO xMult and no scaling at all by ante 3-4. The whole run was flat bridges (Half Joker, +4 Joker, Gros Michel, Sly, Wily) that were all perishable or one-shot; best normal hand at ante 4 was ~800-1700 against 9000/13500/18000 (needs ~5x more). Money never exceeded $12: Gold Small pays $0 and every buy was a $4-6 bridge, so the shops that showed Photograph $5 and Brainstorm $10 at ante 4 were unaffordable ($3).

Decisions I would change:
1. Ante 2 shop: spent $5 of $6 on Mr. Bones. It did save the ante-3 boss, but a run that needs 5x scaling gets nothing from a one-blind save; the $5 + Vagabond/Buffoon money would have been better kept for rerolls at ante 3. Counter-view: without it the Psychic/Window would have ended the run at ante 2-3, so it bought one ante.
2. Ante 3: took Temperance/Wily (eternal, conditional) and sold nothing useful; Wily{E} never fired outside lucky Strength-built Full Houses. An eternal conditional chips joker at ante 3 is a dead slot at ante 4.
3. Ante 4 Mega Buffoon pack (skip Small) offered Chad/Drunkard/Egg/Credit Card: pure junk; the skip cost nothing but also made no difference.

Reusable rules (if-then):
- IF you hold Half Joker (+20 mult on <=3 cards) THEN play 1-2 card hands only: a 1-card High Card scored 315-336 and a 2-card Pair 660-2080 at ante 1-2 (3 hands of 300-2000 clear everything to ante 2). It is a bridge only: perishable 5 rounds and dead vs The Psychic.
- IF Strength is in hand THEN check rank wrap: Ace -> 2 (it turned AH AD into 2H 2D next to 2S and QQ = Full House 6118, solver found it as `USE Strength`). Also Strength on a card one rank under a pair/trips (QS->K) manufactures a Full House with Wily.
- IF the boss is The Psychic (5-card plays, Half Joker dead) THEN a 5-card Flush/Full House still scores ~650-900 with a flat +4 mult joker: 3 hands of 650/900/660 beat 2000, no need to panic.
- IF Mr. Bones is owned THEN any score >= 25% of the blind (even 1600 of 6400) counts as the blind beaten: on the last hand just bank the biggest hand; it is destroyed afterwards and the next blind is unprotected.
- IF Vagabond (free tarot per hand at <=$4) is owned THEN consumable slots must stay free; I held Lovers/Chariot unused and later hands generated nothing.
- IF Gros Michel is bought THEN expect it to be gone after 1-3 rounds (1/6 each round end); it died after one Big blind. Do not count on it for the boss.

Advisor/CLI defects:
- shopadvise at ante 4 ranked Photograph (card-phase x2 on base mult) 130 as XMULT above Brainstorm; with 2 base mult it is worth ~+50%, not an xMult.
- `s`/BOSS WARNING and SCORE CHECK correctly called EMERGENCY from ante 2, but no line existed to fix it with $2-8: nothing in the advisor suggests selling Vagabond/Mr. Bones (sell $5/$2) to afford a $10 Brainstorm/xMult when SIM is 0.00 everywhere.
- Solver `USE Strength (consumable 1) on [1,2]` at Big 4800 was excellent (found rank wrap); the main ADVICE line said "PLAY TWOPAIR est 3402" instead - the ADVICE line did not follow the better USE line.
