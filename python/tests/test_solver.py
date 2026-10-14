"""Round solver (balatro_env/solver.py) on hand-built SELECTING_HAND observations, scored with cli.py's estimate."""

import itertools
import math
import random
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
    assert top["p_model"] == 1.0 and top["hands_left"] == 2.0 and top["discards_used"] == 0.0
    assert top["p_clear"] == pytest.approx(solver.calibrate(1.0)) and top["p_clear"] > 0.99


def test_open_ended_straight_draw_beats_keeping_high_cards():
    # jokerless, final hand, 2 discards: only a straight/flush clears 250 (7805 BB loss: advise kept 3 high cards)
    st = state(["9S", "8H", "7D", "6C", "KD", "QH", "3S", "2C"], need=250, hands=1, discards=2)
    res = plan(st)
    top = res[0]
    assert top["action"] == "DISCARD"
    kept = set(c["index"] for c in st["hand"]) - set(top["cards"])
    assert set(idx(st, "9S", "8H", "7D", "6C")) <= kept, top
    high = solver.evaluate_action(st, "DISCARD", idx(st, "9S", "8H", "7D", "6C", "3S"), estimate)  # keep K Q 2
    assert top["p_model"] >= high["p_model"] + 0.3
    assert top["p_model"] > 0.5


def test_four_flush_with_two_discards_beats_banking_two_pair():
    # 7805: advise played AAKK (124) with 2 discards instead of chasing the 4-heart flush. With 2 hands for 300 the
    # flush (two discards to hit it, then any second hand) beats banking 124 and needing 176 from one last hand.
    st = state(["AH", "KH", "8H", "4H", "AS", "KS", "6C", "2D"], need=300, hands=2, discards=2)
    res = plan(st)
    top = res[0]
    bank = solver.evaluate_action(st, "PLAY", idx(st, "AH", "AS", "KH", "KS"), estimate)
    assert not (top["action"] == "PLAY" and set(idx(st, "AH", "KH")) <= set(top["cards"]))
    assert top["p_model"] > bank["p_model"] + 0.05
    flush = solver.evaluate_action(st, "DISCARD", idx(st, "AS", "KS", "6C", "2D"), estimate)
    assert flush["p_model"] > bank["p_model"]


def test_jokerless_ante1_small_blind_pace():
    st = state(["5S", "5D", "KC", "JH", "9S", "7C", "4D", "2H"], need=300, hands=3, discards=2)
    t0 = time.perf_counter()
    fast = solver.best_round_plan(st, estimate)  # default 2 s budget (stage 1 always completes)
    assert time.perf_counter() - t0 < 6.0 and fast[0]["n"] >= 16  # 2 s budget + top-ups; slack for a loaded machine
    res = plan(st)
    top = res[0]
    assert top["n"] == 400 and 0.4 <= top["p_model"] <= 1.0
    pair_alone = solver.evaluate_action(st, "PLAY", idx(st, "5S", "5D"), estimate)
    assert top["p_model"] > pair_alone["p_model"]
    assert all({"action", "cards", "p_clear", "p_model", "exp_score", "note"} <= set(r) for r in res)
    full = [r["p_model"] for r in res if r["n"] == 400]
    assert top["p_model"] >= max(full) - solver.TIE_P


def test_tied_options_rank_by_dollars_then_growth():
    # every option clears 60 with certainty: play now (2 unused hands = $2) and, with Square Joker, the 4-card play
    st = state(["KS", "KH", "QS", "QD", "7C", "5D", "3H", "2C"], need=60, hands=3, discards=2, jokers=["Square Joker"])
    res = plan(st, samples=100)
    top = res[0]
    assert top["action"] == "PLAY" and top["p_model"] == 1.0 and top["dollars"] == 2.0
    assert sorted(top["cards"]) == idx(st, "KS", "KH", "QS", "QD") and top["growth"] == 1.0
    five = solver.evaluate_action(st, "PLAY", idx(st, "KS", "KH", "QS", "QD", "2C"), estimate, samples=100)
    assert five["p_model"] == 1.0 and five["value"] < top["value"]


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
    assert not set(idx(st, "AS", "AD")) <= set(top["cards"]) or top["p_model"] >= max(r["p_model"] for r in digs)


