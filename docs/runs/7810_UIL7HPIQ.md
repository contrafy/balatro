# Run UIL7HPIQ (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind The House (68972/120000)

Ante 1 (Juggle/Economy/The Psychic 600, $4): Small: spade Flush 324. Shop $6: Buffoon -> Ice Cream{RENTAL} (+100 chips, decays 5/hand). Big: Broadway Straight 724. Shop $5: Supernova $5 ($0). Psychic: 2P 375 + Pair 324 (5-card fillers).
Ante 2 (Polychrome/Boss/The Club 2000): Skipped Small (Polychrome tag -> free polychrome Ramen x2 in the next shop). Big 1500: Flush 960 + 2P 560. Club: club Flush (debuffed cards still make the type) 2310 one-shot. Kept $5.
Ante 3 (Coupon/Juggle/The Tooth 6400): Jumbo Buffoon offered only eternal-rental Blueprint/8 Ball/Castle: took Blueprint left of Ramen (copies x2). Skipped Small (Coupon). Coupon shop: free Odd Todd, Jupiter, gold-seal 3C. Big 2P 3840 + Pair 2280. Tooth 6400: 2P 5448 + 1-card High 1164 (-$5). Cash -$3 after rents.
Ante 4 (Uncommon/Buffoon/The Wall 36000): skipped Small+Big (Buffoon tag -> holo Driver's License + holo Fortune Teller; sold Ice Cream). Holo +10 mult edition made a 1-card High Card ~6000. Wall: Straight 23914 + Flush 23802 = cleared in 2 hands.
Ante 5 (Garbage/Economy/The Wheel 50000): skipped Small (Garbage +$13) and Big (Economy doubled to $22). Wheel: 2P 16781 + spade Flush 22589 + blind face-down fill (rank-sorted hand -> face-down card bounded to 3-5) 10k+ = cleared.
Ante 6 (Coupon/Voucher/The House 120000, $27): Spectral -> Deja Vu, Arcana -> Fool -> Jupiter (Flush L3), 2 rerolls -> sold Supernova for Popcorn $1 (+20 mult). Skipped Small+Big. House: whole first hand face-down; 2P 55/33 33809, Pair 55 + 2 face-down 16383, Pair AA 18780 = 68972/120000.

## Post-mortem

Binding constraint: scaling + money. From ante 3 the wallet sat at -$3..+$9 because two rentals (Ice Cream, then Blueprint{E,R} + Fortune Teller{R} + Popcorn{R}) charged $6-9 per round, so I never bought a Celestial/Buffoon pack with intent; every upgrade was a free tag/Coupon item. Final engine: Odd Todd + two holo +10 mult editions + Popcorn +20 mult, times Ramen x1.8 x its Blueprint copy x poly 1.5 (about x5), main hand Flush L3. It made ~18-34k per hand against 40k/hand needed at the ante-6 boss (120k).

Decisions I would change:
1. Ante 3 Blueprint{ETERNAL,RENTAL}: it doubled the Ramen xMult (clearing ante 3-5) but permanently charged $3/round and could not be sold. I never had cash again. Better: take it only if it replaces another rental the same shop (I did not sell Ice Cream until ante 4).
2. Ante 6 shop: spent $11 on 2 rerolls + packs and ended with Popcorn (+60% on a hand, decaying) but nothing multiplicative. Had I kept the Economy $22 for the Voucher/Coupon tags' post-boss shop nothing changes; the real miss was no growing xMult by ante 4 (Constellation was free at ante 5 but I had no planets to feed it; passing was probably right).
3. The House: I played 3 hands with only odd-rank pairs reaching 30k. Odd Todd makes odd ranks worth 3-5x even ranks (Pair 3 = 10.4k vs Pair 8 = 3.5k, same joker line): at an ante with Odd Todd, discard even ranks when choosing pairs.

Reusable rules (if-then):
- IF a skipped Small/Big gives Polychrome/Coupon/Uncommon/Buffoon/Garbage/Economy tags and you are broke (<$5 after rent), THEN skip both: tags pay NOW (Garbage +$1 per unused discard so far, Economy then doubles it: -$2 -> $11 -> $22 in two skips; Buffoon tag = Mega Buffoon pack immediately).
- IF a joker has a holo edition (+10 mult), THEN it is worth more than most flat jokers at ante 4+ once you own two xMults; put it LEFT of the xMults (a holo Fortune Teller/Driver's License turned a 1-card High Card into 6000).
- IF Ramen/xMult is owned and a Blueprint appears, `order` Blueprint directly left of it: it copies the base x2 (the polychrome edition is not copied), roughly doubling the xMult chain.
- IF the hand is rank-sorted and a card is face-down (Wheel/House), THEN its rank is bounded by the neighbours: a face-down between 5H and 3C is rank 3-5. Play the cards that make a hand for every rank in that interval (3C,fd,5H,6H,7C covered straight / pair of 5 / pair of 3 and cleared the Wheel).
- The Tooth: after one big hand, finish with a single 1-card High Card (-$1) when a holo/xMult build makes it worth ~1000+.
- The House (ante 6, 120k) is a plain scale check: first hand all 8 cards face-down; discard them with one discard (Ramen -0.05) or play a made-visible hand with a face-down filler (they were 2-4 rank here).

Advisor/CLI defects:
- `shopadvise` BARRED Blueprint{ETERNAL,RENTAL} by rule although it doubled the run's only xMult; its SIM treats Blueprint as a UTIL with value 0 until the Ramen copy is modelled (rent barred it, -0.64).
- Pack `advise` at the ante-3 Jumbo Buffoon suggested To Do List (weak) over all; none of the options modelled "copy xMult".
- `advise` after the Ouija/Deja Vu pack did not mention that Ouija turns the whole hand one rank (potential Five/Four of a Kind) when Odd Todd is owned; I skipped it uncertain.
- Under The Wheel `advise` suggested a flush-only discard (72% miss-adjusted) when a straight+flush keep had ~87% outs.
- `est` for face-down cards is not provided; the rank-sorted bounds are printed only for the first hand, not recomputed after later draws.
