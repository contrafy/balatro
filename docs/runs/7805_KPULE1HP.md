# Run KPULE1HP (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 2 blind Big Blind (1042/1500)

Ante 1 (Small 300 Foil / Big 450 Double / The Psychic 600, $4): Small jokerless: dealt diamond Flush 268 + Two Pair AA66 108 = 376. Shop $5 (Crafty, Clever{ETERNAL}, Buffoon, Celestial): Clever{ETERNAL} $4 per ADVICE, $1. Big: Two Pair 9944 252 + QQJJ 280 = 532. Shop $6 (Banner{ETERNAL}, Temperance, Arcana, Mega Celestial): Banner{ETERNAL} $5 (only scorer), $1. Psychic: disc 5 around 99 -> 99922, Full House 724 one-shot.
Ante 2 (Small 1000 D6 / Big 1500 Charm / The Window 2000, $8): shop (Hanging Chad{PERISHABLE}, Pareidolia{PERISHABLE}, Arcana x2): left with $8 (override of Hanging Chad). Small: Two Pair KKQQ 400, disc 3 for T987 straight draw -> Two Pair TT88 332, Two Pair AA99 340 = 1072. Shop $9: Uranus (Two Pair L2), $6. Big 1500: disc 5 around TT -> Two Pair QQTT 570; disc 4 keeping 66+A+K -> Two Pair KK66 456; last hand AD KD QS 7D 6C 5H 4S 2C no pair, High Card 16. 1042/1500. GAME OVER.

## Post-mortem

Binding constraint: zero mult. Both jokers were chips-only Eternals (Clever +80 on Two Pair, Banner +30 per unused
discard), so every hand ran on base mult 2-3. Two Pair L2 maxed at ~630 with both discards held and ~450 once both
were spent; 1500 in 3 hands needed three Two Pairs AND unused discards, which is a contradiction (you discard to find
the Two Pairs). Banner and "discard toward a bigger hand" are anti-synergistic: each discard cost 90 points per
remaining hand at mult 3. Four shops offered zero +mult jokers (Crafty, Clever, Banner, Hanging Chad, Pareidolia,
Reserved Parking).

Decisions I would change:
- Ante 1 shop 1: take the Buffoon Pack (advisor rank 78) instead of Clever{ETERNAL} (rank 67, but the ADVICE line
  chose it). A pack offers 2 jokers, one plausibly +mult; Clever is chips-only and eternal.
- Ante 1 shop 2: Banner{ETERNAL} was a second chips-only eternal. Keeping $6 (-> ~$12 at the ante-2 shop) to buy a
  +mult joker or a Buffoon pack would have scaled better; the Psychic was cleared by a Full House anyway.
- Ante 2 shop 1 ($8): with EMERGENCY flagged and no mult on offer, I left. Defensible, but the D6-tag Small Blind
  shop then offered only Uranus; the money never turned into mult.

Reusable if-then rules:
- IF your scoring jokers are all +chips (Clever, Banner, Sly, Scary...), THEN the next buy must be +mult or xMult;
  never buy a second chips-only joker at ante 1, and never a chips-only Eternal when a Buffoon pack is affordable.
- IF you own Banner, THEN count each discard as -30 chips x mult on every remaining hand; at mult 2-3 a discard costs
  60-90 per hand, so discard only when the current best hand cannot reach its share even with Banner's full bonus.
- IF ante 2 Big Blind (1500) with Two Pair as the only real hand and mult <= 3, THEN you need ~500/hand: this is only
  feasible with a +mult joker; buy one (or a Buffoon pack) in the ante-2 first shop even through the $8 floor.

Advisor/CLI defects:
- shopadvise ante 1 shop 1 ranked "78 pack 1 Buffoon Pack" above "67 buy 2 Clever Joker{ETERNAL}" but the ADVICE line
  said `buy 2` (Clever): ranking and ADVICE disagree. NEEDED NOW should prefer a pack that can yield +mult when the
  only offered scorer is chips-only.
- shopadvise does not treat "all scorers are chips-only" as a gap: it recommended Banner (2nd chips joker) as NEEDED
  NOW and Hanging Chad (retrigger, ~+40/hand at mult 2) as the EMERGENCY buy.
- advise discard suggestions ignore Banner's chip loss when comparing "discard" vs "play" (PACE line uses current est
  for later hands, not the post-discard Banner value); it also kept a random low card (4H, 2H) in 5-card discards
  instead of the highest kicker.
Bridge issues: none; 30 steps, all settled first try (one NOT LEGAL from my own command ordering, nothing sent).
