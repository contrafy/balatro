# Balatro Agent Playbook (Black Deck, Gold Stake)

Curated learnings for agents playing through the RL bridge. Read fully before every run.
Append your post-mortem to `docs/runs/` (section 9) so the next run improves.

## 0. Ground rules

- INFRASTRUCTURE IS OFF LIMITS: never run git commands, never kill/restart/launch any process, never edit any file
  outside docs/runs/. Several agents share this machine; one agent's "restart" killed every game at once and a
  `git checkout` erased hours of harness work. If the bridge is unreachable for 2 minutes, write your log and stop.
- EVERY ACTION IS TRAINING DATA. The bridge records each action you send (with the state it was taken in and your
  `--why`) into a trajectory that later trains models. So: no exploratory or "let's see what happens" actions, no
  testing commands, no junk retries. Read-only commands are free and unrecorded: `s`, `hands`, `advise`, `shopadvise`,
  `legal`, `raw`, `sel`, `help`. Use them as much as you like before committing to an action.
- `--why "..."` IS REQUIRED on every state-changing command: one line, at most 300 characters, the concrete reason
  (numbers, not vibes): `b 7778 play PAIR 2 5 1 3 4 --why "Pair of Kings + 3 fillers, est 340 vs 300 needed"`. The CLI
  refuses the command (nothing is sent) without it. `ADVICE:` lines print the command without `--why`; add your own.
- The CLI checks every action against the game's legal actions BEFORE sending. `NOT LEGAL NOW ... Nothing was sent`
  means the action is not allowed in this state; it prints the legal forms (e.g. which consumables are usable and how
  many targets they take). Fix the command; do not retry the same thing.
- The bridge itself also rejects illegal actions and actions sent while the game is still animating. The CLI waits for
  the game to settle before reading or acting and retries "not settled" responses itself. `ACTION REJECTED: ...`
  means the bridge refused it (recorded as a reject): read the error and the printed state, then act again correctly.
  `BRIDGE OFFLINE ... Connection refused` is not retryable: stop and report.
- LOSING ANY BLIND ENDS THE RUN. There is no "lose this one to save money". Every blind must be beaten.
- You control ONE game instance through the wrapper you were given: `bash python/balatro_env/scripts/b.sh <port> <cmd>`
  (Git Bash; PowerShell: `python\balatro_env\scripts\b.ps1 <port> <cmd>`). This playbook writes it as `b <cmd>`. Never
  touch other ports, never restart the game, never edit harness files. If the bridge misbehaves, note it in your run log.
- Every CLI action prints the new (settled) state. Read it before the next command. Card indices are 1-based, left to
  right, and change after every play/discard/sort/move, so always use indices from the most recent printout.

## 1. CLI reference (`b <cmd>`; `[W]` = state-changing, needs `--why "..."`)

