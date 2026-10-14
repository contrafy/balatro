# Run A5LJXXMW (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 8 blind Crimson Heart (275896/400000)

Ante 1 (D6 / Polychrome / The Window 600, $4): Small jokerless: 2P KK99 116, dig Pair 22 (dump KD TH) -> spade Flush 288. Shop: overrode Even Steven{ETERNAL,RENTAL} for Buffoon $4 -> Lusty{ETERNAL} (over Droll{PERISH}). Big: 2P KKJJ 480 one-shot. Window: FH 222KK 540 + 2P JJ44 384.
Ante 2 (Skip / Juggle / The Needle 1000, $13): reroll -> Odd Todd{PERISH} $4, Egg{PERISH} $4. Skipped Small (Skip tag +$5, $0 payout). Big 1500: FH AAAJJ 1302 + FH QQQ66 574. Shop $11: Hermit -> $16, reroll -> The Duo{ETERNAL} foil $10, Zany{PERISH,RENTAL} foil $1. Needle: disc 5 keep 77 -> 2P 77+22 (2H) 2000 one hand.
Ante 3 (Ethereal / Handy / The Pillar 6400, $2): shop $2 nothing. Small: disc x2 -> Trips QQQ 5760 (3 cards, Pillar). Shop: sold Egg $11, Misprint $4. Big: Trips TTT one-shot. Shop $12: Fool -> Hermit held. Pillar: 2P 9922 5712 + Pair 77 2604.
Ante 4 (Buffoon / Garbage / The Flint 18000, $13): sold perished Odd Todd, Hermit $15->$30, Buffoon -> Swashbuckler, reroll, Strength (held), Jumbo Arcana -> Chariot Steel 4S. Skipped Small for Buffoon tag (Mega): sold Zany, took Throwback (x1.5, 2 skips) + Hologram{ETERNAL}. Big 13500: 2P 3322 7920 + 2P QQJJ. Shop $20: Standard -> 9D blue seal (Holo x1.25), Jumbo Celestial -> Mercury (Pair L2).
Flint 18000: 2P QQ33 5482, disc 4 -> FH AAAJJ 16605.
Ante 5 (Investment / Buffoon / The Wheel 50000, $18): Mega Standard -> 8H steel+blue seal, QD lucky (Holo x1.75), Celestial -> Mercury (Pair L3). Skipped Small (Investment) and Big (Buffoon; Throwback x2.0): Mega Buffoon -> sold Misprint, Half Joker. Wheel: Pair 22 27636 + Pair 44 (4H) ~28.8k. $40 after cash (Investment $25).
Ante 6 (Ethereal / Uncommon / The Eye 120000, $40): Celestial -> Mercury (L4), Arcana -> Fool -> Mercury (L5), 2 rerolls nothing. Skipped Small (Ethereal; Throwback x2.25): Grim -> 2 enhanced Aces (Holo x2.25). Big 90000: Pair 88 66784 + Pair TT. Shop $30: Jumbo Buffoon -> sold Swashbuckler, Brainstorm{ETERNAL} copying Half Joker (leftmost); 2 rerolls; Pluto (High Card L2 for the Eye). Eye: Pair KK 69457, disc 5 keeping 55+AC -> Trips AAA 52629 (cleared).
Ante 7 (Uncommon / Handy / The Plant 220000, $20): 2 Standard -> 4S blue seal, JH steel (Holo x2.75). Small 110000: Pair 22 70587 + Pair JJ. Shop $15: Arcana -> Temperance (+$20), Buffoon junk, 2 rerolls. Skipped Big (Handy tag +$25; Throwback x2.5). Plant: Pair TT 94325 + Pair QQ (debuffed) 75900 + Pair 99 ~87k = cleared.
Ante 8 (Foil / Double / Crimson Heart 400000, $51): Jumbo Celestial (no Mercury) -> Venus, Buffoon junk, 5 rerolls nothing useful ($6 left). Skipped Small and Big (Throwback x3.0).
Crimson Heart: Throwback (x3) disabled on hand 1 -> Pair 66 43741 banked; Brainstorm disabled on hand 2 -> 2 discards + Strength (JH->QH, TS->JS) -> Pair QH QH 108570; Lusty disabled on hand 3 -> Pair JS JS 123585. 275896/400000. GAME OVER.

## Post-mortem

