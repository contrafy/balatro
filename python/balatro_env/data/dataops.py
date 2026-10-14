"""`balatro-data dataops`: the unattended data pipeline loop, and `compress_trajectories` (`balatro-data compress`).

Each iteration: compress closed `.jsonl` files -> manifest (validates new/changed files) -> replay verification of
every closed, schema_ok player run without a verdict: headlessly on `headless_workers` processes
(`balatro_env.headless`), and live (gui) on the replay port for a ~1-in-`gui_every` spot-check sample plus every
headless divergence, one live replay at a time (instance launched / relaunched there by PID when its bridge is
down; no other port is ever touched) -> regenerate the SWARM_STATUS.md block. Logs to `<data>/dataops.log`.
"""

from __future__ import annotations

import gzip
import logging
import multiprocessing as mp
import os
import queue
import re
import shutil
import subprocess
import sys
import time
import zlib
from collections import deque
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

from balatro_env.data.manifest import ReplayVerdict, build_manifest, record_replays
from balatro_env.data.status import (
    LIVE_WINDOW_S,
    REPO_ROOT,
    RUNS_DIR,
    STATUS_PATH,
    PostMortemIndex,
    RunScanner,
    update_status_file,
)
from balatro_env.data.trajectory import data_dir, dataset_files, read_trajectory, run_key

LAUNCHER = REPO_ROOT / "game_mod" / "windows" / "launch_instance.ps1"
_KEY_RE = re.compile(r"^(?P<seed>[^_]+)_(?P<port>\d+)_(?P<ms>\d+)$")
# Bridge-level replay failures (instance died / never settled) are retried this many times before the verdict sticks.
MAX_BRIDGE_ATTEMPTS = 3


def _port_and_ms(path: Path) -> tuple[int | None, int]:
    m = _KEY_RE.match(run_key(path))
    return (int(m["port"]), int(m["ms"])) if m else (None, 0)


def superseded_files(files: list[Path]) -> set[Path]:
    """Plain .jsonl files whose port has a newer trajectory: the bridge keeps one open file per instance, so these
    are closed for good (crashed instance or an end line never written)."""
    newest: dict[int, int] = {}
    for f in files:
        port, ms = _port_and_ms(f)
        if port is not None:
            newest[port] = max(newest.get(port, 0), ms)
    out: set[Path] = set()
    for f in files:
        port, ms = _port_and_ms(f)
        if f.suffix == ".jsonl" and port is not None and ms < newest[port]:
            out.add(f)
    return out


def compress_trajectories(root: str | os.PathLike | None = None, include_unfinished: bool = False,
                          min_age_s: float = 3600, include_superseded: bool = False,
                          superseded_min_age_s: float = 600, log: Callable[[str], None] = print) -> int:
    """Gzip `.jsonl` trajectories that are closed: they have an `end` line; or (`include_unfinished`) are end-less
    and untouched for `min_age_s`; or (`include_superseded`) are end-less, their port has a newer file, and they are
    untouched for `superseded_min_age_s`. The gzip is verified (same line count) before the original is removed."""
    root = data_dir(root)
    files = dataset_files(root)
    superseded = superseded_files(files) if include_superseded else set()
    now = time.time()
    done = 0
    for f in [p for p in files if p.suffix == ".jsonl"]:
        try:
            age = now - f.stat().st_mtime
        except FileNotFoundError:
            continue
        traj = read_trajectory(f)
        if traj.end is None and not ((include_unfinished and age > min_age_s)
                                     or (f in superseded and age > superseded_min_age_s)):
            continue
        gz = f.with_name(f.name + ".gz")
        with open(f, "rb") as src, gzip.open(gz, "wb") as dst:
            shutil.copyfileobj(src, dst)
        check = read_trajectory(gz)
        if check.lines and len(check.lines) == len(traj.lines):
            try:
                f.unlink()
            except OSError as exc:  # still open somewhere: keep the original, drop the copy
                gz.unlink()
                log(f"could not remove {f} ({exc}); kept uncompressed")
                continue
            done += 1
            log(f"compressed {gz}")
        else:
            gz.unlink()
            log(f"compression check failed, kept {f}")
    return done


def replayable(row: dict[str, Any], include_fuzz: bool = False) -> bool:
    """Closed (.gz), schema_ok player run: not a replay, not a `test-*` agent, not a fuzz seed (unless asked)."""
    agent = str(row.get("agent") or "")
    if not (row.get("schema_ok") and str(row.get("path", "")).endswith(".gz")):
        return False
    if row.get("replay_of") or agent == "replay" or agent.startswith("test-"):
        return False
    return include_fuzz or not str(row.get("seed") or "").upper().startswith("FUZZ")


