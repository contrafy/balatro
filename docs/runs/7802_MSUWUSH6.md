# Run MSUWUSH6 (port 7802, claude-fable-5-1) - Black Deck Gold Stake - LOSS at ante 1 blind The Club (385/600)

Ante 1 (300/450/The Club 600; tags Foil/Foil): played Small (advice: Foil pays only after Big, 0 jokers). Small: disc 4 for
  KQT9 draw -> Two Pair QQ99 116, disc 4 again (overrode "keep Pair 2 floor") -> Two Pair JJ33 92, Broadway 324 = 532/300.
  Shop $4: overrode Uranus (advisor 88) for Buffoon $4 -> Swashbuckler / Juggler{ETERNAL,RENTAL}; took Swashbuckler ($2 asset,
  advisor said skip). $0. Big 450: disc 4 keeping QJ98 (overrode "keep Pair 3", disc 2) -> Straight 9-high 260, then dealt
  QQQJJ Full House 360 = 620/450. Shop $5: Devious{ETERNAL} $4 (+100 chips Straight, advisor pick) vs Jumbo Buffoon $6: sold
  Swashbuckler ($7), Jumbo Buffoon -> Ride the Bus{RENTAL} / Egg{RENTAL} / Walkie Talkie{PERISH,RENTAL} / Seeing Double
  {PERISHABLE}; took Seeing Double (x2 club+other suit) over Egg (advisor pick). $1. Boss The Club (clubs debuffed, so Seeing
  Double can never fire): hand KD QC(d) JH TD 8D 7D 6C(d) 2H, disc 4 keeping 4 diamonds (61%) -> Flush D 316 (est exact).
  Then AC(d) KH QS TC(d) 8H 6H 4S 3S, need 284 in 2 hands/1 discard: disc 4 keeping AKQT for a J (40%) -> drew AH QH 9H 4C:
  Two Pair AAQQ real 102 (est said 204, wrong). Dumped AC QS TC 4C as High Card (5) keeping 4 hearts (5 hearts in 31, 52%):
  missed. Final Pair A 64. 385/600. LOSS.

Post-mortem
- Binding constraint: no scoring joker at the ante-1 boss (600) with a suit boss debuffing a quarter of the deck. Three
  jokerless 5-card hands must average 200; one miss on a draw ends it. Every Gold-stake pack joker I saw was stickered
  (Juggler eternal+rental, Ride the Bus/Egg rental, Walkie Talkie perish+rental, Seeing Double perishable); the only
  clean scorers offered all run were Devious{ETERNAL} $4 and Swashbuckler.
- The decisive mistake was shop 2 ($5): I passed on Devious Joker{ETERNAL} (+100 chips if Straight; advisor's pick) for
  a Jumbo Buffoon gamble. A L1 Straight with Devious is (30+100+45) x 4 = 700, a ONE-HAND clear of every ante-1 blind and
  the ante-2 Small; the boss hand 1 had KQJT (8 outs, 4 draws, 57%) and I instead chased a flush worth 316. I let the
  "eternal on a conditional joker" penalty outweigh survival at the ante where most Gold runs die. Straights/flushes are
  the only jokerless hands that score 250+, so a +100-chip straight/flush joker IS the ante-1 engine.
- Second mistake: Seeing Double needs a scoring club and the upcoming boss was The Club. It was guaranteed zero at the
  boss (verified: SMODS.seeing_double_check uses Card:is_suit without bypass_debuff, so a debuffed club never counts).
  I bought it for ante 2 and never reached ante 2. Buy for the next blind first.
- Shop 1 ($4): overriding Uranus (Two Pair L2) for a Buffoon pack was consistent with the playbook (joker first), but it
  whiffed (Swashbuckler/Juggler). With Uranus the boss would have been 316 + 213 (AAQQ at L2) + 64 = 593/600: still a
  loss by 7, so the shop-1 choice was not decisive; shop 2 was.
- Boss play: flush draw 61% (hit), then the 40% Broadway draw with two debuffed cards counting for type, then a 52%
  4-heart dig. Each was the highest-probability line available; est for the two-pair alternatives was inflated by the
  Seeing Double bug and would have led a trusting model into a 5% line.

Reusable rules (if-then):
- IF ante 1 on Gold and the shop has a $4-5 +100-chips Straight/Flush joker (Devious, Crafty) and you own no scorer, THEN
  buy it even if Eternal: a L1 Straight/Flush then scores ~700, one hand clears 300/450/600 and the ante-2 Small 1000.
  An eternal slot costs nothing if you never reach ante 4.
- IF the upcoming boss debuffs a suit (Club/Goad/Head/Window) THEN never buy or pick a joker whose trigger needs that
  suit (Seeing Double = club, Greedy/Lusty/Wrathful/Gluttonous of that suit, suit-flush jokers) before the boss: it
  scores 0 there, and ante-1 Gold runs rarely survive the boss without a scorer.
- IF `hands`/`sel` shows (DEBUFF) on a card inside a Seeing Double/suit-count hand THEN subtract the x2: debuffed cards
  are not "of a suit" for the game. Recompute by hand: (base + scoring chips) x base mult.
- IF jokerless and need > 200 per hand THEN only 5-card hands count (Straight ~260-324, Flush ~316, Full House ~360); a
  made low Pair is not a "floor" worth keeping - discard 4 toward a 4-flush/4-straight draw (9 outs x 4 draws = 61%).
- IF a Buffoon pack at Gold shows only rental/perishable jokers and you have no scorer THEN the perishable one with
  no rent is the only acceptable pick, and only if it fires on the NEXT blind; otherwise Egg/rentals are worth +$2 at
  most and a skip is equal.
- IF you hold $5 and one junk joker at the ante-1 Big shop THEN a guaranteed clean/eternal scorer for $4 beats selling the
  junk to open a Jumbo Buffoon: ~3 of 4 Gold pack jokers carry rent or perish, so the "4 chances" are closer to 1.

Advisor/CLI defects:
- est counts DEBUFFED clubs for Seeing Double: "TWO PAIR T8 idx 4 3 6 7 est 184" with TC(DEBUFF) (real 92) and "TWO PAIR
  FACE AQ est 204" with AC(DEBUFF) (real 102). Source: SMODS.seeing_double_check -> hand[i]:is_suit(k) with no bypass,
  Card:is_suit returns nil when self.debuff. Flower Pot likely shares the bug. `sel` only added "debuffed card scores
  nothing" and kept the x2.
- advise at The Club hand 1 proposed `disc 2 7 5 6 8` (throwing 8D 7D, two of my four diamonds) for a straight draw with
  EV 182 while the 4-flush draw was 9 outs / 4 draws = 61% for 316. It does not evaluate 4-flush draws against straight
  draws when both exist.
- advise at Big 450 (and Small) kept a 2-card low pair "as a floor" (Pair 3 est 32 vs need 450) and drew only 2 cards;
  with no joker a low pair is worth 7% of the blind and halves the straight outs. Draw 4.
- Pack advisor ranked Egg{RENTAL} top at 35 "ECON": Egg under rent nets +$2 total (sell value +3 and rent -3 cancel). It
  should score as a near-skip, below a perishable x2 that fires next ante.
- shopadvise at the first shop with 0 jokers ranked Uranus 88 above the Buffoon pack 78, against playbook section 5
  (first affordable joker before planets at ante 1-2).
Bridge issues: none; every action settled on the first try, est was exact on every non-Seeing-Double hand (116, 92, 324,
260, 360, 316, 5, 64).
