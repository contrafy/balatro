"""Deterministic strategy for Balatro autopilot.

Provides a rule-based decision engine for each game phase.
Not optimal — designed to be "working and somewhat reasonable"
as a baseline that can be refined phase-by-phase.
"""

from collections import Counter
from itertools import combinations
from typing import Any

from balatro_env.schemas import (
    ActionRequest,
    ActionType,
    CardData,
    GameState,
    LegalAction,
    LegalActions,
)

# ---------------------------------------------------------------------------
# Card value helpers
# ---------------------------------------------------------------------------

RANK_ORDER = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
    "9": 9, "10": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14,
}

# Chip value each card adds when scored
RANK_CHIPS = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
    "9": 9, "10": 10, "Jack": 10, "Queen": 10, "King": 10, "Ace": 11,
}


def rank_val(card: CardData | dict) -> int:
    r = card.get("rank") if isinstance(card, dict) else card.rank
    return RANK_ORDER.get(str(r), 0)


def rank_chips(card: CardData | dict) -> int:
    r = card.get("rank") if isinstance(card, dict) else card.rank
    return RANK_CHIPS.get(str(r), 0)


def card_suit(card: CardData | dict) -> str:
    return (card.get("suit") if isinstance(card, dict) else card.suit) or ""


def card_index(card: CardData | dict) -> int:
    if isinstance(card, dict):
        return card.get("hand_index") or card.get("area_index") or 0
    return card.hand_index or card.area_index or 0


def card_label(card: CardData | dict) -> str:
    r = card.get("rank") if isinstance(card, dict) else card.rank
    s = card.get("suit") if isinstance(card, dict) else card.suit
    suit_sym = {"Hearts": "H", "Diamonds": "D", "Clubs": "C", "Spades": "S"}
    return f"{r}{suit_sym.get(s or '', '?')}"


# ---------------------------------------------------------------------------
# Poker hand detection
# ---------------------------------------------------------------------------

# (hand_name, base_chips, base_mult) — from Balatro defaults at level 1
HAND_SCORES: dict[str, tuple[int, int]] = {
    "Straight Flush": (100, 8),
    "Four of a Kind":  (60, 7),
    "Full House":      (40, 4),
    "Flush":           (35, 4),
    "Straight":        (30, 4),
    "Three of a Kind": (30, 3),
    "Two Pair":        (20, 2),
    "Pair":            (10, 2),
    "High Card":       (5,  1),
}


def _is_straight(ranks: list[int]) -> bool:
    """Check if sorted unique ranks form a straight (5 cards)."""
    if len(ranks) != 5:
        return False
    s = sorted(set(ranks))
    if len(s) != 5:
        return False
    # Normal straight
    if s[-1] - s[0] == 4:
        return True
    # Ace-low: A-2-3-4-5
    if s == [2, 3, 4, 5, 14]:
        return True
    return False


def classify_hand(cards: list) -> tuple[str, int, int]:
    """Classify a set of 1-5 cards as a poker hand.

    Returns (hand_name, base_chips, base_mult).
    """
    n = len(cards)
    ranks = [rank_val(c) for c in cards]
    suits = [card_suit(c) for c in cards]
    rc = Counter(ranks)
    mc = rc.most_common()

    is_flush = n == 5 and len(set(suits)) == 1
    is_straight = _is_straight(ranks)

    if n == 5 and is_straight and is_flush:
        return "Straight Flush", *HAND_SCORES["Straight Flush"]
    if mc[0][1] >= 4:
        return "Four of a Kind", *HAND_SCORES["Four of a Kind"]
    if mc[0][1] == 3 and len(mc) > 1 and mc[1][1] == 2:
        return "Full House", *HAND_SCORES["Full House"]
    if is_flush:
        return "Flush", *HAND_SCORES["Flush"]
    if is_straight:
        return "Straight", *HAND_SCORES["Straight"]
    if mc[0][1] == 3:
        return "Three of a Kind", *HAND_SCORES["Three of a Kind"]
    if mc[0][1] == 2 and len(mc) > 1 and mc[1][1] == 2:
        return "Two Pair", *HAND_SCORES["Two Pair"]
    if mc[0][1] == 2:
        return "Pair", *HAND_SCORES["Pair"]
    return "High Card", *HAND_SCORES["High Card"]


def estimate_score(cards: list, hand_levels: dict | None = None) -> tuple[str, float]:
    """Estimate the score from playing these cards.

    Returns (hand_name, estimated_total_score).
    """
    hand_name, base_chips, base_mult = classify_hand(cards)

    # Use actual hand levels if provided
    if hand_levels and hand_name in hand_levels:
        hl = hand_levels[hand_name]
        lvl_chips = hl.get("chips", base_chips) if isinstance(hl, dict) else (hl.chips or base_chips)
        lvl_mult = hl.get("mult", base_mult) if isinstance(hl, dict) else (hl.mult or base_mult)
    else:
        lvl_chips = base_chips
        lvl_mult = base_mult

    # Add chip values of scored cards
    total_chips = lvl_chips + sum(rank_chips(c) for c in cards)
    return hand_name, total_chips * lvl_mult


