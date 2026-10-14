"""Structural comparison of recorded vs replayed observations."""

from __future__ import annotations

import json
from typing import Any

# Wall-clock / envelope fields that legitimately differ between a run and its replay.
VOLATILE_KEYS = frozenset({"timestamp_ms", "ts_ms", "settled", "step", "trajectory", "trajectory_path"})
# Entity ids (sort_id). Compared after relabeling by first appearance so a constant offset is tolerated.
ID_KEYS = frozenset({"id", "sort_id"})


class IdCanon:
    """Relabels entity ids to first-appearance ordinals; one instance per trajectory side."""

    def __init__(self) -> None:
        self.map: dict[Any, int] = {}

    def __call__(self, value: Any) -> Any:
        if value is None:
            return None
        key = str(value)
        if key not in self.map:
            self.map[key] = len(self.map) + 1
        return f"#{self.map[key]}"


def normalize(node: Any, canon: IdCanon | None = None, drop: frozenset[str] = VOLATILE_KEYS) -> Any:
    """Drop volatile keys, relabel ids, treat {} and [] alike. Dict keys are visited in sorted order so
    relabeling is independent of the bridge's (Lua `pairs`) key order."""
    if isinstance(node, dict):
        if not node:
            return []
        out = {}
        for k in sorted(node):
            if k in drop or k == "_line":
                continue
            v = node[k]
            if canon is not None and k in ID_KEYS and not isinstance(v, (dict, list)):
                out[k] = canon(v)
            else:
                out[k] = normalize(v, canon, drop)
        return out
    if isinstance(node, list):
        return [normalize(v, canon, drop) for v in node]
    if isinstance(node, float) and node.is_integer():
        return int(node)
    return node


def first_difference(a: Any, b: Any, path: str = "") -> tuple[str, Any, Any] | None:
    """Depth-first first mismatch between two normalized JSON values: (json_path, a_value, b_value)."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                return (f"{path}.{k}", "<missing>", b[k])
            if k not in b:
                return (f"{path}.{k}", a[k], "<missing>")
            d = first_difference(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_difference(x, y, f"{path}[{i}]")
            if d:
                return d
        if len(a) != len(b):
            return (f"{path}.length", len(a), len(b))
        return None
    if a != b or type(a) is not type(b) and not (_num(a) and _num(b)):
        return (path or "$", a, b)
    return None


def all_differences(a: Any, b: Any, path: str = "", limit: int = 20) -> list[tuple[str, Any, Any]]:
    out: list[tuple[str, Any, Any]] = []

    def walk(x: Any, y: Any, p: str) -> None:
        if len(out) >= limit:
            return
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                if k not in x:
                    out.append((f"{p}.{k}", "<missing>", y[k]))
                elif k not in y:
                    out.append((f"{p}.{k}", x[k], "<missing>"))
                else:
                    walk(x[k], y[k], f"{p}.{k}")
        elif isinstance(x, list) and isinstance(y, list):
            for i, (u, v) in enumerate(zip(x, y)):
                walk(u, v, f"{p}[{i}]")
            if len(x) != len(y):
                out.append((f"{p}.length", len(x), len(y)))
        elif first_difference(x, y, p):
            out.append((p or "$", x, y))

    walk(a, b, path)
    return out


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def format_diff(diffs: list[tuple[str, Any, Any]]) -> str:
    return json.dumps(
        [{"path": p, "recorded": _short(x), "replayed": _short(y)} for p, x, y in diffs], indent=1
    )


def _short(v: Any, limit: int = 300) -> Any:
    text = json.dumps(v, sort_keys=True)
    return v if len(text) <= limit else text[:limit] + "..."
