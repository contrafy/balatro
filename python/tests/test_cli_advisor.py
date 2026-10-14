"""Offline checks of the cli.py advisor on hand-built Gold-stake (8) observations: stake stickers and blind-skip advice."""

import contextlib
import io

import pytest

from balatro_env.scripts import cli


@pytest.fixture(autouse=True)
def _no_run_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "RUNS_DIR", str(tmp_path))  # shop_advise appends to shop_log.tsv
    monkeypatch.setattr(cli, "LEGAL", {})


def _out(fn, d):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(d)
    return buf.getvalue()


def _advice(text):
    return next(line for line in text.splitlines() if line.startswith("ADVICE"))


def joker(name, index, **kw):
    j = {"name": name, "index": index, "set": "Joker", "sell_cost": 2, "eternal": False, "perishable": False, "rental": False}
    j.update(kw)
    return j


def shop(jokers=(), shop_jokers=(), money=10, ante=2, boosters=()):
    return {"phase": "SHOP", "stake": 8, "ante": ante, "money": money, "joker_slots": 6, "consumable_slots": 2, "hands_per_round": 3,
            "jokers": list(jokers), "consumables": [], "hand_levels": {},
            "shop": {"jokers": list(shop_jokers), "vouchers": [], "boosters": list(boosters), "reroll_cost": 5},
            "blind_select": {"on_deck": "Small", "choices": {"Small": {"name": "Small Blind", "chips": 1000, "state": "Upcoming"},
                                                             "Big": {"name": "Big Blind", "chips": 1500, "state": "Upcoming"},
                                                             "Boss": {"name": "The Hook", "chips": 2000, "state": "Upcoming"}}}}


def blind_select(tag, jokers=(), ante=1, levels=None):
    sm, bg, bo = {2: (1000, 1500, 2000), 3: (3200, 4800, 6400)}.get(ante, (300, 450, 600))
    return {"phase": "BLIND_SELECT", "stake": 8, "ante": ante, "money": 4, "joker_slots": 6, "jokers": list(jokers), "hand_levels": levels or {},
            "blind_select": {"on_deck": "Small", "choices": {"Small": {"name": "Small Blind", "chips": sm, "state": "Select", "tag": tag, "tag_key": tag},
                                                             "Big": {"name": "Big Blind", "chips": bg, "state": "Upcoming"},
                                                             "Boss": {"name": "The Hook", "chips": bo, "state": "Upcoming"}}}}


def test_stickers_display():
    assert cli.stickers(joker("Joker", 1, eternal=True, rental=True)) == "{ETERNAL,RENTAL(-$3/round)}"
    assert "PERISHED" in cli.stickers(joker("Joker", 1, perishable=True, perish_tally=0))
    assert cli.stickers(joker("Joker", 1, perishable=True, perish_tally=3)) == "{PERISHABLE(3 rounds left)}"


def test_dead_perishable_is_sold_first():
    d = shop(jokers=[joker("Jolly Joker", 1), joker("Sly Joker", 2, perishable=True, perish_tally=0)])
    out = _out(cli.shop_advise, d)
    assert _advice(out).startswith("ADVICE: SELL FIRST -> b sell 2") and "Shop advisor:" in out  # ranking no longer hidden


def test_eternal_never_sold_for_room():
    # full slots, every joker weak; the Eternal one is the weakest but must not be offered for sale
    owned = [joker("Gros Michel", 1, eternal=True)] + [joker("Joker", i) for i in range(2, 7)]
    d = shop(jokers=owned, shop_jokers=[{"index": 1, "name": "Cavendish", "set": "Joker", "cost": 4}], money=20, ante=4)
    out = _out(cli.shop_advise, d)
    assert "b sell 1 " not in out


def test_second_rental_refused_early():
    d = shop(jokers=[joker("Jolly Joker", 1, rental=True)],
             shop_jokers=[{"index": 1, "name": "Sly Joker", "set": "Joker", "cost": 1, "rental": True}], money=8)
    out = _out(cli.shop_advise, d)
    assert "drains the run to $0" in out
    assert "b buy 1" not in _advice(out)


def test_shop_line_prices_rental_drain():
    d = shop(shop_jokers=[{"index": 1, "name": "Joker", "set": "Joker", "cost": 1, "rental": True}], money=8, ante=1)
    out = _out(cli.shop_advise, d)
    assert "RENTAL: $1 now, then -$3 x" in out


def test_eternal_weak_joker_penalised():
    d = shop(jokers=[joker("Jolly Joker", 1), joker("Sly Joker", 2)],
             shop_jokers=[{"index": 1, "name": "Smeared Joker", "set": "Joker", "cost": 7, "eternal": True}], money=20)
    out = _out(cli.shop_advise, d)
    assert "ETERNAL on a weak/conditional joker" in out
    assert "b buy 1" not in _advice(out)


def test_expiring_perishables_counted_out():
    owned = [joker("Misprint", 1, perishable=True, perish_tally=2), joker("Photograph", 2, perishable=True, perish_tally=2)]
    out = _out(cli.shop_advise, shop(jokers=owned))
    assert "perishing soon" in out
    assert "Scorers still alive next ante: 0" in out


def test_sell_precheck_blocks_eternal(monkeypatch):
    d = shop(jokers=[joker("Joker", 1, eternal=True)])
    with pytest.raises(SystemExit):
        cli.pre_checks("sell", "SELL_JOKER", {"index": 1}, [1], d)


@pytest.mark.parametrize("tag,jokers,ante,expect,strong", [
    ("tag_rare", [], 1, "b blind", None),            # pays in the next shop, after the Big Blind
    ("tag_polychrome", [], 1, "b blind", None),
    ("tag_buffoon", [], 1, "b skip", None),          # Mega Buffoon pack opens right away
    ("tag_rare", [joker("Joker", 1), joker("Jolly Joker", 2)], 1, "b blind", None),  # ante 1: joker-now tags only
    ("tag_rare", [joker("Joker", 1, ability={"mult": 4}), joker("Jolly Joker", 2, ability={"t_mult": 8, "type": "Pair"})], 2, "b blind", None),  # EMERGENCY: no skip
    ("tag_rare", [joker("Joker", 1, ability={"mult": 4}), joker("Jolly Joker", 2, ability={"t_mult": 8, "type": "Pair"})], 2, "b skip", "strong"),
])
def test_small_blind_skip_advice(tag, jokers, ante, expect, strong):
    lv = {"Pair": {"level": 6, "chips": 60, "mult": 7, "played": 5}} if strong else {"Pair": {"level": 1, "chips": 10, "mult": 2, "played": 5}}
    assert expect in _advice(_out(cli.show, blind_select(tag, jokers, ante, lv)))


