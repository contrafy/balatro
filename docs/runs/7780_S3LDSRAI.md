# Run S3LDSRAI (port 7780) - stake 3 (Green Stake)

Ante 1: Small Blind skipped (ADVICE: b skip, Investment Tag). Big Blind: Full House 666AA (320) + Flush clubs (248) = 568/450. Bought Buffoon Pack -> Scholar joker. The Hook (600): Flush hearts (288) + Full House TTT55 (320) = 608/600. Cashed out $37 (Investment Tag payout).
Ante 2: Shop: rerolled (no scorer), bought Joker+4mult ($2), Mega Celestial Pack -> Pair L2 + Two Pair L2 (Earth not offered), bought Telescope voucher ($10, guarantees main-hand planet in Celestial packs), bought Wily Joker ($4, +100 chips Trips, fires on Full House too). Jokers 3/6: Scholar, Joker, Wily.
  Small Blind (900): Flush diamonds (616) + Two Pair T3 (462) = 1078/900.
  Shop: 2x Celestial Pack (Jupiter x2) -> Flush L3. $0 after.
  Big Blind (1350, Orbital Tag Flush): Two Pair AT (1830, Scholar fired on 2 Aces) = 1830/1350 in one hand.
  Shop: bought Ride the Bus ($6, +1 mult per faceless hand, resets on face). Jokers 4/6.
  The Wheel (1800): Full House KKK99 (1504) + Two Pair JT (560) = 2064/1800. $0 cash before cash-out.
Ante 3: Shop after Wheel cash-out $6. Bought Jumbo Arcana Pack ($6) -> Justice, `sel 1` (JS) then Glass x2 applied to a Jack. $0 after. Jokers still 4/6: Scholar, Joker, Wily, Ride the Bus. No xMult joker owned, no rescue tarot held. Levels: Two Pair L2, Pair L2, Flush L3.
  Small Blind (2600): Full House 55599 (1557) + Two Pair KT (560) + Two Pair QQ88 (532) = 2649/2600 (1.9% margin, forced last hand).
  Shop: bought Celestial Pack ($4) -> Earth (Full House L2). $0 after, nothing else affordable.
  Big Blind (3900): Full House 77799 (1611) + Trips 444 (1278, Wily fired) + Pair AA (1566, Scholar fired on 2 Aces) = 4455/3900.
  Shop: $4. Bought Celestial Pack -> Earth again (Full House already L2, no change shown beyond level; see raw). $0 after.
  The Flint (5200, base chips/mult halved): Flush hearts (1212) + forced High Card (60, no pairable ranks, 0 discards left after 3 discards spent chasing the flush) + forced Flush diamonds (584) = 1869/5200. LOST.

RESULT: LOSS at ante 3, The Flint boss, 1869/5200 (36% of requirement).

Post-mortem: binding constraint = boss mechanic (The Flint halves base chips/mult) hitting a build with zero xMult and only L2-L3 hand levels. The build (Scholar/Joker+4mult/Wily/Ride the Bus, no xMult, Full House L2 / Flush L3 / Two Pair L2 / Pair L2) was clearing Small/Big Blinds comfortably (1.4x-1.9x) right up to the boss, then the halving cut effective output roughly in half exactly when three of the four hands drawn had no pair at all (High Card forced, no rescue tarot). The Small Blind clear at 2649/2600 was also uncomfortably close (1.9%) two antes before this loss, an early warning that flat scaling was falling behind the Green Stake curve.
  The one decision I would change: at the ante-3 shop after the Big Blind (had $4, bought a second Celestial Pack that only reinforced an already-L2 Full House) I should have held the money instead and used it plus the next shop's cash toward a rescue tarot (Death/Strength/Justice, $3) or an xMult joker per playbook 7b -- entering The Flint with zero xMult and zero rescue tarot left no way to recover from three consecutive weak/no-pair hands. shopadvise did not flag a rescue-tarot buy at this point even though the "no rescue tarot held" warning had already fired at the start of ante 3; I did not override shopadvise here because it kept directing to Celestial Packs and I had no concrete counter-reason at the time, but in hindsight the zero-xMult + zero-rescue-tarot state going into a halving boss was the decisive gap.

Bridge issues: one retryable `ACTION FAILED: Round eval blocking events still pending, retry shortly None` on `cash` after the ante-1 Hook clear; resolved with a single `sleep 2` + retry per the playbook. No other CLI errors.

Playbook suggestions:
  1. shopadvise should treat "no rescue tarot AND zero xMult joker AND next boss is The Flint/The Wall" as a hard override that ranks a $3 tarot buy or reroll-for-xMult above a second same-hand Celestial Pack, since a halving/doubling boss punishes an already-leveled hand far less than it punishes having no floor (High Card) fallback.
  2. Add The Flint to the explicit "arrive with a rescue tarot" boss list in section 7b/6 (currently only The Water/The Needle are called out for this) -- this run had zero pairs on 2 of 3 hands against The Flint and no consumable to fix a dead hand.
  3. Consider flagging in `advise` when a discard chase (we spent all 3 ante-3 Small-Blind... actually all 3 ante-1 discards chasing a flush earlier) leaves a later boss round with thin pair coverage; this run's deck by ante 3 skewed toward high, unpaired face/broadway cards after several flush chases, which is likely why 2 of 3 Flint hands had zero pairs.
