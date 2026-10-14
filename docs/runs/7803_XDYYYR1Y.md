# Run XDYYYR1Y (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (11071/13500)

Ante 1 (D6/Juggle/The Head 600, $4): Small: Flush 284 + Pair 22. Shop $5: Raised Fist{PERISH} $5 (only scorer; SIM 1.00). Big: 2P 3322 420 + Trips 666. Shop $5: passed Earth (SIM +0.03). Head: 2P QQ66 one-shot.
Ante 2 (Double/Juggle/The House 2000, $13): EMERGENCY 0.34 -> Shoot the Moon $5. Small: Pair 88 910 + Pair TT. Shop $10: Misprint $4 (overrode SIM Merry Andy{ETERNAL} foil $9: -1 hand size forever, $1 left). Big: disc, Pair KK 1080 + Pair 44. Shop $12: Jumbo Celestial -> Mercury (Pair L2). House: disc 5 face-down, Pair AA 736, disc 4, Pair 44 (holding K Q T) cleared. Raised Fist perished.
Ante 3 (Meteor/Polychrome/The Hook 6400, $15): EMERGENCY 0.17; sold perished Fist, reroll $5 -> Supernova{PERISH} $5. Small: Pair 99 1892, disc, Trips JJJ 1980. Shop $7: Jumbo Arcana $6 -> Temperance (+$6). Big: disc, Trips 999 holding QQQ 3819 + Pair QQ. Shop $13: Scary Face{ETERNAL} $4, passed Mega Arcana $8 (kept $9). Hook: disc AA (solver 0.87 vs 0.75), Pair KK holding QQQ 4305 (Misprint low) + Pair TT holding QQ cleared.
Ante 4 (Polychrome/Juggle/The Psychic 18000, $16): EMERGENCY 0.13; reroll $5 -> Mystic Summit{ETERNAL} $5 + Jolly $3 ($3 left, 6/6, 0 xMult). Small 9000: disc 4, disc 2 (Summit on), Pair AA holding QQ 3478 + Pair KK holding QQQ -> cleared. Shop $4: passed Arcana $4. Big 13500: disc 5, disc 4 (no queens came), Pair AA dig 2491, Pair KK holding QS 6195, last deal K Q J T 8 7 5 2 with no pair -> High K 2385. 11071/13500. GAME OVER.

## Post-mortem

Binding constraint: scaling with zero xMult. In 9 shop views plus 2 rerolls no xMult joker of any kind was offered, and
I never had more than $16, so a third reroll was never affordable. The build was flat: Shoot the Moon (+13 per Queen
held), Scary Face (+30 chips per scoring face), Mystic Summit +15, Jolly +8, Misprint, Supernova{PERISH} (+12 at death),
Pair L2. A face pair with 2-3 Queens held made 6-9k, anything else 1-3k, so each round depended on drawing Queens and a
face pair; at ante 4 Big (13500, ~4500 per hand) one deal without a pair lost it.

Decisions I would change:
1. Ante 1 shop 1: Raised Fist{PERISHABLE} $5 over a Buffoon Pack $4. The Fist carried ante 1-2, then died exactly at the
   ante-3 shop, so I paid for a second bridge (Supernova{PERISH}) that died at the ante-4 Big where I lost. Two perishable
   bridges in a row meant I entered ante 4 with no growing scorer. A Buffoon pick that lasts would have been better.
2. Ante 4 shops: I spent $13 of $16 on a reroll + two flat jokers (Summit, Jolly). They were needed to clear the Small
   (est went 2100 -> 4500 per hand), but they filled slot 6 with an Eternal (Summit) and left no money for the Arcana
   or a later xMult. With 2 Eternal flat jokers (Scary, Summit) the build could not have been reshaped anyway.
3. Pair L2 at ante 4 is far behind the curve (playbook: main level >= ante). I passed a Celestial $4 (ante 2) and the
   Mega Arcana $8 (ante 3) to keep $9 for an xMult that never appeared.

Reusable rules (if-then):
- IF you own Shoot the Moon, THEN never play a Queen except as the pair itself; play 2-card pairs (no fillers) so Queens
  stay held, and play the face pair (K/J/A) while 2-3 Queens are held: Pair KK holding QQQ was 8715 est vs ~2000 without.
- IF you own Raised Fist, THEN fillers must be your LOWEST cards so the held cards are high (holding K Q T gave +20 mult;
  the advisor's filler pick held a 3 for +6).
- IF your only scorers at ante 1-3 are perishable, THEN count their death round now: buy a permanent scorer in the shop
  BEFORE the round they die in, not after; Supernova perishing at the ante-4 Big removed ~+12 mult the round I lost.
- IF you own Mystic Summit with 2 discards, THEN spend both discards before the first play (even a 1-2 card discard):
  +15 mult on all 3 hands beat holding a discard for a draw (Small ante 4: 3478 + 8715 after spending both).
- IF The Hook and a held-card joker (Shoot the Moon), THEN play only the 2 pair cards: the Hook discards 2 of 6 held
  cards instead of 2 of 3, protecting the held Queens.

Advisor/CLI defects:
- advise filler choice ignored Raised Fist (ante 2 The House, last 2 hands): rule pick `play PAIR 6 7 5 4` held 3C
  (est 924); playing 3C as a filler instead held K Q T (est 1386, cleared the boss).
- advise rule pick at ante 4 Small discarded 1 + 8 keeping a heart flush draw while AA, QQ and 44 were made and
  Shoot the Moon pays for held Queens; the three made pairs with Summit were ~10k vs 9000 needed.
- SOLVER p looked overconfident on the ante-4 Big: 0.79 (first discard) -> 0.71 -> 0.56 -> 0.74 -> lost with a pairless
  last deal. At ante 1-3 its p >= 0.99 calls were all fine.
- shopadvise SIM rated Merry Andy{ETERNAL} foil $9 (-1 hand size, +3 discards) at p 0.90 vs Misprint 0.74 at ante 2,
  with $1 left; the SIM does not price a permanent eternal -1 hand size slot or the lost interest.
Bridge issues: none; 77 steps, no rejects (one CLI-side NOT LEGAL: I used the old slot index after a buy; nothing sent).