def _card(rank, suit, i):
    return {"rank": rank, "suit": suit, "index": i}


@pytest.mark.parametrize("rem,fires", [(0, True), (1, False), (5, False)])
def test_loyalty_card_fires_when_stored_remaining_is_zero(rem, fires):
    # card.lua recomputes loyalty_remaining during scoring; the stored (previous-hand) value 0 means x4 on this hand
    loyal = joker("Loyalty Card", 1, ability={"loyalty_remaining": rem, "extra": {"Xmult": 4, "every": 5}})
    state = {"jokers": [loyal], "hand_levels": {"Pair": {"chips": 10, "mult": 2, "level": 1}}, "hands_remaining": 3}
    base, _ = cli.estimate("Pair", [_card("King", "Spades", 1), _card("King", "Hearts", 2)], [], dict(state, jokers=[]))
    est, _ = cli.estimate("Pair", [_card("King", "Spades", 1), _card("King", "Hearts", 2)], [], state)
    assert (est == base * 4) is fires


def test_holo_edition_counts_as_floor():
    d = shop(jokers=[joker("Egg", 1, edition="holo")])
    assert "none of your jokers scores on a plain Pair" not in _out(cli.shop_advise, d)


def test_order_never_hides_ranking_and_ignores_card_trigger_xmult():
    # Photograph is a card-trigger xMult: its position does not change the score
    d = shop(jokers=[joker("Photograph", 1), joker("Jolly Joker", 2)], shop_jokers=[{"index": 1, "name": "Joker", "set": "Joker", "cost": 2}])
    out = _out(cli.shop_advise, d)
    assert "ORDER" not in out and "buy 1" in out
    # a joker-main xMult left of a +mult joker: order note, ranking still printed
    d = shop(jokers=[joker("Cavendish", 1), joker("Jolly Joker", 2, ability={"t_mult": 8, "type": "Pair"})], shop_jokers=[{"index": 1, "name": "Joker", "set": "Joker", "cost": 2}])
    d["hand_levels"] = {"Pair": {"level": 1, "chips": 10, "mult": 2, "played": 3}}
    out = _out(cli.shop_advise, d)
    assert "ORDER FIRST (free): b order 2 1" in out and _advice(out)


def test_owned_hand_gated_joker_sets_main_hand():
    d = shop(jokers=[joker("Clever Joker", 1)])
    assert cli.main_hand(d) == "Two Pair"


def test_type_xmult_off_main_hand_is_conditional():
    cls, score = cli.classify_joker("The Order", 0, "Pair")
    assert "other hand" in cls and score < 60
    assert cli.classify_joker("The Trio", 0, "Full House") == ("XMULT", 100)


def test_chips_joker_ranked_below_mult_joker_without_mult_source():
    d = shop(shop_jokers=[{"index": 1, "name": "Sly Joker", "set": "Joker", "cost": 3},
                          {"index": 2, "name": "Jolly Joker", "set": "Joker", "cost": 3}], money=10, ante=1)
    assert "b buy 2" in _advice(_out(cli.shop_advise, d))


def test_obelisk_resets_on_most_played_hand_and_grows_otherwise():
    obel = joker("Obelisk", 1, ability={"x_mult": 2.0, "extra": 0.2})
    hl = {"Pair": {"chips": 10, "mult": 2, "level": 1, "played": 5}, "Flush": {"chips": 35, "mult": 4, "level": 1, "played": 1}}
    cards = [_card("King", "Spades", 1), _card("King", "Hearts", 2)]
    base, _ = cli.estimate("Pair", cards, [], {"jokers": [], "hand_levels": hl})
    est, _ = cli.estimate("Pair", cards, [], {"jokers": [obel], "hand_levels": hl})
    assert est == base  # Pair is the most played hand: Obelisk resets to x1
    hl2 = dict(hl, Flush=dict(hl["Flush"], played=9))
    est2, _ = cli.estimate("Pair", cards, [], {"jokers": [obel], "hand_levels": hl2})
    assert est2 == int(base * 2.2)


def test_card_sharp_main_hand_is_most_played_pair_family():
    hl = {"Pair": {"played": 9, "level": 1}, "Full House": {"played": 3, "level": 4, "chips": 80, "mult": 8}}
    d = shop(jokers=[joker("Card Sharp", 1)])
    d["hand_levels"] = hl
    assert cli.main_hand(d) == "Pair"


def test_all_face_down_hand_discards_them(monkeypatch):
    hand = [{"index": i, "facing": "back"} for i in range(1, 9)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 2, "money": 5, "hands_remaining": 3, "discards_remaining": 2,
         "hand": hand, "jokers": [], "hand_levels": {}, "blind": {"name": "The House", "boss": True, "chips_needed": 2000, "chips_scored": 0}}
    assert _advice(_out(cli.advise, d)).startswith("ADVICE: DISCARD -> b disc 1 2 3 4 5")
    d["discards_remaining"] = 0
    assert _advice(_out(cli.advise, d)).startswith("ADVICE: PLAY -> b play 1 ")


def test_debuffed_joker_adds_nothing_and_is_shown():
    cards = [_card("King", "Spades", 1), _card("King", "Hearts", 2)]
    hl = {"Pair": {"chips": 10, "mult": 2, "level": 1}}
    base, _ = cli.estimate("Pair", cards, [], {"jokers": [], "hand_levels": hl})
    cav = joker("Cavendish", 1, ability={"x_mult": 3}, debuff=True, edition="polychrome")
    est, notes = cli.estimate("Pair", cards, [], {"jokers": [cav, joker("Blueprint", 2)], "hand_levels": hl})
    assert est == base and any("DEBUFFED" in n for n in notes)
    assert "DEBUFFED" in cli.stickers(cav)


def test_crimson_heart_rerolls_disabled_xmult_with_throwaway():
    hand = [_card("King", "Spades", 1), _card("King", "Hearts", 2), _card("2", "Clubs", 3), _card("7", "Diamonds", 4)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 8, "money": 5, "hands_remaining": 3, "discards_remaining": 0,
         "hand": hand, "hand_levels": {"Pair": {"chips": 10, "mult": 2, "level": 1}},
         "jokers": [joker("Joker", 1), joker("Cavendish", 2, ability={"x_mult": 3}, debuff=True)],
         "blind": {"name": "Crimson Heart", "boss": True, "chips_needed": 150, "chips_scored": 0}}
    adv = _advice(_out(cli.advise, d))
    assert adv.startswith("ADVICE: PLAY -> b play HIGH 3") and "re-rolls" in adv


