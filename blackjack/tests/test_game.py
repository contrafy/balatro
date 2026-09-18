import random

import pytest

from bjtrainer.cards import Shoe, card
from bjtrainer.counting import HI_LO, Counter
from bjtrainer.game import DEALER, DONE, INSURANCE, PLAYER, Round
from bjtrainer.strategy import DOUBLE, HIT, SPLIT, STAND, SURRENDER, Rules, basic_action


class StackedShoe(Shoe):
    """A shoe that deals a scripted sequence, then falls back to random."""

    def __init__(self, script, decks=6):
        super().__init__(decks=decks, rng=random.Random(0))
        self.script = [card(c) for c in script]

    def deal(self):
        if self.script:
            c = self.script.pop(0)
            self.dealt.append(c)
            self._cards.remove(c) if c in self._cards else None
            return c
        return super().deal()


def make_round(script, rules=None, bet=10.0):
    rules = rules or Rules()
    shoe = StackedShoe(script)
    rnd = Round(shoe, rules, Counter(HI_LO, rules.decks), bet)
    rnd.start()
    return rnd


def test_deal_order_is_player_dealer_player_hole():
    rnd = make_round(["As", "5h", "9d", "Tc"])
    assert rnd.hands[0].label(False) == "AS 9D"
    assert rnd.upcard.rank == "5"
    assert rnd.hole_card.rank == "T"


def test_hole_card_is_not_counted_until_it_turns_over():
    # Player 7,7; dealer shows 9 over a ten, so the dealer stands on 19 and no
    # further cards muddy the count.
    rnd = make_round(["7s", "9h", "7d", "Tc"])
    assert rnd.counter.running == 0, "only the three face-up cards count"
    rnd.act(STAND)
    rnd.finish_dealer()
    assert rnd.dealer.total == 19
    assert rnd.counter.running == -1, "the hole card joins the count when shown"


def test_player_blackjack_pays_three_to_two():
    rnd = make_round(["As", "9h", "Kd", "7c"])
    assert rnd.state == DONE
    assert rnd.net == pytest.approx(15.0)


def test_blackjack_pushes_against_a_dealer_natural():
    rnd = make_round(["As", "Th", "Kd", "Ac"])
    assert rnd.state == DONE, "the peek settles it before anyone acts"
    assert rnd.net == pytest.approx(0.0)


def test_dealer_natural_beats_a_plain_twenty():
    rnd = make_round(["Ts", "Th", "Kd", "Ac"])
    assert rnd.state == DONE
    assert rnd.net == pytest.approx(-10.0)


def test_insurance_pays_two_to_one_against_a_natural():
    rnd = make_round(["Ts", "Ah", "Kd", "Tc"])
    rnd.take_insurance(True)
    assert rnd.state == DONE
    # Lose 10 on the hand, win 10 on the 5-unit insurance bet.
    assert rnd.net == pytest.approx(0.0)


def test_insurance_loses_when_the_dealer_has_no_natural():
    rnd = make_round(["Ts", "Ah", "Kd", "5c", "6d"])
    rnd.take_insurance(True)
    assert rnd.state == PLAYER
    rnd.act(STAND)
    rnd.finish_dealer()
    # Dealer A,5,6 = 12, must keep drawing; insurance is lost either way.
    assert any(s.result == "insurance" and s.payout == -5.0 for s in rnd.settlements)


def test_double_doubles_the_bet_and_takes_exactly_one_card():
    rnd = make_round(["6s", "9h", "5d", "8c", "9s"])
    assert rnd.hands[0].total == 11
    rnd.act(DOUBLE)
    assert rnd.hands[0].bet == 20.0
    assert len(rnd.hands[0].cards) == 3
    assert rnd.state == DEALER


def test_surrender_returns_half_the_bet():
    rnd = make_round(["Ts", "9h", "6d", "8c"])
    rnd.act(SURRENDER)
    assert rnd.state == DEALER
    rnd.finish_dealer()
    assert rnd.net == pytest.approx(-5.0)


def test_surrender_is_only_offered_on_the_first_two_cards():
    rnd = make_round(["Ts", "9h", "4d", "2c", "2h"])
    rnd.act(HIT)
    assert not rnd.legal()["can_surrender"]
    assert rnd.act(SURRENDER) == "Cannot surrender here."


def test_split_makes_two_hands_each_with_its_own_bet():
    rnd = make_round(["8s", "9h", "8d", "7c", "3h", "2d"])
    rnd.act(SPLIT)
    assert len(rnd.hands) == 2
    assert [len(h.cards) for h in rnd.hands] == [2, 2]
    assert all(h.bet == 10.0 for h in rnd.hands)
    assert all(h.from_split for h in rnd.hands)