# ---------------------------------------------------------------------------
# Hand selection: find best 5-card (or fewer) combo
# ---------------------------------------------------------------------------

def find_best_play(hand: list[CardData], hand_levels: dict | None = None) -> tuple[list[CardData], str, float]:
    """Find the best hand to play from available cards.

    Tries all combinations of 1-5 cards and picks the highest scoring one.
    Returns (selected_cards, hand_name, estimated_score).
    """
    best_cards: list[CardData] = []
    best_name = "High Card"
    best_score = -1.0

    # Try 5-card combos first (most hand types need 5), then smaller
    for size in range(min(5, len(hand)), 0, -1):
        for combo in combinations(hand, size):
            name, score = estimate_score(list(combo), hand_levels)
            if score > best_score:
                best_score = score
                best_cards = list(combo)
                best_name = name

    return best_cards, best_name, best_score


# ---------------------------------------------------------------------------
# Discard selection: throw away lowest-value cards not part of potential hands
# ---------------------------------------------------------------------------

def find_best_discard(hand: list[CardData], hand_levels: dict | None = None) -> list[CardData]:
    """Pick cards to discard — remove cards least likely to contribute to a good hand.

    Strategy: keep cards that are part of the best potential hand, discard the rest
    (up to 5 cards).
    """
    if len(hand) <= 5:
        return []

    # Find best hand we could play
    best_cards, _, _ = find_best_play(hand, hand_levels)
    best_indices = {card_index(c) for c in best_cards}

    # Everything not in the best hand is a discard candidate
    discard_pool = [c for c in hand if card_index(c) not in best_indices]

    # Sort by rank value ascending (discard lowest first)
    discard_pool.sort(key=lambda c: rank_val(c))

    # Discard up to 5
    return discard_pool[:5]


# ---------------------------------------------------------------------------
# Strategy decisions per phase
# ---------------------------------------------------------------------------

class Decision:
    """A strategy decision with reasoning."""

    def __init__(self, action: ActionRequest, reason: str, cards_label: str = ""):
        self.action = action
        self.reason = reason
        self.cards_label = cards_label

    def __repr__(self):
        return f"Decision({self.action.type.value}: {self.reason})"


def decide_selecting_hand(state: GameState, legal: LegalActions) -> Decision:
    """Decide what to do during SELECTING_HAND phase.

    Strategy:
    1. If we have discards and our best hand scores < chips_needed / hands_remaining,
       discard weak cards to try for a better hand.
    2. Otherwise, play the best hand we can find.
    """
    hand = state.hand
    if not hand:
        return Decision(
            ActionRequest(type=ActionType.PLAY_HAND, params={"card_indices": [1]}),
            "No hand data — panic play",
        )

    hand_levels_dict = None
    if state.hand_levels:
        hand_levels_dict = {
            k: {"chips": v.chips, "mult": v.mult, "level": v.level}
            for k, v in state.hand_levels.items()
        }

    best_cards, best_name, best_score = find_best_play(hand, hand_levels_dict)
    best_indices = [card_index(c) for c in best_cards]
    cards_str = " ".join(card_label(c) for c in best_cards)

    chips_needed = 0
    chips_scored = 0
    if state.blind:
        chips_needed = state.blind.chips_needed or 0
        chips_scored = state.blind.chips_scored or 0
    remaining_target = chips_needed - chips_scored
    hands_left = state.hands_remaining

    # Should we discard?
    if state.discards_remaining > 0 and hands_left > 1:
        # If our best hand won't come close, try discarding
        score_per_hand_needed = remaining_target / max(hands_left, 1)
        if best_score < score_per_hand_needed * 0.7:
            discard_cards = find_best_discard(hand, hand_levels_dict)
            if discard_cards:
                discard_indices = [card_index(c) for c in discard_cards]
                discard_str = " ".join(card_label(c) for c in discard_cards)
                return Decision(
                    ActionRequest(type=ActionType.DISCARD, params={"card_indices": discard_indices}),
                    f"Best hand {best_name} (~{best_score:.0f}) too weak for target "
                    f"(~{score_per_hand_needed:.0f}/hand), discarding {len(discard_cards)} cards",
                    discard_str,
                )

    return Decision(
        ActionRequest(type=ActionType.PLAY_HAND, params={"card_indices": best_indices}),
        f"Playing {best_name} (est. {best_score:.0f} chips, need {remaining_target})",
        cards_str,
    )


def decide_blind_select(state: GameState, legal: LegalActions) -> Decision:
    """Decide during BLIND_SELECT phase.

    Strategy: Always select the blind (skip is only useful with specific tags).
    Skip if it's a small/big blind and we have a skip tag, but for simplicity
    just always select.
    """
    return Decision(
        ActionRequest(type=ActionType.SELECT_BLIND, params={}),
        "Select blind (always play)",
    )


