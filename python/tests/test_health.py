"""Tests for bridge health and connectivity.

These are integration tests that require the Balatro game to be running
with the RL Bridge mod loaded.

Run with: pytest tests/test_health.py -v
"""

import pytest

from balatro_env.client import BalatroClient, BalatroConnectionError


@pytest.fixture
def client():
    """Create a client instance."""
    return BalatroClient(host="127.0.0.1", port=7777, timeout=5.0, retry_count=1)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client):
        """Health check should return ok status."""
        try:
            health = client.health()
            assert health.status == "ok"
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_health_has_version(self, client):
        """Health response should include version."""
        try:
            health = client.health()
            assert health.version is not None
            assert len(health.version) > 0
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_health_has_uptime(self, client):
        """Health response should include uptime."""
        try:
            health = client.health()
            assert health.uptime_ms >= 0
        except BalatroConnectionError:
            pytest.skip("Balatro bridge not running")

    def test_is_connected(self, client):
        """is_connected should return True when bridge is running."""
        connected = client.is_connected()
        if not connected:
            pytest.skip("Balatro bridge not running")
        assert connected is True


class TestConnectionHandling:
    """Tests for connection handling."""

    def test_connection_error_on_bad_port(self):
        """Should raise BalatroConnectionError for invalid port."""
        client = BalatroClient(host="127.0.0.1", port=7778, timeout=1.0, retry_count=1)
        with pytest.raises(BalatroConnectionError):
            client.health()

    def test_is_connected_returns_false_when_not_running(self):
        """is_connected should return False when bridge is not running."""
        client = BalatroClient(host="127.0.0.1", port=7778, timeout=1.0, retry_count=1)
        assert client.is_connected() is False
