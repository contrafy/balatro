# Run K8EEKHSD (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Arm (1718/2000)

Ante 1 (300 Boss Tag / 450 D6 / The Window 600, $4): Small: AA discard -> Two Pair AA99 120 + spade Flush 268 = cleared. Shop $5: Buffoon pack offered only Invisible Joker or Supernova{RENTAL}; took Supernova ($1 left). Big: Two Pair KK88 224, Two Pair 8844 220, Pair 60 = 450/450 by 6 chips; rent took money to -$2. Boss Window (diamonds debuffed): Two Pair 9988 324 + Two Pair JJ77 308 = 632/600. Shop $2.
Ante 2 (1000 Economy / 1500 Double / The Arm 2000, $5 after cash out): bought Uranus $3 (Two Pair L2 40x3), left $2. Small: Two Pair 648 + Two Pair 800 = 1448/1000. Money -$1 -> $0 after cash-out; shop had nothing affordable. Big: Two Pair AA99 880 + Pair 3s 64 + Two Pair JJTT 960 = 1904/1500 (needed all three hands, 0 discards left). Cash out left $1; shop (Runner holo $8, Devious Joker foil, Wasteful $10) unaffordable. Boss The Arm: Two Pair 744 + Two Pair (L1 after Arm) 624 = 1368; last hand had Trips 777 / Straight T-high only (est 204 / 350 vs 632 needed) -> 1718/2000.

## Post-mortem

Binding constraint: MONEY and SCALING. Supernova{RENTAL} was my only joker for the whole run and its -$3/round rent kept me at $0-$2 after every cash out (Small pays $0 at Gold), so I never bought a second scorer even though Runner/Devious/Wily/Mime/Egg were in shops. The whole run was one flat Two Pair engine (~650-960 per hand), which is roughly a Small Blind of ante 2, not a Boss of 2000 under The Arm.

Decisions I would change:
1. Ante 1 shop ($5): bought Buffoon Pack ($4) and was forced to choose between Supernova{RENTAL} and Invisible Joker. A rental with $1 left means every later round paid $3 rent: net -$12 over 4 rounds, ~ the price of a real joker. Alternative: the pack was still right (no joker in shop), but I should have sold Supernova at the ante-2 Small shop once it was clear it kept me at $0, and used the $1 + the saved rent toward a $3-5 real joker. I kept it because it was my only scorer; in hindsight Two Pair got ~+11 mult out of it, which is why it was worth keeping, but the cost was zero economy.
2. Ante 2 shop 1 (after Boss 1): bought Uranus ($3, Two Pair L2) with $5. It paid back (Two Pair 324 -> 648+), so keep that call. The real miss was not reaching $8+ for the Buffoon pack / Runner. No fix available without income.
3. Ante 2 Arm boss: first hand played Two Pair at L2 (744, scored one level lower under The Arm, level lost). Then Two Pair again at L1 (624). The Arm plan "play each type once" needs a SECOND strong type; I only had Supernova counting Two Pair. Final hand had Trips/Straight worth 350 max. With Supernova + Two Pair as the only engine, The Arm cuts the engine to 2 plays.

Reusable if-then rules:
- IF you own Supernova and Two Pair is the main hand, THEN Two Pair est grows ~+1 mult per Two Pair played this run (est 308 -> 960 over ~8 plays); keep playing Two Pair and avoid playing other hand types for score unless it clears.
- IF the Small Blind pays $0 (Gold) and you hold a rental, THEN every cash out nets ~$0-2, so plan to SELL the rental the first shop you can afford a non-rental scorer, or you will never afford the second joker.
- IF the ante boss is The Arm and your engine is one hand type, THEN expect to get only 2 plays of that type (L2 -> L1 -> floor) plus one off-type hand; you need ~2000/3 = 667 per hand from a second type or a held Planet for the off-type.
- IF the last hand is a Trips + Straight draw with 1 discard left vs 632 needed, THEN the real fix was earlier: the first hand of the Arm round should have been a Two Pair kept with fillers, not a 5-card discard that threw away AKQ (draw p_clear 8% -> 20% after).

Advisor/CLI defects:
- `shopadvise` ranked Buffoon Pack 78 at $5 with no scorer; the pack offered only a RENTAL scorer and a useless utility joker. It would help to show the expected value after rent ("net -$12 over 4 rounds").
- Ante-1 Buffoon pack `advise` printed the rental price in `-$3 x 23 rounds = -$69`; fine, but did not warn that money would go negative ($1 -> -$2). Negative money is allowed by the game and reset by cash out.
- `play` note "The Arm: scored at one level lower (and the level is lost)": the first Two Pair est (744) used L2 but it actually scored one lower, so est is optimistic by ~1 level at The Arm first play.
