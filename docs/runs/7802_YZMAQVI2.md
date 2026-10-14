# Run YZMAQVI2 (port 7802, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind The Eye (110026/120000)

Ante 1 (Boss/Uncommon/The Pillar 600, $4): Small: disc, Straight A-T 324. Shop $6: Buffoon -> foil Constellation (over Midas{E}; overrode SIM pick Fortune Teller{PERISH,RENTAL}). Big: 2P 88 22 180, disc, FH 99977 524. Shop $7: Jumbo Celestial -> Saturn (SIM 0.44; no Mercury/Uranus). Pillar: FH TTTJJ 528 + Pair 44.
Ante 2 (Ethereal/Boss/The Mouth 2000, $7): EMERGENCY 0.16 -> Mystic Summit{PERISH} $5. Skipped Small (Ethereal -> Aura: foil 6S). Big: 2 disc, FH AAAJJ 2988 one-shot. Shop $8: nothing. Mouth: 2 disc, FH 555QQ 2612 one-shot.
Ante 3 (Garbage/Meteor/The Wheel 6400, $16): left shop. Small: 2 disc, FH QQQJJ 2926 + Pair 22. Shop $20: reroll, Abstract{PERISH} $4, Devious $4 (SIM 0.00 -> 0.26). Skipped Big (Meteor -> Saturn + Mercury, Constellation x1.3; also saved a Mystic perish tick; overrode `s`). Wheel: 2 disc, Pair KK 3705 + 2P 8866 3694.
Ante 4 (Double/Buffoon/The Plant 18000, $14): EMERGENCY 0.29: Crafty{E} $4 (SIM 0.00 -> 0.19), Jupiter $3 (Constellation x1.4). Skipped Small (Double) AND Big (Buffoon x2 = 2 Mega Buffoon packs; overrode `s`): Obelisk + sold Mystic for Popcorn. Plant: disc, 2P AA99 7392 (overrode FH 999AA: FH most played, resets Obelisk), 2P 9955 7683, Trips 777 9275.
Ante 5 (Juggle/Foil/The Hook 50000, $15): left shop (Space/Sock eternals). Small 25000: Trips 999 9976 + club Flush 24752. Shop $19: Buffoon -> Banner{E} (sold Popcorn; SIM preferred skip), Arcana -> Death (9D -> foil 6S). Big 37500: Pair 77 9637, disc, Straight 8-4 32928. Shop $20: 2 Celestial -> Mercury (Pair L3), Uranus (2P L2), Constellation x1.6. Hook: Pair QQ 15558, Flush C 29352, High AC 11491 (Obelisk x3.0). Abstract perished.
Ante 6 (D6/Investment/The Eye 120000, $19): sold perished Abstract; my only +mult left was hand base. Popcorn{RENTAL} $1, sold Devious -> Raised Fist{PERISH,RENTAL} $1 (SIM 0.32 -> 0.44), order +mult left (round est 84k -> 141k), Celestial -> Saturn (Straight L4). Small 60000: 2P AAJJ 36556 + High KH w/ low fillers 23842 (exact). Big 90000: High KS 17595, High KC 28262, disc, disc, hit T: Straight A-T 52598. Shop $13: Mega Celestial -> Saturn (L5) + Venus, Uranus (Constellation x2.0), $2. Eye (Obelisk 4.2, Pair/2P/FH all at count 5 = reset types): High AD 34927, disc 5 (no Q), disc 4 (no Q; overrode solver Pair 66 which resets Obelisk), junk High AS JC 5C scored 0 but drew QC (Obelisk unchanged), Straight A-T 75099 with 3D held (Raised Fist +6) vs 85073 needed. GAME OVER 110026/120000.

## Post-mortem

Binding constraint: FLAT MULT. From ante 5 the build was two growth xMults (foil Constellation x2.0, Obelisk x4.4 = x8.8)
on a mult column of hand base + Popcorn (decaying) + Raised Fist (perishable rental). Abstract{PERISH} carried the +mult
through ante 5 and died; two of six slots were Eternal chip jokers (Crafty, Banner) that never fired together with the
+mult. Every ante-6 hand was ~250 chips x ~35 mult x 8.8; The Eye needed ~40k a hand and I made 35k / 0 / 75k.

Decisions I would change:
1. Ante 4: Crafty{ETERNAL} $4 because SIM said 0.00 -> 0.19 (mostly +3 Abstract). It blocked a slot for the rest of the run
   and fired on 2 flushes. A conditional Eternal joker bought for a perishable's synergy is a permanent loss.
