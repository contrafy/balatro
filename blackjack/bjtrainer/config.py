"""User settings, persisted next to the stats file."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .counting import SYSTEMS_BY_NAME, HI_LO, CountSystem
from .stats import data_home
from .strategy import Rules


@dataclass
class Settings:
    decks: int = 6
    h17: bool = False
    das: bool = True
    surrender: bool = True
    penetration: float = 0.75
    blackjack_pays: float = 1.5

    system: str = "Hi-Lo"
    drill_source: str = "weighted"      # "weighted" | "dealt"
    use_deviations: bool = False        # index plays in the drills and shoe play
    show_count: bool = True             # count readout during shoe play
    ask_true_count: bool = True
    count_speed_ms: int = 900
    bankroll: float = 1000.0
    unit: float = 5.0
    strict_shoe: bool = True            # flag misplays while playing a shoe

    @property
    def rules(self) -> Rules:
        return Rules(
            decks=self.decks,
            h17=self.h17,
            das=self.das,
            surrender=self.surrender,
            penetration=self.penetration,
            blackjack_pays=self.blackjack_pays,
        )

    @property
    def count_system(self) -> CountSystem:
        return SYSTEMS_BY_NAME.get(self.system, HI_LO)

    # -- persistence -------------------------------------------------------
    @classmethod
    def load(cls, path: Path | None = None) -> "Settings":
        path = path or (data_home() / "config.json")
        try:
            raw = json.loads(path.read_text())
        except (OSError, ValueError):
            return cls()
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in raw.items() if k in known})

    def save(self, path: Path | None = None) -> None:
        path = path or (data_home() / "config.json")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=1))
        except OSError:
            pass
