# Run N6ILXWVS (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (39037/60000)

Ante 1 (Juggle/Charm/The Psychic 600, $4): Small: disc, Straight Q-8 308 one-shot. Shop $6: Buffoon -> Half Joker{E} (passed perishable Photograph, advisor's pick). Big: disc, Pair KK 660. Shop $8: Buffoon -> Campfire{P} (sell $4; Burglar{E,R} barred), Crafty{P,R} $1. Psychic: sold Crafty mid-round (Campfire x1.25), Straight 325 + disc + Flush 395.
Ante 2 (Garbage/Buffoon/The Needle 1000, $10): Mercury (Pair L2) + Joker $2. Small: Pair 99 1161. Shop $8: Sly $3, sold Campfire $4 -> Jolly $3. SKIPPED Big for Buffoon tag (override of `b blind`): Mega Buffoon -> Delayed Gratification + The Tribe. Needle: Trips 999 3745 one hand.
Ante 3 (Skip/Ethereal/The Tooth 6400, $16): Mega Celestial $8 -> Mercury (Pair L3) + Earth. SKIPPED Small for Skip tag (+$10). Big: disc, Pair 33 3456 + JJ 3960. Shop $26: 1 reroll, Strength $3 (rescue). Tooth: Pair 44 3528 + 88 3816 (2-card plays).
Ante 4 (Garbage/Juggle/The Window 18000, $26): EMERGENCY 0.24: 2 rerolls, sold Tribe -> foil Mail-In Rebate{P} $6 (+50 chips), sold Delayed Grat -> Scholar $4. Small: Pair 99 5688, disc AA+A for Mail-In +$15, Pair TT 5760. Shop $32: reroll, Mercury (Pair L4), reroll. Big: QQ 6475 + 22 5883 + KK. Shop $25: reroll, sold Joker -> Abstract{ETERNAL,RENTAL} $1 (override: +18 mult, ratio 0.77->0.92). Window: QQ 8925 + 99 8823 + 33 8211.
Ante 5 (Buffoon/Skip/The Mouth 50000, $25): EMERGENCY 0.15: reroll, sold Scholar -> Supernova{RENTAL} $1 (+14 mult, 2nd rental), reroll, sold Mail-In -> Blue Joker{P} $5. SKIPPED Small for Buffoon tag (override): Mega Buffoon had no xMult; sold Jolly -> foil Ceremonial Dagger (rightmost, +50 chips). Big: 77 14906 + 33 14337 + 88 14820. Shop $13: Empress $3, reroll (Photograph/Troubadour). Mouth: no pair dealt (solver p 0.00) -> Strength KS->A, JS->Q, Empress on AA: Mult AA 18285 + QQ 16058 + 99 15939 = 50282/50000 (no discards to keep Blue Joker chips).
Ante 6 (D6/Orbital/The Serpent 120000, $4): rent-broke, no buy. Small 60000: QQ 16832 + 88 16445 + High AC 5760 = 39037. Solver called it UNWINNABLE from the first hand (3 pairs max ~51k). GAME OVER.

## Post-mortem

Binding constraint: scaling. ZERO xMult the whole run. xMult offers seen: perishable Photograph (ante 1, $6), eternal-rental
Tribe, The Tribe (flush, took it from Mega Buffoon and sold it), The Order{ETERNAL} (straight), Bloodstone (ante 3), eternal
Campfire (ante 4), Photograph (ante 5). No r/g pair-compatible xMult in 13 shop views + 7 rerolls + 4 Buffoon packs (10 jokers).
The flat Pair build (Pair L4, Half Joker, Sly, Abstract, Supernova, Blue, foil Dagger) topped at ~16-18k per hand at ante 5-6,
exactly the "flat build tops ~10-15k at a5" cap; ante 6 Small (60000) needs 20k/hand.

Decisions I would change:
1. Ante 3 Mega Celestial $8 (Mercury + Earth). Earth (FH) was never played; that $8 + the $5 reroll was ~2 more joker views.
2. Ante 4: three rerolls + one at ante 5 ($24 total) and two rentals (Abstract eternal, Supernova): the rentals bought
   ~+50% score and got me through the Window and the Mouth (by 282), but left me rent-broke ($4, -$6/round) for the ante-6
   shops where an xMult was the only way forward. With 0 xMult at ante 5 the run was dead either way; the rentals bought one ante.
3. Ante 1 shop: took Buffoon pack over perishable Photograph (advisor's pick); the pack gave eternal Half Joker, which
   carried every ante (+20 mult on 2-3 card plays) and was a good outcome.

Reusable rules (if-then):
- IF The Mouth (or any boss) deals no pair AND you hold Strength, THEN use it on 2 singles one rank below other singles
  (KS->A next to AD, JS->Q next to QC) to make TWO pairs at once, then Empress on the first pair; solver p went 0.00 -> 0.84.
- IF you own Blue Joker AND the cards in hand already clear, THEN do not discard: every card drawn costs 2 chips on every
  later hand (Mouth cleared by 282 with zero discards).
- IF you own Mail-In Rebate AND the blind is already safe, THEN discard the round's rank (+$5 each) and dig with spare
  discards for more (ante 4 Small: +$15 from 3 Aces).
- IF Ceremonial Dagger is offered with an edition (foil/holo/poly), THEN keep it as the RIGHTMOST joker: it destroys nothing and
  the edition is a free flat bonus.
- IF a Buffoon tag is on the Small/Big blind and you own 0 xMult, THEN the skip (Mega Buffoon now, 4 jokers) is worth more
  than the blind's shop at ante 2-5 when your hand clears the next blind by 1.3x+ (done twice; no xMult in either, but 2 picks each).
- IF ante 5 starts with 0 xMult and ratio < 0.2, THEN expect ante 6 Small to be unwinnable (20k/hand) with flat jokers.

Advisor/CLI defects:
- shopadvise ante 4 SIM rated Scholar (+20 chips +4 mult per ACE) at P 0.67 vs 0.00 baseline (sell Delayed Grat): an
  Ace-only joker cannot move P(clear) that much; looks like SIM threshold noise.
- shopadvise kept ranking Arcana/Mega Arcana packs first (45) in EMERGENCY with a flat build, where Glass/Steel are card-phase
  and add little; the 2a CARD PHASE rule says they are not xMult sources.
- Ante 5 blind select: `ADVICE: b blind` "ante 5+: the shop is worth more than a tag" even for a Buffoon tag (Mega Buffoon now)
  with 0 xMult; the Small shop offers 2 jokers, the tag 4.
- My own error: two b.sh commands sent in one tool batch (sell then buy) -> the buy read stale state and was refused
  ("NOT LEGAL NOW", nothing sent). No harm, but the CLI could serialize per port.
