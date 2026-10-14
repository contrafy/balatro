# Run FNL2JWDL (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 7 blind The Eye (18640/220000)

Ante 1 (Skip/Skip/The Pillar 600, $4): Small: 2P 3322 60, disc x2 (flush miss), 2P QQJJ+filler 120, Straight 9-5 260. Shop $4: Buffoon -> Credit Card (overrode Droll{PERISH}), reroll to -$5, foil Faceless $6 (+50 chips). Big: 2P 8844 188 + 2P QQ66 204 + Pair 22. Shop: foil Fortune Teller{RENTAL} $1 (2nd +50 chips). Pillar: 2P TT33 280 + Straight T-6 596.
Ante 2 (Orbital(2P)/Skip/The Mark 2000, $-5): EMERGENCY 0.21: reroll -> Clever{ETERNAL} $4 (-$14). Skipped Small (Orbital: Two Pair L1->L4) and Big (Skip Tag +$10, -14 -> -4). Mark: disc 4 low, drew to 5 face-downs = guaranteed 2P+ (5 faces in 3 ranks) 1500, disc, 2P 7733 1400.
Ante 3 (Standard/Standard/The House 6400, $-1): EMERGENCY 0.24: Photograph $5; sold Fortune Teller rental, Bloodstone $7 (-$12). Small: disc 5 spades, disc to hearts, heart Flush QH-first 2160 (Bloodstone fired), 2P 9933 1755. Shop: Walkie Talkie $4. Big: 2P 9977+filler 1815, disc, 2P JJ22 3510. Shop: sold Walkie, Hanging Chad{PERISH} $4 (-$12). House: blind 5-card dig 152, disc 5, disc 3, moved KD leftmost -> Straight A-T K-first 7248 (est 4832, Bloodstone x1.5).
Ante 4 (D6/Foil/The Arm 18000, $-6): sold Faceless -> Mystic Summit $5; Jumbo Arcana $6 -> Justice on KH (glass). Small 9000: disc 4, disc 3 (arm Summit), moved QH first -> 2P QQ55 31500 (est 11550; Bloodstone). Shop: Buffoon $4 -> sold Summit, Brainstorm{PERISH,RENTAL} (copies Photograph leftmost: x4 per trigger). Skipped Big (Foil; saves Chad/Brainstorm perish ticks + rent). Arm: disc 4, Straight J-7 J-first 54144 (est 24064).
Ante 5 (Standard/Double/The Serpent 50000, $-10): Foil-tag Jolly $0 (sold Bloodstone). Boss-only plan: skipped Small (Standard pack -> steel AS + JH) and Big (Double) to keep Chad (2 rounds) alive for Serpent + ante-6 boss. Serpent: disc 3, 2P QQ22 Q-first with steel AS held, one hand (est 123952).
Ante 6 (Charm/Top-up/The Tooth 120000, $-3): Jumbo Arcana -> Temperance (+$10), Jumbo Celestial -> Saturn (no Uranus), 1 reroll (nothing). Skipped Small (Charm x2 via Double: Justice -> glass KC, High Priestess -> Uranus+Mercury, Justice -> glass QH, Temperance) and Big (Top-up wasted, slots full). Tooth: disc 5 -> glass KH KC drawn, Pair KK 2 cards (est 354200) one-shot. Chad perished.
Ante 7 (Juggle/Uncommon/The Eye 220000, $2): sold dead Chad, 2 rerolls (nothing), Arcana -> Strength (TT -> JJ), Celestial -> Uranus (2P L6). Skipped Small (Juggle +3 hand size) and Big. Eye: best hand est ~10k without Chad: FH JJJ66 5088, 2P AAQQ 10512, Pair QQ 3040 = 18640/220000. LOSS.

## Post-mortem

