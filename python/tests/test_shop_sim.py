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
    # sellable rentals count RENT_KEEP (6) blinds of rent at least (7817 D5DGN1SY: 3 blinds made two rentals cheap)
    assert two["rent_per_round"] == 6 and two["rent_horizon"] == 36 and base["rent_horizon"] == 18
    assert two["money_path"][0] < 0 and any("shop is dead" in n for n in two["notes"])
    assert two["money_path"][-1] <= base["money_path"][-1] - 6  # $1 cost + $9 rent, partly offset by more unused hands
    assert two["p_adj"] == pytest.approx(two["p_next"] * max(0.1, 1 - 0.36 - 0.05 * two["dead_shops"]))


def test_obelisk_growth_carries_across_simulated_rounds():
    # 7803 CLA5SVN7: the SIM restarted Obelisk at the shop's x_mult every blind and suggested selling a growing one
    st = shop_state(jokers=[joker("Obelisk", ability={"x_mult": 1.0, "extra": 0.2})], ante=1, small="Defeated")
    st["hand_levels"]["Pair"]["played"] = 6
    sim = shop_sim._OptionSim(shop_sim._solver(), estimate, st, shop_sim.upcoming_blinds(st, 3, BLIND_BASE), 0)
    sim.base = st
    for s in range(4):
        sim.sample(s)
    later = [key[4] for key in sim.solvers if key[0] > 0]
    assert later and all(ob is not None for ob in later)
    assert any(ob[0] > 1.0 for ob in later)  # non-max types played in a round raise the next round's Obelisk


def test_terminal_boss_values_the_end_of_horizon_build():
    # 7807 SWXRQQVU / 7803 KLHEEA8D: the 3-blind horizon saturates at ~1.0, so the end build is also played once
    # against the next boss; a joker that perishes inside the horizon loses that terminal value
    st = shop_state(ante=1, small="Defeated")
    term = shop_sim.terminal_blind(st, 3, BLIND_BASE)
    assert (term["ante"], term["kind"], term["chips"]) == (2, "Boss", 2000)
    keep = joker("Joker", ability={"mult": 4})
    dies = joker("Joker", ability={"mult": 4}, perishable=True, perish_tally=2)
    res = by_label(run(st, [{"label": "base"}, {"label": "keep", "add_joker": keep, "cost": 2},
                            {"label": "dies", "add_joker": dies, "cost": 2}], budget_s=10, min_samples=48))
    assert res["keep"]["p_term"] > res["dies"]["p_term"] + 0.05
    assert res["keep"]["value"] > res["dies"]["value"]
    assert all(r["terminal"] == "a2 boss 2000" for r in res.values())


def test_weakest_sell_is_judged_with_the_new_joker_in_place():
    # 7803 C5AF29KG: the sell pick ignored that the incoming joker makes an owned one strong
    owned = [joker("Scary Face"), joker("Joker", ability={"mult": 4})]
    st = shop_state(jokers=owned, slots=2, ante=1, small="Defeated")
    w = shop_sim._resolve_weakest(shop_sim._solver(), estimate, st, shop_sim.upcoming_blinds(st, 2, BLIND_BASE), 3, 0,
                                  add=joker("Pareidolia"))
    assert w == 2  # every card is a face with Pareidolia: keep Scary Face (+30 chips per card), sell the Joker


def test_hologram_and_campfire_feeding():
    # 7810 QBEEJKG4: added cards feed Hologram (+x0.25 each); selling cards feeds Campfire (+x0.25, reset after boss)
    holo = shop_state(jokers=[joker("Hologram", ability={"x_mult": 1.5}), joker("Certificate")])
    st, err, notes = shop_sim.apply_option(holo, {"add_cards": [{"rank": "King", "suit": "Spades"}] * 2, "cost": 0})
    assert err is None and st["jokers"][0]["ability"]["x_mult"] == pytest.approx(2.0)
    rs2 = shop_sim._round_state(st, holo, {"name": "Big Blind", "boss": False, "chips": 450}, 2, set())
    assert rs2["jokers"][0]["ability"]["x_mult"] == pytest.approx(2.5)  # Certificate adds a card per round
    camp = shop_state(jokers=[joker("Campfire", ability={"x_mult": 1.0})],
                      shop_jokers=[{"name": "Pluto", "set": "Planet", "cost": 1, "sell_cost": 1}], money=5)
    flips = [o for o in shop_sim.options_from_state(camp) if o.get("flip") is not None]
    assert [o["label"] for o in flips] == ["flip Pluto $1 (Campfire)"]
    st2, err, notes = shop_sim.apply_option(camp, flips[0])
    assert err is None and st2["money"] == 5 and st2["jokers"][0]["ability"]["x_mult"] == pytest.approx(1.25)
    after_boss = shop_sim._round_state(st2, camp, {"name": "Small Blind", "boss": False, "chips": 300}, 1, set(),
                                       boss_passed=True)
    assert after_boss["jokers"][0]["ability"]["x_mult"] == 1.0


