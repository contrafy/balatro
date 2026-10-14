# Run T7PPVCEX (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (17666/60000)

Ante 1 (Polychrome/Skip/The Hook 600, $4): Small: disc, FH 333TT 276 + Pair 44. Shop $5: Buffoon $4 -> Hanging Chad (over eternal Loyalty Card). Big: disc, Straight 7-high 276, disc, 2P KKJJ 160, Pair 66. Shop $5 (TIGHT 0.98x): Celestial $4 -> Mercury (Pair L2). Hook: disc, heart Flush 368, disc, FH 999QQ 428.
Ante 2 (Holo/Rare/The Flint 2000, $7): EMERGENCY 0.11: Smiley Face{PERISH} $4. Skipped Small (Holo; $3, 0.73x). Big 1500: Straight J-high JH first 1786 one-shot. Shop $9: Photograph $5 (SIM +0.53; passed holo Idol{RENTAL} $0). Flint: Pair JJ 4316 one-shot.
Ante 3 (Juggle/Standard/The Needle 3200, $11): shop: left with $11 (EMERGENCY 0.26 was Smiley perishing; SIM all +0.01). Small: disc, Pair QQ 6435. Shop $15: Invisible Joker $8 (SIM +0.35). Big: disc, Pair QQ 6435. Shop $14: Jumbo Spectral $6 -> Wraith -> The Order ($0). Needle: disc, Pair KK 6435. Sold perished Smiley + The Order, then Invisible -> second Hanging Chad (first face: Photograph x2 five times = x32).
Ante 4 (Top-up/Buffoon/The Window 18000, $15): Ramen $6 (SIM +0.18). Skipped Small for Top-up -> Half Joker + Clever. Big: High QC 5720, Pair TT 3910, disc, High KH. Shop $14: Arcana -> Temperance (+$13), Celestial -> Pluto (High Card L2). Window: High QH 10646 x2.
Ante 5 (D6/Buffoon/The Eye 50000, $28): Spectral -> Medium (purple seal 2C), Jumbo Celestial -> Uranus. Small: 2P QQ22 34444 one-shot. Shop $23: Mega Spectral $8 -> Talisman (gold seal QC: $15 per first-card play) + Trance (blue seal 4C). Big: disc, FH QQQ44 gold QC first 48407 (+$15). Shop $41: Buffoon -> Sly{PERISH} (sold Clever), Buffoon skipped, 2 rerolls (nothing). Eye: 2 discards (purple seal -> Tower), Tower 3C stone, 2P QQTT+stone 38438, High QC 9937, Pair KK -> cleared.
Ante 6 (Garbage/Juggle/The Serpent 120000, $49): ratio 0.39. Buffoon (eternal Joker/Fortune Teller, skipped), Overstock $10, Standard (no face, skipped), 2 rerolls (nothing). Left $20. Small 60000: no face pair in 3 hands + 2 discards (High Q 9937 best start; 2 digs drew AA, then TT, then nothing): 731 + 224 + High KD+Stone 16711 = 17666. GAME OVER.

## Post-mortem

Binding constraint: scaling, and a single-card engine. Everything multiplied ONE card: the first scoring face card
(Photograph x2 triggered 5 times by two Hanging Chads = x32 on the BASE hand mult only, then Half +20, Ramen x1.73-2).
That made antes 2-5 trivially one-shot (6435 at ante 3, 34-48k at ante 5) but the output was capped by base mult 2-3
and ~65-135 chips: a face High Card ~10k, face Pair ~29k, face Two Pair ~30-38k. Ante 6 Small (60000) needed two face
pairs in one round; with 12 faces in 52 cards and Ramen eating every discard, a round without a face pair scored 18k.
No joker-phase xMult besides Ramen, no copier, no level investment (Pair L2 at ante 6), no enhanced face cards.

Decisions I would change:
1. Ante 4-5 shops: I kept $15-24 for "interest/next xMult" three shops in a row and passed a Jumbo Standard ($6), Odd
   Todd (+0.10), Celestial packs and Mr. Bones (+0.15). With a 5-trigger first card, every enhancement/edition on a face
   card (Glass x32, Mult +4/trigger ~x4, Bonus +150 chips, Holo +50 mult) and every Pair/High Card level is worth far
   more than interest; the money ($49 at ante 6) bought nothing that scored.
2. Ante 3: Wraith ($8) gave The Order which I sold; the $8 in Celestial/Arcana packs would have scaled base mult.
3. Ante 5 Talisman on QC was the right money play (+$15 per first-card play, +$30 that ante), but the cash then had
   nowhere to go: Arcana packs never appeared in ante 5-6 shops. Earlier (ante 4) Arcana/Celestial buys were the window.

Reusable rules (if-then):
- IF you own Photograph + Hanging Chad, THEN your score is (first face card's triggers) x BASE hand mult: level the
  hand you open with (Pluto doubles a High Card's base mult 1->2) and enchant FACE cards (Empress/Hierophant/Justice/
  Aura/Talisman); joker-phase +mult jokers add only linearly. Track how many faces remain in the deck.
- IF Invisible Joker is ready and you own 1-2 key jokers among junk, THEN sell the junk/perished jokers first so the
  random copy lands on a key joker (here 2 of 2 candidates were good: copied Hanging Chad -> first face x32).
- IF a hand's score depends on drawing a specific card class (a face), THEN the ante-6 Small already needs ~2 of those
  per round: by ante 5 add a second source that does not need the draw (Pareidolia, a joker-phase xMult, levels).
- IF money >= $25 at ante 5 and the next-ante ratio is < 0.7, THEN spend it at ante 5 (packs that level or enchant
  the engine), not at ante 6: the ante-6 Small comes before the next good shop.
- Gold seal (Talisman) on the retriggered first face pays $3 per trigger ($15 per play with 2 Chads).

Advisor/CLI defects:
- Ante 3 SCORE CHECK said EMERGENCY 0.26 while the next ante was cleared by one-shots (it counted Smiley perishing but
  missed Invisible's pending copy: 6435 -> ~20k/hand).
- Pack/shop SIM repeatedly proposed selling Half Joker (+20 mult on my 1-3 card plays, +31% on a face High Card) for
  Sly/Mr. Bones/Wily; Clever (Two Pair only) was the right sale.
- Two commands right after `sell`/`skippack` were refused as NOT LEGAL with the pre-action phase (PACK_OPENING) shown:
  the CLI read a stale state; `sleep 2-3` then the same command worked (steps 93-94, 112-113).
- `advise` filler suggestions for Pair plays with Half Joker owned (e.g. `play PAIR 2 3 8 7 6` at the Flint) would
  have dropped Half Joker's +20 by playing 5 cards; I played the 2-card pair.
