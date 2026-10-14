# Run BRILA2MW (port 7812, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Big Blind (88167/90000)

Ante 1 (Polychrome/Boss Tag/The Manacle 600, $4): Small: FH 777KK 324 one-shot. Shop $6: Blue Joker{ETERNAL} $5 (+2 chips/card in deck = +104 chips, SIM +0.43). Big: Pair QQ 236 + Trips AAA 423. Shop: Greedy{RENTAL} $1 (+3 mult/diamond; single diamond High Card est 424). Manacle: High AD 424 + High TD 388.
Ante 2 (Boss Tag/Buffoon/The Fish 2000, $8): Small: Straight 1155 one-shot. Skipped Big for Buffoon tag: Mega pack (choose 2) -> holo Space Joker (+10 mult, 1/4 level) + Jolly{PERISH}. Fish: Pair 33 2392 (Jolly+Space+Blue+Greedy).
Ante 3 (Investment/Boss Tag/The Tooth 6400, $13): sold Greedy -> Blueprint{RENTAL} $1, Celestial -> Uranus, skipped Small (Investment +$25 after boss). Big 4800: Pair 66 3960 + High KH 2013 (Blueprint LEFT of Blue Joker copies +88 chips: advisor ORDER FIRST +25%). Shop: Abstract{PERISH} $4. Tooth: Pair KK 7210 (-$2).
Ante 4 (Coupon/Buffoon/The Wheel 18000, $35 with Investment): Buffoon -> Dusk, Grabber $10 (4 hands), Arcana -> Tower (stone). Skipped Small (Coupon). Big 13500: Pair 77+stone 10335 + High AD 5460. Coupon shop (free): Venus, Pluto, Emperor (-> High Priestess -> Earth), Jumbo Standard (red-seal TH). Reroll -> sold Dusk -> Swashbuckler{foil} $6. Wheel: single High KC 10865 + Pair 88 13083 (single-card plays keep the deck full for Blue Joker).
Ante 5 (Polychrome/Handy/The Psychic 50000, $19): EMERGENCY 0.28 (8.3k/hand vs 25k Small). 2 rerolls + Judgement -> Clever. Skipped Small for Polychrome tag; Big 37500: Flush 13029 + Pair TT 11130 + Flush 11653 + High 9114 = 37029+. Free polychrome Sly{PERISH} (sold Clever). Psychic: Star -> diamonds, Flush D 26367 + Pair QQ 20130 + Two Pair 20328 = 50000+.
Ante 6 (Holo/Charm/The Water 120000, $13): sold perished Abstract, Even Steven{E} $4, Hermit $7->$14, 1 reroll nothing. Small 60000: Two Pair KK88 19584 (+Space level Two Pair L4), Pair 12720, Two Pair TT66 25437, Pair 99 -> 60000 cleared (4 hands, 2 discards). Big 90000: Two Pair TT22 25137, discards (kept pair 77), Two Pair TT77+stone 24402, Two Pair 6644 22059, last hand FH QQQKK 16569 (needed 18402): 88167/90000 -> LOSS.

## Post-mortem

Binding constraint: scaling. 0 xMult all run: score came from flat chips (Blue Joker +2/card in deck, x2 via Blueprint) + flat mult (Space holo +10, Swashbuckler, Even Steven) and ONE x1.5 (free polychrome Sly from a Polychrome tag). Per-hand ~15-25k at ante 6 against Big 90k / boss 120k (needs 22-30k per hand) = ratio ~1.0. Lost the Big by 2% (1833).

Decisions I would change:
1. Blue Joker counts CARDS REMAINING IN DECK (est drops as you draw). Ante 6 Big: I played 5-card plays with fillers and discarded 6 cards, deck went 45 -> 24, Blue chips 90 -> 48 (x2 with copy). With 1-3 card plays the deck would have stayed ~35+ and the last FH would have been ~+8% (needed +11%): the loss was within noise of this. IF you own Blue Joker THEN play only scoring cards (no fillers) unless the filler draw is needed to find the hand; single-card High Card (L3) plays cost 1 card and scored 10-11k each.
2. Skipped the ante-4 Small for a Coupon tag whose shop was weak (free Venus/Pluto/Emperor/Standard); I would have had two shops with $17 to dig for an xMult. With 0 xMult at ante 4, skipping shops is a loss (PLAYBOOK says so; I trusted advisor ADVICE: skip).
3. Never found an xMult in ~6 rerolls/4 Buffoon/Arcana looks; the free Judgement was Clever. I never had the money (floor $8 reached by buying a flat joker each shop). Should have kept more cash for rerolls at ante 4 ($35 at the start of that shop was the only rich moment; I spent $10 Grabber, $8 packs).
4. Ante 6 Big: at 49539/90000 with 2 hands and no discards I played the 4-card 6644 two pair + a filler; fine. The earlier decision to discard 3 cards (keep pair, solver p 0.32 vs 0.40 to break it) and the second discard cost nothing identifiable.

Reusable rules (if-then):
- IF you own Blue Joker (+2 chips per card in the DECK) AND Blueprint, THEN put Blueprint directly left of Blue Joker (+88-106 chips) early; at ante 5+ re-check `ORDER FIRST` because copying Swashbuckler/Abstract (+13 mult) beats Blue once the deck shrinks.
- IF Blue Joker is owned THEN every card you draw lowers est: prefer 1-3 card plays (High Card L3 single = 10-11k at ante 4-5, same as a Pair).
- IF a Polychrome/Holographic/Foil tag is on the Small THEN the free edition joker appears in the NEXT shop (after the Big): a free polychrome Sly (x1.5 on all mult) lifted 66k -> 106k round est; place it rightmost, +mult jokers left of it.
- IF a Buffoon tag sits on the Big at ante 2 and you own 2 scorers THEN skipping it gives a Mega Buffoon (pick 2): got holo Space Joker + Jolly, scored 2392 vs Fish 2000 at once.
- IF Space Joker (1/4 level up) is owned THEN it leveled Two Pair to L4 and High Card/Flush/Pair repeatedly: play varied pair-family types each round and the est (which ignores it) is a floor, not the mean.
- IF The Psychic is the boss THEN use The Star (3 cards -> diamonds) etc. to make a 5-card Flush hand; every play is 5 cards anyway.
- IF a Charm/Coupon-type skip tag appears at ante 4+ with 0 xMult THEN prefer playing the blind and shopping with money: free-shop tags only help when the shop has jokers.

Advisor/CLI defects:
- shop SIM prints "+0.00 vs buying nothing" for every option when P(clear 3 blinds)=1.00 (saturated) even at 1.11x TIGHT; it said LEAVE at ante 3/4 shops where Abstract (+15 mult, +75% est) was clearly right (I overrode and it carried the Tooth and the Wheel).
- `s`/advise recommended `b skip` for ante-4 Small (Coupon) although the SCORE CHECK was 0.42-0.75 with 0 xMult; the skip lost a shop at the only point I had $35.
- `est` ignores Space Joker level-ups and red-seal retriggers differently (Psychic Pair est 20130 actual 21600; Small est 15k vs actual), so pace lines (PACE: ... < need) are pessimistic by ~5%.
- ORDER FIRST printed twice for orders that change which joker Blueprint copies; fine, but it does not mention that Blue Joker's value falls as the deck is drawn down over the round.
Bridge issues: none.
