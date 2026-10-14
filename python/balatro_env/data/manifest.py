"""`data/manifest.jsonl`: one row per trajectory; only `schema_ok && replay_ok` rows feed training."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from balatro_env.data.trajectory import data_dir, dataset_files, read_trajectory, run_key
from balatro_env.data.validate import validate_trajectory

MANIFEST_NAME = "manifest.jsonl"
# Columns carried over from the previous manifest when a file is re-scanned (set by `replay`).
REPLAY_FIELDS = ("replay_ok", "replay_detail", "replayed_at_ms", "replay_path")


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


def update_replay_result(root: str | os.PathLike | None, traj_path: Path, ok: bool, detail: str | None,
                         replay_path: str | None, now_ms: int, steps_verified: int) -> Path:
    """Record a replay verdict for `traj_path`. The row is rebuilt from the file as it is now; a verdict
    only counts for exactly the steps that were replayed (an open file may have grown meanwhile)."""
    root = data_dir(root)
    rows = load_manifest(root)
    key = run_key(traj_path)
    row = build_row(Path(traj_path), root)
    if row["steps"] != steps_verified:
        ok, detail = None, f"file has {row['steps']} steps, replay covered {steps_verified}; replay again"
    row.update(replay_ok=ok, replay_detail=detail, replayed_at_ms=now_ms, replay_path=replay_path)
    row["quarantined_reason"] = quarantine_reason(row)
    rows[key] = row
    return write_manifest(root, rows)
