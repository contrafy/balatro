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


def blind_select(tag, jokers=(), ante=1):
    return {"phase": "BLIND_SELECT", "stake": 8, "ante": ante, "money": 4, "joker_slots": 6, "jokers": list(jokers),
            "blind_select": {"on_deck": "Small", "choices": {"Small": {"name": "Small Blind", "chips": 300, "state": "Select", "tag": tag, "tag_key": tag},
                                                             "Big": {"name": "Big Blind", "chips": 450, "state": "Upcoming"},
                                                             "Boss": {"name": "The Hook", "chips": 600, "state": "Upcoming"}}}}


def test_stickers_display():
    assert cli.stickers(joker("Joker", 1, eternal=True, rental=True)) == "{ETERNAL,RENTAL(-$3/round)}"
    assert "PERISHED" in cli.stickers(joker("Joker", 1, perishable=True, perish_tally=0))
    assert cli.stickers(joker("Joker", 1, perishable=True, perish_tally=3)) == "{PERISHABLE(3 rounds left)}"


def test_dead_perishable_is_sold_first():
    d = shop(jokers=[joker("Jolly Joker", 1), joker("Sly Joker", 2, perishable=True, perish_tally=0)])
    assert _advice(_out(cli.shop_advise, d)).startswith("ADVICE: SELL -> b sell 2")


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


@pytest.mark.parametrize("tag,jokers,ante,expect", [
    ("tag_rare", [], 1, "b blind"),            # pays in the next shop, after the Big Blind
    ("tag_polychrome", [], 1, "b blind"),
    ("tag_buffoon", [], 1, "b skip"),          # Mega Buffoon pack opens right away
    ("tag_rare", [joker("Joker", 1), joker("Jolly Joker", 2)], 1, "b blind"),  # ante 1: joker-now tags only
    ("tag_rare", [joker("Joker", 1), joker("Jolly Joker", 2)], 2, "b skip"),
])
def test_small_blind_skip_advice(tag, jokers, ante, expect):
    assert expect in _advice(_out(cli.show, blind_select(tag, jokers, ante)))


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
    d = shop(jokers=[joker("Cavendish", 1), joker("Jolly Joker", 2)], shop_jokers=[{"index": 1, "name": "Joker", "set": "Joker", "cost": 2}])
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
    assert "pack 1" not in _advice(_out(cli.shop_advise, d))


def test_flat_rental_sold_when_two_others_carry():
    owned = [joker("Joker", 1), joker("Jolly Joker", 2), joker("Zany Joker", 3, rental=True)]
    d = shop(jokers=owned, money=10, ante=3)
    assert _advice(_out(cli.shop_advise, d)).startswith("ADVICE: SELL -> b sell 3")


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
    d = shop(jokers=[joker("Cavendish", 1), joker("Joker", 2), joker("Jolly Joker", 3)], shop_jokers=[], money=4)
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
