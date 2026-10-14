# Run FPKFX7AQ (port 7815, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Small (19952/25000)

Ante 1 (Foil/Voucher/The Goad 600, $4): Small: Flush KH TH 9H 7H 6H 308 one-shot (exactly 300 need). Shop $6: Even Steven $4. Big: Trips 666 720. Goad: Flush 552 + Pair 44 84. $8.
Ante 2 (Juggle/Orbital/The Wall 4000, $15): EMERGENCY 0.31 -> Shoot the Moon $5 (+13 mult per Queen HELD). Small: Straight 648 + Trips 720. Celestial -> Mercury. Big: Flush 560 + Flush 2001 (Queen held). Shop: Mystic Summit $5 (+15 at 0 discards); MISBOUGHT Neptune $3 (it is Straight Flush, Jupiter is Flush). Wall: burn 2 discards, Flush 3552 + Pair 1443 with Summit.
Ante 3 (Standard/Orbital/The Manacle 6400, $14): Misprint{ETERNAL} $4, Buffoon -> Jolly, Strength, Temperance (+$6), Jupiter. Small: TwoPair 2871 + Pair 2095. Big: FH TTT88 7267 one-shot. Manacle: Strength KK->AA, FH 888AA 3698 + High JC 630 + Two Pair 2875. 5 jokers, 0 xMult.
Ante 4 (Juggle/Meteor/The Wheel 18000, $17): EMERGENCY 0.19. Buffoon pack = Vampire / Ride the Bus{E}: skipped. holo Crafty{PERISHABLE} $7 (+80 chips Flush, ~2x flush hands). Small 9000: spade Flush 9877 one-shot. Big 13500: Flush 10200 + Pair 2829 + Two Pair 3105 (cleared by 80!). Mega Celestial -> Mercury + Earth. Wheel 18000: Pair 3350 + Flush 12012 -> 16958 + Pair 22 4159 (cleared with 1 hand).
Ante 5 (Juggle/D6/The Mark 50000, $7): Mercury (Pair L5), Celestial -> Jupiter (Flush L3), $0 left. Small 25000: Pair 33 4256 dig, Flush 10856 -> 15112, last hand no flush, Pair 99 4840 -> 19952/25000. LOSS by 5048.

## Post-mortem

Binding constraint: scaling. Six flat +mult/chips jokers (Even Steven, Shoot the Moon, Mystic Summit, Misprint{E}, Jolly, Crafty) and ZERO xMult in 17 shops/packs seen. Best hand ~11-12k (Flush with a Queen held, Summit on), typical 3-4 hands ~15-20k vs the 25k ante-5 Small. Money was $0-$17 the whole run (Gold small blind pays $0, three planet/pack buys per ante), so no reroll hunt was ever affordable.

Decisions I would change:
1. Ante 2 shop: bought Neptune believing it was the Flush planet (advisor text "planet for other hand"). Neptune = Straight Flush, Jupiter = Flush. $3 + a lost interest tick, and that $3 never got back. Check the planet's hand before buyuse.
2. Ante 3 Buffoon pick Jolly (+8, pair-gated) over Droll: harmless, but I then had a full 6-joker row of flat jokers with no slot for an xMult; I should have kept a slot open or planned to sell Jolly.
3. Ante 4: skipped Vampire in the pack. Vampire only grows with enhanced cards, so the skip was right; the real miss was spending $8 on a Mega Celestial pack at $10 instead of rerolling for a joker (both gambles failed).
4. At ante 4 I played every blind as the main-hand scoring race. The three ante-4 rounds cleared by 80, 0.0x and ~1000: a ~5% variance margin each. No decision fixes that without an xMult.

Reusable rules (if-then):
- IF you own Shoot the Moon, THEN keep Queens HELD (never play them): +13 mult per held Queen, so a 5-card Flush or Pair played with 1-2 Queens in hand is 2x-3x a normal hand. Choose which flush cards to play so a Queen stays in hand (est shows it).
- IF you own Mystic Summit, THEN burn both discards first (est at 0 discards is ~1.4x), then play the big hand on the first of your 3 hands: every hand after the discards are gone gets +15 mult.
- IF a Planet's name is Neptune THEN it is Straight Flush (not Flush); Jupiter = Flush, Earth = Full House, Mercury = Pair, Venus = Trips, Uranus = Two Pair, Saturn = Straight, Pluto = High Card, Mars = Quads.
- IF Temperance is $3 in the shop and you own 5 jokers THEN it pays ~+$9 (sell values): net +$6 and it is a free money source.
- IF a Strength tarot is held and the hand has K K + an A (or any pair one rank below a stronger rank), THEN Strength can turn it into a made Full House/Trips (used KK->AA on Manacle: FH).
- IF a flat-joker build has ratio <0.5 at ante 4 with no xMult, THEN expect to die at the ante-5 Small (25000): at ante 4 shops put ALL money into Buffoon packs/rerolls for an xMult rather than planets (I got Jupiter + 2 Mercurys + Earth = +25% score, worth ~3k, while the gap was 5k+).

Advisor/CLI defects:
- shopadvise labels Neptune "[planet for other hand]" without naming the hand; buyuse then silently levels Straight Flush. It should print the hand name ("Straight Flush") in the item line.
- `advise` Summit text: "Pair scores 1410 now but 1875 at 0 discards left" is fine, but the SOLVER lines ignore that burning a discard also loses the 'hold Queen' draw; minor.
- On boss The Wheel `advise` printed p 0.88 (low confidence) for a line that needed the Misprint roll above its mean; consistent with the orchestrator's calibration note.
- `s`/`shopadvise` take 60-100s each on ante 3-4 shops; the CLI said "Backgrounded early" and I had to wait for the job.
