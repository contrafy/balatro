"""Pydantic schemas for Balatro game state, legal actions, and action results.

State models keep every field the bridge sends (`extra="allow"`): datasets and replays must not lose
information when a state passes through these models. Shapes: docs/DATA_CONTRACT.md.
"""

from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OpenModel(BaseModel):
    """Base for bridge payloads: unknown fields are kept, never dropped."""
    model_config = ConfigDict(extra="allow")


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
    WIN = "WIN"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: str) -> "GamePhase":
        # Handle STATE_N patterns and other unknown states
        if value and value.startswith("STATE_"):
            return cls.UNKNOWN
        return cls.UNKNOWN


class CardData(OpenModel):
    """A playing card in hand or deck. Face-down cards carry no id or identity (hidden information)."""
    id: Optional[str] = None
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
    perma_bonus: float = 0
    perma_mult: float = 0

    @model_validator(mode="before")
    @classmethod
    def mirror_bridge_keys(cls, data: Any) -> Any:
        # Bridge 2.x reports `debuff` and the 1-based position as `index`; keep both spellings.
        if isinstance(data, dict):
            if "debuffed" not in data and "debuff" in data:
                data = {**data, "debuffed": bool(data["debuff"])}
            if "hand_index" not in data and isinstance(data.get("index"), int):
                data = {**data, "hand_index": data["index"]}
        return data

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_string(cls, v):
        return str(v) if v is not None else v

    @field_validator("rank", mode="before")
    @classmethod
    def coerce_rank_to_string(cls, v):
        return str(v) if v is not None else v


class JokerData(OpenModel):
    """A joker card. Face-down jokers (Amber Acorn) carry no id or identity."""
    id: Optional[str] = None
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


class ConsumableData(OpenModel):
    """A consumable card (tarot, planet, spectral)."""
    index: int
    name: Optional[str] = None
    key: Optional[str] = None
    type: Optional[str] = None  # Tarot/Planet/Spectral
    can_use: bool = False
    ability: Optional[dict[str, Any]] = None


class BlindData(OpenModel):
    """Current blind information."""
    name: Optional[str] = None
    chips_needed: Optional[int] = None
    chips_scored: int = 0
    boss: bool = False
    debuff_text: Optional[str] = None


class ShopCard(OpenModel):
    """A card in a shop area (jokers, vouchers, or boosters)."""
    index: int
    name: Optional[str] = None
    key: Optional[str] = None
    cost: int = 0
    type: str = "unknown"
    edition: Optional[str] = None
    sell_cost: int = 0
    ability: Optional[dict[str, Any]] = None


class ShopData(OpenModel):
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


class PackData(OpenModel):
    """Pack opening state."""
    cards: list[dict[str, Any]] = Field(default_factory=list)
    choices_remaining: int = 1

    @field_validator("cards", mode="before")
    @classmethod
    def convert_empty_dict_to_list(cls, v):
        if isinstance(v, dict) and len(v) == 0:
            return []
        return v


class DeckCounts(OpenModel):
    """Deck and discard pile sizes."""
    deck_size: int = 0
    discard_size: int = 0


class HandLevel(OpenModel):
    """Poker hand upgrade level and play counts."""
    level: int = 1
    mult: Optional[float] = None
    chips: Optional[int] = None
    played: int = 0
    played_this_round: int = 0


class TagData(OpenModel):
    """A tag held from skipping a blind."""
    key: Optional[str] = None
    name: Optional[str] = None
    orbital_hand: Optional[str] = None


class BlindChoice(OpenModel):
    """One of the upcoming blinds offered on the blind-select screen."""
    key: Optional[str] = None
    name: Optional[str] = None
    chips: Optional[int] = None
    state: Optional[str] = None
    tag: Optional[str] = None
    tag_key: Optional[str] = None
    orbital_hand: Optional[str] = None


class BlindSelectData(OpenModel):
    """Blind-select screen: which blind is next and what each option offers."""
    on_deck: Optional[str] = None
    choices: dict[str, BlindChoice] = Field(default_factory=dict)


class DeckComposition(OpenModel):
    """Draw-pile composition; reflects deck backs (Abandoned, Checkered, Erratic) and mid-run changes."""
    total_cards: int = 0
    by_suit: dict[str, int] = Field(default_factory=dict)
    by_rank: dict[str, int] = Field(default_factory=dict)
    face_cards: int = 0


class ShopRates(OpenModel):
    """Shop appearance weights (Ghost Deck raises spectral, vouchers raise tarot/planet)."""
    joker: Optional[float] = None
    tarot: Optional[float] = None
    planet: Optional[float] = None
    spectral: Optional[float] = None
    playing_card: Optional[float] = None


