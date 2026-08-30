# Run VVEMMSAY (port 7782) - LOSS at ante 4 Big Blind (need 7500, scored 5948)

Prior runs on this port (VYP8RXFJ, CIFLYYWN) were lost to instance restarts unrelated to play
quality (see their log files). This is a fresh run starting from ante 1, stake 1, Black Deck.
Bridge update note: jokers/decks previously locked are now unlocked per orchestrator.

Ante 1 Small Blind (need 300): Trips J est 180 actual 180 (cum), TwoPair QT est 120 actual 120
(cum 300, cleared exactly). Cashed out -> $8.
Shop: opened Buffoon Pack -> picked Ancient Joker (x1.5 per card of rotating suit, xMult scaler)
over Troubadour (+2 hand size/-1 hand). Bought Walkie Talkie (+10 chips +4 mult per 10/4 card) $4
-> $0. Reordered jokers so Walkie Talkie (flat) is LEFT of Ancient Joker (xMult): order 2 1.
Jokers: [Walkie Talkie, Ancient Joker]. $0. Boss ante1: The Psychic (exactly 5 cards).

Ante 1 Big Blind (need 450): Pair9->Flush Hearts est 528 actual 528 (Ancient Joker's rotating
suit was not Hearts this hand, contributed x1.0 -- est/actual matched). Cleared, cashed out -> $6.
Shop: Campfire $9 (xMult) too expensive at $6; bought Strength tarot $3 per shopadvise -> $3, LEAVE.
Jokers: [Walkie Talkie, Ancient Joker]. $3.

