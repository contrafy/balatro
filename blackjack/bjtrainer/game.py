"""A playable round of shoe blackjack, driven a step at a time by the UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Hand, Shoe
from .counting import Counter
from .strategy import (
    DOUBLE,
    HIT,
    SPLIT,
    STAND,
    SURRENDER,
    Rules,
    legality,
)

INSURANCE = "insurance"
PLAYER = "player"
DEALER = "dealer"
DONE = "done"


@dataclass
class Settlement:
    hand: Hand
    result: str      # "win" | "lose" | "push" | "blackjack" | "surrender"
    payout: float    # net change to the bankroll


@dataclass
class Round:
    """One hand of blackjack from bet to settlement.

    The dealer's hole card is dealt face down and only reaches the counter when
    it is turned over, so practising the count against this stays honest.
    """

    shoe: Shoe
    rules: Rules
    counter: Counter
    bet: float = 1.0

    dealer: Hand = field(default_factory=Hand)
    hands: list[Hand] = field(default_factory=list)
    active: int = 0
    state: str = INSURANCE
    insurance_bet: float = 0.0
    hole_shown: bool = False
    settlements: list[Settlement] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    # -- setup -------------------------------------------------------------
    def start(self) -> None:
        player = Hand(bet=self.bet)
        player.add(self._draw())
        self.dealer.add(self._draw())
        player.add(self._draw())
        self.dealer.cards.append(self.shoe.deal())  # hole card stays unseen
        self.hands = [player]
        self.active = 0
        self.state = INSURANCE if self.offers_insurance else PLAYER
        if self.state == PLAYER:
            self._check_naturals()

    def _draw(self) -> Card:
        c = self.shoe.deal()
        self.counter.see(c)
        return c

    @property
    def upcard(self) -> Card:
        return self.dealer.cards[0]

    @property
    def hole_card(self) -> Card:
        return self.dealer.cards[1]

    @property
    def offers_insurance(self) -> bool:
        return self.upcard.is_ace

    @property
    def hand(self) -> Hand:
        return self.hands[self.active]

    def legal(self) -> dict[str, bool]:
        return legality(self.hand, self.rules, len(self.hands))

    # -- insurance / naturals ---------------------------------------------
    def take_insurance(self, take: bool) -> str:
        if self.state != INSURANCE:
            return ""
        self.insurance_bet = self.bet / 2.0 if take else 0.0
        self.state = PLAYER
        msg = "Insurance taken." if take else "No insurance."
        self._check_naturals()
        return msg

    def _reveal_hole(self) -> None:
        if not self.hole_shown:
            self.counter.see(self.hole_card)
            self.hole_shown = True

    def _check_naturals(self) -> None:
        """Resolve immediately if either side has a natural."""
        if self.dealer.is_blackjack:
            self._reveal_hole()
            self.state = DONE
            self._settle()
        elif self.hands[0].is_blackjack:
            self.state = DONE
            self._settle()

    # -- player actions ----------------------------------------------------
    def act(self, action: str) -> str:
        if self.state != PLAYER:
            return ""
        hand, legal = self.hand, self.legal()

        if action == HIT:
            hand.add(self._draw())
            if hand.is_bust:
                self._advance()
                return "Bust."
            return ""
        if action == STAND:
            hand.stood = True
            self._advance()
            return ""
        if action == DOUBLE:
            if not legal["can_double"]:
                return "Cannot double here."
            hand.bet *= 2
            hand.doubled = True
            hand.add(self._draw())
            hand.stood = True
            self._advance()
            return "Bust." if hand.is_bust else ""
        if action == SURRENDER:
            if not legal["can_surrender"]:
                return "Cannot surrender here."
            hand.surrendered = True
            self._advance()
            return "Surrendered."
        if action == SPLIT:
            if not legal["can_split"]:
                return "Cannot split here."
            return self._split()
        return ""

    def _split(self) -> str:
        hand = self.hand
        moved = hand.cards.pop()
        hand.from_split = True
        new = Hand([moved], bet=hand.bet, from_split=True)
        self.hands.insert(self.active + 1, new)
        hand.add(self._draw())
        new.add(self._draw())
        if moved.is_ace:
            # Split aces take one card each and stand, bar a resplit.
            for h in (hand, new):
                if not (self.rules.resplit_aces and h.is_pair):
                    h.stood = True
            self._advance()
            return "Split aces: one card each."
        if hand.is_done:
            self._advance()
        return "Split."

    def _advance(self) -> None:
        while self.active < len(self.hands):
            if not self.hands[self.active].is_done:
                return
            self.active += 1
            if self.active < len(self.hands) and len(self.hands[self.active]) < 2:
                self.hands[self.active].add(self._draw())
                continue
        self.state = DEALER

    # -- dealer ------------------------------------------------------------
    def dealer_should_hit(self) -> bool:
        total = self.dealer.total
        if total < 17:
            return True
        return total == 17 and self.dealer.is_soft and self.rules.h17

    def dealer_step(self) -> bool:
        """Turn over the hole card, then draw one card. True while still drawing."""
        if not self.hole_shown:
            self._reveal_hole()
            return self.dealer_should_hit() and self._players_left()
        if self.dealer_should_hit() and self._players_left():
            self.dealer.add(self._draw())
            return self.dealer_should_hit()
        return False

    def _players_left(self) -> bool:
        """The dealer only draws if some hand can still be beaten."""
        return any(not (h.is_bust or h.surrendered) for h in self.hands)

    def finish_dealer(self) -> None:
        self._reveal_hole()
        while self.dealer_should_hit() and self._players_left():
            self.dealer.add(self._draw())
        self.state = DONE
        self._settle()

    # -- settlement --------------------------------------------------------
    def _settle(self) -> None:
        self.settlements = []
        dealer_total = self.dealer.total
        dealer_bj = self.dealer.is_blackjack
        dealer_bust = self.dealer.is_bust

        if self.insurance_bet:
            self.settlements.append(
                Settlement(self.dealer, "insurance",
                           self.insurance_bet * 2 if dealer_bj else -self.insurance_bet)
            )

        for hand in self.hands:
            if hand.surrendered:
                self.settlements.append(Settlement(hand, "surrender", -hand.bet / 2))
            elif hand.is_blackjack and not dealer_bj:
                self.settlements.append(
                    Settlement(hand, "blackjack", hand.bet * self.rules.blackjack_pays)
                )
            elif dealer_bj:
                self.settlements.append(
                    Settlement(hand, "push" if hand.is_blackjack else "lose",
                               0.0 if hand.is_blackjack else -hand.bet)
                )
            elif hand.is_bust:
                self.settlements.append(Settlement(hand, "lose", -hand.bet))
            elif dealer_bust or hand.total > dealer_total:
                self.settlements.append(Settlement(hand, "win", hand.bet))
            elif hand.total < dealer_total:
                self.settlements.append(Settlement(hand, "lose", -hand.bet))
            else:
                self.settlements.append(Settlement(hand, "push", 0.0))

    @property
    def net(self) -> float:
        return sum(s.payout for s in self.settlements)
