"""Basic strategy for shoe blackjack.

The tables below are *generated*, not remembered: ``tools/generate_charts.py``
derives them from the composition-dependent EV engine in ``tools/ev.py`` for a
6-deck shoe, and ``tests/test_strategy.py`` pins the well-known cells. Both the
S17 and H17 charts reproduce the standard published charts cell for cell.

Chart codes
-----------
``H``   hit                    ``S``   stand
``D``   double, else hit       ``Ds``  double, else stand
``P``   split                  ``Ph``  split if DAS, else hit
``Ps``  split if DAS, else stand
``Rh``  surrender, else hit    ``Rs``  surrender, else stand
``Rp``  surrender, else split

Columns run 2, 3, 4, 5, 6, 7, 8, 9, T, A.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Card, Hand

HIT = "H"
STAND = "S"
DOUBLE = "D"
SPLIT = "P"
SURRENDER = "R"

ACTION_NAMES = {
    HIT: "Hit",
    STAND: "Stand",
    DOUBLE: "Double",
    SPLIT: "Split",
    SURRENDER: "Surrender",
}

CODE_NAMES = {
    "H": "Hit",
    "S": "Stand",
    "D": "Double (hit if you cannot)",
    "Ds": "Double (stand if you cannot)",
    "P": "Split",
    "Ph": "Split if DAS (hit if not)",
    "Ps": "Split if DAS (stand if not)",
    "Rh": "Surrender (hit if not offered)",
    "Rs": "Surrender (stand if not offered)",
    "Rp": "Surrender (split if not offered)",
}

UP_LABELS = ("2", "3", "4", "5", "6", "7", "8", "9", "T", "A")


@dataclass(frozen=True)
class Rules:
    """Table rules. Defaults are a typical 6-deck shoe game."""

    decks: int = 6
    h17: bool = False           # dealer hits soft 17
    das: bool = True            # double after split allowed
    surrender: bool = True      # late surrender offered
    resplit_to: int = 4         # max hands from splitting
    resplit_aces: bool = False
    penetration: float = 0.75
    blackjack_pays: float = 1.5

    @property
    def label(self) -> str:
        bits = [
            f"{self.decks}D",
            "H17" if self.h17 else "S17",
            "DAS" if self.das else "NoDAS",
            "LS" if self.surrender else "NoSur",
            "6:5" if abs(self.blackjack_pays - 1.2) < 1e-9 else "3:2",
        ]
        return " ".join(bits)


def upcard_index(up: Card | str) -> int:
    """Column index for a dealer upcard: 0 for a 2 ... 8 for a ten, 9 for an ace."""
    rank = up if isinstance(up, str) else up.rank
    rank = rank.upper()
    if rank == "A":
        return 9
    if rank in ("T", "J", "Q", "K", "10"):
        return 8
    return int(rank) - 2


HARD_S17 = {
    5: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    6: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    7: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    8: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    9: ('H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    10: ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'),
    11: ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H'),
    12: ('H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    13: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    14: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    15: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'Rh', 'H'),
    16: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'Rh', 'Rh', 'Rh'),
    17: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    18: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    19: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    20: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

SOFT_S17 = {
    2: ('H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    3: ('H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    4: ('H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    5: ('H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    6: ('H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    7: ('S', 'Ds', 'Ds', 'Ds', 'Ds', 'S', 'S', 'H', 'H', 'H'),
    8: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    9: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

PAIR_S17 = {
    "A": ('P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'),
    "2": ('Ph', 'Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "3": ('Ph', 'Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "4": ('H', 'H', 'H', 'Ph', 'Ph', 'H', 'H', 'H', 'H', 'H'),
    "5": ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'),
    "6": ('Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H', 'H'),
    "7": ('P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "8": ('P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'),
    "9": ('P', 'P', 'P', 'P', 'P', 'S', 'P', 'P', 'S', 'S'),
    "T": ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

HARD_H17 = {
    5: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    6: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    7: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    8: ('H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'),
    9: ('H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    10: ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'),
    11: ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D'),
    12: ('H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    13: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    14: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'),
    15: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'Rh', 'Rh'),
    16: ('S', 'S', 'S', 'S', 'S', 'H', 'H', 'Rh', 'Rh', 'Rh'),
    17: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'Rs'),
    18: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    19: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
    20: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

SOFT_H17 = {
    2: ('H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    3: ('H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    4: ('H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    5: ('H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    6: ('H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'),
    7: ('Ds', 'Ds', 'Ds', 'Ds', 'Ds', 'S', 'S', 'H', 'H', 'H'),
    8: ('S', 'S', 'S', 'S', 'Ds', 'S', 'S', 'S', 'S', 'S'),
    9: ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

PAIR_H17 = {
    "A": ('P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'),
    "2": ('Ph', 'Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "3": ('Ph', 'Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "4": ('H', 'H', 'H', 'Ph', 'Ph', 'H', 'H', 'H', 'H', 'H'),
    "5": ('D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'),
    "6": ('Ph', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H', 'H'),
    "7": ('P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'),
    "8": ('P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'Rp'),
    "9": ('P', 'P', 'P', 'P', 'P', 'S', 'P', 'P', 'S', 'S'),
    "T": ('S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'),
}

def chart_code(player: Hand, up: Card | str, rules: Rules) -> str:
    """The raw chart entry for this hand, before rule/legality fallbacks."""
    col = upcard_index(up)
    hard = HARD_H17 if rules.h17 else HARD_S17
    soft = SOFT_H17 if rules.h17 else SOFT_S17
    pair = PAIR_H17 if rules.h17 else PAIR_S17

    if player.is_pair:
        rank = player.pair_rank
        assert rank is not None
        return pair[rank][col]

    total = player.total
    if player.is_soft and len(player.cards) >= 2:
        kicker = total - 11
        if 2 <= kicker <= 9:
            return soft[kicker][col]
        return STAND if total >= 19 else HIT

    if total >= 21:
        return STAND
    if total <= 4:
        return HIT
    return hard[total][col]


def resolve(code: str, rules: Rules, *, can_double: bool, can_split: bool,
            can_surrender: bool) -> str:
    """Collapse a chart code to a legal action for the situation at hand."""
    if code.startswith("R"):
        if can_surrender:
            return SURRENDER
        rest = code[1:] or "h"
        return resolve({"h": "H", "s": "S", "p": "P"}[rest], rules,
                       can_double=can_double, can_split=can_split,
                       can_surrender=False)
    if code.startswith("P"):
        needs_das = len(code) > 1
        if can_split and (not needs_das or rules.das):
            return SPLIT
        if code == "Ph":
            return HIT
        if code == "Ps":
            return STAND
        # A plain "P" we cannot take: fall back to playing the total.
        return HIT
    if code.startswith("D"):
        if can_double:
            return DOUBLE
        return STAND if code == "Ds" else HIT
    return code


def legality(player: Hand, rules: Rules, hands_in_play: int = 1) -> dict[str, bool]:
    """What the player is actually allowed to do right now."""
    two_cards = len(player.cards) == 2
    can_split = (
        player.is_pair
        and hands_in_play < rules.resplit_to
        and (player.pair_rank != "A" or not player.from_split or rules.resplit_aces)
    )
    return {
        "can_double": two_cards and (not player.from_split or rules.das),
        "can_split": can_split,
        "can_surrender": rules.surrender and two_cards and not player.from_split,
    }


def basic_action(player: Hand, up: Card | str, rules: Rules,
                 hands_in_play: int = 1) -> str:
    """The correct basic-strategy action, given what is legal right now."""
    return resolve(chart_code(player, up, rules), rules,
                   **legality(player, rules, hands_in_play))


def chart_rows(rules: Rules) -> list[tuple[str, str, tuple[str, ...]]]:
    """(section, row label, codes) for every chart row, for the review screen."""
    hard = HARD_H17 if rules.h17 else HARD_S17
    soft = SOFT_H17 if rules.h17 else SOFT_S17
    pair = PAIR_H17 if rules.h17 else PAIR_S17
    rows: list[tuple[str, str, tuple[str, ...]]] = []
    for total in range(8, 18):
        rows.append(("Hard totals", str(total), hard[total]))
    for kicker in range(2, 10):
        rows.append(("Soft totals", f"A,{kicker}", soft[kicker]))
    for rank in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "T"):
        rows.append(("Pairs", f"{rank},{rank}", pair[rank]))
    return rows
