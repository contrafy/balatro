"""`data/manifest.jsonl`: one row per trajectory; only `schema_ok && replay_ok` rows feed training.

Replay verdicts are kept per host: `gui_*` (live instance, `balatro-data replay`) and `headless_*` (headless engine,
`balatro_env.headless`). `replay_ok` is the gui verdict when there is one (the live game is the reference), else
the headless one, else None; `replay_host` names its host. A gui/headless disagreement is spelled out in
`replay_detail`. Rows written before per-host columns existed (a `replay_ok` without `replay_host`) are gui verdicts.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from balatro_env.data.trajectory import data_dir, dataset_files, read_trajectory, run_key
from balatro_env.data.validate import validate_trajectory

MANIFEST_NAME = "manifest.jsonl"
LOCK_NAME = "manifest.lock"
REPLAY_HOSTS = ("gui", "headless")
_HOST_FIELDS = ("replay_ok", "replay_detail", "replayed_at_ms", "replay_bridge_hash")
# Columns carried over from the previous manifest when a file is re-scanned (set by replays).
REPLAY_FIELDS = ("replay_ok", "replay_detail", "replayed_at_ms", "replay_path", "replay_host", "replay_bridge_hash") \
    + tuple(f"{h}_{f}" for h in REPLAY_HOSTS for f in _HOST_FIELDS)


@contextmanager
def manifest_lock(root: Path, timeout_s: float = 120.0, stale_s: float = 600.0) -> Iterator[None]:
    """Cross-process lock around manifest read-modify-write (dataops, `replay --update-manifest`, `manifest`).
    A lock older than `stale_s` is broken; after `timeout_s` the caller proceeds unlocked rather than stall."""
    path = Path(root) / LOCK_NAME
    deadline = time.monotonic() + timeout_s
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
        except FileExistsError:
            try:
                if time.time() - path.stat().st_mtime > stale_s:
                    path.unlink(missing_ok=True)
                    continue
            except OSError:
                continue
            if time.monotonic() > deadline:
                break
            time.sleep(0.1)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass


def manifest_path(root: Path) -> Path:
    return root / MANIFEST_NAME


def load_manifest(root: Path) -> dict[str, dict[str, Any]]:
    path = manifest_path(root)
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["run_key"]] = row
    return rows


def replace_file(tmp: Path, dest: Path, attempts: int = 20) -> None:
    """os.replace, retried: on Windows it fails while another process (dashboard, status) has `dest` open."""
    for k in range(attempts):
        try:
            os.replace(tmp, dest)
            return
        except PermissionError:
            if k == attempts - 1:
                raise
            time.sleep(0.05 * (k + 1))


def write_manifest(root: Path, rows: dict[str, dict[str, Any]]) -> Path:
    path = manifest_path(root)
    tmp = path.with_suffix(f".jsonl.{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for key in sorted(rows):
            fh.write(json.dumps(rows[key], sort_keys=True) + "\n")
    replace_file(tmp, path)
    return path


def quarantine_reason(row: dict[str, Any]) -> str | None:
    if not row.get("schema_ok"):
        return f"schema: {row.get('schema_error') or 'invalid'}"
    if row.get("replay_ok") is False:
        return f"replay: {row.get('replay_detail') or 'diverged'}"
    return None


def _file_stat(path: Path) -> tuple[int, int]:
    st = path.stat()
    return st.st_size, st.st_mtime_ns


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def build_row(path: Path, root: Path, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    size, mtime_ns = _file_stat(path)  # taken before reading: a file that grows meanwhile is re-read next time
    traj = read_trajectory(path)
    rep = validate_trajectory(traj)
    h = traj.header or {}
    meta = traj.start_meta
    row: dict[str, Any] = {
        "run_key": run_key(path),
        "path": _rel(path, root),
        "seed": h.get("seed"),
        "deck": h.get("deck_key"),
        "stake": h.get("stake"),
        "outcome": rep.outcome,
        "ante": (traj.end or {}).get("ante"),
        "steps": len(traj.steps),
        "rejects": len(traj.rejects),
        "format_version": h.get("format_version"),
        "bridge_version": h.get("bridge_version"),
        "bridge_hash": h.get("bridge_hash"),
        "game_version": h.get("game_version"),
        "agent": meta.get("agent"),
        "replay_of": meta.get("replay_of"),
        "schema_ok": rep.ok,
        "schema_error": rep.errors[0] if rep.errors else None,
        "schema_warnings": rep.warnings,
        "file_size": size,
        "file_mtime_ns": mtime_ns,
        "replay_ok": None,
    }
    if previous and previous.get("bridge_hash") == row["bridge_hash"] and previous.get("steps") == row["steps"]:
        for k in REPLAY_FIELDS:
            if k in previous:
                row[k] = previous[k]
    row["quarantined_reason"] = quarantine_reason(row)
    return row


def build_manifest(root: str | os.PathLike | None = None,
                   reuse_unchanged: bool = False) -> tuple[Path, list[dict[str, Any]]]:
    """Re-scan every trajectory under `root`, validate it, keep earlier replay results; rewrite manifest.
    `reuse_unchanged`: keep a previous row as-is when its file path, size and mtime are unchanged (skips
    re-validation; used by the `dataops` loop)."""
    root = data_dir(root)
    with manifest_lock(root):
        previous = load_manifest(root)
        rows: dict[str, dict[str, Any]] = {}
        for path in dataset_files(root):
            key = run_key(path)
            prev = previous.get(key)
            if reuse_unchanged and prev and prev.get("file_size") is not None:
                try:
                    size, mtime_ns = _file_stat(path)
                except OSError:
                    continue
                if (prev.get("file_size"), prev.get("file_mtime_ns")) == (size, mtime_ns) and \
                        prev.get("path") == _rel(path, root):
                    rows[key] = prev
                    continue
            try:
                rows[key] = build_row(path, root, prev)
            except FileNotFoundError:  # compressed/removed while scanning
                continue
        return write_manifest(root, rows), list(rows.values())


@dataclass
class ReplayVerdict:
    path: str | Path
    host: str  # gui | headless
    ok: bool | None
    detail: str | None
    steps_verified: int
    now_ms: int
    bridge_hash: str | None = None  # of the replaying bridge
    replay_path: str | None = None  # gui: the replay's own recording


def migrate_legacy(row: dict[str, Any]) -> None:
    """A verdict from before per-host columns (no `replay_host`) came from a live instance."""
    if row.get("replay_ok") is not None and not row.get("replay_host"):
        row["gui_replay_ok"] = row["replay_ok"]
        row["gui_replay_detail"] = row.get("replay_detail")
        row["gui_replayed_at_ms"] = row.get("replayed_at_ms")
        row["replay_host"] = "gui"


def combine_verdicts(row: dict[str, Any]) -> None:
    """Set replay_ok/replay_detail/replay_host/replay_bridge_hash/replayed_at_ms from the per-host columns."""
    host = next((h for h in REPLAY_HOSTS if row.get(f"{h}_replay_ok") is not None), None)
    if host is None:
        row.update(replay_ok=None, replay_host=None, replay_bridge_hash=None,
                   replay_detail=next((row.get(f"{h}_replay_detail") for h in REPLAY_HOSTS
                                       if row.get(f"{h}_replay_detail")), None))
    else:
        ok = row[f"{host}_replay_ok"]
        detail = None if ok else f"{host}: {row.get(f'{host}_replay_detail') or 'diverged'}"
        gui, hl = row.get("gui_replay_ok"), row.get("headless_replay_ok")
        if gui is not None and hl is not None and gui != hl:
            note = (f"headless/gui disagree: gui {'matched' if gui else 'diverged'}, headless "
                    + ("matched" if hl else f"diverged: {row.get('headless_replay_detail') or '?'}"))
            detail = f"{detail}; {note}" if detail else note
        row.update(replay_ok=ok, replay_host=host, replay_detail=detail,
                   replay_bridge_hash=row.get(f"{host}_replay_bridge_hash"))
    times = [row.get(f"{h}_replayed_at_ms") for h in REPLAY_HOSTS if row.get(f"{h}_replayed_at_ms")]
    row["replayed_at_ms"] = max(times) if times else None
    row["quarantined_reason"] = quarantine_reason(row)


def record_replays(root: str | os.PathLike | None, verdicts: list[ReplayVerdict]) -> Path | None:
    """Store replay verdicts (one manifest rewrite for the batch). Each row is rebuilt from its file as it is now;
    a verdict only counts for exactly the steps that were replayed (an open file may have grown meanwhile)."""
    root = data_dir(root)
    built: list[tuple[ReplayVerdict, dict[str, Any]]] = []
    for v in verdicts:  # validation outside the lock
        try:
            built.append((v, build_row(Path(v.path), root)))
        except FileNotFoundError:
            continue
    if not built:
        return None
    with manifest_lock(root):
        rows = load_manifest(root)
        for v, row in built:
            prev = rows.get(row["run_key"])
            if prev and prev.get("bridge_hash") == row["bridge_hash"] and prev.get("steps") == row["steps"]:
                migrate_legacy(prev)
                row.update({k: prev[k] for k in REPLAY_FIELDS if k in prev})
            ok, detail = v.ok, v.detail
            if row["steps"] != v.steps_verified:
                ok, detail = None, f"file has {row['steps']} steps, replay covered {v.steps_verified}; replay again"
            row[f"{v.host}_replay_ok"] = ok
            row[f"{v.host}_replay_detail"] = detail
            row[f"{v.host}_replayed_at_ms"] = v.now_ms
            row[f"{v.host}_replay_bridge_hash"] = v.bridge_hash
            if v.host == "gui":
                row["replay_path"] = v.replay_path
            combine_verdicts(row)
            rows[row["run_key"]] = row
        return write_manifest(root, rows)


def update_replay_result(root: str | os.PathLike | None, traj_path: Path, ok: bool, detail: str | None,
                         replay_path: str | None, now_ms: int, steps_verified: int, host: str = "gui",
                         bridge_hash: str | None = None) -> Path | None:
    """Record one replay verdict (see record_replays)."""
    return record_replays(root, [ReplayVerdict(traj_path, host, ok, detail, steps_verified, now_ms, bridge_hash,
                                               replay_path)])