def test_misprint_is_sampled_per_hand():
    # final hand Pair KK = 30 chips x (2 + Misprint 0..23): 300 needs a roll >= 8, i.e. 16/24 (est's fixed +6 says 0)
    st = state(["KS", "KH", "9C", "7D", "5S", "4H", "2C", "JD"], need=300, hands=1, discards=0, jokers=["Misprint"])
    st["jokers"][0]["ability"] = {"extra": {"min": 0, "max": 23}}
    top = plan(st)[0]
    assert 0.55 < top["p_model"] < 0.8


def test_a_certain_clear_with_cards_in_hand_beats_tied_discard_lines():
    # 7805 R87RLKF6 (The Wall): Pair 66 now + held Pair 22 next clears for sure; discards also read p 1.00 (sampled)
    st = state(["KS", "KD", "QS", "QD", "9C", "7H", "4C", "2D"], need=110, hands=2, discards=2)
    res = plan(st, samples=100)
    top = res[0]
    assert top["action"] == "PLAY" and top["certain"] and "certain" in top["note"]
    assert not any(r["certain"] for r in res if r["action"] == "DISCARD")
    # 7807 E1PM6PSH: with Blackboard the next hand also holds the cards drawn now (a red one breaks x3): Pair KK now
    # + Pair QQ next is certain without it, not with it
    hand = ["KS", "KC", "QS", "QC", "9C", "7S", "4C", "2D"]
    for jokers, want in (((), True), (("Blackboard",), False)):
        rs = solver.RoundSolver(state(hand, need=110, hands=2, discards=2, jokers=jokers), estimate)
        assert rs._certain({"kind": solver.PLAY, "pos": (0, 1)}) is want


def test_blackboard_plays_red_cards_away_as_fillers():
    # 7805 16N52CRZ (The Hook): Blackboard x3 needs every held card black; play the reds as fillers
    st = state(["KS", "KC", "9S", "7C", "5S", "4H", "3D", "2C"], need=200, hands=3, discards=0, jokers=["Blackboard"])
    rs = solver.RoundSolver(st, estimate)
    s, play, t = rs.best_play(rs.slots, 3, 0, rs.ctx0)
    labels = {c.label() for c in play}
    assert t == "Pair" and {"KS", "KC", "4H", "3D"} <= labels
    held = [c for c in rs.slots if c not in play]
    assert all(rs._black(c) for c in held)
    assert s > 2 * rs.score(rs.slots[:2], rs.slots[2:], 3, 0, rs.ctx0)[0]  # x3 vs the pair with reds held


def test_bloodstone_is_a_card_phase_x1_5_per_heart():
    # 7804 Z9WILFCR: x1.5 multiplied the whole score, inflating a dig from ~3% to 0.29; it applies to the mult in each
    # Heart's card phase, before the jokers' +mult
    st = state(["KH", "KS", "9C", "7D", "5S", "4C", "3C", "2D"], need=300, hands=3, discards=2,
               jokers=["Joker", "Bloodstone"])
    st["jokers"][0]["ability"] = {"mult": 4}
    rs = solver.RoundSolver(st, estimate)
    kk = rs.slots[:2]
    plain = estimate("Pair", [c.d for c in kk], [], st, played_n=2)[0]  # (10+20) x (2+4) = 180, Bloodstone left out
    got = {rs.score(kk, [], 3, 2, rs.ctx0, random.Random(s))[0] for s in range(40)}
    assert got == {plain, 30 * (2 * 1.5 + 4)}  # 210, not 270
    assert rs.score(kk, [], 3, 2, rs.ctx0)[0] == pytest.approx((180 + 210) / 2)


