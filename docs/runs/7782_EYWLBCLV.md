# Run EYWLBCLV (port 7782) - LOSS at ante 1 boss (The Club), stake 3 (Green Stake)

Started after stake 2 was beaten by another player (target moved to stake 3 mid stake-2 run at ante 5 shop;
that run, 7782_TPK84L2A.md, was abandoned undefeated).

Ante 1: Small Blind tag=Voucher (skip per advice, $0 anyway). Big=Polychrome tag. Boss=The Club.
  Big Blind (450): Straight 7-high 240, Flush C 272 (est 272 actual 272). Total 512/450, cleared 1 hand+2 disc spare.
  Cash $9. Shop: no scoring joker offered (Brainstorm/vouchers $10 too pricey at 0 jokers); Buffoon Pack $4 -> forced
  choice Diet Cola vs Gift Card (neither scores) -> picked Gift Card (economy, +$1 sell value/round) since we had $0
  scoring jokers and no affordable alternative; endshop with $5 per shopadvise LEAVE (nothing else affordable).
  Boss The Club (600, debuffs Clubs): discarded debuffed clubs each hand, chased Straight then fell back to made
  Full House/Trips/Two Pair floors with fillers as debuffs kept eating the good suit. Full House TTT88 est/actual 344,
  Trips 4 (debuffed 4C in it) est 114 actual 114 (last card debuffed scored 0, notes flagged it), final forced hand
  Two Pair KJ (debuffed KC in it) est 100 actual 100. Total 558/600 -- LOST by 42 chips, 0 hands/0 discards left,
  no consumables held (never got $3 spare for a rescue tarot this run).

LOSS at ante 1, The Club boss, 558/600 (short by 42 chips).

Post-mortem: binding constraint was the joker draw + The Club's suit debuff compounding on a 0-joker Black Deck
hand. We entered the boss with only Gift Card (a non-scoring economy joker, forced pick from a Buffoon pack that
offered no scoring joker at all) and zero levels. The Club repeatedly debuffed 2-3 of our best cards per hand
(Clubs are common: 8/52 in Black Deck's composition seen this run), which combined with 0 discards left after the
opening double-discard gamble meant the last 3 hands were forced plays with no way to rebuild. The single decision
I would change: on the very first hand of The Club, I burned 2 of 3 discards chasing value around debuffed clubs
before locking in a Full House; with a 0-scoring-joker hand at ante 1 stake 3 (blinds scale faster than stake 2),
I should have taken the safer, sooner Full House on the first or second hand instead of drawing further, to bank
more raw chips before the debuff attrition made every subsequent hand weaker. A secondary factor: the Buffoon pack
forced a choice between two non-scoring jokers (Diet Cola, Gift Card) -- with 0 scoring jokers already and a Club
boss two blinds away, `shopadvise`/the pack-forced-pick rule doesn't have a lever to avoid this; nothing wrong with
the pick itself, but it meant we fought the whole ante 1 boss with zero joker support, which stake 3's faster
scaling punishes harder than stake 2 did.
Bridge issues: none. All actions succeeded on the first try this run; no ACTION FAILED / retry errors encountered.
Playbook suggestions:
  1. Stake 3+ (faster scaling): when a Buffoon/Arcana pack forced pick offers zero scoring jokers AND the upcoming
     boss debuffs a suit/hand-type, prefer banking the made hand on hand 1-2 over chasing a bigger one -- raw
     chips banked early survive suit-debuff attrition better than a bigger hand chased with fewer discards left.
  2. Consider flagging in shopadvise when ante 1 ends with $0 scoring jokers and the boss is a suit-debuff type
     (Club/Goad/Window/Head): this is a materially higher-risk combination than a non-debuff boss and the current
     ADVICE lines don't distinguish it.
