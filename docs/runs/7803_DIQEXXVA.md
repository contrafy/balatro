# Run DIQEXXVA (port 7803, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 1 blind The Window (192/600)

Ante 1 (Foil/D6/The Window 600, $4): Small: solver disc 4 (keep 4 clubs), club Flush 288 + High K 15 = 303/300. Shop $5: overrode SIM (Smeared Joker{PERISH,RENTAL} $1, p_next 0.31 vs 0.00) for Buffoon $4 -> Wily{RENTAL} / Joker{ETERNAL,RENTAL}: skipped both. Big 450: solver disc 5 + disc 3 into Straight A-T 324, diamond Flush 292 = 616. Shop $6 (Rough Gem{E} $7, 8 Ball{E} $5, Wasteful, Celestial, Arcana): Celestial -> Mars (no useful planet; Neptune/Mars/Pluto). Window: 2 discards for a heart flush missed (drew 3 debuffed diamonds), Pair QQ 40, Pair AA 64, 2P TT22 88 = 192/600. GAME OVER with zero jokers.

## Post-mortem

Binding constraint: zero scoring jokers at the ante-1 boss. Two shops ($5 and $6) never offered a non-eternal scorer; the
one Buffoon pack held only a Wily rental and an eternal-rental Joker. A jokerless deck at Gold scores ~40-90 per pair-family
hand, so the 600 boss needed two 280+ flushes/straights; The Window debuffed diamonds and both discards pulled diamonds.

Decisions I would change:
1. Shop 1: I overrode the SIM (Smeared Joker{PERISH,RENTAL} $1, p_next 0.31 vs 0.00 baseline) for a Buffoon pack that
   produced nothing. With no jokers, flushes are the only ante-1 hands that reach 280+; Smeared turns 4 suits into 2 and
   roughly doubles flush odds for the Big Blind. It was $1 and $3/round for 5 rounds, sellable. Follow the SIM there.
   (Caveat: under The Window, Smeared makes hearts count as diamonds too, so it would have been sold before the boss.)
2. Shop 1 pack: the Joker{ETERNAL,RENTAL} (+4 mult) was ugly (-$69 over the run) but my boss hands (QQ 20 chips, AA 32,
   TT22 44) at x6 mult instead of x2 would have scored ~576 + better plays; survival beats rent. With zero scorers at
   ante 1 and no other joker in sight, even an eternal rental +mult is better than skipping the pack.
3. Shop 2 ($6): Celestial $4 (Mars) was a dead pick. A $5 reroll leaving $1 can still buy a RENTAL joker ($1 at Gold);
   30% of shop jokers are rentals, so the reroll had a real chance at a scorer and the pack had none.

Reusable rules (if-then):
- IF you own zero jokers at ante 1 and shopadvise's SIM shows a cheap item lifting p_next from ~0 to 0.3+, THEN buy it,
  even a perishable rental: the rule ranking (Buffoon pack 78) does not know your deck can't clear without help.
- IF a Buffoon pack at ante 1 with zero scorers offers only rentals, THEN take the scorer that fires on Pair/any hand
  (+mult) even if Eternal-rental; skipping leaves a jokerless deck facing 450/600.
- IF you have $5-6 at ante 1 with zero jokers and no scorer in the shop, THEN prefer a reroll (rental jokers cost $1,
  so $1 left still buys one) over a Celestial pack (1/12 chance it levels the hand you actually play).
- IF the ante-1 boss is The Window/Head/Club/Goad, THEN in the Big Blind shop value suit-neutral scorers; flush draws
  lose ~1/4 of the deck.

Advisor/CLI defects:
- shopadvise shop 2 ($6, 0 jokers): "rerolling to $0 has revealed $3 jokers it could no longer buy - keep the $6" ignores
  that Gold rentals cost $1; a $5 reroll leaving $1 can still buy a rental scorer.
- shopadvise shop 1: rule ADVICE was the Buffoon pack while the SIM preferred Smeared; the final ADVICE followed the SIM
  (correct), but the Smeared line said "[UTIL]" with no mention that it is a flush enabler for a jokerless deck.
- Pack advise: ranked Joker{ETERNAL,RENTAL} 65 (pick) with "+187% round est" - consistent with survival, fine; Wily 30.
Bridge issues: none; 23 steps, no rejects.
