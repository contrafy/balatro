# Run RJYRHSF9 (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (11394/37500)

Ante 1 (300/450/Window 600, $4): Small: Two Pair 124 + spade Flush 260 (I overrode advise and discarded for flush/straight, 11 outs). Shop $5: Buffoon -> Seltzer (other choice: perishable rental Juggler). Big: discarded 4 off-suit cards for a heart flush and drew a straight flush 3-7 hearts, 1200. Shop $7: Swashbuckler $4 (+3 mult from Seltzer's sell value; advisor said AVOID/LEAVE). Window: Pair J 150 + Two Pair T9 290 + Two Pair AAQQ 520.
Ante 2 (1000/1500/House 2000): one reroll found nothing. Skipped Small (Uncommon tag) AND Big (Top-up gave Odd Todd + Scary Face, Swash went to +7). House: sorted the face-down hand by rank and played the top 5 blind as a cycle = 680, then Pair AA 1602 (Odd Todd + Seltzer). The Uncommon tag paid out as Hack with a RENTAL sticker for $0; I left it.
Ante 3 (3200/4800/Flint 6400): Jumbo Spectral -> Grim (+2 enhanced Aces). Skipped Small (Juggle tag). Big with an 11-card hand: Two Pair AAQQ 3132 + Two Pair 9955 2916. Shop: Temperance buyuse ($3 -> +$9), Buffoon -> Misprint (perishable), Arcana -> Emperor -> Hermit ($6->$12) + High Priestess (Saturn, Earth used), reroll -> Jolly $3. Flint: Full House AAA99 in one hand (est 11988).
Ante 4 (9000/13500/Mark 18000): shop $11: Negative Chaos the Clown $9 (the advisor wanted me to sell Swashbuckler, which was giving +10 mult). Skipped Small for Garbage tag (+$8). Big: Two Pair AAJJ 8700 (last Seltzer charge) + Full House 99977 11745. Shop $17: free reroll -> Supernova $5, Temperance (+$15), 2 paid rerolls with no xMult. Mark: 5 face-down cards played as guaranteed Two Pair+ = 7950, Straight 3-7 7298, Two Pair AA22 cleared (18000).
Ante 5 (25000/37500/Serpent 50000): shop $20: 1 free + 2 paid rerolls with no xMult; Jumbo Arcana -> Chariot (Steel 8H). Skipped Small for Orbital (Trips L4). Big 37500: dealt no pair, both discards bricked into a single low pair, then Pair 33 2574 + Pair QQ 4140 + Pair JJ 4680 = 11394. Dead with 0 xMult.

## Post-mortem
Binding constraint: scaling. I reached ante 5 with zero xMult jokers and every hand at L1-L2 (Two Pair L1 was the most played type). The build was flat +mult (Swash +13, Jolly +8, Misprint ~11, Supernova) on top of chips jokers (Odd Todd, Scary Face): good hands did 7-12k and plain pairs 3-4k, against a 37500 Big. In 6 shop rerolls across antes 4-5 (3 free from Chaos) not one xMult joker showed up. Seltzer (10 hands) carried antes 1-3; once it ran out, scores fell by about half.

Decisions I would change:
- Skipping 4 Small Blinds (a2, a3, a4, a5) plus the a2 Big. Each skip was locally right ($0 Small payout, $3 shop, one fewer blind to clear), but together they cost about 5 shop visits. Those were my chances to see an xMult. At a2 and a3 the Top-up/Juggle tags paid well. The a5 skip was the weakest: neither 25000 nor 37500 was realistic for my build, so it bought nothing.
- At ante 4-5 I spent $12 on paid rerolls and $6 on a Jumbo Arcana. The playbook's alternative (main-hand planets) would not have closed a 3x gap either. The real fix was earlier: at ante 3, Celestial/level money for Two Pair instead of the Jumbo Spectral (Grim). The Aces Grim added did show up (AAA99, AA22 hands), so that pick was fine. I never committed to one hand type, though, so Supernova and the levels were spread across Two Pair, Full House, Straight and Trips.
- Chaos the Clown ($9 at ante 4) gave 2 free rerolls before the run ended. It is a good buy only with 3+ antes of shops ahead.

Reusable rules:
- IF Temperance is in the shop and your jokers' total sell value is >= $6, THEN buyuse it: it paid +$9 and +$15 here, and it is the best money item at Gold where Small Blinds pay $0.
- IF the boss is The Mark and you see 5 face-down cards, THEN play all 5: they are J/Q/K over 3 ranks, so the hand is at least Two Pair or Trips. It scored 7950 at ante 4 with Scary Face.
- IF the boss is The House, THEN `sort rank` before the first hand and play positions 1-5. That sends the 5 highest hidden cards (scored 680 at ante 2) and keeps both discards for the face-up draws.
- IF you own Seltzer, THEN count its charges against the blinds still ahead. Skipping a Small Blind saves 3 charges for the harder Big Blind. Plan the replacement scorer before the last charge, because scores roughly halve when it ends.
- IF you hold a Steel card, THEN never use it as a filler. It scores x1.5 only while held (advise used the steel 8H as a filler twice).
- IF you reach ante 4 with 0 xMult on Gold, THEN stop skipping Small Blinds. You need every shop visit to roll for an xMult; tags do not give multiplication.

Advisor/CLI defects:
- shopadvise labels Swashbuckler "AVOID (useless as the only joker)" and advised SELL 3 times while it was giving +10 to +13 mult with 6 other jokers. The AVOID label should apply only when Swashbuckler is the only joker.
- advise picks a Steel card as a play filler (`play PAIR 6 7 8 5 4` included steel 8H; held steel is x1.5). Fillers should exclude Steel/Gold cards that pay off while held.
- At ante 1, advise's filler choice used 4H from a 3-heart flush draw (`play PAIR 3 4 8 7 6` played 4H as filler while it was keeping AH QH for hearts).
- At the ante-1 Window, advise said "discard 4 6 7 8 1" to "keep Two Pair". That discard would have broken the Two Pair, because debuffed TD/9D still count toward the hand type.
- est is badly off with face-down cards: est 40 vs actual 680 (House), est 720 vs actual 7950 (Mark, 5 hidden faces). The Mark hint text was right (~2880 for a pair), but est for the played hand ignores it.
- The Uncommon Tag's free joker arrived with a RENTAL sticker (Hack $0, -$3/round). The skip advice values the tag as a free joker, but at Gold it can be stickered junk.
