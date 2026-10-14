# Run YKQMDZUK (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 7 blind Big Blind (131020/165000)

Ante 1 (Juggle/Uncommon/The Goad 600, $4): Small Flush clubs 280 + Pair 52. Shop $5: Raised Fist $5 (+2x lowest held rank mult; holding high cards = big mult, even 1-card plays est 100+). Big: Pair 4s + fillers 396 + 2P QQJJ 360. Shop $5: Odd Todd $4. Goad: Pair 5s 1148 one-shot.
Ante 2 (Ethereal/Meteor/The Pillar 2000, $8): Baron $8 (xMult per held K). Skipped $0 Small for Ethereal tag -> Spectral pack: Wraith (money already $0) -> foil Campfire. Big 1500: 2P 1200 + High 3C 801 (1 card, Pillar prep). Pillar: High AD + fillers 2085 one-shot.
Ante 3 (Garbage/Orbital/The Arm 6400, $13): Celestial -> Uranus, Mercury, Jumbo Celestial -> Mercury (Pair L3). Small 2670+1183, Big 3473+3339, Arm: Straight L1 3840 + 2P 3564.
Ante 4 (Uncommon/Buffoon/The Water 18000, $15): EMERGENCY ratio 0.25. 2 rerolls found Constellation $6 (unaffordable). Celestial -> Uranus. Skipped Small (Uncommon tag) AND Big (Buffoon tag, no shop before boss at $0): pack gave foil Abstract{E} (+3 mult/joker) + Wrathful. Water: Pair 8360 + Pair 6864 + Pair 4960 = 20184 (no discards).
Ante 5 (Rare/Boss/The Psychic 50000, $5): Uncommon tag = free Seltzer{P}. Sold Wrathful (Campfire +0.25), bought Seltzer. Skipped Small for Rare tag -> free Blueprint{P}; sold Seltzer, Blueprint left of Baron then re-ordered left of Abstract. Big 37500: Pair 11115 + 2P 28200. Psychic: Trips+fillers 21228 + 2P+filler 29250 (5 cards always).
Ante 6 (Negative/Foil/The Tooth 120000, $12): Sold Baron + Campfire flips (buy Jolly $3 sell $1) -> Banner{E} $5; Jumbo Spectral -> Wraith -> The Duo (x2 on Pair), Blueprint moved left of Duo (x4). Skipped Small (Negative tag -> free Trading Card, bought and sold for $5 + Campfire). Big 90000: Pair 68327 + Pair 71337. Tooth: Trips+fill 69264 + Pair 54056 (Campfire x2).
Ante 7 (Voucher/Ethereal/The Serpent 220000, $5): Campfire reset to x1 after Tooth boss (halved every hand). Venus flip -> x1.25. Small 110000: Pair 40515 + 44655 + 50525 = 135695. Big 165000: Pair 37245 + Quads QQQQ 51750 + Pair 42025 = 131020. Blueprint perished at the Big round end. LOSS.

## Post-mortem

Binding constraint: scaling. A flat build (Raised Fist + Abstract + Banner chips) with ONE real xMult (Duo, x4 with Blueprint, which was perishable) and Campfire (reset to x1 after each boss). Ante 7 Small/Big need 55k/hand and I made 40-50k (solver: UNWINNABLE at the Big). No Pair levels beyond L4 and no money ($3-6 at each shop from ante 5) to feed Campfire or buy xMult.

Decisions I would change:
1. Ante 5-6: spent Celestial packs ($4-6 each) that gave Uranus/Venus (off-hand). Pair stayed L4; Mercury never showed after L4. Better: those $ into Campfire flips (each ~$2 net = +0.25 xMult = +14-20% score) BEFORE the boss reset.
2. Sold Baron at ante 6 (x1.5/king held) for Banner. Reasonable, but Blueprint was left copying a perishable chain; I never had a permanent second xMult. Should have kept hunting rerolls when $ allowed instead of Celestial gambles.
3. Ante 7 Small: skipped nothing. The Big was a 0.67x round; no way to prepare because Small pays $0 and I was at $3.
4. Ante 4 double skip (Small+Big) was right: round 10.5k vs 13.5k Big; Buffoon pack gave Abstract. Water cleared with Abstract.

Reusable rules (if-then):
- IF Raised Fist is owned, THEN play pair + low fillers and hold A/K/Q/T: lowest held rank x2 is +20-28 mult (hand est 3-5x a no-fist hand). Hold high cards; play lowest cards as fillers.
- IF Campfire is owned, THEN every sale (jokers AND consumables via sellc) is +x0.25; buy any $0-3 item with a free slot and sell it back (net ~$1-2). A free Negative Trading Card sells for $5: pure profit +0.25. It resets after the boss, so flip BEFORE each ante's boss, and keep a free slot.
- IF a Wraith/Rare tag gives Blueprint, THEN put it directly left of the best xMult (Duo/Baron) when that xMult fires on the hands you play; Blueprint left of The Duo doubled x2 -> x4. Blueprint was perishable: sell it the round it dies.
- IF an Uncommon/Rare/Negative tag is on the Small and money is $0-3 (the Small shop is unusable), THEN skip it: all three paid a joker (Seltzer, Blueprint, Trading Card) and skipped blinds do not tick perishables.
- IF the first Spectral pack shows Wraith while money is $0 and a slot is free, THEN pick it (random Rare, no cost).

Advisor/CLI defects:
- shopadvise at ante 3 EMERGENCY says "Celestial pack, take Uranus" three times; packs held Pluto/Venus/Earth etc. SIM called Celestial gambles +0.00..+0.03.
- `advise` kept recommending DISCARD over a solver PLAY with higher exp (e.g. Water/Small ante 7) - the ADVICE line follows the rule pick, not the solver top line when p ties.
- ORDER FIRST suggestion at the Psychic (Blueprint retarget from Baron to Abstract) was correct (+55%), but it ignores that Baron needs held Kings later in the same round.
- Hand est excludes held-card effects when planning discards; `sel` with fillers (Pair + low cards to remove the lowest held card) showed +40-100% vs the bare Pair (Raised Fist), `hands` does not list those.
