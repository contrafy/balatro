"""Deck modifiers must come from the live run, never from Red Deck constants.

Black Deck grants 6 joker slots and 3 hands, Painted Deck 4 slots and a 10-card hand, Nebula
1 consumable slot, Green Deck no interest. The agent once believed it had 5 joker slots on a
Black Deck because nothing in the state carried the real limit. These tests pin the contract:
the bridge payload carries the run's rules, and every consumer decides from the state.

Offline: builds bridge-shaped payloads by hand, no running game required.
"""

from typing import Any

from balatro_env.action_space import ActionEncoder
from balatro_env.schemas import ActionType, GameState, LegalActions
from balatro_env.scripts.play_agent import choose_pack_action, choose_shop_action


def joker(index: int, name: str) -> dict[str, Any]:
    return {"id": index, "name": name, "sell_cost": 2, "joker_index": index}


def state_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "1.0.0",
        "timestamp_ms": 1,
        "phase": "SHOP",
        "money": 20,
        "jokers": {},
        "consumables": {},
        "hand": {},
    }
    payload.update(overrides)
    return payload


def black_deck_payload(**overrides: Any) -> dict[str, Any]:
    """What the bridge reports for a Black Deck run: values read from G.GAME, not a table."""
    payload = state_payload(
        deck_name="Black Deck",
        deck_key="b_black",
        deck_config={"hands": -1, "joker_slot": 1},
        joker_slots=6,
        consumable_slots=2,
        hand_size=8,
        hands_per_round=3,
        discards_per_round=3,
        interest_amount=1,
        interest_cap=25,
        no_interest=False,
        modifiers={},
        starting_params={"hands": 3, "discards": 3, "joker_slots": 6, "hand_size": 8},
        used_vouchers={},
        tags={},
        stake=1,
        win_ante=8,
    )
    payload.update(overrides)
    return payload


def legal_payload(actions: list[dict[str, Any]], phase: str = "SHOP") -> LegalActions:
    return LegalActions.model_validate({"schema_version": "1.0.0", "phase": phase, "actions": actions})


def sell_actions(count: int) -> list[dict[str, Any]]:
    return [
        {"type": "SELL_JOKER", "description": f"Sell joker {i}",
         "params": {"index": {"one_of": [i]}}, "info": {"sell_value": 2}}
        for i in range(1, count + 1)
    ]


class TestStateCarriesRunRules:
    def test_black_deck_limits_parse_from_live_values(self):
        state = GameState.model_validate(black_deck_payload())

        assert state.deck_name == "Black Deck"
        assert state.deck_key == "b_black"
        assert state.deck_config == {"hands": -1, "joker_slot": 1}
        assert state.joker_slots == 6
        assert state.hands_per_round == 3
        assert state.discards_per_round == 3
        assert state.starting_params["joker_slots"] == 6

    def test_lua_empty_tables_become_empty_lists(self):
        state = GameState.model_validate(black_deck_payload(used_vouchers={}, tags={}))

        assert state.used_vouchers == []
        assert state.tags == []

    def test_green_deck_reports_no_interest(self):
        state = GameState.model_validate(state_payload(
            deck_name="Green Deck", no_interest=True, modifiers={"no_interest": True},
            interest_amount=1, interest_cap=25,
        ))

        assert state.no_interest is True
        assert state.modifiers["no_interest"] is True

    def test_abandoned_deck_composition_has_no_faces(self):
        state = GameState.model_validate(state_payload(
            deck_name="Abandoned Deck",
            deck_composition={"total_cards": 40, "face_cards": 0,
                              "by_suit": {"Spades": 10, "Hearts": 10, "Clubs": 10, "Diamonds": 10},
                              "by_rank": {"Ace": 4, "10": 4}},
        ))

        assert state.deck_composition is not None
        assert state.deck_composition.total_cards == 40
        assert state.deck_composition.face_cards == 0
        assert "Jack" not in state.deck_composition.by_rank

    def test_blind_select_and_tags_parse(self):
        state = GameState.model_validate(state_payload(
            phase="BLIND_SELECT",
            tags=[{"key": "tag_double", "name": "Double Tag"}],
            blind_select={"on_deck": "Small", "choices": {
                "Small": {"key": "bl_small", "name": "Small Blind", "chips": 300, "state": "Select",
                          "tag": "Double Tag", "tag_key": "tag_double"},
            }},
        ))

        assert state.tags[0].name == "Double Tag"
        assert state.blind_select is not None
        assert state.blind_select.choices["Small"].chips == 300

    def test_legacy_bridge_payload_without_rule_fields_still_parses(self):
        state = GameState.model_validate(state_payload())

        assert state.joker_slots is None
        assert state.hands_per_round is None
        assert state.deck_name is None
        assert state.no_interest is False


