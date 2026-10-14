# Run ME9AMTUQ (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 8 blind Crimson Heart (152568/400000)

Ante 1 (Charm/Juggle/The Hook 600, $4): Small FH 333KK 276 + 2P 124. Shop $5: Odd Todd $4 (SIM 0.56 vs Buffoon 0.38). Big: Straight 632 one-shot. Shop $7: Card Sharp $6 (x3 on a repeated hand type). Hook: disc 3 for a straight draw, Straight 5-9 632.
Ante 2 (Holo/Garbage/The Pillar 2000, $8): EMERGENCY 0.19 -> foil Turtle Bean{RENTAL} $1 (+5 hand size decaying). Skipped Small (Holo tag = free holo Gift Card). Big 1500: Flush clubs 764 then disjoint Flush diamonds x3 1788. Shop: free holo Gift Card, Photograph{P} $5. Pillar: FH 77755 3864.
Ante 3 (Rare/Orbital/The Mouth 6400, $8): Skipped Small (Rare tag): the tag gave Brainstorm{RENTAL} $0. Big: Straight 3348 + Two Pair 1896. Shop: sold Turtle Bean (rental swap), Swashbuckler $4 (+mult = sell value of other jokers), Brainstorm copying leftmost Swashbuckler. Mouth: Two Pair 8944 one-shot.
Ante 4 (Rare/Juggle/The Plant 18000, $15): sold Photograph -> Blueprint $10 left of Card Sharp (x9 on repeats). Skipped Small (Rare tag -> Obelisk, passed: any repeat-type play resets it). Big/Plant: High Card spam: 1st High Card (3k), 2nd High Card x9 (22-27k) clears.
Ante 5 (Coupon/D6/The Head 50000): High Card chain every blind (3 hands: 3.5k, x9 ~34-43k, x9 ~37k). Planet Uranus. Never skipped (no Throwback).
Ante 6 (Meteor/Voucher/The Wall 240000): Small HC chain 96k. Big: Pair 55 + Pair AA x9 103k. Arcana pack -> Temperance +$50. Sold Gift Card for Blue Joker ($5, +2 chips per deck card: chips x2.9). Wall: HC chain caps ~230k, so Pair chain: H1 Pair 22 + 2 fillers (draw 4), disc for odd singles AH 7S 5H 3C, drew AA + 77: 9k + 137.6k + 127k = 273k. CLEARED.
Ante 7 (Rare/Boss/The Tooth 220000): Small Pair 66 + Pair 77 x9 (177k). Big: HC chain 256k. Black Hole (all hands +1), Mercury, Pluto, Saturn from packs. Tooth: HC chain 280k.
Ante 8 (Coupon/Juggle/Crimson Heart 400000, $3): skipped Small and Big (Juggle +3 hand size). Crimson Heart: H1 Odd Todd off, Two Pair 9988 22k; H2 Blueprint off (x3 only), Two Pair 6633 78k; H3 Swashbuckler off -> M collapsed to base 6, Two Pair AA77 x27 53k (reordered Blueprint, Card Sharp, Brainstorm): 152568/400000. LOSS.

## Post-mortem

Binding constraint: the ante 8 Crimson Heart boss against a one-point-of-failure engine. Every blind from ante 4 to 7 was cleared by "hand 1 registers a type, hands 2-3 repeat it": Card Sharp x3 with Blueprint (copy) = x9 on the repeat, +mult from Swashbuckler (sell values of other jokers) copied by Brainstorm (+96 mult), Odd Todd/Blue Joker chips. That is x9 on a mult of ~100 for 2 of 3 hands (~135k per High Card, ~200k per odd Pair). Crimson Heart disables exactly one joker EVERY hand (never the same twice): the estimated 3-hand total with one joker off per hand is ~250k at best, and only ~5% of simulated lines reach 400k. Swashbuckler off (M 6 instead of 102) was the killer; Card Sharp off or Blueprint off lose x3-x9 too.

