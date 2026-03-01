#!/usr/bin/env python3
"""Balatro agent - beats Red Deck on White Stake (base difficulty).

Hand strategy
  Primary:   Flush  (keep suited cards, discard off-suit aggressively)
  Fallback:  best available (full house / three-of-a-kind / pair)

Shop strategy
  * Buy jokers that add consistent mult or xmult
  * Buy planet packs to level up our most-played hand
  * Reroll at most once per shop when we have spare cash and joker space

Run loop is synchronous: each iteration fetches state + legal, decides one
action, executes it, then waits a short time for animations.
"""

import argparse
import sys
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from itertools import combinations
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from balatro_env.client import BalatroClient, BalatroConnectionError
from balatro_env.schemas import (
    ActionRequest, ActionType, CardData, GamePhase, GameState, LegalActions
)
from balatro_env.util import print_state_summary

console = Console()

# -- Card constants ------------------------------------------------------------

RANK_ORDER: dict[str, int] = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10, "T": 10,
    "J": 11, "JACK": 11,
    "Q": 12, "QUEEN": 12,
    "K": 13, "KING": 13,
    "A": 14, "ACE": 14,
}
CARD_CHIPS: dict[str, int] = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10, "T": 10,
    "J": 10, "JACK": 10,
    "Q": 10, "QUEEN": 10,
    "K": 10, "KING": 10,
    "A": 11, "ACE": 11,
}

# Hand-type constants (higher = stronger)
HC, PR, TP, TK, ST, FL, FH, FK, SF, FV, FLH, FLF = range(12)

HAND_NAMES = {
    HC: "High Card", PR: "Pair", TP: "Two Pair", TK: "Three of a Kind",
    ST: "Straight", FL: "Flush", FH: "Full House", FK: "Four of a Kind",
    SF: "Straight Flush", FV: "Five of a Kind", FLH: "Flush House", FLF: "Flush Five",
}

# (base_chips, base_mult)
HAND_BASE: dict[int, tuple[int, int]] = {
    HC: (5, 1), PR: (10, 2), TP: (20, 2), TK: (30, 3),
    ST: (30, 4), FL: (35, 4), FH: (40, 4), FK: (60, 7),
    SF: (100, 8), FV: (120, 12), FLH: (140, 14), FLF: (160, 16),
}

# Planets to deprioritize — Four of a Kind (Mars) and Straight Flush (Neptune)
# are hands the flush-first agent almost never completes intentionally.
DEPRIORITIZED_PLANETS: set[str] = {"Mars", "Neptune"}


# -- Smeared Joker helpers -----------------------------------------------------

def has_smeared_joker(jokers: "list | None") -> bool:
    """Return True if the player owns a Smeared Joker."""
    if not jokers:
        return False
    return any((j.name or "") == "Smeared Joker" for j in jokers)


def effective_suit(card: CardData, smeared: bool) -> str:
    """Return the suit used for flush grouping.

    With Smeared Joker active, Hearts/Diamonds → "Red", Clubs/Spades → "Black".
    Without it, returns the card's actual suit.
    """
    suit = card.suit or "?"
    if not smeared:
        return suit
    if suit in ("Hearts", "Diamonds"):
        return "Red"
    if suit in ("Clubs", "Spades"):
        return "Black"
    return suit


def _rank(card: CardData) -> int:
    return RANK_ORDER.get(str(card.rank or "2").upper(), 0)


def _chips(card: CardData) -> int:
    return CARD_CHIPS.get(str(card.rank or "2").upper(), 0)


# -- Hand detection ------------------------------------------------------------

def get_scoring_cards(hand_type: int, cards: list[CardData]) -> list[CardData]:
    """Return only the cards that contribute chips in Balatro scoring.

    In Balatro only the cards that FORM the hand type score — kickers do not
    add chip values.  All five cards score for Straight / Flush / Full House /
    Straight Flush / Five of a Kind / Flush variants.
    """
    if not cards:
        return []
    ranks = [_rank(c) for c in cards]
    rc = Counter(ranks)

    if hand_type == HC:
        return [max(cards, key=_rank)]

    if hand_type == PR:
        for rank in sorted(rc, reverse=True):
            if rc[rank] >= 2:
                return [c for c in cards if _rank(c) == rank][:2]

    if hand_type == TP:
        pairs = sorted([r for r, cnt in rc.items() if cnt >= 2], reverse=True)[:2]
        return [c for c in cards if _rank(c) in set(pairs)][:4]

    if hand_type == TK:
        for rank in sorted(rc, reverse=True):
            if rc[rank] >= 3:
                return [c for c in cards if _rank(c) == rank][:3]

    if hand_type == FK:
        for rank in sorted(rc, reverse=True):
            if rc[rank] >= 4:
                return [c for c in cards if _rank(c) == rank][:4]

    # ST, FL, FH, SF, FV, FLH, FLF — all played cards are scoring cards
    return list(cards)


def detect_hand(cards: list[CardData], jokers: "list | None" = None) -> int:
    """Return the hand-type constant for a list of 1-5 cards."""
    if not cards:
        return HC
    cards = cards[:5]
    ranks = [_rank(c) for c in cards]
    smeared = has_smeared_joker(jokers)
    suits = [effective_suit(c, smeared) for c in cards]
    rc = Counter(ranks)
    sc = Counter(suits)

    is_flush = len(cards) == 5 and max(sc.values()) == 5
    uniq = sorted(set(ranks))
    is_straight = (
        len(uniq) == 5 and (
            uniq[-1] - uniq[0] == 4                 # normal straight
            or uniq == [2, 3, 4, 5, 14]             # wheel (A-low)
        )
    )
    counts = sorted(rc.values(), reverse=True)

    if counts[0] == 5:
        return FLF if is_flush else FV
    if counts[0] == 4:
        return FK
    if counts[0] == 3 and len(counts) > 1 and counts[1] == 2:
        return FLH if is_flush else FH
    if is_flush and is_straight:
        return SF
    if is_flush:
        return FL
    if is_straight:
        return ST
    if counts[0] == 3:
        return TK
    if counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
        return TP
    if counts[0] == 2:
        return PR
    return HC


def estimate_score(hand_type: int, cards: list[CardData], hand_levels: dict,
                   jokers: "list | None" = None) -> float:
    """Rough score estimate: (base_chips + card_chips + joker_chips) * (base_mult + joker_mult)."""
    name = HAND_NAMES[hand_type]
    base_c, base_m = HAND_BASE[hand_type]
    hl = hand_levels.get(name)
    lvl_c = hl.chips if hl and hl.chips is not None else base_c
    lvl_m = hl.mult  if hl and hl.mult  is not None else base_m

    extra_chips = 0
    extra_mult = 0
    if jokers:
        has_face = any(_rank(c) in (11, 12, 13) for c in cards)
        has_ace  = any(_rank(c) == 14 for c in cards)
        for j in jokers:
            jname = j.name or ""
            # Flush jokers
            if hand_type == FL:
                if jname == "Droll Joker":   extra_mult  += 4
                if jname == "Crazy Joker":   extra_chips += 12
                if jname == "Smeared Joker": extra_mult  += 4   # approx
                if jname == "Runner":        extra_chips += 15  # approx (straight+flush)
            # Face-card jokers
            if has_face:
                if jname == "Smiley Face":   extra_mult  += 4
                if jname == "Scary Face":    extra_chips += 30
                if jname == "Sock and Buskin": extra_mult += 4  # retrigger approx
            # Ace joker
            if has_ace and jname == "Scholar":
                extra_chips += 20
                extra_mult  += 4
            # Always-on
            if jname == "Joker":             extra_mult  += 4
            if jname == "Jolly Joker" and hand_type in (PR, TP):  extra_mult += 8
            if jname == "Zany Joker"  and hand_type == TK:         extra_mult += 12
            if jname == "Mad Joker"   and hand_type == TP:         extra_mult += 10
            if jname == "Hiker":             extra_chips += 10   # per card approx
            if jname == "Mystic Summit":     extra_mult  += 15   # if no discards (assume best case)

    return (lvl_c + sum(_chips(c) for c in cards) + extra_chips) * (lvl_m + extra_mult)