def gui_spot_check(run_key: str, every: int) -> bool:
    """Stable ~1-in-`every` sample of runs that also get a live (gui) replay; 0 = none."""
    return every > 0 and zlib.crc32(run_key.encode("utf-8")) % every == 0


def _oldest_first(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (_port_and_ms(Path(r["path"]))[1], r["run_key"]))


def headless_candidates(rows: list[dict[str, Any]], include_fuzz: bool = False) -> list[dict[str, Any]]:
    """Replayable rows without any verdict yet (a pre-per-host `replay_ok` counts as a gui verdict)."""
    return _oldest_first([r for r in rows if replayable(r, include_fuzz) and r.get("replay_ok") is None
                          and r.get("headless_replay_ok") is None and r.get("gui_replay_ok") is None])


def gui_candidates(rows: list[dict[str, Any]], include_fuzz: bool = False, every: int = 10,
                   headless: bool = True) -> list[dict[str, Any]]:
    """Rows for a live replay. Without headless: every unverified row. With headless: the spot-check sample and
    every run the headless engine found divergent (the live game decides whether the data or the engine is off)."""
    out = []
    for r in rows:
        if not replayable(r, include_fuzz) or r.get("gui_replay_ok") is not None:
            continue
        if r.get("replay_ok") is not None and not r.get("replay_host"):  # legacy gui verdict
            continue
        if (r.get("replay_ok") is None if not headless
                else gui_spot_check(r["run_key"], every) or r.get("headless_replay_ok") is False):
            out.append(r)
    return _oldest_first(out)


def split_by_hash(rows: list[dict[str, Any]], bridge_hash: str | None) -> tuple[list[dict[str, Any]], int]:
    """Rows recorded under the replaying bridge's hash (a verdict across bridge versions means nothing), and the
    number skipped."""
    match = [r for r in rows if not bridge_hash or r.get("bridge_hash") == bridge_hash]
    return match, len(rows) - len(match)


def _headless_worker(wid: int, tasks, results) -> None:
    """Worker process: one headless Replayer (engine + temp recording dir), replays paths from `tasks`."""
    from balatro_env.headless.replay import Replayer

    def boot() -> tuple[Any, str | None]:
        rep = Replayer(check_file=True)
        return rep, rep.engine.health().get("bridge_hash")

    try:
        rep, bridge_hash = boot()
    except BaseException as exc:
        results.put(("boot_error", wid, f"{type(exc).__name__}: {exc}"))
        return
    results.put(("boot", wid, bridge_hash))
    try:
        while (path := tasks.get()) is not None:
            try:
                res = rep.replay(path, log=lambda *a: None)
                item = {"path": path, "ok": res.ok, "detail": res.detail(), "steps_total": res.steps_total,
                        "steps_matched": res.steps_matched, "seconds": res.seconds,
                        "bridge_hash": bridge_hash, "report": res.report().splitlines()[0]}
            except Exception as exc:  # not a verdict: engine/tool failure; reboot the engine for the next file
                item = {"path": path, "ok": None, "error": f"{type(exc).__name__}: {exc}"}
                rep.close()
                rep, bridge_hash = boot()
            results.put(("result", wid, item))
    finally:
        rep.close()


