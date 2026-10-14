# Run W9HRFGMW (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Big Blind (13347/13500)

Ante 1: Small=Uncommon Tag (skipped per advice), Big=Foil Tag, Boss=The Pillar.
  Big 450: Flush S 332 + (discarded 4 to dig for a 5) Straight 9-5 260 = 592. Shop $9: free Idol (Uncommon Tag), Buffoon -> Wrathful (perishable; Supernova offered was rental), Even Steven (perishable) $4 -> $1.
  Boss Pillar 600: Pair 4 180, Pair T 300, Two Pair 62 864. Won.
Ante 2 (1000/1500/2000 The House): Odd Todd rental $1. Skipped Small for Negative Tag (-> free negative eternal Business Card). Big 1500: TwoPair 64 960, Pair A 470, FH 2610. House: discarded face-downs twice, TwoPair T5 1456 + TwoPair A2 1728 = 3184/2000.
Ante 3 (3200/4800/6400 The Mark): $9 shop: declined Uranus $3, rerolled $5, sold Wrathful, bought Acrobat $6 (x3 final hand) -> $0. Skipped Small for Rare Tag (-> Baseball Card, perishable+rental). Big 4800: held T9876 straight through 2 junk hands, final Straight x3 Acrobat est 6336, won. The Mark: held FH 88866 while playing the face-down card alone twice, final FH x3 est 12312, won.
Ante 4 (9000/13500/18000 The Manacle): shop $0 (+$2 selling perished Even Steven), nothing bought. Skipped Small for Juggle Tag (+3 hand size; saved $6 rent). Big 13500, every hand still L1: Straight J-7 1224; drew the 4th Ace (Quads A = 3591, x3 final = 10773, so hand 2 needed 1503 without Aces); 2 discards missed the Idol card 5C; played Quads A as hand 2 (3591); final draw gave 5C: Straight 9-5 with Idol x2 + Acrobat x3 + Baseball x2.25 = 8532 (est exact) vs 8685 needed. Lost by 153.

## Post-mortem
Binding constraint: SCALING via money. Every hand type was still Level 1 at the ante-4 Big Blind (13500). Rentals (Odd Todd from ante 2, Baseball from ante 3) cost $3 each per round, and the Small Blinds pay $0. So money sat at $0-2 from ante 3 on and no planet was ever bought. One Saturn (Straight L2, 60x7 instead of 30x4) would have cleared the final hand by about 5000.

Decisions I would change:
1. Ante 3 shop with $9: buy Uranus/Mercury ($3) before the $5 reroll. I rerolled into Acrobat, which was good, but going to $0 meant zero levels for ante 4. A $3 level is permanent; the reroll was a gamble.
2. Odd Todd as a $1 rental at ante 2: it scored well (+31 chips per odd card), but by the loss it had cost $9 in rent plus interest. Selling it at the ante-4 shop would not have helped, because there was nothing to buy.
3. Acrobat round planning: with Acrobat, total = H1 + H2 + 3*H3. Before the first play of a round, pick which made hand will be the final hand and check that the other two hands can cover the rest without the cards it needs. At ante 4 I banked a 1224 straight first. Opening with Full House AAATT (1674) would have scored more, but I could not have known the 4th Ace would come.

Reusable rules (if-then):
- IF you own Acrobat, THEN hold your strongest made hand for the LAST hand of the round. Spend hands 1-2 on junk or small hands, and play a lone face-down card under The Mark/House. This won ante 3 Big and Boss with x3 finals (6336, 12312).
- IF you own Acrobat and the final hand needs 4+ specific cards (Quads), THEN compute need - 3*final before hand 2. If no hand that avoids those cards can cover the gap, play the big hand NOW and use the final draw for a second big hand.
- IF Gold Stake and money is under $10 at ante 3+, THEN a $3 main-hand planet comes before a $5 reroll. Entering ante 4 with all hands at L1 loses even with x6+ multipliers.
- IF a rental joker is offered at ante 1-2, THEN count it as $3 per round for the whole run: buy it only if you will sell it within about 2 rounds or it is your only scorer.
- IF you own The Idol, THEN read `raw` -> `idol_card` every round. Here the Idol card (5C) doubled the final hand from 4266 to 8532.

Advisor/CLI defects:
- `advise` does not model Acrobat sequencing. At The Mark it advised "play TRIPS 888 now est 1822". Holding 888 and drawing into FH 88866 for the x3 final gave 12312.
- `notes: The Idol not modeled` is printed even when est includes the Idol x2: final straight est 8532 = actual 8532 exactly, with 5C scored.
- High Card with 3 junk cards (QH JC TS): est 175 vs actual 15. est seems to score every played card instead of only the highest.
- At ante 1 The Pillar, `advise` proposed a straight chase (EV 258 vs need 600) while Even Steven made even pairs worth 260-300 each. Even pairs + Two Pair 62 (864) cleared it.
- `shopadvise` at ante 2 ($5) advised a perishable straight-only Crazy Joker for $4 that would have left $1.
- At ante 4 with $2, `s` advised playing the Small Blind ("Juggle not worth a shop visit"). With $6 of rental upkeep per round and $0 Small Blind pay, the visit had a negative cash value.