# -- Play / discard selection --------------------------------------------------

def best_play(hand: list[CardData], hand_levels: dict,
              jokers: "list | None" = None) -> tuple[float, list[int], str]:
    """Return (score, [hand_indices], name) for the best play.

    Returns only the *scoring* card indices (no kickers).  In Balatro, kicker
    cards do not contribute chips — only the cards that form the hand type score.
    Playing kickers wastes card slots and removes good cards from your hand.
    """
    best = (-1.0, [hand[0].hand_index] if hand and hand[0].hand_index is not None else [], "High Card")
    for size in range(1, min(6, len(hand)+1)):
        for combo in combinations(range(len(hand)), size):
            cards = [hand[i] for i in combo]
            ht = detect_hand(cards, jokers)
            scoring = get_scoring_cards(ht, cards)
            sc = estimate_score(ht, scoring, hand_levels, jokers)
            if sc > best[0]:
                best = (sc,
                        [c.hand_index for c in scoring if c.hand_index is not None],
                        HAND_NAMES[ht])
    return best


def discard_for_flush(hand: list[CardData],
                      jokers: "list | None" = None) -> Optional[list[int]]:
    """Return indices to discard to chase a flush, or None if not worth it."""
    smeared = has_smeared_joker(jokers)
    suit_groups: dict[str, list[CardData]] = {}
    for c in hand:
        s = effective_suit(c, smeared)
        suit_groups.setdefault(s, []).append(c)

    best_suit = max(suit_groups, key=lambda s: len(suit_groups[s]))
    suited = suit_groups[best_suit]

    if len(suited) < 4:          # not enough suited cards to chase flush
        return None

    if len(suited) >= 5:         # already have a flush — no discard needed
        return None

    # Discard ALL off-suit cards (up to 5 at once)
    off_suit = [c.hand_index for c in hand
                if effective_suit(c, smeared) != best_suit and c.hand_index is not None]

    # Safety: only prevent discard if we'd be left with fewer than 3 cards
    # (Balatro draws back after discard, so this only matters when deck is
    # near-empty and we genuinely cannot refill).
    cards_after_discard = len(hand) - len(off_suit[:5])
    if cards_after_discard < 3:
        return None

    return off_suit[:5] if off_suit else None


def discard_for_straight(hand: list[CardData]) -> Optional[list[int]]:
    """Return indices to discard to chase a straight, or None if not worth it.

    Looks for 4-of-5 straight draws and discards non-matching cards.
    """
    if len(hand) < 5:
        return None
    ranks = sorted(set(_rank(c) for c in hand))
    # Try each window of 5 consecutive ranks (including A-low wheel)
    best_keep: set[int] | None = None
    best_match = 0

    for window_start in range(2, 12):  # windows starting 2..11 (2-6 thru 10-A)
        window = set(range(window_start, window_start + 5))
        matched = window & set(ranks)
        if len(matched) >= 4 and len(matched) > best_match:
            best_match = len(matched)
            best_keep = matched

    # Check wheel: A(14),2,3,4,5
    wheel = {14, 2, 3, 4, 5}
    wheel_matched = wheel & set(ranks)
    if len(wheel_matched) >= 4 and len(wheel_matched) > best_match:
        best_match = len(wheel_matched)
        best_keep = wheel_matched

    if best_keep is None or best_match < 4:
        return None
    if best_match >= 5:
        return None  # already have a straight — no discard needed

    # Keep one card per needed rank, discard the rest
    kept: set[int] = set()
    keep_indices: list[int] = []
    for c in hand:
        r = _rank(c)
        if r in best_keep and r not in kept and c.hand_index is not None:
            kept.add(r)
            keep_indices.append(c.hand_index)

    discard = [c.hand_index for c in hand
               if c.hand_index is not None and c.hand_index not in set(keep_indices)]
    return discard[:5] if discard else None


def discard_for_hand(hand: list[CardData], hand_levels: dict) -> Optional[list[int]]:
    """Discard the weakest cards not in the best play combo."""
    _, keep, _ = best_play(hand, hand_levels)
    keep_set = set(keep)
    to_discard = [c.hand_index for c in hand
                  if c.hand_index not in keep_set and c.hand_index is not None]
    return to_discard[:4] if to_discard else None


def choose_play(hand: list[CardData], hand_levels: dict,
                discards_left: int, hands_left: int,
                jokers: "list | None" = None) -> ActionRequest:
    """Decide whether to discard or play, and which cards."""
    sc, play_idx, hand_name = best_play(hand, hand_levels, jokers)

    # Try flush discard first (aggressive flush building)
    # But only if current best hand is weaker than what a flush would give us
    if discards_left > 0 and hands_left > 1:
        flush_discard = discard_for_flush(hand, jokers)
        if flush_discard:
            flush_est = estimate_score(FL, hand[:5], hand_levels, jokers)
            # Don't discard if we already have something at least as good as a flush
            if sc >= flush_est * 0.9:
                flush_discard = None
        if flush_discard:
            console.print(f"  -> Discard for flush: {flush_discard}")
            return ActionRequest(type=ActionType.DISCARD,
                                 params={"card_indices": flush_discard})

        # Try straight discard (lower priority than flush)
        straight_discard = discard_for_straight(hand)
        if straight_discard:
            straight_est = estimate_score(ST, hand[:5], hand_levels, jokers)
            if sc < straight_est * 0.9:
                console.print(f"  -> Discard for straight: {straight_discard}")
                return ActionRequest(type=ActionType.DISCARD,
                                     params={"card_indices": straight_discard})

        # Discard if hand is weak and we have room to improve
        if hand_name in ("High Card", "Pair", "Two Pair") and hands_left > 1:
            generic_discard = discard_for_hand(hand, hand_levels)
            if generic_discard:
                console.print(f"  -> Discard weak hand: {generic_discard}")
                return ActionRequest(type=ActionType.DISCARD,
                                     params={"card_indices": generic_discard})

    # Pad play with debuffed cards (boss blinds debuff suits/ranks; include
    # debuffed cards alongside scoring cards to cycle them out of hand faster).
    if len(play_idx) < 5:
        play_set = set(play_idx)
        debuffed_extra = [
            c.hand_index for c in hand
            if c.debuffed and c.hand_index is not None and c.hand_index not in play_set
        ]
        spaces = 5 - len(play_idx)
        play_idx = play_idx + debuffed_extra[:spaces]

    console.print(f"  -> Play {hand_name}: {play_idx}  (est. {sc:.0f})")
    return ActionRequest(type=ActionType.PLAY_HAND,
                         params={"card_indices": play_idx})