def test_hanging_chad_retriggers_the_best_card_the_player_can_move_first():
    # 7810 YSPYCXK1: Chad retriggers the first scoring card; `move hand` lets the player put the Glass King first
    st = state(["KS", "KD", "9C", "7D", "5S", "4H", "3C", "2D"], need=500, hands=3, discards=2,
               jokers=["Hanging Chad"])
    st["hand"][1]["enhancement"] = "m_glass"
    rs = solver.RoundSolver(st, estimate)
    kk = rs.slots[:2]
    in_hand_order = estimate("Pair", [c.d for c in kk], [], st, played_n=2)[0]
    best, _t = rs.score(kk, [], 3, 2, rs.ctx0)
    assert best > in_hand_order  # glass x2 three times instead of once
    assert rs.best_first(kk) == 2
    top = next(r for r in plan(st, samples=40) if r["action"] == "PLAY" and sorted(r["cards"]) == [1, 2])
    assert top["first_card"] == 2 and "move KD leftmost" in top["note"]


def test_photograph_doubles_the_mult_added_before_the_first_face():
    # 7805 ZFGUEC54: Photograph x2 fires on the first scoring face; per-card +mult (Lusty, Mult cards) placed before it
    # is doubled, so the faces go after them (not leftmost)
    st = state(["KS", "KC", "5H", "5D", "9C", "7D", "3C", "2D"], need=900, hands=3, discards=2,
               jokers=["Photograph", "Lusty Joker"])
    st["hand"][3]["enhancement"] = "m_mult"
    rs = solver.RoundSolver(st, estimate)
    tp = rs.slots[:4]
    in_hand_order = estimate("Two Pair", [c.d for c in tp], [], st, played_n=4)[0]
    best, _t = rs.score(tp, [], 3, 2, rs.ctx0)
    assert best > in_hand_order
    first, order = rs.best_order(tp)
    assert first is None and set(order[:2]) == {3, 4} and set(order[2:]) == {1, 2}
    top = next(r for r in plan(st, samples=40) if r["action"] == "PLAY" and sorted(r["cards"]) == [1, 2, 3, 4])
    assert top["first_card"] is None and "scoring order left to right" in top["note"]


def test_round_score_quantiles_from_a_shop_state():
    # GoldAdvisor SCORE CHECK: a round played from the full deck with discards; Card Sharp's last-round flag is cleared
    st = state(["KS"], need=300, hands=3, discards=2, jokers=["Card Sharp"])
    st.update(phase="SHOP", hand=[], hands_per_round=4, discards_per_round=2)
    for v in st["hand_levels"].values():
        v["played_this_round"] = 1
    q = solver.round_score_quantiles(st, estimate, n=20)
    assert q["n"] == 20 and q["round"][0] <= q["round"][1] <= q["round"][2]
    assert q["per_hand"][1] * 4 == pytest.approx(q["round"][1], rel=0.5)
    one = solver.round_score_quantiles(st, estimate, n=20, hands=1, discards=0)
    assert one["round"][1] < q["round"][1]


def test_face_down_draws_cannot_be_seen_by_the_policy():
    # 7806 1VG6CJBW (The Fish): later draws come face down, the policy may not pick plays by their identity
    hand = ["KS", "KH", "9C", "7D", "5S", "4H", "3C", "2D"]
    plain = plan(state(hand, need=330, hands=3, discards=0, blind="Small Blind"), samples=300)[0]
    for boss in ("The Fish", "The Mark"):
        fish = plan(state(hand, need=330, hands=3, discards=0, blind=boss, boss=True), samples=300)[0]
        assert fish["low_confidence"] and fish["p_model"] < plain["p_model"]


def test_hit_the_road_discarding_jacks_raises_later_hands():
    # 7805 65YFNPGW: Hit the Road (+x0.5 per Jack discarded this round) was ignored, the round read UNWINNABLE
    hand = ["JS", "JH", "JC", "KS", "KD", "9C", "5H", "2D"]
    st = state(hand, need=500, hands=2, discards=1, jokers=["Hit the Road"])
    st["jokers"][0]["ability"] = {"x_mult": 1, "extra": 0.5}
    rs = solver.RoundSolver(st, estimate)
    hr = next(j for j in rs._state(2, 0, None, 3)["jokers"] if j["name"] == "Hit the Road")
    assert hr["ability"]["x_mult"] == pytest.approx(2.5)
    top = plan(st, samples=200)[0]
    assert top["action"] == "DISCARD" and {1, 2, 3} <= set(top["cards"])
    plain = plan(state(hand, need=500, hands=2, discards=1), samples=200)[0]
    assert plain["action"] == "PLAY" and top["p_model"] > plain["p_model"] + 0.1  # FH 360 now vs x2.5 later


