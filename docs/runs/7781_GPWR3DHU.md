# Run GPWR3DHU (port 7781)

Stake 1 (White), Black Deck.

Ante 1 boss: The Head. Small tag: Foil Tag. Big tag: Coupon Tag.

Ante 1: Small: PAIR->FULLHOUSE TTTJJ est 360/need 300, won. Big: STRAIGHT 7-high est 660/need 450, won.
Shop1: bought Buffoon Pack ($4), picked Even Steven (+4 mult/even card) over Fortune Teller. Skipped Droll Joker
(single-hand-type flush joker, excluded by playbook priority list) despite shopadvise ADVICE to buy it.
Shop2: shopadvise suggested reroll ($12->$7 after); overrode per playbook rule "no reroll unless >=$10 left after
reroll in ante1-2" - ended shop keeping $12, no scoring joker/pair item available anyway.
Boss The Head (hearts debuffed): discarded debuffed JH+extras, played FLUSH(spades) est 576/need 600 (short by
pacing per advise), then PAIR 3s est 26 to finish, scored 602/600 (within est). Ante 1 cleared, no losses, $12->$20.

Ante 2: Small: PAIR->STRAIGHT(A-high) chain, scored 828/800, won. Big: STRAIGHT(royal A-K) 648 then
FULLHOUSE 77755 604 = 1252/1200, won. Boss The Mark (faces facedown): discarded 3 facedowns+extras first
(per playbook rule), then TWOPAIR TT66 est 2888/need 1600 (huge overkill thanks to Clever Joker+Even Steven), won.
Jokers acquired: Even Steven (+4mult/even, from Buffoon pack), Clever Joker (+80 chips if Two Pair, bought $4).
Overrode shopadvise 3x for reroll-below-$10 rule in ante1-2 (playbook explicit threshold vs advisor's looser one);
overrode shopadvise once to buy Clever Joker directly instead of rerolling (advisor didn't recognize it as a
priority ordinary-hand joker since "main hand" tracker still said Straight). Picked Uranus (Two Pair planet) from a
Celestial pack, deliberately pivoting main hand to Two Pair (fits Clever Joker) -> Two Pair now L2(40x3).
$9 -> $17 after ante 2 boss. No misplays, no near-misses.

Ante 3: Small: PAIR->PAIR8->FULLHOUSE TTTAA 3906/2000, won. Big: TWOPAIR JJ88 2520 + STRAIGHT(A-high, hearts hit
Bloodstone) 1116 = 3822/3000 (Bloodstone x1.5 fired twice, above est), won. Boss The Wheel (facedown cards):
discarded facedowns each round per advice, played FULLHOUSE 99977 2040 then FULLHOUSE 88866 5970 = 11045/4000
(massive overkill, extra facedown/discard cycles revealed 2 natural full houses), won.
Jokers: bought plain Joker (+4 mult, $2, cheap universal priority buy) and Bloodstone (xMult, 1/2 chance x1.5 per
Heart in scoring hand, $7, taken as ante-3 placeholder xMult per playbook despite Hearts not being our focus suit -
it hit twice in the ante 3 big blind). Picked Castle Joker (+3 chips/discarded-suit card) over Ice Cream (avoid-list
decaying joker) from a Buffoon pack. Leveled Two Pair->L2 and Full House->L2 (both benefit from Clever Joker: full
house plays confirmed the +80 chips DOES fire, i.e. Full House counts as containing Two Pair in this engine).
Used Chariot tarot (Steel x1.5-while-held) on a spare 9S rather than a core pair card, per playbook guidance to
put Steel on held/filler cards, not scored-every-hand cards. Skipped Judgement/Strength/Moon/Tower in that pack.
Declined Obelisk (shopadvise flagged AVOID: penalizes main hand). $1->$0 twice (spent to zero both shops per
"under-scaled for ante 3" advisor note); ended ante 3 boss with $0, cashed to $6 entering ante 4.
No misplays. Bloodstone's 50% proc is "not counted" in est by design (est notes this), and both actual scores this
ante beat est by 10-90% when Bloodstone or extra facedown-driven windfalls hit — the only >20% est deviations so far.

Ante 4: Small: TWOPAIR AT 6039/5000 (Bloodstone hit), won. Big: FLUSH(hearts, 5 cards) 3925 est1600 (+145%,
Bloodstone hit multiple scoring cards) + TWOPAIR 92 + TWOPAIR A7 = 7609/7500 (won right at the wire). Boss The Eye
(no repeat hand types): played PAIR KK(356) -> TWOPAIR 96(2920) -> FULLHOUSE 888JJ(6362 est/7953 actual, +25%) =
11910/10000, won. All three hands used distinct types per boss rule, advise correctly tracked "types already used"
and excluded them from later candidates.
Jokers: filled last (6th) slot with Judgement tarot -> random Joker = Raised Fist (+2x lowest held card rank mult,
weak/situational); sold it later same shop to fund Constellation (xMult, grows +0.1 per planet used, bought $6)
after selling — overrode shopadvise's suggestion to sell Clever Joker instead (Clever is one of our two reliable
ordinary-hand jokers, firing on both Two Pair and Full House; Raised Fist was strictly weaker/unproven).
Leveled Full House -> L3(90x8) via Celestial pack, which also fed Constellation to x1.1.
Money: $0->$6 shop1(bought Arcana pack->Judgement), $0 after selling Raised Fist+buying Constellation left $1,
ended ante 4 with $6 -> $1 after ante4's Celestial pack purchase, banked to $6 entering ante 5.
Est deviation >20%: FLUSH big-blind hand 1600 est vs 3925 actual (+145%, 5/5 scoring cards were Hearts, Bloodstone
fired on all); FULLHOUSE Eye-boss final hand 6362 est vs 7953 actual (+25%). Both attributable to Bloodstone's
50%-chance x1.5/Heart not being counted in est (documented behavior, not a bug).

