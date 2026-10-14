"""Calibration of the round solver's p_clear on recorded Gold decisions.

Rerun: `cd python && python -m balatro_env.analysis.solver_calib [--module balatro_env.solver] [--data-dir ../data]
[--workers 6] [--samples 200] [--limit N] [--out FILE]`. Read-only over `<data>/trajectories/**` (player Gold runs).

For every SELECTING_HAND step whose action is PLAY_HAND or DISCARD, the solver scores the action the player actually
took (`evaluate_action`, from `obs` alone) and the result is compared with what really happened: whether the
player cleared that blind (true draw order, the player's own later actions). Bins of predicted p_clear vs the
realized clear rate; a bin is calibrated when |mean predicted - realized| < 0.05.
"""

from __future__ import annotations

import argparse
import json
import importlib
import multiprocessing as mp
import statistics
import sys
from pathlib import Path

from balatro_env.analysis.gold_stats import is_player_gold
from balatro_env.analysis.solver_eval import KIND, blind_cleared
from balatro_env.data.trajectory import dataset_files, read_trajectory

BINS = ((0.0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 0.95), (0.95, 0.99), (0.99, 1.01))


def jobs(root: Path, limit: int | None):
    out = []
    for path in dataset_files(root):
        traj = read_trajectory(path)
        if not is_player_gold(traj):
            continue
        steps = traj.steps
        first_of_blind = True
        for i, s in enumerate(steps):
            obs, act = s.get("obs") or {}, s.get("action") or {}
            if obs.get("phase") != "SELECTING_HAND":
                first_of_blind = True
                continue
            if act.get("type") not in KIND:
                continue
            cleared = blind_cleared(steps, i, traj.outcome)
            if cleared is None:
                continue
            b = obs.get("blind") or {}
            out.append({"run": traj.key, "i": i, "obs": obs, "kind": KIND[act["type"]],
                        "cards": (act.get("params") or {}).get("card_indices") or [], "cleared": cleared,
                        "first": first_of_blind, "boss": b.get("name") if b.get("boss") else None,
                        "jokers": [j.get("name") for j in obs.get("jokers") or [] if not j.get("debuff")]})
            first_of_blind = False
            if limit and len(out) >= limit:
                return out
    return out


def _work(args):
    job, module, samples = args
    from balatro_env.scripts.cli import estimate
    mod = importlib.import_module(module)
    try:
        r = mod.evaluate_action(job["obs"], job["kind"], job["cards"], estimate, samples=samples)
    except Exception as e:  # noqa: BLE001 - one odd observation must not stop the sweep
        return {"run": job["run"], "i": job["i"], "error": f"{type(e).__name__}: {e}"}
    return {k: job[k] for k in ("run", "i", "kind", "cleared", "first", "boss", "jokers")} | {"p": r["p_clear"]}


def table(rows, title):
    out = [f"### {title} ({len(rows)} decisions)", "", "| predicted | n | mean predicted | realized | diff | ok |",
           "|---|---|---|---|---|---|"]
    for lo, hi in BINS:
        b = [r for r in rows if lo <= r["p"] < hi]
        if not b:
            continue
        mp_ = statistics.mean(r["p"] for r in b)
        re_ = statistics.mean(1.0 if r["cleared"] else 0.0 for r in b)
        ok = "yes" if abs(mp_ - re_) < 0.05 else ("n<30" if len(b) < 30 else "NO")
        out.append(f"| {lo:.2f}-{min(hi, 1.0):.2f} | {len(b)} | {mp_:.3f} | {re_:.3f} | {re_ - mp_:+.3f} | {ok} |")
    if rows:
        brier = statistics.mean((r["p"] - (1.0 if r["cleared"] else 0.0)) ** 2 for r in rows)
        out += ["", f"Brier {brier:.4f}; mean predicted {statistics.mean(r['p'] for r in rows):.3f}, realized "
                    f"{statistics.mean(1.0 if r['cleared'] else 0.0 for r in rows):.3f}"]
    return "\n".join(out)


def report(rows, module):
    ok = [r for r in rows if "error" not in r]
    errs = [r for r in rows if "error" in r]
    parts = [f"# Solver calibration ({module}): p_clear of the player's action vs realized clear", "",
             f"Decisions {len(ok)}, errors {len(errs)}", "", table(ok, "All decisions"), "",
             table([r for r in ok if r["first"]], "First decision of each blind"), "",
             table([r for r in ok if r["boss"]], "Boss blinds")]
    worst = sorted((r for r in ok if not r["cleared"]), key=lambda r: -r["p"])[:15]
    parts += ["", "## Lost blinds with the highest predicted p", "", "| run step | action | p | boss | jokers |",
              "|---|---|---|---|---|"]
    parts += [f"| {r['run']}#{r['i']} | {r['kind']} | {r['p']:.2f} | {r['boss'] or ''} | {', '.join(r['jokers'])} |"
              for r in worst]
    if errs:
        parts += ["", "Errors:"] + [f"- {r['run']}#{r['i']}: {r['error']}" for r in errs[:10]]
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--module", default="balatro_env.solver")
    ap.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[3] / "data"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dump", default=None, help="write per-decision rows as JSON lines")
    a = ap.parse_args(argv)
    js = jobs(Path(a.data_dir), a.limit)
    print(f"{len(js)} decisions", file=sys.stderr)
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_work, [(j, a.module, a.samples) for j in js], chunksize=8)
    text = report(rows, a.module)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    if a.dump:
        Path(a.dump).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
