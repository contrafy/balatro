# Run XGDKMP9F (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 Small Blind 20610/25000

Ante 1 (Uncommon/Boss Tag/The Manacle 600, $4): Small: 2 discards missed, junk dig kept 4 clubs -> Flush 288 (+15) = 303. Shop $5: Buffoon -> Card Sharp (x3 on repeated hand type). Big: Straight 280 + 2P 120 + Straight x3 720. Shop: Supernova{ETERNAL} $5 (+mult per play of the type). Manacle: Pair TT 90, KK 360, 33 240 (Card Sharp x3 on pairs 2 and 3).
Ante 2 (Coupon/Ethereal/The Needle 1000, $5): skipped Small for Coupon (Small pays $0, nothing buyable). Big 1500: Pair AA 192, KK 630, TT 720 (x3 chain, needed all three pairs). Coupon shop: Ice Cream $0 (+100 chips), free Empress/foil 6S. Needle: Pair JJ 1170 one hand.
Ante 3 (Voucher/Boss Tag/The Psychic 6400, $10): Mercury (Pair L2), Judgement -> Crazy Joker. Small: Pair 99 1518 + foil 66 x3 6372. Big: AA 1716 + QQ 6750. Psychic: 44 1620 + JJ+3 fillers 5520.
Ante 4 (Uncommon/Voucher/The Mark 18000, $22): EMERGENCY 0.34; Justice(glass JS), Magician(lucky JC), Empress held, Joker +4 perish $2, Mercury (Pair L3), Grim (+2 enhanced Aces). Skipped Small (Uncommon tag; tag joker was The Idol rental, passed). Big: KK 2310, AA 8346, QQ 8100. Mark: 3 face-downs+2 fillers = Pair 2750 (67% play), foil 66 11466 (x3), AA 9486 = cleared 14216+9486.
Ante 5 (Skip/Boss Tag/The Wheel 50000, $5): shop with $5: Celestial pack -> no Mercury (Uranus). Small 25000: Pair 33 2268, AA (glass+lucky, no lucky proc) 9108, Empress'd 88 9234 = 20610/25000. LOSS (best case ~22k/round vs 25k Small, 37.5k Big, 50k boss).

## Post-mortem

Binding constraint: scaling. The whole engine was Card Sharp (x3 only on 2nd/3rd hand of the same type) + Supernova (+1 mult per play) + Ice Cream (decaying +100 chips) on Pair L3: ~2.5k first hand, ~8-11k for each of the two x3 hands = ~20k/round vs 25k Small at ante 5. Only ONE xMult (conditional) all run, no growth xMult, money never above $22 (Small pays $0, boss $5, no economy joker), and I never saw a Buffoon pack after ante 1 (shops: Standard/Arcana/Celestial/Spectral packs, junk jokers).

Decisions I would change:
1. Ante 3-4 shops: I held $13-22 and bought Wheel of Fortune (nothing), Celestial/Arcana packs, Judgement (Crazy Joker). That money should have gone to rerolls for an xMult (ante 3, $20 with 3 free slots) - the checklist's "no reliable xMult by ante 3 = reroll $15+" was not followed; I trusted the 0.86 SCORE CHECK ratio, which was based on x3-repeat rounds that need three pair hands every round.
2. Ante 4 shop: Idol (free rental, x2 per exact rank+suit card) was passed correctly, but the Uncommon tag only produced it. Skipping the Small for the tag was fine.
3. Ante 5 shop with $5: nothing could be bought. The real mistake was earlier: no economy/interest (never over $25) so there was never cash for the one shop at ante 4-5 that mattered.

Reusable rules (if-then):
- IF you own Card Sharp, THEN round = H1 cheapest pair of the type (registers) + two x3 hands: sequence pairs low -> high -> high, play the weakest pair first and keep the two best for hands 2-3; keep Empress/glass/lucky cards for the x3 hands (an Empress on the x3 pair was worth ~+25%). Per-round total is only ~2.5x one x3 hand, so it caps ~20k at Pair L3.
- IF The Mark (face-down faces) AND 4 face-downs are in hand THEN they always contain a pair of K/Q/J, but you cannot tell which two: playing 3 of the 4 (+2 non-pairing fillers) gives exactly a Pair 67% of the time (4 cards 44%), so use that as the repeat-registering first hand; worked here (Pair 2750).
- IF a Coupon tag is skipped for, THEN the Coupon shop (after the Big) makes jokers, packs (not vouchers) free: take every free joker with a slot and every free pack; Ice Cream (+100 chips) carried ante 2-3.
- IF Supernova is bought early, THEN it grows with every pair played (+1 mult each, x3 through Card Sharp); still not an xMult, do not count it as one.
- IF the Ante-4 SCORE CHECK is under 0.5 and slots are free, THEN reroll every spare dollar for a Buffoon pack/xMult at antes 3-4 rather than buying planets/Arcana (I bought Mercury x3 which added ~10% total).
- IF Grim is offered in a Spectral pack THEN it creates enhanced Aces (mine: mult, lucky, glass); a glass+lucky Ace pair was my best hand (9-11k x3).

Advisor/CLI defects:
- SCORE CHECK at ante 3 (ratio 0.86-0.92, ~5.5k/hand) overstated: Card Sharp's x3 hands need the SAME type again, and "~16k/round" at ante 4-5 was optimistic (real ~20k at best with 3 perfect pairs); ratio 0.20 at ante 5 said EMERGENCY but there were $5 and nothing to buy.
- `advise` printed no SOLVER lines on several hands (ante 2 Big last discard) and only the rule pick with "register for Card Sharp" even when the first play wasted the best pair; I sequenced low-high-high manually.
- `advise` Judgement/Death/Magician pack ranks ignore that Empress/Magician targets are random future draws (enhancing cards in hand this shop just salts the deck).
- Pack `advise` preferred Deja Vu (red seal) 55 vs Grim 25; Grim (+2 enhanced Aces) was much better for a pair engine.
- `hands` est for lucky cards counts none of the +20 (floor), correct, but SCORE CHECK sim does not reflect 1/5 lucky procs either way.