def test_mouth_and_eye_debuffed_types_score_zero():
    cards = [_card("King", "Spades", 1), _card("King", "Hearts", 2)]
    hl = {"Pair": {"chips": 10, "mult": 2, "level": 1}}
    mouth = {"hand_levels": hl, "jokers": [], "blind": {"name": "The Mouth", "boss": True, "only_hand": "Two Pair"}}
    assert cli.estimate("Pair", cards, [], mouth)[0] == 0
    assert cli.estimate("Pair", cards, [], dict(mouth, blind=dict(mouth["blind"], disabled=True)))[0] > 0
    eye = {"hand_levels": hl, "jokers": [], "blind": {"name": "The Eye", "boss": True, "hands_used": ["Pair"]}}
    assert cli.estimate("Pair", cards, [], eye)[0] == 0


def test_mouth_lock_from_blind_state_steers_advise():
    hand = [_card("King", "Spades", 1), _card("King", "Hearts", 2), _card("3", "Clubs", 3), _card("7", "Diamonds", 4)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 3, "money": 5, "hands_remaining": 2, "discards_remaining": 1,
         "hand": hand, "jokers": [], "hand_levels": {"Pair": {"chips": 10, "mult": 2, "level": 1, "played_this_round": 0}},
         "blind": {"name": "The Mouth", "boss": True, "only_hand": "Two Pair", "chips_needed": 6400, "chips_scored": 100}}
    out = _out(cli.advise, d)
    assert "only Two Pair may be played" in out and _advice(out).startswith("ADVICE: DISCARD")


def test_ramen_and_judgement_valued():
    assert cli.classify_joker("Ramen", 0, "Pair")[0].startswith("XMULT")
    d = shop(jokers=[joker("Joker", 1)], shop_jokers=[{"index": 1, "name": "Judgement", "set": "Tarot", "cost": 3}], money=8, ante=1)
    assert "buyuse 1" in _advice(_out(cli.shop_advise, d))


def test_mouth_locked_high_card_is_playable():
    hand = [_card("King", "Spades", 1), _card("Queen", "Hearts", 2), _card("7", "Hearts", 3), _card("4", "Clubs", 4), _card("3", "Clubs", 5)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 3, "money": 5, "hands_remaining": 2, "discards_remaining": 0,
         "hand": hand, "jokers": [], "hand_levels": {"High Card": {"chips": 5, "mult": 1, "level": 1}},
         "blind": {"name": "The Mouth", "boss": True, "only_hand": "High Card", "chips_needed": 6400, "chips_scored": 100}}
    adv = _advice(_out(cli.advise, d))
    assert "NO VALID PLAY" not in adv and "b play HIGH 1" in adv


def test_order_ignores_chips_jokers():
    d = shop(jokers=[joker("Cavendish", 1), joker("Sly Joker", 2)], shop_jokers=[{"index": 1, "name": "Joker", "set": "Joker", "cost": 2}])
    assert "ORDER" not in _out(cli.shop_advise, d)


def test_rental_money_joker_penalised():
    d = shop(jokers=[joker("Joker", 1), joker("Jolly Joker", 2)], shop_jokers=[{"index": 1, "name": "Egg", "set": "Joker", "cost": 1, "rental": True}], money=8)
    assert "net ~$0" in _out(cli.shop_advise, d)


def test_debuffed_club_does_not_count_for_suits():
    club = dict(_card("King", "Clubs", 1), debuff=True)
    assert "C" not in cli._suit_cover([club, _card("King", "Hearts", 2)], [])


def test_main_mult_source_is_never_dead_weight():
    # Gros Michel is AVOID-class but the only mult source: its real share of the est keeps it
    owned = [joker("Gros Michel", 1, ability={"extra": {"mult": 15}})] + [joker("Egg", i) for i in range(2, 7)]
    d = shop(jokers=owned, ante=5, money=6)
    d["hand_levels"] = {"Pair": {"chips": 10, "mult": 2, "level": 1, "played": 9}}
    assert cli.joker_share(d, owned[0], "Pair") > 0.5
    assert "b sell 1 " not in _out(cli.shop_advise, d)


def test_blackboard_plays_red_fillers():
    hand = [_card("King", "Spades", 1), _card("King", "Clubs", 2), _card("3", "Hearts", 3), _card("9", "Spades", 4),
            _card("5", "Diamonds", 5), _card("7", "Clubs", 6)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 2, "money": 5, "hands_remaining": 3, "discards_remaining": 0,
         "hand": hand, "jokers": [joker("Blackboard", 1)], "hand_levels": {"Pair": {"chips": 10, "mult": 2, "level": 1}},
         "blind": {"name": "Big Blind", "boss": False, "chips_needed": 100, "chips_scored": 0}}
    adv = _advice(_out(cli.advise, d))
    played = adv.split("b play PAIR ")[1].split("   ")[0].split()
    assert {"3", "5"} <= set(played)


def test_joker_stencil_scored_by_empty_slots():
    d = shop(jokers=[joker("Joker", 1)], shop_jokers=[{"index": 1, "name": "Joker Stencil", "set": "Joker", "cost": 8}], money=10, ante=3)
    assert "Stencil: x5 now" in _out(cli.shop_advise, d)


def test_six_flushes_make_flush_the_main_hand():
    d = shop(ante=2)
    d["hand_levels"] = {"Flush": {"played": 6, "level": 1}, "Pair": {"played": 1, "level": 1}}
    assert cli.main_hand(d) == "Flush"


def test_spectral_pack_advice_with_target():
    hand = [_card("King", "Spades", 1), _card("King", "Hearts", 2), _card("4", "Clubs", 3)]
    d = {"phase": "PACK_OPENING", "stake": 8, "ante": 3, "money": 5, "joker_slots": 6, "jokers": [joker("Joker", 1)], "hand": hand,
         "hand_levels": {}, "pack": {"kind": "Spectral", "choices_remaining": 1,
                                     "cards": [{"name": "Sigil", "set": "Spectral"}, {"name": "Aura", "set": "Spectral"}]}}
    assert _advice(_out(cli.pack_advise, d)).startswith("ADVICE: PICK -> b pick 2 1")


def test_no_reroll_without_20_dollars_left():
    d = shop(jokers=[joker("Joker", 1), joker("Jolly Joker", 2)], money=15, ante=3)
    assert "REROLL" not in _advice(_out(cli.shop_advise, d))


