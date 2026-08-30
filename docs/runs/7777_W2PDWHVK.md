# Run W2PDWHVK (port 7777) - LOSS at stake 1, ante 3, Big Blind (need 3000, scored 2336)

Stake 1 (White), Black Deck.

## Stake 1 (White)

Ante 1: Start $4, no jokers. Small Blind (300): discarded twice chasing diamond flush per advise, flush est 288 (played, actual 288) then pair est 56 closed it (scored 344/300). Shop: bought Scary Face ($4, +30 chips/face). Overrode shopadvise's "buy Devious Joker" (rare condition, +100 chips only on Straight, not our build) -> took Buffoon Pack ($4) instead, picked Photograph (x2 mult on first scoring face card) over Crazy Joker -> matches playbook 7b face-pair engine. $0 left, endshop.
Big Blind (450): traded a guaranteed Trips-2 (est 108) to chase a straight per advise (EV 395), missed the straight draw but landed A/A Q/Q two pair (faces) -> TWO PAIR FACE AQ est 488, played, scored 488/450 (est accurate).
Boss The Manacle (600, -1 hand size): built Trips-5 -> drew into Quads-5, est 1428, scored 1428/600 (huge est/actual match; est is directional here per Photograph face bonus not applying since no face card scored).
Shop (ante1->2): $9. Bought Odd Todd ($4, +31 chips/odd card). Reordered jokers to keep Photograph (xMult) rightmost: [Scary Face, Odd Todd, Photograph]. $2 left, endshop.
Jokers after ante 1: Scary Face, Odd Todd, Photograph (3/6 slots). Money: $2 -> ante 2 shop $9.

Ante 2: Shop: bought Celestial Pack ($4) -> picked Uranus (Two Pair level, now L2 40x3) to commit main hand to Two Pair (faces synergize with Scary Face + Photograph). $5 left, shopadvise said LEAVE, endshop.
Small Blind (800): discard chain kept improving (Two Pair 98 -> Full House 99988 est 704) then closed with Pair Q est 360, scored 1064/800.
Shop (after Small Blind): bought Seed Money voucher ($10, economy) per shopadvise, $0 left, endshop.
Big Blind (1200): discarded a made pair chasing straight (EV-driven per advise) -> missed straight, landed Full House QQQJJ (est 1920) available but advise recommended TWOPAIR (est 1200, exactly meets need) using fewer cards (kept QD unplayed) -> followed advice, scored exactly 1200/1200 (est precise, deterministic).
Shop: $6, shopadvise said LEAVE (Hanging Chad $4 retrigger not worth it at this money level), endshop.
Boss The Hook (1600, forces discards): built Two Pair J8 (est 816), played it (816); pair-7 fallback est 172 played (988 total); final hand drew Two Pair FACE AK est 1224, played, final actual 2212/1600 (est understated actual here - Hook's forced-discard chip effect or card_chips undercounted, actual 2212 vs cumulative est 816+172+1224=2212, so est matched exactly, no discrepancy).
Jokers after ante 2: Scary Face, Odd Todd, Photograph (3/6). Levels: Two Pair L2. Money: ante 3 shop $12.

Ante 3 (blinds jumped to 2000/3000/4000, roughly 1.7x ante 2): Shop: $12, shopadvise said LEAVE (interest floor now $10 from Seed Money voucher; only tarots/Astronomer/Planet Merchant voucher offered, all would drop below floor) -- overrode nothing, endshop with $12.
Small Blind (2000): chased Two Pair through 3 discards (QT est 840 -> played), then drew AA KK JJ triple-pair, played Two Pair AK est 1224, total 2064/2000 (cleared, est matched actual exactly both times).
Shop: $18. Bought Clever Joker ($4, +80 chips if Two Pair - directly boosts main hand). Reordered jokers (order 1 2 4 3) to keep Photograph (xMult) rightmost. $14 left, shopadvise LEAVE, endshop.
Blind select: Big Blind carried a Rare Tag (skip-worthy per playbook with 2 free joker slots) but chose to PLAY rather than skip -- reasoned that skipping forfeits both the blind's cash income and the shop before the boss (The House, 4000 chips), which felt riskier than banking the tag. In hindsight this was a defensible but conservative call; see post-mortem.
Big Blind (3000): discard chain (pair -> pair -> flush C est 1560, played) then pair-5 filler est 164 (1724 total), last hand forced (0 discards, 1 hand left) into Two Pair 83 est 612 (best available, no flush/straight materialized - only 4 hearts, needed 5) -> final 2336/3000. BLIND LOST. GAME OVER.
Money at loss: $14 (unspent, but interest floor logic had kept it parked rather than converted to scaling).
Final jokers: Scary Face (+30 chips/face), Odd Todd (+31 chips/odd), Clever Joker (+80 chips if Two Pair), Photograph (x2 mult first face) -- 4/6 slots, no xMult beyond Photograph's single-card x2, Two Pair only ever reached L2 (40x3) despite 3 antes of shops.

## Post-mortem

Binding constraint: SCALING. Ante 3's Big Blind (3000) was roughly 1.7x ante 2's Big Blind (1200), but our Two Pair level never advanced past L2 (40x3) after the one Uranus pick in ante 2 -- no further Celestial pack or planet appeared/was bought in ante 3's two shops. Flat chip jokers (Scary Face, Odd Todd, Clever Joker) and one narrow xMult (Photograph, only x2 on ONE face card) could not keep pace with the chip-requirement curve once the flush/straight draws that had carried ante 1-2 stopped landing (both ante-3 flush chases came up exactly one card short).

Decision I would change: in the ante-3 shop after the Small Blind ($18, then $14 after Clever Joker), shopadvise said LEAVE twice in a row because the only offers (tarots, Riff-raff unknown-foil, Planet Merchant voucher, Standard/Spectral packs) would have dropped money below the new $10 interest floor. I followed that literally both times. With hindsight, taking the Riff-raff (foil, unknown effect, $8) or a pack for a chance at another scaling piece before a near-2x blind jump would have been worth dropping temporarily below the interest floor -- the floor logic optimizes long-run economy but ate the one window we had to add a 5th joker or a hand level before the wall we hit. I did not override shopadvise here despite the a3 chip jump being visible at blind-select; that is the mistake to flag.

Est vs actual: est matched actual on every scored hand this run, including the final loss (cumulative candidate ests summed to exactly the final scored total, 1560+164+612=2336). No case exceeded the 20% divergence threshold -- the CLI's est is deterministic/exact given the played cards, not merely directional.

Bridge issues: none. No `ACTION FAILED ... retry` messages, no Python errors, no connection issues over the entire run.

Playbook suggestions:
1. Add an explicit exception to the interest-floor rule: when the upcoming blind chip requirement is >= ~1.6x the previous blind of the same slot (visible at blind-select before the shop even happens, or via the boss/next-ante multiplier), allow spending below the interest floor for ANY scaling item (joker, pack, or unknown-effect card), not just xMult/main-hand-planet, since a lost blind ends the run regardless of banked interest.
2. When a main hand has not gained a level in an entire ante's shops (no Celestial pack or planet offered), the playbook should flag "no main-hand scaling this ante" explicitly as a warning ante-over-ante, since it's easy to focus on jokers/order/floor and forget the hand level stalled.
3. Confirm (from this run) that `est` in the CLI is exact/deterministic, not merely a probabilistic estimate -- future agents can treat "est >= need" as a hard guarantee once the hand is actually formed, no safety margin required.

