# Run NIMYTH5Y (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Needle (2512/9000)

Ante 1 (D6/Rare/The Window, $4): Small: Straight 240 + 2P 88. Buffoon $4 -> Wrathful{PERISH}. Big: disc, FH 777KK 810. Shop: Odd Todd{RENTAL} $1 (NEEDED NOW). Window: 2P 380 + 2P QQ77 928.
Ante 2 (Top-up/Boss/The Goad, $9): Even Steven{RENTAL} $1 (overrode LEAVE: SIM 0.72 vs 0.07). Skipped Small for Top-up -> Scholar + Fortune Teller. Big: 2P 9944 1728. Buffoon -> Chaos the Clown (advisor said skip). Goad: 648 + Pair AA 1340 + 2P 232 = 2220/2000. $4 -> $-2 after 2 rents.
Ante 3 (Economy/Uncommon/The Tooth, $3): EMERGENCY 0.30. Sold Fortune Teller + Wrathful, Onyx Agate{PERISH} $7 (SIM 0.58 vs 0.07). Skipped Small AND Big (shops unusable at $1 with $6/round rent). Tooth: Straight A-5 5040 + 2P 1248 + High AH -> 6623/6400; money $-14 after cards+rent, $-9 after cash.
Ante 4 (Investment/Garbage/The Needle 9000 in ONE hand, $-9): free-reroll shops showed nothing affordable. Skipped Small (Investment) and Big (Garbage +$5 -> $-4): the Needle is the gate either way. Needle: High Card start, 2 discards (solver p 0.03 -> 0.02), best final hand Flush H 2512/9000. Lost.

## Post-mortem

Binding constraint: money, caused by two flat rentals (Odd Todd + Even Steven) from ante 1-2. -$6 per round with $3-9
in hand meant every shop from ante 3 on was empty-handed (cash went $8 -> $4 -> $-2 -> $3 -> $1 -> $-14 -> $-9). With no
money there was no Celestial (Two Pair stayed L1 the whole run), no xMult, no rescue tarot, and the ante-4 Needle
(9000 in one hand, ~3.8x my 75th-pct hand of 2380) was unreachable. Zero xMult was ever offered in 5 shops
+ 3 free rerolls, but I could not have bought one anyway.

Decisions I would change:
1. Ante 2 shop: buying the second rental (Even Steven $1) at $9. The SIM said 0.72 vs 0.07 for the next 3 blinds, and it
   did carry the Big and The Goad, but the Top-up skip right after brought Scholar anyway and the rent then bankrupted
   ante 3-4. Better: buy Steven, and sell Odd Todd (or Steven) in the very next shop where 2 non-rental scorers exist
   (ante 3 shop: Scholar + Onyx). I overrode that SELL FIRST at ante 3 because each rental was ~half my score; the
   score loss was real, but the money loss was fatal one ante later.
2. Ante 2 Buffoon: Chaos the Clown's free rerolls (3 used) never showed an affordable scorer; with $4 cash a free
   reroll is worth little. Skipping it changed nothing either way.
3. The Tooth with $2: playing a 5-card straight first (-$5) was right for the clear, but it pushed money to $-14 and
   killed interest/shop for ante 4. Unavoidable once broke.

Reusable rules (if-then):
- IF you hold 2 rentals AND have < $10, THEN sell one in the next shop where 2 other scorers exist, even at a 30-40%
  score loss: each round costs $6 and negative money removes every future fix (levels, xMult, rescue tarot).
- IF money is <= $2 (or negative) AND rent is due every round, THEN skipping Small and Big is free: their shops buy
  nothing, the rent you skip ($3 per rental per round) exceeds what the blind pays, and the boss must be beaten anyway.
  (This run: skips at ante 3 and 4 were correct; they just could not rescue the score.)
- IF the upcoming boss is The Needle at ante 4 AND your best hand is < 9000, THEN that ante's Big/Small shops must buy
  levels or an xMult; with no money there is no answer, so the cash discipline has to start at ante 2.
- IF an Odd Todd/Even Steven pair is your engine, THEN face cards score 0: discard Q/K/J freely (solver did this well).

Advisor/CLI defects:
- shopadvise ante 2: printed `ADVICE: LEAVE (SIM: the rule pick changes survival by +0.65; nothing on offer raises it by
  more than 0.02)` while the rule pick itself (Even Steven) was the +0.65 item: the ADVICE line contradicted its SIM.
- `s` at blind select (ante 3 and 4) said "do not skip ... take the shop" while money was $1 / $-9 and two rentals
  charged $6 per round: the skip rule should check whether the shop can buy anything and count rent saved.
- shopadvise SELL FIRST Even Steven ("2 non-rental scorers carry your hands") when Steven supplied ~half the mult of
  every even-card hand; the rule ignores how much score the rental provides. (In hindsight the sell was right for money.)
- SIM gives Chaos the Clown +0.00 (does not model free rerolls); fine at low money.
- Rent can drive money negative (seen $-14); shopadvise did not warn at the second rental buy that cash ($8) would hit
  $0 within 2 rounds.
Bridge issues: none (57 steps, no rejects).
