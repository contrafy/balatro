# Run I9HDGAQA (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big (2152/4800)

Ante 1 (Rare/Polychrome/The Manacle 600, $4): Small FH 555AA 308 one-shot. Shop $6: Wrathful{ETERNAL} $5 (only scorer; passed Buffoon pack). Big: 2P QQTT 480 one-shot. Shop $7: Mercury. Manacle: Straight 8-high 600/600 exact.
Ante 2 (Standard/Holo/The Window 2000, $11): EMERGENCY 0.16; rerolled $5 (Arrowhead{PERISH} $7 appeared, $1 short), left with $6. Small 1000: solver digs, spade Flush 1292 on the last hand. Shop $7: Obelisk $8 ($1 short!), Jumbo Buffoon -> Acrobat (over foil Greedy/Onyx Agate/Blueprint{E}). Big 1500: 2 throwaways + FH QQQ66 x3 = 2460. Shop $5: Gluttonous{ETERNAL} $5 -> $0. Window: dig to spade Flush, final x3 4218.
Ante 3 (Ethereal/Economy/The Head 6400, $5): Celestial $4 -> Jupiter (Flush L2). Small 3200: held spade Flush, 2 throwaways, final x3 5733. Shop $1: Hanging Chad{RENTAL} $1 (SIM 0.34 vs 0.04). Big 4800: solver dig broke AA+JJ (p 0.99), discards to a 4-club draw (p 0.98), dig play (p 0.84), missed the 5th club; forced Pair 66 1764 -> 2152/4800. GAME OVER.

## Post-mortem

Binding constraint: money, which capped scaling. Every shop ended at $0-1 from ante 2 on, so no interest and no $8 joker
was ever affordable. The Acrobat plan (hold the best hand for the x3 final hand, spend the other hands as digs) also
means 0 unused hands, so $0 hand money every round on top of the $0 Small Blind: income was only Big $4 + Boss $5. The
build (Wrathful + Gluttonous suit +mult, Acrobat x3, Chad) only cleared via a 5-card single-suit black flush on the
final hand: ~60-70% per round in practice, and it failed at the ante-3 Big.

Decisions I would change:
1. Ante 2 first shop: the $5 reroll at $11 (shop had no scorer). Without it I would have had ~$12 in the next shop,
   which offered Obelisk $8 (clean, the winning-line xMult) and a Jumbo Buffoon. The reroll showed Arrowhead $7 that I
   could not afford anyway. At $11 with one scorer, keep the money: an $8 xMult is worth more than one reroll.
2. Ante 1: Wrathful{ETERNAL} over the Buffoon pack. Then Gluttonous{ETERNAL} at ante 2. Two eternal one-suit +mult
   jokers locked me into a single-suit flush build (Gold policy: Flush builds never reached ante 4) and blocked 2 slots.
3. Ante 3 Big: following the solver's first dig (play AH QH JH 7D 5D, break AA and JJ at p 0.99). A Two Pair/AA line
   would not have cleared either (420 x3), so the real error was being in a position where one flush draw decides it.

Reusable rules (if-then):
- IF you are at ante 1-2 with $9-12 and one scorer, THEN do not reroll below $8: the next shop's $8 xMult (Obelisk,
  Hologram, Constellation) is the run's best buy and needs $8+ in hand after the $0 Small Blind.
- IF your xMult is Acrobat and you hold the best hand for the final hand, THEN expect $0 hand money every round; count
  income as Big $4 + Boss $5 + interest and keep $5+ banked so interest is not zero.
- IF your +mult jokers are one-suit (Wrathful/Gluttonous/Greedy/Lusty), THEN do not buy a second one of another suit as
  an Eternal: they do not combine on a flush and push you to a single-suit flush build.
- IF the solver says p >= 0.95 on a dig line that needs ONE specific draw (5th card of a suit), THEN treat it as ~0.6-0.7.

Advisor/CLI defects:
- SOLVER p overconfident on Acrobat dig lines needing a 5th suited card: ante 3 Big p 0.99 (dig) -> 0.95 (discard) ->
  0.98 (4-flush draw) -> 0.84 (dig) -> lost 2152/4800. Ante 2 Small also showed p 0.88/0.86/0.72 on near-empty hands.
- shopadvise named the main hand "Three of a Kind", then "Full House" while every cleared blind from ante 2 on was a
  black Flush final hand; the Jupiter pick printed "NOT your main hand... mostly wasted" although SIM ranked it 0.23 vs 0.04.
- `hands` "card chips" label counts debuffed cards (Straight under The Window: "35 card chips"; est 689 used 23, correct).