| Command | Effect |
|---|---|
| `s` | print state + legal action types |
| `hands` | list every poker hand you can make now, with card indices and `est` = estimated score INCLUDING your jokers. Also prints `need N more this blind`. Run it before every play/discard. |
| `advise` / `shopadvise` | hand / shop advisor with an `ADVICE:` line |
| `sel i j ...` | PREVIEW only: the game's reading of those cards (hand type, scoring cards, base level) plus `est`. Selects nothing, sends nothing. |
| `legal` | every legal action with its exact parameter domain (valid indices, target counts, costs) |
| `raw` / `help` | raw state JSON / command list |
| `[W] play TYPE i j k ...` | play cards as TYPE (PAIR, TWOPAIR, TRIPS, STRAIGHT, FLUSH, FULLHOUSE, QUADS, HIGH, ...). The CLI checks the game's own reading of the cards and ABORTS (nothing sent) if they do not form TYPE. Always use this form. |
| `[W] disc i j ...` | discard those cards (1 up to the discard limit, normally 5) |
| `[W] blind` / `[W] skip` | select / skip the blind on deck (the Boss can't be skipped) |
| `[W] rerollboss` | reroll the Boss blind (only with Director's Cut / Retcon) |
| `[W] cash` | cash out after a won blind |
| `[W] buy N` / `[W] vouch N` / `[W] pack N` | buy shop card slot N / voucher N / booster pack N |
| `[W] buyuse N` | buy shop consumable N and use it immediately (works with full consumable slots) |
| `[W] pick N [t1 t2 ...]` / `[W] skippack` | take card N from an open pack, with target hand cards for targeting tarots/spectrals / skip the pack |
| `[W] use N [t1 t2 ...]` | use consumable N; targeting tarots/spectrals take the target hand positions after N (e.g. `use 1 3 6`) |
| `[W] sellc N` / `[W] sell N` | sell consumable N / joker N. Works whenever the game allows it: shop, blind select, mid-round, cash-out screen and with a pack open. Eternal jokers can't be sold. |
| `[W] order [jokers\|hand\|cons] p1 p2 ...` | reorder an area: list the CURRENT positions in the new left-to-right order (area defaults to jokers) |
| `[W] move jokers\|hand\|cons FROM TO` | move one card from position FROM to position TO |
| `[W] sort rank` / `[W] sort suit` | sort hand (indices change) |
| `[W] reroll` / `[W] endshop` | reroll shop ($5, +1 each time) / leave shop |
| `[W] start <deck> <stake> [--seed S]` | start a new run (from MENU, GAME_OVER or the win screen), e.g. `start Black Deck 2 --seed 7K3P9QXA`. Use the seed you were assigned. |

Targets: a targeting consumable accepts 1 up to its maximum number of cards (Death exactly 2), not only the maximum:
Star/Moon/Sun/World up to 3, Magician/Empress/Hierophant/Strength/Hanged Man up to 2, Lovers/Chariot/Justice/Devil/
Tower and the targeting spectrals exactly 1. `legal` shows the exact range for each usable consumable right now.

State line: `[PHASE] ante A rnd R | $money | hands H disc D | blind NAME need X scored Y`.
`Jokers (n/6)` lists each joker with a plain-English effect in parentheses. `Levels:` shows leveled hands.
Ignore `ab={...}` internals: `x_mult: 1` just means "no xMult stored", it does not mean the joker is useless.

## 2. Phase loop

1. `BLIND_SELECT`: read the three blinds (chips, skip tags, boss). Default is `blind` (play). Skip only per section 6.
2. `SELECTING_HAND`: `advise`/`hands`, then decide per section 4, then `play TYPE ... --why` or `disc ... --why`. Repeat
   until `ROUND_EVAL`. Hand order matters for scoring (left to right) and for Death: use `move hand FROM TO` if needed.
3. `ROUND_EVAL`: `cash --why "..."`.
4. `SHOP`: follow section 5 step by step, then `endshop`.
5. `PACK_OPENING`: `pick N` (or `skippack`). Targeting tarots/spectrals in Arcana/Spectral packs (Justice, Strength, Death,
   The Lovers, Empress, Hierophant, Chariot, Devil, Tower, Magician, Star/Moon/Sun/World, Hanged Man, Aura, Cryptid,
   Talisman, Deja Vu, Trance, Medium) apply immediately to the hand cards you name: the hand is shown during pack
   opening, so give the targets in the same command: `pick 2 3 6 --why "..."` applies pack card 2 to hand cards 3 and 6.
   The CLI aborts (nothing sent) if a targeting card is picked without targets. Planets are used immediately.
   You may sell a joker or use/sell a held consumable while the pack is open (e.g. to make room for a Buffoon joker).
   Death direction: `pick N i j` / `use N i j` turns the LEFT card (lower hand position) into a copy of the RIGHT one.
   To duplicate a Glass King at idx 7 onto a junk card at idx 2: targets `2 7`. The CLI prints the resulting copy.
6. `GAME_OVER`: write the run log (section 9). Do not start another run unless told.
7. WIN (you beat the ante 8 boss; state shows `won` true / a win screen): write the run log and stop. One run per agent.

## 2a. Gold Stake (8) on Black Deck: the target (rules verified in the game source)

Gold includes every lower stake's modifier. Together with Black Deck (+1 joker slot, -1 hand):

| Source | Effect |
|---|---|
| Black Deck | 3 hands per round, 6 joker slots (5 + 1) |
| Red (2) | Small Blind pays $0 |
| Green (3) + Purple (6) | blind requirements scale fastest (`scaling = 3`): see the Gold targets in section 3 |
| Black (4) | 30% of shop and pack jokers are Eternal: they can never be sold (dead weight forever if wrong) |
| Blue (5) | -1 discard: with Black Deck you have 3 hands and 2 discards per round |
| Orange (7) | 30% of shop and pack jokers are Perishable: debuffed (scores nothing) after 5 rounds |
| Gold (8) | 30% of shop and pack jokers are Rental: cost $1 to buy, then -$3 at the end of every round |

Stickers show in `s`/`shopadvise` as `{ETERNAL}`, `{PERISHABLE(n rounds left)}`, `{RENTAL(-$3/round)}`. Rent is charged
and perishables tick at every round end, so a skipped blind skips both. `shopadvise`, pack `advise` and `s` encode:
- WINNING LINE (7807 9IIGB2FF, first Gold win, docs/runs/7807_9IIGB2FF.md): flat chips/+mult jokers (Clever, Stuntman,
  Abstract, Even Steven) times two GROWTH xMults (foil Obelisk x3.6, Throwback x3.75), +hand size (Paint Brush, Palette)
  and +1 hand (Grabber). From ante 5 it skipped Small AND Big every ante (9 skips): Throwback +x0.25 per skip, tags paid
  now (Skip/Garbage/Economy money, Boss Tag rerolled The Wall), one blind fought per ante. Obelisk grows on every hand
  whose type is NOT strictly your most played (after +1, ties keep it growing): rotate types, never throw away a card of
  the max type. `s` recommends the skips when Throwback is owned and your rounds beat the boss by 1.3x+.
- SMALL BLIND SKIP: ante 1 only for a tag that gives jokers NOW (Buffoon = Mega Buffoon pack, Top-up = 2 jokers; needs a
  free slot). Ante 2-4: other useful tags need 2+ scoring jokers, and at ante 3-4 your typical hand must reach half this
  ante's boss (skippers died 40-46% vs 25-33%). Rare/Uncommon/Polychrome/Negative/Coupon tags pay in the NEXT shop,
  after the Big Blind. Ante 5+: never skip, except the Throwback plan above. Rent-broke (a rental and <$4 after it):
  skip the Small, its shop could buy nothing.
- RENTAL: priced at -$3 x rounds left (a perishable rental only until it perishes). Take one only for a reliable/growth
  xMult, or as a scorer you need to survive ante 1-2 (`NEEDED NOW`). Never two before ante 5. A flat rental is sold
  once 2 other non-rental scorers carry your hands (41 Gold rentals cost $393, mostly flat jokers held until death).
- PERISHABLE: a bridge for 5 rounds (~1.7 antes). Plan with "scorers still alive next ante" (`shopadvise` prints it):
  a joker with perish_tally <= blinds left this ante does not count, so buy its permanent replacement NOW. A perished
  joker (`PERISHED`) scores nothing: sell it. Growth jokers (Hologram, Constellation...) are never worth it perishable.
- ETERNAL: fine on a core scorer/xMult you would keep anyway; a weak/conditional Eternal joker is a lost slot for the
  whole run (heavily penalised, near-unbuyable once you own 3+ jokers). Eternal jokers can never be sold: `sell` aborts.
- FIRST SCORERS ADD MULT: with no +mult/xMult source, chips-only jokers (Sly, Clever, Scary...) barely scale on a base
  mult of 2-3; `shopadvise` prefers +mult jokers then. Hand-gated xMults (The Order, Trio, Family, Tribe) and suit-gated
  ones (Bloodstone, Ancient, Flower Pot, Seeing Double) only count when they fit your main hand / a Flush build.
- MAIN HAND = the type maximizing (typical est with your jokers and levels) x (how often you made it this run); a Two
  Pair / Trips / Full House play also counts as "could have played a Pair". Before 3 plays an owned hand-gated joker
  decides it (Clever -> Two Pair). Obelisk resets to x1 whenever you play your most played hand; `est` models that.
- DEBUFFED jokers (`{DEBUFFED}` in `s`) do nothing and `est` leaves them out.
- NO SCORER ALIVE NEXT ANTE (or <2 scorers at ante 1-3, or EMERGENCY): an affordable scorer is bought before any
  pack, reroll or leaving; a sticker's cost is small next to losing the run. Packs are already paid for: take a
  stickered scorer into a free slot.
- PACE / SOLVER (`advise`): best hand now + later hands at 85% (printed) below the remaining need -> discard toward a
  bigger hand first; once on pace, bank and keep the discard. `SOLVER` lines (P(clear) by simulation over your remaining
  deck, n samples, $ left) are ADVISORY until calibrated: the ADVICE follows them only for a PLAY that clears now.
- MONEY FLOOR (GOLD_ANALYSIS.md): from ante 2 keep $8 after anything except an xMult, the main-hand planet or a Buffoon
  pack (while owning <2 reliable/growth xMults); 8 of 20 missed xMults were unaffordable, deep runs bought them with
  $11-22. Reroll only with $20+ left after it (rent due at round end kept), at most 2 per shop, never over an affordable
  Buffoon pack. TIGHT (`shopadvise`): when the next blind's projected round is under 1.2x its need (recorded Gold
  shops: 13-40% lost that blind, vs <=6% above 1.2x) the floor is OFF: spend on main-hand score now (7805 lost the
  ante-5 boss by 132 holding $12). Credit Card: floor-exempt buys may go to -$20.
- BUFFOON PACKS: ante 2-5 with <2 reliable/growth xMults they rank 80 (an xMult sighting in 18% of packs). Inside a pack
  run `advise`: jokers are ranked by what they add to a round dealt from YOUR deck (`+N% round est now`; ties never go
  by slot order), with stickers; a bridge must score now (Erosion on a full deck adds 0); SKIP when everything is junk.
- SCORE CHECK and GOLD CHECK (`shopadvise`): your best hand over 40 deals from your deck (75th pct; sees Odd Todd,
  Shoot the Moon, Splash...) vs boss/3 of the next ante; calibrated on 1120 Gold shops (ratio <0.35 died by the next
  ante 84% = EMERGENCY: buy the cheapest multiplier through the floor; <0.7 died 65%: scoring jokers may break the floor;
  >=1.5 died 18%). `shopadvise` lists every higher-ranked item it passes over and why. Targets: 1 reliable/growth xMult
  (incl. Acrobat, Ramen, Stencil; card-trigger xMults like Photograph do not count: they multiply before +mult jokers)
  by the end of ante 2, 2 by ante 5, 3 incl. a growing one by ante 7.
- BOSS PREP (rules checked against blind.lua): The Eye refuses a repeated type in the round and The Needle gives one
  hand, so both kill Card Sharp (and Blueprint/Brainstorm copies of it); The Mouth only locks the first type (Card Sharp
  is fine); The Water sets discards to 0 (Banner dead, Mystic Summit always on); Plant vs face jokers; Psychic vs Half
  Joker (5-card plays); suit bosses vs Flush; Wall/Violet/Needle/Flint/Arm vs a hand too small. Then `shopadvise` ranks
  a counter first (Luchador: sell it during the boss; Chicot; Mr. Bones; Director's Cut) and keeps $10 for `rerollboss`
  when you own Director's Cut. 7802 reached ante 7 and died to The Eye with a Card Sharp engine.
- BUILD: pair-family mains (17 of 28 reached ante 4); Flush/Straight mains reached it 0 of 6, so their jokers and
  planets are non-core. Plan for the next ante: ante 2 -> 3 is the steepest step (1000 -> 3200).
- `RIFF-RAFF` owned (and a free slot): never skip a blind, it makes 2 Common jokers when the blind is selected.
- JOKER ORDER only matters between a +mult joker (or holo edition) and a joker-main xMult; +chips jokers, card-trigger
  xMults (Photograph, Triboulet...) and xMults among themselves can sit anywhere. Brainstorm copies the LEFTMOST joker,
  Blueprint the one to its right: `shopadvise` prints `ORDER FIRST` only when an est over the whole order (copy targets
  included) gains 3%+.
- CARD PHASE BEFORE JOKERS: card enhancements (Glass x2, held Steel x1.5), held-card effects and card-trigger jokers
  resolve before the joker row, so they multiply only the base hand mult plus card +mult (Fable verified 9504/2646).
  Justice/Chariot are not xMult sources on a +mult build.
- JOKER STENCIL: x(empty slots + Stencils), and only while at least one slot is empty; every joker you add costs it x1
  (x2 with a Brainstorm/Blueprint copy). Shop/pack values come from est with the joker added, so slot-fillers that lower
  your rounds show `AVOID(-N% round est)`; Negative jokers bring their own slot.
- AMBER ACORN: the CLI caches your face-up jokers per port; under Acorn `advise` estimates with them, shows the range
  over joker orders, suggests a 1-card High Card probe (it infers the order from the score) and then a `b order`.
- THROWBACK owned: see WINNING LINE (skip Small and Big while your rounds beat the boss by 1.3x+, 1.6x+ vs handicap
  bosses like The House/Fish/Psychic; `s` says when). A skip has no round end: a perishable carrier does not tick, so
  `s` also suggests skipping to keep a key perishable (<= 2 rounds left) alive for the boss.
- SIM IS PRIMARY (`shopadvise`, pack `advise`): every affordable joker/planet/playing card (or pack pick) is played
  through the next 3 blinds plus one round against the boss after them; the ADVICE takes the best SIM `value`
  (rent-adjusted P(clear) x the terminal boss term) over buying nothing (score ratio when every p < 0.05). Rule scores
  only break SIM ties (within 0.03 in the shop, 0.01 in packs; a permanent joker beats a perishable/rental one) and
  decide what the SIM cannot model: vouchers, tarots, boss counters, main-hand planets (they level forever, unless the
  SIM shows the buy hurts). A rental SELL FIRST is simulated: the joker is kept when selling it costs > 0.02. Hard
  rules stay: no eternal rental before ante 7, no second permanent rental before ante 6 unless both are xMults or the
  buy sells the first, no eternal Troubadour / second eternal utility, the $ floor unless TIGHT/EMERGENCY or a +0.15
  SIM gain. In packs (already paid) a sticker rule yields to a +0.15 rent-adjusted gain, and a free sticker-free joker
  into a free slot is never skipped. Credit Card: in EMERGENCY the -$20 debt is spendable on rerolls for a scorer.
- INDICES SHIFT after a reroll/pick/sell: use a name guard, `b buy Clever` or `b buy 1 --expect Clever` (refused on a
  mismatch); every slot command echoes its target name.
- THE MOUTH: the first played hand locks the type for all 3 hands. Open with a type you can repeat (main hand / Pair),
  never a one-off Straight/Flush/Full House unless that one hand clears the whole blind; keep a discard until the lock.
  A locked High Card is any single card. Owning Burglar (0 discards) before The Mouth: sell it or lock High Card.
- ACROBAT (x3 on the final hand): when the best hand clears as the final hand, `advise` spends the earlier hands on
  spare cards and keeps the best one for last. MYSTIC SUMMIT (+15 mult at 0 discards): spend discards early.
- CRIMSON HEART (ante 8 boss, needs ~400000 at Gold) disables one joker per hand and picks a new one after every PLAYED
  hand; discards do not re-roll it, and it never picks the same joker twice in a row. `s` marks the disabled joker
  `{DEBUFFED}`; when it is a key xMult and hands remain, `advise` plays a 1-card throwaway first. 7810_ZY6GJXIG lost
  158620/400000 by banking hands while Photograph was disabled.
- DEEPEST GOLD BUILD SO FAR (7810_ZY6GJXIG, Sonnet, reached the ante 8 boss): face Pair engine. Pair L5 and Trips L7,
  Photograph (x2 on the first face) + Hanging Chad (retriggers the first card twice) + The Duo (x2 on a Pair) +
  Scary Face (+30 chips per face) + Half Joker (+20 at <=3 cards) + Acrobat (x3 on the final hand). It made ~31k on a
  normal hand and ~94k on the final hand at ante 5-6, and cleared ante 7. It lacked a growing xMult for ante 8: from
  ante 6 on, buy one (Hologram, Constellation, Lucky Cat, Glass via Justice).

## 2b. Gold Stake checklist (distilled)

Distilled from 271 Gold runs (`data/swarm_results.jsonl` top_lessons, 1 win: 7807_9IIGB2FF) plus the IF-THEN rules in
their `docs/runs/*.md`. `[N]` = runs whose lesson states the rule; `†N` = runs that died at that boss; a seed = the
run that proved it. 2a explains the why; this is the what. Where a rule here and in 2a differ, 2a wins.

**Each shop (in order):**
1. `s` + `shopadvise`: note SCORE CHECK ratio, next boss, every sticker, every perish tally, money after rent.
2. Ratio < 0.35 = EMERGENCY, < 0.7 or TIGHT = floor OFF: spend to $0 on the best SIM multiplier. Else keep $8 (ante 2+).
3. Sell first: perished jokers (keep them with Abstract), a flat rental once 2 other scorers carry, Gros Michel spares.
4. Buy order: r/g xMult > next-boss counter > $3 main-hand planet > Buffoon pack (<2 xMult) > +mult/+chips scorer >
   Celestial pack > reroll ($20+ left after, max 2). Buy with a name guard (`b buy 1 --expect Clever`); indices shift
   after reroll/pick/sell. Run `s` again after every buy/sell (stale output seen in 19 runs).
5. MONEY DOES NOT SCORE: in the last shop before a blind projected < 1.2x, spend on score now, even a reroll or pack
   when nothing scoring is on offer; 21 runs died holding $8-50 (KLV4P2RZ $22 lost by 18, 3J6IMQB9 $8 at 0.33).
   Then `endshop`; default at blind select is play (skip rules below).

**Each hand (in order):**
1. `s`: boss effect, `{DEBUFFED}` jokers (Crimson Heart), money (The Ox/The Tooth), Obelisk play counts if owned.
2. `hands` + `advise`: take the best est that is not your strict most-played type when Obelisk is owned.
3. Order: Hanging Chad's first scoring card = your best live face/enhanced card (`move hand`); +mult left of xMult.
4. Pace: best hand + 85% of later hands < need -> discard toward a bigger hand (never with Banner/Green Joker owned).
5. Never break a made Pair/Two Pair for a draw when the solver margin is < 0.10, above all at ante 1-2 [10].

**Ante 1-2: economy and first scorers**
- 0 scorers: buy any affordable scorer that adds mult (even suit-gated, eternal, or a $1 rental) before any pack,
  reroll or planet [15]; a chips-only perishable rental is not one: take the $4 Buffoon over it (CFCX6LSH).
- Scorers 1-2 must ADD MULT; chips-only (Sly, Banner, Odd Todd, Scary) on base mult 2-3 never scales [16].
- Concrete scorer > Buffoon pack > chips-only/utility/eternal-conditional joker (5NHAAD92, 4W67ZM38, FA2MCBFK) [4].
- Skip the ante-1 Small only for a tag that gives a joker NOW (Buffoon/Top-up); Rare/Polychrome/Ethereal tags lost [5].
- One $1 rental scorer is fine at 0 scorers; never one that leaves < $5 when a clean $4 joker is buyable [42 rent deaths].
- Second rental before ante 6 only if the same shop sells the first, both are xMults (2a), it is bought and sold in
  the same shop (Campfire feed, no rent: F64SACWK), or it is a perishable bought for ONE named blind and sold right
  after (R87RLKF6 Chad, LFBTMULM Popcorn one-shot the Wall). Otherwise never: $6/round vs $0-5 payouts [19].
- Eternal rental: never before ante 7 (9IIGB2FF passed Raised Fist{E,R}, -$66) [6], EXCEPT an xMult with SCORE CHECK
  < 0.5 AND SIM >= +0.15 (RHQLHNTL passed the Trio at +0.23 and lost by 79).
- At most 2 eternals until you own a reliable xMult; eternal utility/conditional jokers block xMult slots [9].
- No planets/Celestial packs while you own 0-1 scorers (B6JW7ICP, L7B2D714), never off-hand planets in EMERGENCY
  (CFCX6LSH, 6SGZCHWF); from 2 scorers the $3 main-hand planet is a buy [22].
- Reroll never below $5 after it, nor below the $6-8 a revealed joker costs; next shop showed the xMult $1 short [5].
- Jokerless ante 1: 300/3 = 100 a hand is pace, so a made Two Pair (~100) is played on hand 1 (GLE6W9AC lost on a
  p 0.98 Pair dig); after one missed draw bank the made hand and keep a discard; no 3-card flush chases [10].
- Credit Card: -$20 is a hard wall, $-12 = only buys that clear the next blind; never packs/vouchers on credit; in
  EMERGENCY unused credit is worthless, spend it on rerolls for a scorer (NC2N9JRV) [5].
- Main hand is pair-family (Pair/Two Pair/Trips); Flush/Straight-only engines died by ante 3 (0 of 6) [6].

**Ante 3-4: xMult hunt, perishables, Buffoon packs**
- No reliable xMult = hard cap: flat builds top ~2.4k (a3), ~5-8k (a4), ~10-15k (a5) [51]. 1st xMult by end of ante 2.
- 2nd lasting xMult by the first ante-5 shop; one x2 clears ante 4 but tops ~22k vs 25-50k at ante 5 [9].
- 0-1 xMult: Buffoon pack before rerolls/Celestial (~$24 vs ~$91 per xMult sighting) [5]. Under $20, rerolls whiff
  (A5D7B521 $53, B2KYV37D $55) [8]: keep $8-10 for the xMult when it shows (R87RLKF6). With $25+, joker views
  (Buffoon, rerolls) beat levels, Arcana and interest (D9KFK2PH, 7MUK4NI9 $77, HCUCE445) [3].
- Score check < 0.5 with 0-1 xMult: a planet level cannot close the gap; hunt the xMult (LNXDRQDE).
- Perishable carrying a stat: buy its permanent replacement BEFORE its last round; bridges bought together expire
  together (T9QEI78Z, 16N52CRZ) [39].
- Perishable xMult with 1-2 rounds left and best hand >= boss need: skip Small/Big so its last round is the boss [6].
  If the hand is below the boss need instead, play the blinds and spend the shops on its replacement (VF82VQ4A).
- Never skip a blind while holding money you could turn into score, nor at ante 3-4 with 0 xMult or a hand-gated
  engine: skip-tag money is paid after the shop you skipped (6SGZCHWF $13, F64SACWK $28, RTJZMPXF) [17].
- Broke (< $5): skip only the $0 Small, never the Big, whose $5 funds the next shop (3VX28DKP); rent-broke (2+
  rentals, < one round of rent in cash): skip the $0 Small, its shop buys nothing [5].
- Card-phase multipliers (Photograph, Glass, Steel/Chariot, red seals, Bloodstone) only multiply base mult before
  +mult jokers: +10-25% on a flat build, never "the xMult" [10].
- Fill 6 slots by ante 4 with flat +mult in the non-xMult slots (2a); once mult >> chips (~55 mult on 40 chips) buy
  +chips instead (HREAJTJ2 Scary Face, FFN7JZWK Arrowhead) [6].
- Never trade hand size for a flat joker on a Pair/Trips engine (BK2G3JSQ Stuntman/Luchador, JB7Q6L46 Ectoplasm) [2].
- Acrobat as the xMult: the final hand is the main hand, buy its planet every shop; alone it caps ~50-108k [7].
- Mr. Bones saves exactly one blind: skip the Big so only the boss is fought, then sell it next shop [6].
- Hold one rescue tarot (Strength/Death/Justice, $3) from ante 3 for no-discard/one-hand bosses [3 + 7 Water/Needle].

**Ante 5+: skip-to-boss, Throwback, Obelisk**
- Never skip at ante 5+ (5 of 6 skippers died) unless one of the next three lines applies.
- Throwback owned and your 3-hand round (75th pct) >= 1.3x this ante's boss (1.6x vs handicap bosses: House, Fish,
  Mark, Wheel, Psychic, Eye, Mouth, Needle, Water, Pillar, Serpent, Manacle, Hook, Wall, ante-8 finishers): skip Small
  AND Big every ante (+x0.25 each, tags pay now). 9IIGB2FF won with 9 skips (x3.75); N5BDCVFH tried at 0.9x vs The
  House and died; below 0.3x skips add depth, not a win (HREAJTJ2) [6 + 7 post-mortems].
- On the Throwback line buy Director's Cut ($10) at ante 4-6: skip-tag money lands at blind select and boss rerolls
  are the only way to spend it (G2HUKM9D reached The Wall with $50 unusable; its 166k beats a normal 120k boss) [2].
- Without Throwback: skip both when Small and Big each need > 2.5x your typical hand and Mr. Bones/a perishable carry the
  boss, or you are rent-broke (6XN584I7, CMVCIW9Q, 2J1M1T5I, 41KHYKNY, HREAJTJ2) [7].
- Big Blind tag = Boss Tag: skip the Big to reroll The Wall/Violet Vessel or a boss you cannot beat; keep a mild
  boss (C5AF29KG) [5].
- Obelisk: a play resets it only if that type's count (after +1) is STRICTLY above every other; ties keep it growing.
  Keep one type alone at the max and rotate the rest; never a 1-card High Card throwaway when High Card is the max;
  never let 3 makeable types tie at the max with hand size <= 6 (CLA5SVN7 at The Ox). Level only types BELOW the
  max; a planet for the most-played type feeds resets (7C89CEFK) [4: 9IIGB2FF, YZMAQVI2, CLA5SVN7, 7C89CEFK].
- Ante 6+ needs a GROWING xMult on top of 2 xMults (Hologram, Constellation, Lucky Cat, Campfire, Throwback, Obelisk);
  ante 8 needs a 4th multiplier because Crimson Heart disables one per hand [11: ZY6GJXIG, UIL7HPIQ, 83YPG1WJ...].
- From ante 5, two rentals freeze the wallet at $0-12: buy the run's last joker with ante-4 money (MKHAVQ6W).

**Boss counters (only bosses that killed runs; read the boss in the first shop of each ante)**
- The Water (0 discards) †10: own an any-hand flat scorer or Mr. Bones; in the last shop sell dead weight for one,
  even a $1 eternal rental (SL5MJZY1 passed Sly); never skip the Big before it (RTJZMPXF); flush engines count half [10].
- The Needle (1 hand) †1: discards first, rescue tarot last; Card Sharp/Duo-repeat engines get nothing [9].
- The Psychic (exactly 5 cards) †6: Half Joker is dead; at ante 1 buy a 5-card scorer; hold <= 3 for the last hand [7].
- The House/The Fish (face-down) †8/†8: spend discards BEFORE the first play (discard draws come face up); use
  face-downs as fillers next to a made pair; `sort rank` places them by rank [18 House/Fish post-mortems].
- The Goad (spades) / The Club (clubs) †8/†8: debuffed cards still make the type but score 0; discard that suit first,
  never count it for held-card jokers; at ante 1 prefer jokers that do not need that suit [7].
- The Ox †3: read which hand it names; avoid that type when money > 0, play it when money is negative (sets $0) [3].
- The Pillar †7: in its Small/Big play only the cards you can spare (played cards stay debuffed all ante); finish with
  the lowest clearing card, never key cards (V5CU8MEN); debuffed cards still form hand types [7].
- Crimson Heart †3: check `{DEBUFFED}` before every play; if the disabled joker is unused by the best hand, play it
  now; else a cheap hand that does NOT reset Obelisk; discards never re-roll it (9IIGB2FF, ZY6GJXIG, A5LJXXMW).
- Amber Acorn †2: play a cheap 1-card High Card first, infer the order from its score, `order` +mult left of xMult
  before big hands (B6KZC39M lost 64k vs 178k; E57ZB14D shuffle happens once at blind start).
- The Eye †6 / The Manacle †7: repeat-type engines (Card Sharp, Two Pair Blueprint) are dead; reserve $5-10 for
  Luchador/Mr. Bones/Director's Cut, or buy hand size/a second always-on xMult first (MKHAVQ6W, YJGGELMB) [9 + 2].
- The Arm †8: L1 hands are immune, so dig with them; do not buy a planet for the hand you will play there [8].
- The Hook †7: bank made hands now, never hold a draw through a play; held-card jokers lose 2 random holders [6].
- The Serpent †5: every play AND discard draws exactly 3, so discard or play 1 card at a time (1-card High Card digs
  with spare hands) to grow the hand to 10-12; the solver's "draws 5 new cards" is wrong (D5KV79HL) [6].
- The Tooth †6: -$1 per card: play the 1-2 card hand that clears; Bootstraps drops before scoring [7].
- The Wall †10: with 0 xMult at ante 3-4 it is lost in the shops: spend those 2 shops on joker views, Mr. Bones,
  Luchador or Director's Cut (SWXRQQVU saw it twice); Boss Tag on the Big = reroll it [11].
- The Flint †4 / The Plant †7: base-mult (Chad/Photograph/levels) and face engines need Luchador/Chicot or a flat
  +mult joker bought in that ante's Small/Big shops; do not skip those shops (PA2UGD4M, I9RJP8E5, 9MRSNKY7) [10].
- The Mouth †7: lock a repeatable type (Pair/Two Pair); keep a discard; locked type unmakeable with 2 hands left = play
  a 0-score junk hand to cycle (9IIGB2FF found the 5th club); sell Burglar before it (E46A72GI) [18].

**Joker gotchas**
- Never sell a working scorer for one that does not fire on your main hand or starts at x1 (Wily on Two Pair, unfed
  Hologram, hand-gated Trio); with Swashbuckler/Abstract every sale also costs their mult (K4GMJRB5 missed 7040 by the
  sold Ride the Bus; X5MG1LC2, JEMI6XIF) [3].
- Madness: destroys a random non-eternal joker every Small/Big select; never buy it with 4+ needed jokers, sell it by
  ante 3 once flat scorers appear (UH5NGY7A, 1S259TVC; SIM ignores the destruction in 3 runs).
- Joker Stencil: x(empty slots + Stencils). At 0-1 jokers it is x5-6, the best flat multiplier: hold $8 for it
  (ERVFM4CI). At x3+ a new joker must beat losing x1 (-33%): only xMults/Negatives; scale with planets, they take no
  slot (G2HUKM9D, 7C89CEFK). A perishable Stencil as the only multiplier = EMERGENCY from the next shop [6 + 6].
- Hanging Chad: retriggers the FIRST scoring card twice; `move hand` the best live face/Glass/foil/odd Ace first before
  every play; with Photograph play a 2-card face pair (x8) (YSRFMUJQ, CH39BUCC); est may ignore order (TEE3QFI4) [7].
- Blueprint copies the joker to its RIGHT: put it directly left of your xMult (rightmost copies nothing), then switch
  the main hand to what that xMult needs (U377P3KF; RM2XKW5G copied Photograph).
- Flower Pot (x3 when the SCORING cards cover 4 suits): debuffed cards still count for the suit check under suit
  bosses and est/solver drop it (THD1ZBW7 lost by 8); fillers don't count, so a 4-card Two Pair needs 4 suits
  (PBJP26A2). Conditional, not the xMult [2].
- Card Sharp alone needs two same-type made hands per round: buy a flat +mult right after; solver/SIM overrate a
  lone Card Sharp at ante 1 (FRRTMCZ6, W3IP8CM2).
- Burglar: 0 discards, +3 hands; Mystic Summit becomes always on; sell before The Mouth; SCORE CHECK/SIM ignore its
  extra hands, so do not sell it on their advice (BG8RRBW2) [3 + 4 post-mortems].
- Banner / Green Joker: never discard (Banner -30 chips, Green -1 mult forever per discard); no Mystic Summit with
  them; Green Joker makes Small skips costly (VED7UEVL lost by 26, QEY21ZAA) [5].
- Gros Michel: 1/6 to die every round end; treat it as gone next round and buy the permanent scorer now [7].
- Wraith: sets money to $0; only take it at <= $4 or in debt (YSBWEA3U lost a $16 wallet at ante 3) [2 + 2].
- Hologram: x1 without card-adding sources; feed with Standard packs ($4, +0.25/card), else not a growth xMult [5].
- Abstract counts perished and Crimson-disabled jokers: do not sell a perished joker while Abstract is owned [3].
- Riff-raff: keep a slot free at every blind select; sell it once slots fill with keepers [14 post-mortems].
- Campfire: feed it with $1 rentals bought and sold in the same shop (+x0.25, no rent); it resets after every boss,
  so plan each new ante at x1 and keep hunting a permanent xMult (AJGH6ECT, XRWKX6AS, 3IDYS1SA).

**Advisor trust**
- Solver P(clear) at antes 1-2 is calibrated on 2985 recorded decisions: at p >= 0.95 it predicts 0.995 and 0.997
  happened. Lost blinds at 0.9+ (reported in 32 runs, 10 more since) are the expected ~1-in-20 tail, not a bias.
  Trust p, but treat an early line with 1-2 outs as fragile and don't break a made hand for it (step 5 above).
- SIM noise: when every option's p < 0.15 (or all read +0.00 / ~1.00 saturated), differences under ~0.10 are noise
  (BK2G3JSQ Venus 0.00 vs Earth 0.27 in one pack; PBJP26A2 0.44 vs 0.48; CFCX6LSH off-hand planets); decide by
  SCORE CHECK ratio, permanence and step 4 order [7 + 6].
- Follow SIM over heuristic text (LEAVE/AVOID/sell) when SIM gain >= +0.15 and the item has none of the blind spots
  below; text contradicted SIM and SIM was right in 12 runs (e.g. 1S259TVC LEAVE vs Duo +0.41).
- SIM blind spots (override it) [23]: rent past 3 blinds and eternal rentals (8), Madness destruction, Obelisk resets
  (it suggested selling x3.2 Obelisk, CLA5SVN7), perish ticks, Constellation/Hologram growth, Campfire feeding,
  Mr. Bones' save (16N52CRZ, HREAJTJ2), Banner's discard loss, Stencil's slot cost, Riff-raff, packs, Burglar.
- Ignore `NEEDED NOW` / BUY on an eternal rental unless you own 0 scorers, and on any rental whose rent blocks the
  next shop's buy (ERVFM4CI missed Stencil by $6) [18].
- Obelisk `AVOID`/sell advice is wrong on flat builds where hand type is irrelevant (9IIGB2FF foil Obelisk won the run).

## 3. Scoring facts (verified in-game)

- Score = chips x mult. Only the cards forming the poker hand score; extra played cards do not.
- Base chips/mult = the hand's level (`Levels:`). Card chips: 2-10 face value, J/Q/K = 10, A = 11. Aces are NOT faces.
- Card effects fire per scoring card (Smiley +5 mult/face, Scary +30 chips/face, Photograph x2 on first face, Glass x2).
- Then jokers apply LEFT TO RIGHT: +mult/+chips jokers must be LEFT of xMult jokers. Use `order` after buying an xMult.
- Editions: foil +50 chips, holographic +10 mult, polychrome x1.5 mult.
- Forced pack pick with no scoring joker: take the one that does nothing (Fortune Teller, an economy joker) over one with
  a resource penalty (Troubadour -1 hand, Merry Andy -1 hand size): a zero beats a negative on Black Deck's 3 hands.
- Buffoon pack picks at ante 1-2: a Pair-triggered joker (Jolly +8 mult, Sly +50 chips) beats a Trips/Two Pair-triggered one
  (Wily, Mad, Zany, Clever): ante-1 hands are mostly pairs, and the pair jokers also fire on every richer hand.
- Ante 1-2 with fewer than two scoring jokers: a shop with no +mult/+chips joker is a shop to REROLL (keep $4 after),
  not a shop to buy packs in. Two runs lost ante 2 by 10-15 chips holding only levels and an economy joker.
- Cards score in HAND ORDER (left to right as shown by `s`), not in the order you type indices. A Glass (x2) or
  Photograph face early in that order multiplies less than one late in it; `est` models the real order. A Glass card
  that shatters still scored its x2 first (shatter only removes it from the deck afterwards).
- Misprint is +0..23 mult at random; `est` uses 6, so a Misprint hand lands below `est` about 1 time in 4 (7807: Trips
  est 1314, actual 730 on a roll of 2). Do not rely on Misprint for an exact last-hand clear.
- "If hand contains a Pair/Two Pair/Three of a Kind" jokers (Jolly, Sly, Mad, Clever, Zany, Wily, The Duo/Trio...) fire on
  every richer hand too: Two Pair, Full House and Four of a Kind all contain a Pair; Full House contains Two Pair and
  Three of a Kind; Four of a Kind contains a Pair and Three of a Kind but NOT Two Pair (verified: Clever/Mad Joker do not
  fire on Quads). `est` accounts for this.
- The Arm (boss): EVERY hand type you play that round loses one level, each time you play it. Play only unleveled types
  (or accept the loss) and never play your leveled main hand twice under The Arm.
- The Hermit tarot doubles your money (max +$20). Use it when you hold $10-20.
- Gold targets (Small/Big/Boss; Black Deck, `scaling = 3`): a1 300/450/600 | a2 1000/1500/2000 | a3 3200/4800/6400 |
  a4 9000/13500/18000 | a5 25000/37500/50000 | a6 60000/90000/120000 | a7 110000/165000/220000 |
  a8 200000/300000/400000. Beat the a8 boss to win. Bosses can ask more (The Wall x2, Violet Vessel x3); the state's
  `need` is authoritative. Ante 3 is ~3.2x ante 2: plan purchases for the NEXT ante, not the current one.
- Black Deck at Gold: 3 hands, 2 discards, 6 joker slots, 8-card hand. Unused hands pay $1 each at cash out.

## 4. Hand decisions (do this every time)

0. Run `advise`. It prints the candidate hands and an `ADVICE:` line with the exact command to run (play with
   fillers, or which cards to discard). Follow it unless you can state a concrete reason it is wrong (e.g. a boss
   rule it does not know, or a repeat-type joker you are setting up). Then continue with the checks below.
1. Run `hands`. Read `est` for each candidate and `need N more this blind`.
2. If some candidate's `est` >= need: play it with `play TYPE idx...`. Prefer the one using fewest cards only if it still clears.
3. Otherwise, if you have discards left: DISCARD, do not play a weak hand. Keep the cards that build toward the best
   target (a made pair plus its partners, 4 of a suit for a flush, 4 to a straight, face singles if your jokers love faces)
   and discard up to 5 others. Re-run `hands`.
4. Out of discards: play the highest `est` hand that leaves the remaining hands able to finish (sum of realistic ests).
5. FILLER DRAW: when your hand uses fewer than 5 cards, add junk cards to reach 5 so you draw more. Fillers must not change
   the type: no extra pair, no third of a kind, not 5 of one suit, no straight. `play TYPE` aborts if you got it wrong.
6. Repeat-type jokers (Card Sharp x3 if type already played this round): play a cheap version of the type first
   (a low pair + fillers), then the strong versions. `hands` shows "x3 if repeat" values.
7. Boss notes: The Psychic = exactly 5 cards. The Eye = each type once per round. The Mouth = one type only.
   The Mark = faces are face-down (they are always J/Q/K; `sort suit` groups them by suit; 3 face-downs of one suit
   are K,Q,J so a 4th face-down of another suit guarantees a pair; 4 face-downs always contain a pair).
   Debuffed cards count for the type but score nothing.
7b. RESCUE TAROTS come from the SHOP, not from packs: a tarot picked from an Arcana pack is used on the spot (it cannot
   be banked). To hold Death/Strength/Justice for a boss, buy it from the shop's card row ($3); `shopadvise` ranks it
   highly from ante 3 when you hold none.
8. LAST HAND CHECK: before a forced final hand that does not clear, look at your consumables (`s`). A held Tarot
   (Death copies a card, Strength ranks up 2 cards, Devil/Justice/Chariot enhance, Magician Lucky) or Planet can turn a
   dead card into a match or add a level: `use N t1 [t2 ...]` with the target hand positions, then re-run `hands`. Never concede a run with an
   unused consumable.

## 5. Shop procedure (money decides ante 6-8; scaling decides ante 3-5; a joker decides ante 1-2)

Start every shop visit with `shopadvise`. It lists every item with a class (XMULT / PLUS / ECON / PLANET / PACK / VOUCHER),
respects the money floor, and prints an `ADVICE:` command (buy, sell-then-buy, reroll, or endshop). Follow it, then run
`shopadvise` again until it says LEAVE. Override only with a concrete reason (e.g. the upcoming boss line it prints).

Ante 1-2 (you start with $4-8, no jokers). DO THIS:
- Buy the FIRST affordable joker that adds mult or chips to hands you can make (Joker +4, Jolly +8 pair, Mad +10 two pair,
  Zany, Crazy, Droll, Sly, Clever, Half Joker, Smiley Face, any "+X mult"/"+X chips"). A $3-5 joker roughly doubles
  ante-1 scores; without one the Big Blind (450) and boss (600) are usually lost. Two such jokers by the end of ante 2.
- STAKE 2 DATA (27 runs so far, 2026-08-30 evening): most losses are ante 1-2 with zero scoring jokers (the $0 Small
  Blind leaves $4-7 for the first shops) or The Wall at ante 3-4 (double requirement) on a flat build with no multiplier.
  When The Wall is the upcoming boss, that ante's shops buy ONLY the main-hand planet and a multiplier (any xMult that
  fits, or Justice for Glass) — no pack gambles — and you arrive with cash for a rescue tarot.
