# Run X2VSWGJH (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind The Manacle (518/600)

Ante 1 (Economy / Rare / The Manacle 600, $4): Small 300: heart Flush KH6H4H3H2H 240 + 2P 8866 96. Shop $5: only Flower Pot{ETERNAL} / Castle{ETERNAL} $6 (unaffordable) -> Buffoon $4: Hallucination vs Faceless{ETERNAL,RENTAL} (took Hallucination). Big 450 (played, Rare tag not worth skipping into the boss jokerless): 2P 8866+filler 96 (solver p0.85 over discard 0.76), drew QQQ AA KK -> FH QQQAA 368. Shop $6: Ride the Bus{ETERNAL} $6 (only scorer; SIM p_next 0.01 vs 0.00). Manacle (7 cards): 2P 7766 + Q filler 138 (solver 0.47 vs disc 0.42), disc KQJ22 keep T3 (0.56), disc T43 keep 9885 (0.53), dig Pair 22 56 (0.40 vs 2P 8822 0.31), last 7 cards QS 9H 8S 8H 8D 7S 5H: Trips 888 324 vs 406 left. 518/600. GAME OVER.

## Post-mortem

Binding constraint: no scorer at ante 1. Two $0-income rounds left $5 and $6 for the two shops; the first shop's only
jokers were $6 eternal conditional ones, the Buffoon pack held Hallucination + an eternal rental Faceless Joker, the
second shop's only scorer was Ride the Bus (+1/+2/+3 mult over the boss). Three L1 hands on 7 cards against 600 needed
~200 each; the deck gave two pairs and a trips.

Decisions I would change:
1. Small Blind skip for the Economy Tag: it doubles money (max +$40), so at $4 it gives +$4 right away. Playing the Small
   gave $5 at shop 1 (Small pays $0 + $1 unused hand). Skipping would have meant the Big Blind shop with ~$8 + Big payout
   ~$5 = ~$13 instead of $6 - enough for a $6 joker plus a Buffoon pack. Not clearly better (a jokerless Big Blind 450 is
   ~15% to lose), so I would keep playing it; but note the Economy Tag is worth exactly your current $ (cap $40).
2. Manacle second discard: the solver ranked keep 9H 8S 8H 5H (0.53) and keep TD 9H 8S 8H (0.52) equal; the second would
   have made J-T-9-8-7 on the deal that came. Hindsight on draw order, not a rule.
3. Shop 1 alternative: Celestial pack $4 (Two Pair/FH level) instead of Buffoon would not have changed the boss. The
   Buffoon pack was correct by the policy; the pack was just empty.

Reusable rules (if-then):
- IF ante 1 shop 1 has no affordable scorer and the Buffoon pack offers only utility/eternal-rental jokers, THEN take the
  harmless utility (Hallucination) and keep $1+, and in shop 2 buy the first unconditional +mult joker even if Eternal:
  a jokerless Manacle/Wall/Needle boss at ante 1 is ~50% lost.
- IF the boss is The Manacle (7 cards) and you hold <=1 weak scorer, THEN each dig draws only as many cards as you play:
  prefer keeping straight-connected cards (T-9-8 + pair) over a lone kicker, since a 7-card hand rarely completes a
  flush and pair-family hands at L1 cannot reach 200 each.
- IF a 5-card ante-1 boss deal holds Two Pair and no draw, THEN banking the Two Pair with a face filler (keeps Ride the
  Bus growing) and digging with both discards was the solver's line (0.47); it still lost - ante-1 bosses with one weak
  joker are close to coin flips, so the joker must come from shops 1-2 at any sticker cost short of an eternal rental.

Advisor/CLI defects:
- [INFERENCE] SOLVER on the last-but-one Manacle hand: "PLAY 1 6 7 (dig Pair 22, keep 9H 8S 8H 5H) p 0.40 (calibrated)".
  Counting outs with 7-card hand size (3 draws from 29-32 cards, need 406 with Ride the Bus +3: only Flush ~8%, Full
  House ~7%, Straight 5-9 ~2%, Quads) gives ~0.18; Trips 888 (324) does not clear. The solver may be drawing to 8 cards
  under The Manacle (or calibration inflates low-p digs). Check Manacle hand size in the solver.
- SIM line in the ante-1 shop printed "p_next 0.01 (+0.01)" for Ride the Bus vs "0.00" baseline: next-3-blinds p is
  uninformative at ante 1 with no scorer (it includes ante-2 blinds a jokerless deck cannot clear).
Bridge issues: none; 18 steps, no rejects.
