# Run 7RFNYICY (port 7801, claude-fable-5-1) - Black Deck Gold Stake - WIN (beat ante 8 boss Cerulean Bell 493996/400000)

Ante 1 (Skip/Rare/The Club 600, $4): Small: Flush C 292 + 2P. Shop $5: Buffoon $4 -> Burglar (vs Credit Card; 6 hands/0 discards). Big 450: Straight 296, High dig, 2P TT55 100, Pair AA. Shop $7: Card Sharp $6 (passed Raised Fist{E,R}). Club: High dig, Pair 44 register, Pair JJ x3 180, Flush D 284, Pair QQ x3 120 = 628.
Ante 2 (Garbage/Polychrome/The Fish 2000, $7): Greedy Joker{E} $5 (EMERGENCY 0.22, only scorer). Small 1000: Pair 99 register 140, Trips AAA 378, Trips TTT x3 1080. Shop $5: The Star $3 (override LEAVE). Big 1500: Star on 4S 4H KC -> diamonds, Pair 4D4D 144, Flush D 1482. Shop $10: reroll (nothing), Celestial -> Venus. Fish: Pair 66 44, Pair TT+3 facedown = 2P 100, sort suit/rank inference -> KD QD + 3 facedown diamonds Flush 1406, top-5 facedown window 450+ = cleared with 2 hands left.
Ante 3 (Top-up/Foil/The Psychic 6400, $8): Walkie Talkie{E} $4 (override BARRED '2nd eternal flat'; SIM +0.17), Celestial -> Earth, $0. Skipped Small for Top-up Tag -> Raised Fist + Wrathful (free, no stickers). Order Card Sharp rightmost. Big 4800: Pair JJ 840, 2P 8833 1302, 2P AAKK x3 4836. Shop $7: Temperance +$11, sold Wrathful -> Bull $6, Arcana -> Hanged Man (2D 3H destroyed), $10. Psychic: Pair 88 966, Pair TT x3 5460 = 6426/6400.
Ante 4 (Handy/Standard/The Eye 18000, $21): left shop with $21 (Bull: money = chips). Skipped Small for Handy Tag +$25 ($46). Big 13500: Pair 77 1972, Pair 88 x3 8850, Pair AA x3 9300. Shop $58: Emperor -> Wheel (miss) + Justice; passed Seed Money/Celestials to keep Bull chips. Eye (no repeats, Card Sharp dead): Justice on AD, High A dig 2142, Flush D w/ Glass last 9306, 2P TT55 5400, 0-score dig, Pair QQ 2800 = 19648/18000.
Ante 5 (Juggle/Meteor/The Plant 50000, $66): Buffoon (Photograph{R} poly / Swashbuckler{P}: skipped, no slot worth it), Mega Arcana -> Empress on TS 9D + Death 6C->TS(mult). Small 25000: Pair 55 3200, Pair TS TS x3 18012, Pair QQ x3 9108. Shop $62: Buffoon (Hack{R}/Riff-raff{E}) skipped. Big 37500: Pair 77 3080, TT x3 16932, QQ x3 10950, KK x3 10950. Shop $69: 2 Jumbo Celestials -> Mercury x2 (Pair L3), Hierophant. Plant (faces debuffed): Hierophant on TS TH, Pair TT 6448, KK x3 10656, 55 x3 12798, dig 2562, JJ x3 10656, TT x3 20868 = 63988/50000 (all 6 hands).
Ante 6 (Orbital/Negative/The Flint 120000, $64): sold Raised Fist -> foil Supernova $7 (+26 mult growing, +50 chips), Arcana -> Emperor -> Wheel x2 (miss) + Fool. Small 60000: Pair 99 6758, Straight 4500 (Glass AD scored first, not last: -1.5k), dig, TT x3 36000, 44 x3 30096. Shop $61: Arcana -> Fool -> Wheel = HOLO BULL (+10 mult). Big 90000: Flush S 4820, Pair 99 11322, Flush D x3 29400, dig, TT x3 46032 = 94814. Shop $67: left. Flint (base halved): TT 15344, 55 x3 28890, dig, TT x3 44388, AA x3 31866 = 124822/120000.
Ante 7 (Voucher/Juggle/The Tooth 220000, $78): Paint Brush $10 (hand 9). Small 110000: JJ 13038, TT x3 52392, 66 x3 39270, 88 x3 40656. Shop $75: Strength $3 held, Arcana -> Wheel (miss). Big 165000: 77 13680, 4D4D x3 52578, KDKD x3 45756, 88 x3 43560, TT x3 62160. Shop $78: 2 rerolls (nothing). Tooth (-$1/card): JJ 15128, TT x3 62640, 66 x3 43776, 44 x3 53352, KK x3 43164, TT x3 57024 = 269436/220000, $50 left.
Ante 8 (Handy/Standard/Cerulean Bell 400000, $60): Jumbo Spectral -> Trance (blue seal 9H). SKIPPED Small for Handy Tag: +$76 ($130 = Bull +260 chips). Big 300000: Strength 9H 9C -> Ts, Pair 55 23400, TT x3 97020, TT x3 87750, QQ x3 78810, KK x3 79920 = 366900. Shop $140: Spectral (Medium/Hex) skipped. Bell (forced card each play): 77 27448, TT(mult+bonus) x3 107568, JJ x3 85950 (forced JD), AA x3 84096, QQ x3 84804, 4D4D x3 104130 = 493996/400000. WIN. 214 steps, 0 CLI aborts, 0 rejects.

