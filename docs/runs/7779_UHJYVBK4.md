# Run UHJYVBK4 (port 7779) - LOSS at ante 3 boss (The Tooth)

Stake 1 (White), Black Deck.

Ante 1: jokers [Clever Joker(+80chips 2pair), Wily Joker(+100chips trips), Scary Face(+30chips/face)], $7 after shop, levels {L1 all}. Small 300 (scored 320: straight 220 + 2pair 100), Big 450 (scored 548: 2pair 280+268), Boss The Manacle 600 (scored 1138: 2pair 388 + trips 750, Wily fired on trips). Shop buys: Clever Joker($4), Buffoon pack->Wily Joker, Scary Face($4). No skips.

Ante 2: jokers +Gluttonous Joker(+3mult/club), main hand solidifying as Three of a Kind (Wily L3 after Venus x2 via Celestial pack + The Fool copying Venus). Small 800 (scored 980: 2pair 396+180+404), Big 1200 (scored 2030 in ONE hand via TRIPS L3, est matched actual), Boss The Goad (spades debuffed, 1600 need, scored 2900 via TRIPS on Jacks). Shop buys: Celestial pack->Venus, The Fool($3, copied Venus, used to re-level Venus->Three of a Kind L3), Gluttonous Joker($5), The World tarot($3, unused - NOUSE outside hand phase). Money stayed low ($0-$3 most shops). No skips.

Ante 3: jokers +Constellation(xMult grows +0.1/planet used, bought $6 in first ante-3 shop but NEVER fed another planet afterward - stayed near x1.0, effectively dead weight for the rest of the run). Small 2000 (scored 2900: overrode `advise` to keep an open-ended straight draw 9-8-7-6 instead of "keep 3 highest cards" - advise doesn't evaluate straight EV per playbook note; drew a T for the straight, then a K-K-K trips came up L3=2900, cleared easily). Big 3000 (scored 3998: trips 1910 + 2pair 520 + 2pair 1568). Shop after Big: $12, shopadvise said LEAVE (interest floor $10, only $2 above) despite Jumbo Celestial Pack ($6) being available - in hindsight this was the wrong call, see post-mortem. Boss The Tooth (-$1 per card played, need 4000): no trips or flush draw materialized in time; scored only 1930 (flush 540 [-$5], 2pair 1010 [-$4], 2pair 380 [-$4] final hand) against 3 hands / 0 discards (both discards spent chasing the flush that only paid 540). Final hand had no way to reach 2450 more needed - forced loss. Money ended at -$3.

GAME_OVER: stake 1, ante 3, boss blind The Tooth, need 4000 scored 1930.

## Post-mortem

Binding constraint: scaling. Three of a Kind was leveled to L3 early (ante 2) via a lucky Fool+Venus double-use, but no further planets were bought in ante 3 despite two shop visits with $7 and $12 respectively - both times `shopadvise` said LEAVE because spend was below the $10 interest floor, but neither visit weighed that a Celestial Pack ($6) would have both leveled the main hand AND fed the otherwise-dead Constellation xMult joker. By The Tooth (ante 3 boss, need 4000), the deck had no flush suit committed (spades were only sometimes live) and the round simply ran out of hands/discards before assembling a strong Three of a Kind.

Decision I would change: at the $12 shop after the ante-3 Big Blind, buy the Jumbo Celestial Pack instead of leaving. It would have leveled Three of a Kind again and started growing Constellation's xMult, which together likely would have closed most of the 2070-chip gap at the boss. Also, in the boss round itself, given only 1 hand and 0 discards remained with need 2450 and best est 380, there was no salvageable line - the mistake was upstream (spending both discards chasing a flush worth only 540 instead of holding one in reserve for the final hand, and not leveling further beforehand).

`est` vs actual accuracy: `est` matched actual scores closely all game (e.g. TRIPS est 2030 -> exact 2030 chips scored; TWOPAIR est 1010 -> exact). No instance differed by more than 20%.

Bridge issues: none. No `ACTION FAILED` or Python errors encountered this run.

Playbook suggestions:
1. `shopadvise`'s interest-floor heuristic should not veto a Celestial Pack purchase when the player owns a "grows +X per planet used" xMult joker (Constellation, Hologram, etc.) that has not been fed since purchase - that pack is effectively an XMULT purchase, not a pure econ tradeoff, and should be exempted from the floor the same way a main-hand level already is.
2. Add an explicit warning/reminder when a "grows on planet use" xMult joker (Constellation/Hologram) has gone an entire ante without a planet being used - it is otherwise easy to buy one, then forget to keep feeding it, leaving a joker slot dead for the rest of the run.
3. Under boss "The Tooth" (-$1/card played), `advise`'s EV comparison between hand types should also factor in cards-played cost (e.g. Two Pair est slightly below Flush est but costing 1 fewer card) since money matters at ante 3+; it already leans this way informally but doesn't state the money delta.
