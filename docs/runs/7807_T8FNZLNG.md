# Run T8FNZLNG (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Big Blind (61757/90000)

Ante 1 (Polychrome/Voucher/The Hook 600, $4): Small: 2 discards to Straight A-T 324. Shop $6: Buffoon -> Abstract{ETERNAL} (over Flower Pot). Big: 2P QQ22 220, dig High T, heart Flush 525. Shop: Seltzer{RENTAL} $1 (SIM 0.98 vs 0.11). Hook: FH 888KK 1280 one-shot.
Ante 2 (Boss/Economy/The Manacle->Needle 1000, $9): Mystic Summit{PERISH} $5 (SIM 1.00 vs 0.51), passed Celestial ($4->$0 with rent). Skipped Small (rent-broke; Boss Tag rerolled Manacle -> Needle). Big 1500: burn 2 discards, FH 444KK 2912. Shop: passed Tribe $8 (flush). Needle: burn 2 discards, 2P JJ77 2288.
Ante 3 (Investment/Orbital/The Eye 6400, $9): Jumbo Buffoon $6 -> Blue Joker (passed eternal-rental Photograph). Skipped Small (Investment). Big 4800: FH 888AA 6572. Eye: disc 2, Straight K-9 6510 one-shot (Summit on).
Ante 4 (Boss/Garbage/The Club 18000, $35 with Investment): 3 rerolls, Joker{ETERNAL} $2 (+4, +3 Abstract), Spectral -> Immolate (+$20; overrode Aura). Small 9000: burn 2 discards (Summit's last round), FH 333AA 6232 + 2P TT66. Summit perished. Shop: The Order{ETERNAL} $8 (EMERGENCY 0.24, only xMult seen), reroll. Big 13500: discarded into 8765, dig High J, hit 9: junk High 1771 first then Straight 9-5 11388 (would have cleared alone by 311). Shop: Hermit ($26 -> $46), Saturn, 3 rerolls (nothing), Greedy{PERISH,RENTAL} $1, Jumbo Celestial -> Saturn (Straight L3). Club: disc 4 keep 7S6S5S4S, hit 3H: junk High A 1978 then Straight 7-3 17184.
Ante 5 (Economy/Economy/The Mouth 50000, $24): sold perished Summit, holo Lusty{PERISH} $8, Celestial -> Venus (no Saturn). Straight with Order now ~30k, every ante-5 blind is "make a Straight or die"; skipped Small AND Big (2 Economy tags: $14 -> $56).
Mouth 50000: 2 discards into K-Q-J-T-9 33210 (locks Straight), drew 7-6-5-4-3 26163 -> 59373. $64.
Ante 6 (Coupon/Double/The Head 120000, $64): Telescope $10, Celestial -> Saturn (Straight L4), Buffoon skipped (Shoot the Moon/Wee), sold Greedy -> Juggler{PERISH} (hand 9), 3 rerolls (Blackboard{E}, Seltzer rental, nothing). Small 60000: Straight J-7 32400, 2 discards, Straight 7-3 29223. Shop $31: 2 rerolls, High Priestess -> Mars+Pluto (sold). Big 90000: 2 discards into 7-6-5-4-3 31365, wheel A-5 28080, last hand Q-T-9-8 + 5-4-3-2 (no straight), Pair 9 2312 -> 61757/90000. LOST.

## Post-mortem

Binding constraint: SCALING (no reliable xMult ever offered at a price/slot I could use). Every shop from ante 4 on was
EMERGENCY (ratio 0.11-0.47). The only xMult seen in 25 shop views: Tribe $8 (ante 2, $7), eternal-rental Photograph
(twice), perishable Photograph, The Order{ETERNAL} (bought), Blackboard{ETERNAL}. The Order turned the run into "make one
Straight per ~30k of requirement": it carried Big 13500, Club, Mouth (2 straights), ante-6 Small (2 straights) and 2 of
the 3 needed at the ante-6 Big. A per-hand straight of ~30-34k cannot reach 90k/120k blinds in 3 hands.

Decisions I would change:
1. Ante 5: I skipped Small AND Big for two Economy tags ($14 -> $56). The money bought only Telescope + 1 Saturn +
   Juggler + 3 empty rerolls. Two extra shops (with ~$20 each) would have shown ~6 more jokers, which was the real
   bottleneck. Skipping was right for blind risk (each blind = one straight), but it starved the build of shop VIEWS.
2. Ante 4 Spectral: Immolate (+$20) over Aura. The $20 funded rerolls that found nothing; neutral-to-fine.
3. Ante 6: Telescope ($10) for one guaranteed Saturn; only 1 Celestial pack appeared afterwards. At ante 6 a voucher
   that pays off per pack is too slow.

Reusable rules (if-then):
- IF your only xMult is The Order (Straight-gated), THEN every round is "find N straights": with an 8-9 card hand and
  2 discards you find 1 straight in ~75% of rounds, 2 in ~50%, 3 in ~15-20%. Plan blinds so each needs <= 2 straights
  (one straight ~= 30k at Straight L4 with ~50 flat mult); at ante 6 Big (90k) that is already 3.
- IF a straight would clear the blind by < 5%, THEN play spare junk cards first as a High Card (they score ~2k and
  draw nothing you need) and keep the straight for the next hand: twice this saved a 200-300 point shortfall.
- IF you own Mystic Summit, THEN burn both discards with 1-card discards (2 cards max) before playing; it doubled every
  ante-2/3 hand (FH 2912, 2P 2288, Straight 6510 vs 3392).
- IF Abstract Joker is owned and a joker perished, THEN keep the perished joker until you need the slot: it still
  counts for Abstract's +3.
- IF The Hermit is in the shop and you hold $20+, THEN buy-use it before anything else (+$20 for $3).
- IF Seltzer (rental) is the cheap ante-1 scorer, THEN it is fine: it self-destructs after 10 hands, so the rent is
  capped at ~3 rounds ($9).

Advisor/CLI defects:
- shopadvise SIM printed p_next 0.00 baseline vs 0.38 for Crafty Joker (flush-only) before The Eye (ante 3), which I
  then cleared in one hand (Straight 6510); and 0.00 baseline before the ante-4 Big that I cleared. The SIM's baseline
  seems to ignore Mystic Summit's +15 or the Eye's type rotation.
- advise SOLVER p values are badly overconfident on draws: ">=0.99 calibrated" for 2-discard straight draws repeatedly
  (ante 1 Small, ante 4 Big "p 0.99" on a gutshot dig), and "p 0.98" on the ante-6 Small with 2 hands left needing a
  4-out straight draw. Real odds were 50-70%.
- shopadvise SELL FIRST kept recommending selling the perished Mystic Summit although it still fed Abstract Joker +3.
- Score check (75th pct of 40 deals) ignores Straight/Order: it read 4810-8325 while every round actually scored a
  30k straight; ratios looked like 0.11 while the build cleared 60k. It undervalues conditional-xMult hands.
- pack advise ranked Aura over Immolate at $18 with 0 xMult; with an edition landing on one card it is ~1 hand in 8.
Bridge issues: one NOT LEGAL when I sent `blind` in parallel with `endshop` (my error, nothing sent). No rejects.
