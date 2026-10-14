# Run RHYICWF8 (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Small (8634/9000)

Ante 1 (300 Investment / 450 D6 / The Window 600, $4): Small FH QQQ66 328 one-shot. Shop $6: Mystic Summit $5. Big: 2 disc -> FH KK333 1311. Window: 2 disc -> Straight AKQJT 1539.
Ante 2 (1000 Foil / 1500 Voucher / The Manacle 2000, $15): Ride the Bus $6. Small: 2P 8855 828 + Pair TT. Shop $11: reroll -> Scary Face{PERISH} $4. Big: Quads QQQQ 4840. Shop $8: Buffoon -> Popcorn (override SKIP). Manacle: Trips KKK 5700.
Ante 3 (3200 Foil / 4800 Boss / The Club 6400, $9): Joker{PERISH} $2; played Small (override skip advice). Small FH JJJ55 4080. Shop $12: left. Big: Broadway 5985. Shop $20: Mega Celestial -> Mercury+Uranus, Golden Joker $6. Club: FH AAAQQ 4402 + High K 1260 (kept 55) + Trips 555 1395.
Ante 4 (9000 Orbital / 13500 Investment / The Wheel 18000, $16): Scary Face perished (sold). EMERGENCY ratio 0.12-0.16. Buffoon -> Swashbuckler{RENTAL} (+11 mult, override SKIP), reroll (Scholar/Superposition), Celestial -> Uranus (2P L3). Small: 2 disc to turn Summit on, held KK 77 33: 2P 7733 3200 + 2P KKQQ 3800 + forced Pair 99 1634 = 8634/9000. GAME OVER.

Post-mortem
- Binding constraint: scaling. Zero xMult all run; every scorer was temporary (Popcorn decaying, Scary Face and Joker
  perishable) or flat (Mystic Summit +15, Ride the Bus ~0 on a face build, Swashbuckler +11). Ante 1-3 were cleared
  by lucky one-shots (Quads QQQQ, Broadway twice, FH) that masked a build of ~2000-3500 per hand.
- Decisions I would change:
  1. Ante 3 Small: I overrode the advisor's SKIP (Foil tag). That shop bought nothing, and the skip would have saved
     one perishable tick: Scary Face would have been alive at the ante-4 Small, where +120 chips on KKQQ alone turns
     3800 into ~8300 and clears the blind. The skip was right.
  2. Ante 3 last shop ($20, TIGHT 0.96x, ratio 0.53): Golden Joker $6 added 0 score. The $6 should have gone to the
     Jumbo Arcana (Justice/Strength) or a reroll for a permanent scorer.
  3. Ante 2: Ride the Bus $6 (resets on faces) followed by Scary Face (faces): the two fought each other all run.
  4. Ante 2 last shop: passed a permanent Walkie Talkie $4 to save $4; a permanent +4 mult would have been worth
     more than the ~$1 interest it cost.
- Reusable rules:
  - IF you own perishable or decaying scorers (Popcorn, Ice Cream, {PERISHABLE}) AND your best hand >= boss/2 of
    this ante, THEN skipping the Small Blind is worth it for the tick alone: it keeps them alive one more blind
    later in the run, when the blind is 3x bigger.
  - IF shopadvise says TIGHT or ratio < 0.7, THEN do not buy an economy joker (Golden, Egg, To Do List); every dollar
    goes to score now. Economy only pays if you survive the next ante.
  - IF you own Scary Face/Smiley/Photograph (face payoffs), THEN do not buy Ride the Bus, and sell it if owned.
  - IF Mystic Summit is your main mult, THEN burn both discards in the first draw window and keep made pairs across
    hands: holding three pairs (KK 77 33) after the discards gave two Two Pair hands from one deal.
  - IF you reach ante 3 shops with 0 xMult and no permanent scorer, THEN treat every shop as EMERGENCY even when
    the next blind is projected to clear: the ante 3 -> 4 jump (6400 -> 9000 Small) kills a temporary build.
- Advisor/CLI defects:
  - Pack advise SKIP on Swashbuckler with "AVOID(useless as the only joker)" while I owned 5 other jokers (it was
    +11 mult) and on Popcorn (+20 mult) at a TIGHT ante-2 boss with free slots: the AVOID labels ignore context.
  - Ante-2 Big SOLVER listed "DISCARD 1 2 3" (throwing away made Trips QQQ, p>=0.99); the next deal was Quads.
  - Main hand flips with every one-shot (Full House -> Three of a Kind); planet picks of Mercury/Uranus got
    "a level elsewhere is mostly wasted" even though Pair/Two Pair were the hands I actually built toward.
  - Ante-4 Small SOLVER said p 0.60-0.70 for lines that had to find ~2000 on a final undiscarded draw where a
    plain pair maxed at ~1786; outcome: lost by 366.
- Bridge issues: none; 75 steps, no rejects.
