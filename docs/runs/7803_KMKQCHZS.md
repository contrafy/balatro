# Run KMKQCHZS (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (7451/13500)

Ante 1 (Uncommon/Uncommon/The Goad 600, $4): Small 2P QQ99 116 + Flush 320. Shop $5: Buffoon -> Joker{ETERNAL} (over Arrowhead, dead at Goad). Big: FH JJJ44 624 one-shot. Shop $7: Zany $4. Goad: disc x2, 2P QQJJ 300 + 2P JJ22 204 + Pair 77 144 = 648.
Ante 2 (Investment/Buffoon/The Needle 1000, $8): EMERGENCY 0.19: Buffoon -> Crafty{PERISH} (over Ride the Bus{E}). Small 1000: Flush diamonds 1144. Shop $6: Spectral -> Talisman (gold seal 7S). Skipped Big for Buffoon tag (Mega: holo Bull{E} + Hallucination{P}; Big projected 0.8x). Needle: disc 4 keeping 4 clubs, drew Straight 9-5 1242/1000.
Ante 3 (Polychrome/Polychrome/The Arm 6400, $11): Sly $3, Spectral -> Sigil (hand -> spades). Small: 2P AA44 1728 + 2P KK33 1664. Shop $5: left (SIM noise). Big 4800: 2P QQ44 1728, disc 4 -> Straight Flush 8-4 spades 4840. Shop $11: sold Hallucination, Hologram $7, Jumbo Standard $6 -> gold+blue-seal JS (Hologram x1.25), $0. Arm: Flush 3240 + disc + Flush 3487 = 6727 (L1 Flush immune to the Arm). Crafty perished.
Ante 4 (Holo/Foil/The Tooth 18000, $6): EMERGENCY 0.14: sold Crafty, Jumbo Buffoon -> Acrobat{ETERNAL,RENTAL} (exception: check < 0.5, SIM +0.18) over Smiley{E}. $2, rent-broke: skipped Small (Holo tag). Big 13500: High dig 375, disc 4, disc 4, High dig 356 keeping JJ99 for a FH on the Acrobat x3 hand (solver p 0.49); missed, 2P JJ99 6720 -> 7451/13500. GAME OVER.

## Post-mortem

Binding constraint: SCALING + MONEY. No multiplier until Hologram (x1.25) at the end of ante 3 and Acrobat (x3 final hand
only) at ante 4. The build was flat (Joker{E} +4, holo Bull{E} +10 mult, Zany +12 on trips, Sly +50) on L1 hands, making
~2000 a hand at ante 3-4 against 13500-18000 rounds. Money never exceeded $13: every shop from ante 2 on was EMERGENCY and
spent to $0-4, so Bull (+2 chips per $) was nearly blank and no shop could afford a reroll + an xMult. Every blind through
ante 3 was cleared by drawn Flush/Straight/Straight Flush hands (Sigil turned 8 cards into spades), not by the engine.

Decisions I would change:
1. Ante 2 shop 2 ($6) and ante 3 shop 1 ($8): two Spectral packs ($8 total) gave Talisman and Sigil. Sigil did carry the
   ante-3 blinds via spade flushes, but $8 kept for a Buffoon pack/xMult would have been the scaling path; Spectral packs
   with no Wraith target are a gamble the Gold policy says to avoid under $15.
2. Ante 4: playing the Big at a projected ~0.74x with a rent-broke wallet. The alternative (skip Big too, fight only The
   Tooth at ~0.55x) was not better; the real mistake was arriving at ante 4 with one x1.25 multiplier.
3. Ante 2 Small: I skipped the Big for the Buffoon tag (got holo Bull{E} + Hallucination). Bull is a money-scaled joker
   on a $0-6 wallet: its holo +10 mult was the only value. Fine as a pick, but it confirmed that flat eternals at ante 2
   do not move the ante-4 needle.

Reusable rules (if-then):
- IF you own Acrobat and the round needs > 3x your best non-final hand, THEN dig with the first two hands (High Card plays
  of 4 junk cards keep the pair core and both discards) and make the final hand the biggest type you can (FH/trips);
  a made Two Pair x3 is only ~6.7k at ante 4 L1, so FH outs decide the round.
- IF The Arm is the boss AND a Flush/Straight is still L1, THEN play those: L1 hands cannot lose a level (Flush 3240 +
  3487 cleared 6400 here).
- IF you own Hologram and a Standard pack is affordable, THEN the +0.25 usually beats keeping the money even with Bull:
  2P went 1760 -> ~1960 after Bull lost 12 chips.
- IF Bull is your scorer, THEN money is score: each $5 spent costs ~10 chips (~8% of a 2P hand at ante 3).
- IF Sigil is offered on a deck without a Flush plan, THEN it still raises flush frequency strongly (3 of 5 ante-3/4 hands
  that cleared were spade flushes/straight flushes).

Advisor/CLI defects:
- Ante 4 Big, hand 2 (Acrobat owned, need 13125 with 2 hands): `advise` printed "rule pick kept: breaking your made Two Pair
  needs +0.10 (the solver leads by +0.40)" and then ADVICE: PLAY TWOPAIR (p 0.09) over the dig at p 0.49. The +0.10 gate
  passed but the rule pick was kept anyway; also the 2P rule pick ignores that Acrobat x3 belongs to the final hand.
- PACE lines ignore Acrobat's x3 on the final hand ("Two Pair 2240 + 1 later x 85% = 4144 < 13125") while the solver
  includes it; the PACE text pushes discards that are not needed.
- Ante 3 last shop: shopadvise suggested selling Crafty{1 round left} for Hologram although Crafty still scored the boss
  (The Arm); Hallucination (no score) was the right sale. Perishables with 1 round left should still count for the
  next (boss) blind.
- Solver p for ante-4 Big at round start (0.97, "low confidence") was far too high: the round depended on a ~45% FH draw.
Bridge issues: none; 72 steps, no rejects.
