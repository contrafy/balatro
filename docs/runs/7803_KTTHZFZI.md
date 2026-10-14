# Run KTTHZFZI (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Serpent (46894/50000)

Ante 1 (300 Coupon / 450 Holo / The Pillar 600, $4): Small: discarded into a club Flush, 308. Shop $6: the advisor said buy Erosion{ETERNAL,RENTAL} (+0 mult with a 52-card deck!). I overrode it and bought a Buffoon pack -> Clever{PERISH}. Big: Two Pair KK88 272 + KKTT 280. Shop $7: Joker{PERISH} $2 + Supernova{RENTAL} $1. Pillar: Two Pair 66 33, 1062 in one hand.
Ante 2 (Rare / Garbage / The Head 2000, $8): bought Hermit $3 and held it. Skipped Small for the Rare Tag. Big: Two Pair 1220 + Trips Q 480. Shop: free Rare = holo The Tribe{PERISH}. Head: overrode advise's heart-flush chase (hearts debuffed) and played Two Pair KK99 for 2709.
Ante 3 (Charm / Handy / The Mouth 6400, $11): Hermit took $11 to $22, then Mystic Summit $5. Small: spent 2 discards to arm Summit, Two Pair 4662. Shop $20: rerolled -> Stuntman{PERISH} $7 (+250 chips: huge on an all-+mult line) + Gros Michel $5; sold the Supernova rental. Big: Pair 9 8618. Mouth: Pair 6 7344. Gros Michel was destroyed after the Mouth.
Ante 4 (Rare / Boss / The Hook 18000, $20): Raised Fist{PERISH} $5, 1 reroll, Supernova $5. Skipped Small for the Rare Tag (saves perish ticks). Big: 2 discards -> Two Pair TT33, cleared 13500 in one hand. Shop: free Rare = Blueprint (copying Stuntman = +500 chips), rerolled -> Half Joker{ETERNAL} $5. Hook: 2 discards, Pair K 30740 in one hand.
Ante 5 (Coupon / Skip / The Serpent 50000, $15): shop: 1 reroll, nothing. Skipped Small for the Coupon Tag so Stuntman (1 round left) would last through Big. Big 37500: Pair 6 29754 + High Card A 27348. Stuntman perished: Pair fell from ~30k to ~1.8k. Coupon shop: free Jumbo Spectral (Deja Vu on AC) and free Arcana (Temperance +$13 -> $33). Bought Campfire{PERISH,RENTAL} with Blueprint copying it. Sold Fist, Swashbuckler (bought to sell), Death, Pluto, Emperor's 2 tarots, plus Supernova mid-boss: Campfire x2.75, squared x7.56 via Blueprint. Bought Hanging Chad $4. Serpent: Pair J 13990, Trips 7 18679, final diamond Flush 14225 (best available) = 46894/50000. GAME OVER.

## Post-mortem
Binding constraint: SCALING, specifically CHIPS. Every permanent joker I had added mult (Summit +15, Half +20, Supernova, Fist).
All my chips came from one perishable joker: Stuntman +250, doubled by Blueprint. When it perished at ante 5, the hand had ~60 mult on
~30 chips (Pair L1), and the score collapsed from ~30k to ~1.8k. Campfire+Blueprint then got back to ~14k per hand, which was 3.1k short.
No r/g xMult was ever offered except the Campfire rental (13 shop views, 5 rerolls).

Decisions I would change:
1. I skipped Mercury ($3) twice at ante 3-4 because the advisor called it "planet for other hand" (it thought my main hand was Two Pair).
   I was playing Pair. On a line with 40-60 mult, each Pair level adds +15 chips to a ~30-chip hand: +50% per level, multiplied by every
   mult joker. Two Mercuries (Pair L3: 40 chips base instead of 10) would have added ~8k per Serpent hand and won the boss.
2. At the ante-4 Hook shop ($17) I spent $5 on a reroll and $5 on Half Joker. I should have kept money and bought chip sources (planets)
   for the moment Stuntman died. A perishable that carries 95% of a stat needs its replacement bought BEFORE its last round.
3. Spectral pick (Deja Vu on AC) did nothing. Cryptid on a K (more pairs of high rank) or skipping would have been the same.

What worked:
- Skipping Smalls for Rare Tag x2 (Tribe, Blueprint) and Coupon (free Jumbo Spectral + Arcana) was right each time. Each skip also
  saved a perish tick on the bridge jokers.
- Stuntman ($7) on an all-+mult line took Two Pair from ~1.9k to ~11k at ante 3.
- Campfire + Blueprint + selling everything sellable (consumables count) took the hand from 1.8k to 14k in one shop.
- Temperance from an Arcana pack turned 5 cheap jokers into +$13.

## Reusable rules (if-then)
- IF your mult is 40+ and your chips come from the hand base (<60), THEN buy every main-hand planet ($3). +15 chips is +25-50%. A chip
  joker (Stuntman, Ice Cream, Castle, Blue Joker, Sly) beats any +mult joker in this state.
- IF one perishable joker provides more than half your score, THEN buy its permanent replacement while it still has 2+ rounds left. Do not
  wait for the shop after it dies.
- IF a skip tag is Coupon/Rare and a key perishable has 1 round left, THEN skip the Small: the perishable lasts one blind longer
  and the free shop arrives in its place.
- IF you own Campfire + Blueprint (Blueprint left of Campfire), THEN every sale counts squared. Sell all consumables, buy $3 tarots/planets
  or $4 jokers just to sell them (Emperor = 2 free sales), and sell weak +mult jokers mid-boss when (1+0.25(n+1))^2/(1+0.25n)^2 beats their share of mult.
- IF the Head (hearts debuffed) or another suit boss is up, THEN never chase a flush in that suit: the cards count for type but score 0 chips.

## Advisor/CLI defects
- Ante 1 shopadvise ranked Erosion{ETERNAL,RENTAL} 85 "NEEDED NOW: a scorer". Erosion is +4 mult per card BELOW 52, so +0 on a fresh deck.
  It was also eternal and rental, so it could never be sold to stop the $3/round charge. It should be scored 0 (deck is 52).
- Main-hand detection stayed "Two Pair" from ante 3 to the end, though I played Pair/High Card in ~10 straight hands (Half Joker owned).
  SCORE CHECK used "Two Pair KK ~1305-1740" while the real Pair was ~30k, and Mercury was labelled "planet for other hand".
- Throwback was labelled "x0.25 per skipped blind: useless, we never skip" at ante 4 after I had skipped 1-2 blinds (it was x1.25-1.5).
- The free Rare-tag Tribe ($0) was ranked 89, but the ADVICE line said "LEAVE: nothing worth buying at this money level".
- The Head: `advise` said discard toward a 4-heart flush (EV 860) while hearts were debuffed.
- ORDER FIRST at ante 3 proposed `order 2 3 4 5 1`, which put Mystic Summit (+mult) RIGHT of The Tribe (xMult). Summit belongs left of it.
- Half Joker{ETERNAL} was ranked 8 while I played <=3-card Pairs every hand. +20 unconditional mult is a core scorer, so eternal costs nothing there.
- Ante 5 Big: `advise` proposed `disc 1 2 3 4` (AC KH 6S 6H) with Raised Fist owned, throwing away the high held cards that feed Fist.
  `sel` showed Pair 6 + low filler holding A K 8 = 29754 vs the advised line 25578.
Bridge issues: none. est was exact on every hand (Serpent: 13990 / 18679 / 14225, total 46894).
