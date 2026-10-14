# Run B2SNYDTS (port 7810, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 boss The Psychic (11152/18000)

Ante 1 (Rare/Foil/The Club 600, $4): Small: Straight 9-high 260 + Pair 3 32 + High A = 308. Shop $4: Buffoon pack -> holo Scholar{ETERNAL} (+10 mult edition, +20 chips/+4 mult per Ace; over Ramen). Big: Pair AA 1440 one-shot. Shop $6: left (Walkie Talkie eternal junk). Club: Trips 222 442 + Two Pair QQ55 600.
Ante 2 (Rare/Investment/The Window 2000, $13): rerolled once ($8), Shoot the Moon{PERISHABLE,RENTAL} $1 (+13 mult per Queen held). Skipped Small for Rare tag -> free The Order{ETERNAL} (x3 Straight) + Seeing Double{PERISHABLE} $6 -> $3. Big: 2P JJ22 1100 + 2P TT88 1400. Window: Pair 99 1064 + 2P QQ99 1176.
Ante 3 (Polychrome/Charm/The Pillar 6400, $6): no joker worth buying. Small 3200: discards to a 4-straight draw, drew 6S -> STRAIGHT FLUSH TS-6S 13020 one-shot (Order x3). Big 4800: Pair AA 2376 + Trips KKK 3120. Shop: Sly $3 + Devious $4 (both PERISHABLE) -> $0. Pillar: FH JJJ55 3640 + Pair AA 2639 + Pair 66 3600 = 9.9k (cleared by 1 hand to spare). Rent charged to -$3; sold perished Shoot the Moon.
Ante 4 (Double/Holo/The Psychic 18000, $3): sold Seeing Double for $3 -> Jumbo Buffoon $6 -> Popcorn (+20 mult -4/round; passed Raised Fist). Skipped Small (Double Tag) AND Big (Holo x2) to keep Popcorn +20 and fight only the boss. Psychic (5 cards forced, 2 discards): kept gutshot 7S 6C 4S 3S -> drew A A (no 5): Pair AA 4880 (played as 5 cards) + 2P 6644 2880 (dig: kept 9 8 7 for a straight) + final 2P TT88 3392 = 11152/18000. No straight hit; the final draws were J/T/Q (needed J or 6).

## Post-mortem

Binding constraint: SCALING. Reached ante 4 with only flat chips/mult + a conditional x3 (Straight) and three perishable/rental bridges; best non-straight hand ~2.5-5k vs 9k/13.5k/18k. The whole run rode on drawing a straight (Order x3 + Devious +100 = ~17k). It worked once (SF 13020 at ante 3) and failed at the ante 4 boss: Psychic's 5-card rule leaves only 3 hands, so after a 4 and a 3 outs-draw the straight never landed.

Decisions I would change:
1. Ante 1 Buffoon: Scholar (eternal, Aces only) over Ramen. Scholar worked for 3 antes (holo +10 and ~every Ace pair 1.4k-2.6k) but it is a flat joker; Ramen x2 would have been a real xMult kept alive with few discards. Hard to say; Scholar did get me to ante 4.
2. Ante 3 shop: $7 -> $0 on Sly + Devious (perishable) left zero buffer; rent put me at -$3. A Jumbo Buffoon pack at ante 3 ($6) instead of two perishable flats might have found an xMult/Fist; I only found Popcorn/Raised Fist at ante 4 with the last $6.
3. Ante 4 at the Psychic: both discards went into a gutshot (7-6-4-3, only a 5 completes, 4 outs) instead of an open-ended run; the first draw gave AA (Pair 4880) but no 5. Two hands later I had 9-8-7 + T/Q but needed J or 6. With only 3 plays, keep the 8-out draw.
4. Money: ended every shop at $0-6. Never saw a Seed Money/interest; Grabber $10 (extra hand = extra straight draw) was never affordable.

Reusable rules (if-then):
- IF you own The Order (x3 Straight) + Devious/flat chips, THEN keep 4-card straight draws at every blind (discard to draw, do not bank pairs); a straight/SF scored 13k at ante 3 vs ~2.5k for pairs. Count outs: open-ended (8 outs) is ~2x better than gutshot (4 outs): prefer keeping open-ended 4-runs (e.g. 7-8-9-T) over gutshots.
- IF a perishable/rental joker has 1 round left AND the shop offers a pack you cannot afford, THEN sell it before the end of the round/shop for cash (Seeing Double sold for $3 funded the $6 Jumbo Buffoon). Selling a perished rental in ROUND_EVAL before cash out stops the next rent charge.
- IF you hold Popcorn / a decaying joker, THEN skipping blinds does not tick it: skip Small+Big to fight the boss at full +20 (Double Tag duplicates the next tag; Holo x2 = 2 free holo jokers in the next shop).
- IF the boss is The Psychic, THEN every play is exactly 5 cards: Pair A with 3 fillers still scores 4880 (fillers don't count), so banking a pair costs only the filler cards; but straights need all 5 cards, so keep an OPEN-ENDED straight draw, not a gutshot.
- IF holding Shoot the Moon (+13 per held Queen), THEN play pairs/two pairs with fillers that are not Queens and keep QD/QS held (verified est +13/Queen).
- IF the first Buffoon pack offers a holo edition scorer (even Eternal), THEN take it over a decaying xMult at ante 1: holo +10 mult is worth ~5x a Pair at ante 1 (Pair AA = 1440 vs 450 Big).
- IF a Rare tag is skipped for at ante 2, THEN expect an Eternal joker: The Order{ETERNAL} (x3 Straight) was fine, only because 4 free slots remained.

Advisor/CLI defects:
- shopadvise at ante 3: SIM baseline said "P(clear all next 3 blinds) 0.00 / 0.41" inconsistently across visits for the same state; SIM rates flat perishables (Sly 0.00, Devious +0.18) with no explanation of Straight-count assumption. It recommended Devious +100 chips if Straight (+0.18) but Sly 0.00, which ended up not mattering.
- shopadvise ranked Seeing Double (x2 if Club + other suit) as SIM +0.32 at ante 2: it fired often in practice (est included it), no defect there.
- advise at ante 4 Psychic: gave "SOLVER ... p 0.86" for the straight-draw discard that failed twice; n=100 samples are noisy. The solver does not model Psychic's forced 5-card plays correctly for the draw odds (it counted "4 outs, p=0.33") and I over-trusted a gutshot.
- The pack advisor SIM preferred Raised Fist (0.27) over Popcorn (0.20) for the ante-4 pack: SIM probably values Fist's longevity; I overrode with Popcorn and then skipped to keep it unticked. No evidence which was right.
