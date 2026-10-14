# Run GICNFV6Z (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Fish (11960/18000)

Ante 1 (Rare/Investment/The Hook 600, $4): Small: disc AA (solver), Straight T-high 280 + Pair QQ. Shop $5: Smiley{RENTAL} $1 (SIM 0.92 vs 0.01); passed 2nd rental Scary. Big: FH JJJTT 1710 one-shot. Shop $7: Wrathful $5. Hook: 2 discards, 2P KKQQ 1320 one-shot.
Ante 2 (Uncommon/Double/The Water 2000, $6): EMERGENCY 0.35; passed Scholar{E,RENTAL}/Crazy{E}. Skipped Small for Uncommon tag (override). Big: 2P JJ55 900 + 2P QQ77 810. Shop: free Marble (tag), Temperance +$3, reroll -> Scary Face{PERISH} $4. Water: 2P AA55+stone 816 + 2P AAKK 1464.
Ante 3 (Garbage/Standard/The Club 6400, $5): EMERGENCY 0.23 -> Gros Michel $5 ($0). Skipped Small for Garbage (+$5; shop at $0 buys nothing). Big 4800: 2 discards, Pair 55 dig 340, Straight 9-K (3 faces) 5746. Shop $7: Jolly $3; kept Smiley over advisor's SELL (ratio 0.72 with it). Club: disc debuffed clubs, Straight A-K 6840 one-shot.
Ante 4 (Standard/Charm/The Fish 18000, $8): ratio 0.29, no xMult offered; Saturn $3 (never used again). Skipped Small (Standard -> gold KS) and Big (Charm -> Mega Arcana: sold Wrathful, Judgement -> Mystic Summit, Magician -> lucky 9H 9C). Fish: 2 discards, High KS + 2 stones 5220 (est 7175), then blind face-down plays 2240 + 4500 -> 11960/18000. GAME OVER.

## Post-mortem

Binding constraint: scaling. Zero xMult was OFFERED in 8 shop views + 1 reroll + 1 Mega Arcana (no Buffoon pack ever
appeared after ante 1), so the build stayed flat (Smiley, Scary, Gros, Jolly, Mystic Summit ~ +50 mult, ~100-150 chips):
~4.5-7k per face hand at ante 4 vs 6000/hand needed at the Fish. Money was the second constraint: Smiley's rent took
$18 over 6 rounds and every shop was entered with $5-8, so even a $6-8 xMult would have needed a sale.

Decisions I would change:
1. Ante 4 shop: Saturn $3 (Straight L2) was never used; the Arcana pack $4 (Justice/Strength/Death chance) or keeping
   the $3 for the Big-blind shop was worth more. Planets for a non-main hand are not "boss insurance" at ratio 0.29.
2. Ante 4: skipping BOTH Small and Big without Throwback sent a 0.29-ratio deck into the Fish with no shop in between.
   The Charm pack paid (Mystic Summit, lucky cards) but nothing multiplicative; the Big shop (~$10) was the last chance
   at a sighting. [INFERENCE] Neither line was likely to win; the skip did save one coin-flip fight.
3. The Fish: the first play (High KS + 2 stones + 2 fillers) replaced 5 cards with face-down ones, so hands 2 and 3 were
   blind. At the Fish the first hand must carry most of the requirement; play fewer cards per hand so fewer get
   replaced face-down.

Reusable rules (if-then):
- IF ante 3-4, money <= $5, no xMult, and the Small Blind pays $0, THEN skip it for any tag that pays now (Garbage,
  Standard, Charm, Economy): its shop could buy nothing and the skip saves $3 rent and a perishable tick.
- IF a Mega Arcana offers Judgement AND you own a weak flat joker (+3/suit), THEN sell that joker and take Judgement:
  the created joker carries no stake stickers.
- IF The Fish is the boss, THEN spend both discards before the first hand, play the biggest hand first, and play only the
  scoring cards on later hands (every played card is replaced by a face-down one).
- IF a Mystic Summit is owned, THEN burn both discards before the first play (the solver handles this).

Advisor/CLI defects:
- `advise` run immediately after a state-changing action printed the PREVIOUS state's analysis twice (after the Water
  hand 1 and after the ante-3 Big discard); `s` first, then `advise`, was correct. Once `s && advise` printed a stale
  `s` but a fresh `advise`.
- `est` counted a Stone card's underlying rank as a face: High KS + stones "QS(stone)" + "9H(stone)" est 7175, actual
  5220 (= 145 chips x 36 mult, i.e. no Smiley/Scary trigger on the stone Q).
- SOLVER under The Club proposed keeping the debuffed QC (top two lines "keep QC JD 7D"); debuffed faces score nothing.
- shopadvise ranked Scholar{ETERNAL,RENTAL} with SIM +0.23 (unsellable -$63) and called Saturn "boss insurance" at
  ratio 0.29; shopadvise baseline SIM p_next 0.00-0.01 when buying nothing looked very pessimistic at ante 1-2.
Bridge issues: none; 62 steps, no rejects.
