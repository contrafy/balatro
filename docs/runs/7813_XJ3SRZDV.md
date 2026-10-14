# Run XJ3SRZDV (port 7813, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 boss The Mark (1058/6400)

Ante 1 (Rare/Investment/The Psychic 600, $4): Small: disc 3 -> Broadway straight 324 (Straight L1). Shop $6: Buffoon pack -> Joker +4 (over Gluttonous). Big: disc 3, Flush 552. Shop $8: Saturn $3 (Straight L2). Psychic: 2 discs for a Q, Pair T 180 then K-high straight 1199 = 1379/600.
Ante 2 (Double/Double/The Head 2000, $12): Abstract{ETERNAL,RENTAL} passed, 1 reroll ($5) found only Rough Gem{P}/Showman{E}; Jumbo Celestial -> Saturn (L3), $1 left. Small 1000: Full House QQQJJ 720 + straight 9-5 1750. Big 1500: disc for 2-6 straight 1540 (40 over). Shop $8: Celestial -> Saturn (L4). Head: 6-T straight (debuffed TH) 2550/2000.
Ante 3 (Garbage/Holo/The Mark 6400, $11): Mega Celestial $8 -> Saturn (L5 150x16) + Jupiter. Small 3200: straight 5-9 3700. Buffoon -> Odd Todd{P}. Big 4800: straight 9-5 5560. Shop $7: Jumbo Buffoon -> foil Crazy Joker{P} (+12 mult on Straight). Mark 6400: straight draw needed a 6 (4 outs); discarded 4+4 cards, then two cycle plays (pair 44 408, junk 325) never found the 6, last hand gambled a face-down Jack (1/3) for 7-8-9-T-J: missed, 1058/6400. Died with $1, jokers Joker +4 / Odd Todd / Crazy Joker.

## Post-mortem

Binding constraint: no scaling and no money. All three antes were cleared by one lucky Straight per blind (Straight L5 = 150x16 was a real engine, 3.7-5.5k per hand), with ONE flat +4 joker. I never owned an xMult, never had more than $12 at a shop, and every shop's cash went into packs (Celestial x3, Buffoon x3). At ante 3 the straight engine topped at ~5.5k-8k and needed exact draws (a single missing rank, 4 outs) on every blind; The Mark turns every J/Q/K face-down so the draw was unreadable and the 6 never came (3 draws of 4 cards at p~0.35-0.43 each).

Decisions I would change:
1. Ante 2-3: I spent all money on Saturn packs (4 levels) instead of keeping $10+ for a joker reroll; the Straight engine is draw-dependent (needs exactly 1-2 ranks per blind) while a flat joker raises every hand type. 3 jokers only at ante 3, 2 of them perishable.
2. Ante 3 Big: I played 4800 with a 1-card margin on hands (est 5560 vs 4800) for $6; skipping it for the Holographic tag + not ticking the perishables (Odd Todd, Crazy Joker) would have given a free holo joker and kept both bridges for The Mark (they ticked once for nothing). I followed 'never skip the Big when broke'; here the straight engine could not carry two blinds.
3. The Mark: I discarded 4 cards twice to chase a 6 and drew face-down faces back. With Flush L2 and 5 spades in the first hand, nothing; but holding 9D8S7S5S + the 2 face-downs was a lower-p draw than I computed because new face cards come back face-down and unreadable. The better line: play the first made 4-hand (e.g. Flush/straight draw) sooner... in truth nothing here clears 6400 without the exact straight; the real fix is scoring jokers by ante 3.

Reusable rules (if-then):
- IF the only engine is a Straight/Flush and each blind needs exactly 1-2 missing ranks, THEN it will fail by ante 3-4 (it did 0/7 now): by the ante-2 shops put cash into a reroll for a flat +mult scorer rather than a 3rd/4th planet.
- IF you hold Straight L4+ and the boss is The Mark, THEN keep the straight draw in NUMBER cards only and expect face cards to come back face-down: never count on a face-down card being a specific rank (1/3 for a J).
- IF a blind's estimate is within 10% of the need (est 5560 vs 4800, 1540 vs 1500) and you can skip the next blind for a joker tag, THEN skip: margins that thin die one blind later.
- IF money is $1-$8 for three straight shops, THEN you are not buying jokers; stop buying packs that only level a draw-dependent hand and save to $10+ for the reroll.

Advisor/CLI defects:
- shopadvise at ante 2-3 ranked 'Celestial pack' / 'Saturn' while the same shop printed SIM NOISE (all options < 0.15); it never says that a straight-main build with 1 flat joker is a dead end beyond the BUILD warning. Not a bug per se.
- `advise` under The Mark showed Straight draws using face-down cards as if known ('keeping face-down [1, 2]: under The Mark they are face cards') but with draw EV 3638 (below need 6400) it still advised discards; SIM/solver treat the face-down draws as visible, so p (0.9+) was overconfident (the run lost the blind it called p~0.90-0.97).
- Solver p for the Big (0.90, 5560 est vs 4800) vs the Mark boss: no p printed at ante 3 boss; 'SCORE CHECK' read 0.17 for the whole ante yet showed est as a high-card estimate (372-1040) not the Straight L5 hand (5560): ratio ignores a made-hand main engine, so EMERGENCY wording was misleading.