def test_tied_options_prefer_getting_rid_of_debuffed_cards():
    # 7810 YY2DXIBD (The Head): debuffed hearts score nothing; among tied lines discard them
    st = state(["KS", "9C", "8H", "7H", "7C", "6C", "4H", "2S"], need=2000, hands=3, discards=2, blind="The Head",
               boss=True)
    for c in st["hand"]:
        c["debuff"] = c["suit"] == "Hearts"
    res = plan(st, samples=100)
    assert all(r["debuffed_left"] == sum(1 for c in st["hand"] if c["debuff"] and c["index"] not in r["cards"])
               for r in res)
    top_p = max(r["p_model"] for r in res if r["n"] >= res[0]["n"])
    tied = [r for r in res if r["p_model"] >= top_p - solver.TIE_P and r["n"] >= res[0]["n"]]
    assert res[0]["debuffed_left"] == min(r["debuffed_left"] for r in tied) or res[0]["certain"]


def test_acrobat_x3_only_on_final_hand_and_forced_dig_is_reported_raw():
    # 7804 I9HDGAQA: 2 hands, 0 discards, 4 clubs kept by a dig; the 5th club is a plain hypergeometric draw
    st = state(["AC", "7C", "6C", "2C", "TS", "8D", "6H", "5H"], need=2000, hands=2, discards=0,
               jokers=["Gluttonous Joker", "Acrobat"])
    rs = solver.RoundSolver(st, estimate)
    clubs = rs.slots[:4] + [next(c for c in rs.pool if c.suit == "C")]
    s_final, t = rs.score(clubs, [], 1, 0, rs.ctx0)
    s_now, _t = rs.score(clubs, [], 2, 0, rs.ctx0)
    assert t == "Flush" and s_final == pytest.approx(3 * s_now, rel=0.01) and s_final > 2000 > s_now
    r = solver.evaluate_action(st, "PLAY", idx(st, "TS", "8D", "6H", "5H"), estimate, samples=400)
    exact = 1 - math.comb(44 - 9, 4) / math.comb(44, 4)  # 9 clubs left in 44 cards, 4 drawn
    assert abs(r["p_model"] - exact) < 0.06 and r["p_clear"] == r["p_model"]


def test_obelisk_resets_inside_the_round():
    # 7802 YZMAQVI2: Pair was strictly the most played type; playing it resets Obelisk to x1 for the later hands
    st = state(["6S", "6D", "KC", "9H", "7S", "5D", "3H", "2C"], need=2000, hands=3, discards=0, jokers=["Obelisk"])
    st["jokers"][0]["ability"] = {"x_mult": 4.2, "extra": 0.2}
    st["hand_levels"]["Pair"]["played"] = 10
    st["hand_levels"]["High Card"]["played"] = 3
    rs = solver.RoundSolver(st, estimate)
    ob = rs.ctx0[3]
    after_pair = rs._obelisk_after(ob, "Pair")
    after_high = rs._obelisk_after(ob, "High Card")
    assert after_pair[0] == 1.0 and after_high[0] == pytest.approx(4.4)
    kk = [rs.slots[2]]
    s_before, _t = rs.score(kk, [], 3, 0, rs.ctx0)
    s_after, _t = rs.score(kk, [], 2, 0, rs.ctx0[:3] + (after_pair, 0))
    assert s_after < s_before / 3


def test_banner_plays_on_pace_instead_of_discarding():
    st = state(["KS", "KH", "QS", "QD", "7C", "5D", "3H", "2C"], need=700, hands=3, discards=2, jokers=["Banner"])
    rs = solver.RoundSolver(st, estimate)
    kind, sel = rs.policy(rs.slots, rs.pool, 3, 2, 700, rs.ctx0)
    assert kind == "PLAY" and {c.label() for c in sel} >= {"KS", "KH", "QS", "QD"}


