# Run UDRRTZQ9 (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Wall (2703/4000)

Ante 1 (Double/Polychrome/The Head 600, $4): Small jokerless: 2P AAQQ 124, disc, Trips 555 135, 2P KK77 -> cleared. Shop $4: Buffoon $4 (SIM 0.23 > perishable Sly 0.16) -> Droll{RENTAL} (SIM 0.60) over Runner. Big 450: 2 discards to diamonds, Flush AD-3D 1036 one-shot. Shop $3: left (Square{E,R}, 8 Ball{P}). Head (hearts debuffed): disc 5, disc 4 to clubs, Flush AC KC JC 9C 6C 1134 one-shot.
Ante 2 (Charm/Investment/The Wall 4000, $7): Shop $7: EMERGENCY 0.07, only Photograph{ETERNAL,RENTAL} $1 / Invisible $8: left with $7. Played Small 1000 (Charm = Mega Arcana, no joker): 2 discards + High Card dig -> Flush 952 + Trips KKK = cleared. Shop $4 (rent ate the interest): Celestial $4 for a 1/3 Jupiter -> Neptune/Pluto/Mercury, took Mercury. Big 1500: Flush 994 + spade Flush 1120. Shop $2: Joker $2 (+4 mult). Wall 4000: disc 5 to diamonds, disc 3, Flush AD QD JD 9D 8D 1494, dig for straight flush, spade Flush 1134 -> 2703/4000. GAME OVER.

## Post-mortem

Binding constraint: no scorer economy. In 5 shop views the only jokers offered were perishable Sly (chips only), eternal
rentals (Square, Photograph), 8 Ball, Invisible $8, Banner{P} $5 (unaffordable) and a $2 Joker. The single Buffoon pack
gave Droll{RENTAL} (+10 mult on Flush) - the only reason ante 1-2 Small/Big were cleared (every clear was a Droll flush,
1000-1500). But a flush engine tops at ~1500 per hand, and an ante-2 Wall (4000 = 2x) needs ~1350 on EVERY hand, i.e.
three flushes in three hands. Droll's rent (-$3 x 4 rounds = $12) on a $0-Small economy kept the wallet at $0-7, so no
reroll or $5 joker was ever affordable.

Decisions I would change:
1. Ante 2 first shop ($7, The Wall upcoming, EMERGENCY 0.07): I left to "keep $7 for the next shop". Under a rental and a
   $0 Small Blind, held money does not grow: $7 became $4 next shop (+$1 interest, -$3 rent, $0 blind pay). A $5 reroll
   (2 more joker views) or the $4 Arcana there was strictly better than holding; holding only bought nothing later.
2. Ante 2 second shop ($4): Celestial pack for a 1/3 Jupiter missed. Keeping the $4 would have given $6 at the Big shop
   ($2 Joker + $3 planet or a $5-6 joker). Small edge either way; the real error was #1.
3. Ante 1 first shop: Buffoon vs perishable Sly $3 was right by SIM, and Droll cleared 4 blinds; but a flush-only rental
   is a dead end against a 2x boss at ante 2. With The Wall known at ante 2's first shop, the plan had to be "joker
   views now", not "money floor".

Reusable rules (if-then):
- IF you hold a rental AND the next blind is the $0 Small, THEN money held in the shop shrinks (~-$2 per round): spend it
  on joker views (reroll/Buffoon/Arcana) when SCORE CHECK is EMERGENCY instead of carrying it.
- IF The Wall is the ante-2 boss AND your only scorer is a Flush/Straight-gated joker, THEN that engine cannot clear 4000
  (needs a 1350+ hand on all 3 hands): every ante-2 shop must buy any flat +mult/xMult joker or reroll for one; a level
  gamble (Celestial for Jupiter) does not close a 3x gap.
- IF you play flush-digging rounds with 2 discards, THEN discard non-suit cards even off a made flush when you need two
  flushes in the round (6 diamonds after the second discard), but one flush per round is the realistic ceiling.
- IF `advise` right after `blind` prints the BLIND_SELECT screen, THEN run it again; the select had already happened.

Advisor/CLI defects:
- `advise` run immediately after `blind` (twice: Head and ante-2 Big) printed the stale BLIND_SELECT state instead of the
  hand; the second call worked.
- SOLVER at ante-2 Small (n=100) proposed keeping QH TD 3H (mixed suits, p 0.94) over 3-diamond keeps; small-sample
  solver lines flip on noise and produce odd keeps.
- SCORE CHECK printed ~153 (75th pct) while the Droll flush engine actually scored 950-1500 per round; the deal-only
  estimate ignores discards, so it overstates EMERGENCY for dig-based builds (same as 7804_SL5MJZY1).
- Bridge issues: none (42 steps, no rejects).