- STAKE 2+ (Red Stake and up): the Small Blind pays $0, so skipping it costs only one shop visit. Skip the Small Blind
  (ante 1-4) when its tag is worth a joker or a pack: Uncommon/Rare/Negative/Foil/Holo/Polychrome, Buffoon, Charm,
  Meteor, Ethereal, Coupon, Top-up, Investment — but with fewer than two scoring jokers only a tag that GIVES a joker
  (Uncommon, Rare, Buffoon, Top-up, Coupon) beats the shop visit. At ANTE 1 with no jokers, SKIP the Small Blind for any
  tag except the Boss tag: it pays $0, three pair-shaped hands against 300 lost 4 of ~8 stake-2 attempts (292/300,
  256/300, 224/300), and the $4 shop it unlocks rarely buys a joker anyway. `s` at blind select prints `ADVICE: b skip`
  when it applies; Big and
  Boss blinds are never skipped, and at stake 1 nothing is skipped.
- Ante 1-2 rerolls: reroll ONLY when the shop has no scoring joker and you keep $4+ after it (shopadvise says when). Do NOT buy planets/tarots before you own 2 jokers,
  except a Planet for a hand you just played twice.
- Buffoon Pack ($4) is fine at ante 1 if no joker is in the shop (pick the mult/chips joker; check editions: holo/poly/foil).
  If the pack offers no scoring joker, take the one that scores soonest (economy > slow scaling), and buy a scoring joker
  in the next shop before anything else. Ceremonial Dagger, Fortune Teller, Pareidolia, Space Joker do nothing for ante 1-2.

