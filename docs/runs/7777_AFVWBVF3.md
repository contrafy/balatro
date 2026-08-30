# Run AFVWBVF3 (port 7777) - LOSS at ante 1, boss The Manacle (need 600, scored 457)

Stake 1 (White), Black Deck.

Ante 1: Small=Charm Tag, Big=Economy Tag, Boss=The Manacle (-1 hand size, 600).
  Shop1 ($7 after Small): no scoring joker offered (Golden Joker[ECON +$4/rnd], Saturn[planet], Tarot Merchant[voucher]).
    Per top-level task rule ("if no scoring joker offered, a Buffoon Pack is better than leaving with cash"), overrode
    shopadvise's ADVICE (buy Golden Joker) and bought Buffoon Pack ($4) instead. Pack offered Baron vs Ramen
    (Ramen is explicitly on the playbook avoid list); picked Baron (x1.5 mult per King held in hand, sell$4).
  Small(300): TWO PAIR AK est124 act124, PAIR6 est44 act44, STRAIGHT KQJT9(2 Kings held for Baron) est316 act316 =
    484 total, won (needed 300). Est matched actual on every hand.
  Shop2 ($9 after Big... see below): no scoring joker or Buffoon Pack offered (Pluto[planet], Hallucination[util],
    Tarot Merchant[voucher], 2x Arcana Pack[tarot]). Reroll ($5) would drop money to $4, below the $10 floor
    (playbook: "Do NOT reroll in ante 1-2 unless you have >= $10 after the reroll") -- correctly did not reroll.
    shopadvise said LEAVE both times; followed it. Ended ante 1 with only 1 joker (Baron) the whole run.
  Big(450): STRAIGHT KQJT9 with 2 Kings held back (unplayed) for Baron x1.5*x1.5 est711 act711, single hand, won.
  Boss The Manacle(600, hand_size 7): spent all 3 discards up front chasing the best made hand on hand 1 (ended on
    Pair7->Trips777), leaving 0 discards for hands 2-3:
    hand1 TRIPS 777 (1 King held for Baron) est229 act229
    hand2 TWOPAIR TT44 (1 King held for Baron) est144 act144 (cumulative 373)
    hand3 PAIR99 (King+Queen held, only King counts for Baron) est84 act84 (cumulative 457)
    LOST: needed 600, scored 457, short by 143. Est matched actual exactly on every single hand this entire run
    (0% error, no case >20% off).

Post-mortem: binding constraint = scaling/variance, not misplay. We ended the ante-1 boss with only 1 joker (Baron),
  a conditional joker whose bonus (x1.5 mult per King HELD, i.e. NOT played) requires giving up cards from the best
  possible hand rather than adding flat value like Jolly/Sly/Droll would. Shop 2 genuinely offered no scoring joker
  and no Buffoon Pack, and reroll was correctly skipped per the $10 floor rule, so there was no available action to
  get a second joker before the boss. Playbook's own fact ("the 600 boss needs ~200 per hand") held exactly: we
  averaged 152/hand (457/3) with only one narrow conditional joker and lost by 143.
  Decision I would change: none within the rules given the information available at each shop -- this looks like a
  legitimate bad-luck gap (no Buffoon Pack in shop 2) compounded by a joker (Baron) whose value ceiling is capped by
  needing to hold cards out of play. If forced to choose differently, I would treat "only 1 conditional/held-card
  joker by end of ante 1" as a red flag at blind-select for the boss (see suggestion 3 below) and consider spending
  the boss-round discards more conservatively (e.g. keep 1 discard in reserve for hand 3) even though it likely
  would not have closed a 143-point gap.
Bridge issues: none. Every `play`/`disc`/`advise`/`shopadvise`/`pack`/`pick`/`blind`/`cash`/`endshop` command worked
  as documented; no retries needed; no `ACTION FAILED` messages seen.
Playbook suggestions:
  1. Add explicit guidance for "held in hand" / conditional jokers (Baron, Mime, Raised Fist, Seeing Double, Reserved
     Parking, etc.): their bonus competes directly with playing your best possible hand (e.g. holding a King back
     from a straight/pair reduces the made hand's card chips to gain Baron's x1.5). Note the play/hold tradeoff
     explicitly, similar to the existing xMult-ordering (`order`) guidance.
  2. Extend the ante-1 "buy the Buffoon Pack if no scoring joker offered" rule (section 5) beyond just the FIRST
     shop: state plainly that if a LATER ante-1/2 shop also has no scoring joker and no Buffoon Pack, and reroll is
     blocked by the $10 floor, there is no mitigation available under current rules -- so agents recognize this as
     an accepted risk rather than second-guessing it in the post-mortem.
  3. Codify the ~200/hand average as an explicit early-warning check: if an agent reaches ante-1 boss blind-select
     with fewer than 2 scoring jokers, OR only conditional/held-card jokers (whose average per-hand value is lower
     than a flat +mult of the same rarity), flag the loss risk at blind-select time (before spending any boss-round
     discards) rather than only discovering it in the post-mortem after the run is already lost.
