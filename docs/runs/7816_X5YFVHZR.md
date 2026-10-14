# Run X5YFVHZR (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 1 boss The Pillar (560/600)

Ante 1 (Skip/Holo/The Pillar 600, $4): Small 300: Two Pair 99 88 108, Two Pair 88 77 100, Club Flush 244 (hand 3, solver p 0.88-0.94 throughout). Shop $4: Golden Joker{E,R} $1 passed (eternal rental), Buffoon pack $4 -> Gluttonous Joker (+3 mult per Club) over perishable Scholar; $0 left. Big 450: disc 3 keeping JJ + KC JC TC 3C, drew a Broadway straight; played Two Pair JJ TT (4 cards, est 480) one-shot to keep A/K/Q/straight cards clean for the Pillar; 2 unused hands = $2 (cash $2 + nothing else, so $6 in shop). Shop $6: Erosion $6 (+0 now), Seance{E}, Celestial x2; bought Celestial pack $4 -> Uranus (Two Pair L2); $2 left, no joker. Pillar 600: first deal 3 of 8 cards debuffed (8H 8D 7C from Small/Big), disc 5 (kept KC TH 6S; drew JH 9C 8S debuffed again), Straight T-high 212 (3 debuffed cards scoring 0), Two Pair JJ33 +filler 168 (total 380), disc 4 keeping AD KC QS QD for a two-pair draw (p 0.63), drew QH: Trips QQQ est 180 vs 220 needed -> 560/600. GAME OVER.

## Post-mortem

Binding constraint: scale at ante 1 with ONE joker (Gluttonous, club-only; Pair/TwoPair hands without clubs got +0) and Two Pair L2; Pillar debuffs every card played in the ante (14+ cards by the boss) so effective draws were thin. Missed by 40 chips.

Decisions I would change:
1. Ante 1 Big: I stopped at one Two Pair (480 vs 450) and cashed out with 2 unused hands. That kept the cards cleaner (4 cards played) but the Big was already over; fine. The real leak was Small: hands 1-2 played two Two Pairs (8 cards debuffed later: 99, 88, 77) plus a 5-card club Flush (JC 7C 4C 3C 2C), so ~13 cards from the Small and Big were debuffed at the Pillar. IF the Pillar is the ante-1 boss, THEN at the Small play the minimal made hand each time and take the Flush only when it is the only way to clear; never play a 5-card flush as a "bank" when a 2-card Pair would not matter. The advisor's "fewest cards" note exists but the ante-1 Small needed 300 and I had to play 3 hands anyway.
2. Shop 2 ($6): bought a Celestial pack (Uranus, Two Pair +10 chips +1 mult, ~+20 per hand: invisible) instead of keeping $6 + rerolling nothing. With a Pillar boss and 1.0x pace a +20 gain was worthless; Erosion/Seance were junk. Nothing in the shop could have added the needed ~+40, so mostly luck, but a $4 pack for a level is the weakest possible use of the last ante-1 money. Alternative: Hone voucher ($10) unaffordable; so the marginal call was nothing.
3. Boss final discard: kept AD KC QS QD (two pair draw p 0.63). The made hand at that point was Pair QQ 60. Alternatives needed 220; both ~0.7. Drew QH for Trips 180: 40 short. Pure tail.

Reusable rules (if-then):
- IF the ante-1 boss is The Pillar, THEN count every card you played in Small and Big; at the boss ~1/3 of every deal is debuffed (debuffed cards still make the hand type but score 0). Plan boss hands from the non-debuffed cards only; est already excludes them.
- IF you own a suit-only +mult joker (Gluttonous), THEN hands without that suit get +0 from it: at ante 1 value it on the share of your hands that include clubs (~1 in 3), not on the flush case.
- IF the last hand needs X and your best made hand is Trips (est 180) vs 220, THEN nothing helps: keep a Pair/Two Pair that already contains your highest-chip cards instead of discarding to draw (the final discard turned Pair QQ+K+A into Trips QQQ with no kicker value).

Advisor/CLI defects:
- shopadvise ante 1 second shop: rule advice was `buy Erosion` ("adds ~0 now") while SIM said Celestial pack; the ADVICE followed SIM. Fine. But neither flagged that at $6 with 1 scorer nothing in the shop scored on non-club hands.
- advise at the boss hand 1: est for Straight 212 vs 188 ignored that playing the 5-card 10-high straight puts 3 more cards into debuff state for the rest of the boss round (minor: Pillar debuff applies for later blinds this ante, not within the boss round for the cards played in it, so likely irrelevant).
