"""Empirical Gold-stake pools for shop_sim's Buffoon / Celestial pack options.

Rerun: `cd python && python -m balatro_env.analysis.pack_pool [--data-dir ../data] [--out balatro_env/pack_pool.json]`.
Read-only over `<data>/trajectories/**` (player Gold runs, gold_stats filter).

- jokers: every joker seen in a shop joker slot or a Buffoon pack (each physical item once: deduplicated by run and
  card id), grouped by (name, edition, eternal, perishable, rental) with its count. Shop and Buffoon jokers come from
  the same pool with the same Gold sticker rates, so together they estimate what a Buffoon pack offers.
- planets: Celestial pack contents by name with counts.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from balatro_env.analysis.gold_stats import is_player_gold
from balatro_env.data.trajectory import dataset_files, read_trajectory

KEEP = ("key", "name", "set", "rarity", "edition", "eternal", "perishable", "perish_tally", "rental", "sell_cost", "ability")


def build(root: Path) -> dict:
    seen = set()
    groups: dict[tuple, dict] = {}
    counts: Counter = Counter()
    planets: Counter = Counter()
    planet_seen = set()
    runs = 0
    for path in dataset_files(root):
        traj = read_trajectory(path)
        if not is_player_gold(traj):
            continue
        runs += 1
        for s in traj.steps:
            obs = s.get("obs") or {}
            items = []
            if obs.get("phase") == "SHOP":
                items = [c for c in (obs.get("shop") or {}).get("jokers") or [] if c.get("set") == "Joker"]
            elif obs.get("phase") == "PACK_OPENING":
                pk = obs.get("pack") or {}
                if pk.get("kind") == "Buffoon":
                    items = [c for c in pk.get("cards") or [] if c.get("set") == "Joker"]
                elif pk.get("kind") == "Celestial":
                    for c in pk.get("cards") or []:
                        k = (traj.key, c.get("id"))
                        if c.get("id") is not None and k not in planet_seen:
                            planet_seen.add(k)
                            planets[c.get("name")] += 1
            for c in items:
                k = (traj.key, c.get("id"))
                if c.get("id") is None or k in seen or c.get("facing") == "back":
                    continue
                seen.add(k)
                g = (c.get("name"), str(c.get("edition") or ""), bool(c.get("eternal")), bool(c.get("perishable")),
                     bool(c.get("rental")))
                counts[g] += 1
                groups.setdefault(g, {f: c.get(f) for f in KEEP})
    jokers = [dict(groups[g], count=n) for g, n in counts.most_common()]
    return {"runs": runs, "joker_items": sum(counts.values()), "planet_items": sum(planets.values()),
            "jokers": jokers, "planets": dict(planets.most_common())}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[3] / "data"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "pack_pool.json"))
    a = ap.parse_args(argv)
    pool = build(Path(a.data_dir))
    Path(a.out).write_text(json.dumps(pool, separators=(",", ":")), encoding="utf-8")
    print(f"{a.out}: {pool['runs']} runs, {pool['joker_items']} jokers in {len(pool['jokers'])} groups, "
          f"{pool['planet_items']} planets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
