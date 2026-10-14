# Run HABVRNM1 (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Mouth (boss, 16707/50000)

Ante 1 (Juggle/Rare/The Window 600, $4): Small flush hearts 236 + Straight 280. Shop $4: Buffoon pack -> Spare Trousers (+2 mult per Two Pair, grows; passed Wrathful{E,R}). Big 2P 348. Window: 2P AA88 464 + 2P KK44 340.
Ante 2 (Orbital/Ethereal/The Water 2000, $12): EMERGENCY 0.34; reroll -> Arrowhead $7 (+50 chips/spade; huge with Trousers mult 10+). Skipped Small for Orbital (Trips +3 levels, $0 shop). Big: 2P 624 + Pair JJ 960. Scary Face{E} $4. Water: JS high card 1045 + 2P AA88 2212.
Ante 3 (Buffoon/Economy/The Eye 6400, $7): skipped Small for Buffoon tag -> Misprint{E} + Constellation. Big: A-high Straight 10027 (est 7452). Droll (free pick). Eye: 2P AAJJ 4300 + Pair KK.
Ante 4 (Ethereal/Foil/The Mark 18000, $18): Uranus + Venus (Trips L5), sold Droll -> Sly. Small: Trips JJJ 11764. Big: 2P 7800 + Pair 4332 + 2P 6624. Mark: 4 face-down = 2P 8640, 2P 6264, Trips AAA ~12k.
Ante 5 (Charm/Boss Tag/The Plant->The Mouth 50000, $7): Neptune+Saturn (Constellation x1.4). Skipped Small (Charm: Mega Arcana -> Wheel (missed), Hierophant on 2 aces) and Big (Boss Tag rerolled The Plant into The Mouth 50000, no say in the new boss). Mouth: Justice -> glass 8S, Trips 888 16707 locked Trips, then no trips on 2 hands (needed ~16.6k twice) -> 16707/50000.

## Post-mortem

Binding constraint: scaling. Final build: Spare Trousers (+22 mult) + Arrowhead (+50/spade) + Scary Face{E} + Misprint{E} + Sly + Constellation x1.4. ~10-13k per hand at ante 5 vs 50k boss = needs ~17k/hand. No xMult beyond Constellation (x1.4 from 4 planets). Never found a real xMult: only 2 Buffoon packs, 3 rerolls all game; all money went to a $7-18 wallet.

Decisions I would change:
1. Ante 5: skipping Big for the Boss Tag turned a beatable-ish The Plant (50k, my est ~8k/hand without faces) into The Mouth, which is worse for a build whose best type (Trips) cannot be repeated 3 times. A Boss Tag reroll is a coin flip on a worse boss; only use it on The Wall/Violet/Needle-class bosses or a boss that kills your engine outright.
2. Under The Mouth I locked Trips (18k est, glass) because one hand alone needs ~17k/hand; Two Pair would have been ~11-12k x3 = ~35k, also short. Real problem was entering a 50k boss at 12k/hand.
3. Ante 4: bought Justice ($3) instead of keeping $11 for a reroll; one Glass card never mattered until the Mouth (+25% on one hand).

Reusable rules (if-then):
- IF Arrowhead/Scary-type flat CHIPS jokers sit next to a big accumulated +mult (Spare Trousers +10..22), THEN each +50 chips is worth ~+1500-2800 points per hand: Arrowhead $7 and Sly $3 gave more than Droll/Constellation. Chips jokers beat +mult jokers once mult is 20+.
- IF a Straight/Flush is made with 5 scoring cards (all hit Scary/Arrowhead), THEN it can out-score Two Pair 2x (A-high Straight 10027 vs 2P 4-6k) even at L1.
- IF The Mark (faces face-down) is the boss, THEN 4 face-down cards always contain a pair of faces: play those 4 first (it was a Two Pair 8640) and keep the visible pair for hand 2.
- IF The Mouth is the boss and you need > 3x your best hand, THEN you are already dead: spend the ante-4/5 shops on xMult hunting instead of planets (Neptune/Saturn only added Constellation +0.1 each = 7% each).
- IF skipping the Small for a pack tag with $7 in hand, THEN it is nearly free (the skipped shop was worthless): Orbital/Buffoon/Charm skips at ante 2-5 each gave a usable joker/level.

Advisor/CLI defects:
- shopadvise ranked Neptune (Straight Flush planet) +82 "feeds Constellation" while the hand it levels is never played; fine as +0.1x but the SIM said score ratio +0.03. Minor.
- advise `est` with Misprint: est is the mean; actual hands landed 0.65-1.0x of est on 4 of 6 big hands (e.g. Pair KK est 6726 -> 4332, Two Pair 9360 -> 6624). Misprint builds should plan on roll ~5-8.
- Under The Mouth, `advise` listed every non-locked hand with est 0 (correct) but `SOLVER DISCARD` kept recommending digs for Trips with p 0.2 on a round that needed two ~17k Trips; correct but the boss-reroll choice was made before that: shopadvise/`s` at the Big blind did not warn that Boss Tag could reroll into something worse than The Plant.
- `s` at ante-5 blind select says "do not skip" even though the Charm and Boss tags were both used productively here (Charm gave a pack); no Throwback.
