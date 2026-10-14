# Run YSPYCXK1 (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 boss The Tooth (47271/120000)

Ante 1 (Foil/Charm/The Goad 600, $4): Small FH 555/66 268 + 2P. Shop $5: Supernova{ETERNAL} $5 (only scorer). Big: Straight 8-high 300 + Straight K-high 474. Shop $5: Drunkard $4. Goad: Flush H 380 + 2P AA55 208 + FH 888/33.
Ante 2 (Top-up/Investment/The Head 2000, $6): skipped Small for Top-up -> Swashbuckler + holo Hanging Chad (free). Big 1500: 2P 9966 1496 + Trips QQQ 1680. Shop: Jumbo Buffoon -> Walkie Talkie. Head: High A 798 + 2P QQ33 1575.
Ante 3 (Charm/Ethereal/The Club 6400, $13): Buffoon -> Wrathful; skipped Small for Charm (Mega Arcana: Hermit $9->$18, Hierophant bonus cards). Big: 2P KK88 2812 + High TD 2340. Shop: sold Drunkard, The Order{PERISH,RENTAL} $1 (x3 Straight). Club: Pair 44 3168 + 2P 1767 + 2P AAKK 2583.
Ante 4 (Top-up/Polychrome/The Needle 9000, $33): Mega Arcana -> Justice (glass 4C) + Fool. Skipped Small AND Big (Order perish ticks saved; Polychrome tag). Needle (1 hand): Justice glass on 4C, disc to Straight 4-8, moved glass card FIRST (Hanging Chad x3) -> 26166 vs 9000.
Ante 5 (Garbage/Buffoon/The Flint 50000, $25): shop: sold Wrathful -> To the Moon $0 polychrome (x1.5 mult edition; Swashbuckler counts its $5 sell value). Small 25000: Straight Q-high with bonus Qs first 31027 one-shot. Skipped Big (Buffoon tag, pack junk). Flint (halves base): Pair KK dig 1755, Straight 7-J bonus TC first 37611, High Card foil 4H first card 11349 -> 50731/50000.
Ante 6 (D6/Holo/The Tooth 120000, $22): sold Walkie -> Blue Joker{E} $5 (+2 chips/deck card), Grabber $10 (4 hands). The Order had 1 perish round left, so skipped Small and Big to spend it on the boss. Tooth: Straight 6-T 24354, then no 2nd straight (no discards after the first dig): Pair 3948, 2P KKQQ 11703, High TC 7266 = 47271/120000. LOSS ($-5 from Tooth).

## Post-mortem

Binding constraint: scaling at ante 6 (60k/90k/120k) with a perishable engine. The only multiplier that mattered was The Order{PERISHABLE,RENTAL} (x3 Straight) + Hanging Chad (first scoring card retriggered twice = x3 on that card) + poly To the Moon + Blue Joker chips. It perished the round I needed it for ante 6; no permanent growth xMult was ever seen (shops: Cloud 9, Drunkard, Wee, Odd Todd, Greedy, Golden, Blue, Lusty, Squares: all flat).

Decisions I would change:
1. Ante 6: skipping Small AND Big to save The Order for the boss was a gamble that needed 3-4 straights; one straight (24k) came and 4 hands only reach ~75k even with all straights. Alternative (Small 60000 with Order, 4 hands) was a ~55% clear but equally ended at Big 90000. No branch survives ante 6 without a new xMult; the real mistake was not stockpiling a replacement xMult earlier (money was spent on Arcana/Celestial/Standard packs at ante 5, $25 -> $16).
2. Ante 4 shop: rerolled once and bought Mega Arcana (Justice + Fool). OK. But I never used The Fool's Justice (Fool copy was wasted by using Justice on the Needle at once, and the second Justice was not available): should have used Justice then Fool-copy on a second first-card straight card.
3. Walkie Talkie/Wrathful sells: fine.

Reusable rules (if-then):
- IF you own Hanging Chad (retrigger first card x2), THEN the first SCORING card of the played hand is worth x3 (chips, edition, enhancement, and Walkie/Scholar-type per-card jokers). Put the best card (Glass, Bonus, foil, 4/10 with Walkie Talkie) FIRST with `move hand FROM 1` before playing. A single foil/bonus 4 or 10 played alone as High Card scored 8.9k-11k at ante 5 with Walkie. Glass first card = x2 per retrigger = x8 on base mult: Straight 8-high 26166.
- IF you own The Order (x3 Straight) with a poly/edition xMult, THEN straights (even 7-high) make 25-37k at ante 4-5 and carried the run to ante 6; discard 4-5 cards toward an open-ended 4-card draw every blind and keep one discard for the 2nd straight.
- IF the Flint is the boss, THEN it only halves BASE chips/mult: a Straight with first-card bonus still made 37611 (Order x3 + Chad); do not treat it as a x0.5 on the whole hand.
- IF a perishable x3 joker has N rounds left, THEN skipping blinds preserves its ticks; use Skip tags on Small/Big of the ante before its last round and fight the one that is clearable (here Small 60000 was clearable, boss 120000 was not): I skipped to the unclearable blind.
- IF a polychrome joker is free (Polychrome tag) THEN buy it even if the joker does nothing (To the Moon): x1.5 mult edition; also raises Swashbuckler via its $5 sell value.
- Strength can turn a 4-card gutshot (J T 9 7) into an open-ended draw (J T 9 8): 7 outs vs 4.
- Top-up tag at ante 2 with 4 free slots gave Swashbuckler + holo Hanging Chad: that carried antes 2-5. Skip Small at ante 2 for Top-up when jokerless.

Advisor/CLI defects:
- Advisor treated Two Pair (then Straight) as the main hand and told me to "Shift to Pair/Two Pair/Trips" while Straight with Order+Chad was making 25-37k and every blind. The Gold rule "Straight mains die" is wrong for Order/Chad builds; shopadvise ranked planets for Venus/Earth as "wasted" but never suggested Saturn priority or Four Fingers/Shortcut.
- shopadvise rule advice ranked "sell The Order" (my x3 Straight xMult, 1 round left) as weakest when the Order still had a round to live; `advice` SIM "no option clears": sim does not model Hanging Chad first-card x3 or Glass first card.
- `advise` for Two Pair at ante 2 est 1496 vs need 1500 (short by 4) printed the discard plan fine; est is exact (matched actual in every observed play: 3168/1767/37611/11349).
- Mystic Summit{ETERNAL,RENTAL} showed +62% round est and SIM +0.41; the advice picked Wrathful correctly but the SIM would have ranked a permanent -$3/round eternal as the best buy.
- Pack `advise` for Standard Pack printed "No pack advice" (4H foil was the right pick given Chad).
