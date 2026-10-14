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


def blind_select(tag, jokers=()):
    return {"phase": "BLIND_SELECT", "stake": 8, "ante": 1, "money": 4, "joker_slots": 6, "jokers": list(jokers),
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


@pytest.mark.parametrize("tag,jokers,expect", [
    ("tag_rare", [], "b blind"),            # pays in the next shop, after the Big Blind
    ("tag_polychrome", [], "b blind"),
    ("tag_buffoon", [], "b skip"),          # Mega Buffoon pack opens right away
    ("tag_rare", [joker("Joker", 1), joker("Jolly Joker", 2)], "b skip"),
])
def test_small_blind_skip_advice(tag, jokers, expect):
    assert expect in _advice(_out(cli.show, blind_select(tag, jokers)))


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
