"""Notable swarm events (lucky/crazy/abnormal plays) for the dashboard's "Notable events" section.

One store, `data/notable_events.jsonl`, one row per event:
`{"ts": unix_s, "port", "seed", "model", "ante", "text", "source"}`.

Two writers:
- `harvest()`: player agents append `NOTABLE: <ante N> <sentence>` lines to their own run log
  (`docs/runs/<port>_<seed>.md`) as things happen; the dashboard copies new lines into the store, stamping them
  with the time it first saw them (dedupe key: port + seed + text).
- the orchestrator: `swarm_ctl.py note ...` for events it reads in finished runs' results and post-mortems.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

EVENTS_FILE = "notable_events.jsonl"
NOTABLE_RE = re.compile(r"^\s*(?:[-*]\s*)?\**NOTABLE\**\s*(?:\[[^\]]*\])?\s*:\s*(?P<text>\S.*?)\s*$")
ANTE_RE = re.compile(r"\bante\s*(\d+)", re.IGNORECASE)
HEADER_RE = re.compile(r"^#\s*Run\s+(?P<seed>\S+)\s*\(port\s*(?P<port>\d+),\s*(?P<model>[^)]+)\)")
NAME_RE = re.compile(r"^(?P<port>\d+)_(?P<seed>[A-Za-z0-9]+)\.md$")


def _key(port: Any, seed: Any, text: str) -> tuple[str, str, str]:
    return str(port), str(seed), " ".join(text.split()).lower()


def load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a half-written line from a concurrent append
    return rows


def append(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        with path.open("a", encoding="utf-8") as f:
            f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


class Harvester:
    """Copies run-log NOTABLE lines into the store; rescans only run logs whose mtime changed."""

    def __init__(self, data_root: Path, runs_dir: Path) -> None:
        self.path = data_root / EVENTS_FILE
        self.runs_dir = runs_dir
        self._mtimes: dict[Path, int] = {}

    def run(self) -> list[dict[str, Any]]:
        """Harvest new run-log events, then return every stored event, newest first."""
        rows = load(self.path)
        seen = {_key(r.get("port"), r.get("seed"), r.get("text", "")) for r in rows}
        new: list[dict[str, Any]] = []
        now = time.time()
        for log in self.runs_dir.glob("*_*.md") if self.runs_dir.is_dir() else []:
            m = NAME_RE.match(log.name)
            try:
                mt = log.stat().st_mtime_ns
            except OSError:
                continue
            if not m or self._mtimes.get(log) == mt:
                continue
            self._mtimes[log] = mt
            try:
                lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            h = HEADER_RE.match(lines[0]) if lines else None
            port, seed = int(m["port"]), m["seed"]
            for line in lines:
                n = NOTABLE_RE.match(line)
                if not n:
                    continue
                k = _key(port, seed, n["text"])
                if k in seen:
                    continue
                seen.add(k)
                a = ANTE_RE.search(n["text"])
                new.append({"ts": now, "port": port, "seed": seed, "model": h["model"].strip() if h else None,
                            "ante": int(a.group(1)) if a else None, "text": n["text"], "source": "runlog"})
        append(self.path, new)
        rows += new
        rows.sort(key=lambda r: r.get("ts") or 0, reverse=True)
        return rows