2. Ante 5: Banner{ETERNAL} over keeping Popcorn (SIM preferred skip; round SIM ratio fell 0.70 -> 0.57). Banner (+30 chips per
   unused discard) fights the discard-to-dig play that Straight/Flush need, and a second Eternal chip joker left room for
   only 2 +mult jokers. Should have skipped the pack.
3. Obelisk count management: Full House was played 5 times at antes 1-3 (it was the made hand), Pair and Two Pair reached 5
   by ante 6. With three types tied at the max, Pair/2P/FH all reset Obelisk, which left Straight/Flush/Trips/High as the
   only growth types: exactly what The Eye and a pair-heavy deck punish. From the moment Obelisk is bought, keep the
   max-count type alone at the top (spend High Card / Trips / Flush plays on the others) so the common types stay usable.
4. Ante 6 Big: the solver's High Card lines worked (52598 straight hit), but I entered The Eye with $2 after the Mega
   Celestial + Uranus; fine for that boss, but it meant no rescue tarot. A $3 shop Death/Strength would have fixed the 3D.

What worked: Ante 3 skip of Big for Meteor (free Mega Celestial: Constellation +0.2, and it saved a Mystic perish tick);
ante 4 double skip (Double tag on Small + Buffoon tag on Big = 2 Mega Buffoon packs -> Obelisk) with The Plant cleared
7392+7683+9275; Popcorn (+20, no sticker) replacing Mystic (1 round left) inside the pack.

Reusable rules (if-then):
- IF the Small tag is Double and the Big tag gives a pack (Buffoon/Meteor/Ethereal...), THEN skip both: you get two packs
  now, and perishables/rentals do not tick on skipped blinds.
- IF a boss makes a hand score 0 (The Eye repeat type, a debuffed hand), THEN Obelisk is neither grown nor reset by it
  (verified: x4.2 stayed x4.2 after a 0-score High Card under The Eye), but the type's play count still rises. Use a junk
  repeated type to cycle cards without touching Obelisk.
- IF you own Obelisk and Pair/Two Pair/Full House are tied at the max play count, THEN any of them resets it: the solver's
  "play the pair" can be a run-ender; compute the remaining need at x1 before following it.
- IF your only +mult jokers are perishable/decaying (Abstract, Popcorn, Mystic), THEN buy a permanent +mult joker before
  any chip joker or level: xMult jokers multiply the mult column, and an empty column makes x8.8 worth ~35x8.8.
- IF a joker is Eternal and conditional (Crafty, Banner, Runner...), THEN do not buy it at ante 3+ even when SIM likes it
  for a perishable's synergy (Abstract +3): it outlives the synergy by the whole run.
- IF you own Raised Fist on the last hand, THEN the held cards matter as much as the played ones: with no discards, a held
  3 cost 10k here (RF +6 instead of +16).

Advisor/CLI defects:
- `advise` at The Eye (Obelisk x4.2, Pair count tied at max) printed `SOLVER PLAY 5 6 7 8 p 0.82` for Pair 66 + fillers: that
  play resets Obelisk to x1, after which the last hand could make ~25k of the 72k needed. The solver does not carry the
  Obelisk reset into later hands.
- shopadvise ante 6 twice said `SELL FIRST` Popcorn / Raised Fist ("flat RENTAL and 3 non-rental scorers carry your hands")
  while they were the only +mult jokers; the 3 "scorers" were Crafty (flush-only chips), Banner (chips) and the two xMults.
  Chip-only and xMult jokers should not count as carrying a +mult-less hand.
- shopadvise ante 6 first view: `SCORE CHECK ... ~3563` (vs 15433 one shop earlier) right after Abstract perished; plausible
  but it flagged EMERGENCY with nothing to buy except rentals.
- Main hand label: "Full House" through ante 5 (FH was played 5 times at ante 1-3 as the made hand), "Straight" at ante 6;
  Mercury/Uranus picks printed "NOT your main hand".
- `s` at ante 3/4 blind select said "do not skip" for Meteor and for Double+Buffoon; both skips were the best moves of the run.
- SIM rated Crafty{ETERNAL} +0.19 and Devious +0.26 at antes 3-4 from Abstract's +3 alone, with no penalty for an Eternal
  conditional slot.
Bridge issues: none; 130 steps, no rejects.
