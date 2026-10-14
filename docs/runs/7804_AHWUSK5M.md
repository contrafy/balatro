# Run AHWUSK5M (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Window (5130/6400)

Ante 1 (Holo/Double/The Psychic 600, $4): Small: disc 4 (solver kept 33 + clubs), Flush C 288 + Pair AA. Shop $5: Buffoon -> Walkie Talkie{PERISH} (other: Delayed Gratification{PERISH}). Big: Trips TTT 1350 one-shot (Walkie on tens). Shop $7: Popcorn{RENTAL} $1 (+20 mult, SIM +0.61). Psychic: 2P 9988+filler 1188 one-shot.
Ante 2 (Juggle/Polychrome/The Manacle 2000, $10): shop Green Joker $4 (advisor BUY) - I overrode and rerolled ($5): Crazy{P,R} + Flash Card, bought nothing. Skipped Small (rent-broke $5, Juggle tag). Big 1500 (11-card hand): FH 66699 1520 one-shot. Shop $8: Madness/Sun/Standard packs, left. Manacle: Pair TT 1100 + FH KKK99 1408.
Ante 3 (Voucher/Polychrome/The Window 6400, $12): foil Ramen $8 (x2 +50 chips, EMERGENCY 0.10). Skipped Small (rent-broke $4; kept Walkie's last round + Popcorn 8 for the Big). Big 4800: 2P 9955 1960 + 2P JJ22 1880 + FH 444KK. Walkie perished. Shop $5: sold Walkie, Celestial $4 -> Earth (Saturn/Jupiter/Earth). Window: 2 discards for FH, FH TTT77 2948, no pair dealt -> High K 630 dig, final Straight A-T (3 debuffed diamonds) 1552. 5130/6400. LOSS.

## Post-mortem

Binding constraint: no permanent +mult scorer by ante 3. My only scorers in ante 1-2 were a perishable Walkie Talkie (Buffoon
pack) and a decaying rental Popcorn (+20, -4 per round). At the Window Popcorn was down to +4, Walkie had perished, and Ramen
x2 multiplied a base mult of 2-6: Two Pair ~1150, FH L2 ~2950, against 2133 per hand needed. Money was never above $12
because Popcorn's rent ($3 x 4 rounds = $12) ate the income, and the $0 Small Blinds pay nothing.

Decisions I would change:
1. Ante 2 shop 1 ($10): the advisor said BUY Green Joker $4 (+1 mult per hand, -1 per discard; SIM +0.06). I rerolled
   instead ($5) and saw Crazy{P,R}/Flash Card, then had $5 and nothing to buy. Green Joker was the only PERMANENT +mult
   offered in antes 1-3; by the Window it would have been ~+4-6 mult, roughly doubling the base mult that Ramen x2
   multiplies (FH 2948 -> ~4300, enough with the 1st-hand score). A permanent weak +mult beats a reroll lottery at $10.
2. Ante 3 shop 2 ($7 after selling Walkie): Celestial pack ($4, no Mercury, took Earth). With Popcorn about to die, the
   money should have gone toward a +mult source (Jumbo Arcana $6 for Empress mult cards, or keeping $7 for the reroll
   next ante) - the Earth level added ~+10% to one hand type.
3. The two rent-broke Small skips (ante 2 and 3) were consistent with the rule, but each removed a shop visit while I
   still had zero permanent +mult; with only rentals/perishables, shop views were the scarce resource.

Reusable rules (if-then):
- IF at ante 1-2 your scorers are only perishable/decaying (Walkie{PERISH}, Popcorn, Gros Michel, Ice Cream), THEN the
  first PERMANENT +mult joker the shop offers is a buy even if weak (Green Joker, Joker, Half), before any reroll or pack.
- IF your only +mult is Popcorn, THEN count its value at the ante-3 boss as (20 - 4 x rounds held): it is a 2-ante bridge,
  and its $3 rent per round costs more than a $4 permanent joker within 2 rounds.
- IF you own a lone xMult (Ramen x2) with no +mult joker, THEN its value is x2 on base mult 2-6: buy +mult first, the
  xMult only pays once flat mult exists.

Advisor/CLI defects:
- Celestial pack `advise`: rule line said Earth (pair-family), SIM line picked Saturn by 0.04 (noise) and the ADVICE took
  the SIM; then `pick` printed "Earth levels Full House (NOT your main hand Pair; a level elsewhere is mostly wasted)"
  although Earth had been the rule pick and FH was my most played type (3x).
- shopadvise ante 3 shop 2 ranked a $4 Celestial pack (no main-hand planet guaranteed) above a Jumbo Arcana while the
  build's real gap was +mult, not levels.
- None blocking; all bridge actions succeeded.
