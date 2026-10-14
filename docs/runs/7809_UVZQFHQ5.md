# Run UVZQFHQ5 (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Small Blind (546/1000)

Ante 1 (300/450/Club 600, $4 start): Small: discarded 4 off-suit for a heart flush (missed), then played AS JS TS 2C as a High Card "dig" (16) to keep the 4-heart draw and the last discard; Flush 280 + Full House QQQ77 cleared. Shop $4: Buffoon pack -> Hiker (other card was an Eternal Scary Face). Big 450: club Flush 316, dig play KD 9D 8C 5D (15) keeping 4 hearts, heart Flush 288 = 619. Shop $4: Ride the Bus $6 unaffordable, LEFT (Celestial pack $4 skipped on advisor's "take None"). Club boss 600: heart Flush 296, discard to a diamond Flush 256, Two Pair AATT 114 = 666.
Ante 2 (1000/1500/Window 2000): shop $9: advisor REROLL ($5) -> Chariot/Star tarots only, left with $4. Small 1000 with only Hiker: Full House 999 88 352, Two Pair KK55 120, Pair AA 74 = 546/1000. GAME OVER.

## Post-mortem
Binding constraint: zero +mult jokers entering ante 2. Ante 1 was won entirely on L1 flushes (~260-316 each, 6 flushes in 9 scoring hands). Gold's $0 Small Blind and $4 start meant every shop had $4-9, and the shops offered no affordable +mult joker (Campfire $9 Eternal, Ride the Bus $6, Popcorn perishable $5, Satellite, Rough Gem). The single Buffoon pack offered Hiker (chips-only, slow) or an Eternal Scary Face (chips-only). With base mult 4 on a flush and no mult source, the ante-2 Small Blind (1000 = 333/hand) was out of reach of every L1 hand except a lucky quads/straight flush.

Decisions I would change:
- Ante 1 shop 2 ($4): I left on the advisor's LEAVE. A Celestial pack ($4) had a real chance at Jupiter: Flush L2 is 50x6 instead of 35x4, i.e. my 280-point flushes become ~500. Two of those clear the 1000 Small Blind. With no joker affordable, a level for the hand I had already played 5 times was the only scaling available.
- Ante 2 shop ($9): the advisor's $5 reroll found only tarots. The Arcana pack ($4) plus The Star ($3, 3 cards -> diamonds, flush consistency) or keeping $9 for interest were no worse. A Celestial pack was not offered there.
- Hiker vs Scary Face Eternal: both chips-only; Hiker was fine, but neither fixes base mult 4. In a jokerless flush deck, chips jokers add only ~10%.

Reusable rules (if-then):
- IF you hold 4 cards of a suit with 2 hands left and a discard, THEN play the 4 off-suit cards as a High Card "dig" instead of discarding: it scores a little, draws 4 cards, and keeps the discard for a second try (worked twice this run: 296 + 15 dig -> flushes cleared Small and Big).
- IF your ante-1 scoring came from Flushes (3+ played) and you own no +mult joker, THEN spend a $4 shop on a Celestial pack or a direct Jupiter before leaving ante 1: Flush L2 (50x6) almost doubles a jokerless flush, and the ante-2 Small Blind needs 333 per hand.
- IF you enter ante 2 with zero +mult/xMult jokers at Gold, THEN expect the 1000 Small Blind to need a Full House/Flush every hand; a chips-only joker (Hiker, Scary Face) does not change that.

Advisor/CLI defects:
- shopadvise printed "main hand undecided" and "take None" for both Celestial packs after six Flush plays in ante 1 (ante 1 shop 2: "Jumbo Celestial Pack $6 [hand level gamble: take None ...]"). The main-hand detector should count Flush plays; it then rated the $4 Celestial pack 30 and said LEAVE, with no affordable joker in the shop.
- shopadvise at ante 2 ($9, one chips-only joker) said REROLL and left $4; the reroll found nothing. When the run already depends on one hand type, the reroll should weigh against a planet/Celestial for that type.
Bridge issues: none.