# -- Shop scoring & decisions --------------------------------------------------

# Higher = more desirable to buy
JOKER_PRIORITY: dict[str, float] = {
    # Always-on mult
    "Joker": 5,
    "Jolly Joker": 6,       "Zany Joker": 6,   "Mad Joker": 6,
    "Crazy Joker": 7,       "Droll Joker": 9,  # +4 mult on flush — core flush joker
    # Face-card synergy (great for flush builds with face cards)
    "Smiley Face": 7,       "Scary Face": 7,    "Photograph": 8,
    # Scaling / high-value
    "Fibonacci": 8,          "Scholar": 7,       "Hack": 7,
    "Hiker": 8,              "Dusk": 8,          "Mime": 7,
    "Mystic Summit": 8,      "Half Joker": 7,
    "Four Fingers": 9,       "Shortcut": 8,      "Smeared Joker": 9,  # flush in 4 cards
    "Sock and Buskin": 7,    "Hanging Chad": 6,
    # Hand size
    "Juggler": 8,            "Troubadour": 6,
    # xMult jokers (extremely powerful)
    "Steel Joker": 9,        "Blueprint": 9,     "Brainstorm": 9,
    "Oops! All 6s": 9,       "Baron": 9,         "Triboulet": 9,
    "Hologram": 8,           "DNA": 9,           "Pareidolia": 7,
    "Stuntman": 8,           "Bootstraps": 8,
    "Spare Trousers": 7,     "Ice Cream": 6,     "Bull": 7,
    "Cavendish": 8,
    "Loyalty Card": 7,       "Campfire": 8,
    "Riff-raff": 7,
    # Flush-specific
    "Splash": 6,             "Walkie Talkie": 7,  "Midas Mask": 7,
}


def owned_joker_priority(joker) -> float:
    """Return the priority score for an owned joker (lower = more expendable)."""
    return JOKER_PRIORITY.get(joker.name or "", 4.0)


def shop_item_priority(item, state: GameState) -> float:
    name = item.name or ""
    cost = item.cost
    money = state.money

    if cost > money:
        return -1.0   # can't afford

    itype = item.type

    if itype == "Joker":
        base = JOKER_PRIORITY.get(name, 4.0)
        # Edition bonus: holo/poly/negative jokers are extra valuable
        if item.edition in ("holo", "polychrome", "negative"):
            base += 2.0
        return base

    if itype == "Planet":
        if name in DEPRIORITIZED_PLANETS:
            return -1.0  # Mars/Neptune: hands we rarely make
        # Only level up hands that fit our flush-first strategy
        flush_planets = {"Jupiter"}              # Flush
        ok_planets    = {"Pluto", "Venus"}       # High Card / Three of a Kind (fallbacks)
        if name in flush_planets:
            return 9.0
        if name in ok_planets:
            return 5.0
        return 2.0   # Earth/Saturn/Mercury etc — not useful for flush build

    if itype == "Tarot":
        # No-select tarots: buy when affordable
        if name in NO_SELECT_TAROTS:
            priorities = {
                "Judgement":            8.5,   # free random joker
                "The Hermit":           8.0,   # doubles money
                "The High Priestess":   7.0,   # 2 free planets
                "Temperance":           7.0,   # money from joker sell values
                "The Emperor":          5.0,   # 2 free tarots
                "The Wheel of Fortune": 5.0,   # chance for joker edition
            }
            return priorities.get(name, 4.5)
        # Targeting tarots: buy if we can use them on hand cards
        if name in TARGETING_TAROT_PRIORITY:
            shop_buy_priority = {
                "The Star":  7.5,  "The Moon": 7.5, "The Sun": 7.5, "The World": 7.5,
                "The Lovers": 7.0,
                "The Empress": 6.5, "Justice": 6.5,
                "Death": 6.0,
                "The Hierophant": 6.0,
                "The Chariot": 5.5, "The Magician": 5.5, "Strength": 5.0,
                "The Hanged Man": 4.5,
                "The Devil": 4.0, "The Tower": 2.0,
            }
            return shop_buy_priority.get(name, 4.5)
        return 0.0   # unknown / unhandled targeting tarot

    if itype == "Spectral":
        return 0.0   # can't use spectrals without SELECT_CARDS targeting

    return 2.0


def choose_shop_action(state: GameState, legal: LegalActions,
                       rerolled_this_visit: int,
                       failed_slots: "set[tuple] | None" = None) -> ActionRequest:
    """One step of shop logic - buy best available or end."""
    shop = state.shop
    if not shop:
        return ActionRequest(type=ActionType.SHOP_END)

    money = state.money
    joker_count = len(state.jokers)

    # -- collect all candidates ----------------------------------------------
    candidates: list[tuple[float, ActionRequest, str, int]] = []

    for action in legal.get_actions_of_type(ActionType.SHOP_BUY):
        slot = action.params.slot
        if failed_slots and (ActionType.SHOP_BUY, slot) in failed_slots:
            continue
        if slot and 0 < slot <= len(shop.jokers):
            item = shop.jokers[slot - 1]
            p = shop_item_priority(item, state)
            # Strongly boost joker priority when we have none yet
            if p > 0 and item.type == "Joker" and joker_count == 0:
                p += 4.0
            if p >= 0:
                candidates.append((p, ActionRequest(
                    type=ActionType.SHOP_BUY, params={"slot": slot}
                ), item.name or "?", item.cost))

    for action in legal.get_actions_of_type(ActionType.SHOP_BUY_BOOSTER):
        slot = action.params.slot
        if failed_slots and (ActionType.SHOP_BUY_BOOSTER, slot) in failed_slots:
            continue
        if slot and 0 < slot <= len(shop.boosters):
            item = shop.boosters[slot - 1]
            if item.cost <= money:
                name = item.name or ""
                p = (7.0 if "Planet" in name or "Celestial" in name
                     else 7.0 if "Buffoon" in name   # jokers from Buffoon packs!
                     else 5.5 if "Tarot" in name or "Arcana" in name  # can contain Judgement/Hermit
                     else 0.0 if "Spectral" in name                   # can't use spectrals
                     else 2.0)
                # Deprioritize packs when we have no jokers (save money for jokers)
                if joker_count == 0 and "Buffoon" not in name:
                    p -= 3.0
                candidates.append((p, ActionRequest(
                    type=ActionType.SHOP_BUY_BOOSTER, params={"slot": slot}
                ), name, item.cost))

    for action in legal.get_actions_of_type(ActionType.SHOP_BUY_VOUCHER):
        slot = action.params.slot
        if failed_slots and (ActionType.SHOP_BUY_VOUCHER, slot) in failed_slots:
            continue
        if slot and 0 < slot <= len(shop.vouchers):
            item = shop.vouchers[slot - 1]
            if item.cost <= money:
                candidates.append((6.0, ActionRequest(
                    type=ActionType.SHOP_BUY_VOUCHER, params={"slot": slot}
                ), item.name or "?", item.cost))

    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        best_p, best_act, best_name, best_cost = candidates[0]

        # -- Sell weakest joker if a significantly better one is in the shop ---
        if joker_count >= 5 and best_p >= 4.5:
            # Find the weakest owned joker
            sell_actions = legal.get_actions_of_type(ActionType.SHOP_SELL_JOKER)
            if sell_actions and state.jokers:
                weakest_j = min(state.jokers, key=owned_joker_priority)
                weakest_p = owned_joker_priority(weakest_j)
                # Only sell if the shop joker is 3+ points better
                if best_p - weakest_p >= 3.0:
                    # Find the sell action matching the weakest joker
                    for sa in sell_actions:
                        ji = sa.params.joker_index
                        if ji is not None and 0 < ji <= len(state.jokers):
                            if state.jokers[ji - 1] is weakest_j:
                                console.print(
                                    f"  -> Sell {weakest_j.name!r} (p={weakest_p:.1f}) "
                                    f"to make room for {best_name!r} (p={best_p:.1f})")
                                return ActionRequest(
                                    type=ActionType.SHOP_SELL_JOKER,
                                    params={"joker_index": ji})

        # Lower buy threshold slightly (4.5) so affordable jokers are always bought
        if best_p >= 4.5:
            console.print(f"  -> Buy {best_name!r} (${best_cost}, p={best_p:.1f})")
            return best_act

    # -- consider rerolls ----------------------------------------------------
    reroll_actions = legal.get_actions_of_type(ActionType.SHOP_REROLL)
    # Allow up to 2 rerolls when no jokers (desperately need one), else 1
    max_rerolls = 2 if joker_count == 0 else 1
    if (rerolled_this_visit < max_rerolls
            and reroll_actions
            and joker_count < 5):
        rc = reroll_actions[0].params.cost or 5
        # Reroll when: no jokers and we can afford it, or cheap reroll with spare cash
        no_jokers_reroll = joker_count == 0 and money >= rc + 4
        cheap_reroll = rc <= 5 and money >= rc + 6
        if no_jokers_reroll or cheap_reroll:
            console.print(f"  -> Reroll (cost ${rc})")
            return ActionRequest(type=ActionType.SHOP_REROLL)

    return ActionRequest(type=ActionType.SHOP_END)