class HeadlessVerifier:
    """N worker processes replaying trajectories in the headless engine; results arrive on a queue."""

    def __init__(self, n: int) -> None:
        ctx = mp.get_context("spawn")
        self.tasks, self.results = ctx.Queue(), ctx.Queue()
        self.procs = [ctx.Process(target=_headless_worker, args=(i, self.tasks, self.results), daemon=True)
                      for i in range(n)]
        for p in self.procs:
            p.start()
        self.pending = 0
        self.closed = False

    def boot(self, timeout_s: float = 300.0) -> tuple[str | None, list[str]]:
        """Wait for every worker's boot report: (bridge_hash of the engines or None, boot errors)."""
        hashes, errors, seen = set(), [], 0
        deadline = time.monotonic() + timeout_s
        while seen < len(self.procs) and time.monotonic() < deadline:
            try:
                msg = self.results.get(timeout=1)
            except queue.Empty:
                if not any(p.is_alive() for p in self.procs):
                    break
                continue
            seen += 1
            if msg[0] == "boot":
                hashes.add(msg[2])
            else:
                errors.append(msg[2])
        if seen < len(self.procs):
            errors.append(f"{len(self.procs) - seen} worker(s) did not boot within {timeout_s:.0f}s")
        return (hashes.pop() if len(hashes) == 1 else None), errors

    def submit(self, paths: list[Path]) -> None:
        for p in paths:
            self.tasks.put(str(p))
        self.pending += len(paths)
        for _ in self.procs:  # one stop sentinel per worker: they exit once the queue is drained
            self.tasks.put(None)

    def active(self) -> bool:
        return self.pending > 0 and any(p.is_alive() for p in self.procs)

    def poll(self, timeout_s: float = 0.0) -> list[dict[str, Any]]:
        out = []
        try:
            msg = self.results.get(timeout=timeout_s) if timeout_s > 0 else self.results.get_nowait()
            while True:
                if msg[0] == "result":
                    self.pending -= 1
                    out.append(msg[2])
                msg = self.results.get_nowait()
        except queue.Empty:
            pass
        return out

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        for p in self.procs:
            p.join(timeout=30 if self.pending <= 0 else 1)
            if p.is_alive():
                p.kill()
                p.join(timeout=5)
        self.tasks.cancel_join_thread()
        self.results.cancel_join_thread()


class ReplayInstance:
    """The one Balatro instance on the replay port. Only ever looks up, kills or launches that port's process."""

    def __init__(self, port: int, log: Callable[[str], None], launch_timeout_s: float = 120.0) -> None:
        self.port = port
        self.log = log
        self.launch_timeout_s = launch_timeout_s
        self.pid: int | None = None

    def health(self) -> dict[str, Any] | None:
        try:
            h = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=3).json()
        except (requests.RequestException, ValueError):
            return None
        return h if h.get("status") == "ok" else None

    def find_pid(self) -> int | None:
        """PID of the Balatro.exe whose --mod-dir is this port's instance dir (docs/SWARM.md section 5)."""
        ps = ("Get-CimInstance Win32_Process -Filter \"name='Balatro.exe'\" | "
              f"Where-Object {{ $_.CommandLine -like '*balatro-instances\\{self.port}\\*' }} | "
              "Select-Object -ExpandProperty ProcessId")
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                                 timeout=60).stdout
        except (OSError, subprocess.TimeoutExpired):
            return None
        pids = [int(x) for x in out.split() if x.strip().isdigit()]
        return pids[0] if pids else None

    def kill(self) -> None:
        pid = self.find_pid() or self.pid
        if pid:
            self.log(f"killing replay instance PID {pid} (port {self.port})")
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=30)
            time.sleep(2)
        self.pid = None

    def launch(self) -> None:
        out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER),
                              "-Port", str(self.port)], capture_output=True, text=True, timeout=120)
        m = re.search(r"Balatro PID (\d+)", out.stdout)
        if not m:
            raise RuntimeError(f"launcher failed on port {self.port}: {out.stdout.strip()} {out.stderr.strip()}")
        self.pid = int(m.group(1))
        self.log(f"launched replay instance PID {self.pid} on port {self.port}")

    def ensure(self) -> dict[str, Any]:
        """Healthy bridge on the replay port, settled at a decision point; (re)launch only this port if needed."""
        h = self.health()
        if h is None:
            pid = self.find_pid()
            if pid:  # process alive but bridge gone: crashed
                self.log(f"replay port {self.port}: process {pid} alive but bridge offline; restarting it")
                self.kill()
            self.launch()
            deadline = time.monotonic() + self.launch_timeout_s
            while (h := self.health()) is None:
                if time.monotonic() > deadline:
                    raise RuntimeError(f"replay instance on port {self.port} not healthy after "
                                       f"{self.launch_timeout_s:.0f}s")
                time.sleep(2)
        else:
            self.pid = self.pid or self.find_pid()
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:  # MENU settles once the profile unlock has run
            try:
                if requests.get(f"http://127.0.0.1:{self.port}/legal", timeout=3).json().get("settled"):
                    break
            except (requests.RequestException, ValueError):
                pass
            time.sleep(1)
        return h


def setup_logging(root: Path) -> logging.Logger:
    logger = logging.getLogger("balatro_dataops")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
        root.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(root / "dataops.log", encoding="utf-8")
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger


