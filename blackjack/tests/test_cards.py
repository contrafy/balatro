import random

import pytest

from bjtrainer.cards import Card, Hand, Shoe, card, hand


def test_hard_and_soft_totals():
    assert hand("A6").total == 17
    assert hand("A6").is_soft
    assert hand("A6").hard_total == 7
    assert hand("A6T").total == 17
    assert not hand("A6T").is_soft
    assert hand("AA").total == 12
    assert hand("AA").is_soft
    assert hand("AAA").total == 13
    assert hand("AAAT").total == 13
    assert not hand("AAAT").is_soft


def test_bust_and_blackjack():
    assert hand("TT2").is_bust
    assert hand("AK").is_blackjack
    assert not hand("A5K").is_blackjack
    split = Hand(hand("AK").cards, from_split=True)
    assert not split.is_blackjack, "21 after a split is not a natural"


def test_pairs_match_on_value_not_rank():
    assert hand("KQ").is_pair
    assert hand("KQ").pair_rank == "T"
    assert hand("88").pair_rank == "8"
    assert hand("AA").pair_rank == "A"
    assert not hand("T9").is_pair


def test_describe():
    assert hand("T6").describe() == "hard 16"
    assert hand("A7").describe() == "soft 18"
    assert hand("88").describe() == "pair of 8s"
    assert hand("AA").describe() == "pair of aces"


def test_card_parsing():
    assert card("As") == Card("A", "s")
    assert card("T").rank == "T"
    with pytest.raises(ValueError):
        card("Z")
    with pytest.raises(ValueError):
        card("Ax")


def test_shoe_composition_and_dealing():
    shoe = Shoe(decks=6, rng=random.Random(0))
    assert shoe.total_cards == 312
    assert shoe.cards_left == 312
    ranks = {}
    for _ in range(312):
        c = shoe.deal()
        ranks[c.rank] = ranks.get(c.rank, 0) + 1
    assert set(ranks.values()) == {24}, "every rank appears 4x6 times"
    assert shoe.cards_left == 0


def test_cut_card_penetration():
    shoe = Shoe(decks=6, penetration=0.5, rng=random.Random(1))
    for _ in range(155):
        shoe.deal()
    assert not shoe.needs_shuffle
    shoe.deal()
    assert shoe.needs_shuffle
    shoe.shuffle()
    assert shoe.cards_left == 312 and not shoe.needs_shuffle
