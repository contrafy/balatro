# Run BQVA4RPV (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Water (33004/50000)

Ante 1 (Boss/Foil/The Head 600, $4): Small: 2 discards to spade flush, 2 dig pairs, Flush 292 (368/300). Shop $4: Buffoon -> Scary Face (overrode rental Seeing Double at $0). Big: disc 4, Straight Q-8 548 one-shot. Shop $6: Green Joker{RENTAL} $1. Head: 2P 189 + 2P 132 + club Flush 707.
Ante 2 (Buffoon/Boss/The Manacle 2000, $7): sold Green, Joker{PERISH} $2 + Clever $4 ($2). Skipped Small (Buffoon -> Mega Buffoon: Popcorn + Stuntman{RENTAL}; hand size 6). Big: Pair AA 7332 one-shot (Stuntman +250 chips x ~25 mult). Shop $5: nothing. Manacle: Pair 99 6116 one-shot.
Ante 3 (Investment/Garbage/The Window 6400, $9): Buffoon $4 -> Shoot the Moon (Splash{E} other). Skipped Small (Investment). Big: Pair JJ 10540 one-shot. Shop $8: left (floor). Window: disc 4 (drew QC), Pair JJ + QC held 9180 one-shot. Cash $38.
Ante 4 (Rare/Double/The House 18000, $38): 2 rerolls (nothing), Spectral -> Medium (purple seal 2H), Grabber $10 (4 hands). Skipped Small for Rare Tag (override). Big 13500: 2P KK33 4360, disc purple 2H -> Judgement, Pair 22 2640, High K 5-card dig 2655, drew QC -> Pair 55 w/ Q held 6210. Popcorn/Joker expired; Judgement -> Blueprint (copies Stuntman: 590 chips). Shop: Rare Tag = The Family{E,RENTAL} (passed), Jumbo Celestial -> Mercury, 1 reroll. House: disc 5 face-down, disc 4, High K w/ QH held 7630, Pair 33 8496, Pair JJ 9680.
Ante 5 (Skip/Charm/The Water 50000, $9): EMERGENCY 0.21. Celestial -> Uranus (no Mercury). Small 25000: disc 4, disc 5 (drew QD), High J 7630 + Pair KK 9680 (Q held) + Pair AA w/ QQ held 15863 = 33173. Shop $3: sold Clever, Arcana (World/Lovers/Moon) skipped = wasted $4. Skipped Big for Charm -> Mega Arcana: Emperor (-> Judgement = Bloodstone, Temperance +$13), Lovers on 9S. Water (no discards, 4 hands): Pair TT 8720, High KH 7902, Pair AA 8752, High J 7630 -> 33004/50000. GAME OVER.

## Post-mortem

Binding constraint: scaling (mult). The build was all chips: Stuntman +250 copied by Blueprint, Scary +30/face (~600
chips per hand) on a mult of 3 (Pair L2). The only mult source was Shoot the Moon (+13 per Queen held), so a hand was
~1.8k without a Queen in the 6-card hand and ~7.6-9.7k with one. Popcorn (+20) and a perishable Joker (+4) carried
ante 2-3 and both expired at the ante-4 Big. Zero xMult was offered in 8 shop views + 4 rerolls; the Rare Tag gave
The Family{ETERNAL,RENTAL} (unusable). Ante 5 Water needed 12.5k avg per hand with no discards to dig for Queens.

Decisions I would change:
1. Ante 5 shop: sold Clever and bought an Arcana pack ($4) that offered only suit changers; keeping Clever and $5 changed
   nothing either, but an Arcana pack is not a Queen-maker unless Strength/Death AND a target land in the same pack.
2. Ante 4 first shop ($38): 2 rerolls + Spectral + Grabber spent $25 for +1 hand. Paint Brush/Grabber help, but the
   real missing piece was +mult; I should have kept $15+ for a +mult joker in the Big-blind shop (which had none, so
   [INFERENCE] the result is likely the same).
3. Ante 3: Stuntman's -2 hand size (6 cards) halved the odds of holding a Queen for Shoot the Moon. With a chips-heavy
   build, a mult joker should have been the priority from ante 3 (Popcorn's decay was visible: 20 -> 0 by ante 4).

Reusable rules (if-then):
- IF your mult comes from decaying/perishable jokers (Popcorn, perishable Joker, Ice Cream) THEN count the ante they
  expire in and treat the shop before it as EMERGENCY for +mult/xMult, not for chips or hand count.
- IF your chips are huge (Stuntman, Blueprint on Stuntman, ~600) and base mult is 2-3 THEN every +1 mult is worth ~+20-33%:
  main-hand planets and any flat +mult joker beat more chips; Bloodstone/xMult beat everything.
- IF Shoot the Moon is your only mult source THEN discard/dig to find a Queen first and HOLD it for every remaining
  hand (it scores while held; playing it wastes it). Play 4-5 card hands with fillers to dig while holding the Queen.
- IF a Rare/Uncommon tag joker turns out ETERNAL+RENTAL and off-type THEN leave it (The Family here); the tag is not
  guaranteed value, so do not skip a winnable blind's shop just for it when you need that shop.
- IF a purple-seal card is in hand and you have a discard to spare THEN discard it: it gave Judgement (-> Blueprint).
- IF Emperor/Mega Arcana gives Temperance THEN use it before the round end that pays interest.

Advisor/CLI defects:
- shopadvise run right after a `buy` printed the PRE-buy state (showed $8 and 1/6 jokers after buying Joker); a second
  run was correct. Also `shopadvise` straight after a pack pick said "only works in the shop" (state still settling).
- Pack advise ranked Seeing Double{RENTAL} over Scary Face at $0 (rent would take money negative before the first
  real shop).
- Solver p_clear looked overconfident early (Small ante 1 p 0.98 with no jokers; ante-5 Small p 0.84 with 1.8k hands) but
  was well calibrated at The Water (0.50 -> 0.39 -> 0.19, lost).
- `hands` lists HIGH CARD QD 545 while holding QD is the point (High J with Q held = 7630 not listed); Shoot the Moon
  hands should rank "play X, hold the Queens" options.
Bridge issues: none (one NOT LEGAL when I sent `blind` in parallel with `endshop`; my error).
