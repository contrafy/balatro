# Run XRWKX6AS (port 7809, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind Small Blind (17727/60000)

Ante 1 (Rare/Coupon/The Hook 600, $4): Small 2P x3 (124+112+108). Shop $4: Buffoon -> Credit Card{PERISH} (override Blue Joker{ETERNAL,RENTAL} = -$69 unsellable), then on debt Raised Fist $5 + Swashbuckler{E} $4 (-$9). Big: 2P 9966 one-shot (est 750). Hook: 2P AATT one-shot (est 1054).
Ante 2 (Investment/Boss/The Fish 2000, $-3 -> $4): Banner $5 (-$1). Skipped Small for Investment ($25). Big: Straight A-5 1725 one-shot. Buffoon -> Even Steven. Fish: Pair 77 + low fillers holding KQJ for Fist, one-shot.
Ante 3 (Rare/Charm/The Mouth 6400, $33): Half Joker{PERISH} $5, Jumbo Celestial -> Mercury (Pair L2; override Earth). Passed Madness (SIM +0.22, destroys a scorer per blind). Skipped Small for Rare tag. Big: Pair KK 4410 + Pair 66. Shop: sold perished Credit Card, Rare tag = free Campfire; Arcana -> High Priestess (Venus+Saturn) sold both -> Campfire x1.5. Mouth: Pair 22 one-shot (est 6808). $30.
Ante 4 (Top-up/Boss/The Window 18000, $42): EMERGENCY 0.30. Found the CAMPFIRE FEED: buy any cheap card and sell it (+0.25 until the boss). Star/Venus/Lovers bought+sold, reroll x1, Arcana -> Strength (55 -> 66), Jumbo Celestial -> Mercury (Pair L3). Small: Trips 333 6385 + Pair 99 (x1.5). Big: High AH 5130 + Pair 88 8332 + Pair 77. Window: High QH 4856 + Pair 22 10192 + Pair 88 11368 = 26.4k/18000 (x1.75). $36.
Ante 5 (Investment/Juggle/The Plant 50000, $46): sold perished Half Joker, Neptune/Saturn, Spectral -> Medium (purple seal on 2C), RENTAL $1 jokers (Onyx, Lusty, Seance, Square) bought and sold back for $1 = +0.25 each at $0 net, Walkie/Shoot the Moon/Faceless bought+sold ($2-3 net each): Campfire x1 -> x3.5 over 2 shops. Small 25000: Pair 66 10080 + Pair 77 9690 + Straight A-high 10575. Bought Half Joker{PERISH,RENTAL} $1 (kept: +20 mult), ordered it left of Campfire (round est 32k -> 47k). Skipped Big for Juggle (+3 hand size at the boss). Plant: Pair 99 16933 + Pair 33 15953 + Pair 22 (+4D filler for Fist) 20020 = 52906/50000. $5.
Ante 6 (Juggle/Standard/The Wall 240000, $11): MISPLAY: accidentally sold Banner (step 117, a stray `sell 4` with a junk --why while I meant to only run `legal`); Banner was ~half of my chips. Mad Joker rental bought+sold (x1.5), Seltzer{PERISH} $6, Celestial -> Pluto. Small 60000 (projected ~21k): Flush C 7119 + Pair QQ 5040 + Pair 66 5568 = 17727. GAME OVER.

## Post-mortem

Binding constraint: scaling. Zero permanent xMult all run: 22 shop views (8 rerolls) showed no reliable/growth xMult
except the Rare-tag Campfire (and Madness twice). The build was flat (Raised Fist, Swashbuckler{E}, Banner, Even Steven,
Half Joker) at ~3.7k per Pair hand at x1, and Campfire fed by buy-and-sell carried antes 4-5 (x1.75 at the Window,
x3.5 at the Plant). Campfire resets after every boss, so each ante it costs a full wallet just to get back to x3-4, while
ante 6 needs x8+ on this base (Small 60k, The Wall 240k). The ante-6 wall was coming with or without the Banner mistake
(projected Small round 29k with Banner, 21k without).

Decisions I would change:
1. The accidental Banner sale: never chain a state-changing command into a read-only pipeline. Cost ~30% of every hand.
2. Ante 3: with $33 I bought Half Joker{PERISH} + Jumbo Celestial + Arcana; I should have kept ~$10 more and used the
   Mega Arcana / Buffoon slots for a permanent multiplier search earlier (one Buffoon pack at ante 3-4 instead of the
   Jumbo Celestial / Strength Arcana).
3. Ante 1: Credit Card -> Raised Fist + Swashbuckler{E} on debt worked (one-shot every ante-1/2 blind), keep that.

Reusable rules (if-then):
- IF you own Campfire, THEN every $1 RENTAL joker in the shop is +x0.25 for $0: buy it and sell it straight back
  ($1 sell value, no rent is charged inside the shop). Consumables ($3 buy, $1 sell) and $4-5 commons ($2 sell)
  are +x0.25 for $2-3 net. Feed in the FIRST shop of the ante: the xMult lasts for Small, Big and the boss.
- IF you own Campfire, THEN sell a perished joker, an unused planet/tarot, or a joker that adds nothing to the
  current hand (Banner at 0 discards, Even Steven on an odd pair) before the hand: each sale is +x0.25.
- IF Campfire is your only multiplier and the Big Blind tag is Juggle (+3 hand size) or Boss, THEN skip the Big and
  put all money into Campfire for one boss fight: Campfire does not reset on skips. (Plant 52906/50000 this way.)
- IF a +mult joker (Half Joker) sits right of your xMult, THEN `order` it left first: here round est 32k -> 47k.
- IF you own Raised Fist and Half Joker (<=3 cards), THEN play pair + your LOWEST card as the one filler: Fist then
  doubles the next-lowest held card (Pair 22 + 4D: 18564 -> 20020, cleared the Plant).
- IF a Buffoon pack offers an ETERNAL RENTAL joker at ante 1 (Blue Joker here, ranked 65 BUY), THEN take any other
  non-negative option: Credit Card let me buy two $4-5 scorers on credit the same shop.
- IF Campfire is the only xMult at ante 5 THEN plan for death at ante 6 unless a permanent xMult appears: the
  reset means each ante needs a fresh $30-40 just to reach x3.5.

Advisor/CLI defects:
- shopadvise/advise kept "main hand Two Pair" through ante 4 while every play since ante 3 was Pair (Half Joker,
  Mercury L3); advise twice suggested `play TWOPAIR` over a bigger Pair ("Two Pair is the hand you are leveling",
  e.g. Window last hand 2P 6545 vs Pair 88 11368). Mercury picks were flagged "NOT your main hand".
- shopadvise does not model Campfire feeding: it never suggested buy-and-sell of $1 rentals/consumables, and
  ranked Telescope/Seed Money vouchers above cheap sell fodder while EMERGENCY.
- shopadvise ADVICE "SELL FIRST: b sell 6" for Half Joker{PERISH,RENTAL} (as a "flat rental") although the same
  output's ORDER FIRST line showed it was +45% round est for the boss in the same ante.
- pack advise ranked Blue Joker{ETERNAL,RENTAL} (-$69 unsellable) as PICK at ante 1 (same defect as 7807 Raised Fist).
- SIM recommended Madness (p_next 0.41 vs 0.20) at ante 3 with 4 non-eternal scorers; it appears not to model the
  joker destruction.
- advise's pair line missed the better filler choice for Raised Fist (Pair 22 + 4D 20020 vs its 18564).
Bridge issues: none; 129 steps. One self-inflicted junk action (step 117 sell Banner).
