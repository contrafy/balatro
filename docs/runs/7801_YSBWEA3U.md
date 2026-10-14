# Run YSBWEA3U (port 7801, claude-fable-5-1) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (25219/37500)

Ante 1 (Uncommon/Voucher/The Manacle 600, $4): Small: disc to QJT9, Straight Q-8 308 one-shot. Shop $6: Ice Cream $5 (bridge, SIM 0.86 vs Buffoon 0.36). Big 450: Pair 33 232 + 2P AAQQ 314. Shop $6: Even Steven{ETERNAL} $4. Manacle: Pair TT 1200 one-shot.
Ante 2 (Holo/Economy/The Water 2000, $9): Jumbo Buffoon $6 -> Wrathful{PERISH 5} (free) over Jolly{RENTAL} (SIM 1.00 vs 0.93; refused rent on a $3 wallet). Skipped Small for Holo tag. Big 1500: 2P QQ99 715 + 2P 7766 1260. Holo shop: the free holo joker was Ride the Bus{ETERNAL,RENTAL} (SIM 0.97 vs 0.41) - passed (hard rule). Water: club Flush 8-6-5-4-2 (4 evens) 2700 one-shot.
Ante 3 (Garbage/Foil/The Psychic 6400, $16): EMERGENCY 0.32, no joker in shop: Jumbo Spectral $6 -> Wraith -> Driver's License (dead), $0. Skipped Small for Garbage Tag (+$6). Big 4800: 2P 8844 2394, disc odd FH, Pair AA dig 485, Straight 2-6 2420. Shop $11: Odd Todd $4, Juggler{PERISH} $4. Psychic: FH 88822 3690 + Straight 4-8 3784.
Ante 4 (Top-up/Double/The Flint 18000, $9): Mega Buffoon $8 (sold DL $3, Wrathful $2 in-pack) -> Fibonacci + Swashbuckler; sold Juggler -> Mystic Summit{PERISH,RENTAL} $1 (SIM 0.63 vs 0.31). Small 9000: 2 discards first (Summit), 2P 9988 8372 + High 3S 2765. Big 13500: 2P TT99 3255, disc, High 9H dig 2025, 2P 7755 8492 = 13772. Shop $6: sold Ice Cream -> Blue Joker $5. Flint: 2 discards, Pair AA 6837, club Flush 9204, Straight 5-9 10140 = 26233/18000.
Ante 5 (Standard/Boss/The Head 50000, $5): EMERGENCY 0.28, shop had Photograph (useless pre-joker x2 on faces) and Zany; left. Skipped Small 25000 (override: $0 reward, shop would hold $2; Summit 2 rounds kept for Big+Boss) -> Mega Standard: holo 6S + bonus 3C. Big 37500: disc KK, disc to 8833 w/ Summit 14688, High Q (misplayed: meant 5D 4025, got 2403), Flush 8128 = 25219/37500. GAME OVER, 87 steps.

## Post-mortem

Binding constraint: SCALING - zero xMult in 11 shop views + 3 packs across 5 antes, and money never above $16 (one time) so
no reroll hunt was possible. The build was a pure flat-add engine: Even Steven{E} (+4/even), Odd Todd (+31 chips/odd),
Fibonacci (+8 per A/2/3/5/8), Swashbuckler (+11), Blue Joker (+~75 chips), Mystic Summit (+15 at 0 discards). That tops out
at ~15k per hand (two pair 8833 with Summit 14688) at ante 5, i.e. 2x short of the 37500 Big (12.5k/hand sustained) and
3.5x short of the boss. The single xMult-shaped offer in the whole run was Photograph at ante 5 (worthless: it multiplies the
base mult before the +mult jokers), plus the Wraith gamble that returned Driver's License (x3 at 16 enhanced cards: 0 owned).
Money: $0 Small Blinds, $4/$5 for Big/Boss, and a rental from ante 4 meant every shop was entered with $5-11 and left at $0-7.

Decisions I would change:
1. Ante 3 Jumbo Spectral ($6) for the Wraith lottery. It cost the whole $16 wallet (Wraith sets money to $0) and returned a
   dead rare. The $16 was the only time this run could have afforded a $6-9 xMult in a later shop; two Celestials/one reroll
   with $8 kept would have been the disciplined line. Rule 7 of the Gold policy (no gambling while poor) applies to Wraith too.