def test_psychic_half_joker_never_counts_on_short_plays():
    st = state(["KS", "KD", "9H", "7C", "5D", "4S", "3H", "2C"], need=600, hands=3, discards=2, blind="The Psychic",
               boss=True, jokers=["Half Joker"])
    rs = solver.RoundSolver(st, estimate)
    plain = solver.RoundSolver(dict(st, jokers=[]), estimate)
    kk = rs.slots[:2]
    assert rs.score(kk, [], 3, 2, rs.ctx0)[0] == plain.score(kk, [], 3, 2, plain.ctx0)[0]


def _small_deck(st, keep_ids):
    """Only the listed deck card ids stay in the draw pile."""
    for c in st["deck"]["cards"]:
        c["remaining"] = c["remaining"] and c["id"] in keep_ids
    st["deck"]["draw_pile"] = sum(c["remaining"] for c in st["deck"]["cards"])
    return st


def _exact_last_discard(st, discard_idx):
    """Exact P(clear) of a last-hand discard: every draw of the discarded count from the pile, then the best play over
    all 1-5 card subsets of the new hand (with the solver's own scoring of a play)."""
    rs = solver.RoundSolver(st, estimate)
    keep = [c for c, ix in zip(rs.slots, rs.slot_index) if ix not in discard_idx]
    pile = rs.pool[:rs.pile_n]
    hits = tot = 0
    for drawn in itertools.combinations(pile, len(discard_idx)):
        hand = keep + list(drawn)
        best = 0.0
        for k in range(1, 6):
            for play in itertools.combinations(hand, k):
                s, _t = rs.score(list(play), [c for c in hand if c not in play], 1, 0, rs.ctx0)
                best = max(best, s)
        hits += best >= rs.need0
        tot += 1
    return hits / tot


@pytest.mark.parametrize("need,discard", [(400, ("9C", "6D", "2S")), (330, ("QH", "QD", "2S")), (700, ("JS", "9C", "6D"))])
def test_last_hand_discard_matches_exhaustive_enumeration(need, discard):
    # 7803 JEMI6XIF / 7804 GWCJ5DMP: last-hand discard p must be the exact chance that the best final hand clears;
    # the multi-hand calibration map must not inflate it (no later decision is left to outplay the policy)
    hand = ["QH", "QD", "JS", "9C", "7S", "7D", "6D", "2S"]
    st = state(hand, need=need, hands=1, discards=1, jokers=["Joker"])
    st["jokers"][0]["ability"] = {"mult": 4}
    ids = {c["id"] for c in st["deck"]["cards"] if c["rank"] in ("Queen", "7", "Jack", "3") and c["suit"] != "Spades"}
    st = _small_deck(st, ids | {c["id"] for c in st["deck"]["cards"] if c["rank"] == "4"})
    exact = _exact_last_discard(st, idx(st, *discard))
    r = solver.evaluate_action(st, "DISCARD", idx(st, *discard), estimate, samples=400)
    assert abs(r["p_model"] - exact) < 0.07, (r["p_model"], exact)
    assert r["p_clear"] == r["p_model"]


def test_filler_play_is_labelled_by_what_the_game_reads():
    # 7804: a dig KC TH 7H 7C was labelled "High Card KC est 15" although it plays Pair 77
    st = state(["KC", "TH", "7H", "7C", "AS", "AD", "QS", "QD"], need=5000, hands=3, discards=0, jokers=["Joker"])
    st["jokers"][0]["ability"] = {"mult": 4}
    for r in plan(st, samples=30):
        if r["action"] == "PLAY" and r["hand"] and not r["note"].startswith(("dig", "throwaway")):
            assert r["note"].startswith(r["hand"]), r


