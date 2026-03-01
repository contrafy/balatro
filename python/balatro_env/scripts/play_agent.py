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

import sys
import time
from collections import Counter
from itertools import combinations
from typing import Optional

from rich.console import Console
from rich.panel import Panel

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


def _rank(card: CardData) -> int:
    return RANK_ORDER.get(str(card.rank or "2").upper(), 0)


def _chips(card: CardData) -> int:
    return CARD_CHIPS.get(str(card.rank or "2").upper(), 0)


# -- Hand detection ------------------------------------------------------------

def detect_hand(cards: list[CardData]) -> int:
    """Return the hand-type constant for a list of 1-5 cards."""
    if not cards:
        return HC
    cards = cards[:5]
    ranks = [_rank(c) for c in cards]
    suits = [c.suit for c in cards]
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
    """Return (score, [hand_indices], name) for the best 1-5 card play."""
    best = (-1.0, list(range(1, min(6, len(hand)+1))), "High Card")
    for size in range(1, min(6, len(hand)+1)):
        for combo in combinations(range(len(hand)), size):
            cards = [hand[i] for i in combo]
            ht = detect_hand(cards)
            sc = estimate_score(ht, cards, hand_levels, jokers)
            if sc > best[0]:
                best = (sc, [hand[i].hand_index for i in combo
                              if hand[i].hand_index is not None],
                        HAND_NAMES[ht])
    return best


def discard_for_flush(hand: list[CardData]) -> Optional[list[int]]:
    """Return indices to discard to chase a flush, or None if not worth it."""
    suit_groups: dict[str, list[CardData]] = {}
    for c in hand:
        s = c.suit or "?"
        suit_groups.setdefault(s, []).append(c)

    best_suit = max(suit_groups, key=lambda s: len(suit_groups[s]))
    suited = suit_groups[best_suit]

    if len(suited) < 4:          # not enough suited cards to chase flush
        return None

    if len(suited) >= 5:         # already have a flush — no discard needed
        return None

    # Discard ALL off-suit cards (up to 5 at once)
    off_suit = [c.hand_index for c in hand
                if (c.suit or "?") != best_suit and c.hand_index is not None]

    # Safety: if deck is low (hand already < 8 cards) only discard if we'd
    # still have at least 5 cards after drawing back (worst case: draw 0).
    cards_after_discard = len(hand) - len(off_suit[:5])
    if cards_after_discard < 5:
        return None

    return off_suit[:5] if off_suit else None


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
        flush_discard = discard_for_flush(hand)
        if flush_discard:
            flush_est = estimate_score(FL, hand[:5], hand_levels, jokers)
            # Don't discard if we already have something at least as good as a flush
            if sc >= flush_est * 0.9:
                flush_discard = None
        if flush_discard:
            console.print(f"  -> Discard for flush: {flush_discard}")
            return ActionRequest(type=ActionType.DISCARD,
                                 params={"card_indices": flush_discard})

        # Discard if hand is weak and we have room to improve
        if hand_name in ("High Card", "Pair", "Two Pair") and hands_left > 1:
            generic_discard = discard_for_hand(hand, hand_levels)
            if generic_discard:
                console.print(f"  -> Discard weak hand: {generic_discard}")
                return ActionRequest(type=ActionType.DISCARD,
                                     params={"card_indices": generic_discard})

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
        # Only level up hands that fit our flush-first strategy
        flush_planets = {"Jupiter", "Neptune"}   # Flush, Straight Flush
        ok_planets    = {"Pluto", "Venus"}       # High Card / Three of a Kind (fallbacks)
        if name in flush_planets:
            return 9.0
        if name in ok_planets:
            return 5.0
        return 2.0   # Earth/Saturn/Mercury etc — not useful for flush build

    if itype == "Tarot":
        # Buy high-value no-select tarots — we can use them immediately
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
        return 0.0   # card-targeting tarots — can't use without SELECT_CARDS

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

# Tarots that require NO card selection (can be used immediately in any phase)
NO_SELECT_TAROTS: set[str] = {
    "The Hermit",           # doubles current money — use ASAP (before spending)
    "Temperance",           # gives money = total joker sell value
    "Judgement",            # creates a random Joker — extremely valuable
    "The High Priestess",   # adds 2 planet cards to consumables
    "The Emperor",          # draws 2 tarot cards to consumables
    "The Wheel of Fortune", # chance to add edition to a random joker
    "The Fool",             # copies last used consumable
}

TAROT_PRIORITY: dict[str, float] = {
    "The Hermit":           10.0,  # doubles money — highest priority
    "Temperance":           9.5,   # money from joker sell values
    "Judgement":            9.0,   # free joker
    "The High Priestess":   8.0,   # 2 free planet cards
    "The Emperor":          7.5,   # 2 free tarots
    "The Wheel of Fortune": 7.0,   # edition upgrade
    "The Fool":             6.0,   # copy last consumable (situational)
}


