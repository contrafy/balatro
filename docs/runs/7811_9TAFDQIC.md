# Run 9TAFDQIC (port 7811, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Needle (60/9000)

Ante 1 (Investment/Economy/The Club 600, $4): Small: royal flush H 1208 one-shot. Shop $5: Buffoon -> Flower Pot{E} (x3 if 4 suits) over Green Joker{R}; Ice Cream{R} $1 (+100 chips). Big: 2P 268 + 2P 314. Boss Club: 2P 258 + 286 + FH 640.
Ante 2 (Double/Garbage/The Flint 2000, $4): Arcana -> Magician (Lucky TH TC). Skipped Small (broke, $0 pay). Big: 2P(4 suits, Flower Pot x3) 678 + FH 616 + Trips 330. Flint: Flush with Lucky TC fired 2508 (est 226) - 20% luck.
Ante 3 (Charm/Orbital/The Manacle 6400): Crazy Joker $4 left of Flower Pot (+12 mult on Straight, x3 with 4 suits). Skipped Small: Charm doubled by Double Tag = 2 Mega Arcana (Hierophant, Empress, High Priestess). Big: 4-suit Straight 7632 one-shot. Celestial -> Saturn. Manacle: Straight 3657 (3 suits) + 4-suit Straight 10281.
Ante 4 (Coupon/Orbital/The Needle 9000, $4): sold Ice Cream{R}, bought Blueprint{E,R} $1 left of Flower Pot (copies x3 -> x9 on 4-suit hands; est 14535 for a 4-suit straight). Skipped Small (Coupon). Big 13500: two junk digs holding 3D 4H 5C 6S (4 suits, 8 outs) then 4-suit Straight 14535. Coupon shop: Hallucination, Uranus, Earth, 9H, Death (no Saturn). Needle (1 hand, 2 discards): kept QD 9H 8S, then 7C 8S 9H TD, missed the 6/J (p 0.61), final 60/9000.

## Post-mortem

Binding constraint: scaling/variance. The whole build was ONE hand type (4-suit Straight, x9 via Flower Pot + Blueprint copy) with flat score ~2000 otherwise. Every blind needed a 4-suit straight, and The Needle (one hand, 9000) turned that into a single ~0.6 x 0.45 coin flip. No second multiplier source, no Saturn in 3 Celestial packs (L2 only), $0-5 all run (Gold rent + $0 Small).

Decisions I would change:
1. Ante 4 shop: spent the last $4 on a Celestial pack (no Saturn) instead of keeping money; with an engine this narrow nothing bought mattered, but a Needle/one-hand boss at ante 4 should be anticipated: hold the Death/Strength and 4 suits worth of keepers.
2. Needle first discard: kept QD 9H 8S (3 suits, needs T+J: p~0.13). It is better to look for a keep set that already has 4 distinct suits in a straight window; the second discard found one (7C 8S 9H TD) and still missed a 61% shot. Unlucky but the first discard's 13% line was the real loss.
3. Took Flower Pot{ETERNAL} at ante 1 (a conditional xMult); it worked only because Crazy Joker/Blueprint made 4-suit Straights x9. Fine, but it made the run all-in on suit diversity.

Reusable rules (if-then):
- IF you own Flower Pot (x3 for 4 suits scored) THEN the hand to build is a Straight/Two Pair with 4 distinct suits; before every play use `sel` on the alternative card choices: swapping one card (8S -> 8H) changed est 2544 -> 7632 at ante 3.
- IF you hold a draw that already has 4 distinct suits (3D 4H 5C 6S) THEN every completing rank gives the suit bonus automatically: dig with junk plays (HIGH cards that keep the 4) rather than discarding; it cleared Big 13500 at ante 4.
- IF a Blueprint (even {ETERNAL,RENTAL}) can sit directly left of an xMult you already own THEN it is functionally an xMult: swap it for your old chips-only rental in the same shop (same $3 rent).
- IF the stake pays $0 Small and you are broke THEN skip Small whenever the tag is Charm/Coupon/Double: Charm doubled by Double Tag gave 2 Mega Arcana packs at ante 3.
- IF you have a Lucky card and the boss halves base (Flint) THEN a Flush/any hand including the Lucky card has a 20% shot at +20 mult (2508 vs est 226): `est` does not count it.
- IF the next boss is The Needle (one hand) THEN the engine needs a hand that clears boss/hand in a single deal with 2 discards: pre-position cards (Death to fix a suit/rank, Strength) and do not enter with a 4-suit-only straight engine unless p >= 0.7.

Advisor/CLI defects:
- SIM/solver does not model Flower Pot x3 or Blueprint copying it: it showed round p ~0.2-0.55 and `est` for non-4-suit hands as the only value, and rated every shop buy "+0.00 / SIM NOISE" while Crazy Joker + Flower Pot was worth x9; shopadvise AVOIDed Blueprint{E,R} (-90/-135) with the "eternal rental" text although it triples the score here.
- shopadvise ranked Droll Joker (+10 mult if Flush) 89 for a free Coupon item even though a Flush can never carry 4 suits; pack advice "skip pack if Saturn not offered" fine.
- `advise` Needle line says "UNWINNABLE this round" when no 6/J: correct, but its discard advice (keep QD 9H 8S, p 0.13) ignored that keeping suit-diverse cards matters for Flower Pot.
- Hallucination ("1/2 tarot when pack opened") fired once in three packs (Death); advisor ranks it 20 (UTIL): fine.