def test_mr_bones_is_a_tie_break_not_a_clear():
    # 7804: with Mr. Bones every option read >= 0.99 and the solver could not rank; real clears come first
    st = state(["AS", "AD", "QH", "9C", "7S", "5D", "3H", "2C"], need=700, hands=3, discards=2)
    bones = dict(st, jokers=[{"name": "Mr. Bones", "index": 1, "ability": {}}])
    a = solver.evaluate_action(st, "DISCARD", idx(st, "QH", "9C", "7S", "5D", "3H"), estimate, samples=200)
    b = solver.evaluate_action(bones, "DISCARD", idx(st, "QH", "9C", "7S", "5D", "3H"), estimate, samples=200)
    assert b["p_model"] == a["p_model"] < 0.9 and b["p_survive"] > b["p_model"]
    res = plan(bones, samples=100)
    tops = [r["p_model"] for r in res if r["n"] == res[0]["n"]]
    assert res[0]["p_model"] >= max(tops) - solver.TIE_P


def test_options_near_the_top_never_rest_on_16_samples():
    # 7810: an n=16 discard printed p=0.63; at n=100 it was 0.23
    st = state(["AS", "KD", "QH", "7C", "7D", "4S", "3H", "2C"], need=900, hands=3, discards=2, jokers=["Joker"])
    st["jokers"][0]["ability"] = {"mult": 4}
    res = plan(st, time_budget_s=0.01)
    best = max(r["p_model"] for r in res)
    assert res[0]["n"] >= solver.MIN_N
    assert all(r["n"] >= solver.MIN_N or r["low_n"] for r in res if r["p_model"] >= best - 0.3)
    assert any(r["n"] >= solver.MIN_N for r in res[1:4])


def test_psychic_pads_to_five_and_half_joker_gets_nothing():
    st = state(["KS", "KD", "9H", "7C", "5D", "4S", "3H", "2C"], need=600, hands=3, discards=2, blind="The Psychic",
               boss=True, jokers=["Half Joker"])
    rs = solver.RoundSolver(st, estimate)
    kk = rs.slots[:2]
    padded = rs._pad(kk, rs.slots, 5)
    s5, _t = rs.score(padded, [c for c in rs.slots if c not in padded], 3, 2, rs.ctx0)
    st0 = dict(st, jokers=[])
    s_plain = solver.RoundSolver(st0, estimate).score(padded, [c for c in rs.slots if c not in padded], 3, 2, rs.ctx0)[0]
    assert len(padded) == 5 and s5 == s_plain  # Half Joker needs <= 3 played cards
    assert rs.score(kk, rs.slots[2:], 3, 2, rs.ctx0)[0] == 0.0  # a 2-card play does not score under The Psychic


def test_jokerless_rounds_report_raw_p_and_broken_pairs_are_named():
    # 7802: ante-1 jokerless options read 0.98-0.99; jokerless rounds are calibrated raw (the joker map inflated them)
    st = state(["AS", "KD", "QH", "7C", "7D", "4S", "3H", "2C"], need=300, hands=3, discards=2)
    res = plan(st, samples=100)
    assert all(r["p_clear"] == r["p_model"] for r in res)
    assert solver.calibrate(0.8, jokerless=True) == 0.8 and solver.calibrate(0.8) > 0.8
    breaking = [r for r in res if r["action"] == "DISCARD" and set(idx(st, "7C", "7D")) & set(r["cards"])]
    assert breaking and all("breaks 77" in r["note"] for r in breaking)
    assert not any("breaks" in r["note"] for r in res if r["action"] == "DISCARD" and r not in breaking)


def test_misprint_planning_uses_mean_roll_not_est_floor():
    # 7810 PISY2P91 ante 3 Small 3200: est 945 (Misprint at +6) for QQ77+8C looked like 3 x 945 < 3200, but the roll is
    # 0..23 (mean +11.5): the hand averaged ~1245 and actually scored 1550; the blind cleared in 2 hands (p 0.95 raw)
    st = state(["AC", "QS", "QC", "JD", "9D", "8C", "7H", "7D"], need=3200, hands=3, discards=2,
               jokers=["Joker", "Even Steven", "Splash", "Misprint"])
    st["jokers"][0]["ability"] = {"mult": 4}
    st["jokers"][3]["ability"] = {"extra": {"min": 0, "max": 23}}
    rs = solver.RoundSolver(st, estimate)
    play = [rs.slots[i] for i in (1, 2, 5, 6, 7)]
    held = [c for c in rs.slots if c not in play]
    est6 = estimate("Two Pair", [c.d for c in play], [c.d for c in held], dict(st, _misprint_roll=6), played_n=5)[0]
    plan_v, _t = rs.score(play, held, 3, 2, rs.ctx0)
    base, slope = rs._components("Two Pair", play, play, held, 3, 2, None)[:2]
    assert base + 6 * slope == pytest.approx(est6, abs=1)
    assert plan_v == pytest.approx(base + 11.5 * slope) and plan_v > est6


