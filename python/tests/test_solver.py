"""Round solver (balatro_env/solver.py) on hand-built SELECTING_HAND observations, scored with cli.py's estimate."""

import time

import pytest

from balatro_env import solver
from balatro_env.scripts.cli import estimate

RK = {"A": "Ace", "K": "King", "Q": "Queen", "J": "Jack", "T": "10"}
ST = {"S": "Spades", "H": "Hearts", "D": "Diamonds", "C": "Clubs"}
LEVELS = {"High Card": (5, 1), "Pair": (10, 2), "Two Pair": (20, 2), "Three of a Kind": (30, 3), "Straight": (30, 4),
          "Flush": (35, 4), "Full House": (40, 4), "Four of a Kind": (60, 7), "Straight Flush": (100, 8),
          "Five of a Kind": (120, 12), "Flush House": (140, 14), "Flush Five": (160, 16)}


def card(spec, **kw):
    c = {"rank": RK.get(spec[0], spec[0]), "suit": ST[spec[1]], "enhancement": None, "edition": None, "seal": None,
         "perma_bonus": 0}
    c.update(kw)
    return c


def state(hand, need, hands=3, discards=2, jokers=(), blind="Small Blind", boss=False, hand_size=8, **extra):
    """Full 52-card deck; every card not in hand is in the draw pile (remaining)."""
    deck, ids = [], {}
    for s in "SHDC":
        for r in "23456789TJQKA":
            ids[r + s] = len(deck) + 1
            deck.append(dict(card(r + s), id=ids[r + s], remaining=r + s not in hand))
    h = [dict(card(sp), id=ids[sp], index=i + 1, facing="front", debuff=False, highlighted=False, forced=False)
         for i, sp in enumerate(hand)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 1, "money": 4, "hands_remaining": hands,
         "discards_remaining": discards, "hand_size": hand_size, "highlight_limit": 5, "hand": h,
         "jokers": [{"name": n, "index": i + 1, "ability": {}} for i, n in enumerate(jokers)],
         "blind": {"name": blind, "boss": boss, "chips_needed": need, "chips_scored": 0, "disabled": False},
         "deck": {"cards": deck, "draw_pile": 52 - len(hand), "remaining": 52 - len(hand), "total": 52},
         "hand_levels": {k: {"level": 1, "chips": c, "mult": m, "played": 0, "played_this_round": 0, "visible": True}
                         for k, (c, m) in LEVELS.items()}}
    d.update(extra)
    return d


def idx(st, *specs):
    by = {(c["rank"], c["suit"]): c["index"] for c in st["hand"]}
    return sorted(by[(RK.get(s[0], s[0]), ST[s[1]])] for s in specs)


def plan(st, **kw):
    kw.setdefault("time_budget_s", 30.0)
    return solver.best_round_plan(st, estimate, **kw)


def find(res, action, cards):
    return next(r for r in res if r["action"] == action and sorted(r["cards"]) == sorted(cards))


def test_made_hand_that_clears_is_played_now():
    st = state(["AH", "KH", "9H", "6H", "3H", "QS", "7D", "2C"], need=280)
    res = plan(st)
    top = res[0]
    assert top["action"] == "PLAY" and set(idx(st, "AH", "KH", "9H", "6H", "3H")) <= set(top["cards"])
    assert top["p_clear"] == 1.0 and top["hands_left"] == 2.0 and top["discards_used"] == 0.0


def test_open_ended_straight_draw_beats_keeping_high_cards():
    # jokerless, final hand, 2 discards: only a straight/flush clears 250 (7805 BB loss: advise kept 3 high cards)
    st = state(["9S", "8H", "7D", "6C", "KD", "QH", "3S", "2C"], need=250, hands=1, discards=2)
    res = plan(st)
    top = res[0]
    assert top["action"] == "DISCARD"
    kept = set(c["index"] for c in st["hand"]) - set(top["cards"])
    assert set(idx(st, "9S", "8H", "7D", "6C")) <= kept, top
    high = solver.evaluate_action(st, "DISCARD", idx(st, "9S", "8H", "7D", "6C", "3S"), estimate)  # keep K Q 2
    assert top["p_clear"] >= high["p_clear"] + 0.3
    assert top["p_clear"] > 0.5


def test_four_flush_with_two_discards_beats_banking_two_pair():
    # 7805: advise played AAKK (124) with 2 discards instead of chasing the 4-heart flush. With 2 hands for 300 the
    # flush (two discards to hit it, then any second hand) beats banking 124 and needing 176 from one last hand.
    st = state(["AH", "KH", "8H", "4H", "AS", "KS", "6C", "2D"], need=300, hands=2, discards=2)
    res = plan(st)
    top = res[0]
    bank = solver.evaluate_action(st, "PLAY", idx(st, "AH", "AS", "KH", "KS"), estimate)
    assert not (top["action"] == "PLAY" and set(idx(st, "AH", "KH")) <= set(top["cards"]))
    assert top["p_clear"] > bank["p_clear"] + 0.05
    flush = solver.evaluate_action(st, "DISCARD", idx(st, "AS", "KS", "6C", "2D"), estimate)
    assert flush["p_clear"] > bank["p_clear"]