## Post-mortem

Binding constraint: slots, then multiplier. From ante 3 all 6 slots were full (two of them eternal) and no joker-row xMult
ever appeared that beat Burglar's 6 hands, so the run was carried by a money engine instead: Bull (+2 chips per $) with
interest, unused-hand dollars and TWO Handy Tags (+$25 at ante 4, +$76 at ante 8) turned cash into +100..+280 chips on
every hand; foil Supernova (+1 mult per Pair played, bought at +26, finished at +61) was the mult; Card Sharp x3 fired
on 4-5 of Burglar's 6 hands per round. Final build: Burglar, Greedy{E}, Walkie Talkie{E}, foil Supernova, holo Bull,
Card Sharp (rightmost), Pair L3, hand size 9, $136. Typical ante-8 x3 pair: ~250-300 chips x ~70 mult x 3 = 80-105k.

Decisions I would change:
1. Ante 2 shop ($10): a $5 reroll found nothing and left $5; with Burglar (0 discards) the Celestial/Venus was fine but
   the reroll was dead money. Ante 1-2 rerolls at <$20 whiff (playbook already says so).
2. Ante 6 Small: played a wheel Straight with the Glass AD at hand position 1, so x2 fired first (4500 vs the 6075 the
   solver showed for the A-last order). `move hand` the Glass card to the right end BEFORE every play that scores it.
3. Ante 7 shop: two rerolls ($11) for a Cavendish/Blueprint-tier joker at ~3% per reroll; with Bull that cost 22 chips
   per hand for nothing. Rerolls on a full-slot Bull build are only worth it with $100+.
4. Ante 4 shop: I could have bought Seed Money ($10) before The Eye for +$5 interest x 13 rounds; I chose the Eye's
   chips. Fine at 0.93x, but with a Bull build Seed Money early is +120 chips by ante 8.

Reusable rules (if-then):
- IF you own Bull (+2 chips per $), THEN money IS score: never spend below what the next blind needs (each $5 = 10 chips
  on every hand = ~5% of a 200-chip hand), hold $25+ for max interest, and treat a Handy Tag (+$1 per hand played this
  run) as the best skip in the game: at ante 4 it paid $25 (+50 chips/hand), at ante 8 $76 (+152 chips/hand, the Bell
  went from ~0.67x to 1.2x). Skip the Small for it even at ante 8.
