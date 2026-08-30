# Run VNPUS4SV (port 7778) - LOSS at ante 5 boss The Fish - Stake 2 (Red Stake)

Continuing from previous run G8BE3NLF (loss at ante 6 Big Blind, stake 1). Orchestrator notified that another player
beat stake 1, so all players advance to stake 2 (Red Stake: no Small Blind reward) per playbook section 2 step 7.

Ante 1: starting $4, no jokers, boss ahead = The Head (hearts debuffed). Bought Buffoon Pack, picked Card Sharp (x3 mult
  if hand type already played this round) as FIRST joker -- rare xMult joker found at ante 1! Then bought Walkie Talkie
  ($4, +10 chips +4 mult per 10/4 rank card). Ordered xMult (Card Sharp) rightmost. Small 368/300 (Full House AAKKK dealt
  naturally). Big 696/450 (registered Two Pair for Card Sharp hand 1, then Two Pair x3 twice). Head boss 1740/600:
  registered Straight (hearts debuffed so flush was weak), then Straight x3 with a wheel straight (A-2-3-4-5) cleared
  easily. Excellent start with Card Sharp acquired ante 1 -- much stronger than the previous stake-1 run's xMult (found
  only at ante 5).
Ante 2: bought Arrowhead ($7, +50 chips/Spade), reordered xMult (Card Sharp) rightmost. Boss = The Manacle (-1 hand size,
  7 instead of 8). Small 1112/800 (Straight, no Card Sharp registration needed since already registered same round? no --
  fresh round, played straight anyway since it cleared outright). Big 5648/1200 (registered Two Pair, then Two Pair x3
  with an Arrowhead spade filler). Manacle boss 4632/1600: registered Two Pair hand 1 (960), then Two Pair x3 (3672)
  cleared it in 2 hands despite reduced hand size. Picked Smiley Face WITH HOLO EDITION (+10 mult bonus) from a Buffoon
  pack -- first edition card of this run. 4/6 joker slots, still just 1 xMult (Card Sharp) but it is already carrying
  the run (est values now in the thousands at ante 2, far ahead of the stake-1 run's pace at the same point).
Ante 3: filled last 2 joker slots (6/6): Bull (economy, avoided Ice Cream from same pack per do-not-list) and Scholar
  (+20 chips +4 mult per Ace, playbook-flagged good). Reordered Card Sharp rightmost each time a joker was added. Leveled
  Two Pair->L2 (Uranus) and Full House->L2 (Earth, secondary pair-family per playbook) via 2 Celestial packs, spending down
  to $0 despite the upcoming Tooth boss -- a deliberate call to keep scaling since shopadvise didn't flag Tooth-specific
  caution and the level compounds forever. Boss = The Tooth (-$1/card played). Small 3252/2000 (registered Trips, then
  Pair). Big 4232/3000 (registered Pair, then Two Pair). Tooth boss 7177/4000: registered Two Pair (4 cards, no fillers
  per advise), then Three of a Kind on a natural AAA draw with Scholar tripling the Ace bonus (est 4325) -- cleared in 2
  hands. Money went to -$7 from the Tooth debuff (confirms debt goes negative, not floored at 0) and sat at -$1 through
  the ante 4 shop with nothing affordable.
Ante 4: money recovered from Tooth debt ($-1 -> $0 -> $4) across the ante; nothing affordable most shops. Boss = The
  House (first hand fully face down). Small 5320/5000 (registered Pair, then Pair Aces x3 with Scholar). Big 13460/7500
  (registered Pair, Two Pair QT, Two Pair KJ x3). House boss 20022/10000: discarded 5 face-down cards on the fully-blind
  first hand per playbook 3/6 guidance, revealing visible cards over 2 more discards, then registered Two Pair and rode
  Card Sharp x3 through the rest of the round (Two Pair K4 -> Two Pair 53 -> forced final hand Two Pair T6 est 12600,
  cleared easily). 6/6 joker slots still, only 1 xMult (Card Sharp) but est values now regularly 5-20k per hand at ante 4-5
  boundary -- far ahead of the stake-1 run's ante-4 pace (its best hand was ~11k at ante 4).
Ante 5: bought last Celestial Pack (Jupiter, Flush->L2, diversifying hand types since no Uranus offered) and an Arcana
  Pack, using The Lovers tarot on a Jack to give it Wild Card enhancement (counts as any suit) rather than a simple suit
  swap. Could not afford Seeing Double ($6, conditional xMult) with only $1 -- shopadvise confirmed no room to hold cash
  for it. Boss = The Fish (drawn cards come back face down). Small 11209/11000 (registered Straight, then Full House,
  Two Pair -- very tight margin, only 209 to spare). Big 20303/16500 (registered Full House TTTAA with Scholar+Walkie
  Talkie, then Two Pair, then Straight A-high to close it). Fish boss LOST at 13669/22000: registered Full House hand 1,
  but every subsequent draw came back mostly face-down (3-5 of 8 cards each time) and playable material dried up --
  final 2 hands were High Card/Pair only, with no consumables held (The Lovers had already been spent) to rescue the
  gap. Ended at 13669/22000, a 62% completion.

Post-mortem: binding constraint was BOSS-SPECIFIC BAD LUCK compounding on an already-thin scaling base, not a clear
  misplay. Card Sharp (x3, found ante 1) carried the whole run and let flat Pair/Two Pair/Full House hands reach
  8-20k by ante 5, comfortably clearing Small and Big Blind -- but The Fish's face-down redraws meant repeated discards
  returned unusable cards, and by the final forced hand only 3 visible cards remained with no pair among them. With
  only 1 xMult joker for the whole run (despite 6/6 slots filled by ante 3), there was no scaling margin to absorb a
  bad-luck boss; a second xMult or an enhanced (Glass/Steel) card in hand would very likely have let an earlier hand
  clear before the face-down attrition became fatal. The decision I would change: with 6/6 joker slots full and money
  routinely at $0-5 through antes 3-5, I should have sold one of the weaker flat jokers (Bull, an economy joker worth
  little once ante 5+ scaling matters more than interest) at the first ante-5 shop to keep a slot open for any xMult
  offer, rather than staying full and hoping shopadvise's sell-then-buy trigger fired again (it never did this run).
Bridge issues: none. All commands behaved as documented; `advise`/`shopadvise`/`hands` outputs matched actual scores
  within a few percent on every hand that completed normally (no >20% est-vs-actual miss to report). Confirmed The
  Tooth boss's money debt goes negative (not floored at $0): reached $-7 after two Tooth hands.
Playbook suggestions:
  1. Under The Fish (drawn cards face down), the playbook's existing guidance ("never chase flushes/straights, play
     rank-based hands from visible cards") held up well for hands 1-3, but by hands 4-5 nearly the whole hand was
     face-down and no amount of correct play could recover -- worth adding an explicit note that The Fish, unlike The
     Wheel/Mark/House, can compound across MULTIPLE hands in the same round (redraws stay face-down repeatedly), so a
     round that starts strong can still fail once several hands are spent; budget for finishing in 1-2 hands under
     this boss rather than planning to grind it out over 3.
  2. Confirmed from this run: Card Sharp (x3, common rarity) found at ante 1 is an exceptionally strong early xMult --
     worth calling out in 7a as a top-priority Buffoon Pack pick alongside Photograph/Baron, since it applies to
     WHATEVER hand type you register each round, making it far more flexible than a fixed-type xMult.
  3. Reinforce rule from stake-1 run's post-mortem: with 6/6 joker slots full and fewer than 2 xMult sources by ante 5,
     proactively sell the weakest flat/economy joker (not wait for shopadvise's specific sell-then-buy trigger) to keep
     a slot open -- this run and the prior stake-1 run both lost with exactly one xMult joker and a full bench of flat
     jokers that could not have absorbed an xMult even had one appeared.
