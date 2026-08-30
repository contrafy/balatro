# Run 9WJNUQCD (port 7782) - stake 3 (Green Stake)

Ante 1: Small Blind 300 tag=Charm Tag (not a joker/pack tag) -> ADVICE b blind, played.
- Small Blind: discarded per advise, Full House JJJKK L1 est 360 -> actual 360, cleared 300. Shop: bought Fibonacci from Buffoon pack ($4, floor joker), $2 left, endshop.
- Big Blind: Trips AAA (Fibonacci fires on 3 Aces) est 1701 -> actual 1701, cleared 450 in 1 hand. Shop: bought Smiley Face $4 (2nd floor joker), Celestial pack -> Mars (levels Four of a Kind, pair-family), $0 left.
- Boss The Hook: only Straight 6-high cleared (est 1400, Trips only est 144) -> actual 1400, cleared 600 in 1 hand (2 hands, 3 discards unused -> +$5 at cashout).
- Ante 1 complete, no losses. Jokers: Fibonacci, Smiley Face. Levels: Four of a Kind L2. $7 entering ante 2 shop.

Ante 2: Small Blind 900 tag=Top-up Tag -> ADVICE b skip (gives 2 free Common jokers), skipped. Shop: bought Half Joker $7 (foil, 3rd floor joker, +20 mult if <=3 cards).
- Skip granted 2 free jokers: Crazy Joker (+12 mult if Straight, off-type) and Shoot the Moon (+13 mult per Queen held, conditional) -> 5/6 slots filled.
- Big Blind 1350: Pair 2,2 (2 cards, triggers Half Joker) est 2432 -> actual 2432, cleared in 1 hand. Shop: Celestial pack -> Earth (levels Full House, pair-family) L2.
- Boss The Needle (1 hand only, need 900): no pair in hand at start; advise found HIGH card Ace (Fibonacci fires on Ace + Half Joker <=3 cards) est 2772 -> actual 2772, cleared without touching discards.
- Ante 2 complete, no losses. Jokers: Fibonacci, Smiley Face, Half Joker, Crazy Joker, Shoot the Moon (5/6). Levels: Four of a Kind L2, Full House L2. $7 entering ante 3 shop. No rescue tarot held yet (playbook flags ante 3+ shops where none held).

Ante 3 (upcoming boss The Water): shop -> Arcana pack, applied Empress (+4 mult) to Ace+2 (Fibonacci ranks). Bought The Chariot tarot $3 (held as consumable, not yet used -- no Steel target chosen).
- Skipped Small Blind for Holographic Tag (free +10 mult edition on next joker).
- Big Blind 3900: Straight JT987 est 3596 (pacing, kept discards) -> actual 3596; then Pair KK (2 cards) est 4640 -> actual scored total 8236, cleared in 2 hands (1 discard used, 2 left).
- Shop: bought free Blackboard ($0, holo, x3 if all held cards Spades/Clubs -- conditional/unreliable per shopadvise but free) -> 6/6 joker slots full. Left $5 unspent (Jumbo Celestial $6 unaffordable, Supernova would empty wallet with full slots) per shopadvise LEAVE.
- Boss The Water (no discards, need 5200): Pair 2,2 (1 enhanced Mult) est 4160 -> actual 4160; Pair QQ (Shoot the Moon fires) est 3360 -> actual scored total 7520, cleared in 2 hands, 1 hand unused (+$1).
- Ante 3 complete, no losses. Jokers: Fibonacci, Smiley Face, Half Joker, Crazy Joker, Shoot the Moon, Blackboard (6/6, full). Levels: Four of a Kind L2, Full House L2. Cons: The Chariot (unused). $12 entering ante 4 shop. Still no rescue tarot (Death/Strength/Justice) banked -- Chariot is Steel enhancement, not one of the three.

