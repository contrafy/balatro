# Run ZNZNQN4M (port 7782) - LOSS at ante 4 Boss blind (The Window)

Stake 1 (White). Ante 1 boss: The Manacle (-1 hand size).

Ante 1: jokers Chaos the Clown, Odd Todd (+31 chips/odd card). $5 end. Small 300: FH 232 + TwoPair 100 = 332 win.
Big 450: TwoPair 108 + FH(KKKTT) 360 = 468 win. Boss Manacle 600: FH(888KK) 336 + TwoPair 200 + TwoPair(Q5) 224 = 760 win.
No scoring joker until pack 2 shops (Odd Todd). Chaos the Clown free rerolls used to fish shops at no cost.

Ante 2 shop: bought Celestial pack (no Uranus offered); picked Earth (Full House) over Jupiter/Mercury -
deviation from shopadvise's "main hand Two Pair" tag (Full House scored highest in ante1 and naturally forms from Two Pair draws). FH now L2 65x6.

Ante 2: jokers +Mystic Summit (+15 mult @0 disc), +Astronomer (free planets/celestial). Small 800: FH(55577) 1494 win alone.
Big 1200: TwoPair(KKTT) 1440 (Mystic Summit fired, big boost) win alone. Boss The Psychic (5-card-only) 1600:
Trips(777) L2 820 + Flush(clubs) 564 + TwoPair(6644) L2 1080(Mystic Summit) = 2464 win. Bought Venus (free via Astronomer,
used immediately) leveling Three of a Kind to L2. Levels: FullHouse L2, TwoPair L2, ThreeOfAKind L2. $1 end of ante.

Ante 3: got 5H Glass card via Justice tarot (fired for x2 on a Pair, huge score jump). FullHouse leveled to L4 via free
Astronomer celestial packs + Earth. Small 2000: Flush(clubs) 1805 + Pair(Glass 5) 1558 = 3363 win. Big 3000:
Quads(KKKK) 700 + Pair(3s,Mystic Summit) 1674 + TwoPair(8866) 1224 = 3598 win. Bought Constellation joker (xMult
+0.1/planet used, fed reliably by free Astronomer planets) - first xMult source. Boss The Needle (1 hand only) 2000:
built AAKK, used last remaining discard AFTER advise said PLAY (est 432, guaranteed loss vs need 2000) to chase a
third A/K -> drew KKK for FullHouse(KKKAA) L4 est 5725, played that instead of advise's smaller-but-clearing TWOPAIR
suggestion (both cleared; FullHouse used the same cards with zero downside) -> win 5725/2000.

Ante 4: bought Chariot (Steel on an Ace) + Magician (Lucky on both Kings, needs 2 sel targets) from Arcana packs.
Got Constellation joker (xMult, fed by free Astronomer planets, grew to x1.1 by end of ante). Money stayed at
$0-4 all ante (every shop spent to $0-1 on packs per shopadvise) - never had $5-10 free when Photograph/The Trio/
Blueprint (real xMult jokers) appeared in shops, so none were bought. Small 5000: TwoPair 1224 + Straight(no
discards left) 2090 + Pair(Steel Ace,Mystic Summit) 1962 = 5276 win (only 276 margin - tight). Big 7500:
FullHouse(66633) L4 5025 + Pair(Lucky Kings) est810/actual1710 (>100% miss, Lucky Card +20 mult undercounted by
advise) + Trips(888) 1665 = 8400 win. Boss The Window (Diamonds debuffed) 10000: multiple diamond cards
scored 0 all round (AD, KD, 7D, 6D, 2D, JD debuffed across the 3 hands) crippling chip totals despite good hand
types (Flush clubs 3364, TwoPair KK77 1742, Straight 8-high 2549) = total 7655/10000, LOSS. Final jokers (5/6):
Chaos the Clown, Odd Todd, Mystic Summit, Astronomer, Constellation(x1.1). Levels: FullHouse L4, ThreeOfAKind L2,
TwoPair L2, Pair L3, HighCard L2(wasted, picked Pluto by mistake thinking it leveled Pair - it levels High Card).

Post-mortem: binding constraint = scaling (money never accumulated enough for a real xMult joker; only had
Constellation which was still weak at x1.1) compounded by The Window debuffing Diamonds across 3 hands of cards
we'd already committed to holding. The Window boss is unusually punishing when your deck/hand draws lean on one
suit by chance - est correctly modeled the debuff (scores matched est closely each hand) but the aggregate chip
loss across a whole round of draws was too much to overcome with only 1 weak xMult and no card enhancements on the
scoring suits. The one decision I'd change: at ante 4's second shop (after Small Blind, $4 in hand), skip the
$4 Arcana pack once and instead bank money 1-2 shops toward Photograph ($5, x2 mult on first face card, seen at
ante 3 shop) or The Trio ($8, x3 mult if Three-of-a-Kind, seen at ante 4 first shop) - either would have made the
Big Blind and Boss far safer. Following shopadvise's per-shop "buy the affordable scaling item" logic greedily
left us permanently too poor to grab the bigger, more impactful xMult jokers when they appeared.

Bridge issues: none - all commands worked as documented. One calibration note: Pair with a Lucky Card scoring
(idx1,2 Kings) est 810 vs actual 1710 (+111%), because est apparently does not model the Lucky Card's random
+20 mult proc; flagged per playbook's >20% miss threshold.

Playbook suggestions:
1. Add a rule: when a Photograph/The Trio/Blueprint/other reliable xMult joker appears but is unaffordable,
   explicitly note in shopadvise output that this justifies skipping the current shop's pack purchase to bank
   for it next visit, rather than always spending down to $0 on Arcana/Celestial packs at ante 3-4.
2. Warn explicitly under The Window/Head/Club/Goad bosses: when your hand naturally draws many cards of the
   debuffed suit across a full round (not just the current hand), the cumulative chip loss can sink a boss even
   when the current hand's est correctly excludes debuffed cards - consider holding a spare discard specifically
   to filter out debuffed-suit cards rather than only optimizing for the immediate best-scoring subset.
3. `advise`'s est for Lucky-enhanced cards appears to under-model the random +20 mult proc (score came in at
   more than double the estimate); worth flagging Lucky-card hands as "est is a floor, actual may run much higher"
   the way Misprint hands already are.
