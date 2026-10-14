# Run 6SGZCHWF (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Fish (13395/18000)

Ante 1 (Rare/Economy/The Goad 600, $4): Small: 2P TT99 116 + Flush D 280. Shop $5: Jolly{PERISH} $3. Big: Pair JJ 300 + 2P AA44 500. Shop $7: Wily{ETERNAL} $4 (SIM +0.39). Goad: 2P 350 + FH 333KK 1872 (Wily fired).
Ante 2 (Skip/Negative/The Head 2000, $9): EMERGENCY 0.24 -> Popcorn{P,R} $1 (+20 mult). Skipped Small (Skip tag $5 now). Big: Pair 77 720 + Straight A-T 1944. Shop $17: Abstract{E} $4 + Jumbo Buffoon -> Ancient{E}. Head: Pair 88 1066 + Pair 99 1148.
Ante 3 (Foil/Rare/The Mark 6400, $10): Joker{E} +4 mult $2. Small: 2P 9988 2511 + 2P 2160. Jumbo Celestial -> Uranus (2P L2). Big: 2P TT55 2572 + FH 33377 5868. Sold Jolly(perished)+Popcorn -> Ice Cream $5 (+100 chips). Mark: 2P TT22 4223 + Trips 555 5640.
Ante 4 (Charm/Holo/The Fish 18000, $6): EMERGENCY 0.24. Celestial -> Uranus (2P L3). Skipped Small (Charm = Mega Arcana: Temperance +$11, Lovers wild TH) and Big (Holo tag), $13 unspent. Fish: 2 discards chasing FH missed; 2P JJTT 4750, Trips 222 (+2 face-downs) 6225, last hand 5 face-downs 2420 -> 13395/18000.

Final build: Wily{E}, Joker{E} +4, Abstract{E}, Ancient{E}, Ice Cream{P}; Two Pair L3, no xMult that fired. $13 unspent.

## Post-mortem

Binding constraint: scaling. Five jokers, of which three eternal flat ones and Ancient (xMult that matched a suit in ~1 of 3 scoring hands) -> typical hand 4-6k vs a 18000 boss (needs 6k x3). No reliable xMult ever appeared in 6 shop views + 2 Buffoon packs (Ancient was the only one and conditional).

Decisions I would change:
1. Ante 4: I skipped Small and Big with $13 in hand and then entered the boss with no shop, so the money could not buy a single point of score. Skipping Big with $13 + a Holo tag gave nothing before the boss; either play the Big (the 13.5k was 3.3x a 4.0k hand, i.e. also unlikely) or, better, do not enter ante 4 with $2 after a Celestial pack: keep $6-8 for the Small shop. The real mistake was earlier: spending $6 on a Celestial pack at ante 3 and the ante-4 shop Celestial instead of holding for rerolls toward an xMult.
2. Accepted three eternal flat jokers by ante 3 (Wily, Joker, Abstract) + Ancient eternal: 4 of 6 slots locked with no xMult; when xMult candidates (Blackboard {E} $6 at ante 3) appeared I was $1-2 short because everything had been spent on Ice Cream/planets.
3. At The Fish I discarded two times for a FH draw (25%) instead of playing made hands in order; the discard miss cost ~one hand of value. With need = 3x typical hand the p was 0.21 either way.

Reusable rules (if-then):
- IF the build has no xMult at ante 3 and typical hand < boss/3 of next ante, THEN every dollar must be kept for the next Buffoon pack/xMult sighting (no off-hand planets, no 2nd Celestial pack); +1 Two Pair level was only +25% on a 4k hand.
- IF Ice Cream (+100 chips) is offered while chips are the weak side (base chips < 80), THEN it nearly doubles Pair/Two Pair (2.8k -> 5.4k at ante 3): buy it by selling a perished joker + a dying rental (done at ante 3).
- IF Fish makes cards face-down, THEN `sort rank` places each face-down card in rank order: a face-down card between two 2s is a 2 (it produced Trips 222 for 6225).
- IF Ancient Joker is owned, THEN the raw state has run.ancient_card.suit (it rotates every round): count which hand cards match before choosing the play; est did not model a Wild card for it (JJTT with Wild TH scored 4750 vs est 4370).
- IF skipping a blind only for a tag (Holo, Charm) while holding $13, THEN you lose the shop where that $13 could have bought score; skip only when broke (< $5).

Advisor/CLI defects:
- `shopadvise` at ante 3 Small shop recommended Jumbo Celestial ($6) at SIM +0.03 while TIGHT; all three planets were off-main-hand or +25%: low value, drained to $1 and caused -$2 at round end (Popcorn rent).
- `est` for Two Pair with a Wild card did not apply Ancient Joker (scored 4750 vs est 4370); facedown hands show no est at all and `sel` returns "None scoring None".
- The ante-4 `s` advice 'do not skip' for the Small is generic; with $2 it did not weigh that the shop was unusable.
- Advisor ranked Walkie Talkie rental $1 as BUY (SIM +0.08) in an ante-4 shop with $6 and an EMERGENCY ratio; rent -$3 per round would have made money negative.
Bridge issues: none (71 steps, no rejects); `sel` with face-down cards returns None (expected).
