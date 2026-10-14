# Run PBATS6ST (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Mark (8872/18000)

Ante 1 (D6/Charm/The Psychic 600, $4): Small: Straight J-high 296 + Pair AA. Shop $5: Buffoon -> Hack{PERISHABLE} (over Square). Big: 2P 96, Flush 308, 2P 116. Shop: Jupiter (Flush L2). Psychic: dig Trips QQQ 180 (keep flush draw), Flush D L2 552 = 732.
Ante 2 (Ethereal/Negative/The Hook 2000, $8): Mad Joker $4 + sold Hack -> Photograph{E} $5 (x2 first face; Even Steven before it = card phase). Small 2P KKJJ 840 + 2P 576. Shop: Even Steven $4 (+4 mult per even card, card phase), Arcana -> Death (2C->QS). Big: FH KKKJJ 1620. Hook: 2P 22/KK 1320 + 2P 88/JJ 1680.
Ante 3 (D6/Uncommon/The Mouth 6400, $6): Swashbuckler{P} $4, sold ($2) for Clever $4. Small: FH 222KK 3168 (order 2s first). Big: Quads 1400 + 2P 66KK 3960. Shop: Jumbo Arcana -> Death (9S->8D). Mouth: FH TTTQQ 7140 one-shot (order evens first, then Q).
Ante 4 (Meteor/Holo/The Mark 18000, $7): foil Mime{P} $7 (+50 chips), skipped Small (9000, $0 shop) for Meteor tag -> Uranus (Two Pair L2) + Mars. Big 13500: 2P 99/88 4284, 2P 66/KK 6464, 2P QQ/JJ 3360 = 14108 (cleared). Shop $4: nothing. Mark 18000: 2P est 6k/hand needed all 3 hands; TT + 3 face-downs made only a Pair (800), then 2P 66/22 5394 + 2P AA77 2678 = 8872. LOSS.

## Post-mortem

Binding constraint: scaling. Final build was Mad (+10) + Photograph (x2 first face) + Even Steven (+4/even card, card phase) + Clever (+80 chips) + foil Mime (+50 chips): a flat +mult/+chips build on Two Pair L2 made 4-7k per good hand. That cleared ante 3 comfortably (Mouth one-shot) and the ante-4 Big by 600, but the ante-4 boss needs 18000 = 3 perfect 6k hands; with 0 xMult (only Photograph's card-phase x2) and $0-7 every shop there was no way to scale. The first-buy rule (permanent +mult x2 by end of ante 2) was met (Mad, Even Steven), but money stayed at $0-7 for the whole run (Gold Small pays $0, each shop spent to $0-2), so no xMult/Buffoon pack/reroll was ever affordable.

Decisions I would change:
1. Ante 4 Mark hand 1: I played TT + 3 face-downs hoping for a rank pair (85% by my calc: 4 face-downs always contain one) but the 3 picked were K,Q,J distinct (the 4th was the match) -> Pair 800 instead of ~6.7k. Playing TTT + a different guess would not have been better; the real error was playing it as hand 1 with 2 hands left needing 6k+ each. Better: use the 1 discard first? No: the real fix is scale before ante 4.
2. Ante 4 shop 1: bought foil Mime{P} for $7 (all my money) for +50 chips; maybe a Standard/Arcana pack for Justice (Glass) would have scaled more. Unknown.
3. Ante 3: I could have skipped Small to take Uncommon... no, played them fine. No clear fix; the build was one xMult short from ante 3 on.

Reusable rules (if-then):
- IF you own Photograph and Even Steven (or any card-phase +mult), THEN `order hand` so the scoring cards are in the order: even/+mult cards first, the face pair last. Photograph doubles only what accumulated before it: est went 968 -> 1320 and 2376 -> 3168 just by reordering (advisor prints the REORDER hint; follow it).
- IF Death is in a pack, THEN copy onto junk so the deck concentrates 2 ranks (a face rank + an even rank); the third Q and fifth 8 made Quads/Full House appear several times (FH TTTQQ 7140 beat The Mouth 6400 in one hand).
- IF a Mouth/boss locks a type and a Full House is in hand with est >= need, THEN play it, reorder evens first.
- IF The Mark (face-down faces) and you hold 4 face-downs, THEN do not expect 3 chosen face-downs to pair (they matched only 15% of the time on my choice); sorting by rank keeps face-downs in descending rank order but it did not help me identify which equal pair. Plan the hand as a plain TTT-or-Pair, not a two-pair.
- IF the Small blind is skippable for a free Celestial pack tag (Meteor) while you have $0 (its shop is unusable and the Small pays $0), THEN skip it: free Two Pair level and no 9000 fight.

Advisor/CLI defects:
- shopadvise EMERGENCY text says "buy the cheapest multiplier through the floor" but at $4-7 nothing multiplicative was offered in 6 shops; no output about how to get cash (interest requires $5+, Small pays $0). A suggestion to skip purchases that cost the interest threshold is missing.
- Face-down `sel`/`hands` give no true-rank information and the solver treated my 3-face-down play as a pair play (est 800): fine, but advise did not mention that a face-down pair among exactly 3 chosen cards is only ~50-60%.
- Solver round p on The Mark showed 0.19 max ("low confidence"); it said UNWINNABLE only after hand 1. A shop-time warning that Mark 18000 needs three 6k hands (all of them perfect) would have flagged that the ante-4 shop needed an xMult not a +50 chips Mime.
