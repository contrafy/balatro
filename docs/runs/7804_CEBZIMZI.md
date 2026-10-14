# Run CEBZIMZI (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The Goad (1472/2000)

Ante 1 (Rare / Foil / The Club 600, $4): Small: disc to 4 spades, spade Flush 328 one-shot. Shop $6: overrode Supernova{RENTAL} $1 (advisor 125) for Buffoon $4 -> Zany{RENTAL} / 8 Ball{ETERNAL}, skipped both. Big 450: club Flush 308, dig High Card, diamond Flush 316 = 639. Shop $6: Jumbo Celestial $6 -> Jupiter (Flush L2), $0 left. Club: Two Pair AA22 dumping 3 debuffed clubs 66, diamond Flush 462, Broadway Straight 324 = 852.
Ante 2 (Coupon / Voucher / The Goad 2000, $5): Jolly{ETERNAL} $3. Skipped Small (1000, $0 payout, ~$4 shop) for Coupon. Big 1500: 2P AAKK 620 + 2P QQ99 580 + 2P JJ55 500 = 1700. Free shop: Jumbo Celestial -> Jupiter (Flush L3; no Uranus), Jumbo Standard -> Blue Seal 5S, Pluto and Delayed Gratification{RENTAL} taken and sold (+$2). Declined the advised $5 reroll ($8 -> $3). Goad (spades debuffed): solver 0.05 from the deal; disc 5 for hearts -> trips 444; disc 3 for FH missed; Trips 418 + Pair 150 + heart Flush 904 = 1472/2000. GAME OVER with $8 unspent.

## Post-mortem

Binding constraint: SCALING (one joker, Jolly +8, at the ante-2 boss). The boss needed ~670 per hand; my
made pair-family hands scored 150-620 and only an L3 flush (~900) beat the pace, so the round needed two flushes
under a suit debuff. Money was not the binding limit at the end: I died holding $8.

Decisions I would change:
1. Ante 2 free shop ($8, SCORE CHECK 0.24 = EMERGENCY, Goad TIGHT 0.78x): I declined the advised $5 reroll to keep
   interest. A reroll had perhaps 20-30% to show a $2-3 scorer (Joker/Jolly/Sly/Half), which turns the Goad from ~5%
   into a coin flip. Money saved for "the next shop" is worth nothing if the next blind kills the run.
2. Ante 1 second shop: $6 on a Jumbo Celestial for Jupiter. In hindsight the Club boss was cleared by 252 over need
   and Jupiter added ~150 of it; the $6 kept would have meant ~$11 in the ante-2 shop: Jolly + a second $4-5 joker
   or a reroll. With 0 jokers, a level on a non-pair hand was the wrong use of the last $6.
3. Ante 1 first shop: I passed Supernova{RENTAL} $1 and the pack offered junk. A $1 rental scorer held for 4 rounds
   (-$12) would have been a second scorer at the Goad; the Buffoon pack ($4) returned nothing.

Reusable if-then rules:
- IF `shopadvise` says EMERGENCY (ratio < 0.35) AND the next blind is TIGHT (< 1.2x) AND no scorer is on offer, THEN
  reroll down to $2-3 at ante 1-2: dying with $8 in the bank is the worst outcome; interest only pays if you survive.
- IF you own 0 jokers at ante 1, THEN spend on jokers (pack or $1 rental scorer) before planets; a level on Flush
  helps one blind, a joker helps every blind and the pair-family plan.
- IF ante 2 Small Blind pays $0 and the shop after it would have <= $4, THEN skip it for any tag (here Coupon gave
  two free Jumbo packs + 2 free items worth $2 sold); it removes a 1000-point risk blind.
- IF a Coupon tag shop shows a free rental joker or a planet you will not use, THEN take it and sell it at once
  (+$1 each, rent is only charged at round end).
- IF the boss debuffs a suit and you hold a 3-of-suit flush draw plus a low pair, THEN discarding the low pair is
  fine: a low pair with Jolly (~140) never keeps pace with 2000; only Flush L3 / Full House do.

Advisor/CLI defects:
- Blind-select ADVICE said "do not skip" the ante-2 Small (Coupon) "the shop after this Small Blind is your chance
  to add a scorer" while I had $2 and the Small pays $0 at Gold: that shop could buy nothing (same defect as
  7804_U4HS5KQK).
- Pack advise in the free Jumbo Celestial said "Jupiter levels your most played / second hand", then the pick note
  said "Jupiter levels Flush (NOT your main hand Two Pair; a level elsewhere is mostly wasted)": the two messages
  disagree about the main hand.
- Pack advise has no ranking for Standard packs ("No pack advice for this pack type").
- Solver p_clear at the Goad deal (0.04-0.05) matched the outcome; at the ante-1 Big it said 0.99 for "play Flush
  then 72 on the last hand", which was right too. No overconfidence seen this run.
Bridge issues: none; 45 steps, no rejects.
