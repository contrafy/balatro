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
    GAME_OVER = "GAME_OVER"
    ROUND_EVAL = "ROUND_EVAL"
    NEW_ROUND = "NEW_ROUND"
    PLAY_TAROT = "PLAY_TAROT"
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
    type: Optional[str] = None  # Tarot/Planet/Spectral
    can_use: bool = False
    ability: Optional[dict[str, Any]] = None


class BlindData(BaseModel):
    """Current blind information."""
    name: Optional[str] = None
    chips_needed: Optional[int] = None
    chips_scored: int = 0
    boss: bool = False
    debuff_text: Optional[str] = None


class ShopCard(BaseModel):
    """A card in a shop area (jokers, vouchers, or boosters)."""
    index: int
    name: Optional[str] = None
    key: Optional[str] = None
    cost: int = 0
    type: str = "unknown"
    edition: Optional[str] = None
    sell_cost: int = 0
    ability: Optional[dict[str, Any]] = None


class ShopData(BaseModel):
    """Shop state with three separate card areas."""
    jokers: list[ShopCard] = Field(default_factory=list)
    vouchers: list[ShopCard] = Field(default_factory=list)
    boosters: list[ShopCard] = Field(default_factory=list)
    reroll_cost: int = 5

    @field_validator("jokers", "vouchers", "boosters", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v):
        if isinstance(v, dict) and len(v) == 0:
            return []
        return v


class PackData(BaseModel):
    """Pack opening state."""
    cards: list[dict[str, Any]] = Field(default_factory=list)
    choices_remaining: int = 1

    @field_validator("cards", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v):
        if isinstance(v, dict) and len(v) == 0:
            return []
        return v


class DeckCounts(BaseModel):
    """Deck and discard pile sizes."""
    deck_size: int = 0
    discard_size: int = 0


class HandLevel(BaseModel):
    """Poker hand upgrade level."""
    level: int = 1
    mult: Optional[float] = None
    chips: Optional[int] = None


class TagData(BaseModel):
    """A tag held from skipping a blind."""
    key: Optional[str] = None
    name: Optional[str] = None
    orbital_hand: Optional[str] = None


class BlindChoice(BaseModel):
    """One of the upcoming blinds offered on the blind-select screen."""
    key: Optional[str] = None
    name: Optional[str] = None
    chips: Optional[int] = None
    state: Optional[str] = None
    tag: Optional[str] = None
    tag_key: Optional[str] = None
    orbital_hand: Optional[str] = None


class BlindSelectData(BaseModel):
    """Blind-select screen: which blind is next and what each option offers."""
    on_deck: Optional[str] = None
    choices: dict[str, BlindChoice] = Field(default_factory=dict)


class DeckComposition(BaseModel):
    """Draw-pile composition; reflects deck backs (Abandoned, Checkered, Erratic) and mid-run changes."""
    total_cards: int = 0
    by_suit: dict[str, int] = Field(default_factory=dict)
    by_rank: dict[str, int] = Field(default_factory=dict)
    face_cards: int = 0


class ShopRates(BaseModel):
    """Shop appearance weights (Ghost Deck raises spectral, vouchers raise tarot/planet)."""
    joker: Optional[float] = None
    tarot: Optional[float] = None
    planet: Optional[float] = None
    spectral: Optional[float] = None
    playing_card: Optional[float] = None


