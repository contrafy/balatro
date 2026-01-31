"""Tests for game state schema validation.

These tests validate that the game state conforms to the expected schema.
Requires Balatro to be running with the RL Bridge mod.

Run with: pytest tests/test_state_schema.py -v
"""

import pytest

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import GamePhase, GameState


@pytest.fixture
def client():
    """Create a client instance."""
    return BalatroClient(host="127.0.0.1", port=7777, timeout=5.0, retry_count=1)


@pytest.fixture
def game_state(client) -> GameState:
    """Fetch current game state."""
    try:
        return client.get_state()
    except BalatroConnectionError:
        pytest.skip("Balatro bridge not running")


class TestStateSchema:
    """Tests for game state schema."""

    def test_state_has_schema_version(self, game_state):
        """State should have a schema version."""
        assert game_state.schema_version is not None
        assert game_state.schema_version == "1.0.0"

    def test_state_has_timestamp(self, game_state):
        """State should have a timestamp."""
        assert game_state.timestamp_ms > 0

    def test_state_has_valid_phase(self, game_state):
        """State should have a valid phase."""
        assert game_state.phase is not None
        assert isinstance(game_state.phase, GamePhase)

    def test_state_has_money(self, game_state):
        """State should have money field."""
        assert game_state.money >= 0

    def test_state_has_ante(self, game_state):
        """State should have ante field."""
        assert game_state.ante >= 0

    def test_hand_cards_are_valid(self, game_state):
        """Hand cards should have required fields."""
        for card in game_state.hand:
            assert card.id is not None
            # rank and suit may be None for jokers/consumables in hand
            assert isinstance(card.debuffed, bool)
            assert isinstance(card.highlighted, bool)

    def test_jokers_are_valid(self, game_state):
        """Jokers should have required fields."""
        for joker in game_state.jokers:
            assert joker.id is not None
            assert joker.sell_cost >= 0

    def test_deck_counts_are_valid(self, game_state):
        """Deck counts should be non-negative."""
        assert game_state.deck_counts.deck_size >= 0
        assert game_state.deck_counts.discard_size >= 0


class TestStateInDifferentPhases:
    """Tests for state in different game phases."""

    def test_shop_phase_has_shop_data(self, client):
        """Shop phase should include shop data."""
        try:
            state = client.get_state()
            if state.phase == GamePhase.SHOP:
                assert state.shop is not None
                assert hasattr(state.shop, 'items')
                assert hasattr(state.shop, 'reroll_cost')
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_hand_phase_has_hand(self, client):
        """Hand selection phase should have hand cards."""
        try:
            state = client.get_state()
            if state.phase == GamePhase.SELECTING_HAND:
                assert len(state.hand) > 0
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_blind_info_during_play(self, client):
        """Should have blind info during gameplay."""
        try:
            state = client.get_state()
            if state.phase in {GamePhase.SELECTING_HAND, GamePhase.HAND_PLAYED}:
                assert state.blind is not None
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")