def test_pillar_ahead_plays_fewest_cards():
    st = state(["AS", "AD", "QH", "9C", "7S", "5D", "3H", "2C"], need=3000, hands=3, discards=0, blind="Big Blind",
               blind_select={"choices": {"Boss": {"name": "The Pillar", "boss": True}}})
    res = plan(st, samples=60)
    assert not any("filler" in r["note"] for r in res)
    assert all(len(r["cards"]) == 1 for r in res if r["note"].startswith("dig"))



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
    assert any(r["note"].startswith("throwaway") and r["p_model"] == 1.0 for r in res)
    assert top["p_model"] == 1.0
    now = find(res, "PLAY", idx(st, "AH", "KH", "9H", "6H", "3H"))
    assert now["p_model"] < 0.5


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


def test_tarot_use_options_change_hand_cards_then_plan():
    # 7802 4EP3BAN9: Death was held at The Needle, every line read 0.02 without it
    st = state(["KS", "KH", "KD", "9C", "7H", "4C", "3S", "2D"], need=420, hands=1, discards=0)
    st["consumables"] = [{"index": 1, "key": "c_death", "name": "Death", "set": "Tarot"}]
    plain = plan(st, samples=60)[0]
    res = solver.consumable_options(st, estimate, time_budget_s=3, samples=60)
    top = res[0]
    assert top["action"] == "USE" and top["name"] == "Death" and top["p_clear"] > plain["p_clear"]
    assert hand_rank(st, top["targets"][1]) == "King" and "Four of a Kind" in top["then"]["note"]
    sun = dict(st, consumables=[{"index": 1, "key": "c_sun", "name": "The Sun", "set": "Tarot"}])
    assert solver._apply_tarot(st["hand"], "Hearts", (0, 2))[2]["suit"] == "Hearts"
    assert solver.consumable_options(dict(sun, consumables=[]), estimate) == []


def hand_rank(st, index):
    return next(c["rank"] for c in st["hand"] if c["index"] == index)


def test_held_card_jokers_get_low_single_card_plays():
    # 7810 R5DXHPXU: Shoot the Moon (+13 mult per Queen HELD) - the round policy played its Queens as High Card
    st = state(["QS", "QH", "QC", "9D", "7S", "5C", "3H", "2D"], need=5000, hands=3, discards=0,
               jokers=["Shoot the Moon"])
    rs = solver.RoundSolver(st, estimate)
    s, play, t = rs.best_play(rs.slots, 3, 0, rs.ctx0)
    assert all(c.rank != 12 for c in play)  # every Queen stays held


def test_tower_targets_a_junk_card_not_a_joker_scorer():
    # 7817 8KNB2U3T: The Tower stoned a valuable card instead of junk; equal best plays now -> the target that loses
    # the least on its own (here a Mult card 4C vs a plain 2S)
    st = state(["KS", "KC", "4C", "9S", "8D", "6H", "2S", "JH"], need=5000, hands=1, discards=0)
    st["hand"][2]["enhancement"] = "m_mult"
    st["consumables"] = [{"index": 1, "key": "c_tower", "name": "The Tower", "set": "Tarot"}]
    res = solver.consumable_options(st, estimate, time_budget_s=2, samples=20)
    four = next(c["index"] for c in st["hand"] if c["rank"] == "4")
    assert res and four not in res[0]["targets"]


