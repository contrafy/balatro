# Run R5DXHPXU (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Goad (10076/18000)

Ante 1 (D6/Economy/The Head 600, $4): Small 300: Straight 8-high 240 + Two Pair JT 120. Shop $5: Raised Fist $5 (first scorer, $0 left). Big 450: Two Pair JJ55 + 2D filler 500. Shop $6: Shoot the Moon $5 ($1 left). Head: Trips 999 + fillers 1824 one-shot (QC held).
Ante 2 (Double/Polychrome/The Manacle 2000, $8): shop $8 nothing scoring (Runner{R}, Fortune Teller{P}), left with $8. Small 1000: dug for Straight T-6 1680 one-shot. Big 1500: Two Pair 760 + Two Pair 972. Shop $18: Popcorn{R} $1 (+20 decaying), Celestial -> Venus (Trips L2). Manacle: Pair 99 1092 + Two Pair QQ22 1584.
Ante 3 (Handy/Meteor/The Psychic 6400, $10): EMERGENCY 0.32; 1 reroll nothing, Uranus (Two Pair L2). Small 3200: Two Pair 2178 + Trips AAA 2573. Shop: The Duo{P} $8 (x2 pair, $1 left). Big 4800: Pair QQ 2040 + Two Pair AA77 5016. Judgement $3 -> Chaos the Clown. Psychic: Two Pair KK55 6160 + Pair JJ 2220 (5 cards forced).
Ante 4 (Foil/Standard/The Goad 18000, $0-4): money $0-4 all ante, rent debt, Small pays $0. Sold Popcorn. Arcana -> Justice (Glass AC). Small 9000: dug twice (High 900 x2) then Trips JJJ with QQQ held (STM +39) 10240 = cleared. Buffoon pack -> Jolly{E}. Big 13500: Trips KKK 6080 + Two Pair 7744 6076 + Pair JJ 2400 = 14556 cleared. Goad (spades debuffed): Trips 999 6256 + Two Pair 3220 + Pair 600 = 10076/18000 LOSS (solver p 0.28 -> 0.04 -> 0.00).

## Post-mortem

Binding constraint: scaling and money. Zero xMult for the whole run except a perishable Duo (x2, 5 rounds). Final build Raised Fist + Shoot the Moon + Jolly{E} + Duo{P} + Chaos: ~6k per good hand at ante 4 vs Goad 18000 (needs 6k x 3 perfect hands). Money was $0-4 at every shop from ante 3 on (Small pays $0, rental Popcorn, judgement/packs spent to $0), so no reroll hunts or xMult buys; 4 shops at <$5 saw one xMult (Duo) and one Buffoon pack total.

Decisions I would change:
1. Ante 1 spent both shops to $0-1 on two conditional held-card jokers (Raised Fist, Shoot the Moon). They scored well early (Trips 1824, Straight 1680) but are flat adds that cap ~6k/hand at ante 4. Neither can ever be an xMult plan, and each shop after that arrived with <$5.
2. Ante 2 Big/Manacle shop: $18 spent on Popcorn rental + Celestial (Venus, an off-hand planet) instead of keeping money for interest/rerolls; Popcorn fell to +4 by ante 3 and its rent kept me at $0.
3. Ante 3: Judgement for the last $3 (random joker) gave Chaos the Clown, no scoring value.

Reusable rules (if-then):
- IF you own Shoot the Moon, THEN keep Queens in hand and play a made trips/pair from other ranks: three Queens held = +39 mult. JJJ trips + QQQ held est 10240 vs 4000 with fewer held. `sel` with and without fillers shows it; always fill plays to 5 cards with LOW junk so Raised Fist's lowest held card rises.
- IF Raised Fist is owned, THEN play low fillers (2-5) and hold high cards; est covers it (760 vs 684 on the same Two Pair).
- IF the boss is The Goad (spades debuffed) and your hands are ~6k, THEN it is lost without an xMult: spades count for hand type but score 0, and discards of debuffed spades only help marginally.
- IF a joker pack/shop sells xMult on a perishable timer (Duo, 5 rounds), THEN it covers exactly ante 3 (Big + Psychic) and ante 4 Small/Big; plan the replacement the shop after buying it, not when it perishes.

Advisor/CLI defects:
- shopadvise ranked "Uranus $3 [MAIN SCALING]" 98 ahead of everything at $4 with a Buffoon pack available and an EMERGENCY (0.07) in the same printout; the emergency says buy a multiplier.
- Packs: Buffoon pack with $4 offered Bull and Jolly{E} only; ADVICE chose the eternal Jolly (fine).
- SCORE CHECK said ratio 0.07 vs Goad while the actual round reached 10k (0.55 of boss): pessimistic for held-card jokers (STM/Raised Fist), same as the Acrobat build in 7810_AQJ81BLL.
- "D6 Tag: reroll costs $0" note printed in shops but the reroll was the Chaos free one ($5 afterwards): the banner is misleading when the reroll price is $5.
- advise at Small 9000: rule pick (Trips now) p 0.54 vs solver discard p 0.73 (solver was right: dig + Trips JJJ held QQQ).
Bridge issues: none (87 steps, no rejects).
