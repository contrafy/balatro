# Run D5SPSIPM (port 7777) - LOSS at ante 2 boss (The House)

Stake 1 (White), Black Deck.

Ante 1: jokers [Droll Joker +10mult-if-Flush], $0->$7, levels {Flush L2}, buys: Droll Joker($4 pack), Jupiter(pack), The Moon tarot($3, unused so far).
  Small 300: flush S est272 actual351 (multi-hand). Big 450: flush S est910 actual910. Boss The Hook 600: flush H L2 est1552 actual1552 (single hand).
Ante 2: jokers [Droll Joker +10mult-if-Flush] (only 1 joker whole run - no second joker ever appeared/bought), $4 start ->
  levels {Flush L2->L3->L4->L5 via 4 Jupiter buys}. Small 800: flush S est1764 actual1764. Big 1200: full house
  L1 est344 + two pair L1 est84 + flush H L4 est2420 actual2848 total (multi-hand, last-hand flush saved it).
  Boss The House (1600, first hand face-down): discarded all-facedown opening hand blind (5 cards), rebuilt with
  full house x2 (304+308=612) using two Full Houses formed from re-drawn cards, then final hand only Pair 7
  (est48, needed 988) - no flush/straight material, no discards left, no xMult/chips joker to save it. LOST.
  Used The Moon tarot (sel 1, use 1) on the final hand hoping to convert toward a flush - only converts 1 card at
  a time (despite sel-ing 5 earlier which silently failed with ACTION FAILED, only sel 1 card actually enabled use),
  converted AH->AC, insufficient (max suit count 3, needed 5). Did not matter for outcome.

# FINAL: LOSS at ante 2, The House boss (1600 needed, 660 scored)

Post-mortem:
- Binding constraint: SCALING, not misplay. The entire run had exactly ONE joker (Droll Joker, +10 mult if Flush)
  the whole way from ante 1 through the ante-2 boss loss. No second joker ever appeared as an affordable/worthwhile
  buy in any of the 4 shops visited (shopadvise's own item lists show only Tarots/Planets/Vouchers/Packs being
  the ADVICE picks each time - no Joker was ever the top-scored ADVICE after Droll). Playbook 5's ante-1-2 rule
  ("buy the FIRST affordable joker that adds mult/chips... two such jokers by end of ante 2") was not met: we
  ended ante 2 with only 1 joker despite following shopadvise every shop. With only a single conditional
  (Flush-only) mult joker and no flat-chip/mult joker as a floor, the moment a round's draws didn't cooperate
  with a flush (The House boss: forced to discard the entire face-down opening hand, blind, losing a full
  discard for zero information), there was no fallback scoring path strong enough (Pair est only 48 vs 988 needed).
- Money was also never above $8 the whole run (spent every shop down near $0 to buy hand levels), so there was
  never a reroll or joker-shopping option available when the shop only offered tarots/vouchers/packs and no joker.
- The one decision I would change: at the ante-2 shop after the Small Blind (state: $8, jokers 1/6, shop had
  Wily Joker $4 <PLUS other hand +100 chips if Trips> and The Hanged Man $3 tarot), shopadvise's ADVICE was
  "pack 1" (Jumbo Celestial Pack $6, another Flush level). Buying Wily Joker instead (a second, non-Flush-
  conditional scoring joker, fits our secondary Full House play which we in fact used twice at the boss) would
  have left us with 2 jokers and a real fallback, at the cost of one flush level (L5 vs L4) we barely needed
  (we never scored a losing hand where the missing points were level-4-vs-5 flush math; we scored 0 flushes at
  all during the boss round). shopadvise's own [PLUS(other hand)] tagging on Wily Joker shows it recognized the
  option but weighted the Flush-level pack higher every single time scoring/mult jokers were available alongside
  planets - across 4 shops we bought 4 planets/packs-for-levels and only 1 joker total.
- The House boss forces the FIRST hand of the round face-down/unknown; discarding it blind costs a full discard
  for zero information (no way to identify pairs before committing). This ate 1 of 3 discards for nothing,
  leaving only 2 real discards to build hands with for the rest of the round - a meaningful tax that the
  playbook's boss section doesn't currently call out for The House (it's only listed as a face-down suit/rank
  boss under section 6's face-down list, without the "you lose your first discard for free" framing).

Bridge issues:
- `use N` (consumable) failed twice with `ACTION FAILED: Consumable cannot be used right now (may need target
  cards selected) None` when either no cards were selected, or when 5 cards were `sel`-ed at once for The Moon
  tarot (a suit-conversion tarot). It only succeeded after `sel 1` (exactly one card highlighted). The Moon
  appears to convert only 1 selected card per use in this game version, not "up to 3" as commonly documented;
  playbook section 7a's card-targeting-tarot list should note single-card-only behavor was observed for The Moon,
  or that agents should sel exactly 1 card and re-use repeatedly rather than multi-select.
- No other CLI errors or retries were needed this run; all `disc`/`play`/`buy`/`pack`/`pick`/`cash`/`blind`/`use`
  actions succeeded on the first or (for the 2 `use` cases above) second attempt.

Playbook suggestions:
1. Ante 1-2 shop rule should be stricter: if after 2 shops the run still has fewer than 2 jokers, treat buying
   ANY scoring joker (even a conditional/other-hand one like Wily's "+100 chips if Trips") as higher priority
   than a 4th+ hand-level planet purchase, even when shopadvise's own scoring ranks a planet pack higher - a
   single-joker build has no fallback when the main hand's cards don't show up.
2. Add The House boss to the "boss notes" (section 4 point 7) explicitly: "the first hand of the round is dealt
   fully face-down; you cannot see ranks to keep good cards, so the opening discard is blind and costs a discard
   for zero information - plan the round assuming only 2 usable discards, not 3."
3. Confirm/clarify The Moon (and other Star/Sun/World-type suit-conversion) tarot's actual per-use card limit in
   this game build (observed: exactly 1 card via `sel`, not multiple) so agents don't waste a `sel`/`use` cycle
   over-selecting.
