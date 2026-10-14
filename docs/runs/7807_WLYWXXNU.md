# Run WLYWXXNU (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (31140/37500)

Ante 1 (Juggle/Skip/The Club 600, $4): Small Straight 308. Shop $6: Buffoon pack (passed Ice Cream rental per hard rule) -> Blueprint{E}. Big: Straight 308 + Flush 252. Shop $7: Clever{E} $4. Club: disc, Full House 555/99 932.
Ante 2 (Top-up/Skip/The Flint 2000, $10): shop: Green Joker{E} weak, rerolled ($5) for nothing; Skipped Small for Top-up Tag -> Popcorn + To Do List (free, no stickers); Blueprint left of Popcorn = +40 mult. Big: To Do High Card junk +$4, Two Pair 4956. Shop: Temperance +$11, reroll -> Joker $2. Flint: Trips 1710 + Pair 999.
Ante 3 (Buffoon/Uncommon/The Manacle 6400, $25): Jumbo Buffoon -> Wily. Skipped Small for Buffoon Tag -> foil Smiley Face{E} (sold To Do). Big: Two Pair 5040. Shop $31: sold Popcorn -> polychrome Blue Joker $10; Jumbo Buffoon -> Jolly (sold Joker); Mercury. Manacle: Two Pair 12600 one-shot.
Ante 4 (Coupon/Orbital/The Goad 18000, $23): Skipped Small for Coupon (free shop: Standard -> KC purple seal, Celestial -> Pluto). Big: disc to face two pair, KKJJ 19800 one-shot. Reroll, Death $3 held. Goad: Death on debuffed 4S -> KC (moved 4S left first), Two Pair KKTT 12240 + Pair JJ 4693 + Pair KK 6928 = 23861/18000.
Ante 5 (Voucher/Foil/The Plant 50000, $35): sold Wily -> Mad Joker. 3 rerolls over 2 shops ($15) found no xMult (Baseball Card with no uncommons, The Idol, Juggler, Business Card{E,R}). Small: Full House KKK TT 24180 + High Card 2790. Big 37500: Two Pair AAQQ 16560, dig (no FH), Two Pair KK55 14160 = 31140. LOSS by 6360.

## Post-mortem

Binding constraint: scaling. Final build was all flat chips/+mult (Jolly, Clever, Mad, Smiley, Blueprint copy) plus one polychrome x1.5 (Blue Joker): ~14-24k per hand vs 37.5k Big, with zero reliable/growth xMult and Pair/Two Pair still L1-L2. SCORE CHECK said EMERGENCY (0.27-0.38) at both ante-5 shops and I could not fix it with $22-35.

Decisions I would change:
1. Ante 4: I bought nothing with $23-33 over 3 shops (SIM said "nothing helps", Vampire had no enhanced cards) and sat on $25 at the Goad. At ante 4 the SCORE CHECK next-ante ratio was 0.56; I should have spent on Arcana/Mega packs (Justice/Chariot/Hermit) or Buffoon packs earlier. Money did not score; I ended the run with $22.
2. Main hand levels: Two Pair never got a Uranus (4 Celestial packs seen, none had it; I skipped two ante-5 Celestial packs for $4 each). A Full House/Two Pair at L4+ would have been +30% - exactly the 17% I lacked on the Big.
3. Ante 5 Big last hand: after the high-card dig (p 0.50 vs 0.46 Two Pair now) no FH came. It was a coin flip I could not avoid, but the ante-5 Big needed ~1.2x my typical 3-hand round, i.e. I entered it at TIGHT 0.94x and no shop could add a multiplier.
4. Ante 2/3 Top-up and Buffoon tag skips worked great (Popcorn+Blueprint = +40 mult at ante 2, Smiley at ante 3).

Reusable rules (if-then):
- IF you own Blueprint and have a +mult joker (Popcorn +20) at ante 2, THEN put Blueprint directly left of it: +40 mult cleared a 1500 Big and the Flint without a rental.
- IF Top-up Tag or Buffoon Tag is offered at ante 2-3 with a free slot (or a sellable To Do List/Joker +4), THEN skip the $0 Small: the tag jokers carried the next 2 antes.
- IF Death is used, THEN move the junk card to a LOWER hand position than the card to copy (the right card is the source); the advisor's `use 1 7 2` had the direction reversed (it would have turned KC into 4S).
- IF a Celestial pack/shop offers the planet of your main hand at ante 3-4 with $20+, THEN buy it: flat builds need levels because no xMult appeared in 12 shop views; do not hold $25 for interest.
- IF only one xMult (polychrome) at ante 4, THEN buy Mega Arcana/Buffoon packs at every shop at ante 4 (money floor irrelevant): Blue Joker polychrome was the only x1.5 and it still needed another.
- To Do List: playing the listed hand with 1 junk card gives +$4, worth it when the hand still clears.
- Blue Joker counts cards left in the DRAW pile (+2 each), so its chips shrink during a round: est drops 14640 -> 14160 after draws.

Advisor/CLI defects:
- Advise `use 1 7 2` for Death had the direction reversed (4S at idx 7, KC at idx 2: the RIGHT card is the source, so the copy would have gone the wrong way); I moved the card and used `use 1 1 3` (CLI printed the correct direction text).
- shopadvise EMERGENCY at ante 5 had no buy to offer (every SIM option within noise), so the "buy the cheapest multiplier" advice is not actionable; a reroll-vs-pack ranking would help.
- shopadvise ORDER FIRST flipped Blueprint between Smiley and Clever repeatedly (est differences 3-8%); with The Plant ahead it should account for the debuffed face jokers.
- Initial ante-1 shopadvise "BUY Ice Cream rental" (SIM +0.29) conflicts with the new hard rule; I followed the rule and the Buffoon pack gave Blueprint.
