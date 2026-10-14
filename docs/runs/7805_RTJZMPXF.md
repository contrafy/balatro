# Run RTJZMPXF (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Water (4194/6400)

Ante 1 (Foil/Polychrome/The Club 600, $4): Small: disc x2 around 2P QQ66 (overrode solver's 3-flush draw, margin 0.07 < 0.10) -> FH 666QQ 312 one-shot. Shop $6: Jolly $3 (SIM 0.96 vs 0.01). Big 450: Pair AA 320 + 2P JJ99 580. Shop $8: Crazy{PERISH} $4 (SIM +0.13; passed Satellite{E}). Club: 2P 4422 280 (no filler, kept JT98 draw) + Straight J-7 896.
Ante 2 (Juggle/Juggle/The Arm 2000, $10): EMERGENCY 0.28 -> Walkie Talkie{RENTAL} $1 (SIM +0.26), ratio 0.56 after. Small 1000: disc, Straight J-7 1680. Shop $9: passed Celestial packs (+0.09, Arm strips levels). Big 1500: 2P JJ77 540, disc, 2P KK55 500, Pair 44 684. Shop $11: Splash $3 (passed Tribe{RENTAL}, flush-only). Arm: disc, Pair 77 + TH 4C JH 1224 (Splash), Straight 6-2 1200 (all L1, Arm-immune).
Ante 3 (Investment/Handy/The Water 6400, $12): EMERGENCY 0.20, TIGHT. Reroll $5 (Fortune Teller{P}/Tower), Celestial -> Saturn (Straight L2; no pair planet offered). $3 + rental = rent-broke: skipped Small (Investment) and Big (Handy +$11; Crazy kept alive for its last round). Water (0 discards): 2P 4422+6S 1044, 2P AAQQ 620, Straight T-6 2530 = 4194/6400. GAME OVER with $14 unspent.

## Post-mortem

Binding constraint: SCALING. 8 shop views (incl. 1 reroll) offered zero reliable/growth xMult (the only xMult was The Tribe{RENTAL},
flush-gated) and only one Buffoon pack (ante 1, when $6 had to buy the first scorer). Build at death: Jolly + Walkie{RENTAL} +
Splash + perishing Crazy, L1 pair hands ~1.0-1.2k, Straight L2 ~2.5k with Crazy. The Water needs 2133/hand with no discards.
Money never exceeded $14: Small $0 + Walkie rent -$3/round left $8-12 per shop, which buys one $4 item plus maybe a reroll.

Decisions I would change:
1. Ante 3 blind select: skipping BOTH Small and Big sent a ~1.2k/hand build into a 0-discard 6400 boss with no shop in between
   (solver p 0.04 on the first hand). The Handy tag paid $11 that I died holding. Playing the Big (4800 with 2 discards per round,
   3 hands) was also unlikely (~1/3), but a won Big gives a shop with ~$20 (Handy-less) before the Water. Rule below.
2. Ante 2 Small shop ($9, ratio 0.56): left with $9 to keep the floor. With TIGHT/0.56 the floor was OFF per 2b step 2; a Jumbo
   Celestial (Pair/Two Pair level) or a $5 reroll for a joker view was the only way to move the ratio. Keeping $9 bought nothing later.
3. Ante 1: Crazy{PERISH} (straight-only) did win the Club and ante-2 Small, but it made the advisor call Straight my main hand and
   steered the ante-3 pack to Saturn. Fine as a bridge; do not let its plays define the main hand.

Reusable rules (if-then):
- IF the boss is The Water (0 discards) AND your typical hand (`hands` best est on a random deal) is < 0.5x boss/3, THEN do not skip
  the Big into it: the Big's shop is the last chance to add score, and skip-tag money (Handy/Investment) cannot be spent before
  the boss. Skip both only when the boss is beatable without a shop (est >= 0.8x boss/3).
- IF you own Splash, THEN play 5 cards on every Pair/Two Pair (fillers' chips score: Pair 77 + T 4 J = 1224 vs 240 bare) and
  prefer 10s/4s as fillers with Walkie Talkie (+10 chips +4 mult each).
- IF the ante-3 first shop shows ratio <= 0.25 with 0 xMult and <= $12, THEN the run is ~85% dead regardless; spend on the item
  with the biggest immediate score (a joker view via reroll beats a Celestial gamble that may not contain your main planet).
- IF a Celestial pack offers no pair-family planet, THEN take the planet of the type you actually make most often (Saturn here
  turned the last hand into 2530), but don't pay $4 for a pack expecting Mercury/Uranus (38%).

Advisor/CLI defects:
- SCORE CHECK stayed "~1188" before and after buying Splash (ante-2 Big shop with Walkie: 1188; ante-3 shop with Walkie + Splash:
  1188), although Splash hands scored 1224 (Pair 77 + 3 fillers) vs 684 for the same Pair without it: Splash is not modelled there.
- `advise` during a Celestial PACK_OPENING: "advise only works while selecting a hand" (playbook says pack advise ranks picks;
  maybe only Buffoon packs).
- Ante-1 Small: SOLVER advised breaking a made 2P QQ66 for a 3-card spade flush draw (p 0.98 vs 0.91 for the rule pick); the
  rule pick then made FH 666QQ. The margin rule (<0.10) should be applied inside the ADVICE line, not left to the player.
- Blind-select ADVICE recommended the ante-3 Small skip (rent-broke, correct) but said nothing about the Big; the 2b rule
  "skip both ... a perishable carries the boss" made me skip the Big into The Water without a check of boss beatability.
Bridge issues: none (46 steps, no ACTION REJECTED, no NOT LEGAL).
