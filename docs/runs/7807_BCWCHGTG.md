# Run BCWCHGTG (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Head (3978/18000)

Ante 1 (Charm/Voucher/The Pillar 600, $4): Small: disc 5 keep AA+QH, Straight A-T 324 one-shot. Shop $6: Buffoon -> Joker{RENTAL} (vs perishable Business Card). Big: heart Flush 616 one-shot. Shop $5: Zany{PERISH} $4 (SIM 0.61 vs 0.22). Pillar: 2P KK88 276, 2P JJ77 264, Pair QQ 180 -> 720/600. $-2 after rent.
Ante 2 (Double/Orbital/The Mouth 2000, $3): EMERGENCY 0.19: sold Zany, Ice Cream $5 -> $0. Skipped Small (Double tag; $0 shop useless, saves rent). Big 1500: Trips 777 1057 + Pair KK 750. Shop $2: nothing affordable. Mouth: locked Pair, AA 732 + QQ 690 + 66 612 = 2034/2000.
Ante 3 (Meteor/Uncommon/The Eye 6400, $4): Jolly{PERISH} $3. Skipped Small for Meteor x2 (Double): Mercury, Venus, Uranus, Earth (all L2). Big 4800: 2P 6633 1995 + FH 222JJ 2898. Shop $3: sold Joker rental, Seeing Double{RENTAL} $1. Eye: Pair TT 2420, disc 5, 2P AAJJ 3124, Quads 8888 4410 -> 9954/6400.
Ante 4 (Standard/Uncommon/The Head 18000, $5): EMERGENCY 0.13, SIM tied everything at 0.52: Arcana $4 -> Magician (Lucky 2H 2D). $1: skipped Small (Standard pack skipped) and Big (one fight instead of two; post-Big shop would have had ~$4). Head: solver "UNWINNABLE" from the first deal; 2P AAKK 2442 + Straight 816 + Straight 720 = 3978/18000. GAME OVER.

## Post-mortem

Binding constraint: money from the first shop. The run never held more than $6 at any shop. Ante 1 Small pays $0, the
first Buffoon pack ($4 of $6) gave only a rental Joker (+4 mult, -$3/round) and every later shop opened at $1-5, so each
shop could buy at most one $3-5 item and interest was $0 for all 8 rounds. No scorer better than a perishable Jolly ever
became affordable; the only multiplier was a conditional rental (Seeing Double). Typical hand at ante 4 was ~2.4k
against 6k/hand needed: three bosses in a row were won by draws (Mouth exactly, Eye on a dealt Quad 8s), not by build.

Decisions I would change:
1. Ante 1 shop 1: Buffoon pack with $6 -> rental Joker. With $2 left and $3 rent per round, the rental ate every later
   shop: it cost $1 + 3 rounds x $3 = $10 for +4 mult. The perishable Business Card or skipping the pack, then buying
   the $4 Zany/Jolly in the next shop, would have kept interest alive. A rental at ante 1 needs $5+ left after it.
2. Ante 1 shop 2: Zany{PERISH} (+12 only on Trips) at $4 on SIM 0.61; I sold it one shop later for $2 to afford Ice
   Cream. A trips-only perishable is not a first scorer; the playbook's Pair-triggered rule (Jolly/Sly) was right.
3. Ante 4: the Arcana pack ($4 -> $1) changed nothing (Magician on 2s). With SIM tied, Egg ($4, +$3 sell value per round)
   or simply holding $5 for interest was the only thing that could have changed the ante-5 shop, had the boss been won.

Reusable rules (if-then):
- IF you are broke at the start of an ante (shop money < $4 after rent) AND your hands are well short of the Big Blind,
  THEN skip the Small (and consider the Big): the $0 Small shop buys nothing, while the skip saves $3 rent, a perish
  tick and decaying-joker hands. Here the Double -> Meteor x2 skip gave 4 free planets (Pair/Trips/2P/FH to L2) and won
  the ante-3 Big with FH 2898.
- IF a Double Tag is held, THEN the next skip tag is worth twice as much: skip a Small whose tag pays immediately (Meteor,
  Buffoon, Charm, Standard) even below the usual skip bar.
- IF you own Seeing Double, THEN pick which pair to play by suits: a pair containing a club plus a non-club card doubles
  the whole hand (TT club/spade 2420 vs ~1200 without).
- IF the money after a buy is under $3 at ante 1-2 AND you would own a rental, THEN do not buy: rent makes you negative
  and the next shop opens below the $3-4 a Jolly/Sly costs.

Advisor/CLI defects:
- shopadvise ante 3 shop 2: "(rule advice was: BUY Seeing Double)" but ADVICE LEAVE with the text "the rule pick changes
  survival by +0.12; nothing on offer raises it by more than 0.02" (SIM baseline p 0.00 vs Seeing Double 0.12). It
  rejected the only item that raised survival; the LEAVE wording contradicts its own numbers.
- shopadvise ante 4: SIM printed identical score ratio 0.52 for baseline, Egg and Fortune Teller, so it cannot rank
  econ vs nothing; packs are not simulated at all.
- `shopadvise` after a pack was opened from the shop printed "shopadvise only works in the shop" although the state was
  [SHOP] (one-off, right after `pick`).
- Blind select at ante 3 and 4 said "do not skip: your typical hand is under half this ante's boss" with $1 in hand. When
  the shop after the Small cannot afford anything, the skip only saves rent/decay; the rule should check money.
- Pack advise for an Arcana pack prints "No pack advice for this pack type".
Bridge issues: none.
