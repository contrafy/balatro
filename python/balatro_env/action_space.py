"""Action space encoding and decoding for Balatro RL."""

from itertools import combinations
from typing import Any

from balatro_env.schemas import ActionRequest, ActionType, LegalAction, LegalActions


class ActionEncoder:
    """Encodes and decodes actions for RL training.

    Provides a stable mapping between action indices and game actions,
    handling the variable action space that changes based on game state.
    """

    # Maximum hand size for card selection
    MAX_HAND_SIZE = 10
    MAX_JOKERS = 5
    MAX_SHOP_SLOTS = 6
    MAX_PACK_CHOICES = 5

    def __init__(self):
        """Initialize the action encoder with fixed action space mapping."""
        self._build_action_space()

    def _build_action_space(self):
        """Build the complete action space mapping.

        The action space is organized as:
        - Simple actions (no parameters): indices 0-N
        - Card selection actions: encoded as bitmap for selected cards
        - Shop actions: indexed by slot number
        """
        self.simple_actions = {
            "SHOP_REROLL": 0,
            "SHOP_END": 1,
            "SKIP_BLIND": 2,
            "SKIP_PACK": 3,
            "SORT_HAND_RANK": 4,
            "SORT_HAND_SUIT": 5,
        }

        # Card selection actions use a bitmap encoding
        # For 10 cards max, we have 2^10 = 1024 possible selections
        # But we limit to 1-5 cards, which is much smaller
        self.play_hand_offset = 10
        self.discard_offset = self.play_hand_offset + 1024

        # Shop buy actions: one per slot
        self.shop_buy_offset = self.discard_offset + 1024

        # Sell joker actions
        self.sell_joker_offset = self.shop_buy_offset + self.MAX_SHOP_SLOTS

        # Pack selection actions
        self.pack_select_offset = self.sell_joker_offset + self.MAX_JOKERS

        # Blind selection
        self.blind_select_offset = self.pack_select_offset + self.MAX_PACK_CHOICES

        # Total action space size
        self.action_space_size = self.blind_select_offset + 3  # small, big, boss

    def card_indices_to_bitmap(self, indices: list[int]) -> int:
        """Convert a list of card indices to a bitmap.

        Args:
            indices: List of card indices (1-indexed)

        Returns:
            Integer bitmap representing selected cards
        """
        bitmap = 0
        for idx in indices:
            if 1 <= idx <= self.MAX_HAND_SIZE:
                bitmap |= 1 << (idx - 1)
        return bitmap

    def bitmap_to_card_indices(self, bitmap: int) -> list[int]:
        """Convert a bitmap to a list of card indices.

        Args:
            bitmap: Integer bitmap

        Returns:
            List of card indices (1-indexed)
        """
        indices = []
        for i in range(self.MAX_HAND_SIZE):
            if bitmap & (1 << i):
                indices.append(i + 1)
        return indices

    def encode_action(self, action: ActionRequest) -> int:
        """Encode an action request to an integer index.

        Args:
            action: The action to encode

        Returns:
            Integer action index
        """
        action_type = action.type.value if isinstance(action.type, ActionType) else action.type

        if action_type == "SHOP_REROLL":
            return self.simple_actions["SHOP_REROLL"]
        elif action_type == "SHOP_END":
            return self.simple_actions["SHOP_END"]
        elif action_type == "SKIP_BLIND":
            return self.simple_actions["SKIP_BLIND"]
        elif action_type == "SKIP_PACK":
            return self.simple_actions["SKIP_PACK"]
        elif action_type == "SORT_HAND":
            mode = action.params.get("mode", "rank")
            return self.simple_actions[f"SORT_HAND_{mode.upper()}"]
        elif action_type == "PLAY_HAND":
            indices = action.params.get("card_indices", [])
            bitmap = self.card_indices_to_bitmap(indices)
            return self.play_hand_offset + bitmap
        elif action_type == "DISCARD":
            indices = action.params.get("card_indices", [])
            bitmap = self.card_indices_to_bitmap(indices)
            return self.discard_offset + bitmap
        elif action_type == "SHOP_BUY":
            slot = action.params.get("slot", 1)
            return self.shop_buy_offset + slot - 1
        elif action_type == "SHOP_SELL_JOKER":
            joker_idx = action.params.get("joker_index", 1)
            return self.sell_joker_offset + joker_idx - 1
        elif action_type == "SELECT_PACK_ITEM":
            choice_idx = action.params.get("choice_index", 1)
            return self.pack_select_offset + choice_idx - 1
        elif action_type == "SELECT_BLIND":
            options = {"small": 0, "big": 1, "boss": 2}
            option = action.params.get("option", "small")
            return self.blind_select_offset + options.get(option, 0)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def decode_action(self, action_idx: int) -> ActionRequest:
        """Decode an integer action index to an action request.

        Args:
            action_idx: Integer action index

        Returns:
            ActionRequest ready to be executed
        """
        if action_idx == self.simple_actions["SHOP_REROLL"]:
            return ActionRequest(type=ActionType.SHOP_REROLL)
        elif action_idx == self.simple_actions["SHOP_END"]:
            return ActionRequest(type=ActionType.SHOP_END)
        elif action_idx == self.simple_actions["SKIP_BLIND"]:
            return ActionRequest(type=ActionType.SKIP_BLIND)
        elif action_idx == self.simple_actions["SKIP_PACK"]:
            return ActionRequest(type=ActionType.SKIP_PACK)
        elif action_idx == self.simple_actions["SORT_HAND_RANK"]:
            return ActionRequest(type=ActionType.SORT_HAND, params={"mode": "rank"})
        elif action_idx == self.simple_actions["SORT_HAND_SUIT"]:
            return ActionRequest(type=ActionType.SORT_HAND, params={"mode": "suit"})
        elif self.play_hand_offset <= action_idx < self.discard_offset:
            bitmap = action_idx - self.play_hand_offset
            indices = self.bitmap_to_card_indices(bitmap)
            return ActionRequest(type=ActionType.PLAY_HAND, params={"card_indices": indices})
        elif self.discard_offset <= action_idx < self.shop_buy_offset:
            bitmap = action_idx - self.discard_offset
            indices = self.bitmap_to_card_indices(bitmap)
            return ActionRequest(type=ActionType.DISCARD, params={"card_indices": indices})
        elif self.shop_buy_offset <= action_idx < self.sell_joker_offset:
            slot = action_idx - self.shop_buy_offset + 1
            return ActionRequest(type=ActionType.SHOP_BUY, params={"slot": slot})
        elif self.sell_joker_offset <= action_idx < self.pack_select_offset:
            joker_idx = action_idx - self.sell_joker_offset + 1
            return ActionRequest(type=ActionType.SHOP_SELL_JOKER, params={"joker_index": joker_idx})
        elif self.pack_select_offset <= action_idx < self.blind_select_offset:
            choice_idx = action_idx - self.pack_select_offset + 1
            return ActionRequest(type=ActionType.SELECT_PACK_ITEM, params={"choice_index": choice_idx})
        elif self.blind_select_offset <= action_idx < self.action_space_size:
            options = ["small", "big", "boss"]
            option_idx = action_idx - self.blind_select_offset
            return ActionRequest(type=ActionType.SELECT_BLIND, params={"option": options[option_idx]})
        else:
            raise ValueError(f"Invalid action index: {action_idx}")

    def get_legal_action_mask(self, legal_actions: LegalActions, hand_size: int = 8) -> list[bool]:
        """Generate a boolean mask for legal actions.

        Args:
            legal_actions: The current legal actions
            hand_size: Current hand size for card selection actions

        Returns:
            Boolean list where True indicates a legal action
        """
        mask = [False] * self.action_space_size

        for action in legal_actions.actions:
            action_type = action.type.value if isinstance(action.type, ActionType) else action.type

            if action_type == "SHOP_REROLL":
                mask[self.simple_actions["SHOP_REROLL"]] = True
            elif action_type == "SHOP_END":
                mask[self.simple_actions["SHOP_END"]] = True
            elif action_type == "SKIP_BLIND":
                mask[self.simple_actions["SKIP_BLIND"]] = True
            elif action_type == "SKIP_PACK":
                mask[self.simple_actions["SKIP_PACK"]] = True
            elif action_type == "SORT_HAND":
                mask[self.simple_actions["SORT_HAND_RANK"]] = True
                mask[self.simple_actions["SORT_HAND_SUIT"]] = True
            elif action_type == "PLAY_HAND":
                # Mark all valid card combinations as legal
                params = action.params
                if params and params.card_indices:
                    available = params.card_indices.get("available", list(range(1, hand_size + 1)))
                    min_select = params.card_indices.get("min_select", 1)
                    max_select = params.card_indices.get("max_select", 5)
                    # Generate all valid combinations
                    for size in range(min_select, min(max_select, len(available)) + 1):
                        for combo in combinations(available, size):
                            bitmap = self.card_indices_to_bitmap(list(combo))
                            mask[self.play_hand_offset + bitmap] = True
            elif action_type == "DISCARD":
                params = action.params
                if params and params.card_indices:
                    available = params.card_indices.get("available", list(range(1, hand_size + 1)))
                    min_select = params.card_indices.get("min_select", 1)
                    max_select = params.card_indices.get("max_select", 5)
                    for size in range(min_select, min(max_select, len(available)) + 1):
                        for combo in combinations(available, size):
                            bitmap = self.card_indices_to_bitmap(list(combo))
                            mask[self.discard_offset + bitmap] = True
            elif action_type == "SHOP_BUY":
                params = action.params
                if params and params.slot:
                    slot = params.slot
                    if 1 <= slot <= self.MAX_SHOP_SLOTS:
                        mask[self.shop_buy_offset + slot - 1] = True
            elif action_type == "SHOP_SELL_JOKER":
                params = action.params
                if params and params.joker_index:
                    joker_idx = params.joker_index
                    if 1 <= joker_idx <= self.MAX_JOKERS:
                        mask[self.sell_joker_offset + joker_idx - 1] = True
            elif action_type == "SELECT_PACK_ITEM":
                params = action.params
                if params and params.choice_index:
                    choice_idx = params.choice_index
                    if 1 <= choice_idx <= self.MAX_PACK_CHOICES:
                        mask[self.pack_select_offset + choice_idx - 1] = True
            elif action_type == "SELECT_BLIND":
                # All three blind options
                for i in range(3):
                    mask[self.blind_select_offset + i] = True

        return mask

    def get_action_space_size(self) -> int:
        """Get the total action space size."""
        return self.action_space_size
