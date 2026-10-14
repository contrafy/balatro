# Run HREAJTJ2 (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 boss The Arm (31234/120000)

Ante 1 (Rare/Polychrome/The Window 600, $4): Small: disc for spade draw -> Straight 280 + Two Pair 92 = 372/300. Shop $5: Shoot the Moon $5 (+13 mult per held Queen; only scorer offered). Big: A-5 straight 220 + Two Pair 88 44 660 (QH held). Window: High Card A 432 (2 Queens held) + Two Pair JJ66 1456.
Ante 2 (Holo/D6/The Hook 2000, $12): EMERGENCY 0.21 -> holo Midas Mask $10 (+10 mult). Skipped Small (Holo tag, $2 broke). Big: Two Pair AAJJ 1550/1500 (est). Shop: free holo Faceless Joker + Even Steven $4. Hook: Pair 99 616 (Hook discarded held QS: est 980 -> 616), Straight 7-J 2368.
Ante 3 (Coupon/Top-up/The Head 6400, $10): Abstract $4, Scary Face $4 (+30 chips/face; chips are the multiplicand under flat +mult), Jumbo Celestial -> Uranus (Two Pair L2). Small: Pair TT 1350 + Two Pair KK44 2160. Big: High Card K 2340 + Four Tens 7400. Head: Two Pair KK55 3485 + Straight 3906. 0 xMult, flat build ~5k/hand.
Ante 4 (Holo/Juggle/The Wheel 18000, $16): EMERGENCY 0.31. Jumbo Buffoon -> sold Even Steven for Mr. Bones{PERISHABLE}; Jumbo Arcana -> Hierophant (bonus AS 8D), Arcana -> Wheel of Fortune (nothing). Small: Straight 7-J 5720 + Two Pair 9988 3996. Big: Pair KK 4770 + Straight 8-Q (bonus 8D) 7014 + Two Pair 2870 = 14.6k/13.5k. Shop: Throwback $6 (sold Shoot the Moon; Bones kept), Celestial -> Mercury. Wheel: Trips QQQ 7687 + Two Pair KKJJ 10250 + Two Pair 3177 = 21114/18000 (first hands were 63 short; last hand any).
Ante 5 (Juggle/Buffoon/The Mouth 50000, $8): Uranus (Two Pair L3), Emperor -> Strength + Devil. Skipped Small (Juggle) and Big (Buffoon tag: Stencil/Wrathful/Sly/Splash, skipped pack) -> Throwback x1.75. Mouth: Strength made TT -> JJ, FH JJJ99 13083 + FH KK888 12789 + FH QQ444 9702 = 35.6k/50000; Mr. Bones saved it (>=12.5k).
Ante 6 (Coupon/Juggle/The Arm 120000, $4): shop had nothing (Riff-raff rental, Chariot). Skipped Small and Big (Throwback x2.25). Arm: FH JJJ99 15619 + Two Pair QQTT 11970 + High Card K 3645 = 31234/120000. LOSS.

## Post-mortem

Binding constraint: scaling. The whole run was flat +mult/+chips (Midas holo +10, Faceless holo +10, Abstract +18, Scary Face +30/face) with NO xMult until Throwback at ante 4 (x1.25..x2.25 only from skips). Hand sizes ~5k at ante 3 to ~15k at ante 6 vs 18000/50000/120000 bosses. Ante 6 needs ~100k/hand; this build topped out at 15k. Money stayed $0-$16 all run (no economy joker; every shop was an emergency spend), so no second xMult was ever affordable. Shops over 6 antes showed exactly one xMult-ish offer (Throwback at ante 4; The Idol perishable at ante 3/5 which I passed).

Decisions I would change:
1. Ante 3 shop: passed The Idol{PERISHABLE} $6 (x2 per card of the shown rank+suit) and Celestial; neither would have changed the outcome, but an xMult shown at ante 3 was the only one before Throwback. A perishable conditional xMult is worth a try when the build has 0 xMult.
2. Ante 4 shop 1: sold Even Steven for Mr. Bones instead of Loyalty Card (x4 on every 6th hand). Bones did save the ante-5 boss (Mouth, 35.6k of 50k) and bought one extra ante, so it was right for depth, but it did not help win.
3. Ante 4: spent $15 on 3 packs (Hierophant bonus cards, Wheel nothing, Mercury) with no xMult found; interest was $0 afterwards. Hierophant bonus (+30 chips) on a flat-mult build is real (+1.2k per scoring bonus card) but it was only 2 cards of 52.

Reusable rules (if-then):
- IF your build is flat +mult (50+ mult from holo jokers/Abstract) and chips are small, THEN +chips sources are the real multiplier: Scary Face (+30 chips per scoring face) made a face Two Pair/Full House (4-5 faces) worth 10-15k at ante 4-6; Strength on a pair of Tens (T->J) added ~5k by turning them into faces.
- IF Shoot the Moon (+13 per Queen HELD) is the first joker, THEN keep Queens in hand and play non-Queen High Cards/pairs: High Card with 2 Queens held = 432 at ante 1 (Pair est 56). Do not play the Queen. The Hook discards held cards before scoring, so its est is 40% optimistic there.
- IF an ante-4+ hand is face-heavy, THEN playing Straight/Two Pair/Full House with 3-5 face cards scores 2-3x a High Card; hunt face cards with discards (Faceless Joker pays $5 when 3+ faces are discarded).
- IF The Mouth is the boss and you hold a Full House shape, THEN lock Full House: KK888 and JJJ99 and QQ444 appeared on 3 consecutive hands from an 11-card hand (Juggle tag +3 hand size).
- IF Mr. Bones is owned and the boss needs 4x your hand, THEN skip Small and Big (Throwback +0.25 each, tags pay) and reach 25% of the boss: it passed a 50000 boss with 35.6k. Perish ticks only on played rounds, so skipping does not burn it.
- IF Throwback is owned but your hand is < 0.3x the boss, THEN skipping still helps depth (no fights lost), but it cannot win: x2.25 on 15k is nowhere near 120k. Win requires a second and third xMult by ante 4.

Advisor/CLI defects:
- shopadvise sold Mr. Bones in its Throwback recommendation (SIM does not value Bones' blind-save); I kept Bones and sold Shoot the Moon instead, which later saved ante 5.
- `est` for The Hook is 40% high because held Queens get discarded before scoring (est 980 vs actual 616).
- `advise` at the Mouth planned a Two Pair lock (est 7203) while a Full House JJJ99 (13083) and later two more Full Houses were on hand; it only saw the face Two Pair after Strength was used. No consumable-aware estimate (Strength T->J) before use.
- shopadvise RANKED The Chariot (30) at ante 6 $3 although steel is negligible on a flat build; and did not offer Loyalty Card (x4 every 6 hands) ranked above Bones in the Buffoon pack (it was ranked below Cloud 9).
- Wheel of Fortune pack pick gave no feedback on whether it failed ("Nope!"); the state line just shows no edition.
