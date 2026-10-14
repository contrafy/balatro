# Run UEC3HDUI (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Eye (4392/18000)

Ante 1 (Coupon/Charm/The Manacle 600, $4): Small FH 999KK 348 + 2P 120 (300). Shop $4: Buffoon -> Crazy Joker (+12 mult Straight; Shortcut perish passed). Big: Broadway straight 1296. Shop $6: Gros Michel{PERISH} $5. Manacle: Pair 272 + Pair TT 510.
Ante 2 (Polychrome/Economy/The Hook 2000, $7): Small 2P 850 + Trips 1080. Big 2P 680 + Pair 510 + Flush 1501. Shop $14: reroll -> Scary Face $4 (chips x mult ~17 = big). Hook: Broadway Straight 5301 one-shot.
Ante 3 (Orbital/Skip/The Needle 3200, $13): Jumbo Celestial -> Saturn (Straight L2). Skipped Small (Orbital +3 Two Pair) AND Big (Skip tag +$10) so perishable Gros Michel (1 round left) lived for The Needle: Two Pair JJTT L4 3600 one hand.
Ante 4 (Foil/Holo/The Eye 18000, $25): sold perished Gros, Dusk foil $7 + Photograph{PERISH,RENTAL} $1, 2 Celestials (Uranus Two Pair L5, Jupiter). Small 9000: 2 junk digs then royal diamond Straight Flush 19008 (Dusk retriggers final hand ~x3). Big 13500: 3 digs, A-high Straight final 15680. Shop $4: Buffoon -> Gift Card (junk), $0 left. The Eye 18000: Two Pair KKQQ 3720, then dug for a K-high straight final (15520) for 3 hands/discards, never saw K+8: final High Card 540. LOSS 4392/18000.

## Post-mortem

Binding constraint: no xMult and no money. The whole build was ONE final hand per round (Dusk retriggers every card on the last hand, Photograph x2 retriggered = x4 base mult, Crazy +12 mult, Scary +30 chips/face): a K/A-high straight on the final hand = 15.5k, a Two Pair = 11k, anything else ~5k. That cleared 9000 and 13500 (using hands 1-2 purely as digs) but The Eye forbids repeating a hand type, so the final hand had to be a straight AND hand 1 had to be a different type; I needed ~18000 from 3 distinct types with no xMult, and the straight never came (J T 9 8 7 made J-high = 10.3k final, short).

Decisions I would change:
1. Eye: Two Pair KKQQ first (3720) was right, but with J T 9 8 7 made (J-high straight, final only ~10.3k) I spent both discards and hand 2 digging for K+Q (p~0.19) and missed. No other 3-type line reached 18000, so the real mistake was earlier: arriving at the ante-4 boss with $0 (Photograph rent -$3/round, two Celestial packs, a reroll) and a build that only reaches 18000 with a perfect K/A-high straight final.
2. Ante 4 shop 1 ($25): spent $19 on Dusk (good), Photograph rental, 2 Celestial packs (Uranus L5 useless on the straight engine, Jupiter useless), reroll (nothing). Should have kept ~$10 and bought the straight planet only; leaving with $0 meant the Buffoon pack and Holo-tag shop later bought a Gift Card.
3. I never got a second +mult/xMult: only Crazy, Gros(perished), Photograph(rental). By ante 4 it was one engine (final-hand straight), which The Eye kills.

Reusable rules (if-then):
- IF the build is Dusk/Acrobat final-hand (x3) and the boss is The Eye, THEN you need THREE different types worth the need: only the final hand carries the x3, so a 2-type plan (Two Pair first, then straight last) must still fit with the middle hand being a zero-ish dig; buy a second final-hand-capable type (Flush/Two Pair levels) BEFORE the Eye, and sell/avoid rentals that drain the money the Eye shop needed.
- IF Crazy Joker (+12 mult on Straight) is owned, THEN Straight is the main hand: every +chips joker (Scary Face on face straights K-Q-J) and Straight planet matters; ante 1-2 straights hit 1296/5301 with only Crazy+Gros+Scary: ignore the 'Flush/Straight non-core' text when the first scorer is a straight joker and keep faces in hand.
- IF a perishable (Gros Michel, 1 round left) is the main +mult and the boss is a ONE-hand blind (The Needle), THEN skip Small AND Big (perishables do not tick on skips): worked, cleared the Needle 3600/3200 with Gros alive; skip tags paid +$10.
- IF a final-hand engine (Dusk/Acrobat) owns hands 1-2 as digs, THEN spare cards (play only the non-key ones) and use free discards to dig for the key hand before the last play: 19008 SF and 15680 straight were found that way at ante 4 Small/Big.
- Photograph + Dusk: Dusk retriggers Photograph (x2 twice on base mult) - est shows it (final straight mult 40 vs 26).

Advisor/CLI defects:
- shopadvise main hand label said 'Two Pair/Pair' and SCORE CHECK ~905/hand while my real straight hands were 5301-15680 (est models only the median 3-hand round, not the final-hand x3 digs); EMERGENCY alarms were wrong at ante 2-4 for the Dusk build, but right at ante 4 boss.
- `advise` at The Eye correctly says 3 distinct types needed but never says which type must be the final hand or estimates the final-hand x3 per type; the solver rule pick (disc 3 5 8) had p 0.29 vs 0.43 for the K-dig, and the best-p line was low-confidence n=100/400.
- `play PAIR 6 7 8` gave 'forms High Card' abort when I mis-indexed a spare card: fine (guard worked).
