# Run GWQANQ4Y (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (483/1500)

Ante 1 (Boss/Skip/The Psychic 600, $4): Small: 2P 99 77 104 + 2P KK66 104 + Straight Q-8 308. Shop $4 (no scorer; Banner{P,R} barred): Buffoon -> Crazy Joker{E} (SIM 0.32 vs Hanging Chad{E} 0.19). Big: 2 disc digs, Straight J-7 1184 one-shot. Shop $6 (Erosion{E} SIM -0.01): Celestial -> Venus (no Saturn/Uranus). Psychic: 2 disc, Straight A-T 1296 one-shot.
Ante 2 (Orbital/Ethereal/The Mark 2000, $9): EMERGENCY 0.21 -> Blue Joker $5 (SIM +0.15), Saturn $3 (Straight L2, SIM +0.10), $1. Small 1000: 2 disc, Straight K-9 3553 one-shot. Shop $3: Hallucination / Splash{P,R} / Arcana packs only, left. Big 1500: disc KK J 9 keeping 6432 (p 0.88), disc 9 8 6 4 keeping 6432 again (p 0.87), dig High TC 4 3 2 keeping 7643 (p 0.69), Pair 77+2 fillers keeping 7643 (p 0.45, over Trips 777 675 at 0.37): never drew a 5. Forced 2P JJ77 220. 483/1500. GAME OVER.

## Post-mortem

Binding constraint: scaling on anything but a Straight. The only mult source was Crazy Joker{ETERNAL} (+12 mult on a
Straight) plus Straight L2: a made Straight scored 1184-3553 (each blind before the Big was a one-shot), any other hand
scored 170-240 (Blue Joker's ~+90 chips on base mult 2). The ante-2 Big needed 1500, which only a Straight reached, so
the round became four consecutive draws to one rank (a 5, 4 outs each time) and missed all of them. Six shops offered zero
permanent +mult jokers (Midas, Banner{P,R}, Erosion{E}, Blue, Splash{P,R}, Hallucination), so the run never got a
pair-family floor.

Decisions I would change:
1. Ante 2 first shop ($9): Blue Joker ($5) then Saturn ($3, -> $1). Saturn made Straights bigger but the build's problem
   was the non-Straight rounds; keeping $4 would have given $6 at the Small shop (which had no scorer) = one reroll for an
   any-hand +mult joker. Small edge, but a planet for a draw-only hand does not fix a 200-per-hand fallback.
2. Ante 1 Buffoon: Crazy{E} vs Hanging Chad{E}. Crazy was right for antes 1-2 (it carried 4 one-shots) but it is the reason
   the deck had no fallback: with a gated first scorer, every later dollar must go to an ungated +mult first.
3. Big Blind hand 1 (KS KH JS 9S 6C 4C 3C 2S): I followed the solver (break KK, keep 6432, p 0.89). With a 4-out gutshot
   as the only clearing line it was probably still right; the real error was arriving at 1500 with only one clearing hand type.

Reusable rules (if-then):
- IF your only +mult joker is hand-gated (Crazy/Droll/Zany...), THEN treat yourself as having 0 scorers for the any-hand
  floor: the next shops buy an ungated +mult joker (or Buffoon pack) BEFORE that hand's planet, and keep $5+ for a reroll
  when the shop shows none.
- IF a blind can only be cleared by one draw (a gutshot straight, one rank, 4 outs), THEN expect it to fail about half the
  time across a whole round even when the solver prints 0.85-0.9 at the first discard; plan the shop before it so that
  a second hand type can clear (here Trips L2 777 = 675 was the next best, half of what was needed).
- IF a Buffoon pack at ante 1 offers two ETERNAL jokers, one gated (Crazy) and one weak-now (Hanging Chad), THEN the
  gated one wins the next 3 blinds (SIM 0.32 vs 0.19) but locks the main hand; buy the any-hand +mult as soon as it shows.

Advisor/CLI defects:
- Solver P(clear) on straight draws looked optimistic in this round: 0.88 -> 0.87 -> 0.69 -> 0.45 -> 0 on a line that
  needed one specific rank (four 5s) through 2 discards + 2 dig plays. One sample, so [INFERENCE]: check calibration of
  gutshot-only rounds (the made-hand fallback projected ~700 of 1500).
- shopadvise at ante 2 ranked Saturn (main hand = Straight after 3 plays) as MAIN SCALING while warning earlier that no
  joker scores on a plain Pair; with a gated build the any-hand floor should outrank the gated hand's planet (or the
  planet should keep $5 for a reroll when the next shop is the $0 Small).
Bridge issues: none (37 steps, 0 rejects, 0 CLI aborts).
