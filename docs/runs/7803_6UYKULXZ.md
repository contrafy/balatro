# Run 6UYKULXZ (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Big Blind (68164/90000)

Ante 1 (Charm/Rare/The Club 600, $4): Small jokerless: disc x2, 2P JJ33 92 + Straight 8-4 240 = 332. Shop $5: Buffoon -> Popcorn{PERISH} (over Drunkard{E}). Big: disc for hearts, Flush 1560 one-shot. Shop $7: Buffoon (overrode SIM Zany{ETERNAL}, trips-only) -> Jolly{RENTAL}. Club: 2P AA66 1404 one-shot.
Ante 2 (Rare/Standard/The Wall 4000, $7): foil Smiley $6. Skipped Small for Rare tag ($1, shop useless). Big: Broadway 4061 one-shot. Shop: Rare tag -> The Tribe $0 (x2 Flush). Wall: club Flush 5588 one-shot.
Ante 3 (Investment/Top-up/The Mouth 6400, $8): EMERGENCY 0.32; sold Popcorn, passed Baron $8 (held Kings, SIM +0.02), reroll -> Joker $2. Skipped Small (Investment, $3 shop useless). Big 4800: 2P QQ88 2544 + Straight Flush J-7 6596. Shop $5 TIGHT: Arcana -> Emperor -> Judgement (Onyx Agate) + Hierophant. Mouth: disc, Hierophant on QQ, Pair QQ 4340 (locks Pair) + TT 1680 + JJ 2480. $28 after Investment.
Ante 4 (Double/D6/The Water 18000, $28): EMERGENCY 0.18: Mystic Summit{PERISH} $5, reroll, sold Joker -> holo Loyalty Card $8. Small 9000: disc x2, Broadway 5764 + 2P 6633 4312. Shop $10: Jumbo Arcana -> Temperance (+$17), reroll, sold Jolly{R} -> Burglar $6 (6 hands, Mystic always on). Big: Trips 2576, High 2015 dig, Flush AD KD JD 9D 8D 10374 (advisor est 41496 assumed Loyalty x4: off by one). Shop $20: Temperance (+$16), Buffoon skip (Matador/Red Card), 2 rerolls nothing, Celestial -> Jupiter. Water: 2P 5533 14104 (Loyalty x4 on 6th hand, raw hands_played_at_create 11) + 2P JJTT. $29.
Ante 5 (Buffoon/Skip/The Window 50000, $29): EMERGENCY 0.24: 2 rerolls (passed Photograph{E,R}), sold Onyx -> Card Sharp $6, Celestial -> Mercury. Skipped Small for Buffoon tag (Mega: Flower Pot{P}/Wily{P,R}/Devious/Raised Fist{P}, skipped; keeps Mystic alive). Big 37500: Pair 22 register, 66 x3 7308, 44, 77, JJ x3x4 43320 = 67k. Shop $18: reroll, sold Tribe -> Popcorn{P,R} $1 (SIM 0.67 vs 0.61). Window (diamonds): 33 register, AA 13968, 55 11520, High KS, KK 13515, AA x4 49536. Mystic perished. $20.
Ante 6 (Holo/Top-up/The Pillar 120000, $20): EMERGENCY 0.30: sold perished Mystic, reroll (nothing), Jumbo Arcana -> Empress (Mult 5H 5D), Paint Brush $10 (hand 9) -> $1. Skipped Small (rent-broke $1 with Popcorn rent; Holo tag; keeps cards clean for Pillar). Big 90000 (solver: UNWINNABLE, exp ~41k from hand 1): Straight 4340, 2P AA66 2912, 2P 4433 x3 7056, Pair 66, 22 x3 6873, KK x3 x4 44460 = 68164. GAME OVER.

## Post-mortem

