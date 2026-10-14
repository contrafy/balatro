# Run YJGGELMB (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 7 blind The Manacle (25312/220000)

Ante 1 (300 Uncommon / 450 D6 / The Psychic 600, $4): Small: disc 4 off-suit for heart flush, drew broadway Straight 324 one-shot. Shop $6: Mystic Summit $5. Big: 2 discards to arm Summit, Two Pair QQJJ 1020 one-shot. Shop $7: Riff-raff{PERISHABLE} $6 (advisor UNKNOWN 20, overrode). Psychic: Riff-raff -> Green + Gluttonous; dealt FH QQQTT, discarded 1+1 to arm Summit, FH QQQ77 1932 one-shot.
Ante 2 (1000 Charm / 1500 Standard / The Hook 2000, $8): Celestial -> Mercury (Pair L2). Small: Riff-raff -> Shoot the Moon + foil Droll; dealt FH 1416 one-shot. Sold Green+Gluttonous at blind select -> Riff-raff made Clever + Splash. Big: Pair 9 + Splash fillers, QD held (Moon) 1920 one-shot. Shop $18: Uranus (2P L2), left $15 (advisor wanted Jumbo Celestial). Sold Splash -> Riff-raff made Wrathful. Hook: drew quad 7s while arming Summit, Two Pair JJ77 6936 one-shot.
Ante 3 (3200 Rare / 4800 Investment / The Needle 3200, $26): sold Wrathful, Jolly $3, Celestial -> Uranus (2P L3), Grabber $10 (4 hands). Skipped Small for Rare tag. Big: 2P TT66 + QD held 5550 one-shot. Sold perished Riff-raff; Rare tag = free Blueprint (ordered left of Summit: +30 mult with discards spent); Celestial -> Uranus (2P L4). Needle: 2 discards, spade Flush 7638 one-shot.
Ante 4 (9000 Charm / 13500 Investment / The Water 18000, $27): Death $3 (banked). Small: 2 junk discards, 2P TT55 + QQ held 16560. Shop $31: reroll, Jumbo Celestial (no Uranus) -> Earth. Big: 2P KK88 + QQ held 16974. Shop $31: reroll, Spectral -> Immolate (+$20), 2nd Spectral skipped (Ouija/Hex), reroll; no xMult in 4 views. Water (Summit live at 0 discards): Pair 7 3649 + 2P AAJJ 10836 + 2P 8866 13328.
Ante 5 (25000 D6 / 37500 Buffoon / The Mark 50000, $43): Celestial -> Uranus (2P L5), reroll -> Card Sharp{RENTAL} $1, sold Shoot the Moon, ordered Blueprint left of Card Sharp (x9 on a repeated type). Small: register 2P JJ22 3556, x9 2P AA22 32256. Big: register 2P TT77 3696, 2 discards to arm Summit, x9 2P 6633 64728. 4 rerolls over 2 shops: no 2nd xMult. Mark: no pair dealt; 2 discards -> AA + 2 face-downs + 4455 after Death (TS -> 5S); register 2P 5544 7192; then AA + 3 face-downs (65% exactly one face pair) -> x9 2P ~65k. Cleared.
Ante 6 (60000 Double / 90000 Coupon / The Mouth 120000, $33): sold foil Droll for Mr. Bones $5, Celestial -> Uranus (2P L6). Small: 2 discards -> AA444; register 2P AA44 6900, dig High (9 7 6 4 2), x9 2P KKQQ 64800. Shop: Justice $3, Buffoon -> Swashbuckler (sold Jolly; +12-15 mult). Big 90000: no pair dealt; discards -> KK; dig High; register 2P KK55 8240; dig High T873 (sim: keep AA J 9 = 73% pair) -> AAA JJJ; Justice Glass on AH, x9 2P AAJJ ~78k+ cleared (kept Mr. Bones). Shop: sold Mr. Bones for Brainstorm{PERISHABLE} $10 (copies leftmost Summit: +15). Mouth: lock 2P 5544 (solver p 0.68) 4796, 2 single-card discards to arm Summit x3, x9 2P JJ88 110448, x9 2P AA77 to close.
Ante 7 (110000 Ethereal / 165000 Coupon / The Manacle 220000, $12): Celestial (no Uranus, skipped). Skipped Small (Ethereal -> Talisman Gold seal) and Big (Coupon tag) because each needed 2 x9 hands I rarely assemble, and to save rent + a Brainstorm tick. Manacle (7-card hand): no second pair after 2 discards (solver p_clear 0.04 -> 0.00), dig, register 2P JJ66 12478, drew 555 with no two pair, dig, High Card x9. 25312/220000. GAME OVER.

## Post-mortem

