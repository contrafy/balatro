# Run EUQNSU4D (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind The Goad (67612/120000)

Ante 1 (Juggle/Voucher/The Window 600, $4): Small FH 55588 284 + Pair AA. Shop: Buffoon -> Smiley{PERISH} (over Swashbuckler{R}). Big: Trips JJJ 1080 one-shot. Shop: nothing ($7). Window: 2P KKQQ 480 + High K + High Q.
Ante 2 (Polychrome/Meteor/The Needle 1000, $13): reroll (nothing), Celestial -> Uranus. Small: Straight A-T 1539 one-shot. Shop: reroll to $1 (nothing; Pareidolia{E,R} passed). Skipped Big (broke, 1500 = 6x my hand) for Meteor: Earth + Saturn. Needle: disc 5, Straight K-9 2398.
Ante 3 (Foil/Investment/The Eye 6400, $6): Joker Stencil{ETERNAL,RENTAL} $1 (override of BARRED: xMult exception, SCORE CHECK 0.05, SIM +0.21), Celestial -> Saturn (Straight L3). Skipped Small (Foil) and Big (Investment) so Smiley (1 round) carried the Eye: Trips KKK 5400 + FH QQQ55 11025.
Ante 4 (D6/Top-up/The Tooth 18000, $29): Smiley perished (sold, Stencil x6). 2 rerolls (nothing), Celestial -> Mercury. Small 9000: two discards to KQJT, Pair 88 dig 738, Straight A-T 8460. Shop $16: Celestial -> Pluto, reroll, Justice $3. Skipped Big for Top-up: Raised Fist + Square (sold Square). Tooth: Justice 7H glass, disc 5, disc 2D (Fist holds a 6), Straight 7-3 18400 one-shot.
Ante 5 (Double/Orbital FH/The Serpent 50000, $5): Spectral pack -> Ankh: the eternal Stencil survived and was copied (Raised Fist destroyed): two Stencils x6 = x36, rent $6/round. Skipped Small (Double) and Big (Orbital x2 = Full House L2 -> L8). Serpent: disc 1, disc 1 (hand grows), 1-card dig, Straight A-T 50760 -> cleared 52560.
Ante 6 (Coupon/Handy/The Goad 120000, $1): polychrome Ice Cream{RENTAL} $1 (Stencils x5 each). Skipped Small (Coupon). Big 90000: disc 5, FH AAAJJ 248400 one-shot. Free Coupon shop: Jumbo Celestial -> Saturn (Straight L4), Celestial -> Jupiter, Pluto, Hierophant. Goad: Hierophant TD 8D bonus, two discards toward a 9/6 straight (missed), digs High 13500 + High 14062 keeping 8877 for a FH (missed), forced 2P 40050 -> 67612/120000. GAME OVER.

## Post-mortem

Binding constraint: no additive scoring and no money. From ante 3 the whole engine was Joker Stencil (later two Stencils,
x25-36) on bare hand levels: Pair L2 ~15-18k, Two Pair ~40k, while the ante-6 boss needed 120k. Only Straight L4
(~130-300k) and Full House L8 (~250-490k) cleared, so every blind became "draw a straight/full house in 3 hands and
2 discards". The Serpent (more cards) and the Big (dealt AAA JJ) went fine; The Goad (spades debuffed, 13 fewer live
cards) whiffed all 4-out draws. Rent of $6-9 per round kept money at $-3..$1 from ante 5, so shops were dead except the
free Coupon shop.

Decisions I would change:
1. Ante 2: two rerolls ($11) found nothing and left me jokerless for the ante-3 shop. With 1 perishable scorer, the
   first-shop $13 would have been better kept to $8+ for the ante-3 shop (where Stencil was $1 anyway) or spent on a
   Buffoon pack had one appeared.
2. Ante 4 and 6 Celestial picks: I took Saturn/Pluto/Jupiter/Mars-tier planets for rare hands. With a hand-agnostic
   xMult engine (Stencil), the planets should go to the hand made EVERY round (Pair/Two Pair): Two Pair L2 at x25 was
   only 40k at ante 6. A Two Pair L5 would have been ~85k as a guaranteed floor at The Goad.
3. Ante 6 shop: Ice Cream rental cost each Stencil x1. It was +79% on straights, but the money it ate (-$3/round)
   was irrelevant only because I was already broke. Acceptable; not the cause.
4. The Goad: I spent both discards on 2-out straight draws (needs 6+9) and the first two hands on digs. Playing the
   made 2P/Pair hands first is no better (40k + 27k + 18k = 85k < 120k), so the round was decided in the shops.

What worked: Stencil{ETERNAL,RENTAL} at $1 with 0 scorers alive next ante (exception: SCORE CHECK 0.05, SIM +0.21);
skipping Small+Big at ante 3 so a 1-round Smiley carried The Eye and the Investment tag paid $25; Top-up skip at ante 4
(Raised Fist); Ankh with an ETERNAL Stencil (eternal jokers are never destroyed by Ankh, so it is a free copy of Stencil
or of the other joker); Double + Orbital skip = Full House +6 levels; Serpent 1-card plays to grow the hand to 14.

Reusable rules (if-then):
- IF you own an eternal Joker Stencil and 1 other joker AND a Spectral pack offers Ankh, THEN take it: the eternal
  Stencil survives, and either you get a second Stencil (x6 * x6 = x36 with 2 jokers) or a copy of the other joker.
- IF your only multiplier is Stencil (hand-agnostic), THEN level Pair/Two Pair (the hands you make every round) before
  Straight/Flush/FH levels, or the round depends on drawing the rare hand; a Pair L2 at x36 is only ~16k.
- IF a Double Tag is on the Small and the Big gives Orbital (or any tag) AND you are broke, THEN skip both: the doubled
  Orbital gave +6 levels and the skips saved $12 rent.
- IF you are at $0-5 with $6+ rent per round, THEN skip every Small/Big whose shop you cannot use; only the Coupon/free
  shops and tags still buy anything.
- IF The Goad/The Club/The Window debuffs a suit AND your clear depends on a straight/FH draw, THEN expect the solver's
  p to be optimistic: the boss removes ~25% of live outs (Goad: p 0.93 -> 0.71 -> 0.55 -> loss).

Advisor/CLI defects:
- shopadvise BARRED Joker Stencil{ETERNAL,RENTAL} $1 at ante 3 (0 scorers alive next ante, SCORE CHECK 0.05,
  SIM +0.21) although PLAYBOOK 2b's exception (xMult, SCORE CHECK < 0.5, SIM >= +0.15) applied; it was the only
  reason the run reached ante 6.
- Spectral pack advise ranked Ankh 10 and said SKIP; it does not know eternal jokers survive Ankh (Stencil x6 -> two
  Stencils x6 each = x36, est 13.8k -> 50k on the same straight).
- `buyuse 1 --expect Pluto` was REFUSED "buyuse 1 is None now, not 'pluto'" while `s` showed J1:Pluto; `buyuse Pluto`
  then worked as `buyuse 1`.
- `blind` sent right after `endshop` was refused "SELECT_BLIND is not available in SHOP" although the endshop printout
  showed BLIND_SELECT (nothing sent; `sleep 2` fixed it).
- Under The Goad the solver gave p 0.97/0.93 for 2-out straight discards and 0.71/0.55 for 4-out digs; all missed.
  It may count debuffed-suit cards' draws as scoring value or overweight the 1-in-10 draw lines.
- `s` at the ante-6 BLIND_SELECT said "round reaches ~114075 vs The Goad 120000" while shopadvise SCORE CHECK said
  ~178128 (172512 under its rule): two different numbers for the same round.
