# Run HGM3CNYK (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Hook (46987/50000)

Ante 1: Small 300 (Investment Tag), Big 450 (Coupon Tag), Boss The Goad 600 (spades debuffed). Start $4.
  Small: two discards to a diamond 4-flush missed, dumped Pair 2 (28), drew QQQ88 Full House 344. Shop $5: Blue Joker (perishable) $5 -> $0.
  Big 450: Two Pair AAJJ 300 + Pair 9 212. Shop $5: nothing (Jumbo Buffoon $6). Goad 600: discard to diamonds, drew JJJ77 FH 616.
Ante 2 (1000/1500/Pillar 2000): shop $13: Raised Fist rental $1, reroll -> Juggler/Midas eternal, left $7. Skipped Small for Rare Tag
  (it rolled DNA perishable+rental: wasted). Big 1500: Pair 44 alone 1908 (Fist on held 8). Pillar: Pair 6 + low fillers so Fist reads
  held 7: 1760 (advise said 880 with high fillers), Pair T 1080. $14.
Ante 3 (3200/4800/The Mouth 6400): shop $14: reroll -> Half Joker ETERNAL $5 (advisor wanted Celestial for "Full House"). $4.
  Skipped Small for Skip Tag (+$10 = $5 x 2 skips, no rent, Blue's last round kept for the Big Blind). $14.
  Big 4800: 44+2H 2968, 33 3332 (Fist on held 6). Blue perished, sold. Shop $20: Buffoon -> Shoot the Moon (Walkie eternal), Jumbo
  Celestial (no Mercury) -> Uranus, Misprint rental $1, reroll -> foil Joker ETERNAL $4. $0.
  The Mouth 6400: locked Pair (not Trips 4290): KK+3D 3520, JJ+4H -> cleared. $-6 rent then $0.
Ante 4 (9000/13500/The Flint 18000): sold Misprint (2 rentals = $6/round at $0). Skipped Small for Polychrome Tag ($1, shop useless).
  Big 13500: 99+2D 3822, discard 4 lows, KKK 6160, TTT 5940. Shop: free polychrome Wily Joker (tag). Flint: AA+5H w/ QQ held 7276,
  99+2C 6898, Two Pair 66/44 with QQ held -> won. $4.
Ante 5 (25000/37500/The Hook 50000): Temperance +$11, Spectral -> Immolate +$20, Celestial -> Mars (no Mercury), 2 rerolls ->
  Venus x2 (Trips L3). $7. Skipped Small for Orbital Tag (Pair +3 -> L4).
  Big 37500: discard 9/5/3/2 keeping 77+A J -> drew 7777; Trips 7 16267 (over Quads 12060, Half needs <=3 cards), AA+7D w/ QD held
  11049, discard 22 -> drew TTT 22500. Shop $8: banked Hierophant $3 (skipped Jumbo Celestial/Arcana). $5.
  The Hook 50000: discard K J 7 2 keeping QQ 33 (advise wanted to discard QQ), Hierophant on 33 -> bonus 33+6S w/ QQ held 19237;
  discard T 9 2 -> KK QQQ J TT; Trips Q 19125 (all held cards 10s, Hook-proof). Last hand needed 11638 with TT 22 K Q 9 8: no line
  could reach it (max 11250 if Hook dropped 2C+8D). Pair T 8625 -> 46987/50000. GAME OVER.

## Post-mortem
Binding constraint: SCALING (one xMult, the free polychrome Wily x1.5; everything else flat +mult). The build topped out at
~19k per hand at ante 5 (Trips L3 + Wily 100 chips, or a bonus pair with Queens held for Shoot the Moon), and The Hook 50000
needs 16.7k per hand from three hands, with the Hook randomly discarding the held Queens/high cards that Moon and Raised Fist
feed on. Lost by 3013. Money was the second constraint: Gold rentals (Raised Fist, Misprint) held the wallet at $0-7 from
ante 3 to 5, so there was never a reroll budget for a real xMult.

Decisions I would change:
1. Ante 5 Big-Blind shop ($8): I banked Hierophant ($3) and kept $5. Jumbo Celestial ($6, ~68% Mercury or Venus) would have
   added +15 chips/+1 mult to every pair for the rest of the run; Hierophant added +60 chips to ONE pair. The Hook loss was 3013;
   Pair L5 on hand 1 and hand 3 is worth ~+2000, so it might not have been enough alone, but it is the permanent choice.
2. Ante 4 I sold Misprint to stop rent at $0. Correct for money, but at The Hook Misprint's average +11.5 mult x1.5 was worth
   ~2-3k per hand: exactly the deficit. With an Immolate +$20 coming later, the rent would have been affordable.
3. Ante 3 shop ($20): Jumbo Celestial without Mercury ($6) and a Misprint I sold one ante later; a reroll for an xMult instead.

Things that worked (reusable if-then rules):
- IF you own Raised Fist, THEN pick fillers that are your LOWEST cards (3-card play with Half Joker) so the held floor rises:
  Pillar Pair 6 with low fillers est 1760 vs advise's high fillers 880.
- IF you own Half Joker and Wily/trips levels, THEN play Trips (3 cards) over Quads/Full House: Trips 7 16267 vs Quads 12060.
- IF you own Shoot the Moon, THEN never play Queens in a pair: keep them held (each +13 mult before the x1.5) and play another
  pair; play QQQ only as trips when every other held card is a 10-value card (Hook-proof Raised Fist).
- IF the Small Blind tag is Skip Tag after 2+ skips, Orbital Tag for your main hand, or Polychrome with $0-2, THEN skip it at
  Gold: it pays now ($10 cash / +3 levels / a free x1.5), saves $3 rent per rental and one perishable tick (Blue Joker survived
  into the Big Blind that way).
- IF Temperance is in the shop and your jokers sell for $8+ total, THEN buyuse it ($4 -> $12 here).
- IF The Mouth is the boss, THEN lock Pair with the first hand (not a one-off Trips) when Pair is your repeatable hand.
- IF the boss is The Hook, THEN it discards 2 random HELD cards before scoring: held-card jokers (Moon, Raised Fist, Baron)
  lose value; prefer a hand where every held card is equally good (all 10s here) or the scoring cards carry the value.

Advisor/CLI defects:
- `shopadvise` set the main hand to Full House after one ante-1 Full House and ranked a Celestial ("take Earth") over Half
  Joker (30) while every later hand was a 2-card pair.
- `advise` filler choice ignores Raised Fist: Pillar `play PAIR 5 6 7 4 3` est 880 vs low fillers `5 6 8 7 3` est 1760.
- `advise` at The Hook (QQ 33 held, Shoot the Moon owned) said `disc 1 2 3 4 5`, discarding both Queens (+26 mult held).
- Blind-select advice: "do not skip: Skip Tag not worth a shop visit" at ante 3 (it paid $10 after 2 skips and saved rent);
  "ante 5+: never skip" with an Orbital Tag for my main hand (+3 Pair levels).
- `shopadvise` scored Temperance 30 without computing the payout (+$11 for $3).
- est does not model The Hook (2 held cards dropped before scoring): est 18211 actual 19237; held-card jokers swing both ways.
- Rare Tag at ante 2 produced DNA {PERISHABLE,RENTAL}: the tag's "free Rare" can be sticker junk at Gold; advise still rated
  the skip as joker-paying.
- Bridge: one `NOT LEGAL NOW: SELECT_BLIND is not available in SHOP` right after `endshop` printed BLIND_SELECT (state lag);
  re-run after 2s worked. Otherwise no failures.
