"""Shop option simulator (balatro_env/shop_sim.py) on hand-built Gold SHOP / PACK_OPENING observations."""

import time

import pytest

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


def shop_state(jokers=(), shop_jokers=(), money=10, ante=1, small="Defeated", boss="The Hook", slots=6, pack=None,
               boosters=()):
    deck = [{"id": i + 1, "rank": RK.get(r, r), "suit": ST[s], "remaining": True}
            for i, (s, r) in enumerate((s, r) for s in "SHDC" for r in "23456789TJQKA")]
    base = BLIND_BASE[3][ante - 1]
    owned = [dict(j, index=i + 1) for i, j in enumerate(jokers)]
    return {"phase": "PACK_OPENING" if pack else "SHOP", "stake": 8, "ante": ante, "money": money, "joker_slots": slots,
            "hand_size": 8, "hands_per_round": 3, "discards_per_round": 2, "highlight_limit": 5, "jokers": owned,
            "deck": {"cards": deck, "draw_pile": 52, "total": 52},
            "hand_levels": {k: {"level": 1, "chips": c, "mult": m, "played": 0, "played_this_round": 0, "visible": True}
                            for k, (c, m) in LEVELS.items()},
            "shop": {"jokers": [dict(j, index=i + 1) for i, j in enumerate(shop_jokers)], "vouchers": [],
                     "boosters": list(boosters)},
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


def test_buffoon_and_celestial_packs_are_valued_as_expected_best_pick():
    boosters = [{"index": 1, "kind": "Buffoon", "name": "Buffoon Pack", "size": 2, "choose": 1, "cost": 4},
                {"index": 2, "kind": "Celestial", "name": "Celestial Pack", "size": 3, "choose": 1, "cost": 4},
                {"index": 3, "kind": "Arcana", "name": "Arcana Pack", "size": 3, "choose": 1, "cost": 4}]
    st = shop_state(ante=1, small="Defeated", money=6, boosters=boosters)
    st["hand_levels"]["Pair"]["played"] = 3
    assert not any(o.get("pack") for o in shop_sim.options_from_state(st))  # opt-in only
    opts = shop_sim.options_from_state(st, packs=True)
    assert [o["label"] for o in opts if o.get("pack")] == ["buy Buffoon Pack $4", "buy Celestial Pack $4"]
    assert opts[1]["booster_index"] == 1
    res = by_label(run(st, opts, blinds=2, budget_s=20, min_samples=40))
    buff, cel = res["buy Buffoon Pack $4"], res["buy Celestial Pack $4"]
    assert buff["feasible"] and buff["money_after"] == 2 and buff["delta"] > 0.05  # jokerless ante 1: any joker helps
    assert 0 <= cel["delta"] < buff["delta"]
    assert any("virtual packs" in n for n in buff["notes"]) and not any(r.startswith("_pack") for r in res)


def test_mult_joker_beats_baseline_and_planet_is_not_negative():
    # jokerless ante 1 after the Small: Big 450 + The Hook 600
    jolly = joker("Joker", ability={"mult": 4})
    st = shop_state(ante=1, small="Defeated", boss="The Hook", money=10)
    res = by_label(run(st, [{"label": "base"}, {"label": "Joker +4", "add_joker": jolly, "cost": 2},
                            {"label": "Mercury", "levels": ["Pair"], "cost": 3}], blinds=2))
    assert res["Joker +4"]["delta"] > 0.05
    assert res["Mercury"]["delta"] >= -0.02
    assert res["Joker +4"]["money_after"] == 8 and res["Mercury"]["money_after"] == 7


def test_selling_the_only_scorer_hurts_and_slots_are_enforced():
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4})], ante=1, small="Defeated", slots=1)
    res = by_label(run(st, [{"label": "base"}, {"label": "sell", "sell": [1]},
                            {"label": "buy no slot", "add_joker": joker("Jolly Joker"), "cost": 3}], blinds=2))
    assert res["sell"]["delta"] < -0.05 and res["sell"]["money_after"] == 12
    assert not res["buy no slot"]["feasible"] and res["buy no slot"]["p_next"] is None


def test_perishable_expiry_and_rent():
    def scorer(tally):
        return joker("Joker", ability={"mult": 4}, perishable=True, perish_tally=tally, rental=True)
    st = shop_state(ante=1, small="Defeated")
    res = by_label(run(st, [{"label": "base"}, {"label": "dies", "add_joker": scorer(1), "cost": 1},
                            {"label": "lives", "add_joker": scorer(5), "cost": 1}], blinds=2))
    dies, lives = res["dies"], res["lives"]
    assert abs(dies["p_blinds"][0] - lives["p_blinds"][0]) < 0.05  # same deals, same joker in the first blind
    assert dies["p_blinds"][1] < lives["p_blinds"][1] - 0.05
    assert any("perishes" in n for n in dies["notes"])
    assert lives["rent_per_round"] == 3 and lives["money_after_rent"] == 10 - 1 - 6


