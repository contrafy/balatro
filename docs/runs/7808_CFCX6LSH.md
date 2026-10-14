# Run CFCX6LSH (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 2 Big Blind (557/1500)

Stale run first (seed UQPYJH7B, inherited mid-blind on port 7808 from a parked agent; Main approved playing it out): LOSS at ante 2 Small Blind (724/1000). Only joker Matador (never paid on The Hook); Hook cleared with 2P+FH+Flush; shops offered no scorer (Hallucination rental, Satellite perishable), took Uranus x2 (Two Pair L3), $0, lost Small: both discards went to Two Pair draws that missed.

Ante 1 (Small 300 / Big 450 / The Pillar 600, $4): Small 2P 9966 + 2P TT44 + Straight 9-5 260 (cleared at last hand). Shop $4: no scorer except Banner{PERISHABLE,RENTAL} $1 (advisor NEEDED NOW) vs Buffoon pack $4; took Banner (+30 chips per remaining discard = +60 on every hand, High Card 76). Big: Pair 99 176 + 2P 8833 204 + Pair 44 156. Shop: nothing ($4). Pillar: Pair 55 + 3 fillers 160, then Straight T-6 464 (debuffed cards score 0 but still form the hand) = 624/600.
Ante 2 (Flint boss 2000; $7 after rent): EMERGENCY 0.16, shop had Splash/Magician only; Celestial pack -> Earth (FH L2 65x6). Skipped Small (Meteor tag, free Mega Celestial -> Jupiter, Venus; Flush L2 50x6, Trips L2 50x5). Big 1500: High-card cycle 75, Straight KQJT9 offered 556 but needed 1425 so I drew; used 3-card discard (cut Banner to +30), cycled again, 557 total. Lost.

## Post-mortem

Binding constraint: no real scorer by ante 2. The whole run was Banner (+chips only, rental, perishes) on base Two Pair L1; typical hand ~330 vs Big 1500 / Small 1000 (ratio 0.16 at the ante-2 shop). No xMult, no +mult joker ever appeared in 3 shops (0 joker slots usable: shops showed Blueprint{E,R}, Banner{P,R}, Splash, Hallucination, Satellite; one Buffoon pack passed).

Decisions I would change:
1. Ante 1 shop: I took Banner $1 over the $4 Buffoon pack. Banner got me through ante 1 but its rent ($3/round) ate every payout, so at ante 2 I had $7 with the same weak build and could not afford a Buffoon pack plus reroll. A Buffoon pack at $4 (SIM value equal) would have sampled 2-3 permanent jokers. If you own 0 jokers at ante 1 and have exactly $4 for the Buffoon pack, buy the pack unless a flat +mult joker is offered.
2. Ante 2 Big Blind: I spent the 3-card discard on a flush draw, which cut Banner from +60 to +30 chips and the Straight's value. With Banner, discards are score: playing High Card with fillers to cycle (keeps both discards) was solver-best and worked once.
3. Celestial picks: I levelled Earth/Jupiter/Venus (non-main hands). They do not rescue a 1500 Big; a Standard-type tag or Buffoon would have been better than 3 off-hand planets. (Skipping the ante-2 Small for Meteor was reasonable: Small pays $0.)

Reusable rules (if-then):
- IF you have 0 scoring jokers at ante 1 AND the shop offers a Buffoon pack for all your money AND the only joker is a perishable rental chips joker, THEN buy the Buffoon pack.
- IF you own Banner, THEN never spend discards before the last hand; cycle junk through High Card plays instead (each discard left = +30 chips, +60 on every hand).
- IF a Pillar boss is next, THEN play pair/high-card with fewest cards in Small/Big; at the boss debuffed cards still form the straight/pair type but score 0, so a Straight with 3 debuffed cards still did 464 here (est was right).
- IF the ante-2 SCORE CHECK ratio is < 0.2 with 0 jokers, THEN the run is almost certainly lost; the only out is a Buffoon pack/reroll for any scorer before the Small.

Advisor/CLI defects:
- `shopadvise` Celestial-pack advice "take Uranus" and SIM ranking prefers off-hand planets (Pluto/Earth) in EMERGENCY; their score ratio gain (0.47 vs 0.39) is not a real clear-chance gain (P(clear) stays ~0.1).
- On a first shop the advisor SIM scored Banner +0.18 and Buffoon pack +0.19 as equal but ignored that Banner's rent (-$3/round x 5) empties the following shop.
- On `start` the port was mid-run on another seed (stale UQPYJH7B, left in SELECTING_HAND by a parked agent): START_RUN is illegal until GAME_OVER; the swarm launcher should reset ports between agents.
