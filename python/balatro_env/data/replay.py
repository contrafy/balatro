"""Live replay verifier: re-run a trajectory's seed + actions on an instance and compare every obs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from balatro_env.data.bridge import Bridge, BridgeError
from balatro_env.data.diff import IdCanon, all_differences, format_diff, normalize
from balatro_env.data.trajectory import Trajectory, find_trajectories, read_trajectory, run_key

END_PHASE = {"loss": "GAME_OVER", "win": "WIN"}


@dataclass
class ReplayResult:
    path: str
    ok: bool = False
    steps_total: int = 0
    steps_matched: int = 0
    divergence_step: int | None = None
    divergence_kind: str | None = None  # obs | legal | rejected | final | start | bridge | post_file
    diff: list[tuple[str, Any, Any]] = field(default_factory=list)
    message: str = ""
    replay_path: str | None = None
    seconds: float = 0.0

    def detail(self) -> str | None:
        if self.ok:
            return None
        where = f"step {self.divergence_step}" if self.divergence_step is not None else "start"
        first = f" at {self.diff[0][0]}" if self.diff else ""
        return f"{self.divergence_kind} divergence {where}{first}: {self.message}"[:500]

    def report(self) -> str:
        head = (f"{'REPLAY_OK' if self.ok else 'REPLAY_DIVERGED'} {self.path} "
                f"matched={self.steps_matched}/{self.steps_total} in {self.seconds:.0f}s")
        if self.replay_path:
            head += f" replay_file={self.replay_path}"
        if self.ok:
            return head
        return f"{head}\n  {self.detail()}\n{format_diff(self.diff)}" if self.diff else f"{head}\n  {self.detail()}"


class _Sides:
    """Per-side id canonicalizers, shared across the whole trajectory (consistent bijection)."""

    def __init__(self) -> None:
        self.rec, self.live = IdCanon(), IdCanon()

    def diff(self, recorded: Any, live: Any) -> list[tuple[str, Any, Any]]:
        return all_differences(normalize(recorded, self.rec), normalize(live, self.live))


def replay(path: str | Path, port: int, settle_timeout: float = 90.0, compare_legal: bool = True,
           check_file: bool = True, log=print) -> ReplayResult:
    traj = read_trajectory(path)
    res = ReplayResult(path=str(path), steps_total=len(traj.steps))
    t0 = time.monotonic()
    try:
        _run(traj, Bridge(port), res, settle_timeout, compare_legal, log)
        if res.ok and check_file and res.replay_path:
            _compare_files(traj, res, log)
    except BridgeError as exc:
        res.ok = False
        res.divergence_kind = res.divergence_kind or "bridge"
        res.message = str(exc)
    res.seconds = time.monotonic() - t0
    return res


def _run(traj: Trajectory, bridge: Bridge, res: ReplayResult, settle_timeout: float,
         compare_legal: bool, log) -> None:
    if traj.header is None:
        res.divergence_kind, res.message = "start", "trajectory has no header"
        return
    key = traj.key
    params = {k: v for k, v in traj.start_params.items() if v is not None}
    meta = {"why": f"replay verification of {key}", "agent": "replay", "replay_of": key}
    started = bridge.act_settled("START_RUN", params, meta)
    if not started.get("ok"):
        res.divergence_kind, res.message = "start", f"START_RUN rejected: {started}"
        return
    res.replay_path = started.get("trajectory_path") or bridge.health().get("trajectory_path")
    sides = _Sides()
    for step in traj.steps:
        i = step.get("i")
        state, legal = bridge.wait_settled(settle_timeout)
        diffs = sides.diff(step.get("obs"), state)
        if diffs:
            res.divergence_step, res.divergence_kind, res.diff = i, "obs", diffs
            res.message = f"{len(diffs)} differing paths (first {diffs[0][0]})"
            return
        if compare_legal:
            diffs = sides.diff(step.get("legal"), legal)
            if diffs:
                res.divergence_step, res.divergence_kind, res.diff = i, "legal", diffs
                res.message = f"{len(diffs)} differing paths in /legal"
                return
        action = step["action"]
        out = bridge.action(action["type"], action.get("params") or {},
                            {"why": f"replay step {i} of {key}", "agent": "replay", "replay_of": key,
                             "replay_step": i})
        if not out.get("ok"):
            res.divergence_step, res.divergence_kind = i, "rejected"
            res.message = f"recorded action {action} rejected on replay: {out.get('error')!r}"
            return
        res.steps_matched += 1
        if res.steps_matched % 50 == 0:
            log(f"  replay {key}: {res.steps_matched}/{res.steps_total} steps match")
    end = traj.end
    if end and end.get("outcome") in END_PHASE and isinstance(end.get("final_obs"), dict):
        state, _ = bridge.wait_settled(settle_timeout)
        diffs = sides.diff(end["final_obs"], state)
        if diffs:
            res.divergence_kind, res.diff = "final", diffs
            res.message = f"final obs differs ({len(diffs)} paths)"
            return
    res.ok = True


def _find_replay_file(replay_path: str, wait_s: float = 15.0) -> Path | None:
    """The bridge may gzip a closed file; look for either name."""
    p = Path(replay_path)
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        for cand in (p, p.with_name(run_key(p) + ".jsonl.gz"), p.with_name(run_key(p) + ".jsonl")):
            if cand.exists():
                return cand
        time.sleep(0.5)
    return None


def _compare_files(orig: Trajectory, res: ReplayResult, log) -> None:
    """Post-hoc: the replay's own recording must match the original step-for-step, including hidden
    draw order (which the live check cannot see). Skipped while the replay file is still open."""
    path = _find_replay_file(res.replay_path or "")
    if path is None:
        log(f"  replay file {res.replay_path} not found; skipped post-hoc file comparison")
        return
    rep = read_trajectory(path)
    if len(rep.steps) < len(orig.steps):
        log(f"  replay file has {len(rep.steps)}/{len(orig.steps)} steps so far; skipped file comparison")
        return
    sides = _Sides()
    for a, b in zip(orig.steps, rep.steps):
        for part in ("obs", "hidden", "legal", "action", "refs"):
            diffs = sides.diff(a.get(part), b.get(part))
            if diffs:
                res.ok = False
                res.divergence_step, res.divergence_kind, res.diff = a.get("i"), f"post_file:{part}", diffs
                res.message = f"replay recording differs in step.{part}"
                return
    if orig.end and rep.end and orig.end.get("outcome") != rep.end.get("outcome"):
        res.ok = False
        res.divergence_kind = "post_file:end"
        res.message = f"outcome {orig.end.get('outcome')} vs replay {rep.end.get('outcome')}"


def replay_many(paths: list[str], port: int, **kw) -> list[ReplayResult]:
    files: list[Path] = []
    for p in paths:
        files.extend(find_trajectories(p))
    return [replay(f, port, **kw) for f in files]
