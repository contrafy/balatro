"""HTTP client for communicating with the Balatro RL Bridge."""

import time
from typing import Any

import requests
from requests.exceptions import ConnectionError, Timeout

from balatro_env.schemas import (
    ActionRequest,
    ActionResult,
    GameState,
    HealthResponse,
    LegalActions,
)


class BalatroConnectionError(Exception):
    """Raised when unable to connect to the Balatro bridge."""
    pass


class BalatroClient:
    """HTTP client for the Balatro RL Bridge.

    Provides methods to interact with the in-game HTTP server,
    including fetching state, legal actions, and executing actions.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7777,
        timeout: float = 5.0,
        retry_count: int = 3,
        retry_delay: float = 0.5,
    ):
        """Initialize the client.

        Args:
            host: Host address of the Balatro bridge
            port: Port number of the Balatro bridge
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self._session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            json_data: JSON body for POST requests

        Returns:
            Parsed JSON response

        Raises:
            BalatroConnectionError: If unable to connect after retries
        """
        url = f"{self.base_url}/{endpoint}"
        last_error = None

        for attempt in range(self.retry_count):
            try:
                if method == "GET":
                    response = self._session.get(url, timeout=self.timeout)
                elif method == "POST":
                    response = self._session.post(url, json=json_data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except ConnectionError as e:
                last_error = e
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
            except Timeout as e:
                last_error = e
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
            except requests.exceptions.HTTPError as e:
                # Don't retry HTTP errors (4xx, 5xx)
                raise BalatroConnectionError(f"HTTP error: {e}")

        raise BalatroConnectionError(
            f"Failed to connect to Balatro at {url} after {self.retry_count} attempts: {last_error}"
        )

    def health(self) -> HealthResponse:
        """Check if the Balatro bridge is running and healthy.

        Returns:
            HealthResponse with status, version, and uptime
        """
        data = self._request("GET", "health")
        return HealthResponse.model_validate(data)

    def is_connected(self) -> bool:
        """Check if the bridge is reachable.

        Returns:
            True if connected, False otherwise
        """
        try:
            health = self.health()
            return health.status == "ok"
        except BalatroConnectionError:
            return False

    def wait_for_connection(self, timeout: float = 30.0, poll_interval: float = 1.0) -> bool:
        """Wait for the bridge to become available.

        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between connection attempts

        Returns:
            True if connected within timeout, False otherwise
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.is_connected():
                return True
            time.sleep(poll_interval)
        return False

    def get_state(self) -> GameState:
        """Fetch the current game state.

        Returns:
            Complete GameState snapshot
        """
        data = self._request("GET", "state")
        return GameState.model_validate(data)

    def get_legal_actions(self) -> LegalActions:
        """Fetch the current legal actions.

        Returns:
            LegalActions with available actions for current phase
        """
        data = self._request("GET", "legal")
        return LegalActions.model_validate(data)

    def execute_action(self, action: ActionRequest) -> ActionResult:
        """Execute an action in the game.

        Args:
            action: The action to execute

        Returns:
            ActionResult with success status and new state
        """
        data = self._request("POST", "action", action.model_dump())
        return ActionResult.model_validate(data)

    def reset(self, seed: str | None = None) -> tuple[GameState, LegalActions]:
        """Request a game reset.

        Note: Full reset may not be implemented yet - may require manual intervention.

        Args:
            seed: Optional seed for the new run

        Returns:
            Tuple of (initial state, legal actions)
        """
        body = {"seed": seed} if seed else {}
        data = self._request("POST", "reset", body)

        # Reset might return an error if not fully implemented
        if "error" in data:
            raise BalatroConnectionError(f"Reset not supported: {data.get('error')}")

        state = self.get_state()
        legal = self.get_legal_actions()
        return state, legal

    def config(self, **kwargs) -> dict[str, Any]:
        """Update bridge configuration.

        Args:
            **kwargs: Configuration options to update

        Returns:
            Current configuration
        """
        data = self._request("POST", "config", kwargs)
        return data

    def close(self):
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> "BalatroClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
