"""Composition-dependent expected-value engine for shoe blackjack.

Used offline to *generate* the basic-strategy tables that ship in
``bjtrainer/strategy.py`` so the charts are derived rather than remembered.
Index convention: slot 0 is the ace, slots 1..9 are values 2..10 (slot 9
holds all four ten-ranks).
"""

from __future__ import annotations

import functools
from typing import Sequence

ACE = 0
TEN = 9


def fresh_comp(decks: int = 6) -> tuple[int, ...]:
    return tuple([4 * decks] * 9 + [16 * decks])


def remove(comp: Sequence[int], *slots: int) -> tuple[int, ...]:
    c = list(comp)
    for s in slots:
        c[s] -= 1
        if c[s] < 0:
            raise ValueError("removed more cards than the shoe holds")
    return tuple(c)


def slot_value(slot: int) -> int:
    return 1 if slot == ACE else slot + 1


def add_card(total: int, soft: bool, slot: int) -> tuple[int, bool]:
    """Add a card, keeping ``soft`` = "an ace is still counted as 11"."""
    if slot == ACE:
        if total + 11 <= 21:
            return total + 11, True
        return total + 1, soft
    total += slot + 1
    if total > 21 and soft:
        total -= 10
        soft = False
    return total, soft


# --------------------------------------------------------------------------
# Dealer
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _dealer_play(total: int, soft: bool, comp: tuple[int, ...], h17: bool) -> tuple[float, ...]:
    """Distribution over final totals: (17, 18, 19, 20, 21, bust)."""
    if total > 21:
        return (0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    if total > 17 or (total == 17 and not (soft and h17)):
        out = [0.0] * 6
        out[total - 17] = 1.0
        return tuple(out)

    n = sum(comp)
    acc = [0.0] * 6
    for slot, count in enumerate(comp):
        if not count:
            continue
        p = count / n
        t2, s2 = add_card(total, soft, slot)
        sub = _dealer_play(t2, s2, remove(comp, slot), h17)
        for i in range(6):
            acc[i] += p * sub[i]
    return tuple(acc)


@functools.lru_cache(maxsize=None)
def dealer_dist(up: int, comp: tuple[int, ...], h17: bool, peek: bool = True) -> tuple[float, ...]:
    """Dealer final-total distribution given the upcard, conditioned on the
    dealer *not* having blackjack (US hole-card peek)."""
    n = sum(comp)
    acc = [0.0] * 6
    weight = 0.0
    for hole, count in enumerate(comp):
        if not count:
            continue
        if peek and ((up == ACE and hole == TEN) or (up == TEN and hole == ACE)):
            continue  # ruled out by the peek
        p = count / n
        t, s = add_card(0, False, up)
        t, s = add_card(t, s, hole)
        sub = _dealer_play(t, s, remove(comp, hole), h17)
        for i in range(6):
            acc[i] += p * sub[i]
        weight += p
    if weight <= 0:
        raise ValueError("dealer has no legal hole card")
    return tuple(a / weight for a in acc)


# --------------------------------------------------------------------------
# Player
# --------------------------------------------------------------------------

def ev_stand(total: int, dist: tuple[float, ...]) -> float:
    if total > 21:
        return -1.0
    ev = dist[5]  # dealer busts
    for i, d in enumerate(dist[:5]):
        dealer = 17 + i
        if total > dealer:
            ev += d
        elif total < dealer:
            ev -= d
    return ev


@functools.lru_cache(maxsize=None)
def ev_hit(total: int, soft: bool, comp: tuple[int, ...], dist: tuple[float, ...]) -> float:
    n = sum(comp)
    ev = 0.0
    for slot, count in enumerate(comp):
        if not count:
            continue
        p = count / n
        t2, s2 = add_card(total, soft, slot)
        if t2 > 21:
            ev -= p
            continue
        stand = ev_stand(t2, dist)
        if t2 == 21:
            ev += p * stand
        else:
            ev += p * max(stand, ev_hit(t2, s2, remove(comp, slot), dist))
    return ev


def ev_double(total: int, soft: bool, comp: tuple[int, ...], dist: tuple[float, ...]) -> float:
    n = sum(comp)
    ev = 0.0
    for slot, count in enumerate(comp):
        if not count:
            continue
        p = count / n
        t2, _ = add_card(total, soft, slot)
        ev += p * 2.0 * (-1.0 if t2 > 21 else ev_stand(t2, dist))
    return ev


def ev_best(total: int, soft: bool, comp: tuple[int, ...], dist: tuple[float, ...],
            can_double: bool) -> float:
    best = max(ev_stand(total, dist), ev_hit(total, soft, comp, dist))
    if can_double:
        best = max(best, ev_double(total, soft, comp, dist))
    return best


def ev_split(pair_slot: int, comp: tuple[int, ...], dist: tuple[float, ...],
             das: bool, max_hands: int = 4) -> float:
    """EV of splitting, as the standard independent-hands approximation.

    Resplitting is modelled by letting a hand that draws another matching card
    turn back into two fresh split hands, up to ``max_hands`` total. Split aces
    draw exactly one card and stand, the near-universal shoe rule.
    """
    n = sum(comp)
    resplit_aces = False

    def one_hand(hands_used: int) -> float:
        ev = 0.0
        for slot, count in enumerate(comp):
            if not count:
                continue
            p = count / n
            if slot == pair_slot and hands_used < max_hands and (
                pair_slot != ACE or resplit_aces
            ):
                ev += p * 2.0 * one_hand(hands_used + 1)
                continue
            t, s = add_card(0, False, pair_slot)
            t, s = add_card(t, s, slot)
            c2 = remove(comp, slot)
            if pair_slot == ACE:
                ev += p * ev_stand(t, dist)
            else:
                ev += p * ev_best(t, s, c2, dist, can_double=das)
        return ev

    return 2.0 * one_hand(2)