class TestSlotDecisionsUseStateLimit:
    def test_sixth_joker_fits_on_black_deck(self):
        state = GameState.model_validate(black_deck_payload(
            jokers=[joker(i, "Joker") for i in range(1, 6)],
        ))

        assert state.joker_slots_free == 1
        assert state.can_add_joker() is True

    def test_five_jokers_fill_a_five_slot_deck(self):
        state = GameState.model_validate(black_deck_payload(
            deck_name="Red Deck", joker_slots=5,
            jokers=[joker(i, "Joker") for i in range(1, 6)],
        ))

        assert state.joker_slots_free == 0
        assert state.can_add_joker() is False

    def test_painted_deck_fills_at_four(self):
        state = GameState.model_validate(black_deck_payload(
            deck_name="Painted Deck", joker_slots=4, hand_size=10,
            jokers=[joker(i, "Joker") for i in range(1, 5)],
        ))

        assert state.can_add_joker() is False
        assert state.hand_size == 10

    def test_nebula_deck_single_consumable_slot(self):
        state = GameState.model_validate(black_deck_payload(
            deck_name="Nebula Deck", consumable_slots=1,
            consumables=[{"index": 1, "name": "The Fool", "type": "Tarot"}],
        ))

        assert state.consumable_slots_free == 0
        assert state.can_add_consumable() is False

    def test_unknown_limit_defers_to_bridge_legality(self):
        state = GameState.model_validate(state_payload(
            jokers=[joker(i, "Joker") for i in range(1, 8)],
        ))

        assert state.joker_slots_free is None
        assert state.can_add_joker() is True


class TestShopAgentHonorsDeckSlots:
    """Five owned jokers is a full Red Deck but has a free slot on a Black Deck."""

    def shop_state(self, joker_slots: int) -> GameState:
        return GameState.model_validate(black_deck_payload(
            joker_slots=joker_slots,
            jokers=[joker(i, "Joker") for i in range(1, 6)],
            shop={"jokers": [{"index": 1, "name": "Droll Joker", "type": "Joker", "cost": 6}],
                  "vouchers": {}, "boosters": {}, "reroll_cost": 5},
        ))

    def shop_legal(self) -> LegalActions:
        return legal_payload(
            [{"type": "SHOP_BUY", "description": "Buy Droll Joker",
              "params": {"slot": {"one_of": [1]}}, "info": {"cost": 6}}]
            + sell_actions(5)
            + [{"type": "SHOP_END", "description": "Leave", "params": {}}]
        )

    def test_black_deck_buys_into_sixth_slot_instead_of_selling(self):
        action = choose_shop_action(self.shop_state(joker_slots=6), self.shop_legal(), 0)

        assert action.type == ActionType.SHOP_BUY
        assert action.params == {"slot": 1}

    def test_full_five_slot_deck_sells_before_buying(self):
        action = choose_shop_action(self.shop_state(joker_slots=5), self.shop_legal(), 0)

        assert action.type == ActionType.SELL_JOKER
        assert action.params == {"index": 1}

    def test_rerolls_stop_when_run_limit_is_full_not_at_five(self):
        state = GameState.model_validate(black_deck_payload(
            deck_name="Painted Deck", joker_slots=4, money=50,
            jokers=[joker(i, "Joker") for i in range(1, 5)],
            shop={"jokers": [], "vouchers": {}, "boosters": {}, "reroll_cost": 5},
        ))
        legal = legal_payload([
            {"type": "SHOP_REROLL", "description": "Reroll", "params": {}, "info": {"cost": 5}},
            {"type": "SHOP_END", "description": "Leave", "params": {}},
        ])

        assert choose_shop_action(state, legal, 0).type == ActionType.SHOP_END


class TestPackAgentHonorsLegality:
    def test_only_picks_cards_the_bridge_allows(self):
        """A Buffoon-pack joker is not selectable when joker slots are full; pick what is."""
        state = GameState.model_validate(black_deck_payload(
            phase="PACK_OPENING", joker_slots=6,
            jokers=[joker(i, "Joker") for i in range(1, 7)],
            pack={"choices_remaining": 1, "cards": [
                {"index": 1, "name": "Droll Joker", "type": "Joker", "facing": "front"},
                {"index": 2, "name": "Pluto", "type": "Planet", "facing": "front"},
            ]},
        ))
        legal = legal_payload([
            {"type": "SELECT_PACK_CARD", "description": "Select Pluto", "params": {"index": {"one_of": [2]}}},
            {"type": "SKIP_PACK", "description": "Skip", "params": {}},
        ], phase="PACK_OPENING")

        action = choose_pack_action(state, legal)

        assert action is not None
        assert action.params == {"index": 2}


class TestActionEncoderCoversRunLimits:
    def test_sixth_joker_sell_is_encodable_and_maskable(self):
        encoder = ActionEncoder()
        legal = legal_payload(sell_actions(6))

        mask = encoder.get_legal_action_mask(legal, hand_size=8)
        sixth = encoder.sell_joker_offset + 5

        assert mask[sixth] is True
        assert encoder.decode_action(sixth).params == {"index": 6}

    def test_encoder_capacity_exceeds_every_vanilla_deck(self):
        assert ActionEncoder.MAX_JOKERS >= 6
        assert ActionEncoder.MAX_HAND_SIZE >= 10
