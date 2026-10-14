# Run FYEJZFFU (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (4668/4800)

Ante 1 (D6/Skip/The Goad 600, $4): Small: disc x2 kept 7766, drew Flush clubs 260 + Pair 88 52. Shop $5: Even Steven{PERISH} $4 (SIM 0.65 vs 0.00). Big 450: disc x2 kept 555, FH 555 66 804 one-shot. Shop $7: Baron $8 ($1 short), left. Goad: disc 5 kept 88, Trips 888 (8S debuffed) 506 + Straight A-T 568.
Ante 2 (Polychrome/Holo/The Arm 2000, $14): EMERGENCY 0.07 (Even Steven perishing): Scholar{ETERNAL} $4, reroll $5, Popcorn $5 -> $0. Skipped Small (broke) for Polychrome tag. Big 1500: High AC 900 (Scholar+Popcorn) + Straight J-7 2368. Shop $5: polychrome Driver's License{RENTAL} $0 (= x1.5). Arm: FH 444 66 3840 one-shot (L1 hands immune).
Ante 3 (Standard/Meteor/The Wall 12800, $9): EMERGENCY 0.28: Buffoon pack $4 -> Business Card{PERISH} (Golden{PERISH,RENTAL} barred); passed Mad Joker{PERISH} $4 (SIM 0.00 = all options 0). Small 3200: 2P 6633 1254 + Pair AA 2376. Even Steven perished (sold $2). Shop $5: left (Celestial/Juggler SIM noise). Big 4800: 2P JJ66 780, disc, disc, FH TTT99 1584, last hand Flush clubs 2304 (est exact) -> 4668/4800, lost by 132.

## Post-mortem

Binding constraint: money and scaling at ante 2-3. Every scorer I owned was temporary or conditional: Even Steven
(perishable, died after ante-3 Small), Popcorn (+20 decaying -4/round, +4 at the death), Scholar{E} (Aces only),
polychrome Driver's License{RENTAL} (the only multiplier, x1.5, costing $3/round). The ante-2 shop went to $0
(Scholar $4 + reroll $5 + Popcorn $5) and with $0 Small Blinds plus $3 rent I never had more than $9 again, so no
xMult view was ever affordable. The Wall (12800) as the ante-3 boss made every 3-blind SIM horizon read 0.

Decisions I would change:
1. Ante 3 first shop ($9): the Buffoon pack ($4) gave Business Card/Golden Joker junk. Mad Joker{PERISH} $4 (+10 mult
   on Two Pair, also fires on Full House) would have turned the Big's 2P 780 into ~1170 and FH TTT99 1584 into ~2900:
   it clears the Big that I lost by 132. SIM showed 0.00 for every option because the horizon includes The Wall.
2. Ante 2 reroll ($10 -> $5) found Popcorn (good), but the result was $0 for the rest of ante 2; skipping the reroll and
   keeping $10 would not have found a scorer either. Root cause is earlier: Even Steven perishable as the first scorer.
3. Big Blind hand 1: solver chose play 2P 780 (p 0.67) over a discard; fine, but the run was already a coin flip.

Reusable rules (if-then):
- IF every SIM option reads 0.00 / "no option clears the next 3 blinds" because a Wall/Violet boss sits in the horizon,
  THEN decide by the NEXT blind only: buy the cheapest +mult that fires on your made hands (Mad/Jolly/any +mult perishable)
  over a Buffoon pack gamble; a lost Big ends the run before the Wall matters.
- IF your only scorers at ante 2 are perishable/decaying (Even Steven{P}, Popcorn), THEN count them as gone at ante 3 and
  buy a permanent +mult before any reroll; the ante-3 Small/Big still need ~1100-1600 per hand.
- IF a Polychrome tag lands on a useless joker (Driver's License) as a $0 rental, THEN it is a real x1.5 multiplier, but
  the $3/round rent at a $0-9 wallet costs a joker per ante; sell it the moment a permanent +mult is affordable.
- IF the last hand is a Flush/Full House short by <10%, THEN there is no recovery: carry a $3 rescue tarot (none was
  ever affordable here); keep $3 spare from ante 2 when the Big is projected < 1.2x.

Advisor/CLI defects:
- shopadvise at ante 3 shop 1: "SIM: no option clears the next 3 blinds" (Mad Joker 0.00, baseline 0.00) because The
  Wall 12800 is in the 3-blind horizon; it then fell back to rule scores (Buffoon 95 > Mad Joker 25 "other hand"). Mad
  Joker was labeled "PLUS(other hand)" although Two Pair and Full House (which contains Two Pair) were 4 of my 10 plays.
  When the horizon is 0, SIM should report P(clear next blind) instead.
- Pack advise ranked Business Card 25 and said SKIP; picking it (sell value $2 > $0) is never worse in a free slot.
- Advise est was exact on every hand (Flush 2304/2304, FH 1584/1584).
