# Run LNEBMNPC (port 7782) - stake 3 (Green Stake) - LOSS at ante 1 Big Blind

Ante 1: Small Blind (300) tag=Polychrome Tag. ADVICE: `b skip` (zero jokers, Polychrome is in the
"good tag" list for a skip). Skipped -> no shop, straight to Big Blind (450) still with zero jokers, $4.
  - Hand 1: dealt AA 66 among junk. `advise` -> disc 3 4 7 8 (keep AA66). Then TWOPAIR A6 idx 1 2 5 6 (+filler 8),
    est 108, actual 108 (scored 108/450).
  - Hand 2: dealt 8877 pairs, also a made STRAIGHT 8-7-6-5-4 (idx 1 3 5 6 7) sitting in hand already.
    `advise` -> disc 2 4 8 (drop the duplicate 8/7/2, keep the 5 straight cards, draw 3 new).
  - Hand 3: redrew TH, no straight but still had straight cards + a new pair(6). `advise` -> PLAY STRAIGHT
    idx 2 3 4 6 7, est 240, actual 240 (scored 348/450 cumulative). Pacing note in ADVICE said "1 discard for
    2 hands", 1 discard, 1 hand left, need 102 more.
  - Hand 4 (2nd-to-last, 1 disc left): dealt JC TS TH 9S 8S 6D 2S 2H (TT pair, 22 pair, near-straight
    J-T-9-8 missing a 7 or Q). `advise` -> disc 6 only (drop the lone 6D), keep TWOPAIR T2 as floor (est 88)
    while drawing 1 for a shot at the straight. Redrew 3C: no straight completed.
  - Hand 5 (forced final hand, 0 discards): only viable play TWOPAIR T2 idx 2 3 7 8 (+filler), est 88,
    need 102 (14 short). `advise` said so explicitly: "est 88, still 14 short; 0 hands left after this" -
    no consumables held, no alternative hand available (no straight, no flush, no trips). Played it anyway
    (only legal productive action). Actual score 88 (matched est exactly). Final: 436/450. GAME_OVER.

Jokers held all run: NONE (never reached a shop; the ante-1 Small Blind skip forfeited the only shop visit
before the Big Blind).
Money curve: flat at $4 the entire run (no blind cleared -> no cash-out, no shop, no income).

Post-mortem: binding constraint was SCALING (zero jokers) compounded by a SEQUENCING decision (the Small
Blind skip). A jokerless deck averages roughly 100-150/hand on pair-family hands at L1; three such hands
cannot reliably clear 450 (this run: 108+240+88=436, 14 short) even with a lucky pre-made straight landing
in hand for free. The Small Blind (300) would very likely have been cleared by hand 1+2 alone (108+240=348
> 300, with a discard to spare), which would have opened a shop visit (~$4-7) BEFORE facing the Big Blind -
giving a real chance to buy the first scoring joker the playbook says is mandatory by "end of ante 2." Emphasis
line, playbook section 5, also states the tag has to be joker-GIVING to be worth more than the shop when
holding fewer than two scoring jokers (Uncommon/Rare/Buffoon/Top-up/Coupon) - Polychrome Tag is an EDITION
tag (affects next shop's joker edition), not a joker-granting one, so by that clause alone the shop should
have outranked the skip. The CLI's `advise`/blind-select ADVICE followed the separate, more specific
ante-1-stake-2+ rule ("skip for any tag except Boss") to the letter (as instructed), so this is not a bug,
but the two written rules in section 5 point in different directions for a non-joker-granting tag at ante 1,
and this run is a concrete data point that the blanket "skip any tag" rule can cost the only pre-Big-Blind
shop and the run.

The one decision I would change: at ante 1 with zero jokers, do NOT skip the Small Blind for a tag that does
not itself grant a joker (Polychrome/Foil/Holo/Negative/Meteor/Ethereal/Charm/Investment) - only skip for a
joker-granting tag (Uncommon/Rare/Buffoon/Top-up/Coupon) or the already-excepted Boss tag case. Playing the
Small Blind here would have banked a clean win (348 from the first two hands alone) and opened a shop before
the much harder 450 Big Blind.

Bridge issues: none. Every ADVICE-recommended action executed as printed; `est` matched actual score exactly
on both hands checked against >20% drift criteria (108 vs 108, 240 vs 240, 88 vs 88 - all exact, no entries
qualify for the est-vs-actual >20% table).

Playbook suggestions:
1. Section 5's ante-1 Small-Blind-skip rule ("skip for any tag except Boss") should be narrowed to match the
   adjacent joker-granting-tag clause already in the same section: with zero scoring jokers, only skip for a
   tag that GIVES a joker (Uncommon, Rare, Buffoon, Top-up, Coupon) or when the tag itself is worth more than
   a guaranteed shot at clearing the cheaper Small Blind (300) and reaching a shop before the Big Blind (450).
   As written, the two clauses in section 5 conflict for edition-only tags (Polychrome/Foil/Holo/Negative)
   and this run shows the cost: 436/450 lost, with no shop ever reached.
2. Add a check to `advise`/blind-select ADVICE: when skipping the Small Blind would leave the deck jokerless
   AND the recent-hands average (from `hands`) projects under the Big Blind's need with 3 hands, flag that
   the skip trades a likely-winnable smaller blind (plus a shop) for a harder blind with no scaling - "skip
   the shop, not the sure thing" is the more common failure per the run data logged so far.
