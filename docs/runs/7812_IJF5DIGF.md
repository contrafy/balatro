# Run IJF5DIGF (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (53142/60000)

Ante 1 (Economy/Foil/The Pillar 600, $4): Small: 2P QQ88 112 + 2P JJ44 96 + Trips 666 144. Shop $4: Buffoon pack -> Smeared{PERISHABLE} (Hearts=Diamonds, Spades=Clubs: 2-colour flushes, est 300-600 at ante 1). Big: Smeared flush 324 + 296. Shop $5: Walkie Talkie{ETERNAL} $4 (only scorer). Pillar: flush 504 + High TH 125 (Walkie).
Ante 2 (Coupon/Uncommon/The Head 2000, $7): Small 1000 one-shot Flush 1176. Shop: Juggler $4. Big: Flush 912 + 640. Shop $12: Buffoon -> Even Steven{R}. Head debuffs red (Smeared): discarded debuffed cards, Flush 1152 + Straight 204 (cycle) + Flush 1296 = 2652/2000.
Ante 3 (Economy/Economy/The Club 6400, $11): Smeared perished, sold. Buffoon -> Gros Michel (+15 mult), Blue Joker{R} $1 (+2 chips x cards in deck: a 1-card High Card makes 1600-2600!). Skipped Small (Economy +$9). Big 4800: Straight 4779 + High 4C 2280. Shop: Popcorn $5. Club: Broadway Straight 8319 one-shot.
Ante 4 (Coupon/Negative/The Window 18000, $16): sold Even Steven (rental) -> holo Scary Face $7. Skipped Small (Coupon). Big 13500: Pair KK 7568 + FH 777TT 9381 (Gros Michel died). Coupon shop: Fibonacci{P} $0, free Emperor -> Temperance + Fool (copy) = banked sell value, free Celestial -> Saturn, free Arcana -> Hierophant (bonus KC/JS). Reroll -> Cavendish $4 (sold Popcorn). Window: Straight 11526 + FH 14040.
Ante 5 (Double/Boss/The Arm 50000, $17): rerolls -> Brainstorm $10 (sold Juggler). Brainstorm LAST copying Cavendish leftmost = x9 (advisor measured est 67k -> 115k). Temperance +$17, Hermit doubled $14 -> $28, Saturn x2 (Straight L4), Pluto. Small 25000: 2P 4422 21840 + High 5S 7128. Big 37500: Flush 29808 + High AS 7128 + High 3D 6318. Arm: Flush 30498 + Straight 64296 (one-shot; Arm costs a level).
Ante 6 (Coupon/Juggle/The Mark 120000, $20): EMERGENCY 0.29-0.33. Sold perishing Fibonacci -> Abstract $4 (+18); 2 rerolls ($13) found nothing (Ice Cream, Credit Card, Red Card, Swashbuckler); Arcana -> Temperance. Small 60000: 2P KK77 20604, then discarded (4) for a T-straight (p0.36) missed, discarded 5 more (p0.90), 2P KK77 20808, final hand best High TD 11730 -> 53142/60000. LOSS.

## Post-mortem

Binding constraint: scaling at ante 6. Typical hand ~20k (Two Pair/Pair/high card) vs a 60k Small; the build was flat +mult/+chips x one Cavendish x3 with a Brainstorm copy of Cavendish, no growth xMult, and the best hand type (Straight L3, ~48-64k) needs a rare 5-card draw. I never got a second source of x-mult beyond the Brainstorm copy, and with 6 slots full of mediocre jokers (eternal Walkie, rental Blue, perishable Abstract) there was no room to take one.

Decisions I would change:
1. Ante 6 Small, hands 2-3: I discarded 4 then 5 cards chasing a straight/flush (solver p 0.97 / 0.90) while holding a 12-20k Two Pair that was 1/3 of the need each. The combination "need 39k, two hands" had no hand worth ~39k except Straight/Flush; I should have first played the single KC bonus/face High Cards? No: honestly the right lever was the previous shop: with $20-26 and Temperance I spent $13 on 2 empty rerolls + $4 Arcana instead of buying Saturn/Celestial packs to raise Straight (my only 50k+ hand). Spending on levels for the hand that actually clears would have given +20% per level.
2. Skipping the ante-6 Small for the Coupon tag (free shop after Big) was the other option; I played it because the Big (90k) looked harder. In hindsight both blinds were beyond one-hand reach; the skip would at least have saved a Boss-ward shop.
3. Joker slots: I kept Walkie Talkie{ETERNAL} (fires on 10/4 only) as a permanent slot from ante 1. With 6 slots, an eternal conditional joker cost me one real scorer for the whole run.

Reusable rules (if-then):
- IF Blue Joker (+2 chips per card IN DECK) is owned THEN its chips shrink during the round (deck count drops with each draw: 104 at round start, 50 by the last hand). Play the biggest hand FIRST while the deck is full; the last hand of a round gets ~half the Blue bonus (est already includes this).
- IF Brainstorm is owned with a leftmost xMult THEN put Brainstorm LAST (rightmost) so its copy multiplies all +mult jokers: advisor measured est 67k -> 115k. Card-phase jokers (Walkie, Scary, Fibonacci, Even Steven) are multiplied by BOTH x3s, joker-phase +mult only by the second.
- IF Temperance + The Fool appear (Emperor creates them) THEN use Temperance, then The Fool (copies it) to double cash; Hermit doubles $14 into $28 next. Banked cash feeds rerolls and interest.
- IF a one-card High Card is worth ~5k+ (Blue Joker, Fibonacci, Walkie on a 4/10) THEN hand type is irrelevant; keep 3 distinct qualifying single cards for the three hands rather than building flushes.
- IF the Small blind needs more than one hand's typical score x2.5 and you have discards left THEN do not spend both discards on a straight draw of p0.36/0.20: keep the made 20k hand and look for the 2nd-best repeat hand, or buy levels of the 50k hand type in the previous shop.
- IF the boss is The Head/Club/Window (suit debuff) with Smeared Joker THEN BOTH suits of that colour are debuffed; discard them at once and flush with the other colour.

Advisor/CLI defects:
- `shopadvise` ranks Walkie Talkie{ETERNAL} as "core joker you would keep anyway" at ante 1 although it only fires on 10s/4s.
- SIM treated Brainstorm as +0.31 but ORDER FIRST later found a 1.7x better order (Cavendish leftmost/Brainstorm last); the SIM's reorder-awareness in the buy decision lags.
- Solver p 0.90 for the Small 60000 discard assumed Straight/Flush hits; 36%/20% draws plus the lost 20k Two Pair floor was a 10% tail that hit. `advise` never printed the "max est if every remaining hand is High Card" fallback (11.7k) which was the real floor.
- After a Pair/Two Pair `play ... + filler` the CLI does not warn that the filler is the card I wanted for a later High Card (kept AC/4C choice mattered).
