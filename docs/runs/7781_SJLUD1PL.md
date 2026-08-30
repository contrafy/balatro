# Run SJLUD1PL (port 7781) - stake 3 (Green Stake) - LOSS at ante 2 boss (The Manacle, 1106/1800)

Ante 1: Small Blind tag=Boss Tag (played per rule: Boss tag is the exception to "skip at ante 1"; CLI ADVICE also said `b blind`).
  - Small Blind (300): played STRAIGHT (K Q J T 9), no jokers yet, est 316, actual 316. Cleared in 1 hand.
  - Shop: bought Odd Todd $4 (unconditional +31 chips/odd card, valid floor joker per playbook). $2 left, shopadvise said LEAVE.
  - Big Blind (450): discarded once to build Two Pair -> drew Full House (9-9-9-8-8), played FULLHOUSE, est 704, actual 704. Cleared in 2 hands, 2 discards left.
  - Shop ($8): shopadvise ADVICE was BUY Devious Joker $4 (+100 chips if Straight). OVERRODE: our engine is pair/full-house
    (both hands played so far were pair-family or a forced straight), and the playbook explicitly lists Devious among
    straight-only jokers that "must never be your only scorer or your first buy" and warns "do NOT drift into a flush or
    straight build." Devious would never fire under our intended build. No other real scaling was affordable without
    breaking the ante-1 $4 floor (Jumbo Arcana Pack $6 would leave $2). Ended shop with $8 unspent instead.
  - Boss The Psychic (600, exactly 5 cards/hand): discarded once (kept 5s/3s), then played TWOPAIR 5 6 7 8 (+filler) est 320,
    actual 320; drew a straight next hand, played STRAIGHT (A K Q J T) est 448, actual 448. Cleared 768/600 in 2 hands,
    1 hand + 2 discards banked for cash-out interest/leftover.

Ante 2: Small Blind tag=Meteor Tag ($0 reward at stake 3+). CLI's `s` ADVICE line said `b blind` (not skip) despite the
  tag being on the playbook's "worth a joker/pack" list with 2 scoring jokers held; followed the CLI ADVICE line exactly
  per instructions.
  - Shop before Small Blind ($15): no scoring joker in shop twice in a row -> shopadvise said REROLL both times
    ($15->$10->$4), then bought Wily Joker $4 (+100 chips if Three of a Kind; Trips-gated, explicitly fine as SECOND
    joker per playbook). Ended at $0.
  - Small Blind (900): discarded twice building toward Two Pair, then a Straight appeared; played TWOPAIR (+filler) est
    344 actual 344, then STRAIGHT est 592 actual 592. Cleared 936/900 in 2 hands, 1 discard left, $0 reward (stake 3+).
  - Shop ($1): nothing affordable, shopadvise LEAVE.
  - Big Blind (1350): chased a Flush (5 spades appeared: K Q J T + one more), played FLUSH est 452 actual 452 (1 hand,
    2 discards used building it). Then no discards left forced two Trips plays: TRIPS of Kings est 480 actual 480 (Wily
    Joker firing), then final forced hand TRIPS of 5s est 714 actual 714 (Wily Joker again). Cleared 1646/1350 across
    3 hands, all discards spent building the flush/trips chain — no discard survived to the final hand, but the final
    hand happened to be a made Trips anyway so it didn't matter.
  - Shop ($5): shopadvise LEAVE (Juggler +1 hand size, AVOID Ramen, Spectral pack, Celestial pack all below advised
    money level). Ended shop with $5 unspent, still only 2 jokers (Odd Todd + Wily).
  - Boss The Manacle (1800, hand size 7): only a Two Pair (4s/3s) available for 3 straight draws (discarded into the
    SAME 4-3 two pair three times in a row - deck was thin on other pairs). Played TWOPAIR est 192 actual 192 (used
    all 3 discards trying to escape it without success), then forced (0 discards): PAIR 9 est 164 actual 164, then
    TRIPS of 9s est 750 actual 750 (Wily Joker), final forced hand nothing left but the same shape. Total 1106/1800.
    LOST THE RUN. No `est` vs actual discrepancy >20% occurred anywhere this run; every played hand's est matched the
    actual score exactly.

Final: stake 3, ante 2, lost to boss blind The Manacle, 1106/1800 needed (694 short). Money at game over: $5.
Jokers held at loss: Odd Todd (+31 chips/odd card), Wily Joker (+100 chips if Three of a Kind). Main hand never got
past L1 (no planet was ever bought — money was spent on jokers/rerolls at ante 1-2 per the floor-joker priority, and
no Celestial pack/planet was affordable without breaking the ante-1/2 money floor).

Post-mortem: binding constraint was SCALING, not a single misplay. Two flat +chips jokers (Odd Todd, Wily) at L1 hand
levels simply do not produce enough chips to clear a stake-3 ante-2 boss (1800) once RNG stops handing a bigger hand
(Full House/Straight/Flush) and settles into a repeating weak Two Pair (4-3) with no discards left to escape it. The
one decision I would change: at the ante-2 shop with $5 before the boss, shopadvise said LEAVE, but in hindsight a
Celestial Pack ($4, would have leveled Two Pair or Pair by one level) might have been worth overriding LEAVE for, since
we were about to face a Two Pair-heavy hand at 1800 chips needed with only L1 levels and zero hand-leveling all run.
I followed shopadvise as instructed and did not override, so this is a playbook/advisor observation rather than a
misplay on my part.

Bridge issues: none. Every `play`/`disc`/`buy`/`shopadvise`/`advise` call succeeded on the first try, no
`ACTION FAILED ... retry` or Python errors encountered this run.

Playbook suggestions:
1. shopadvise never surfaced a hand-level planet/Celestial pack as worth buying at ante 1-2 in this run (it always said
   LEAVE or pushed jokers/rerolls first), and the run ended at ante 2 with the main hand still at L1. Consider having
   shopadvise weight a cheap Celestial Pack ($4) higher once 2 scoring jokers are held and money exceeds the floor by
   $4+, even at ante 1-2, since a repeating weak Two Pair at L1 cannot clear a stake-3 ante-2 boss (1800).
2. Confirm/clarify the interaction between "STAKE 2+ skip the Small Blind for a tag worth a joker/pack (Meteor is
   listed) once you have >=2 scoring jokers" and the CLI's own blind-select ADVICE line, which said `b blind` at ante 2
   with a Meteor tag and 2 scoring jokers held — the two sources disagreed and I followed the CLI's ADVICE line per
   this run's explicit instructions, but the playbook text would have suggested skipping for the $0-cost Meteor tag.
3. No est-vs-actual discrepancy occurred this run (every hand's est exactly matched the actual score), so nothing to
   flag there this time.
