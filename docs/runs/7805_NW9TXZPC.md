# Run NW9TXZPC (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Wheel (49868/50000)

Ante 1 (300 Holo / 450 Coupon / The Psychic 600, $4): Small: heart Flush 284 + Pair J. Shop $5: Buffoon over Green Joker -> Banner{RENTAL} (other: Red Card). Big: Pair Q 180, Two Pair JJ44 216 (overrode flush-draw discard: Ace High w/ Banner already cleared the rest), Pair T. Shop $2: sold Banner, Sly $3. Psychic: disc 5 around 99 -> FH 33399 468, Pair K 160.
Ante 2 (1000 Investment / 1500 Garbage / The Club 2000, $6): Mystic Summit $5. Skipped Small for Investment. Big: 2 discards then Two Pair QQ88 1802 one-shot. Shop $7: left. Club: 2 discards -> FH 777JJ 2166 one-shot. $40 after Investment.
Ante 3 (3200 Orbital / 4800 Foil / The Flint 6400, $40): 2 rerolls -> Half Joker{ETERNAL} $5. Small: 2 discards, Trips 666 3724 one-shot. Shop: The Duo{RENTAL} $1, Jumbo Celestial -> Mercury (Pair L2). Big: Pair T 7220 one-shot. Shop: Jumbo Celestial -> Mercury (Pair L3). Flint: Pair J 6660 one-shot.
Ante 4 (9000 Buffoon / 13500 Top-up / The Goad 18000, $32): Jumbo Celestial (no Mercury) -> Venus, reroll, Even Steven $4. Skipped Small for Buffoon tag (Mega: Mad Joker; rest rental/perishable junk). Big: kept 66+55 through discards, Pair 6 9588 + Pair 5 7800. Goad: Pair 6 9588 + Trips 333 8720 (over advisor's Pair 8 with 16 margin). $27.
Ante 5 (25000 Skip / 37500 Orbital / The Wheel 50000, $27): Mercury $3 (Pair L4), reroll, sold Mad Joker, holo Dusk{ETERNAL,RENTAL} $1 (+10 mult every hand, final-hand retrigger), Celestial -> Mercury (Pair L5). Small: Pair T 16520 + Pair 4 15104. Shop $13: left. Big: Pair K 14280, no pair -> Straight 2050 (solver p 0.46), final Pair T with Dusk 21440 vs 21170 needed. Shop $12: left (Arcana x2, Lovers, Pluto; advisor LEAVE on the $10 floor). Wheel: 2 discards, Pair 6 15576, Pair 3 12852 (+filler), final Pair T with Dusk 21440 vs 21572 needed: 49868/50000. GAME OVER.

## Post-mortem

Binding constraint: SCALING (one xMult). Build was Pair L5 + Sly (+50 chips) + Mystic Summit (+15) + Half Joker (+20)
+ Even Steven (+4/even card) + holo Dusk (+10, final-hand retrigger) + The Duo (x2). That made ~13-16.5k per normal
pair and ~21.4k on a Dusk final hand, i.e. ~50k per round at best, exactly the ante-5 boss. Only one reliable xMult
(The Duo, rental) was offered all run; Half Joker and Summit carried antes 2-4 cleanly (every blind one-shot or two
hands through ante 4). Money was never the problem until the end ($40 at ante 3 from the Investment tag).

Decisions I would change:
- Ante 5 boss shop ($12): I left to keep the $10 floor for an ante-6 xMult. The round projection (15.5k + 13k + 21.4k
  ~ 50k) was at the boss line; any score item would have decided it (lost by 132 = 0.3%). Two $4 Arcana packs
  (Empress/Hierophant/Strength on an even pair rank) or even the money for a re-level was worth more than the next shop.
- Ante 4 first shop: rerolled ($5) and took Venus from a Jumbo Celestial; $11 that bought nothing for Pair. A plain
  Celestial in a later shop (Mercury = +15 chips +1 mult, ~+8% per hand) would have covered the 132 alone.
- The Wheel hand 2: Pair 3 + KH filler. Fine per solver, but the whole round was decided by needing Pair T on the
  Dusk final to be 132 bigger - no in-round fix existed once the shop was left.

Reusable if-then rules:
- IF the last shop before a boss shows your best 3-hand round (normal pair, normal pair, best final) within ~10% of the
  boss need, THEN spend every dollar on anything that adds score to the main hand (main-hand planet, Celestial, Arcana
  for Empress/Hierophant/Glass); the money floor only matters if you survive, and the next ante's xMult cannot be
  bought from a game-over screen.
- IF you own Half Joker (+20 at <=3 cards), THEN play Pair + 1 filler (3 cards) to draw an extra card without losing
  the +20, and value Pair levels above Trips: Pair L5 + Half beat Trips L2 every time here.
- IF you own Mystic Summit, THEN burn both discards before the first play every round (all 3 hands then carry +15);
  keep made pairs through the discards and dump unknown/odd cards.
- IF you own Dusk (final-hand retrigger), THEN save the highest EVEN pair (with Even Steven) for the final hand: the
  retrigger doubles card chips and per-card mult (Pair T: 16.5k normal -> 21.4k final).
- IF a holo/poly edition joker is offered for $1 (even eternal/rental) while you have 1 xMult and are below the next
  boss pace, THEN buy it: holo Dusk added +25% to every hand and was the difference in the ante-5 Big Blind.

Advisor/CLI defects:
- shopadvise SCORE CHECK ignored Mystic Summit through ante 4 ("one Pair (KK) ~160" at ante 2-3 while real pairs
  scored 1360-7220), so EMERGENCY was printed every shop and carried no signal; from ante 5 it says "Summit active".
- shopadvise in the last shop before The Wheel: ADVICE LEAVE ($12, Arcana packs passed for "would leave $8, below the
  $10 floor") while the score check showed the boss pace was not covered; the floor should not apply then.
- Blind-select ADVICE at ante 4 said "do not skip: no free joker slot for the tag's jokers" with 5/6 jokers (1 free)
  for a Buffoon tag (Mega pack, 2 picks).
- shopadvise ranked holo Dusk{ETERNAL,RENTAL} $1 at 27 (below Celestial 76) and never mentioned the holo +10 mult.
- advise at the ante-5 Big ranked the 2050 Straight correctly via SOLVER (p 0.46) - the solver lines were accurate
  and est was exact on every hand (21440 predicted and needed-132 confirmed).
Bridge issues: none; 112 steps, no rejects.
