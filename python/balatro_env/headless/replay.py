"""Headless replay verifier: re-run a trajectory's seed + actions in the headless engine and compare every
obs/legal with the recording, using the same normalization and diff code as the live verifier
(`balatro_env.data.replay`)."""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from balatro_env.data.replay import END_PHASE, ReplayResult, _compare_files, _Sides
from balatro_env.data.trajectory import Trajectory, find_trajectories, read_trajectory
from balatro_env.headless.engine import Engine, EngineError

SETTLE_FRAMES = 60_000


def replay(path: str | Path, engine: Engine | None = None, compare_legal: bool = True,
           check_file: bool = True, log=print, **engine_kw: Any) -> ReplayResult:
    """Replay one file. With check_file, the replay is recorded to a temporary data dir and its file is
    compared step-for-step with the original, including `hidden` (draw order, face-down cards)."""
    traj = read_trajectory(path)
    res = ReplayResult(path=str(path), steps_total=len(traj.steps))
    t0 = time.monotonic()
    tmp = Path(tempfile.mkdtemp(prefix="balatro-headless-replay-")) if check_file else None
    try:
        if engine is None or check_file:
            engine = Engine(data_dir=tmp, **engine_kw)
        _run(traj, engine, res, compare_legal, log)
        if res.ok and check_file and res.replay_path:
            _finish_recording(engine)
            _compare_files(traj, res, log)
    except EngineError as exc:
        res.ok = False
        res.divergence_kind = res.divergence_kind or "bridge"
        res.message = str(exc)
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
    if tmp is not None:
        res.replay_path = None  # temporary file, already deleted
    res.seconds = time.monotonic() - t0
    return res


def _finish_recording(engine: Engine) -> None:
    # The recorder closes (and gzips) the file on the frame after GAME_OVER / win.
    engine.frames(2)


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
    meta = {"why": f"headless replay verification of {key}", "agent": "test-headless-replay", "replay_of": key}
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
                            {"why": f"replay step {i} of {key}", "agent": "test-headless-replay",
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
        state, _ = _settled(engine, res, None)
        diffs = sides.diff(end["final_obs"], state)
        if diffs:
            res.divergence_kind, res.diff = "final", diffs
            res.message = f"final obs differs ({len(diffs)} paths)"
            return
    res.ok = True


def replay_many(paths: list[str], log=print, **kw: Any) -> list[ReplayResult]:
    files: list[Path] = []
    for p in paths:
        files.extend(find_trajectories(p))
    return [replay(f, log=log, **kw) for f in files]
