# Run YSRFMUJQ (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 boss The Arm (16064/120000)

Ante 1 (Rare/Boss/Manacle 600, $4): Small: Straight 6-high 200 + 2P KK22 88 + High A, 300 exact. Shop $4: Photograph $5 and Mystic Summit $5 both unaffordable; Buffoon pack -> Sly Joker{PERISHABLE} (other pick Runner eternal rental). Big: flush draw hit, FH AAA66 540 after Flush 252. Shop $5: Celestial -> Venus. Manacle: disc x2 keeping AA44, Trips AAA 665 (Venus L2) one-shot.
Ante 2 (Holo/Buffoon/The House 2000, $8): EMERGENCY (0 scorers): Smiley Face{ETERNAL,RENTAL} $1 (override: eternal rental, SIM 0.78 vs 0.03). Skipped Small (Holo tag) AND Big (Buffoon tag = Mega Buffoon: Ice Cream + Photograph, both perishable). House: disc 5 facedown x2, FH 222QQ 4968 one-shot (Smiley +5/face, Photograph x2).
Ante 3 (Orbital/Investment/Tooth 6400, $11): Holo tag -> free holo Vampire $0. Skipped Small (Orbital Pair +3 levels -> L4) and Big (Investment $25). Tooth: Pair KK 7700 with 2 cards. Shop $39.
Ante 4 (Buffoon/Meteor/Head 18000, $39): Banner, Mercury (Pair L5), 2 Temperance (+$10 each), Judgement -> Mad Joker (sold later), rerolls x4 found nothing. Skipped Small (Mega Buffoon -> Half Joker). Big: Pair TT 8640 + Pair 44 8028. Bought Hanging Chad{ETERNAL,RENTAL} $1 (retriggers first card x3: Photograph+Smiley chain, ~2.7x). Head: K-high straight 12078 + Pair AA 4104 + Pair QQ 16830 = 33012.
Ante 5 (Orbital/Negative/Window 50000, $30): Venus, Mercury (Pair L6). Photograph had 1 round left, so skipped Small and Big (Negative tag) to keep it for the boss. Window: cycled junk hand, Pair KH+KD(debuffed) 27300, disc, Pair JS+JD(debuffed) 22620 -> 52691/50000. Photograph perished at that round end.
Ante 6 (Polychrome/Top-up/Arm 120000, $20): best hand fell to ~10k without Photograph (EMERGENCY ratio 0.14). Free negative To Do List, Gros Michel from Top-up. Skipped Small and Big. Arm: Trips 4500, Straight 5852, Pair 5712 = 16064/120000. LOSS.

## Post-mortem

Binding constraint: scaling. The whole build was card-phase multiplication from PERISHABLE Photograph (x2 per first face, x2 per Chad retrigger) on a Pair/Smiley face engine; it died at ante 5 and nothing permanent replaced it. No permanent xMult was ever found (Vampire stayed x1; 6 shop rerolls and 3 Buffoon packs offered none). Hand ~28k at ante 5 -> ~10k at ante 6 vs 60k Small.

Decisions I would change:
1. Ante 5 shop: I spent $26 of $30 on two Celestial packs (Venus, Mercury) for ~+15% and rerolled once. With a perishable Photograph at 1 round left, that money should have been kept to buy a permanent xMult / Negative-slot joker, but none was offered anyway. The root error was relying on perishable jokers as the core engine at ante 3-5 without a permanent replacement lined up.
2. Ante 4: Banner (perishable, +30 chips per remaining discard) was worth ~+27% chips only while discards were kept; using discards cost real score (single face est 7020 -> 3780 after discarding). Discard-based jokers conflict with discarding for face pairs.
3. Ante 4 shop: sold Ice Cream and took Hanging Chad; correct, it tripled the Photograph chain (Pair QQ 16830 vs 7700 before), but it is only good while Photograph lives.

Reusable rules (if-then):
- IF you own Photograph (or any first-scoring-card joker) AND Hanging Chad, THEN play a 2-card face pair (Half Joker keeps +20 at <=3 cards): est 16-28k at Pair L5-6 and ante 4-5. Put the face card FIRST in hand order (`move hand`).
- IF a perishable joker is your multiplier AND it has 1 round left, THEN skip Small and Big (a skip does not tick perishables) and spend it on the boss; plan its replacement before that boss shop.
- IF The Window (diamonds debuffed) is the boss, THEN a pair containing one debuffed same-rank card still counts as a Pair and the non-debuffed one scores (Pair KH+KD(d) scored 27300; Pair JS+JD(d) 22620); do not discard such pairs.
- IF The House draws 8 face-down cards, THEN discard 5 and then the other 3 face-down cards (advise says so); 2 discards fully reveal the hand.
- IF Banner is owned, THEN count remaining discards in the est: keep 1 discard for the last hand if it makes the clear (Pair J 22620 vs 19929 needed was cleared only because 1 discard remained).
- IF you are at ante 2 with 0 scorers and a Rental+Eternal $1 face/mult joker is offered, THEN it can carry (Smiley + Photograph won ante 2 House 4968) if you skip blinds so the -$3/round rent only ticks on boss rounds.
- IF a Mega Buffoon tag is on the Small/Big blind and your best hand is below that blind's need, THEN skip it: two jokers now beat a likely loss (did it at ante 2 and 4).
- Temperance ($3) pays total joker sell value: +$10-13 net at ante 4; buy it on sight when holding $20+.
- To Do List/Negative tags: a Negative tag makes the next shop's first joker free+Negative regardless of quality (it was To Do List here).

Advisor/CLI defects:
- shopadvise: "BUY Banner" SIM 0.11 treated Banner as full value, but its +60 chips vanish if you discard (single face est 7020 -> 3780 after one discard); `advise` est already models the discard count, shopadvise SIM should too.
- Ante 5 boss with 1-round Photograph: s/advise at blind select said "do not skip: shop is worth more than a tag" while the joker was about to perish; skip rule should note perishable-engine preservation.
- Ante 4 shopadvise ranked Arcana pack (95) over Celestial/xMult hunts while Photograph/Ice Cream were about to perish; it did warn about perishing but ranked buys by generic score.
- advise high-card ests with Half Joker/Banner/Photograph are large (single K 7020) but Pair advice "PACE" text still says "discard toward a bigger hand" in cases where three single faces clear the blind (est 3 x 7020 >= 18000); solver caught it, rule text did not.
- Hanging Chad shopadvise: no est shown for the retrigger x Photograph interaction before buying (I computed 2.7x by hand).