def test_arcana_pack_respects_8_dollar_floor():
    d = shop(jokers=[joker("Joker", 1), joker("Jolly Joker", 2)], money=10, ante=3,
             boosters=[{"index": 1, "name": "Arcana Pack", "set": "Booster", "cost": 4}])
    d["blind_select"]["choices"]["Small"]["chips"] = 100  # comfortable next blind: the floor holds (TIGHT lifts it)
    d["hand_levels"] = {"Pair": {"level": 1, "chips": 10, "mult": 2, "played": 3}}
    assert "pack 1" not in _advice(_out(cli.shop_advise, d))


def test_flat_rental_sold_when_two_others_carry():
    owned = [joker("Joker", 1), joker("Jolly Joker", 2), joker("Zany Joker", 3, rental=True)]
    d = shop(jokers=owned, money=10, ante=3)
    out = _out(cli.shop_advise, d)
    assert _advice(out).startswith("ADVICE: SELL FIRST -> b sell 3") and "Shop advisor:" in out  # ranking printed too


def test_gros_michel_bought_as_only_mult_source():
    d = shop(jokers=[joker("Sly Joker", 1)], shop_jokers=[{"index": 1, "name": "Gros Michel", "set": "Joker", "cost": 5, "ability": {"extra": {"mult": 15}}}], money=8, ante=2)
    out = _out(cli.shop_advise, d)
    assert "AVOID" not in out.split("Gros Michel")[1][:80] and "b buy 1" in _advice(out)


def test_sly_fires_on_flush_with_a_pair():
    flush = [_card("Jack", "Diamonds", 1), _card("10", "Diamonds", 2), _card("10", "Diamonds", 3), _card("5", "Diamonds", 4), _card("4", "Diamonds", 5)]
    hl = {"Flush": {"chips": 35, "mult": 4, "level": 1}}
    sly = joker("Sly Joker", 1, ability={"t_chips": 50, "type": "Pair"})
    base, _ = cli.estimate("Flush", flush, [], {"jokers": [], "hand_levels": hl})
    est, _ = cli.estimate("Flush", flush, [], {"jokers": [sly], "hand_levels": hl})
    assert est == base + 50 * 4


def test_steel_queen_x15_before_its_own_shoot_the_moon():
    pair = [_card("2", "Spades", 1), _card("2", "Hearts", 2)]
    held = [dict(_card("Queen", "Spades", 3), enhancement="m_steel")]
    hl = {"Pair": {"chips": 10, "mult": 2, "level": 1}}
    est, _ = cli.estimate("Pair", pair, held, {"jokers": [joker("Shoot the Moon", 1)], "hand_levels": hl})
    assert est == int((10 + 4) * (2 * 1.5 + 13))


# --- regressions on recorded Gold observations (fixtures/advisor/*.json; source trajectory + step in each file) ---------
import json
import pathlib

FIX = pathlib.Path(__file__).parent / "fixtures" / "advisor"


def _fixture(name):
    rec = json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))
    cli.LEGAL = rec.get("legal") or {}
    return rec["obs"]


def test_rec_ante1_zero_jokers_buys_gluttonous_over_buffoon():
    # 7805_XURWZ2L2: advice ranked the Buffoon pack 78 over Gluttonous 26 with 0 jokers; the run lost the ante-1 Big
    adv = _advice(_out(cli.shop_advise, _fixture("gold_ante1_shop_gluttonous_vs_buffoon")))
    assert "Gluttonous Joker" in adv and "b buy" in adv


def test_rec_pack_with_no_jokers_never_skips_scorers():
    # 7801_XDLNJ8SC: Buffoon pack with 0 jokers owned and two stickered scorers
    adv = _advice(_out(cli.pack_advise, _fixture("gold_pack_half_joker_no_jokers")))
    assert adv.startswith("ADVICE: PICK")


def test_rec_celestial_picks_pair_family_planet():
    # 7801_1QAUCRHI: Jumbo Celestial without the main planet: Uranus (Two Pair), never Saturn/Neptune
    adv = _advice(_out(cli.pack_advise, _fixture("gold_celestial_uranus_pair_main")))
    assert "Uranus" in adv


def test_rec_mega_buffoon_half_joker_not_buried():
    # 7801_TIEL478W: perishable+rental Half Joker was ranked -75 in a pack (already paid for, 2 free slots)
    out = _out(cli.pack_advise, _fixture("gold_mega_buffoon_half_joker_4_jokers"))
    half = next(line for line in out.splitlines() if "Half Joker" in line and "pick" in line)
    assert int(half.split()[0]) >= 15 and _advice(out).startswith("ADVICE: PICK")


def test_never_leave_with_affordable_scorer_when_under_scaled():
    # 7810: EMERGENCY flagged, Half Joker (perishable, rental) ranked 28 and the ADVICE was LEAVE
    half = {"index": 1, "name": "Half Joker", "set": "Joker", "cost": 1, "perishable": True, "perish_tally": 5, "rental": True}
    d = shop(jokers=[joker("Egg", 1)], shop_jokers=[half], money=6, ante=3)
    assert "LEAVE" not in _advice(_out(cli.shop_advise, d))


def test_pace_rule_discards_when_hands_cannot_clear():
    # 7810: jokerless 300 with 3 hands, Two Pair est ~84: banking it lost 216/300; discard toward a bigger hand first
    hand = [_card("King", "Spades", 1), _card("King", "Hearts", 2), _card("4", "Clubs", 3), _card("4", "Diamonds", 4),
            _card("9", "Spades", 5), _card("7", "Hearts", 6), _card("3", "Clubs", 7), _card("2", "Diamonds", 8)]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 1, "money": 4, "hands_remaining": 3, "discards_remaining": 2,
         "hand": hand, "jokers": [], "hand_levels": {"Two Pair": {"chips": 20, "mult": 2, "level": 1}, "Pair": {"chips": 10, "mult": 2, "level": 1}},
         "blind": {"name": "Small Blind", "boss": False, "chips_needed": 300, "chips_scored": 0}}
    assert _advice(_out(cli.advise, d)).startswith("ADVICE: DISCARD")


def test_main_hand_pair_over_leveled_two_pair():
    # 7803: ten Pair plays (with Half Joker owned) vs three Two Pair plays must stay Pair even with Two Pair leveled higher
    d = shop(jokers=[joker("Half Joker", 1)])
    d["hand_levels"] = {"Pair": {"played": 10, "level": 2, "chips": 25, "mult": 3}, "Two Pair": {"played": 3, "level": 4, "chips": 80, "mult": 5}}
    assert cli.main_hand(d) == "Pair"


