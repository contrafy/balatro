# Run YYSKPHK2 (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 boss The Arm (3949/6400)

Ante 1 (Investment/D6/The Window 600, $4): Small: pair bank 60 + Flush 280 (solver). Shop $5: Supernova{ETERNAL} $5 (only scorer, SIM +0.24). Big: Two Pair AAJJ 186 + Straight K-high 395. Shop $5: Wrathful{RENTAL} $1 (+3 mult/spade). Window: Two Pair 370 + Full House 315.
Ante 2 (Ethereal/Foil/The Psychic 2000, $7): no jokers in shop; Celestial pack -> Uranus (Two Pair L2). Small: Straight 720 + Two Pair 612. Shop $1: sold Wrathful, bought Mystic Summit{RENTAL} $1 (+15 mult at 0 discards). Big: burned both discards on junk, Two Pair AA88 1716 one-shot. Psychic: Flush 1638 + Flush 1584.
Ante 3 (Boss Tag/Handy/The Club 6400, $7): shop: only Dagger/Emperor/Celestial packs; Jumbo Celestial -> Saturn (Straight L2), $1 left. Skipped Small (Boss Tag; rerolled The Club -> The Arm 6400, $0 Small, saves rent) AND Big (Handy Tag only +$11: counts hands played). No shop before boss. The Arm: Flush 1817 + Flush 1752 + Pair 380 = 3949/6400.

## Post-mortem

Binding constraint: scaling/economy. Ran ante 1-3 on 2 jokers (Supernova{E} +small mult, Mystic Summit{R} +15 mult). Rent ($3/round) plus $0 Small kept me at $0-7 in every shop, and only 1 joker was ever purchasable at a price I could afford; zero Buffoon packs, zero xMult sightings in 5 shops. Round ~1600/hand vs The Arm 6400 (needs 2133/hand x3).

Decisions I would change:
1. Skipping Small for the Boss Tag rerolled The Club (mild: clubs only) into The Arm (-1 level per hand type). The Boss Tag is a coin flip that more often swaps a mild boss for a worse one; take it only to escape a known killer (Wall/Needle/Violet Vessel).
2. Skipping the Big for Handy: it paid only $11 (hands played so far) and cost the shop between Big and boss, where I had $1 + $11 to spend. A Handy/money tag that costs the pre-boss shop is a bad trade unless the boss is already beatable; playing the 4800 Big (~45%) with a shop afterwards was not clearly worse. Together the two skips left me at the boss with no way to buy anything.
3. Ante 3 first shop: Jumbo Celestial ($6) for Saturn instead of holding $7 for interest / next joker. Level gains were small (+~10%) and left $1.

Reusable rules (if-then):
- IF you own Mystic Summit, THEN burn BOTH discards on junk (keep the made hand) every round: Two Pair 462 -> 1716 and Flush 468 -> 1638 at 0 discards. `advise` says so; always follow it.
- IF a Handy Tag shows, THEN it pays only $1 per hand played this run (~$11 at ante 3, not $20+): it is not a money tag worth skipping a shop for.
- IF the Boss Tag would reroll a mild boss (The Club/Window/Head), THEN do not skip for it.
- IF you hold <= $7 with a rental in play at ante 3, THEN skipping the $0 Small saves $3 rent, but still keep the Big's shop unless the Big is unwinnable.
- Flush/Straight can carry ante 1-2 with Summit/Supernova (all hands cleared 1.0-1.7x), but ante 3 needs xMult: none appeared.

Advisor/CLI defects:
- `s` at the ante-3 Small recommended `b skip` for Boss Tag; the tag swapped The Club for The Arm, a worse boss for a flat Flush build with no counters; skip advice should discount Boss Tag unless the current boss is a killer.
- shopadvise EMERGENCY flagged "buy cheapest multiplier" while offering no affordable one; at $7 it advised a $6 pack leaving $1 and rent due, i.e. effectively broke next shop.
- Handy Tag value was not shown in `s` skip advice (actual $11).

Note: the orchestrator's new rule (no flat rental at antes 1-2, rental_study.md) arrived after the run ended; this run bought Wrathful then Mystic Summit (both flat rentals) at antes 1-2. Rent plus the $0 Small kept every shop at $0-7, which matches the study. Summit did carry ante 1-2 (about 3x score), but the economy cost left nothing for a permanent +mult joker.
