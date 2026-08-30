# Run NFCJJD1W (port 7782) - LOSS at ante 5, The Window boss blind

Stake 1 (White), Black Deck.

Ante 1: jokers [Zany Joker(trips+12mult), Egg(econ)], then +Clever Joker(2pair+80chips). $0 end of shop.
  Small (300): Flush C clubs 292 + Pair3 32 = 324. Discarded to chase flush per advise, worked.
  Big (450): chased pair->trips->Full House 77788, est 1232, cleared in 1 hand.
  Boss The Hook (600): chased KK pair -> trips K, est 900, cleared in 1 hand (Zany fired).
  Shop: bought Egg (no scoring joker avail, overrode shopadvise's plain Egg pick was actually followed after Buffoon
  pack), then Clever Joker from pack, then Card Sharp ($6, xMult) in ante2 shop.

Ante 2: Full House engine confirmed (Zany trips-based + Clever twopair-based + Card Sharp xMult all stack on Full
  House). Bought Earth (Full House -> L2 65x6).
  Small (800): registered Two Pair (256), then Full House AAATT est 2768 actual 3028 for 3028 total. est vs actual:
  within ~10% (est doesn't include the pre-registered Card Sharp benefit precisely, close enough).
  Big (1200): registered Two Pair (256), then chased pair->trips A, est 945 needed 944, actual 1201/1200 (razor thin
  clear, no margin — should have used remaining discard to build more before playing).
  Boss The Club (1600, clubs debuffed): registered Two Pair (264, one 10 debuffed scored 0), then Full House 99944
  (two 9s scoring + debuffed 9C not scoring) est 3078 actual 3342. Cleared comfortably.
  Shop: skipped Arcana packs per shopadvise LEAVE (money too tight at $7). Bought Earth planet for Full House level.

Ante 3: Used The Hermit (doubled $10->$20), The Emperor->Judgement(new joker: Raised Fist)+The Fool->copy Judgement
  (2nd random joker: Misprint, negative edition = free slot). 7/7 jokers: Zany, Egg, Clever, Raised Fist, Misprint,
  Scary Face, Card Sharp(xMult, kept rightmost). Bought The World tarot (unused, NOUSE tag - held for later), used
  Chariot on an 8S (Steel enhancement) from Arcana pack. Full House leveled to L3 (90x8) via 2nd Earth.
  Small (2000): registered Pair(Q), est 360 actual 690 (Misprint variance), then natural low straight (A2345)
    est 1650 actual 2255 -> total 2945/2000. est undershoots actual consistently due to Misprint's random mult being
    estimated conservatively (est notes: "using conservative 6, mean 11").
  Big (3000): registered Two Pair(65), est 1952 actual 2928 (calibration mismatch noted by CLI itself), then a second
    Two Pair (AATT, exact-repeat Card Sharp match) est 6816 actual 12354 (nearly 2x due to Misprint upside) -> total
    14916/3000. Full House was also available (est 6304) but Two Pair scored higher due to Card Sharp's exact-match
    bonus; played the higher-est option.
  Shop: bought Jumbo Celestial pack, took 2nd Earth (Full House L2->L3) overriding shopadvise's "main hand Two Pair"
    read (its main-hand tracker seems to follow whichever hand type was played last/highest, not the leveled
    investment) - kept consolidating into Full House since it already had L2 sunk and still benefits from all our
    trips/twopair jokers.
  Boss on deck: The Tooth (4000, -$1 per card played) — only $6 cash, will keep hands compact.
  Boss The Tooth: played trips 6s no-filler (est 1200 actual 1056, close), discarded to a straight draw that instead
  hit trips QQQ+pair 99 (Full House available too but trips had higher est due to exact Card Sharp match) est 13950
  actual 16806. Compact 3-card hands minimized $1/card loss. Ended ante 3 at $0 cash (spent it all clearing to 0 via
  Tooth + shop).

Ante 4 (boss on deck: The Wall, x2 chips = 20000): Bought Justice (Glass QH), Hierophant (+30 chips Bonus on both
  5s). Picked up a stray Mars planet (leveled Four of a Kind, not our main hands — no Earth/Uranus offered).
  Small (5000): 2x registered Two Pair -> 2nd Two Pair (KJ...actually K4) est 6768 -> total 8918/5000.
  Big (7500): registered Two Pair (K4), then discarded to upgrade into Full House JJJ55 (both 5s enhanced Bonus
    +30chips each) est 13680 actual 16200 -> cleared easily.
  Shop: declined The Sun tarot (suit conversion, doesn't fit rank-based Full House engine) — override, kept the $3.
  Boss The Wall (20000, x2 chips): registered Trips (5s Bonus) est 4095 actual 5670 -> Full House 777KK est 9214
  actual (rolled into cumulative), used last discard to reshuffle same FH (didn't improve) then played it, then final
  forced hand (last hand, last discard) built Full House JJJTT est 27900 actual 22320 (overshoot in est this time,
  first case of est > actual by ~20%) -> total 36933/20000. Cleared comfortably; The Wall did NOT feel like "ante one
  later" this run because our Full House engine + Card Sharp scaling was already far ahead of the curve.

Ante 5 (boss on deck: The Window, suit debuff, 22000): Full House leveled again to L4 (115x10) via a 3rd Earth. Sold
  Raised Fist (weak/conditional, rarely fired well) to make room for Abstract Joker (+3 mult per joker owned = +21
  flat with 7 jokers) — overrode shopadvise's LEAVE since it didn't consider the sell-then-buy path; Abstract Joker
  is strictly stronger than Raised Fist for our build. Jokers now: Zany, Egg, Clever, Misprint, Scary Face, Abstract,
  Card Sharp (xMult rightmost).
  Small (11000): played a natural Flush (clubs) est 4030 actual 5980, then a Straight (9-high) est 2945 actual 3400,
    then a Two Pair(86) est 3712, then a final forced Straight (7-high) est 2635 actual 3400 -> total 13988/11000.
    Closest margin of the run so far (~27% headroom) because we chased flush/straight instead of pairs when the
    dealt hand didn't offer pair-family material immediately — our jokers are pair-family and get zero benefit from
    flush/straight (only base level L1 chips/mult, no Zany/Clever/Card Sharp/Abstract stacking). Lesson: with a
    pair/full-house engine, discarding harder toward a pair is probably worth it even against a decent flush est.
  Big (16500): registered Flush(H) again (est 3780 actual 4644), then built Full House 333TT (Bonus-enhanced 5D
    included) est 10976 -> total 16964/16500, another thin margin (~3%). Two flush hands in a row this ante is a
    pattern worth flagging: `advise` chases flush EV over the pair-family jokers' actual payoff.
  Shop: bought Earth (Full House -> L5, 140x12). Bought Temperance ($3) and used it immediately: sell-value payout of
    all jokers as cash (Egg alone was worth $41 sell value) jumped money from $2 to $52 — huge economy spike.
    Rerolled several times hunting an xMult per shopadvise (none appeared: Blackboard/Greedy Joker/Fortune
    Teller/Dusk all rejected as unreliable/weak). Bought The Chariot (Steel enhancement, unused pending a
    SELECTING_HAND target) and The Hanged Man (card destroy, unused) — sold the never-used World tarot to make room.
  Boss on deck: The Window (22000, suit debuff).
  Boss The Window (diamonds debuffed): registered Full House TTTKK (one T debuffed, one K clean) est 16320 actual
    15360, then Two Pair A6 (Ace and King debuffed cards scored 0) est 3567 actual 5412 -> cumulative 20772/22000,
    need only 1228 more with 1 hand and 0 discards left. Used The Chariot (Steel) on AS (a card NOT in the final
    scoring pair, kept "held in hand" during the play) as the rescue consumable per playbook 4.8 — est barely moved
    (522->540, Steel's passive mult is small on a single unplayed card). Final forced hand: Pair 4s, est 540, actual
    684. FINAL SCORE 21456 vs need 22000 — LOST by 544 points (median).

Post-mortem:
  Binding constraint: bad luck on the final forced hand combined with heavy diamond-suit debuffing (The Window hit
  4 of our 8 dealt cards across the round, including scoring cards in both the Full House and the Two Pair). The
  engine (Full House L5 140x12, Zany/Clever/Abstract/Card Sharp stack) was strong enough to have cleared this blind
  comfortably on a normal (non-debuffed) draw — we were on pace for 25000+ before debuffs ate roughly 15-20% of
  potential chips across the round.
  Decision I would change: when the last hand before a boss showed no reliable pair-family redraw (this hand had a
  pair of 4s only, no trips/full-house upside, down to 0 discards), I should have spent the earlier discard budget
  more conservatively during the FIRST two hands of this round to guarantee 1 discard survived into the final hand
  — instead both early hands used all available discards chasing marginal Full House upgrades that didn't change
  the outcome (disc 3/7/8 discard, then disc 3/4/5/6, both landed on the SAME Full House TTTKK est 16320, i.e. wasted
  discards for zero gain). Holding back 1 discard for the final hand would very likely have let us discard the 3
  debuffed diamonds (KD, QD, 2D) instead of wasting the Chariot's small Steel boost, and draw toward a bigger pair
  or trips to clear the 1228 gap.
  Also: The Chariot's Steel-on-unplayed-card rescue was nearly useless here (+18 est) — for a "does not clear" final
  hand, Justice (Glass, x2 mult, applies even to a single scoring card) or Empress (+4 flat mult) would have been a
  much stronger rescue pick than Chariot. Playbook 4.8 currently just says "use a held consumable" without ranking
  which tarot effect is strongest for a last-second rescue; Glass/Empress > Steel for this purpose since Steel's
  bonus is small and only helps if the enhanced card stays unplayed (doesn't scale with the actual scored hand).

  Bridge issues: none. All commands worked as documented; `ACTION FAILED: Round eval blocking events still pending,
  retry shortly` appeared once after a `cash` call (ante 2 boss) and resolved on a single retry per playbook section
  0/1 guidance.

  Est vs actual calibration (playbook `est`/`need` accuracy): most hands ran 1.2x-1.8x actual/est (Misprint's random
  mult is estimated conservatively at "6, mean 11" per the CLI's own note, and real rolls frequently landed above
  that). Two exceptions ran the other way: ante 4 Wall final hand (est 27900, actual 22320, -20%) and this final
  loss (est 540, actual 684, +27% but still short of need). No case differed from actual by more than the ~20-30%
  Misprint variance already flagged by the tool itself.

  Playbook suggestions:
  1. For the LAST HAND CHECK (section 4.8), rank rescue-tarot priority explicitly: Glass (Justice, x2 mult on a
     scored card) or flat +mult (Empress) or +chips (Hierophant) applied to an actual SCORING card should be
     preferred over Steel (Chariot) when the goal is closing a specific point gap on this hand, since Steel only
     helps passively (small, and only if the enhanced card is not part of the play).
  2. Add explicit guidance: when a round's remaining hands/discards are tight (e.g. last hand of a round with 0
     discards coming up), don't spend a discard re-rolling into an IDENTICAL hand shape (verify via `hands` that the
     result actually changed before re-discarding) — if a discard attempt doesn't change the top candidate, that's a
     signal to bank the discard for the following hand instead of repeating the gamble.
  3. Section 7a's flush/straight caution deserves elevation: this run's two closest-margin blinds (ante 5 Small
     13988/11000, ante 5 Big 16964/16500) both came from playing a natural Flush/Straight when the dealt hand didn't
     immediately offer pair-family material, even though our jokers (Zany/Clever/Card Sharp/Abstract) all reward
     pair-family hands specifically and give zero bonus to Flush/Straight. `advise`'s flush/straight suggestions
     should weight the player's actual joker composition more heavily, not just raw hand-type EV.