Binding constraint: SCALING. My only real multiplier was Card Sharp (x3, copied by Blueprint for x9). It needs a repeat of the same hand type, so every x9 hand needs a fresh Two Pair. From ante 7 a blind needs one register plus two x9 Two Pairs (~110k each). That is 6 pairs in one round from 7-8 card hands with 2 discards. The Manacle (-1 hand size) made that close to 0% (solver 2-4% before the first discard). Flat scaling never caught up: Two Pair stayed at L6 because 3 of the last 4 Celestial packs had no Uranus. No second xMult turned up in ~12 shop views and 8 rerolls (offers were Baron perishable rental, The Order, Driver's License).

Decisions I would change:
- Ante 6 shop: I sold Mr. Bones for Brainstorm (+15 mult, +44% on x9). It was right for The Mouth (110448 + close). It would not have saved the Manacle anyway: 25% is 55k and I scored 25k.
- Ante 4-5: I spent ~$30 on 6 rerolls and 2 Spectral packs. The Immolate pack paid for itself. The rerolls only found Card Sharp (worth it). Cutting 2 rerolls and buying the Ante 2 Jumbo Celestial would have given +1 Two Pair level, about +10% on every hand. That is not enough to change the outcome.
- Ante 7 skips: neutral. Playing the Big would also have needed 4 pairs in a round. The real fix was earlier: get a second xMult that fires on every hand (any r/g xMult, Glass on main ranks, hand size).

What worked (reusable):
- Riff-raff at ante 1 ($6, perishable). It made 2 sticker-free Commons at each blind select. Selling weak Commons at BLIND_SELECT refilled the slots for free (Green/Gluttonous became Clever/Splash, Splash became Wrathful), and each sale paid $1-2.
- Mystic Summit on Gold's 2 discards: to arm it, discard ONE junk card at a time while you keep the made hand. Blueprint copying Summit was +30 mult, and Brainstorm on the leftmost Summit added another +15. Under The Water (0 discards) Summit is live from hand 1.
- Card Sharp + Blueprint directly to its left = x9 on every repeated type. The Mouth helps this engine because every hand is the same type.
- Death made the second pair for a Two Pair (TS -> 5S). Under The Mark, AA + 3 face-down cards holds exactly one face pair 65% of the time.
- Justice (Glass) doubles only the BASE hand mult, because cards score before the +mult jokers: about +20% here (74k -> ~89k). Use it to keep Mr. Bones unspent, not as a doubling.
- When digging, `raw` deck.remaining_by_rank shows which ranks are dead (no 3s or 7s left). I simulated which singles to keep (keep AA J 9 = 73% vs AA 3 = 43%).

Reusable if-then rules:
- IF Riff-raff is offered at ante 1-2 and you have free slots THEN buy it. Sell your weakest Common at blind select so it refills, and sell Riff-raff once it perishes.
- IF Mystic Summit is owned THEN spend both discards on 1-card junk discards before your scoring hand. Keep the made pair-family hand intact. Never sell Summit for a flat +mult joker.
- IF Card Sharp is your engine THEN put Blueprint directly left of it. Open each round with the cheapest Two Pair plus 1 filler and keep singles as pair outs. Count pairs: a blind that needs N x9 hands needs 2(N+1) pairs in the round.
- IF you own Card Sharp and the blind needs 2+ x9 hands THEN buy hand size (Juggler, even as a rental at ante 6-7) or a second unconditional xMult BEFORE that ante. Rerolls for a conditional xMult do not fix this.
- IF the next boss is The Manacle and your engine needs several repeated Two Pairs THEN treat it like a 2x boss and spend everything on hand size, levels or a flat xMult first.
- IF a Spectral pack offers Immolate and you have $10-30 THEN take it: +$20 for 5 random hand cards.

Advisor/CLI defects:
- shopadvise WARNING "upcoming boss The Water disables Mystic Summit": false. Summit fires when discards_left == 0 (card.lua:4081), so it is live all round under The Water.
- shopadvise BOSS PREP "The Mouth counters this build (it forbids repeating a hand type)": wrong. The Mouth forces ONE type, which suits Card Sharp. The Eye is the boss that forbids repeats.
- SCORE CHECK ignored an armed Mystic Summit and Blueprint copying it through ante 2-5 (e.g. Two Pair "~624" when it really scored 6936). That produced false EMERGENCY lines and "SELL then BUY: Mystic Summit is your weakest sellable joker" 4 times, with Summit+Blueprint worth +30 mult.
- Riff-raff was rated "UNKNOWN 20 / effect not in table". It is one of the best ante-1 buys (2 free Commons per blind).
- Pack advise said SKIP over Immolate ($22 -> $42 here).
- est undervalues Swashbuckler: x9 Two Pair JJ88 est 95580 vs actual 110448, and register 5544 est 3270 vs actual 4796 (Swashbuckler ab mult 15).
- Skip advice says "ante 5+: never skip". It does not consider that at Gold the Small pays $0 and a skip saves a rental charge and a perishable tick.
Bridge issues: none. Every action settled on the first try (171 steps).
