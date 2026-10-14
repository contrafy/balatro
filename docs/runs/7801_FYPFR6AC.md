# Run FYPFR6AC (port 7801, claude-fable-5-1) - Black Deck Gold Stake - LOSS at ante 4 blind The Mark (9285/18000)

Ante 1 (Polychrome/Boss/The Manacle 600, $4): Small: disc 4 to diamonds, Flush 296 + Pair 77. Shop $5: Shoot the Moon{ETERNAL} $5 (+13 mult per held Q). Big 450: disc 5 keeping TS 99, drew QS + TT -> 2P TT99 870 one-shot. Shop $6: nothing (Dagger, Hit the Road $8). Manacle (hand 7): no Q in 2 discards; Pair 88 probe 52 keeping JJ, disc 5 -> QH + TT: 2P JJTT 900 = 952/600.
Ante 2 (Holo/Boss/The Window 2000, $13): EMERGENCY 0.21 -> Odd Todd{RENTAL} $1 (+31 chips/odd card), Celestial -> Mercury (Pair L2). Skipped Small for Holo tag (2 scorers). Big 1500: High A w/ Q 658 + Straight 3-7 2516. Shop $11 (no joker, Holo tag stayed pending): Celestial -> Mercury (Pair L3). Window: no Q for 2 discards, Pair 77 (7D debuffed) 1326 + Pair 99 2040 = 3366/2000.
Ante 3 (D6/Buffoon/The Psychic 6400, $10): shop: free holo Greedy{RENTAL} (second rental, EMERGENCY 0.17/TIGHT 0.96x; +10 mult). Skipped Small for D6 (rerolls from $0; rent -$6/round made the Small shop worthless). Big 4800: never saw a Q: Pair AA 1736 + Pair 55 1904 + Pair 77 1972 = 5612. Shop $8: D6 rerolls $0/$1/$2 (Gluttonous{P}, Ice Cream, Mail-In{E}, Egg{E}, Death, Photograph{E}, Midas{R}, Joker) -> Joker $2 (+4). Psychic: Pair 77 2436, disc, Pair 99 w/ Q 4080 = 6516/6400. $3 after rent.
Ante 4 (Charm/Voucher/The Mark 18000, $3): EMERGENCY 0.19, TIGHT 1.04x vs Small 9000. Sold Joker ($1) -> Arcana $4 -> Death (2H became a 5th Queen). $0. Skipped Small (rent-broke; Charm = Mega Arcana: Hierophant on 9C 9D + Wheel of Fortune, which missed). Skipped Big 13500 (3.6x my ~3700 hand; a win would leave -$1 with no shop value). Mark: disc x2 fishing, Straight A-5 4884 (1 Q held), Pair 99 3240, High 7D 1161 = 9285/18000. GAME OVER, 69 steps, no rejects.

## Post-mortem

Binding constraint: SCALING, caused by MONEY, caused by two rentals. The engine was Shoot the Moon (+13 mult per held Queen) +
Odd Todd (+31 chips per odd scoring card, rental) + holo Greedy (+10 mult, rental) on Pair L3: an odd pair with a Queen held
scored 3200-4100 at ante 3-4, which is exactly ante-3 money and nowhere near ante 4 (9000/13500/18000). From the ante-3 Small
shop on I paid $6 of rent per round on a $0 Small Blind economy: cash went $10 -> $8 -> $3 -> $0 -> rent-broke, so every
later shop (8 joker views at ante 3-4) was a window-shop. In 16 joker views over the run I saw zero end-phase xMults
(Photograph{E} was the only x-anything, card-phase) and never had $6+ when a real one could have appeared. The run was not
decided by a hand: the Mark round scored 9285 with three decent hands; no three hands of this build make 18000.

Decisions I would change:
1. Ante 3 first shop ($10): taking the free holo Greedy{RENTAL} as a SECOND rental. It added +10 mult (+60%) and did carry
   ante 3, but -$6/round on a Red-stake economy (Small pays $0) is -$18 per ante against ~$10 of income: by the ante-4 shop I
   held $3. The playbook rule "never two rentals before ante 6" exists for exactly this; the EMERGENCY (0.17) made me override
   it. The better line: take Greedy AND sell Odd Todd in the same shop ($1 back, rent $3), accept a weaker ante 3 (odd pairs
   1566 instead of 3240 with a Q) and arrive at ante 4 with ~$15-20 for a real joker. Or skip Greedy, buy the Mega Celestial
   ($8, two Pair levels) and keep one rental.
