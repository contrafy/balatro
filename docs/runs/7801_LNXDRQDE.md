# Run LNXDRQDE (port 7801, claude-fable-5-1) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (33982/37500)

Ante 1 (300 Foil / 450 Double / The Hook 600, $4): Small jokerless: solver digs (disc x2, High K dig) -> diamond Flush 312 one hand. Shop $5: Jolly $3. Big: Pair QQ 300 + Pair 55 200. Shop $7: override LEAVE -> Spectral $4 -> Wraith -> The Duo (x2 on Pair, no sticker), $0. Hook: Trips KKK 1320 one-shot.
Ante 2 (1000 Handy / 1500 Handy / The Flint 2000, $7): Mad Joker $4, ordered left of Duo. Small: 2P TT44 1920 one-shot. Shop $5: Popcorn{PERISH} $5 (+20 decaying; override floor). Big: 2P 8866 3840 one-shot. Shop $6: Buffoon $4 -> foil 8 Ball{RENTAL} (+50 chips). Flint: Pair 88 3550 one-shot (foil chips beat the halved base).
Ante 3 (3200 Rare / 4800 Boss / The Psychic 6400, $6): Temperance buyuse $3 -> +$10 (sell values). Skipped Small for Rare Tag. Big: 2P KK88 6784 one-shot. Rare tag -> Baseball Card $0 (x1, 0 Uncommons; took it for the $4 sell). Mega Buffoon $8: sold Baseball+Popcorn, took Astronomer{PERISH} + Swashbuckler (+12). Free Venus (Trips L2), free Celestial -> Mercury (Pair L2). Psychic: disc 4 around JJ66 -> FH JJJ66 8976 one-shot.
Ante 4 (9000 Meteor / 13500 Buffoon / The Mouth 18000, $22): free Earth (FH L2) + free Celestial (Jupiter; no pair planet). 2 rerolls ($11) -> sold Astronomer, Abstract{ETERNAL} $4 (+18). Skipped Small for Meteor: Mega Celestial -> Uranus (2P L2) + Earth (FH L3). Big: Flush 4930 banked, 2P JJ55 11760. Shop $14: Jumbo Celestial $6 -> Uranus (2P L3), passed Justice. Mouth: Pair lock JJ 7410, AA 7566 (TTT held), TT 7410 = 22386.
Ante 5 (25000 Orbital(Quads) / 37500 Economy / The Goad 50000, $11): SCORE CHECK 0.35, SIM p_next 0.10, no xMult in shop (Supernova{E}, Four Fingers). Jumbo Celestial $6 -> Uranus (2P L4 80x5) over Mercury, $5. Skipped Small (rent-broke: $5, $3 rent, Small pays $0). Big 37500: no pair dealt, disc 4 then disc 5 -> 2P 9944 15912, Pair KK 7410 (kept A Q J), last draw QQQ: Trips 10660 = 33982/37500. GAME OVER, $5, 1 xMult all run.

## Post-mortem

Binding constraint: SCALING, caused by MONEY. The Duo (x2, from a $4 Spectral Wraith at ante 1) was the only xMult the run
ever saw; in ~11 shop views, 2 Buffoon packs, 1 Mega Buffoon and 2 rerolls no second xMult appeared and I never held
$20+ to hunt one: the 8 Ball rental cost $3 x 9 rounds = $27 (foil +50 chips was 35-45% of my chips every hand, so I
never sold it), the Small Blinds paid $0, and ante 3-5 shops ran at $5-18. The engine topped out at Two Pair L4 ~16k /
FH L3 ~20k / Pair L2 7.4k at ante 5: the Big (37.5k) needs three ~12.5k hands, i.e. two Two Pairs and a Pair, and the
first deal had no pair at all, so both discards went into finding one.

Decisions I would change:
1. Ante 5 shop ($11): I bought the Jumbo Celestial (Uranus) for a guaranteed +17%. The Big needed +130%; only an xMult
   could do that. With p_next 0.10 the variance play (reroll $5, keep $6 for a cheap/rental xMult) was at least equal in
   EV and was the only line that could win the run. Levels do not fix a 2.3x gap.
2. Ante 4 second shop ($14): passing Justice was right, but I also could have sold 8 Ball there ($1, stops $3/round):
   with Abstract +18 and 2P L3, the chips loss (-40%) would have cost the Mouth. So the real mistake is earlier:
3. Ante 3 post-Big shop ($18): Mega Buffoon $8 for Astronomer (sold one shop later for $4) + Swashbuckler (+10). Net
   ~$4 for +10 mult and two free planets (Venus/Jupiter were off-type; Mercury/Earth useful). Keeping $18 and rerolling
   at ante 4 with $27 instead of $22 would have given one more joker view. Marginal either way.
