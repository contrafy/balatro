# Run VTEKN3IB (port 7777) - stake 3 (Green Stake)

Ante 1: Small Blind tag=Juggle Tag (not a joker/pack tag) -> per ANTE-1 rule, play (no jokers yet, this is not Uncommon/Rare/Buffoon/Top-up/Coupon).
Small 340/300 (Two Pair KQ then Straight). Shop: bought Buffoon Pack -> Joker (+4 mult), floor joker #1.
Big 492/450 (Two Pair K9 then Pair 7). Shop: bought Buffoon Pack -> The Trio (x3 mult if Trips; also fires Full House/Quads), scorer #2.
Boss The Goad (suit debuff) 1092/600: drew Trips Aces (one debuffed spade), The Trio fired huge. Jokers 2/6, $2 leaving ante 1.

Ante 2: Small Blind skipped (Investment Tag: pays $0 at stake3 anyway, tag gives $25 after boss per shopadvise). Big 1676/1350 (Flush D then Two Pair Q7).
Shop buys: Uranus (Two Pair -> L2), Buffoon Pack -> Seltzer (retrigger all cards, 10 hands - real scorer), 2nd Buffoon Pack -> Marble Joker (adds Stone card each blind, benign forced pick over Castle/Gros Michel/Splash).
Boss The Flint (base chips/mult halved) 1813/1800: forced final hand only "Pair A" pre-check est 245 (needing 732) but a Stone-card filler (idx8) scored anyway when included in the play -> actual play est 745, exact match to score gained (745) and cleared by 13. NOTABLE: advise's pre-check candidate-hand est (245) undercounted a Stone-card filler bonus that the `play` line correctly priced; see playbook suggestion below.
$31 into ante 3 (Investment Tag payout).

Ante 3: main hand Two Pair L3 after The Fool copied last-used Uranus -> used for another level (L2->L3).
Enhancements: Magician on both Aces (Lucky Card x2), Deja Vu (Red Seal/retrigger) on a 3rd Ace, Hierophant (+30 chips Bonus) on both 7s, Temperance (one-time cash = total joker sell value, +$14).
Bought Blackboard (x3 if all held Spades/Clubs, conditional/unreliable per shopadvise but only xMult-shaped option offered) and Justice tarot ($3, banked as rescue tarot per playbook 7b).
Small 2624/2600 (Two Pair 98 w/ stone filler, Two Pair 73). Big 4752/3900 (chain of Pair 5/6 hands w/ stone filler after committing all 3 discards early -- forced-hand ests were badly low again: pre-check 180-204 vs actual plays scoring 2340-2412 per hand, same Stone-filler underestimate pattern).
Boss The Head (Hearts debuffed) 7368/5200: Flush D (est 3192, Lucky Aces noted "not counted, floor only") then Two Pair J7 w/ stone filler (pre-check est 992, actual 4176 - again the Stone-filler gap).
$22 into ante 4. Jokers: Joker(+4mult), Marble Joker, Blackboard, The Trio (Seltzer expired after 10 hands and dropped off the list). Justice tarot still banked (NOUSE).

Ante 4: Small Blind skipped (Negative Tag: next shop joker becomes free-slot Negative, per shopadvise). Shop: Uranus from Jumbo Celestial Pack (Two Pair -> L4), bought Odd Todd (+31 chips/odd card).
Big Blind (need 12000): built up through Two Pair A5 (est 2124), Full House AAA55 (The Trio fired: est 5712, actual gain 5712) = 5712/12000. Then Trips Queens with stone/bonus filler: est 2961 but actual gain only 2310 (CLI printed "(est 2961 vs actual 2310: logged for calibration)" - a ~22% OVER-estimate, the opposite direction from the earlier Stone-filler under-estimates). Total 8022/12000, 1 forced hand left, 0 discards, only a lone 9-pair in hand (no straight/flush possible). Used the banked Justice tarot on 9S (Glass x2, per playbook 4.8 "never concede with an unused consumable") but the projected gain (est 720 vs 540) was nowhere near the 3978 still needed. Forced final Pair 9 scored 1120 (scoring [3,4,8], stone filler included) -> final 9142/12000. LOSS.

# RESULT: LOSS at stake 3, ante 4, Big Blind (9142/12000)

Post-mortem: binding constraint was SCALING, not money ($12 unspent at death) or a single misplay. The build never had a reliable xMult that applied to the actual main hand (Two Pair): The Trio only fires on Trips/Full House/Quads (it happened to fire twice this run on lucky Full House/Trips draws, which is why the run got as far as ante 4), and Blackboard (x3 if ALL held cards Spades/Clubs) never fired once all game - it was bought at ante 3 as the only xMult-shaped item in that shop, but it is not a real scoring source for a mixed-suit pair build. Two Pair itself (our leveled main hand, L4 by the end) had ZERO xMult support the entire run. The one decision I would change: at the ante-3 shop with Blackboard vs nothing, either reroll harder for a real xMult/Two-Pair-fitting joker before settling, or bank the money instead of a conditional xMult that structurally cannot fire for this build - shopadvise flagged it as "conditional/unreliable" itself but had nothing better on offer that shop.

Bridge issues: none. No `ACTION FAILED` or connection errors all run; one `pick` aborted once with a clear, correct error ("The Magician targets 2 hand card(s) but 1 are highlighted") when I under-selected targets for a 2-target tarot - not a bug, just needed `sel 1 2` instead of `sel 1`.

Playbook suggestions:
1. `advise`'s pre-check candidate-hand `est` (shown before you pick a play) repeatedly undercounted Stone-card fillers by 2-4x when the actual `play` command recalculated with the filler included (e.g. "Pair A est 245" precheck vs "play ... est 745" actual at ante 2 Flint boss; several more at ante 3). The precheck should price a Stone-card filler the same way `play` does, so DISCARD-vs-PLAY decisions near the need threshold aren't made on a falsely pessimistic number.
2. Conversely, a Trips/Full House `est` can OVER-count by ~20%+ relative to actual (2961 est vs 2310 actual scoring Queens Trips at ante 4) - worth a `logged for calibration` audit of what inflates that estimate (possibly Lucky Card 1-in-5 procs being counted asymmetrically, or The Trio's x3 mult ordering versus flat jokers).
3. This is the second stake-3 run (after 7777_8S1B92B4, also a zero-xMult ante-4 loss under similar conditions) to reach ante 4 with a leveled main hand but no xMult that actually applies to it. Consider having `shopadvise` explicitly flag "0 of your N xMult-labeled jokers can fire on your current main hand" as a distinct, louder warning from ante 3 on, separate from the general "under-scaled" note - Trips/FullHouse-gated xMult on a Two-Pair build is a trap that looks like progress (2 xMult jokers owned) but scores like zero.
