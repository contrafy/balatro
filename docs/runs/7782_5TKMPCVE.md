# Run 5TKMPCVE (port 7782) - LOSS at ante 1, Small Blind (stake 3, Green Stake)

Ante 1, Small Blind (need 300, tag Foil Tag - not a joker/pack tag, so `s` ADVICE correctly said `b blind` per the
ante-1 revised skip rule): zero jokers all round.
- Hand 1: disc 1 4 7 8 (advice) -> kept QQ 66.
- Hand 2: play TWOPAIR 2 3 6 7 (+8 filler) est 104, actual 104. Running score 104.
- Disc: disc 1 2 5 8 (advice) -> kept TT 77.
- Hand 3 (of 3 hands total... actually 2nd play): play TWOPAIR 3 4 6 7 (+8 filler) est 108, actual 108. Running score 212.
- Final hand (0 discards, 1 hand left): advice discarded 6 7 8 keeping K Q J 9 9 to chase a straight while keeping
  the pair as floor; drew 2C 2D (no straight), making Two Pair 9x2x2.
- Forced last hand: play TWOPAIR 4 5 7 8 (+6 filler), est 84 (advice itself flagged "still 4 short"), actual 84.
  Final score 296 / need 300. LOST by 4 chips. Money never left $4 (no shop reached).

Post-mortem: binding constraint was pure scoring power (zero jokers) meeting stake-3's higher Small Blind
requirement (300, vs 300 at stake 1/2 also but here the achievable ceiling from this exact deal capped at 296).
`advise`'s own pre-hand-1 projection said "pair-family hands project to 312 vs need 300" -- a 16-chip margin -- but
the actual sequence of discards/draws only realized 296, 16 short of that projection, which was exactly enough to
lose. Every individual hand's `est` matched its `actual` score exactly (104/104, 108/108, 84/84), so the CLI/advise
scoring model was accurate throughout; the loss was a projection-vs-realized-draw gap, not a misplay or a stale-estimate
bug. The decision I would change: nothing in-round was misplayed against `advise`, but the final discard (disc 6 7 8,
chasing a straight with K Q J held) drew into a second pair for only +28 over the already-guaranteed Pair-9 floor (56);
a flush/straight draw never had a realistic shot with only 3 replacement cards and no suit/sequence support in hand,
so the "keep drawing toward the straight" framing in that ADVICE line was optimistic - the realistic outcome was
always going to be "some second pair or nothing," and it landed 4 chips under. This is a genuine coin-flip loss at
the deck's own scoring ceiling with zero jokers on stake 3's Small Blind, not a shop or economy failure - the run
never reached a shop.

Bridge issues: none. Every command returned the expected state; no ACTION FAILED, no retries needed, no
Connection refused.

Playbook suggestions:
1. STAKE 3 DATA POINT: a jokerless Small Blind (300) can now be lost outright on a bad deal even when
   `advise`'s own pre-hand projection shows a positive margin (312 vs 300 projected here, 296 actual) - the margin
   was inside the variance of which two pair-ranks actually pair up as cards are drawn. Consider whether `advise`'s
   final-hand chase framing ("keep the made Pair as a floor while still drawing to the straight") should note the
   straight is not live (no suited/sequential support in the held cards) rather than implying it's a real chase,
   since here it was arithmetically just "floor Pair (56) vs whatever new pair turns up."
2. Given stake-3's tighter economy (Small Blind pays $0 at stake 2+, but a LOSS on the very Small Blind itself is
   new for this stake's logged data), it may be worth flagging in section 5/6 that stake 3's Small Blind alone
   can now end a run pre-shop with zero jokers, distinct from the existing "jokerless Big Blind (450)" note in 7a.
