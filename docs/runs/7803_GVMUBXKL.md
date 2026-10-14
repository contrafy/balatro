# Run GVMUBXKL (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Eye (38993/50000)

Ante 1 (Rare/Foil/The Head 600, $4): Small: disc to straight draw, Trips JJJ 180 + FH QQQKK. Shop $5: Buffoon -> Raised Fist{E} (over Egg{P,R}). Big: Pair 44 396 + Pair KK. Shop $6: Mystic Summit $5. Head: disc 5, Trips JJJ + low fillers 1150 one-shot.
Ante 2 (D6/Charm/The Mark 2000, $8): Arrowhead $7 (SIM +0.31). Small: club Flush 1104 one-shot. Shop $3: passed Blue Joker{R}. Big: Pair JJ held AAA 1920 one-shot. Shop $9: passed foil Runner $7. Mark: 4 face-downs pair 1110 + FH AAATT.
Ante 3 (Orbital/Economy/The Needle 3200, $16): Jumbo Celestial -> Uranus (no Mercury). Small: 2P 8844 3772 one-shot. Shop $14: Celestial -> Uranus (TP L3). Skipped Big for Economy ($10 -> $20). Needle: 2 discards (Summit), 2P JJTT + 4D kicker 7000.
Ante 4 (Uncommon/Voucher/The Club 18000, $29): EMERGENCY 0.25, 0 xMult. Reroll x2 ($11): Jolly{P} $3. Small 9000: 2 disc, 2P QQ88 6860 + 2P AA77 5402. Shop $19: Ice Cream{P,R} $1 (only rental), reroll -> Abstract{P} $4 (passed Photograph). Big 13500: 2 disc, Straight 2-6 10750 + Pair 88 10773. Shop $12: Buffoon -> Odd Todd (sold perishing Jolly). Club: 2 disc (overrode advise breaking QQ99 for a straight), 2P QQ99 19950 one-shot.
Ante 5 (Charm/Meteor/The Eye 50000, $14): EMERGENCY 0.15. Reroll $5 (Popcorn{R}/Saturn). Small 25000: 2 disc, 2P 7755 19551 + Trips QQQ 9880. Shop $8: Jumbo Celestial -> Mercury. Skipped Big (37500 ~ round est, shop unaffordable) for Meteor: Mercury + Saturn. Eye: no made hand in 8 cards, 2 discards for a spade flush (missed), Pair 55 13509 + 2P AAJJ 17034 + Trips 888 8450 = 38993/50000.

## Post-mortem

Binding constraint: scaling. Zero reliable/growth xMult was offered in 13 shop views + 2 Buffoon packs (only
Photograph, a card-phase x2 on a no-face build). The engine was purely additive: Raised Fist (+2x lowest held rank,
~+16-24), Mystic Summit (+15 at 0 discards), Abstract (+18), Arrowhead/Odd Todd/Ice Cream chips. That tops out at
~15-20k per hand at ante 5, exactly the "0 xMult tops out ~10-20k" cap in GOLD_ANALYSIS. The Eye then forbids
repeating Two Pair, so the 3 hands were Pair/Two Pair/Trips at 13.5k/17k/8.5k (est matched actual exactly).

Decisions I would change:
1. Ante 3: two Celestial packs ($10) for two Uranus levels. Two Pair L3 added maybe +10%; the same $10 kept would have
   funded 2 rerolls at ante 4 with money left for a $6-8 xMult. With Raised Fist + Summit (mult ~40-55), a level's
   +1 mult/+20 chips is worth little.
2. Ante 4 shop 1: two rerolls ($11) bought only Jolly{P}. With 3 empty slots, a $4 Buffoon/any flat joker would have
   come anyway; the rerolls were the right idea but $29 is too little to hunt at Gold (expected ~$91 per r/g xMult).
3. Ante 5 shop 2: Jumbo Celestial $6 (Mercury) left $2. Irrelevant to the outcome (the Eye needed +11k).

Reusable rules (if-then):
- IF you own Raised Fist, THEN play your low cards as fillers and keep high cards held (it doubles the LOWEST held
  rank): Pair 44 + low fillers with A/K/T held scored 396 at ante 1; the CLI's rule pick sometimes discards held
  K/Q (it ignores Fist) while the solver keeps them: prefer the solver line.
- IF you own Mystic Summit, THEN spend both discards before the first play whenever the made hand survives them
  (Two Pair 2800 -> 5400 at The Needle, 6460 -> 10750 for a Straight); it pairs naturally with Raised Fist (discard low).
- IF The Eye is the ante-5 boss and you own 0 xMult, THEN the boss needs boss/3 from your 2nd and 3rd best TYPES, not
  your best hand: a Two-Pair engine at ~17k cannot clear 50000 (Pair 13.5k + 2P 17k + Trips 8.5k). Skip the Big for
  a pays-now tag (Meteor/Economy) rather than fight a ~1.0x Big when the next shop cannot afford an xMult anyway.
- IF the ante-3 Big has an Economy tag and your best hand is >= boss/2, THEN skipping it is ~money-neutral vs playing
  it ($10 doubled to $20 vs $5 + interest) and removes one blind fight; it costs one shop view.
- IF your build is 0 xMult at the first ante-3 shop, THEN keep money for joker views (Buffoon packs, rerolls with
  $20+), not Celestial packs: levels cannot close a 2-3x gap (score check stayed 0.15-0.30 after 4 levels).

Advisor/CLI defects:
- `advise` rule pick at The Club (ante 4) said `disc 7 2 8` = break made Two Pair QQ99 (est 9200 floor) for a 4-out
  open straight, with all solver lines tied at p >= 0.99; I kept the Two Pair and it cleared 18000 in one hand
  (19950). The rule should not break a made Two Pair when the solver shows no gain.
- `advise` rule picks discarded high held cards (KH QH at ante 5 Small; QH JH at ante 4 Big) with Raised Fist owned;
  the solver's best kept them. The rule's discard choice should model Raised Fist's held-card mult.
- Pack pick message "Uranus levels Two Pair (NOT your main hand Pair)" while SIM chose Uranus and Two Pair was the
  hand I played most from then on; main-hand detection lagged (shopadvise switched to Two Pair only at ante 5).
- shopadvise ante 4/5 SIM said "P(clear next 3 blinds) 0.04 / 0.00" while the actual next blinds were cleared with
  margin (Small 9000 one-shot-ish, Big 13500 with 21.5k, Club 18000 one-shot): the SIM looked very pessimistic for
  a Raised Fist + Mystic Summit build (it may not model Fist's held card choice or Summit's discard timing).
