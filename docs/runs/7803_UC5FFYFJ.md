# Run UC5FFYFJ (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Wall (4142/12800)

Ante 1 (Skip/Economy/The Window 600, $4): Small Flush clubs 300 one-shot. Shop $6: Jolly{PERISH} $3 (SIM 0.96 vs 0.01). Big: 2P 8877 500 one-shot. Shop $9: left (Celestial +0.06 = noise, Four Fingers{E}). Window: disc, 2P JJTT 600.
Ante 2 (Handy/Polychrome/The Club 2000, $17): EMERGENCY 0.07: Wily{E} $4 (SIM +0.30), reroll -> Abstract{E,R} $1 (passed: eternal rental). Small 1000: 2P 560 + Straight 220 + 2P 600. Shop $9: reroll -> Juggler{R} (passed). Big 1500: 2P 520 + 2P 440 + 2P 600. Shop $8: reroll -> The Idol{P}/Riff-raff{P} $6 with $3 left. Club: disc x2, FH 444JJ 2064 one-shot. Jolly perished.
Ante 3 (Polychrome/Double/The Wall 12800, $10): sold Jolly, reroll -> Raised Fist $5 ($1 left). Small 3200: disc, Flush 1580, Straight 1036, disc 22, Straight 3-7 holding TD 9D 8D 1100. Big 4800: disc 4 -> KKK TTT, Trips KKK holding TTT 3680 + Trips TTT 3040. Shop $6: Clever $4. Wall: disc (solver straight draw), disc -> 999, 1-card dig, Trips 999 3611, Pair 55 440 = 4142/12800. GAME OVER.

## Post-mortem

Binding constraint: SCALING with no money. The ante 1-2 shops offered one usable +mult joker (Jolly, perishable) and
otherwise Wily{E}, Hanging Chad{P}, Four Fingers{E}, Superposition{E}, Cartomancer{E}, Abstract{E,R}, Juggler{R}; no
Buffoon pack after the first shop. Income was $5-8 per shop (Red Stake $0 Smalls), so every shop was EMERGENCY and spent
to $1-4. Entering ante 3 with Wily (+100 on trips), Raised Fist and Clever (no xMult, all L1 hands) against The Wall
(12800 = x2 ante-3 boss) was a ~2-4k/hand build against a 4.3k/hand need: the round was unwinnable on the simulation
before the last two hands.

Decisions I would change:
1. Ante 2: three rerolls ($15) at $8-13 wallets (Small shop, Big shop, ante-3 shop 1). Two whiffed; the Big-shop reroll
   revealed The Idol $6 when I had $3 left. Without the Small-shop reroll I would have had $8 there. GOLD_ANALYSIS rule 7
   (reroll only with $20+ left) is right even in EMERGENCY: at < $10 the reroll eats the money that buys what it shows.
2. Ante 1 shop 1: Jolly{PERISH} $3 over the Buffoon pack $4. SIM was clear (+0.63 vs +0.22) and Jolly carried ante 1-2,
   but it perished exactly at the ante-3 jump; a permanent pick from the pack would have been worth more at ante 3.
3. Ante 3 Wall, hand 1: I followed the solver's straight-draw discard (p 0.11, n=64) that broke JJ22 over the rule
   pick (p 0.02). Both lines were < 0.15 (noise); the round was lost in the shops, not here.

Reusable rules (if-then):
- IF you own Raised Fist, THEN the cards you HOLD matter: play low cards (as the hand or as fillers) and keep high cards
  held; its mult is 2x the lowest held card (face = 10, Ace = 11). Here a Straight 3-7 holding T 9 8 scored 1100 vs the
  Flush 710 holding a 3; Trips KKK + 2 low fillers holding TTT scored 3680. Before a last hand, discard the low cards you
  will not play (22) so the held minimum rises (568 -> clears).
- IF Raised Fist is owned, THEN low pairs are good pairs: play 22/33 as the made hand and hold the face cards.
- IF your ante-2 wallet is under $13, THEN do not reroll: a reroll at $8-13 leaves $3-8, below the $6 the revealed joker
  costs (The Idol $6 with $3 left).
- IF The Wall is the ante-3 boss and the ante-3 SCORE CHECK is < 0.3 with 0 xMult, THEN the boss is a ~10% coin flip
  at best: every ante-3 shop must buy score (planet for the main hand, any +mult), not utility.

Advisor/CLI defects:
- Ante 2 shop: after buying Wily{E}, `shopadvise` printed the same SCORE CHECK (~520) and "Scorers still alive next
  ante: 0", while the SIM baseline jumped 0.07 -> 0.74; the score check ignores trips-gated chip jokers entirely.
- Ante 1 boss (The Window), first discard with best hand High Card 16 vs 600: SOLVER printed `p >=0.99 (calibrated,
  n=100)` for three different discard lines; it cleared, but p 0.99 from no made hand looks overconfident.
- Ante 3 Small last hand: `advise` listed only the Flush (568, holding a 3) and proposed discarding 22; after the
  discard, the best play was a Straight 3-7 holding T98 (1100) that I found via `sel`. The candidate list ranks by type,
  not by what is held for Raised Fist.
Bridge issues: none; 60 steps, no rejects.
