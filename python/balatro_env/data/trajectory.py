"""Reading trajectory JSONL / JSONL.GZ files written by the bridge recorder (docs/DATA_CONTRACT.md)."""

from __future__ import annotations

import gzip
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

LINE_TYPES = ("header", "step", "reject", "end")
SUFFIXES = (".jsonl.gz", ".jsonl")


def data_dir(explicit: str | os.PathLike | None = None) -> Path:
    """Dataset root: explicit arg, else $BALATRO_RL_DATA_DIR, else ./data."""
    if explicit:
        return Path(explicit)
    return Path(os.environ.get("BALATRO_RL_DATA_DIR") or "data")


def run_key(path: str | os.PathLike) -> str:
    """File name without .jsonl/.jsonl.gz; stable across compression."""
    name = Path(path).name
    for suffix in SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def find_trajectories(root: str | os.PathLike) -> list[Path]:
    """All trajectory files under `root` (a .jsonl is skipped when its .jsonl.gz twin exists)."""
    root = Path(root)
    if root.is_file():
        return [root]
    found: dict[str, Path] = {}
    for path in sorted(root.rglob("*.jsonl*")):
        if not path.name.endswith(SUFFIXES) or path.name == "manifest.jsonl":
            continue
        key = str(path.parent / run_key(path))
        if key not in found or path.name.endswith(".gz"):
            found[key] = path
    return sorted(found.values())


def dataset_files(root: str | os.PathLike) -> list[Path]:
    """Trajectory files of a dataset root: `<root>/trajectories/**` (the recorder's layout); other JSONL files in
    the root (manifest, orchestrator notes) are not trajectories. Falls back to `root` itself without that dir."""
    root = Path(root)
    base = root / "trajectories"
    if base.is_dir():
        return find_trajectories(base)
    return find_trajectories(root) if root.exists() else []


def open_text(path: str | os.PathLike):
    path = Path(path)
    if path.name.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return open(path, encoding="utf-8", newline="")


@dataclass
class Trajectory:
    path: Path
    header: dict[str, Any] | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    rejects: list[dict[str, Any]] = field(default_factory=list)
    end: dict[str, Any] | None = None
    # Every parsed line in file order (header/step/reject/end), for ordering checks.
    lines: list[dict[str, Any]] = field(default_factory=list)
    # (line_no, message) for lines that are not valid JSON objects.
    parse_errors: list[tuple[int, str]] = field(default_factory=list)
    # The final line is incomplete (writer crashed or file still being written).
    truncated: bool = False
    read_error: str | None = None

    @property
    def key(self) -> str:
        return run_key(self.path)

    @property
    def outcome(self) -> str:
        """win/loss/abandoned from the end line; a missing end line means the run was abandoned/crashed."""
        if self.end and self.end.get("outcome"):
            return str(self.end["outcome"])
        return "abandoned"

    @property
    def start_params(self) -> dict[str, Any]:
        h = self.header or {}
        params = dict(h.get("start_params") or {})
        params.setdefault("deck", h.get("deck_key"))
        params.setdefault("stake", h.get("stake"))
        params.setdefault("seed", h.get("seed"))
        return params

    @property
    def start_meta(self) -> dict[str, Any]:
        return dict((self.header or {}).get("start_meta") or {})


def iter_lines(path: str | os.PathLike) -> Iterator[tuple[int, str]]:
    with open_text(path) as fh:
        for no, raw in enumerate(fh, start=1):
            yield no, raw


def read_trajectory(path: str | os.PathLike) -> Trajectory:
    """Parse a trajectory file. Never raises on bad content; problems land in the returned object."""
    traj = Trajectory(path=Path(path))
    raw_lines: list[tuple[int, str]] = []
    stream_cut = False
    try:
        for item in iter_lines(path):
            raw_lines.append(item)
    except EOFError as exc:  # gzip stream cut off: keep what decoded, flag truncation
        stream_cut = True
        traj.truncated = True
        traj.parse_errors.append((len(raw_lines) + 1, f"compressed stream truncated: {exc}"))
    except (OSError, gzip.BadGzipFile, UnicodeDecodeError) as exc:
        traj.read_error = f"{type(exc).__name__}: {exc}"
        return traj
    last_no = raw_lines[-1][0] if raw_lines else 0
    for no, raw in raw_lines:
        text = raw.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            if no == last_no and (stream_cut or not raw.endswith("\n")):
                traj.truncated = True
            traj.parse_errors.append((no, f"invalid JSON: {exc.msg} at col {exc.colno}"))
            continue
        if not isinstance(obj, dict):
            traj.parse_errors.append((no, "line is not a JSON object"))
            continue
        obj["_line"] = no
        traj.lines.append(obj)
        t = obj.get("t")
        if t == "header" and traj.header is None:
            traj.header = obj
        elif t == "step":
            traj.steps.append(obj)
        elif t == "reject":
            traj.rejects.append(obj)
        elif t == "end" and traj.end is None:
            traj.end = obj
    return traj
