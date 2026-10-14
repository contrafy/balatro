"""Headless replay verifier: re-run a trajectory's seed + actions in the headless engine and compare every
obs/legal with the recording, using the same normalization and diff code as the live verifier
(`balatro_env.data.replay`): ids relabeled by first appearance, volatile envelope keys dropped."""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from balatro_env.data.replay import (
    END_PHASE,
    ReplayResult,
    _compare_files,
    _Sides,
    end_from_file,
    finish_final,
)
from balatro_env.data.trajectory import Trajectory, find_trajectories, read_trajectory
from balatro_env.headless.engine import Engine, EngineError

SETTLE_FRAMES = 60_000
REPLAY_AGENT = "test-headless-replay"


class Replayer:
    """One engine reused for many replays. Its recordings go to a private temporary data dir, are compared
    with the originals (including `hidden`) and deleted; the dir is removed on close()."""

    def __init__(self, check_file: bool = True, **engine_kw: Any):
        self.check_file = check_file
        self.tmp = Path(tempfile.mkdtemp(prefix="balatro-headless-replay-")) if check_file else None
        self.engine = Engine(data_dir=self.tmp, **engine_kw)

    def replay(self, path: str | Path, compare_legal: bool = True, log=print) -> ReplayResult:
        traj = read_trajectory(path)
        res = ReplayResult(path=str(path), steps_total=len(traj.steps))
        t0 = time.monotonic()
        try:
            _run(traj, self.engine, res, compare_legal, log)
            if res.ok and self.check_file and res.replay_path:
                self.engine.frames(2)  # the recorder closes + gzips the file on the frame after the run ends
                _compare_files(traj, res, log)
            finish_final(res)
        except EngineError as exc:
            res.ok = False
            res.divergence_kind = res.divergence_kind or "bridge"
            res.message = str(exc)
        self._discard()
        res.replay_path = None  # temporary recording, deleted
        res.seconds = time.monotonic() - t0
        return res

    def _discard(self) -> None:
        """Delete finished temporary recordings. A run without an end line keeps its file open until the
        next START_RUN closes it as abandoned (Windows refuses to delete it before); a later call or
        close() removes it."""
        if self.tmp is None:
            return
        for f in self.tmp.rglob("*.jsonl*"):
            try:
                f.unlink()
            except OSError:
                pass

    def close(self) -> None:
        if self.engine is not None:
            self.engine.close()
            self.engine = None
        if self.tmp is not None:
            shutil.rmtree(self.tmp, ignore_errors=True)

    def __enter__(self) -> Replayer:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def replay(path: str | Path, compare_legal: bool = True, check_file: bool = True, log=print,
           **engine_kw: Any) -> ReplayResult:
    """Replay one file in a fresh engine."""
    with Replayer(check_file=check_file, **engine_kw) as r:
        return r.replay(path, compare_legal=compare_legal, log=log)


def _settled(engine: Engine, res: ReplayResult, i: int | None) -> tuple[dict[str, Any], dict[str, Any]]:
    frames, ok, phase, reason = engine.settle(SETTLE_FRAMES)
    if not ok:
        res.divergence_step, res.divergence_kind = i, "bridge"
        raise EngineError(f"not settled after {frames} frames (phase={phase}, reason={reason})")
    return engine.state(), engine.legal()


def _run(traj: Trajectory, engine: Engine, res: ReplayResult, compare_legal: bool, log) -> None:
    if traj.header is None:
        res.divergence_kind, res.message = "start", "trajectory has no header"
        return
    key = traj.key
    params = {k: v for k, v in traj.start_params.items() if v is not None}
    meta = {"why": f"headless replay verification of {key}", "agent": REPLAY_AGENT, "replay_of": key}
    engine.settle(SETTLE_FRAMES)
    started = engine.action("START_RUN", params, meta)
    if not started.get("ok"):
        res.divergence_kind, res.message = "start", f"START_RUN rejected: {started}"
        return
    res.replay_path = started.get("trajectory_path")
    sides = _Sides()
    for step in traj.steps:
        i = step.get("i")
        state, legal = _settled(engine, res, i)
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
        out = engine.action(action["type"], action.get("params") or {},
                            {"why": f"replay step {i} of {key}", "agent": REPLAY_AGENT,
                             "replay_of": key, "replay_step": i})
        if not out.get("ok"):
            res.divergence_step, res.divergence_kind = i, "rejected"
            res.message = f"recorded action {action} rejected on replay: {out.get('error')!r}"
            return
        res.steps_matched += 1
        if res.steps_matched % 100 == 0:
            log(f"  replay {key}: {res.steps_matched}/{res.steps_total} steps match")
    end = traj.end
    if end and end.get("outcome") in END_PHASE and isinstance(end.get("final_obs"), dict):
        state, _ = _settled(engine, res, None)  # GAME_OVER / WIN overlay; the recorder has written its end line
        if end_from_file(end):
            res.final_pending = True  # verified by _compare_files against the replay's own end line
        else:
            diffs = sides.diff(end["final_obs"], state)
            if diffs:
                res.divergence_kind, res.diff = "final", diffs
                res.message = f"final obs differs ({len(diffs)} paths)"
                return
    res.ok = True


def expand(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        files.extend(find_trajectories(p))
    return files
