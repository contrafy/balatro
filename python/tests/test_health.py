"""Tests for bridge health and connectivity.

These are integration tests that require the Balatro game to be running
with the RL Bridge mod loaded.

Run with: pytest tests/test_health.py -v
"""

import socket

import pytest

from balatro_env.client import BalatroClient, BalatroConnectionError


def _unused_port() -> int:
    """A port nothing listens on (other bridge instances occupy 7777+ during swarm runs)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


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
        """Should raise BalatroConnectionError for a port with no listener."""
        client = BalatroClient(host="127.0.0.1", port=_unused_port(), timeout=1.0, retry_count=1)
        with pytest.raises(BalatroConnectionError):
            client.health()

    def test_is_connected_returns_false_when_not_running(self):
        """is_connected should return False when no bridge listens on the port."""
        client = BalatroClient(host="127.0.0.1", port=_unused_port(), timeout=1.0, retry_count=1)
        assert client.is_connected() is False
