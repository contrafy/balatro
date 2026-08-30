# Run SDCDPVJE (port 7777) - LOSS at ante 1 Big Blind (stake 3, Green Stake)

Ante 1: Small Blind (300, Coupon Tag) skipped per CLI ADVICE (pays $0 at stake 2+, Coupon Tag would have made next shop free).
  Big Blind 450, no jokers, no shop visit ever reached.
  Hand 1 dealt: AC QS QC 9C 8H 8D 7S 7C (three pairs Q/8/7). `advise` said DISCARD 2 5 6 7 to chase a flush
    (4 clubs held: AC QC 9C 7C, EV 187 vs made Two Pair est 112). Followed it. Flush did not land; redraw gave
    a new Two Pair (Q9). Played TWOPAIR 2 3 4 5 (+filler 8): est 116, actual 116. Score 116/450.
  Hand 2 dealt only a Pair 4 (est 36). `advise` said DISCARD to chase a straight (A Q J T held, EV 130 vs
    made Pair est 36). Followed it; straight did not land (drew 9S, 6H, 6C -> Two Pair A6 possible).
    Then advised a single-card discard (last discard) to lock in the Two Pair A6 floor (est 108) while still
    holding J/Q for a straight shot. Played TWOPAIR 1 2 7 8 (+filler): est 108, actual 108. Score 224/450.
  Hand 3 (forced final hand, 0 discards): dealt K Q J T T 5 4 3 - only Pair T (est 60), 166 short of need.
    No consumables held (Coupon Tag gives free shop items, not a starting consumable) so the LAST HAND CHECK
    (playbook 4.8) had nothing to use. Played PAIR 4 5 (+fillers): est 60, actual 60. Final score 284/450. LOSS.

Post-mortem: binding constraint = zero scoring jokers, compounded by never reaching a shop at all (Small Blind
  was skipped per the CLI's own stake-3 advice before any joker could be bought). The two flush/straight chase
  discards (EV 187 and EV 130) both missed, which is expected at ~40-60% hit rates but left no discards for the
  forced final hand. The decision I would change: on Hand 1, do not chase the flush at all when it is ante 1
  and skipping the Small Blind already forfeited the only chance at a joker before this blind — a jokerless
  Big Blind with 3 hands / 3 discards should sequence the three pairs (play Q8, then 7-pair, then whatever
  redraws) rather than spend a discard hunting a low-40s-percent flush, since a miss (as happened) leaves the
  same or worse floor than just playing the made Two Pair immediately for guaranteed chip income toward the
  final tally. Two Pair Q8 (est 112) + Two Pair 87 or similar sequenced immediately across 3 hands (roughly
  112+100+100=312) would likely still have lost to 450, but so did the chase (284) - the real fix is upstream:
  do not skip the ante-1 Small Blind at stake 3 when zero jokers are held and the Big Blind (450) is already
  a stretch for a jokerless pair engine (playbook 7 says jokerless pair engine is ~100-120/hand, i.e. ~300-360
  max across 3 hands even with perfect sequencing) - the $0 Small Blind skip trades away the ONLY shop that
  could have bought a scoring joker before the Big Blind, for a Coupon Tag benefit (free shop) that never
  materializes because the run ends first.

Bridge issues: none. All commands returned expected state; `est` matched `actual` exactly on both played hands
  (116/116 and 108/108), so no >20% est-vs-actual discrepancy to report.

Playbook suggestions:
  1. At stake 3 (Green Stake), reconsider the blanket "skip Small Blind ante 1 for any non-Boss tag" rule: with
     zero jokers, a jokerless pair engine tops out around 300-360 across 3 perfectly-sequenced hands (playbook
     section 7 verified numbers), which is already short of the Big Blind's 450 - skipping the Small Blind
     removes the only shop visit that could add a joker before that Big Blind is faced. Section 5's own stake-3
     data (two of three early Green Stake runs already died ante 1-2 zero-joker) supports NOT skipping when the
     tag itself doesn't grant a joker (Coupon/Investment/etc. do not).
  2. Flush/straight EV-chase advice (`advise`'s DISCARD branch) should weight the cost of a miss more heavily
     when it is the ONLY early blind before any shop: a miss leaves fewer discards for later hands with no
     compensating floor, whereas immediately sequencing made pair-family hands banks guaranteed chips. Consider
     suppressing the flush/EV chase specifically on ante-1 zero-joker Big Blinds in favor of the sequenced-pairs
     line from section 5's "ZERO-JOKER HANDS" guidance.
