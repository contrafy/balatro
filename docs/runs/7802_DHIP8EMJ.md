# Run DHIP8EMJ (port 7802, claude-fable-5-1) - Black Deck Gold Stake - LOSS at ante 1 blind Small Blind (200/300)

Ante 1 (300/450/Manacle 600; tags Double/Holographic): played Small (Double Tag gives no joker/pack). Dealt TS 8C 6D 5C 4S 4C 2S 2C: Two Pair 44/22 est 64, 4 clubs. disc TS 6D (kept two pair + 4-flush, ~50% flush/FH) -> KS QH. disc KS QH -> 9D 7S. 0 discards, 3 hands: Two Pair 44/22 64 (no filler, kept 9 8 7 5 straight draw, 3 sixes left) -> drew QS 9S 7D 3C; Two Pair 99/77 + QS filler 104 (kept 8C 5C 3C, 30% club flush) -> drew QD TH 7H 3H 2H; Pair 3 32 = 200/300. GAME OVER with $4, no jokers, no consumables. est exact on all 3 hands.

## Post-mortem

Binding constraint: LUCK on a jokerless 300, compounded by one sequencing misplay. Gold's ante-1 Small Blind is 300 with 3 hands, 2 discards and nothing on the table: a low two pair is 64, so it takes a flush/straight/full house (220-260) or three pair-family hands averaging 100. Two 4-flush draws (37%/39%) both missed, and with both discards gone the last two hands were pure deal luck.

Decision I would change (verified against the actual deck order): after the first discard missed (hand KS QH 8C 5C 4S 4C 2S 2C) I spent the SECOND discard on the same 4-flush instead of banking Two Pair 44/22 + KS filler and keeping one discard. The cards that actually came (9D 7S, then QS 9S 7D 3C, then QD TH 7H) would have given Two Pair QQ99 (116) and, with the kept discard, Trips 7 (153): 64 + 116 + 153 = 333 >= 300. I broke the playbook's "keep ONE discard for the forced final hand" rule on the very first round because I assumed only a 5-card hand could clear; three 8-card deals produce pairs/two pairs/trips often enough that the discard is worth more on the last hand than as a second look at a 4-flush.

Reusable rules (if-then):
- IF you have no jokers and a 300 Small Blind, THEN never spend both discards before your first play. Bank the made Two Pair (even 64) with a filler, use ONE discard to chase a 4-flush/4-straight/full house, and keep the other for the final hand: 64 + ~100 + a last hand with a discard (Two Pair of 9+ ranks or any Trips clears the remaining ~130) beats two blind looks at a 4-flush.
- IF you chase a 4-flush with no jokers, THEN one discard is the budget: a miss (63%) followed by a second miss (61%) leaves 3 hands of ~64 each, which never reaches 300.
- IF the first hand of a jokerless round is a low Two Pair plus a 4-flush, THEN play the Two Pair with a filler that is NOT one of the flush suit and NOT part of a straight draw (keep 3 suited + connected cards), so the 5-card draw keeps both outs alive.
- IF the ante-1 Small tag is Double/Holographic/etc. (no joker, no pack), THEN still play the Small: skipping sends a jokerless deck into 450 (Big) or 600 (boss) instead of 300; the only lever at Gold ante 1 is hand sequencing.
- IF a last hand must clear ~130 with no jokers, THEN only Trips (rank >= 5), Two Pair with 46+ card chips (e.g. QQ TT), a straight or a flush do it; count those outs when choosing which 3-4 cards to keep, not just the flush.

Advisor/CLI defects:
- `advise` ADVICE "play TWOPAIR 5 6 7 8 4" proposed the 5C as a filler, which would have broken the 9-8-7-5 open-ended straight draw (the only single-card out left: three 6s). Filler choice ignores straight/flush draws among the kept cards; the no-filler play (draw 4, keep the draw) was better and the ADVICE should say so when a 4-card draw with 1 out exists.
- `advise` after the first miss (KS QH 8C 5C 44 22, 1 discard left) would again have discarded (it only values the Two Pair as a "floor" for the flush chase); it never prices "bank now + keep a discard for the final hand", which was the winning line here.
- Blind-select `s` ADVICE text "the Double Tag tag is not worth a shop visit" is correct but the reason is wrong at Gold: the Small pays $0, the shop visit is worth $4; the real reason to play is that 450/600 is worse than 300 for a jokerless deck.
Bridge issues: none; every command settled on the first try.
