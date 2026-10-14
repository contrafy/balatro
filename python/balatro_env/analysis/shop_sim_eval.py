"""Offline validation of balatro_env.shop_sim on recorded Gold shop and pack decisions.

Rerun: `cd python && python -m balatro_env.analysis.shop_sim_eval [--data-dir ../data] [--workers 6] [--budget 2.0]
[--limit N] [--out FILE]`. Read-only over `<data>/trajectories/**` (player Gold runs, gold_stats filter).

Decision points: SHOP steps whose action is SHOP_END (bought nothing more), SHOP_BUY / SHOP_BUY_AND_USE of a joker,
planet or playing card, and PACK_OPENING SELECT_PACK_CARD / SKIP_PACK. At each, `value_options` ranks the default
options from the observation alone; the player's choice is matched to an option by label.

- Calibration: at SHOP_END steps, the baseline p_next (survive the next 3 blinds with the board as it is) against
  whether the run actually got through the next 3 blinds (each cleared via CASH_OUT or skipped via SKIP_BLIND).
- Decisions: agreement (player's option tied with the simulator's top), regret = p(top) - p(player's option), and
  whether survival of the next 3 blinds differs between followed / not-followed decisions; correlation of the
  player's delta (vs baseline) and of regret with that survival.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import statistics
import sys
from pathlib import Path

from balatro_env import shop_sim
from balatro_env.analysis.gold_stats import is_player_gold
from balatro_env.data.trajectory import dataset_files, read_trajectory
from balatro_env.scripts.cli import estimate


def survived_next(steps: list[dict], i: int, outcome: str, n: int = 3) -> bool | None:
    """Whether the run resolved the next n blinds (CASH_OUT = cleared, SKIP_BLIND = skipped) after step i; False
    when it ended in a loss first; None when the file stops first without a loss."""
    k = 0
    for s in steps[i + 1:]:
        if (s.get("action") or {}).get("type") in ("CASH_OUT", "SKIP_BLIND"):
            k += 1
            if k >= n:
                return True
    if outcome == "win":
        return True
    return False if outcome == "loss" else None


def player_label(obs: dict, act: dict) -> str | None:
    t, p = act.get("type"), act.get("params") or {}
    if t == "SHOP_END":
        return "baseline (buy nothing)"
    if t == "SKIP_PACK":
        return "skip pack"
    if t in ("SHOP_BUY", "SHOP_BUY_AND_USE"):
        items = (obs.get("shop") or {}).get("jokers") or []
        k = p.get("slot")
        if isinstance(k, int) and 1 <= k <= len(items):
            c = items[k - 1]
            return f"buy {c.get('name') or c.get('key')}" + (f" ${int(c.get('cost') or 0)}" if c.get("cost") else "")
    if t == "SELECT_PACK_CARD":
        items = (obs.get("pack") or {}).get("cards") or []
        k = p.get("index")
        if isinstance(k, int) and 1 <= k <= len(items):
            return f"take {items[k - 1].get('name') or items[k - 1].get('key')}"
    return None


def jobs(root: Path, limit: int | None):
    out = []
    for path in dataset_files(root):
        traj = read_trajectory(path)
        if not is_player_gold(traj):
            continue
        steps = traj.steps
        for i, s in enumerate(steps):
            obs, act = s.get("obs") or {}, s.get("action") or {}
            if obs.get("phase") not in ("SHOP", "PACK_OPENING"):
                continue
            lab = player_label(obs, act)
            if lab is None:
                continue
            out.append({"run": traj.key, "i": i, "obs": obs, "label": lab, "action": act.get("type"),
                        "survived": survived_next(steps, i, traj.outcome)})
            if limit and len(out) >= limit:
                return out
    return out


def evaluate(job: dict, budget: float) -> dict:
    try:
        res = shop_sim.value_options(job["obs"], budget_s=budget, estimate_fn=estimate)
    except Exception as e:  # noqa: BLE001 - one odd observation must not stop the sweep
        return {"run": job["run"], "i": job["i"], "error": f"{type(e).__name__}: {e}"}
    ok = [r for r in res if r.get("p_next") is not None]
    if not ok:
        return {"run": job["run"], "i": job["i"], "skip": True}
    top = ok[0]
    pl = next((r for r in ok if r["label"] == job["label"] or r["label"].startswith(job["label"] + " (sell")), None)
    base = next((r for r in ok if r["label"] in ("baseline (buy nothing)", "skip pack")), None)
    o = job["obs"]
    return {"run": job["run"], "i": job["i"], "phase": o.get("phase"), "ante": o.get("ante"), "money": o.get("money"),
            "action": job["action"], "label": job["label"], "survived": job["survived"], "n_opts": len(ok),
            "top": top["label"], "p_top": top["p_next"], "p_player": pl["p_next"] if pl else None,
            "p_base": base["p_next"] if base else None, "blinds": top["blinds"],
            "jokers": ", ".join(str(j.get("name")) for j in o.get("jokers") or []),
            "options": [(r["label"], round(r["p_next"], 3)) for r in ok]}


def _work(args):
    return evaluate(*args)


def pct(a, b):
    return f"{100 * a / b:.0f}% ({a}/{b})" if b else "-"


def corr(xs, ys):
    """Pearson correlation (point-biserial when ys is 0/1)."""
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx and sy else float("nan")


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return float("nan")
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def report(rows: list[dict]) -> str:
    ok = [r for r in rows if r and "error" not in r and not r.get("skip")]
    errs = [r for r in rows if r and "error" in r]
    out = ["# Shop simulator vs Gold players (balatro_env.analysis.shop_sim_eval)", "",
           f"Decision points: {len(ok)} (errors {len(errs)}), runs {len({r['run'] for r in ok})}", ""]
    cal = [r for r in ok if r["action"] == "SHOP_END" and r["p_base"] is not None and r["survived"] is not None]
    if cal:
        ps = [r["p_base"] for r in cal]
        ys = [1 if r["survived"] else 0 for r in cal]
        brier = statistics.mean((p - y) ** 2 for p, y in zip(ps, ys))
        clim = statistics.mean(ys)
        out += ["## Calibration: baseline p(survive next 3 blinds) at SHOP_END vs actual", "",
                f"{len(cal)} shops; actual survival {clim:.2f}, mean predicted {statistics.mean(ps):.2f}; Brier {brier:.3f} "
                f"(climatology {statistics.mean((clim - y) ** 2 for y in ys):.3f}); AUC {auc(ps, ys):.2f}", "",
                "| predicted | shops | mean predicted | actual |", "|---|---|---|---|"]
        for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, .95), (.95, 1.01)):
            b = [(p, y) for p, y in zip(ps, ys) if lo <= p < hi]
            if b:
                out.append(f"| {lo:.2f}-{min(hi, 1):.2f} | {len(b)} | {statistics.mean(p for p, _ in b):.2f} | "
                           f"{statistics.mean(y for _, y in b):.2f} |")
    dec = [r for r in ok if r["n_opts"] >= 2 and r["p_player"] is not None]
    if dec:
        followed = [r for r in dec if r["p_player"] >= r["p_top"] - shop_sim.TIE_P]
        notf = [r for r in dec if r not in followed]
        regrets = [r["p_top"] - r["p_player"] for r in dec]
        surv = [r for r in dec if r["survived"] is not None]
        fs = [r for r in followed if r["survived"] is not None]
        ns = [r for r in notf if r["survived"] is not None]
        out += ["", "## Decisions (2+ feasible options, player's choice simulated)", "",
                "| metric | value |", "|---|---|",
                f"| decisions | {len(dec)} |",
                f"| player choice tied with sim top (within {shop_sim.TIE_P}) | {pct(len(followed), len(dec))} |",
                f"| mean regret p(top) - p(player) | {statistics.mean(regrets):.3f} |",
                f"| regret >= 0.10 | {pct(sum(g >= 0.10 for g in regrets), len(dec))} |",
                f"| survived next 3 blinds, followed sim | {pct(sum(r['survived'] for r in fs), len(fs))} |",
                f"| survived next 3 blinds, did not follow | {pct(sum(r['survived'] for r in ns), len(ns))} |"]
        d = [r for r in surv if r["p_base"] is not None]
        if d:
            ys = [1 if r["survived"] else 0 for r in d]
            out += [f"| corr(player delta vs baseline, survived) | {corr([r['p_player'] - r['p_base'] for r in d], ys):.3f} |",
                    f"| corr(regret, survived) | {corr([r['p_top'] - r['p_player'] for r in d], ys):.3f} |",
                    f"| corr(p(player's option), survived) | {corr([r['p_player'] for r in d], ys):.3f} |"]
        out += ["", "## Largest regrets", "", "| run step | ante $ | jokers | player | p | sim top | p | blinds | survived |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(dec, key=lambda r: r["p_player"] - r["p_top"])[:20]:
            out.append(f"| {r['run']}#{r['i']} | a{r['ante']} ${r['money']} | {r['jokers']} | {r['label']} | "
                       f"{r['p_player']:.2f} | {r['top']} | {r['p_top']:.2f} | {'; '.join(r['blinds'])} | {r['survived']} |")
    if errs:
        out += ["", "Errors:"] + [f"- {r['run']}#{r['i']}: {r['error']}" for r in errs[:10]]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[3] / "data"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--budget", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    js = jobs(Path(a.data_dir), a.limit)
    print(f"{len(js)} decision points", file=sys.stderr)
    rows = []
    with mp.Pool(a.workers) as pool:
        for k, r in enumerate(pool.imap_unordered(_work, [(j, a.budget) for j in js], chunksize=2), 1):
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
