# Run FYTRU4PT (port 7814, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (9384/13500)

Ante 1 (Juggle/Uncommon/The Manacle 600, $4): Small: disc to hearts, Straight Q-8 308 one-shot. Shop $6 (Idol{E} $6, no scorer): Buffoon $4 -> Devious{RENTAL} (other option Zany{E,R}; SIM +0.15). Big: Trips 666 144 + disc + Straight K-9 716. Shop $4: Zany{PERISH,RENTAL} $1 (override of the 2-rental rule, TIGHT 0.60x, SIM +0.27). Manacle: 2 discs, Straight J-7 696 one-shot. $-3 -> $4 after cash.
Ante 2 (Orbital(FH)/Uncommon/The Mouth 2000, $4): EMERGENCY 0.13: Wrathful{RENTAL} $1 (3rd rental). Skipped Small (Orbital: FH L4) and Big (shop would open at ~-$1; Uncommon tag). Mouth: disc 5, FH 555AA 4256 one-shot. $-6 -> $1.
Ante 3 (Juggle/Voucher/The Psychic 6400, $1): Uncommon tag = Card Sharp{PERISH,RENTAL} $0. Skipped Small (Juggle +3 hand size) and Big (kept Juggle for the boss). Psychic with 11 cards: FH 77733 3124 + disc + FH AAA99 x3 ~10.9k. $-11 -> $-5.
Ante 4 (Top-up/Voucher/The Eye 18000, $-5): sold Devious (+$1). Skipped Small (Top-up: Splash + Ice Cream). Big 13500: disc 4, disc 3 (broke a made spade Flush 3344 for FH, solver 0.28 vs 0.04), FH TTT88 7308, dig High Card 528 (kept 66 55, 4 outs, missed), High Card x3 1548 -> 9384/13500. GAME OVER.

## Post-mortem

Binding constraint: money. The first ante-1 shop ($6) had no scorer, so every joker after that came as a rental
($1 + $3/round). By ante 2 I held 3 rentals (-$9/round, later -$12 with the free rental Card Sharp) against ~$4-6
income per blind, so money stayed at $-11..$4 from ante 1 to the end and I never saw a shop I could buy in after the
ante-1 Big. No permanent joker was ever bought; the build was Zany(perishable) + Wrathful + Card Sharp(perishable) +
FH L4 from an Orbital tag. Skipping 5 of 6 Small/Big blinds (rent-broke) kept me alive through ante 3 (each skip saved
$9-12 rent, a perish tick, and the tags carried: Orbital FH+3, Uncommon -> Card Sharp, Juggle +3 hand size for The
Psychic, Top-up -> Splash/Ice Cream), but with no money the ante-4 Big 13500 needed two Full Houses in one round.
Even winning it, The Eye 18000 disables Card Sharp; the run was dead by ante 3 money.

Decisions I would change:
1. Ante 1 shop 2 ($4): buying Zany{PERISH,RENTAL} as a second rental. It did clear The Mouth (FH 4256), but it started
   the spiral that made the Wrathful buy "necessary". Better: sell Devious ($1) -> $5 and buy Zany as the only rental,
   or keep $4 and buy the next shop's clean joker.
2. Ante 1 shop 1: Devious{RENTAL} from the Buffoon pack for a straight-only +100 chips. It won two blinds (716, 696),
   but a rental on a Flush/Straight-gated joker is the worst kind of bridge; skipping the pack card would have kept
   rent at 0 and the ante-1 money for the Big-blind shop.
3. Ante 2: Wrathful as a third rental (SIM +0.19). With money already <$4, a third rental guaranteed negative money for
   the rest of the run; I should have sold one rental first (rent > income = no future shop ever).

Reusable rules (if-then):
- IF total rent per round >= your per-blind income (~$4-6 at ante 1-3), THEN never add another rental, even at SIM +0.2:
  every later shop opens at $0 or below, so the run can only use what it already owns. Sell a rental before buying one.
- IF you are rent-broke (money < rent due) at ante 2-4, THEN skip BOTH Small and Big when their shops would open
  negative: a shop you cannot buy in is worth nothing, each skip saves the rent and the perish tick, and the tag often
  pays now (Juggle +3 hand size carries to the boss if you skip the Big too; Uncommon/Top-up give jokers).
- IF Card Sharp is your xMult AND you have a leveled Full House (Orbital tag), THEN register the FH with the lower pair
  and keep the higher pair/trips for the x3 repeat (Psychic: 77733 3124 then AAA99 x3 10956).
- IF the ante's boss is The Eye AND your only xMult is Card Sharp, THEN the Small/Big shops must buy a non-repeat
  multiplier or a counter; with negative money that is impossible, so the ante is effectively lost.

Advisor/CLI defects:
- shopadvise SIM rated a 2nd and 3rd rental at +0.27 / +0.19 (Zany at $4, Wrathful at $4) without modelling that rent
  > income makes every later shop unusable; the "a later shop sees $-3 / $-9" hint was printed but not penalised.
- Pack advise at ante 1 picked Devious{RENTAL} (Straight-gated, "non-core at Gold") at SIM +0.15 with $2 left; the
  rent (-$3 x 23 rounds) and the lost ante-1 shop money are not in the value.
- Blind-select ADVICE says "Big and Boss blinds are never skipped" even when the shop after the Big would open at
  negative money (rent-broke); the rent-broke skip rule should cover the Big too.
- Bridge issues: none (45 steps, no rejects).
