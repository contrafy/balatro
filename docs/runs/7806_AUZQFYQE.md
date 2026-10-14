# Run AUZQFYQE (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Small Blind (606/1000)

Ante 1 (Double/Investment/The Goad 600, $4): Small: 2 discards to KQJT, Broadway Straight 324/300. Shop $6: Buffoon $4 -> only To Do List{ETERNAL} / Troubadour{ETERNAL}; took To Do List (advisor SIM said Troubadour). Big: 2P KK99 116, Straight J-7 296, 2 free digs for trips (missed), 2P QQ77 108 -> 520/450. Shop $6: Jupiter $3 (Flush L2, SIM 0.08 vs 0.00). Goad: disc 5, diamond Flush 510 + heart Flush 570 -> 1080/600.
Ante 2 (Holo/Foil/The Wheel 2000, $9): shop had Wily{ETERNAL} $4 + Earth; rerolled ($9 -> $4) -> Photograph $5 (unaffordable by $1) + Drunkard{PERISH,RENTAL}; left with $4. Small 1000 with 0 scorers: disc to clubs, Flush 546, dig Pair 33 (kept 3 spades, drew 1 of 2 needed), Pair 22 28 -> 606/1000. GAME OVER.

## Post-mortem

Binding constraint: zero scoring jokers entering ante 2 (MONEY + pack luck). The only joker in 4 shop views + 1 Buffoon pack that
scored and was affordable never appeared; the one that did (Photograph $5, an xMult) was $1 out of reach because I had just
spent $5 on the reroll that revealed it. Without jokers the ante-2 Small (1000) needs two Flush L2 hands out of 3.

Decisions I would change:
1. Ante 2 shop, $9: the reroll ($5 -> $4 left) was the losing move. Common/uncommon scorers and Photograph cost $4-6; with $4
   left the reroll could only reveal a $4 joker. Better: keep $9, play the Small with To Do List (High Card was listed = +$4),
   or reroll only if $6+ stays after. The advisor's zero-scorer reroll cap ("keep $3-4 so a $3 Sly/Jolly is affordable")
   is one dollar too tight.
2. Ante 1 Big shop: Jupiter $3. The Goad was cleared 1080/600; two Flush L1 (~320 each) plus any pair would also have
   cleared it. That $3 would have made the ante-2 reroll leave $7 (Photograph affordable).
3. Ante 1 Small shop: Buffoon pack ($4 of $6, SIM 0.37) vs Blackboard{PERISHABLE} $6 (SIM 0.23). The pack whiffed (two
   eternal non-scorers). Defensible either way; the pack was the higher-EV call.

Reusable rules (if-then):
- IF you own 0 scorers at ante 1-2 AND a reroll would leave you under $5, THEN do not reroll: a reroll that shows a $5
  Photograph/Hologram/$5-6 joker you cannot buy is pure loss; bank the money for the next shop (+interest, +To Do List).
- IF a Buffoon pack offers only eternal non-scorers (To Do List, Troubadour), THEN never take Troubadour{ETERNAL}: -1 hand on
  Black Deck is permanent (3 -> 2 hands every round). To Do List{ETERNAL} is a $4/round economy joker at the cost of a slot.
- IF your build has no jokers at ante 1, THEN planets for a side type (Jupiter) only when the boss is otherwise lost; money
  for the first joker outranks a level you can win without.
- IF the final hand needs a Flush to clear and no discards remain, THEN dig with a 5-card play of off-suit cards keeping
  the 3+ suited cards (P(flush) ~25% with 3 held and 6 left in 30); it missed here.

Advisor/CLI defects:
- Buffoon pack `advise` (ante 1): ADVICE `pick 2` Troubadour{ETERNAL} because SIM 0.11 > To Do List 0.08 over 3 blinds; the
  SIM horizon ignores that an eternal -1 hand is permanent. The rule pick (To Do List) was right; SIM should not
  override toward an eternal resource-penalty joker.
- shopadvise ante 2 ($9, 0 scorers): rule advice REROLL with "$4 left after"; the reroll showed Photograph $5, unaffordable.
  The zero-scorer reroll floor should be >= $5 (most scorers cost $4-6).
- shopadvise ante 1 Big shop marked "TIGHT ... projected round ~458 vs Goad 600" and pushed Jupiter; actual round was 1080
  (flush-heavy deal). The projection ignored that Flush L1 x2 already clears 600.
- advise first discard on the ante-2 Small proposed "keep AC KS 3S (breaks AA, KK)" as the top solver line (p 0.48) over
  keeping two pair or 3 clubs (0.47); n=100 noise is choosing odd lines.
Bridge issues: none (29 steps, no rejects).