# -- Consumable use decisions --------------------------------------------------

# Tarots that need NO card selection — can be fired immediately in any phase.
NO_SELECT_TAROTS: set[str] = {
    "The Hermit",           # doubles current money — use ASAP (before spending)
    "Temperance",           # gives money = total joker sell value
    "Judgement",            # creates a random Joker — extremely valuable
    "The High Priestess",   # adds 2 planet cards to consumables
    "The Emperor",          # draws 2 tarot cards to consumables
    "The Wheel of Fortune", # chance to add edition to a random joker
    "The Fool",             # copies last used consumable
}

NO_SELECT_TAROT_PRIORITY: dict[str, float] = {
    "The Hermit":           10.0,  # doubles money — highest priority
    "Temperance":           9.5,   # money from joker sell values
    "Judgement":            9.0,   # free joker
    "The High Priestess":   8.0,   # 2 free planet cards
    "The Emperor":          7.5,   # 2 free tarots
    "The Wheel of Fortune": 7.0,   # edition upgrade
    "The Fool":             6.0,   # copy last consumable (situational)
}

# Tarots that require SELECT_CARDS first — priority when we have a good target.
# Only tried in SELECTING_HAND where a hand of cards exists.
TARGETING_TAROT_PRIORITY: dict[str, float] = {
    "The Star":       8.0,   # 3 cards → Spades  (great for flush building)
    "The Moon":       8.0,   # 3 cards → Clubs
    "The Sun":        8.0,   # 3 cards → Hearts
    "The World":      8.0,   # 3 cards → Diamonds
    "The Lovers":     7.5,   # 1 card  → Wild (any suit — fits any flush)
    "The Empress":    7.0,   # 2 cards → Mult  enhancement
    "Justice":        7.0,   # 1 card  → Glass (2x mult when scored)
    "Death":          7.0,   # 2 adj   → copy left onto right
    "The Hierophant": 6.5,   # 2 cards → Bonus chip enhancement
    "The Chariot":    6.0,   # 1 card  → Steel (1.5x mult when NOT in hand)
    "The Magician":   6.0,   # 1 card  → Lucky
    "Strength":       5.5,   # 1 card  → +1 rank
    "The Hanged Man": 5.0,   # 2 cards → destroys them (thins weak cards)
    "The Devil":      4.0,   # 1 card  → Gold card ($3 per hand)
    "The Tower":      2.0,   # 1 card  → Stone (removes rank/suit, big chips)
}

# Which suit each suit-changing tarot targets
SUIT_CHANGER_TARGET: dict[str, str] = {
    "The Star":  "Spades",
    "The Moon":  "Clubs",
    "The Sun":   "Hearts",
    "The World": "Diamonds",
}


def get_tarot_target_cards(tarot_name: str, hand: list[CardData],
                           jokers: "list | None" = None) -> list[int]:
    """Return hand_index list for the best target cards for a targeting tarot.

    Returns [] if this tarot cannot be usefully applied to the current hand.
    """
    if not hand:
        return []

    smeared = has_smeared_joker(jokers)
    suit_counts = Counter(effective_suit(c, smeared) for c in hand)
    dominant_suit = max(suit_counts, key=suit_counts.__getitem__)
    suited = [c for c in hand if effective_suit(c, smeared) == dominant_suit and not c.debuffed]
    off_suit = [c for c in hand if effective_suit(c, smeared) != dominant_suit and not c.debuffed]
    suited_desc = sorted(suited, key=_rank, reverse=True)
    off_suit_asc = sorted(off_suit, key=_rank)          # weakest off-suit first

    # -- Suit-changers ---------------------------------------------------------
    if tarot_name in SUIT_CHANGER_TARGET:
        target_suit = SUIT_CHANGER_TARGET[tarot_name]
        # When smeared, group by color; target suit maps to its color group
        if smeared:
            target_eff = "Red" if target_suit in ("Hearts", "Diamonds") else "Black"
        else:
            target_eff = target_suit
        off_target = [c for c in hand if effective_suit(c, smeared) != target_eff and not c.debuffed]
        new_count = suit_counts.get(target_eff, 0) + min(3, len(off_target))
        # Only use if converting to target_suit would give us flush territory (>=5)
        if new_count < 5 or not off_target:
            return []
        # Convert weakest off-target cards (keep high-value suited cards)
        off_target_asc = sorted(off_target, key=_rank)
        return [c.hand_index for c in off_target_asc[:3] if c.hand_index is not None]

    # -- The Lovers (Wild card): best off-suit card or best suited if all same suit
    if tarot_name == "The Lovers":
        # Make off-suit card wild so it "fits" the flush suit
        targets = off_suit_asc[:1] or suited_desc[:1]
        return [c.hand_index for c in targets if c.hand_index is not None]

    # -- Enhancement tarots: best suited cards ---------------------------------
    if tarot_name in ("The Empress", "The Hierophant"):
        return [c.hand_index for c in suited_desc[:2] if c.hand_index is not None]

    if tarot_name in ("The Magician", "The Chariot", "Justice", "The Devil"):
        return [c.hand_index for c in suited_desc[:1] if c.hand_index is not None]

    if tarot_name == "Strength":
        # Increase rank of best suited non-Ace card (Ace can't go higher)
        non_ace = [c for c in suited_desc if _rank(c) < 14]
        return [c.hand_index for c in non_ace[:1] if c.hand_index is not None]

    if tarot_name == "The Tower":
        # Stone on weakest off-suit card (removes rank/suit but adds big chips)
        return [c.hand_index for c in off_suit_asc[:1] if c.hand_index is not None]

    # -- The Hanged Man: destroy 2 weakest off-suit cards ----------------------
    if tarot_name == "The Hanged Man":
        if len(off_suit_asc) < 2:
            return []
        return [c.hand_index for c in off_suit_asc[:2] if c.hand_index is not None]

    # -- Death: copy source card onto adjacent target card ---------------------
    if tarot_name == "Death":
        # Death: "Left card becomes Right card" — select [target, source]
        # so target (left pos) becomes source (right pos).
        # Cards must be adjacent (hand_index differs by 1).
        for source in suited_desc:
            for target in off_suit_asc:
                if (source.hand_index is not None and target.hand_index is not None and
                        abs(source.hand_index - target.hand_index) == 1):
                    # Put lower index first (left), higher index second (right)
                    lo, hi = sorted([target.hand_index, source.hand_index])
                    # We want the worse card (lo) to become the better card (hi)
                    # Death: left → right means lo becomes hi value.
                    # Select [lo, hi]: lo is left → becomes hi (source)
                    if hi == source.hand_index:
                        return [lo, hi]
        return []  # no adjacent pair found

    return []


