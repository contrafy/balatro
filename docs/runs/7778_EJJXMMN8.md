# Run EJJXMMN8 (port 7778) - LOSS at ante 3 boss (The Wall)

Stake 1 (White). Boss preview: The Hook (ante 1).

Ante 1: jokers [Sly Joker $3 (+50 chips/Pair), Smiley Face (pack, +5 mult/face), Wily Joker $4 (+100 chips/Trips)],
  consumables: The Wheel of Fortune $3 tarot (used on a joker in shop - no visible edition applied).
  Small Blind 300: DISCARD x2 (advise) -> STRAIGHT 12-high est 308 -> scored 308. Cash->$9.
  Big Blind 450: STRAIGHT 9-high est 260 -> scored 260, then PAIR FACE QQ est 960 (Smiley Face x2 faces + Sly
    Joker pair chips) -> scored 960. Total 1220 vs need 450. Cash->$7.
  Boss The Hook (600, discards 2 random cards each hand played): DISCARD x1 chasing flush (advise EV371 vs
    made pair 128) -> drew into 5 spades already -> FLUSH S est 612 -> scored 612 vs need 600. Cash->$0.
  Shop buys: Sly Joker $3, Smiley Face (Buffoon pack pick over Reserved Parking econ joker - scoring joker
    preferred per playbook), Wily Joker $4, Wheel of Fortune tarot $3 (per shopadvise; spent to $0).

Ante 2: jokers +Greedy Joker (Buffoon pack, +3mult/diamond, over Square Joker's awkward exactly-4-card
  condition), +Justice tarot $3 (held unused, NOUSE, saved as a targeted-save option per playbook 7a),
  Mercury planet (Celestial pack, no Saturn offered) -> Pair L2(25x3).
  Small Blind 800: DISCARD x2 (advise, chasing straight) -> STRAIGHT 9-high est 650 -> scored 650, then
    TWOPAIR FACE Q7 est 1560 -> scored 1560. Total 2210 vs need 800. Cash->$4.
  Big Blind 1200: DISCARD x1 (advise) -> FLUSH D est 1368 -> scored 1368 vs need 1200. Cash->$6.
  Boss The House (1600, first hand dealt face-down): discarded facedown cards in two batches (5 then 3) until
    fully revealed -> THREE OF A KIND FACE K (KS KH KC) est 3780 -> scored 3780 vs need 1600. Cash->$9.
  Shop buys: Even Steven $4 (+4mult/even) - OVERRIDE of shopadvise's Flower Pot ($6, x3 if all 4 suits): our
    engine has played 2 flushes already (single-suit hands), which structurally can never trigger Flower
    Pot's all-4-suits condition, and playbook 7a explicitly warns never to make Flower Pot a sole xMult
    source. Bought Even Steven instead (reliable, hand-type-agnostic). Jokers now 5/6, still zero xMult.

Ante 3: jokers 5/6 unchanged (Sly, Smiley, Wily, Greedy, Even Steven - all flat +chips/+mult, ZERO xMult all
  run). Uranus planet (Celestial pack) -> Two Pair L2(40x3). Justice tarot still held.
  Small Blind 2000: DISCARD x2 (advise) -> TWOPAIR FACE K6 est 2652 -> scored 2652 vs need 2000. Cash->$15.
  Big Blind 3000 (tag D6): DISCARD x2 (advise) -> TWOPAIR T5 est 2040 -> scored 2040, then TWOPAIR FACE FACE
    KQ est 2990 -> scored 2990. Total 5030 vs need 3000. Cash->$18.
  Shop ($18): main hand identified as Two Pair. REROLLED once ($5) per playbook (ante3+, no xMult, $15+)
    hunting an xMult joker before locking the 6th slot with Golden Joker (econ) - reroll surfaced only Flower
    Pot (unreliable xMult, AVOID per playbook) and The Idol (unknown). Did NOT reroll again (would have
    dropped below the $10 ante1-3 floor per section 8 do-not list) - LEFT with 5/6 slots, still zero xMult.
  Boss The Wall (8000, x2 chips required - the doubled requirement was already baked into the displayed
    8000 need): drew a 6-spade hand. DISCARD x3 (all advice-driven) chasing/refining a spade flush; used the
    held Justice tarot (`sel 1` then `use 1`) to add Glass Card (x2 mult) to the Ace of Spades in the flush
    since 0 discards remained after round-shaping and every point mattered. Final sequence, no discards left
    after hand 1: FLUSH S (AS-glass, KS, TS, 9S, 8S) est 1743 -> scored 1743, TWOPAIR FACE K7 est 1612 ->
    scored 1612, TWOPAIR 42 est 2244 -> scored 2244 (forced final hand, no discards/consumables left, all
    three ests matched actual exactly). Total 5599 vs need 8000 - LOST by 2401 (30% short). GAME_OVER.

