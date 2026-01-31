"""Pydantic schemas for Balatro game state, legal actions, and action results."""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class GamePhase(str, Enum):
    """Possible game phases/states."""
    MENU = "MENU"
    SPLASH = "SPLASH"
    SELECTING_HAND = "SELECTING_HAND"
    HAND_PLAYED = "HAND_PLAYED"
    DRAW_TO_HAND = "DRAW_TO_HAND"
    BLIND_SELECT = "BLIND_SELECT"
    SHOP = "SHOP"
    PACK_OPENING = "PACK_OPENING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: str) -> "GamePhase":
        # Handle STATE_N patterns and other unknown states
        if value and value.startswith("STATE_"):
            return cls.UNKNOWN
        return cls.UNKNOWN


class CardData(BaseModel):
    """A playing card in hand or deck."""
    id: str
    rank: Optional[Union[str, int]] = None
    suit: Optional[str] = None
    name: Optional[str] = None
    edition: Optional[str] = None
    enhancement: Optional[str] = None
    seal: Optional[str] = None
    debuffed: bool = False
    facing: str = "front"
    highlighted: bool = False
    hand_index: Optional[int] = None
    area_index: Optional[int] = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_string(cls, v):
        return str(v) if v is not None else v

    @field_validator("rank", mode="before")
    @classmethod
    def coerce_rank_to_string(cls, v):
        return str(v) if v is not None else v


class JokerData(BaseModel):
    """A joker card."""
    id: str
    name: Optional[str] = None
    key: Optional[str] = None
    rarity: Optional[int] = None
    sell_cost: int = 0
    ability: Optional[dict[str, Any]] = None
    edition: Optional[dict[str, Any]] = None
    joker_index: Optional[int] = None
    area_index: Optional[int] = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_string(cls, v):
        return str(v) if v is not None else v


class ConsumableData(BaseModel):
    """A consumable card (tarot, planet, spectral)."""
    index: int
    name: Optional[str] = None
    key: Optional[str] = None


class BlindData(BaseModel):
    """Current blind information."""
    name: Optional[str] = None
    chips_needed: Optional[int] = None
    chips_scored: int = 0
    boss: bool = False
    debuff_text: Optional[str] = None


class ShopItem(BaseModel):
    """An item in the shop."""
    slot: int
    name: Optional[str] = None
    cost: int = 0
    type: str = "unknown"


class ShopData(BaseModel):
    """Shop state."""
    items: list[ShopItem] = Field(default_factory=list)
    reroll_cost: int = 5


class PackData(BaseModel):
    """Pack opening state."""
    cards: list[dict[str, Any]] = Field(default_factory=list)


class DeckCounts(BaseModel):
    """Deck and discard pile sizes."""
    deck_size: int = 0
    discard_size: int = 0


class HandLevel(BaseModel):
    """Poker hand upgrade level."""
    level: int = 1
    mult: Optional[float] = None
    chips: Optional[int] = None


class GameState(BaseModel):
    """Complete game state snapshot."""
    schema_version: str
    timestamp_ms: int
    phase: GamePhase
    error: Optional[str] = None

    # Run metadata
    run_id: Optional[Union[str, int]] = None
    round: int = 0
    ante: int = 0

    # Resources
    money: int = 0
    hands_remaining: int = 0
    discards_remaining: int = 0
    hands_played: int = 0

    # Current blind
    blind: Optional[BlindData] = None

    # Cards in hand
    hand: list[CardData] = Field(default_factory=list)

    # Jokers owned
    jokers: list[JokerData] = Field(default_factory=list)

    # Consumables
    consumables: list[ConsumableData] = Field(default_factory=list)

    # Shop state (when in SHOP phase)
    shop: Optional[ShopData] = None

    # Pack state (when in PACK_OPENING phase)
    pack: Optional[PackData] = None

    # Deck counts
    deck_counts: DeckCounts = Field(default_factory=DeckCounts)

    # Hand levels (poker hand upgrades)
    hand_levels: dict[str, HandLevel] = Field(default_factory=dict)

    @field_validator("jokers", "consumables", "hand", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v):
        # Lua returns {} for empty tables which becomes {} in JSON, not []
        if isinstance(v, dict) and len(v) == 0:
            return []
        return v

    @field_validator("run_id", mode="before")
    @classmethod
    def coerce_run_id_to_string(cls, v):
        return str(v) if v is not None else v

    def is_decision_point(self) -> bool:
        """Check if current phase requires a decision from the player."""
        return self.phase in {
            GamePhase.SELECTING_HAND,
            GamePhase.SHOP,
            GamePhase.BLIND_SELECT,
            GamePhase.PACK_OPENING,
        }


class ActionType(str, Enum):
    """Types of actions that can be taken."""
    PLAY_HAND = "PLAY_HAND"
    DISCARD = "DISCARD"
    SORT_HAND = "SORT_HAND"
    SHOP_BUY = "SHOP_BUY"
    SHOP_REROLL = "SHOP_REROLL"
    SHOP_SELL_JOKER = "SHOP_SELL_JOKER"
    SHOP_END = "SHOP_END"
    SELECT_BLIND = "SELECT_BLIND"
    SKIP_BLIND = "SKIP_BLIND"
    SELECT_PACK_ITEM = "SELECT_PACK_ITEM"
    SKIP_PACK = "SKIP_PACK"


class ActionParams(BaseModel):
    """Parameters for an action."""
    card_indices: Optional[dict[str, Any]] = None
    mode: Optional[list[str]] = None
    slot: Optional[int] = None
    cost: Optional[int] = None
    joker_index: Optional[int] = None
    sell_value: Optional[int] = None
    options: Optional[list[str]] = None
    choice_index: Optional[int] = None


class LegalAction(BaseModel):
    """A single legal action that can be taken."""
    type: ActionType
    description: str
    params: ActionParams = Field(default_factory=ActionParams)


class LegalActions(BaseModel):
    """Set of legal actions available in current state."""
    schema_version: str
    phase: GamePhase
    actions: list[LegalAction] = Field(default_factory=list)
    error: Optional[str] = None

    def has_action_type(self, action_type: ActionType) -> bool:
        """Check if a specific action type is available."""
        return any(a.type == action_type for a in self.actions)

    def get_actions_of_type(self, action_type: ActionType) -> list[LegalAction]:
        """Get all actions of a specific type."""
        return [a for a in self.actions if a.type == action_type]


class ActionRequest(BaseModel):
    """Request to execute an action."""
    type: ActionType
    params: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    """Result of executing an action."""
    ok: bool
    error: Optional[str] = None
    state: Optional[GameState] = None
    legal: Optional[LegalActions] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_ms: int
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