def choose_consumable_action(
    state: GameState, legal: LegalActions
) -> Optional[ActionRequest]:
    """Return the best consumable action available right now.

    May return USE_CONSUMABLE (for planets / no-select tarots, or after cards
    are already highlighted for a targeting tarot) or SELECT_CARDS (to
    highlight target cards before a USE_CONSUMABLE next iteration).

    Returns None if no consumable action is worth taking.
    """
    use_map = {a.params.index: a for a in legal.get_actions_of_type(ActionType.USE_CONSUMABLE)}
    can_select = legal.has_action_type(ActionType.SELECT_CARDS)
    hand = state.hand  # empty list in SHOP phase

    # Build index → ConsumableData for all consumables
    consumable_by_idx = {c.index: c for c in state.consumables}

    best_priority = -1.0
    best_action: Optional[ActionRequest] = None
    best_label = ""

    for c in state.consumables:
        cname = c.name or ""
        ctype = c.type or ""
        priority = -1.0
        action: Optional[ActionRequest] = None
        label = ""

        # -- Planet cards: always use immediately ------------------------------
        if ctype == "Planet":
            if c.can_use and c.index in use_map:
                priority = 10.0
                action = ActionRequest(type=ActionType.USE_CONSUMABLE,
                                       params={"index": c.index})
                label = f"Use planet {cname!r}"

        # -- No-select tarots: use when can_use is True -----------------------
        elif ctype == "Tarot" and cname in NO_SELECT_TAROTS:
            if c.can_use and c.index in use_map:
                priority = NO_SELECT_TAROT_PRIORITY.get(cname, 6.0)
                action = ActionRequest(type=ActionType.USE_CONSUMABLE,
                                       params={"index": c.index})
                label = f"Use tarot {cname!r}"

        # -- Targeting tarots: need hand cards (only in SELECTING_HAND) -------
        elif ctype == "Tarot" and cname in TARGETING_TAROT_PRIORITY and hand:
            tp = TARGETING_TAROT_PRIORITY[cname]
            if c.can_use and c.index in use_map:
                # Target cards already highlighted — execute the tarot now
                priority = tp
                action = ActionRequest(type=ActionType.USE_CONSUMABLE,
                                       params={"index": c.index})
                label = f"Use targeting tarot {cname!r}"
            elif not c.can_use and can_select:
                # Need to highlight target cards first
                targets = get_tarot_target_cards(cname, hand, state.jokers)
                if targets:
                    priority = tp - 0.1   # slightly lower than the USE step
                    action = ActionRequest(type=ActionType.SELECT_CARDS,
                                           params={"card_indices": targets})
                    label = f"Select targets for {cname!r}: {targets}"

        if priority > best_priority and action is not None:
            best_priority = priority
            best_action = action
            best_label = label

    if best_action is not None:
        console.print(f"  -> {best_label}")
        return best_action

    return None


# -- Pack decisions ------------------------------------------------------------

def pack_cards_revealed(pack) -> bool:
    """Return True if all pack cards are face-up with populated name/type."""
    if not pack or not pack.cards:
        return False
    for c in pack.cards:
        if c.get("facing") == "back":
            return False
        if not c.get("name") and not c.get("rank"):
            return False
    return True


def choose_pack_action(state: GameState, legal: LegalActions) -> Optional[ActionRequest]:
    """Choose a pack action.  Returns None to signal 'wait this iteration'."""
    pack = state.pack
    pick_actions = legal.get_actions_of_type(ActionType.SELECT_PACK_CARD)

    if not pick_actions:
        # No cards available yet (pack is still opening) OR all choices used
        # (pack will close by itself).  Either way, just wait.
        return None

    # Guard: if choices_remaining has dropped to 0, the pack is closing —
    # do NOT pick again even if SELECT_PACK_CARD still appears in legal actions
    # (the legal list can lag one frame behind the actual state).
    if pack is None or pack.choices_remaining <= 0:
        return None

    # Wait for pack cards to be fully revealed (flip animation)
    if not pack_cards_revealed(pack):
        return None

    best_idx: Optional[int] = None
    best_score = -1.0

    for card in pack.cards:
        idx = card.get("index")
        if idx is None:
            continue
        ctype = card.get("type", "")
        name  = card.get("name", "")
        score = 0.0

        if ctype == "Planet":
            if name in DEPRIORITIZED_PLANETS:
                score = -1.0   # Mars/Neptune: never pick
            elif name == "Jupiter":
                score = 10.0   # Flush planet — core strategy
            elif name in ("Pluto", "Venus"):
                score = 6.0
            else:
                score = 3.0
        elif ctype == "Tarot":
            # No-select high-value tarots
            if name in NO_SELECT_TAROT_PRIORITY:
                score = NO_SELECT_TAROT_PRIORITY[name]
            elif name in TARGETING_TAROT_PRIORITY:
                score = TARGETING_TAROT_PRIORITY[name]
            else:
                score = 3.0
        elif ctype == "Spectral":
            score = 4.0
        elif ctype == "Joker":
            score = JOKER_PRIORITY.get(name, 4.0)
        elif card.get("suit") and card.get("rank"):
            # Playing card from Standard pack
            score = RANK_ORDER.get(str(card.get("rank", "2")).upper(), 2)

        if score > best_score:
            best_score = score
            best_idx = idx

    if best_idx is not None:
        console.print(f"  -> Pick pack card {best_idx} (score {best_score:.1f})")
        return ActionRequest(type=ActionType.SELECT_PACK_CARD,
                             params={"index": best_idx})

    # fallback: first available
    return pick_actions[0].to_request()