class GameState(OpenModel):
    """Complete game state snapshot (GET /state)."""
    schema_version: str
    timestamp_ms: int = 0  # envelope field; absent in recorded step.obs
    phase: GamePhase
    phase_raw: Optional[str] = None  # Original phase string before enum mapping
    error: Optional[str] = None
    # True when the game is at a stable decision point and accepts actions.
    settled: Optional[bool] = None
    won: bool = False
    # Poker hand of the currently highlighted cards.
    preview: Optional[dict[str, Any]] = None

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
        """Whether the bridge accepts actions now (falls back to the phase for old bridges)."""
        if self.settled is not None:
            return self.settled
        return self.phase in {
            GamePhase.SELECTING_HAND,
            GamePhase.SHOP,
            GamePhase.BLIND_SELECT,
            GamePhase.PACK_OPENING,
            GamePhase.ROUND_EVAL,
        }


class ActionType(str, Enum):
    """Action types of the bridge Action API (docs/DATA_CONTRACT.md)."""
    START_RUN = "START_RUN"
    SELECT_BLIND = "SELECT_BLIND"
    SKIP_BLIND = "SKIP_BLIND"
    REROLL_BOSS = "REROLL_BOSS"
    PLAY_HAND = "PLAY_HAND"
    DISCARD = "DISCARD"
    REORDER = "REORDER"
    SORT_HAND = "SORT_HAND"
    USE_CONSUMABLE = "USE_CONSUMABLE"
    SELL_JOKER = "SELL_JOKER"
    SELL_CONSUMABLE = "SELL_CONSUMABLE"
    CASH_OUT = "CASH_OUT"
    SHOP_BUY = "SHOP_BUY"
    SHOP_BUY_AND_USE = "SHOP_BUY_AND_USE"
    SHOP_BUY_VOUCHER = "SHOP_BUY_VOUCHER"
    SHOP_BUY_BOOSTER = "SHOP_BUY_BOOSTER"
    SHOP_REROLL = "SHOP_REROLL"
    SHOP_END = "SHOP_END"
    SELECT_PACK_CARD = "SELECT_PACK_CARD"
    SKIP_PACK = "SKIP_PACK"


class LegalAction(OpenModel):
    """One /legal entry: `params` maps each param name to its domain (`one_of`, `subset`,
    `permutation`, `seed`; see balatro_env.data.legality). `info` is non-normative (cost, name, key)."""
    type: ActionType
    description: Optional[str] = None
    params: dict[str, dict[str, Any]] = Field(default_factory=dict)
    info: dict[str, Any] = Field(default_factory=dict)

    @field_validator("params", "info", mode="before")
    @classmethod
    def convert_empty_list_to_dict(cls, v):
        # Lua encodes empty tables as []
        if isinstance(v, list) and len(v) == 0:
            return {}
        return v

    def options(self, name: str) -> list[Any]:
        """Values of a `one_of` param domain ([] when absent or not a one_of)."""
        domain = self.params.get(name) or {}
        values = domain.get("one_of")
        return list(values) if isinstance(values, list) else []

    def subset(self, name: str) -> Optional[dict[str, Any]]:
        """The `subset` spec {of, min, max, must_include?} of a param, if any."""
        domain = self.params.get(name) or {}
        spec = domain.get("subset")
        return spec if isinstance(spec, dict) else None

    def to_request(self) -> "ActionRequest":
        """Concrete request when every required param domain is a single-valued `one_of`."""
        params: dict[str, Any] = {}
        for name, domain in self.params.items():
            values = domain.get("one_of")
            if isinstance(values, list) and len(values) == 1:
                params[name] = values[0]
            elif not domain.get("optional") and not (
                name == "targets" and (domain.get("subset") or {}).get("min", 0) == 0
            ):
                raise ValueError(f"{self.type.value}: param {name!r} needs a choice from {domain}")
        return ActionRequest(type=self.type, params=params)


class LegalActions(OpenModel):
    """Set of legal actions available in current state (GET /legal). Empty unless `settled`."""
    schema_version: str
    phase: GamePhase
    settled: Optional[bool] = None
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
    """Request to execute an action. `meta` is stored verbatim on the recorded step (e.g. meta.why)."""
    type: ActionType
    params: dict[str, Any] = Field(default_factory=dict)
    meta: Optional[dict[str, Any]] = None


class ActionResult(OpenModel):
    """Result of executing an action (`retry` = not settled yet, resend later)."""
    ok: bool
    error: Optional[str] = None
    retry: Optional[bool] = None
    state: Optional[GameState] = None
    legal: Optional[LegalActions] = None


class HealthResponse(OpenModel):
    """Health check response."""
    status: str
    version: str
    uptime_ms: int
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
