"""Shop option simulator (balatro_env/shop_sim.py) on hand-built Gold SHOP / PACK_OPENING observations."""

import time

from balatro_env import shop_sim
from balatro_env.scripts.cli import BLIND_BASE, estimate

RK = {"A": "Ace", "K": "King", "Q": "Queen", "J": "Jack", "T": "10"}
ST = {"S": "Spades", "H": "Hearts", "D": "Diamonds", "C": "Clubs"}
LEVELS = {"High Card": (5, 1), "Pair": (10, 2), "Two Pair": (20, 2), "Three of a Kind": (30, 3), "Straight": (30, 4),
          "Flush": (35, 4), "Full House": (40, 4), "Four of a Kind": (60, 7), "Straight Flush": (100, 8)}


def joker(name, **kw):
    j = {"name": name, "set": "Joker", "ability": {}, "sell_cost": 2, "cost": 5, "eternal": False, "perishable": False,
         "rental": False, "rarity": 1}
    j.update(kw)
    return j


def shop_state(jokers=(), shop_jokers=(), money=10, ante=1, small="Defeated", boss="The Hook", slots=6, pack=None):
    deck = [{"id": i + 1, "rank": RK.get(r, r), "suit": ST[s], "remaining": True}
            for i, (s, r) in enumerate((s, r) for s in "SHDC" for r in "23456789TJQKA")]
    base = BLIND_BASE[3][ante - 1]
    owned = [dict(j, index=i + 1) for i, j in enumerate(jokers)]
    return {"phase": "PACK_OPENING" if pack else "SHOP", "stake": 8, "ante": ante, "money": money, "joker_slots": slots,
            "hand_size": 8, "hands_per_round": 3, "discards_per_round": 2, "highlight_limit": 5, "jokers": owned,
            "deck": {"cards": deck, "draw_pile": 52, "total": 52},
            "hand_levels": {k: {"level": 1, "chips": c, "mult": m, "played": 0, "played_this_round": 0, "visible": True}
                            for k, (c, m) in LEVELS.items()},
            "shop": {"jokers": [dict(j, index=i + 1) for i, j in enumerate(shop_jokers)], "vouchers": [], "boosters": []},
            "pack": {"cards": [dict(c, index=i + 1) for i, c in enumerate(pack or [])]},
            "blind_select": {"choices": {
                "Small": {"name": "Small Blind", "boss": False, "chips": base, "state": small},
                "Big": {"name": "Big Blind", "boss": False, "chips": int(base * 1.5), "state": "Upcoming"},
                "Boss": {"name": boss, "boss": True, "chips": base * 2, "state": "Upcoming"}}}}


def run(st, options=None, budget_s=20.0, min_samples=80, **kw):
    return shop_sim.value_options(st, options, budget_s=budget_s, estimate_fn=estimate, min_samples=min_samples, **kw)


def by_label(res):
    return {r["label"]: r for r in res}


def test_upcoming_blinds_continue_into_next_ante():
    st = shop_state(ante=2, small="Defeated", boss="The Water")
    bl = shop_sim.upcoming_blinds(st, 3, BLIND_BASE)
    assert [(b["ante"], b["kind"], b["chips"]) for b in bl] == [(2, "Big", 1500), (2, "Boss", 2000), (3, "Small", 3200)]
    assert bl[1]["name"] == "The Water" and bl[1]["boss"]


def test_mult_joker_beats_baseline_and_chips_only_at_base_mult():
    jolly = joker("Joker", ability={"mult": 4})
    st = shop_state(ante=2, small="Upcoming", boss="The Hook", money=10)
    res = by_label(run(st, [{"label": "base"}, {"label": "Joker +4", "add_joker": jolly, "cost": 2},
                            {"label": "Mercury", "levels": ["Pair"], "cost": 3}], budget_s=60, min_samples=150))
    assert res["Joker +4"]["delta"] > 0.05
    assert res["Joker +4"]["p_next"] > res["base"]["p_next"]
    assert res["Mercury"]["delta"] >= -0.02
    assert res["Joker +4"]["money_after"] == 8 and res["Mercury"]["money_after"] == 7


def test_selling_the_only_scorer_hurts_and_slots_are_enforced():
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4})], ante=2, small="Upcoming", slots=1)
    res = by_label(run(st, [{"label": "base"}, {"label": "sell", "sell": [1]},
                            {"label": "buy no slot", "add_joker": joker("Jolly Joker"), "cost": 3}]))
    assert res["sell"]["delta"] < -0.05 and res["sell"]["money_after"] == 12
    assert not res["buy no slot"]["feasible"] and res["buy no slot"]["p_next"] is None


def test_perishable_expiry_and_rent():
    def scorer(tally):
        return joker("Joker", ability={"mult": 4}, perishable=True, perish_tally=tally, rental=True)
    st = shop_state(ante=2, small="Upcoming")
    res = by_label(run(st, [{"label": "base"}, {"label": "dies", "add_joker": scorer(1), "cost": 1},
                            {"label": "lives", "add_joker": scorer(5), "cost": 1}]))
    dies, lives = res["dies"], res["lives"]
    assert abs(dies["p_blinds"][0] - lives["p_blinds"][0]) < 0.05  # same deals, same joker in blind 1
    assert dies["p_blinds"][2] < lives["p_blinds"][2] - 0.05
    assert any("perishes" in n for n in dies["notes"])
    assert lives["rent_per_round"] == 3 and lives["money_after_rent"] == 10 - 1 - 9


def test_mr_bones_saves_a_failed_blind():
    st = shop_state(ante=2, small="Upcoming")
    res = by_label(run(st, [{"label": "base"}, {"label": "bones", "add_joker": joker("Mr. Bones"), "cost": 5}]))
    assert res["bones"]["delta"] > 0.05 and any("Mr. Bones" in n for n in res["bones"]["notes"])


def test_default_options_and_latency():
    shop = [joker("Joker", ability={"mult": 4}, cost=2), joker("Scary Face", cost=4),
            {"name": "Mercury", "set": "Planet", "cost": 3}, joker("Blueprint", cost=10)]
    st = shop_state(shop_jokers=shop, money=6, ante=1, small="Defeated")
    labels = [o["label"] for o in shop_sim.options_from_state(st)]
    assert labels == ["baseline (buy nothing)", "buy Joker $2", "buy Scary Face $4", "buy Mercury $3"]
    t0 = time.perf_counter()
    res = shop_sim.value_options(st, estimate_fn=estimate)  # default 4 s budget
    assert time.perf_counter() - t0 < 8.0
    assert all(r["n"] >= 24 for r in res) and res[0]["label"] != "baseline (buy nothing)"


def test_pack_options_and_full_slots_sell_weakest():
    owned = [joker("Joker", ability={"mult": 4}), joker("Egg", ability={})]
    pack = [joker("Jolly Joker", ability={"t_mult": 8, "type": "Pair"}), {"name": "Jupiter", "set": "Planet"}]
    st = shop_state(jokers=owned, slots=2, pack=pack, ante=2, small="Upcoming")
    opts = shop_sim.options_from_state(st)
    assert [o["label"] for o in opts] == ["skip pack", "take Jolly Joker", "take Jupiter"]
    assert opts[1]["sell"] == "weakest"
    res = by_label(run(st, budget_s=30))
    take = next(r for r in res.values() if r["label"].startswith("take Jolly"))
    assert "(sell Egg)" in take["label"] and take["delta"] > 0
