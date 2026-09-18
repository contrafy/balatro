"""Card-counting systems, true-count conversion, and index plays."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from .cards import Card, Hand
from .strategy import DOUBLE, HIT, SPLIT, STAND, SURRENDER, Rules, basic_action


@dataclass(frozen=True)
class CountSystem:
    name: str
    tags: dict[str, int]
    balanced: bool = True
    level: int = 1
    blurb: str = ""

    def tag(self, card: Card | str) -> int:
        rank = card if isinstance(card, str) else card.rank
        return self.tags.get(rank.upper(), 0)

    def initial_running_count(self, decks: int) -> int:
        """Unbalanced systems start off zero so the pivot lands where it should."""
        if self.balanced:
            return 0
        return -4 * (decks - 1)  # KO's standard IRC


def _tags(plus_one: str = "", plus_two: str = "", minus_one: str = "",
          minus_two: str = "") -> dict[str, int]:
    out: dict[str, int] = {}
    for rank in "A23456789TJQK":
        out[rank] = 0
    for rank in plus_one:
        out[rank] = 1
    for rank in plus_two:
        out[rank] = 2
    for rank in minus_one:
        out[rank] = -1
    for rank in minus_two:
        out[rank] = -2
    # Face cards always track the ten.
    for rank in "JQK":
        out[rank] = out["T"]
    return out


HI_LO = CountSystem(
    "Hi-Lo",
    _tags(plus_one="23456", minus_one="TA"),
    blurb="2-6 = +1, 7-9 = 0, 10-A = -1. The standard; learn this one first.",
)

KO = CountSystem(
    "KO",
    _tags(plus_one="234567", minus_one="TA"),
    balanced=False,
    blurb="Like Hi-Lo but the 7 counts +1. Unbalanced: no true-count division.",
)

HI_OPT_I = CountSystem(
    "Hi-Opt I",
    _tags(plus_one="3456", minus_one="T"),
    blurb="3-6 = +1, 10 = -1, aces neutral. Better for playing, needs an ace side-count.",
)

OMEGA_II = CountSystem(
    "Omega II",
    _tags(plus_one="237", plus_two="456", minus_one="9", minus_two="T"),
    level=2,
    blurb="Level two: 2,3,7 = +1, 4,5,6 = +2, 9 = -1, 10 = -2. Stronger, harder.",
)

SYSTEMS = (HI_LO, KO, HI_OPT_I, OMEGA_II)
SYSTEMS_BY_NAME = {s.name: s for s in SYSTEMS}


@dataclass
class Counter:
    """Running/true count tracker for one shoe."""

    system: CountSystem = HI_LO
    decks: int = 6
    running: int = 0
    seen: int = 0
    quarter_deck_truecount: bool = False

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.running = self.system.initial_running_count(self.decks)
        self.seen = 0

    def see(self, cards: Card | Iterable[Card]) -> None:
        if isinstance(cards, Card):
            cards = [cards]
        for c in cards:
            self.running += self.system.tag(c)
            self.seen += 1

    @property
    def decks_remaining(self) -> float:
        left = max(self.decks * 52 - self.seen, 1)
        return left / 52.0

    @property
    def true_count(self) -> float:
        """Running count per remaining deck (meaningless for unbalanced systems)."""
        if not self.system.balanced:
            return float(self.running)
        remaining = self.decks_remaining
        if self.quarter_deck_truecount:
            remaining = max(round(remaining * 4) / 4, 0.25)
        else:
            remaining = max(round(remaining * 2) / 2, 0.5)
        return self.running / remaining

    @property
    def true_count_floor(self) -> int:
        """True count floored toward zero, which is how index plays are applied."""
        tc = self.true_count
        return math.floor(tc) if tc >= 0 else math.ceil(tc)


# ---------------------------------------------------------------------------
# Index plays
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Deviation:
    """One index play: take ``action`` on the indicated side of ``index``."""

    kind: str            # "hard" | "soft" | "pair" | "insurance"
    total: int | str     # hard/soft total, or the pair rank
    up: str              # dealer upcard label
    index: float
    action: str
    direction: str = "ge"   # "ge": TC >= index; "le": TC <= index
    other: str | None = None  # action on the far side; None means basic strategy
    group: str = "I18"

    @property
    def key(self) -> tuple[str, int | str, str]:
        return (self.kind, self.total, self.up)

    def applies(self, tc: float) -> bool:
        return tc >= self.index if self.direction == "ge" else tc <= self.index

    def describe(self) -> str:
        cmp = ">=" if self.direction == "ge" else "<="
        where = "Insurance" if self.kind == "insurance" else self.label
        return f"{where}: {self.action_name} at TC {cmp} {self.index:+g}"

    @property
    def label(self) -> str:
        if self.kind == "insurance":
            return "Insurance"
        if self.kind == "pair":
            return f"{self.total},{self.total} v {self.up}"
        if self.kind == "soft":
            return f"soft {self.total} v {self.up}"
        return f"{self.total} v {self.up}"

    @property
    def action_name(self) -> str:
        from .strategy import ACTION_NAMES

        return ACTION_NAMES.get(self.action, self.action)


# The Illustrious 18 and Fab 4, the standard Hi-Lo index plays for a shoe game.
# Together they capture the large majority of the gain available from varying
# strategy with the count.
ILLUSTRIOUS_18: tuple[Deviation, ...] = (
    Deviation("insurance", 0, "A", 3, "take insurance", group="I18"),
    Deviation("hard", 16, "T", 0, STAND),
    Deviation("hard", 15, "T", 4, STAND),
    Deviation("pair", "T", "5", 5, SPLIT),
    Deviation("pair", "T", "6", 4, SPLIT),
    Deviation("hard", 10, "T", 4, DOUBLE),
    Deviation("hard", 12, "3", 2, STAND),
    Deviation("hard", 12, "2", 3, STAND),
    Deviation("hard", 11, "A", 1, DOUBLE),
    Deviation("hard", 9, "2", 1, DOUBLE),
    Deviation("hard", 10, "A", 4, DOUBLE),
    Deviation("hard", 9, "7", 3, DOUBLE),
    Deviation("hard", 16, "9", 5, STAND),
    Deviation("hard", 13, "2", -1, HIT, direction="le"),
    Deviation("hard", 12, "4", 0, HIT, direction="le"),
    Deviation("hard", 12, "5", -2, HIT, direction="le"),
    Deviation("hard", 12, "6", -1, HIT, direction="le"),
    Deviation("hard", 13, "3", -2, HIT, direction="le"),
)

FAB_4: tuple[Deviation, ...] = (
    Deviation("hard", 14, "T", 3, SURRENDER, group="Fab4"),
    Deviation("hard", 15, "9", 2, SURRENDER, group="Fab4"),
    # Basic strategy already surrenders 15 v T; below TC 0 you take the hit instead.
    Deviation("hard", 15, "T", 0, SURRENDER, other=HIT, group="Fab4"),
    Deviation("hard", 15, "A", -1, SURRENDER, other=HIT, group="Fab4"),
)

ALL_DEVIATIONS = ILLUSTRIOUS_18 + FAB_4

# A cell can carry both a playing index and a surrender index (15 v T has both),
# so each key holds every deviation that covers it.
DEVIATION_INDEX: dict[tuple[str, int | str, str], tuple[Deviation, ...]] = {}
for _d in ALL_DEVIATIONS:
    DEVIATION_INDEX[_d.key] = DEVIATION_INDEX.get(_d.key, ()) + (_d,)


def hand_key(player: Hand, up_label: str) -> tuple[str, int | str, str]:
    if player.is_pair and player.pair_rank == "T":
        return ("pair", "T", up_label)
    kind = "soft" if player.is_soft else "hard"
    return (kind, player.total, up_label)


def deviations_for(player: Hand, up_label: str, *, include_fab4: bool = True,
                   can_surrender: bool = True) -> tuple[Deviation, ...]:
    """Every index play covering this cell, surrender indices first.

    Surrender is worth a flat -0.5, which beats the hit/stand indices in the
    cells where both exist, so it gets first refusal whenever it is offered.
    """
    devs = DEVIATION_INDEX.get(hand_key(player, up_label), ())
    out = [
        d for d in devs
        if d.kind != "insurance"
        and not (d.group == "Fab4" and not include_fab4)
        and not (d.group == "Fab4" and not can_surrender)
    ]
    out.sort(key=lambda d: 0 if d.group == "Fab4" else 1)
    return tuple(out)


def find_deviation(player: Hand, up_label: str, *, include_fab4: bool = True
                   ) -> Deviation | None:
    devs = deviations_for(player, up_label, include_fab4=include_fab4)
    return devs[0] if devs else None


def counting_action(player: Hand, up: Card, rules: Rules, true_count: float,
                    hands_in_play: int = 1, *, use_deviations: bool = True,
                    include_fab4: bool = True) -> tuple[str, Deviation | None]:
    """The correct play with index plays applied, plus the deviation used (if any).

    Falls back to basic strategy whenever no index covers the cell, the count is
    on the wrong side of the index, or the deviation's action is not legal here.
    """
    from .strategy import legality

    up_label = "T" if up.value == 10 and not up.is_ace else up.rank
    basic = basic_action(player, up, rules, hands_in_play)
    if not use_deviations:
        return basic, None

    legal = legality(player, rules, hands_in_play)
    for dev in deviations_for(player, up_label, include_fab4=include_fab4,
                              can_surrender=legal["can_surrender"]):
        wanted = dev.action if dev.applies(true_count) else (dev.other or basic)
        if wanted == basic:
            continue
        # Surrender's flat -0.5 beats what the playing indices buy in these
        # cells, so never let a *playing* index talk you out of an available
        # surrender. A surrender index saying "not here" is another matter.
        if basic == SURRENDER and wanted != SURRENDER and dev.group != "Fab4":
            continue
        if wanted == DOUBLE and not legal["can_double"]:
            continue
        if wanted == SPLIT and not legal["can_split"]:
            continue
        if wanted == SURRENDER and not legal["can_surrender"]:
            continue
        return wanted, dev
    return basic, None


def should_insure(true_count: float) -> bool:
    return true_count >= 3


def bet_units(true_count: float, spread_max: int = 12, ramp: int = 1) -> int:
    """A plain (TC - 1) x ramp bet ramp, capped — enough to practise sizing."""
    tc = math.floor(true_count)
    if tc < 2:
        return 1
    return max(1, min(spread_max, (tc - 1) * ramp))
