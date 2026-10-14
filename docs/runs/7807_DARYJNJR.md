# Run DARYJNJR (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind The Psychic (344/600)

Ante 1 (Investment/Skip/The Psychic 600, $4): Small 300: disc x2 to a straight draw, Straight T-6 280 + Pair 44 36 = 316. Shop $5: Buffoon $4 -> Riff-raff{PERISH} over Ice Cream{PERISH,RENTAL} (override of pack SIM 0.84 vs 0.10). Big 450: Riff-raff made Half Joker + Hallucination; Pair 99 616 one-shot. Shop $7: left (Banner{RENTAL}, Hanging Chad{ETERNAL,RENTAL}; SIM nothing > +0.02). Psychic: Riff-raff made Photograph + Crazy. Disc to KQJ9 (solver 0.88), disc breaking 2P JJ55 (200) for QJ98 (solver 0.84 vs 0.70) -> drew no T; dig 2P 8844 88 (solver 0.69 vs 0.54) keeping QQJ; dig High A 16 keeping QQT (solver 0.51 vs 0.31) -> drew KH JS JH TD 4D, no Q; last hand 2P QQJJ 240 -> 344/600. GAME OVER.

## Post-mortem

Binding constraint: no joker that scores on a 5-card hand at the ante-1 Psychic. Half Joker (the run's only real
scorer, Pair 99 616 at the Big) is dead under The Psychic, Crazy only fires on straights, Photograph only doubles a
L1 hand (Pair/Two Pair face 120/240). Every line therefore needed a drawn Straight (~2500) or Full House (720); two
discards and two dig plays missed both (no T in 3 draws, no 3rd Q in 5).

Decisions I would change:
1. Psychic hand 2 (0 discards, 2P QQ88 224 on board): I followed the solver's dig (2P 8844 for 88, keep QQJ). That
   threw away 136 points of a 600 target to chase a 2-card combination. With Two Pair face at ~200-240 per hand,
   banking 224 and needing ~376 from two more 5-card hands was at least comparable and less draw-dependent.
2. Psychic discard 2: broke a made 2P JJ55 (200) to chase a single-rank inside straight (4 outs). Under The Psychic
   with Photograph, a made face Two Pair is the floor; keep it and discard the other 4 cards.
3. Ante-1 Big shop ($7, Psychic upcoming, Half Joker my only scorer): I left. Nothing on offer fixed it, but this was
   the moment to note that the boss kills the main scorer; an Arcana pack ($4) for a Strength/Death to build trips or
   a Banner rental would at least have added something for 5-card plays.

Reusable rules (if-then):
- IF the ante-1 boss is The Psychic AND your only scorer is Half Joker (or another <=3-card joker), THEN treat the
  boss as jokerless: in the Big-blind shop buy any +chips/+mult joker that fires on 5-card Pair/Two Pair hands, even a
  $1 rental, before saving money.
- IF a Buffoon pack offers Riff-raff at ante 1 with 4+ empty slots, THEN take it over a decaying/rental bridge: it made
  4 free sticker-free commons (Half Joker, Hallucination, Photograph, Crazy) in two blind selects. Select every blind.
- IF under The Psychic you hold a made face Two Pair (~200+ with Photograph) and 2 hands remain after it, THEN play it
  instead of a 5-card dig hand that scores <100; the dig needs a specific 2-card combination.

Advisor/CLI defects:
- Pack advise ranked Riff-raff 25 / SIM p 0.10 vs Ice Cream{PERISH,RENTAL} 85 / 0.84: the SIM does not model the free
  Commons Riff-raff creates at every blind select (it produced Photograph + Half Joker + Crazy here).
- Psychic solver looked over-optimistic across consecutive decisions: p 0.88 -> 0.84 -> 0.69 -> 0.51 -> 0.00
  ("calibrated"). At hand 3 (need 512 in 2 hands, keep QQT) my count was ~0.25 (needs a Q in 5 draws, 30%, plus a
  T/pair). The dig lines it labelled "keep QH QC JC (made Pair 720)": 720 is the Full House QQQTT value, not a Pair;
  the label is misleading.
- shopadvise at the ante-1 Big shop printed "BOSS PREP: The Psychic counters this build" but then advised LEAVE with
  nothing to counter it; it did not rank any 5-card-capable scorer.
Bridge issues: none.