def choose_consumable_action(
    state: GameState, legal: LegalActions
) -> Optional[ActionRequest]:
    """Return a USE_CONSUMABLE action if there's a consumable worth using now,
    else None.  Only uses items that require no card pre-selection."""
    use_actions = legal.get_actions_of_type(ActionType.USE_CONSUMABLE)
    if not use_actions:
        return None

    # Build index → consumable map (only usable ones)
    consumable_map = {c.index: c for c in state.consumables if c.can_use}
    if not consumable_map:
        return None

    best_idx: Optional[int] = None
    best_priority = -1.0

    for action in use_actions:
        idx = action.params.index
        if idx is None:
            continue
        c = consumable_map.get(idx)
        if c is None:
            continue

        ctype = c.type or ""
        cname = c.name or ""
        priority = -1.0

        if ctype == "Planet":
            # Always use planet cards immediately — levels up hand types
            priority = 10.0

        elif ctype == "Tarot" and cname in NO_SELECT_TAROTS:
            priority = TAROT_PRIORITY.get(cname, 6.0)

        # Spectral and card-targeting tarots: skip (need SELECT_CARDS first or
        # complex targeting we don't handle yet)

        if priority > best_priority:
            best_priority = priority
            best_idx = idx

    if best_idx is not None:
        c = consumable_map[best_idx]
        console.print(f"  -> Use consumable {c.name!r} (type={c.type})")
        return ActionRequest(type=ActionType.USE_CONSUMABLE, params={"index": best_idx})

    return None


# -- Pack decisions ------------------------------------------------------------

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
            # Prefer flush-strategy planets; deprioritize others
            if name in ("Jupiter", "Neptune"):
                score = 10.0
            elif name in ("Pluto", "Venus"):
                score = 6.0
            else:
                score = 3.0
        elif ctype == "Tarot":
            high_val = {"The World", "The Star", "The Sun", "Judgement",
                        "The Emperor", "The Lovers", "The High Priestess"}
            score = 7.0 if name in high_val else 4.0
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


# -- Main loop -----------------------------------------------------------------

