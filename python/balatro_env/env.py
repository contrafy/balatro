"""Gymnasium-compatible environment wrapper for Balatro."""

from typing import Any, SupportsFloat

import gymnasium as gym
import numpy as np
import torch
from gymnasium import spaces

from balatro_env.action_space import ActionEncoder
from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.obs_tokenizer import ObservationTokenizer
from balatro_env.schemas import ActionRequest, ActionType, GamePhase, GameState


class BalatroEnv(gym.Env):
    """Gymnasium environment for Balatro.

    Wraps the Balatro game via the HTTP bridge to provide a standard
    RL training interface with observations, actions, and rewards.
    """

    metadata = {"render_modes": ["human", "ansi"]}

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7777,
        render_mode: str | None = None,
        device: str = "cpu",
        max_steps: int = 10000,
        wait_for_connection: bool = True,
        connection_timeout: float = 30.0,
    ):
        """Initialize the Balatro environment.

        Args:
            host: Bridge host address
            port: Bridge port number
            render_mode: Rendering mode ('human', 'ansi', or None)
            device: PyTorch device for tensors
            max_steps: Maximum steps per episode
            wait_for_connection: Whether to wait for game connection on init
            connection_timeout: Timeout for waiting for connection
        """
        super().__init__()

        self.host = host
        self.port = port
        self.render_mode = render_mode
        self.device = device
        self.max_steps = max_steps

        # Initialize components
        self.client = BalatroClient(host=host, port=port)
        self.action_encoder = ActionEncoder()
        self.tokenizer = ObservationTokenizer(device=device)

        # Define spaces
        self.action_space = spaces.Discrete(self.action_encoder.get_action_space_size())
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.tokenizer.get_observation_size(),),
            dtype=np.float32
        )

        # Episode state
        self._current_state: GameState | None = None
        self._current_legal: Any = None
        self._step_count = 0
        self._episode_reward = 0.0
        self._prev_money = 0
        self._prev_chips = 0
        self._connected = False

        # Wait for connection if requested
        if wait_for_connection:
            if not self.client.wait_for_connection(timeout=connection_timeout):
                raise BalatroConnectionError(
                    f"Could not connect to Balatro at {host}:{port} within {connection_timeout}s. "
                    "Make sure the game is running with the RL Bridge mod loaded."
                )
            self._connected = True

    def _get_obs(self) -> np.ndarray:
        """Convert current state to observation array."""
        if self._current_state is None:
            return np.zeros(self.tokenizer.get_observation_size(), dtype=np.float32)

        tensor = self.tokenizer.tokenize_state(self._current_state)
        return tensor.cpu().numpy()

    def _get_info(self) -> dict[str, Any]:
        """Get additional info about current state."""
        info = {
            "step_count": self._step_count,
            "episode_reward": self._episode_reward,
            "connected": self._connected,
        }

        if self._current_state:
            info.update({
                "phase": self._current_state.phase.value,
                "money": self._current_state.money,
                "ante": self._current_state.ante,
                "round": self._current_state.round,
                "hands_remaining": self._current_state.hands_remaining,
                "discards_remaining": self._current_state.discards_remaining,
                "hand_size": len(self._current_state.hand),
                "joker_count": len(self._current_state.jokers),
            })

            if self._current_state.blind:
                info["chips_needed"] = self._current_state.blind.chips_needed
                info["chips_scored"] = self._current_state.blind.chips_scored

        if self._current_legal:
            # Generate action mask
            hand_size = len(self._current_state.hand) if self._current_state else 8
            mask = self.action_encoder.get_legal_action_mask(self._current_legal, hand_size)
            info["action_mask"] = np.array(mask, dtype=np.bool_)

        return info

    def _compute_reward(self, prev_state: GameState | None, new_state: GameState) -> float:
        """Compute reward based on state transition.

        Current reward shaping:
        - +1 per $1 gained
        - +0.01 per 1000 chips scored toward blind
        - +10 for completing a blind
        - +100 for completing an ante
        - -100 for game over

        Args:
            prev_state: Previous game state
            new_state: New game state after action

        Returns:
            Float reward value
        """
        if prev_state is None:
            return 0.0

        reward = 0.0

        # Money gained
        money_diff = new_state.money - prev_state.money
        reward += money_diff

        # Chips scored
        prev_chips = prev_state.blind.chips_scored if prev_state.blind else 0
        new_chips = new_state.blind.chips_scored if new_state.blind else 0
        chip_diff = new_chips - prev_chips
        if chip_diff > 0:
            reward += chip_diff / 1000.0 * 0.01

        # Blind completion
        prev_blind_name = prev_state.blind.name if prev_state.blind else None
        new_blind_name = new_state.blind.name if new_state.blind else None
        if prev_blind_name and new_blind_name and prev_blind_name != new_blind_name:
            reward += 10.0

        # Ante completion
        if new_state.ante > prev_state.ante:
            reward += 100.0

        # Check for game over (returned to menu or error)
        if new_state.phase == GamePhase.MENU and prev_state.phase != GamePhase.MENU:
            # Likely game over
            reward -= 100.0

        return reward

    def _is_terminal(self, state: GameState) -> bool:
        """Check if the current state is terminal.

        Args:
            state: Current game state

        Returns:
            True if episode should end
        """
        # Game over if returned to menu
        if state.phase in {GamePhase.MENU, GamePhase.SPLASH}:
            return True

        # Max steps reached
        if self._step_count >= self.max_steps:
            return True

        # Error state
        if state.error:
            return True

        return False

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset the environment for a new episode.

        Note: Full reset requires manual game restart currently.
        This will attempt to call the bridge's reset endpoint but
        may need user intervention.

        Args:
            seed: Random seed (forwarded to game if supported)
            options: Additional options

        Returns:
            Tuple of (observation, info)
        """
        super().reset(seed=seed)

        self._step_count = 0
        self._episode_reward = 0.0

        # Try to reset via bridge
        try:
            seed_str = str(seed) if seed else None
            self._current_state, self._current_legal = self.client.reset(seed=seed_str)
        except BalatroConnectionError:
            # Reset not fully implemented - just get current state
            self._current_state = self.client.get_state()
            self._current_legal = self.client.get_legal_actions()

        self._prev_money = self._current_state.money
        self._prev_chips = self._current_state.blind.chips_scored if self._current_state.blind else 0

        return self._get_obs(), self._get_info()

    def step(
        self, action: int
    ) -> tuple[np.ndarray, SupportsFloat, bool, bool, dict[str, Any]]:
        """Execute an action in the environment.

        Args:
            action: Integer action index from action space

        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        self._step_count += 1
        prev_state = self._current_state

        # Decode action
        action_request = self.action_encoder.decode_action(action)

        # Execute action
        try:
            result = self.client.execute_action(action_request)

            if result.ok and result.state:
                self._current_state = result.state
                self._current_legal = result.legal
            else:
                # Action failed - re-fetch state
                self._current_state = self.client.get_state()
                self._current_legal = self.client.get_legal_actions()

        except BalatroConnectionError as e:
            # Connection lost
            self._connected = False
            info = self._get_info()
            info["error"] = str(e)
            return self._get_obs(), -100.0, True, False, info

        # Compute reward
        reward = self._compute_reward(prev_state, self._current_state)
        self._episode_reward += reward

        # Check termination
        terminated = self._is_terminal(self._current_state)
        truncated = self._step_count >= self.max_steps

        return self._get_obs(), reward, terminated, truncated, self._get_info()

    def render(self) -> str | None:
        """Render the current state.

        Returns:
            String representation if render_mode is 'ansi', None otherwise
        """
        if self._current_state is None:
            return None

        if self.render_mode == "human":
            from balatro_env.util import print_state_summary
            print_state_summary(self._current_state)
            return None

        elif self.render_mode == "ansi":
            lines = []
            state = self._current_state
            lines.append(f"Phase: {state.phase.value}")
            lines.append(f"Money: ${state.money} | Ante: {state.ante} | Round: {state.round}")
            lines.append(f"Hands: {state.hands_remaining} | Discards: {state.discards_remaining}")

            if state.blind:
                lines.append(f"Blind: {state.blind.name} - {state.blind.chips_scored:,}/{state.blind.chips_needed:,}")

            if state.hand:
                hand_str = ", ".join(f"{c.rank}{c.suit[0] if c.suit else '?'}" for c in state.hand)
                lines.append(f"Hand: [{hand_str}]")

            if state.jokers:
                joker_str = ", ".join(j.name or "?" for j in state.jokers)
                lines.append(f"Jokers: [{joker_str}]")

            return "\n".join(lines)

        return None

    def close(self):
        """Clean up resources."""
        self.client.close()

    def get_action_mask(self) -> np.ndarray:
        """Get the current legal action mask.

        Returns:
            Boolean array where True indicates legal action
        """
        if self._current_legal is None:
            # All actions masked (none legal)
            return np.zeros(self.action_space.n, dtype=np.bool_)

        hand_size = len(self._current_state.hand) if self._current_state else 8
        mask = self.action_encoder.get_legal_action_mask(self._current_legal, hand_size)
        return np.array(mask, dtype=np.bool_)

    def sample_legal_action(self) -> int:
        """Sample a random legal action.

        Returns:
            Integer action index
        """
        mask = self.get_action_mask()
        legal_indices = np.where(mask)[0]

        if len(legal_indices) == 0:
            # No legal actions - return random (will likely fail)
            return self.action_space.sample()

        return int(np.random.choice(legal_indices))


# Register the environment with Gymnasium
gym.register(
    id="Balatro-v0",
    entry_point="balatro_env.env:BalatroEnv",
    max_episode_steps=10000,
)
