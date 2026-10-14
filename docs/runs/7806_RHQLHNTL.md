# Run RHQLHNTL (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Small Blind (8921/9000)

Ante 1 (Foil/Holo/The Club 600, $4): Small: disc 4, Straight A-T 324. Shop $6: Shoot the Moon $5 (only scorer). Big: Trips 333 with QQ held 1131. Shop $7: Smiley Face{E} $4. Club: 2 disc, 2P 7766 80, heart Flush 666 -> 746.
Ante 2 (Top-up/Handy/The Fish 2000, $9): passed Greedy (SIM +0.02). Skipped Small (Top-up -> Jolly + Popcorn). Big: FH 55566 2144. Shop $16: Mystic Summit{E} $5. Fish: 2 disc, Straight A-T 4050 one-shot.
Ante 3 (Top-up/Economy/The Water 6400, $20): passed The Trio{ETERNAL,RENTAL} (hard rule), Celestial -> Mercury, Even Steven{RENTAL} $1. Small: 2P AA99 3000 + High K. Shop: Mercury $3 (Pair L3). Big: Quads 7777 5632. Shop: Buffoon -> Joker{PERISH} (sold Popcorn). Water: Pair 88 + JJ + 55 with Qs held -> ~7600/6400.
Ante 4 (Standard/Buffoon/The Mouth 18000, $18): EMERGENCY 0.18. Sold Even Steven{RENTAL}, Buffoon -> Abstract{E} (Mail-In other), sold Joker{PERISH} -> Odd Todd{PERISH,RENTAL} $1 (SIM 0.52 vs 0.00), passed Arcana, $15. Small 9000: disc 3H 2C (straight draw), disc 8H 6D 3S keeping QQ + odd A/9/7, High AS with QQ held 2820, Pair QQ with QD held 4080, last hand had no pair (KC QD JH TH 8D 7S 5S 2S): High 7S with QD held 2021 -> 8921/9000. GAME OVER (79 short).

## Post-mortem

Binding constraint: scaling, 0 xMult at ante 4. The build was all flat: Shoot the Moon (+13 per Queen held), Smiley{E},
Jolly, Mystic Summit{E}, Abstract{E}, Odd Todd. ~45-70 mult on ~50-120 chips made 2-4k per hand against a 9000 Small;
the score check was 0.18-0.35 (EMERGENCY) from the ante-4 shop on. The only xMult offered in 9 shop views was
The Trio{ETERNAL,RENTAL} $1 at ante 3.

Decisions I would change:
1. Ante 3 shop: passed The Trio{ETERNAL,RENTAL} $1 (SIM +0.23, 0.49 -> 0.72) because of the "no eternal rental before
   ante 7" rule. At the losing Small I held QQQ on hand 2: Trips QQQ est 3540 x3 = ~10.6k would have cleared the blind
   alone (Trio also fires on FH/Quads; I made Quads and a FH earlier). -$3/round is ~$9/ante; losing the run is everything.
2. Ante 4 Small, last discard: I kept QQ + A/9/7 and discarded 8H 6D 3S (solver-style odd-pair draw) and then played
   High AS first to keep QQ held. The final 8 cards had no pair. Playing Pair QQ first (3300) and digging for a third
   Q / odd pair would have been similar EV; no clear misplay, but the margin was 79 chips.
3. Ante 4 shop: skipped the Arcana pack ($4, kept $15). Hierophant (+30 chip bonus card) or Empress on an odd card was
   worth more than 79 chips; with EMERGENCY flagged the $1 interest was not the right priority.

Reusable rules (if-then):
- IF the score check is < 0.5 at ante 3 with 0 xMult AND The Duo/Trio/another hand-type xMult that fits your pair-family
  hands is offered as a $1 eternal rental, THEN take it: the rent (~$9/ante) is cheaper than the run. (Data-free
  [INFERENCE]; it would have cleared the losing blind directly.)
- IF you own Shoot the Moon (+13 per Queen HELD), THEN play non-Queen hands and keep Queens in hand: Pair 77 with QQ held
  2484 vs Pair QQ 1800 in the same hand; High Card A with QQ held 2820.
- IF you own Odd Todd, THEN on a forced High Card last hand compare EVERY odd card with `sel`: High 7S scored 2021 while
  `advise` only offered High KC 780 (Odd Todd's +31 makes a low odd card beat a King).
- IF you own Mystic Summit, THEN spend both discards before the hands that need to score (+15 mult on every later hand);
  under The Water it is always on.
- IF a shop offers a $1 rental flat joker (Even Steven, Odd Todd) while you own fewer than 6 scorers, THEN it is a fine
  bridge; swap rental for rental (sell the old one first) so you never pay two rents.

Advisor/CLI defects:
- `advise` at the final hand (KC QD JH TH 8D 7S 5S 2S, Odd Todd + Moon) listed only High Card KC (est 780) and printed
  "UNWINNABLE ... PLAY 1"; `sel 6` showed High 7S est 2021 (Odd Todd +31 chips). High Card candidates should be ranked
  by est with jokers, not by rank.
- `shopadvise` ante 3 marked The Trio{ETERNAL,RENTAL} -125 in the second view ("conditional, other hand: needs Three of
  a Kind, your main hand is Straight") after a Straight count tie flipped the main-hand label; one view earlier its SIM
  said +0.23. Main-hand labels flip between Trips/Straight/Pair on 1-2 plays and swing rule scores by 100+.
- SOLVER p values were >= 0.99 on nearly every option through ante 3 and 0.96 on the losing Small's hand 3 line that
  lost; not discriminating.
Bridge issues: none; 66 steps, no rejects.
