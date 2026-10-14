# Run JJLWEZDK (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 boss The Arm (42274/50000)

Ante 1 (Holo/Skip/The Club 600, $4): Small: disc to Flush 252 + Pair QQ 60 = 312. Shop $5: Buffoon pack -> Credit Card (or Drunkard) -> bought Supernova{P} $5 on debt (-$4). Big: Flush KQT98C 492 one-shot. Shop (-$4+): reroll (-$3) found nothing. Club: Pair 9s dig 76 + Flush 504 + Pair 85 = 665/600.
Ante 2 (Foil/Double/The Head 2000, $2): EMERGENCY 0.07; reroll on debt -> Stuntman $7 (+250 chips, hand size 6), debt -$10. Skipped Small for Foil Tag (free foil Hallucination in the next shop). Big: Pair KK 1680 one-shot. Head: Pair QQ 2310 one-shot.
Ante 3 (Foil/Investment/The Tooth 6400, $3): Even Steven{ETERNAL} $4 (debt -$1). Skipped Small (Foil) AND Big (Investment $25) so Supernova stayed alive for the boss. Tooth: disc, Pair 88 5216 + High Card TD 1890... = 7106.
Ante 4 (Ethereal/Meteor/The Hook 18000, $27): sold perished Supernova, free foil Gros Michel (+15 mult); 2 rerolls found nothing ($18 left). Skipped Small (Ethereal: Incantation) and Big (Meteor: Venus + Jupiter). Hook: Two Pair KKTT 10250 + Two Pair 5544 9700 = 19950/18000.
Ante 5 (Rare/D6/The Arm 50000, $21): free rental Swashbuckler (+12 mult). Skipped Small (Rare tag) and Big (D6) to fight only The Arm. Justice -> glass 2C. Hands: High TS 11680, High 10136, Trips 2S2H2C 20458 (Arm drops a level) = 42274/50000. DIED with $21, 0 xMult, Rare+D6 tags unused.

## Post-mortem

Binding constraint: scaling at ante 5, 0 xMult all run. Build was Stuntman (+250 chips) + Even Steven (+4/even card) + Gros Michel (+15) + Swashbuckler (+12): every hand scored 10-20k (High Card 11k, even pair 14k, Trips 20k) but ante 5 needed 25k/37.5k/50k per blind. No xMult, Buffoon pack or Rare joker was ever on offer in 6 shops (5 rerolls).

Decisions I would change:
1. Ante 5: I skipped BOTH Small and Big to bank the Rare+D6 tags for a post-boss shop that I never reached. The Rare tag only pays in the shop after the next blind that is PLAYED; skipping Small AND Big makes the boss the next fight with no shop in between, i.e. an 50000 boss at a ~40k round. Playing the 25k Small (1.1x, ~85%) would have given a shop with $21; better still: skip Small, play Big (37.5k, ~45%), then the Rare shop before the boss. Skip-both only pays when the boss is clearable without the tags.
2. Ante 4: skipping Small+Big for Ethereal/Meteor gave Incantation and Venus/Jupiter: all off-hand, ~0 score. The planets offered did not include Mercury. A skip for a pack with 5 random planets only pays if your main hand is likely in it.
3. Last two hands of The Arm: followed the solver's "dig" (High Card 11-10k) over banking Trips 20458 first; both lines died, but the solver's p 0.27 for the dig line was clearly optimistic (the best final hand was Trips 20458 vs 28184 needed). When two hands are left and the max reachable single hand is < need/2, the solver numbers are not trustworthy.

Reusable rules (if-then):
- IF you hold Credit Card at $0-5 in ante 1-2 with a scorer on offer, THEN buy it on debt: debt is just an advance that the next blind payouts repay (Supernova -$4, Stuntman -$10 both fine).
- IF Stuntman (+250 chips) is owned, THEN every hand is ~10x baseline: even a High Card single is 10k at ante 5. Mult is the bottleneck, so buy +mult (Even Steven, Gros Michel, Swashbuckler) not chips; hand size 6 is workable.
- IF Even Steven is owned, THEN an even High Card (1 card) beats an odd Pair; keep even cards for the last hands and play 2-card pairs of evens (+8 mult).
- IF Foil Tag appears at ante 2-4 and you are broke, THEN skip the Small: it gave a free foil joker (Hallucination, Gros Michel +15 mult) in the next shop.
- Glass (Justice) on a card scores x2 on the mult built up by EARLIER scoring cards: put the glass card last in hand order (`move hand`), est models it.
- The Arm: a leveled hand you play loses a level AFTER being scored one level lower (Trips L2 played as L1); unleveled hands are immune.

Advisor/CLI defects:
- SOLVER on the last 2 hands of The Arm: "PLAY HIGH 1 3 dig p 0.27" with need 28184 and best reachable 20458; actual p was ~0. The dig line modelled no real path to 28k.
- shopadvise at ante 2 said REROLL (110 score for Stuntman listed above it) while the Hallucination/Foil shop buys were the real adds; harmless.
- Pack advisor gave Incantation 25 and ADVICE SKIP; Incantation adds enhanced cards but destroys one; ante-4 Small skip for the Ethereal tag was suggested by `s` without noting the pack is ~value 0.
- `s` skip ADVICE at ante 3 / 4 correctly said to skip but did not warn that skipping both the Small and the Big removes every shop before the boss.
