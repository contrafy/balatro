"""The shipped charts must still be what the EV engine derives.

This re-runs the generator in tools/ and compares cell by cell, so a hand-edit
to strategy.py that drifts from the maths fails loudly.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from bjtrainer import strategy  # noqa: E402

generate_charts = pytest.importorskip("generate_charts")


@pytest.mark.parametrize("h17", [False, True])
def test_tables_match_the_generator(h17):
    name = "H17" if h17 else "S17"
    hard = getattr(strategy, f"HARD_{name}")
    soft = getattr(strategy, f"SOFT_{name}")
    pair = getattr(strategy, f"PAIR_{name}")

    for total, shipped in hard.items():
        evs = [generate_charts.cell(6, h17, True,
                                    generate_charts.combos_for_hard(total), up)
               for up in generate_charts.UP_ORDER]
        derived = tuple(generate_charts.code_for(e, True, True, False) for e in evs)
        assert derived == shipped, f"hard {total} ({name})"

    for kicker, shipped in soft.items():
        evs = [generate_charts.cell(6, h17, True, [(generate_charts.ACE, kicker - 1)], up)
               for up in generate_charts.UP_ORDER]
        derived = tuple(generate_charts.code_for(e, True, True, False) for e in evs)
        assert derived == shipped, f"soft A,{kicker} ({name})"

    def slot_of(rank: str) -> int:
        if rank == "A":
            return generate_charts.ACE
        if rank == "T":
            return generate_charts.TEN
        return int(rank) - 1

    for rank, shipped in pair.items():
        slot = slot_of(rank)
        evs = [generate_charts.cell(6, h17, True, [(slot, slot)], up, is_pair=True)
               for up in generate_charts.UP_ORDER]
        derived = tuple(generate_charts.code_for(e, True, True, True) for e in evs)
        assert derived == shipped, f"pair {rank},{rank} ({name})"


def test_dealer_probabilities_match_the_published_table():
    """Dealer bust rates by upcard, 6 decks, S17, blackjacks included."""
    from ev import ACE, dealer_dist, fresh_comp, remove

    expected = {"2": .354, "3": .374, "4": .396, "5": .418, "6": .423,
                "7": .262, "8": .244, "9": .229, "T": .212, "A": .116}
    slots = {"2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6, "8": 7, "9": 8,
             "T": 9, "A": ACE}
    for label, slot in slots.items():
        dist = dealer_dist(slot, remove(fresh_comp(6), slot), h17=False, peek=False)
        assert dist[5] == pytest.approx(expected[label], abs=0.002), label


def test_house_edge_lands_where_the_books_put_it():
    """Basic strategy's cost, and what each rule is worth, from the engine."""
    import subprocess

    def edge(*args):
        out = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "house_edge.py"), *args],
            capture_output=True, text=True, check=True,
        ).stdout
        return float(out.rsplit("=", 1)[1].strip().rstrip("%"))

    s17 = edge()
    h17 = edge("--h17")
    no_das = edge("--no-das")
    no_sur = edge("--no-surrender")

    assert -0.45 < s17 < -0.20, f"6D S17 DAS LS came out at {s17:+.3f}%"
    assert 0.15 < s17 - h17 < 0.25, "H17 should cost about 0.20%"
    assert 0.10 < s17 - no_das < 0.18, "DAS should be worth about 0.14%"
    assert 0.04 < s17 - no_sur < 0.12, "late surrender should be worth about 0.08%"
