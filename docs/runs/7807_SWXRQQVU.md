# Run SWXRQQVU (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Wall (10555/12800)

Ante 1 (Polychrome/Charm/The Window 600, $4): Small: disc 3, heart Flush 300/300 exact. Shop $6: Jumbo Buffoon (Egg/Cartomancer{E,R}/Credit/Riff-raff{R}) -> Riff-raff{RENTAL}. Big: Riff-raff made Clever + Blue; 2P TT66 440 + Pair 55. Shop $2: sold Blue, Jolly{E} $3. Window: Riff-raff made Ice Cream + Photograph, sold Riff-raff mid-round (no rent); 2P KK77 2808 one-shot.
Ante 2 (D6/Meteor/The Head 2000, $9): shop: passed Hanging Chad{PERISH,RENTAL}. Small: Pair TT 1250 one-shot. Shop $12: passed Zany{ETERNAL} $4 (advisor BUY). Big: Pair 66 1120 + Pair 55. Shop $19: Bootstraps $7; passed Celestial (advisor BUY) to keep $12 for Bootstraps +4. Head: Pair 88 1484 + Pair 99 (debuffed 9H) -> cleared.
Ante 3 (Holo/Holo/The Wall 12800, $20): score check 0.61, BOSS PREP flagged the Wall. Reroll $5 (nothing), Celestial -> Uranus (2P L2). Small 3200: 2P 6655 3180 + Pair 33. Shop $14: Buffoon $4 (Scholar{P,R}/Ride the Bus{R}) skipped. Big 4800: 2P QQ44 3744 + Pair TT. Shop $17: TIGHT 0.80x; reroll $5 -> Mercury/Lusty{E}, left with $12. Wall: FH QQQ33 4120, solver UNWINNABLE (max ~4100/hand vs 8680 in 2), 2P 7755 2835, 2P KKTT 3600 -> 10555/12800. GAME OVER with $12 unspent.

## Post-mortem

Binding constraint: SCALING against a doubled ante-3 boss. The Wall at ante 3 needs 12800 = ~4270 per hand. My build was
Clever (+80 chips on 2P) + Jolly{E} (+8) + decaying Ice Cream + Bootstraps (+4 at $10-14) + Photograph. I had been
counting Photograph as a multiplier, but it is card-phase: it doubles only the hand's base mult (3-4) before the +mult
jokers, so the real build had 0 xMult and capped at ~4100 per hand (FH QQQ33 with a face). The solver called the Wall
unwinnable on the first deal (exp 9448), and I died 2245 short with $12 in the bank.

Decisions I would change:
1. Ante 2 shops: I passed Zany{ETERNAL} $4 and a Celestial pack $4 (both advisor BUYs) to protect Bootstraps' $5
   brackets and interest. The SIM showed +0.00 for everything because its 3-blind horizon only covered the easy ante 2.
   Zany (+12 on trips/FH) would have made the Wall's opening FH ~6600 instead of 4120, which closes most of the gap.
   I died holding $12, so that money did nothing.
2. Ante 3: two rerolls ($10) found nothing usable. One Celestial plus Lusty{E}/Mercury would have added ~15-20% to the
   round, and that was the whole gap (10555 vs 12800).
3. Ante 2: Director's Cut ($10) was offered twice. With $12 in the Small shop it was the only Wall answer I ever saw.
   At Gold, one ante-3+ Wall/Violet boss is almost certain, so it is a defensible buy once 2 scorers are owned.

Reusable rules (if-then):
- IF you count your multipliers, THEN leave out Photograph/Glass/Steel/Bloodstone on a flat +mult build: they multiply
  only the base mult (FH here: 4 x2 = 8, then +8 +4). With them as your only "xMult", plan as if you own 0.
- IF the SIM shows +0.00 for every item at ante 2 (the next 3 blinds are easy), THEN the SIM is blind to the ante-3 jump:
  buy +mult jokers/levels for boss/3 of ANTE 3 (~2130-4270 per hand), and do not bank for interest.
- IF Riff-raff shows up in an ante-1 pack with 0 jokers, THEN take it, select the Big and the Boss with it, and sell it
  mid-round at the boss (before the round ends, so no rent). It made 4 free unstickered commons for $0 net.
- IF you own Bootstraps, THEN a purchase costs its price plus the mult lost to the $5 bracket, BUT only below the money you
  will still hold at the next boss. Dying with $12 means the brackets were not worth protecting.
- IF the upcoming boss is The Wall at ante 3-4 AND projected round < 1.0x, THEN spend everything on flat mult that fires on
  your made hands (any +mult joker, eternal included, plus levels). Do not reroll for a perfect xMult.

Advisor/CLI defects:
- Pack `advise` (ante 3 Buffoon): "SIM: take Scholar 0.10 (+0.10 vs skipping)" then "ADVICE: SKIP (no pick raises survival
  by more than 0.02)". The ADVICE line contradicts its own SIM numbers.
- shopadvise rule pick ranked Mercury 88 "MAIN SCALING" BUY while its own SIM showed it LOWERING the ratio (0.54 vs
  0.60 baseline): $12->$9 drops Bootstraps from +4 to +2. The rules ignore Bootstraps' money brackets.
- SIM horizon: at ante 2 every item read +0.00 (the next 3 blinds were already ~1.00), so the SIM gave no signal for the
  ante-3 step. A 4th-blind or next-boss/3 term is needed.
- shopadvise (ante 1 Big shop) said SELL FIRST Riff-raff. Keeping it one more blind produced Photograph + Ice Cream for
  free (sold mid-boss before rent). It should value Riff-raff's pending blind selects while slots are free.
- `est` on FH QQQ33 with Photograph was 4120 (correct, card-phase). This is not a defect, but shopadvise's SCORE CHECK
  numbers were the only place this showed; nothing labels Photograph as base-mult-only.
Bridge issues: none (55 steps, no rejects).