def test_order_note_moves_mult_left_of_xmult():
    # `b order` lists old positions in their new order: +mult jokers must come first (left of the xMult)
    d = shop(jokers=[joker("Cavendish", 1), joker("Joker", 2, ability={"mult": 4}), joker("Jolly Joker", 3, ability={"t_mult": 8, "type": "Pair"})], shop_jokers=[], money=4)
    d["hand_levels"] = {"Pair": {"level": 1, "chips": 10, "mult": 2, "played": 3}}
    line = next(l for l in _out(cli.shop_advise, d).splitlines() if "ORDER FIRST" in l)
    order = [int(x) for x in line.split("b order ")[1].split("   ")[0].split()]
    assert order[-1] == 1 and set(order[:2]) == {2, 3}


def test_erosion_with_full_deck_is_not_a_scorer():
    d = shop(shop_jokers=[{"index": 1, "name": "Erosion", "set": "Joker", "cost": 1, "eternal": True, "rental": True}], money=8, ante=1)
    d["deck"] = {"cards": [{"rank": "2", "suit": "Spades", "remaining": True}] * 52}
    out = _out(cli.shop_advise, d)
    assert "NEEDED NOW" not in out and "adds ~0 now" in out


def test_scorer_outranks_utility_with_no_scorers_ante1():
    # 7805: Astronomer (75) outranked Walkie Talkie (45) in a pack with 0 scorers; the ante-1 Big was lost 444/450
    d = {"phase": "PACK_OPENING", "stake": 8, "ante": 1, "money": 2, "joker_slots": 6, "jokers": [], "hand": [], "hand_levels": {},
         "pack": {"kind": "Buffoon", "choices_remaining": 1, "cards": [{"name": "Astronomer", "set": "Joker"}, {"name": "Walkie Talkie", "set": "Joker"}]}}
    assert _advice(_out(cli.pack_advise, d)).startswith("ADVICE: PICK -> b pick 2")
    s = shop(shop_jokers=[{"index": 1, "name": "Astronomer", "set": "Joker", "cost": 8}, {"index": 2, "name": "Walkie Talkie", "set": "Joker", "cost": 4}], money=10, ante=1)
    assert "b buy 2" in _advice(_out(cli.shop_advise, s))


def test_order_keeps_holo_xmult_with_xmults():
    # 7803: [Clever, Joker, Supernova, Tribe(holo), Summit] got `order 2 3 4 5 1`, leaving Summit right of the Tribe
    owned = [joker("Clever Joker", 1), joker("Joker", 2), joker("Supernova", 3), joker("The Tribe", 4, edition="holo"), joker("Mystic Summit", 5)]
    d = shop(jokers=owned, money=4)
    d["hand_levels"] = {"Flush": {"played": 6, "level": 2}}
    line = next(l for l in _out(cli.shop_advise, d).splitlines() if "ORDER FIRST" in l)
    order = [int(x) for x in line.split("b order ")[1].split("   ")[0].split()]
    assert order[-1] == 4 and order.index(5) < order.index(4)


def test_photograph_not_counted_as_xmult_target():
    d = shop(jokers=[joker("Photograph", 1), joker("Jolly Joker", 2)], money=4, ante=3)
    assert "GOLD CHECK: 0 reliable/growth xMult" in _out(cli.shop_advise, d)


def test_main_hand_two_pair_with_clever_and_big_two_pair_plays():
    # 7809: Clever owned, big plays Two Pair/Full House, a few Pairs -> Two Pair, not Pair
    d = shop(jokers=[joker("Clever Joker", 1, ability={"t_chips": 80, "type": "Two Pair"})])
    d["hand_levels"] = {"Pair": {"played": 4, "level": 1, "chips": 10, "mult": 2}, "Two Pair": {"played": 5, "level": 1, "chips": 20, "mult": 2},
                        "Full House": {"played": 2, "level": 1, "chips": 40, "mult": 4}}
    assert cli.main_hand(d) == "Two Pair"


def test_no_reroll_into_unpaid_rent():
    # two rentals = $6 due at round end: a $5 reroll from $8 would push the run negative
    d = shop(jokers=[joker("Joker", 1, rental=True, perishable=True, perish_tally=4), joker("Jolly Joker", 2, rental=True, perishable=True, perish_tally=4)],
             money=8, ante=1)
    assert "REROLL" not in _advice(_out(cli.shop_advise, d))


def test_boss_prep_eye_vs_card_sharp_buys_counter():
    # 7802 died at ante 7 to The Eye with a Card Sharp repeat engine: a counter in the shop must come first
    d = shop(jokers=[joker("Card Sharp", 1), joker("Jolly Joker", 2)], shop_jokers=[{"index": 1, "name": "Luchador", "set": "Joker", "cost": 5}], money=12, ante=6)
    d["blind_select"]["choices"]["Boss"] = {"name": "The Eye", "chips": 120000, "state": "Upcoming"}
    out = _out(cli.shop_advise, d)
    assert "BOSS PREP: The Eye" in out and "b buy 1" in _advice(out)


_RANK = __import__("re").compile(r"^\s{1,4}(\d{1,3}) ((?:buy|buyuse|pack|vouch) \d+)\s+(.*)$")


def _ranking_violation(out):
    """None when the ADVICE is the top ranked option or every option ranked above it is listed with a reason."""
    lines = out.splitlines()
    adv = next((ln for ln in lines if ln.startswith("ADVICE")), "")
    notes = " ".join(ln for ln in lines if "passed over" in ln or "cannot afford" in ln)
    for ln in lines:
        m = _RANK.match(ln)
        if not m:
            continue
        if f"b {m[2]} " in adv + " ":
            return None
        name = m[3].split(" [")[0].split(" -> ")[-1]
        if int(m[1]) >= 30 and "[AVOID" not in m[3] and name not in notes:
            return f"{m[2]} {name} ranked above {adv!r} without a reason"
    return None


@pytest.mark.parametrize("d", [
    shop(jokers=[joker("Joker", 1)], shop_jokers=[{"index": 1, "name": "Clever Joker", "set": "Joker", "cost": 4}],
         boosters=[{"index": 1, "name": "Buffoon Pack", "cost": 4}], money=9, ante=2),
    shop(jokers=[joker("Joker", 1)], shop_jokers=[{"index": 1, "name": "Ice Cream", "set": "Joker", "cost": 5}], money=7, ante=1),
    shop(jokers=[joker("Joker", 1), joker("Jolly Joker", 2)], shop_jokers=[{"index": 1, "name": "Cavendish", "set": "Joker", "cost": 4}], money=6, ante=3),
] + [p.stem for p in sorted(FIX.glob("*.json")) if json.loads(p.read_text(encoding="utf-8"))["obs"].get("phase") == "SHOP"])
def test_advice_follows_printed_ranking(d):
    assert _ranking_violation(_out(cli.shop_advise, _fixture(d) if isinstance(d, str) else d)) is None


