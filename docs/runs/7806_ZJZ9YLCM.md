# Run ZJZ9YLCM (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Big Blind (87251/90000)

Ante 1 (300/450/Hook 600): Small Broadway 324. Shop $6: bought Riff-raff $6 over Buffoon pack -> Big select gave Jolly + Abstract; Quads 2 dealt 1632. Blue Joker $5. Hook select -> Popcorn + Splash; Two Pair 6816 one-shot.
Ante 2 (1000/1500/Goad 2000): skipped Small for Negative Tag. Big Pair 9 5764. Shop: CLI refused buying the $0 negative Even Steven at 6/6 slots (bug), sold dead Riff-raff to buy it. Goad Two Pair AAKK 6864. $22.
Ante 3 (3200/4800/Wheel 6400): Constellation (eternal) $6, Spectral -> Aura on 8C (holo). Small Straight 5863. Sold dying Popcorn -> Odd Todd $4; Jumbo Celestial -> Mercury. Big Pair 6 + odd fillers 10428. Jumbo Arcana -> Justice glass 8H. Wheel: discarded 2 face-downs, Pair K + odd/even fillers 8197.
Ante 4 (9000/13500/Arm 18000): Uranus, Jumbo Arcana -> Empress (Mult AS/AC). Skipped Small (Uncommon Tag -> gave an eternal+rental Certificate, declined). Big: Two Pair 12096 + Broadway 7524. Celestial -> Mercury, Arcana -> Fool -> Mercury (Pair L4, Constellation x1.4). Arm: Two Pair (L2->L1) 12448 + Straight L1 8593 (Arm can't lower L1, kept Pair L4). $6.
Ante 5 (25000/37500/Needle 25000): Saturn, Jumbo Arcana -> High Priestess (Pluto+Mars, Constellation x1.7). Skipped Small for Investment Tag ($4 wallet; override of "don't skip ante 5"). Big: Pair A (mult) + odd fillers 22028, Pair Q 15432 (40 short, by design), Pair K finish. Bought Earth+Neptune (x1.9). Needle: Pair 6 + AD, holo 8C, 5D = 25642/25000 exact est. $2.
Ante 6 (60000/90000/Pillar 120000): shop $32 (Investment paid): Mars (x2.0), Buffoon pack blocked by CLI (slots full), 2 rerolls ($11) found only rental/eternal junk. $18.
  Small 60000: Pair A (mult) + 9,T,2 27900, Pair 6 + A,8,5 21252, Pair 5 alone 13260 (2 cards for Pillar). Shop $21: sold Jolly -> Hanging Chad (perishable), 2 Celestial packs -> Earth, Uranus (x2.2). $10.
  Big 90000: Pair A + 7,5,3 35028; discarded KQQ then 7D/4C/2H -> Full House 999+77 27561; forced last hand Pair 6 + A,T,5 24662 (best of every `sel`) -> 87251/90000. GAME OVER.

## Post-mortem
Binding constraint: SCALING. Constellation (x1.1 -> x2.2 from 12 planets) was the only multiplier the whole run. The Splash + Odd Todd +
Even Steven + Blue + Abstract flat engine made 25-35k per hand at ante 6, and that ante needs 30k/40k per hand at the Big/Boss.
No clean xMult joker was offered in any shop or pack. Every joker the shop rolled at ante 4-6 was Eternal/Rental junk (Certificate,
Reserved Parking x2, Runner, Hiker, Ceremonial Dagger, Troubadour).

Decisions I would change:
- Ante 6 shop 1: I spent $11 on two rerolls that found nothing. Three $3-4 planets instead would have made Constellation x2.5, not x2.2
  (+13.6% on every hand). That alone turns 87251 into about 99000, so the lost Big Blind is cleared. This was the losing decision.
- Ante 6 Big, hand 2: I spent both discards before hand 2, which left the forced last hand with 3 leftover cards, 5 draws and no
  discard. It fell 2749 short. Close call either way, but keeping one discard for the final hand is the playbook rule. I broke it.
- Ante 4: The Fool (-> Mercury) over Hermit (+$6) was fine. Leaving ante 4 with $6 and ante 5 with $2 meant no interest all run.

What worked: Riff-raff ($6) at ante 1 gave four free commons (Jolly, Abstract, Popcorn, Splash), which carried antes 1-3. Splash plus
odd/even jokers turns every filler into +31 chips or +4 mult, and `sel` on filler sets found 20-50% more than the ADVICE line.
Skipping the ante-5 Small Blind for Investment ($4 wallet) paid $25 at ante 6. The est was exact on every hand in the run.

Reusable rules (if-then):
- IF Constellation is your only xMult at ante 5+, THEN buy every $3 planet and Celestial pack before any $5+ reroll. Each planet is a
  guaranteed +0.1x (about +5%). At Gold, rerolls at ante 6 found only sticker junk (2 rerolls, 0 usable jokers).
- IF you own Splash, THEN `sel` 3-4 filler sets before every play. Use odd cards with Odd Todd, even cards with Even Steven, and
  Mult/Glass/holo cards anywhere. ADVICE picked weaker fillers (Pair 6: 10212 vs 10428; Pair A: core est 14664, best play line 22028).
- IF you own Hanging Chad, THEN the retriggered card is the leftmost scoring card, and hands sort by rank, so it is the highest card
  played. A Mult Ace or an odd card (Odd Todd) first beats a face card first (Pair 9 hand: 19206 with K first vs 24076 with T first).
- IF the boss is The Arm, THEN close the round with an L1 hand type (Straight L1 8593): the Arm cannot lower L1, so your leveled Pair
  keeps its level.
- IF a one-hand boss (Needle) shows est >= need, THEN play at once. Discards draw cards out of the deck, and that lowers Blue Joker chips.
- IF the ante-5+ wallet is under $5 and the Small Blind tag is Investment, THEN skip the Small Blind: +$25 next ante beats a $0 Small Blind shop.
- IF an Uncommon Tag is the only reason to skip, THEN expect its free joker to carry stickers at Gold: here it was an Eternal+Rental
  Certificate, which I declined.

Advisor/CLI defects:
- `buy 1` ABORTED "joker slots are full (6/6)" on a $0 NEGATIVE Even Steven (from Negative Tag), although the game's legal list had
  SHOP_BUY slot 1. A negative joker needs no slot. I had to sell Riff-raff to buy it. shopadvise also said LEAVE while ranking it 89.
- `pack 1` ABORTED for a Buffoon pack with full joker slots ("could only be skipped"), but selling inside an open pack is allowed.
  This blocked an xMult hunt at ante 6.
- The "main hand" flips with the last played type (Straight -> Two Pair -> Pair). Planet picks then print "NOT your main hand" for
  Mercury, although Pair was played most often.
- With Splash, the `advise` candidate est is the core-cards est (Pair A 14664), while the `play` line with fillers was 22028. Its
  filler choice was also suboptimal (see rules above).
- Under the Pillar, `advise` printed "Playing WITHOUT fillers and with the fewest cards". At ante 6, fillers were 30-50% of each hand,
  and every blind needed them.
Bridge issues: none. One orchestrator-side rate-limit pause mid-run; the game state was intact.
