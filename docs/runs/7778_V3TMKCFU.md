# Run V3TMKCFU (port 7778) - stake 3 (Green Stake) - LOSS at ante 2 Small Blind

Ante 1: skipped Small Blind ($0 at stake 3). Big Blind: Flush(D) 304 + Full House 276 = 580/450. Shop: bought
Buffoon Pack $4, picked Splash (only non-penalty option vs economy-only Faceless Joker); rerolled to $0 per
shopadvise (no scoring joker offered/rerolled), left with jokers 1/6 ($0 remaining). Boss The Club (clubs
debuffed): Flush(H) 288 + Flush(D) 280 + Pair(3s)+fillers 72 = 640/600. Cleared with 0 scoring jokers via flush
chases (had discards to spare each time). Money $0 -> $5 at cash out.

Ante 2 shop: rerolled to $0 (Popcorn/Erosion only offers, no scoring joker; shopadvise said REROLL then LEAVE).
Left shop with jokers 1/6 (Splash only), $0.

Ante 2 Small Blind (need 900): `s` ADVICE said `b blind` (play, not skip) despite 0 scoring jokers and a
$0-reward Small Blind at stake 3 - followed it. Full House AAAKK 372, Straight 7-high 220, Flush(S) forced
final hand 252 = 844/900 total. LOST by 56 (900 needed, 844 scored). Final hand had 0 discards/0 hands left
(all 5 spades already in the flush, no filler headroom under the 5-card play cap) - mathematically could not
close the gap once the Straight-chase hand (220) undershot. Run ends here; stake 3 stays unbeaten by this
instance.

Playing FLUSH 1 4 5 6 8 est 252 -> actual 252/scored total 844 (matched est exactly, no deviation).
Playing PAIR 6 7 1 2 3 (ante 1 boss final hand) advise-line est 32 -> play-line est 72 (fillers via Splash
added 40) -> actual matched play-line est 72 exactly. Not a >20% miss against the number actually used to plan
(play-line est), only against the earlier advise-line est before fillers were chosen - not counted as a
playbook-relevant discrepancy since `play`'s own est already corrected for it.

Post-mortem: binding constraint was SCALING / STARTING JOKER, not this hand's luck. We entered ante 2 with a
single non-scoring joker (Splash) after two consecutive $0-money shops (rerolled to zero both times because no
scoring joker was ever offered) - the deck was doing pure flat pair/flush/straight chip totals against a 900
target that needs ~3x an ante-1 hand. The Full House (372) and Straight (220) both underperformed their
"needed" share; with zero mult multiplier jokers, hitting exactly the right total every hand at stake 3 has
very little slack once a mid-round hand undershoots (this Straight at 220 was well short of a proportional
303 share of 900/3). The one decision I would change: at the ante-2 Small Blind blind-select, override the
CLI's `ADVICE: b blind` and SKIP instead - stake 3's Small Blind still pays $0 and the tag was only a plain
Skip Tag (no joker/pack upside per playbook section 5), so skipping cost nothing but a shop visit and would
have sent us straight to a Big Blind we had two extra ante's worth of runway to prepare for (1 fewer forced
weak hand at 0-scorer strength). Section 5's "with fewer than two scoring jokers only a tag that GIVES a joker
beats the shop visit" rule argues for skipping a plain Skip Tag Small Blind even when the CLI blind-select
ADVICE says otherwise, and I should have applied that override rather than following `b blind` verbatim.

Bridge issues: none. No `ACTION FAILED`, no `Connection refused`, no aborted `play` due to stale indices. All
commands returned expected state transitions.

Playbook suggestions:
1. The `s`/blind-select ADVICE line said `b blind` for the ante-2 Small Blind while we held 0 scoring jokers
   and the tag was a plain Skip Tag (no joker/pack payoff) - section 5's own text says this combination should
   be skipped. The blind-select advisor should special-case "0 scoring jokers AND tag has no joker/pack upside"
   at stake 2+ and recommend skip, not just at ante 1.
2. Consider having `advise` project the running per-hand share of the blind requirement (e.g. "this hand should
   land >= N/3 of the remaining total to stay on pace") rather than only "est >= need this hand", since two
   individually-reasonable "keep drawing, pacing" PLAY calls in a row (220 then a forced 252) left no way to
   recover once the middle hand came up short - a pacing floor per hand might catch this earlier.
3. Nothing to change about Splash as a first joker choice; it behaved as documented (fillers scored, matched
   its own est exactly) but confirms it is not a substitute for a genuine scoring/mult joker at stake 3 - the
   REROLL-to-$0 rule for "no scoring joker" shops did its job twice but never found one before ante 2's blind.
