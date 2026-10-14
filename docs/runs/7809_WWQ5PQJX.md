# Run WWQ5PQJX (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (12555/13500)

Ante 1 (Foil / Skip / The Pillar 600, $4): Small: solver flush disc -> club Flush 304 one-shot. Shop $6: Buffoon $4 (over Greedy{PERISH} $5) -> Mad Joker{PERISH}. Big: 2 discards -> Two Pair KKQQ 720. Shop $8: left (override reroll to $3). Pillar: Two Pair AA22 552 + 9988 648.
Ante 2 (Negative / Orbital / The Head 2000, $15): EMERGENCY 0.33. Reroll -> Droll{RENTAL} $1; Small: Full House 999AA 1246 one-shot. Shop $9: reroll -> Misprint{ETERNAL} $4, sold Droll (rent at $0). Big: Broadway 1053 + Full House 22233. Shop $6: Smiley{ETERNAL} $4. Head: Broadway (3 faces) one-shot 2000+. Mad perished.
Ante 3 (Juggle / Holo / The Mark 6400, $11): shop: sold dead Mad, Mystic Summit{PERISH} $5, Justice $3. Small 3200: 2 discards -> FH 999QQ est 3045, used Justice on QD (Glass) -> 3828 one-shot. Shop $5: Strength $3. Big 4800: Two Pair AAKK 2604, Strength JC->Q + 8H->9 made FH 999QQ for the rest. Shop $7: Odd Todd{ETERNAL} $4. Mark: kept face-downs (override), AA + 3 sorted face-downs 4340, 44 + 3 face-downs 2160 -> 6500.
Ante 4 (Polychrome / Holo / The Club 18000, $9): polychrome Hallucination{ETERNAL,RENTAL} $1 (x1.5, only multiplier offered). Skipped Small 9000 for Polychrome tag (keep Summit alive for Big+boss, avoid -$3 rent). Big 13500: diamond Flush (Glass Q, Summit, x1.5) 6525, dig High J 990, final Two Pair 7755 needed Misprint >=7 (~71%), rolled ~3: 5040 -> 12555/13500. GAME OVER.

## Post-mortem
Binding constraint: SCALING. Every hand type stayed at L1 the whole run (no planet bought, no Celestial pack) and the only
multiplier (polychrome Hallucination x1.5) arrived at ante 4. The build was flat: Misprint (avg +11, random), Smiley
(+5/face), Summit (+15, perishable), Odd Todd (+31 chips/odd). Typical hand at ante 4 was ~4-6k against 4.5k/hand needed
for the Big; the run came down to a Misprint roll. Money was the secondary cause: $0-9 every shop (Black Deck Gold pays
~$9-12 per ante), so no $6-8 xMult would have been affordable even if offered.

Decisions I would change:
1. Ante 3 Small: I used Justice on QD to one-shot a blind that was already safe (FH 3045 + 2 more hands vs 3200) for +$2.
   Glass only doubled the pre-joker mult (est 3045 -> 3828, x1.26, not x2). Held as a rescue, Justice on a K in the
   final KK77 / 7755 hand of the ante-4 Big would have added ~+25% (5040 -> ~6300 > 5985 needed) and saved the run.
2. Ante 2: Droll{RENTAL} $1 bought and sold one shop later ($1 + no gain); the $5 reroll before it found nothing. Keeping
   $15 for interest and the Smiley/Misprint shops would have left ~$5 more for a planet.
3. Ante 4 Big: I could have bought the $4 Celestial pack (Hallucination also gives 1/2 tarot per pack) instead of keeping
   the $8 floor; one Uranus level (+20 chips, +1 mult) on Two Pair 7755 = 188 x 37.5 ~ 7050 > 5985.
4. The ante-4 Small skip was neutral: it kept Summit alive for the Big (needed) but cost one shop at ~$8.

## Reusable rules (if-then)
- IF a round already clears without your rescue tarot (made hand est + later hands >= need), THEN keep the tarot; spend
  it only on the forced final hand of a round you would otherwise lose. +$2 of saved hands is never worth it.
- IF your mult is mostly flat joker +mult, THEN a Glass card (Justice) is worth ~x1.2-1.4, not x2: it multiplies only the
  base mult and per-card mult scored before jokers. Rank Glass below any joker xMult and below a main-hand planet.
- IF The Mark is the boss and you own face jokers (Smiley/Scary/Photograph), THEN never discard face-down cards (they are
  always J/Q/K). 5 face-downs always contain two pair or better. The hand is auto-sorted by rank, so 3 ADJACENT
  face-downs hold a pair ~92% of the time: play your best visible pair + 3 adjacent face-downs as Two Pair.
- IF a final hand depends on Misprint, THEN compute the roll threshold yourself (score = chips x (flat mult + roll) x
  xMult): the solver uses a fixed roll of 6 and reports p_clear 0.00 for a line that clears ~70%.
- IF you are at ante 3-4 with every hand at L1 and the shop has a $3-4 main-hand planet/Celestial pack, THEN buy it even
  below the $8 floor: chips were my small factor (60-170 chips vs 35-55 mult) and a level is +20 chips permanently.

## Advisor/CLI defects
- `shopadvise` (ante 2, $10, 0 scorers alive next ante) ranked Droll{RENTAL} 95 -> BUY; right after the buy, the next
  `shopadvise` said "SELL -> b sell 2 (Droll is a RENTAL and not a core scorer)". Buy and sell rules contradict.
- `advise` under The Mark with Smiley Face owned advised `disc 1 2 3 4 5` / `disc 3 4 5 6 7`, i.e. discarding the
  face-down J/Q/K cards that Smiley pays +5 each; its final-hand advice was `play PAIR 7 8 ...` (44 + fillers, est 414)
  while 44 + 3 face-downs scored 2160 (full house). Face-down cards should be modelled as "unknown face, J/Q/K".
- Solver treats Misprint as a fixed +6: final-hand 7755 got `p_clear 0.00` though it cleared on any roll >= 7 (17/24).
  It should sample the 0-23 roll.
- Solver p_clear is overconfident at ante 1-3 with no jokers (0.93-0.98 on 2000-3200 needs), and once suggested
  `disc 5 7 8` keeping a useless 8C over discarding all 4 non-pair cards.
- `play ... HIGH` est for Glass/face cards fine; `play` est for face-down hands is meaningless (2392 vs 4340 actual,
  644 vs 2160) - expected, but `advise` should not base the ADVICE line on it.
- My own junk action: `sort rank` at step 64 was a no-op (hand already sorted by rank; face-downs keep sort order).
Bridge issues: none; 77 steps, no rejects.