def test_mr_bones_saves_a_failed_blind():
    st = shop_state(ante=1, small="Defeated")
    res = by_label(run(st, [{"label": "base"}, {"label": "bones", "add_joker": joker("Mr. Bones"), "cost": 5}],
                       blinds=2))
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


def test_dagger_and_madness_destroy_jokers_and_baseline_has_fixed_samples():
    scorer = joker("Joker", ability={"mult": 4})
    st = shop_state(jokers=[joker("Ceremonial Dagger", ability={"mult": 0}), scorer], ante=1, small="Defeated")
    res = by_label(run(st, [{"label": "base"}, {"label": "sell Dagger", "sell": [1]}], blinds=2, budget_s=0.01,
                       min_samples=4))
    assert res["base"]["n"] >= shop_sim.BASE_N  # guaranteed whatever the budget
    assert any("destroy" in n for n in res["base"]["notes"])
    dag = shop_sim._OptionSim(shop_sim._solver(), estimate, st, shop_sim.upcoming_blinds(st, 2), 0)
    removed, growth = set(), {}
    dag._select_blind({"boss": True}, removed, growth, __import__("random").Random(0))
    assert removed == {1} and growth == {0: 4.0}  # the Joker to its right (sell $2) becomes +4 Dagger mult
    mad = shop_state(jokers=[joker("Madness", ability={"x_mult": 1}), scorer, joker("Egg", eternal=True)], ante=1,
                     small="Upcoming")
    sim = shop_sim._OptionSim(shop_sim._solver(), estimate, mad, shop_sim.upcoming_blinds(mad, 3), 0)
    removed, growth = set(), {}
    sim._select_blind({"boss": False}, removed, growth, __import__("random").Random(0))
    assert removed == {1} and growth == {0: 0.5}  # Egg is eternal: only the Joker can go
    sim._select_blind({"boss": True}, removed, growth, __import__("random").Random(0))
    assert growth == {0: 0.5}  # Madness fires on Small/Big only


def test_riff_raff_creates_commons_into_free_slots():
    st = shop_state(ante=1, small="Defeated", slots=4)
    res = by_label(run(st, [{"label": "base"}, {"label": "riff", "add_joker": joker("Riff-raff"), "cost": 6}], blinds=2))
    riff = res["riff"]
    assert any("Riff-raff creates 3.0" in n for n in riff["notes"])  # 3 free slots: 2 on the first select, 1 more
    assert riff["delta"] > 0.05


def test_eternal_rental_is_flagged_with_run_rent_and_constellation_grows_on_planets():
    lusty = joker("Lusty Joker", eternal=True, rental=True, cost=1)
    st = shop_state(ante=2, small="Defeated")  # Big + Boss of ante 2 open, antes 3-8 ahead: 2 + 18 round-ends
    res = by_label(run(st, [{"label": "base"}, {"label": "lusty", "add_joker": lusty, "cost": 1}], blinds=1,
                       budget_s=1, min_samples=8))
    assert res["lusty"]["rent_run"] == 3 * 20 and any("ETERNAL RENTAL" in n for n in res["lusty"]["notes"])
    con = shop_state(jokers=[joker("Constellation", ability={"x_mult": 1.2})])
    st3, err, notes = shop_sim.apply_option(con, {"levels": ["Pair"], "cost": 3})
    assert err is None and st3["jokers"][0]["ability"]["x_mult"] == pytest.approx(1.3)


def test_every_rental_pays_rent_each_round_and_dead_shops_are_flagged():
    # 7807 B6JW7ICP: a 2nd rental was rated +0.56 with no rent; two rentals at $4 leave every later shop below $0
    owned = joker("Joker", ability={"mult": 4}, rental=True)
    second = joker("Jolly Joker", ability={"t_mult": 8, "type": "Pair"}, rental=True, cost=1)
    st = shop_state(jokers=[owned], money=4, ante=1, small="Defeated")
    res = by_label(run(st, [{"label": "base"}, {"label": "2nd rental", "add_joker": second, "cost": 1}],
                       budget_s=2, min_samples=16))
    two, base = res["2nd rental"], res["base"]
    assert two["rent_per_round"] == 6 and two["rent_horizon"] == 18 and base["rent_horizon"] == 9
    assert two["money_path"][0] < 0 and any("shop is dead" in n for n in two["notes"])
    assert two["money_path"][-1] <= base["money_path"][-1] - 6  # $1 cost + $9 rent, partly offset by more unused hands
    assert two["delta_adj"] <= two["delta"] - 0.09 + 1e-9
