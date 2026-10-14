# Run PAWYYBSZ (port 7815, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 6 boss The House (98658/120000)

Ante 1 (Double/Voucher/The Window 600, $4): Small: Flush 308 (kept JJ+4 hearts draw). Shop $6: Abstract{PERISH} $4. Big: 2P JJ22 220 + 2P KK77 270. Shop $7: sold Abstract ($2) -> Joker Stencil $8 (x6 with 6 free slots). Window: Flush 1656.
Ante 2 (Buffoon/Economy/The Needle 1000, $8): reroll nothing. Skipped Small for Buffoon tag (Mega Buffoon: Smiley Face + Gros Michel; Stencil x4, order +mult left). Big: Straight 3800. Jupiter. Needle: 2P 2992.
Ante 3 (Handy/Foil/The Hook 6400, $11): Saturn, skipped Small for Handy (+$6). Big: 2P 2312 + Pair KK 3240. Shop $20: Ramen $6 (Stencil x3, Ramen x2), Jupiter (Flush L3). Hook: Flush clubs 19404.
Ante 4 (Rare/D6/The Goad 18000, $16): Jupiter (Flush L4), High Priestess -> Uranus + Mercury. Skipped Small (Rare tag) -> post-Big shop Stuntman{E} $0 (+250 chips, hand size 6). Big: Straight 16342. Goad: 1-card High JH 21592.
Ante 5 (Meteor/Uncommon/The Water 50000, $21): rerolls found nothing, then Acrobat $6; MISTAKE: sold Ramen + Smiley to fit it (miscounted Stencil: 5 jokers = x2 not x3). Small: Straight 28168. Big: two 1-card Highs 21592. Water: 12720 + 12720 + final Pair TT x3 47790.
Ante 6 (Voucher/Juggle/The House 120000, $2-11): reroll + Mercury. Small: Pair 17442 + High 12768 + final Pair JJ 53010 (Acrobat). Skipped Big (90k vs ~85k/round) for Juggle (+3 hand size) -> House: disc 5 face-down, disc the other 4, Pair 99 17556, Flush D 27750, final Pair AA 53352 = 98658/120000 (needed a hearts flush final ~83k, drew none).

## Post-mortem

Binding constraint: scaling at ante 6. Engine = Stencil x3 + Gros Michel +15 + Stuntman +250 chips + Acrobat x3 (final only): 1-card hands ~12.7k, final hand ~48-53k, ~85k/round vs 90k Big / 120k Boss. Money was $2-11 from ante 4 on (Small pays $0, nothing to spend on), so no xMult/Blueprint reroll hunt was ever affordable more than twice. No growth xMult (Throwback/Obelisk/Hologram) was seen in ~8 shops + 3 packs.

Decisions I would change:
1. Ante 5 shop: selling Ramen (x1.94) + Smiley to buy Acrobat. I thought Stencil would stay x3; it is x(empty slots + 1): 4 jokers = x3, 5 jokers = x2. Net effect: non-final hands lost ~35%, final hand gained ~55%. Should have kept Ramen and NOT bought Acrobat unless a free 5th slot still left Stencil >= x2 AND I kept Ramen (Stencil x2 + Ramen + Acrobat + Gros + Stuntman = all 5 slots, nothing sold except Smiley).
2. Ante 5: used 3 rerolls ($17) before Acrobat showed; money for ante 6 was then $2. A Throwback/Obelisk-style growth was never found; with Stencil I never held 4+ jokers worth of money for rerolls.
3. Ante 6 Big skip for Juggle was a coin flip; fine but the House's first hand being face-down plus 0 discards left cost the Flush draw.

Reusable rules (if-then):
- IF you own Joker Stencil, THEN value = x(6 - jokers + 1): every joker you add costs 1 x. Count BEFORE selling/buying: 4 jokers = x3, 5 = x2, 6 = x1. A new joker must beat (stencil_now / stencil_next) to be worth a slot.
- IF Stencil + a flat +chips joker (Stuntman +250) + Gros Michel (+15 mult) are owned, THEN any 1-card High Card scores ~13-22k at ante 4-5: play single spare cards, keep the pair/flush/straight for the Acrobat final hand (x3).
- IF a free Rare Tag appears at ante 4 and you own Stencil, THEN take it: it paid Stuntman $0 (a 4x jump 7k -> 29k best hand).
- IF the boss is The House, THEN discard 5 face-down cards first (new cards come face up), then the other 4 face-down ones; a 9-card hand (Juggle tag) gives a visible 5-diamond flush after a pair spare.
- IF you need a total over N hands and the last hand has Acrobat x3, THEN compute (spare1 + spare2 + 3*final_est) at the start; mine was 17+17+53 = 87k vs 90k Big, so it was clear at ante 6 that a 2x scale-up (growth xMult) was needed by the ante-5 shop.

Advisor/CLI defects:
- shopadvise at ante 5 printed "buy Acrobat" without warning that buying it at 5 jokers drops Stencil x3 -> x2 (it does model Stencil in AVOID text for other jokers but ranked nothing for Acrobat because I sold first); no check that selling Ramen/Smiley loses more than Acrobat adds.
- advise `HIGH 1` suggestions under Acrobat were right (spare 1-card, keep the pair for final).
- Parallel `s` + `endshop` call in one tool batch returned a stale shop; avoid parallel b.sh calls (my fault, but the CLI does not guard it).
