# Run FGQZFMKN (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Hook (6344/6400, short by 56)

Ante 1 (Economy/Skip/The Pillar 600, $4): Small: 2P 76 + 2P 112 + Flush 272 (kept discards, flush drew in). Shop $4: Buffoon pack -> only Drunkard (+1 discard) / eternal-rental Credit Card. Big 450: 2P 124 + Trips 180 + Straight 296. Shop $4: Scholar{PERISH,RENTAL} $1 (+4 mult +20 chips per Ace: a lone Ace = 180). Pillar: Straight 200 + Flush 236 + lone AH 180 = 616.
Ante 2 (Investment/Charm/The Window 2000, $5): Buffoon -> Even Steven{ETERNAL} (over a 2nd rental). Skipped Small (Investment tag, $1 in hand, rent due) -> tag paid $25 after the boss. Big 1500: 2P QQ22 440 + FH 88855 1184. Shop $3: Jolly. Window (diamonds debuffed): 2P 504 + 2P 500 + FH 44488 1792 = 2796.
Ante 3 (Buffoon/Meteor/The Hook 6400, $27): EMERGENCY 0.15. 3 rerolls ($18) found nothing but Earth ($3, Full House L2 = 65x6) and a +4 Joker $2. Skipped Small (Buffoon tag -> Crafty/Cartomancer/Droll/Devious: junk, took Crafty) and Big (Meteor tag -> Mega Celestial: Earth -> FH L3 90x8, Jupiter). Hook: dug twice, drew FH 222JJ 3712, 2P KK88 1232, last hand 10-high Straight 1400 vs 1456 needed -> 6344/6400. LOSS.

## Post-mortem

Binding constraint: no xMult at all by ante 3 (6 jokers: Drunkard, Scholar, Even Steven, Jolly, +4 Joker, Crafty = all flat); typical round ~3000 vs a 6400 boss. The run was decided by a 56-point miss on the last hand: my last hand was a Straight and the free Mega Celestial pack offered Saturn (Straight +30 chips +3 mult, would have made it ~2300) which I passed for Jupiter (Flush), a hand I never played.

Decisions I would change:
1. Mega Celestial pick 2: I took Jupiter (Flush) because Crafty gave +80 chips. Straight/Flush/Quads were all unlevelled; the pair-family/FH main hands were not in the pack. In an `any other planet` choice, pick the hand you have actually been MAKING most often off-main (this run: Straight 3x, Flush 2x, FH 3x). Saturn would have cleared the Hook.
2. Ante 3 shop: left with $4 unspent after Earth; Venus ($3, Trips) was also for sale. Money does not score: with TIGHT/EMERGENCY, buy the second cheap planet.
3. Ante 3 Hook hand 1: I discarded twice to dig for a Full House (got 4 pairs, then 2222+JJ) and never banked a hand first; that was fine (FH 3712), but the last two hands only had ~2700 total left and no discard. Hook discards make late digging unreliable: after the first big hand, bank everything.
4. Ante 3 shop: 3 rerolls ($18) never found an xMult. The $18 would have bought 6 planets/packs; reroll hunting at $27 with 0 xMult whiffed (Vampire was the only xMult seen and needs enhanced cards).

Reusable rules (if-then):
- IF the Meteor/Celestial tag gives a choice of 2 planets and your main-hand planet is not offered, THEN take the planet of the hand you most recently needed (count Straight/Flush plays in the log), not the one your off-hand joker supports; +30 chips/+3 mult on a Straight outscored +15/+2 on Flush plus a +80 chips joker.
- IF Even Steven is owned, THEN Full House/Quads of even ranks are the real engine (222JJ FH 3712 at L3, 22+88 two pair ~1200); a lone Ace with Scholar is 324 at ante 3 (+4 mult per Ace x 1 base mult).
- IF the Hook is the boss and the last hand needs more than a Two Pair, THEN do not play a hand that leaves 5+ cards held (2 random held cards are discarded; the dig line `play 2 junk cards, keep 6` loses half its keepers).
- IF the Small Blind skip tag is Investment and you hold <$5, THEN skip: it paid $25 after the ante-2 boss and avoided a $3 rent tick.
- IF rent would push money below $0, it does (-$2/-$3) and the next cash-out recovers it; Scholar's rent made every shop start at $3-4.

Advisor/CLI defects:
- `advise` at The Hook: SOLVER lines (p 0.54 for a flush-draw discard, p 0.48 'play 2 3 6 7') ignore that The Hook discards 2 held cards at every play; the 'dig: play 2 junk keep 6' line (p 0.30 vs two pair 0.24) is the one to avoid.
- Pack `advise` for the Mega Celestial said 'NOT your main hand' for Earth even though Full House was my best hand (it uses the two-pair main hand label from L1 plays); it ranked Jupiter over Saturn from SIM score ratio (0.63 vs 0.57) although the last hand turned out to be a Straight.
- SCORE CHECK said ratio 0.15 at ante 3 (EMERGENCY) while shopadvise offered nothing but planets and perishable +4 mult; there was no xMult in 3 rerolls, so the EMERGENCY text had no actionable buy.