# -- TUI dashboard (ported from autopilot.py) ----------------------------------

@dataclass
class RunStats:
    """Statistics for a single run."""
    run_id: str = ""
    rounds_survived: int = 0
    max_ante: int = 0
    max_money: int = 0
    hands_played: int = 0
    blinds_beaten: int = 0
    won: bool = False

    def summary_line(self) -> str:
        result = "WON" if self.won else "Lost"
        return (
            f"Run {self.run_id}: {result} | "
            f"Ante {self.max_ante} Round {self.rounds_survived} | "
            f"${self.max_money} peak | "
            f"{self.hands_played} hands"
        )


@dataclass
class SessionStats:
    """Statistics across all runs in this session."""
    runs_completed: int = 0
    total_rounds: int = 0
    total_hands: int = 0
    best_ante: int = 0
    wins: int = 0
    run_history: list[RunStats] = field(default_factory=list)
    current_run: RunStats = field(default_factory=RunStats)

    def finish_run(self, won: bool = False):
        self.current_run.won = won
        self.run_history.append(self.current_run)
        self.runs_completed += 1
        self.total_rounds += self.current_run.rounds_survived
        self.total_hands += self.current_run.hands_played
        if self.current_run.max_ante > self.best_ante:
            self.best_ante = self.current_run.max_ante
        if won:
            self.wins += 1
        self.current_run = RunStats()

    def new_run(self, run_id: str):
        self.current_run = RunStats(run_id=run_id)


@dataclass
class AgentDecision:
    """Tracks the most recent agent decision for TUI display."""
    reason: str = ""
    cards_label: str = ""


def _card_label(card) -> str:
    """Short display label for a card (e.g. 'KH', '10S')."""
    if isinstance(card, dict):
        r = card.get("rank", "?")
        s = card.get("suit", "?")
    else:
        r = card.rank or "?"
        s = card.suit or "?"
    suit_sym = {"Hearts": "H", "Diamonds": "D", "Clubs": "C", "Spades": "S"}
    return f"{r}{suit_sym.get(str(s), '?')}"


LOG_MAX = 30


def build_dashboard(
    state: GameState | None,
    legal: LegalActions | None,
    last_decision: AgentDecision | None,
    session: SessionStats,
    log_lines: deque[str],
    status_msg: str = "",
) -> Layout:
    """Build the Rich Layout for the live TUI dashboard."""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=5),
    )

    # Header
    phase_str = state.phase.value if state else "Connecting..."
    run_id = state.run_id or "N/A" if state else "N/A"
    header_text = Text.from_markup(
        f"  [bold cyan]BALATRO AGENT[/]  |  "
        f"Phase: [bold yellow]{phase_str}[/]  |  "
        f"Run: {run_id}  |  "
        f"Runs: {session.runs_completed} ({session.wins}W)  |  "
        f"Best Ante: {session.best_ante}"
    )
    layout["header"].update(Panel(header_text, style="blue"))

    # Body: split into left (game state) and right (log)
    layout["body"].split_row(
        Layout(name="state_panel", ratio=2),
        Layout(name="log_panel", ratio=1),
    )

    # State panel
    state_content = build_state_panel(state, legal, session)
    layout["state_panel"].update(state_content)

    # Log panel
    log_text = "\n".join(log_lines) if log_lines else "[dim]No actions yet[/dim]"
    layout["log_panel"].update(
        Panel(Text.from_markup(log_text), title="Action Log", border_style="dim")
    )

    # Footer — current decision
    if status_msg:
        footer_text = Text.from_markup(status_msg)
    elif last_decision and last_decision.reason:
        footer_text = Text.from_markup(
            f"[bold green]>>> {last_decision.reason}[/]\n"
            f"    {last_decision.cards_label}"
        )
    else:
        footer_text = Text.from_markup("[dim]Waiting...[/dim]")
    layout["footer"].update(Panel(footer_text, title="Decision", border_style="green"))

    return layout


def build_state_panel(
    state: GameState | None,
    legal: LegalActions | None,
    session: SessionStats,
) -> Panel:
    """Build the game state display panel."""
    if not state:
        return Panel("[dim]No state yet[/dim]", title="Game State")

    parts: list[str] = []

    # Resources
    chips_scored = state.blind.chips_scored if state.blind else 0
    chips_needed = state.blind.chips_needed or 0 if state.blind else 0
    blind_name = state.blind.name if state.blind else "?"
    boss = " [red]BOSS[/]" if state.blind and state.blind.boss else ""

    parts.append(
        f"[bold]Ante {state.ante} | Round {state.round}[/] | "
        f"Blind: {blind_name}{boss}"
    )
    parts.append(
        f"Score: [bold]{chips_scored:,}[/] / {chips_needed:,} | "
        f"Money: [green]${state.money}[/] | "
        f"Hands: {state.hands_remaining} | "
        f"Discards: {state.discards_remaining}"
    )
    parts.append(
        f"Deck: {state.deck_counts.deck_size} | "
        f"Discard pile: {state.deck_counts.discard_size}"
    )
    parts.append("")

    # Hand
    if state.hand:
        hand_str = "  ".join(
            f"[{'bold yellow' if c.highlighted else 'white'}]{_card_label(c)}[/]"
            for c in state.hand
        )
        parts.append(f"[cyan]Hand ({len(state.hand)}):[/] {hand_str}")

    # Jokers
    if state.jokers:
        joker_strs = [j.name or j.key or "?" for j in state.jokers]
        parts.append(f"[magenta]Jokers ({len(state.jokers)}):[/] {', '.join(joker_strs)}")

    # Consumables
    if state.consumables:
        cons_strs = []
        for c in state.consumables:
            name = c.name or c.key or "?"
            usable = "*" if c.can_use else ""
            cons_strs.append(f"{name}{usable}")
        parts.append(f"[magenta]Consumables:[/] {', '.join(cons_strs)}")

    # Shop
    if state.shop:
        shop = state.shop
        parts.append("")
        if shop.jokers:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.jokers]
            parts.append(f"[yellow]Shop Jokers:[/] {' | '.join(items)}")
        if shop.vouchers:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.vouchers]
            parts.append(f"[yellow]Vouchers:[/] {' | '.join(items)}")
        if shop.boosters:
            items = [f"{it.name or it.key or '?'} ${it.cost}" for it in shop.boosters]
            parts.append(f"[yellow]Boosters:[/] {' | '.join(items)}")
        parts.append(f"Reroll: ${shop.reroll_cost}")

    # Pack
    if state.pack and state.pack.cards:
        pack_items = []
        for c in state.pack.cards:
            name = c.get("name", "?")
            if c.get("suit") and c.get("rank"):
                name = f"{c['rank']}{c['suit'][0]}"
            pack_items.append(name)
        parts.append(
            f"[yellow]Pack ({state.pack.choices_remaining} choices):[/] "
            f"{' | '.join(pack_items)}"
        )

    # Legal action summary
    if legal and legal.actions:
        action_types: dict[str, int] = {}
        for a in legal.actions:
            t = a.type.value
            action_types[t] = action_types.get(t, 0) + 1
        summary = ", ".join(f"{t}({n})" for t, n in action_types.items())
        parts.append(f"\n[dim]Legal: {summary}[/]")

    content = "\n".join(parts)
    return Panel(Text.from_markup(content), title="Game State", border_style="cyan")


