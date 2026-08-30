# Run 7ZHPLKSF (port 7782) - stake 2 (Red Stake) - LOSS at ante 4 Boss (The Plant)

Ante 1: started. $4 -> $5 after start. Blind on deck: Small Blind 300 (tag Skip Tag), Big 450 (tag Charm Tag), Boss The Head 600.
Ante 1 Small (300): TwoPair A5 est104 actual104, FullHouse 333JJ est276 actual380(diff 38%, deck bonus/joker not modeled?) -> won 380/300. Bought Smiley Face ($4).
Ante 1 Big (450): TwoPair FACE QT est720 actual720 -> won 720/450. Bought Odd Todd ($4, +31 chips/odd card).
Ante 1 Boss The Head (600, debuffs Hearts confirmed - NOT clubs): chased club flush per advise, Flush C est1233 actual1233 -> won 1233/600. Jokers: Smiley Face, Odd Todd. $3 -> cash to $10 in shop.
Ante2 shop: bought Earth planet (Full House L2) since Uranus not offered, bought Abstract Joker ($4, +3mult/joker). Jokers 3/6.
Ante2 Small (800, tag Juggle): TwoPair A7 est1980 actual1980 -> won 1 hand. $2->$4.
Ante2 shop2: bought The World tarot ($3, banked, unused suit-convert).
Ante2 Big (1200, tag Buffoon): TwoPair FACE J5 est2352 actual2352 -> won 1 hand. $1->$7.
Ante2 shop3: bought Uranus ($3, used -> Two Pair L2), then Celestial pack ($4) offered Uranus again -> Two Pair L3(60x4). $0 left.
Boss on deck: The Wall 3200 (doubled requirement, per playbook).
Ante2 Boss The Wall (3200): Pair A est1034(pacing), then chased diamond flush per advise: Flush D est3105 actual4139 (diff 33% - est underestimates high-card diamond flush) -> won 4139/3200. $0->$6 in shop.
Ante3 shop1: picked Arcana pack -> Judgement tarot -> got Green Joker (+1mult/hand,-1/discard) as random joker (4/6 slots).
Ante3 Small (2000, tag Rare): TwoPair A5 est3672 actual3672 -> won 1 hand. $2->$4.
Ante3 shop2: Arcana pack -> High Priestess -> Earth planet -> used, Full House now L3(90x8).
Ante3 Big (3000, tag Garbage): TwoPair FACE KJ est3700 actual3700 -> won 1 hand. $0->$6.
Ante3 shop3: Arcana pack -> Wheel of Fortune (1/4 chance Polychrome on random joker) -> no visible effect (gamble missed). Skipped Death tarot ($3, couldn't afford after pack). $2, endshop.
Boss on deck: The Flint 4000 (base chips/mult halved).
Ante3 Boss The Flint (4000, base chips/mult halved): FullHouse 44488 est1241(pacing), then chased straight per advise, Straight AKQJT est2910 actual4151 (diff 43% - est underestimates high straight w/ Odd Todd) -> won 4151/4000. $2->$8 in shop.
Ante4 shop1: Mega Celestial pack ($8, choose 2) -> Uranus(TwoPair L4) + Earth(FullHouse L4). WARNING from shopadvise: upcoming boss The Plant disables Smiley Face.
Ante4 Small (5000, tag Ethereal): Straight 6high est2016(pacing) actual2516, then TwoPair FACE J4 est3024 actual3024(within round total 5540) -> won 5540/5000. $0->$1.
Ante4 shop2: $1, nothing affordable, endshop.
Ante4 Big (7500, tag Uncommon): FullHouse 66699 est4899(pacing) actual4899, Pair3 est1170(pacing) actual part of total, TwoPair FACE K7 est5104 -> won 11173/7500 total.
Ante4 shop3: Celestial pack ($4) -> Uranus -> Two Pair now L5(100x6). $1 left, endshop.
Boss on deck: The Plant 10000 (faces debuffed - disables Smiley Face per shopadvise warning).
Ante4 Boss The Plant (10000, faces debuffed, Smiley Face disabled): forced to burn all 3 discards early clearing debuffed faces
(JC/JD, KH/QD, QH/QC across three discard rounds) which left almost no cards to build a strong hand with. Sequence:
TwoPair 64 est2280 actual(part of running total, scored 2280 -> total 2280), HIGH CARD (forced, no pairs, 0 discards left)
est705 actual(total went 2280->2985, so this hand scored 705, matched est exactly), TwoPair 95 est5292 (LAST HAND, still
1723 short of need per advise's own math) actual(total 2985->8277, so this hand scored 5292, again matched est exactly)
-> LOST 8277/10000 (short by 1723). No consumable was usable at the last-hand check: The World tarot showed no
USE_CONSUMABLE legal action in SELECTING_HAND (it is a suit-conversion tarot with apparently no rescue value for a
dead final hand), so playbook 4.8's "never concede with unused consumable" check had nothing actionable to use.

Post-mortem: binding constraint = boss debuff (The Plant) combined with having spent all 3 discards on ante 3's boss
(The Flint) and ante 4 Small/Big before hitting The Plant, so 0 discards were available to work around the face-debuff.
By the time The Plant hit, every one of our first 3 hands drew face cards (J,K,Q x3) that scored nothing, and discarding
them away consumed the only tool we had to hunt for a second pair to complete Two Pair/Full House. The single decision
I would change: at ante 4's shop before The Plant, buy Luchador if it appears (playbook 6 explicitly recommends this
for suit/face-debuff bosses) even at the cost of skipping a hand-level pack; we had no Luchador offered in any of the
ante-4 shops we saw, so the real fix upstream is to REROLL specifically hunting for Luchador once the upcoming boss is
known to be a face/suit debuff, rather than always taking the Celestial/Arcana pack shopadvise defaults. Also: with
only 2 jokers being flat +mult/+chips beyond ante 2 (Smiley Face got disabled, Odd Todd/Abstract/Green Joker are
rank/count-based and unaffected by the face debuff) our per-hand ceiling was capped once the faces were gone; a second
scoring joker that does not care about faces (we had 3: Odd Todd, Abstract Joker, Green Joker) was not quite enough
chips/mult to clear a doubled-tier boss (The Plant's 10000 is not doubled per se, but ante 4's base 7500->10000 boss
step plus a still-early-level main hand L5 was too slow).

Bridge issues: none. Every `advise`/`shopadvise` call returned a clean ADVICE line; `ACTION FAILED` was never seen this
run; no retries were needed.

Playbook suggestions:
1. When shopadvise's WARNING flags an upcoming boss that disables a joker (e.g. "The Plant disables Smiley Face"),
   explicitly suggest buying/holding a Luchador if seen, or rerolling specifically for one, rather than only noting the
   warning passively — the current wording only says "plan around it," which does not translate into a concrete shop
   action once no Luchador is on offer.
2. `advise`'s LAST HAND CHECK should also state explicitly when a held consumable is NOT usable (e.g. "The World: no
   rescue value, suit-conversion only") so the agent does not have to discover this by testing for a missing
   USE_CONSUMABLE legal action mid-round.
3. Consider flagging, at the shop BEFORE a face/suit-debuff boss, how many discards remain unused relative to how many
   face cards the current deck composition holds — spending all 3 discards on faces during Small/Big left 0 discards
   for the boss itself, which is exactly the scenario playbook 6's Pillar-style "minimize total cards played" logic
   was designed to prevent, but nothing currently warns about discard budget specifically for face/suit bosses.