def test_mr_bones_ranks_above_nothing_when_the_next_blind_is_lost():
    # 7805 16N52CRZ: Bones was -0.14 at P 0.00 (rent penalties pushed p below 0); the save counts as survival
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4}, rental=True)], ante=3, small="Defeated", boss="The Wall")
    res = by_label(run(st, [{"label": "base"}, {"label": "bones", "add_joker": joker("Mr. Bones"), "cost": 1}],
                       blinds=2, budget_s=4, min_samples=32))
    assert res["bones"]["p_blinds"][0] > res["base"]["p_blinds"][0] and res["base"]["p_adj"] >= 0
    assert res["bones"]["delta_value"] >= 0


def test_blueprint_and_brainstorm_are_placed_to_copy_the_best_joker():
    # 7810 UIL7HPIQ: a new Blueprint was appended rightmost (copying nothing) and lost to To Do List
    import balatro_env.scripts.cli as cli_mod
    owned = [joker("Joker", ability={"mult": 4}), joker("Ramen", ability={"x_mult": 2.0})]
    st = shop_state(jokers=owned)
    bp = shop_sim._place_copy(st, {"add_joker": joker("Blueprint")}, cli_mod)
    assert bp["insert_at"] == 1 and bp["lead"] is None  # Joker | Blueprint | Ramen
    st2, err, notes = shop_sim.apply_option(st, bp)
    assert [j["name"] for j in st2["jokers"]] == ["Joker", "Blueprint", "Ramen"] and any("order:" in n for n in notes)
    egg_first = shop_state(jokers=[joker("Egg"), joker("Ramen", ability={"x_mult": 2.0})])
    bs = shop_sim._place_copy(egg_first, {"add_joker": joker("Brainstorm")}, cli_mod)
    st3, err, notes = shop_sim.apply_option(egg_first, bs)
    assert st3["jokers"][0]["name"] == "Ramen"  # Brainstorm copies the leftmost joker: move Ramen there


def test_survival_gain_never_ranks_below_baseline_and_rent_only_hits_the_future():
    # 7804 SL5MJZY1: a $1 eternal-rental Sly Joker was -0.20 although it cleared The Water; dead runs pay no rent
    sly = joker("Sly Joker", ability={"t_chips": 50, "type": "Pair"}, eternal=True, rental=True, cost=1)
    st = shop_state(ante=1, small="Defeated", boss="The Water")
    res = by_label(run(st, [{"label": "base"}, {"label": "sly", "add_joker": sly, "cost": 1},
                            {"label": "pluto", "levels": ["High Card"], "cost": 1}], budget_s=6, min_samples=32))
    s, b = res["sly"], res["base"]
    assert s["rent_run"] > 0
    if s["p_next"] >= b["p_next"] + shop_sim.SURVIVE_GAIN:
        assert s["value"] >= b["value"]
    assert s["value"] >= s["p_next"] * shop_sim.TERM_A  # rent never discounts the survival part
    assert res["pluto"]["delta_value"] >= 0  # a level-up is never worse than nothing


def test_red_card_buy_and_skip_option():
    st = shop_state(jokers=[joker("Red Card", ability={"mult": 0})], money=6,
                    boosters=[{"index": 1, "kind": "Standard", "name": "Standard Pack", "cost": 4}])
    opt = next(o for o in shop_sim.options_from_state(st) if o.get("red_card"))
    assert opt["label"] == "buy+skip Standard Pack $4 (Red Card +3)" and opt["booster_index"] == 1
    st2, err, notes = shop_sim.apply_option(st, opt)
    assert err is None and st2["money"] == 2 and st2["jokers"][0]["ability"]["mult"] == 3


