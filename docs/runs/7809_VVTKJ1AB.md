# Run VVTKJ1AB (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Pillar (1628/2000)

Ante 1 (Foil/Foil/The Goad 600, $4): Small 300: disc 4 keep JH 9H 8H 6H 3H, Flush H 284 + Two Pair JJ99 116. Shop $5: Buffoon pack $4 (nothing else scored) -> Delayed Gratification{E} / Turtle Bean: took Turtle Bean (+5 hand size, -1/round). Big 450: FH 888JJ 336 + Flush H 260. Shop $6: Gluttonous Joker $5 (+3 mult per Club, clean). Goad (spades debuffed): Straight Q-8 469 + FH 222KK 448 = cleared with a hand to spare.
Ante 2 (Boss Tag/Foil/The Pillar 2000, $7): Shop: Buffoon pack $4 -> Bull{E} / Juggler{PERISH}: took Juggler ($3 left). Small 1000: Club Flush AC KC TC 9C 4C 1501 one-shot (Gluttonous x5). Shop $5: Temperance $3 (+$7 sell values), reroll $5, sold Juggler -> Seltzer $6 (retrigger all cards, 10 hands; $0 left). Big 1500: FH TTT22 1728 one-shot (Seltzer ~x2). Shop $6: Celestial pack -> Jupiter (Flush L2), $2. Pillar (9-card hand, played cards debuffed): disc keep JJ99, FH JJJ99 1180, Straight 280, disc 5 for a 4-heart flush draw (solver p 0.85) missed, last hand Two Pair AATT 168 -> 1628/2000. LOSS.

## Post-mortem

Binding constraint: only 2 real scorers (Gluttonous = clubs only, Seltzer = temporary retrigger) and 0 xMult at ante 2; the Pillar boss debuffed every card I had played in Small/Big (5 clubs + 5 FH cards) and with hand size 9 and Turtle Bean shrinking, the last two hands had no good outs. Money was $0-2 at every shop (Small pays $0): I could not buy a second +mult joker; Seltzer ate the money that would have been a permanent scorer.

Decisions I would change:
1. Ante 2 Pillar hand 1: with 2 discards I discarded 5 cards keeping JH JD 9S 9C (FH draw) and later spent the last discard drawing to a heart flush. A solver p of 0.85 for the final hand was a 0.73 flush draw plus a pair fallback that could not reach 540; the real fallback (Two Pair ~168) was far below the need. When the made-hand floor is < 0.4 of the need, the p is basically the draw p; I took a ~27% loss on the last hand after a 0.91 line on hand 2 that left 540 with a ~0.93 'solver' line.
2. Ante 2 Small: the Club Flush one-shot (1501 vs 1000) was played with 5 cards that were then debuffed at the Pillar. A cheaper clear (e.g. Full House / Two Pair not using the clubs) would have kept clubs for the boss. The advisor printed 'fewest, lowest cards' but still advised the 5-card Flush.
3. Ante 2 Small shop: selling the perishable Juggler to buy Seltzer was fine for the Big (1728 one-shot) but a rotating 10-hand joker did not carry the Pillar. Alternative: keep $6 for the post-Big shop (reroll/Buffoon for a permanent +mult).

Reusable rules (if-then):
- IF The Pillar is this ante's boss AND your engine is one suit (Gluttonous/clubs, a flush build), THEN clear Small/Big WITHOUT that suit's cards (play off-suit pairs / FH) so the boss still has them; the one-shot 1501 Club Flush cost the boss round its +mult cards.
- IF Seltzer (retrigger all cards, 10 hands) is bought, THEN it lasts ~3 rounds (10 hands, tick per played hand): buy it only with a plan for the next 3 blinds; it multiplies card scoring ~x2 (FH 1728 vs ~900), but it is not a permanent scorer.
- IF the last hand needs > 3x your best made hand, THEN the solver p is just the draw p; with a 4-card flush draw and 1 discard it is ~0.7, not safe: bank more on earlier hands (I played Straight 280 on hand 2 instead of discarding for a bigger hand because the solver preferred it).
- IF you are at hand size 9 (Turtle Bean decayed) under The Pillar, THEN 3 debuffed held cards cut the usable hand to 6: expect fewer outs; dig earlier.

Advisor/CLI defects:
- advise on the Pillar Small recommended the 5-card Club Flush (1501) 'fewest, lowest cards' although it burns 5 clubs that Gluttonous needs at the boss.
- shopadvise ranked Temperance (+$7) first at 60 then 'LEAVE'; the reroll with $9 was my call. Not a defect.
- Solver p 0.93 for 'play Straight 280 with need 820 and 1 hand left' (hand 2 of the Pillar): the line effectively assumed the last hand would reach 540 from a fresh 5-card draw; actual last-hand p was ~0.73 flush + ~0.0 other. The model seems to overestimate last-hand outs under The Pillar (3 debuffed held cards).
- Turtle Bean was valued +0.16 by SIM at ante 1, and 'Delayed Gratification{E}' ranked 30 by the rule; both are fine.
