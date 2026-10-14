"""Schema + legality validation of a recorded trajectory (docs/DATA_CONTRACT.md invariants 2-6)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from balatro_env.data.legality import check_action
from balatro_env.data.trajectory import Trajectory, read_trajectory

SUPPORTED_FORMAT_VERSIONS = {1}
OUTCOMES = {"win", "loss", "abandoned"}
HEADER_REQUIRED = (
    "format_version", "bridge_version", "bridge_hash", "game_version", "lovely_version",
    "seed", "deck_key", "stake", "unlocks",
)
# Version fields that must be non-empty strings for the run to be attributable.
HEADER_VERSIONS = ("bridge_version", "bridge_hash", "game_version", "lovely_version")
STEP_REQUIRED = ("i", "obs", "legal", "action", "result")
# Keys that carry hidden information and must never appear anywhere inside obs.
HIDDEN_KEYS = {"seed", "run_id", "draw_order", "deck_order", "face_down", "hidden", "pseudorandom"}
# A face-down card/joker in obs must not reveal any of these.
FACE_DOWN_IDENTITY_KEYS = {
    "id", "sort_id", "key", "rank", "suit", "name", "enhancement", "edition", "seal", "ability", "label",
}
MAX_ERRORS = 50


@dataclass
class ValidationReport:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    outcome: str = "abandoned"
    steps: int = 0
    rejects: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, msg: str) -> None:
        if len(self.errors) < MAX_ERRORS:
            self.errors.append(msg)
        elif len(self.errors) == MAX_ERRORS:
            self.errors.append("... further errors suppressed")

    def summary(self) -> str:
        status = "OK" if self.ok else "INVALID"
        head = f"{status} {self.path} outcome={self.outcome} steps={self.steps} rejects={self.rejects}"
        if self.errors:
            head += f" errors={len(self.errors)} first={self.errors[0]!r}"
        if self.warnings:
            head += f" warnings={'; '.join(self.warnings)}"
        return head


def hidden_leaks(obs: Any, seed: str | None, path: str = "obs") -> list[str]:
    """Locations in `obs` that expose hidden information (seed, draw order, face-down identities)."""
    leaks: list[str] = []

    def walk(node: Any, where: str) -> None:
        if isinstance(node, dict):
            if node.get("facing") == "back":
                shown = sorted(k for k in FACE_DOWN_IDENTITY_KEYS if node.get(k) not in (None, ""))
                if shown:
                    leaks.append(f"{where}: face-down entity exposes {shown}")
            for k, v in node.items():
                if k in HIDDEN_KEYS:
                    leaks.append(f"{where}.{k}: hidden key in obs")
                walk(v, f"{where}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{where}[{i}]")
        elif seed and len(seed) >= 6 and isinstance(node, str) and seed in node:
            leaks.append(f"{where}: contains the run seed")

    walk(obs, path)
    return leaks


def _check_header(traj: Trajectory, rep: ValidationReport) -> None:
    h = traj.header
    if h is None:
        rep.error("no header line")
        return
    if traj.lines and traj.lines[0] is not h:
        rep.error("header is not the first line")
    for key in HEADER_REQUIRED:
        if key not in h:
            rep.error(f"header missing {key!r}")
    fv = h.get("format_version")
    if fv is not None and fv not in SUPPORTED_FORMAT_VERSIONS:
        rep.error(f"unsupported format_version {fv!r}")
    for key in HEADER_VERSIONS:
        if key in h and (not isinstance(h[key], str) or not h[key]):
            rep.error(f"header {key!r} empty")
    if "seed" in h and (not isinstance(h["seed"], str) or not h["seed"]):
        rep.error("header seed empty (run not seeded)")
    unlocks = h.get("unlocks")
    if isinstance(unlocks, dict):
        for k in ("locked", "undiscovered"):
            if unlocks.get(k) != 0:
                rep.error(f"unlocks.{k} = {unlocks.get(k)!r} (profile not fully unlocked)")
    elif "unlocks" in h:
        rep.error("header unlocks is not an object")
    if sum(1 for line in traj.lines if line.get("t") == "header") > 1:
        rep.error("more than one header line")


def _check_step(step: dict[str, Any], seed: str | None, rep: ValidationReport) -> None:
    where = f"step {step.get('i')} (line {step['_line']})"
    for key in STEP_REQUIRED:
        if key not in step:
            rep.error(f"{where}: missing {key!r}")
    action, legal, obs = step.get("action"), step.get("legal"), step.get("obs")
    if not isinstance(action, dict) or not isinstance(action.get("type"), str):
        rep.error(f"{where}: action must be {{type, params}}")
        return
    result = step.get("result")
    if not isinstance(result, dict) or result.get("ok") is not True:
        rep.error(f"{where}: result.ok is not true")
    if not isinstance(legal, dict):
        rep.error(f"{where}: legal is not an object")
    else:
        if legal.get("settled") is not True:
            rep.error(f"{where}: legal.settled is not true")
        reason = check_action(legal, action)
        if reason:
            rep.error(f"{where}: illegal action {json.dumps(action, sort_keys=True)}: {reason}")
    if not isinstance(obs, dict):
        rep.error(f"{where}: obs is not an object")
        return
    if isinstance(legal, dict) and obs.get("phase") != legal.get("phase"):
        rep.error(f"{where}: obs.phase {obs.get('phase')!r} != legal.phase {legal.get('phase')!r}")
    for leak in hidden_leaks(obs, seed):
        rep.error(f"{where}: {leak}")


def validate_trajectory(traj: Trajectory | str | os.PathLike) -> ValidationReport:
    if not isinstance(traj, Trajectory):
        traj = read_trajectory(traj)
    rep = ValidationReport(path=str(traj.path), steps=len(traj.steps), rejects=len(traj.rejects),
                           outcome=traj.outcome)
    if traj.read_error:
        rep.error(f"unreadable: {traj.read_error}")
        return rep
    if traj.truncated:
        rep.error("truncated: last line incomplete")
    for no, msg in traj.parse_errors:
        if not (traj.truncated and no >= max((ln["_line"] for ln in traj.lines), default=0)):
            rep.error(f"line {no}: {msg}")
    _check_header(traj, rep)
    seed = (traj.header or {}).get("seed")

    prev_step_i: int | None = None
    prev_i: int | None = None
    prev_ts: int | None = None
    end_seen = False
    for line in traj.lines:
        t = line.get("t")
        if t == "debug":
            rep.error(f"line {line['_line']}: debug/eval line (test-only bridge mode; run is tainted)")
            continue
        if t not in ("header", "step", "reject", "end"):
            rep.error(f"line {line['_line']}: unknown line type {t!r}")
            continue
        if end_seen:
            rep.error(f"line {line['_line']}: {t} line after end")
        ts = line.get("ts_ms")
        if t in ("step", "reject", "end"):
            if not isinstance(ts, (int, float)):
                rep.error(f"line {line['_line']}: {t} missing ts_ms")
            elif prev_ts is not None and ts < prev_ts:
                rep.error(f"line {line['_line']}: ts_ms went backwards ({ts} < {prev_ts})")
            else:
                prev_ts = ts
        if t in ("step", "reject"):
            i = line.get("i")
            if not isinstance(i, int) or isinstance(i, bool):
                rep.error(f"line {line['_line']}: {t} index i={i!r} is not an int")
                continue
            if prev_i is not None and i < prev_i:
                rep.error(f"line {line['_line']}: {t} index {i} < previous {prev_i}")
            prev_i = i
            if t == "step":
                if prev_step_i is not None and i != prev_step_i + 1:
                    rep.error(f"line {line['_line']}: step index {i} does not follow {prev_step_i}")
                prev_step_i = i
                _check_step(line, seed, rep)
            elif "action" not in line or "error" not in line:
                rep.error(f"line {line['_line']}: reject missing action/error")
        elif t == "end":
            end_seen = True

    end = traj.end
    if end is None:
        rep.warnings.append("no end line (abandoned/crashed run)")
    else:
        if end.get("outcome") not in OUTCOMES:
            rep.error(f"end outcome {end.get('outcome')!r} not in {sorted(OUTCOMES)}")
        if end.get("steps") != len(traj.steps):
            rep.error(f"end.steps={end.get('steps')!r} but file has {len(traj.steps)} steps")
        if end.get("tainted"):
            rep.error("end.tainted = true (debug eval was used)")
        if isinstance(end.get("final_obs"), dict):
            for leak in hidden_leaks(end["final_obs"], seed, "final_obs"):
                rep.error(f"end: {leak}")
        elif "final_obs" in end:
            rep.error("end final_obs is not an object")
    return rep
