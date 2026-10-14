# Run PFMSHPC7 (port 7802, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Big Blind (26269/90000)

Ante 1 (Charm/Boss/The Window 600, $4): Small: disc keep 333K, FH 333KK 276 + Pair AA. Shop $5: Photograph{P} $5 (SIM 0.29 vs Buffoon 0.22). Big: flush dig, Flush QC 552 one-shot. Shop $6: Even Steven $4. Window: disc, FH AAAJJ 576 + High 6H.
Ante 2 (Buffoon/Skip/The Fish 2000, $8): EMERGENCY 0.31: Ice Cream{P} $5. Skipped Small for Buffoon tag -> Mega Buffoon: Lusty Joker + Walkie Talkie{P} (passed Green{E}, Egg{E}).
  Big 1500: Pair TT 2700 one-shot. Shop $9: passed Banner{P,R} (SIM +0.28, chips-only rental). Fish: ordered 2C 2D before KK (Photograph after Even Steven), 2P 22KK 2780 one-shot.
Ante 3 (Double/Polychrome/The Tooth 6400, $17): EMERGENCY 0.14: Hermit ($17->$28), reroll -> holo Hanging Chad $7, Strength $3. Played Small (0 xMult, overrode skip): Pair 44 7332. Shop: reroll (Wrathful{P} passed). Big: High TD 5250. Shop $22: Buffoon -> Egg (Blue Joker{E,R} barred), Arcana -> Temperance (+$13), reroll -> Brainstorm $10 (sold Egg), Chad leftmost. Tooth: High 4H alone 10230 ($1).
Ante 4 (Uncommon/Voucher/The Wheel 18000, $13): sold perished Ice Cream/Walkie, Odd Todd{P} $4, Arcana -> Fool->Temperance (+$14), reroll -> Blue Joker{P} $5 (leftmost: Brainstorm copies it), Arcana -> Temperance (+$16). Played Small (overrode Uncommon skip): 2P TT33 11248. Shop $32: 2 rerolls, Uranus, Jumbo Arcana -> Temperance, Jumbo Arcana -> Fool->Temperance ($38), reroll. Big: High AH 6140 + FH 55599 9280. Shop $41: Fool $3->Temperance (+$16), 3 rerolls (no xMult), Jumbo Celestial -> Uranus (2P L3). $22.
  Wheel 18000: disc AD QD, Trips KKK (KH first) 5456 dig, Strength 2C->3C made 2P 5533 10920, 2P AA33 -> 26220.
Ante 5 (Standard/Ethereal/The House 50000, $31): EMERGENCY 0.11. 2 rerolls, sold Blue -> foil Ice Cream $7 (leftmost, Brainstorm copy), Arcana -> Fool->Strength, Arcana -> Justice (Glass TC). Small 25000: 2P 6644 12996 + FH TTT55 14874. Shop $9: sold Odd Todd -> Photograph $5, order Photograph leftmost (Brainstorm copies it): first face x2 x2 on each of 3 Chad triggers = x64 (round est 47k -> 208k). Big: disc for spades, Flush QS-first 63720 one-shot. House: sort rank + discard 5 lowest face-downs, played 3 top face-downs + 66 (6253, no pair), disc 5, dig AS (1848), drew QH: 2P QH QC 4S 4D 93200 -> cleared 101k/50k.
Ante 6 (Holo/Orbital/The Plant 120000, $20): Plant warning (debuffs every face). Buffoon (Abstract{P}/Greedy{R}) skipped, Jumbo Celestial without Uranus -> Mercury (Pair L2). Small 60000: Quads 4444 10200 (no face), disc to KS 88, drew QC, Strength QC->KC: 2P KS KC 8S 8D 63294. Shop $13: Arcana -> Chariot (steel 5S). Big 90000: 5-heart flush, no face; disc AC 3S (drew TH), disc 4 (no face), dig Pair 88 8684 (drew KC QS), dig 7H 3275 (needed a J for K-high straight, missed), High KC 14310 -> 26269/90000. GAME OVER. 159 steps, no rejects.

