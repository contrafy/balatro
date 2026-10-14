"""Offline evaluation of balatro_env.solver against recorded Gold player PLAY/DISCARD decisions.

Rerun: `cd python && python -m balatro_env.analysis.solver_eval [--data-dir ../data] [--workers 6] [--samples 300]
[--budget 1.5] [--limit N] [--out FILE]`. Read-only over `<data>/trajectories/**` (player Gold runs, same filter as
gold_stats). For every SELECTING_HAND step whose action is PLAY_HAND or DISCARD:

- the solver ranks the decision from `obs` alone (its sampled draw orders never use `hidden`);
- the player's recorded action is scored on the same sampled orders (common random numbers), so
  gap = p_clear(solver top) - p_clear(player action) is the expected loss of the player's choice under the solver's
  model and continuation policy;
- realized outcomes (evaluation only): the solver's first action and the player's first action are each replayed on
  the TRUE recorded draw order (`hidden.draw_order`, `hidden.face_down`) followed by the solver's greedy policy, and
  compared with what actually happened to that blind (cleared or not).
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import statistics
import sys
from pathlib import Path
from typing import Any

from balatro_env import solver
from balatro_env.analysis.gold_stats import is_player_gold
from balatro_env.data.trajectory import dataset_files, read_trajectory
from balatro_env.scripts.cli import card_str, estimate

KIND = {"PLAY_HAND": solver.PLAY, "DISCARD": solver.DISCARD}
CLEARED_PHASES = {"ROUND_EVAL", "SHOP", "BLIND_SELECT", "PACK_OPENING"}


def blind_cleared(steps: list[dict], i: int, outcome: str) -> bool | None:
    """Whether the blind being played at step i was cleared: the next non-SELECTING_HAND step is a post-round phase;
    a run that ends inside the blind lost it; None when the file stops mid-blind without an end line."""
    for s in steps[i + 1:]:
        ph = (s.get("obs") or {}).get("phase")
        if ph != "SELECTING_HAND":
            return ph in CLEARED_PHASES
    return False if outcome == "loss" else None


def jobs(root: Path, limit: int | None):
    out = []
    for path in dataset_files(root):
        traj = read_trajectory(path)
        if not is_player_gold(traj):
            continue
        steps = traj.steps
        for i, s in enumerate(steps):
            obs = s.get("obs") or {}
            act = s.get("action") or {}
            if obs.get("phase") != "SELECTING_HAND" or act.get("type") not in KIND:
                continue
            out.append({"run": traj.key, "i": i, "obs": obs, "hidden": s.get("hidden") or {}, "action": act,
                        "why": (s.get("meta") or {}).get("why"), "cleared": blind_cleared(steps, i, traj.outcome)})
            if limit and len(out) >= limit:
                return out
    return out


def _positions(rs, indices):
    want = set(indices or [])
    return tuple(p for p, ix in enumerate(rs.slot_index) if ix in want)


def _true_order(rs, hidden):
    """Resolved hand and draw order from the recorded hidden state (evaluation only); None when inconsistent."""
    by_id = {c.id: c for c in rs.pool}
    hand = list(rs.slots)
    fd = {f.get("index"): f.get("id") for f in hidden.get("face_down") or [] if f.get("area") == "hand"}
    for p in rs.fd_pos:
        c = by_id.get(fd.get(rs.slot_index[p]))
        if c is None:
            return None
        hand[p] = c
    order = [by_id.get(i) for i in hidden.get("draw_order") or []]
    if not order or any(c is None for c in order):
        return None
    return hand, order


def evaluate_step(job: dict, samples: int, budget: float) -> dict[str, Any] | None:
    obs = job["obs"]
    try:
        rs = solver.RoundSolver(obs, estimate, seed=0)
        if rs.h0 <= 0 or not rs.slots:
            return None
        res = rs.evaluate(rs.candidates(), samples=samples, time_budget_s=budget)
        if not res:
            return None
        top = res[0]
        kind = KIND[job["action"]["type"]]
        ppos = _positions(rs, (job["action"].get("params") or {}).get("card_indices"))
        pl = rs.evaluate([{"kind": kind, "pos": ppos, "note": "player"}], samples=top["n"], time_budget_s=1e9)[0]
        tpos = _positions(rs, top["cards"])
        real = _true_order(rs, job["hidden"])
        top_real = pl_real = None
        if real:
            top_real = rs.run_with_order((top["action"], tpos), real[0], real[1])[0]
            pl_real = rs.run_with_order((kind, ppos), real[0], real[1])[0]
    except Exception as e:  # noqa: BLE001 - one odd observation must not stop the sweep
        return {"run": job["run"], "i": job["i"], "error": f"{type(e).__name__}: {e}"}
    b = obs.get("blind") or {}
    return {
        "run": job["run"], "i": job["i"], "blind": b.get("name"), "ante": obs.get("ante"),
        "need": (b.get("chips_needed") or 0) - (b.get("chips_scored") or 0), "h": rs.h0, "d": rs.d0,
        "hand": " ".join(f"{c.get('index')}:{card_str(c)}" for c in obs.get("hand") or []),
        "jokers": ", ".join(str(j.get("name")) for j in obs.get("jokers") or []),
        "player": (kind, sorted((job["action"].get("params") or {}).get("card_indices") or [])), "why": job["why"],
        "top": (top["action"], sorted(top["cards"])), "top_note": top["note"],
        "p_top": top["p_clear"], "p_player": pl["p_clear"], "n": top["n"],
        "cleared": job["cleared"], "top_real": top_real, "player_real": pl_real,
    }


def _work(args):
    return evaluate_step(*args)


def pct(a, b):
    return f"{100 * a / b:.0f}% ({a}/{b})" if b else "-"


def report(rows: list[dict]) -> str:
    ok = [r for r in rows if r and "error" not in r]
    errs = [r for r in rows if r and "error" in r]
    exact = sum(r["top"] == r["player"] for r in ok)
    same_kind = sum(r["top"][0] == r["player"][0] for r in ok)
    gaps = [r["p_top"] - r["p_player"] for r in ok]
    near = sum(g <= 0.02 for g in gaps)
    nontriv = [r for r in ok if not (r["p_top"] >= 0.999 and r["p_player"] >= 0.999) and r["p_top"] > 0.001]
    out = ["# Solver vs Gold players (balatro_env.analysis.solver_eval)", "",
           f"Decisions: {len(ok)} (errors {len(errs)}), runs {len({r['run'] for r in ok})}", "",
           "| metric | value |", "|---|---|",
           f"| exact same action | {pct(exact, len(ok))} |",
           f"| same action type (play/discard) | {pct(same_kind, len(ok))} |",
           f"| player within 0.02 p_clear of solver top | {pct(near, len(ok))} |",
           f"| non-trivial decisions (some option < 1, top > 0) | {len(nontriv)} |",
           f"| mean gap p(top) - p(player), all | {statistics.mean(gaps):.3f} |" if gaps else "| mean gap | - |",
           f"| mean gap, non-trivial | {statistics.mean([r['p_top'] - r['p_player'] for r in nontriv]):.3f} |" if nontriv else "| mean gap, non-trivial | - |",
           f"| gap >= 0.10 | {pct(sum(g >= 0.10 for g in gaps), len(ok))} |",
           f"| gap >= 0.25 | {pct(sum(g >= 0.25 for g in gaps), len(ok))} |",
           f"| gap < -0.05 (player beat the solver's top) | {pct(sum(g < -0.05 for g in gaps), len(ok))} |"]
    real = [r for r in ok if r["top_real"] is not None and r["cleared"] is not None]
    lost = [r for r in real if not r["cleared"]]
    won = [r for r in real if r["cleared"]]
    out += ["", "Realized on the true draw order (first action, then the solver's greedy policy):", "",
            "| blinds the player | steps | solver-first clears | player-first + policy clears |", "|---|---|---|---|",
            f"| lost | {len(lost)} | {pct(sum(r['top_real'] for r in lost), len(lost))} | {pct(sum(r['player_real'] for r in lost), len(lost))} |",
            f"| cleared | {len(won)} | {pct(sum(r['top_real'] for r in won), len(won))} | {pct(sum(r['player_real'] for r in won), len(won))} |"]
    lost_blinds = {}
    for r in lost:
        lost_blinds.setdefault((r["run"], r["ante"], r["blind"]), []).append(r)
    saved = sum(any(x["top_real"] for x in v) for v in lost_blinds.values())
    saved_pl = sum(any(x["player_real"] for x in v) for v in lost_blinds.values())
    out += ["", f"Lost blinds: {len(lost_blinds)}; a solver first action clears on the true order at one of its steps "
                f"in {pct(saved, len(lost_blinds))} (player's first action + solver policy: {pct(saved_pl, len(lost_blinds))}).", "",
            "## Largest gaps", "", "| run step | blind | need h/d | hand | player | p | solver | p | solver note | why |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(ok, key=lambda r: r["p_player"] - r["p_top"])[:20]:
        out.append(f"| {r['run']}#{r['i']} | a{r['ante']} {r['blind']} | {int(r['need'])} {r['h']}/{r['d']} | {r['hand']} | "
                   f"{r['player'][0]} {r['player'][1]} | {r['p_player']:.2f} | {r['top'][0]} {r['top'][1]} | {r['p_top']:.2f} | "
                   f"{r['top_note']} | {(r['why'] or '')[:120]} |")
    if errs:
        out += ["", "Errors:"] + [f"- {r['run']}#{r['i']}: {r['error']}" for r in errs[:10]]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[3] / "data"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--samples", type=int, default=300)
    ap.add_argument("--budget", type=float, default=1.5)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    js = jobs(Path(a.data_dir), a.limit)
    print(f"{len(js)} decisions", file=sys.stderr)
    args = [(j, a.samples, a.budget) for j in js]
    rows = []
    with mp.Pool(a.workers) as pool:
        for k, r in enumerate(pool.imap_unordered(_work, args, chunksize=4), 1):
            rows.append(r)
            if k % 100 == 0:
                print(f"  {k}/{len(js)}", file=sys.stderr)
    text = report(rows)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
