# Blackjack trainer

A terminal trainer for perfect basic strategy and card counting. No network, no
dependencies, no install — the whole thing is the Python standard library, which
is the point: it is built to be used on a plane.

```
python3 blackjack/bj          # or: cd blackjack && python3 -m bjtrainer
```

Needs Python 3.9+ and a terminal at least 72x20. Colour and box-drawing
characters are used when available and quietly dropped when not
(`BJTRAINER_ASCII=1` forces plain ASCII).

## What it does

**1 · Basic strategy drill** — a hand and a dealer upcard, you play it, you find
out immediately. Hands are weighted toward the cells you keep getting wrong, so
the drill chases your weak spots instead of re-teaching you 20 vs 6. Set *Drill
hands* to "dealt off a shoe" in settings if you would rather practise realistic
frequencies.

**2 · Count drill** — cards flash past at a speed you control (`+`/`-`, or `m`
for manual). Every 12–26 cards it stops and asks for the running count, and then
the true count, showing you the division it wanted. The shoe reshuffles at the
cut card and the count resets with it.

**3 · Deviation drill** — the Illustrious 18 and Fab 4 index plays. Each hand
comes with a true count near the index, landing on either side of it about
equally often, so you learn the *threshold* rather than the cell.

**4 · Play a shoe** — real hands with splits, doubles, surrender, insurance, a
bet ramp off the count and a bankroll. It flags misplays as you make them
(switchable). `k` hides the count readout so you have to keep it yourself; `c`
asks you to call it.

**5 · Strategy chart** — the whole chart, colour coded, for the current rules.
Reachable with `?` from inside the drills.

**6 · Stats** — accuracy per section and the cells you miss most, saved between
sessions.

**7 · Settings** — decks, S17/H17, DAS, late surrender, 3:2 vs 6:5,
penetration, counting system, and drill behaviour. Rule changes feed straight
through to the charts and to what counts as correct.

## Counting systems

Hi-Lo, KO, Hi-Opt I and Omega II. Hi-Lo is the default and the one the index
plays are built for. KO is unbalanced, so it starts at its usual -4 × (decks-1)
and the trainer never asks you to divide by decks remaining.

## Where the strategy comes from

The charts are not typed in from memory — they are *derived*. `tools/ev.py` is a
composition-dependent expected-value engine (exact dealer distribution with card
removal, the hole-card peek applied, hit/stand/double/split/surrender compared
on EV) and `tools/generate_charts.py` runs it over every cell of a 6-deck shoe:

```
python3 blackjack/tools/generate_charts.py --h17 --margins
python3 blackjack/tools/house_edge.py
```

The output is what ships in `bjtrainer/strategy.py`, and
`tests/test_chart_generation.py` re-derives it on every test run, so the tables
cannot drift from the maths behind them. Both the S17 and H17 charts come out
matching the standard published charts cell for cell, including the cells people
get wrong: 11 vs A hits under S17 and doubles under H17, soft 18 vs 2 stands
under S17 and doubles under H17, A,3 vs 4 hits, 8,8 vs A surrenders under H17.

Independent checks that the engine is sound, all in the test suite: dealer bust
rates by upcard match the published table to within 0.2%, basic strategy's cost
comes out at -0.33% for 6D S17 DAS LS, and each rule is worth what the books say
(H17 -0.20%, DAS +0.14%, late surrender +0.08%). A 20,000-hand autoplay of the
round engine lands on the same number from the other direction.

A note on index plays and surrender: where a cell has both a playing index and a
surrender index, surrender's flat -0.5 wins whenever it is offered. So 16 vs 10
is a surrender at every count at a table with late surrender, and the familiar
"stand at 0" index only matters where surrender is not on offer. The trainer
scores it that way.

## Keys

| Key | Meaning |
| --- | --- |
| `h` `s` `d` `p` `r` | hit, stand, double, split, surrender |
| `?` | strategy chart |
| `c` | call the count |
| `k` | hide/show the count readout (shoe play) |
| `+` `-` `m` | speed up, slow down, manual (count drill) |
| `q` / `Esc` | back, and out |

## Data

Stats and settings live in `~/.local/share/bjtrainer/` (or `$XDG_DATA_HOME`).
Set `BJTRAINER_HOME` to put them somewhere else. Both files are written
atomically and a corrupt one is ignored rather than fatal.

## Layout

```
bjtrainer/
  cards.py      cards, hands, shoe with a cut card
  strategy.py   the generated charts and the lookup
  counting.py   count systems, true count, index plays
  game.py       a round of blackjack, driven a step at a time
  drills.py     scenario generation and cell weighting
  stats.py      per-cell accuracy, persisted
  config.py     settings
  ui.py         curses primitives: colour, card art, input
  app.py        the screens
tools/          the EV engine and chart generator
tests/          173 tests, including chart re-derivation
```

## Tests

```
cd blackjack && python3 -m pytest tests -q
```
