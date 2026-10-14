# Run GJWWQBMF (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big (33294/37500)

Ante 1 (Double/Polychrome/The Head 600, $4): Small: 2P KK99 116 + Trips 555 135 + 2P. Shop $4: Buffoon pack -> Riff-raff{P} (SIM 0.86) over Scholar. Riff-raff made Scholar+Banner (Big: Ace high card 480 one-shot) and holo Wily + Hallucination (Head: Pair JJ 1080).
Ante 2 (Ethereal/Rare/The Wheel 2000, $14): Celestial -> Venus x2 (Trips L3, Wily holo trips 6480). Riff-raff made Swashbuckler+Egg. Skipped Big for Rare Tag -> got Vagabond{RENTAL} (junk, passed). Wheel: 2P KK55 2970.
Ante 3 (Double/Uncommon/The Flint 6400, $19): 2 rerolls -> Even Steven{E}. Skipped Small (Double) + Big (Uncommon x2) -> shop gave Cloud 9/Onyx Agate perishable (junk). Flint: Pair 88 2916 + Star->Flush 4510.
Ante 4 (Orbital/Handy/The Pillar 18000, $14): EMERGENCY 0.33 (0 xMult). Scholar->Jolly{P}, Death (QC->TD), Emperor (Magician+Hanged Man). Skipped Small for Orbital (Two Pair L4). Big 13500: 2P AA22 8300 + High 2250 + Trips 333 10516. Pillar: Trips TTT 15340 + Pair 44 3900.
Ante 5 (Negative/Meteor/The Mark 50000, $8): shop junk (Rough Gem{E,R}, holo Scholar{E}), reroll -> nothing. Small 25000: Magician lucky TT, 2P TT99 9968 + 2P 55 44 8848 + Trips KKK 10000 = cleared. Buffoon pack ($4, sold Jolly to afford) -> Mystic Summit. Big 37500: Trips TTT 13340 + Trips 888 12992 + (disc for FH, drew only JJ99) 2P 6962 = 33294/37500. LOSS by 4206.

## Post-mortem

Binding constraint: scaling. Zero xMult all run; best flat hand ~13k at ante 5 (Trips L3 + holo Wily +100 chips/+10 mult, Swashbuckler +30 mult, Even Steven). Ante 5 Big 37500 needs 12.5k x 3 with no variance; I got two 13k Trips and a 7k Two Pair.

Decisions I would change:
1. Ante 2 Big skip for the Rare Tag: the tag produced Vagabond{RENTAL} (a Rare in the first shop slot) = useless. Rare Tag is a coin flip on junk; I gave up the Big shop and ~$7 for it. Ante 3 double skip (Double+Uncommon x2) likewise produced Cloud 9 / Onyx Agate (both perishable, $0): lost two shops + two Egg/Swashbuckler growth ticks for nothing. Tag-skips for "a random joker" with 0 xMult is a bad trade; the Egg/Swashbuckler build grows +3 mult per ROUND PLAYED.
2. Ante 4 shop: hunted xMult with a reroll at $14, then Arcana packs. Never saw one all run (about 8 shops, 0 xMult-shaped jokers). No fix at that point; Riff-raff's commons (Wily holo, Swashbuckler) carried to ante 5.
3. Last hand of the ante-5 Big: after Trips 888 I discarded for a Full House (p 0.36) and drew nothing. Solver p was 0.39 vs the Two Pair floor of 6.5-7k; no better line existed.
4. Banner (+30 chips/discard left) and Mystic Summit (+15 mult at 0 discards) anti-synergize; Summit never fired usefully (hand est excludes it unless discards are 0 and it printed 6962 at 0 discards, i.e. +15 appeared not counted or small).

Reusable rules (if-then):
- IF the first Buffoon pack has Riff-raff and you have 5+ free slots, THEN take it (SIM 0.86): it created Wily holo / Swashbuckler / Egg / Banner / Scholar which carried antes 1-4. Sell the Riff-raff when slots are full (it makes nothing).
- IF you have 0 xMult entering ante 3, THEN skipping Small/Big for a random-joker tag (Rare/Uncommon) is not worth it: both shops gave unusable stock. Prefer shops, rerolls and playing every round so growth jokers (Egg/Swashbuckler) tick.
- IF a Trips-gated joker (Wily +100 chips) is held, THEN level Trips with Venus and keep 3 of a kind as the main hand; two Trips in one round (TTT 888 from a Full House deal) gave 13k each at ante 5.
- IF The Star/tarot can turn a hand into a Flush that clears the boss, THEN use it before playing (Flint ante 3: 4510 cleared with a spare hand).
- Orbital tag (+3 levels on the hand named) on a Two Pair deck jumped Two Pair 5.4k -> 8.3k: a skip that pays NOW is worth it.

Advisor/CLI defects:
- shopadvise EMERGENCY at ante 4-5 suggests Celestial packs / LEAVE with $3-8 and 0 xMult; no line exists that actually finds an xMult (not a defect so much as no option).
- hands/advise `est` for Mystic Summit: Two Pair JJ99 at 0 discards est 6962 which already looks like it excludes or barely includes +15; I could not verify actual vs est for Summit.
- Rare Tag advice: the tag item was a rental Vagabond; the advisor did not warn that the Rare tag slot could be rental/useless before skipping.
