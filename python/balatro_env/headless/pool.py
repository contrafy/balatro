"""Vectorized headless environments: one HeadlessEnv per worker process, driven over pipes.

    with HeadlessPool(4) as pool:
        first = pool.reset([{"seed": s, "deck": "b_black", "stake": 1} for s in seeds])   # [(obs, legal)]
        out = pool.step(actions)                                                           # [(obs, legal, done, info)]

Every call is broadcast to all workers first and then collected, so the workers step in parallel.
`send`/`recv` give per-worker asynchronous control for policies that do not step in lockstep.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import traceback
from typing import Any

from balatro_env.headless.engine import EngineError


def _worker(conn, index: int, env_kw: dict[str, Any]) -> None:
    from balatro_env.headless.env import HeadlessEnv

    try:
        env = HeadlessEnv(port=env_kw.pop("port", 0) + index, **env_kw)
        conn.send(("ok", None))
    except BaseException as exc:  # boot failure: report and exit
        conn.send(("err", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"))
        return
    while True:
        try:
            cmd, args, kwargs = conn.recv()
        except (EOFError, KeyboardInterrupt):
            return
        if cmd == "close":
            conn.send(("ok", None))
            return
        try:
            conn.send(("ok", getattr(env, cmd)(*args, **kwargs)))
        except BaseException as exc:
            conn.send(("err", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"))


class HeadlessPool:
    """N headless games in N processes. Worker i records (if record_dir is set) with header port = port + i."""

    def __init__(self, n_workers: int, record_dir: str | os.PathLike | None = None, agent: str = "headless",
                 port: int = 0, start_method: str = "spawn", **env_kw: Any):
        ctx = mp.get_context(start_method)
        self.n = n_workers
        self._conns = []
        self._procs = []
        kw = dict(env_kw, record_dir=str(record_dir) if record_dir else None, agent=agent, port=port)
        for i in range(n_workers):
            parent, child = ctx.Pipe()
            p = ctx.Process(target=_worker, args=(child, i, dict(kw)), daemon=True)
            p.start()
            child.close()
            self._conns.append(parent)
            self._procs.append(p)
        errors = [r for r in (self._recv_raw(i) for i in range(n_workers)) if r[0] != "ok"]
        if errors:
            self.close()
            raise EngineError(f"{len(errors)} worker(s) failed to boot: {errors[0][1]}")

    # -- per-worker async ------------------------------------------------------------------------------

    def send(self, i: int, cmd: str, *args: Any, **kwargs: Any) -> None:
        self._conns[i].send((cmd, args, kwargs))

    def _recv_raw(self, i: int) -> tuple[str, Any]:
        try:
            return self._conns[i].recv()
        except EOFError:
            return ("err", f"worker {i} died (exit code {self._procs[i].exitcode})")

    def recv(self, i: int) -> Any:
        status, value = self._recv_raw(i)
        if status != "ok":
            raise EngineError(f"worker {i}: {value}")
        return value

    # -- batched ----------------------------------------------------------------------------------------

    def call(self, cmd: str, args_per_worker: list[tuple] | None = None,
             kwargs_per_worker: list[dict[str, Any]] | None = None) -> list[Any]:
        for i in range(self.n):
            self.send(i, cmd, *(args_per_worker[i] if args_per_worker else ()),
                      **(kwargs_per_worker[i] if kwargs_per_worker else {}))
        return [self.recv(i) for i in range(self.n)]

    def reset(self, starts: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        """starts[i] = reset kwargs for worker i: seed, deck, stake, meta."""
        return self.call("reset", kwargs_per_worker=starts)

    def step(self, actions: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any], bool, dict[str, Any]]]:
        return self.call("step", args_per_worker=[(a,) for a in actions])

    def close(self) -> None:
        for i, c in enumerate(self._conns):
            try:
                c.send(("close", (), {}))
            except (OSError, BrokenPipeError):
                pass
        for p in self._procs:
            p.join(timeout=5)
            if p.is_alive():
                p.kill()
        for c in self._conns:
            c.close()
        self._conns, self._procs = [], []

    def __enter__(self) -> HeadlessPool:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def __len__(self) -> int:
        return self.n
