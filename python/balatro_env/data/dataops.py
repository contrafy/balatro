"""`balatro-data dataops`: the unattended data pipeline loop, and `compress_trajectories` (`balatro-data compress`).

Each iteration: compress closed `.jsonl` files -> manifest (validates new/changed files) -> replay every closed,
schema_ok player run without a verdict, one at a time, on the replay port (instance launched / relaunched there by
PID when its bridge is down; no other port is ever touched) -> regenerate the SWARM_STATUS.md block. Logs to
`<data>/dataops.log`.
"""

from __future__ import annotations

import gzip
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

from balatro_env.data.manifest import build_manifest, update_replay_result
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


def replay_candidates(rows: list[dict[str, Any]], bridge_hash: str | None = None,
                      include_fuzz: bool = False) -> tuple[list[dict[str, Any]], int]:
    """Closed (.gz), schema_ok rows without a replay verdict, oldest first; skips replays of replays, `test-*`
    agents, fuzz seeds (unless `include_fuzz`). Rows recorded under another bridge_hash than the replay instance's
    are skipped (a verdict across bridge versions means nothing); returns (candidates, skipped_for_hash)."""
    out, other_hash = [], 0
    for row in rows:
        agent = str(row.get("agent") or "")
        if not (row.get("schema_ok") and row.get("replay_ok") is None and str(row.get("path", "")).endswith(".gz")):
            continue
        if row.get("replay_of") or agent == "replay" or agent.startswith("test-"):
            continue
        if not include_fuzz and str(row.get("seed") or "").upper().startswith("FUZZ"):
            continue
        if bridge_hash and row.get("bridge_hash") != bridge_hash:
            other_hash += 1
            continue
        out.append(row)
    out.sort(key=lambda r: (_port_and_ms(Path(r["path"]))[1], r["run_key"]))
    return out, other_hash


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
                 live_window_s: float = LIVE_WINDOW_S) -> None:
        self.root = data_dir(root)
        self.log = setup_logging(self.root)
        self.replay_port = replay_port
        self.status_out = Path(status_out)
        self.runs_dir = Path(runs_dir)
        self.include_fuzz = include_fuzz
        self.max_replays = max_replays
        self.live_window_s = live_window_s
        self.instance = ReplayInstance(replay_port, self.log.info)
        self.scanner = RunScanner(self.root)
        self.pm_index = PostMortemIndex(self.runs_dir)
        self.bridge_attempts: dict[str, int] = {}
        self.known_invalid: set[str] = set()

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
        from balatro_env.data.replay import replay

        pre, _ = replay_candidates(rows, None, self.include_fuzz)
        if not pre:
            self.log.info("replay: nothing pending")
            return 0
        try:
            health = self.instance.ensure()
        except Exception as exc:  # launcher/instance problems must not kill the loop
            self.log.error(f"replay instance unavailable: {exc}")
            return 0
        bridge_hash = health.get("bridge_hash")
        todo, other = replay_candidates(rows, bridge_hash, self.include_fuzz)
        if other:
            self.log.info(f"replay: {other} pending runs recorded under another bridge_hash than port "
                          f"{self.replay_port}'s ({str(bridge_hash)[:12]}); skipped")
        if self.max_replays is not None:
            todo = todo[: self.max_replays]
        self.log.info(f"replay: {len(todo)} runs to replay on port {self.replay_port}")
        done = 0
        for row in todo:
            path = self.root / row["path"]
            key = row["run_key"]
            if not path.exists():
                continue
            try:
                self.instance.ensure()
            except Exception as exc:
                self.log.error(f"replay instance unavailable: {exc}")
                break
            self.log.info(f"replay: {key} ({row.get('steps')} steps)")
            res = replay(path, self.replay_port, log=self.log.info)
            if not res.ok and res.divergence_kind in ("bridge", "start"):  # instance trouble, not a divergence
                n = self.bridge_attempts[key] = self.bridge_attempts.get(key, 0) + 1
                alive = self.instance.health() is not None
                self.log.warning(f"replay: {key} bridge failure #{n} ({res.message}); instance "
                                 f"{'alive (hung)' if alive else 'down'}; restarting port {self.replay_port}")
                try:  # crashed or hung: restart only the replay port's own process
                    self.instance.kill()
                    self.instance.ensure()
                except Exception as exc:
                    self.log.error(f"replay instance unavailable: {exc}")
                    break
                if n < MAX_BRIDGE_ATTEMPTS:
                    continue
            update_replay_result(self.root, path, res.ok, res.detail(), res.replay_path,
                                 int(time.time() * 1000), res.steps_total)
            done += 1
            self.log.info(res.report().splitlines()[0] + ("" if res.ok else f" | {res.detail()}"))
            self.status()
        return done

    def run(self, interval_s: float, once: bool = False) -> None:
        self.log.info(f"dataops start: data {self.root.resolve()}, replay port {self.replay_port}, "
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