4. Ante 5 Big hand 2: playing KK with fillers kept A Q J (solver 0.70). The draw was KH QS QH 7C 3H. A dig keeping
   KS KD AD JH would have made FH KKKQQ 20520 -> 36432, still 1068 short. The blind was lost at the shop, not at the table.
5. 8 Ball rental: taking it at ante 2 was right (it one-shot the Flint and carried antes 2-4). The error was never
   budgeting an exit: by ante 4 it had cost $18 and the sum of rent + lost interest was the price of one xMult.

What worked: Spectral $4 at ante 1 with one joker -> Wraith -> The Duo. Temperance buyuse for +$7 net. Discarding
around a made Two Pair at the Psychic (-> FH). Pair lock at The Mouth with TTT held as the guaranteed third Pair.
Meteor Tag skip at ante 4 (Uranus + Earth before the Big). Banking a made Flush that cleared its 1/3 share instead
of spending the last discard.

Reusable rules (if-then):
- IF ante 1 and you own exactly one joker and a Spectral pack costs $4, THEN buy it: Wraith (random Rare, money to $0
  when you have $3), Ankh (copy your joker), Hex (Polychrome it, nothing else to destroy) are all run-changing.
- IF Temperance is in the shop ($3) and your jokers' sell values sum to $7+, THEN `buyuse` it: it is pure cash (+$7
  here), whatever the advisor ranks it.
- IF a Buffoon pick is a foil/holo RENTAL scorer at ante 1-2, THEN take it (foil +50 chips doubled every ante-2 hand)
  but write the exit: sell it in the first ante-4 shop or when 2 other chip/mult sources exist; 9 rounds of rent ($27)
  is the price of an xMult.
- IF the ante-5 shop shows SCORE CHECK < 0.4 and no xMult, THEN do not buy levels: a level is +15-20%, the Big needs
  +100%+. Reroll ($5) once and keep $6+ for a rental/cheap xMult; only an xMult sighting changes the outcome.
- IF The Mouth is the boss and you hold a Pair plus Trips of another rank, THEN lock Pair with the pair + 3 fillers and
  keep the Trips: two of them are the guaranteed third Pair (7410 + 7566 + 7410 cleared 18000 with zero draw risk).
- IF The Psychic is the boss and you hold a made Two Pair with 2+ discards, THEN discard the 4 junk cards first: the
  Two Pair survives any draw and a Full House (4 outs) adds 40% margin.
- IF a skip tag pays NOW (Meteor = Mega Celestial) at ante 3-4 and your typical hand >= boss/2, THEN skip the Small:
  Uranus + Earth before the Big carried both ante-4 blinds.
- IF your Big Blind need is > 2.3x your typical best hand (37.5k vs 16k), THEN two discards spent on a pairless first
  deal lose the blind ~1/3 of the time; the fix is in the two preceding shops, not at the table.

Advisor/CLI defects:
- shopadvise "main hand" flip-flopped Pair <-> Two Pair every shop; planet picks printed "Uranus levels Two Pair (NOT
  your main hand Pair; a level elsewhere is mostly wasted)" while Two Pair was my most frequent clearing hand and
  Mad Joker's hand. The main-hand rule should count hands that cleared blinds, with Two Pair >= Pair when both fire
  the same jokers.
- Celestial pack advice: "Saturn levels a pair-family hand, the best fallback" - Saturn is Straight.
- shopadvise ranked Temperance 30 / LEAVE when it netted +$7 (sum of sell values $10 - $3). Rank it by that number.
- Rare Tag -> Baseball Card ranked 89 "XMULT(conditional, unreliable)" with 0 Uncommon jokers owned (x1). Same defect as
  7801_UX7FJYS3; it should count Uncommons and rank x1 as a $4 sell.
- Buffoon pack advice said SKIP (Astronomer + Swashbuckler) while my two weakest sellable jokers were a 2-round Popcorn
  (+8 -> +4 -> dead) and the x1 Baseball Card; "beats your weakest sellable joker" should value a perishing joker at
  its remaining rounds.
- Justice ranked 86 "RESCUE tarot" at ante 4: Justice does not change rank (not a rescue) and Glass x2 on a +46
  flat-mult build is ~+6% (card phase precedes joker +mult).
- Ante-5 shop SIM said buy Supernova -> p_next 0.00 (-0.10) and the baseline 0.10; consistent with the loss. The
  Jumbo Celestial was not SIM'd (packs are not simulated), so the only buy that mattered had no number.
Bridge issues: none; 91 steps, no rejects, every action settled first try.
