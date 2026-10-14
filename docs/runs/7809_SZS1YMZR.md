# Run SZS1YMZR (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind The House (1346/2000)

Ante 1 (300 Polychrome / 450 Voucher / The Manacle 600, $4): Small: disc 4 keeping AA QJ -> drew K T, Broadway Straight 324 one-shot. Shop $6: Buffoon $4 -> Hallucination{PERISH} (over Banner{PERISH,RENTAL}, to avoid 2 rentals), Shoot the Moon{PERISH,RENTAL} $1 -> $1. Big: club Flush keeping QH QC held 1980 one-shot (advise played QC in the flush, est 1241). Shop $4: nothing (Walkie Talkie rental, Arcana). Manacle: disc 5 -> heart Flush 288, disc 5 -> drew QD, Pair 9 with Q held 420 = 708.
Ante 2 (1000 Uncommon / 1500 Polychrome / The House 2000, $7): shop $7: Wily $4 (EMERGENCY, only scorer). Skipped Small for Uncommon tag (saved $3 rent + a Moon tick). Big: Straight 220, disc 5 keeping TT+K -> drew T + QH: Trips T + Wily + Q held 2560. Shop $5: free tag joker was Shortcut{PERISH} (sold $3), sold Hallucination $2, Wrathful{ETERNAL} $5. House: discarded 5 face-downs, then KC + 3 face-downs for a heart flush (missed, drew QD), Pair T + Q held 450, dumped High A 224 keeping 77+QD for trips (31%, missed; drew a 2nd Q), Pair 7 with QQ held 672. 1346/2000. GAME OVER.

## Post-mortem
Binding constraint: SCALING with zero unconditional mult. Every joker I could afford was conditional: Shoot the Moon (+13 per Queen held, rental, perishable), Wily (+100 chips only on Trips), Wrathful (+3 per scoring Spade; scored 0 Spades in the boss). Base mult stayed 2-4 unless a Queen happened to be held. Economy made it worse: Small Blind $0 + Moon rent $3/round left every shop at $4-7, so no $5-6 +mult joker or Buffoon pack after ante 1. The House (first 8 cards face down) cost the first discard on blind cards, leaving 1 discard for a 2000 blind that needed two good hands.

Decisions I would change:
- Ante 2 Big shop ($5 + $2 Hallucination): Wrathful{ETERNAL} (+3 per Spade) added ~0 to the boss. A Celestial pack ($4, Mercury/Venus) or holding $7 for interest would not have saved it either; the real fix was earlier: a reliable +mult joker in ante 1. I'd still take Moon, but at ante 1 shop 1 I would pick Banner{RENTAL} over Hallucination only if I were NOT also buying Moon - never two rentals was right.
- The House hand 1 (all face down): I discarded 5 unknown cards. Playing the 5 face-down cards as the first hand instead would have kept both discards (and a random 5 cards make a Pair or better ~50% of the time). With only 3 hands and a 2000 need, discards were worth more than the hand. Not sure it is better; noting for data.
- The House last discard: chasing a 4-card heart flush (67%) that was worth only ~300 without a Queen. The flush was not big enough to matter; keeping the 3 face-downs (possible Queens) and discarding 5 visible for pairs/trips was probably the better shape.

Reusable if-then rules:
- IF you own Shoot the Moon, THEN never play a Queen unless it is the only way to make the hand: play the flush/straight/pair without the Queens (Big a1: club flush 1241 with QC vs 1980 holding QH QC). Keep every Queen across discards.
- IF your only mult sources are conditional (held Queens, Trips-only, one suit) at ante 2, THEN treat the shop SCORE CHECK as EMERGENCY even when one lucky hand cleared the Big: the next blind will not repeat the luck. Spend on an unconditional +mult (Joker, Jolly, Half, Abstract...) or a Buffoon pack before any suit-gated eternal.
- IF the Small Blind tag is Uncommon, THEN remember the tag joker is random (here Shortcut, useless): it is worth roughly $3 (its sell value) plus the saved rent/perish tick, not "a free scorer".
- IF The House deals 8 face-down cards and the blind needs 2+ strong hands, THEN consider playing 5 face-down cards as hand 1 (keeps both discards) instead of discarding them blind.

Advisor/CLI defects:
- `advise` ignores Shoot the Moon held-Queen value when choosing the cards: at the a1 Big it advised FLUSH 2 3 4 6 7 including QC (est 1241); the flush without Queens was est 1980.
- `shopadvise` SCORE CHECK ignores Shoot the Moon: "one Pair (KK) ~60" and "Three of a Kind (KK) ~480" (ante 2), although Pair+Queen-held was 420-450 and Trips+Q 2560 in play.
- `shopadvise` (ante 2 shop 1): ranked Jumbo Celestial 87 above Wily 65, but the ADVICE line said buy Wily (the keep-$4 rule filtered the pack; the ranking list does not show that).
- Skip advice sold the ante-2 Uncommon tag as "a free Uncommon joker"; it produced Shortcut{PERISHABLE} (straights with gaps), no scoring value.
Bridge issues: none; every command settled first try.