class DataOps:
    def __init__(self, root: str | os.PathLike | None, replay_port: int, status_out: str | os.PathLike = STATUS_PATH,
                 runs_dir: str | os.PathLike = RUNS_DIR, include_fuzz: bool = False, max_replays: int | None = None,
                 live_window_s: float = LIVE_WINDOW_S, headless_workers: int = 3, gui_every: int = 10) -> None:
        self.root = data_dir(root)
        self.log = setup_logging(self.root)
        self.replay_port = replay_port
        self.status_out = Path(status_out)
        self.runs_dir = Path(runs_dir)
        self.include_fuzz = include_fuzz
        self.max_replays = max_replays
        self.live_window_s = live_window_s
        self.headless_workers = headless_workers
        self.gui_every = gui_every
        self.instance = ReplayInstance(replay_port, self.log.info)
        self.scanner = RunScanner(self.root)
        self.pm_index = PostMortemIndex(self.runs_dir)
        self.bridge_attempts: dict[str, int] = {}
        self.known_invalid: set[str] = set()
        self._gui_hash: str | None = None
        self._gui_up: bool | None = None  # per iteration: None = not checked yet

    def status(self) -> None:
        path, _, st = update_status_file(self.root, self.status_out, self.runs_dir, self.scanner, self.pm_index,
                                         self.live_window_s)
        c = st["counts"]
        self.log.info(f"status: {path} ({c['player_runs']} player runs, {c['live']} live)")

    def iteration(self) -> dict[str, int]:
        t0 = time.monotonic()
        compressed = compress_trajectories(self.root, include_superseded=True, log=self.log.info)
        _, rows = build_manifest(self.root, reuse_unchanged=True)
        bad = [r for r in rows if not r["schema_ok"]]
        for r in bad:
            if r["run_key"] not in self.known_invalid:
                self.log.warning(f"validate: {r['run_key']} invalid: {r.get('schema_error')}")
        self.known_invalid = {r["run_key"] for r in bad}
        self.log.info(f"compress: {compressed} files; validate+manifest: {len(rows)} rows, {len(bad)} schema-invalid")
        replayed = self.replay_pending(rows)
        self.status()
        self.log.info(f"iteration done in {time.monotonic() - t0:.0f}s ({replayed} replays)")
        return {"compressed": compressed, "rows": len(rows), "invalid": len(bad), "replayed": replayed}

    def replay_pending(self, rows: list[dict[str, Any]]) -> int:
        """Headless verification of every unverified run on `headless_workers` processes, concurrently with live
        (gui) replays on the replay port, one at a time: the ~1-in-`gui_every` spot-check sample plus every run the
        headless engine found divergent. Without headless workers every unverified run is replayed live."""
        headless = self.headless_workers > 0
        hl_rows = headless_candidates(rows, self.include_fuzz) if headless else []
        gui_rows = gui_candidates(rows, self.include_fuzz, self.gui_every, headless)
        if not hl_rows and not gui_rows:
            self.log.info("replay: nothing pending")
            return 0
        self._gui_up = None
        verifier = self._start_headless(hl_rows) if hl_rows else None
        gui_q = deque(self._gui_filter(gui_rows, "spot-check" if headless else "pending")) if gui_rows else deque()
        queued = {r["run_key"] for r in gui_q}
        done = 0
        last_status = time.monotonic()
        try:
            while True:
                if verifier is not None:
                    done += self._record_headless(verifier.poll(), gui_q, queued)
                if gui_q:
                    done += self._gui_replay(gui_q.popleft())
                elif verifier is not None and verifier.active():
                    done += self._record_headless(verifier.poll(2.0), gui_q, queued)
                else:
                    break
                if time.monotonic() - last_status > 120:
                    self.status()
                    last_status = time.monotonic()
        finally:
            if verifier is not None:
                if verifier.pending > 0:
                    self.log.warning(f"headless: {verifier.pending} runs got no result (worker died); "
                                     "they stay pending")
                verifier.close()
        return done

    def _start_headless(self, rows: list[dict[str, Any]]) -> HeadlessVerifier | None:
        n = min(self.headless_workers, len(rows))
        t0 = time.monotonic()
        verifier = HeadlessVerifier(n)
        bridge_hash, errors = verifier.boot()
        for e in errors:
            self.log.error(f"headless: worker boot failed: {e}")
        if bridge_hash is None:
            self.log.error("headless: no usable engine (boot failed or inconsistent bridge_hash); skipped")
            verifier.close()
            return None
        todo, other = split_by_hash(rows, bridge_hash)
        if other:
            self.log.info(f"headless: {other} pending runs recorded under another bridge_hash than the engine's "
                          f"({bridge_hash[:12]}); skipped")
        if self.max_replays is not None:
            todo = todo[: self.max_replays]
        if not todo:
            verifier.close()
            return None
        verifier.submit([self.root / r["path"] for r in todo])
        self.log.info(f"headless: verifying {len(todo)} runs on {n} workers (booted in "
                      f"{time.monotonic() - t0:.0f}s, bridge {bridge_hash[:12]})")
        return verifier

    def _record_headless(self, items: list[dict[str, Any]], gui_q: deque, queued: set[str]) -> int:
        verdicts = []
        now_ms = int(time.time() * 1000)
        for item in items:
            if item.get("ok") is None:
                self.log.error(f"headless: {item['path']}: no verdict ({item.get('error')}); stays pending")
                continue
            verdicts.append(ReplayVerdict(item["path"], "headless", item["ok"], item["detail"], item["steps_total"],
                                          now_ms, item["bridge_hash"]))
            if item["ok"]:
                self.log.info(f"headless {item['report']}")
                continue
            self.log.warning(f"headless {item['report']} | {item['detail']}")
            path = Path(item["path"])
            row = {"run_key": run_key(path), "steps": item["steps_total"], "bridge_hash": item["bridge_hash"],
                   "path": path.resolve().relative_to(self.root.resolve()).as_posix()}
            if row["run_key"] not in queued and self._gui_filter([row], "headless divergence"):
                queued.add(row["run_key"])
                gui_q.append(row)
        if verdicts:
            record_replays(self.root, verdicts)
        return len(verdicts)

    def _gui_filter(self, rows: list[dict[str, Any]], why: str) -> list[dict[str, Any]]:
        """Rows the live replay instance can verify (same bridge_hash); starts the instance on first use."""
        if self._gui_up is None:
            try:
                self._gui_hash = self.instance.ensure().get("bridge_hash")
                self._gui_up = True
            except Exception as exc:  # launcher/instance problems must not kill the loop
                self.log.error(f"replay instance unavailable: {exc}")
                self._gui_up = False
        if not self._gui_up:
            return []
        todo, other = split_by_hash(rows, self._gui_hash)
        if other:
            self.log.info(f"gui: {other} {why} runs recorded under another bridge_hash than port "
                          f"{self.replay_port}'s ({str(self._gui_hash)[:12]}); skipped")
        if self.max_replays is not None:
            todo = todo[: self.max_replays]
        if todo:
            self.log.info(f"gui: {len(todo)} {why} runs queued for port {self.replay_port}")
        return todo

    def _gui_replay(self, row: dict[str, Any]) -> int:
        from balatro_env.data.replay import replay

        path = self.root / row["path"]
        key = row["run_key"]
        if not path.exists():
            return 0
        try:
            self.instance.ensure()
        except Exception as exc:
            self.log.error(f"replay instance unavailable: {exc}")
            return 0
        self.log.info(f"gui replay: {key} ({row.get('steps')} steps)")
        res = replay(path, self.replay_port, log=self.log.info)
        if not res.ok and res.divergence_kind in ("bridge", "start"):  # instance trouble, not a divergence
            n = self.bridge_attempts[key] = self.bridge_attempts.get(key, 0) + 1
            alive = self.instance.health() is not None
            self.log.warning(f"gui replay: {key} bridge failure #{n} ({res.message}); instance "
                             f"{'alive (hung)' if alive else 'down'}; restarting port {self.replay_port}")
            try:  # crashed or hung: restart only the replay port's own process
                self.instance.kill()
                self.instance.ensure()
            except Exception as exc:
                self.log.error(f"replay instance unavailable: {exc}")
                self._gui_up = False
            if n < MAX_BRIDGE_ATTEMPTS:
                return 0
        record_replays(self.root, [ReplayVerdict(path, "gui", res.ok, res.detail(), res.steps_total,
                                                 int(time.time() * 1000), self._gui_hash, res.replay_path)])
        self.log.info("gui " + res.report().splitlines()[0] + ("" if res.ok else f" | {res.detail()}"))
        return 1

    def run(self, interval_s: float, once: bool = False) -> None:
        self.log.info(f"dataops start: data {self.root.resolve()}, replay port {self.replay_port}, headless workers "
                      f"{self.headless_workers}, gui spot-check 1/{self.gui_every or 'off'}, "
                      f"interval {interval_s:.0f}s, status {self.status_out}")
        while True:
            t0 = time.monotonic()
            try:
                self.iteration()
            except Exception:
                self.log.exception("iteration failed")
            if once:
                return
            time.sleep(max(5.0, interval_s - (time.monotonic() - t0)))
