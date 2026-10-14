# Run ZSI1CNNI (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 boss The Plant (56640/120000)

Ante 1 (Rare/Economy/The Pillar 600, $4): Small: Trips 666 144 + 2P JJTT 120 + Pair KK (264+60). Shop $4: Buffoon pack -> Red Card{E} (+3 mult per pack skipped; over Reserved Parking{P}). Big 450: disc to keep KH QC 7C dig -> Straight A-high 324 + Flush D 292. Shop $5: Even Steven{P} $4 (+4 mult per even scoring card). Pillar 600: 2 discards, High TD 75, then dug Spade Flush 552 (4 cards kept, 5th spade came) = cleared, lucky.
Ante 2 (Buffoon/Standard/The Water 2000, $7): Celestial pack bought only to SKIP (Red Card 3 -> 6). Skipped Small for Buffoon tag: Mega Buffoon -> Rough Gem{E} ($1/diamond), skipped 2nd pick (Red Card 9). Big 1500: Flush H 1242 + Pair 99 224 + Trips TTT. Shop: Blue Joker{P,R} $1 (+2 chips per card left in deck ~ +90 chips), Standard pack skipped (Red Card 9). Water 2000 (0 discards): Pair 22 1938 + Pair 66 1900.
Ante 3 (Handy/Investment/The Hook 6400, $9): Ramen{R} $1 (x2, my first xMult). Skipped Small for Handy tag +$12 ($8 -> $20). Big 4800: Quads 9999 5888 one-shot. Shop: Blueprint{R} $1 left of Ramen = second x2 (x3.9). Standard pack skipped (Red Card 12). Hook: Two Pair JJ88 12672 one-shot.
Ante 4 (Standard/Skip/The Psychic 18000, $12): Even Steven perished, sold. 2 packs skipped (Red Card 18). Skipped Small (Standard tag -> free Mega Standard, TD red seal, skipped 2nd: Red Card 21). Big 13500: Pair 33 9557 + Pair 99 10279. Shop $12: Buffoon -> Gros Michel (+15 mult, over Odd Todd{E}). Psychic: Trips 888 + 2 fillers 22016 one-shot. Blue Joker perished -> sold. $8 -> $0 after $9/round rent.
Ante 5 (Uncommon/Coupon/The Manacle 50000, $8): without Blue Joker best hand ~9k. Bought Seltzer{R} $1 (retrigger all cards) and a Celestial pack (skipped, Red Card 24). Skipped Small (Uncommon) and Big (Coupon) = no rent, $3 cash. Manacle (7 cards): Flush S 18374, Two Pair AA33 ~18215 actual, disc 2 for straight draw -> Two Pair JJTT 22396 = cleared (money -$1 after rent).
Ante 6 (Boss/Investment/The Fish->Plant 120000, $4): Coupon shop: free Celestial -> Uranus (Two Pair L2), free Arcana -> The Fool copying Uranus (Two Pair L3, 60x4). Skipped Small (Boss Tag rerolled Fish -> Plant) and Big (Investment). Plant 120000: Two Pair 9955 19161 + Straight 14415 + Two Pair AATT 23064 = 56640. Lost.

## Post-mortem

Binding constraint: scaling. Final build = Red Card (+24 mult from 8 skipped packs) + Gros Michel (+15) + Ramen x1.96 + Blueprint(Ramen) x1.96 + Seltzer, Two Pair L3 only. ~19-23k per hand vs 120k boss (ratio 0.2). The run was carried to ante 5 by Blue Joker (+90 chips on a ~40 chip base turned every hand into ~9-10k), and when it perished (ante 4 boss) per-hand score dropped from ~16-22k to ~9k and I never replaced chips. Money was the second constraint: three rentals = -$9/round kept me at $0-8 from ante 3 on, so I could not afford shop jokers/packs (Buffoon packs were the only joker source and one showed up per ante at best).