def test_score_check_counts_summit_and_acrobat():
    # 7809/7803: EMERGENCY fired every shop because SCORE CHECK left out Mystic Summit / Acrobat
    base = shop(jokers=[joker("Joker", 1)], ante=3)
    full = shop(jokers=[joker("Joker", 1), joker("Mystic Summit", 2), joker("Acrobat", 3)], ante=3)
    num = lambda out: int(out.split("SCORE CHECK: best")[1].split("~")[1].split()[0])
    assert num(_out(cli.shop_advise, full)) > 3 * num(_out(cli.shop_advise, base))


def test_advise_shows_solver_and_keeps_one_advice_line():
    hand = [{"index": i + 1, "rank": r, "suit": s} for i, (r, s) in enumerate(
        [("King", "Spades"), ("King", "Hearts"), ("9", "Clubs"), ("7", "Diamonds"), ("5", "Spades"), ("4", "Hearts"), ("3", "Clubs"), ("2", "Diamonds")])]
    d = {"phase": "SELECTING_HAND", "stake": 8, "ante": 1, "hands_remaining": 4, "discards_remaining": 3, "hand_size": 8,
         "hand": hand, "jokers": [joker("Joker", 1)], "hand_levels": {}, "deck": {"cards": []},
         "blind": {"name": "Small Blind", "boss": False, "chips_needed": 300, "chips_scored": 0}}
    out = _out(cli.advise, d)
    assert sum(1 for ln in out.splitlines() if ln.startswith("ADVICE")) == 1
    assert "SOLVER " in out or "solver unavailable" not in out


def _boss(d, name, chips):
    d["blind_select"]["choices"]["Boss"] = {"name": name, "chips": chips, "state": "Upcoming"}
    return d


def test_boss_prep_facts_from_blind_lua():
    # The Mouth locks one type (Card Sharp wants repeats: compatible); The Water sets discards to 0 (Summit always on)
    sharp = [joker("Card Sharp", 1), joker("Jolly Joker", 2)]
    assert "BOSS PREP" not in _out(cli.shop_advise, _boss(shop(jokers=sharp, ante=6, money=12), "The Mouth", 120000))
    assert "BOSS PREP: The Eye" in _out(cli.shop_advise, _boss(shop(jokers=sharp, ante=6, money=12), "The Eye", 120000))
    out = _out(cli.shop_advise, _boss(shop(jokers=[joker("Mystic Summit", 1), joker("Jolly Joker", 2)], ante=3, money=12), "The Water", 12800))
    assert "Mystic Summit" not in "".join(ln for ln in out.splitlines() if "BOSS" in ln or "crippl" in ln.lower())


def test_summit_counts_in_joker_share():
    d = shop(jokers=[joker("Mystic Summit", 1), joker("Joker", 2)], ante=3)
    d["discards_remaining"] = 3
    assert cli.joker_share(d, d["jokers"][0], "Pair") >= 0.2


def test_tight_blind_suspends_money_floor():
    # 7805: $12 before a boss it could barely beat, LEAVE for the $10 floor, lost by 132
    d = _boss(shop(jokers=[joker("Joker", 1)], ante=5, money=12, boosters=[{"index": 1, "name": "Arcana Pack", "cost": 4}]), "The Wheel", 50000)
    d["blind_select"]["choices"]["Small"] = {"name": "Small Blind", "chips": 25000, "state": "Defeated"}
    d["blind_select"]["choices"]["Big"] = {"name": "Big Blind", "chips": 37500, "state": "Defeated"}
    out = _out(cli.shop_advise, d)
    assert "TIGHT" in out and "LEAVE" not in _advice(out)


def test_pack_ties_break_on_marginal_est():
    # 7805: Eternal Hanging Chad and Eternal Scary Face both 90, slot order picked Chad; Scary adds far more to KK
    d = {"phase": "PACK_OPENING", "stake": 8, "ante": 1, "money": 4, "joker_slots": 5, "jokers": [], "hand": [], "hand_levels": {},
         "hands_per_round": 4, "pack": {"kind": "Buffoon", "choices_remaining": 1, "cards": [
             {"name": "Hanging Chad", "set": "Joker", "eternal": True}, {"name": "Scary Face", "set": "Joker", "eternal": True}]}}
    assert _advice(_out(cli.pack_advise, d)).startswith("ADVICE: PICK -> b pick 2")


def test_half_joker_anchors_main_hand_over_more_straights():
    # 7809: 6 Straights vs 4 Pairs + 1 Two Pair with Half Joker (<=3 cards) owned: the main hand is Pair
    d = shop(jokers=[joker("Half Joker", 1), joker("Supernova", 2)], ante=3)
    d["hand_levels"] = {"Pair": {"played": 4, "level": 1, "chips": 10, "mult": 2}, "Two Pair": {"played": 1, "level": 1, "chips": 20, "mult": 2},
                        "Straight": {"played": 6, "level": 1, "chips": 30, "mult": 4}}
    assert cli.main_hand(d) == "Pair"


def test_pack_erosion_on_full_deck_is_not_a_bridge():
    # 7809: Erosion ranked 90 with a 52-card deck (it adds 0)
    deck = {"cards": [{"rank": r, "suit": s} for r in ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")
                      for s in ("Spades", "Hearts", "Clubs", "Diamonds")]}
    d = {"phase": "PACK_OPENING", "stake": 8, "ante": 1, "money": 4, "joker_slots": 5, "jokers": [], "hand": [], "deck": deck,
         "hand_levels": {"Pair": {"level": 1, "chips": 10, "mult": 2}}, "hands_per_round": 4,
         "pack": {"kind": "Buffoon", "choices_remaining": 1, "cards": [{"name": "Erosion", "set": "Joker"}, {"name": "Jolly Joker", "set": "Joker"}]}}
    assert _advice(_out(cli.pack_advise, d)).startswith("ADVICE: PICK -> b pick 2")


def _hand_state(cards, jokers=(), need=300, hands=3, discards=0, ante=1):
    hand = [{"index": i + 1, "rank": r, "suit": s} for i, (r, s) in enumerate(cards)]
    return {"phase": "SELECTING_HAND", "stake": 8, "ante": ante, "hands_remaining": hands, "discards_remaining": discards, "hand_size": 8,
            "hand": hand, "jokers": list(jokers), "hand_levels": {"Pair": {"level": 1, "chips": 10, "mult": 2}, "Two Pair": {"level": 1, "chips": 20, "mult": 2}},
            "deck": {"cards": []}, "blind": {"name": "Small Blind", "boss": False, "chips_needed": need, "chips_scored": 0}}


