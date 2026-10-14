# Run NZDVLMA4 (port 7811, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Head (17606/18000)

Ante 1 (Economy/Investment/The Club 600, $4): Small Straight Q-high 308. Buffoon pack -> Lusty Joker{E}; Big Trips 252 + Straight K-high 790; shop Buffoon -> Misprint{E}. Club: discards to a 4-heart draw, Heart Flush 1482 (Lusty +3/heart).
Ante 2 (Orbital/Orbital/The Manacle 2000): Celestial packs -> Jupiter (Flush L2), Uranus. Skipped Small for Orbital Tag (+3 Trips levels = L4 90x9). Big Trips QQQ; Judgement $3 -> Shoot the Moon (+13 mult per Queen HELD). Manacle: 2P 1976 + 2P.
Ante 3 (Skip/Investment/The Mouth 6400): Even Steven{PERISH} $4 (EMERGENCY 0.33). Small 2P 3108 + Pair; Big Trips 4080 + Pair 66 704 (missed by 16) + Pair; Vagabond{PERISH, foil} $10 (tarot per hand at <=$4 money). Mouth: locked High Card, 1-card hands ~2700-3400 each (Shoot the Moon with 2 Queens held), 6400 cleared.
Ante 4 (Juggle/D6/The Head 18000): Vagabond tarots: Star (3 cards to diamonds -> 5-diamond Flush 7242 vs Small 9000), Death + Fool(copy) -> 2 more Queens (4 held), High Card 4361. Big 13500: Trips AAA 6055, Pair 88 2957, Pair 55 w/ Hierophant bonus 4857 (cleared 14k). MISTAKE: typed `pack 2` meaning the Jumbo Buffoon (slot 1) and bought a Standard Pack for $4 (could not afford the Buffoon after). Head debuffs Hearts (2 of my 6 Queens + Lusty): Trips JJJ 6240, High Card 3036, last hand Magician lucky on 2 Queens + Trips QQQ 8330 (both lucky procs hit) = 17606/18000. Lost by 394.

## Post-mortem

Binding constraint: no xMult at all by ante 4 (flat mult + Shoot the Moon held-Queen mult +13/Queen). Round ~1.06x the Big and 0.7x the Head boss. 6 jokers never filled: 4 slots, $0-6 all run, never saw a Buffoon pack I could afford past ante 2.

Decisions I would change:
1. Ante 4 shop: typed `pack 2` instead of `pack 1`: bought a Standard Pack ($4) not the Jumbo Buffoon ($6), money gone. 394 short at the boss; a Buffoon pick (any +mult/xMult) or the $4 kept for rerolls could have closed it. ALWAYS use a name guard (`pack Jumbo`/`buy Name`) in packs/slots; slot numbers shift after a purchase empties a slot.
2. Ante 4 Small: the skip-free route would not have helped, but I discarded 5-6 times digging for Queens at the Small (7242 of 9000) and cleared only because The Star made a 5-diamond Flush; Death/Fool and Hierophant also came from Vagabond. Vagabond at <=$4 money (foil +50 chips, 1 tarot/hand) was the best $10 of the run: it supplied Death x2, Hierophant, Hanged Man, Magician, Chariot, Star. Buy it earlier (ante 2) when broke anyway.
3. Never found an xMult: 3 Celestial packs ($12 total) at ante 2-3 gave planets that barely mattered once Trips L4 existed; the same money in rerolls/Buffoon packs was the only xMult path.

Reusable rules (if-then):
- IF you own Shoot the Moon (+13 mult per Queen HELD), THEN 1-card High Card plays score 2500-4400 (est counts held Queens): at The Mouth lock High Card and keep every Queen in hand; use Death/Fool on junk LEFT of a Queen to clone Queens (each clone = +13 mult for ever).
- IF Vagabond is owned, THEN keep money <= $4 before every hand (spend on packs, not interest): it makes 1 tarot per hand played; Fool copies the last tarot used (Death twice).
- IF an Orbital Tag names your main-hand type (Trips here), THEN skip the $0 Small for it: +3 levels (Trips 30x3 -> 90x9) cleared antes 2-3.
- IF a hand of 8 cards has 3-5 cards of one suit and Star/Lusty-type suit jokers exist, THEN The Star on 3 off-suit cards makes a 5-card Flush (7242 at ante 4).
- IF The Head is the boss, THEN hearts are debuffed: held-card jokers (Shoot the Moon) ignore debuffed Queens of Hearts; clone non-heart Queens before it.
- IF the last hand needs ~2.5x its est and you hold Magician, THEN Lucky on the two scoring cards (+20 mult at 1 in 5 each) is a real 4% line; it hit twice here (est 3485 -> actual 8330).
- NEVER index a pack/slot by memory after buying: re-read `s` and use the name guard.

Advisor/CLI defects:
- shopadvise ranked a $6 Jumbo Buffoon Pack 95 correctly but its `ADVICE: b pack 1` form was ambiguous when I later re-typed: `pack 2` bought a Standard Pack with no confirmation of the pack type (the CLI printed "pack 2 = Standard Pack" only after sending). A `--expect` guard for packs would have prevented it.
- SCORE CHECK / BOSS WARNING projected ~12.6k vs The Head 18000 but did not model held-card jokers (Shoot the Moon) debuffed by The Head or the Magician/Death tarots; est for 1-card High Card under Mouth/Shoot the Moon was right (2739 est vs 3432 actual).
- advise at ante 4 Small suggested discards toward Two Pair that ignored a 5-diamond flush made possible by The Star in hand.
- est understates Misprint (older note): Pair 55 4857 est vs 5000+ actual typical; Trips QQQ lucky est 3485 (floor, lucky excluded) vs 8330.
