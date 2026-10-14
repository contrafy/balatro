"""Observation tokenization for transformer-based RL models."""

from typing import Any

import torch

from balatro_env import vocab
from balatro_env.schemas import CardData, GamePhase, GameState, JokerData


class ObservationTokenizer:
    """Tokenizes Balatro game state into tensor representations.

    Converts the structured game state into fixed-size tensor observations
    suitable for transformer or MLP-based RL models.
    """

    # Vocabulary sizes for various game elements
    VOCAB = {
        "phase": 10,
        "rank": 15,  # A, 2-10, J, Q, K + padding + unknown
        "suit": 6,   # Hearts, Diamonds, Clubs, Spades + padding + unknown
        "edition": 6,  # None, Foil, Holo, Polychrome, Negative, unknown
        "enhancement": len(vocab.ENHANCEMENTS) + 2,  # padding + enhancements + unknown
        "seal": 6,   # None, Gold, Red, Blue, Purple, unknown
        "joker": len(vocab.JOKER_KEYS) + 2,  # padding + vanilla jokers + unknown
        "consumable": len(vocab.CONSUMABLE_KEYS) + 2,  # padding + tarots/planets/spectrals + unknown
        "item_set": len(vocab.ITEM_SETS) + 2,
    }

    # Rank mapping
    RANK_MAP = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "Jack": 11, "Queen": 12, "King": 13, "Ace": 14, "J": 11, "Q": 12, "K": 13, "A": 14,
    }

    # Suit mapping
    SUIT_MAP = {"Hearts": 1, "Diamonds": 2, "Clubs": 3, "Spades": 4}

    # Edition mapping
    EDITION_MAP = {"foil": 1, "holo": 2, "polychrome": 3, "negative": 4}

    # Phase mapping
    PHASE_MAP = {
        GamePhase.MENU: 0,
        GamePhase.SPLASH: 1,
        GamePhase.SELECTING_HAND: 2,
        GamePhase.HAND_PLAYED: 3,
        GamePhase.DRAW_TO_HAND: 4,
        GamePhase.BLIND_SELECT: 5,
        GamePhase.SHOP: 6,
        GamePhase.PACK_OPENING: 7,
        GamePhase.UNKNOWN: 8,
        GamePhase.ROUND_EVAL: 9,
        GamePhase.GAME_OVER: 10,
        GamePhase.NEW_ROUND: 11,
        GamePhase.PLAY_TAROT: 12,
    }

    # Padding ceilings, not game rules: live limits come from GameState (joker_slots etc.).
    # Black Deck grants 6 joker slots, negative editions add more; Nebula/Painted shift the others.
    MAX_HAND_SIZE = 10
    MAX_JOKERS = 10
    MAX_CONSUMABLES = 6
    MAX_SHOP_ITEMS = 6

    def __init__(self, device: str = "cpu"):
        """Initialize the tokenizer.

        Args:
            device: PyTorch device for tensor creation
        """
        self.device = torch.device(device)
        self._build_embedding_dims()

    def _build_embedding_dims(self):
        """Calculate embedding dimensions."""
        # Card embedding: rank + suit + edition + enhancement + seal + flags
        self.card_features = 8  # rank, suit, edition, enhancement, seal, debuffed, highlighted, position

        # Total observation size
        self.obs_size = (
            10 +  # Scalar features: phase, money, ante, round, hands, discards, chips_needed, chips_scored, deck_size, discard_size
            4 +  # Run rules: joker_slots, consumable_slots, hand_size, no_interest
            self.MAX_HAND_SIZE * self.card_features +  # Hand cards
            self.MAX_JOKERS * 4 +  # Jokers (id, rarity, sell_cost, has_ability)
            self.MAX_CONSUMABLES * 2 +  # Consumables
            self.MAX_SHOP_ITEMS * 3  # Shop items (type, cost, purchasable)
        )

    def tokenize_card(self, card: CardData) -> list[float]:
        """Tokenize a single card.

        Args:
            card: Card data to tokenize

        Returns:
            List of float features
        """
        rank = 0
        if card.rank:
            rank = self.RANK_MAP.get(str(card.rank), 0)
            if rank == 0:
                # Try numeric rank
                try:
                    rank = int(card.rank)
                except (ValueError, TypeError):
                    rank = 0

        suit = 0
        if card.suit:
            suit = self.SUIT_MAP.get(card.suit, 0)

        edition = 0
        if card.edition:
            edition = self.EDITION_MAP.get(card.edition, 0)

        enhancement = vocab.lookup(vocab.ENHANCEMENT_IDS, card.enhancement)

        # Seal encoding
        seal_map = {"Gold": 1, "Red": 2, "Blue": 3, "Purple": 4}
        seal = seal_map.get(card.seal, 0) if card.seal else 0

        return [
            rank / 14.0,  # Normalized rank
            suit / 4.0,   # Normalized suit
            edition / 4.0,
            enhancement / self.VOCAB["enhancement"],
            seal / 4.0,
            1.0 if card.debuffed else 0.0,
            1.0 if card.highlighted else 0.0,
            (card.hand_index or 0) / self.MAX_HAND_SIZE,
        ]

    def tokenize_joker(self, joker: JokerData) -> list[float]:
        """Tokenize a joker.

        Args:
            joker: Joker data to tokenize

        Returns:
            List of float features
        """
        joker_id = vocab.lookup(vocab.JOKER_IDS, joker.key)

        return [
            joker_id / self.VOCAB["joker"],
            (joker.rarity or 1) / 4.0,  # Rarity 1-4
            joker.sell_cost / 20.0,  # Normalize sell cost
            1.0 if joker.ability else 0.0,
        ]

    def tokenize_state(self, state: GameState) -> torch.Tensor:
        """Tokenize a complete game state into a tensor.

        Args:
            state: Game state to tokenize

        Returns:
            Float tensor of shape (obs_size,)
        """
        features = []

        # Scalar features (normalized)
        features.append(self.PHASE_MAP.get(state.phase, 8) / len(self.PHASE_MAP))
        features.append(min(state.money, 500) / 500.0)  # Cap at 500
        features.append(state.ante / 8.0)  # 8 antes max
        features.append(state.round / 32.0)  # ~32 rounds per ante
        # Normalize by the run's per-round allowance (deck backs and vouchers change it)
        hands_per_round = state.hands_per_round or 5
        discards_per_round = state.discards_per_round or 5
        features.append(state.hands_remaining / max(hands_per_round, 1))
        features.append(state.discards_remaining / max(discards_per_round, 1))

        # Blind info
        chips_needed = state.blind.chips_needed if state.blind else 0
        chips_scored = state.blind.chips_scored if state.blind else 0
        # Log scale for chips (can be very large)
        import math
        features.append(math.log10(max(chips_needed, 1)) / 12.0)  # Log10 scale
        features.append(math.log10(max(chips_scored, 1)) / 12.0)

        # Deck counts
        features.append(state.deck_counts.deck_size / 52.0)
        features.append(state.deck_counts.discard_size / 52.0)

        # Run rules (0.0 when the bridge did not report them)
        features.append((state.joker_slots or 0) / self.MAX_JOKERS)
        features.append((state.consumable_slots or 0) / self.MAX_CONSUMABLES)
        features.append((state.hand_size or 0) / self.MAX_HAND_SIZE)
        features.append(1.0 if state.no_interest else 0.0)

        # Hand cards (pad to MAX_HAND_SIZE)
        for i in range(self.MAX_HAND_SIZE):
            if i < len(state.hand):
                features.extend(self.tokenize_card(state.hand[i]))
            else:
                features.extend([0.0] * self.card_features)

        # Jokers (pad to MAX_JOKERS)
        for i in range(self.MAX_JOKERS):
            if i < len(state.jokers):
                features.extend(self.tokenize_joker(state.jokers[i]))
            else:
                features.extend([0.0] * 4)

        # Consumables (pad to MAX_CONSUMABLES)
        for i in range(self.MAX_CONSUMABLES):
            if i < len(state.consumables):
                cons = state.consumables[i]
                cons_id = vocab.lookup(vocab.CONSUMABLE_IDS, cons.key)
                features.extend([cons_id / self.VOCAB["consumable"], 1.0])
            else:
                features.extend([0.0, 0.0])

        # Shop items (pad to MAX_SHOP_ITEMS) — flatten jokers+vouchers+boosters
        shop_items = []
        if state.shop:
            shop_items = list(state.shop.jokers) + list(state.shop.vouchers) + list(state.shop.boosters)
        for i in range(self.MAX_SHOP_ITEMS):
            if i < len(shop_items):
                item = shop_items[i]
                set_id = vocab.lookup(vocab.ITEM_SET_IDS, item.type)
                features.extend([
                    set_id / self.VOCAB["item_set"],
                    item.cost / 50.0,  # Normalize cost
                    1.0 if item.cost <= state.money else 0.0,  # Purchasable flag
                ])
            else:
                features.extend([0.0, 0.0, 0.0])

        return torch.tensor(features, dtype=torch.float32, device=self.device)

    def get_observation_size(self) -> int:
        """Get the observation vector size."""
        return self.obs_size

    def batch_tokenize(self, states: list[GameState]) -> torch.Tensor:
        """Tokenize a batch of states.

        Args:
            states: List of game states

        Returns:
            Float tensor of shape (batch_size, obs_size)
        """
        tensors = [self.tokenize_state(s) for s in states]
        return torch.stack(tensors)
