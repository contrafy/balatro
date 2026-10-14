# Run 2JAKDJCQ (port 7809, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 4 blind The Mark (5271/18000)

Ante 1 (Charm/Charm/The Pillar 600, $4): Small 2P JJ55 + 2P AAKK + 2P 9933 (300). Shop $4: Smiley Face. Big: 2P JJ22 528 one-shot. Shop $6: Misprint. Pillar: 2P 8866 144 (Misprint roll 1), disc, FH QQQTT 1980.
Ante 2 (Orbital/Meteor/The Water 2000, $8): Scary Face{PERISH,RENTAL} $1 (only rental), Buffoon -> Wily{E} (Greedy/Wily). Small FH+2P KK22, Big discard-dig Flush 2250, Water 2P QQ33 3180.
Ante 3 (Top-up/Orbital/The Mouth 6400, $8): sold Scary rental -> Throwback{E,R} $1 (xMult exception). Skipped Small for Top-up (8 Ball + Crazy Joker). Big: disc -> FH 55577 5281 one-shot. Shop: Celestial -> Earth, Spectral -> Immolate (+$20), reroll x2 -> Blue Joker (sold Crazy). Mouth: locked Pair TT 2940, KK 2750, QQ ~2500 = cleared.
Ante 4 (Buffoon/Buffoon/The Mark 18000, $13): Arcana -> Temperance (+$11), 2 rerolls -> Photograph $5 (sold 8 Ball). Skipped Small AND Big for two free Mega Buffoon packs (Throwback x1.75): pack 1 had Pareidolia{E}: sold Misprint, took it. Pack 2 nothing. Mark: with Pareidolia EVERY card is a face, so all 8 cards were drawn face-down; blind plays High Card 1953, Pair 1764, last hand (rank-sorted block) 1554 -> 5271/18000. LOSS.

## Post-mortem

Binding constraint: I deliberately took Pareidolia (eternal, cannot be sold) with The Mark as the VERY NEXT boss. The Mark flips every face card face-down, and Pareidolia makes every card a face, so the whole hand is hidden and the engine (Pair/FH hunting, discards, Blue/Smiley/Photograph) became a coin flip. Without Pareidolia the same round estimated ~17.7k vs 18000 with visible cards; with it I averaged ~1.7k per blind 5-card play (Pareidolia mult was never realised because the types were High Card / Pair).

Decisions I would change:
1. Pareidolia before The Mark. I computed "x2 on non-face hands" but dismissed the Mark/Plant interaction as acceptable risk. IF the boss of this ante is The Mark (or The Plant/Pillar-like face bosses) THEN never add Pareidolia this ante; wait for the post-boss shop.
2. Skipping both Small and Big at ante 4 left me with $8 and no shop before the boss; I accepted packs that could not fix the visible Mark problem. A Big-blind shop (+$4, one more shop) might have found Luchador/other help. Skipping was fine for Throwback but the boss prep was nil.
3. Selling Misprint (+11.5 avg mult) for Pareidolia reduced the chance that the plain hand clears.
4. Blue Joker deck-size dynamics: Blue counts the DRAW PILE, it falls ~2 chips per card drawn each hand (est 2034 at 39 cards, 1815 at 34).

Reusable rules (if-then):
- IF you own or are about to take Pareidolia AND the ante boss is The Mark, THEN do not take it (every card is face-down, hand type unknowable); IF The Plant is possible later, Pareidolia debuffs EVERY card (eternal, unsellable).
- IF The Mark with unavoidable blind hands: `sort rank` puts equal ranks adjacent (descending), the played five reveal their ranks via `raw` deck.remaining_by_rank diff; unplayed cards are the lowest of the sorted hand. A contiguous block catches pairs ~1.6x more often than a random subset, but a blind round only averages ~High Card/Pair, so you need ~2x the usual margin.
- IF Top-up/Buffoon tags are offered and slots are free, skipping Small was right (Top-up gave 2 jokers instantly; Buffoon tags opened packs immediately at the skip).
- IF a Throwback{ETERNAL,RENTAL} is offered at ante 3 with only a chips-only rental owned, THEN selling the old rental and buying it is allowed; with skips planned the rent is paid only on rounds actually played.
- IF Immolate is offered in a Spectral pack at ante 3+ with <$10, THEN +$20 funded two rerolls that found Blue Joker (+2 chips per deck card, ~+80 chips at ante 3 = big on 25-chip hands).
- Misprint est uses mean 11.5 but results vary 2x; Mouth/Pair lock: High Card is a repeatable lock only if single faces are ~40% of need.

Advisor/CLI defects:
- Pack advice listed Pareidolia +115% round est with 'ETERNAL: fine, a core joker' and did not warn that The Mark (known boss of this ante) makes all cards face-down with Pareidolia; the only text was the generic SIM -0.02. It should flag Pareidolia vs The Mark/The Plant as AVOID.
- `advise` under The Mark with all cards face-down suggests 'play 1 2 3 4: 4 face-downs contain at least a pair' which is false with Pareidolia (all cards face-down, ranks unrestricted).
- shopadvise EMERGENCY text at ante 3 rated The Mouth ratio 0.19 although Pair-lock rounds scored ~8k; the 'under its rule' estimate for Mouth was too pessimistic.
- SELL then BUY rental swap SIM said -0.14 for Throwback although the skip plan nets positive; the SIM does not model Throwback skips.
