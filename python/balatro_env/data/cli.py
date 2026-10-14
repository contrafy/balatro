"""`balatro-data` command line: validate | manifest | replay | fuzz | compress | seeds | status | dashboard | dataops."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from balatro_env.data import seeds as seedmod
from balatro_env.data.manifest import build_manifest, update_replay_result
from balatro_env.data.status import LIVE_WINDOW_S, RUNS_DIR, STATUS_PATH
from balatro_env.data.trajectory import data_dir, dataset_files, find_trajectories
from balatro_env.data.validate import validate_trajectory


def _expand(paths: list[str], root: Path) -> list[Path]:
    if not paths:
        return dataset_files(root)
    out: list[Path] = []
    for p in paths:
        out.extend(find_trajectories(p))
    return out


def cmd_validate(args: argparse.Namespace) -> int:
    files = _expand(args.paths, data_dir(args.data_dir))
    if not files:
        print("no trajectory files found", file=sys.stderr)
        return 1
    bad = 0
    for f in files:
        rep = validate_trajectory(f)
        print(rep.summary())
        if args.verbose:
            for e in rep.errors:
                print(f"  - {e}")
        bad += not rep.ok
    print(f"{len(files) - bad}/{len(files)} valid")
    return 1 if bad else 0


def cmd_manifest(args: argparse.Namespace) -> int:
    path, rows = build_manifest(args.data_dir)
    usable = sum(1 for r in rows if r["schema_ok"] and r.get("replay_ok"))
    pending = sum(1 for r in rows if r["schema_ok"] and r.get("replay_ok") is None)
    print(f"wrote {path}: {len(rows)} trajectories, {usable} usable (schema_ok && replay_ok), "
          f"{pending} awaiting replay, {sum(1 for r in rows if r['quarantined_reason'])} quarantined")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    from balatro_env.data.replay import replay

    files = _expand(args.paths, data_dir(args.data_dir))
    failed = 0
    for f in files:
        res = replay(f, args.port, compare_legal=not args.no_legal, check_file=not args.no_file_check)
        print(res.report())
        failed += not res.ok
        if args.update_manifest:
            update_replay_result(args.data_dir, f, res.ok, res.detail(), res.replay_path,
                                 int(time.time() * 1000), res.steps_total)
    print(f"{len(files) - failed}/{len(files)} replays matched")
    return 1 if failed else 0


def cmd_fuzz(args: argparse.Namespace) -> int:
    from balatro_env.data.fuzz import Fuzzer, write_report

    inst = Path(args.instance_dir) if args.instance_dir else \
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / "balatro-instances" / str(args.port)
    fz = Fuzzer(args.port, seed_start=args.seed_start, rng_seed=args.rng_seed,
                probes_per_step=args.probes, instance_dir=inst)
    stats = fz.run(args.runs, args.steps, args.total_steps)
    report = write_report(stats, data_dir(args.data_dir) / "fuzz")
    d = stats.as_dict()
    print(json.dumps({k: d[k] for k in ("runs", "steps", "acceptance_rate", "probes_sent", "probes_rejected",
                                        "accepted", "phases", "run_summaries")}, indent=1, default=str))
    problems = {k: len(d[k]) for k in ("legal_rejections", "probe_accepted", "probe_state_changed",
                                       "bridge_errors", "log_errors", "crashes", "stuck")}
    print(f"problems: {problems}\nreport: {report}")
    return 1 if any(problems.values()) else 0


def cmd_compress(args: argparse.Namespace) -> int:
    from balatro_env.data.dataops import compress_trajectories

    done = compress_trajectories(args.data_dir, include_unfinished=args.include_unfinished, min_age_s=args.min_age_s,
                                 include_superseded=args.include_superseded)
    print(f"{done} files compressed")
    return 0


def cmd_seeds(args: argparse.Namespace) -> int:
    if args.check:
        reason = seedmod.reserved_reason(args.check)
        print(f"{args.check}: {reason or 'free'}")
        return 1 if reason else 0
    if args.write_eval:
        seedmod.write_eval_seeds()
        print(f"wrote {seedmod.EVAL_SEEDS_PATH}")
        return 0
    for s in seedmod.swarm_seeds(args.count):
        print(s)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    from balatro_env.data.status import update_status_file

    path, block, st = update_status_file(args.data_dir, args.out, args.runs_dir, live_window_s=args.live_window)
    if args.print:
        print(block)
    c = st["counts"]
    print(f"wrote {path}: {c['player_runs']} player runs ({c['finished']} finished, {c['live']} live)")
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    from balatro_env.data.dashboard import serve

    serve(args.data_dir, args.host, args.port, args.runs_dir, args.live_window, args.refresh)
    return 0


def cmd_dataops(args: argparse.Namespace) -> int:
    from balatro_env.data.dataops import DataOps

    DataOps(args.data_dir, args.replay_port, args.status_out, args.runs_dir, include_fuzz=args.include_fuzz,
            max_replays=args.max_replays, live_window_s=args.live_window).run(args.interval, once=args.once)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="balatro-data", description=__doc__)
    p.add_argument("--data-dir", default=None, help="dataset root (default $BALATRO_RL_DATA_DIR or ./data)")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="schema + legality check of trajectory files")
    v.add_argument("paths", nargs="*", help="files or directories (default: <data>/trajectories)")
    v.add_argument("-v", "--verbose", action="store_true", help="print every error")
    v.set_defaults(fn=cmd_validate)

    m = sub.add_parser("manifest", help="rebuild <data>/manifest.jsonl (keeps earlier replay results)")
    m.set_defaults(fn=cmd_manifest)

    r = sub.add_parser("replay", help="live replay verification on an idle instance")
    r.add_argument("paths", nargs="+")
    r.add_argument("--port", type=int, required=True)
    r.add_argument("--update-manifest", action="store_true", help="store replay_ok in the manifest")
    r.add_argument("--no-legal", action="store_true", help="compare obs only, not /legal")
    r.add_argument("--no-file-check", action="store_true", help="skip comparing the replay's own recording")
    r.set_defaults(fn=cmd_replay)

    f = sub.add_parser("fuzz", help="live legality fuzzer (FUZZ* seeds)")
    f.add_argument("--port", type=int, required=True)
    f.add_argument("--runs", type=int, default=5)
    f.add_argument("--steps", type=int, default=400, help="max steps per run")
    f.add_argument("--total-steps", type=int, default=None, help="stop after this many steps overall")
    f.add_argument("--seed-start", type=int, default=0, help="first FUZZ seed index")
    f.add_argument("--rng-seed", type=int, default=None)
    f.add_argument("--probes", type=int, default=6, help="illegal probes per decision point (0 = off)")
    f.add_argument("--instance-dir", default=None, help="default ~/balatro-instances/<port>")
    f.set_defaults(fn=cmd_fuzz)

    c = sub.add_parser("compress", help="gzip finished trajectories")
    c.add_argument("--include-unfinished", action="store_true", help="also gzip end-less files older than --min-age-s")
    c.add_argument("--min-age-s", type=float, default=3600)
    c.add_argument("--include-superseded", action="store_true",
                   help="also gzip end-less files whose port has a newer trajectory (closed by a crash)")
    c.set_defaults(fn=cmd_compress)

    s = sub.add_parser("seeds", help="fresh training seeds (never eval/fuzz seeds)")
    s.add_argument("--count", type=int, default=1)
    s.add_argument("--check", metavar="SEED", help="exit 1 if SEED is reserved (eval or fuzz)")
    s.add_argument("--write-eval", action="store_true", help=argparse.SUPPRESS)
    s.set_defaults(fn=cmd_seeds)

    st = sub.add_parser("status", help="regenerate the AUTO block of docs/SWARM_STATUS.md")
    st.add_argument("--out", default=str(STATUS_PATH), help="status markdown file (default docs/SWARM_STATUS.md)")
    st.add_argument("--runs-dir", default=str(RUNS_DIR), help="post-mortems dir (default docs/runs)")
    st.add_argument("--live-window", type=float, default=LIVE_WINDOW_S,
                    help="seconds since the last write for an open run to count as live")
    st.add_argument("--print", action="store_true", help="also print the generated block")
    st.set_defaults(fn=cmd_status)

    d = sub.add_parser("dashboard", help="local auto-refreshing status page (stdlib HTTP server)")
    d.add_argument("--port", type=int, default=8765)
    d.add_argument("--host", default="127.0.0.1")
    d.add_argument("--refresh", type=int, default=15, help="page auto-refresh seconds")
    d.add_argument("--runs-dir", default=str(RUNS_DIR))
    d.add_argument("--live-window", type=float, default=LIVE_WINDOW_S)
    d.set_defaults(fn=cmd_dashboard)

    o = sub.add_parser("dataops", help="loop: compress, validate, manifest, replay new runs, status")
    o.add_argument("--replay-port", type=int, required=True, help="port of the dedicated replay instance")
    o.add_argument("--interval", type=float, default=300, help="seconds between iteration starts")
    o.add_argument("--once", action="store_true", help="run a single iteration and exit")
    o.add_argument("--max-replays", type=int, default=None, help="cap replays per iteration")
    o.add_argument("--include-fuzz", action="store_true", help="also replay FUZZ* runs")
    o.add_argument("--status-out", default=str(STATUS_PATH))
    o.add_argument("--runs-dir", default=str(RUNS_DIR))
    o.add_argument("--live-window", type=float, default=LIVE_WINDOW_S)
    o.set_defaults(fn=cmd_dataops)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
