# Run FVPWB9XC (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Eye (15560/18000)

Ante 1 (Holo/Skip/The Goad 600, $4): Small: 2P 80, disc, Flush D 308 (cleared). Shop $5: only Merry Andy{R}/Jupiter/Hone, took Buffoon pack $4 -> only Vagabond{E} / Bull{E,R}; took Vagabond (free tarots at <=$4). Big 450: 2P TT88 112, High 15, Vagabond gave Chariot -> steel on a spare KD, Flush AS KS QS 7S 3S est 456 (x1.5 held steel) -> cleared 583. Shop $5: Abstract{R} $1 (+3 mult/joker). Goad: diamond Flush 780 one-shot.
Ante 2 (Boss Tag/Economy/The Club 2000, $8): EMERGENCY 0.23. Hologram $7 (unfed) vs Greedy{R} $1: bought Greedy (+3 via Abstract, +3/diamond). Small 1000: FH TTT77 1344 one-shot. Shop $3: Temperance buyuse ($3 -> +$6). Big 1500: Flush 1040 + Trips AAA 945. Shop $5: Sly{P,R} $1 (+50 chips). Club 2000: Pair JJ 1190 + 2P AA44 1700 -> 2890. Money $-5 after rent.
Ante 3 (Skip/Uncommon/The Window 6400, $1): shop: sold Hanged Man, bought Clever{R} + Joker{R} ($1 each, 6/6 slots, Abstract = +18). Skipped Small (Skip Tag +$5, saves $15 rent). Big 4800: 2P KK77 5520 one-shot. Window: used The World to turn debuffed 9D 6D 5D into spades (un-debuffs them), Pair 66 1728 + 2P AA55 4368 + FH 999-22 -> cleared 6400 by ~1500. Money $-19 (rent $15/round).
Ante 4 (Foil/Handy/The Eye 18000, $-14): skipped Small (Foil tag; no money for a shop). Big 13500: FH 6272 + 2P AA77 5580 + 2P QQ66 4368 = 16220. Shop at $-25: free foil Baron (Foil tag) after selling Greedy (SHOP_BUY illegal until a slot was free). Eye: FH 55566 6916 (KH held x1.5) + 2P KK44 5472 + Flush (Moon made 5th club) 3172 = 15560/18000. LOSS, $-24.

## Post-mortem

Binding constraint: scaling + money. The whole run was flat +mult/+chips from five $1 rentals (Abstract +3 per joker, Joker, Clever, Sly, Greedy). It reached ~5-6k per hand on Two Pair/FH at ante 3-4 with no xMult until a free foil Baron at the ante-4 boss shop. Rent was $15/round against ~$7-9 income, so money went negative at ante 2 and stayed there: from ante 3 on I could not pay for any shop item (a free item was the only purchase possible). Result: 3 hands x ~5.2k with the Eye's distinct-type rule = 15.5k, 2.4k short.

Decisions I would change:
1. Ante 1 first shop (as in the previous Y1LKY6TW log): the $4 Buffoon pack was two Eternal jokers, one an Eternal rental. A Vagabond{E} slot is a permanent dead slot that only produced Chariot/Hanged Man/World/Moon/Fool/Justice (never held: slots stayed full). Better: keep $5, reroll nothing, skip? Honest alternative was Jupiter/nothing; the pack was the only scorer route though.
2. Ante 2 Small shop: buying Hologram ($7) with no feed would not have helped; but I never fed any growth/xMult plan at all. With $8 the correct hunt was a Buffoon pack, not a second rental. I bought a second AND third AND fourth AND fifth rental (Greedy, Sly, Clever, Joker): each is +$3/round, total -$15/round, ~ -$45/ante. Abstract with 6 jokers (+18) is fine score-wise (Two Pair 4.4-5.6k) but it made money impossible. Fewer rentals + a Celestial for Two Pair would have been poorer now but kept $.
3. Ante 4: I skipped the Small (9000, ~50%) and then had no shop. The Handy tag on the Big (about +$20) was left unused because I played the Big for the Foil-tag Baron. Fine, but I should have kept Kings: Baron x1.5 per held King; I played both Kings in the Two Pair (lost x2.25).

Reusable rules (if-then):
- IF a Gold Abstract Joker is your first scorer, THEN each extra $1 rental joker is +3 mult (+4 for plain Joker) but costs $3/round: stop at 3 rentals unless you can pay; count rent as income -$3 each when planning ante 2+ shops.
- IF the boss debuffs a suit (Window/Club/Goad/Head) AND you hold The World/Moon/Star/Sun, THEN convert the DEBUFFED cards into another suit before playing: it un-debuffs them (verified: The World on 3 debuffed diamonds, Window cleared 6400 with 1.5k to spare).
- IF Vagabond{E} is the pick from a Buffoon pack with $<=4, THEN it makes a tarot each hand only while a consumable slot is free: use or sell the tarots so slots stay open (Chariot on a spare card gave steel x1.5 for the 450 Big at ante 1).
- IF a Chariot steel card is held (not played) on the last hand, THEN est includes x1.5 (Flush 456 vs 323 needed): use consumables BEFORE the final play, then run `sel`.
- IF you owe money (negative), THEN SHOP_BUY is not offered while slots are full even for $0 items; sell a rental first (cost $0 jokers from tags/packs are buyable at negative money).
- IF Baron (x1.5 per King held) is owned, THEN do not play your Kings: hold both (x2.25) and play pairs/trips of other ranks.
- IF the boss is The Eye with a flat build, THEN you need 3 distinct types each ~boss/3: with ~5.2k per best hand the cap is ~15.5k, i.e. ante-4 boss 18000 needs one xMult before ante 4.

Advisor/CLI defects:
- shopadvise at ante 1 (shop 1) ranked a Buffoon pack first (SIM +0.22) with $5 and two sticker-heavy jokers; the pack held Eternal Vagabond and Eternal-rental Bull (same pattern as Y1LKY6TW). Pack value should discount the all-stickered case.
- shopadvise ante 3/4 "SELL FIRST: b sell 3 (Greedy)" kept recommending selling a rental every shop even when Abstract counted it (+3 mult) and the SIM +0.3 said keep; it also listed "Mega Celestial $8" as ranked-higher while money was -$14 (negative money never covered by it).
- shopadvise at $-24 showed Baron $0 foil as BUY 140 but the first `legal` had no SHOP_BUY (slots full); it correctly said "sell first" only because of the rental text. A "slots full, sell X to take free joker" note would be clearer.
- est for the final Eye hand ignores that Kings played vs held changes Baron: it showed Two Pair KK44 5472 but no hold-the-Kings alternative.
- Bridge issues: none.
