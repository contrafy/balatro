# Run SCSDWJWT (port 7802, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Fish (16820/50000)

Ante 1 (Skip/Rare/The Manacle 600, $4): Small: Straight 9-high 260 + 2P 5522. Shop $5: Blue Joker $5. Big: 2P JJTT 296 + spade Flush 632. Shop $5: Droll $4 (SIM 0.99 vs 0.60). Manacle: disc, Trips JJJ 432 + heart Flush 2114.
Ante 2 (Uncommon/Holo/The Window 2000, $7): EMERGENCY 0.22 -> Half Joker $5. Skipped Small (Uncommon tag = Sock and Buskin{PERISH,RENTAL}, passed). Big: Pair 22 2244 one-shot. Shop $8: Buffoon -> Joker Stencil{PERISH 5}; sold Droll (Stencil x3 -> x4). Window: Pair AA 9592 one-shot.
Ante 3 (Boss/Ethereal/The Eye->The Water 6400, $14): Skipped Small (Boss Tag rerolled The Eye -> The Water; saved a Stencil tick). Big: Pair 66 9680 one-shot. Shop $22: Jumbo Buffoon -> Onyx Agate (over rental/eternal junk). Water: wheel Straight A-5 with 3 clubs 10725 one-shot.
Ante 4 (Meteor/Skip/The Club 18000, $26): reroll (nothing), passed Arcana. Skipped Small (Meteor: Mercury, Pair L2; CLI sent Saturn instead of Venus, see defects) AND Big (Skip Tag +$20; Stencil kept for the boss). Club (Onyx dead): Pair AA 9315, disc 5, Pair 88 7935, Pair 66 -> 24k/18000. $41.
Ante 5 (Uncommon/Coupon/The Fish 50000, $51): EMERGENCY 0.34. 3 rerolls ($18) + Mercury (Pair L3) + 2 Arcana (Temperance +$11, Strength) + Sly{ETERNAL} $3: no xMult offered. Skipped Small (Uncommon). Big 37500 with Stencil's last round (sold Onyx -> x3): Pair TT 14256 + 33 12960 + 66 -> 40k. Stencil perished. Shop $34: Uncommon tag = Pareidolia{ETERNAL} (useless), 4 rerolls ($27) found no xMult, Swashbuckler{E} $4, 2 Standard (glass 8C, red-seal TC). Fish: ~5.5-6k per Pair hand, 16820/50000. GAME OVER.

## Post-mortem

Binding constraint: SCALING. In 24 joker offers + 6 pack picks over antes 1-5 (incl. 7 rerolls, $46) I was offered exactly one
xMult I could use: a PERISHABLE Joker Stencil. It carried antes 2-5 (x3-x4, every blind cleared 1.5-3x) and its death after
the ante-5 Big dropped my best hand from ~14k to ~5.5k against a 50000 boss. The only other xMult seen was The Order
{PERISH,RENTAL} (straight-only) and an Uncommon tag that rolled Pareidolia.

Decisions I would change:
1. Ante 3-4 shops: I banked $14-$26 for interest while 0 r/g xMult were owned, treating Stencil as the engine. With a
   perishable as the only multiplier, those shops should have bought Buffoon packs/rerolls one ante earlier (ante 4 first
   shop $26: one reroll only). The $51 I finally spent at ante 5 came too late to find anything.
2. Ante 4: skipping BOTH ante-4 blinds (Meteor + Skip Tag $20) kept Stencil alive for the boss but removed the Big's shop,
   i.e. 1 of only ~5 remaining shop views before Stencil died. With Stencil the Club boss was easy anyway (24k/18k), so
   the tick I saved bought nothing that a shop view could not.
3. Ante 5: skipping the Small for an Uncommon tag (Pareidolia{ETERNAL}) cost another shop view. A random-Uncommon tag is
   not an xMult; at ante 5 with no xMult, the Small's shop + interest was worth more.
4. Taking Joker Stencil itself was right (it won 4 antes); the error was not treating "my only multiplier is perishable" as
   EMERGENCY from the moment I got it.

Reusable rules (if-then):
- IF your only multiplier is Perishable (e.g. Stencil{PERISH}), THEN you are in EMERGENCY for xMult hunting from the next
  shop on, even when the SCORE CHECK says 2-4x: count only the scorers still alive at the boss after it perishes, and spend
  on Buffoon packs/rerolls before banking interest.
- IF you own Joker Stencil, THEN every slot you fill costs x1: sell flush/suit-only jokers (Droll, Onyx) while Stencil is
  live (Droll sold: x3 -> x4; Onyx sold before its last round: Pair 12.3k -> 14.3k).
- IF a perishable has N rounds left and the boss is the round after N, THEN skipping a blind keeps it alive for that boss
  (rounds tick only on played blinds): useful once, but each skip also removes a shop view; do it only when the shop could
  not have bought anything anyway.
- IF Half Joker is a core scorer, THEN Pair/Trips/High Card (<=3 cards) are the only hands; Two Pair/Full House/Flush lose
  +20 mult and score ~1/5. Level Mercury/Venus, not Uranus/Earth.
- IF The Water: a made 5-card hand on the deal that clears is fine (wheel Straight with 3 clubs one-shot 10725/6400).

Advisor/CLI defects:
- PACK INDEX REMAP BUG (Meteor Mega Celestial, choose 2): after picking Mercury, the state listed
  `1:Uranus 2:Mars 3:Saturn 4:Venus`; `pick 4` printed "(pack indices shifted since your listing: Saturn is now pick 3;
  sending pick 3)" and used SATURN (Straight) instead of Venus. The CLI remapped against the pre-pick listing, not the
  newest state it had just printed. Wasted a level.
- Stale pack cache: `pick N` in a NEW pack was REFUSED 4 times with "pick N was <card from a previous pack> ... no longer in
  the pack" (Mercury, Devious Joker, Strength, None); needed `advise`/`s` first each time.
- Pack `advise` for Arcana packs: "No pack advice for this pack type".
- shopadvise "main hand Flush" for ante 2-3 with Half Joker owned (Pair is the only Half-Joker hand); fixed itself after
  Pair plays.
- SIM next-3-blinds horizon hid the Stencil cliff: at ante 3/4 every option showed p 1.00 (+0.00) and ADVICE LEAVE, while
  the perishable xMult was going to die before the ante-5 boss. The SIM should model perish ticks.
- Uncommon Tag pays a random uncommon (Sock and Buskin{PERISH,RENTAL}, Pareidolia{ETERNAL}); `s` skip advice valued it as
  "a free joker", which at Gold is often a stickered dud.
Bridge issues: none; 88 steps, no rejects.
