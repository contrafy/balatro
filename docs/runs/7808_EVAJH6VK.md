# Run EVAJH6VK (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Window (117/2000)

Ante 1 (D6/Uncommon/The Hook 600, $4): Small 300: Two Pair 96 + 108 + 96 (exactly 300, last hand). Shop $4: bought Gluttonous{PERISHABLE,RENTAL} $1 (+3 mult/club; only 1 rental; advisor SIM +0.39 vs Buffoon pack +0.22). Big 450: 2P 88 + 240 then dug a J-high Straight 518. Shop $4: Banner{ETERNAL} $5 unaffordable, left with $4. Hook 600: 2P 84, then club Flush KC JC TC 7C 6C 1482 (Gluttonous +15 mult).
Ante 2 (Skip/Rare/The Window 2000, $7): SCORE CHECK 0.07 EMERGENCY. Shop: bought Hack $6 (only affordable scorer; Tribe $8 was $1 short). Skipped Small (Skip Tag $5, avoid rent/perish tick), skipped Big 1500 (Rare tag; chosen to concentrate on one boss hand). Window: only 1 club in the opening hand, 3 diamonds debuffed, no 2000-point hand available (flat hands 50-170); dug for a club flush (2 discards then cycled 2 non-club plays), ended 117/2000.

## Post-mortem

Binding constraint: scaling. At ante 2 my typical hand was ~150 (Two Pair L1, one conditional +mult joker) against a 1000/1500/2000 ante; the only big hand was a 5-club Flush (1482) that needs a lucky draw. With $1-7 the whole time I could not buy a real scorer (Tribe $8 was $1 short at the key shop).

Decisions I would change:
1. Ante 1 shop 1: took Gluttonous (perishable, clubs only, 5 rounds) for $1 instead of the Buffoon pack ($4). It carried ante 1 (the club flush cleared the Hook) but gave no permanent engine; at ante 2 I had a 3-round perishable and one 2-5 retrigger.
2. Ante 1 shop 2 ($4): left with $4 after passing a $5 eternal Banner. With $4 the Arcana pack or Empress did nothing; I think holding was fine, but the ante-2 shop then had $7 vs Tribe $8: selling Gluttonous ($1) would have bought a Flush-gated x2, which together with a flush plan was still < 1000.
3. Skipping the Ante-2 Big for the Rare tag was a pure gamble (tag pays only in the shop AFTER the boss). Skipping Small for the Skip tag was fine. The alternative (play Big 1500, then shop with ~$10) was also ~5%; the run was already lost at the ante-2 shop (ratio 0.07).

Reusable rules (if-then):
- IF Gluttonous (+3/club) is your only +mult joker THEN only a 5-club flush (~1500) scales; any other hand is ~100-250. Do not count on it for a 2000 blind.
- IF a boss debuffs diamonds (Window) and 3+ of the 8 dealt cards are diamonds THEN the effective hand is 5 cards: dig early; cycling by playing non-key cards after discards run out gave P~0.58 of 2 more clubs but the flush still scores <2000 without retrigger/xMult.
- IF Skip tag is Rare and the next stop is the boss THEN the Rare tag pays only after the boss: it does not help clear this ante; value it only if you can already clear the boss.
- IF you are at ante 2 with 0 permanent scorers, $7 and a $8 conditional xMult (Tribe/Order) in the shop THEN sell the rental ($1) to afford it only if you also own a flush plan; otherwise nothing at this price saves the run: the decision that mattered was ante 1 (buy permanent +mult over a perishable rental).

Advisor/CLI defects:
- shopadvise BUY Hack (score 120, "PLUS retrigger") at ante 2: Hack does almost nothing for Pair/Two Pair of high ranks (retrigger 2-5 only); SIM gave +0.09 but p(next 3 blinds) was 0.31, still an EMERGENCY. No better alternative was affordable.
- Solver at The Window (round p 0.45) kept counting debuffed diamonds as keepers ("keep QD 9S 7C", "keep JD TS 7C 6H") and gave p ~0.42 for a 2000 blind from flat hands (est ~165); the real chance was a few percent (needs a 5-club flush). p was badly overestimated under suit-debuff bosses.
- advise rule pick under Window discarded 9S while keeping debuffed cards, then said "keep Two Pair" while discarding one of its pairs (confusing PACE lines).
