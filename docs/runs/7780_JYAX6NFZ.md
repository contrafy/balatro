# Run JYAX6NFZ (port 7780) - LOSS at ante 1 Big Blind

Stake 1 (White), Black Deck.

Ante 1: Small Blind 300 (tag Investment), Big Blind 450 (tag Rare), Boss The Psychic 600. Starting $4, no jokers.
- Small Blind: dealt AD KS QS JH TS TD 5H 2H -> STRAIGHT (A-K-Q-J-T) idx 1-5, advise est 324 >= need 300. Played, scored 324. Cashed out, $9.
- Shop: shopadvise -> BUY Hiker $5 (+5 chips/scored card, permanent). Bought. Then shopadvise -> BUY Buffoon Pack $4 (joker choice). Bought ($0 left). Pack offered Wily Joker (+100 chips if Three of a Kind) vs Walkie Talkie (+10 chips/+4 mult per 10 or 4). Picked Wily Joker (flat conditional chips seemed stronger than rank-specific). Jokers: Hiker, Wily Joker. shopadvise -> LEAVE (no money). endshop.
- Big Blind (need 450): dealt two/three-pair-heavy hands throughout (K/J pairs, then Q/9, then 9/6/5, then T/5). Never drew a Three of a Kind, so Wily Joker never fired all round (dead joker slot). advise/hands guided every play/discard:
  - disc 5,6,7,8 (keep KK JJ) -> hands 3,disc 2
  - disc 5,6,7,8 (keep KK JJ) -> hands 3,disc 1
  - PLAY TWOPAIR 1 2 4 5 8 (KKJJ, filler 8) est 120, actual 120. scored 120/450, hands 2 disc 1.
  - Redraw gave QQ99. advise recommended DISCARD 1 2 4 8 to chase a straight draw (5-6-8-9 held) because two projected two-pair plays (232) still < need (330). Followed. Straight did not complete; landed on 9,9,6,6,5,5 three-pair hand instead.
  - PLAY TWOPAIR 2 3 5 6 7 (99/66, filler 5H) est 100, actual 100. scored 220/450, hands 1 disc 0.
  - Final hand JC TS TH 8C 5C 5D 4S 3S, no discards left. PLAY TWOPAIR 2 3 5 6 8 (TT/55, filler JC) est 100, actual 100. Final scored 320/450. GAME_OVER.
- est matched actual on every hand this run (no >20% deviation to report).

Post-mortem: binding constraint was scaling/luck, not misplay. Zero xMult and, more importantly, no two-pair-scoring joker was ever offered in the ante-1 shop (only a Three-of-a-Kind conditional joker and a rank-specific one were on offer); the actual hand type produced all round was Two Pair, so Wily Joker never fired and was a dead slot for the entire blind. Base Two Pair L1 (~100-120/hand per playbook table) times 3 hands (~320-360 max) cannot clear a 450 Big Blind without a matching joker or a leveled hand, and Black Deck's 3-hand/3-discard limit gives no room to fish for a better shape once behind. The one decision I would change: with only $9 total across the ante-1 shop and no Two-Pair or generic +mult joker on offer, there was no purchasable fix; if forced to pick differently, Walkie Talkie might have contributed on the several 10s seen, but it is equally conditional per playbook guidance (rank-specific, not type-specific) so likely would not have changed the outcome either.

Bridge issues: none. All `ACTION` calls succeeded on first try, `advise`/`hands`/`shopadvise` outputs were internally consistent, and every `est` matched the actual score exactly.

Playbook suggestions:
1. Section 5 (ante 1-2 shop) could note explicitly: if the only joker choices in a pack are hand-type-conditional (Wily/Mad/Jolly/etc.) and none matches the hand shape you are actually drawing (check `hands` history, not just current hand), a generic flat +mult/+chips joker (or even a rank-specific one like Walkie Talkie) may be safer than a mismatched conditional joker that can go the whole blind without firing.
2. Section 7 "verified numbers" table could add: Two Pair L1 with no matching joker averages ~100-120/hand in this harness (confirmed again here: 120, 100, 100) — three such hands (~320-360) reliably fail a 450 Big Blind, reinforcing that ante-1 Big Blind essentially requires either a joker that scores your actual hand type or a made hand better than two pair.