## Post-mortem

Binding constraint: a single-card engine. From the ante-5 Big on every big hand was "a face card scores first": Photograph
leftmost + Brainstorm copying it + Hanging Chad = x2 x2 on each of 3 triggers (x64 on the base mult). With a face it made
63-93k; without one the same deck made 6-15k. The ante-6 Big drew 20 cards with only two faces (K, Q, no pair, no J for the
straight) and lost by 64k. The Plant (faces debuffed) was waiting behind it anyway with no counter found.

Decisions I would change:
1. Ante 4 shops: ~$43 went into 7 rerolls that never showed an xMult, while the Arcana packs offered The Hanged Man three
   times (I took Temperance money). Deck shaping was the real fix for a face engine: Hanged Man on 2s-5s, Strength on J/T,
   Death copying a face would have raised face density from 12/52 to ~12/44 or better.
2. Ante-6 Big, first discard: I discarded only 2 cards (AC 3S) to keep a faceless 5-heart flush worth 15k. When the engine
   needs one card class you do not hold, discard 5 every time; a 15k fallback is worth nothing vs a 90k blind.
3. Ante 6 Celestial without Uranus: Mercury was fine, but the $6 would have been better as a reroll toward Luchador/Mr. Bones
   once The Plant was known (the run could not beat 120k without faces).
4. Antes 1-2: perishable bridges (Photograph, Ice Cream, Walkie, then Odd Todd, Blue) carried me but left 0 permanent
   multipliers until ante 5; the first permanent multiplier came from a $5 Photograph at the ante-5 Small shop.

Reusable rules (if-then):
- IF you own Hanging Chad + Photograph + Brainstorm/Blueprint, THEN put Photograph where the copier copies it (Brainstorm:
  Photograph leftmost): the first face gets x2 x2 on each of 3 triggers (x64); `shopadvise` ORDER FIRST measured 47k -> 208k.
- IF your multiplier needs one card class (first face, a Glass card), THEN every shop buys deck shaping (Hanged Man on low
  non-class cards, Strength T->J / J->Q, Death onto a face) before rerolls, and each hand without that class discards 5.
- IF you just used Temperance, THEN a $3 shop Fool (or a pack Fool) makes another Temperance: +$13-16 each (did it 4 times).
  Use it to fund the shop, not to pile up rerolls at 0 xMult.
- IF you hold Strength and a face single plus a card one rank below it (Q+K, J+Q), THEN Strength turns them into a face pair:
  QC->KC made Two Pair KK88 63294 at the ante-6 Small (advise did not list that line).
- IF The House, THEN `sort rank` before the first discard: the face-down cards line up high to low; discard the 5 rightmost
  and keep the 3 highest (likely faces/aces).
- IF a single-card face engine meets The Plant, THEN its shops must buy Luchador/Mr. Bones/Chicot or a non-face xMult; Glass
  on one card (x32 with Brainstorm copying Chad) is too rare to rely on.

Advisor/CLI defects:
- `sel 2 4 5 6 8` right after `move hand 5 4` (step 156) printed the PRE-move hand order and est 7181; `s` and a second `sel`
  showed the moved order and est 8684. sel can read a stale state right after a reorder.
- advise at the ante-6 Small (KS QC 88 33, Strength held) listed Strength on 8S AH (flush) and never QC->KC (Two Pair KK88,
  est 63294, the line that cleared). At the ante-5 Big it did list Strength AS QS -> KK, so face-pair Strength lines are
  found inconsistently.
- Pack advise for a Jumbo Celestial without the main-hand planet picked Venus (Trips) by rule; SIM showed every planet at
  0.70 (saturated by The Plant), so the fallback choice was unguided.
- shopadvise ante 6 SCORE CHECK printed ~141k round vs The Plant 120000 although The Plant disables the face engine (the BOSS
  PREP line did warn).
Bridge issues: none.