Decisions I would change:
1. Ante 2 Mega Buffoon (Hologram/Lusty rentals, To the Moon, Rough Gem): I took Rough Gem{ETERNAL}; it paid ~$1-4 per round but occupied a slot forever and never carried score. A flat scorer was not offered, so fine, but it shows eternal econ jokers are a dead slot by ante 5.
2. Ante 3: Blueprint + Ramen + Blue were all rentals ($9/round): at ante 4-5 cash was always <$10. I should have sold Blue Joker's slot earlier for a permanent chips/mult joker and sold Seltzer after ante 5. Mid-run I skipped Small+Big at ante 5 and 6 purely to avoid rent and the tags brought nothing on the boss (Uncommon tag found no uncommon joker slot: all 6 slots full).
3. Slots full at 6 with an eternal Red Card and eternal Rough Gem blocked every Uncommon/Rare tag payout and left no room for the Buffoon pack jokers (Odd Todd eternal was refused). Two eternals = real cost.
4. Red Card pack-skipping was my main +mult source: +3 mult per skip is ~+7% per $4 at mult ~40, much weaker than a planet at chips ~60 (Uranus gave ~+17%); buy planets/Fool-copies before pack skips once packs are not free.

Reusable rules (if-then):
- IF you hold Blue Joker (+2 chips per deck card) at ante 2-4, THEN every hand (even High Card) is worth ~9k; play 2-card hands (drawing fewer cards keeps the deck count) and expect the perish at 5 rounds: plan the replacement chips source BEFORE round 5 (it perishes right before the ante-4/5 boss in this seed).
- IF Blueprint is offered next to a Ramen/xMult you own, THEN buy it (rental $1) and `move jokers` it directly left of the xMult: x2 -> x3.9 for $1; rent $3/round is cheap compared with the multiplier.
- IF Red Card (+3 per pack skipped) is owned, THEN tag packs (Buffoon/Standard/Arcana Tag) skipped = free +3 mult each, and picking 1 card then `skippack` on a Mega pack still counts as a skip (verified 3 -> 6 after a Mega Buffoon pick + skip).
- IF you own rentals and sit at $0-8 at ante 5+, THEN skip Small and Big (each skip avoids a -$9 rent tick) and play only the boss; tags (Uncommon/Coupon) pay only in the post-boss shop and need a free slot.
- IF Coupon tag is active, THEN open the free Arcana pack and pick The Fool when you just used a Planet (it copies the last Planet/Tarot used): free extra hand level.
- IF a boss hits with est ~ 0.2x need (solver says UNWINNABLE), THEN nothing in-round helps: the fix is the shop two antes earlier (a growing xMult / more chips), not a better line.
- Money can go negative from rent (-$1 observed) without losing the run; interest/payout restores it.
- Rule of thumb observed: `est` equals the actual score (23064 est vs the difference of 23064), except when Seltzer retriggers (AA33 est 12215 gave 18215, ~1.5x on that hand only).

Advisor/CLI defects:
- shopadvise at ante 5 said LEAVE and "no option raises P(clear) by more than 0.02" while Seltzer was ranked best by SIM (0.79 vs 0.61): the hard 'second rental before ante 6' rule vetoed the best option even though I already owned two xMult-supporting rentals.
- At ante 5 blind select `s` printed "do not skip" for Small even with $3, 3 rentals ($9/round) and no way to use the next shop; the skip saved $9 per blind that I then used.
- Boss Tag on the Small Blind rerolled The Fish into The Plant immediately on skip (good), but `s` did not say that the new boss was visible only after the skip.
- Standard Tag skip opened a Mega Standard pack ("choose 2") and `advise` printed "No pack advice for this pack type"; Red Card skip value is not modelled in pack advice for Standard/Arcana/Celestial packs.
- `hands` est ignores Seltzer's retrigger on some plays (AA33 est 12215 actual 18215) and `shopadvise` SCORE CHECK dropped by ~40% when Blue Joker perished without a warning that its chips were doing 40% of the score.
