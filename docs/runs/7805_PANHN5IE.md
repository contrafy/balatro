# Run PANHN5IE (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Water (18597/50000)

Ante 1 (Foil/Foil/The Club 600, $4): Small: Straight K-9 316 one-shot. Shop $6: Mystic Summit{P} $5 (SIM 0.99 vs Buffoon 0.20). Big: 2 discards burned, Pair AA 544. Shop $7: nothing (Hallucination{E}). Club: disc x2, 2P QQ33 731.
Ante 2 (Meteor/Holo/The Wall 4000, $15): EMERGENCY 0.07; reroll, Celestial -> Uranus (2P L2). Small 1000: Straight T-6 1330 (Summit). Shop $9: reroll, Popcorn{R} $1, Mad{P,R} $1 as a Wall bridge (override LEAVE, SIM 0.50->0.88). Skipped Big (broke $2: saves $6 rent, keeps Summit/Popcorn). Wall: FH 66677 3528 + 2P TT44 3264.
Ante 3 (Poly/Uncommon/The Psychic 6400, $2): holo Hack{P,R} $0, Credit Card{P} $1, reroll on credit, Ice Cream $5 -> $-9. Skipped Small AND Big (rent $9/round > Big pay; Summit stays alive for the boss). Psychic: 1 discard, 2P QQ77+filler 6786 one-shot.
Ante 4 (Holo/Juggle/The Manacle 18000, $-11): Uncommon tag shop: sold perished Summit, Buffoon (Superposition/Fortune Teller, skipped), poly Dusk{P,R} $0. Skipped Small and Big (Juggle = 10-card hand vs Manacle). Manacle: 2P TT55 9187, Straight J-7 6396 (kept KK), FH KKK66 final 11286 -> 26869.
Ante 5 (Buffoon/Charm/The Water 50000, $-20 credit wall): sold Popcorn -> holo Luchador{R} $0. Skipped Small (Mega Buffoon: sold Credit Card, Wrathful{E,R}) and Big (Mega Arcana: Hierophant on KC KD, World -> spades). Water: High AD 3024 dig, Pair 44 3333 dig, Pair KS KS (bonus) final 12240 -> 18597/50000. GAME OVER.

## Post-mortem

Binding constraint: ECONOMY -> SCALING. I never owned a permanent scorer. Every joker I bought was a perishable, a
rental, or decaying (Summit{P}, Popcorn{R}, Mad{P,R}, Hack{P,R}, Dusk{P,R}, Ice Cream, Luchador{R}, Wrathful{E,R}). From
ante 2 on, rent was $6-15 per round, more than any blind pays at Gold (Small $0, Big $5), so money went $2 -> $-9 ->
$-20 and every shop from ante 4 could only take $0 stickered jokers. The skip-everything line (8 skips) kept me alive
through ante 4 (each skip dodged a rent charge and a perish/decay tick, and the skip tags were the only free items I
could get), but the ante-5 boss needed ~4x what a flat, xMult-less build could make (best hand ~12k vs 50k).

Decisions I would change:
1. Ante 1 first shop ($6): Mystic Summit{P} over the Buffoon pack. SIM said 0.99 vs 0.20 for the next 3 blinds, and it
   did carry ante 1-2, but it left me with zero permanent scorers when it perished. The ante-2 shops then had only
   stickered jokers, and from there each rental bought the next blind at the price of the next shop.
2. Ante 2 Small-blind shop: the second rental (Mad{P,R}) as a "Wall bridge". It did help clear the 4000 Wall (FH 3528 +
   2P 3264), but $3/round on top of Popcorn put me at $2 for the next shop. The Wall was cleared with ~70% margin, so
   Mad was probably not needed. Popcorn + Summit alone would have been ~2700/hand vs 4000/3.
3. Ante 3: Credit Card + rerolls to -$9 bought Ice Cream (a decaying joker). Credit should only be spent on a permanent
   scorer or an xMult. Ice Cream was a third bridge.

What worked:
- With rent >= blind pay and a broke wallet, skipping Small AND Big is correct at any ante: no rent, no perish tick,
  no Popcorn/Ice Cream decay, and the tags (Uncommon, Polychrome, Juggle, Buffoon, Charm) were my only free items.
  Juggle (+3 hand size) on the Manacle turned a 0.5x fight into a clear (10 cards: 2P, Straight, FH in one round).
- Mystic Summit: burn both discards first, then every hand gets +15 (ante 1 Big 544, Club 731, ante-2 Small 1330).
- Ante 4 Manacle: I overrode a discard and played a straight that kept the KK pair for a certain final hand.

Rules (if-then):
- IF you have 0 permanent scorers AND the shop offers only stickered jokers, THEN take at most ONE rental; with 2+
  rentals, rent is more than the blinds pay ($6/round vs Big $5, Small $0) and every later shop is dead.
- IF rent per round >= $5 AND money < $5, THEN skip Small and Big until the rentals perish or are sold: playing them
  costs money and ticks perishables, and their shops can't buy anything.
- IF you own Credit Card, THEN spend the credit only on a permanent scorer/xMult or a Buffoon pack, never on decaying
  jokers (Ice Cream, Popcorn) or packs that can't contain a scorer.
- IF the ante-1 first shop offers a perishable +mult joker AND a Buffoon pack, THEN prefer the pack once the cleared
  Small showed a natural straight/flush deck (the perishable only moves the problem to ante 3).
- IF a joker has a polychrome edition, THEN it is a x1.5 xMult no matter its own effect (Dusk{P,R} at $0 was my only
  multiplier); put it rightmost.

Advisor/CLI defects:
- shopadvise ante 2: a contradiction: "keep the $9 for the next shop" next to "ADVICE: REROLL" in the same output.
- shopadvise ante 3 with Credit Card: Celestial/Arcana "passed over: would leave $-2, below the $8 money floor" while
  EMERGENCY and Credit Card credit were available; then ADVICE LEAVE although credit could buy a reroll.
- Pack advise ante 5: ADVICE Square Joker (+2% round est) over Wrathful (+25% round est) because of the eternal-rental
  penalty, at the -$20 credit wall where rent no longer limits anything and the run dies this ante without score.
- `s` at blind select said "never skip the Big" while rent ($9-15/round) was more than the Big pays and the money was
  negative; skipping was clearly right (a perishable-carrier skip line was suggested only once).
- Buffoon pack advice suggested picking Superposition (adds 0 score) into the only free slot that poly Dusk needed.
Bridge issues: none (73 steps, no rejects).
