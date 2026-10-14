# Run BWSASTCX (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Head (805/2000)

Ante 1 (D6/Double/The Goad 600, $4): Small: Flush hearts 260 + 2P AAQQ 124. Shop $5: Egg{E}/Juggler{E} only -> Buffoon $4: Banner{PERISH,RENTAL} vs Merry Andy, took Banner (SIM 0.19 vs 0.04). Big 450: 2P QQTT 240 + Pair 77 168 (no discards: Banner) + 2P AAJJ 244. Shop $2: Supernova{PERISH,RENTAL} $1 refused (hard one-rental rule; SIM keep-both 0.66 vs 0.04, swap-for-Banner 0.07), Mime{E}. Goad: 2P 192 + 2P 188 + disc 4 -> Flush diamonds 404 (640/600).
Ante 2 (Economy/Uncommon/The Head 2000, $4 after rent): EMERGENCY 0.07: Wily{PERISH} $4 (only scorer; Delayed Gratification, 2x Arcana). Skipped Small at $0 (rent-broke: shop would buy nothing, saves Banner rent/tick; Economy doubled $0). Big 1500: Trips 666 624 + disc -> FH 444TT 808 + Straight A-T 444 (Wily made 200+400 of it). Shop $1: Red Card{E}, The Moon, Arcana packs: left. The Head: hand had Flush D 528 made; solver p 0.24 discard to JJTT FH draw twice (missed), 0 discards, solver UNWINNABLE; FH QQQTT 760 last. 805/2000.

## Post-mortem

Binding constraint: no scoring joker supply plus no money. Four shops offered Egg{E}, Juggler{E}, Mime{E}, Red Card{E},
Delayed Gratification, Supernova{P,R}, Wily{P}; the one Buffoon pack had Banner{P,R}/Merry Andy. Red Stake $0 Smalls and
Banner's $3 rent kept money at $0-5, so no reroll was ever affordable. Entering ante 2 with Banner (+60 chips) and Wily
(+100 chips on trips) on base mult 2-4: best hand ~800 vs a 2000 boss (score check 0.07-0.21 all ante).

Decisions I would change:
1. Ante 1 shop 2: Supernova{PERISH,RENTAL} $1 with Banner owned. The SIM gave keep-both 0.66 (P next 3 blinds 0.87, vs a2
   boss 0.73) vs 0.04 for nothing: Supernova's +mult (times Two Pair played, 3-5 already) is a x2.5-3 on base mult 2. I
   followed the hard one-rental rule. With $2 and two rentals money would go negative (-$6/round), so the run would still
   have been broke, but it would have entered The Head with ~+5 mult. Not changeable under the rule; data point for it.
2. The Head: I discarded a made Flush 528 (solver p 0.24 for the FH draw). The alternative (Flush first, then 2 hands needing
   736 each) was probably similar; the boss was ~unwinnable at 2000 with chips-only jokers. Real fix was upstream.
3. Ante 1 shop 1: Buffoon pack over saving $5. Correct per rules (0 scorers), the pack whiffed.

Reusable rules (if-then):
- IF you own Banner, THEN every discard costs 30 chips on EVERY later hand: play made hands without discarding while
  the made hands keep pace (ante 1 Big: Pair 77 168 + any card ~75 cleared 42 remaining without touching a discard).
- IF you are rent-broke ($0-2 with a rental) before an ante-2 Small that your hands cannot clear easily, THEN skip it:
  the post-Small shop buys nothing and the skip saves a rent charge and a perish tick (advisor recommends this).
- IF the only scorers are chips-only (Banner, Wily) at ante 2, THEN the ante-2 boss (2000) needs ~700/hand: L1 Full House
  with both barely reaches 800. Treat ante 1 +mult jokers as the only thing that matters; chips-only bridges do not
  carry an ante-2 boss.

Advisor/CLI defects:
- shopadvise ante 1 shop 2: rule pick BUY Supernova{P,R} ("NEEDED NOW") then LEAVE because of the hard rule. Fine, but the
  SIM line "buy Supernova (sell Banner)" 0.07 vs keep-both 0.87 means the swap was not worth it; the advisor never
  offered "sell Banner" alone (Banner rent -$3/round, $1 back).
- `s` at ante 2 Small advised skipping for the Economy Tag "pays" while money was $0 (doubling $0 = $0); the skip was right
  for the rent-broke reason, but the tag text overstated it.
