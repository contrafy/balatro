# Run JGH4NQBH (port 7817, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Small Blind (7548/9000)

Ante 1 (Rare/Voucher/The Club 600, $4): Small: disc x2 -> Flush D 276 + Pair AA. Shop $5: Buffoon -> Photograph{P} (over Clever). Big: 2P JJ77 216, disc 3 -> FH 99988 332. Shop $6: Buffoon -> Shoot the Moon{P} (over Gluttonous, Club boss). Club: FH 77799 252 + Straight A-T 560.
Ante 2 (Charm/Ethereal/The Head 2000, $8): EMERGENCY 0.28 -> foil Invisible{RENTAL} $1. Skipped Small (Charm: Hermit $7->$14, Chariot steel KS). Big 1500: Pair 77 + QQ held 2072 one-shot. Shop $19: Buffoon -> Scholar{E} (SIM over Sly{P}), left with $15. Head: 2 digs, junk cycle, Flush AS JS 9S 5S 3S 2288.
Ante 3 (Coupon/Meteor/The Wheel 6400, $20): EMERGENCY 0.29: reroll, Odd Todd{P} $4, Emperor -> Death + Magician. Small: 2P 4433 2190 + Pair JJ w/ QQ held 2560. Shop: sold perished Photograph, sold Invisible -> duplicated Shoot the Moon (2x StM, +26/held Q), Uranus. Skipped Big (both StM had 1 round left; Meteor -> Mercury, Venus). Wheel: face-down card sat between AS and AD in the rank-sorted deal = Ace; Death 5D->AD, Magician lucky on 2 Aces, Quads A one-shot (>6400).
Ante 4 (Investment/Buffoon/The House 18000, $15): both StM perished (sold), left with Scholar{E} + Odd Todd{P}: SCORE CHECK 0.04. 2 rerolls ($11): no joker except Superposition{E,R}. Arcana -> Death (6th Ace), Mercury (Pair L3), $1. Small 9000: disc 5, disc 5 keeping AAA, dig JJ (drew 4th Ace), dig 88 for a 5th Ace (missed), last hand Quads A 7308 (lucky AS did not fire) -> 7548/9000. LOSS.

Final build: Scholar{ETERNAL} (+20 chips +4 mult per Ace), Odd Todd{PERISHABLE}; Pair L3, Two Pair L2, Trips L2; 6 Aces in deck (2 lucky). Zero xMult all run.

## Post-mortem

Binding constraint: scaling, caused by perishables. Of the 7 jokers I held, 5 were perishable (Photograph, Shoot the Moon x2, Odd Todd) or a 2-round tool (Invisible); the only permanent one was a weak eternal Scholar. Every source of mult expired between the ante-3 Wheel and the ante-4 Small, so I entered ante 4 at ~630 per hand against 9000 and 6 shop views at antes 2-4 offered no permanent +mult joker and no xMult. Death/Magician/Ace tricks pushed one hand to 7.5k, not enough.

Decisions I would change:
1. Ante 2 Big shop ($19, ratio 0.81): I bought a Buffoon pack and then LEFT with $15 while both my mult jokers were perishable with 2-3 rounds left. That money should have gone on 1-2 rerolls for a PERMANENT +mult joker; by the ante-4 shop the same rerolls were too late (Small 9000 needs 3000/hand).
2. Ante 1 first pack: Photograph{PERISHABLE} over Clever (permanent). SIM was right for ante 1-2, but stacking perishables made ante 4 a cliff. With 0 permanent scorers, prefer the permanent option when SIM gaps are < 0.15.
3. Ante 2 pack: Scholar{ETERNAL} over Sly{PERISHABLE}: fine, but neither was a real scorer; skipping and keeping $ would have been similar.

Reusable rules (if-then):
- IF all your mult jokers are perishable AND they expire before the next ante's Big, THEN treat the shop as "0 scorers next ante": spend through the floor on rerolls/Buffoon for a PERMANENT +mult joker now; do not leave with $15 (shopadvise counted them as "alive next ante" one ante too long).
- IF a key perishable has 1 round left and the boss is next, THEN skip the Big so it survives to the boss (did this: 2x Shoot the Moon carried the Wheel; Meteor tag gave 2 planets).
- IF Invisible Joker is ready and your jokers include a strong perishable you need for the boss, THEN sell Invisible: the copy here doubled Shoot the Moon (+26 mult per held Queen) for the boss.
- IF The Wheel/House flips a card face down in the INITIAL deal, THEN read its rank bound from the rank-sorted order BEFORE any `move hand`: here it sat between AS and AD = an Ace; advise lost the bound after I reordered.
- IF Scholar is owned and you have Death, THEN copy Aces (move the Ace rightmost first, Death overwrites the LEFT card): Quads A with Scholar+Odd Todd ~7k, Five A ~13.7k from a 2-joker build.
- IF the last hand is Quads with a Lucky card, the 1/5 +20 mult is not in est; the solver's "dig for the 5th Ace" line (0.52 vs 0.24) was right in expectation but lost.

Advisor/CLI defects:
- shopadvise ante 3: "Uranus $3 ranked higher but passed over: consumable slots hold only rescue items" although `buyuse` works with full slots; it should propose `buyuse`.
- advise (Wheel): after `move hand`, the face-down card lost its rank bound ("unknown random cards") and ADVICE fell back to Trips 4012 instead of Quads; the bound should be carried by card id, not position.
- advise printed stale candidates once right after a discard (The Head, ante 2): the output showed the pre-discard hand until I ran `s` first.
- shopadvise ante 2 advised Diet Cola at SIM -0.01 vs buying nothing (rule score overrode a negative SIM).
- "Scorers still alive next ante" counted Shoot the Moon (3 rounds left at the ante-2 Big shop) as alive at ante 3 although it would expire mid-ante 3; perishables that die before next ante's Big should not count.
Bridge issues: none (74 steps, no rejects).