Binding constraint: SCALING. No reliable xMult until Card Sharp at ante 5; the run lived on flat +mult (Smiley foil,
Popcorn, Mystic Summit, Loyalty holo +10 ~ 29-34 mult on Pair L2) times Card Sharp x3 and one Loyalty x4 per 6 hands.
That made ~67k rounds at ante 5 (6 hands via Burglar) and the same ~68k at ante 6, against 90k. SCORE CHECK was 0.18-0.32
(EMERGENCY) in every shop from ante 3 on; 7 rerolls across antes 3-6 showed one real xMult (Card Sharp) and one conditional
(Loyalty), plus Baron and eternal-rental Photograph. Money was the second constraint: Jolly{RENTAL} cost $15 of rent over
antes 1-3 while the wallet sat at $0-5, so ante 2-3 shops could not buy anything after the first joker.

Decisions I would change:
1. Ante 6 shop ($22): Paint Brush ($10) + Jumbo Arcana ($6, Empress) added ~10-15%. 3 more rerolls ($6-8 each) hunting a
   second xMult was the only line that could reach 90k from a 66k projection; +1 hand size could not.
2. Ante 1: Jolly{RENTAL} as the second joker. It scored, but its rent kept me at $0-5 for two antes, which is why the ante-3
   Baron ($8) and ante-3 rerolls were out of reach. Take a rental only with a plan to sell it in the next shop.
3. Ante 4-5: Loyalty Card was worth more than it looked (x4 once per round with Burglar's 6 hands, it decided every blind
   from the Water on). But its timing must come from raw state, not the advisor; I wasted one x4 on a High Card plan
   at the Window by counting by hand.
4. Ante 3: passing Baron ($8) for Joker $2 was right (held Kings, card phase), but I should have rerolled once more
   instead of buying the Arcana pack at $5.

Reusable rules (if-then):
- IF you own Loyalty Card, THEN read raw `hands_played_at_create` (C) and `hands_played_total` (T): the x4 fires on the
  hand played when T == C + 5 + 6n (T before the play). Save your best hand (Card Sharp repeat) for that hand; the
  advisor's "fires on THIS hand" note is one hand early (verified 4 times).
- IF you own Burglar (6 hands, 0 discards) AND Card Sharp, THEN register Pair with the cheapest pair in hand 1, keep the
  best pair for the Loyalty/x3 hand, and play High Card/Straight digs only when no pair is in hand.
- IF Temperance is offered (shop $3 or Arcana pick) AND your jokers sell for $15+, THEN take it: +$16-19 twice here.
- IF The Emperor is in an Arcana pack AND you have a free joker slot, THEN take it: Judgement is a free joker (Onyx here).
- IF you are rent-broke (< $3 after rent) at a $0 Small Blind, THEN skip it for any tag; the shop after it buys nothing
  (done 4 times this run: Rare, Investment, Buffoon, Holo tags all paid).
- IF the SCORE CHECK stays < 0.35 for two antes with 0-1 xMult, THEN every non-xMult purchase (levels, vouchers,
  Arcana) is a loss: put all money into rerolls/Buffoon packs that can show an xMult.

Advisor/CLI defects:
- Loyalty Card off by one: `advise`/`play` said "fires on THIS hand (x4)" one hand early (est 41496 vs actual 10374,
  29904 vs 7476, 54060 vs 13515, 27492 vs 6873) and "fired on the LAST hand" on the hand that actually fired
  (est 3526 vs 14104, 10830 vs 43320, 12384 vs 49536, 11115 vs 44460). Raw `extra.remaining` stays "5 remaining";
  `loyalty_remaining` and `hands_played_at_create` are correct and should drive the note/est.
- Mega Buffoon SIM (ante 5) proposed selling The Tribe for Flower Pot{PERISHABLE} with The Window (diamonds debuffed)
  as the boss; Flower Pot needs a scoring diamond, so it is dead at that boss.
- shopadvise ante 1 SIM picked Zany Joker{ETERNAL} (trips-only) over a Buffoon pack (0.82 vs 0.76); rule line was right.
- shopadvise ante 3 ranked Baron $8 as BUY in EMERGENCY although its x1.5 per held King is card phase and SIM gave +0.02.
Bridge issues: none; 130 steps, no rejects.