def decide_shop(state: GameState, legal: LegalActions) -> Decision:
    """Decide what to do in the SHOP phase.

    Strategy priority:
    1. Buy affordable jokers (they're the biggest power multiplier)
    2. Buy affordable boosters if we can
    3. Reroll once if we have plenty of money and nothing good
    4. End shop
    """
    money = state.money

    # Check for affordable joker buys
    buy_actions = legal.get_actions_of_type(ActionType.SHOP_BUY)
    for action in buy_actions:
        cost = action.params.cost or 0
        if cost <= money:
            return Decision(
                action.to_request(),
                f"Buy from shop (${cost})",
            )

    # Buy voucher if affordable
    voucher_actions = legal.get_actions_of_type(ActionType.SHOP_BUY_VOUCHER)
    for action in voucher_actions:
        cost = action.params.cost or 0
        if cost <= money:
            return Decision(
                action.to_request(),
                f"Buy voucher (${cost})",
            )

    # Reroll if we have money to spare (>= reroll_cost + 5 buffer)
    reroll_actions = legal.get_actions_of_type(ActionType.SHOP_REROLL)
    reroll_cost = 0
    if state.shop:
        reroll_cost = state.shop.reroll_cost
    for action in reroll_actions:
        if money >= reroll_cost + 5:
            return Decision(
                action.to_request(),
                f"Reroll shop (${reroll_cost}, have ${money})",
            )

    # End shop
    return Decision(
        ActionRequest(type=ActionType.SHOP_END),
        "Leave shop",
    )


def decide_pack_opening(state: GameState, legal: LegalActions) -> Decision:
    """Decide during PACK_OPENING phase.

    Strategy: Pick the first available card (any card from a pack is usually good).
    Skip if no selections remain.
    """
    pick_actions = legal.get_actions_of_type(ActionType.SELECT_PACK_CARD)
    if pick_actions:
        action = pick_actions[0]
        return Decision(
            action.to_request(),
            f"Pick card from pack: {action.description}",
        )

    # Legacy action type
    pick_legacy = legal.get_actions_of_type(ActionType.SELECT_PACK_ITEM)
    if pick_legacy:
        action = pick_legacy[0]
        return Decision(
            action.to_request(),
            f"Pick item from pack: {action.description}",
        )

    return Decision(
        ActionRequest(type=ActionType.SKIP_PACK),
        "Skip pack (no picks available or choices exhausted)",
    )


def decide_round_eval(state: GameState, legal: LegalActions) -> Decision:
    """Decide during ROUND_EVAL — cash out to proceed to the shop."""
    return Decision(
        ActionRequest(type=ActionType.CASH_OUT),
        "Cash out to proceed to shop",
    )


def decide_game_over(state: GameState, legal: LegalActions) -> Decision:
    """Decide during GAME_OVER — start a new run."""
    return Decision(
        ActionRequest(type=ActionType.START_RUN, params={"stake": 1}),
        "Game over — starting new run",
    )


def decide_menu(state: GameState, legal: LegalActions) -> Decision:
    """Decide from MENU — start a new run."""
    return Decision(
        ActionRequest(type=ActionType.START_RUN, params={"stake": 1}),
        "At menu — starting new run",
    )


def decide(state: GameState, legal: LegalActions) -> Decision | None:
    """Top-level decision dispatcher.

    Returns a Decision for actionable phases, or None for transitional phases
    (HAND_PLAYED, DRAW_TO_HAND, ROUND_EVAL, NEW_ROUND) where we just wait.
    """
    # Use raw phase string to preserve STATE_N codes before enum mapping
    phase = state.phase_raw or state.phase.value

    # Map STATE_N codes to known phases (for when mod hasn't been reloaded)
    STATE_NUM_MAP = {
        "STATE_1": "SELECTING_HAND",
        "STATE_2": "HAND_PLAYED",
        "STATE_3": "DRAW_TO_HAND",
        "STATE_4": "GAME_OVER",
        "STATE_5": "SHOP",
        "STATE_6": "PLAY_TAROT",
        "STATE_7": "BLIND_SELECT",
        "STATE_8": "ROUND_EVAL",
        "STATE_9": "PACK_OPENING",   # TAROT_PACK
        "STATE_10": "PACK_OPENING",  # PLANET_PACK
        "STATE_11": "MENU",
        "STATE_13": "SPLASH",
        "STATE_15": "PACK_OPENING",  # SPECTRAL_PACK
        "STATE_17": "PACK_OPENING",  # STANDARD_PACK
        "STATE_18": "PACK_OPENING",  # BUFFOON_PACK
        "STATE_19": "NEW_ROUND",
    }
    phase = STATE_NUM_MAP.get(phase, phase)

    if phase == "SELECTING_HAND":
        return decide_selecting_hand(state, legal)
    elif phase == "BLIND_SELECT":
        return decide_blind_select(state, legal)
    elif phase == "SHOP":
        return decide_shop(state, legal)
    elif phase == "PACK_OPENING":
        return decide_pack_opening(state, legal)
    elif phase == "ROUND_EVAL":
        return decide_round_eval(state, legal)
    elif phase == "GAME_OVER":
        return decide_game_over(state, legal)
    elif phase == "MENU":
        return decide_menu(state, legal)
    elif phase in ("HAND_PLAYED", "DRAW_TO_HAND", "NEW_ROUND", "PLAY_TAROT", "SPLASH"):
        return None  # Transitional — wait
    else:
        return None  # Unknown state — wait