2. Ante 2 holo shop: refusing holo Ride the Bus{ETERNAL,RENTAL} (SIM 0.97 vs 0.41) was the hard rule, and with Even Steven the
   build never scores faces, so Ride the Bus would have grown +1/hand all run (~+30 by ante 5 plus holo +10). At -$3/round it
   would have cost ~$45 over 15 rounds, roughly what I spent on Summit rent + Spectral + Juggler anyway. I still think the rule
   is right on average (7809/7801_QS3 died broke with rentals), but a holo growth joker on a build that never resets it is the
   exception worth coding: evaluate ETERNAL RENTAL by (growth per round x rounds left) vs rent, not by a flat ban.
3. Ante 5 Big hand 2: I played `HIGH 1 2 3 4 6` thinking the 5D (4025) would score; High Card scores the HIGHEST card (QC, 2403).
   Irrelevant to the outcome (needed 22.8k in 2 hands) but a real misplay: a dig must be played as the single best card.
4. Ante 4 shop 2: Blue Joker over keeping $6 was right (it was +80 chips vs a dying Ice Cream), but by then the run needed x2,
   not +80 chips. Every ante 3-5 shop offered only flat adds; the only fix was money in hand at ante 3 (see 1).

Reusable rules (if-then):
- IF Even Steven and Odd Todd are both owned THEN every non-face card scores (+4 mult or +31 chips) and faces (J/Q/K) score
  NOTHING: discard faces first, never keep KK/QQ pairs as "made hands" (KK pair est 1260 vs 55 pair est 4700 at ante 4).
- IF Fibonacci is added to Even Steven THEN 2s and 8s are worth +12 mult each: the ideal hand is 88822 / 8833 / 2-6 straights;
  `advise` found these but it is worth reading the ranks yourself (FH 88822 scored 3690 at ante 3 vs an odd-face FH 576).
- IF Mystic Summit is owned THEN spend both discards BEFORE the first play of every round unless a made hand already clears
  the blind: +15 mult is ~+25-35% on a flat build; it cleared the ante-4 Small (8372+2765) and Flint (6837+9204+10140).
- IF a dig (throwaway hand) is intended THEN play ONE card: High Card scores the highest-ranked card you include, so adding
  fillers with a face card turns a 4025 odd/Fib single into a 2403 Queen.
- IF the shop money after the next blind would be under $4 (rent due, $0 Small) THEN skip that Small for any tag: the shop
  cannot buy anything and the skip saves the rent and a perish tick (did this at ante 3 for Garbage +$6 and at ante 5).
- IF Wraith is offered while holding $10+ THEN count the money as part of its price: at ante 3 that $10-16 is the only reroll /
  xMult budget the run will ever have; take Wraith only with <$6 or a free slot plus a scorer already alive next ante.
- IF the only xMult offered is Photograph/Glass/Steel (card-phase multipliers) on a +mult joker build THEN it adds ~2-5%:
  `shopadvise` labels Photograph XMULT (84) but the SIM correctly rated it below baseline (0.66 vs 0.70); trust the SIM.
- IF ante 5 arrives with 0 xMult and <$10 THEN the run is lost with ~97%: the Big (37500) needs 12.5k/hand x3, and no flat build
  in these logs exceeded ~15k per hand. Spend ante 3-4 money ONLY on things that can become x2+ (Buffoon packs, rerolls at $20+).

Advisor/CLI defects:
- shopadvise ranked Photograph 84 XMULT at ante 5 on a build with zero face-card scorers; the SIM said -0.04. The rule score
  should treat card-trigger xMults (Photograph, Glass via Justice) as near-zero when the build's mult comes from +mult jokers.
- Pack `advise` (Mega Buffoon) rated Swashbuckler "+162% round est now" and the SIM 0.61, Misprint "+75%" and 0.67: the two
  numbers disagreed by rank; Swashbuckler's sell-value mult (11) was right in play (est exact: 8492/8492, 14688/14688).
- Spectral pack advise ranks Wraith 75 without pricing the money it destroys ($10 here); add "costs your $N" to the line and
  demote it when $ >= 8 at ante 3+.
- `advise` dig lines like "play QC TS 9H 7C 5D (High Card)" print the exp of the LINE but not that the Queen scores, so a reader
  who wants the 5D to score picks the wrong set; print "scores QC 2403" on multi-card High Card digs.
- `s` at ante 5 blind select said "do not skip: the shop after the Small is worth more than a tag" with $5, a $3 rental and a
  $0 Small reward (projected shop money $2); the skip advice should project the shop's cash.
- Standard-pack `advise` prints "No pack advice for this pack type" - it could at least rank enhanced/edition cards by the
  owned jokers (holo 6S was +14 mult for Even Steven, bonus 3C +69 chips/+8 for Odd Todd/Fibonacci).
Bridge issues: none; 87 steps, no rejects, no offline time.
