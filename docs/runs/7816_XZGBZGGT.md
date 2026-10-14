# Run XZGBZGGT (port 7816, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind The Needle (480/3200)

Ante 1 (Economy/Double/The Psychic 600, $4): Small: disc to Flush hearts 260 + Two Pair 92. Shop $5: Buffoon pack -> only Dusk{RENTAL} / Business Card{P,R}; took Dusk ($0, $1 left). Big 450: 2P KK99 116 + Straight 200 + 2P AAQQ 208 (cleared 524). Rent hit at round end: $-2. Shop $2: SELL Dusk, BUY Spare Trousers{RENTAL} $1 (+2 mult per Two Pair, grows). Psychic: 2P+filler 152, 336, 464 (Trousers +2 -> +6) = 952.
Ante 2 (Juggle/Orbital/The Pillar 2000, $4): shop $4 could not afford $5 Supernova{P}/Ice Cream. Small 1000: Trips TTT 540 + 2P 99 77 520. Shop $2: passed Raised Fist{P,R} (2nd rental barred), Lusty $5. SKIPPED Big for Orbital Tag (Two Pair L1 -> L4, +3 levels, est x2.8). Pillar: 2P 1380 + Straight 1036 (one hand spare).
Ante 3 (D6/Foil/The Needle 3200, $5 after cash): shop: Celestial pack $4 -> Earth (no Uranus). Small 3200: 2P AAQQ 2074 + 2P 1786. Shop at $-1: could not buy Uranus $3 / Scary Face. Big 4800: 2P 2310 + 2P 2438 + Pair (4748 then 440). Shop at $0: Odd Todd $4 and Uranus $3 unaffordable. Needle (1 hand, need 3200): best Two Pair AA99 = 3000, +2 mult growth included; no hand >= 3200 except Straight Flush; dug 2 discards for clubs, missed, 480.

## Post-mortem

Binding constraint: money. One joker (Spare Trousers, a rental at $3/round) was my only scorer for 3 antes; rent plus the $0 Small meant I was at $-4..$5 every shop and could not buy a single $3-5 item (Uranus x2, Odd Todd, Scary Face, Supernova). With no 2nd scorer and no xMult, the Needle (one hand, 3200) was a hard wall: best hand 3000-3050.

Decisions I would change:
1. Ante 1 Buffoon pack with $5: the pack offered only rentals. Taking Dusk was harmless (sold next shop for +$1), but the pack (-$4) left me at $1. A $4 Crafty Joker (+80 chips flush) was a real scorer. Lesson: at $5 with a $4 Joker in the shop that adds anything, buy the joker rather than gamble a pack that may only show stickered jokers.
2. Keeping Spare Trousers{RENTAL} as the sole scorer from ante 1 to 3: rent cost ~$12 total (3 rounds x $3 + $1 buy) = ~3 shops of purchasing power. It did grow to +18 mult (real value), but a Needle boss needs 3200 in ONE hand: I needed an extra ~250 (a single Uranus at $3 or Odd Todd at $4 would have cleared it, e.g. Odd Todd +31 chips x2 aces odd on AAKK).
3. After the ante-3 Small I was at $-1 (shop had Uranus $3, Scary Face $1): rent at round end is charged even when cash out leaves me negative, and negative money blocks ALL purchases. I should have SOLD the rental one round earlier or skipped the Big for Foil Tag? (No: Big 4800 was cleared easily with 2P 4748+, the problem was only the boss.)
4. I should have anticipated the Needle at the ante-3 first shop (boss known at ante start): BOSS PREP said best x1 hand 1800-2200 < 3200. With $5 I bought a Celestial pack (Earth, off-hand). Better: keep the $5 for Uranus ($3) the next shop (it was there at the next shop for $3) i.e. don't spend $4 on a pack gamble, then buy Uranus when it shows (it did appear at the very next shop and I had $-1 by then).

Reusable rules (if-then):
- IF the only owned scorer is a rental AND the Small Blind pays $0 AND money < $5 after rent, THEN every round-end drops money by $3: you will be locked out of the shop. Sell the rental the moment a clean non-rental scorer costs <= your cash + $1.
- IF The Needle is the ante boss, THEN compute the single best hand with the +growth already included (`hands` est is exact: 3000 predicted, 3000 realised). You need est >= boss need with any hand you can make from 8 cards (best Two Pair AAKK) PLUS margin: buy a main-hand planet / flat chips joker in every shop of that ante (each +10 chips/+1 mult is +5-10% here).
- IF an Orbital Tag for your main hand (Two Pair) is on the Big at ante 2, THEN skipping the Big is right: +3 levels (est x2.8) and no -$3 rent round. Worked: cleared the Pillar with a hand to spare.
- Spare Trousers: a Full House also contains Two Pair (it grows on FH in the real game); Pair/Trips/Straight plays do not grow it. Play Two Pair every hand it can clear.

Advisor/CLI defects:
- shopadvise at ante 3 ($5) said BUY Celestial pack ($4, 'take Uranus') but the pack held Mercury/Earth/Jupiter only; Uranus was a $3 single in the NEXT shop. The advisor ranked the pack over holding $5 for the main-hand planet, and it does not model that rent turns $5 into $-1 by the next shop (it printed 'a later shop sees $1.76').
- SIM 'a later shop sees $X' is wrong when a rental is held and income is $0: the next shop saw $-1 (predicted +$1.76).
- At ante 3 Needle boss the advisor flagged EMERGENCY / BOSS PREP correctly, but 'ADVICE: LEAVE' at $-1, $0 gave no way out; no line to raise cash (sell rental for $1 only) exists.
- The pack advisor ranked 'Dusk{RENTAL}' PICK (SIM +0.08) at ante 1 even though it leaves rent -$3 against $1 cash: Dusk adds only chips on the final hand.