# -- Main loop -----------------------------------------------------------------

def run_agent(client: BalatroClient, tui: bool = False, delay: float = 0.8):
    if not tui:
        console.print(Panel.fit(
            "[bold green]Balatro Agent[/bold green]\n"
            "Deck: Red  |  Stake: White (base)\n"
            "Strategy: flush-first, opportunistic shop",
            title="Agent"
        ))

    # TUI state
    session = SessionStats()
    log_lines: deque[str] = deque(maxlen=LOG_MAX)
    last_decision = AgentDecision()
    status_msg = ""
    tui_state: GameState | None = None
    tui_legal: LegalActions | None = None
    live: Live | None = None

    def tui_log(msg: str):
        if tui:
            log_lines.append(msg)
        else:
            console.print(msg)

    def tui_update():
        if live:
            live.update(build_dashboard(
                tui_state, tui_legal, last_decision, session, log_lines, status_msg))

    rerolled_this_shop = 0  # count of rerolls this shop visit
    failed_shop_slots: set[tuple] = set()
    prev_phase: Optional[GamePhase] = None
    # When we send SELECT_CARDS to prepare for a targeting tarot, remember which
    # consumable index we're preparing for.  If USE_CONSUMABLE still isn't
    # available after one SELECT_CARDS attempt, we abandon (prevents loops).
    awaiting_consumable: Optional[int] = None

    def _agent_loop():
        nonlocal rerolled_this_shop, failed_shop_slots, prev_phase
        nonlocal awaiting_consumable, tui_state, tui_legal, status_msg
        while True:
            # -- fetch state ------------------------------------------------
            try:
                state  = client.get_state()
                legal  = client.get_legal_actions()
            except BalatroConnectionError as e:
                tui_log(f"[red]Connection error: {e} - retrying[/red]")
                time.sleep(1.0)
                continue

            tui_state = state
            tui_legal = legal

            phase = state.phase

            # Track run stats for TUI
            if tui and state.run_id and state.run_id != session.current_run.run_id:
                if session.current_run.run_id:
                    session.finish_run()
                    tui_log(f"[red]Run ended: {session.run_history[-1].summary_line()}[/]")
                session.new_run(str(state.run_id))

            if tui:
                run = session.current_run
                run.rounds_survived = max(run.rounds_survived, state.round)
                run.max_ante = max(run.max_ante, state.ante)
                run.max_money = max(run.max_money, state.money)

            # Phase-change banner
            if phase != prev_phase:
                tui_log(
                    f"[bold cyan]-- {phase.value}[/bold cyan]  "
                    f"ante={state.ante} round={state.round}  "
                    f"${state.money}  "
                    f"hands={state.hands_remaining} discards={state.discards_remaining}"
                )
                prev_phase = phase
                if phase == GamePhase.SHOP:
                    rerolled_this_shop = 0
                    failed_shop_slots.clear()
                awaiting_consumable = None  # reset on any phase change

            if state.error:
                tui_log(f"[yellow]  State error: {state.error}[/yellow]")
                time.sleep(0.4)
                tui_update()
                continue

            # -- GAME OVER / MENU handle even with no legal actions -----------
            if phase in (GamePhase.GAME_OVER, GamePhase.MENU):
                pass  # fall through to phase handlers below
            elif not legal.actions:
                time.sleep(0.3)
                tui_update()
                continue

            # -- MENU ------------------------------------------------------
            if phase == GamePhase.MENU:
                r = client.execute_action(
                    ActionRequest(type=ActionType.START_RUN, params={"stake": 1}))
                if r.ok:
                    tui_log("[green]  Run started[/green]")
                    time.sleep(3.0)
                else:
                    tui_log(f"[red]  START_RUN failed: {r.error}[/red]")
                    time.sleep(1.0)

            # -- BLIND SELECT ----------------------------------------------
            elif phase == GamePhase.BLIND_SELECT:
                if legal.has_action_type(ActionType.SELECT_BLIND):
                    r = client.execute_action(
                        ActionRequest(type=ActionType.SELECT_BLIND, params={}))
                    if r.ok:
                        tui_log("[green]  Blind selected[/green]")
                        time.sleep(1.5)
                    else:
                        tui_log(f"[yellow]  {r.error}[/yellow]")
                        time.sleep(0.5)
                else:
                    time.sleep(0.3)

            # -- SELECTING HAND --------------------------------------------
            elif phase == GamePhase.SELECTING_HAND:
                hand = state.hand
                if not hand:
                    time.sleep(0.3)
                    tui_update()
                    continue

                # Use consumables before playing (planets / tarots)
                consumable_action = choose_consumable_action(state, legal)
                if consumable_action:
                    is_select = consumable_action.type == ActionType.SELECT_CARDS
                    prep_idx = None
                    if is_select:
                        for c in state.consumables:
                            cname = c.name or ""
                            if (c.type == "Tarot" and cname in TARGETING_TAROT_PRIORITY
                                    and not c.can_use):
                                prep_idx = c.index
                                break
                        if prep_idx is not None and awaiting_consumable == prep_idx:
                            use_map = {a.params.index: a
                                       for a in legal.get_actions_of_type(ActionType.USE_CONSUMABLE)}
                            if prep_idx in use_map:
                                tui_log(f"  -> USE_CONSUMABLE now ready for {prep_idx}")
                                consumable_action = ActionRequest(
                                    type=ActionType.USE_CONSUMABLE,
                                    params={"index": prep_idx})
                                is_select = False
                            else:
                                tui_log(f"[yellow]  SELECT_CARDS retry blocked for consumable {prep_idx}[/yellow]")
                                awaiting_consumable = None
                                consumable_action = None

                if consumable_action:
                    r = client.execute_action(consumable_action)
                    if r.ok:
                        if is_select:
                            awaiting_consumable = prep_idx
                            tui_log("[green]  Cards selected for tarot[/green]")
                            for _ in range(8):
                                time.sleep(0.3)
                                try:
                                    s2 = client.get_state()
                                except BalatroConnectionError:
                                    break
                                for c in s2.consumables:
                                    if c.index == prep_idx and c.can_use:
                                        break
                                else:
                                    continue
                                break
                        else:
                            awaiting_consumable = None
                            tui_log("[green]  Consumable used[/green]")
                            time.sleep(1.2)
                    else:
                        awaiting_consumable = None
                        tui_log(f"[yellow]  Consumable action failed: {r.error}[/yellow]")
                        time.sleep(0.5)
                    tui_update()
                    continue

                needed = (state.blind.chips_needed or 0) if state.blind else 0
                scored = (state.blind.chips_scored or 0) if state.blind else 0
                hand_str = " ".join(f"{c.rank}{(c.suit or '?')[0]}" for c in hand)
                tui_log(f"  Hand: {hand_str}  [{scored:,}/{needed:,}]")

                action = choose_play(hand, state.hand_levels,
                                     state.discards_remaining,
                                     state.hands_remaining,
                                     state.jokers)
                r = client.execute_action(action)
                if r.ok:
                    tui_log("[green]  OK[/green]")
                    if tui:
                        session.current_run.hands_played += (
                            1 if action.type == ActionType.PLAY_HAND else 0)
                    time.sleep(1.2 if action.type == ActionType.PLAY_HAND else 0.5)
                else:
                    tui_log(f"[red]  Failed: {r.error}[/red]")
                    if action.type == ActionType.DISCARD:
                        _, idx, name = best_play(hand, state.hand_levels, state.jokers)
                        tui_log(f"  -> Fallback play {name}: {idx}")
                        r2 = client.execute_action(ActionRequest(
                            type=ActionType.PLAY_HAND,
                            params={"card_indices": idx}))
                        if r2.ok:
                            time.sleep(1.2)
                        else:
                            tui_log(f"[red]  Fallback also failed: {r2.error}[/red]")
                            time.sleep(0.5)

            # -- ROUND EVAL ------------------------------------------------
            elif phase == GamePhase.ROUND_EVAL:
                for _ in range(15):
                    r = client.execute_action(
                        ActionRequest(type=ActionType.CASH_OUT, params={}))
                    if r.ok:
                        tui_log("[green]  Cashed out[/green]")
                        time.sleep(1.0)
                        break
                    tui_log(f"[yellow]  {r.error}[/yellow]")
                    time.sleep(0.4)

            # -- SHOP ------------------------------------------------------
            elif phase == GamePhase.SHOP:
                consumable_action = choose_consumable_action(state, legal)
                if consumable_action:
                    r = client.execute_action(consumable_action)
                    if r.ok:
                        tui_log("[green]  Consumable used[/green]")
                        time.sleep(1.2)
                    else:
                        tui_log(f"[yellow]  Consumable use failed: {r.error}[/yellow]")
                        time.sleep(0.5)
                    tui_update()
                    continue

                action = choose_shop_action(state, legal, rerolled_this_shop,
                                            failed_shop_slots)
                r = client.execute_action(action)
                if r.ok:
                    if action.type == ActionType.SHOP_REROLL:
                        rerolled_this_shop += 1
                        failed_shop_slots.clear()
                    if action.type == ActionType.SHOP_END:
                        tui_log("[green]  Left shop[/green]")
                        time.sleep(1.5)
                    else:
                        time.sleep(0.5)
                else:
                    tui_log(f"[red]  Shop action failed: {r.error}[/red]")
                    if action.type in (ActionType.SHOP_BUY,
                                       ActionType.SHOP_BUY_BOOSTER,
                                       ActionType.SHOP_BUY_VOUCHER):
                        params = action.params or {}
                        slot = (params.get("slot") if isinstance(params, dict)
                                else getattr(params, "slot", None)) or 0
                        failed_shop_slots.add((action.type, slot))
                        time.sleep(0.5)
                    else:
                        client.execute_action(ActionRequest(type=ActionType.SHOP_END))
                        time.sleep(1.0)

            # -- PACK OPENING ----------------------------------------------
            elif phase == GamePhase.PACK_OPENING:
                action = choose_pack_action(state, legal)
                if action is None:
                    time.sleep(0.5)
                    tui_update()
                    continue
                prev_choices = state.pack.choices_remaining if state.pack else 0
                r = client.execute_action(action)
                if r.ok:
                    tui_log("[green]  Pack action OK[/green]")
                    for _ in range(10):
                        time.sleep(0.5)
                        try:
                            s2 = client.get_state()
                        except BalatroConnectionError:
                            break
                        if s2.phase != GamePhase.PACK_OPENING:
                            break
                        if s2.pack and s2.pack.choices_remaining < prev_choices:
                            break
                    time.sleep(0.5)
                else:
                    tui_log(f"[red]  Pack action failed: {r.error}[/red]")
                    time.sleep(1.0)

            # -- GAME OVER -------------------------------------------------
            elif phase == GamePhase.GAME_OVER:
                tui_log(
                    f"[red bold]GAME OVER[/red bold]  "
                    f"ante={state.ante} round={state.round}")
                if tui:
                    session.finish_run(won=False)
                time.sleep(4.0)
                r = client.execute_action(
                    ActionRequest(type=ActionType.START_RUN, params={"stake": 1}))
                if r.ok:
                    tui_log("[green]  New run started[/green]")
                    time.sleep(3.0)
                else:
                    tui_log(f"[yellow]  Couldn't restart: {r.error}[/yellow]")
                    time.sleep(1.0)

            # -- Transition / unknown --------------------------------------
            else:
                time.sleep(0.3)

            tui_update()

    # -- Run the loop (TUI or plain) ---------------------------------------
    try:
        if tui:
            with Live(
                build_dashboard(tui_state, tui_legal, last_decision, session,
                                log_lines, "[yellow]Starting...[/]"),
                console=console,
                refresh_per_second=4,
                screen=True,
            ) as live_ctx:
                live = live_ctx  # type: ignore[assignment]  # noqa: F841
                _agent_loop()
        else:
            _agent_loop()
    except KeyboardInterrupt:
        pass

    # Session summary (TUI mode)
    if tui:
        if session.current_run.run_id:
            session.finish_run()

        console.print()
        console.print(Panel.fit(
            f"[bold]Session Summary[/]\n"
            f"Runs: {session.runs_completed} ({session.wins} wins)\n"
            f"Best Ante: {session.best_ante}\n"
            f"Total Rounds: {session.total_rounds}\n"
            f"Total Hands: {session.total_hands}",
            title="[bold blue]Agent Finished[/]",
            border_style="blue",
        ))

        if session.run_history:
            history_table = Table(title="Run History")
            history_table.add_column("#", style="dim")
            history_table.add_column("Run ID")
            history_table.add_column("Result", style="bold")
            history_table.add_column("Ante")
            history_table.add_column("Round")
            history_table.add_column("Hands")
            history_table.add_column("Peak $")
            for i, run in enumerate(session.run_history, 1):
                result_style = "green" if run.won else "red"
                history_table.add_row(
                    str(i),
                    run.run_id[:8],
                    f"[{result_style}]{'WIN' if run.won else 'LOSS'}[/]",
                    str(run.max_ante),
                    str(run.rounds_survived),
                    str(run.hands_played),
                    f"${run.max_money}",
                )
            console.print(history_table)


def main():
    p = argparse.ArgumentParser(description="Balatro agent - Red Deck White Stake")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7777)
    p.add_argument("--tui", action="store_true",
                   help="Enable Rich TUI dashboard (fullscreen)")
    p.add_argument("--delay", type=float, default=0.8,
                   help="Delay between decisions in seconds (default: 0.8)")
    args = p.parse_args()

    console.print(f"Connecting to {args.host}:{args.port} ...")
    for attempt in range(20):
        try:
            client = BalatroClient(host=args.host, port=args.port)
            h = client.health()
            console.print(f"[green]Connected - bridge v{h.version}[/green]")
            break
        except BalatroConnectionError:
            if attempt == 19:
                console.print("[red]Could not connect - is Balatro running?[/red]")
                sys.exit(1)
            time.sleep(1.0)
    else:
        sys.exit(1)

    run_agent(client, tui=args.tui, delay=args.delay)


if __name__ == "__main__":
    main()
