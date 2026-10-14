# Run IBXYJAUA (port 7804, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Wheel (14782/18000)

Ante 1 (Voucher/Economy/The Pillar 600, $4): Small Flush 272 + Pair TT. Shop $5: Blue Joker $5 (SIM 0.43 vs Buffoon 0.19). Big 2P QQ66 + Pair 44 (2-card plays for Pillar). Shop $5: Obelisk{RENTAL} $1 (only rental). Pillar: disc debuffed, FH AAA66 729 one-shot.
Ante 2 (Coupon/Rare/The Manacle 2000, $8): EMERGENCY 0.30 -> Wrathful $5, ordered left of Obelisk. Skipped Small (Coupon). Big: spade Flush 4495 one-shot. Coupon shop: Jumbo Arcana -> The World (3 cards to spades), Arcana -> Chariot (steel KD), free Seance (sell $3); overrode advisor BUY of a 2nd rental Supernova. Manacle: 2P 1766 + High KH + High QH (kept Obelisk growing to x2).
Ante 3 (Double/Meteor/The Club 6400, $8): EMERGENCY 0.33 -> Supernova $5 (permanent; tie with perishable Baseball). Small: dig, spade Flush 3124 (4-way Obelisk tie forced reset) + High 5S. Shop $1 (rent). Big: 2P AA66 2063, straight dig, Straight 1535, FH 555TT 2700 (p 0.73 spot). Shop $2: left. Club: Pair QQ+fillers 1728, Straight J-7 4158, Pair KK 630 = 6515/6400.
Ante 4 (Investment/Juggle/The Wheel 18000, $4): EMERGENCY 0.17 -> sold Seance, Half Joker{PERISHABLE} $5. Small: High QS 3708, High AC (cheap Obelisk reset at x1.2) 2703, Pair 99 3628. Shop $-1 (rent): nothing affordable. Skipped Big (rent-broke, 1.05x, Juggle +3 hand size for the boss). Wheel (11 cards): Trips 444 4166, Trips 333 5152, two digs, spade Flush 5464 = 14782/18000. GAME OVER.

## Post-mortem

Binding constraint: money, and through it scaling. Every shop from ante 2 on was entered with $-1 to $8: Gold Small Blinds
pay $0 and the Obelisk rental took $3 every round, so income net of rent was ~$2-4 per round. I bought exactly four
scorers in the whole run (Blue, Wrathful, Supernova, Half Joker), all flat; I never had $6-8 in a shop where a real xMult
could have been bought, and the only xMult was Obelisk, which kept resetting.

Obelisk as a $1 rental was the wrong first xMult for this deck. It only grows on hands that are not your most-played
type, but with 3 hands/round and ~5 common types the counts tie quickly (4-way tie at 2 plays by ante 3, so EVERY made
hand reset it). Its value peaked at x2.2 and it sat at x1-x1.4 most of the time, while costing $3 x 9 rounds = $27 —
more than everything I spent on jokers. Then Half Joker (+20 on <=3 cards) pushed me onto Pair/High Card, the two
types that were already tied at the top, so Half Joker and Obelisk fought each other.

Decisions I would change:
1. Ante 1 Big shop: Obelisk{RENTAL} $1 (SIM +0.26). On Gold the rent turns into the whole economy. A Buffoon pack next
   shop or simply banking $5 toward a permanent +mult joker was better. Growth xMults that reset (Obelisk) are not
   "reliable" enough to be worth rent at ante 1.
2. Ante 3 Small shop ($1) / ante 4 shop ($-1): I should have sold Obelisk once it was reset to x1 and I was under $8 two
   shops in a row: it was a flat-ish x1.2 rental by then, and $3/round over 4 rounds would have bought Half Joker plus a
   main-hand planet or a Buffoon pack earlier.
3. Ante 3 Big, hand 1: I played Two Pair AA66 (est 2063) over the solver's AAKK + filler (p 0.96 vs 0.89); the round
   went to a p 0.73 spot. Small, but trust the solver's PLAY line at n>=100 when it leads by >= 0.05.

Reusable rules (if-then):
- IF Gold ante 1-2 AND the only xMult offered is Obelisk{RENTAL}, THEN do not buy it unless you already own 2 +mult
  scorers: with 3 hands a round the type counts tie within ~2 antes and every made hand resets it, while rent eats
  ~$9 per ante (this run: peak x2.2, average ~x1.4, $27 rent).
- IF you own Obelisk AND 3+ types are tied at the top, THEN reset it on purpose with the cheapest hand while it is
  x1.0-1.4 (one type then leads by 1) instead of waiting until it is high.
- IF you own Obelisk, THEN do not buy Half Joker / Pair-gated jokers that force the max type; they cancel each other.
- IF money is < $3 after rent at two shops in a row AND your rental is below x1.5, THEN sell the rental at once.
- IF rent-broke at ante 3-4 AND the Big's tag is Juggle (+3 hand size) AND the boss ratio is < 0.7, THEN skipping the
  Big is reasonable: it only gave 11 cards at the boss here, which helped find trips but cannot fix a 0.6x build.

Advisor/CLI defects:
- shopadvise ADVICE at ante 2 Coupon shop: `BUY -> b buy 1` (Supernova{RENTAL}) while already owning the Obelisk rental
  (a 2nd rental before ante 5); the ADVICE line itself broke the hard rule (later in the run the same case was correctly
  printed as BARRED).
- advise notes "Obelisk resets to x1: this is your most played hand" appear on every candidate list even when the
  top candidate (e.g. Two Pair at 2 plays vs Flush/High at 3) would not reset it; the note should be per hand.
- SIM rated Obelisk{RENTAL} $1 at ante 1 at +0.26 (the best buy): it does not model the rent through ante 3-4 nor the
  tie-driven resets; the economic death came 2 antes later.
- At the Wheel boss the solver said p 0.31 for Trips 333 with 2 hands left when the max reachable last hand (~6.4k)
  was below the remaining 8682; the "low confidence" label was right, the number was not.