2. Ante 2 first shop ($13): Odd Todd{RENTAL} $1 over the $8 money floor... it was right as the NEEDED NOW scorer, but I should
   have planned its sale by ante 3 (it never happened because the Queen engine made odd pairs the main hand, so Odd Todd
   became "core"). A rental that becomes core is the trap: its rent is paid until death.
3. Ante 3 second shop (D6, $8): Ice Cream (+100 chips, -5/hand) was offered before the free reroll; on a 120-chip / 31-mult
   build that was +80% for ante 3-4's six rounds. I rerolled it away hunting an xMult I could not have afforded ($8).
4. Ante 4 Charm pack: Hierophant on two 9s + Wheel of Fortune (25% edition, missed). The Tower (Stone card, always scores
   +50 chips as a filler) was the concrete pick; Wheel was a lottery I took because only an edition could change the ante-4
   math. With hindsight nothing in that pack changes 18000.

Reusable rules (if-then):
- IF you own one rental and the shop offers a second one (even $0, even holographic), THEN sell the weaker rental in the
  same shop or do not take it: at Gold the Small pays $0, so two rentals (-$6/round) exceed a whole ante's income and the
  ante-4 shops will hold $0-3. A free holo rental is not free: it cost $18 this ante.
- IF your engine is "+N mult per held card of rank R" (Shoot the Moon), THEN count Queens as the scaling resource: Death
  on a junk card next to a Queen adds a 5th Queen; never play a Queen; keep face-downs under The Mark (5/13 were Queens, the
  straight scored with +13 from one). The build tops ~4000/hand at Pair L3 and needs a real xMult by ante 3 like every
  other flat build.
- IF a D6 tag is on the Small and you are rent-broke, THEN skipping is right ($0/$1/$2 rerolls = 6 joker views for $3), but
  only if you keep $5+ to buy what the rerolls show; with $8 total the views were useless (Joker $2 was all I could afford).
- IF the Big Blind needs > 3x your typical hand AND winning it leaves you under $0 after rent (no shop value), THEN skipping
  the Big to face the boss directly loses nothing: the boss must be fought either way and the Big only adds a death roll.
  (Here: skipped Big 13500 at $0; the Mark was lost anyway, but the Big would have killed the run one blind earlier.)
- IF money is $0-3 at an ante-4 shop with a 0.19 ratio, THEN a flat +4 joker is worth less than one Arcana pack
  (Judgement/Hierophant/High Priestess/Death); the +13% cannot bridge a 3x gap, the pack has a ~30% shot at +40-50%.
- IF Odd Todd is owned, THEN build odd pairs: A/3/5/7/9 pairs score 2x an even pair; keep odd singles over even pairs when
  discarding (Big 4800 at ante 3 was cleared with three odd pairs and no Queen).

Advisor/CLI defects (with examples):
- shopadvise ante 3 ($10, EMERGENCY 0.17): ADVICE "BUY Greedy Joker{RENTAL} $0" with SIM +0.61 while I already held a
  rental; the rule text warned "a second rental before ante 5 drains the run to $0" but the ADVICE still said BUY without a
  "sell Odd Todd first" pairing. It then said SELL FIRST Odd Todd in the next 3 shops at ratios 0.42/0.42/0.19, i.e. the
  joker that doubled my odd pairs. The sell suggestion should name the weaker rental by est contribution (Greedy +10 vs Odd
  Todd +62 chips on an odd pair), and the BUY of a second rental should be bundled with the sell.
- shopadvise ante 3 shop 2 (D6 tag): no mention that rerolls cost $0; the ADVICE was "SELL Odd Todd then BUY Ice Cream" with
  the reroll line missing. A $0 reroll should be listed first.
- `s`/blind-select ADVICE at ante 4 said "do not skip: take the shop" with $0 cash and -$6/round rent (the shop would open at
  about -$5); the rent-broke rule in the playbook should fire in the CLI (same defect as 7801_D9KFK2PH and 7801_YSBWEA3U).
- Pack advise (Mega Arcana, choose 2): ranked The Hermit 40 ("+$0") second; a Hermit at $0 is worth nothing and should rank
  below Tower/Magician.
- advise under The Mark: ests include face-downs as 5/13 Queens (fine) but the ADVICE kept Pair 66 (est 1109) over keeping
  AD + face-downs; with 18000 needed the only relevant question is "which keep maximizes P(odd pair + Queens)".
- Solver p "calibrated" was 0.90-0.99 on ante-1/2 lines that were closer to 0.5-0.6 by my own count (Manacle, Big 450): the
  playbook's "overconfident at ante 1-2" warning held every time.
Bridge issues: none (69 steps, no rejects, no offline time).