def test_fillers_never_break_a_held_pair():
    # 7801: `play TWOPAIR 1 2 5 6 7` spent 2S while 22 was the pair the next hand needed
    d = _hand_state([("King", "Spades"), ("King", "Hearts"), ("Queen", "Clubs"), ("Queen", "Diamonds"), ("2", "Spades"), ("2", "Hearts"), ("7", "Clubs"), ("5", "Diamonds")],
                    need=5000, hands=3)
    adv = cli._advise_rules
    out = _out(adv, d)
    a = _advice(out)
    if "b play" in a:
        played = a.split("b play ")[1].split("   ")[0].split()
        assert not ({"5", "6"} & set(played) and not {"5", "6"} <= set(played))


def test_square_joker_plays_exactly_four():
    d = _hand_state([("King", "Spades"), ("King", "Hearts"), ("Queen", "Clubs"), ("Queen", "Diamonds"), ("9", "Spades"), ("7", "Hearts"), ("4", "Clubs"), ("3", "Diamonds")],
                    jokers=[joker("Square Joker", 1)], need=50, hands=3)
    a = _advice(_out(cli._advise_rules, d))
    assert "b play TWOPAIR" in a and len([x for x in a.split("b play TWOPAIR ")[1].split("   ")[0].split() if x.isdigit()]) == 4


def test_two_rentals_never_sell_the_only_xmult():
    # 7807: ante 5, two rentals -> advised selling Acrobat (the only xMult) instead of decaying Popcorn
    d = shop(jokers=[joker("Acrobat", 1, rental=True), joker("Popcorn", 2, rental=True), joker("Jolly Joker", 3), joker("Joker", 4)], ante=5, money=12)
    a = _advice(_out(cli.shop_advise, d))
    assert "b sell 1" not in a


def test_type_xmult_rental_is_not_flat():
    # 7805: The Trio{RENTAL} called a "flat rental" and sold
    d = shop(jokers=[joker("The Trio", 1, rental=True), joker("Jolly Joker", 2), joker("Joker", 3)], ante=3, money=12)
    assert "b sell 1" not in _advice(_out(cli.shop_advise, d))


def test_shoot_the_moon_queen_kept_on_discard():
    d = _hand_state([("Queen", "Spades"), ("9", "Hearts"), ("7", "Clubs"), ("5", "Diamonds"), ("4", "Spades"), ("3", "Hearts"), ("2", "Clubs"), ("8", "Diamonds")],
                    jokers=[joker("Shoot the Moon", 1)], need=2000, hands=3, discards=3)
    a = _advice(_out(cli._advise_rules, d))
    if "b disc" in a:
        assert "1" not in a.split("b disc ")[1].split("   ")[0].split()


def test_mark_face_down_held_cards_count_for_shoot_the_moon():
    d = _hand_state([("King", "Spades"), ("King", "Hearts")], jokers=[joker("Shoot the Moon", 1)], need=2000)
    d["hand"] += [{"index": 3, "facing": "back"}, {"index": 4, "facing": "back"}]
    base = cli.estimate("Pair", d["hand"][:2], d["hand"][2:], dict(d, blind={"name": "Small Blind"}))[0]
    mark = cli.estimate("Pair", d["hand"][:2], d["hand"][2:], dict(d, blind={"name": "The Mark", "boss": True}))[0]
    assert mark > base


def test_half_joker_rental_not_sold_when_it_carries():
    # 7803: told to sell Half Joker{RENTAL} as a flat rental though it gave +20 of ~22 mult
    deck = {"cards": [{"rank": r, "suit": s} for r in ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")
                      for s in ("Spades", "Hearts", "Clubs", "Diamonds")]}
    d = shop(jokers=[joker("Half Joker", 1, rental=True), joker("Joker", 2), joker("Sly Joker", 3), joker("Jolly Joker", 4, rental=True)], ante=3, money=10)
    d["deck"] = deck
    d["hand_levels"] = {"Pair": {"level": 2, "chips": 25, "mult": 3, "played": 6}, "Two Pair": {"level": 1, "chips": 20, "mult": 2, "played": 2}}
    assert "b sell 1" not in _advice(_out(cli.shop_advise, d))


def test_high_card_always_listed():
    d = _hand_state([("King", "Spades"), ("7", "Hearts"), ("7", "Clubs"), ("5", "Diamonds"), ("4", "Spades")],
                    jokers=[joker("Half Joker", 1), joker("Hanging Chad", 2)], need=5000)
    assert "HIGH CARD" in _out(cli.show_hands, d)


def test_amber_acorn_uses_cached_jokers_and_probes(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "CACHE_DIR", str(tmp_path))
    face_up = [joker("Joker", 1), joker("Cavendish", 2, ability={"extra": 3})]
    d_shop = shop(jokers=face_up)
    cli._with_known_jokers(d_shop)  # face-up: cached
    d = _hand_state([("King", "Spades"), ("King", "Hearts"), ("9", "Clubs"), ("7", "Diamonds"), ("5", "Spades"), ("4", "Hearts"), ("3", "Clubs"), ("2", "Diamonds")],
                    need=300, hands=4)
    d["jokers"] = [{"index": 1, "facing": "back"}, {"index": 2, "facing": "back"}]
    d["blind"] = {"name": "Amber Acorn", "boss": True, "chips_needed": 300, "chips_scored": 0}
    d2 = cli._with_known_jokers(d)
    assert d2.get("_jokers_cached") and [j["name"] for j in d2["jokers"]] == ["Joker", "Cavendish"]
    out = _out(cli._advise_rules, d2)
    assert "AMBER ACORN" in out


def test_summit_valued_with_discards_burned():
    d = shop(jokers=[joker("Mystic Summit", 1), joker("Joker", 2)], ante=3)
    d["hand_levels"] = {"Pair": {"level": 2, "chips": 25, "mult": 3, "played": 5}}
    assert cli.joker_share(d, d["jokers"][0], "Pair") >= 0.4


def test_steel_card_never_a_filler():
    d = _hand_state([("King", "Spades"), ("King", "Hearts"), ("9", "Clubs"), ("7", "Diamonds"), ("5", "Spades"), ("4", "Hearts"), ("3", "Clubs"), ("2", "Diamonds")],
                    need=50, hands=3)
    d["hand"][7]["enhancement"] = "Steel Card"
    a = _advice(_out(cli._advise_rules, d))
    if "b play" in a:
        assert "8" not in a.split("b play ")[1].split("   ")[0].split()[1:]


def test_eternal_rental_never_needed_now():
    # 7807 (first Gold win): Raised Fist{ETERNAL,RENTAL} ranked BUY at ante 1 (-$66 unsellable rent)
    d = shop(jokers=[joker("Clever Joker", 1)], shop_jokers=[{"index": 1, "name": "Raised Fist", "set": "Joker", "cost": 1, "eternal": True, "rental": True}], money=6, ante=1)
    assert "b buy 1" not in _advice(_out(cli.shop_advise, d))


