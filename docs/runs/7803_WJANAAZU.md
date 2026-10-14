# Run WJANAAZU (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (21884/37500)

Ante 1 (300/450/Goad 600, $4): Small: discarded to 888 55, Full House 296, then K high card. Shop $5: Buffoon pack offered Misprint{ETERNAL,RENTAL} or The Family; I took Family as a $4 sell bank. Big 450 with no jokers: club Flush 288, Two Pair AA88 116, Straight 240. Shop $5: Droll Joker{ETERNAL} $4 (advisor said LEAVE). Goad: spade Flush 490 (all cards debuffed, but Droll still fired), dig High Card 15, diamond Flush 994.
Ante 2 (1000/1500/Needle 1000, $6): Arcana pack -> Empress on KS KH (Mult cards). Skipped Small for Rare Tag. Big: KKK (two Mult) 660, then spade Flush 980. Shop: free Rare-tag Campfire{RENTAL}, sold Family -> x1.25; Egg{PERISHABLE} $4. Needle: 2 discards to a heart Flush, 1207/1000.
Ante 3 (3200/4800/Flint 6400, $9): sold Campfire. Jumbo Buffoon -> foil Gros Michel{RENTAL}. Skipped Small for Investment Tag. Big: diamond Flush 3422 + Two Pair 1666. Shop: Jupiter; sold Egg ($8) for a Buffoon pack -> Half Joker{ETERNAL}; Arcana -> High Priestess (Jupiter + Mercury). Flint: High Card KH(Mult) 2520, Pair 6 2775, High Card A -> won with 0 discards used.
Ante 4 (9000/13500/Plant 18000, $30 after Investment): Celestial pack (no Jupiter/Mercury) -> Uranus, Arcana -> Wheel (Nope), Popcorn{RENTAL} $1, 1 reroll ($5, nothing). Skipped Small for Charm Tag: Mega Arcana -> Justice on AS + Death copy = 2 Glass AS. Big: Pair 2 4582, Pair A 5917, Pair 5 4930. Shop: Bull{PERISHABLE} $6. Plant: Pair 8 5994, heart Flush (debuffed QH JH) 7448, Pair 2 5346.
Ante 5 (25000/37500/Hook 50000, $9): Sly $3, Mercury $3 (Pair L3). Played Small (D6 Tag): spade Flush 9690, Pair 6 8058, Pair A 8568. Money -$3 after $6 rent, shop had only $5 jokers. Big: Pair K 8160, Pair 4 6956, Pair 2 6768 = 21884/37500. GAME OVER.

## Post-mortem
Binding constraint: SCALING. No xMult joker appeared in any shop or pack the whole run: 10 shops, 1 reroll, 4 Buffoon packs.
The best hand was ~8-10k (Pair L3 + Sly + foil Gros + Half Joker + Popcorn), and the ante-5 Big needs 12.5k per hand. Money was the
second constraint. The two rentals (Gros, Popcorn) cost $6 a round and took the wallet from $30 at ante 4 to -$3 at ante 5. So no
reroll budget was left when it mattered.

Decisions I would change:
1. Ante 4 shop ($30): I spent $14 on a Celestial pack (Uranus, wasted), an Arcana pack (Wheel, Nope), Popcorn and one reroll. Better:
   stay at $25+ for $5 interest, and spend only on rerolls hunting an xMult. Popcorn did help clear the Plant, though.
2. Mega Arcana (Charm Tag): I took Justice + Death to make 2 Glass Aces. Glass x2 applies when the CARD scores, before the jokers add
   their +mult. With an all-+mult joker line, Glass AS was worth +7% (est 3762 vs 3528). Temperance (~$9) plus Strength, or saving for
   rerolls, would have been worth more.
3. Bull{PERISHABLE} $6 at ante 4: its +2 chips per $ fell to 0 once rent pushed money to $3 or less. It was a bad buy with two rentals owned.

What worked:
- Droll Joker{ETERNAL} plus flush digging carried antes 1-2 with no other scorer.
- Skipping three Small Blinds (Rare, Investment, Charm) was right each time. The Small shop would have had $2-4, and each skip saved rent and Gros rolls.
- Half Joker with 3-card plays: Pair, or a High Card + 2 fillers, scored 2.5-6k at ante 3-4. Under the Flint, a single Mult K scored 2520.

## Reusable rules (if-then)
- IF your jokers are all +mult/+chips (no joker xMult), THEN do not spend a Justice/Death pick on Glass cards. Glass x2 multiplies
  the base mult (1-8) before the jokers add theirs, which is worth ~5-25%. Glass pays only once an xMult joker is to its right.
- IF you own Half Joker, THEN play Pairs and High Cards as 2-3 card plays (pair + 1 filler). Under the Flint, a single Mult/high card
  with Half (+20) scores like a pair. Two Pair (4 cards) loses the +20 and scores less than a Pair.
- IF your only scorer is Droll/flush-gated and you hold 4 of a suit with 2 hands left, THEN play the off-suit cards as a dig
  (High Card) rather than a weak pair. A flush with Droll is ~3x any pair at ante 1-2.
- IF two rentals are owned at ante 4+ and you have $25+, THEN sell the weaker rental before the next round end unless it decides
  THIS blind. Rent turned $30 into -$3 within 4 rounds.
- IF the next blind needs more than 1.5x your best hand x 3 and no xMult is in sight, THEN put every dollar into rerolls in the shop
  BEFORE that blind. Packs and planets for off-type hands add 5-10% and cannot close a 50% gap.

## Advisor/CLI defects
- Pack `advise` ranked The Family (x4 only on Four of a Kind) 100 "XMULT" at ante 1 with 0 jokers. `shopadvise` then set "main hand
  Four of a Kind" from owning Family with zero Quads played. Gated xMults should count only when the gate hand is the main hand.
- `advise` filler choice destroys flush draws. At ante 2 Big it advised `play TRIPS 2 3 4 8 7` with fillers 2S 4S out of a 4-spade draw.
  At ante 3 Big it advised `play PAIR 4 5 8 7 6` with fillers 7D 6D 2D out of a 4-diamond draw (a flush the next draw made 3422).
- At the Plant's last hand, `advise` picked the Flush/Trips that score the Glass AS (1/4 shatter) when Pair 2 (no glass) also cleared.
  It should prefer a clearing hand that doesn't risk Glass.
- Blind-select advice said "do not skip" at ante 2 (Rare Tag) and ante 3 (Investment Tag). Both skips were clearly right: the Small
  shop would have had $2-4.
- Arcana packs: "No pack advice for this pack type" (Arcana, Mega Arcana).
- `shopadvise` kept proposing "sell Popcorn" one shop after I bought it as a 3-blind bridge. Minor.
Bridge issues: none. Estimates were exact on almost every hand (Flint Pair 6: est 2664, actual 2775).