Binding constraint: SCALING that was entirely perishable. From ante 3 to 6 the engine was Photograph + Hanging Chad{PERISHABLE}
(+ Brainstorm{PERISHABLE,RENTAL} copying Photograph from ante 4): a face card leading the hand got x2 three times (x8), then
x4 three times (x64) with Brainstorm, and glass faces doubled that again. It one-shot the Arm (54k), Serpent (124k) and Tooth
(354k). When Chad perished after the ante-6 boss the same deck dropped to ~10k per hand (x4 on the lead face only) against
110k-220k at ante 7. Money was negative from ante 1 to the end (Credit Card debt, -$15 at the Eye), so the last two shops had
$20-24 of buying power and saw no retrigger/xMult joker in 6 joker slots (2 rerolls each).

Decisions I would change:
1. Ante 1: Credit Card over Droll was right for survival (it bought foil Faceless, foil Fortune Teller, Clever, Photograph,
   Bloodstone, Chad), but I treated -$20 as free money for 6 antes: I never earned $1 of interest and every late shop started
   at ~$0. Once Chad/Photograph were found (ante 3) I should have stopped buying flat stuff (Walkie, Celestial/Arcana gambles)
   and climbed back above $0.
2. Ante 4/5: skipping all Small/Big blinds from ante 4 Big on kept the perishables alive for the bosses (good), but it also
   removed 5 shop visits. The ante-5/6 shops were where a permanent replacement for Chad had to come from; with $0 and no
   shop visits there was no chance. Better: play the Small blinds while Chad was still fresh (ante 5 Small 25k was a
   one-hand clear) for the shop, and skip only once Chad was down to its last 1-2 rounds.
3. Ante 6 Jumbo Celestial ($6, got Saturn) and ante 7 Celestial/Arcana: levels/glass cannot replace a x8 retrigger; that money
   ($10) was one more reroll.

Reusable rules (if-then):
- IF you own Photograph AND a first-card retrigger (Hanging Chad) THEN `move hand` the face you want to lead (a Glass or heart
  face) to the leftmost played position before every play: Photograph fires on each retrigger. Verified: Straight K-first
  7248 (est with A-first 1224), 2P QH-first 31500, Pair glass KK 354200 vs 120000.
- IF you own Photograph THEN Brainstorm (copy leftmost) with Photograph leftmost doubles the face x2 on every trigger
  (x4 per trigger, x64 with Chad). Blueprint to Photograph's right does the same.
- IF your whole multiplier is perishable THEN skip Small/Big blinds only to spend its last rounds on bosses; while it has 3+
  rounds left, play the Small blind for the shop and spend that shop on a permanent replacement.
- IF The Mark shows 5+ face-down cards THEN they are all J/Q/K, 5 of them always contain Two Pair or better: play all 5.
- IF The House deals all 8 face-down AND one hand clears the blind THEN play 5 unknown cards as a dig (keeps discards).
- IF The Tooth AND a 2-card pair clears THEN play just the pair (glass KK cost $2).
- IF Credit Card is your only way to buy THEN never "sell CC then buy": selling at negative money leaves you unable to buy.

Advisor/CLI defects:
- shopadvise said "SELL then BUY -> b sell 2 (Credit Card) then b buy" twice (ante 4 Mystic Summit at -$6, ante 6 Scary Face at
  -$3): selling Credit Card while in debt makes every buy impossible. CC should never be the sell candidate when money < price.
- shopadvise ranked Director's Cut ($10) BOSS PREP at -$8 money with Credit Card: its $10 boss rerolls would be unaffordable.
- SCORE CHECK / est ignore first-card retriggers and leading-face order: ante 4 score check ~4240 while the real hands were
  31500 and 54144; ests were 2-4x low (11550 vs 31500, 24064 vs 54144) whenever Hanging Chad + Photograph led with a face.
  `advise` never suggests `move hand` to put a face/glass card first (House: it advised a 3-card dig; K-first straight cleared).
- SIM line ante 1: "buy Egg{ETERNAL,RENTAL} p_next 1.00 vs 0.01 baseline" (nonsense; Egg adds no score).
- Solver p>=0.99 calibrated for ante 4/5 discards that relied on finding a face; real outcomes were fine but the numbers look
  uncalibrated with Chad (n=64-100).
- Tags show as `Juggle Tag([poker hand])` (placeholder text).
Bridge issues: one `NOT LEGAL NOW` (my pack slot index after a pack was bought; nothing sent); one auto-retried "not settled".
