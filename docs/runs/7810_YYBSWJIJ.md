# Run YYBSWJIJ (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 boss The Wall (3159/12800)

Ante 1 (Voucher/D6/The Goad 600, $4): Small: Flush 292 + Pair KK. Shop $5: Buffoon pack -> forced choice Photograph{PERISH} vs Jolly{ETERNAL,RENTAL}; took Jolly (SIM 0.96 vs 0.49), $1 left. Big: Pair JJ 300 + Flush 280. Goad: Flush 284 + Two Pair 9955 390 (debuffed spades). Money after every round: $1 -> $-2 -> $3 -> $0 -> $6.
Ante 2 (Charm/Skip/The Wheel 2000, $6): EMERGENCY 0.24 -> Wily{ETERNAL} $4 (+100 chips on trips). Skipped Small for Charm tag: Mega Arcana -> Strength (8D->9D, 5D->6D) + Hierophant (bonus on 9H, 9C). Big 1500: 2P 460 + 2P 540 + 2P 620 = 1620. Wheel 2000: 2P QQ99 880 + 3-facedown pair play 1379 (cleared).
Ante 3 (Orbital/Standard/The Wall 12800, $6): Celestial pack -> Venus (Trips L2). Skipped Small for Orbital tag (+3 Pair levels, L4). Big 4800: Trips 444 2106 + Pair 99 1729 + Pair AA 1001 = 4836 (cleared by 36). Shop $3: The Fool -> Venus (Trips L3). Wall 12800: only 3159 (best hand ~2700 trips / 1339 pair). LOSS.

## Post-mortem

Binding constraint: money / scaling. A forced Buffoon-pack pick at ante 1 offered only Photograph{PERISH} or Jolly{ETERNAL,RENTAL}; I took the Eternal Rental Jolly (SIM +0.51) and its -$3 every round (unsellable) held me at $0-6 through ante 3: every shop was a $3-6 shop and I could never afford an xMult, a Buffoon pack ($6) or a reroll ($5). Round income (Big $4-5 + hand bonus) was consumed by rent. Result: 2 flat jokers (Jolly + eternal Wily) and zero xMult at ante 3 boss The Wall (needs 12800, my best hand ~2.1-2.7k, p 0.00).

Decisions I would change:
1. Ante 1 pack pick: Photograph{PERISH} (x2 on face) would have kept the economy intact; the eternal rental drained ~$3 per round and, with Small paying $0, left $0-6 in every shop (never reached the $8-10 for a Buffoon pack/xMult). SIM overrated Jolly because it cannot see rent shortfall blocking later buys.
2. Ante 2 shop: bought Wily{ETERNAL} (second eternal flat) with $4 of $6. Conditional on trips; it did produce 2106-trips twice but left a stuck slot and $2.
3. Ante 3 Wall: with a flat build the Wall at ante 3 (12800) is a hard wall; no Luchador/Chicot/Director's Cut was affordable. Should have prioritized hoarding for a reroll in ante 3 Big shop instead of The Fool+Venus (+30% trips only).

Reusable rules (if-then):
- IF a forced Buffoon pick offers an ETERNAL+RENTAL joker vs a non-rental perishable xMult/scorer, THEN take the non-rental one at ante 1: eternal rentals cost -$3 every round for the whole run and no shop after that can afford xMults (this run had $0-6 at every shop).
- IF you own a rental and the Small Blind pays $0, THEN skip every Small that has a useful tag (Charm = Mega Arcana, Orbital = +3 levels): it also saves the -$3 charge.
- IF Strength is offered in a free Arcana pack with a pair of 9s in hand, THEN rank 8D->9D and 5D->6D to increase pair/trips density permanently (duplicates appear in the deck; est unaffected until drawn).
- IF the boss is The Wheel and 3+ cards are face-down, THEN play the visible pair plus ALL face-downs (they drew into a winning Pair/TwoPair 1379 here) rather than discarding blind.
- IF the Wall (x2) is the ante 3 boss and the build has 0 xMult and best hand < 3k, THEN the run is lost at that boss; avoid reaching ante 3 on a flat build with < $8 by taking money/xMult routes at antes 1-2.

Advisor/CLI defects:
- Pack `advise` ranked Jolly Joker{ETERNAL,RENTAL} #1 by SIM (+0.51) and the pick note said only "-$69"; SIM ignores that rent leaves $0 at every later shop so no xMult/Buffoon is ever buyable (blind spot noted in PLAYBOOK).
- Shopadvise at the ante-3 pre-Wall shop recommended `buy The Fool` as BUY (rank 30) without saying it copies Venus (Trips) not the main hand; SIM said all options under noise.
- `advise` rule line recommended discarding 5 cards that broke good Q/J/T/9 Straight draws vs the solver's pair lines; fine, but rule lines vs solver disagreed often at ante 2 (e.g. 0.57 vs 0.90 for the Big Blind discard).
