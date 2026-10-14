# Run LXDWKCRY (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (976/1500)

Ante 1 (Small 300 Double / Big 450 Charm / The Head 600, $4): Small jokerless: AH JH 8H 7H -> disc 4 off-suit, heart Flush 324 one-shot. Shop $6 (The Sun, Diet Cola, Buffoon, Jumbo Celestial): Buffoon -> Seeing Double (over Flower Pot{ETERNAL}), $2. Big 450: Two Pair QQTT 240 + Two Pair 9955 192 + Pair 77 96 = clear. Shop $6 (Golden Joker{RENTAL}, Credit Card{ETERNAL}): Buffoon -> Ride the Bus{RENTAL} (over Matador{ETERNAL}), $2. The Head: disc 4 keeping 7744 (hearts debuffed but count for type) -> FH 77744 580, High Card TC 45 = 625/600. Rent took money to -$1.
Ante 2 (Small 1000 Investment / Big 1500 Orbital / The Psychic 2000, $5): sold Ride the Bus ($1), bought Zany{RENTAL} $1 (only scorer on offer), $5. Small: dealt KK 88 55, disc 5 5 4 2 -> KKK888, FH 2752 one-shot. Shop $4 (Hanging Chad, Cartomancer, Mega Celestial $8, Jumbo Arcana $6): left. Big 1500: no pair, disc 5432 keeping QJT9 -> Straight KQJT9 632; disc 5 keeping 99+A -> AA 99 88 (no trips); dig Pair 88 + 4H 3C 104 keeping AA99 (3 outs, ~36% FH) -> missed; Two Pair AA99 240. 976/1500. GAME OVER.

## Post-mortem

Binding constraint: no unconditional +mult/+chips joker by ante 2 (supply + money). In four shops the only scoring
jokers offered were rentals (Golden Joker, Zany) and two Buffoon packs that gave Seeing Double / Flower Pot{ETERNAL}
and Ride the Bus{RENTAL} / Matador{ETERNAL}. Seeing Double (x2) on a base mult of 2-4 is only +2..4 mult, and Zany
fires only on Trips/FH, so every blind from 1000 up needed a Trips or Full House: the Small hit FH (2752), the Big
missed it (best regular hands: Straight 632, Two Pair 240). Money never exceeded $6 (Small pays $0, rent -$3 twice).

Decisions I would change:
- Ante 2 first shop ($6 after selling Ride the Bus): Zany rental was right as a scorer, but Ride the Bus (+1 mult per
  faceless hand, already at +2) could have stayed until a non-rental scorer arrived; selling it saved $3 rent but cost
  ~+2-4 mult on every pair-family hand. Close call; not the main cause.
- Big Blind first discard: keeping QJT9 for a straight was fine for cycling, but the straight could never clear (632
  max); every winning line needed Trips. I would still play it (it banks score while drawing 5).

Reusable if-then rules:
- IF your only multiplier is Seeing Double (x2 club + other suit) and you have no +mult joker, THEN treat it as
  "+2..4 mult": it does not carry ante 2 (1000/1500) on Pair/Two Pair (~100-240). Buy any unconditional +mult first.
- IF your only scorer is Trips-gated (Zany/Wily/Trio) at ante 2, THEN the blind plan is "find Trips/FH": keep every
  pair you hold (three pairs = up to 6 outs), discard singles, and dig by PLAYING a junk pair + low singles while
  holding the other two pairs; never play your two best pairs as Two Pair before the last hand.
- IF a jokerless Buffoon pack offers Matador{ETERNAL}, THEN know it pays only on bosses that set blind.triggered
  (Hook, Tooth, Flint, Psychic, Eye, Mouth, Arm, Ox, Fish, Crimson Heart), never on suit-debuff bosses (Head, Club,
  Goad, Window, Plant): verified in blind.lua. Not worth an eternal slot early.
- IF The Head (hearts debuffed) and you hold a heart pair, THEN keep it for type: debuffed cards still count for the
  hand type (FH 77744 with 7H 4H debuffed scored 580 as a Full House).

Advisor/CLI defects:
- Ante 2 Small shop: SCORE CHECK used "one Full House (KK) ~1408" as the typical hand after a single dealt FH; main
  hand flipped from Two Pair to Full House on one play, overstating the build (real repeatable hand ~240).
- Matador is described as "$8 if boss ability triggers" with no note that suit-debuff bosses never trigger it.
- shopadvise listed Mega Celestial $8 at rank 81 with $4 in hand (unaffordable item at the top of the list; ADVICE
  correctly said LEAVE).
Bridge issues: none; 35 steps, all settled first try.