## Post-mortem

Best result: stake 1 (White), ante 3, boss blind The Wall (need 8000), lost by 2401 (scored 5599, 70% of
target). Every blind ante 1-3 up to this point was cleared comfortably (typically 1.3x-2.7x the requirement).
Every `est` matched the actual scored amount exactly across all plays this run (0% deviation) - no case
exceeded the 20% threshold the log is supposed to flag, including the boss-debuff-adjacent Glass Card play.

Final jokers (5/6, in scoring order): Sly Joker (+50 chips/Pair), Smiley Face (+5 mult/scoring face),
Wily Joker (+100 chips/Trips), Greedy Joker (+3 mult/Diamond), Even Steven (+4 mult/even card). Zero xMult
jokers the entire run (four antes). Consumables: The Wheel of Fortune (used ante 1, no visible effect),
Justice (used ante 3 boss, Glass Card on 1 flush card, +332 to that hand's est). Hand levels: Two Pair
L2(40x3), Pair L2(25x3).

Money curve: ante1 $4->9->7->0 (Hook boss, spent to $0 twice); ante2 $0->4->6->9 (House boss); ante3 $9->15->
18->13 (after one reroll)->13 (start of boss, no further spend since no xMult surfaced) -> $13 at loss.
Money never crossed $20; the run never reached the $25-by-ante-4 target because it never got there.

Binding constraint: SCALING, not a misplay. This run repeated the exact failure mode flagged in the prior
run's post-mortem (D65ZIET8): five joker slots filled with flat +chips/+mult jokers and genuinely zero xMult
source across four antes, despite one explicit reroll hunt at ante 3. The Wall's x2-chips requirement (8000,
effectively needing ~2667/hand average) was simply out of reach for a build whose best single hand all game
was ~2990 (a lucky double-face Two Pair) - a build with even one x2-x3 mult joker would have cleared this
with room to spare. Two shops in a row (ante 2 end, ante 3 start) offered zero real xMult jokers at all,
which is a luck factor, but the response to that scarcity (one reroll, then stopping at the $10 floor) may
have been too conservative once a boss known to double the requirement (The Wall) was the very next fight.

The one decision I would change: after the ante-3 reroll surfaced only Flower Pot/The Idol and the shop
showed "Upcoming boss: The Wall" (a doubling boss), I should have treated that boss preview as the deciding
factor and either (a) bought Flower Pot anyway despite its unreliability - Two Pair's two ranks can span all
four suits often enough to be a real x3 shot, unlike a single-suit Flush - or (b) rerolled at least once more
even below the $10 floor, since the floor guidance is a general antes-1-3 heuristic and this was the single
highest-leverage moment all run to break it (a x2-chips boss immediately following two joker-less shops).
Section 5's blanket "never reroll to under $10 in antes 1-3" should probably carry an explicit exception for
"the next blind is a boss that doubles/triples the requirement and you own zero xMult."

Bridge issues: none. Every `disc`/`play`/`buy`/`pack`/`pick`/`sel`/`use`/`reroll`/`endshop`/`blind`/`cash` call
succeeded on the first try all run; no `ACTION FAILED` or retry was ever needed.

Playbook suggestions:
1. Section 8 do-not list: add an explicit exception to "Never reroll to under $10 in antes 1-3" for the case
   where the upcoming boss doubles/triples the chip requirement (The Wall, Violet Vessel-style) AND you still
   own zero xMult jokers - in that specific situation the doubling boss is the more dangerous risk than a
   thin bankroll, and shopadvise/advise do not currently flag this tradeoff explicitly.
2. Section 7a: Flower Pot's "rarely fires, never make it your only xMult" warning was written with a
   Flush-only mental model in mind; note that it is considerably more viable as a Two-Pair-engine's xMult
   (2 ranks x 2 suits each naturally spans up to 4 suits) than as a Flush-engine's (structurally 1 suit,
   can never trigger). shopadvise's blanket AVOID-style framing does not currently distinguish these cases.
3. Confirms this run: `est` was exact in every single play this run (~14 plays across 4 antes), including
   the one Glass-Card-modified play. No changes needed to the est engine based on this run's evidence.
