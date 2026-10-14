# Run LFBTMULM (port 7802, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Goad (12942/18000)

Ante 1 (Charm/Uncommon/The Hook 600, $4): Small: disc keep KK QT, Straight K-9 316. Shop $6: Mad Joker $4. Big: 2P 8866 576. Shop $8: Raised Fist $5. Hook: disc lows, Trips 888 held A K T -> 1350 (est 522).
Ante 2 (Polychrome/Buffoon/The Head 2000, $10): Wily $4 (ratio 0.51). Skipped Small for Polychrome tag. Big: 2P AATT holding KQJ 1984 one-shot. Shop: free polychrome Credit Card{ETERNAL} (x1.5). Head: 2P AA66 2064 one-shot.
Ante 3 (Top-up/Negative/The Wall 12800, $22): EMERGENCY 0.27: Jumbo Buffoon -> Ride the Bus, Clever{RENTAL} $1, Arcana -> Hierophant (QS QC bonus). Small: 2P AA55 6534 one-shot. Shop: sold Bus, Popcorn{RENTAL} $1 (2nd rental, override for the Wall), Celestial -> Uranus. Big: 2P AATT 11907 one-shot. Wall: disc x2, 2P QQ44 holding KJ8 14040 one-shot.
Ante 4 (Boss/Standard/The Goad 18000, $10): first shop nothing (Flash Card, Star). Small: Trips QQQ 10890 one-shot. Shop $6: sold Popcorn (+8), 2 rerolls on Credit Card ($11: Chaos{E}, Walkie Talkie{E}) -> $-4. Big: 3 hands, 2P KK55 7425 + 2P AAKK 7047. Shop $-2 (TIGHT 0.77x): Uranus (2P L3), Buffoon -> Loyalty Card, sold Wily, Even Steven -> $-11. Goad: 2P JJ33 (JS 3S debuffed) 6426, disc, FH 888QQ 6084, disc 5 for a two pair needing 5490 -> drew none, Pair 22 432. LOSS 12942/18000.

## Post-mortem

Binding constraint: SCALING. No reliable/growth xMult was offered in 9 shop views, 2 rerolls and 3 Buffoon/Jumbo Buffoon
packs (Ride the Bus, Loyalty Card, 8 Ball, Superposition, Crafty, Drunkard). The only multiplier was the polychrome
eternal Credit Card (x1.5, from the ante-2 Polychrome skip tag). A flat Two Pair build (Mad +10, Clever +80 chips, Raised
Fist +2x lowest held, Even Steven) peaked at ~6-7k per real hand at ante 4, i.e. exactly the 6000/hand The Goad needed,
so one dead final draw lost the run. The Raised Fist build is also held-card fragile: the same Two Pair is 5.8k with a 2
held and 11k with only T+ held.

Decisions I would change:
1. Ante 3 Popcorn{RENTAL} as a 2nd rental (override of the hard rule): the Wall was one-shot at 14040, and without Popcorn
   (+16) the 2P would have been ~10k with 2 more hands. It cost $1 + $6 rent and two ante-4 shops ran on debt. The
   rule "never 2 rentals before ante 6" was right; the SCORE CHECK jump (3936 -> 7920) came mostly from the decaying +20.
2. Ante 4 Small shop: two rerolls ($5 + $6) found nothing. The checklist says rerolls at ante 3-4 mostly whiff; that $11
   would have bought Even Steven + Uranus one shop earlier, or a Jumbo Arcana (Strength/Death as a rescue for the final
   Goad hand, which needed just one more pair).
3. The Goad final sequence: after the FH (6084) I had 1 hand + 1 discard needing 5490 = a Two Pair with good held cards
   (p 0.68 per solver). Playing the 2P QQ88 (5808) first was 0.74; fine either way. The loss was decided in the shops,
   not the hands.
4. No rescue tarot held at ante 4 despite the advisor's repeated note. [INFERENCE] A $3 Death/Strength would only have
   helped if it turned the final 8 cards into a Two Pair (e.g. Death 9H -> JH gives JJ + 22); not certain to clear 5490.

Reusable rules (if-then):
- IF your build's mult comes from Raised Fist, THEN treat SCORE CHECK as optimistic: real hands holding a low card score
  about half; keep high cards in hand and discard 2-5s first even when they are not needed for the type.
- IF a decaying joker (Popcorn, Ice Cream) is offered as a rental, THEN count only its value at the boss round (Popcorn
  +16 at the 3rd round) and refuse it as a second rental unless the boss is unclearable without it by est.
- IF you own Credit Card at ante 4 with no r/g xMult, THEN spend the credit on concrete scorers/levels (Even Steven,
  main planet, Buffoon pack) before rerolls; 2 rerolls at $5-6 showed only eternal utilities.
- IF ante 4 boss is a suit boss (The Goad/Club/Head/Window), THEN buy a $3 rescue tarot in the ante-4 shops: a quarter of
  the deck forms types but scores 0, so the last hand often lacks one scoring pair.

Advisor/CLI defects:
- Loyalty Card: raw ab stayed `"remaining":"5 remaining"` across 4 played hands, and the advise notes contradicted each other
  ("fired on the LAST hand: x4 again in 6 hands" on the first Goad hand, then "x4 in 5 hand(s)", then "x4 in 4 hand(s)").
- Hand est under The Hook with Raised Fist: est 522 vs actual 1350 (held effects counted at 33% is too pessimistic when
  the held cards are all high).
- shopadvise (ante 4 Big shop) proposed SELL Loyalty Card (weakest) for Even Steven while Wily (+100 chips only on Trips,
  main hand Two Pair) was owned; Wily was the right sale.
- SIM in the ante-3 Celestial pack preferred Earth (+0.05) over Uranus for a Two Pair main with Mad + Clever (noise-level
  SIM gaps overriding the main-hand rule).
Bridge issues: none (81 steps, no rejects).