Ante 4 (resumed mid-run after session cutoff -- state on resume showed 5/6 jokers: Fibonacci, Smiley Face, Half Joker,
Shoot the Moon, Blackboard; Crazy Joker no longer present -- presumably sold in the ante-4 shop by the prior agent
before the cutoff, no record of what it was sold for; Chariot tarot still held unused). Boss The Wheel (need 16000)
was already in progress at hand 3/3, disc 1/1, scored 9359 when resumed.
- Final hand: `advise` showed only Pair 4 est 3060 (need 6641) -> DISCARD idx 3,5 (TD + facedown card) to keep the
  4-pair floor and draw toward the 4 held clubs. Redraw gave Two Pair (4s+3s): advise est TWOPAIR 5 6 7 8 4 = 4368,
  still 2273 short with 0 discards/0 hands left after. Per playbook 4.8 (LAST HAND CHECK), used the held Chariot
  tarot (`sel 3` then `use 1`) on 8C (an unplayed/held card, clubs) for a Steel enhancement (+1.5x mult while held) --
  this also preserved Blackboard's "all held cards Spades/Clubs" condition (held cards after play: KC, QC, 8C-Steel,
  all clubs). Re-ran advise: est rose to 6032 (still 609 short) -> played it anyway as the only remaining option.
  ACTUAL: `play` line showed "est 18096" (not the advise-line 6032) and the real score matched exactly: scored total
  jumped 9359 -> 27455, clearing 16000 comfortably. **advise-vs-play discrepancy >20% (6032 vs 18096, 3x)**: the
  `advise`/`hands` candidate-hand estimator appears to under-value this hand (Two Pair 4,4,3,3 + Fibonacci x2(+8) +
  Shoot the Moon (Queen held, +13) + Blackboard x3 (all-clubs held) + fresh Steel 8C x1.5) relative to the `play`
  command's own preview, which was accurate. Logging per playbook instructions.
- Cashed out ($2 -> $7). Ante 4 complete, no losses. Jokers: Fibonacci, Smiley Face, Half Joker, Shoot the Moon,
  Blackboard (5/6, one open slot). Levels: Four of a Kind L2, Full House L3, Three of a Kind L2, Two Pair L2 (Pair
  still L1). Chariot tarot consumed (no rescue tarot Death/Strength/Justice held -- flagged again). $7 entering
  ante 5 shop. Upcoming boss: The Window (suit debuff).

Ante 5: Small Blind (need 20000), tag=Meteor Tag (not joker/pack, but ADVICE said `b blind` -> played, not skipped).
- Hand 1: Trips QQQ kept, drew KK -> Full House QQQKK est 8170 -> actual 8170, scored 8170.
- Hand 2: drew a Full House 666+55, est 5712 -> actual 5712, scored 13882 total.
- Hand 3 (1 hand, 1 discard left, need 6118 more): 5 spades held (A,Q,9,5,4) = a made Flush, plus JD/TC kept for a
  possible Broadway straight (A-K-Q-J-T) if a King was drawn. ADVICE: disc 8 (3D) to keep JD/TC for the straight draw.
  Drew 2C (no King) -> no straight, only the Flush remained. Final forced hand: FLUSH idx 1,2,5,6,7 (all spades) est
  4340 -> actual 4340 (est matched exactly this time), total 18222 -- 1778 SHORT of 20000. LOST the Small Blind, GAME_OVER.
  Bridge showed `Legal:` empty after, confirming no further actions possible.
- **Root cause worth flagging**: the discard on hand 3 kept JD (a diamond) among the held/unplayed cards. Blackboard
  (x3 if ALL held cards are Spades/Clubs) needs the cards NOT played to be suit-pure; JD held broke that condition,
  so Blackboard's x3 never fired on the final hand (4340 stayed 4340; with it, 4340x3=13020 would have cleared easily,
  13882+13020=26902 >> 20000). Discarding JD instead of 3D (keeping TC alone, or just the 5 flush spades + no chase)
  would have preserved Blackboard's condition. `advise`'s discard logic optimized for the straight-chase upside but
  did not account for Blackboard's held-card suit-purity requirement.
