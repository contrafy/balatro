"""Cards, hands, and shoes.

Deliberately dependency-free: this has to run from a laptop at 35,000 feet
with no network and whatever Python the machine already has.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable, Iterator

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K")
SUITS = ("s", "h", "d", "c")
SUIT_GLYPH = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
RED_SUITS = ("h", "d")


def rank_value(rank: str) -> int:
    """Blackjack value of a rank, with the ace counted high (11)."""
    if rank == "A":
        return 11
    if rank in ("T", "J", "Q", "K"):
        return 10
    return int(rank)


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        return rank_value(self.rank)

    @property
    def is_ace(self) -> bool:
        return self.rank == "A"

    @property
    def is_red(self) -> bool:
        return self.suit in RED_SUITS

    def label(self, unicode_suits: bool = True) -> str:
        suit = SUIT_GLYPH[self.suit] if unicode_suits else self.suit.upper()
        return f"{self.rank}{suit}"

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.label()


def card(text: str) -> Card:
    """Parse ``"As"`` / ``"T"`` / ``"9h"`` into a :class:`Card`.

    A missing suit gets a random one, which keeps test and drill code terse.
    """
    text = text.strip()
    if not text:
        raise ValueError("empty card")
    rank = text[0].upper()
    if rank == "1" and text[1:2] == "0":
        rank, text = "T", "T" + text[2:]
    if rank not in RANKS:
        raise ValueError(f"bad rank: {text!r}")
    suit = text[1].lower() if len(text) > 1 else random.choice(SUITS)
    if suit not in SUITS:
        raise ValueError(f"bad suit: {text!r}")
    return Card(rank, suit)


def hand(text: str) -> "Hand":
    """Parse ``"As 8d"`` or ``"A8"`` into a :class:`Hand`."""
    parts = text.split()
    if len(parts) == 1 and len(parts[0]) >= 2 and all(ch.upper() in RANKS for ch in parts[0]):
        parts = list(parts[0])  # "T6" / "AA" is a rank-only shorthand
    return Hand([card(p) for p in parts])


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)
    # Bookkeeping used by the shoe-play screen; drills ignore these.
    bet: float = 0.0
    from_split: bool = False
    doubled: bool = False
    surrendered: bool = False
    stood: bool = False

    def add(self, c: Card) -> "Hand":
        self.cards.append(c)
        return self

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self.cards)

    @property
    def total(self) -> int:
        """Best total that does not bust; the hard total once it would."""
        raw = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.is_ace)
        while raw > 21 and aces:
            raw -= 10
            aces -= 1
        return raw

    @property
    def hard_total(self) -> int:
        return sum(1 if c.is_ace else c.value for c in self.cards)

    @property
    def is_soft(self) -> bool:
        """True when an ace is still being counted as 11."""
        return any(c.is_ace for c in self.cards) and self.hard_total + 10 <= 21

    @property
    def is_bust(self) -> bool:
        return self.total > 21

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21 and not self.from_split

    @property
    def is_pair(self) -> bool:
        """Two cards of equal *value* — T/J/Q/K all pair with each other."""
        return len(self.cards) == 2 and self.cards[0].value == self.cards[1].value

    @property
    def pair_rank(self) -> str | None:
        """Canonical rank of a pair: any ten-card reports as ``T``."""
        if not self.is_pair:
            return None
        c = self.cards[0]
        return "T" if c.value == 10 and not c.is_ace else c.rank

    @property
    def is_done(self) -> bool:
        return self.stood or self.surrendered or self.is_bust or self.total == 21

    def label(self, unicode_suits: bool = True) -> str:
        return " ".join(c.label(unicode_suits) for c in self.cards)

    def describe(self) -> str:
        """``"pair of 8s"`` / ``"soft 18"`` / ``"hard 16"`` — for feedback text."""
        if self.is_pair:
            r = self.pair_rank
            return f"pair of {'aces' if r == 'A' else r + 's'}"
        return f"{'soft' if self.is_soft else 'hard'} {self.total}"


class Shoe:
    """A multi-deck shoe with a cut card, dealt from the top."""

    def __init__(
        self,
        decks: int = 6,
        penetration: float = 0.75,
        rng: random.Random | None = None,
    ) -> None:
        if decks < 1:
            raise ValueError("decks must be >= 1")
        if not 0.1 <= penetration <= 1.0:
            raise ValueError("penetration must be in [0.1, 1.0]")
        self.decks = decks
        self.penetration = penetration
        self.rng = rng or random.Random()
        self._cards: list[Card] = []
        self.dealt: list[Card] = []
        self.shuffle()

    def shuffle(self) -> None:
        self._cards = [Card(r, s) for _ in range(self.decks) for s in SUITS for r in RANKS]
        self.rng.shuffle(self._cards)
        self.dealt = []
        self._cut = int(len(self._cards) * self.penetration)

    @property
    def total_cards(self) -> int:
        return self.decks * 52

    @property
    def cards_left(self) -> int:
        return len(self._cards)

    @property
    def decks_left(self) -> float:
        return self.cards_left / 52.0

    @property
    def needs_shuffle(self) -> bool:
        """True once the cut card has been passed."""
        return len(self.dealt) >= self._cut

    def deal(self) -> Card:
        if not self._cards:
            self.shuffle()
        c = self._cards.pop()
        self.dealt.append(c)
        return c

    def deal_many(self, n: int) -> list[Card]:
        return [self.deal() for _ in range(n)]

    def remove(self, cards: Iterable[Card]) -> None:
        """Pull specific cards out of the shoe (used to force drill scenarios)."""
        for c in cards:
            try:
                self._cards.remove(c)
            except ValueError:
                continue
            self.dealt.append(c)
