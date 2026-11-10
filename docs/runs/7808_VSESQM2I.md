# Run VSESQM2I (port 7808, claude-sonnet-5-5) - Black Deck Gold Stake - WIN (beat ante 8 boss Crimson Heart 576257/400000)

Ante 1 (Foil/Skip/The Head 600, $4): Small: 2P+High dig+Flush 328. Shop $4: Buffoon -> Abstract{E}. Big: Trips 270 + 2P 300. Shop $5: Hanging Chad{E} $4 (needed scorer). Head: High Q 245 + 2P 432 (Chad first card).
Ante 2 (Juggle/Buffoon/The Water 2000): Pluto + Celestial -> Uranus. Small: 2P 720 + Pair AA 432. SKIPPED Big for Buffoon Tag (Mega): Scholar + Swashbuckler. Water: High Card AD alone 3456 (Chad x3 -> Scholar x3).
Ante 3 (Ethereal/Polychrome/The Mark 6400): sold Swashbuckler -> Blueprint $10 left of Scholar (copies Scholar). Skipped Small (Ethereal) -> Cryptid on AS (+2 Aces). Big: High AC 6384. Mark: Pair AA 9844.
Ante 4 (Buffoon/Uncommon/The Arm 18000, $14): skipped Small for Mega Buffoon -> Bloodstone + Zany. Big 13500: Flush 2322 + 2P AAQQ. Shop $21: The Sun (hold, Aces->Hearts for Bloodstone), Grabber.
NOTABLE: ante 4 - The Sun turned QC TC AD into hearts for a heart Straight Flush AH-KH-QH-JH-TH under The Arm: est 14650 but Bloodstone's seven 50% x1.5 rolls (Chad x3 on the Ace) made 64606 vs 18000 needed.
Ante 5 (Garbage/Top-up/The Wall 100000, $9): Mega Arcana -> Fool(Sun) + Lovers (wild AS). Small: Sun on KD JD 9S, heart Flush AS-first 21451 + High A. Shop: sold Zany -> Ramen x2 (perishable), Mega Arcana -> Fool(Sun) + Death (AH copy). Big: Trips AAA 32930 + 2P. Reordered Blueprint right of Bloodstone, left of Ramen (copies Ramen x2). Shop: Fool -> Death. Wall: Sun, heart Flush 54108, Death 9C->7H, Flush House 90002 => cleared 144k.
Ante 6 (Charm/Charm/The Eye 120000, $10): sold Scholar -> Fibonacci{R} $1 (+8 mult per A/2/3/5/8), Celestial -> Earth. SKIPPED Small AND Big for 2 Charm Tags (Mega Arcana): Fool(Earth), Temperance +$16, High Priestess(Ceres Flush House L2 + Venus), Emperor -> Hermit +$20 + Sun ($43). Eye: Sun on 3 cards, heart Flush 79480, disc, Full House AH-first 54181 => 133k/120k.
Ante 7 (D6/Rare/The Club 220000, $52): sold Ramen -> Photograph{E} $5 with Blueprint directly left (x2 per Chad retrigger, x4/trigger with the copy), Hanged Man, Standard -> 7H bonus; 2 rerolls: sold Fibonacci -> Throwback $6 (perishable). SKIPPED Small+Big (Throwback x2.75). Club: QH-first Full House 456885 vs 220000 in ONE hand (est 206965).
NOTABLE: ante 7 - Photograph{E} bought for $5 with Blueprint directly left of it and Hanging Chad retriggering the first card turned a Full House with est 206965 into 456885 against The Club's 220000 in a single hand.
Ante 8 (Orbital/Ethereal/Crimson Heart 400000, $23): Jumbo Buffoon x2 skipped (junk), free rerolls (nothing). SKIPPED Small (Orbital: Two Pair L5) and Big (Ethereal -> Grim) -> Throwback x3.25. Crimson Heart: Throwback disabled -> 5-card dig, Two Pair QH-first 212868; Bloodstone off -> Straight JH-first 83707 (296575); Photograph off -> hand 3 as a 1690 reroll of the disabled joker (new pick Abstract, the weakest); last hand heart Flush KH-first (est 82368) 277992 => 576257/400000. WIN.
NOTABLE: ante 8 - Crimson Heart disabled Photograph with 103k still needed and 2 hands left; a throwaway Pair rerolled it onto Abstract (the weakest joker) and a KH-first heart Flush made 278k from est 82k.