def test_invisible_joker_duplicates_an_owned_joker_after_two_rounds():
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4}), joker("Invisible Joker", ability={"invis_rounds": 1})])
    sim = shop_sim._OptionSim(shop_sim._solver(), estimate, st, shop_sim.upcoming_blinds(st, 2, BLIND_BASE), 0)
    sim.base = st
    sim.sample(0)
    keys = sorted(sim.solvers, key=lambda key: key[0])
    assert keys[0][3] == () and 1 not in keys[0][1]  # round 1: Invisible still held
    assert keys[1][3] == (-1,) and 1 in keys[1][1]  # round 2: sold, a copy of the Joker added
    assert [j["name"] for j in sim.solvers[keys[1]].state["jokers"]] == ["Joker", "Joker"]


def test_the_needle_with_burglar_gives_one_plus_three_hands():
    # 7813 7FVPDIEW: The Needle sets 1 hand, then Burglar adds +3 at blind select (4 hands, 0 discards)
    st = shop_state(jokers=[joker("Burglar")], boss="The Needle")
    rs = shop_sim._round_state(st, st, {"name": "The Needle", "boss": True, "chips": 600}, 1, set())
    assert rs["hands_remaining"] == 4 and rs["discards_remaining"] == 0
    plain = shop_sim._round_state(shop_state(boss="The Needle"), shop_state(boss="The Needle"),
                                  {"name": "The Needle", "boss": True, "chips": 600}, 1, set())
    assert plain["hands_remaining"] == 1


def test_income_jokers_feed_the_money_path():
    # 7801 4JA3JTD1: Golden Joker (+$4 per round) was worth $0 in the sim
    st = shop_state(money=10)
    bl = shop_sim.upcoming_blinds(st, 3, BLIND_BASE)
    stats = [[1, 1, 1.0, 0.0] for _ in bl]
    gold = dict(st, jokers=[dict(joker("Golden Joker", ability={"extra": 4}), index=1)])
    assert shop_sim._income(gold, bl) == [4.0, 4.0, 4.0]
    plain = shop_sim._money_path(st, st, bl, stats, 10)
    rich = shop_sim._money_path(st, gold, bl, stats, 10)
    assert rich[-1] >= plain[-1] + 12
    assert shop_sim._rent_factor({"income": 12.0}) == pytest.approx(1.12)


def test_gift_card_grows_sell_values_and_swashbuckler():
    # 7802 4EP3BAN9: Gift Card (+$1 sell value per joker per round) feeding Swashbuckler was valued -0.14
    st = shop_state(jokers=[joker("Swashbuckler", sell_cost=2), joker("Gift Card", sell_cost=3),
                            joker("Joker", ability={"mult": 4}, sell_cost=1)])
    r0 = shop_sim._round_state(st, st, {"name": "Small Blind", "boss": False, "chips": 300}, 0, set())
    r2 = shop_sim._round_state(st, st, {"name": "Big Blind", "boss": False, "chips": 450}, 2, set())
    assert r0["jokers"][0]["ability"]["mult"] == 4  # 3 + 1
    assert r2["jokers"][0]["ability"]["mult"] == 8  # (3 + 2) + (1 + 2)


def test_grim_familiar_incantation_add_enhanced_cards():
    st = shop_state(pack=[{"name": "Grim", "set": "Spectral"}])
    st["hand"] = [dict(c, index=i + 1) for i, c in enumerate(st["deck"]["cards"][:8])]
    opt = next(o for o in shop_sim.options_from_state(st) if o["label"] == "take Grim")
    assert len(opt["add_cards"]) == 2 and all(c["rank"] == "Ace" and c["enhancement"] != "m_stone"
                                              for c in opt["add_cards"])
    st2, err, _n = shop_sim.apply_option(st, opt)
    assert err is None and len(st2["deck"]["cards"]) == len(st["deck"]["cards"]) + 1


