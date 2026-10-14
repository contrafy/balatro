# Run WC7ZJRHM (port 7817, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Needle (2598/9000)

Ante 1 (Foil/Investment/The Pillar 600, $4): Small: 2P KKJJ 120, Straight T-6 280. Shop $5: no joker, Buffoon -> Misprint{PERISH,RENTAL} (SIM 0.81 vs Walkie Talkie 0.41). Big: Flush H 1271 one-shot. Pillar: Flush S 285, 2P 4422 608.
Ante 2 (Handy/Foil/The Mouth 2000, $7): EMERGENCY 0.07 -> Scary Face{E} $4. Skipped Small (Handy +$5; projected 452 vs 1000). Big: Trips 666 720, FH AAA77 870. Shop: nothing (Jupiter, 8 Ball{R}). Mouth: locked Two Pair AAJJ 366 (Misprint roll ~1), disc 5, QQTT 3000 (roll 23).
Ante 3 (Orbital(Trips)/Economy/The Tooth 6400, $15): EMERGENCY 0.04. Buffoon -> Zany (Astronomer{E} barred), Jolly{PERISH} $3, Temperance +$3. Skipped Small (Orbital: Trips L1->L4) and Big (Economy $11->$22) so Misprint (1 round left) fought the boss. Tooth: disc 4 -> Trips 777 5550 (kept QQ over FH 777QQ, solver 0.99 vs 0.91), Pair QQ 1530. Misprint perished, sold.
Ante 4 (Rare/D6/The Needle 9000, $22): EMERGENCY 0.10. Buffoon -> Arrowhead{RENTAL} (Golden{E} barred), Celestial gamble deferred, 1 reroll -> Throwback{RENTAL} $1 at x1.75 (3 skips already): sold Arrowhead to keep one rental, bought Throwback. Celestial -> Mercury (no Venus/Uranus). $9. Skipped Small (Rare) and Big (D6) -> Throwback x2.25 (override of `b blind` advice). Needle: 77 + junk, disc 5 keep AD QC 8C, drew QS JS, disc 5 keep QQ+JS (solver 0.30), missed the 3rd Q -> Pair QQ 2598/9000. LOSS.

## Post-mortem

Binding constraint: scaling + boss. No permanent scorer until ante 3 (Misprint{PERISH,RENTAL} bridged antes 1-3 on dice
rolls: 366 and 3000 at The Mouth), so the ante-3/4 shops were spent on flat jokers (Zany, Jolly) and the first xMult
(Throwback) only arrived in the ante-4 shop. My real engine was Trips L4 (Orbital tag) + Zany + Jolly + Scary Face: it
needs a face trips to reach the Needle's 9000 in ONE hand (pre-xMult need 4000 at x2.25: KKK/QQQ/JJJ = 6090; 777 = 3219,
AAA = 3567, two pair QQJJ = 1800). Only ~15-30% of Needle deals make a face trips, so the boss was mostly a coin I lost.

Decisions I would change:
1. Ante 4 blind select: I skipped Small AND Big into The Needle (Throwback x2.25, no shop). shopadvise had the Small at
   1.01x (13% loss bucket); playing it would have bought one more shop (a Venus makes any 7+ trips clear the Needle at
   x2.0, or Mr. Bones/Luchador), then skip the Big. The Throwback skip plan needs the boss beaten by 1.6x (Needle is a
   handicap boss); I was at ~0.3x per-hand probability and skipped anyway.
2. Ante 4 shop order: the Celestial pack gamble ($4, gave Mercury) before knowing the Needle math; $4 kept + the Small's
   shop might have bought Venus directly.
3. The Mouth: locking Two Pair with a Misprint scorer (0-23 mult) was high variance; it scored 366 on hand 1.

Reusable rules (if-then):
- IF the boss is The Needle, THEN compute "one-hand need / your xMults" and list which hands reach it with your levels and
  jokers (e.g. only face trips); IF fewer than ~half your deals make such a hand, THEN do NOT skip both Small and Big:
  play the Small (if its ratio is >= 1.0x) for one more shop and buy the level/counter (Venus for a Trips engine, Mr.
  Bones, Luchador, Director's Cut) that turns a common hand into a clear.
- IF an Orbital Tag levels a hand your gated +mult joker fires on (Zany on Trips), THEN that hand is your main hand:
  buy its planet over the advisor's "main hand" label, which still said Two Pair from 4 early plays.
- IF Throwback appears as a $1 rental while you already pay rent on a chips-only joker before ante 5, THEN sell the old
  rental and buy Throwback in the same shop (skips already made count: it arrived at x1.75 here).
- IF your only mult source is Misprint, THEN under The Mouth lock the type with the most outs to repeat (Pair), not Two
  Pair: a low roll on the lock hand leaves you needing two more made Two Pairs.

Advisor/CLI defects:
- shopadvise main hand stayed "Two Pair (L1, 4 plays)" after the Orbital Tag made Trips L4 with Zany: the Celestial pack
  advice said "take Uranus" and called Mercury/Venus off-hand; Trips was the strongest hand by 2-3x.
- Needle solver lines (p 0.13-0.15 on the opening hand) kept AD 8C for a "pair draw" although no pair except a face
  trips could clear; the useful keep (faces only) was not distinguished.
- Blind select advice at ante 4 said "do not skip ... take the shop" without quantifying the Needle one-hand odds;
  with Throwback owned the skip plan text did not appear (rounds < 1.6x), which was correct and I overrode it.
Bridge issues: none (58 steps, no rejects).
