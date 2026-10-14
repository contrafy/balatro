# Run QRYGWYX6 (port 7818, claude-haiku-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Small (3200, scored 940 in 3 hands)

Ante 1 (Pillar 600): Small 300 cleared with Flush 328 (disc once). Shop $6: Scary Face{PERISH,RENTAL} $1 + Buffoon pack -> Gluttonous Joker{ETERNAL} (+3 mult/Club). Big 450 cleared with Two Pair 550. Money ended at $-2 after rent, $4 next shop, nothing bought. Pillar cleared with Straight 1370.
Ante 2 (Needle 1000): $8 shop: Jumbo Celestial $6 -> Saturn (Straight L2). Skipped Small (Charm tag: Mega Arcana, took Empress + Hermit, no scoring gain). Big 1500 cleared with Full House 1176 + Straight 1105. Shop $6: Buffoon pack -> Devious Joker (+100 chips per Straight), $2 left. Needle cleared with Flush 1159 (1 hand).
Ante 3 (Arm 6400): $5 after cash; sold Scary Face (rent stop). Shop had no mult or xMult affordable (Earth, Devil, Standard pack, Jumbo Celestial $6). Small 3200: Flush 340 + Pair 120 + Two Pair 480 = 940. LOSS.

## Post-mortem

Binding constraint: no mult scaling by ante 2. The whole build was Gluttonous (+3 mult per Club, eternal) plus Devious (+100 chips on Straight), and a perishable rental (Scary Face) that died in the ante-3 shop. Hands were 300-1100 from the natural hand alone; Small 3200 at ante 3 needed about 3x that. Money was $-2 to $8 for the whole run, so the shops could not buy the one scorer that was needed.

Decisions I would change:
1. Ante 1 shop: I bought Scary Face (rental, $1) with $2 left, which put me at $-2 after the Big blind. That cost the ante-2 shop its only affordable $5 joker. With $4 total at ante 1, a $1 rental is a trap: prefer keeping the $4 for a permanent joker next shop (Space Joker/Onyx pick).
2. Ante 2: I skipped Small (1000) for a Charm tag. The Mega Arcana gave Empress and Hermit (no scoring, $2->$4). Playing Small would have paid $0 but kept the shop visit for a scorer. Skip only with a tag that gives a joker or $ now (Economy/Investment), not Charm.
3. Ante 3 shop: at $4-5 with 2 jokers and no xMult, I had no buy. I should have banked more money at ante 2 instead of the Scary Face rental and the Buffoon pack pick (Devious is straight-gated, not a core scorer).
4. Celestial pick at ante 2: I overrode advisor Venus for Saturn (Straight was the hand that cleared the Pillar). Result was fine for the Needle but Saturn gave no lift for the Small 3200.

Reusable rules (if-then):
- IF money after a rental buy would be < $3 at ante 1-2, THEN do not buy the rental; keep the $4 for the next shop's permanent joker. Rent at -$3/round makes the run unfundable.
- IF you own 1 scorer at ante 2 and shop money is $8, THEN buy the best +mult/xMult you can afford before any Buffoon pack; a chips-only conditional (Devious +100 Straight, Scary Face) does not solve a 3200 blind.
- IF the Small blind gives a Charm/Arcana-only tag and you have <2 scoring jokers, THEN play the Small blind; the tarot pack does not add score in this build.
- IF the ante-3 boss gap is >= 3x your best hand (940 vs 3200) with no xMult in the shop, THEN the run is lost; use the last money on any reroll that could show an xMult (I kept $5 and left, which was wrong: a $5 reroll was the only path to an xMult).
- Empress/Hermit: Empress needs target cards (`pick 2 4 5`); Hermit doubles money only when money is under $20 (use it when $2-8).

Advisor/CLI defects:
- shopadvise at ante 1 ranked Scary Face (rental, perishable) NEEDED NOW with SIM +0.24 while it left $1 and $-3/round rent; the SIM did not charge the rent to the next shop's score. Example: after buying it, money went $1 -> $-2.
- advise at The Pillar boss marked JD DEBUFF in hand from the earlier Small play; the hint "every card you play now is debuffed" is ambiguous (it means cards played earlier this ante, not the current hand). Clarify the text.
- shopadvise at ante 3 said "EMERGENCY: buy the cheapest multiplier" but listed no mult joker affordable; the emergency line should say "no mult in shop: save money for reroll" instead of recommending The Devil (no scoring).
- `pick 2` for The Empress aborted with "needs target hand cards": the advisor did not show that tarot targets are required; the legal list should say `pick 2 <idx...>`.
- Celestial pack advise recommended Venus as "best fallback" while SIM ranked Earth higher; with a Straight as the only boss-clearing hand, the Saturn override was not offered by the advisor at all.
