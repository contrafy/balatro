# Run 3WSFNWWA (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (23529/37500)

Ante 1 (300 Boss tag / 450 Rare / The Pillar 600, $4): Small: disc toward spades, Flush 316 one-shot. Shop $6: Buffoon (over Odd Todd{ETERNAL}) -> holo Scary Face. Big: Pair 7 288 + Pair T 360 (2-card plays for Pillar). Shop $7: Misprint{RENTAL} $1. Pillar: Pair Q 2880 one-shot.
Ante 2 (1000 Top-up / 1500 Charm / The Fish 2000, $10): Arrowhead $7. Skipped Small (Top-up -> Joker, 8 Ball). Big: Pair A 3034. Shop $6: sold Misprint (rent). Fish: overrode diamond-flush chase (it discarded KS), dumped 5 low, Pair KK 2240 one-shot.
Ante 3 (3200 Standard / 4800 Coupon / The Arm 6400, $15): Celestial -> no Mercury, took Jupiter. Passed The Tribe{PERISH,RENTAL} (flush-gated). Small: FH 66633 2052 + Pair Q 1440. Shop $14: passed Photograph{PERISH} (card-phase x2 on base mult = +2 mult), Mr. Bones{PERISH} $5. Big: 2 discards to spade Flush L2 7340 one-shot. Shop $16: passed Mega Arcana, left. Arm: 2P QQ88 3456 + Trips KKK 3400 (L1 types, nothing to lose).
Ante 4 (9000 Rare / 13500 Negative / The Mouth 18000, $25): Ramen $6 (first xMult), sold 8 Ball, Jumbo Celestial -> Mercury (Pair L2), Arcana -> Emperor (Moon, Lovers). Small: FH 4163, Lovers on QD (wild = spade for Arrowhead), dig Pair 4 1077 keeping 4 spades, Pair JJ 5059. Shop $13: Jolly{ETERNAL} $3, kept Mr. Bones (advisor said sell). Big: spade Flush (wild Q) 22635 one-shot. Shop $18: Buffoon (Crafty/Popcorn rental, skipped), Celestial -> Mercury (Pair L3). Mouth: locked Pair: TT 5376, JJ 8088, 99 4998 = 18462/18000.
Ante 5 (25000 Standard / 37500 Meteor / The Manacle 50000, $17): sold perished Mr. Bones, Jumbo Celestial -> Mercury (Pair L4), left $13 (no scorer on offer, reroll odds poor). Small: solver lines, Pair TT 5872 + Pair KK 8691, then discarded 5 keeping 5S 3S 2S and drew a spade straight flush 13756 = 28319/25000. Shop $15: Celestial -> no Mercury, Jupiter (Flush L3); 1 reroll ($5) -> Photograph{ETERNAL} $5 (advisor 130), $1 left. Big: Pair 66 5338, 2 discards (best FH 9397 could not pace), 2P JJ77 6822, Moon -> club flush 11369 = 23529/37500. GAME OVER. Jokers [holo Scary Face, Arrowhead, Joker, Jolly(E), Ramen x1.60, Photograph(E)], Pair L4, Flush L3.

## Post-mortem

Binding constraint: SCALING. One joker-phase xMult (Ramen) for the whole run, bought at ante 4, and it decayed from x2.00
to x1.60 within 6 rounds (40 cards discarded at 2 discards x 4-5 cards). The flat stack (holo +10, Joker +4, Jolly +8 =
+22 mult) on Pair L4 gave ~5-9k per pair at ante 5 vs 12.5k per hand needed at the Big. The only hands that ever beat pace
were spade flushes (Arrowhead +50 per spade: 7340 at ante 3, 22635 at ante 4, straight flush 13756 at ante 5); pairs
cleared ante 4 by margins of 3%. Money never exceeded $25: every ante-3/5 shop had no r/g xMult, and the one I found (Ramen)
came from saving $25 into ante 4.

Decisions I would change:
1. Ante 3 first shop: Mr. Bones{PERISHABLE} $5 never fired (perished after The Mouth). Those $5 plus the $3 interest they
   would have earned were a reroll or most of a Celestial. With B >= boss/3 for the current ante, insurance is a luxury.