def test_jokerless_ante1_small_blind_pace():
    st = state(["5S", "5D", "KC", "JH", "9S", "7C", "4D", "2H"], need=300, hands=3, discards=2)
    t0 = time.perf_counter()
    fast = solver.best_round_plan(st, estimate)  # default 2 s budget (stage 1 always completes)
    assert time.perf_counter() - t0 < 6.0 and fast[0]["n"] >= 16  # 2 s budget + top-ups; slack for a loaded machine
    res = plan(st)
    top = res[0]
    assert top["n"] == 400 and 0.4 <= top["p_clear"] <= 1.0
    pair_alone = solver.evaluate_action(st, "PLAY", idx(st, "5S", "5D"), estimate)
    assert top["p_clear"] > pair_alone["p_clear"]
    assert all({"action", "cards", "p_clear", "exp_score", "note"} <= set(r) for r in res)
    full = [r["p_clear"] for r in res if r["n"] == 400]
    assert top["p_clear"] >= max(full) - solver.TIE_P


def test_tied_options_rank_by_dollars_then_growth():
    # every option clears 60 with certainty: play now (2 unused hands = $2) and, with Square Joker, the 4-card play
    st = state(["KS", "KH", "QS", "QD", "7C", "5D", "3H", "2C"], need=60, hands=3, discards=2, jokers=["Square Joker"])
    res = plan(st, samples=100)
    top = res[0]
    assert top["action"] == "PLAY" and top["p_clear"] == 1.0 and top["dollars"] == 2.0
    assert sorted(top["cards"]) == idx(st, "KS", "KH", "QS", "QD") and top["growth"] == 1.0
    five = solver.evaluate_action(st, "PLAY", idx(st, "KS", "KH", "QS", "QD", "2C"), estimate, samples=100)
    assert five["p_clear"] == 1.0 and five["value"] < top["value"]


def test_green_joker_loses_mult_per_discard():
    st = state(["KS", "KH", "9C", "7D", "5S", "4H", "3C", "2D"], need=300, hands=3, discards=2,
               jokers=["Green Joker"])
    st["jokers"][0]["ability"] = {"mult": 6}
    rs = solver.RoundSolver(st, estimate)
    kk = rs.slots[:2]
    now, _t = rs.score(kk, [], 3, 2, rs.ctx0)
    after_discard, _t = rs.score(kk, [], 3, 1, rs.ctx0)
    after_play, _t = rs.score(kk, [], 2, 2, rs.ctx0)
    assert after_discard < now < after_play


def test_no_discards_offers_dig_plays_and_keeps_the_pair():
    # 7804: with 0 discards a junk play is the only dig; throwing away the aces (that became trips) lost the blind
    st = state(["AS", "AD", "QH", "9C", "7S", "5D", "3H", "2C"], need=300, hands=3, discards=0)
    res = plan(st)
    digs = [r for r in res if r["note"].startswith("dig")]
    assert digs
    top = res[0]
    assert top["action"] == "PLAY"
    assert not set(idx(st, "AS", "AD")) <= set(top["cards"]) or top["p_clear"] >= max(r["p_clear"] for r in digs)


def test_hidden_draw_order_is_never_read():
    st = state(["9S", "8H", "7D", "6C", "KD", "QH", "3S", "2C"], need=250, hands=1, discards=2)
    a = plan(st, samples=60)
    st2 = dict(st, hidden={"draw_order": [c["id"] for c in st["deck"]["cards"]][::-1], "seed": "X"})
    b = plan(st2, samples=60)
    assert [(r["action"], r["cards"], r["p_clear"]) for r in a] == [(r["action"], r["cards"], r["p_clear"]) for r in b]


def test_psychic_plays_five_cards():
    st = state(["KS", "KD", "9H", "7C", "5D", "4S", "3H", "2C"], need=100, hands=2, discards=1, blind="The Psychic",
               boss=True)
    res = plan(st, samples=60)
    assert all(len(r["cards"]) == 5 for r in res if r["action"] == "PLAY")
    assert res[0]["action"] == "PLAY" or res[0]["p_clear"] > 0


def test_acrobat_holds_the_made_hand_for_the_final_hand():
    # flush 296 now, x3 = 888 as the final hand: burn a junk card first (E46A72GI held its straight for Acrobat)
    st = state(["AH", "KH", "9H", "6H", "3H", "QS", "7D", "2C"], need=600, hands=2, discards=0, jokers=["Acrobat"])
    res = plan(st, samples=100)
    top = res[0]
    assert top["action"] == "PLAY" and set(top["cards"]) <= set(idx(st, "QS", "7D", "2C"))
    assert any(r["note"].startswith("throwaway") and r["p_clear"] == 1.0 for r in res)
    assert top["p_clear"] == 1.0
    now = find(res, "PLAY", idx(st, "AH", "KH", "9H", "6H", "3H"))
    assert now["p_clear"] < 0.5


def test_classify_and_odds():
    rs = solver.RoundSolver(state(["AH", "2S", "3D", "4C", "5H", "KH", "KS", "KD"], need=1), estimate)
    hand = rs.slots
    assert rs.classify(hand[:5])[0] == "Straight"
    assert rs.classify(hand[5:8])[0] == "Three of a Kind"
    assert rs.classify(hand[5:7] + hand[0:1] + hand[4:5])[0] == "Pair"
    rs4 = solver.RoundSolver(state(["AH", "KH", "QH", "JH", "2S"], need=1, jokers=["Four Fingers"]), estimate)
    assert rs4.classify(rs4.slots)[0] == "Straight Flush"
    assert solver.p_none(44, 8, 4) == pytest.approx(58905 / 135751)  # OESD (8 outs) missed with 4 draws
    assert solver.p_atleast(44, 9, 4, 1) == pytest.approx(1 - 52360 / 135751)  # 4-flush hit with 4 draws