def test_new_joker_goes_leftmost_when_brainstorm_is_owned():
    # 7807 2WEJC1IS: Stuntman read +0.00 although Brainstorm copies the leftmost joker
    import balatro_env.scripts.cli as cli_mod
    st = shop_state(jokers=[joker("Egg"), joker("Brainstorm")])
    o = shop_sim._place_copy(st, {"add_joker": joker("Ramen", ability={"x_mult": 2.0})}, cli_mod)
    assert o.get("insert_at") == 0
    plain = shop_state(jokers=[joker("Egg")])
    assert "insert_at" not in shop_sim._place_copy(plain, {"add_joker": joker("Ramen", ability={"x_mult": 2.0})},
                                                   cli_mod)


def test_planet_pick_prefers_the_main_hand_within_noise():
    base = {"label": "skip", "p_next": 0.5, "p_term": 0.5}
    sat = {"label": "_pack Celestial: Saturn", "p_next": 0.49, "p_term": 0.5}
    jup = {"label": "_pack Celestial: Jupiter", "p_next": 0.52, "p_term": 0.5}
    plan = {"kind": "Celestial", "main": "Saturn"}
    assert shop_sim._pick_value(sat, base, plan) >= shop_sim._value(base)  # never below skipping
    assert shop_sim._pick_value(sat, base, plan) > shop_sim._pick_value(jup, base, plan)


def test_terminal_build_drops_perishables_expiring_at_the_horizon_end():
    # 7817 6GRAU5IC: both carriers perish exactly at the end of the 3 blinds; the terminal round must play without
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4}, perishable=True, perish_tally=3)])
    blind = {"name": "Boss (unknown)", "boss": False, "chips": 800}
    assert not shop_sim._round_state(st, st, blind, 2, set())["jokers"][0].get("debuff")
    assert shop_sim._round_state(st, st, blind, 3, set())["jokers"][0]["debuff"]


def test_value_keeps_a_signal_when_a_far_blind_is_hopeless():
    # 7806 FYEJZFFU: The Wall made P(all 3) 0 for every option; the option clearing the next blind more often wins
    base = {"p_blinds": [0.98, 0.5, 0.0], "p_next": 0.0, "p_term": 0.0}
    mad = {"p_blinds": [1.0, 0.58, 0.0], "p_next": 0.0, "p_term": 0.0}
    assert shop_sim._value(mad) > shop_sim._value(base)
    sure = {"p_blinds": [1.0, 1.0, 1.0], "p_next": 1.0, "p_term": 1.0, "p_stretch": 1.0, "score_ratio_term": 1.0,
            "score_ratio_stretch": 1.0}
    assert shop_sim._value(sure) == pytest.approx(1.0)


def test_stretch_check_looks_past_perishables_and_keeps_a_signal():
    # 7808 NE4L52DR: perishables bought at ante 1-2 die at the ante-3 cliff; 7812 BRILA2MW: when the next boss was
    # hopeless (or sure) for every option, Abstract's +75% est read +0.00. The stretch round (STRETCH_X x the
    # terminal boss chips) plays the build without the perishables dying within TERM_PERISH_AHEAD rounds after it
    st = shop_state(jokers=[joker("Joker", ability={"mult": 4}, perishable=True, perish_tally=5)])
    term = shop_sim.terminal_blind(st, 3, BLIND_BASE)
    assert "perish_ahead" not in term and not shop_sim._round_state(st, st, term, 3, set())["jokers"][0].get("debuff")
    stretch = dict(term, perish_ahead=shop_sim.TERM_PERISH_AHEAD)
    assert shop_sim._round_state(st, st, stretch, 4, set())["jokers"][0].get("debuff")
    assert shop_sim._term_w(shop_state(ante=1)) == shop_sim.TERM_EARLY
    assert shop_sim._term_w(shop_state(ante=3)) == (shop_sim.TERM_A, shop_sim.TERM_B)
    sure = {"p_blinds": [1.0] * 3, "p_next": 1.0, "p_term": 0.0, "score_ratio_term": 0.6, "score_ratio_stretch": 0.2}
    more = dict(sure, score_ratio_term=0.9, score_ratio_stretch=0.3)
    assert shop_sim._value(more) > shop_sim._value(sure)  # score gains register when every p is 0 or 1
