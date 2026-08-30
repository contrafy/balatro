# Run TED2VFEK (port 7780) - LOSS at ante 2 Big Blind

Stake 1 (White), Black Deck. Boss ante 1: The Psychic (exactly 5 cards).

Ante 1: Buffoon pack -> Credit Card (Crafty Joker was the only other option, both non-priority). Small Blind (300):
Full House 44455 est248/act248, Pair T est60/act60 -> won 308. Big Blind (450): Two Pair est112/act112,
Straight K-high est316/act316, Pair 5 est40/act40 -> won 468. Shop: Celestial Pack -> Earth (Full House L2);
no Mercury (Pair) offered, advisor flagged this as a partial-waste level since "main hand" was tagged Pair, but
Full House is also pair-family so kept it. Boss The Psychic (5-card hands): Flush C est248/act248, Straight
J-high est296/act296, Straight 5-high est220/act220 -> won 764 (need 600). Jokers after ante1: Credit Card.
Ante 2 shop: bought Wily Joker $4 (+100 chips if Three of a Kind) OVERRIDING shopadvise's REROLL suggestion -
Wily is explicitly named in the playbook's ante1-2 priority joker list and fires on Full House too (which
contains a Three of a Kind), fitting the pair-family build; advisor didn't recognize it as "scoring" because
main-hand tag was Straight, not pair-family. $5 left, nothing else worth buying, endshop.
Boss ante 2: The Needle (1 hand only) - never reached it.

Ante 2 Small Blind (800): Two Pair FaceK3 est92/act - discarded twice per advise chasing bigger pair, then drew
KKK 333 (Full House) on the forced 0-discard hand: Full House KKK33 est1206/act1206 -> won in 1 hand (need 800).
Shop ($11): OVERRODE shopadvise's REROLL suggestion (playbook rule: "Do NOT reroll in ante 1-2 unless you have
>= $10 after the reroll"; reroll would have left only $6). Nothing else worth buying (Temperance tarot, Jupiter
planet for Flush - not our family) -> endshop, kept $11.

Ante 2 Big Blind (1200): drew AH KH 9D 5S 5H 4C 3C 2H, chased a heart flush per advise across all 3 discards
(disc 2 3 7 / disc 2 3 5 / disc 3) while holding the A2345 straight as a floor; flush never completed (stuck at
4 hearts). Forced hand 1 (no discards left): Straight 5-high est220/act220 (need 1200, 980 short).
Forced hand 2: Pair T est60/act60 (scored 280 total, 920 short, 1 hand left).
Forced hand 3 (last hand, no rescue consumable held - both consumable slots were empty all game, no tarot/
planet pack ever bought after ante 1's Buffoon/Celestial picks): Two Pair AJ est124/act124. Final scored 404
vs need 1200. LOSS.

Post-mortem: Binding constraint was SCALING, not luck of this one hand - by the Big Blind of ante 2 we had
only Full House L2 (65x6) and one conditional joker (Wily, +100 chips on Three of a Kind, useless on a Pair/
Two Pair/Straight hand and never triggered once all game since we never scored a bare Three of a Kind). We had
zero card-targeting tarots and zero consumables in reserve for a rescue (playbook 4.8), and zero flat +mult
joker - only Credit Card (economy, no scoring effect) and Wily (conditional, never fired). A Big Blind of 1200
with a L2 Full House (max ~370) and no generic +mult support was never going to clear in 3 hands once the
straight/flush chase didn't pan out.
  Decision I would change: at the ante-2 shop after the Small Blind (11 dollars, shop had Temperance tarot,
Jupiter planet, Grabber voucher, two Celestial packs), I ended the shop per shopadvise's implicit "nothing
better" read and playbook's reroll-money-floor rule, but I should have bought Temperance ($3, a tarot - even
though not card-targeting, it's a consumable that fills a slot) or, better, treated the two back-to-back
0-joker/0-tarot shops (ante1 rnd2 and ante2 rnd3-4) as a signal to actively hunt: with only Wily (conditional)
and Credit Card (non-scoring) after 2 full shops, the playbook's "TWO scoring jokers by end of ante 2" target
was already missed after just one shop cycle, and nothing in the routine forced a reroll-until-found once
money allowed it later. Concretely: I would reroll ante 2's second shop ($11, well above the $10 floor) to
hunt for a second flat +mult/+chips joker instead of ending it with a leveled hand but no support.
Bridge issues: none - every CLI command returned cleanly, all `est` values matched actual scored values
exactly (0% deviation on every hand played this run, including the two Full Houses, three Straights, one
Flush, and Two Pairs/Pairs). No ACTION FAILED or retry-worthy errors encountered.
Playbook suggestions:
  1. shopadvise's "main hand" detection lagged behind actual play (tagged "Straight" or "Pair" late in ante 2
     even after two Full Houses were played and leveled) which caused it to mislabel Wily Joker as
     non-scoring and recommend REROLL even when Wily fit the already-leveled Full House family. Consider
     having shopadvise weight the leveled hand (Levels: line) over most-recently-played hand when picking
     "main hand".
  2. Add an explicit rule: if 2 consecutive shops pass with fewer than 2 scoring (+mult/+chips on ordinary
     hands) jokers owned, and money is >= $10, reroll that shop specifically to hunt for one rather than
     ending it - being "not below the reroll floor" isn't sufcient; being behind on the ante-2 joker target
     should trigger an active hunt.
  3. Empty consumable slots for an entire run (this run had 2 free cons_slots unused start to finish) is a
     wasted resource; playbook 7a's "RESCUE TAROT" rule only kicks in "from ante 3 on" - consider extending it
     to ante 2 boss/Big Blind fights too, since a single Justice/Strength/Death would have turned this Two
     Pair AJ into a much bigger scoring hand on the final forced draw.