## Post-mortem

Binding constraint: none ever bound hard; the closest points were ante 1-2 (0-1 scorers, $0-4) and Crimson Heart (Photograph disabled with 103k needed).
Build: Hanging Chad{E} (retrigger first scored card x3) as the hub. Early: Abstract{E} + Scholar + Blueprint copy (single Ace = 3-6k at ante 2-3). Mid: Bloodstone + The Sun/Death/Lovers turning the deck into hearts (heart Flush/Flush House/Straight Flush 54-90k at antes 4-6, 2-4x the advisor est). Late: Photograph{E} with Blueprint directly left (x4 per trigger, x64 on base mult via Chad) and Throwback x3.25 after 9 skipped blinds (A2 Big, A3 Small, A4 Small, A6 Small+Big, A7 Small+Big, A8 Small+Big). From ante 6 I fought only bosses; one good hand cleared ante 7 (456k vs 220k).

Decisions I would change:
1. Ante 5 Fool picks: used Fool right after a planet/other consumable and got Earth instead of Death/Sun once (Fool copies the LAST used consumable, planets included).
2. Ante 4 Straight Flush play was luck-assisted; I should have kept the 4th hand in reserve less aggressively... fine, but note est was 4x low.
3. Kept Scholar until ante 6; Fibonacci/Photograph would have paid earlier once Aces were rare.

Reusable rules (if-then):
- IF you own Hanging Chad, THEN every per-card joker (Scholar, Fibonacci, Photograph, Bloodstone) fires 3x on the FIRST scored card: `move hand` the best card there (Ace for Scholar, heart face for Photograph+Bloodstone) before every play, and re-sel.
- IF you own Bloodstone, THEN The Sun (and Lovers wild, Death copies of hearts) converts the deck to Hearts and a 5-heart Flush gets 4-7 independent 50% x1.5 rolls: actual scores were 2-4.4x `est` (14650 -> 64606, 23168 -> 90002, 22400 -> 79480, 82368 -> 277992). `est` never counts those rolls, so a Flush est of 1/3 of the need is enough.
- IF Photograph{E} is in the shop (any ante), THEN buy it and put Blueprint directly LEFT of it: x2 per trigger doubles again with the copy; with Chad on a face first card that is x64 on base mult (Full House est 206965 -> 456885).
- IF The Fool is picked, THEN it copies the LAST used consumable including planets: use the tarot you want copied immediately before.
- IF Crimson Heart disables a joker your hand does not need (Throwback/Abstract/Bloodstone), THEN play the big hand NOW and use discards freely (they do not reroll); IF it disables the key joker (Photograph) with 2 hands left, THEN play a cheap 5-card hand to reroll (the new pick never repeats and can hit a weaker joker) and keep the discard for the last hand.
- IF both Small and Big carry useful tags (Charm, Buffoon, Ethereal) and your single best hand beats the boss/2, THEN skip both and keep Throwback/perishables alive: two Charm tags gave Hermit +$20, Temperance +$16, Sun, Ceres.
- IF a Buffoon/Mega pack has a clean scorer, THEN each extra joker also adds +3 mult with Abstract; sellable early flat jokers (Swashbuckler, Zany, Scholar) are the funding for Blueprint/Ramen/Throwback.
- IF a Straight/Flush hand under The Eye/other restrictions is needed, THEN The Eye only blocks repeats of the same TYPE: Flush -> Full House -> Two Pair worked for 133k.

Advisor/CLI defects (with examples):
- `est`/SIM ignores Bloodstone rolls ("50% x1.5 not counted"): at ante 6 SIM proposed selling Bloodstone for Fibonacci/Blueprint although the real scores were 2-4x est.
- ORDER FIRST repeatedly proposed Blueprint left of Abstract/Chad (copy +mult), lowering Ace-hand est; right once Ramen/Photograph is the copy target (est 16464 -> 32928 at ante 5).
- Crimson Heart advice (`PLAY HIGH` throwaway) ignored that a harmless disabled joker (Throwback/Abstract) is a reason to play the big hand now and dig with discards.
- `use N targets` prints no preview of the converted hand; advise after a Sun use sometimes lagged one state.
- Fool advice (not shown by CLI) does not tell what it will copy; picking it after a planet copies the planet.
- shopadvise took 60-90s at ante 6+ (auto-backgrounded).