- Money at loss: $1 (spent $6 on a Jumbo Celestial pack in the ante-5 shop for Uranus/Two Pair, since Full House's
  planet Earth was not offered in that pack).

FINAL RESULT: LOSS, stake 3 (Green Stake), ante 5, Small Blind, 18222/20000 (1778 short).
Jokers at loss (5/6, one slot never filled after Crazy Joker was sold by the prior session before this agent
resumed): Fibonacci (+8 mult per A/2/3/5/8), Smiley Face (+5 mult per scoring face), Half Joker (+20 mult if <=3
cards played, foil), Shoot the Moon (+13 mult per Queen held), Blackboard (x3 if all held cards Spades/Clubs, holo).
No true xMult joker: Blackboard is the only multiplier and it is fully conditional on suit purity of the cards NOT
played, which is easy to break by accident during a discard/keep decision (as happened here).
Levels at loss: Four of a Kind L2, Full House L3, Three of a Kind L2, Two Pair L3 (Pair never leveled past L1).
Money curve: ante1 exit $7, ante2 exit $7, ante3 exit $12, ante4 exit (resumed mid-boss) $2 -> cashed to $7,
ante5 shop spent to $1, lost with $1 in hand.

Post-mortem: binding constraint was the Blackboard suit-purity condition silently breaking on the forced final
hand's discard choice, compounding a build that had no unconditional xMult joker (Fibonacci/Smiley/Half Joker/
Shoot the Moon are all flat +mult; Blackboard was the only x-mult and it required active suit management that
`advise` did not surface). Decision I would change: on the ante-5 final-hand discard, keep only clubs/spades among
the retained cards (discard JD, not 3D) to preserve Blackboard's x3 even at the cost of the straight-chase upside --
a guaranteed x3 was worth far more than a low-probability King draw.
Bridge issues: none this session -- all commands (`s`, `advise`, `hands`, `disc`, `play`, `sel`, `use`, `pack`,
`pick`, `shopadvise`, `cash`, `endshop`, `blind`) returned normally, no retries needed. One notable estimator gap
(not an error): on the ante-4 boss The Wheel final hand, `advise`'s candidate-hand est (6032, after the Chariot
Steel enhancement) was far below the `play` command's own preview and the actual score (both 18096, an
advise-vs-play discrepancy of ~3x / >200%). Also see the "Playing Two Pair ... est 18096" line above.
Playbook suggestions:
  1. When Blackboard (or any "all held cards must be suit X/Y" joker) is owned, `advise`'s discard recommendation on
     a forced-final-hand setup should prefer discarding off-condition-suit cards over on-condition-suit cards, even
     when the off-suit card is part of a chase (straight/flush draw) -- losing a guaranteed x3 is usually worse than
     the chase's marginal EV. This run's loss (1778 short) would have been avoided by that rule.
  2. `advise`'s candidate-hand `est` for Two Pair/pair-family hands with a Steel-enhanced held card and/or Blackboard
     active can undershoot the real `play`-time score by 3x (6032 vs 18096, ante 4 boss The Wheel here); the `hands`/
     `advise` estimator may not be folding in a freshly-applied Steel card's xMult or Blackboard's x3 correctly when
     computing the pre-play candidate list, even though the `play` command's own preview gets it right. Worth an
     estimator audit specifically for Blackboard + Steel interactions.
  3. Re-confirm the "resumed mid-run" case in the playbook/prompt template: this run had a gap where a previous
     agent's session was cut off mid-ante-4-shop with no log entry for what was bought/sold (Crazy Joker vanished,
     joker slots went from 6/6 to 5/6, money dropped $12->$2, with no record of the trade). Consider having the CLI
     or bridge persist a lightweight shop-transaction log so a resuming agent can reconstruct what happened.