Ante 1 Boss (The Psychic, need 600, exactly 5 cards/hand): Full House TTT77 est 1824 actual
2736 (est was WRONG by ~50%, "Ancient Joker not modeled" -- rotating suit matched several
scoring cards this hand, big xMult boost the advisor doesn't compute). DISCREPANCY LOGGED:
hand=FullHouse TTT77, jokers=[Walkie Talkie, Ancient Joker], est=1824, actual=2736 (+50%).
Cleared in 1 hand. Cashed out -> $10.
ANTE 1 COMPLETE. Jokers: [Walkie Talkie, Ancient Joker]. Upcoming boss ante 2: The Club.

Ante 2 shop: bought Celestial Pack -> Uranus (Two Pair L2). Bought Buffoon Pack -> picked Mad
Joker (+10 mult if Two Pair) over Faceless Joker. Reordered: Walkie Talkie, Mad Joker (both flat)
LEFT of Ancient Joker (xMult) -> order 1 3 2. $2, shopadvise LEAVE.
Jokers: [Walkie Talkie, Mad Joker, Ancient Joker]. Levels: Two Pair L2. $2.

Ante 2 Small Blind (need 800): Trips3->4H draw->6H Flush est 1128 actual 1128 (Ancient Joker
x1.0 this hand). Cleared, cashed out -> $7.
Shop: bought Jumbo Celestial Pack -> Jupiter (Flush now L2, 50x6). $1 left, LEAVE.
Jokers: [Walkie Talkie, Mad Joker, Ancient Joker]. Levels: Flush L2, Two Pair L2. $1.

Ante 2 Big Blind (need 1200): Two Pair chain -> Full House 666AA est 1120 actual 1280 (cleared).
Cashed out -> $7.
Shop: bought Loyalty Card (x4 every 6 hands, xMult) $5 -> $2. Joker order already flats-then-xMult
(Walkie Talkie, Mad Joker, Ancient Joker, Loyalty Card) so no reorder needed. shopadvise LEAVE.
Jokers: [Walkie Talkie, Mad Joker, Ancient Joker, Loyalty Card] (4/6). $2.

Ante 2 Boss (The Club, need 1600, some Clubs debuffed): TwoPair42 est 1512 actual 1512 (Ancient
Joker x1.0 this hand); High Card with Ace-partner debuffed: advisor's `hands`/`advise` picks the
raw-highest-rank card even if debuffed (AC(DEBUFF) is Ace, but scoring it would give 0) -- overrode
to score KS instead (idx 2 3 4 5 6, excluding the debuffed Ace): actual 15 vs advisor's own est 5
for its (bad) AC pick -- so overriding was correct; separately the CLI's own est-vs-actual for MY
chosen play was est 39 vs actual 15 (~62% off, because my filler set still included a different
debuffed card, TC, whose debuff the estimator undercounts) -- BUG NOTED for playbook. Then
TwoPair AQ (one Ace debuffed) est 923 actual 2450 combined for round -- final actual 2450 vs need
1600, cleared comfortably despite the debuff. Cashed out -> $7.
BUG: `hands`/`advise` HIGH CARD picker (cli.py ~line 522) chooses max chip-value card without
checking DEBUFF status -- can recommend a card that scores 0. Always sanity-check HIGH CARD
picks against the DEBUFF tags before following advice.
ANTE 2 COMPLETE. Jokers: [Walkie Talkie, Mad Joker, Ancient Joker, Loyalty Card] (4/6).
Levels: Flush L2, Two Pair L2. Upcoming boss ante 3: The Mark (faces face-down).

Ante 3 Small Blind (need 2000): Trips5->FullHouse 55544 est 1826 actual 2573 (+41%, Ancient
Joker rotating suit matched this hand). DISCREPANCY LOGGED: hand=FullHouse 55544,
jokers=[Walkie Talkie, Mad Joker, Ancient Joker, Loyalty Card], est=1826, actual=2573 (+41%).
Cleared in 1 hand. Cashed out -> $13.

Ante 3 Big Blind (need 3000): Chased Flush over guaranteed Full House 888AA (est 1204) per advise
-- correct call, got 6-club Flush est 1512 actual 1512 (cum 1512). Then forced Pair T (no
discards, no better hand) est 500 actual 2000 (cum 3512, cleared before last hand needed!).
HUGE DISCREPANCY LOGGED: hand=Pair T (fillers), jokers=[Walkie Talkie, Mad Joker, Ancient Joker,
Loyalty Card], est=500, actual=2000 (+300%) -- Ancient Joker's rotating suit + Loyalty Card's
periodic x4 (both "not modeled"/uncounted by advisor) can combine for huge swings on ANY hand,
not just big ones. Cashed out -> $20.

Ante 3 shop: bought Scholar (+20 chips +4 mult per Ace) $4, then Jolly Joker (+8 mult if Pair) $3
-> $13, all 6 joker slots filled. Reordered flats-then-xMult: Walkie Talkie, Mad Joker, Scholar,
Jolly Joker, Ancient Joker, Loyalty Card (order 1 2 3 6 4 5). shopadvise LEAVE.
Jokers (6/6): [Walkie Talkie, Mad Joker, Scholar, Jolly Joker, Ancient Joker, Loyalty Card].
Levels: Flush L2, Two Pair L2. $13.

Ante 3 Boss (The Mark, need 4000, faces face-down): Advisor's `hands`/`advise` does NOT know
the boss rule "4+ face-down cards from J/Q/K guarantee a pair (or better)" and kept suggesting
discarding all face-downs as junk -- OVERRODE this each time and kept accumulating face-downs
via discarding only the visible junk cards (reached 5 face-downs, guaranteeing >= Three of a
Kind by pigeonhole since only J/Q/K exist and 5 cards can't avoid a repeat among 3 ranks without
one rank appearing 3x). `play TYPE` skips its own type-check when face-down cards are selected
(confirmed message: "Preview hidden (face-down cards selected): type check skipped, playing as
requested") -- the underlying game still scores the true hand. Results:
  Hand1: TRIPS on 5 facedowns (idx1,2,3,5,8), est 330 actual 1800 (+445%!)
  Hand2: forced PAIR 2s (no discards left), est 140 actual 154 (close)
  Hand3 (last hand): TRIPS Aces (3 in hand) + included the 2 remaining facedowns as fillers
    instead of advisor's visible-card fillers, hoping for a facedown pair -> Full House upgrade:
    est 2829 actual 6426 (+127%) -- cumulative round total 8380 vs need 4000, huge clear.
DISCREPANCIES LOGGED (all "Ancient Joker suit unknown"/"Loyalty Card" uncounted by advisor):
  hand=Trips(facedowns), jokers=[all 6], est=330, actual=1800 (+445%)
  hand=Trips Aces+facedowns, jokers=[all 6], est=2829, actual=6426 (+127%)
Cashed out -> $20.
BUG/PLAYBOOK GAP: `advise`/`hands` has zero awareness of The Mark's face-down-guarantees-pair
rule; always override its discard suggestions when facing 4+ face-down cards on this boss --
keep the face-downs, discard only visible junk, and prefer including remaining face-down cards
as "fillers" over known junk cards since they can only help (chance of upgrading to Full House).
ANTE 3 COMPLETE. Jokers (6/6): [Walkie Talkie, Mad Joker, Scholar, Jolly Joker, Ancient Joker,
Loyalty Card]. Levels: Flush L2, Two Pair L2. $20 (recovering interest well).
Upcoming boss ante 4: The Water (no discards).

Ante 4 shop: bought Telescope voucher $10 (celestial packs show most-played hand) -> $10 (at
interest floor). shopadvise LEAVE. Jokers unchanged (6/6, full). $10.

Ante 4 Small Blind (need 5000): SKIPPED to claim Negative Tag (playbook section 5/8 explicitly
lists Negative as a "take" tag; joker slots were full at 6/6 but Negative-edition jokers do not
consume a slot in Balatro, so slot-fullness was not a blocker). Forfeited Small Blind's chip
income and round; tag never got claimed since the run ended at the very next blind before
reaching another shop -- net negative in hindsight (see post-mortem).

Ante 4 Big Blind (need 7500): Straight J-7 est 672 -> discarded only true junk (not the straight,
overriding advisor's "keep 3 highest, discard everything else" default which would have broken
the made straight) -> upgraded hand to 5 spades + Two Pair T7. advisor again suggested a discard
that would have destroyed the Two Pair T7/flush structure it had just identified as best (a third
instance of the "lists best hand but then discards its cards" bug) -- overrode with a
minimal single-card discard (just the dead Ace) preserving both Two Pair and Flush candidates.
  Hand1: TwoPair T7, est 2726 actual 2726 (cum 2726)
  Hand2: Flush S, est 486 actual 486 (cum 3212)
  Hand3 (last hand, 0 discards, forced): Pair 4 (only made hand available), est 2736 actual 2736
    (cum 5948) -- Ancient Joker/Loyalty Card did NOT swing this one despite "Loyalty Card x4 in
    1 hands" hint before hand 2 (the proc apparently needed one more hand than the counter implied,
    or simply didn't match to a scoring card this hand).
FINAL: scored 5948 vs need 7500 (short by 1552). GAME_OVER. RUN LOST at ante 4 Big Blind.

=== POST-MORTEM ===
Result: LOSS, ante 4 Big Blind, need 7500, scored 5948 (short by 1552, ~79% of target).
Jokers at death (6/6): Walkie Talkie (+10 chips +4 mult per 10/4 card), Mad Joker (+10 mult if
Two Pair), Scholar (+20 chips +4 mult per Ace), Jolly Joker (+8 mult if Pair), Ancient Joker
(x1.5 per card of a rotating suit), Loyalty Card (x4 every 6 hands). Levels: Flush L2 (50x6),
Two Pair L2 (40x3). Money curve: $4 (ante1 start) -> $0 -> $8 -> $6 -> $3 -> $10(a2 start) -> $2
-> $7 -> $1 -> $7 -> $2 -> $13(a3 start) -> $13 -> $20 -> $13 -> $20(a3 end) -> $10(a4, after
Telescope voucher) -> $10 (unspent at death).

Binding constraint: SCALING, not money or a single misplay. By ante 4 our only xMult sources
were Ancient Joker (conditional on a rotating suit matching scoring cards -- roughly 1-in-4
useless per hand) and Loyalty Card (fires once every 6 hands only). Neither is a reliable
per-hand multiplier; most of our huge scores in antes 1-3 came from LUCK (the rotating suit
happening to match) rather than a guaranteed engine, so when ante 4's Big Blind needed a truly
big number on a hand where neither proc'd, we fell short with an otherwise-decent Two
Pair/Flush/Pair mixed round. We also had 5 flat/conditional jokers (Walkie Talkie, Mad Joker,
Scholar, Jolly Joker) that each add only situational chips/mult and no true reliable xMult.

Decision I would change: skipping the Ante 4 Small Blind for the Negative Tag. It forfeited a
full round of chip-clearing practice/income AND we never even reached a shop to claim the
tag's joker before the run ended -- pure downside in this run. Given joker slots were already
full (6/6) and our scaling was already shaky, the better play would have been to PLAY the Small
Blind (banking money/hand reps) and let Investment/other economy tags carry ante 5+ instead.
More importantly, by ante 3 we should have been selling a flat/situational joker (e.g. Walkie
Talkie or Scholar, both narrow-condition) for a second unconditional xMult source (Campfire,
which we saw for $9 in ante 1 shop and passed on for money reasons) rather than filling all 6
slots with only 2 xMult-capable jokers, one of which (Ancient Joker) is probabilistic per hand.

Cases where est differed from actual by more than 20% (for playbook calibration):
  1. Ante1 Boss: FullHouse TTT77, jokers=[Walkie Talkie, Ancient Joker], est=1824, actual=2736 (+50%)
  2. Ante3 Small: FullHouse 55544, jokers=[WT,Mad,Ancient,Loyalty], est=1826, actual=2573 (+41%)
  3. Ante3 Big: Pair T (fillers), jokers=[WT,Mad,Ancient,Loyalty], est=500, actual=2000 (+300%)
  4. Ante3 Boss hand1: Trips(facedowns), jokers=[all 6], est=330, actual=1800 (+445%)
  5. Ante3 Boss hand3: Trips Aces+facedowns, jokers=[all 6], est=2829, actual=6426 (+127%)
  All five discrepancies are the SAME root cause: Ancient Joker's rotating-suit xMult (and
  occasionally Loyalty Card's periodic x4) are never modeled by `advise`/`hands`, so est is a
  systematic floor/underestimate whenever either joker is owned. This makes `est` unreliable
  for go/no-go decisions near a blind's `need` threshold when Ancient Joker or Loyalty Card is
  in the joker list -- treat their `est` as a soft floor, not a prediction, and lean toward
  playing a marginal hand rather than folding to a "safer" alternative when either is present.

Bridge issues / bugs found (exact behavior):
  1. SELECT_BLIND transiently failed for several minutes at the start of a fresh run/session
     with "ACTION FAILED: blind_on_deck not set yet, retry None" (this was on the prior lost
     runs on this port, not this one -- see docs/runs/7782_VYP8RXFJ.md and
     docs/runs/7782_CIFLYYWN.md for detail). main.lua already has a `current_blind_on_deck()`
     fallback (checks round_resets.blind_states for the "Select" entry) used elsewhere but NOT
     wired into the SELECT_BLIND handler (main.lua ~line 1567 uses `G.GAME.blind_on_deck`
     directly instead of the fallback) -- this looks like the fix for exactly this failure mode
     already exists in the file but isn't applied to SELECT_BLIND.
  2. cli.py's `hands`/`advise` HIGH CARD picker (~line 522) selects the max-chip-value card
     without checking DEBUFF status, so on debuff bosses it can recommend scoring a card worth
     $0. Always cross-check a HIGH CARD recommendation against the DEBUFF tags before playing.
  3. cli.py's discard-advice logic repeatedly recommends a discard that destroys the very hand
     it just listed as best (`advise`'s "keep 3 highest, chase a flush/straight" default
     heuristic overrides an already-made higher-value hand such as Two Pair or a made Straight).
     Seen 3 times this run (Ante2 Boss, Ante3 Big, Ante4 Big). Always double check that the
     advised discard set doesn't include cards forming your current best candidate hand before
     running it.
  4. `advise`/`hands` has no model at all for The Mark's face-down-card rule (4+ face-down
     cards from J/Q/K guarantee at least a pair/trips by pigeonhole) and will suggest discarding
     them as junk. `play TYPE` does correctly skip its own type-check when face-down cards are
     selected ("Preview hidden (face-down cards selected): type check skipped, playing as
     requested"), and the underlying game scores the true hand regardless of the declared TYPE
     label -- so it's safe to declare any plausible label.
  5. Bridge/instance was killed and relaunched twice by the orchestrator during this session for
     reasons unrelated to gameplay (a bridge update, and a prior process restart) -- see the two
     prior run logs on this port for detail; this run (VVEMMSAY) itself completed without any
     bridge outage.

Playbook suggestions:
  1. Add to section 3 or 8: "If you own Ancient Joker or Loyalty Card, treat `est` as a soft
     floor, not a prediction -- actual scores can run 40-450% higher when the rotating suit/
     periodic proc lines up, and CAN also come in exactly at est when it doesn't. Do not fold to
     a discard-and-hope plan when a made hand's est is within ~30% of `need` and either joker is
     owned; the upside case is common enough to prefer playing the made hand."
  2. Add to section 6 (The Mark) or section 4: "Never let `advise`'s default discard heuristic
     discard cards that are part of the currently-best-listed candidate hand -- verify the
     discard set is disjoint from your best candidate's idx list before running it. This bug has
     been observed on non-boss hands too, not just The Mark."
  3. Add to section 8 (do-not list): "Do not skip a blind for a Skip Tag reward (even a
     'take'-listed one like Negative) if joker slots are already full AND you won't reliably
     reach another shop before the run's binding constraint (weak scaling) catches up -- banking
     the round's income/reps can matter more than a probabilistic bonus joker, especially past
     ante 3 where blind requirements roughly double each ante and a lost round of practice can't
     be recovered."