Ante 5: Small Blind (need 11000). FULLHOUSE AAAKK 3418 -> STRAIGHT(8-high) 2112 (still 5470 short, 1 hand left,
0 discards) -> forced HIGH CARD (AH only) est 286, no consumables held (rescue tarot slot was empty all game -
every Arcana pick this run was consumed immediately on hand cards, never held in reserve), scored total
5816/11000. LOST. Run ends here: stake 1, ante 5, Small Blind.

Final jokers: Even Steven (+4mult/even), Clever Joker (+80chips if TwoPair), plain Joker (+4mult), Castle
(+3chips/discarded-suit, accumulated to +36), Bloodstone (1/2 chance x1.5/Heart), Constellation (xMult x1.1,
grown from 2 planet buys). Levels: Full House L3(90x8), Two Pair L2(40x3). Money never exceeded $20; spent to $0
or near-$0 at the end of nearly every shop chasing jokers/packs (ante1 $20 high point, ante3-4 repeatedly $0-$1).

Post-mortem: binding constraint was MISPLAY, not money/scaling/boss/luck. The ante 5 Small Blind hand sequence
used all 3 discards chasing progressively bigger made hands (Full House -> Straight) without ever keeping a
guaranteed pair-family fallback for the final forced hand, directly violating playbook section 4: "On the
second-to-last discard of a round, keep cards that guarantee a made pair-family hand on the final draw rather
than chasing a bigger one." After the Full House cleared 3418 (need 11000), the second hand's discard (down to 0
discards) was spent chasing a flush/straight instead of preserving pair-forming cards; the resulting 8-card hand
had zero pairs and no flush/straight, leaving only a High Card (est 286) against a remaining need of 5470 -
mathematically unwinnable regardless of any single hand. Compounding this: this run never held a rescue tarot
(Death/Strength/Justice) in a consumable slot at any point - both Arcana pack picks were spent immediately on
hand-card enhancement (Chariot->Steel) or joker generation (Judgement), never banked as insurance. Either fix
(preserve a guaranteed pair on the last discard, or hold one rescue tarot) would very likely have saved this hand.

The one decision I would change: on the ante-5 Small Blind's 3rd hand (2 discards used, 1 left, held
A-Q-T-8-7-6-4-3 no pairs), discard toward a guaranteed pair/trips rather than the straight/flush EV the advisor
computed - `advise` itself flagged this as "still short" both times it recommended playing, but did not surface
that the FOLLOWING forced hand would have zero legal path above High Card; a future advise version could warn
explicitly when a suggested play leaves the *next* hand with no pair in the remaining cards and 0 discards.

Bridge issues: none. Every command behaved as documented; no ACTION FAILED retries were needed this run.

Playbook suggestions:
1. Add to section 4 (Last Hand Check): before spending the SECOND-TO-LAST discard of a round on a straight/flush
   chase, verify that the remaining hand cards (post-discard) still contain at least one pair as a floor - if not,
   the chase risks a hard unwinnable final hand even though each individual discard/play decision looked locally
   correct (positive EV vs need at the time).
2. Extend the RESCUE TAROT rule beyond bosses: hold one card-targeting tarot (Death/Strength/Justice) heading into
   ANY blind from ante 3+ where discards are being spent aggressively on flush/straight chases, not just bosses -
   this run's loss was on a Small Blind, not a boss.
3. `advise`'s "DISCARD: drawing to a flush/straight (EV X)" recommendation should flag when doing so would leave
   zero pairs among the kept+likely-drawn cards AND this is the last or second-to-last discard of the round -
   i.e. surface the downstream risk, not just the current-decision EV.
