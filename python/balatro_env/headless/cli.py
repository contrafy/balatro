"""`balatro-headless`: replay verification and throughput benchmark for the headless engine.

    balatro-headless replay <trajectory.jsonl[.gz] | dir>... [--manifest] [--workers N]
    balatro-headless bench --workers N --steps M
    balatro-headless extract            # extract the game source from Balatro.exe into the cache
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

from balatro_env.data.trajectory import data_dir


# -- replay ---------------------------------------------------------------------------------------------

def _manifest_paths(root: Path, include_all: bool) -> list[Path]:
    manifest = root / "manifest.jsonl"
    if not manifest.is_file():
        raise SystemExit(f"no manifest at {manifest}")
    out = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if include_all or row.get("replay_ok"):
            p = root / row["path"]
            if p.exists():
                out.append(p)
    return out


def _replay_worker(files: list[str], opts: dict[str, Any], queue) -> None:
    from balatro_env.headless.replay import Replayer

    with Replayer(check_file=opts["check_file"], dt=opts["dt"]) as r:
        for f in files:
            res = r.replay(f, compare_legal=opts["compare_legal"], log=lambda *a: None)
            queue.put({"path": f, "ok": res.ok, "report": res.report(), "detail": res.detail(),
                       "steps_total": res.steps_total, "steps_matched": res.steps_matched,
                       "divergence_step": res.divergence_step, "divergence_kind": res.divergence_kind,
                       "seconds": res.seconds})
    queue.put(None)


def cmd_replay(args: argparse.Namespace) -> int:
    from balatro_env.headless.replay import expand

    root = data_dir(args.data_dir)
    files = [str(p) for p in expand(args.paths)]
    if args.manifest or args.manifest_all:
        files += [str(p) for p in _manifest_paths(root, args.manifest_all)]
    files = list(dict.fromkeys(files))
    if not files:
        print("no trajectory files given", file=sys.stderr)
        return 2
    opts = {"check_file": not args.no_file_check, "compare_legal": not args.no_legal, "dt": args.dt}
    n = max(1, min(args.workers, len(files)))
    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    shards = [files[i::n] for i in range(n)]
    procs = [ctx.Process(target=_replay_worker, args=(s, opts, queue), daemon=True) for s in shards]
    for p in procs:
        p.start()
    t0 = time.monotonic()
    results, done = [], 0
    while done < n:
        item = queue.get()
        if item is None:
            done += 1
            continue
        results.append(item)
        print(item["report"], flush=True)
    for p in procs:
        p.join()
    ok = sum(r["ok"] for r in results)
    steps = sum(r["steps_matched"] for r in results)
    print(f"{ok}/{len(files)} replays matched ({steps} steps) in {time.monotonic() - t0:.0f}s "
          f"with {n} worker(s)")
    if len(results) < len(files):
        print(f"{len(files) - len(results)} file(s) produced no result (worker crashed)", file=sys.stderr)
    if args.json:
        Path(args.json).write_text(json.dumps(sorted(results, key=lambda r: r["path"]), indent=1), encoding="utf-8")
    return 0 if ok == len(files) else 1


# -- bench ----------------------------------------------------------------------------------------------

def cmd_bench(args: argparse.Namespace) -> int:
    from balatro_env.headless.env import random_legal_action
    from balatro_env.headless.pool import HeadlessPool

    decks = ["b_red", "b_blue", "b_yellow", "b_green", "b_black", "b_magic", "b_nebula", "b_ghost",
             "b_abandoned", "b_checkered", "b_zodiac", "b_painted", "b_anaglyph", "b_plasma", "b_erratic"]
    rng = random.Random(args.rng_seed)
    run_no = 0

    def start() -> dict[str, Any]:
        nonlocal run_no
        run_no += 1
        return {"seed": f"BENCH{run_no:03d}"[-8:], "deck": rng.choice(decks), "stake": rng.randint(1, 8)}

    t_boot = time.monotonic()
    with HeadlessPool(args.workers, dt=args.dt) as pool:
        boot = time.monotonic() - t_boot
        rngs = [random.Random(args.rng_seed * 1000 + i) for i in range(pool.n)]
        cur = pool.reset([start() for _ in range(pool.n)])
        frames0 = sum(s["frames"] for s in pool.call("stats"))
        steps = runs = 0
        t0 = time.monotonic()
        while steps < args.steps:
            actions = [random_legal_action(legal, rngs[i]) for i, (obs, legal) in enumerate(cur)]
            out = pool.step(actions)
            steps += pool.n
            restart = [i for i, (_, _, done, _) in enumerate(out) if done]
            cur = [(o[0], o[1]) for o in out]
            for i in restart:
                runs += 1
                pool.send(i, "reset", **start())
            for i in restart:
                cur[i] = pool.recv(i)
        elapsed = time.monotonic() - t0
        frames = sum(s["frames"] for s in pool.call("stats")) - frames0
    total = steps / elapsed
    print(json.dumps({
        "workers": pool.n, "steps": steps, "seconds": round(elapsed, 2), "runs_finished": runs,
        "steps_per_s": round(total, 1), "steps_per_s_per_worker": round(total / pool.n, 1),
        "frames_per_step": round(frames / steps, 1), "boot_seconds": round(boot, 2), "dt": args.dt,
        "cpu_count": os.cpu_count(),
    }, indent=1))
    return 0


# -- extract --------------------------------------------------------------------------------------------

def cmd_extract(args: argparse.Namespace) -> int:
    from balatro_env.headless.source import extract_source, game_version

    out = extract_source(args.exe)
    print(f"game source {game_version(out)} at {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from balatro_env.headless.engine import DEFAULT_DT

    ap = argparse.ArgumentParser(prog="balatro-headless", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", help="data root (default $BALATRO_RL_DATA_DIR or ./data)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("replay", help="replay trajectories headlessly and diff every obs/legal")
    p.add_argument("paths", nargs="*")
    p.add_argument("--manifest", action="store_true", help="also every replay_ok row of <data>/manifest.jsonl")
    p.add_argument("--manifest-all", action="store_true", help="every row of the manifest")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--no-legal", action="store_true", help="skip /legal comparison")
    p.add_argument("--no-file-check", action="store_true",
                   help="skip the post-hoc comparison of the replay's own recording (hidden, refs)")
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--json", help="write per-file results to this JSON file")
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("bench", help="random legal policy throughput")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--steps", type=int, default=2000, help="total steps over all workers")
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--rng-seed", type=int, default=0)
    p.set_defaults(func=cmd_bench)

    p = sub.add_parser("extract", help="extract the game source from Balatro.exe into the cache")
    p.add_argument("--exe", help="path to Balatro.exe (default: $BALATRO_EXE or the Steam install)")
    p.set_defaults(func=cmd_extract)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
