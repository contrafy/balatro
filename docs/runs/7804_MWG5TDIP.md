# Run MWG5TDIP (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Wheel (543/2000)

Ante 1 (Charm/Boss/The Head 600, $4): Small: Straight T-6 280 + Pair 55 40. Shop $5: Arrowhead{P} $7 / Delayed Grat{P}; Buffoon $4 -> Odd Todd{RENTAL} (over Dusk{ETERNAL}, SIM 0.57 vs 0.18). Big: wheel Straight A-5 one-shot 592. Shop $4: Credit Card $1, Uranus, Jumbo Arcana, Celestial; left (advice LEAVE). Head: disc to JJ999, FH 520 + Straight 7-3 448.
Ante 2 (Ethereal/Top-up/The Wheel 2000, $7): shop EMERGENCY 0.19: Wily{P} $4 (advice BUY), Bull{E,R}, Spectral $4, Mega Arcana $8; overrode Wily (chips-only, Trips-gated, SIM +0.05 noise) and left with $7. Small 1000: broke QQJJ (solver 0.61 vs 0.52), 5533 dig, High dig, FH 55533 864 + 2P AA88 -> cleared. Shop $4 (rent ate it): Blackboard $6 / Riff-raff $6 unaffordable. Skipped Big (1500 vs projected 992) for Top-up: To Do List + Faceless Joker (both economy, 0 score). Wheel: dug for a spade flush/straight flush, Flush 436 + Pair 60 = 543/2000. GAME OVER.

## Post-mortem

Binding constraint: no mult. In 5 views (4 shops + 1 Buffoon pack) the only +mult/xMult offer was Blackboard $6 when I had
$4. The only scorer was a chips-only RENTAL Odd Todd: Gold Small Blinds pay $0 and its -$3 rent turned each cash-out into
$+0..3, so I never had more than $7 in a shop. Base-mult L1 hands (Pair x2, FH x4) plus +31 chips per odd card cap at
~450-860 per hand; 2000 at the ante-2 boss needs ~670 per hand on every hand.

Decisions I would change:
1. Ante 1 shop 2 ($4): buy Credit Card $1. With Gold rent and $0 Small Blinds the wallet never recovers; Credit Card
   (-$20) would have bought Blackboard $6 (x3 conditional, the only multiplier I saw) in the ante-2 Small shop, or a
   reroll in the ante-2 EMERGENCY shop. SIM said -0.02 (noise) because it does not model later-shop affordability.
2. Ante 2 shop 1 ($7, EMERGENCY 0.19): either buy Wily{P} or a reroll; leaving with $7 bought nothing because rent took
   $3 and the next shop had $4. Money held in EMERGENCY with a rental draining it is worth less than its face value.
3. Skipping the Big for Top-up was a coin flip on Common jokers; it produced two economy jokers. It did avoid a 0.66x
   Big blind; I still think it was right given the 2000 boss needed new jokers either way, but it is high variance.

Reusable rules (if-then):
- IF ante 1, you own a chips-only rental as your only scorer AND a $1 Credit Card is offered, THEN buy it: rent plus
  $0 Small Blinds keep you at $4-7, and the -$20 line is what lets you buy the first $6 multiplier at ante 2.
- IF EMERGENCY (ratio < 0.35) AND you pay rent AND the shop has any scorer or reroll you can afford, THEN spend now: the
  next shop will have less money (rent), not more.
- IF you skip a Big for Top-up, THEN count on ~half the Commons being non-scorers (To Do List, Faceless, Credit Card,
  Delayed Grat...): only skip when the Big is lost anyway (< 0.7x projected) or you already have 2 scorers.

Advisor/CLI defects:
- shopadvise LEAVE on Credit Card $1 at ante 1 with a rental scorer and $4 (SIM -0.02): SIM only looks 3 blinds ahead and
  never values the debt line for buying the next shop's multiplier.
- `s` at the ante-2 Big ("never skip the Big") does not weigh a Top-up tag against a 0.66x projected Big; the BOSS WARNING
  line (~1188 vs 2000) and the shop TIGHT line (992 vs 1500) give different round projections for the same build.
