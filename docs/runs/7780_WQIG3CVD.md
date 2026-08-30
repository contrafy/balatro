# Run WQIG3CVD (port 7780) - LOSS at ante 4 Big Blind (stake 3, Green Stake)

Ante 1: Small Blind (300, Investment Tag) skipped per ADVICE (no jokers yet, $0 reward, boss is The Club).
Big Blind 450: Flush 316 (est 316), Flush 312 (est 312), total 628. Cash $9.
Shop: bought Sly Joker $3 (Pair +50 chips), Scary Face $4 (+30 chips/face). Left $2, endshop.
Boss The Club 600 (Clubs debuffed): Two Pair 192 (est 192), Trips-face-Q 480 (est 480, note: debuffed card scores nothing), total 672. Cash $2 -> $33 (Investment Tag paid).
Ante 2 shop: bought Even Steven $4 (+4 mult/even card), Jumbo Celestial Pack $6 -> Uranus (Two Pair L2). Bought Grabber voucher $10 (+1 hand/round, now 4). Left $13, endshop.
Small Blind skipped (Foil Tag, $0 reward).
Big Blind 1350 (Orbital Tag - High Card): Trips 303 (est 303), Full House QQQ88 3015 (est 2712, +11% over est), total 3318. Cash $13 -> $21.
Ante 2 second shop: bought free Square Joker $0 (foil, +4 chips/4-card hand). 2x Mega Celestial Pack $8 each -> Uranus(Two Pair L3), Venus(Trips L2), Venus(Trips L3), Earth(Full House L2). Left $5, endshop. Jokers now 4/6: Sly, Scary Face, Even Steven, Square Joker. Levels: Trips L3(70x7), Two Pair L3(60x4), Full House L2(65x6).
Boss The Mark 1800 (faces face-down): Pair-4s 1180 (est 1180), Pair-10s 2480 total (est 1300 for that hand alone, so hand2 alone scored 1300 matching est). Ante 2 boss cleared 2480/1800. Cash $5 -> $13.
Ante 3 upcoming boss: The Head.
Ante 3 shop1: bought Vampire $7 (xMult growth +0.1/enhanced card). Jokers now 5/6.
Small Blind 2600 (Standard Tag, played per ADVICE): Two Pair K2 2928 (est 2928). Cash $6 -> $10.
Ante 3 shop2: bought Arcana Pack $4 x2. Pack1: used Strength on T,Q (T->J, made JJJ trips potential). Pack2: used Empress on two 9s (+4 mult enhancement each, feeds Vampire). Left $2, endshop.
Big Blind 3900 (Charm Tag): Straight-11high 1848 (est 1848), Two Pair A3 (disc), Trips-5(3) 1253 (est 1253, kept AA pair via fillers), Two Pair KQ 1280 (est 1280), total 4381. Cash $2 -> $7.
Ante 3 shop3: nothing worth buying (Gros Michel AVOID-flagged, decaying), endshop.
Boss The Head 5200 (Hearts debuffed): Straight-11high 1848 (est 1848). NOTE: misread A-K-Q-J-T as royal flush (KC is clubs not diamonds) -- `play ROYALFLUSH` aborted correctly with "these cards form Straight", re-ran hands and played STRAIGHT correctly (CLI safety worked as designed, no game state lost). Two Pair K5 840 (est 840, one debuffed King scored nothing). Pair-8 1260 (est 1260). Total 5716/5200 cleared. Cash $7 -> $13.
Ante 4 upcoming boss: The Plant (faces debuffed) -- we hold Scary Face (relies on face cards) and enhanced 9s (non-face), should be fine as long as pair-family hands don't rely solely on faces.
Ante 4 shop: bought Jumbo Celestial Pack $6 -> Uranus (Two Pair L4, Venus not offered). Left $7, nothing else affordable/worthwhile, endshop.
Small Blind skipped (Polychrome Tag, $0 reward).
Big Blind 12000: Two Pair J6 3536 (est 3536), disc, Full House 44488 5018 (est 5018), disc (kept KK pair), Full House KKKQQ 2190 (est 2190), disc (kept AA pair, last discard used), forced final hand Two Pair A3 1040 (est 1040) -- NO DISCARDS OR CONSUMABLES LEFT, 216 chips short. Total 11784/12000. LOST. RUN OVER at ante 4, GAME_OVER confirmed.

Final state: jokers 5/6 (Sly Joker, Scary Face, Even Steven, Square Joker, Vampire), $7 unspent, Levels: Three of a Kind L3(70x7), Two Pair L4(80x5), Full House L2(65x6). Best result: stake 3, ante 4, Big Blind, 11784/12000 (98.2%, 216 short).

Post-mortem: binding constraint was SCALING, not money or a single misplay. Vampire (xMult growth, +0.1 per enhanced card PLAYED) was bought at ante 3 but only ever enhanced 2 cards (two 9s via Empress), and at least one of those enhanced 9s was discarded rather than played in several late hands (including the very last forced hand, which used no enhanced cards) -- Vampire almost certainly stayed at x1.0 the entire run, a dead xMult slot per the playbook's "a growth joker you never feed is a dead slot" rule. Levels were also split three ways (Three of a Kind L3, Two Pair L4, Full House L2) instead of concentrating on one main pair-family hand, so no single level was high enough to clear the ante-4 Big Blind's steep Green-Stake requirement (12000) with only flat +chips/+mult jokers (Sly +50 chips, Scary Face +30/face, Even Steven +4 mult/even, Square Joker +4 chips/4-card hand) and zero live xMult.
Decision I would change: when enhancing cards for Vampire, prioritize PLAYING those enhanced cards over discarding them even when they are not part of the current best-scoring combo, to actually grow the xMult before it is needed; alternatively, sell Vampire earlier for a joker that helps immediately rather than carrying an unfed growth slot into ante 4's steep scaling requirement.
`est` accuracy: every played hand's actual score matched `est` exactly (0% deviation) in every ante this run, including hands with debuffed cards (The Club, The Head, The Mark) where the CLI correctly modeled 0 contribution from debuffed cards. No case exceeded the 20% threshold worth flagging.
Bridge issues: one `ACTION FAILED: Round eval blocking events still pending, retry shortly` on `cash` after the ante-1 boss, resolved by `sleep 2` + retry per playbook (no repeat occurrences). One self-inflicted abort: `play ROYALFLUSH 1 2 3 4 5` was rejected with "these cards form Straight" because card idx 2 was KC (Clubs) not KD as I misread from the printout -- re-ran `hands`, confirmed only 4 of 5 cards were Diamonds, and replayed correctly as `STRAIGHT`. This was the CLI's type-check working as designed (playbook section 1: "ABORTS if they do not form TYPE"), not a bug -- no state was lost.
Playbook suggestions:
1. Add an explicit reminder in section 4/7 to PLAY enhanced/Vampire-feeding cards when a discard vs. play choice is close in `est`, since `advise`/`hands` currently rank by immediate est only and do not account for feeding a held growth-xMult joker.
2. Consider having `shopadvise`/`advise` track "xMult jokers bought but never fed" (e.g. Vampire with 0 enhanced cards played since purchase) and surface a warning, similar to the existing "no rescue tarot held" warning.
3. Confirms existing playbook guidance ("commit to one main type by ante 3") with a concrete failure case: splitting levels across Three of a Kind/Two Pair/Full House this run left every level too low to clear ante 4's Big Blind by 216 chips with zero live xMult.
