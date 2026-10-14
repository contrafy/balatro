# Run ZYK9EUJR (port 7807, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (36698/60000)

Ante 1 (Holo/Rare/The Pillar 600, $4): Small: disc to Straight J-7 296 + High 4S. Shop $5: Even Steven{ETERNAL} $4 (SIM 0.98). Big: 2P TT66 936 one-shot. Shop $7: Gros Michel{RENTAL} $1 (SIM 0.90 vs 0.63). Pillar: 2P KK77 918 one-shot.
Ante 2 (Buffoon/D6/The Club 2000, $10): Raised Fist{PERISH} $5 (SIM +0.19). Skipped Small for Buffoon -> Mega Buffoon: Half Joker{ETERNAL} (skipped Photograph{PERISH,RENTAL}: 2nd rental). Big: Pair AA 1312 + JJ. Shop $7: Jumbo Celestial $6 -> Mercury (Pair L2). Club: Pair TT 1610 + 99 1806. $-2 after rent.
Ante 3 (Holo/D6/The Manacle 6400, $4): sold Raised Fist (perishing) to afford Constellation{E} $6, then SIM showed Constellation 0.00 vs Jumbo Buffoon 0.51 -> Buffoon: Odd Todd{PERISH}. Skipped Small (broke, Holo tag). Big: Pair 77 3838 + 33 3534. Gros Michel went extinct. Shop: free holo Hologram (tag). Manacle: disc KK, spade Flush 3510 + Pair 33 3069 (exact).
Ante 4 (Foil/Standard/The Fish 18000, $8): EMERGENCY 0.20 -> Ice Cream $5 (SIM 0.26 vs 0.00). Skipped Small AND Big (overrode `s`: broke shop, saved Odd Todd tick; Standard tag -> Mega Standard TS + 9C, Hologram x1.5). Fish: Pair KK 7177, High AH 6603, High 5C 6091 (sel; `hands` only listed JC 4882) = 19871.
Ante 5 (Negative/Skip/The Mark 50000, $8): free foil Mail-In Rebate{RENTAL}. Small 25000: Pair AA 12078 + 88 10516, dug for 7s (+$5), Trips 222. Shop $12: sold Odd Todd -> Mr. Bones $5, Jumbo Standard -> mult/purple-seal AC (Hologram x1.75). Skipped Big (Skip tag +$25). Mark: discarded purple AC (-> Chariot), Trips TTT 14175 + 2 weak hands = 27.8k/50000: Mr. Bones saved the run.
Ante 6 (D6/Voucher/The Wall 240000, $30): Spectral (Ankh/Ectoplasm, skipped), 2 rerolls (nothing), Swashbuckler{E} $4 (+12 mult), Celestial -> Venus. Small 60000: solver "UNWINNABLE" (exp ~39k); 2 discards found no trips; Pair 88 13541 + AA 12605 + 77 10552 = 36698. Dead.

## Post-mortem

Binding constraint: SCALING. I never owned a real xMult beyond Hologram x1.75 (fed by only 3 cards). Every hand was a
2-card Pair (Half Joker +20) on Pair L2 with flat +mult/+chips: ~3k at ante 3, ~7k at ante 4, ~12k at ante 5, ~13.5k at
ante 6 against a 20k-per-hand Small. Money was the cause of the scaling gap: Gros Michel rent (-$9 over 3 rounds) plus the
Jumbo Celestial left me at $-2/$0/$2/$3 through antes 2-4, so nothing (Constellation $6 twice, Photograph{E} $5, Mega
Buffoon $8) was affordable when it appeared.

Decisions I would change:
1. Ante 3 shop: sold Raised Fist to afford Constellation{E}, then bought the Jumbo Buffoon instead (SIM 0.00 vs 0.51 only
   showed AFTER the sale). Run `shopadvise` on the sell-then-buy line BEFORE selling: the sale removed a scorer for nothing.
2. Ante 2 Big shop: Jumbo Celestial $6 down to $1 (SIM +0.15) on a 2-rental-free but rent-paying wallet. It kept me broke
   for two antes; Constellation (offered the next two shops at $6) would have turned every later planet into xMult.
3. Ante 1: Gros Michel{RENTAL} was right for survival, but I should have planned its sale: it cost $9 in rent before going
   extinct, exactly the money missing for Constellation at ante 3.
4. Ante 5: Jumbo Standard ($6) for +0.25 Hologram; with the Skip tag money coming, holding cash for an ante-6 xMult was
   equal; fine either way.

Reusable rules (if-then):
- IF you are about to sell a joker to afford X, THEN run `shopadvise` first and confirm the SIM line for X is positive;
  SIM can rate a growth xMult at 0.00 (no planets to feed it) and prefer a pack instead.
- IF you own Mr. Bones and the boss is out of reach but 25% of it is not, THEN skip the Big Blind (Skip tag money) and let
  Bones carry the boss; it bought one more ante here (Mark 27.8k/50k).
- IF the Small Blind pays $0 and your money after rent is under $5 at ante 3-4, THEN skipping it costs nothing (its shop
  buys nothing) and saves a rent charge + perishable tick; skipping Small AND Big at ante 4 for a Standard tag was fine.
- IF the boss is The Mark and 4+ cards are face-down, THEN playing them blind is a 4-card hand: Half Joker (+20 at <=3)
  turns off (3640 actual vs ~9k hoped); play 3 face-down cards or a visible pair instead.
- IF your best High Card candidate is the top rank, THEN still `sel` the odd/even low cards when Odd Todd / Even Steven are
  owned: 5C high card 6091 vs JC 4882 at the Fish.
- IF a pack contains a purple-seal card and you will discard anyway, THEN discard it for a free Tarot.

Advisor/CLI defects:
- `hands`/`advise` High Card lists only the highest rank (JC 4882) and missed 5C 6091 / TC 5512 with Odd Todd/Even Steven.
- shopadvise "main hand Two Pair" while owning Half Joker{E} and playing 2-card Pairs (Mercury pick note "NOT your main
  hand" was wrong at ante 2).
- `pick 4` in a Jumbo Standard pack was REFUSED ("pick 4 was None in the listing you saw") after only `s`; it worked after
  running `advise` (which printed "No pack advice for this pack type").
- Constellation{E} SIM 0.00 at ante 3 shown only after I sold Raised Fist; the rule line (score 110) had ranked it first.
- SIM baseline jumped 0.47 -> 0.00 from selling a 3-round perishable Raised Fist (~12% of mult) at ante 3; looks too
  sensitive.
