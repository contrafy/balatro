# Run DJ5ZWVAG (port 7807, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind Small Blind (7557/9000)

Ante 1 (Foil/Polychrome/The Window 600, $4): Small: disc to AKQJT, Broadway Straight 324 vs 300. Shop $6: Scholar{E}/Crazy/Buffoon pack -> took Buffoon (overrode SIM Crazy 0.44) -> Half Joker{PERISH} (+20 mult at <=3 cards). Big 450: Trips AAA 1449 one-shot. Shop $8: reroll ($3 left, Lusty{E,R}/Saturn: nothing). Window (diamonds debuffed): Pair KK 660 vs 600.
Ante 2 (Coupon/Holo/The Flint 2000, $3): Half Joker made every <=3-card hand ~300-1450 (even a single Ace High Card 798). EMERGENCY 0.31, reroll found Bootstraps{E} $7 (unaffordable). Small 1000: Trips 897 + Pair 484. Shop $7: Hanging Chad{E} $4 (first card x3: Ace high card 798). Big 1500: High A 798 + High J 735. Shop $8: reroll -> Scholar $4 at $3 (missed by $1). Flint (base halved): Pair QQ 945, High K 693, High Q 672 = 2310/2000; Half Joker perished at round end.
Ante 3 (Charm/Polychrome/The Fish 6400, $8): sold perished Half, Mystic Summit{E} $5 (+15 mult only at 0 discards LEFT: burn both discards first). Skipped Small for Charm tag (Mega Arcana: High Priestess -> Venus+Earth, Death duplicated a J). Big 4800: AA33 1190 + Pair AA 918 + FH TTTJJ L2 2835 = 4943 (won by 143). Shop $10: Clever{PERISH,RENTAL} $1 (+80 chips on two pair/FH), Jumbo Arcana -> Temperance +$5, reroll nothing. Fish: 2 face-up discards first, FH 777JJ 4326, TT + 3 face-down cards 2000, High 6C 368 = 6694+/6400.
Ante 4 (Economy/Orbital/The Club 18000, $5): shop nothing ($5; Matador/Saturn). Small 9000: burned discards, FH JJJKK 4515, High JD dig 560, forced Two Pair TT33 2482 = 7557/9000. LOSS.

## Post-mortem

Binding constraint: scaling. Final build was Hanging Chad + Mystic Summit + a rental Clever: purely flat +chips/+mult with Pair/Trips/FH at L1-L2, zero xMult, 3 of 6 slots, $0-10 wallet all run. Hands topped out ~4500 (full house) against a 9000 Small at ante 4. Money was the second constraint: every shop had $3-10 and rerolls ($5) left $3 after, so jokers priced $4+ were out of reach twice (Bootstraps $7 at $5; Scholar $4 at $3).

Decisions I would change:
1. Ante 2 shop 3 ($8): rerolled to $3 and then saw Scholar $4 (non-eternal, +20 chips/+4 mult per Ace, triggers x3 on Chad's first card). Selling Half Joker ($2) was not an option before the Flint boss, but a reroll of $5 versus buying the Mega/Jumbo pack or keeping $8 for the ante-3 shop was close; I burned $5 for nothing twice (reroll ante 1, ante 2 x2 total ~$15).
2. Ante 3 Small skip for Charm tag gave High Priestess/Death: low value. Playing Small (3200) would have needed ~1100/hand which I could not make; the skip was OK but the pick (planets) did not move the needle.
3. Ante 4 Small: with a 3-hand dig, solver chose a 560 High Card + 3 fillers over Two Pair 2482 now (solver p 0.47 vs 0.39); the dig missed (no T/3 drawn). The disagreement was within noise; no change.

Reusable rules (if-then):
- IF you own Mystic Summit THEN it needs 0 discards REMAINING: spend both discards (toward the made hand) before the first play; est shows both numbers.
- IF you own Hanging Chad THEN a single high Ace/face High Card scores ~3x its chips (Half Joker made a lone Ace 798): lead with the best first scoring card via `move hand`.
- IF Half Joker is owned THEN every <=3-card hand fires +20 mult: even a lone High Card clears ante 1-2 blinds (798/735/672), so don't fill to 5 cards; against The Flint the flat +20 survives base halving.
- IF The Fish flipped your hand AND you must find a pair among face-down cards, THEN include the face-down cards bounded to high ranks (rank-sorted bounds) with your visible pair as a 5-card play: it made two-pair-or-better (2000 from 3 face-downs) and cleared 6326 -> win.
- IF a joker you can almost afford ($4 at $3) would be a permanent flat scorer THEN do not reroll below its price: rerolls at $5 with $8 left cost the $4 joker next time.

Advisor/CLI defects:
- shopadvise ante 1 SIM ranked Crazy Joker (straight-only) +0.44 over a Buffoon pack; the pack gave Half Joker (SIM +0.87 inside the pack). SIM undervalues packs (known blind spot) - the playbook override was right.
- advise at Fish (face-down) cannot value playing the face-down cards; "Otherwise prefer discarding the face-down cards" is wrong when you have 2 hands left and no discards: the facedown dig scored 2000 on 3 unknown cards.
- advise "PLAY HIGH" dig at ante 4 Small (p 0.47) lost; the rule (two pair now) was p 0.39 - no clear defect, just variance.
