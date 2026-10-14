# Run Y9VLHVKS (port 7811, claude-sonnet-5-5) - Black Deck Gold Stake - LOSS at ante 5 boss The Wall (32966/100000)

Ante 1 (D6/Economy/The Hook 600, $4): Small FH 44455 248 + 2P 9922. Shop $5: Buffoon -> Mystic Summit (+15 mult at 0 discards; burn both discards every round, hands then est 800-1400). Big 2P QQ44 816. Hook flush 1368.
Ante 2 (Double/Holo/The Pillar 2000): Riff-raff $6 (gave Mad, Odd Todd, Business, Greedy, Gros Michel). Small Pair AA 1598 (2 cards for Pillar), Big flush 2603, Pillar 2P AA33 4988. Celestial -> Uranus.
Ante 3 (Garbage/Ethereal/The Needle 3200, $33): Buffoon pack -> Obelisk{E} (growth xMult), Acrobat{E} $6 (sold Greedy). Small High 5S 1525 + Trips 2771, Big FH 5913, Needle Pair QQ 4373 (Acrobat x3 on the single hand). Planets Mercury/Venus/Uranus x2/Neptune. Paint Brush $10.
Ante 4 (Coupon/Buffoon/The Flint 18000, $25): Skipped $0 Small for Coupon. Big FH TTT99 13200 + Trips 777 (13500). Coupon shop: Shoot the Moon $0 (+13 mult per Queen held), free Empress/7H mult+blue seal. Flint: Pair AA 16128 (QQQ held) + High 7H 7280 = 18k. Gros Michel died.
Ante 5 (Charm/Handy/The Wall 100000, $48): Hermit ($38 -> $55), Grabber (4 hands), planets (Pluto/Jupiter/Mercury/Venus/Jupiter), 4 rerolls found no counter, Lusty $5. Small: Straight AKQJT 11916 + Straight T-6 22968 (Obelisk x3). Big 37500: forced Obelisk reset (all non-reset types needed 5 cards I did not have), High junk digs, final Flush 29559 -> 38k (cleared by ~1.5%). Wall: FH 13288, Straight 7612, Pair 44 4147, Pair QQ 7920 = 32966/100000. LOST.

## Post-mortem

Binding constraint: scaling at ante 5 (Wall = 100000, my hands 8-14k, 1 xMult growth that I kept resetting). Final build: Summit + Odd Todd + Shoot the Moon + Lusty (flat) x Obelisk x Acrobat, hand 9, 4 hands. A "typical" non-final hand at ante 5 was 8-13k, so 4 hands + one x3 final = ~50k; the Wall needed 2x that. No Luchador/Chicot/Mr Bones/Director's Cut seen in 6 shop views.

Decisions I would change:
1. Obelisk bookkeeping: I let 4 hand types tie at 3 plays (Two Pair, Pair, Full House, High Card) by playing whatever scored most each blind (Two Pair, FH, Pair, High Card). From ante 4 on every play was either a reset or a hand that tied the max. At the ante-5 Big I had NO legal non-reset play (only Flush/Straight/Trips below max and none in hand) and had to drop Obelisk x3.2 -> x1, which cut that blind to a 1.5% margin. Rule: before each ante, list play counts and keep 2-3 types strictly below max that you can actually make; spend a reset deliberately on a cheap blind (Small).
2. Ante 4 Big: I played FH + Trips, filling counts to ties. A single Pair or High Card would have kept the budget.
3. Ante 5 shop: 4 rerolls ($29) bought Lusty only. I had 2 xMults but no third scaler; the Dusk{E,R} (retrigger final hand) at $1 would have added ~+40% on the Acrobat final hand and I passed it because of the eternal-rental rule. In a hopeless TIGHT spot (0.47x vs the boss) that rule should be off.
4. Gros Michel/Greedy/Business/Mad were all flat 1-slot jokers; no growth joker was found after Obelisk/Acrobat. Hologram/Constellation would have been needed.

Reusable rules (if-then):
- IF you own Obelisk THEN at the start of each blind write down counts per hand type; the safe plays are types with count < max (a tie at the top is fine, strictly greater resets). If every type you can make is at max, play the cheapest 1-card High Card FIRST in a Small blind to take the reset there, not in a Big/Boss.
- IF Mystic Summit is owned THEN burn both discards on junk every round (hands 3-5x bigger); keep made hands and discard everything else.
- IF Shoot the Moon is owned THEN keep Queens HELD and play non-Queen hands; each held Queen is +13 mult (a pair of aces with QQQ held = 16k at ante 4).
- IF a Coupon Tag is available on a $0 Small blind with 6 scorers THEN skip it: free Shoot the Moon + free Standard/Arcana packs came from it.
- IF the ante-5 boss is The Wall and you have no counter after 2 rerolls THEN spend the remaining money on Dusk/retrigger or xMult at any price; money left has no value.
- IF Obelisk is the only growth xMult THEN do not expect it to exceed x3 past ante 4 with 3-4 hands per blind; plan a second growth source (Hologram, Throwback skips).

Advisor/CLI defects:
- advise at ante 4 Big wanted to burn discards "keep [2,3]" while a FH/Trips was available; fine, but it never mentions Obelisk hand-count budget (the shopadvise OBELISK WARNING appears only in shops, not mid-hand when a reset is forced).
- hands/advise est for non-final hands excludes Acrobat but the FINAL hand est includes it; the 'need' comparison at the Wall used the same line, fine. SCORE CHECK said ~24.7k/hand vs 100k Wall: correct.
- shopadvise ranked Hallucination/Flash Card/Vagabond as BUY candidates at ante 5 TIGHT; none scores.
- Bridge: 142 actions, no rejects. Two 'pack 2' attempts after a pack disappeared were refused by the CLI (index shift), nothing sent.
