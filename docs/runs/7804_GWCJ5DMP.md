# Run GWCJ5DMP (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (1486/1500)

Ante 1 (Juggle/Rare/The Manacle 600, $4): Small: 2P AAJJ 124 + 2P 8866 96 + disc, Trips KKK 180 = 400. Shop $4: Buffoon pack -> Seeing Double{ETERNAL} (advisor tie 60/60 with foil Drunkard{PERISH,RENTAL}; took the free permanent x2 over -$15 rent at $0). Big: 2P QQ77 216 + 2P TT33 184 + Pair 44 72 = 472. Shop $4: Shoot the Moon $5 unaffordable, left. Manacle: FH KKK99 704 one-shot.
Ante 2 (D6/Double/The Goad 2000, $11): EMERGENCY 0.12, shop had only Flower Pot{E}; reroll $5 -> The Trio $8 (unaffordable at $6) -> Celestial pack $4 -> Venus (no Uranus), $2. Small 1000: disc 5 (solver), Straight 5-9 520, disc 5 keep AA K, Trips AAA L2 830 = 1350. Shop $3: Death $3 (no jokers on offer). Big 1500: Death KS->5C, Trips 555 650; disc 5 keep KC QC JH; solver dig Pair 77 96 keeping QQJJ (p 0.74); final disc keep AC QS QC (solver p 0.57) drew 888 -> Trips 888 740 vs 754 needed. Lost by 14.

## Post-mortem

Binding constraint: economy/scorers at ante 1-2. Black Deck Gold gave $4 per shop for the first three shops; the only
joker I ever owned was Seeing Double (x2, no flat chips/mult), so every hand was (base + card chips) x base mult x2:
~120-250 for pairs, 650-830 only on Trips L2. Ante 2 shops showed zero +mult/+chips jokers in 3 views (Flower Pot{E},
The Trio $8, nothing). A $4-5 flat joker anywhere would have cleared the Big Blind easily.

Decisions I would change:
1. Ante 2 shop 1 ($11): the reroll ($5) left $6 and revealed The Trio $8, unaffordable. Without the reroll I could have
   bought the Celestial pack and still had $7 for the next shop (instead of $3), i.e. the next shop's $4-7 joker. With
   $11 and no scorer, the reroll should only happen if it leaves >= the price of the joker you are hunting ($6-8).
2. Big Blind hand 2: the solver's dig (Pair 77 for 96, keeping QQJJ) gave up 144 points vs playing Two Pair QQJJ (240);
   I lost by 14. The dig only pays if the final hand hits a CLEARING out; low-rank trips (888 = 740) did not clear.
3. Big Blind final discard: the solver said p 0.57 for keep AC QS QC while its own line said "set draw Q p=0.30"; my outs
   count gave ~0.35 for either keep. The calibrated p looked inflated; I followed it anyway.

Reusable rules (if-then):
- IF you own 0 flat +mult/+chips jokers at ante 2 and have $9-12, THEN do not reroll down to under $7: the joker a reroll
  reveals usually costs $5-8, and an unaffordable reveal is a wasted $5 (here: Trio $8 at $6).
- IF a dig play (cycling cards with a small hand) gives up 100+ points vs a made Two Pair, THEN count the final-hand outs
  that actually reach the remaining need with exact chips (a low-rank Trips may fall short); prefer banking the made hand
  when the clearing outs are fewer than ~6.
- IF your only joker is an xMult with no flat support (Seeing Double, Flower Pot...), THEN Trips L2 is your real scorer
  at ante 2: Venus/Death that turn pairs into trips are worth more than Two Pair levels (Trips 555 L2 x2 = 650 vs FH L1 472).
- IF Death is held and you have a pair plus a junk card LEFT of it, THEN Death the junk card into the pair rank for Trips
  (no `move` needed when the junk is already left of the target).

Advisor/CLI defects:
- advise SOLVER labelled `PLAY 1 6 7 8` as "High Card KC est 15 + filler(s) 7H 7C TH" while the cards form Pair 77
  (est 96); the ADVICE line then said `play PAIR 1 6 7 8`. The label should name the hand the cards actually form.
- SOLVER p_clear looked overconfident on last-hand discards: "keep AC QS QC (set draw Q, p=0.30)" was printed as
  p 0.57 calibrated; the clearing outs were 2 Queens (+ ~6% for AA). Similar to the Hook overconfidence in 7804_URLL5KX1.
- `advise` right after a discard once printed the PREVIOUS hand's analysis (stale; a second call 2s later was correct).
  `shopadvise` right after `cash` once said "only works in the shop" while the state already showed SHOP.
- shopadvise REROLL at ante 2 with $11 -> $6 left did not consider that likely xMult reveals cost $6-8.
