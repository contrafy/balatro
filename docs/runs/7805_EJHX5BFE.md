# Run EJHX5BFE (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (31052/37500)

Ante 1 (Uncommon/Economy/The Psychic 600, $4): Small FH JJJTT 360 one-shot. Shop $6: Buffoon -> Raised Fist. Big: Pair 77 + low fillers 528 (J held lowest). Shop $8: kept money (overrode Celestial). Psychic: 2P 8822+4 800.
Ante 2 (Top-up/Top-up/The Goad 2000, $16): EMERGENCY 0.34 -> reroll -> foil Abstract{RENTAL} $1. Skipped Small for Top-up (Devious, Square). Big: 2P QQ77 2376. Jumbo Buffoon -> Scary Face (overrode perishable Dusk). Goad: Pair QQ + debuffed spade fillers 3312 (kept 3C held for Fist).
Ante 3 (Double/Orbital/The Mark 6400, $13): Celestial -> Uranus (no Mercury). Small: Pair KK + 5/6/7 fillers 4752. Shop $9: Hermit buy-use ($9->$12), Celestial -> Mercury (Pair L2). Big: Pair JJ + fillers 6042. Shop $12: Smiley $4 (SIM 0.68->0.92) over Buffoon $4. Mark: 2P TT44+3 4026, Straight 9-5 9198.
Ante 4 (Skip/Orbital(Two Pair)/The Mouth 18000, $12): score check 0.44. Celestial -> Mercury (Pair L3). Small: 2P 8822+5 3990, 2P KKQQ 13674. Shop $7: nothing. Big 13500: disc, disc, solver dig High 9 2660, Straight K-9 17543. Shop $9: sold Devious, Misprint{PERISH,RENTAL} $1. Mouth: locked Pair KK 10738, Pair 33 4536, Pair 77 ~4.4k. $4 after rent.
Ante 5 (Economy/Holo/The Arm 50000, $9): EMERGENCY 0.20. Jumbo Buffoon $6 -> sold Misprint, took Fibonacci. $4 left. Skipped Small (overrode `s`: $0 Small + $4 - $3 rent = a shop that buys nothing) for Economy (+$4). Big 37500: 2 discards (solver p0.15 line), 2P AAQQ+4 12852, Pair KK+fillers 9464, Pair JJ ~8.7k -> 31052/37500. GAME OVER.

## Post-mortem

Binding constraint: SCALING (zero xMult all run) made worse by MONEY. In ~12 shop views (ante 1-5) plus 3 Buffoon packs I
never saw a reliable/growth xMult; the build was all flat: Raised Fist (+2x lowest held rank), foil Abstract{RENTAL}
(+18 mult, +50 chips), Scary + Smiley (faces), Square, Fibonacci, Pair L3. That tops out at ~8-13k per hand (face Two Pair
13.6k, typical Pair 4-9k) vs 12.5k/hand at the ante-5 Big. Money never exceeded $16: Abstract's rent took $3 every round
(~$27 total) and Gold income is ~$5-8/round, so every shop from ante 3 on started at $7-13 with nothing to reroll.

Decisions I would change:
1. Ante 3 Big shop ($12): I bought Smiley ($4, SIM best) and passed the $4 Buffoon pack. Rule 6 (Buffoon before
   anything with <2 xMults) plus the floor exemption allowed both ($4 left). That was one of only 3 Buffoon packs seen.
2. Three Celestial packs ($12) for Pair L1->L3 + Uranus: each level was ~+10-15% on a hand whose mult was already ~50
   from jokers. With a flat build, the same $12 in Buffoon/Jumbo Buffoon packs is 2 xMult lottery tickets (~18% each).
3. Misprint{PERISH,RENTAL} at ante 4: bought for the Mouth, sold one shop later for Fibonacci. Net -$3 for one round
   of +avg 11 mult; the Mouth was cleared with ~2k to spare, so it may have mattered, but it was not a plan.
4. Ante 4 Big had an Orbital tag for Two Pair (+3 levels: L2 -> L5). I played it (B < boss/2 rule). With face Two Pair
   being my best hand (13.6k at L2), Two Pair L5 would have been ~+35-65% on that hand. Not clearly wrong, but at 0 xMult
   a permanent +3 levels is the only big multiplier a tag offers.

Reusable rules (if-then):
- IF you own Raised Fist THEN fillers are your LOWEST cards and under a suit boss your DEBUFFED cards (a debuffed held
  card is still "lowest" and gives Fist nothing); keep the highest cards held. `sel` both variants: Goad QQ+debuffed
  fillers 3312 vs advisor's club fillers 2448; KK+5/6/7 4752 vs plain 3888.
- IF ante 5+ AND (money - rent due) < $5 THEN skip the $0 Small Blind: its shop cannot buy anything, the skip saves a
  rent tick and a risky fight, and the tag pays now (Economy doubled $4 -> $8). `s` still says "do not skip" here.
- IF the build has 0 xMult at ante 3-4 AND a Buffoon pack is on offer THEN buy it before any flat +mult joker or
  Celestial pack, even to $4: a flat joker adds ~20-30%, the pack is the only route to the x2-x3 needed at ante 5.
- IF a flat rental (Abstract) is your biggest scorer THEN plan to sell it by ante 4: at Gold income it consumes ~40% of
  every round's earnings and kept every ante-3/5 shop below the reroll threshold.
- IF The Mouth AND your pairs are weak THEN lock Pair with the best pair available first (KK 10738 here), then play
  2-card pairs keeping the next pair + high cards held for Raised Fist; this cleared 18000 with ~$0 spare discards.

Advisor/CLI defects:
- Pack `advise` after `sell` inside an open Buffoon pack: still printed "jokers 6/6 ... ADVICE: SKIP (joker slots are
  full)" although the slot was now free (5/6). It does not refresh the slot count after a mid-pack sell.
- Goad (spades debuffed) with Raised Fist: ADVICE picked live club fillers (est 2448) over the debuffed spades (3312);
  filler choice should prefer debuffed cards and keep the low live card for Fist only when it is the lowest.
- shopadvise contradicted itself across consecutive calls: SIM "buy Misprint (sell Devious) 0.74->0.85" (SIM disagrees)
  then, right after the buy, "SELL FIRST: b sell 6 Misprint" (flat rental rule) with no change in state.
- Ante 1 shop: "Ranked higher but passed over: Celestial ... no scoring joker on offer, so the money goes to a reroll"
  printed on the same screen as "ADVICE: BUY -> b pack 1 (Celestial)".
- Ante 5 blind select: `s` said "do not skip: the shop after the Small is worth more than a tag" with $4 and $3 rent due;
  the rent-broke Small-skip rule from PLAYBOOK 2a is not applied at ante 5+.