def test_split_aces_take_one_card_each_and_stop():
    rnd = make_round(["As", "9h", "Ad", "7c", "Kh", "Qd"])
    rnd.act(SPLIT)
    assert rnd.state == DEALER, "no further action on split aces"
    assert [h.total for h in rnd.hands] == [21, 21]
    assert not any(h.is_blackjack for h in rnd.hands), "21 after a split is not a natural"
    rnd.finish_dealer()
    assert rnd.net == pytest.approx(20.0), "paid even money, not 3:2"


def test_resplit_limit_is_enforced():
    rules = Rules(resplit_to=2)
    shoe = StackedShoe(["8s", "9h", "8d", "8c", "8h"])
    rnd = Round(shoe, rules, Counter(HI_LO, 6), 10.0)
    rnd.start()
    rnd.act(SPLIT)
    assert len(rnd.hands) == 2
    assert not rnd.legal()["can_split"]


def test_busting_every_hand_skips_the_dealer_draw():
    rnd = make_round(["Ts", "6h", "6d", "9c", "Kh"])
    rnd.act(HIT)  # 16 + K = bust
    assert rnd.state == DEALER
    before = len(rnd.dealer.cards)
    rnd.finish_dealer()
    assert len(rnd.dealer.cards) == before, "dealer does not draw to a busted table"
    assert rnd.net == pytest.approx(-10.0)


def test_dealer_stands_on_soft_17_under_s17():
    rnd = make_round(["Ts", "Ah", "8d", "6c"], rules=Rules(h17=False))
    rnd.take_insurance(False)
    rnd.act(STAND)
    rnd.finish_dealer()
    assert rnd.dealer.total == 17
    assert len(rnd.dealer.cards) == 2
    assert rnd.net == pytest.approx(10.0)


def test_dealer_hits_soft_17_under_h17():
    rnd = make_round(["Ts", "Ah", "8d", "6c", "2s"], rules=Rules(h17=True))
    rnd.take_insurance(False)
    rnd.act(STAND)
    rnd.finish_dealer()
    assert rnd.dealer.total == 19
    assert rnd.net == pytest.approx(-10.0)


def test_push():
    rnd = make_round(["Ts", "9h", "9d", "Tc"])
    rnd.act(STAND)
    rnd.finish_dealer()
    assert rnd.net == pytest.approx(0.0)
    assert rnd.settlements[0].result == "push"


def test_basic_strategy_over_many_hands_lands_near_the_known_edge():
    """A long autoplay should sit within a percent of the book figure."""
    rules = Rules()
    rng = random.Random(4)
    shoe = Shoe(rules.decks, rules.penetration, rng)
    counter = Counter(HI_LO, rules.decks)
    bank = 0.0
    rounds = 20000
    for _ in range(rounds):
        if shoe.needs_shuffle:
            shoe.shuffle()
            counter.reset()
        rnd = Round(shoe, rules, counter, 1.0)
        rnd.start()
        if rnd.state == INSURANCE:
            rnd.take_insurance(False)
        guard = 0
        while rnd.state == PLAYER and guard < 40:
            guard += 1
            rnd.act(basic_action(rnd.hand, rnd.upcard, rules, len(rnd.hands)))
        assert guard < 40, "player loop failed to terminate"
        if rnd.state == DEALER:
            rnd.finish_dealer()
        bank += rnd.net
    edge = bank / rounds
    assert -0.03 < edge < 0.02, f"basic strategy EV per hand was {edge:+.4f}"


def test_no_round_ever_hangs_or_leaves_a_hand_unsettled():
    rules = Rules(h17=True)
    rng = random.Random(9)
    shoe = Shoe(rules.decks, rules.penetration, rng)
    counter = Counter(HI_LO, rules.decks)
    for _ in range(3000):
        if shoe.needs_shuffle:
            shoe.shuffle()
            counter.reset()
        rnd = Round(shoe, rules, counter, 1.0)
        rnd.start()
        if rnd.state == INSURANCE:
            rnd.take_insurance(rng.random() < 0.2)
        guard = 0
        while rnd.state == PLAYER and guard < 60:
            guard += 1
            legal = rnd.legal()
            choices = [HIT, STAND]
            if legal["can_double"]:
                choices.append(DOUBLE)
            if legal["can_split"]:
                choices.append(SPLIT)
            if legal["can_surrender"]:
                choices.append(SURRENDER)
            rnd.act(rng.choice(choices))
        assert rnd.state in (DEALER, DONE)
        if rnd.state == DEALER:
            rnd.finish_dealer()
        assert rnd.state == DONE
        hand_settlements = [s for s in rnd.settlements if s.result != "insurance"]
        assert len(hand_settlements) == len(rnd.hands)
        assert all(h.total <= 21 or h.is_bust for h in rnd.hands)


def test_insurance_is_only_offered_against_an_ace():
    rnd = make_round(["9s", "Th", "7d", "5c"])
    assert rnd.state == PLAYER
    assert rnd.take_insurance(True) == ""
    assert rnd.insurance_bet == 0.0
