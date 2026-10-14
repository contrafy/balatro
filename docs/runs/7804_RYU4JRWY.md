# Run RYU4JRWY (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind Big Blind (29896/37500)

Ante 1 (Charm/Holo/The Window 600, $4): Small Flush 300 (solver discards). Shop $6: Smiley{PERISHABLE} $4 (SIM 0.53 vs Buffoon 0.23). Big 2P QQTT 720. Shop $8: Hanging Chad $4, Buffoon -> Chaos the Clown{ETERNAL} (free reroll/shop). Window: Straight 332 + High KS (Chad x3 Smiley) 560.
Ante 2 (Handy/Boss/The Club 2000, $6): EMERGENCY 0.09: free reroll, Jumbo Buffoon -> Gros Michel. Skipped Small (Handy +$4). Big: Straight K-9 4356 one-shot. Gros Michel died at round end. Shop $10: free reroll (Baseball), passed Celestial, kept $10. Club: Pair JJ 1100 + Pair QQ 1100.
Ante 3 (Top-up/Foil/The Psychic 6400, $18): EMERGENCY 0.03: free reroll -> Mystic Summit $5, $5 reroll (passed Vampire{E}, nothing to feed it). Skipped Small for Top-up -> Even Steven + Greedy. Big: FH 777QQ 5151 one-shot (QD first for Chad). Shop: sold perished Smiley, free reroll -> Sly{E} $3, Jumbo Arcana -> Star (KC JC TC to diamonds for Greedy). Psychic: 2P 8844+JS 5100, 2P 5522+TH clears.
Ante 4 (Double/Uncommon/The Mark 18000, $15): EMERGENCY 0.27: sold Greedy -> Seeing Double $6; Arcana -> Temperance +$12; $5 reroll -> sold Chad for Abstract{E} $4, sold Even Steven for Odd Todd{P,R} $1 (SIM P 0.71 vs 0.41); ratio 1.49. Played Small (Double tag useless): FH 55599 12232. Shop: sold Odd Todd -> Ramen{RENTAL} x2 (still one rental), free reroll -> Justice $3 held. Big: Trips AAA 7891 + Pair 99 5296 + Trips KKK. Mark: FH 444AA (AC) 16975 + 2P 8855 (8C) clears.
Ante 5 (Handy/Juggle/The Tooth 50000, $18): EMERGENCY 0.26: free reroll, Buffoon (Jolly{R} / Wrathful{E,R}: skipped), $5 reroll (nothing), Celestial -> Uranus (Two Pair L2). Skipped Small for Handy (+$16, $21). Big 37500: Justice on 3C (solver 0.53 -> 0.61), FH 333QQ 17661 (glass 3C, Seeing Double fired), Pair JJ 5068 (no club, SD off), Trips TTT 7167 (no club) = 29896/37500. GAME OVER.

## Post-mortem

Binding constraint: scaling. At ante 5 the build was flat (Summit +15, Abstract +18, Sly +50 chips) times Ramen x1.8
and Seeing Double x2 that only fires when a CLUB scores. The Big's three hands: 17661 with a club in the Full House,
5068 and 7167 without one. A conditional xMult doubled one hand in three; I needed a second always-on xMult (or main-hand
levels for chips) and never saw one in ~12 joker views (8 free Chaos rerolls + 3 paid).

Decisions I would change:
1. Ante 4: Seeing Double was bought as "the xMult" (SIM +0.13). With a pair-family deck it fired on maybe 40% of hands.
   The ante-4 Big shop SIM showed Blue Joker replacing it at P 0.71 vs 0.35 (eternal rental, so correctly refused), which
   was the signal that SD was dead weight; I should then have replaced SD with any always-on chips/+mult joker in the
   ante-5 shop instead of a paid reroll.
2. Levels: Two Pair stayed L1 until ante 5 (one Uranus). I passed a Celestial at ante 2 ($10) and ante 4 ($11) to keep the
   floor. My mult was ~35-50 on ~80-100 chips, so +20 chips per Two Pair level was +20% per level, worth more than interest.
3. Ante 4: swapping Odd Todd (+31 chips per odd card) for Ramen x2 was right for the xMult count, but Mystic Summit needs
   discards burned and Ramen loses 0.01 per discarded card: 2.00 -> 1.81 in three rounds. Summit and Ramen fight.
4. Chaos the Clown{ETERNAL} took a slot all run. Its free rerolls found Summit, Sly, Seeing Double and Justice, so it paid
   for itself early; by ante 5 the slot mattered more than a $5 reroll. Neutral overall; do not take it after ante 2.

Reusable rules (if-then):
- IF Seeing Double is your only second xMult on a pair-family deck, THEN count it as x1.4, not x2: it needs a scoring Club
  (fillers don't count without Splash). Keep looking for an always-on xMult and replace SD first.
- IF the SIM shows that replacing a joker raises P(next 3 blinds) by 0.3+ (even with a barred joker), THEN that joker is dead
  weight: replace it with the best allowed scorer in the next shop.
- IF you own Mystic Summit AND Ramen, THEN burn discards 1 card at a time (Summit only needs 0 discards left); a 5-card
  discard costs Ramen x0.05.
- IF the ante-5 Small Blind tag is Handy (or another tag paying $15+ now) AND the Small's shop would see under $10, THEN skip
  it: one fewer risky fight and the cash lands before the Big's shop.
- IF your main hand is under L2 at ante 4 with 2+ scorers AND mult is 2-3x chips, THEN buy main-hand planets/Celestial over
  holding interest.

Advisor/CLI defects:
- Arcana pack advisor ranked The Fool first ("copy of the last tarot/planet used") when no tarot or planet had been used
  in the run, so it would have copied nothing.
- shopadvise printed "REROLLS ARE CHEAP: the next reroll costs $0 (D6 Tag: starts at $0, +$1 each)" every shop; the free
  reroll came from Chaos the Clown, not a D6 Tag, and only the first reroll was free.
- Ante 5 blind select: `s` advised "do not skip: ante 5+" for a Handy Tag worth $16 when the Small was a ~1.3x fight;
  the skip rule should price money tags that pay at the skip.
- SCORE CHECK jumped from 0.82 to 1.49 (Mark) with Seeing Double + Odd Todd; SIM treats SD as close to always-on on this
  deck. Actual ante-5 Big: SD fired on 1 of 3 hands.
- Ramen x2 + Mystic Summit: `advise` kept recommending 5-card discards ("burn your discards on junk") with Ramen owned;
  the solver's 2-3 card lines were equal on p and cheaper for Ramen.
