"""Integrated validation: total basic-strategy EV for a rule set.

Published figures for reference (6 decks, 3:2, DAS, late surrender):
S17 ~ -0.26%, H17 ~ -0.46% (roughly +0.20% worse for H17).
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ev import (  # noqa: E402
    ACE,
    TEN,
    add_card,
    dealer_dist,
    ev_best,
    ev_split,
    fresh_comp,
    remove,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--h17", action="store_true")
    ap.add_argument("--no-das", action="store_true")
    ap.add_argument("--no-surrender", action="store_true")
    ap.add_argument("--decks", type=int, default=6)
    args = ap.parse_args()
    h17, das, sur = args.h17, not args.no_das, not args.no_surrender

    base = fresh_comp(args.decks)
    total_w = 0.0
    ev_sum = 0.0

    for up in range(10):
        for a, b in itertools.combinations_with_replacement(range(10), 2):
            # combinatorial weight of {player a,b} x {dealer up}
            c = list(base)
            w = float(c[up])
            c[up] -= 1
            if a == b:
                w *= c[a] * (c[a] - 1) / 2.0
            else:
                w *= c[a] * c[b]
            if w <= 0:
                continue
            comp = remove(tuple(c), a, b)
            total_w += w

            # dealer blackjack probability given the upcard
            n = sum(comp)
            if up == ACE:
                p_bj = comp[TEN] / n
            elif up == TEN:
                p_bj = comp[ACE] / n
            else:
                p_bj = 0.0

            t, s = add_card(0, False, a)
            t, s = add_card(t, s, b)
            player_bj = t == 21

            if player_bj:
                ev_sum += w * (p_bj * 0.0 + (1 - p_bj) * 1.5)
                continue

            dist = dealer_dist(up, comp, h17)
            best = ev_best(t, s, comp, dist, can_double=True)
            if a == b:
                best = max(best, ev_split(a, comp, dist, das))
            if sur:
                best = max(best, -0.5)
            ev_sum += w * (p_bj * -1.0 + (1 - p_bj) * best)

    print(f"{args.decks}D {'H17' if h17 else 'S17'} "
          f"{'DAS' if das else 'NoDAS'} {'LS' if sur else 'NoSur'}: "
          f"player EV = {ev_sum / total_w * 100:+.4f}%")


if __name__ == "__main__":
    main()
