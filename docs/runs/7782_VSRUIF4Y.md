# Run VSRUIF4Y (port 7782)

Boss for ante 6 is The Club (seen at ante-1 blind select as upcoming... will confirm each ante). Black Deck, stake 1.

Ante 1: jokers [Even Steven, Jolly Joker], $1 (pre-boss), Full House L2. Small Blind: TwoPair T7 est108/actual108, Flush C est308/actual416 (34% over). Big Blind: TwoPair 62(even) est648/actual648. Shop: overrode shopadvise ante-1 buy (The Order, x3mult-if-Straight, off pair-family strategy) -> Jumbo Buffoon Pack -> Even Steven; then bought Jolly Joker + Celestial Pack(Earth->FullHouse L2). Boss ante1: The Club (suit debuffed).
Ante 1 boss The Club (clubs debuffed): TwoPair 5-2 est612/actual612 -> cleared 600. Ante 1 WON. Upcoming boss ante2: The Flint (half base chips/mult).
Ante 2: TwoPair L2 leveled (Uranus). Small: TwoPair JT est1080/actual1080. Big: Pair8 est468/actual468(reg for pacing), TwoPair QT est1520/actual1988(31% over). Shop overrides: skipped Bloodstone(Heart-suit conditional xMult) for Arcana Pack->Justice(Glass on a 5); skipped Swashbuckler (shopadvise itself tagged AVOID yet recommended buy - contradiction) for Jumbo Arcana Pack->Death (converted a T into a copy of J, building 3xJ toward Full House with AA pair). Boss ante2: The Flint (half base chips/mult).
Ante 3: overrode shopadvise buy of The Tribe (x2mult-if-Flush, off pair-family strategy) -> Jumbo Celestial Pack (Uranus, TwoPair L3); bought Constellation (reliable growth xMult, feeds off planets we buy anyway) over another Celestial pack in shop 2; bought another Celestial pack (Uranus->TwoPair L4) in shop3, feeding Constellation to x1.1. Small: FullHouse TTT33 est2626/actual2626. Big: overrode advise's straight-chase (discarded toward keeping Pair-8 for Jolly Joker synergy per playbook's pair-preference override rule) -> built FullHouse 88822 est3162/actual3162. Money tight all ante (never above $8 pre-shop). Boss ante3: The Tooth (-$1/card played, need 4000) - the boss that ended the previous run's run at ante 6; will minimize cards played this hand.

Ante 3 boss The Tooth (need 4000, -$1/card played, entered with only $1): overrode advise's straight-chase discards twice to protect existing pairs (per playbook pair-preference rule); played trip/quad hands with minimal cards (3 instead of 5-card filler) to limit Tooth's per-card cost. Hand1 QUADS-5 est1936/actual1936 (cum 1936). Hand2 TRIPS-K(3 cards only) est726/actual726 (cum 2662). Final hand forced (0 discards left): drew TRIPS-7 est617/actual617 (cum 3279) vs need 4000 -> LOST, run over. Final money $-9 (Tooth debt from ~10 cards played across the round while money floor was already ~$1).

# Run VSRUIF4Y (port 7782) - FINAL RESULT: LOSS at ante 3, Boss blind (The Tooth), stake 1 (White)

Best result: stake 1, ante 3, boss blind The Tooth. Scored 3279 / needed 4000 (82%).
Jokers at loss: Even Steven (+4 mult/even card), Jolly Joker (+8 mult if Pair), Constellation (xMult grows +0.1/planet, only reached x1.1).
Levels at loss: Full House L2 (65x6), Two Pair L4 (80x5).
Money curve: ante1 start $4 -> spent to ~$1-2 every shop; ante2 similar ($8->$1-2 each shop); ante3 same pattern ($7-8->$1 each shop); never banked money, never reached even $10, so interest (playbook target $25 by ante4) was never in play. Boss (The Tooth) then drove money to $-9 from playing ~10 scoring cards across 3 hands starting from a $1 floor.

Post-mortem:
Binding constraint: SCALING, not luck or misplay. We split hand-level investment between Two Pair (leveled 3x to L4) and Full House (leveled 1x to L2), but Full House was consistently our highest-scoring made hand (2626, 3162 vs Two Pair's 1080-1988). Only one xMult joker (Constellation) was ever found, bought in the very last shop of ante 3 and barely fed (x1.1) before the boss. Flat mult jokers (Jolly +8, Even Steven +4/even) were not enough combined with weak xMult to clear a boss that doubled the Big Blind requirement (3000->4000).

Decision I would change: consolidate hand-level purchases into ONE main hand (Full House, since it scored highest every time it appeared) instead of splitting 3 Celestial-pack levels into Two Pair. A Full House at L4-L5 (per playbook table: L5 140x12) would very likely have cleared 4000 where our L2 Full House (65x6, actual best hit 3162) fell short by 721.

Bridge/CLI issues: none. Every action succeeded on the first try; no ACTION FAILED, no retries needed, no Connection refused.

est vs actual divergence >20%: two cases, both in our favor (actual higher than est), no cause for concern but noting per instructions:
- Ante1 Small Blind Flush: est 308, actual 416 (+35%).
- Ante2 Big Blind TwoPair QT: est 1520, actual 1988 (+31%).
All other hands matched est almost exactly (within a few chips).

Playbook suggestions:
1. When multiple hand types are viable scoring hands (e.g. both Two Pair and Full House show up often), the shop advisor should identify which ONE has scored highest historically this run and bias Celestial-pack picks toward leveling that single hand, rather than leaving the choice generic ("take Uranus if offered") when a higher-scoring hand's planet (Earth for Full House) is also on offer alongside Uranus.
2. shopadvise recommended buying jokers it had itself flagged AVOID (Swashbuckler: "AVOID(useless as the only joker)" yet ADVICE line said buy) and jokers whose condition explicitly requires an off-strategy hand type (The Order needs Straight, The Tribe needs Flush, Bloodstone needs Hearts) despite the pair-family directive — the advisor's top-line numeric ADVICE should suppress or down-rank items it has already tagged AVOID or that require a hand type outside the run's declared main-hand family.
3. Consider flagging in shopadvise when a run has spent every shop down to under $3 for 3+ consecutive shops (as happened here every single shop across 3 antes) — this "never banks money" pattern directly explains scaling shortfalls at boss blinds and could be an explicit warning line distinct from the "under-scaled" note.
