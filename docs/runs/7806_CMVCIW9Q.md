# Run CMVCIW9Q (port 7806, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 6 blind The Pillar (31266/120000)

Ante 1 (Rare/Juggle/The Club 600, $4): Small: dig High A (solver) then spade Flush 312. Shop $5: Raised Fist{ETERNAL} $5 (only scorer, SIM 0.99). Big: Pair 99 + low fillers (lowest held T -> +20) 616 one-shot. Passed Celestial ($6 kept). Club: Pair AA 640 one-shot.
Ante 2 (Foil/Skip/The Arm 2000, $14): EMERGENCY 0.34; rerolled past eternal Splash -> Banner $5. Played Small (wheel Straight 1610). Jumbo Celestial -> Mercury (SIM +0.13). Swashbuckler{PERISH,RENTAL} $1 (SIM +0.32). Big: Pair 1339 + Pair. Arm: Pair 44 2028 one-shot (Pair L2 -> L1).
Ante 3 (Investment/Rare/The Window 6400, $8): sold Swashbuckler, bought Joker Stencil{ETERNAL,RENTAL} $1 (score check 0.35 -> 1.12, SIM 0.09 -> 0.99; x4 with 3 empty slots). Skipped Small (Investment) and Big (Rare). Window: Pair 44 5920 + Pair 99.
Ante 4 (Coupon/Rare/The Eye 18000, $37): Rare tag -> The Duo{PERISH,RENTAL} $0 (Stencil x3, net x1.5), Mercury (Pair L2), 2 rerolls nothing. Skipped Small (Coupon). Big: 2P QQ33 12720 + Pair AA. Coupon shop: Celestial -> Mercury (L3), Jumbo Standard -> Mult JH, reroll -> Uranus. Eye: 2P 6655 8052, Pair 44 11664. $11.
Ante 5 (Holo/Economy/The Tooth 50000, $19): EMERGENCY 0.25. Spectral -> Familiar (Hex would have destroyed Banner), Arcana -> High Priestess (Venus+Earth used). Skipped Small (Holo) and Big (Economy $11 -> $22). Tooth: Pair 88 15312, Trips JJJ (glass) 28560, Trips AAA 16302 -> ~60k/50000. Rent+cards left $4.
Ante 6 (Uncommon/Orbital/The Pillar 120000, $9): free holo Seltzer (Holo tag), Jumbo Spectral -> Wraith = Driver's License (dead, sold $3). Skipped Small and Big (Orbital: Quads L4). Pillar: kept JJJ and dug twice for the 4th Jack (solver 0.44 -> 0.22), never came; Trips 19800. 31266/120000. LOSS.

## Post-mortem

Binding constraint: SCALING. The run never owned a growing or reliable xMult. Its multiplier was Joker Stencil (eternal
rental) x Duo (perishable rental), and the Stencil made every new joker a net loss, so the row stayed at 4-5 jokers with
~+20 mult (Raised Fist) and +60 chips (Banner). Typical hand: ~2k at ante 2, ~7k at ante 3-4, ~12-15k at ante 5-6 vs
40k per hand needed at the ante-6 boss. The two eternals (Raised Fist from ante 1, Stencil from ante 3) were each correct
for survival at the moment (SIM 0.99 vs 0.01; 0.99 vs 0.09) but together they capped the build.

Decisions I would change:
1. Ante 5 shop ($19): Spectral + Arcana ($8) returned Familiar and two off-type planets. With the Stencil build the only
   slot-free scaling is Pair levels; I would have bought the Jumbo Celestial in ante 6 and kept the ante-5 money for one
   reroll + a $3 Mercury, not two gamble packs.
2. Ante 6: Wraith with 5/6 slots under Joker Stencil: any rare that is not a big xMult is a loss (it fills the slot that
   Stencil counts). Driver's License was dead. Should have taken nothing or Cryptid on a Jack.
3. Ante 2: buying the Jumbo Celestial to $0 (SIM +0.13) then the Swashbuckler rental cost the interest and pushed me
   into the Stencil emergency at ante 3; a bigger cash pile at ante 3 would have afforded a real xMult if offered.

Reusable rules (if-then):
- IF you own Raised Fist, THEN play your LOW cards as fillers and keep your highest cards held: lowest held T/9 gave
  +18-20 mult every hand (advise does this; the candidate list est ignores it, the play line is right).
- IF you buy Joker Stencil, THEN the build is frozen at its current joker count: only planets, card enhancements and
  edition/negative jokers scale it. Plan the Celestial money for it, and do not open Wraith/Buffoon packs with a slot
  you cannot afford to fill.
- IF the ante-5/6 Small and Big are each > 2.5x your typical hand AND you lack Throwback, THEN skipping both is still right
  (saves $6 rent per round, keeps perishables alive, no Pillar debuffs, Economy tag doubled $11 -> $22) but it is not
  a plan: no shop visit between, so the boss is fought with exactly the build you leave ante N-1 with.
- IF The Eye is the boss, THEN play the rarer pair-family type first (Two Pair) and keep Pair for the last hand
  (8052 + 11664 cleared 18000).
- IF you chase quads under a 120k boss with 3 Jacks, THEN dig with full 5-card plays (more draws); expect it to miss
  more often than the solver's p suggests (0.44 -> 0.22 -> 0).

Advisor/CLI defects:
- `advise` candidate est ignores Raised Fist fillers: "PAIR 9 est 1133" while the play line printed 1339; Window "PAIR 4
  est 3552" vs play line 5920. The ADVICE commands themselves picked the right fillers.
- Pack advice: Spectral advisor ranked Wraith first (75) with 5/6 slots under Joker Stencil; the random rare fills the
  slot Stencil counts (x2 -> x1), and Driver's License came out dead. Wraith should be penalised when Stencil is owned.
- Standard pack: `advise` prints "No pack advice for this pack type"; `pick 1` echoed "(pick 1 = None in the current pack
  listing)" although JH(mult) was taken correctly.
- Familiar/Grim give no listing of the cards they added (deck count changed 53 -> 55 silently).
- Solver at the Pillar: p 0.40/0.44 for the Jack-quads chase at the start, ended 31k/120k; it looks overconfident on
  set-draw lines when the made hand is far below need.
- `s` at ante 5-6 blind select always says "do not skip: the shop after the Small Blind is worth more than a tag" even
  when money is $3 and the Small is 4x the typical hand.