Ante 3-5:
- Every shop: is there an xMult joker (x2, x3, "xMult grows", Photograph, Card Sharp, The Duo/Trio/Order/Tribe, Baron,
  Hologram, Constellation, Cavendish, Steel/Glass Joker, Blackboard, Campfire, Ancient Joker, Baseball Card)? Buy it,
  selling the weakest flat +mult joker if slots are full. Put xMult jokers rightmost with `order`.
  CONDITIONAL xMult (The Idol, Bloodstone, Flower Pot, Seeing Double, Driver's License, Loyalty Card, Acrobat...) also
  counts once you are at ante 4+ with none: a run that lost ante 6 by 461 chips had passed on The Idol at ante 5 while
  rerolling for a clean xMult that never came. Take the first one; upgrade later if a better one appears.
- Level the hand you actually play (Pair->Mercury, Two Pair->Uranus, Three of a Kind->Venus, Straight->Saturn,
  Flush->Jupiter, Full House->Earth). Celestial Pack ($4) = one level; take the planet for your main hand.
- Keep an economy joker if you have one (Cloud 9, Golden Joker, Egg, Rocket, Bull). Do not sell it before ante 6.
- Money target: reach $25 by ante 4 and stay above it; interest pays $1 per $5 (max $5) every round.
  Spend below $25 only for an xMult joker or a level for your main hand.

Ante 6-8:
- Two or more xMult sources plus main-hand level 4+ is the minimum. If you are not there, spend everything on getting there.
- Bosses: check the boss name at blind select (section 6). Luchador (sell to disable), Director's Cut voucher, Chicot answer bosses.
- Campfire-style "grows when you sell" jokers: every sale (jokers AND consumables via `sellc`) counts; the boost resets
  after each boss, so it is a per-ante rental, not a plan.

Ante 3+: if you own no xMult joker (ante 4+: fewer than two) and have $15+ after the reroll, REROLL until one appears,
then sell your weakest flat +mult joker to make room. Money sitting idle at ante 5 with no xMult is a lost run.
`advise` chases a flush only when its expected value beats your made hands; if your jokers are pair/trips based, prefer
keeping pairs (say so in the log when you override).

STAKE 1: NEVER SKIP A BLIND, at any ante (every logged stake-1 skip at antes 3-4 was followed by a loss). STAKE 2+: skip
the Small Blind for a joker/pack tag per section 5 (it pays $0 there). Otherwise:
a skip forfeits a shop visit and income exactly when the blind curve steepens. `s` at blind select prints `ADVICE: b blind`.
Avoid self-destructive or decaying jokers as scaling: Madness (destroys a joker every blind), Ceremonial Dagger,
Ice Cream, Popcorn, Gros Michel; Swashbuckler is worthless as your only joker. `shopadvise` marks these AVOID. Ramen
(x2, -0.01 per discarded card) is an exception: a real xMult for several antes at Gold's 2 discards.
After every joker buy/sell, keep +mult jokers left of joker-main xMults (`shopadvise` prints ORDER FIRST when needed).

Always: fill all 6 joker slots by ante 4. Skip tags at Gold: follow section 2a (`s` prints the skip ADVICE); a tag that pays
in the next shop never helps the Big Blind in between. Investment/Economy at ante 5+ only if the shop is not needed.

## 6. Bosses

The Hook (2 random discards per hand) | The Wall (x2 chips) | The Wheel (1/7 face down) | The Arm (-1 level)
The Club/Goad/Window/Head (a suit debuffed) | The Psychic (5 cards) | The Eye (no repeat types) | The Mouth (one type)
The Plant (faces debuffed) | The Pillar (cards played earlier this ante debuffed) | The Needle (1 hand) | The Manacle (-1 hand size)
The Mark (faces face-down) | The Serpent (draw 3) | The Ox (money to 0 on most played hand) | The House (first hand face down)
The Water (no discards) | The Fish (draw face down) | The Tooth (-$1 per card) | The Flint (half base chips/mult).
Ante 8: Amber Acorn (shuffles joker order: budget 15% less), Verdant Leaf (sell a joker to un-debuff), Violet Vessel (x3 chips),
Crimson Heart (a random joker disabled per hand), Cerulean Bell (one card forced selected).
BOSS BLINDS CANNOT BE SKIPPED. Skipping Small/Big only forfeits their income and sends you to the boss sooner.
The boss for the ante is shown at blind select and in the shop ("Upcoming boss"). Prepare for it during Small/Big:
- The Pillar: every card you play in Small/Big this ante is debuffed at the boss. What matters is the TOTAL number of
  distinct cards played across the whole ante: clear Small/Big with the smallest hands that clear (2-card pairs, no fillers,
  no 5-card flushes/straights for show) so most of the deck is still clean for the boss; or keep a Luchador/Director's Cut.
- The Plant / suit bosses (Club, Goad, Window, Head): if your engine depends on faces or that suit, buy Luchador or
  Director's Cut, or level a backup hand type before the boss.
- The Needle (1 hand): you need one hand that scores the full amount; level your main hand and hold discards for setup.
- The Water (no discards): build the hand from what you are dealt; prefer flexible +mult jokers.
- The Serpent (always draw 3 after a play or discard): a 5-card discard leaves you with fewer cards for the rest of
  the round (7777_P6KN2G8G ended its last hand with 3 cards). Discard at most 3 at a time; play made hands early.
- The Wheel / The Fish / The Mark / The House (cards face down): never chase flushes or straights; play rank-based hands
  (pairs, trips, two pair) from the visible cards. `play TYPE` skips its type check when face-down cards are included.
- The Arm (levels down each hand type you play, every time): sell Luchador before your first hand, or play only
  unleveled hand types for all three hands. Buy Luchador ($5) whenever it appears from ante 3 on: it is boss insurance.
- Always keep ONE discard for the final hand of a round when your engine depends on finding a specific card (pairs, suit).

## 7. Verified numbers from real runs

- Two Pair L1 with no jokers ~100-120 per hand; Pair ~50; Flush ~280; Straight ~240; Full House ~370; Trips ~160.
  Ante 1 Big Blind (450) with 3 hands and no jokers therefore needs a flush/straight/full house or a +mult joker.
- Face pair with Smiley+Scary+Photograph, Pair L6, Campfire x3, Card Sharp x3: 57915 (ante 7). Same at Campfire x1: 19305.
- Run 1 (seed WFBK57R4) lost ante 8 Big Blind (75000) with 35199: temporary Campfire scaling + $0 money. Permanent xMult
  and interest income are what carry ante 7-8.
- Batch 1 (8 Haiku runs): all lost in ante 1-2 for three reasons: misread hand type (fixed by `play TYPE`), unused discards,
  and shops spent on rerolls/planets instead of a first joker.

## 7a. Lessons from the deepest runs (ante 7 boss, ante 6, several ante 4-5)

- DATA (1175 logged shop visits, 2026-08-30): a clean xMult joker (Photograph, Baron, The Trio/Duo/Order/Tribe, Card Sharp)
  was offered in 2% of shops; a conditional or growth xMult (Flower Pot, Bloodstone, Hologram, Constellation, Campfire,
  Vampire, Seeing Double, Loyalty Card, Acrobat, Blackboard...) in another 8%. Expect 2-3 xMult-shaped offers per run
  and take the first one from ante 4 on. Ride the Bus/Throwback/Hit the Road are NOT real xMult sources.
- Flat builds cap around 20-30k per hand at ante 8 levels; 100000 needs x3-x5 on top: Glass cards (Justice) on your
  main ranks, Steel (Chariot) on cards you hold, Death/Cryptid to copy an enhanced card, Aura/Wheel of Fortune for
  Polychrome. Arcana and Spectral packs are the reliable route to multiplication; buy them every shop from ante 3.
- FIRST WIN (7779_E19RBJB8, 2026-08-30 ~15:30): beat the ante 8 boss Verdant Leaf 153664/100000. Build: Two Pair L8 +
  Full House L7 as the second type, Spare Trousers (+2 mult per Two Pair played, reached +56), Supernova (+1 mult per
  play of the type), Yorick (x1 per 23 discards, reached x4), Photograph x2 with Pareidolia (every card is a face, so
  Photograph always fires), Smiley Face sold at the boss (Verdant Leaf debuffs all cards until one joker is sold). The
  lesson: ONE growth +mult joker for the main type (Spare Trousers/Supernova) plus TWO xMult sources (a guaranteed one
  like Photograph+Pareidolia and a growth one like Yorick/Constellation) on a L8 pair-family hand clears 150k per hand.
  From now on all players start at stake 2 (`start Black Deck 2`).
- STAKE 2 WIN (7777_YYA2GKBR, 2026-08-30 ~13:30, Red Stake): beat Cerulean Bell 108480/100000. Build: Two Pair L12
  (Space Joker fired its 1/4 level-up many times), Clever (+80 chips) + Jolly (+8 mult) flat stackers, Photograph x2
  (faces in the Two Pair) and a foil Cavendish x3 bought at ante 5 after selling Flower Pot; enhanced main-rank cards
  (Mult Aces via Empress/Death copy, Steel AD, Glass via Justice) and Justice+Hanged Man held unused as rescue. Money
  stayed $10-40 and was reinvested every shop. From now on all players start at stake 3 (`start Black Deck 3`).
- STAKE 3 ANTE 1-2 (two of the first three Green Stake runs died at ante 1-2 with ZERO scoring jokers, 558/600 and 414/900):
  the ante-2 Small Blind is already 900, so a jokerless pair engine (~135-150 per hand) cannot clear it. With zero scoring
  jokers and none offered, `shopadvise` now says REROLL down to $0 (the $4 floor only matters if you survive to the next
  shop). A weak but unconditional joker (Green Joker) beats no joker; a straight-only/flush-only one still does not.
- STAKE 3 SHOP TRAPS seen in the first Green Stake runs: Burnt Joker ($8) and Bull ($6) bought at ante 2 with no scorer
  (Bull is +2 chips per $ and worth nothing once the wallet is empty; Burnt Joker levels hands but scores nothing), Flash
  Card + Constellation as the only jokers, a LEAVE with $5 and two Buffoon packs on offer. `shopadvise` now demotes Bull
  when it would leave under $10, demotes Burnt Joker while you own fewer than two scorers, and ranks a Buffoon pack above
  everything when you own no scorer. The Fish (final hand dealt face down) at ante 2 needs a joker that scores on any
  Pair and one discard kept for the last hand.
- ANTE 1 WITH NO JOKER (7777_SDCDPVJE, 284/450): `advise` chased a flush and then a straight on the Big Blind; both
  missed and the forced last hand was a lone Pair. With zero jokers `advise` now refuses a chase whenever the made
  pair-family hands already project to the requirement; sequence Two Pair / Pair hands and keep one pair for the end.
- STAKE 3 ANTE 3-4 (five runs died at ante 3-4 Big Blinds, 3052/3900, 11068/12000, 3956/12000, 12637/16000): every one
  was a flat build with zero xMult and a main hand at L1-L2, money spent to $0-2 each shop on third/fourth flat jokers.
  `shopadvise` now demotes a third flat joker once you own two scorers and no multiplier (when it would also eat the
  reroll budget), rerolls for an xMult from ante 3 on with $6+ left after, and ranks the main-hand planet above a third
  flat joker at ante 1-2. `hands`/`advise` now list 4-card flushes and straights when you own Four Fingers. Keep ONE
  discard for the forced final hand of EVERY round, not just boss rounds (7781_8C3BV4GW died on a High Card).
- SPLASH: `advise` shows the est of the core hand; the `play` line shows the est with your fillers scoring (exact in
  7777_ITH36UMC: 3341/3341, 3601/3601). Compare the `play` line, not `advise`, when judging a Splash hand.
- FREE ITEMS (Coupon Tag): a $0 pack or joker is never worse than leaving; `shopadvise` now ranks every $0 item above
  LEAVE (7781_C7CJ1SDJ left a free Arcana pack on the table and died at the ante-2 Big Blind). Mr. Bones from a forced
  Buffoon pick is a real safety net at ante 1-2 when you own no scorer (it saved 7781's ante-1 boss at 524/600).
- PAIR-GATED JOKERS FIRE ON EVERY PAIR-FAMILY HAND: Sly/Jolly (+50 chips / +8 mult "if Pair") fire on Pair, Two Pair,
  Trips, Full House and Quads; Wily/Zany/The Trio ("if Three of a Kind") also fire on Full House and Quads. `shopadvise`
  had mislabeled Sly as "other hand" dead weight on Trips/Two Pair builds (7779_99SVFW6J, 7782_FG1RS4V4); fixed.
- LOYALTY CARD timing (est_log, 6 rows): the stored counter is one hand stale; it fires when the state shows
  "1 remaining", and "0 remaining" means it fired on the LAST hand. `advise`/`play` notes now say which.
- VAMPIRE strips the enhancement from every scoring card BEFORE it scores (a Bonus/Mult/Glass card is a plain card under
  Vampire; 7782_8FEWFG6A est 2368 vs actual 481) and grows x0.1 per stripped card. Do not pair Vampire with Glass/Steel
  builds; est now models both.
- BLUEPRINT/BRAINSTORM copy a neighbour: `shopadvise` now ranks them as a real buy (sell-then-buy when slots are full) once
  you own an xMult or two scorers; `order` the copy next to the joker it should mirror (7781_DVJG9FYF left Blueprint
  in the shop with $39 and full slots).
- ANTE-1 SKIP RULE REVISED (stake 3 data): skipping the ante-1 Small Blind for a tag that does not give a joker or pack
  (Polychrome, Skip, Coupon-less editions, Double...) sent jokerless decks into the 450 Big Blind and lost 284, 404 and 436
  of 450. `s` now advises the skip only for joker/pack tags (Uncommon, Rare, Buffoon, Top-up, Coupon) or, with two
  scorers, the usual SKIP_TAGS; otherwise play the 300 Small Blind and take the shop.
- HALF JOKER (+20 mult when 3 or fewer cards are played): `advise` no longer pads its plays with fillers while you own it,
  and under The Psychic (5 cards forced) `hands`/`advise` est now drops the +20 (7777_NTR8WJDQ est 1760 vs actual 160).
- RAISED FIST doubles the LOWEST card left in hand: play your low spare cards as fillers and keep the Ace/King held
  (7778_6D6A7CTT doubled a final hand from 480 to 960 this way).
- THE TOOTH AHEAD: `shopadvise` keeps $6 in that ante's shops (non-xMult buys are skipped below it).
- FORCED BUFFOON PICK WITH ONLY OFF-TYPE JOKERS (7778_P5K9ADR2 skipped Crafty/Devious and died jokerless at the ante-1
  boss): take the harmless one (Crafty/Devious/Crazy/Droll/Runner) over `skippack` - ante 1-2 hands make flushes and
  straights often, and it sells for $2-3 when a real scorer appears. `shopadvise` now proposes SELL-then-BUY of such a
  dead-weight joker whenever you own no scorer and the shop's scoring joker is $1-3 out of reach.
- RESCUE TAROT now outranks every pack from ante 3 on when you hold none (five ante-3/4 losses ended on a forced final
  hand with no Death/Strength/Justice while the shop had one for $3).
- STONE FILLERS are now part of the `hands`/`advise` candidate line (idx list and est), so the ADVICE est matches the `play`
  line (7777_VTEKN3IB saw "Pair A est 245" vs play est 745 under The Flint).
- ZERO-SCORER REROLL CAP: `shopadvise` rerolls only while $3 would remain, so the $3 Sly/Jolly the reroll reveals is still
  affordable (7781_MCBMZ8ED rerolled to $0 and watched a $3 Sly Joker appear). Blackboard / Seeing Double / Flower Pot /
  Driver's License / Joker Stencil almost never fire on a pair-family build: they are no longer "the xMult-shaped buy".
- BLACKBOARD (x3 when every card HELD is a Spade or Club) is broken by whatever you keep: when it is your only
  multiplier, discard the red cards you are not playing (7782_9WJNUQCD kept a JD for a straight draw and lost 18222/20000
  when the x3 never fired; one hand earlier, keeping all-black held cards turned est 6032 into actual 18096).
- CASH FLOOR WITH NO MULTIPLIER (ante 3+): almost every ante 4-5 loss held zero xMult because every shop was spent to
  $0-3 on packs, so the rare xMult/rescue offer was unaffordable. `shopadvise` now keeps $5 through low-priority buys
  (score < 80) whenever you own no xMult from ante 3 on; planets and rescue tarots are exempt.
- THE EYE: do not open with your strongest hand type - it can only score once; sequence weakest-clearing first
  (7782_XVMRUA8A spent Two Pair L3 first for 2040 and lost 15270/16000).
- THE TOOTH, SURVIVAL OUTRANKS MONEY: play the fewest cards that keep pace, but when the small play cannot keep pace
  with the requirement, play the bigger hand and accept negative money - a lost run never recovers, negative money does
  (7781_MXFJHNPS saved $2 with a 2-card Pair and lost the boss by 1460).
- STAKE 3 (Green Stake) FIRST LOSS (7777_8S1B92B4): ante 4 The Arm 10749/16000 with zero xMult (Mad, Odd Todd,
  Supernova, Even Steven). Green Stake requirements scale faster, so the stake-2 rule "an xMult by ante 4" becomes "an
  xMult by ante 3, and never enter ante 4 with fewer than one". Under The Arm keep a list of hand types not yet played
  this round and rotate through them; repeating a non-main type degrades it to nothing with no fallback.
- DEEPEST RUN BEFORE THE WIN (7779_UNWYPMGM, 2026-08-30): Two Pair L9 + Spare Trousers (+40 mult) + Mad + Abstract + Hiker + Constellation
  x2.8 cleared every blind through ante 8 Big (86k per hand, est within 3%) and lost the ante 8 boss Violet Vessel, which
  needs 300000 (3x the 100000 base). Plan for a 3x final boss: by ante 7 you need ~100k per hand, i.e. one more x2-x3
  (second xMult joker or two Glass cards in the main hand) on top of that build. Justice never appeared in that run,
  so do not rely on a single multiplication source: pursue xMult jokers AND Glass/Steel/Polychrome in parallel.
- OLDER DATA (46 logged shop visits): an xMult joker was offered in ONE of them. Do not build your plan around finding one and
  do not burn money rerolling for it. The reliable scaling is HAND LEVELS: buy the main-hand planet / every Celestial pack
  every shop (each level is roughly +30-40% and never resets), stack flat +mult/+chips that fire on that hand, and keep
  economy for interest. Take an xMult if it appears; treat it as a bonus.
- The other multiplicative path that IS common: card enhancements from Arcana packs. Justice makes a card Glass (x2 mult
  every time it scores; 1/4 chance to shatter), The Chariot makes it Steel (x1.5 while held in hand), Empress = +4 mult,
  Hierophant = +30 chips. Apply them to cards of the ranks your main hand uses (e.g. your Kings/Queens for a pair engine).
  A pair of Glass Kings is x4 by itself. In a pack, give the targets with the pick (`pick N i`); held tarots: `use N i`
  during SELECTING_HAND. Buy Arcana packs from ante 3 on; Standard packs can also offer enhanced/edition cards.
- `play` type words: HIGH, PAIR, TWOPAIR, TRIPS, STRAIGHT, FLUSH, FULLHOUSE, QUADS, STRAIGHTFLUSH, ROYALFLUSH (A-K-Q-J-T
  of one suit), FIVE, FLUSHHOUSE, FLUSHFIVE. A straight of one suit must be played as STRAIGHTFLUSH (or ROYALFLUSH).
- Level math: Pair L1 10x2, L3 40x4, L5 70x6, L7 100x8. Two Pair L1 20x2, L3 60x4, L5 100x6. Full House L1 40x4,
  L3 90x8, L5 140x12. A L5 main hand with +30 mult of flat jokers beats a L1 hand with one x2.

- Reliable xMult beats conditional xMult: The Duo/Trio (type-based), Card Sharp (sequence it), Hologram/Constellation/
  Campfire (grow them), Cavendish, Baron. Blackboard (all held cards black), Flower Pot (all four suits), Seeing Double,
  Loyalty Card (1 in 6 hands), Ancient Joker (rotating suit) rarely fire in practice: never let one be your only xMult.
- If no reliable xMult has appeared by ante 3, take a conditional one that fits your build (Seeing Double with clubs,
  Blackboard with a black-suit deck, The Duo with a pair engine) as a PLACEHOLDER and keep hunting; zero xMult at ante 5 loses.
- Feed growth jokers you own: Constellation needs planets/Celestial packs every shop; Hologram needs cards added (Standard
  packs); Campfire needs sales. A growth joker you never feed is a dead slot.
- The Wall boss DOUBLES the blind requirement (ante 5 boss becomes 44000, ante 6 80000): treat it like a boss one ante later.
  Violet Vessel (ante 8) is x3. Plan levels/xMult for that number before entering.
- When you already hold a made hand that clears its share, PLAY IT (it registers Card Sharp and banks score); do not spend
  discards trying to upgrade a made hand while later hands still need discards.
- Card Sharp: the FIRST hand of a round should register the type you will repeat (cheapest version + fillers); the
  next two hands of that type get x3. Playing three different types wastes it. `advise` now suggests the registration.
- Money left unspent at ante 6+ is a lost run: with $40+ sell utility jokers (Blue Joker, Abstract, economy) and buy flat
  +chips/+mult jokers or hand levels. Base-halving bosses (The Flint) punish builds with no flat adds.
- Supernova, Spare Trousers, Hiker, Wee Joker etc. only grow if you keep repeating the same hand type: commit to one main
  type by ante 3 and level it; keep Pair as the fallback.
- Unused card-targeting tarots (Strength, Justice, Death) can turn a losing final hand into a winning one: `use N i [j]`.

## 7b. Reference builds that went deep (copy the shape, not the exact jokers)

- Full House engine (reached ante 6 boss undefeated, every blind by 1.5-4x): Jolly Joker (+8 mult, fires on the pair inside
  a Full House) + Sly Joker (+50 chips, same) + Supernova (+mult per time played) + Cavendish (x3) + Hologram (xMult grows)
  rightmost, Full House leveled to L6 (Earth planets, Black Hole spectral) with Pair leveled as a boss fallback. Every blind:
  discard aggressively for trips + pair. Weakness: money stayed under $22; needed Egg's sell value as a bank.
- Face-pair engine (orchestrator run, reached ante 8 Big Blind): Smiley Face + Scary Face + Photograph + Card Sharp,
  Pair leveled to L6. Weakness: scaling was Campfire (temporary) and money hit $0; needed a permanent second xMult.
- Ancient Joker + suit flush (Haiku, ante 3 boss): x1.5 per card of the rotating suit on a 5-card flush is x7.5;
  died to The Pillar because every flush card had been played earlier that ante.

## 8. Do-not list

- Never play a hand whose `est` is far below `need` while you still have discards.
- Ante 3+: never reroll to under $10 (ante 1-2: the shopadvise rule above applies; a joker beats the interest floor).
- Never sell your only income joker for a flat +mult joker.
- Never include a card you still need as a filler.
- Never assume a joker is useless because `x_mult` shows 1; read its description.

## 9. Run log (mandatory)

Create `docs/runs/<port>_<run_id>.md` at run start, add one short line after each ante, finish with a post-mortem:

```
# Run <run_id> (port <port>) - <WIN|LOSS at ante N blind X>
Ante N: jokers [...], $money, levels {...}, buys/skips, hands and scores (from `est` and actual).
...
Post-mortem: binding constraint (money / scaling / boss / luck / misplay)? Which decision would you change?
Bridge issues: failed or odd actions with exact error text.
Playbook suggestions: 1-3 concrete rules to add or change.
```
