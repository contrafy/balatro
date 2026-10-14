"""`data/manifest.jsonl`: one row per trajectory; only `schema_ok && replay_ok` rows feed training."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from balatro_env.data.trajectory import data_dir, find_trajectories, read_trajectory, run_key
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


def write_manifest(root: Path, rows: dict[str, dict[str, Any]]) -> Path:
    path = manifest_path(root)
    tmp = path.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for key in sorted(rows):
            fh.write(json.dumps(rows[key], sort_keys=True) + "\n")
    os.replace(tmp, path)
    return path


def quarantine_reason(row: dict[str, Any]) -> str | None:
    if not row.get("schema_ok"):
        return f"schema: {row.get('schema_error') or 'invalid'}"
    if row.get("replay_ok") is False:
        return f"replay: {row.get('replay_detail') or 'diverged'}"
    return None


def build_row(path: Path, root: Path, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    traj = read_trajectory(path)
    rep = validate_trajectory(traj)
    h = traj.header or {}
    meta = traj.start_meta
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    row: dict[str, Any] = {
        "run_key": run_key(path),
        "path": rel,
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
        "replay_ok": None,
    }
    if previous and previous.get("bridge_hash") == row["bridge_hash"] and previous.get("steps") == row["steps"]:
        for k in REPLAY_FIELDS:
            if k in previous:
                row[k] = previous[k]
    row["quarantined_reason"] = quarantine_reason(row)
    return row


def build_manifest(root: str | os.PathLike | None = None) -> tuple[Path, list[dict[str, Any]]]:
    """Re-scan every trajectory under `root`, validate it, keep earlier replay results; rewrite manifest."""
    root = data_dir(root)
    previous = load_manifest(root)
    rows: dict[str, dict[str, Any]] = {}
    for path in find_trajectories(root) if root.exists() else []:
        key = run_key(path)
        rows[key] = build_row(path, root, previous.get(key))
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