Binding constraint: SCALING for the 3x-per-hand final boss. The engine (Pair L5, Half Joker + Brainstorm copy = +40,
The Duo x2, Throwback x3, Hologram x2.75, 2-3 Steel cards held) made ~124k on a clean hand with two steels held; the
400k boss needed ~133k on EVERY hand, and Crimson Heart cut the first hand to 1/3 (Throwback off) and the second by
~30% (Brainstorm off). Realistic max was ~300k. Reached the ante-8 boss with 0 lost blinds; 8 blinds skipped.

Decisions I would change:
1. Ante 6-8 shops: I spent ~$60 on 9 rerolls that found nothing (Madness, Jolly, rentals). The same money as
   Standard packs (Hologram +0.25 each, ~+9%) or Celestials for Mercury was the better sink; rerolls only change the
   two card slots. With 3 eternal slots (Lusty, Duo, Hologram) plus Brainstorm, I had 2 flexible slots, so a joker
   find had to beat Half Joker/Throwback: rerolling for jokers was nearly hopeless.
2. Ante 1 Lusty Joker{ETERNAL} from a forced Buffoon pick: a permanent weak slot all run. It saved ante 1-2, but an
   eternal +3/heart joker is a 6th-slot tax at ante 8 (a Baron/Cavendish/second xMult never had a home).
3. Ante 8: skipping Small and Big (Throwback 2.5 -> 3.0) was right (my 3-hand total ~280k would not have cleared
   the 300k Big), but it meant only ONE shop in ante 8. I should have used the ante-7 Small shop money on two more
   Standard/Celestial packs instead of rerolls.

Reusable if-then rules:
- IF you own Throwback, THEN every $0 Small Blind skip (Red+ stake) is +x0.25 permanently AND removes a blind;
  skip Small at every ante where the tag/shop is weak and your typical hand clears the Big at >=1.3x. 8 skips here
  took Throwback to x3.0, the biggest multiplier in the build.
- IF you own Hologram, THEN Standard packs ($4, +0.25 per card taken; Mega = +0.5) beat rerolls ($5-9) every time;
  Grim (2 enhanced Aces) from a Spectral pack is +0.5 too.
- IF you own Brainstorm and Half Joker, THEN put Half Joker leftmost: Brainstorm copies its +20 (pairs/trips only,
  <=3 cards played, so never add fillers beyond 1).
- IF the boss is The Eye with a Pair main, THEN play your best Pair first, keep 2 discards to dig for Trips (Strength
  turns X-1 into X), and use High Card (Half Joker +40, foil Duo +50 chips) as the 3rd type (~17k at ante 6).
- IF Crimson Heart disables your biggest xMult on hand 1, THEN bank a made pair without spending discards (they do not
  re-roll the disabled joker); save discards and rank-up tarots for the hands where the xMult is back.
- IF a Fool is offered after you used Hermit/Mercury, THEN it is a second Hermit (+$9-20) or a second main-hand level
  for $3 (used twice here).
- IF Egg is perishable, THEN it is still a good $4 savings account: sell it before it perishes (+$7 here).

Advisor/CLI defects:
- `shopadvise` run right after a buy/reorder printed the PREVIOUS state twice (step 30 after buying The Duo showed
  $11 and "buy 2 The Duo"; after reordering Misprint it printed "ORDER FIRST b order 3 5 1 2 4" for the old order).
  Running it again fixed it.
- At ante 1 `shopadvise` labelled Even Steven{ETERNAL,RENTAL} "an xMult you cannot afford" and counted the owned
  Lusty Joker as "0 scoring jokers alive next ante".
- `advise` Misprint range note was wrong: "roll 0 -> 105" for a Pair 22 whose real floor was ~456.
- Blind-select ADVICE always says "do not skip ... ante 5+" even when you own Throwback (each skip +x0.25) and the
  Small Blind pays $0; the skip logic ignores Throwback entirely.
- Pack `advise` rated Throwback "useless, we never skip" while it was x1.5 already; it still ranked it first.
- `advise` at Crimson Heart hand 1 advised discarding 4 to dig while Throwback (x3) was disabled for that hand
  regardless; banking the made pair and saving discards for the x3 hands was better.
- SOLVER p_clear >=0.99 at the ante-6/7 Small blinds and 0.85 at The Eye were reasonable; no overconfidence seen.
Bridge issues: one CLI call sent in parallel with endshop returned "NOT LEGAL NOW: SELECT_BLIND is not available in
SHOP. Nothing was sent" (race on my side); no rejects otherwise.