2. Ante 4 Small: played it (advice "under half the boss") instead of skipping for the Rare tag. The shop it bought me gave
   Jolly{ETERNAL} (+8). A Rare tag is the only reliable way to see Baron/Blueprint/Ancient/Stencil-class jokers; with 1
   xMult and a pair engine below pace, a free Rare joker is worth more than one ante-4 shop with $13.
3. Ante 5 Celestial picks: Mercury twice for Pair while every big score came from spade flushes. With Arrowhead + a wild
   card, Flush was the real main hand; Jupiter first would have made the flush ~25-28k at ante 5.
4. Ante 5 Big: Photograph{ETERNAL} for my last $5. It is card-phase (x2 on Pair L4 base mult 5 = +5 mult, ~+18%) and
   cost the interest; it did not change the outcome. Keeping $6 changes nothing either; the run was lost in the ante-4 shops.

What worked:
- The Lovers on a Queen: a Wild face card counts as a spade for Arrowhead and completes spade flushes (22635 Big one-shot).
- Solver "dig" lines (play a weak pair with fillers, hold 3-4 spades) found a straight flush for the ante-5 Small (52% line).
- The Mouth: locking Pair with a 5-card filler play and saving both discards for 2 more pairs (18462/18000).
- The Pillar: 2-card plays in Small/Big kept the boss deck clean.

Reusable rules (if-then):
- IF you own a suit joker that adds +50 chips or +3 mult per card (Arrowhead, Wrathful, Greedy...) AND a Wild card, THEN
  that suit's Flush is your main hand: take Jupiter over Mercury, and with 3+ cards of that suit after the first play,
  dig for the flush instead of the pair.
- IF Ramen is your only xMult, THEN count it as x1.8 next ante and x1.6 the ante after (2 discards of 4-5 cards per round);
  buy the second xMult one ante earlier than the GOLD CHECK target says.
- IF your joker-phase flat mult is >= 20, THEN Photograph/Glass/Steel (card-phase x2 on a base mult of 2-5) add only
  +10-20%: never spend the last $5 or your interest bracket on one at ante 5.
- IF a perishable Mr. Bones would cost $5 while your best hand already reaches boss/3 of this ante, THEN skip it; buy it
  only when B < boss/3 and no scorer is on offer.
- IF the ante-4 Small offers a Rare tag and you own exactly 1 xMult, THEN skip for it (the next shop holds a rare joker);
  the $0 Small only buys one shop visit.

Advisor/CLI defects:
- `advise` at The Fish (ante 2, need 2000): rule pick `disc 2 3 4 6` threw away KS (face + spade, the 2240 pair card) to
  chase a diamond flush whose own est (~1170) could not clear the blind. A chase should be rejected when the made target
  does not reach the need.
- `shopadvise` ranked Photograph{ETERNAL} 130 [XMULT] at ante 5 (and 75 perishable at ante 3) although it is a card-phase
  x2 on base mult; with +22 flat joker mult it is worth ~+18%. The playbook already says card-trigger xMults do not count.
- `shopadvise` SELL advice for Mr. Bones{PERISHABLE 2 rounds} in the ante-4 Big shop, with Big 13500 + The Mouth 18000 ahead
  and B 7440 < boss/2: it was the only insurance and no xMult was on offer to fill the slot.
- SCORE CHECK / main hand stays "best Pair (KK)" with Arrowhead + a Wild spade Queen, where the spade flush (22635) was 3x
  the pair; Celestial pack advice kept saying "take Mercury" and labeled Jupiter "mostly wasted".
- Ante 4 Small: the ADVICE line picked a straight-draw rule line (`disc 1 6 7 8`, p 0.99) over the solver's own top line
  (4-spade flush draw p 1.00, exp 14226 vs 10731); I followed the solver.
- `shopadvise` right after a Celestial `pick` printed "shopadvise only works in the shop" once (state not settled); retry
  after 2 s worked.
- Bridge: no rejects, no offline; est exact on every non-Misprint hand.
