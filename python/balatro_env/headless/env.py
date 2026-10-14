"""Single-process headless environment: reset(seed, deck, stake) / step(action) over the bridge API."""

from __future__ import annotations

import gzip
import json
import os
import random
from pathlib import Path
from typing import Any

from balatro_env.data.legality import entry_is_satisfiable, sample_params
from balatro_env.headless.engine import Engine, EngineError

TERMINAL_PHASES = frozenset({"GAME_OVER", "WIN"})
SETTLE_FRAMES = 60_000


class HeadlessEnv:
    """One headless game. Observations and legality are the bridge's own `/state` (minus the envelope)
    and `/legal` bodies, so they are identical to a live instance's.

    record_dir: when set, every run is recorded by the bridge recorder as `<record_dir>/trajectories/
    <date>/<seed>_<port>_<ms>.jsonl` in the DATA_CONTRACT format, with `"host": "headless"` in the header.
    """

    def __init__(self, record_dir: str | os.PathLike | None = None, agent: str = "headless",
                 exe: str | None = None, dt: float | None = None, **engine_kw: Any):
        kw = dict(engine_kw)
        if dt is not None:
            kw["dt"] = dt
        self.record_dir = Path(record_dir) if record_dir else None
        self.agent = agent
        self.engine = Engine(exe=exe, data_dir=self.record_dir, **kw)
        self._done = True
        self.frames = 0
        self.steps = 0

    # -- API ------------------------------------------------------------------------------------------

    def reset(self, seed: str | None = None, deck: str = "b_red", stake: int = 1,
              meta: dict[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        params: dict[str, Any] = {"deck": deck, "stake": int(stake)}
        if seed:
            params["seed"] = seed
        self._settle()
        res = self.engine.action("START_RUN", params, {"agent": self.agent, "why": "reset", **(meta or {})})
        if not res.get("ok"):
            raise EngineError(f"START_RUN rejected: {res}")
        self.run_params = res.get("params") or params
        self.trajectory_path = res.get("trajectory_path")
        self._done = False
        self.steps = 0
        obs, legal = self._observe()
        return obs, legal

    def step(self, action: dict[str, Any], meta: dict[str, Any] | None = None
             ) -> tuple[dict[str, Any], dict[str, Any], bool, dict[str, Any]]:
        """Execute `{type, params}`. An illegal action is rejected by the bridge without changing the game:
        info['ok'] is False and info['error'] says why (obs/legal are unchanged)."""
        if self._done:
            raise EngineError("step() on a finished run; call reset()")
        res = self.engine.action(action["type"], action.get("params") or {},
                                 {"agent": self.agent, **(meta or {})})
        info: dict[str, Any] = {"ok": bool(res.get("ok")), "step": res.get("step")}
        if not res.get("ok"):
            info["error"] = res.get("error")
            if res.get("retry"):
                raise EngineError(f"bridge reports unsettled state at a decision point: {res}")
        else:
            self.steps += 1
        obs, legal = self._observe()
        done = obs.get("phase") in TERMINAL_PHASES or bool(obs.get("won"))
        info["phase"] = obs.get("phase")
        info["frames"] = self._last_frames
        if done:
            self._done = True
            self.engine.frames(1)  # let the recorder close the trajectory (rec_watch runs per frame)
            info["outcome"] = "win" if obs.get("won") else "loss"
        return obs, legal, done, info

    # -- helpers --------------------------------------------------------------------------------------

    def _settle(self) -> None:
        frames, ok, phase, reason = self.engine.settle(SETTLE_FRAMES)
        self._last_frames = frames
        self.frames += frames
        if not ok:
            raise EngineError(f"game did not settle after {frames} frames (phase={phase}, reason={reason})")

    def _observe(self) -> tuple[dict[str, Any], dict[str, Any]]:
        self._settle()
        state = self.engine.state()
        for k in ("settled", "settle_reason", "timestamp_ms", "step", "trajectory"):
            state.pop(k, None)
        return state, self.engine.legal()

    @property
    def done(self) -> bool:
        return self._done

    def stats(self) -> dict[str, int]:
        """Virtual frames run so far (all runs) and steps in the current run."""
        return {"frames": self.frames, "steps": self.steps}


def random_legal_action(legal: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Uniform over legal entries (START_RUN excluded), then uniform params inside the entry's domains."""
    entries = [e for e in legal.get("actions") or []
               if e.get("type") != "START_RUN" and entry_is_satisfiable(e)]
    if not entries:
        raise EngineError(f"no legal action in phase {legal.get('phase')}")
    e = rng.choice(entries)
    return {"type": e["type"], "params": sample_params(e, rng)}