class GameState(BaseModel):
    """Complete game state snapshot."""
    schema_version: str
    timestamp_ms: int
    phase: GamePhase
    phase_raw: Optional[str] = None  # Original phase string before enum mapping
    error: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def preserve_raw_phase(cls, data: Any) -> Any:
        if isinstance(data, dict) and "phase" in data:
            data["phase_raw"] = data["phase"]
        return data

    # Run metadata
    run_id: Optional[Union[str, int]] = None
    deck_name: Optional[str] = None
    deck_key: Optional[str] = None
    deck_config: dict[str, Any] = Field(default_factory=dict)
    stake: Optional[int] = None
    win_ante: Optional[int] = None
    round: int = 0
    ante: int = 0

    # Run rules read from the live game (deck backs, vouchers, stakes and mods all change these).
    # None means the bridge did not report the value; never substitute a Red Deck default.
    joker_slots: Optional[int] = None
    consumable_slots: Optional[int] = None
    hand_size: Optional[int] = None
    hands_per_round: Optional[int] = None
    discards_per_round: Optional[int] = None
    interest_amount: Optional[int] = None
    interest_cap: Optional[int] = None
    no_interest: bool = False
    modifiers: dict[str, Any] = Field(default_factory=dict)
    starting_params: dict[str, Any] = Field(default_factory=dict)
    shop_rates: Optional[ShopRates] = None
    used_vouchers: list[str] = Field(default_factory=list)
    tags: list[TagData] = Field(default_factory=list)
    blind_select: Optional[BlindSelectData] = None

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
    deck_composition: Optional[DeckComposition] = None

    # Hand levels (poker hand upgrades)
    hand_levels: dict[str, HandLevel] = Field(default_factory=dict)

    @field_validator("jokers", "consumables", "hand", "used_vouchers", "tags", mode="before")
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

    @property
    def joker_slots_free(self) -> Optional[int]:
        """Free joker slots per the live limit, or None when the bridge did not report one."""
        if self.joker_slots is None:
            return None
        return self.joker_slots - len(self.jokers)

    @property
    def consumable_slots_free(self) -> Optional[int]:
        """Free consumable slots per the live limit, or None when unknown."""
        if self.consumable_slots is None:
            return None
        return self.consumable_slots - len(self.consumables)

    def can_add_joker(self) -> bool:
        """Whether another joker fits. Unknown limit defers to the bridge's legal actions."""
        free = self.joker_slots_free
        return free is None or free > 0

    def can_add_consumable(self) -> bool:
        """Whether another consumable fits. Unknown limit defers to the bridge's legal actions."""
        free = self.consumable_slots_free
        return free is None or free > 0

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
    SELECT_CARDS = "SELECT_CARDS"
    PLAY_HAND = "PLAY_HAND"
    DISCARD = "DISCARD"
    SORT_HAND = "SORT_HAND"
    SHOP_BUY = "SHOP_BUY"
    SHOP_BUY_VOUCHER = "SHOP_BUY_VOUCHER"
    SHOP_BUY_BOOSTER = "SHOP_BUY_BOOSTER"
    SHOP_REROLL = "SHOP_REROLL"
    SHOP_SELL_JOKER = "SHOP_SELL_JOKER"
    SHOP_END = "SHOP_END"
    SELECT_BLIND = "SELECT_BLIND"
    SKIP_BLIND = "SKIP_BLIND"
    SELECT_PACK_CARD = "SELECT_PACK_CARD"
    SELECT_PACK_ITEM = "SELECT_PACK_ITEM"  # legacy alias
    SKIP_PACK = "SKIP_PACK"
    USE_CONSUMABLE = "USE_CONSUMABLE"
    CASH_OUT = "CASH_OUT"
    START_RUN = "START_RUN"
    REORDER_JOKERS = "REORDER_JOKERS"
    SELL_CONSUMABLE = "SELL_CONSUMABLE"


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
    index: Optional[int] = None  # for pack card selection, consumable use
    stake: Optional[int] = None
    order: Optional[list[int]] = None  # for REORDER_JOKERS


class LegalAction(BaseModel):
    """A single legal action that can be taken."""
    type: ActionType
    description: str
    params: ActionParams = Field(default_factory=ActionParams)

    def to_request(self) -> "ActionRequest":
        """Convert to an ActionRequest for execution."""
        return ActionRequest(
            type=self.type,
            params=self.params.model_dump(exclude_none=True),
        )


class LegalActions(BaseModel):
    """Set of legal actions available in current state."""
    schema_version: str
    phase: GamePhase
    actions: list[LegalAction] = Field(default_factory=list)
    error: Optional[str] = None

    @field_validator("actions", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v):
        if isinstance(v, dict) and len(v) == 0:
            return []
        return v

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
