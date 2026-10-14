# Run FA2MCBFK (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Pillar (6090/6400)

Ante 1 (D6/D6/The Hook 600, $4): Small jokerless: disc to clubs, Flush 296 + High 11. Shop $5: Buffoon (SIM 0.37 > Clever{E} 0.27) -> Wily{ETERNAL} (only scorer; Juggler rental perish). Big: disc 5 keep KK, disc 4 keep KK99 -> FH 999KK 748. Shop $7: Lusty $5 (SIM 0.64 vs Photograph 0.35). Hook: disc to hearts, heart Flush 1387 one-shot.
Ante 2 (Boss/Foil/The Psychic 2000, $9): EMERGENCY 0.16: Gluttonous{RENTAL} $1. Played Small (override skip: Boss Tag would reroll the benign Psychic): FH 999KK 2431. Shop $8: left (ratio 0.28, a level cannot fix it). Big 1500: dig High 60 keeping 4 hearts -> heart Flush 1482. Shop $11: reroll -> Sly{PERISH} $3. Psychic: disc x2 to clubs, Straight 3-7 880 (kept AA), 2P AAJJ 1232 = 2112.
Ante 3 (Meteor/Investment/The Pillar 6400, $6): EMERGENCY 0.15: Celestial -> Uranus (2P L2). $2 = rent-broke: skipped Small (Meteor: Uranus 2P L3 + Venus Trips L2) and Big (Investment +$25 after boss; Pillar faces a clean deck).
  Pillar: 2P JJ44 1794 (+filler), disc 4 keep AATT (drew KK), 2P AAKK 1976 (kept TTT JD, est exact), last discard kept JH TTT for TH/JC (~25%), missed: FH TTT66 2320 -> 6090/6400. LOSS by 310.

## Post-mortem

Binding constraint: SCALING caused by MONEY. Never owned a multiplier: the build was Wily{E} (+100 chips on trips),
Lusty (+3/heart), Gluttonous{RENTAL} (+3/club), Sly{PERISH} (+50 chips on pair) on L1-L3 hands, i.e. ~1.5-2.4k per
hand at ante 3 vs 2133 average needed at the Pillar. Cash never exceeded $11: Small Blinds pay $0, the rental took $3 a
round (4 rounds = $12), and the only xMults seen were Photograph (ante 1, card-phase, $5), The Family{PERISH} (quads)
and Blueprint ($10, nothing worth copying). 12 joker views in 6 shops; no affordable reliable xMult ever appeared.

Decisions I would change:
1. Ante 1 shop 1: Buffoon pack over Clever{ETERNAL} $4. The pack gave Wily{ETERNAL} (trips-only chips), strictly worse
   than Clever (two pair is far more common and Two Pair became my main hand at L3). The SIM preferred the pack by +0.10,
   but a pack whose best case is "a +mult joker" vs a concrete scorer that fits the likely main hand should go to the
   concrete scorer (playbook: "Concrete scorer > Buffoon pack").
2. Ante 2 shop 1 ($9): Gluttonous{RENTAL} $1. It scored (+3 to +15 mult) but cost $12 by ante 3 in a run whose real
   problem was being unable to afford a $6-8 xMult. With Lusty already owned, two suit jokers only fire together on a
   mixed hand; the money mattered more.
3. Pillar hand 2: I played 2P AAKK (1976) holding AATTKK and one discard (solver 0.44 vs 0.38). After the play the
   last hand had FH TTTJJ = 2400, 230 short of 2630. Discarding JD 9S for a FH (6 outs, 2 draws) first was the
   alternative; both were coin flips below 50%, the real loss was the build.

Reusable rules (if-then):
- IF the ante-1 shop offers a concrete chips/mult joker that fires on Pair/Two Pair (Clever, Sly, Jolly, Mad) AND a
  Buffoon pack at the same price, THEN buy the concrete joker: the pack's realistic outcome is a conditional or
  stickered joker (here Wily{E} trips-only vs Juggler rental).
- IF you are rent-broke (a rental and <= $4) at an ante-3 Small/Big whose shop buys nothing, THEN skipping for a tag
  that pays NOW (Meteor = 2 planets, Investment = $25 after the boss) is right: it saved $6 rent and two death rolls, and
  The Pillar then faces a clean deck. It is not enough without a multiplier.
- IF your only scorers are suit jokers (Lusty/Gluttonous), THEN the 5-card suited flush is your biggest hand (1.4-1.5k
  at ante 2 at L1) and The Psychic is harmless: keep it rather than reroll it with a Boss Tag.
- IF the last hand is a fixed FH short by < 15%, THEN count outs that raise MULT (a suit-joker card in the scoring
  five, quads) rather than chips; keep the suited pair-maker and discard the off-suit cards.

Advisor/CLI defects (with examples):
- Pack advise (Meteor Mega Celestial, 2nd pick): SIM ranked Venus 0.62 > Jupiter 0.61, but the ADVICE line said
  `pick 4` (Jupiter, "your most played / second hand"); the ADVICE contradicted its own SIM ranking.
- shopadvise ante 2 last shop: ADVICE `buy 1` The Family{PERISHABLE} $8 (x4 on Four of a Kind, "~x1 on your deck")
  because SIM rent-adjusted 0.03 > -0.02; a quads-only perishable xMult that leaves $3 is noise, not a buy.
- `s` at the ante-2 Small advised `skip` for a Boss Tag that rerolls The Psychic; Psychic is near-harmless for a build
  that plays 5-card hands (flush/FH/2P+filler); a Boss Tag should only be valued against a harmful boss for this build.
- `s` at the ante-3 Small said "do not skip: take the shop" with $2 and a rental (rent-broke rule not in the CLI; same
  defect as 7801_FYPFR6AC).
- est was exact on every play checked (1794/1794, 1976/1976, 2320/2320).
Bridge issues: none (55 steps, no rejects).
