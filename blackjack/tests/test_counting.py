import random

import pytest

from bjtrainer.cards import Card, card, hand
from bjtrainer.counting import (
    ALL_DEVIATIONS,
    HI_LO,
    KO,
    SYSTEMS,
    Counter,
    bet_units,
    counting_action,
    deviations_for,
    should_insure,
)
from bjtrainer.strategy import DOUBLE, HIT, SPLIT, STAND, SURRENDER, Rules

S17 = Rules()
H17 = Rules(h17=True)
NO_SUR = Rules(surrender=False)


@pytest.mark.parametrize("system", [s for s in SYSTEMS if s.balanced])
def test_balanced_systems_sum_to_zero_over_a_deck(system):
    total = sum(system.tag(Card(r, s)) for r in "A23456789TJQK" for s in "shdc")
    assert total == 0, f"{system.name} is meant to be balanced"


def test_ko_is_unbalanced_by_four_per_deck():
    total = sum(KO.tag(Card(r, s)) for r in "A23456789TJQK" for s in "shdc")
    assert total == 4
    assert Counter(KO, decks=6).running == -20
    assert Counter(KO, decks=1).running == 0


def test_hi_lo_tags():
    assert [HI_LO.tag(card(r)) for r in "23456"] == [1] * 5
    assert [HI_LO.tag(card(r)) for r in "789"] == [0] * 3
    assert [HI_LO.tag(card(r)) for r in "TJQKA"] == [-1] * 5


def test_faces_track_the_ten():
    for system in SYSTEMS:
        for face in "JQK":
            assert system.tag(card(face)) == system.tag(card("T")), system.name


def test_running_count_tracks_cards_seen():
    c = Counter(HI_LO, decks=6)
    c.see([card("5"), card("6"), card("K")])
    assert c.running == 1
    assert c.seen == 3


def test_true_count_divides_by_decks_remaining():
    c = Counter(HI_LO, decks=6)
    c.running, c.seen = 6, 156  # three decks gone
    assert c.decks_remaining == pytest.approx(3.0)
    assert c.true_count == pytest.approx(2.0)


def test_true_count_floors_toward_zero():
    c = Counter(HI_LO, decks=6)
    c.running, c.seen = 7, 156
    assert c.true_count == pytest.approx(7 / 3)
    assert c.true_count_floor == 2
    c.running = -7
    assert c.true_count_floor == -2


def test_unbalanced_system_reports_the_running_count():
    c = Counter(KO, decks=6)
    c.see([card("7")] * 5)
    assert c.true_count == float(c.running)


def test_counter_resets_with_the_shoe():
    c = Counter(HI_LO, decks=6)
    c.see([card("5")] * 10)
    c.reset()
    assert c.running == 0 and c.seen == 0


def test_insurance_index():
    assert not should_insure(2.9)
    assert should_insure(3.0)


def test_bet_ramp_stays_flat_at_low_counts():
    assert bet_units(-3) == 1
    assert bet_units(0) == 1
    assert bet_units(1.9) == 1
    assert bet_units(2) == 1
    assert bet_units(3) == 2
    assert bet_units(50) <= 12


# -- index plays ----------------------------------------------------------