def run_agent(client: BalatroClient):
    console.print(Panel.fit(
        "[bold green]Balatro Agent[/bold green]\n"
        "Deck: Red  |  Stake: White (base)\n"
        "Strategy: flush-first, opportunistic shop",
        title="Agent"
    ))

    rerolled_this_shop = 0  # count of rerolls this shop visit
    failed_shop_slots: set[tuple] = set()
    prev_phase: Optional[GamePhase] = None

    while True:
        # -- fetch state ----------------------------------------------------
        try:
            state  = client.get_state()
            legal  = client.get_legal_actions()
        except BalatroConnectionError as e:
            console.print(f"[red]Connection error: {e} - retrying[/red]")
            time.sleep(1.0)
            continue

        phase = state.phase

        # Phase-change banner
        if phase != prev_phase:
            console.print(
                f"\n[bold cyan]-- {phase.value}[/bold cyan]  "
                f"ante={state.ante} round={state.round}  "
                f"${state.money}  "
                f"hands={state.hands_remaining} discards={state.discards_remaining}"
            )
            prev_phase = phase
            if phase == GamePhase.SHOP:
                rerolled_this_shop = 0
                failed_shop_slots.clear()

        if state.error:
            console.print(f"[yellow]  State error: {state.error}[/yellow]")
            time.sleep(0.4)
            continue

        # -- GAME OVER / MENU handle even with no legal actions ---------------
        if phase in (GamePhase.GAME_OVER, GamePhase.MENU):
            pass  # fall through to phase handlers below
        elif not legal.actions:
            time.sleep(0.3)
            continue

        # -- MENU ----------------------------------------------------------
        if phase == GamePhase.MENU:
            r = client.execute_action(
                ActionRequest(type=ActionType.START_RUN, params={"stake": 1}))
            if r.ok:
                console.print("[green]  Run started[/green]")
                time.sleep(3.0)
            else:
                console.print(f"[red]  START_RUN failed: {r.error}[/red]")
                time.sleep(1.0)

        # -- BLIND SELECT --------------------------------------------------
        elif phase == GamePhase.BLIND_SELECT:
            if legal.has_action_type(ActionType.SELECT_BLIND):
                r = client.execute_action(
                    ActionRequest(type=ActionType.SELECT_BLIND, params={}))
                if r.ok:
                    console.print("[green]  Blind selected[/green]")
                    time.sleep(1.5)
                else:
                    console.print(f"[yellow]  {r.error}[/yellow]")
                    time.sleep(0.5)
            else:
                time.sleep(0.3)

        # -- SELECTING HAND ------------------------------------------------
        elif phase == GamePhase.SELECTING_HAND:
            hand = state.hand
            if not hand:
                time.sleep(0.3)
                continue

            # Use consumables before playing (planets level up hands immediately)
            consumable_action = choose_consumable_action(state, legal)
            if consumable_action:
                r = client.execute_action(consumable_action)
                if r.ok:
                    console.print("[green]  Consumable used[/green]")
                    time.sleep(1.2)
                else:
                    console.print(f"[yellow]  Consumable use failed: {r.error}[/yellow]")
                    time.sleep(0.5)
                continue

            needed   = (state.blind.chips_needed  or 0) if state.blind else 0
            scored   = (state.blind.chips_scored   or 0) if state.blind else 0
            console.print(
                f"  Hand: {' '.join(f'{c.rank}{(c.suit or '?')[0]}' for c in hand)}"
                f"  [{scored:,}/{needed:,}]"
            )

            action = choose_play(hand, state.hand_levels,
                                 state.discards_remaining,
                                 state.hands_remaining,
                                 state.jokers)
            r = client.execute_action(action)
            if r.ok:
                console.print("[green]  OK[/green]")
                time.sleep(1.2 if action.type == ActionType.PLAY_HAND else 0.5)
            else:
                console.print(f"[red]  Failed: {r.error}[/red]")
                # If discard failed, try playing instead
                if action.type == ActionType.DISCARD:
                    _, idx, name = best_play(hand, state.hand_levels, state.jokers)
                    console.print(f"  -> Fallback play {name}: {idx}")
                    r2 = client.execute_action(ActionRequest(
                        type=ActionType.PLAY_HAND,
                        params={"card_indices": idx}))
                    if r2.ok:
                        time.sleep(1.2)
                    else:
                        console.print(f"[red]  Fallback also failed: {r2.error}[/red]")
                        time.sleep(0.5)

        # -- ROUND EVAL ----------------------------------------------------
        elif phase == GamePhase.ROUND_EVAL:
            for _ in range(15):
                r = client.execute_action(
                    ActionRequest(type=ActionType.CASH_OUT, params={}))
                if r.ok:
                    console.print("[green]  Cashed out[/green]")
                    time.sleep(1.0)
                    break
                console.print(f"[yellow]  {r.error}[/yellow]")
                time.sleep(0.4)

        # -- SHOP ----------------------------------------------------------
        elif phase == GamePhase.SHOP:
            # Use consumables first — especially Hermit to double money before buying
            consumable_action = choose_consumable_action(state, legal)
            if consumable_action:
                r = client.execute_action(consumable_action)
                if r.ok:
                    console.print("[green]  Consumable used[/green]")
                    time.sleep(1.2)
                else:
                    console.print(f"[yellow]  Consumable use failed: {r.error}[/yellow]")
                    time.sleep(0.5)
                continue

            action = choose_shop_action(state, legal, rerolled_this_shop,
                                        failed_shop_slots)
            r = client.execute_action(action)
            if r.ok:
                if action.type == ActionType.SHOP_REROLL:
                    rerolled_this_shop += 1
                    failed_shop_slots.clear()  # reroll refreshes shop items
                if action.type == ActionType.SHOP_END:
                    console.print("[green]  Left shop[/green]")
                    time.sleep(1.5)
                else:
                    time.sleep(0.5)
            else:
                console.print(f"[red]  Shop action failed: {r.error}[/red]")
                # Mark this slot as failed and try the next best item
                if action.type in (ActionType.SHOP_BUY,
                                   ActionType.SHOP_BUY_BOOSTER,
                                   ActionType.SHOP_BUY_VOUCHER):
                    params = action.params or {}
                    slot = (params.get("slot") if isinstance(params, dict)
                            else getattr(params, "slot", None)) or 0
                    failed_shop_slots.add((action.type, slot))
                    time.sleep(0.5)
                else:
                    # Non-retryable failure → leave
                    client.execute_action(ActionRequest(type=ActionType.SHOP_END))
                    time.sleep(1.0)

        # -- PACK OPENING --------------------------------------------------
        elif phase == GamePhase.PACK_OPENING:
            action = choose_pack_action(state, legal)
            if action is None:
                # Pack cards not dealt yet or all choices used; just wait.
                time.sleep(0.5)
                continue
            r = client.execute_action(action)
            if r.ok:
                console.print("[green]  Pack action OK[/green]")
                time.sleep(2.0)  # give game time to update choices_remaining
            else:
                console.print(f"[red]  Pack action failed: {r.error}[/red]")
                # Do not force-skip: wait and retry next iteration
                time.sleep(1.0)

        # -- GAME OVER -----------------------------------------------------
        elif phase == GamePhase.GAME_OVER:
            console.print(
                f"[red bold]GAME OVER[/red bold]  "
                f"ante={state.ante} round={state.round}")
            time.sleep(4.0)
            r = client.execute_action(
                ActionRequest(type=ActionType.START_RUN, params={"stake": 1}))
            if r.ok:
                console.print("[green]  New run started[/green]")
                time.sleep(3.0)
            else:
                console.print(f"[yellow]  Couldn't restart: {r.error}[/yellow]")
                time.sleep(1.0)

        # -- Transition / unknown ------------------------------------------
        else:
            time.sleep(0.3)


def main():
    import argparse
    p = argparse.ArgumentParser(description="Balatro agent - Red Deck White Stake")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7777)
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

    run_agent(client)


if __name__ == "__main__":
    main()
