"""Tests for legal actions.

These tests validate that legal actions are correctly computed.
Requires Balatro to be running with the RL Bridge mod.

Run with: pytest tests/test_legal_actions.py -v
"""

import pytest

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import ActionType, GamePhase, LegalActions


@pytest.fixture
def client():
    """Create a client instance."""
    return BalatroClient(host="127.0.0.1", port=7777, timeout=5.0, retry_count=1)


@pytest.fixture
def legal_actions(client) -> LegalActions:
    """Fetch current legal actions."""
    try:
        return client.get_legal_actions()
    except BalatroConnectionError:
        pytest.skip("Balatro bridge not running")


class TestLegalActionsSchema:
    """Tests for legal actions schema."""

    def test_legal_has_schema_version(self, legal_actions):
        """Legal actions should have schema version."""
        assert legal_actions.schema_version is not None

    def test_legal_has_phase(self, legal_actions):
        """Legal actions should have phase."""
        assert legal_actions.phase is not None
        assert isinstance(legal_actions.phase, GamePhase)

    def test_actions_have_type(self, legal_actions):
        """Each action should have a type."""
        for action in legal_actions.actions:
            assert action.type is not None
            assert isinstance(action.type, ActionType)

    def test_actions_have_description(self, legal_actions):
        """Each action should have a description."""
        for action in legal_actions.actions:
            assert action.description is not None
            assert len(action.description) > 0


class TestPhaseSpecificActions:
    """Tests for phase-specific legal actions."""

    def test_shop_phase_actions(self, client):
        """Shop phase should have shop-specific actions."""
        try:
            legal = client.get_legal_actions()
            if legal.phase == GamePhase.SHOP:
                action_types = {a.type for a in legal.actions}
                # Should have at least end shop action
                assert ActionType.SHOP_END in action_types
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_hand_phase_actions(self, client):
        """Hand selection should have play/discard actions."""
        try:
            legal = client.get_legal_actions()
            if legal.phase == GamePhase.SELECTING_HAND:
                action_types = {a.type for a in legal.actions}
                # Should have play hand action
                assert ActionType.PLAY_HAND in action_types or ActionType.DISCARD in action_types
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_play_hand_has_card_indices(self, client):
        """Play hand action should specify valid card indices."""
        try:
            legal = client.get_legal_actions()
            for action in legal.actions:
                if action.type == ActionType.PLAY_HAND:
                    assert action.params is not None
                    assert action.params.card_indices is not None
                    # Should have available indices
                    available = action.params.card_indices.get("available", [])
                    assert len(available) > 0
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")


class TestActionHelpers:
    """Tests for LegalActions helper methods."""

    def test_has_action_type(self, legal_actions):
        """has_action_type should work correctly."""
        for action in legal_actions.actions:
            assert legal_actions.has_action_type(action.type)

    def test_get_actions_of_type(self, legal_actions):
        """get_actions_of_type should return correct actions."""
        for action in legal_actions.actions:
            actions_of_type = legal_actions.get_actions_of_type(action.type)
            assert len(actions_of_type) > 0
            assert all(a.type == action.type for a in actions_of_type)