def test_obelisk_is_a_growth_xmult():
    cls, sc = cli.classify_joker("Obelisk", 0, "Pair")
    assert cls.startswith("XMULT(growth") and sc >= 55


def test_abstract_counts_disabled_jokers():
    s = {"jokers": [joker("Abstract Joker", 1), joker("Joker", 2, debuff=True)], "hand_levels": {"Pair": {"level": 1, "chips": 10, "mult": 2}}}
    kk = [_card("King", "Spades", 1), _card("King", "Hearts", 2)]
    assert cli.estimate("Pair", kk, [], s)[0] == (10 + 20) * (2 + 6)


def test_throwback_skips_big_with_margin():
    d = blind_select("tag_garbage", jokers=[joker("Throwback", 1), joker("Stuntman", 2)], ante=5)
    d["blind_select"]["on_deck"] = "Big"
    d["blind_select"]["choices"]["Boss"]["chips"] = 10
    d["hands_per_round"] = 3
    assert "ADVICE: b skip" in _out(cli.show, d)


def test_main_hand_invariant_twice_the_plays():
    # 7809: 'Flush' from ante 3 despite ~14 Pair plays at Pair L10
    d = shop(jokers=[joker("Droll Joker", 1)], ante=4)
    d["hand_levels"] = {"Pair": {"played": 14, "level": 10, "chips": 100, "mult": 20}, "Flush": {"played": 6, "level": 2, "chips": 50, "mult": 6}}
    assert cli.main_hand(d) == "Pair"


def test_main_hand_prefers_much_higher_level():
    d = shop(ante=4)
    d["hand_levels"] = {"Pair": {"played": 6, "level": 7, "chips": 70, "mult": 14}, "Two Pair": {"played": 5, "level": 2, "chips": 40, "mult": 3}}
    assert cli.main_hand(d) == "Pair"


def test_thin_margin_takes_biggest_clearing_hand():
    # 7810 The Eye last hand: Two Pair 5874 (main hand) vs need 5350 was advised over a Full House 10036
    d = _hand_state([("King", "Spades"), ("King", "Hearts"), ("King", "Clubs"), ("9", "Diamonds"), ("9", "Spades"), ("4", "Hearts"), ("3", "Clubs"), ("2", "Diamonds")],
                    need=370, hands=1)
    d["hand_levels"] = {"Two Pair": {"level": 3, "chips": 60, "mult": 4, "played": 9}, "Full House": {"level": 2, "chips": 65, "mult": 6, "played": 1},
                        "Pair": {"level": 1, "chips": 10, "mult": 2}, "Three of a Kind": {"level": 1, "chips": 30, "mult": 3}}
    a = _advice(_out(cli._advise_rules, d))
    assert "FULL" in a or "b play 1 2 3 4 5" in a


def test_main_hand_hysteresis_keeps_previous_until_two_shops():
    d = shop(jokers=[joker("Mad Joker", 1, ability={"t_mult": 10, "type": "Two Pair"})], ante=3)
    d["hand_levels"] = {"Pair": {"played": 5, "level": 2, "chips": 15, "mult": 3}, "Two Pair": {"played": 4, "level": 2, "chips": 30, "mult": 3}}
    raw = cli._main_hand_raw(dict(d))
    other = "Pair" if raw == "Two Pair" else "Two Pair"
    d["_mh_hyst"] = {"mh": other}
    assert cli.main_hand(d) == other  # remembered main hand kept
    d["_mh_hyst"] = {"mh": other, "pend": raw, "n": 2}
    assert cli.main_hand(d) == raw


def test_sim_veto_covers_needed_now(monkeypatch):
    # 7810: Banner{ETERNAL} 'NEEDED NOW' advised although its own SIM was 0.71 vs baseline 0.72
    d = shop(jokers=[], shop_jokers=[{"index": 1, "name": "Banner", "set": "Joker", "cost": 5, "eternal": True}], money=8, ante=1)
    d["hand_levels"] = {"Pair": {"level": 1, "chips": 10, "mult": 2}}

    class FakeSim:
        def options_from_state(self, st):
            return [{"label": "baseline (buy nothing)"}, {"label": "buy Banner $5", "add_joker": st["shop"]["jokers"][0], "cost": 5}]

        def value_options(self, st, opts, **kw):
            return [{"label": "baseline (buy nothing)", "option": opts[0], "feasible": True, "p_next": 0.72, "delta": 0.0, "money_after": 8},
                    {"label": "buy Banner $5", "option": opts[1], "feasible": True, "p_next": 0.71, "delta": -0.01, "money_after": 3}]
    monkeypatch.setattr(cli, "_SHOP_SIM", FakeSim())
    rules = _advice(_out(cli.shop_advise, d))
    out = _out(cli.shop_advise_sim, d)
    assert "b buy 1" in rules
    assert "SIM" in _advice(out) and "b buy 1" not in _advice(out)


def test_sim_primary_picks_sim_best_joker(monkeypatch):
    # orchestrator 06:4x: SIM is primary for jokers (Mad Joker rule 0 vs SIM +0.21)
    d = shop(jokers=[joker("Joker", 1)], shop_jokers=[{"index": 1, "name": "Mad Joker", "set": "Joker", "cost": 4},
                                                      {"index": 2, "name": "Jolly Joker", "set": "Joker", "cost": 3}], money=20, ante=3)
    d["hand_levels"] = {"Pair": {"level": 1, "chips": 10, "mult": 2}}

    class FakeSim:
        def options_from_state(self, st):
            sj = st["shop"]["jokers"]
            return [{"label": "baseline (buy nothing)"}, {"label": "buy Mad Joker $4", "add_joker": sj[0], "cost": 4}, {"label": "buy Jolly Joker $3", "add_joker": sj[1], "cost": 3}]

        def value_options(self, st, opts, **kw):
            return [{"label": opts[0]["label"], "option": opts[0], "feasible": True, "p_next": 0.50, "delta": 0.0, "money_after": 20},
                    {"label": opts[1]["label"], "option": opts[1], "feasible": True, "p_next": 0.71, "delta": 0.21, "money_after": 16},
                    {"label": opts[2]["label"], "option": opts[2], "feasible": True, "p_next": 0.55, "delta": 0.05, "money_after": 17}]
    monkeypatch.setattr(cli, "_SHOP_SIM", FakeSim())
    assert "b buy 1" in _advice(_out(cli.shop_advise_sim, d))