- IF you own Burglar (6 hands, 0 discards) AND Card Sharp, THEN hand 1 registers Pair with your WEAKEST pair plus 3
  junk fillers (draw 5), and hands 2-6 are x3 pairs; keep the best pair (Ts with Walkie, enhanced cards) for a x3 hand.
  Every play draws, so a High Card dig with 5 junk cards replaces the missing discards. Under The Tooth fillers cost
  only $1 each: still use them.
- IF Supernova is for sale and you play 5-6 Pairs per round, THEN it beats Raised Fist / any flat +mult from ante 5 on:
  it starts at your Pair count (+26 here) and grows ~+5 per Burglar round (+35 over three antes).
- IF a Buffoon/shop joker is an xMult but every slot holds a core piece, THEN compute 'round units': Burglar+Card Sharp
  = 1 + 4..5 x3 hands = 13-16 units; a replacement xMult X with 3 hands = (1 + 2 x 3) x X = 7X units, so only x2.3+
  (Cavendish x3, Blueprint next to Card Sharp) beats Burglar; The Duo/Baron/poly Photograph do not.
- IF The Fish (face-down draws) is the boss and you have 0 discards, THEN `sort suit` and `sort rank` still order the
  face-down cards by their real values: a face-down card grouped after your diamonds in suit order is a diamond, one
  that sorts below all your known cards is low. I played a 5-card diamond Flush with 3 face-down diamonds (1406) and a
  'top-5 window' of a rank-sorted all-face-down hand (adjacent equal ranks) that scored the last 450.
- IF The Eye is the boss (each type once) with Card Sharp, THEN dig with a 4-card High Card first (keeping a 4-flush),
  play Flush/Two Pair/Pair as they come and use a 0-score junk High Card as a pure dig once High Card is spent; Justice
  (Glass) on a flush card placed LAST in hand order gives (4+12)x2+3 = 35 card-phase mult instead of 19.
- IF Raised Fist is owned, THEN fillers are the LOWEST cards and a T/J/Q/K must be the lowest card left in hand (+20);
  under The Plant a debuffed face as the lowest held card gives +0, so keep a Ten as the lowest.
- IF Death is picked from a pack, THEN `move hand` the junk card LEFT of the card to copy first: the lower index becomes
  the copy (the CLI says so, but the advisor's default targets had the direction wrong for my intent).
- IF Top-up Tag is on the ante 1-3 Small and you have 2 free slots, THEN skip: tag jokers carry no stickers (Raised
  Fist + Wrathful free here) and the $0 Small shop with $0-4 buys nothing anyway.

Advisor/CLI defects (with examples):
- shopadvise BARRED Walkie Talkie{ETERNAL} $4 at ante 3 as 'a 2nd ETERNAL non-xMult locks another slot the xMult hunt
  needs' with 3/6 jokers, EMERGENCY 0.26, TIGHT 0.91x and SIM +0.17; the bar should not fire with 2+ free slots or
  when the SIM gain is >= 0.15 (it became a core scorer: +10 chips +4 mult per T/4, 8 Tens in the deck by ante 8).
- `s` at blind select (ante 4 and ante 8 Small) said 'do not skip' with a Handy Tag worth $25 / $76 while Bull was
  owned; skip advice should price Handy (hands played x $1) and, with Bull, convert $ to chips x hands.
- advise/hands under The Fish list nothing for face-down cards; it could at least say 'sort suit/rank orders face-down
  cards by their real value' (the trick that cleared the round).
- advise under The Eye kept saying 'register for Card Sharp' (useless there) and est for the Straight with Glass AD
  (ante 6 Small) showed 4500 for the idx order I used but the solver line showed 6075 for 'A last' without telling me
  that the hand ORDER (not the typed order) decides it; a `move hand` suggestion would have been right.
- SCORE CHECK at ante 8 projected ~267k for the Bell (ratio 0.67) with $60; it does not model that unused hands,
  interest and tags change Bull's chips; after the Handy skip it jumped to 478k.
- shopadvise 'ante 6+ money is worth nothing unspent' is wrong with Bull owned (every $ is 2 chips on every hand).
Bridge issues: none (214 steps, no rejects, no offline time). Three shopadvise calls took 70-80s (backgrounded).
