# Run J3REMTSE (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (9378/13500)

Ante 1 (Economy/Holo/The Hook 600, $4): Small jokerless 2P KK44 96 + 2P AATT 124 + 2P 9977 104. Shop $4: Buffoon (SIM 0.22 > Chad{P} 0.08) -> Jolly. Big: disc 5 keep 33 -> FH 33322 636. Shop $6: passed Celestial (1-scorer rule). Hook: Trips TTT 660 one-shot.
Ante 2 (Meteor/Polychrome/The Head 2000, $14): EMERGENCY 0.24 -> Gros Michel{RENTAL} $1, Uranus $3. Skipped Small for Meteor (Uranus 2P L3, Earth FH L2). Big: Pair JJ 750 + 2P AA88 2646; Gros Michel destroyed at that round end (and rent charged). Shop $13: Even Steven{RENTAL} $1, passed Earth. Head: 2 digs, 2P JJ44 1344 + 2P TT88 2688.
Ante 3 (Investment/Charm/The Needle 3200, $16): Hanging Chad{E} $4. Small: 2P QQ55 1320 + TT66 4032. Shop $11: Sly $3. Big: 2P 7722 (2H led for Chad) 3696 + KKTT. Shop $11 (last before Needle, TIGHT): Clever{PERISH} $4, Celestial -> Earth (FH L3), $3 left. Needle: disc 4 keep QQ 8 6 -> drew QQQ888, FH 888QQ 7952 one-shot.
Ante 4 (Uncommon/Skip/The Tooth 18000, $5): shop had nothing affordable that scores (SCORE CHECK 0.18). Rent-broke ($2 after rent): skipped Small for the Uncommon tag. Big 13500: 2 digs (solver ~0.5) -> FH AAA22 (2C led) 8352; no discards left, dig play of 7D 5H 3C keeping KK T 6 4 (solver 0.72 vs straight-first 0.64) missed all 9 even outs; forced Pair KK 1000 -> 9378/13500. LOSS.

## Post-mortem

Binding constraint: SCALING through MONEY. Zero xMult was ever offered: 8 shop screens showed Hanging Chad (x2), Dusk{R},
Gros Michel{R}, Even Steven{R}, Red Card{R}, Sly, Hallucination{P}, Ceremonial Dagger{E}, Clever{P}, Business Card{P},
Four Fingers. The build (Jolly, Even Steven, Chad, Sly, Clever on 2P L3 / FH L3) made ~3-4k on a typical hand and 7-8k
only on a Full House or an all-even Two Pair, i.e. the ante-4 Big (4500 per hand) was a coin flip on every deal. Cash
peaked at $16; Small Blinds pay $0 and the two rentals took $18 in rent by ante 4, so no reroll budget ever existed.

Decisions I would change:
1. Ante 2 shop 1: Gros Michel{RENTAL} $1. It scored one blind and then died (1/6) at the same round end that charged its
   rent: $4 for one Big Blind I would likely have cleared anyway (AA88 2646 vs 750 left). A rental that can also self-
   destruct is the worst sticker combination.
2. Ante 2 Small skip for Meteor (2 planets): it cost a shop view at 0 xMult. Two Pair L3 / FH L2 helped, but a shop view
   was the only way an xMult could appear; with 1-2 scorers and 0 xMult I would now play the Small at ante 2.
3. Ante 4 Big hand 2: both lines were coin flips (0.64 / 0.72); the real error was arriving at ante 4 with $5.

Reusable rules (if-then):
- IF you own Hanging Chad AND Even Steven (or any per-card +mult joker), THEN `move hand` an even/qualifying card to the
  leftmost scoring position before every big hand: +25% each time here (2P 2840 -> 3696, FH 6696 -> 8352).
- IF The Needle is the boss and you own a leveled Full House plus Pair jokers, THEN dig both discards keeping the pair
  plus even/trip-able cards: FH is the only one-hand clear (FH 888QQ 7952 vs Pair QQ 1000 dealt).
- IF a Two Pair build's per-card mult joker is Even Steven, THEN odd two pairs score ~3k and even ones ~7k at L3:
  discard odd kickers first and count only even outs when digging.
- IF the shop offers Gros Michel as a RENTAL, THEN treat its expected life as ~3 rounds and its true cost as $1 + $3 x 3:
  buy it only when it decides the very next blind.
- IF you are at ante 4 with SCORE CHECK < 0.25 and <= $5 (rent-broke), THEN skip the $0 Small (its shop buys nothing),
  but know the Big is still ~50%: the fix had to come one ante earlier (keep a reroll budget at ante 3).

Advisor/CLI defects:
- `advise` replaces the SOLVER block with a REORDER suggestion whenever a Chad reorder raises the best hand, even when
  that hand cannot clear: at The Needle (one hand, 3200 needed) it said `move hand 5 4` for a 9-high straight (1620)
  instead of giving the dig advice; I had to choose the discard myself. Reorder advice should only win when the
  reordered hand clears (or be printed alongside the solver lines).
- `shopadvise` before The Needle projected the round at ~1408 (0.44x) while the dealt round made 7952 with two discards;
  the Needle projection seems to drop the discards' digging value.
- `advise` reorder suggestion at the Big ("move hand 7 1") was useful; est with the even lead matched exactly (8352).
- est exact on every play checked (3696, 7952, 8352, 1000). Bridge issues: none (65 steps, no rejects).
