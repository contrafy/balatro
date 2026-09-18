"""Per-cell accuracy tracking, persisted between sessions."""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path


def data_home() -> Path:
    override = os.environ.get("BJTRAINER_HOME")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base).expanduser() / "bjtrainer"
    return Path.home() / ".local" / "share" / "bjtrainer"


@dataclass
class CellStat:
    attempts: int = 0
    errors: int = 0
    last_seen: float = 0.0
    last_wrong: float = 0.0

    @property
    def accuracy(self) -> float:
        return 1.0 if not self.attempts else 1.0 - self.errors / self.attempts


@dataclass
class Stats:
    """Accuracy by chart cell, plus lifetime totals."""

    cells: dict[str, CellStat] = field(default_factory=dict)
    totals: dict[str, int] = field(default_factory=dict)
    count_drills: dict[str, int] = field(default_factory=dict)
    path: Path | None = None

    # -- recording ---------------------------------------------------------
    def record(self, key: str, correct: bool, section: str = "basic") -> None:
        cell = self.cells.setdefault(key, CellStat())
        cell.attempts += 1
        cell.last_seen = time.time()
        if not correct:
            cell.errors += 1
            cell.last_wrong = cell.last_seen
        self.totals[f"{section}_attempts"] = self.totals.get(f"{section}_attempts", 0) + 1
        if not correct:
            self.totals[f"{section}_errors"] = self.totals.get(f"{section}_errors", 0) + 1

    def record_count_drill(self, correct: bool) -> None:
        self.count_drills["attempts"] = self.count_drills.get("attempts", 0) + 1
        if not correct:
            self.count_drills["errors"] = self.count_drills.get("errors", 0) + 1

    # -- queries -----------------------------------------------------------
    def section_accuracy(self, section: str) -> tuple[int, int]:
        a = self.totals.get(f"{section}_attempts", 0)
        e = self.totals.get(f"{section}_errors", 0)
        return a, e

    def weight(self, key: str) -> float:
        """Sampling weight: unseen cells first, then the ones you keep missing."""
        cell = self.cells.get(key)
        if cell is None or cell.attempts == 0:
            return 4.0
        miss = cell.errors / cell.attempts
        recency = 1.5 if cell.last_wrong and time.time() - cell.last_wrong < 3600 else 1.0
        return (0.5 + 6.0 * miss) * recency

    def worst_cells(self, limit: int = 12, min_attempts: int = 2) -> list[tuple[str, CellStat]]:
        rows = [
            (k, c) for k, c in self.cells.items()
            if c.attempts >= min_attempts and c.errors
        ]
        rows.sort(key=lambda kv: (-kv[1].errors / kv[1].attempts, -kv[1].errors))
        return rows[:limit]

    # -- persistence -------------------------------------------------------
    @classmethod
    def load(cls, path: Path | None = None) -> "Stats":
        path = path or (data_home() / "stats.json")
        stats = cls(path=path)
        try:
            raw = json.loads(path.read_text())
        except (OSError, ValueError):
            return stats
        for key, blob in raw.get("cells", {}).items():
            stats.cells[key] = CellStat(**blob)
        stats.totals = {k: int(v) for k, v in raw.get("totals", {}).items()}
        stats.count_drills = {k: int(v) for k, v in raw.get("count_drills", {}).items()}
        return stats

    def save(self) -> None:
        path = self.path or (data_home() / "stats.json")
        blob = {
            "cells": {k: vars(v) for k, v in self.cells.items()},
            "totals": self.totals,
            "count_drills": self.count_drills,
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Write-then-rename so a mid-write quit cannot corrupt the file.
            with tempfile.NamedTemporaryFile(
                "w", dir=path.parent, prefix=".stats-", suffix=".tmp", delete=False
            ) as fh:
                json.dump(blob, fh, indent=1)
                tmp = Path(fh.name)
            tmp.replace(path)
        except OSError:
            pass  # a trainer is not worth crashing over a read-only home

    def reset(self) -> None:
        self.cells.clear()
        self.totals.clear()
        self.count_drills.clear()
        self.save()