@pytest.mark.parametrize("cards,up,tc,rules,expected", [
    # 16 v T: stand from 0 up, but surrender beats both when it is offered.
    ("T6", "T", 0, NO_SUR, STAND),
    ("T6", "T", -1, NO_SUR, HIT),
    ("T6", "T", 5, S17, SURRENDER),
    # 12 v 3 and 12 v 2 stand at their indices.
    ("T2", "3", 2, S17, STAND),
    ("T2", "3", 1, S17, HIT),
    ("T2", "2", 3, S17, STAND),
    ("T2", "2", 2, S17, HIT),
    # Negative-side indices: drop the stand and take a card.
    ("T3", "2", -1, S17, HIT),
    ("T3", "2", 0, S17, STAND),
    ("T2", "4", 0, S17, HIT),
    ("T2", "4", 1, S17, STAND),
    ("T2", "5", -2, S17, HIT),
    ("T2", "6", -1, S17, HIT),
    ("T3", "3", -2, S17, HIT),
    # Doubling indices.
    ("65", "A", 1, S17, DOUBLE),
    ("65", "A", 0, S17, HIT),
    ("64", "T", 4, S17, DOUBLE),
    ("64", "A", 4, S17, DOUBLE),
    ("54", "2", 1, S17, DOUBLE),
    ("54", "7", 3, S17, DOUBLE),
    ("54", "7", 2, S17, HIT),
    # Splitting tens at a big count.
    ("TT", "5", 5, S17, SPLIT),
    ("TT", "5", 4, S17, STAND),
    ("TT", "6", 4, S17, SPLIT),
    # Fab 4 surrenders.
    ("T4", "T", 3, S17, SURRENDER),
    ("T4", "T", 2, S17, HIT),
    ("T5", "9", 2, S17, SURRENDER),
    ("T5", "9", 1, S17, HIT),
    ("T5", "T", -1, S17, HIT),      # below the index, take the card instead
    ("T5", "T", 0, S17, SURRENDER),
    ("T5", "A", -1, H17, SURRENDER),
    # 15 v T with no surrender falls back to the playing index.
    ("T5", "T", 4, NO_SUR, STAND),
    ("T5", "T", 3, NO_SUR, HIT),
    ("T6", "9", 5, NO_SUR, STAND),
    ("T6", "9", 4, NO_SUR, HIT),
])
def test_index_plays(cards, up, tc, rules, expected):
    got, _ = counting_action(hand(cards), card(up), rules, tc)
    assert got == expected, f"{cards} v {up} at TC {tc:+}: got {got}"


def test_deviations_can_be_switched_off():
    got, dev = counting_action(hand("T2"), card("3"), S17, 5, use_deviations=False)
    assert got == HIT and dev is None


def test_deviation_never_returns_an_illegal_action():
    """A three-card 16 cannot surrender and a non-pair cannot split."""
    got, _ = counting_action(hand("664"), card("T"), S17, 10)
    assert got in (HIT, STAND)
    got, _ = counting_action(hand("T5"), card("T"), S17, 5, hands_in_play=1)
    assert got == SURRENDER


def test_both_indices_on_one_cell_are_reachable():
    devs = deviations_for(hand("T5"), "T", can_surrender=True)
    assert {d.group for d in devs} == {"I18", "Fab4"}
    assert devs[0].group == "Fab4", "surrender gets first refusal"
    assert all(d.group == "I18" for d in deviations_for(hand("T5"), "T",
                                                        can_surrender=False))


def test_every_deviation_is_reachable_from_its_own_cell():
    """Each index play must change the play on one side of its index.

    The playing indices for 15 and 16 are checked without surrender, because a
    flat -0.5 beats what standing buys in those cells whenever it is offered.
    Two Fab 4 entries (15 v T, 15 v A) sit on cells basic strategy already
    surrenders, so their work is done on the *low* side: below the index you
    take the card instead.
    """
    from bjtrainer.drills import cards_for_cell
    from bjtrainer.strategy import basic_action

    rng = random.Random(0)
    for dev in ALL_DEVIATIONS:
        if dev.kind == "insurance":
            continue
        cell = (dev.kind, dev.total if dev.kind == "pair" else int(dev.total), dev.up)
        player = cards_for_cell(cell, rng)
        up = card("T" if dev.up == "T" else dev.up)
        if dev.group == "Fab4":
            rules = H17 if dev.up == "A" else S17
        else:
            rules = NO_SUR

        changed = []
        for offset in (-3, -2, -1, 0, 1, 2, 3):
            tc = dev.index + offset
            got, used = counting_action(player, up, rules, tc)
            basic = basic_action(player, up, rules)
            if used is not None:
                assert got != basic, f"{dev.label} reported a deviation that changed nothing"
                changed.append((tc, got))
            else:
                assert got == basic, f"{dev.label} at TC {tc:+} drifted off basic silently"

        assert changed, f"{dev.label} never changes the play at any count"
        # Everything it changes must land on one consistent side of the index:
        # normally the deviating side, or the far side for a reverse index.
        sides = {dev.applies(tc) for tc, _ in changed}
        assert len(sides) == 1, f"{dev.label} fires on both sides of its index"
        assert sides == ({False} if dev.other else {True})


def test_reverse_surrender_indices_fire_below_the_index():
    """15 v T and 15 v A are surrenders basic already takes; the index tells
    you when to stop taking them."""
    got, dev = counting_action(hand("T5"), card("T"), S17, -1)
    assert got == HIT and dev is not None and dev.group == "Fab4"
    got, dev = counting_action(hand("T5"), card("A"), H17, -2)
    assert got == HIT and dev is not None and dev.group == "Fab4"
