# Run AJGH6ECT (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (31657/37500)

Ante 1 (Foil/Boss/The Goad 600, $4): Small: 2P AA99 120 + 2P QQ77 108 + disc + 2P KKJJ 120 = 348. Shop $4: Even Steven $4. Big 450: disc, disc -> spade Flush 984 one-shot. Shop $6: Walkie Talkie{PERISH} $4. Goad: disc, Straight 4-8 1400 one-shot.
Ante 2 (Rare/Handy/The Wheel 2000, $9): Judgement $3 -> Crafty. Skipped Small for Rare tag. Big 1500: 2P AA22 460, disc, diamond Flush 2016. Shop $12: Rare tag = Campfire{ETERNAL} $0, Buffoon -> Shoot the Moon{RENTAL}. Wheel: disc, Straight K-9 1068, High TC w/ QQ held 875, Pair 77 672.
Ante 3 (Buffoon/Rare/The Mouth 6400, $11): Stencil{R} $1 bought+sold (Campfire +0.25), Greedy $5. Skipped Small (Buffoon -> Mega: sold Shoot the Moon, took Smeared{P,R}) and Big (Rare tag). Mouth: disc, disc, sold Walkie mid-round (Campfire x1.75), red Flush 7229 one-shot.
Ante 4 (Buffoon/Buffoon/The House 18000, $14): Rare tag = Brainstorm{P,R} $0 bought+sold, Hermit ($12->$24), reroll, Four Fingers{P,R} $1 bought+sold, Walkie $4, reroll, Celestial -> Jupiter. Skipped Small+Big (2 Mega Buffoons): sold Walkie, took+sold Scholar{R}, Certificate, Juggler -> Campfire x2.5; kept Mystic Summit{R}. House: disc 5 face-down, disc 5, black Flush 10375 + red Flush 19680.
Ante 5 (Coupon/D6/The Flint 50000, $14): Campfire reset to x1. Celestial -> Jupiter, reroll, Jupiter $3 (Flush L4), $2 left. Small 25000: disc, disc, red Flush 10244, sold Greedy + Even Steven mid-round (Campfire x1.5), black Flush 7837, red Flush 7762 = cleared. Shop $0 (rent ate Small pay): sold Mystic, Popcorn{R} $1. Big 37500: red Flush 10290, disc, red Flush 10710, black Flush 10657 = 31657. Solver: UNWINNABLE after hand 1 (max flush ~11k x 2 < 27210). GAME OVER.

## Post-mortem

Binding constraint: scaling. The only multiplier all run was Campfire{ETERNAL} (free from a Rare tag), which RESETS after
every boss, so each ante restarted at x1 and every +0.25 had to be paid for by selling something. I never saw a permanent
xMult in ~6 shop views + 3 Mega Buffoon packs (21 joker views). The scorers were flat and conditional (Even Steven, Walkie,
Crafty on flush, Greedy via Smeared), and the run lived on Smeared Joker{PERISH,RENTAL} turning every hand into a 2-colour
flush. By ante 5 a flush made ~10k at x1.75 against 12.5k/hand needed for the Big and ~17k/hand for The Flint (halved base).
Money was the second constraint: two rentals ($6/round) on a $0 Small payout took the wallet from $14 to $0 in one round.

Decisions I would change:
1. Ante 4: skipping BOTH Small and Big for two Mega Buffoons. It cleared The House comfortably (Campfire x2.5) but cost two
   shops and two paydays; the packs had no xMult, and all the Campfire value from selling evaporated at the boss. At ante 4
   with Campfire as the only multiplier, the shops (xMult hunt, money for ante 5) were worth more than the burst.
2. Ante 4: taking Mystic Summit{RENTAL} as a second rental. It paid at The House but its $3/round plus Smeared's left me at
   $0 after the ante-5 Small, unable to buy anything in the last shop before the Big.
3. Ante 5 first shop ($14): Celestial + reroll + Jupiter took me to $2. Flush levels could not close a 0.17 score check;
   keeping $10+ for interest and a $5-8 xMult/Swashbuckler-type scorer in the next shop would have been at least as good.
4. Ante 2-3: building around Flush (Crafty from Judgement, Greedy, Smeared) instead of pairs. It worked while Smeared lived,
   but every scorer was conditional and none scaled.

Reusable rules (if-then):
- IF Campfire is your only xMult, THEN it is a per-ante burst, not a scaling source: count it as x1 when planning the NEXT
  ante's Small/Big, and keep hunting a permanent xMult every shop. It reset to x1 at ante 5 and the build collapsed.
- IF you own Campfire and a joker slot is free, THEN buy every $0-1 RENTAL joker in the shop and sell it at once: +x0.25 for
  this ante at $0 net (done 4 times here: Stencil, Brainstorm, Four Fingers, Scholar). Keep a slot free for this.
- IF a Buffoon/Mega Buffoon pick is a $0 non-rental joker (Certificate $3 sell, Juggler $2 sell) and you own Campfire, THEN
  take it and sell it: +x0.25 and cash.
- IF you own Campfire and the current hand cannot use a joker (Greedy on a black flush, Even Steven on odd cards), THEN sell
  that joker mid-round BEFORE the play: the +0.25 multiplies this hand and the rest of the ante (ante-5 Small cleared this way).
- IF you hold two rentals at ante 5 on a $0 Small payout, THEN expect $0 after the Small: buy the next joker before the Small.
- IF the boss is The Flint and your hands are flat +mult/+chips on a leveled hand, THEN the boss needs ~2x your normal hand;
  if the Big's projected round is < 0.8x, the ante is lost: spend the ante's first shop on money and a non-level scorer.

Advisor/CLI defects:
- `s` at ante-3 Big blind select advised `skip` with text about "a free MEGA Buffoon pack opens right now" while the Big's tag
  was a Rare Tag (the reason text seems copied from the Small's Buffoon tag).
- Pack/shop SIM never models Campfire feeding: Brainstorm $0 / Four Fingers $1 rentals scored -35/-25 and LEAVE, although
  buy+sell = +x0.25 for free; pack advise said SKIP for Scholar/Certificate/Juggler that were +x0.25 each when sold.
- advise listed "flush draw 3/5" for AH 8H 2H while 7H was also held (Smeared hearts=diamonds counting looked inconsistent
  in the solver's keep descriptions).
