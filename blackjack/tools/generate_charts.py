"""Generate basic-strategy charts from the EV engine.

Run it to regenerate (and eyeball) the tables hardcoded in
``bjtrainer/strategy.py``::

    python blackjack/tools/generate_charts.py --h17
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ev import (  # noqa: E402
    ACE,
    TEN,
    dealer_dist,
    ev_double,
    ev_hit,
    ev_split,
    ev_stand,
    fresh_comp,
    remove,
    slot_value,
)

UPCARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # slot indices 1..9 then ace handled below
UP_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, ACE]  # slots: 2..T, then ace
UP_LABEL = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "A"]


def combos_for_hard(total: int) -> list[tuple[int, int]]:
    """Unordered two-card slot pairs (no aces) summing to ``total``."""
    out = []
    for a, b in itertools.combinations_with_replacement(range(1, 10), 2):
        if slot_value(a) + slot_value(b) == total:
            out.append((a, b))
    return out


def weight(comp, a: int, b: int) -> float:
    if a == b:
        return comp[a] * (comp[a] - 1) / 2.0
    return float(comp[a] * comp[b])


def cell(decks: int, h17: bool, das: bool, cards: list[tuple[int, int]], up: int,
         is_pair: bool = False) -> dict[str, float]:
    """Frequency-weighted EVs over every two-card composition of a total."""
    acc: dict[str, float] = defaultdict(float)
    total_w = 0.0
    base = remove(fresh_comp(decks), up)
    for a, b in cards:
        w = weight(base, a, b)
        if w <= 0:
            continue
        comp = remove(base, a, b)
        dist = dealer_dist(up, comp, h17)
        t, s = 0, False
        from ev import add_card

        t, s = add_card(t, s, a)
        t, s = add_card(t, s, b)
        acc["stand"] += w * ev_stand(t, dist)
        acc["hit"] += w * ev_hit(t, s, comp, dist)
        acc["double"] += w * ev_double(t, s, comp, dist)
        if is_pair:
            acc["split_das"] += w * ev_split(a, comp, dist, das=True)
            acc["split_nodas"] += w * ev_split(a, comp, dist, das=False)
        total_w += w
    return {k: v / total_w for k, v in acc.items()}


def code_for(evs: dict[str, float], das: bool, surrender: bool,
             is_pair: bool) -> str:
    stand, hit, double = evs["stand"], evs["hit"], evs["double"]
    fallback = "S" if stand > hit else "H"
    best_no_split = max(stand, hit, double)

    split = (evs["split_das"] if das else evs["split_nodas"]) if is_pair else -9.0
    if is_pair and split > best_no_split and split > -0.5:
        # Does the split depend on being able to double afterwards?
        if evs["split_nodas"] <= best_no_split:
            return "Ph" if fallback == "H" else "Ps"
        return "P"

    if surrender and -0.5 > max(best_no_split, split):
        # Surrender wins; the suffix says what to do when it is not offered.
        if is_pair and split > best_no_split:
            return "Rp"
        return "R" + fallback.lower()
    if double >= best_no_split:
        return "D" if fallback == "H" else "Ds"
    return fallback


def render(title: str, rows: list[tuple[str, list[str]]]) -> str:
    out = [title, "        " + "  ".join(f"{u:>2}" for u in UP_LABEL)]
    for label, codes in rows:
        out.append(f"{label:>6}  " + "  ".join(f"{c:>2}" for c in codes))
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--h17", action="store_true", help="dealer hits soft 17")
    ap.add_argument("--no-das", action="store_true")
    ap.add_argument("--no-surrender", action="store_true")
    ap.add_argument("--decks", type=int, default=6)
    ap.add_argument("--margins", action="store_true", help="print EV margins per cell")
    args = ap.parse_args()
    h17, das, sur = args.h17, not args.no_das, not args.no_surrender

    hard_rows, soft_rows, pair_rows = [], [], []
    margins: list[str] = []

    for total in range(5, 21):
        codes = []
        for up in UP_ORDER:
            evs = cell(args.decks, h17, das, combos_for_hard(total), up)
            c = code_for(evs, das, sur, is_pair=False)
            codes.append(c)
            if args.margins:
                ranked = sorted(evs.items(), key=lambda kv: -kv[1])
                gap = ranked[0][1] - ranked[1][1]
                if gap < 0.02:
                    margins.append(
                        f"hard {total} v {UP_LABEL[UP_ORDER.index(up)]}: {c} "
                        + " ".join(f"{k}={v:+.4f}" for k, v in ranked[:3])
                    )
        hard_rows.append((str(total), codes))

    for x in range(2, 10):
        codes = []
        for up in UP_ORDER:
            evs = cell(args.decks, h17, das, [(ACE, x - 1)], up)
            c = code_for(evs, das, sur, is_pair=False)
            codes.append(c)
            if args.margins:
                ranked = sorted(evs.items(), key=lambda kv: -kv[1])
                gap = ranked[0][1] - ranked[1][1]
                if gap < 0.02:
                    margins.append(
                        f"A,{x} v {UP_LABEL[UP_ORDER.index(up)]}: {c} "
                        + " ".join(f"{k}={v:+.4f}" for k, v in ranked[:3])
                    )
        soft_rows.append((f"A,{x}", codes))

    for slot in [ACE] + list(range(1, 10)):
        label = "A,A" if slot == ACE else f"{slot_value(slot)},{slot_value(slot)}"
        if slot == TEN:
            label = "T,T"
        codes = []
        for up in UP_ORDER:
            evs = cell(args.decks, h17, das, [(slot, slot)], up, is_pair=True)
            c = code_for(evs, das, sur, is_pair=True)
            codes.append(c)
            if args.margins:
                ranked = sorted(evs.items(), key=lambda kv: -kv[1])
                gap = ranked[0][1] - ranked[1][1]
                if gap < 0.02:
                    margins.append(
                        f"{label} v {UP_LABEL[UP_ORDER.index(up)]}: {c} "
                        + " ".join(f"{k}={v:+.4f}" for k, v in ranked[:3])
                    )
        pair_rows.append((label, codes))

    tag = f"{args.decks}D {'H17' if h17 else 'S17'} {'DAS' if das else 'NoDAS'} {'LS' if sur else 'NoSur'}"
    print(render(f"HARD  [{tag}]", hard_rows))
    print()
    print(render(f"SOFT  [{tag}]", soft_rows))
    print()
    print(render(f"PAIRS [{tag}]", pair_rows))
    if margins:
        print("\nCLOSE CALLS (top-2 EV gap < 0.02):")
        for m in margins:
            print("  " + m)


if __name__ == "__main__":
    main()


def dump_python() -> str:
    """Emit the S17 and H17 tables as the literals used by bjtrainer.strategy."""
    out = []
    for h17 in (False, True):
        name = "H17" if h17 else "S17"
        hard, soft, pair = {}, {}, {}
        for total in range(5, 21):
            hard[total] = [code_for(cell(6, h17, True, combos_for_hard(total), up),
                                    True, True, False) for up in UP_ORDER]
        for x in range(2, 10):
            soft[x] = [code_for(cell(6, h17, True, [(ACE, x - 1)], up),
                                True, True, False) for up in UP_ORDER]
        for slot in [ACE] + list(range(1, 10)):
            key = "A" if slot == ACE else ("T" if slot == TEN else str(slot_value(slot)))
            pair[key] = [code_for(cell(6, h17, True, [(slot, slot)], up, is_pair=True),
                                  True, True, True) for up in UP_ORDER]
        for label, table in (("HARD", hard), ("SOFT", soft), ("PAIR", pair)):
            out.append(f"{label}_{name} = {{")
            for k, v in table.items():
                key = f'"{k}"' if isinstance(k, str) else k
                out.append(f"    {key}: {tuple(v)!r},")
            out.append("}\n")
    return "\n".join(out)