Decisions I would change:
1. Ante 6 shop: I sold Gift Card (holo, grows every joker's sell value, i.e. Swashbuckler) for Blue Joker. Right for the ante 6 Wall (+x2 score) but it ended Swashbuckler's growth (+10 mult per round); the engine stalled at ~280k per round from ante 6 and never grew toward 400k.
2. Never found a second independent multiplier (xMult, Duo, Throwback) or a boss counter (Luchador, Chicot, Director's Cut). With $20-50 I rerolled only at ante 6. At ante 7 ($33) I rerolled once and skipped Throwback (x1.75, would have needed selling Odd Todd).
3. Built 6/6 slots with every joker load-bearing. A decoy/redundancy slot (a flat +mult or a junk joker) halves the odds that Crimson Heart hits Swashbuckler/Card Sharp.
4. Ante 8: skipping Small and Big (to avoid a 300k Big the HC chain could not clear and take Juggle +3 hand size) was right for survival but left no shop before the boss.

Reusable rules (if-then):
- IF you own Card Sharp + Blueprint (left of it) and a +mult stack, THEN every round is: hand 1 = cheapest card of the type you will repeat (1-card High Card ~3-12k), hand 2 and 3 = the two best cards/pairs of that type at x9. Check `hands` after hand 1: the est shows the x9 values. Pair of ODD ranks (with Odd Todd) beats High Card by +40%.
- IF the High Card chain tops out below the boss (Wall 240k: HC chain ~230k), THEN switch to a Pair chain with fillers: H1 low pair + fillers (draws 4-5 cards), discard non-odd singles, aim for two odd pairs; simulated 80% vs 0% for HC. Each card drawn costs Blue Joker 2 chips x9 hands, so count it.
- IF Swashbuckler is your +mult, THEN Gift Card (+$1 sell value per joker per round) is its growth engine and Temperance (shop/pack, = sum of sell values, max $50) converts it into cash: Temperance paid $50 at ante 6 and funded the Blue Joker/planets.
- IF the boss is Crimson Heart, THEN the win condition is 3 hands where EVERY hand survives its own disabled joker: you need baseline per-hand scores ~2.5x the boss/2 and engine redundancy (decoy jokers, two +mult sources, no copy chain whose root can be disabled). Do not enter ante 8 with the whole score in Swashbuckler -> Brainstorm and Card Sharp -> Blueprint.
- IF a Rare tag gives a rental joker (Brainstorm) or Obelisk, THEN rentals are fine with a rental swap (sell Turtle Bean the same shop) but Obelisk conflicts with repeat-type engines (reset every repeat).
- IF the Big blind needs more than your 3-hand HC chain at ante 8 (300k vs 276k), THEN skipping it for Juggle (+3 hand size) is correct: only the boss must be beaten.
- Black Hole from a Jumbo Celestial pack (Spectral inside a Celestial pack) levels all hands: take it over a single planet.

Advisor/CLI defects:
- shopadvise at ante 8 (Duo rental) proposed SELL Odd Todd then BUY The Duo; my est shows Odd Todd chips (+62 on odd pairs) offset Duo x2 almost exactly, and HC chain loses 38%. SIM undervalues Odd Todd's share of chips.
- shopadvise ante 7 recommended Throwback{P,R} selling Odd Todd (SIM +0.18) while skipping would have been needed to grow it; it never evaluated that no slot of this engine is spare.
- `advise` under Crimson Heart suggests a 1-card throwaway to re-roll the disabled joker, but with 3 hands (Black Deck) there is no spare hand when Card Sharp needs a registered type; the advice should only appear when hands >= 4 or the engine does not need registration.
- Card Sharp est: the "x3 if repeat" notes are accurate (all est matched exactly), but `advise` ADVICE lines at ante 3-7 showed "PLAY TWOPAIR ... later hands x3" even when a High Card chain with fillers-free single cards scored 2-3x more; the solver does not model single-card x9 repeats.
- `s` prints 'do not skip' at ante 8 Small/Big with no mention that only the boss matters; skipping both was the right call there.
