"""Scenario generation for the drills.

Two ways to get a hand: deal one off a real shoe (realistic frequencies, so you
practise what you will actually see), or sample a chart cell weighted by the
cells you keep getting wrong (thorough coverage, so nothing hides).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .cards import Card, Hand, Shoe
from .counting import ALL_DEVIATIONS, Counter, Deviation
from .stats import Stats
from .strategy import Rules, UP_LABELS, upcard_index

UP_RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "T", "A")


@dataclass
class Scenario:
    player: Hand
    upcard: Card
    true_count: float = 0.0
    deviation: Deviation | None = None

    @property
    def cell_key(self) -> str:
        return cell_key(self.player, self.upcard)


def cell_key(player: Hand, upcard: Card) -> str:
    up = UP_LABELS[upcard_index(upcard)]
    if player.is_pair:
        return f"pair {player.pair_rank},{player.pair_rank} v {up}"
    kind = "soft" if player.is_soft else "hard"
    return f"{kind} {player.total} v {up}"


# --------------------------------------------------------------------------
# Cell enumeration
# --------------------------------------------------------------------------

def all_cells() -> list[tuple[str, int | str, str]]:
    """Every drillable chart cell: (kind, total-or-rank, dealer upcard)."""
    cells: list[tuple[str, int | str, str]] = []
    for up in UP_RANKS:
        # Hard 20 is only ever T,T off two cards, so it lives in the pair rows.
        for total in range(5, 20):
            cells.append(("hard", total, up))
        for kicker in range(2, 10):
            cells.append(("soft", 11 + kicker, up))
        for rank in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "T"):
            cells.append(("pair", rank, up))
    return cells


CELLS = all_cells()


def key_for_cell(cell: tuple[str, int | str, str]) -> str:
    kind, total, up = cell
    if kind == "pair":
        return f"pair {total},{total} v {up}"
    return f"{kind} {total} v {up}"


def _random_rank(value: int, rng: random.Random) -> str:
    if value == 10:
        return rng.choice(("T", "J", "Q", "K"))
    return str(value)


def cards_for_cell(cell: tuple[str, int | str, str], rng: random.Random) -> Hand:
    """Build a concrete two-card hand for a chart cell."""
    kind, total, _ = cell
    if kind == "pair":
        rank = str(total)
        if rank == "T":
            return Hand([Card(_random_rank(10, rng), s) for s in rng.sample("shdc", 2)])
        return Hand([Card(rank, s) for s in rng.sample("shdc", 2)])
    if kind == "soft":
        kicker = int(total) - 11
        cards = [Card("A", rng.choice("shdc")), Card(str(kicker), rng.choice("shdc"))]
        rng.shuffle(cards)
        return Hand(cards)

    t = int(total)
    # Hard total from two non-ace cards that are not a pair (pairs get their own row).
    options = [
        (a, t - a) for a in range(2, 11)
        if 2 <= t - a <= 10 and a != t - a
    ]
    if not options:
        options = [(a, t - a) for a in range(2, 11) if 2 <= t - a <= 10]
    a, b = rng.choice(options)
    cards = [
        Card(_random_rank(a, rng), rng.choice("shdc")),
        Card(_random_rank(b, rng), rng.choice("shdc")),
    ]
    rng.shuffle(cards)
    return Hand(cards)


# --------------------------------------------------------------------------
# Generators
# --------------------------------------------------------------------------

def weighted_scenario(stats: Stats, rng: random.Random,
                      counter: Counter | None = None) -> Scenario:
    """Sample a chart cell, biased toward the ones you keep missing."""
    weights = [stats.weight(key_for_cell(c)) for c in CELLS]
    cell = rng.choices(CELLS, weights=weights, k=1)[0]
    player = cards_for_cell(cell, rng)
    up_rank = cell[2]
    upcard = Card(_random_rank(10, rng) if up_rank == "T" else up_rank,
                  rng.choice("shdc"))
    tc = counter.true_count if counter else 0.0
    return Scenario(player, upcard, tc)


def dealt_scenario(shoe: Shoe, counter: Counter | None = None) -> Scenario:
    """Deal a real hand off the shoe: realistic frequencies, real count."""
    if shoe.needs_shuffle:
        shoe.shuffle()
        if counter:
            counter.reset()
    cards = shoe.deal_many(3)  # two player cards, one dealer upcard
    if counter:
        counter.see(cards)
    player = Hand(cards[:2])
    return Scenario(player, cards[2], counter.true_count if counter else 0.0)


def deviation_scenario(rng: random.Random, rules: Rules,
                       include_fab4: bool = True) -> Scenario:
    """A hand sitting on an index play, with a count near the index.

    Half the time the count lands on the deviation side and half the time it
    does not, so the drill teaches the threshold rather than the cell.
    """
    devs = [d for d in ALL_DEVIATIONS if d.kind != "insurance"
            and (include_fab4 or d.group != "Fab4")]
    dev = rng.choice(devs)
    cell = (dev.kind, dev.total if dev.kind == "pair" else int(dev.total), dev.up)
    player = cards_for_cell(cell, rng)
    upcard = Card(_random_rank(10, rng) if dev.up == "T" else dev.up, rng.choice("shdc"))

    offset = rng.choice((-2, -1, -1, 0, 0, 1, 1, 2))
    tc = float(dev.index + offset)
    return Scenario(player, upcard, tc, deviation=dev)