def test_obelisk_policy_avoids_resets_and_quantiles_take_a_boss():
    # 7804 9BFAAC9S: Obelisk x3.4; the round policy reset it with the most played type and projected 2.5-5k/hand
    st = state(["KS", "KD", "9C", "7H", "5S", "4C", "3D", "2D"], need=10 ** 9, hands=4, discards=0,
               jokers=["Obelisk"])
    st["jokers"][0]["ability"] = {"x_mult": 3.4, "extra": 0.2}
    for k, v in st["hand_levels"].items():
        v["played"] = {"Pair": 9, "High Card": 3}.get(k, 0)
    rs = solver.RoundSolver(st, estimate)
    raw_s, _p, raw_t = rs.best_play(rs.slots, 4, 0, rs.ctx0, raw=True)
    s, _p, t = rs.best_play(rs.slots, 4, 0, rs.ctx0)
    assert raw_t == "Pair" and t != "Pair"  # Pair KK resets x3.4 for the 3 later hands
    flint = solver.round_score_quantiles(st, estimate, n=20, boss="The Flint")
    plain = solver.round_score_quantiles(st, estimate, n=20)
    assert flint["round"][1] < plain["round"][1]
    needle = solver.round_score_quantiles(dict(st, jokers=[]), estimate, n=10, boss="The Needle")
    assert needle["per_hand"] == needle["round"]  # one hand


def test_quantiles_keep_the_pillars_played_cards_debuffed():
    # 7814 41YJQ6Q7 / 7811 V3KKS63Z: cards played earlier this ante are debuffed at The Pillar
    st = state(["KS"], need=300, hands=3, discards=2, jokers=["Joker"])
    st.update(phase="SHOP", hand=[], hands_per_round=3, discards_per_round=2)
    played = [c["id"] for c in st["deck"]["cards"] if c["rank"] in ("King", "Queen", "Jack", "Ace", "10")]
    hit = solver.round_score_quantiles(st, estimate, n=20, boss="The Pillar", debuff_ids=played)
    free = solver.round_score_quantiles(st, estimate, n=20, boss="The Pillar")
    assert hit["round"][1] < free["round"][1]


def test_raised_fist_plays_low_fillers_and_holds_high_cards():
    # 7807 ELNXY7D1: Raised Fist doubles the lowest HELD rank; KK + low fillers keeps Q J 5 held (5 -> +10 mult)
    st = state(["KS", "KD", "QC", "JH", "5S", "4C", "3D", "2H"], need=10 ** 9, hands=3, discards=0,
               jokers=["Raised Fist"])
    rs = solver.RoundSolver(st, estimate)
    s, play, t = rs.best_play(rs.slots, 3, 0, rs.ctx0)
    held = [c for c in rs.slots if c not in play]
    assert t == "Pair" and min(c.rank for c in held) >= 5 and len(play) == 5


def test_loyalty_card_counter_advances_inside_the_round():
    # 7808 W99CGI9N: Loyalty Card x4 was counted on every simulated hand; it fires once every 6 hands
    st = state(["KS", "KD", "9C", "7H", "5S", "4C", "3D", "2D"], need=10 ** 9, hands=4, discards=0,
               jokers=["Loyalty Card"], run={"hands_played_total": 10})
    st["jokers"][0]["ability"] = {"extra": {"every": 5, "Xmult": 4}, "hands_played_at_create": 5}
    rs = solver.RoundSolver(st, estimate)
    kk = rs.slots[:2]
    vals = [rs.score(kk, rs.slots[2:], h, 0, rs.ctx0)[0] for h in (4, 3, 2, 1)]
    assert sum(1 for v in vals if v == max(vals)) == 1 and max(vals) == 4 * min(vals)  # x4 on one hand of the 4


def test_boss_calibration_is_capped_and_monotone():
    # 2026-10-14 since 14:00: boss rounds mapped into 0.95-0.99 realized 0.895; raw p was calibrated there
    ps = [i / 100 for i in range(101)]
    boss = [solver.calibrate(p, boss=True) for p in ps]
    assert all(b2 >= b1 for b1, b2 in zip(boss, boss[1:]))
    assert solver.calibrate(0.95, boss=True) == pytest.approx(0.95) < solver.calibrate(0.95)
    assert solver.calibrate(0.5, boss=True) == solver.calibrate(0.5)
