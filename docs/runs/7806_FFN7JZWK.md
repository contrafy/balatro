# Run FFN7JZWK (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Fish (47890/50000)

Ante 1 (Polychrome/D6/The Hook 600, $4): Small: 2 discards, dig, diamond Flush 308. Shop $5: Buffoon -> Throwback{E} (over Madness{E}). Big: 2P 88 + club Flush 276 + heart Flush. Shop $5: Photograph $5. Hook: Pair AA + fillers 64, disc 4, heart Flush KH.. 656.
Ante 2 (Handy/D6/The Head 2000, $6): Swashbuckler{E} $4. Skipped Small (Handy +$7, Throwback x1.25). Big 1500: diamond Flush 1056 + Pair JJ 337 + Pair 99. Shop $14: Onyx Agate $7 (SIM 0.61 vs 0.00), Uranus. Head: 2P QQ88 1330, disc 4 to club Flush 6337.
Ante 3 (Standard/Meteor/The House 6400, $10): passed Earth (SIM +0.09). Skipped Small (Standard tag: KC lucky, TC gold; Throwback x1.5). Big: club Flush 6264 one-shot. Shop $18: Mega Arcana -> Temperance (+$10), Empress (QC 8C mult); Half Joker{PERISH} $5. House: 2 discards, 2P QQJJ 1920, club Flush 6570.
Ante 4 (Uncommon/Ethereal/The Goad 18000, $24): Obelisk{E} $8 (only xMult; SIM 0.15 vs 0.07), Arcana -> WoF (miss). Skipped Small (Uncommon tag; Throwback x1.75). Big 13500: disc, Straight A-T 6123, disc 4 into club Flush 16502 (est 10762, lucky KC). Shop $19: Uncommon tag = Arrowhead{E} (passed twice: spades, Goad), Celestial -> Mercury (no Jupiter), Arcana -> Hermit ($11->$22), 1 reroll, Justice $3. Goad: Justice -> glass KC, 2P AAKK 10504, disc 4 debuffed, 2P QQ77 6164 (moved 7C before QH), Pair 44 4065.
Ante 5 (Holo/Ethereal/The Fish 50000, $21): Buffoon $4 (Wily{E}/Shortcut{E}, skipped), Celestial -> Uranus (2P L3). Skipped Small (Holo) AND Big (Ethereal -> Cryptid on KC; Throwback x2.25). Fish: disc 5 (solver), 2P QQ44 15681, disc the 5 face-down cards -> junk, 2P 7766 6965, last hand blind AC AD KC KD (picked via rank+suit sort inference) 25244 -> 47890/50000. GAME OVER.

## Post-mortem

Binding constraint: CHIPS (scaling), lost by 2110. By ante 5 the mult side was big (Swashbuckler +14, Onyx +7/club,
Photograph, Throwback x2.25, Obelisk x2.2, i.e. ~x300 effective mult) but every hand was ~90-110 chips (2P L3 60 +
card chips; no chip joker at all). Each +50 chips was worth ~+50% score.

Decisions I would change:
1. Ante 4 Big shop: I passed Arrowhead{ETERNAL} ($0 from the Uncommon tag, +50 chips per Spade) twice as "off-suit,
   Goad debuffs spades, eternal". The SIM preferred it (ratio 0.75 vs 0.66). At the Fish, 2P 7S7D6S6H would have
   scored ~15k instead of 6965 and the final AAKK the same: that alone wins the blind. Flat chips were my missing axis.
2. Ante 5 Buffoon pack ($4, eternal junk) was the SIM's 0.52 pick; it bought nothing.
3. Skipping both ante-5 blinds into The Fish (draws face down after each play) was defensible (both blinds were coin
   flips at x1.75) but it removed two shops; with a chip joker from those shops the boss is easy.

Reusable rules (if-then):
- IF your hands are ~100 chips while effective mult is x200+ (several +mult jokers and 2 xMults), THEN any +chips joker
  (Arrowhead, Stuntman, Scary/Sly/Clever, Hiker, Bull) is worth +30-60% per hand: buy it over another +mult/level.
  Do not reject a free chips joker for suit mismatch: Arrowhead fires on any scoring Spade in pairs/two pairs.
- IF you own Obelisk and Flush is your most played type, THEN Flush plays reset it to x1: play pair-family hands
  (Two Pair/Pair/Straight) and level Uranus/Mercury; a Flush is only the emergency hand.
- IF you own Onyx Agate (per-club +mult) and Photograph/Glass, THEN order the hand so clubs score BEFORE the first face
  and the Glass card is scored LAST: x2 effects then multiply the accumulated +7s (2P QQ77 4895 -> 6164 by moving 7C).
  Justice on your best club face card turned 2P AAKK into 10504 (from ~7700).
- IF The Fish/The House leaves face-down cards in hand, THEN `sort rank` and `sort suit` once each: positions relative
  to your face-up cards pin rank range and suit (here it found AC AD KC KD blind, 25244). Discards draw face-up under
  The Fish; only post-play draws are face-down.
- IF you own Throwback, THEN skipping the ante-2/3/4 Smalls for paying tags (Handy $7, Standard, Uncommon) was fine
  (+x0.25 each, never lost a Big afterward); it reached x2.25 by the ante-5 boss.
- IF a Standard tag pack shows enhanced clubs while you own Onyx Agate, THEN take the face/lucky club first.

Advisor/CLI defects:
- shopadvise BUILD/planet labels: "Uranus/Mercury: NOT your main hand Flush; mostly wasted" while I owned Obelisk, which
  resets on the most-played Flush; Two Pair was the scorer every round from ante 4 on. Main-hand logic should account
  for Obelisk making the max type the worst hand.
- SIM rated a Buffoon pack p_next 0.52 vs 0.05 (ante 5) with 6/6 slots and no xMult guaranteed; contents were 2 eternal
  commons. Pack SIM seems to assume a strong pick.
- Pack advise SIM suggested selling Half Joker for Wily{ETERNAL} (trips-only).
- est low on flushes with a Lucky card / clubs: club Flush est 10762, actual 16502.
- advise under The Fish/House only says "discard the face-down cards"; it could use rank/suit sort positions.
- `s` at ante 5 says "do not skip" with Throwback owned (known).
- First `shopadvise` right after a pack pick returned "only works in the shop" (state still settling); retry worked.
Bridge issues: none; 104 steps, no rejects.
