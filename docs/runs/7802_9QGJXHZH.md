# Run 9QGJXHZH (port 7802, claude-opus-5-5) - Black Deck Gold Stake - LOSS at ante 5 blind The Fish (15056/50000)

Ante 1 (Juggle/Holo/The Pillar 600, $4): Small: 2P KK99 116 + 2P TT88 + Trips 777. Shop $4: passed Hanging Chad{ETERNAL} (no mult), Buffoon -> Acrobat{RENTAL}. Big: 2 spare singles + spade Flush x3 = 936. Pillar: discard to 5 spades, spare 77 + AC, final Straight A-5 x3 660.
Ante 2 (Buffoon/Economy/The Window 2000, $3): skipped Small for Buffoon tag (Mega Buffoon): SOLD Acrobat{R} and took Joker Stencil{P,R} (x5) + foil Fortune Teller{E}. Big: 2P 8844 940 + 2P JJ33. Window: Straight 9-K 2580 one-shot.
Ante 3 (Juggle/Ethereal/The Manacle 6400, $10): Emperor $3 -> Fool (copied Emperor) + Judgement (Droll, sold) -> Emperor -> Lovers + Star: 6 tarots = Fortune Teller +6 mult (advisor ignores it). Small: used Star/Lovers, diamond Flush 6000 one-shot (est 2400). Shop: Uranus. Skipped Big (Ethereal; keeps Stencil alive for ante-4 Small): Wraith -> Brainstorm ($6 -> $0). Order Stencil, FT, Brainstorm (copies Stencil: x4 x4). Manacle: 2P TT22 8208 one-shot (est 5472).
Ante 4 (Buffoon/Standard/The Water 18000, $4): Arcana -> Star. Skipped Small (Mega Buffoon: Gros Michel + Seltzer sold for $3) and Big (Standard: purple-seal JH, red-seal QD) so Stencil's last round was The Water. Water: Pair 44 dig 5712 + Straight 9-K 13158 (est 10449). Stencil perished, Gros Michel went extinct.
Ante 5 (Meteor/Handy/The Fish 50000, $7): FT (10 tarots) + Brainstorm copying FT = +20 mult, no xMult. Arcana -> Temperance (+$9), reroll -> Emperor + Fool. Best hand ~4-8k vs Small 25000: skipped Small (Mega Celestial: Jupiter, Venus) and Big (Handy, $20 with no shop). Fish: Death/Emperor/Hanged Man/Hierophant/Strength, Flush 8398 + 2P 4290 + Pair 2368 = 15056/50000.

## Post-mortem

Binding constraint: scaling. I never owned a permanent xMult. Joker Stencil{PERISHABLE,RENTAL} (x5, then x4/x3 copied by
Brainstorm = x9-x16) carried antes 2-4 for its 5 rounds, and three skips stretched it over 6 blinds. Once it perished, the
permanent build was foil Fortune Teller{ETERNAL} plus Brainstorm (about +20 flat mult), roughly 4k per hand against an
ante 5 that needs 8-17k per hand. Money stayed at $0-7 the whole run (Acrobat rent at ante 1, Stencil rent, Wraith set it
to $0), so I saw only one reroll and never had $6-8 spare for a shop xMult.

Decisions I would change:
1. Ante 3 Ethereal pack: Wraith ($6 -> $0) rolled Brainstorm, which only copies; the run needed a base xMult more than a
   copier. Keeping $6 and playing the Big ($5 + a shop) would have given 2 extra shop views at ante 3-4 to find an xMult.
   Brainstorm doubled Stencil for 2 rounds, then only doubled Fortune Teller's flat mult.
2. Ante 4: skipping the Small and Big kept Stencil for The Water, but it also cost 2 shops and their income. With $0-4 that
   was right for surviving ante 4, but it also meant I reached ante 5 with no xMult and no shop money. The real error came
   earlier: not building any money at ante 2-3.
3. Ante 3 first shop: I spent $3 on Uranus. I should have kept it so the next shop reached $9+ for an xMult.

Reusable rules (if-then):
- IF you own Fortune Teller, THEN every tarot you use is +1 mult forever (Brainstorm/Blueprint copying it doubles that).
  The Emperor ($3) is +3 tarots, and The Fool right after The Emperor copies it (+3 more). Use Star/Lovers/etc. on junk
  cards just for the count. `est` ignores Fortune Teller completely (logged: 2400 vs 6000, 5472 vs 8208, 390 vs 4290).
- IF Joker Stencil is the only xMult and Brainstorm/Blueprint is owned, THEN put Stencil leftmost (Brainstorm copies it:
  x4 x4) and the flat +mult jokers between them. Every joker you add costs it x1, twice over.
- IF a perishable xMult carrier has 1-2 rounds left and a skip tag pays now (Buffoon/Ethereal/Standard), THEN skipping
  Small/Big makes its last round the boss. This works for one ante. It does not replace finding a permanent xMult, so
  the shops you still visit must buy the xMult first.
- IF you have <= $6 at ante 3 with 0 permanent xMult, THEN Wraith gambles the money you need for the next xMult. Only
  take it when the rare pool's copiers (Blueprint/Brainstorm) would also have something to copy.

Advisor/CLI defects:
- Fortune Teller's mult (tarots used, in `run.consumeable_usage_total.tarot`) is missing from `hands`/`advise`/`sel` est,
  SIM and SCORE CHECK. Every recommendation from ante 3 was based on ests 30-90% low. At ante 5 Brainstorm copying
  Fortune Teller was also dropped (est 390, actual 4290).
- `legal` index/name mismatch: with cons [1] Hanged Man, [2] Hierophant, `use 2 2 3` was refused and the legal form said
  "index: one of 1 (The Hierophant)".
- The ante-5 blind-select advice said "do not skip" while also saying the best round reaches under half of the Small. With
  no way to win the blind, the skip (tag) is strictly better.
