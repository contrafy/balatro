# Run UGQG5ZYN (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (45456/60000)

Ante 1 (Holo/Skip/The Club 600, $4): Small: disc 4 -> Flush spades 280 + Pair AA 64. Shop $5: no joker, Buffoon $4 -> Raised Fist{PERISH} (SIM 0.86 vs Chad 0.08).
Ante 1 cont: Big 450: Pair AA + low fillers (Raised Fist on held 8) 576 one-shot. Shop $7: Blue Joker{RENTAL} $1 (+104 chips; the one rental). Club 600: Pair 88 + fillers 2508 one-shot.
Ante 2 (Charm/Investment/The Water 2000, $10): EMERGENCY 0.22 -> Jumbo Buffoon $6 -> Popcorn{PERISH}. Skipped Small (Charm: Mega Arcana -> Death 5S->AC, Devil gold KD). Big 1500: Trips 777 4865 one-shot. Shop $10: nothing. Water: High QD + fillers 3811 one-shot.
Ante 3 (Top-up/Investment/The Flint 6400, $15): EMERGENCY 0.07 -> reroll, Scholar{PERISH} $4. Skipped Small (Top-up: Egg + Golden Ticket) AND Big (Investment; keeps Raised Fist 1 round for the boss). Flint: Pair 22 3201 + Pair AA 5945. Raised Fist perished. $38 after Investment.
Ante 4 (Juggle/Rare/The Arm 18000, $38): sold Fist, reroll -> Seeing Double $6, reroll -> foil Hologram{E} $9 (sold Golden Ticket), 2 Standard packs (glass KD, purple KD; Holo x1.5), Death $3. Skipped Small (Juggle +3 hand size). Big 13500: Flush clubs 5736 + 2P TT22 5100 + FH 99955 7020. Shop $6: sold Egg $8 -> Mega Standard (wild gold-seal 9D, QC; Holo x2.0). Arm: Straight A-T 11472, disc, Straight T-6 6080, High AC = cleared 18000. Popcorn gone.
Ante 5 (Holo/Voucher/The Serpent 50000, $12): EMERGENCY 0.09; reroll -> Raised Fist{PERISH} $5 (only +mult in a mult-2 build: round 7k -> 35k). Skipped Small (rent-broke $2; Holo tag). Big 37500: Pair KK 14080 + 2P AA66 25760. Shop $4: free holo Glass Joker{RENTAL} (+10 mult, 2nd rental at ante 5), Celestial -> Uranus. Serpent: 2P 4422 19800 + Pair TT 21760 + High AC with fillers holding KS 11900 (advice est 8.3k) = 53460. Scholar perished.
Ante 6 (Double/Rare/The Pillar 120000, $-1): sold Scholar, Death, Glass Joker -> Temperance +$10 -> Buffoon (Hallucination only) + Jumbo Celestial (Mercury). Small 60000 vs ~35k round: disc 5, disc 3, 2P AA77 17304 + Pair 99 14996 + Pair 44 13156 = 45456. LOSS.

## Post-mortem

Binding constraint: no permanent +mult, ever. Every mult source was perishable or decaying (Raised Fist twice, Popcorn,
Scholar) and the only permanent scorers were Blue Joker (+chips, rental) and two xMults (Seeing Double x2 conditional,
foil Hologram x2). On a base mult of 2-3 the xMults multiplied almost nothing: without Raised Fist the median round was
~7k at ante 5 and ~7k at ante 6 (shopadvise 6850). Money was the second constraint: Blue Joker rent from ante 1 ($3 x 9
rounds) plus $0 Small Blinds kept me at $0-6 in every shop except one ($38 from the Investment tag at ante 4).

Decisions I would change:
1. Ante 4 shop ($38): I spent it on Seeing Double $6 + foil Hologram{E} $9 + 2 Standard packs + Death, with zero
   permanent +mult. Two xMults on mult 2 were worth less than one Jolly/Joker/Abstract. I should have spent the 3
   rerolls looking for a +mult joker first (the next ante's Raised Fist turned 7k into 35k, a 5x jump).
2. Ante 2: Jumbo Buffoon gave Popcorn (decaying); I passed nothing better, but the Charm Mega Arcana Devil (gold KD)
   paid ~$6 total; Strength/Death on Aces would not have changed anything. Fine.
3. Ante 6 shop: selling Glass Joker (+10 mult) for Temperance -> Buffoon/Celestial got nothing; the holo +10 was ~30%
   of my score. With ~0% either way it did not matter, but keeping scorers over pack gambles is the rule.

Reusable rules (if-then):
- IF your build's mult comes only from perishable/decaying jokers (Raised Fist, Popcorn, Scholar), THEN the next shop
  with money buys a PERMANENT +mult joker before any xMult, Hologram feed or pack: an xMult on mult 2-3 is ~x2 of nothing.
- IF Raised Fist is owned, THEN play low cards as fillers and hold only high cards (A/K/Q): holding one K turned a
  1-card High Card from 8.3k (held K 4 3) into 11.9k and Pair 22 into 3.2k; `sel` shows it, `advise` sometimes misses it.
- IF a perishable carrier has 1 round left and Small/Big tags pay (Top-up, Investment), THEN skip both so it carries
  the boss: it cleared The Flint 6400 at ante 3 and the Investment tag paid $25 (advisor suggested it correctly).
- IF Seeing Double is owned, THEN pick pairs/two pairs that include a Club (wild cards count) and never play an
  all-club Flush; the advisor ranks the club pair correctly (Pair TS TC 21760 vs ~11k off-suit).
- IF you are rent-broke at ante 5+ (rental + < $4), THEN skip the Small Blind anyway: its shop has $0 to spend
  (I skipped ante-5 Small with $2 and the Holo tag gave a free holo joker in the next shop).

Advisor/CLI defects:
- `s` at ante-5 blind select said "do not skip: the shop after the Small Blind is worth more than a tag" with $2 and
  $3 rent due (post-Small shop would have $0); the rent-broke exception should apply at ante 5+ too.
- `advise` final-hand pick at The Serpent offered no line holding KS alone for Raised Fist (High AC + fillers 4S 3D =
  11900 by `sel`); its candidates assumed every unplayed card is held.
- Ante 4 shopadvise: SIM ranked Seeing Double (+0.22 ratio) and Hologram over continuing to reroll for +mult while
  the build had no permanent mult source; it should weight "first permanent +mult" above a second xMult.
- Pack Death advice printed `pick 4 1 8` (targets AC 5S) which would turn AC into 5S; the note said to move first, but
  the ADVICE command itself was wrong-direction.
