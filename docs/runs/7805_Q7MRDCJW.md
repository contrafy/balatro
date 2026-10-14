# Run Q7MRDCJW (port 7805, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 3 blind Big Blind (4578/4800)

Ante 1 (Charm/Uncommon/The Window 600, $4): Small jokerless: disc around KK44, disc to KK + 4 clubs -> club Flush 308 one-shot. Shop $6 (Blackboard $6, Photograph{P,R} $1, Buffoon $4): Buffoon -> Gluttonous{P,R} (+3/club; Swashbuckler the other card); passed Photograph{P,R} (2nd rental). Big 450: 2P 5522 170 + club Flush 1292. Shop $4: Mad Joker{RENTAL} $1 (+10 on Two Pair; Photograph $5 permanent $1 short). Window: disc 4 debuffed/off-suit -> club Flush 1444 one-shot.
Ante 2 (Meteor/Foil/The Hook 2000, $4): shop $4 (Mega Buffoon $8, Ride the Bus $6 unaffordable): left. Skipped Small (rent-broke, Meteor -> Uranus + Jupiter). Big 1500: Straight 3-7 385 (solver p 0.98), disc, 2P AAKK 1312. Shop $3: left. Hook: 2 discs -> club Flush L2 1869 + 2P KK22 = cleared.
Ante 3 (Negative/Holo/The Psychic 6400, $3): EMERGENCY 0.16. Sold Gluttonous (1 round left), Buffoon $4 -> Even Steven{P,R} (Delayed Gratification other); Photograph{ETERNAL} $5 unaffordable. $0. Skipped Small 3200 (rent-broke, Negative tag). Big 4800: 2P QQTT 1680, disc, 2P KK66 1512 (solver 0.57), last disc missed (needed an 8 or even diamond): 2P AA22 1386 -> 4578/4800. GAME OVER.

## Post-mortem

Binding constraint: MONEY -> scaling. Every scorer I ever owned was a RENTAL (Gluttonous{P,R}, Mad{R}, Even Steven{P,R}).
Rent paid: $21 over 7 rounds (Gluttonous $12, Mad $9) against ~$4-6 income per round, so the wallet never exceeded $6
after ante 1 and was $0-4 in every shop. Two permanent scorers that would have changed the run were in shops at $5:
Photograph (ante 1, shop 2, $4 in hand) and Photograph{ETERNAL} (ante 3, $3 in hand). Lost the ante-3 Big by 222.

Decisions I would change:
1. Ante 1 shop 2 ($4): bought Mad{RENTAL} $1 as a 2nd rental while holding Gluttonous{P,R}. Better: sell Gluttonous ($1)
   and buy permanent Photograph $5 (no rent), or at least sell Gluttonous right there instead of keeping both through
   the Window (cost $3 and both rentals then overlapped for 3 rounds = $9 extra). The Window was a one-shot club flush.
2. Ante 1 shop 1 ($6): the permanent Blackboard $6 (x3 with black held cards, SIM 0.25) vs Buffoon (0.22) -> rental.
   With rent-free scoring the ante-2 shops (Mega Buffoon $8, Ride the Bus $6) would have been reachable. Unclear, but the
   rental chain is what killed the run.
3. Ante 3 Big hand 3: alternatives were all ~0.25; no big misplay there. Ante 3 Small skip (Negative tag) was forced by
   $0 money; playing a 3200 Small with ~1500 hands was no better.

Reusable rules (if-then):
- IF you already own one rental AND income per round is <= $6, THEN a second rental (even $1, even SIM +0.25) makes every
  later shop $0-4: prefer selling the first rental for a $5 permanent joker in the same shop if one is on offer.
- IF a perishable rental has <= 2 rounds left and its score is not needed to clear the next blind with margin, THEN sell
  it now: its remaining rent ($3/round) is better spent on a permanent replacement.
- IF your scorers are Mad Joker / Even Steven style flat +mult only at ante 3 (Two Pair ~1500), THEN the ante-3 Big
  (4800) is a coin flip: the xMult/permanent-scorer purchase must happen in ante 2, which requires NOT bleeding rent.
- IF Even Steven is owned, THEN two pair of even ranks (88 22) is worth ~+50% over odd pairs; keep even pairs/even
  same-suit cards when digging.

Advisor/CLI defects:
- shopadvise ante 1 shop 1, right after I took Gluttonous{P,R} from the pack, still ranked Photograph{P,R} "NEEDED NOW"
  (SIM +0.18 though its own line said "a later shop sees $-3"): NEEDED NOW should not fire for a 2nd rental when a
  scorer is already owned.
- shopadvise ante 1 shop 2 printed ADVICE LEAVE while its SIM rated Mad{RENTAL} +0.25 and never proposed SELL Gluttonous
  -> BUY Photograph $5 (a permanent option $1 out of reach that a sale would fund).
- SCORE CHECK at ante 3 (~936-1040) under-reads a dig build: the actual hands were 1386-1680 with Even Steven.
Bridge issues: none (45 steps, no rejects).
