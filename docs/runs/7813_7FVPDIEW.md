# Run 7FVPDIEW (port 7813, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 Small Blind (6946/9000)

Ante 1 (Juggle/Juggle/The Head 600, $4): Small 300: dug Pair 77 -> Pair+fillers 48, then club Flush 276. Shop $5: Abstract Joker $4 (SIM +0.39 over Buffoon). Big 450: dug open-ended straight, J-high Straight 518. Shop $7: Raised Fist{PERISHABLE,RENTAL} $1 (NEEDED NOW, SIM +0.85). Head: Trips 777 + 2 low fillers (Raised Fist then hits 6S) 1071.
Ante 2 (D6/Coupon/The Mark 2000, $10): passed Even Steven{RENTAL}, Celestial. Small 1000: Two Pair AA55 832 + Pair TT 720. Shop $9: Burglar{ETERNAL} $6 (+3 hands, 0 discards; 6 hands/round). Skipped Big for Coupon (broke, saves rent). Mark: 3 facedown cards played blind = pair 630, then Trips 1530 -> 2520/2000.
Ante 3 (Charm/Garbage/The Needle 3200, $8): Coupon shop: free Jumbo Celestial -> Mercury, free Jumbo Standard -> gold-seal TC, sold Raised Fist -> free Popcorn rental. Skipped Small for Charm (Mega Arcana: High Priestess -> Uranus+Venus, Temperance +$6). Big 4800: Pair KK 1440 + Trips AAA 2822 + 2P QQTT 2560. Shop $21: Saturn (off-hand), reroll, swapped Popcorn -> foil Gros Michel{RENTAL}. Needle (Burglar still gave 4 hands): High AS 1650 + Two Pair 3240. Gros Michel died at round end.
Ante 4 (Holo/D6/The Club 18000, $17): EMERGENCY ratio 0.09. Buffoon pack -> Riff-raff (over perishable Supernova), reroll found nothing. Small 9000: Riff-raff gave Runner + Superposition (junk). Hands 1368, 1501 flush, 1120 trips, 1349 flush, 240, 1368 -> 6946/9000. LOST.

## Post-mortem

Binding constraint: no xMult and no real +mult by ante 4. The build was Abstract (+3/joker) + Burglar (+3 hands, 0 discards) + flat commons: every hand scored ~1100-1500 regardless of type, so six hands cap around 7-8k vs a 9000 ante-4 Small. Zero discards (Burglar) also meant I could never dig for Two Pair/Trips/flush: hands were whatever 8 random cards gave.

Decisions I would change:
1. Burglar{ETERNAL} at ante 2 for $6 (advisor +0.23): it doubled hands but removed all discards and was unsellable; at ante 4 flat-per-hand ~1300 x 6 hands could not reach 9000. It helped through ante 3 (blinds 3200/4800) but became a cap. A real +mult joker/pack would have scaled better.
2. Ante 3 shop: I left with $12 and no Buffoon pack (none offered); I rerolled once ($5) and swapped Popcorn for Gros Michel which died the same round (1/6). Spending ~$6 on an Arcana pack or keeping Popcorn to its decay was no better; the real miss was never finding an xMult in 3 shops (few Buffoon packs offered).
3. Riff-raff pick (SIM +0.06) delivered Runner and Superposition: with Abstract each adds only +3 mult. Supernova (perishable, +mult per hand type played) might have been better; Riff-raff with 3 free slots at 0 xMult is weak.

Reusable rules (if-then):
- IF you own Burglar (0 discards, 6 hands): est per hand is nearly type-independent; plan score as (avg hand) x 6, and cap check = need/6 per hand. Ante 4 Small (9000) needs ~1500 avg: not reachable with ~1300 flat hands. Buy Burglar only when you also have an xMult plan.
- IF facedown cards (The Mark) and no discards, THEN play all facedown J/Q/K together: 3 facedowns held a pair (+630).
- IF Needle is the boss and you own Burglar, THEN you still get 4 hands (Burglar adds +3 after the Needle sets hands to 1); advisor said "x 1 hand" wrongly.
- IF Coupon tag is on the Big and you are broke ($3) before the Boss, THEN skip the Big: the post-boss shop was entirely free (Jumbo Celestial, Jumbo Standard, rental Popcorn) and it saved rent.
- IF a rental flat joker is about to die (Gros Michel 1/6/round, Popcorn decay), THEN do not count it toward next-ante projections.

Advisor/CLI defects:
- BOSS PREP for The Needle said "best hand x 1 hand(s) below 3200" ignoring Burglar's +3 hands; the Needle round actually had 4 hands and cleared with 3240+1650.
- SCORE CHECK/ratio at ante 4 showed 0.09 (738) after Gros Michel died; it does not model Burglar's 6 hands, so projections (~4428 round) undersold; actual round reached 6946 (still short).
- SIM ranked Riff-raff 0.06 vs skip 0.00 and Supernova 0.00 with all p ~0: uninformative.
- Mark: `play PAIR` on facedown cards skips type check as documented; est not available (fine).
Bridge issues: none.
