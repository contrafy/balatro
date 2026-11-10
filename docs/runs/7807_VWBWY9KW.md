# Run VWBWY9KW (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Plant (11453/18000)

Ante 1 (Investment/Investment/The Pillar 600, $4): Small 300: 2P TT88 112 + 2P KKQQ 120 + 2P 9966 100 = 332. Shop $4: Buffoon pack -> Arrowhead{PERISHABLE} (+50 chips/spade; Vampire was the other). Big 450: 2P TT77 308 + Trips KKK 330. Shop $5: only Devious{E,R}/Chaos{P,R} at $1 (barred), left. Pillar: disc, FH AAAQQ 532 + High QS 65 + High 9S 64 = 661.
Ante 2 (Standard/Buffoon/The Psychic 2000, $11): shop: Supernova $5 (2nd scorer). Small 1000: Pair-dig, Straight 775 (est; scored 859), Spade Flush 1675 (Arrowhead: spades = +50 chips each, High Card of a spade ~250). Shop $7: Jumbo Buffoon $6 -> Abstract{ETERNAL} (over Ice Cream; advisor wanted Ice Cream), $1 left. SKIPPED Big for Buffoon Tag (Mega Buffoon: Stuntman{E,R} barred / Egg / Midas / Bull{E}) -> Egg + Midas Mask. Psychic: 2P 3322 + filler 1760, Broadway Straight 2751 = 4511.
Ante 3 (Top-up/Rare/The Mark 6400, $7): sold Midas -> holo 8 Ball $8 (+10 mult). Skipped Small (Top-up -> Square Joker) AND Big (Rare tag; keeps Arrowhead alive for the boss). Mark: disc 3 (kept one face-down), FH 55533 5474 + High TS 2080 (Arrowhead's last round).
Ante 4 (Meteor/Polychrome/The Plant 18000, $12): Arrowhead perished; Rare tag gave Blueprint{ETERNAL} $0 -> ordered left of Abstract (x2 Abstract = +36 mult at 6 jokers). Buffoon pack = Madness / Delayed Gratification (skipped), 1 reroll (nothing). Skipped Small (Meteor: Mega Celestial -> Earth + Venus) and Big (Polychrome). Plant: sim said UNWINNABLE (round ~8000 vs 18000): FH 88866 5555 (8 Ball -> High Priestess -> Neptune+Mars, useless mid-round), 2P 74 2268, 2P AATT 3630 = 11453/18000. LOSS.

## Post-mortem

Binding constraint: no xMult and no chips scaling by ante 4. The build was ~50 flat mult (Abstract x2 via Blueprint, 8 Ball holo, Supernova) times only ~60-100 chips. Every normal hand was ~2-5.5k; the Plant at 18000 needed 6000/hand. Arrowhead (+50 chips per spade) carried antes 1-3 (a spade High Card = 250-2000) and its perish at ante 3's boss removed ~60% of my chips. I never found an xMult: 3 Buffoon packs (Vampire, Ice Cream/Abstract/Cloud 9, Stuntman/Egg/Midas/Bull, Madness) and the shops showed none; $1-12 all run so no rerolling budget.

Decisions I would change:
1. Ante 2 Big skip for the Buffoon Tag: the Mega Buffoon had no scorer worth a slot (only Stuntman{E,R}, barred). Egg+Midas were near-useless. Playing the Big would have paid ~$4 and kept Supernova growing; the skip left me at $1 until the post-Psychic shop.
2. Ante 3: skipping Small AND Big (Top-up, Rare) kept Arrowhead alive but cost two shops AND all income; I entered ante 4 with $12 instead of ~$25 and 0 chips scaling. Money (not just skips) was the constraint; Rare tag Blueprint was the only real gain and only doubled Abstract.
3. Ante 4: both skips (Meteor, Polychrome) left a 0.45x boss; the free poly joker never arrived. I should have played the Small 9000 (ratio 0.54) for money and a shop visit to hunt chips/xMult.

Reusable rules (if-then):
- IF your scoring is a flat ~50 mult (Abstract/8 Ball/Supernova) and chips are under 100, THEN chips are the multiplier: buy +chips jokers (Scary, Arrowhead-type, Banner, Stuntman if allowed) and planets (+15-30 chips per level = +20-30% each) before another flat +mult.
- IF Arrowhead (+50 chips per Spade scored) is owned, THEN play 1-card spade High Cards when mult is high (est 250 at ante 2, 2080 at ante 3 with Abstract +15): it beats pairs; keep it alive past the boss by skipping blinds (perishables do not tick on skips) - but sell nothing it needs.
- IF Madness is the pack pick and you own non-eternal scorers, THEN skip: it destroys them first.
- Supernova counts plays per hand TYPE: junk High Card fillers early (Pillar ante-1) gave it +4..+7 for High Card, making single-card plays strong until FH/Pair counts catch up. Commit to one repeated type after ante 2 if Supernova is your growth joker.
- Blueprint left of Abstract Joker works: est and actual scale with the joker count (+36 mult at 6 jokers).

Advisor/CLI defects:
- Pack advise at ante 2 ranked Ice Cream (decaying perishable) above Abstract{E}; I overrode (SIM blind spot: it ignores growth/decay past 3 blinds). Fine in hindsight (Abstract carried to ante 4).
- Shop advise "ADVICE: SELL arrowhead to fund 8 Ball" suggested selling a joker with a live blind to score; I sold Midas instead (correct).
- Plant (faces debuffed): `advise` rule pick "disc 2 3 4 1 5" would have thrown away AH; solver best lines differed from the rule pick without explanation of exp vs p when p=0.00 everywhere.
- est undercounts nothing notable; 2P AATT est 3630 (actual 3630), FH est 5555 exact.
