#!/usr/bin/env python
"""Compact CLI controller for the Balatro RL bridge.

Every state-changing command needs `--why "one-line rationale"`; it is sent as the action's `meta.why` and
recorded in the trajectory (docs/DATA_CONTRACT.md). Read-only commands (s, hands, advise, shopadvise, legal,
raw, sel) never send an action.
"""
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter

import requests

PORT = os.environ.get("BALATRO_RL_PORT", "7777")
BASE = f"http://127.0.0.1:{PORT}"
RUNS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "docs", "runs")
SUIT = {"Spades": "S", "Hearts": "H", "Clubs": "C", "Diamonds": "D"}
RANK = {"Ace": "A", "King": "K", "Queen": "Q", "Jack": "J", "10": "T"}
WHY_MAX = 300


def get(path):
    return requests.get(f"{BASE}/{path}", timeout=5).json()


def _client_id():
    with open(os.path.abspath(__file__), "rb") as f:
        return "cli.py@" + hashlib.sha1(f.read()).hexdigest()[:10]


_META = {}


def act(typ, params):
    body = {"type": typ, "params": params, "meta": _META}
    return requests.post(f"{BASE}/action", json=body, timeout=10).json()


def preview(idxs):
    """Read-only /preview: the game's own poker-hand reading of a hypothetical selection (no state change)."""
    return requests.post(f"{BASE}/preview", json={"card_indices": idxs}, timeout=5).json()


def wait_settled(timeout=30.0):
    """Poll /state until the bridge reports a settled decision point; returns the last state seen."""
    t0 = time.time()
    d = get("state")
    while not d.get("settled") and time.time() - t0 < timeout:
        time.sleep(0.25)
        d = get("state")
    if not d.get("settled"):
        print(f"(state not settled after {timeout:.0f}s: phase {d.get('phase')}; run `s` again shortly)")
    return d


def card_str(c):
    r = str(c.get("rank"))
    r = RANK.get(r, r)
    s = SUIT.get(c.get("suit"), str(c.get("suit"))[:1])
    tags = []
    if c.get("enhancement") and c.get("enhancement") not in ("Default Base", "c_base"):
        tags.append(str(c["enhancement"]).replace("m_", ""))
    if c.get("edition"):
        tags.append(str(c["edition"]))
    if c.get("seal"):
        tags.append(str(c["seal"]) + "seal")
    if c.get("debuff"):
        tags.append("DEBUFF")
    if c.get("facing") == "back":
        tags.append("facedown")
    t = "(" + ",".join(tags) + ")" if tags else ""
    return f"{r}{s}{t}"


def lst(v):
    if isinstance(v, dict):
        return list(v.values()) if v else []
    return v or []


def _enh(c):
    """Enhancement as a capitalised word ("m_glass" -> "Glass"; "" when none)."""
    e = str(c.get("enhancement") or "")
    return e[2:].capitalize() if e.startswith("m_") else e


LEGAL = {}  # last /legal response (filled by main before advising or acting)


def usable_cons():
    """Indices of consumables the game lets you use right now (from /legal)."""
    return {i for a in legal_entries(LEGAL, "USE_CONSUMABLE") for i in ((a.get("params") or {}).get("index") or {}).get("one_of", [])}


def stickers(c):
    """Stake stickers on a joker (owned, shop or pack): eternal (never sellable), perishable (debuffed after N rounds),
    rental (-$3 per round)."""
    src = dict(c.get("ability") or {})
    st = c.get("stickers")
    if isinstance(st, dict):
        src.update(st)
    elif isinstance(st, list):
        src.update({s: True for s in st})
    src.update({k: c[k] for k in ("eternal", "perishable", "perish_tally", "rental") if k in c})
    out = []
    if src.get("eternal"):
        out.append("ETERNAL")
    if src.get("perishable"):
        out.append(f"PERISHABLE({src.get('perish_tally', '?')} rounds left)")
    if src.get("rental"):
        out.append("RENTAL(-$3/round)")
    return f"{{{','.join(out)}}}" if out else ""


def show(d):
    ph = d.get("phase")
    b = d.get("blind") or {}
    dc = d.get("deck") or {}
    print(f"[{ph}] stake {d.get('stake')} ante {d.get('ante')} rnd {d.get('round')} | ${d.get('money')} | hands {d.get('hands_remaining')} disc {d.get('discards_remaining')} "
          f"| blind {b.get('name')} need {b.get('chips_needed')} scored {b.get('chips_scored')} | deck {dc.get('draw_pile')}/disc {dc.get('discard_pile')}")
    hand = lst(d.get("hand"))
    if hand:
        print("Hand: " + " ".join(f"{c.get('index')}:{card_str(c)}" for c in hand))
        suits = Counter(SUIT.get(c.get("suit"), "?") for c in hand)
        ranks = Counter(RANK.get(str(c.get("rank")), str(c.get("rank"))) for c in hand)
        print("  suits " + " ".join(f"{k}{v}" for k, v in suits.most_common()) + " | ranks " + " ".join(f"{k}x{v}" for k, v in ranks.most_common() if v > 1))
    jk = lst(d.get("jokers"))
    if jk:
        print(f"Jokers ({len(jk)}/{d.get('joker_slots')}) cons_slots {d.get('consumable_slots')} hand_size {d.get('hand_size')}: " + " | ".join(f"[{j.get('index', i + 1)}] {j.get('name')}{stickers(j)} ({JOKER_DESC.get(j.get('name'), 'effect not in table')}) sell${j.get('sell_cost')}"
                                    + (f" {j['edition'].get('type', j['edition']) if isinstance(j.get('edition'), dict) else j['edition']}" if j.get("edition") else "")
                                    + (f" ab={compact_ability(j.get('ability'))}" if compact_ability(j.get('ability')) else "")
                                    for i, j in enumerate(jk)))
    tg = lst(d.get("tags"))
    if tg:
        print("Tags: " + ", ".join(str(t.get("name")) + (f"({t['orbital_hand']})" if t.get("orbital_hand") else "") for t in tg))
    cons = lst(d.get("consumables"))
    if cons:
        print("Cons: " + " | ".join(f"[{c.get('index')}] {c.get('name')} ({c.get('set')}){'' if c.get('index') in usable_cons() else ' NOUSE'}" for c in cons))
    hl = d.get("hand_levels") or {}
    lv = [f"{k} L{v.get('level')}({v.get('chips')}x{v.get('mult')})" for k, v in hl.items() if (v.get("level") or 1) > 1]
    if lv:
        print("Levels: " + ", ".join(lv))
    sh = d.get("shop")
    if sh and ph == "SHOP":
        js = " ".join(f"J{c['index']}:{c.get('name')}{stickers(c)}${c.get('cost')}" + (f"[{c['edition']}]" if c.get("edition") else "") + f"<{c.get('set')}>" for c in lst(sh.get("jokers")))
        vs = " ".join(f"V{c['index']}:{c.get('name')}${c.get('cost')}" for c in lst(sh.get("vouchers")))
        bs = " ".join(f"B{c['index']}:{c.get('name')}${c.get('cost')}" for c in lst(sh.get("boosters")))
        print(f"Shop: {js} | {vs} | {bs} | reroll ${sh.get('reroll_cost')}")
    pk = d.get("pack")
    if pk and ph == "PACK_OPENING":
        cards = lst(pk.get("cards"))
        print(f"Pack (choose {pk.get('choices_remaining')}): " + " | ".join(f"{i + 1}:{pack_card(c)}" for i, c in enumerate(cards)))
    bs = d.get("blind_select")
    if bs and ph == "SHOP":
        boss = ((bs.get("choices") or {}).get("Boss") or {}).get("name")
        if boss:
            print(f"Upcoming boss this ante: {boss}")
    if bs and ph == "BLIND_SELECT":
        ch = bs.get("choices") or {}
        parts = []
        for k in ("Small", "Big", "Boss"):
            c = ch.get(k) or {}
            parts.append(f"{k}:{c.get('name')} {c.get('chips')} [{c.get('state')}]" + (f" tag={c.get('tag')}/{c.get('tag_key')}" if c.get("tag") else "") + (f"({c['orbital_hand']})" if c.get("orbital_hand") and c["orbital_hand"] != "[poker hand]" else ""))
        print(f"Blinds (on deck {bs.get('on_deck')}): " + " | ".join(parts))
        SKIP_TAGS = {"tag_uncommon": "a free Uncommon joker", "tag_rare": "a free Rare joker", "tag_negative": "next shop joker becomes Negative (free slot)",
                     "tag_foil": "next shop joker Foil (+50 chips)", "tag_holo": "next shop joker Holographic (+10 mult)", "tag_polychrome": "next shop joker Polychrome (x1.5)",
                     "tag_buffoon": "a free Buffoon pack (joker choice)", "tag_charm": "a free Mega Arcana pack", "tag_meteor": "a free Mega Celestial pack",
                     "tag_ethereal": "a free Spectral pack", "tag_coupon": "next shop's jokers and packs are free", "tag_top_up": "two free Common jokers",
                     "tag_investment": "$25 after the boss"}
        small = ch.get("Small") or {}
        stake_n = int(d.get("stake") or 1)
        tk = str(small.get("tag_key") or "")
        JOKER_TAGS = {"tag_uncommon", "tag_rare", "tag_buffoon", "tag_top_up", "tag_coupon"}
        scoring_j = sum(1 for j in lst(d.get("jokers")) if classify_joker(j.get("name"), 0, main_hand(d))[0] in ("PLUS", "PLUS(main hand)", "PLUS(common condition)", "PLUS(fires on any pair-family hand)", "PLUS(permanent growth)") or (classify_joker(j.get("name"), 0, main_hand(d))[0].startswith("XMULT") and "conditional" not in classify_joker(j.get("name"), 0, main_hand(d))[0]))
        skip_ok = tk in JOKER_TAGS or (tk in SKIP_TAGS and scoring_j >= 2)  # with fewer than 2 scoring jokers only a tag that GIVES a joker beats the shop visit
        USELESS_TAGS = {"tag_boss", "tag_double", "tag_handy", "tag_garbage"}
        # ante-1 Small Blind with no jokers: 3 pair-shaped hands vs 300 lost 4 of ~8 stake-2 attempts this morning (292/300, 256/300, 224/300,
        # 352/600 after a $0 shop); the $4 shop it unlocks rarely buys a joker, so skip for any tag except the useless Boss tag.
        # 2026-08-30 stake 3: skipping for a non-joker tag sent jokerless decks into the 450 Big Blind and lost 284, 404, 436 of 450;
        # the shop after the Small Blind is the only chance at a joker before it, so only joker/pack tags justify the skip now.
        ante1_skip = False
        if bs.get("on_deck") == "Small" and stake_n >= 2 and int(d.get("ante") or 1) <= 4 and (skip_ok or ante1_skip):
            why_tag = SKIP_TAGS.get(tk, f"the {small.get('tag')} tag")
            extra = " With no jokers the ante-1 Small Blind (300 in 3 hands) is lost to card variance about 1 run in 10 for a $0 reward; the Big Blind pays and still gets a shop." if ante1_skip and tk not in SKIP_TAGS else ""
            print(f"ADVICE: b skip   (stake {stake_n}: the Small Blind pays $0, so skipping it costs only one shop visit and gives {why_tag} ({small.get('tag')}).{extra} Big and Boss blinds are never skipped.)")
        else:
            print("ADVICE: b blind   (never skip the Big or Boss blind; at stake 1 never skip at all: income and a shop matter more than any tag)")

JOKER_DESC = {
    "Joker": "+4 mult", "Jolly Joker": "+8 mult if hand has a Pair", "Zany Joker": "+12 mult if Three of a Kind",
    "Mad Joker": "+10 mult if Two Pair", "Crazy Joker": "+12 mult if Straight", "Droll Joker": "+10 mult if Flush",
    "Sly Joker": "+50 chips if Pair", "Wily Joker": "+100 chips if Three of a Kind", "Clever Joker": "+80 chips if Two Pair",
    "Devious Joker": "+100 chips if Straight", "Crafty Joker": "+80 chips if Flush", "Half Joker": "+20 mult if <=3 cards played",
    "Smiley Face": "+5 mult per scoring face card", "Scary Face": "+30 chips per scoring face card",
    "Photograph": "x2 mult on first scoring face card", "Greedy Joker": "+3 mult per Diamond", "Lusty Joker": "+3 mult per Heart",
    "Wrathful Joker": "+3 mult per Spade", "Gluttonous Joker": "+3 mult per Club", "Even Steven": "+4 mult per even card",
    "Odd Todd": "+31 chips per odd card", "Fibonacci": "+8 mult per A/2/3/5/8", "Scholar": "+20 chips +4 mult per Ace",
    "Walkie Talkie": "+10 chips +4 mult per 10/4", "Card Sharp": "x3 mult if this hand type already played this round",
    "The Duo": "x2 mult if Pair", "The Trio": "x3 mult if Three of a Kind", "The Family": "x4 mult if Four of a Kind",
    "The Order": "x3 mult if Straight", "The Tribe": "x2 mult if Flush", "Abstract Joker": "+3 mult per joker owned",
    "Stuntman": "+250 chips, -2 hand size", "Baron": "x1.5 mult per King held in hand", "Blackboard": "x3 if all held cards Spades/Clubs",
    "Bull": "+2 chips per $", "Campfire": "xMult grows +0.25 per card sold, resets after boss", "Constellation": "xMult grows +0.1 per planet used",
    "Hologram": "xMult grows +0.25 per card added to deck", "Cavendish": "x3 mult (1/1000 destroyed)", "Gros Michel": "+15 mult (1/6 destroyed)",
    "Steel Joker": "x0.2 per Steel card in deck", "Glass Joker": "x0.75 per Glass card destroyed", "Madness": "xMult +0.5 per blind, destroys a joker",
    "Ramen": "x2 mult, -0.01 per discard", "Throwback": "x0.25 per blind skipped", "Vampire": "xMult +0.1 per enhanced card played",
    "Hit the Road": "x0.5 per Jack discarded this round", "Lucky Cat": "xMult +0.25 per Lucky trigger", "Green Joker": "+1 mult per hand, -1 per discard",
    "Ride the Bus": "+1 mult per consecutive hand without a face", "Square Joker": "+4 chips per 4-card hand played", "Runner": "+15 chips per Straight played",
    "Ice Cream": "+100 chips, -5 per hand", "Popcorn": "+20 mult, -4 per round", "Supernova": "+mult = times this hand played",
    "Misprint": "+0..23 mult random", "Acrobat": "x3 on final hand of round", "Mystic Summit": "+15 mult when 0 discards left",
    "Banner": "+30 chips per discard remaining", "Flower Pot": "x3 if all four suits scored", "Seeing Double": "x2 if a Club and another suit score",
    "Triboulet": "x2 per scoring K/Q", "Bloodstone": "1/2 chance x1.5 per Heart", "Arrowhead": "+50 chips per Spade", "Onyx Agate": "+7 mult per Club",
    "Rough Gem": "+$1 per Diamond", "Cloud 9": "+$1 per 9 in deck each round", "Golden Joker": "+$4 per round", "Egg": "+$3 sell value per round",
    "Rocket": "+$1 per round, grows at bosses", "To the Moon": "+1 interest per $5", "Satellite": "+$1 per unique planet used",
    "Delayed Gratification": "$2 per discard if none used", "Astronomer": "Planets and Celestial packs free", "Luchador": "sell to disable boss blind",
    "Chaos the Clown": "1 free reroll per shop", "Juggler": "+1 hand size", "Drunkard": "+1 discard", "Troubadour": "+2 hand size, -1 hand",
    "Burglar": "+3 hands, no discards", "Four Fingers": "4-card flushes/straights", "Shortcut": "straights with gaps", "Splash": "every played card scores",
    "The Idol": "x2 mult per scored card of the shown rank+suit (changes every round)", "Pareidolia": "all cards count as faces", "Smeared Joker": "Hearts=Diamonds, Spades=Clubs", "Blueprint": "copies joker to the right",
    "Brainstorm": "copies leftmost joker", "Mime": "retrigger held-in-hand effects", "Dusk": "retrigger cards on final hand", "Hack": "retrigger 2/3/4/5",
    "Sock and Buskin": "retrigger face cards", "Hanging Chad": "retrigger first card 2x", "Seltzer": "retrigger all cards, 10 hands",
    "Joker Stencil": "x1 per empty joker slot", "Loyalty Card": "x4 every 6 hands", "8 Ball": "1/4 tarot per 8 played", "Vagabond": "tarot if hand played with <=$4",
    "Riff-Raff": "2 common jokers at blind start", "Ceremonial Dagger": "destroys joker to right at blind start, gains double its value as mult",
    "Fortune Teller": "+1 mult per tarot used", "Space Joker": "1/4 level up played hand", "Sixth Sense": "destroy lone 6 for a spectral",
    "DNA": "copy first card if 1 card played hand 1", "Faceless Joker": "$5 if 3+ faces discarded", "Marble Joker": "adds Stone card per blind",
    "Credit Card": "-$20 debt allowed", "Turtle Bean": "+5 hand size, -1 per round", "Erosion": "+4 mult per card below 52 in deck",
    "Stone Joker": "+25 chips per Stone card", "Wee Joker": "+8 chips per 2 scored (permanent)", "Hiker": "+5 chips permanently per scored card",
    "Castle": "+3 chips per discarded card of a suit", "Blue Joker": "+2 chips per card in deck", "Obelisk": "x0.2 per hand not most played",
    "Spare Trousers": "+2 mult per Two Pair played", "Swashbuckler": "+mult = sell value of other jokers", "Bootstraps": "+2 mult per $5",
    "Red Card": "+3 mult per pack skipped", "Matador": "$8 if boss ability triggers", "Reserved Parking": "faces held 1/2 chance $1",
    "Mail-In Rebate": "$5 per discarded card of a rank", "To Do List": "$4 if listed hand played", "Trading Card": "destroy lone discard for $3",
    "Business Card": "faces held 1/2 chance $2", "Gift Card": "+$1 sell value to jokers per round", "Golden Ticket": "$4 per Gold card scored",
    "Midas Mask": "faces become Gold when played", "Driver's License": "x3 if 16+ enhanced cards", "Burnt Joker": "level up first discarded hand",
    "Perkeo": "copies consumable at end of shop", "Chicot": "disables boss", "Canio": "x1 per face destroyed", "Yorick": "x1 per 23 discards",
    "Showman": "duplicates allowed", "Oops! All 6s": "doubles probabilities", "Invisible Joker": "duplicate a joker after 2 rounds",
    "Certificate": "adds sealed card at round start", "Hallucination": "1/2 tarot when pack opened", "Seance": "spectral on Straight Flush",
    "Superposition": "tarot if Ace in Straight", "Cartomancer": "tarot at blind select", "Mr. Bones": "survive at 25% of blind, destroys self",
    "Diet Cola": "sell for Double Tag", "Merry Andy": "+3 discards, -1 hand size", "Ancient Joker": "x1.5 per card of a rotating suit",
    "Shoot the Moon": "+13 mult per Queen held", "Baseball Card": "x1.5 per uncommon joker", "Idol": "x2 on a specific card",
    "Duo": "x2 if Pair", "Raised Fist": "+2x lowest held card rank mult", "Hanged Man": "", "Stencil": "",
}


def compact_ability(a):
    if not a or not isinstance(a, dict):
        return ""
    keep = {k: v for k, v in a.items() if k in ("mult", "x_mult", "extra", "t_mult", "t_chips", "h_size", "d_size", "chips") and v not in (0, None, {}, [], 1)}
    return json.dumps(keep, separators=(",", ":")) if keep else ""


def pack_card(c):
    if c.get("rank") or c.get("suit"):
        return card_str(c)
    n = c.get("name") or c.get("key") or "?"
    extra = []
    if c.get("edition"):
        extra.append(str(c["edition"]))
    if c.get("set"):
        extra.append(str(c["set"]))
    return n + stickers(c) + (f"({','.join(extra)})" if extra else "")


RANK_VAL = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
CHIP_VAL = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 10, "Q": 10, "K": 10, "A": 11}
FACES = {"J", "Q", "K"}


# --- Score estimator (best effort; unknown jokers are listed, not modeled) -------------------------
HAND_WORDS = {"HIGH": "High Card", "PAIR": "Pair", "TWOPAIR": "Two Pair", "TRIPS": "Three of a Kind",
              "STRAIGHT": "Straight", "FLUSH": "Flush", "FULLHOUSE": "Full House", "QUADS": "Four of a Kind",
              "STRAIGHTFLUSH": "Straight Flush", "ROYALFLUSH": "Royal Flush", "FIVE": "Five of a Kind",
              "FLUSHHOUSE": "Flush House", "FLUSHFIVE": "Flush Five"}
SUIT_JOKERS = {"Greedy Joker": "D", "Lusty Joker": "H", "Wrathful Joker": "S", "Gluttonous Joker": "C"}
TYPE_X_JOKERS = {"The Duo": ("Pair", 2), "The Trio": ("Three of a Kind", 3), "The Family": ("Four of a Kind", 4),
                 "The Order": ("Straight", 3), "The Tribe": ("Flush", 2)}
MODELED = {"Joker", "Jolly Joker", "Zany Joker", "Mad Joker", "Crazy Joker", "Droll Joker", "Sly Joker", "Wily Joker",
           "Clever Joker", "Devious Joker", "Crafty Joker", "Half Joker", "Smiley Face", "Scary Face", "Photograph",
           "Even Steven", "Odd Todd", "Fibonacci", "Scholar", "Walkie Talkie", "Card Sharp", "Abstract Joker",
           "Stuntman", "Baron", "Blackboard", "Bull", "Campfire", "Constellation", "Hologram", "Madness", "Vampire",
           "Ramen", "Throwback", "Glass Joker", "Cavendish", "Gros Michel", "Ceremonial Dagger", "Green Joker",
           "Red Card", "Ride the Bus", "Square Joker", "Runner", "Ice Cream", "Popcorn", "Spare Trousers", "Fortune Teller",
           "Bootstraps", "Swashbuckler", "Erosion", "Supernova", "Banner", "Mystic Summit", "Misprint", "Acrobat",
           "Steel Joker", "Stone Joker", "Flower Pot", "Seeing Double", "Triboulet", "Hit the Road", "Lucky Cat",
           "Wee Joker", "Obelisk", "Castle", "Hiker", "Blue Joker", "Bloodstone", "Arrowhead", "Onyx Agate", "Rough Gem",
           "Onyx Agate", "Shortcut", "Four Fingers", "Pareidolia", "Smeared Joker", "Splash", "Cloud 9", "Golden Joker",
           "Egg", "Rocket", "To the Moon", "Satellite", "Delayed Gratification", "Astronomer", "Luchador", "Chaos the Clown",
           "Credit Card", "Juggler", "Drunkard", "Troubadour", "Merry Andy", "Oops! All 6s", "Burglar", "Gift Card",
           "Turtle Bean", "Marble Joker", "Hallucination", "Sixth Sense", "Seance", "Vagabond", "Cartomancer",
           "Superposition", "8 Ball", "Riff-Raff", "Certificate", "DNA", "Faceless Joker", "Invisible Joker", "Brainstorm",
           "Blueprint", "Showman", "Mr. Bones", "Chicot", "Perkeo", "Yorick", "Canio", "Mail-In Rebate", "To Do List",
           "Matador", "Reserved Parking", "Trading Card", "Business Card", "Space Joker", "Dusk", "Sock and Buskin",
           "Hanging Chad", "Hack", "Mime", "Seltzer", "Loyalty Card", "Joker Stencil", "Driver's License", "Burnt Joker",
           "Diet Cola", "Midas Mask", "Cloud 9"}
CARD_TRIGGER_JOKERS = {"Smiley Face", "Scary Face", "Photograph", "Even Steven", "Odd Todd", "Fibonacci", "Scholar",
                       "Walkie Talkie", "Triboulet", "Bloodstone", "Arrowhead", "Onyx Agate", "Rough Gem", "Hiker",
                       "Hack", "Sock and Buskin", "Dusk", "Seltzer", "Hanging Chad", "Ancient Joker"} | set(SUIT_JOKERS)


# Balatro "hand contains X" semantics: a hand of a richer type also contains the simpler ones.
CONTAINS = {
    "High Card": {"High Card"},
    "Pair": {"Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind", "Five of a Kind", "Flush House", "Flush Five"},
    "Two Pair": {"Two Pair", "Full House", "Flush House"},  # the game needs two distinct pairs (or trips+pair): Quads do not count
    "Three of a Kind": {"Three of a Kind", "Full House", "Four of a Kind", "Five of a Kind", "Flush House", "Flush Five"},
    "Four of a Kind": {"Four of a Kind", "Five of a Kind", "Flush Five"},
    "Straight": {"Straight", "Straight Flush"},
    "Flush": {"Flush", "Straight Flush", "Flush House", "Flush Five"},
    "Full House": {"Full House", "Flush House"},
    "Straight Flush": {"Straight Flush"},
}


def hand_contains(hand_name, needed):
    return hand_name in CONTAINS.get(needed, {needed})


def _r(c):
    return RANK.get(str(c.get("rank")), str(c.get("rank")))


SMEAR = {"H": "HD", "D": "HD", "S": "SC", "C": "SC"}


def _suit_key(c, jnames):
    """suit group key; Smeared Joker merges Hearts/Diamonds and Spades/Clubs; Wild cards join any suit."""
    su = SUIT.get(c.get("suit"), "?")
    if "Wild" in _enh(c):
        return "WILD"
    return SMEAR.get(su, su) if "Smeared Joker" in jnames else su


def _suit_matches(c, wanted, jnames):
    su = SUIT.get(c.get("suit"), "?")
    if "Wild" in _enh(c):
        return True
    if "Smeared Joker" in jnames:
        return SMEAR.get(su) == SMEAR.get(wanted)
    return su == wanted


def _suit_cover(scoring, jnames):
    """suits covered by a scoring hand the way Flower Pot/Seeing Double count them: each non-Wild card fills the
    first still-empty suit it matches (Smeared Joker lets a Heart fill Diamonds etc.), Wild cards fill leftovers."""
    covered = set()
    plain = [c for c in scoring if "Wild" not in _enh(c)]
    wild_n = len(scoring) - len(plain)
    for c in plain:
        for su in ("H", "D", "S", "C"):
            if su not in covered and _suit_matches(c, su, jnames):
                covered.add(su)
                break
    for su in ("H", "D", "S", "C"):
        if wild_n and su not in covered:
            covered.add(su)
            wild_n -= 1
    return covered


def _is_face(c):
    return _r(c) in FACES


def _joker_edition(j):
    e = j.get("edition")
    if isinstance(e, dict):
        return e.get("type") or ("holo" if e.get("holo") else "foil" if e.get("foil") else "polychrome" if e.get("polychrome") else None)
    return e


def estimate(hand_name, scoring, held, state, repeat=None, played_n=None):
    """Return (score, notes). scoring = cards that form the hand; held = remaining hand cards (not played)."""
    notes = []
    hl = (state.get("hand_levels") or {}).get(hand_name) or {}
    chips = float(hl.get("chips") or 0)
    mult = float(hl.get("mult") or 1)
    boss = ((state.get("blind") or {}).get("name") or "") if (state.get("blind") or {}).get("boss") else ""
    if boss == "The Flint":
        chips = float(int(chips // 2)); mult = float(int(mult // 2)) or 1.0
        notes.append("The Flint: base chips and mult halved")
    if boss == "The Arm" and int(hl.get("level") or 1) > 1:
        inc = {"High Card": (10, 1), "Pair": (15, 1), "Two Pair": (20, 1), "Three of a Kind": (20, 2), "Straight": (30, 3),
               "Flush": (15, 2), "Full House": (25, 2), "Four of a Kind": (30, 3), "Straight Flush": (40, 4)}.get(hand_name, (0, 0))
        chips -= inc[0]; mult -= inc[1]
        notes.append("The Arm: scored at one level lower (and the level is lost)")
    jokers = lst(state.get("jokers"))
    # Blueprint copies the joker to its right, Brainstorm copies the leftmost joker: score them as that joker
    resolved = []
    for i, j in enumerate(jokers):
        n0 = j.get("name")
        if n0 == "Blueprint":
            k = i + 1
            while k < len(jokers) and jokers[k].get("name") in ("Blueprint", "Brainstorm"):
                k += 1
            resolved.append(dict(jokers[k], edition=j.get("edition")) if k < len(jokers) else j)
        elif n0 == "Brainstorm":
            resolved.append(dict(jokers[0], edition=j.get("edition")) if jokers and jokers[0].get("name") not in ("Blueprint", "Brainstorm") else j)
        else:
            resolved.append(j)
    jokers = resolved
    jnames = [j.get("name") for j in jokers]
    scoring = sorted(scoring, key=lambda c: c.get("index") or 0)
    is_face = (lambda c: c.get("rank") is not None) if "Pareidolia" in jnames else _is_face  # Pareidolia: every card is a face
    first_face_done = False
    first_face_idx = next((c.get("index") for c in scoring if is_face(c) and not c.get("debuff")), None)
    final_hand = int(state.get("hands_remaining") or 0) == 1
    expanded = []
    for pos, c in enumerate(scoring):
        times = 1
        if "Hack" in jnames and _r(c) in {"2", "3", "4", "5"}:
            times += 1
        if "Sock and Buskin" in jnames and is_face(c):
            times += 1
        if "Dusk" in jnames and final_hand:
            times += 1
        if "Seltzer" in jnames:
            times += 1
        if "Hanging Chad" in jnames and pos == 0:
            times += 2
        if str(c.get("seal") or "") == "Red":
            times += 1
        expanded.extend([c] * times)
    vamp_n = sum(1 for c in scoring if c.get("enhancement") and not c.get("debuff"))  # Vampire grows +0.1 per enhanced card, before it fires
    for c in expanded:
        if c.get("debuff"):
            notes.append("debuffed card scores nothing")
            continue
        enh = _enh(c)
        if "Vampire" in jnames:
            enh = ""  # Vampire strips the enhancement before the card scores
        if "Stone" in enh:
            chips += 50
        else:
            chips += CHIP_VAL.get(_r(c), 0)
        chips += float(c.get("perma_bonus") or 0)
        mult += float(c.get("perma_mult") or 0)
        if "Bonus" in enh:
            chips += 30
        if enh.startswith("Mult"):
            mult += 4
        if "Glass" in enh:
            mult *= 2
        if "Lucky" in enh:
            notes.append("Lucky card: +20 mult 1 in 5, not counted (est is the floor)")
        ed = c.get("edition")
        if ed == "foil":
            chips += 50
        elif ed == "holo":
            mult += 10
        elif ed == "polychrome":
            mult *= 1.5
        for j in jokers:
            n = j.get("name")
            if n == "Smiley Face" and is_face(c):
                mult += 5
            elif n == "Scary Face" and is_face(c):
                chips += 30
            elif n == "Photograph" and c.get("index") == first_face_idx:
                mult *= 2  # fires on every trigger of the first face card (Red seal / Hanging Chad / Sock and Buskin retriggers included)
                first_face_done = True
            elif n in SUIT_JOKERS and _suit_matches(c, SUIT_JOKERS[n], jnames):
                mult += 3
            elif n == "Even Steven" and _r(c) in {"2", "4", "6", "8", "T"}:
                mult += 4
            elif n == "Odd Todd" and _r(c) in {"A", "3", "5", "7", "9"}:
                chips += 31
            elif n == "Fibonacci" and _r(c) in {"A", "2", "3", "5", "8"}:
                mult += 8
            elif n == "Scholar" and _r(c) == "A":
                chips += 20
                mult += 4
            elif n == "Walkie Talkie" and _r(c) in {"T", "4"}:
                chips += 10
                mult += 4
            elif n == "Triboulet" and _r(c) in {"K", "Q"}:
                mult *= 2
            elif n == "The Idol":
                idol = (state.get("run") or {}).get("idol_card")
                if isinstance(idol, dict):
                    ir = RANK.get(str(idol.get("rank")), str(idol.get("rank")))
                    if _r(c) == ir and SUIT.get(c.get("suit")) == SUIT.get(idol.get("suit"), str(idol.get("suit"))[:1]):
                        mult *= 2
            elif n == "Ancient Joker":
                suit_a = ((state.get("run") or {}).get("ancient_card") or {}).get("suit")
                if suit_a and SUIT.get(c.get("suit")) == SUIT.get(suit_a, suit_a[:1]):
                    mult *= 1.5
                elif not suit_a:
                    notes.append("Ancient Joker suit unknown: x1.5 per matching card not counted")
            elif n == "Bloodstone" and SUIT.get(c.get("suit")) == "H":
                notes.append("Bloodstone 50% x1.5 not counted")
            elif n == "Arrowhead" and _suit_matches(c, "S", jnames):
                chips += 50
            elif n == "Onyx Agate" and _suit_matches(c, "C", jnames):
                mult += 7
            elif n == "Rough Gem" and SUIT.get(c.get("suit")) == "D":
                notes.append("Rough Gem +$1")
    held = [c for c in held if not c.get("debuff")]
    # held-card phase: joker +mult from held cards (Raised Fist, Shoot the Moon) lands before the Steel x1.5
    # (verified against logged hands: est was 26% low when Steel was applied first)
    for j in jokers:
        n0 = j.get("name")
        if n0 == "Shoot the Moon":
            mult += 13 * sum(1 for c in held if _r(c) == "Q")
        elif n0 == "Raised Fist":
            lows = [RANK_VAL.get(_r(c), 0) for c in held if c.get("rank") is not None]
            if lows:
                lo = min(lows)
                mult += 2 * (11 if lo == 14 else min(lo, 10))
    for c in held:
        enh = _enh(c)
        if "Steel" in enh:
            mult *= 1.5
    for j in jokers:
        n = j.get("name")
        ab = j.get("ability") or {}
        ed = _joker_edition(j)
        if ed == "foil":
            chips += 50
        elif ed == "holo":
            mult += 10
        if n in CARD_TRIGGER_JOKERS:
            pass
        elif n == "Half Joker":
            if (played_n if played_n is not None else len(scoring)) <= 3:
                mult += 20
        elif n == "Card Sharp":
            x = (ab.get("extra") or {}).get("Xmult", 3) if isinstance(ab.get("extra"), dict) else 3
            if repeat is True:
                mult *= x
            elif repeat is None:
                notes.append(f"Card Sharp x{x} only if the played type was already played this round")
        elif n in TYPE_X_JOKERS:
            t, x = TYPE_X_JOKERS[n]
            if hand_contains(hand_name, t):
                mult *= x
        elif n == "Abstract Joker":
            mult += 3 * len(jokers)
        elif n == "Cavendish":
            mult *= 3
        elif n in ("Caino", "Canio"):
            mult *= float(ab.get("caino_xmult") or ab.get("x_mult") or 1)
        elif n == "Yorick":
            mult *= float(ab.get("x_mult") or 1)
        elif n == "Baseball Card":
            unc = sum(1 for j2 in jokers if int(j2.get("rarity") or 0) == 2)
            mult *= 1.5 ** unc
        elif n == "Loyalty Card":
            rem = ab.get("loyalty_remaining")  # the game recomputes this DURING scoring: the stored value is one hand stale
            if rem == 1:
                mult *= float((ab.get("extra") or {}).get("Xmult", 4) if isinstance(ab.get("extra"), dict) else 4)
                notes.append("Loyalty Card fires on THIS hand (x4)")
            elif rem == 0:
                notes.append("Loyalty Card fired on the LAST hand: x4 again in 6 hands")
            else:
                notes.append(f"Loyalty Card x4 in {rem - 1} more hand(s)" if rem is not None else "Loyalty Card x4 every 6 hands: timing unknown")
        elif n == "Gros Michel":
            mult += 15
        elif n == "Blue Joker":
            chips += 2 * int(((state.get("deck") or {}).get("draw_pile")) or 0)
        elif n == "Supernova":
            mult += int(((state.get("hand_levels") or {}).get(hand_name) or {}).get("played") or 0) + 1
        elif n == "Ride the Bus":
            if any(is_face(c) for c in scoring):
                notes.append("Ride the Bus resets: a face card scores in this hand")
            else:
                mult += float(ab.get("mult") or 0) + 1
        elif n == "Square Joker":
            chips += float(ab.get("extra", {}).get("chips", 0) if isinstance(ab.get("extra"), dict) else 0)
        elif n == "Spare Trousers":
            mult += float(ab.get("mult") or 0)
        elif n == "Runner":
            chips += float(ab.get("extra", {}).get("chips", 0) if isinstance(ab.get("extra"), dict) else 0)
        elif n == "Ice Cream":
            chips += float(ab.get("extra", {}).get("chips", 0) if isinstance(ab.get("extra"), dict) else 0)
        elif n == "Popcorn":
            mult += float(ab.get("mult") or 0)
        elif n == "Green Joker":
            mult += float(ab.get("mult") or 0) + 1  # it gains +1 for this hand before scoring
        elif n == "Bootstraps":
            mult += 2 * (int(state.get("money") or 0) // 5)
        elif n == "Swashbuckler":
            mult += sum(int(j2.get("sell_cost") or 0) for j2 in jokers if j2 is not j)
        elif n == "Fortune Teller":
            mult += float(ab.get("mult") or 0)
        elif n == "Erosion":
            mult += 4 * max(0, 52 - int(((state.get("deck") or {}).get("total")) or 52))
        elif n == "Stone Joker":
            notes.append("Stone Joker +25 per Stone card in deck not counted")
        elif n == "Steel Joker":
            notes.append("Steel Joker xMult per Steel card not counted")
        elif n == "Stuntman":
            chips += 250
        elif n == "Baron":
            ks = sum(1 for c in held if _r(c) == "K")
            mult *= 1.5 ** ks
        elif n in ("Shoot the Moon", "Raised Fist"):
            pass  # applied in the held-card phase above
        elif n == "Reserved Parking" or n == "Business Card":
            pass
        elif n == "Blackboard":
            if all(SUIT.get(c.get("suit")) in {"S", "C"} for c in held):
                mult *= 3
        elif n == "Bull":
            chips += 2 * max(0, int(state.get("money") or 0))
        elif n == "Mystic Summit":
            if int(state.get("discards_remaining") or 0) == 0:
                mult += 15
        elif n == "Acrobat":
            if int(state.get("hands_remaining") or 0) == 1:
                mult *= 3
        elif n == "Banner":
            chips += 30 * int(state.get("discards_remaining") or 0)
        elif n == "Misprint":
            mult += 6
            notes.append("Misprint random 0-23 mult, using conservative 6 (mean 11)")
        elif n == "Flower Pot":
            if {"S", "H", "C", "D"} <= _suit_cover(scoring, jnames):
                mult *= 3
        elif n == "Seeing Double":
            suits = _suit_cover(scoring, jnames)
            if "C" in suits and len(suits) > 1:
                mult *= 2
        else:
            applied = False
            t_type = ab.get("type")
            if ab.get("t_mult") and t_type and hand_contains(hand_name, t_type):
                mult += float(ab["t_mult"]); applied = True
            if ab.get("t_chips") and t_type and hand_contains(hand_name, t_type):
                chips += float(ab["t_chips"]); applied = True
            if ab.get("mult"):
                mult += float(ab["mult"]); applied = True
            ex = ab.get("extra")
            if isinstance(ex, dict) and ex.get("Xmult") and ex.get("type") and hand_contains(hand_name, ex.get("type")):
                mult *= float(ex["Xmult"]); applied = True
            if isinstance(ex, dict) and (ex.get("chips") or n == "Wee Joker") and not ex.get("type") and n in ("Wee Joker", "Castle", "Stone Joker"):
                chips += float(ex.get("chips") or 0); applied = True
                if n == "Wee Joker":
                    chips += float(ex.get("chip_mod") or 8) * sum(1 for c in scoring if _r(c) == "2")  # grows before it fires
            xm0 = float(ab.get("x_mult") or 0) + (0.1 * vamp_n if n == "Vampire" else 0)
            if xm0 > 1:
                mult *= xm0; applied = True
            if not applied and n not in MODELED:
                notes.append(f"{n} not modeled")
        if ed == "polychrome":
            mult *= 1.5
    return int(chips * mult), notes


def _cards_by_idx(d, idxs):
    hand = {c.get("index"): c for c in lst(d.get("hand"))}
    return [hand[i] for i in idxs if i in hand]


def _held(d, idxs):
    return [c for c in lst(d.get("hand")) if c.get("index") not in set(idxs)]


def _repeat_flag(d, hand_name):
    v = (d.get("hand_levels") or {}).get(hand_name) or {}
    ptr = v.get("played_this_round")
    if ptr is None:
        return None
    return int(ptr) > 0


def show_hands(d):
    """List candidate poker hands present in the current hand with indices and level base score."""
    hand = [c for c in lst(d.get("hand")) if c.get("rank") is not None and "Stone" not in _enh(c)]
    stones = [c for c in lst(d.get("hand")) if "Stone" in _enh(c)]
    if stones:
        print(f"Stone cards (no rank/suit, +50 chips when played, ideal fillers): idx {[c.get('index') for c in stones]}")
    hl = d.get("hand_levels") or {}
    by_rank, by_suit = {}, {}
    jn_all = [j.get("name") for j in lst(d.get("jokers"))]
    wilds = [c for c in hand if "Wild" in _enh(c)]
    for c in sorted(hand, key=lambda c: 1 if c.get("debuff") else 0):
        r = RANK.get(str(c.get("rank")), str(c.get("rank")))
        by_rank.setdefault(r, []).append(c)
        k = _suit_key(c, jn_all)
        if k != "WILD":
            by_suit.setdefault(k, []).append(c)
    for k in list(by_suit.keys()):
        by_suit[k] = by_suit[k] + wilds
    fd = [c for c in lst(d.get("hand")) if c.get("rank") is None]
    if fd:
        print(f"Face-down cards (unknown face cards): idx {[c.get('index') for c in fd]}")

    def base(name):
        v = hl.get(name) or {}
        return f"L{v.get('level', 1)} {v.get('chips')}x{v.get('mult')}"

    def idx(cards):
        return " ".join(str(c.get("index")) for c in cards)

    def card_chips(cards):
        return sum(CHIP_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0) for c in cards)

    out = []
    pairs = {r: cs for r, cs in by_rank.items() if len(cs) >= 2}
    for r, cs in sorted(pairs.items(), key=lambda kv: -RANK_VAL.get(kv[0], 0)):
        n = len(cs)
        tag = "FACE " if r in FACES else ""
        if n >= 4:
            out.append(f"FOUR OF A KIND {tag}{r}: idx {idx(cs[:4])} | {base('Four of a Kind')} + {card_chips(cs[:4])} card chips")
        if n >= 3:
            out.append(f"THREE OF A KIND {tag}{r}: idx {idx(cs[:3])} | {base('Three of a Kind')} + {card_chips(cs[:3])} card chips")
        out.append(f"PAIR {tag}{r}: idx {idx(cs[:2])} | {base('Pair')} + {card_chips(cs[:2])} card chips")
    ranks_paired = sorted(pairs.keys(), key=lambda r: -RANK_VAL.get(r, 0))
    for i in range(len(ranks_paired)):
        for j in range(i + 1, len(ranks_paired)):
            a, b = ranks_paired[i], ranks_paired[j]
            cs = pairs[a][:2] + pairs[b][:2]
            tags = ("FACE " if a in FACES else "") + ("FACE " if b in FACES else "")
            out.append(f"TWO PAIR {tags}{a}{b}: idx {idx(cs)} | {base('Two Pair')} + {card_chips(cs)} card chips")
    trips = [r for r, cs in pairs.items() if len(cs) >= 3]
    for t in trips:
        for r in ranks_paired:
            if r != t:
                cs = pairs[t][:3] + pairs[r][:2]
                out.append(f"FULL HOUSE {t}{t}{t}{r}{r}: idx {idx(cs)} | {base('Full House')} + {card_chips(cs)} card chips")
    ff = any(j.get("name") == "Four Fingers" for j in lst(d.get("jokers")))
    run_len = 4 if ff else 5
    for s_, cs in by_suit.items():
        if len(cs) >= run_len:
            svals = {}
            for c in cs:
                v = RANK_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0)
                svals.setdefault(v, c)
                if v == 14:
                    svals.setdefault(1, c)
            for hi in range(14, run_len - 1, -1):
                run = [svals.get(v) for v in range(hi, hi - run_len, -1)]
                if all(run):
                    out.append(f"STRAIGHT FLUSH {s_} {hi}-high: idx {idx(run)} | {base('Straight Flush')} + {card_chips(run)} card chips")
                    break
            best = sorted(cs, key=lambda c: -CHIP_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0))[:5]
            out.append(f"FLUSH {s_}: idx {idx(best)} | {base('Flush')} + {card_chips(best)} card chips")
    vals = {}
    for c in sorted(hand, key=lambda c: 1 if c.get("debuff") else 0):
        v = RANK_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0)
        vals.setdefault(v, c)
        if v == 14:
            vals.setdefault(1, c)
    for L in ([5, 4] if ff else [5]):
        found = False
        for hi in range(14, L - 1, -1):
            run = [vals.get(v) for v in range(hi, hi - L, -1)]
            if all(run):
                out.append(f"STRAIGHT {hi}-high: idx {idx(run)} | {base('Straight')} + {card_chips(run)} card chips")
                found = True
                break
        if found:
            break
    if not out:
        hc = max(hand, key=lambda c: (0 if c.get("debuff") else 1, CHIP_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0)), default=None)
        if hc:
            out.append(f"HIGH CARD {card_str(hc)}: idx {hc.get('index')} | {base('High Card')}")
    print("Candidate hands (est = estimated score with your jokers; 'x3 if repeat' hands show both):")
    b = d.get("blind") or {}
    need = (b.get("chips_needed") or 0) - (b.get("chips_scored") or 0)
    scored = []
    for line in out:
        name_word = line.split(":")[0].split(" ")
        hand_name = {"FOUR": "Four of a Kind", "THREE": "Three of a Kind", "PAIR": "Pair", "TWO": "Two Pair",
                     "FULL": "Full House", "FLUSH": "Flush", "STRAIGHT": "Straight", "HIGH": "High Card"}.get(name_word[0], "High Card")
        if line.startswith("STRAIGHT FLUSH"):
            hand_name = "Straight Flush"
        idxs = [int(x) for x in line.split("idx ")[1].split("|")[0].split()]
        b_ = d.get("blind") or {}
        jn_ = [j.get("name") for j in lst(d.get("jokers"))]
        if len(idxs) < 5 and not (b_.get("boss") and b_.get("name") == "The Tooth") and "Splash" not in jn_:
            stones = [c.get("index") for c in lst(d.get("hand")) if "Stone" in _enh(c) and c.get("index") not in idxs and not c.get("debuff")]
            stones = stones[:5 - len(idxs)]
            if stones and not ("Half Joker" in jn_ and len(idxs) + len(stones) > 3):
                idxs = idxs + stones  # Stone cards always score +50: fold them into the candidate so est and the play line agree
                head_, rest_ = line.split("idx ", 1)
                line = f"{head_}idx {' '.join(map(str, idxs))} |{rest_.split('|', 1)[1]}"
        cards = _cards_by_idx(d, idxs)
        rep = _repeat_flag(d, hand_name)
        psy5 = 5 if (bool((d.get("blind") or {}).get("boss")) and (d.get("blind") or {}).get("name") == "The Psychic") else None
        est, notes = estimate(hand_name, cards, _held(d, idxs), d, repeat=rep, played_n=psy5)  # The Psychic forces 5 cards: Half Joker etc. see the padded play
        extra = ""
        if rep is None and any(j.get("name") == "Card Sharp" for j in lst(d.get("jokers"))):
            est3, _ = estimate(hand_name, cards, _held(d, idxs), d, repeat=True)
            extra = f" (x3 if repeat: {est3})"
        scored.append((est, f"{line} => est {est}{extra}"))
    for est, line in sorted(scored, key=lambda t: -t[0]):
        print("  " + line)
    if need > 0:
        print(f"  need {need} more this blind")
    notes_all = set()
    for line in out:
        pass
    _, nts = estimate("High Card", [], [], d)
    for n in nts:
        notes_all.add(n)
    if notes_all:
        print("  notes: " + "; ".join(sorted(notes_all)))
    singles = [r for r, cs in by_rank.items() if len(cs) == 1 and r in FACES]
    if singles:
        print("  face singles held: " + " ".join(sorted(singles)))


def _candidates(d):
    """Return list of (hand_name, idxs, est) for hands present, using the same enumeration as show_hands."""
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        show_hands(d)
    cands = []
    for line in buf.getvalue().splitlines():
        line = line.strip()
        if "idx " not in line or "=> est" not in line:
            continue
        word = line.split(":")[0].split(" ")[0]
        hand_name = {"FOUR": "Four of a Kind", "THREE": "Three of a Kind", "PAIR": "Pair", "TWO": "Two Pair",
                     "FULL": "Full House", "FLUSH": "Flush", "STRAIGHT": "Straight", "HIGH": "High Card"}.get(word)
        if line.startswith("STRAIGHT FLUSH"):
            hand_name = "Straight Flush"
        if not hand_name:
            continue
        idxs = [int(x) for x in line.split("idx ")[1].split("|")[0].split()]
        est = int(line.split("=> est ")[1].split()[0])
        cands.append((hand_name, idxs, est))
    return cands


TYPE_WORD = {v: k for k, v in HAND_WORDS.items()}


def advise(d):
    if d.get("phase") != "SELECTING_HAND":
        print("advise only works while selecting a hand"); return
    b = d.get("blind") or {}
    need = (b.get("chips_needed") or 0) - (b.get("chips_scored") or 0)
    hands_left = int(d.get("hands_remaining") or 0)
    discards = int(d.get("discards_remaining") or 0)
    hand = lst(d.get("hand"))
    cands = _candidates(d)
    show_hands(d)
    if not cands:
        print("ADVICE: no hand found (all face-down?). Play 4 face-down cards if you have them, else discard non-faces.")
        return
    boss_now = ((d.get("blind") or {}).get("name") or "") if (d.get("blind") or {}).get("boss") else ""
    played_now = [k for k, v in (d.get("hand_levels") or {}).items() if int(v.get("played_this_round") or 0) > 0]
    if boss_now == "The Eye" and played_now:
        unused = [c for c in cands if c[0] not in played_now]
        print(f"The Eye: hand types already used this round ({', '.join(played_now)}) score ZERO and are excluded.")
        if not unused:
            # every candidate type was already played: a repeat scores nothing, so rebuild toward a new type
            all_idx = [c.get("index") for c in hand]
            if discards > 0:
                disc_idx = all_idx[:5]
                print(f"ADVICE: DISCARD -> b disc {' '.join(map(str, disc_idx))}   (The Eye: no unused hand type is available; any play scores 0, so draw for a new type — High Card counts if unused)")
            else:
                print("ADVICE: NO SCORING PLAY: every type you can form was already played this round (0 points under The Eye). Use a held Strength/Death/Justice to change the hand type if you can; otherwise play any cards to end the round.")
            return
        cands = unused
    if boss_now == "The Mouth" and played_now:
        locked = played_now[0]
        matching = [c for c in cands if c[0] == locked]
        print(f"The Mouth: only {locked} may be played this round; other types score NOTHING.")
        if not matching:
            pair_family = {"Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind"}
            keep = []
            if locked in pair_family:
                for c in cands:
                    if c[0] in pair_family:
                        keep = sorted(set(keep) | set(c[1]))
            elif locked == "Flush":
                by_s = {}
                for c in hand:
                    by_s.setdefault(SUIT.get(c.get("suit")), []).append(c.get("index"))
                keep = max(by_s.values(), key=len) if by_s else []
            elif locked == "Straight":
                keep = [c.get("index") for c in sorted(hand, key=lambda c: -RANK_VAL.get(_r(c), 0))[:4]]
            disc_idx = [c.get("index") for c in hand if c.get("index") not in keep][:5]
            if discards > 0 and disc_idx:
                print(f"ADVICE: DISCARD -> b disc {' '.join(map(str, disc_idx))}   (no {locked} available; rebuilding it, keeping {keep})")
            else:
                print(f"ADVICE: NO VALID PLAY: you cannot form {locked} and have no discards. Any other hand scores 0. Play your closest cards to end the round (the blind is likely lost).")
            return
        cands = matching
    if not cands:
        print("ADVICE: no legal scoring hand under this boss; discard toward a new type or play the least bad option manually.")
        return
    best = max(cands, key=lambda t: t[2])
    fds = [c.get("index") for c in hand if c.get("rank") is None]
    boss_name = ((d.get("blind") or {}).get("name") or "") if (d.get("blind") or {}).get("boss") else ""
    if fds and boss_name != "The Mark":
        print(f"Face-down cards {fds} are unknown random cards ({boss_name or 'no boss'}): do not count on them; prefer discarding them and playing visible hands.")
    if len(fds) >= 4 and boss_name == "The Mark":
        fake = [{"rank": "King", "suit": "Spades"}, {"rank": "King", "suit": "Hearts"}]
        est_fd, _n = estimate("Pair", fake, [c for c in hand if c.get("index") not in fds[:4]], d, repeat=_repeat_flag(d, "Pair"))
        print(f"Face-down cards {fds}: any 4 of them always contain a pair (3 same-suit face-downs are K,Q,J). A face pair here would score about {est_fd}.")
        if est_fd >= best[2]:
            print(f"ADVICE: PLAY -> b play {' '.join(map(str, fds[:4]))}   (4 face-down cards: guaranteed at least a pair of faces, est ~{est_fd}; no TYPE given because the exact type is hidden)")
            return
    face_jokers = any(j.get("name") in ("Smiley Face", "Scary Face", "Photograph", "Triboulet", "Sock and Buskin") for j in lst(d.get("jokers")))
    all_idx = [c.get("index") for c in hand]

    jnames_all = [j.get("name") for j in lst(d.get("jokers"))]
    protect_ranks = set()
    if "Shoot the Moon" in jnames_all:
        protect_ranks.add("Q")
    if "Baron" in jnames_all:
        protect_ranks.add("K")
    if "Raised Fist" in jnames_all:
        protect_ranks |= {"2", "3"}

    upcoming_boss = (((d.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}).get("name")
    pillar_ahead = upcoming_boss == "The Pillar" and not (d.get("blind") or {}).get("boss")
    if pillar_ahead:
        print("The Pillar is this ante's boss: every card you play now is debuffed at the boss. Playing WITHOUT fillers and with the fewest cards.")
    if boss_name == "The Serpent":
        print("The Serpent: every play or discard draws exactly 3 cards, so a 4-5 card discard shrinks your hand for the rest of the round. Discard at most 3 cards at a time and play made hands early.")
    if boss_name == "Verdant Leaf" and any(c.get("debuff") for c in hand) and lst(d.get("jokers")):
        weakest_v = min(lst(d.get("jokers")), key=lambda j: classify_joker(j.get("name"), 0, main_hand(d))[1])
        print(f"ADVICE: SELL -> b sell {weakest_v.get('index')}   (Verdant Leaf debuffs every card until you sell ONE joker; {weakest_v.get('name')} is your least valuable. Do not discard before selling.)")
        return
    if boss_name == "The Tooth":
        pillar_ahead = True
        print("The Tooth: you lose $1 per card played. Playing WITHOUT fillers; if a 2-card pair clears the remaining need, play just the pair.")

    def fillers(idxs, hand_name):
        if "Half Joker" in jnames_all and len(idxs) <= 3 and not psychic:
            return []  # Half Joker's +20 mult needs 3 or fewer cards played: fillers would cost more than they draw
        """non-scoring cards safe to add: no rank already in the hand, no face if face jokers, avoid making flush/straight."""
        if pillar_ahead:
            return []
        if "Half Joker" in jnames_all and len(idxs) <= 3:
            return []
        used_ranks = {_r(c) for c in _cards_by_idx(d, idxs)} | protect_ranks
        used_suits = [SUIT.get(c.get("suit")) for c in _cards_by_idx(d, idxs)]
        suit_counts = {}
        for c in hand:
            if c.get("rank") is not None and c.get("index") not in idxs:
                suit_counts[SUIT.get(c.get("suit"))] = suit_counts.get(SUIT.get(c.get("suit")), 0) + 1
        live_suit = {su for su, n in suit_counts.items() if n >= 4}
        out = []
        for c in hand:
            i = c.get("index")
            if i in idxs:
                continue
            if "Stone" in _enh(c):
                out.append((-100, i, None))
                continue
            if c.get("rank") is None:
                continue
            r = _r(c)
            splash = "Splash" in jnames_all
            if r in used_ranks or (face_jokers and r in FACES and not splash) or SUIT.get(c.get("suit")) in live_suit:
                continue
            if hand_name in ("Pair", "Two Pair", "Three of a Kind", "High Card"):
                if splash:
                    # every played card scores: pick the fillers that add the most (faces for face jokers, joker-favoured ranks, high chips)
                    bonus = (60 if (face_jokers and r in FACES) else 0) + (40 if ("Fibonacci" in jnames_all and r in {"A", "2", "3", "5", "8"}) else 0)
                    bonus += (30 if ("Even Steven" in jnames_all and r in {"2", "4", "6", "8", "T"}) else 0) + (30 if ("Odd Todd" in jnames_all and r in {"A", "3", "5", "7", "9"}) else 0)
                    bonus += (40 if ("Scholar" in jnames_all and r == "A") else 0) + (30 if ("Walkie Talkie" in jnames_all and r in {"T", "4"}) else 0)
                    enh_f = _enh(c)
                    bonus += (200 if "Glass" in enh_f else 0) + (40 if enh_f.startswith("Mult") else 0) + (30 if "Bonus" in enh_f else 0) + (25 if "Lucky" in enh_f else 0)
                    out.append((-(CHIP_VAL.get(r, 0) + bonus), i, SUIT.get(c.get("suit"))))
                else:
                    out.append((CHIP_VAL.get(r, 0), i, SUIT.get(c.get("suit"))))
        out.sort()
        chosen = []
        chosen_ranks = set()
        for _, i, su in out:
            if len(idxs) + len(chosen) >= 5:
                break
            r_i = _r(_cards_by_idx(d, [i])[0])
            if r_i in chosen_ranks:
                continue
            suits = used_suits + [x[1] for x in chosen] + [su]
            if suits.count(su) >= 5:
                continue
            chosen.append((i, su)); chosen_ranks.add(r_i)
        return [i for i, _ in chosen]

    psychic = bool((d.get("blind") or {}).get("boss")) and (d.get("blind") or {}).get("name") == "The Psychic"
    if psychic:
        print("The Psychic: every play must be exactly 5 cards. The ADVICE line below includes fillers; if you type `play` yourself, add filler indices to reach 5.")
    if "Burnt Joker" in jnames_all and discards == int(d.get("discards_per_round") or 3):
        print("Burnt Joker: your FIRST discard this round levels up the hand type those cards form -> discard cards that form your main hand type (e.g. two pairs) if you can spare them.")
    if "Splash" in jnames_all:
        print("Splash: every played card scores, so fillers add chips and trigger suit/rank jokers; prefer high-chip fillers of your bonus suits.")
    if best[2] >= need:
        # prefer the cheapest hand that still clears
        ok = [c for c in cands if c[2] >= need]
        mh_now = main_hand(d)
        PAIR_FAMILY = ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind")
        # any of these clears; prefer the hand we are building (main hand, then pair family) so levels and Supernova stay consolidated
        pick = max(ok, key=lambda t: (t[0] == mh_now, t[0] in PAIR_FAMILY, t[2], -len(t[1])))
        why = "" if pick[2] == max(c[2] for c in ok) else f"; a bigger {max(ok, key=lambda t: t[2])[0]} also clears but {pick[0]} is the hand you are leveling"
        fl = fillers(pick[1], pick[0]) if len(pick[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(pick[0], 'HIGH')} {' '.join(map(str, pick[1] + fl))}   (est {pick[2]} >= need {need}{why}" + (f"; fillers {fl} just draw cards)" if fl else ")"))
        return
    has_sharp = any(j.get("name") == "Card Sharp" for j in lst(d.get("jokers")))
    played_types = [k for k, v in (d.get("hand_levels") or {}).items() if int(v.get("played_this_round") or 0) > 0]
    if has_sharp and not played_types and best[2] < need and hands_left >= 2:
        # register the type whose x3 version is strongest, using its cheapest instance
        by_type = {}
        for hn, idxs, est in cands:
            e3, _ = estimate(hn, _cards_by_idx(d, idxs), _held(d, idxs), d, repeat=True)
            by_type.setdefault(hn, []).append((e3, est, idxs))
        REBUILDABLE = {"Pair", "Two Pair", "Three of a Kind", "Full House", "High Card", main_hand(d)}
        rebuild = {k: v for k, v in by_type.items() if k in REBUILDABLE}
        if rebuild:
            by_type = rebuild  # a Flush/Straight rarely comes twice in one round; register a type the deck keeps dealing
        if by_type:
            tname, lst_ = max(by_type.items(), key=lambda kv: max(x[0] for x in kv[1]))
            e3, est1, idxs1 = min(lst_, key=lambda x: (len(x[2]), -x[1]))
            if e3 * (hands_left - 1) + est1 >= need and est1 < need:
                fl = fillers(idxs1, tname) if len(idxs1) < 5 else []
                print(f"ADVICE: PLAY (register for Card Sharp) -> b play {TYPE_WORD.get(tname, 'HIGH')} {' '.join(map(str, idxs1 + fl))}   (est {est1} now; later {tname} hands score x3 ~ {e3} each)")
                return
    if boss_now == "The Eye" and discards > 0 and discards < hands_left and best[2] > 0:
        fl = fillers(best[1], best[0]) if len(best[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(best[0], 'HIGH')} {' '.join(map(str, best[1] + fl))}   (The Eye: {hands_left} distinct hand types still needed, only {discards} discard(s) left; ration one discard per hand)")
        return
    feasible_after = hands_left < 2 or (need - best[2]) / max(1, hands_left - 1) <= 1.6 * best[2]  # the later hands must be reachable too
    if 0 < discards < hands_left and hands_left >= 2 and best[2] >= 0.6 * need / hands_left and feasible_after:
        fl = fillers(best[1], best[0]) if len(best[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(best[0], 'HIGH')} {' '.join(map(str, best[1] + fl))}   (est {best[2]}; {discards} discard(s) for {hands_left} hands: pacing, keep discards for later hands)")
        return
    if discards == 1 and hands_left >= 2 and best[2] >= 0.8 * need / hands_left and feasible_after:
        fl = fillers(best[1], best[0]) if len(best[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(best[0], 'HIGH')} {' '.join(map(str, best[1] + fl))}   (est {best[2]}; keeping the last discard for the final hand)")
        return
    if discards > 0:
        # choose a keep set by expected value
        by_suit = {}
        for c in hand:
            if c.get("rank") is not None:
                by_suit.setdefault(SUIT.get(c.get("suit")), []).append(c.get("index"))
        flush_draw = max(by_suit.items(), key=lambda kv: len(kv[1])) if by_suit else (None, [])
        made = [c for c in cands if c[0] in ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind", "Straight", "Flush", "Straight Flush")]
        keep = []
        why = ""
        flush_ev = 0
        if len(flush_draw[1]) == 4:
            fcards = _cards_by_idx(d, flush_draw[1])
            flush_est, _n = estimate("Flush", fcards + [fcards[0]], _held(d, flush_draw[1]), d)
            deck_n = int(((d.get("deck") or {}).get("draw_pile")) or 40)
            draws = min(5, len(hand) - 4)
            remaining_suit = max(0, 13 - len(flush_draw[1]) - 1)
            p_miss = 1.0
            for k in range(draws):
                p_miss *= max(0.0, (deck_n - remaining_suit - k) / max(1, deck_n - k))
            flush_ev = flush_est * (1 - p_miss)
        # straight draw: 4 distinct ranks inside a 5-card window
        straight_ev, straight_keep = 0, []
        vals = {}
        for c in hand:
            if c.get("rank") is None:
                continue
            v = RANK_VAL.get(_r(c), 0)
            vals.setdefault(v, c.get("index"))
            if v == 14:
                vals.setdefault(1, c.get("index"))
        for hi in range(14, 4, -1):
            window = [vals.get(v) for v in range(hi, hi - 5, -1)]
            have = [i for i in window if i is not None]
            if len(have) == 4:
                scards = _cards_by_idx(d, have)
                st_est, _n = estimate("Straight", scards + [scards[0]], _held(d, have), d)
                deck_n = int(((d.get("deck") or {}).get("draw_pile")) or 40)
                draws = min(5, len(hand) - 4)
                outs = 4 if (window[0] is None or window[-1] is None) and not (hi == 14 or hi - 4 == 1) else 4
                outs = 8 if (window[0] is not None and window[-1] is not None) is False and hi not in (14, 5) else outs
                p_miss = 1.0
                for k in range(draws):
                    p_miss *= max(0.0, (deck_n - outs - k) / max(1, deck_n - k))
                if st_est * (1 - p_miss) > straight_ev:
                    straight_ev, straight_keep = st_est * (1 - p_miss), have
                break
        if has_sharp and played_types:
            reg = [m for m in made if m[0] in played_types]
            pair_types = {"Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind"}
            if reg:
                made = reg
                print(f"Card Sharp: steering toward registered type(s) {', '.join(played_types)} (x3).")
            elif pair_types & set(played_types):
                made = [m for m in made if m[0] in pair_types] or made
                print(f"Card Sharp: keeping pairs to rebuild {', '.join(t for t in played_types if t in pair_types)} (x3).")
        best_made = max([m[2] for m in made], default=0)
        proj = best_made * hands_left
        made_ev = best_made * (1.3 if proj >= 0.85 * need else 0.8)
        chase = max([(flush_ev, "flush", list(flush_draw[1]) if len(flush_draw[1]) == 4 else []), (straight_ev, "straight", straight_keep)], key=lambda t: t[0])
        floor_needed = made and (discards == 1 or hands_left == 1)  # last discard, or the final hand: never throw away the made floor
        jokerless_ok = not jnames_all and proj >= 0.9 * need  # no joker: a missed chase strips the pair ranks that clear this blind
        if jokerless_ok and chase[2] and chase[0] > 1.25 * made_ev:
            print(f"No jokers: made pair-family hands project to {int(proj)} vs need {need}; sequencing them beats a {chase[1]} chase (EV {int(chase[0])}) that leaves nothing when it misses.")
        if chase[0] > 1.25 * made_ev and chase[0] > 0.3 * need and chase[2] and not floor_needed and not jokerless_ok:
            keep = chase[2]; why = f"drawing to a {chase[1]} (EV {int(chase[0])}) because made hands (best {best_made}) project to {int(proj)} {'<' if proj < need else '>='} need {need}"
        elif floor_needed and chase[2]:
            top = max(made, key=lambda t: t[2])
            keep = sorted(set(top[1]) | set(chase[2])); why = f"{'final hand' if hands_left == 1 else 'last discard'}: keeping the made {top[0]} as a floor while still drawing to the {chase[1]}"
        elif made:
            top = max(made, key=lambda t: t[2])
            keep = list(top[1]); why = f"keep {top[0]} (est {top[2]}) and draw around it"
            if top[0] in ("Straight", "Flush", "Straight Flush") and len(keep) == 5:
                # a made 5-card hand that is still short: keep it and discard the rest hoping to improve later hands
                pass
            if face_jokers:
                for c in hand:
                    if _is_face(c) and c.get("index") not in keep and len(keep) < len(hand) - 1:
                        keep.append(c.get("index")); why += ", keep face singles"
        else:
            # keep high cards / faces
            hi = sorted(hand, key=lambda c: -CHIP_VAL.get(_r(c), 0))[:3]
            keep = [c.get("index") for c in hi]; why = "no made hand: keep the 3 highest cards"
        debuffed_idx = [c.get("index") for c in hand if c.get("debuff")]
        if debuffed_idx:
            keep = [i for i in keep if i not in debuffed_idx]
            why += f"; debuffed cards {debuffed_idx} score nothing, discard them first"
        disc = (debuffed_idx + [i for i in all_idx if i not in keep and i not in debuffed_idx])[:5]
        if disc:
            print(f"ADVICE: DISCARD -> b disc {' '.join(map(str, disc))}   ({why}; best now {best[0]} est {best[2]} < need {need})")
            return
    # no discards: play the best, with fillers
    fl = fillers(best[1], best[0]) if len(best[1]) < 5 else []
    short = need - best[2]
    print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(best[0], 'HIGH')} {' '.join(map(str, best[1] + fl))}   (est {best[2]}, still {short} short; {hands_left - 1} hands left after this)")


PLANET_FOR = {"Pair": "Mercury", "Two Pair": "Uranus", "Three of a Kind": "Venus", "Straight": "Saturn", "Flush": "Jupiter",
              "Full House": "Earth", "Four of a Kind": "Mars", "Straight Flush": "Neptune", "High Card": "Pluto"}
ECON_WORDS = ("$", "interest")


def second_hand(d):
    hl = d.get("hand_levels") or {}
    ranked = sorted(hl.items(), key=lambda kv: -int(kv[1].get("played") or 0))
    return ranked[1][0] if len(ranked) > 1 and int(ranked[1][1].get("played") or 0) >= 3 else None


def main_hand(d):
    hl = d.get("hand_levels") or {}
    best = None
    total = 0
    for name, v in hl.items():
        total += int(v.get("played") or 0)
        key = (int(v.get("played") or 0), int(v.get("level") or 1))
        if best is None or key > best[0]:
            best = (key, name)
    if not best or total < 3 or best[0][0] < 2:
        return "undecided"
    if int(d.get("ante") or 1) <= 2 and best[1] not in ("Pair", "Two Pair", "Three of a Kind", "Full House"):
        return "undecided"  # an early Straight/Flush streak is dealt luck, not a plan
    # re-anchor: a pair-family hand played at least 30% as often as the leader but worth much more per play
    # (higher level x base) is the hand to level, e.g. Full House L3 over Two Pair L2 (playbook 7a "re-anchor")
    def worth(name):
        v = hl.get(name) or {}
        return int(v.get("played") or 0) * float(v.get("chips") or 1) * float(v.get("mult") or 1)
    lead = best[1]
    cands = [n for n in ("Pair", "Two Pair", "Three of a Kind", "Full House") if n != lead and n in hl
             and int(hl[n].get("played") or 0) >= max(2, 0.3 * int(hl[lead].get("played") or 0))]
    alt = max(cands, key=worth, default=None)
    if alt and lead in ("Pair", "Two Pair", "Three of a Kind", "Full House") and worth(alt) > 1.5 * worth(lead):
        return alt
    return lead


AVOID_JOKERS = {"Madness": "destroys one of your jokers every blind", "Ceremonial Dagger": "destroys the joker to its right",
                "Ramen": "decays with discards", "Ice Cream": "decays each hand", "Popcorn": "decays each round", "Turtle Bean": "decays",
                "Gros Michel": "1/6 to self-destruct", "Swashbuckler": "useless as the only joker", "Joker Stencil": "x1 with full slots",
                "Obelisk": "penalizes playing your main hand", "Troubadour": "-1 hand per round: Black Deck has only 3",
                "Merry Andy": "-1 hand size", "Mr. Bones": "saves a lost blind once but is destroyed: not scaling"}


def classify_joker(name, cost, mh):
    desc = JOKER_DESC.get(name, "")
    dl = desc.lower()
    if name in AVOID_JOKERS:
        return "AVOID(" + AVOID_JOKERS[name] + ")", 5
    if name == "Burnt Joker":
        return "LEVELS(first discarded hand type levels up every round: discard your main hand type first)", 95
    if name == "Astronomer":
        return "LEVELS(planets and Celestial packs free)", 85
    if name == "Space Joker":
        return "LEVELS(1/4 chance to level the played hand)", 65
    if name in ("Hiker", "Wee Joker", "Castle"):
        return "PLUS(permanent growth)", 60
    if name in ("Walkie Talkie", "Square Joker", "Scary Face", "Smiley Face"):
        # rank/face-gated: fire only when specific ranks score; decent second joker, not a floor
        return ("PLUS(common condition)", 55) if name in ("Scary Face", "Smiley Face") else ("PLUS(rare condition)", 35)
    if name == "Ride the Bus":
        return "PLUS(growth: +1 mult per faceless hand, resets on a face)", 50
    if name == "Throwback":
        return "PLUS(x0.25 per skipped blind: useless, we never skip)", 15
    if name == "Hit the Road":
        return "PLUS(x0.5 per Jack discarded this round: rarely fires)", 30
    if name in ("Blackboard", "Flower Pot", "Seeing Double", "Driver's License", "Joker Stencil", "Acrobat", "Loyalty Card", "Bloodstone", "Ancient Joker", "Obelisk", "Baseball Card", "The Idol"):
        return "XMULT(conditional, unreliable)", (40 if name in ("Blackboard", "Flower Pot", "Seeing Double", "Driver's License", "Joker Stencil") else 55)  # the first group almost never fires on a pair-family build
    if name in ("Red Card", "Fortune Teller", "Green Joker", "Ice Cream", "Popcorn", "Square Joker", "Runner"):
        return "PLUS(weak/conditional)", 25
    if name in SUIT_JOKERS:
        return "PLUS(one suit)", 18  # ~1 matching card per pair-family hand: +3 mult on average, not worth a slot
    if name in ("Hologram", "Vampire", "Constellation", "Campfire", "Madness", "Lucky Cat", "Glass Joker", "Steel Joker", "Canio", "Yorick"):
        return "XMULT(growth: must be fed)", 80
    if dl.startswith("x") or " x" in dl or "xmult" in dl:
        return "XMULT", 100
    if "+$" in desc or "interest" in dl or "per round" in dl and "$" in desc:
        return "ECON", 60
    if "+" in dl and ("mult" in dl or "chips" in dl):
        cond = None
        if " if " in dl:
            cond = dl.split(" if ")[1]
        COND_TYPE = {"pair": "Pair", "two": "Two Pair", "three": "Three of a Kind", "straight": "Straight", "flush": "Flush", "four": "Four of a Kind"}
        ctype = None
        if cond:
            if "two pair" in cond:
                ctype = "Two Pair"
            elif "pair" in cond:
                ctype = "Pair"
            else:
                ctype = COND_TYPE.get(cond.split()[0])
        if ctype and mh != "undecided" and hand_contains(mh, ctype):
            return "PLUS(main hand)", 70  # fires on every play of the main hand (a Trips joker fires on Full House, a Pair joker on Two Pair/Trips)
        if ctype == "Pair":
            return "PLUS(fires on any pair-family hand)", 64  # Jolly/Sly: every Pair, Two Pair, Trips, Full House and Quads
        if ctype and mh != "undecided":
            return "PLUS(other hand)", 30
        if cond and ("three" in cond or cond.split()[0] in ("straight", "flush", "four")):
            return "PLUS(rare condition)", 40
        if cond and cond.split()[0] in ("pair", "two"):
            return "PLUS(common condition)", 58
        return "PLUS", 50
    if desc == "":
        return "UNKNOWN", 25
    return "UTIL", 20


def shop_advise(d):
    if d.get("phase") != "SHOP":
        print("shopadvise only works in the shop"); return
    money = int(d.get("money") or 0); ante = int(d.get("ante") or 1)
    jokers = lst(d.get("jokers")); slots = int(d.get("joker_slots") or 5)
    free = slots - len(jokers)
    mh = main_hand(d)
    sh = d.get("shop") or {}
    floor = 0 if ante <= 2 else (10 if ante <= 4 else 15)
    if ante >= 6:
        floor = 0  # two antes left at most: interest cannot pay back, every dollar goes into scaling
    n_x_now = sum(1 for j in jokers if (classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") or _joker_edition(j) == "polychrome"))
    main_lvl = int(((d.get("hand_levels") or {}).get(mh) or {}).get("level") or 1) if mh != "undecided" else 1
    if ante >= 3 and (n_x_now == 0 or main_lvl < ante):
        floor = 0
        print(f"  (under-scaled for ante {ante}: {n_x_now} xMult, main hand L{main_lvl}; interest floor suspended, buy scaling)")
    print(f"Shop advisor: ante {ante}, ${money}, jokers {len(jokers)}/{slots}, main hand {mh}, interest floor ${floor} (spend below it only for XMULT or your main-hand planet)")
    # keep xMult jokers rightmost
    kinds = [classify_joker(j.get("name"), 0, mh)[0] for j in jokers]
    desired = [i + 1 for i, k in enumerate(kinds) if k != "XMULT"] + [i + 1 for i, k in enumerate(kinds) if k == "XMULT"]
    if desired != list(range(1, len(jokers) + 1)):
        print(f"ADVICE: ORDER -> b order {' '.join(map(str, desired))}   (put xMult jokers rightmost so they multiply everything)")
        return
    def _is_scoring(cls):
        # jokers that reliably add to ordinary hands; suit-, growth- and rare-condition jokers do not count
        return cls in ("PLUS", "PLUS(main hand)", "PLUS(common condition)", "PLUS(fires on any pair-family hand)", "PLUS(permanent growth)") or (cls.startswith("XMULT") and "conditional" not in cls)
    scoring_now = sum(1 for j in jokers if _is_scoring(classify_joker(j.get("name"), 0, mh)[0]))
    ENGINE_KEEP = {"Splash", "Four Fingers", "Shortcut", "Smeared Joker", "Pareidolia", "Blueprint", "Brainstorm", "Sock and Buskin", "Hack", "Dusk", "Mime", "Seltzer", "Hanging Chad"}
    def keep_value(j):
        """how much selling this joker would hurt: class score, economy jokers cheap from ante 4, editions add value"""
        cls_k, sc_k = classify_joker(j.get("name"), 0, mh)
        if cls_k == "ECON" and ante >= 4:
            sc_k = 20
        ed_k = _joker_edition(j)
        sc_k += 40 if ed_k == "polychrome" else (15 if ed_k in ("holo", "foil") else 0)
        return sc_k
    if ante >= 4 and free == 0 and n_x_now < 2 and jokers:
        ranked = sorted([j for j in jokers if j.get("name") not in ENGINE_KEEP], key=keep_value) or list(jokers)
        w = ranked[0]; wcls, wsc = classify_joker(w.get("name"), 0, mh); wsc = keep_value(w)
        if wsc <= 45 and not wcls.startswith("XMULT") and w.get("name") not in ENGINE_KEEP:
            print(f"ADVICE: SELL -> b sell {w.get('index')}   ({w.get('name')} [{wcls}] is dead weight; with {n_x_now} xMult at ante {ante} an open slot lets you take the next xMult on sight. Re-run shopadvise after selling.)")
            return
    options = []
    boss_c = ((d.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}
    boss_ahead = boss_c.get("name") if boss_c.get("state") != "Defeated" else None
    BOSS_KILLS = {"The Plant": {"Smiley Face", "Scary Face", "Photograph", "Sock and Buskin", "Business Card", "Midas Touch", "Reserved Parking", "Triboulet"},
                  "The Head": {"Lusty Joker", "Bloodstone"}, "The Goad": {"Wrathful Joker", "Arrowhead"},
                  "The Club": {"Gluttonous Joker", "Onyx Agate"}, "The Window": {"Greedy Joker", "Rough Gem"},
                  "The Needle": {"Card Sharp"}, "The Water": {"Banner", "Mystic Summit"}}
    crippled = [j.get("name") for j in jokers if j.get("name") in BOSS_KILLS.get(boss_ahead or "", set())]
    FLOOR_CLS = ("PLUS", "PLUS(fires on any pair-family hand)", "PLUS(permanent growth)")
    has_floor = any(classify_joker(j.get("name"), 0, mh)[0] in FLOOR_CLS for j in jokers)
    if jokers and not has_floor:
        print("  WARNING: none of your jokers scores on a plain Pair (all are Trips/Two Pair/type-gated or utility). Buy one unconditional or Pair-triggered joker (Joker, Jolly, Sly, Scholar, Fibonacci, Even/Odd, Smiley) as the floor when one is offered; if this shop only has Two Pair/Trips-gated ones, buying one of those still beats leaving with nothing (the ADVICE line below already accounts for this).")
    if ante >= 3 and not any(k.get("name") in ("Death", "Strength", "Justice") for k in lst(d.get("consumables"))):
        print("  (no rescue tarot held: a shop-bought Death/Strength/Justice saves a forced final hand; buy one when $3 is spare)")
    if crippled:
        print(f"  WARNING: upcoming boss {boss_ahead} disables {', '.join(crippled)}. Plan the boss without them (levels, other ranks) or buy a counter (Luchador: sell it during the boss).")
    for c in lst(sh.get("jokers")):
        name, cost, typ = c.get("name"), int(c.get("cost") or 0), c.get("set")
        if typ == "Joker":
            cls, score = classify_joker(name, cost, mh)
            if name == "Bull" and money - cost < 10:
                cls, score = "PLUS(weak/conditional)", 25  # +2 chips per $: worthless for a wallet that is about to be empty
            if name == "Burnt Joker" and ante <= 2 and scoring_now < 2:
                score = 40  # levels come second: with fewer than two scorers the $8 is the next floor joker
            if name in ("Blueprint", "Brainstorm"):
                cls, score = "COPY(copies the joker to its right / your leftmost joker: `order` it beside your best xMult or flat joker)", (80 if n_x_now >= 1 or scoring_now >= 2 else 30)
            if ante >= 3 and n_x_now == 0 and scoring_now >= 2 and cls.startswith("PLUS") and cls != "PLUS(permanent growth)" and money - cost - int(sh.get("reroll_cost") or 5) < 6:
                score = min(score, 28)  # two scorers and no multiplier: a third flat joker that also kills the reroll budget is how flat builds die at ante 4-5
            if ante <= 2 and scoring_now < 2 and _is_scoring(cls):
                score = max(score, 90)  # ante 1-2: the first two scoring jokers beat any pack; after that the main-hand planet (88) comes before a third flat joker
            if not has_floor and cls in FLOOR_CLS:
                score = max(score, 92)  # the build has no joker that fires on a plain Pair: this one is the floor
            if cls == "ECON" and (scoring_now < 2 or (ante <= 3 and money - cost < 8) or (ante >= 4 and free <= 1 and n_x_now < 2)):
                score = 20  # below the buy threshold: money jokers do not clear blinds; two scoring jokers come first, and the last slot is for an xMult
            if cls.startswith("XMULT(growth") and ante <= 2 and scoring_now < 2:
                score = 50  # a growth xMult starts at x1 and needs feeding; ante 1-2 blinds are cleared by flat jokers and levels
            if cls.startswith("XMULT(conditional") and n_x_now < 2 and ante >= 4:
                score = 85 if n_x_now == 0 else 78
            if cls.startswith("XMULT(conditional") and ante <= 2 and scoring_now < 2:
                score = 25  # Loyalty Card/Acrobat/Flower Pot-style conditionals do not clear ante 1-2 blinds; a floor joker does
                print(f"  {name}: a conditional xMult beats none at ante {ante}; runs that reroll for a clean xMult usually never see one (1 in ~45 shops).")
            if name == "Luchador" and (crippled or boss_ahead in ("The Wall", "The Needle", "The Flint", "The Arm", "The Eye", "The Mouth", "The Psychic")):
                cls, score = "COUNTER", 92
                print(f"  Luchador in shop: buy and SELL it while the boss {boss_ahead} is active to disable the boss (`sell N` during the blind).")
            ed = c.get("edition")
            if ed in ("holo", "polychrome"):
                score += 30
            elif ed:
                score += 10
            options.append((score, cls, f"buy {c['index']}", f"{name} ${cost} [{cls}]{' ' + ed if ed else ''}: {JOKER_DESC.get(name, 'unknown effect')}", cost, (cls.startswith("XMULT") and not cls.startswith("XMULT(conditional")) or (cls.startswith("XMULT(conditional") and n_x_now < 2 and ante >= 4) or (name in ("Blueprint", "Brainstorm") and n_x_now >= 1), True))
        elif typ == "Planet":
            good = name == PLANET_FOR.get(mh)
            sh2 = second_hand(d)
            if not good and sh2 and name == PLANET_FOR.get(sh2):
                options.append((66, "PLANET", f"buy {c['index']}", f"{name} ${cost} [planet for your second-most-played hand {sh2}: boss insurance]", cost, True, False))
                continue
            feeds = any(j.get("name") in ("Constellation", "Satellite", "Astronomer") for j in jokers)
            psc = 88 if good else 15
            if good and main_lvl >= 6 and n_x_now < 2:
                psc = 52  # diminishing: L6+ adds ~12% per level while an xMult or Glass card adds 50-100%
            options.append((psc + (25 if feeds else 0), "PLANET", f"buy {c['index']}", f"{name} ${cost} [{'MAIN SCALING: main-hand planet' if good else 'planet for other hand'}{' (already L' + str(main_lvl) + ': multiplication now beats another level)' if good and main_lvl >= 6 else ''}{'; feeds Constellation' if feeds else ''}]", cost, good or feeds, False))
        elif name == "The Hermit":
            options.append((45 if money - cost >= 10 else 5, "TAROT", f"buy {c['index']}", f"{name} ${cost} [doubles money up to +$20: only worth it with $10+ left after buying]", cost, False, False))
        elif name in ("Death", "Strength", "Justice") and ante >= 3:
            held_rescue = any(k.get("name") in ("Death", "Strength", "Justice") for k in lst(d.get("consumables")))
            options.append((30 if held_rescue else 86, "TAROT", f"buy {c['index']}", f"{name} ${cost} [RESCUE tarot: hold it for a forced final hand; pack tarots must be used on the spot, only shop-bought ones can be banked]", cost, not held_rescue, False))
        else:
            options.append((30 if ante >= 3 else 12, "TAROT", f"buy {c['index']}", f"{name} ${cost} [{typ}{'; not before your main hand is leveled' if ante < 3 else ''}]", cost, False, False))
    for c in lst(sh.get("boosters")):
        name, cost = c.get("name") or "", int(c.get("cost") or 0)
        if "Celestial" in name:
            feeds = any(j.get("name") == "Constellation" for j in jokers)
            big = 5 if ("Jumbo" in name or "Mega" in name) else 0
            telescope = "v_telescope" in lst(d.get("used_vouchers"))
            if ante < 2:
                csc = 30
            elif telescope or mh == "undecided":
                csc = 90 if telescope else 82
            elif main_lvl >= 6 and n_x_now < 2:
                csc = 40  # main hand already high; multiplication now beats another level
            elif main_lvl < min(ante, 5):
                csc = 76  # main hand behind the ante curve: a level compounds on every future hand, an enhancement only on one card
            else:
                csc = 58  # ~1 in 3 packs shows your planet; a fallback planet is a wasted level
            note = "Telescope: your main planet is guaranteed" if telescope else f"take {PLANET_FOR.get(mh)}; if it is not offered, a fallback planet is worth little (skip the pack if you can buy your planet directly next shop)"
            options.append((csc + big + (15 if feeds else 0), "PACK", f"pack {c['index']}", f"{name} ${cost} [hand level gamble: {note}{'; feeds Constellation' if feeds else ''}]", cost, ante >= 2 and (telescope or mh == "undecided"), False))
        elif "Buffoon" in name:
            n_x = sum(1 for j in jokers if (classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") or _joker_edition(j) == "polychrome"))
            bscore = 55 if free > 0 else 0
            if free > 0 and ante >= 3 and n_x == 0:
                bscore = 72
            if free > 0 and scoring_now == 0:
                bscore = 88  # no scorer at all: a joker choice beats every pack and beats leaving with cash
            options.append((bscore, "PACK", f"pack {c['index']}", f"{name} ${cost} [joker choice; prefer xMult, then +mult for {mh}]", cost, ante >= 3 and n_x == 0, True))
        elif "Arcana" in name:
            feeds = any(j.get("name") == "Vampire" for j in jokers)
            arc = 70 if ante >= 3 else 15
            if ante >= 3 and mh != "undecided" and main_lvl < min(ante, 5):
                arc = 62  # level the main hand first
            options.append((arc + (25 if feeds else 0) + (8 if (ante >= 4 and n_x_now == 0) else 0), "PACK", f"pack {c['index']}", f"{name} ${cost} [tarots: Justice=Glass x2 / Chariot=Steel x1.5 on your main-hand ranks (`pick N i` with the target card), Empress=+4 mult cards, Hermit=$; {'; enhancement tarots feed Vampire' if feeds else ''}]", cost, ante >= 3, False))
        elif "Standard" in name:
            feeds = any(j.get("name") == "Hologram" for j in jokers)
            options.append((60 if feeds else 10, "PACK", f"pack {c['index']}", f"{name} ${cost} [playing cards{'; each card added feeds Hologram +0.25' if feeds else ''}]", cost, feeds, False))
        elif "Spectral" in name:
            options.append((68 if ante >= 3 else 20, "PACK", f"pack {c['index']}", f"{name} ${cost} [spectral: Aura = Foil/Holo/Polychrome on a target card (`pick N i` with a main-rank card), Cryptid = 2 copies of a target card (copy a Glass/Steel one), Talisman = Gold seal, Ectoplasm = Negative joker, Wraith = a random RARE joker (rares are often xMult; it sets money to $0 so take it when poor and a slot is free), Immolate = destroy 5 random hand cards for $20 (fine when broke); skip Ouija/Sigil/Ankh/Hex unless you understand them]", cost, ante >= 3, False))
        else:
            options.append((10, "PACK", f"pack {c['index']}", f"{name} ${cost}", cost, False, False))
    for c in lst(sh.get("vouchers")):
        name, cost = c.get("name") or "", int(c.get("cost") or 0)
        sc = 45 if name in ("Overstock", "Clearance Sale", "Hone", "Telescope", "Grabber", "Wasteful", "Seed Money", "Money Tree") else 20
        if (ante >= 5 and money - cost < 15) or (ante >= 3 and money - cost < 8):
            sc = 15  # a voucher that empties the wallet costs the next joker/planet; late ones cannot pay back before the run ends
        options.append((sc, "VOUCHER", f"vouch {c['index']}", f"{name} ${cost} [voucher]", cost, False, False))
    options = [((max(o[0], 89) if o[4] == 0 and not o[1].startswith("AVOID") else o[0]),) + tuple(o[1:]) for o in options]  # Coupon Tag / free items: a $0 pack or joker is never worse than leaving
    options.sort(key=lambda t: -t[0])
    for o in options:
        print(f"  {o[0]:>3} {o[2]:<9} {o[3]}")
    try:
        with open(os.path.join(RUNS_DIR, "shop_log.tsv"), "a", encoding="utf-8") as f:
            f.write(f"{os.environ.get('BALATRO_RL_PORT', '7777')}\ta{ante}\t${money}\tjokers={len(jokers)}/{slots}\txmult_owned={sum(1 for j in jokers if classify_joker(j.get('name'), 0, mh)[0] == 'XMULT')}\t" + " | ".join(f"{o[1]}:{o[3].split(' [')[0]}" for o in options) + "\n")
    except Exception:
        pass
    need_joker = len(jokers) < 2 and ante <= 3
    if need_joker:
        options = [(sc + (30 if cls.startswith("PLUS") or cls == "XMULT" else 0), cls, cmd, label, cost, strong, ns)
                   for sc, cls, cmd, label, cost, strong, ns in options]
        options.sort(key=lambda t: -t[0])
        print("  (fewer than 2 jokers: scoring jokers weighted up)")
    if ante >= 6 and money >= 40:
        options = [(sc + (25 if cls.startswith("PLUS") else 0), cls, cmd, label, cost, True if cls.startswith("PLUS") else strong, ns)
                   for sc, cls, cmd, label, cost, strong, ns in options]
        options.sort(key=lambda t: -t[0])
        print("  (ante 6+ with $40+: money is worth nothing unspent; flat +chips/+mult jokers weighted up, sell utility jokers to fit them)")
    cons = lst(d.get("consumables"))
    cons_full = len(cons) >= int(d.get("consumable_slots") or 2)
    save_for_joker = ante <= 2 and scoring_now < 2 and free > 0
    if save_for_joker:
        print(f"  (ante {ante} with {scoring_now} scoring joker(s): keep at least $4 after any pack/planet/voucher so the next shop's $4-5 joker is affordable; a hand with no joker support cannot clear ante 2)")
    joker_offers = [o for o in options if (_is_scoring(o[1]) or (o[1].startswith("LEVELS") and scoring_now >= 1)) and o[4] <= money]
    reroll0 = int(sh.get("reroll_cost") or 5)
    cannot_reroll = money - reroll0 < 4
    if save_for_joker:
        if not joker_offers and not any("Buffoon" in o[3] and o[4] <= money for o in options):
            if money - reroll0 >= 4:
                print(f"ADVICE: REROLL -> b reroll   (no scoring joker in this shop and you own {scoring_now}: at ante {ante} a joker matters more than any pack; ${money - reroll0} left after)")
                return
            if scoring_now == 0 and money - reroll0 >= 3:
                print(f"ADVICE: REROLL -> b reroll   (you own NO scoring joker and none is offered: a jokerless deck does not clear the next blind at this stake; ${money - reroll0} stays for a $3 Sly/Jolly if the reroll shows one)")
                return
            if scoring_now == 0 and money >= reroll0:
                print(f"  (no scorer offered and a reroll would leave under $3: rerolling to $0 has revealed $3 jokers it could no longer buy - keep the ${money} for the next shop)")
    for score, cls, cmd, label, cost, strong, needs_slot in options:
        if cost > money and cmd.startswith("buy") and ((cls.startswith("XMULT") and ante >= 3) or (_is_scoring(cls) and scoring_now == 0 and jokers)):
            # an xMult (or, with no scorer at all, the first scoring joker) we cannot afford: sell the weakest non-xMult joker if that pays for it, otherwise keep the money
            sellable = [(int(j.get("sell_cost") or 0), j) for j in jokers if not classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") and not _is_scoring(classify_joker(j.get("name"), 0, mh)[0]) and j.get("name") not in ENGINE_KEEP]
            sellable.sort(key=lambda t: (classify_joker(t[1].get("name"), 0, mh)[1], -t[0]))
            if sellable and money + sellable[0][0] >= cost:
                print(f"ADVICE: SELL then BUY -> b sell {sellable[0][1].get('index')}  then  b {cmd}   ({label}; selling {sellable[0][1].get('name')} for ${sellable[0][0]} makes it affordable)")
                return
            print(f"  {label.split(' [')[0]} is an xMult you cannot afford (${money}): do not spend on packs this shop unless they clear the next blind; it is gone next shop, so only hold cash if a reroll/next shop is likely to show another")
        if cost > money or cls.startswith("AVOID"):
            continue
        if mh != "undecided" and main_lvl < min(ante, 5) and cls in ("PACK", "VOUCHER", "TAROT") and "Celestial" not in label and not strong and money - cost < 4:
            continue  # main hand behind the level curve: keep $4 so the next shop's planet is affordable instead of a setup pack
        if boss_ahead == "The Tooth" and not strong and money - cost < 6:
            print(f"  (The Tooth is this ante's boss: -$1 per card played; keeping $6 instead of buying {label.split(' [')[0]})")
            continue
        if save_for_joker and cls in ("PACK", "PLANET", "TAROT", "VOUCHER") and "Buffoon" not in label and money - cost < 4:
            if cls == "PLANET" and not joker_offers and cannot_reroll and strong:
                pass  # no joker to save for and no reroll possible: a cheap level for the main hand beats idle cash
            else:
                continue
        min_left = 0 if (strong or need_joker or ante <= 2) else floor
        if ante >= 3 and n_x_now == 0 and score < 80 and not strong:
            min_left = max(min_left, 5)  # no multiplier yet: keep $5 so a surprise xMult, rescue tarot or reroll stays affordable
        if money - cost < min_left:
            continue
        if cls in ("PLANET", "TAROT") and cons_full:
            usable = [c for c in cons if c.get("index") in usable_cons()]
            if usable:
                print(f"ADVICE: USE first -> b use {usable[0].get('index')}   (consumable slots full; use {usable[0].get('name')} then re-run shopadvise to buy {label.split(' [')[0]})")
            else:
                RESCUE = {"Justice", "The Chariot", "The Empress", "The Hierophant", "The Magician", "The Devil", "The Tower", "The Lovers", "Strength", "Death", "The Hanged Man", "The Hermit", "Temperance", PLANET_FOR.get(mh)}
                if all(c.get("name") in RESCUE for c in cons):
                    print(f"  (consumable slots hold only rescue/main-hand items {[c.get('name') for c in cons]}: keeping them beats buying {label.split(' [')[0]})")
                    continue
                junk = sorted(cons, key=lambda c: (c.get("name") in RESCUE, c.get("set") == "Planet"))
                print(f"ADVICE: SELL first -> b sellc {junk[0].get('index')}   (consumable slots full; {junk[0].get('name')} is your least useful consumable, sell it then buy {label.split(' [')[0]})")
            return
        if needs_slot and free <= 0:
            weakest = None
            ENGINE = {"Splash", "Four Fingers", "Shortcut", "Smeared Joker", "Pareidolia", "Blueprint", "Brainstorm", "Sock and Buskin", "Hack", "Dusk", "Mime", "Seltzer", "Hanging Chad"}
            for j in jokers:
                if j.get("name") in ENGINE:
                    continue
                s2 = keep_value(j)
                if weakest is None or s2 < weakest[0]:
                    weakest = (s2, j)
            if strong and weakest and weakest[0] < min(score, 100) and cmd.startswith("buy"):
                print(f"ADVICE: SELL then BUY -> b sell {weakest[1].get('index')}  then  b {cmd}   ({weakest[1].get('name')} is your weakest joker; {label})")
                return
            continue
        if score < 30:
            break
        print(f"ADVICE: BUY -> b {cmd}   ({label})")
        return
    reroll = int(sh.get("reroll_cost") or 5)
    n_xmult = sum(1 for j in jokers if (classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") or _joker_edition(j) == "polychrome"))
    want_xmult = (ante >= 3 and n_xmult == 0) or (ante >= 4 and n_xmult < 2) or (ante >= 6 and n_xmult < 3)
    if want_xmult and (money - reroll >= 20 or (ante >= 3 and n_xmult == 0 and money - reroll >= 6)):
        print(f"ADVICE: REROLL -> b reroll   (you own {n_xmult} xMult joker(s) at ante {ante}: hunt for one; ${money - reroll} left after; sell your weakest flat joker to make room when it appears)")
        return
    scoring = scoring_now
    if ante <= 2 and scoring < 2 and free > 0 and money - reroll >= 3:
        print(f"ADVICE: REROLL -> b reroll   (ante {ante} with only {scoring} scoring joker(s): a reroll leaving ${money - reroll} for a $3-4 joker beats leaving; the 600 boss needs ~200 per hand)")
        return
    if free > 0 and ante >= 2 and money - reroll >= max(floor, 10):
        print(f"ADVICE: REROLL -> b reroll   (nothing worth buying, {free} free joker slot(s), ${money - reroll} left after)")
        return
    print("ADVICE: LEAVE -> b endshop   (nothing worth buying at this money level)")
    bs = d.get("blind_select") or {}
    boss = ((bs.get("choices") or {}).get("Boss") or {}).get("name")
    if boss:
        print(f"Upcoming boss this ante: {boss}")


def show_legal(l):
    print("Legal: " + ", ".join(sorted({a["type"] for a in lst(l.get("actions"))})))


def _fmt_domain(dom):
    if not isinstance(dom, dict):
        return json.dumps(dom)
    if "one_of" in dom:
        return "one of " + ",".join(map(str, dom["one_of"]))
    if "subset" in dom:
        s = dom["subset"]
        of = s.get("of") or []
        rng = f"{of[0]}..{of[-1]}" if of and of == list(range(of[0], of[0] + len(of))) else ",".join(map(str, of))
        inc = f", must include {s['must_include']}" if s.get("must_include") else ""
        return f"{s.get('min')}-{s.get('max')} of [{rng}]{inc}"
    if "permutation" in dom:
        return f"permutation of 1..{dom['permutation']}"
    if dom.get("seed"):
        return "any seed (`--seed S`)" + (", optional" if dom.get("optional") else "")
    return json.dumps(dom)


def fmt_entry(a):
    ps = "; ".join(f"{k}: {_fmt_domain(v)}" for k, v in (a.get("params") or {}).items())
    info = a.get("info") or {}
    tag = info.get("name") or info.get("key")
    return f"{a['type']}" + (f"  {ps}" if ps else "") + (f"  ({tag}" + (f" ${info['cost']}" if info.get("cost") is not None else "") + ")" if tag else "")


def _domain_ok(dom, v):
    if not isinstance(dom, dict):
        return False
    if "one_of" in dom:
        return v in dom["one_of"]
    if "subset" in dom:
        s = dom["subset"]
        if not isinstance(v, list) or len(set(v)) != len(v):
            return False
        return (s.get("min", 0) <= len(v) <= s.get("max", len(v)) and set(v) <= set(s.get("of") or [])
                and set(s.get("must_include") or []) <= set(v))
    if "permutation" in dom:
        return isinstance(v, list) and sorted(v) == list(range(1, int(dom["permutation"]) + 1))
    if dom.get("seed"):
        return isinstance(v, (str, int))
    return True


def legal_entries(l, typ):
    return [a for a in lst(l.get("actions")) if a.get("type") == typ]


def legal_match(l, typ, params):
    """True iff params match one /legal entry of typ (every given param in its domain; absent params optional)."""
    for a in legal_entries(l, typ):
        doms = a.get("params") or {}
        if any(k not in doms for k in params):
            continue
        if all((k in params and _domain_ok(dom, params[k])) or (k not in params and isinstance(dom, dict) and dom.get("optional"))
               for k, dom in doms.items()):
            return True
    return False


AREAS = {"hand": "hand", "h": "hand", "jokers": "jokers", "joker": "jokers", "j": "jokers",
         "consumables": "consumables", "cons": "consumables", "c": "consumables"}

# Commands that only read state; everything else sends an action and therefore needs --why.
FREE = {"s", "state", "hands", "advise", "shopadvise", "legal", "raw", "sel", "help"}
USAGE = """commands (state-changing ones need --why "..."):
  read-only: s | hands | advise | shopadvise | legal | raw | sel i j ... (preview a selection) | help
  run:   start <deck> <stake 1-8> [--seed S]
  blind: blind | skip | rerollboss
  hand:  play [TYPE] i j ... | disc i j ... | sort rank|suit
  cards: use N [t1 t2 ...] | sellc N | sell N | order [hand|jokers|cons] p1 p2 ... | move hand|jokers|cons FROM TO
  shop:  buy N | buyuse N [t1 ...] | vouch N | pack N | reroll | endshop | cash
  pack:  pick N [t1 t2 ...] | skippack
  raw:   do TYPE '{json params}'   (harness testing only: skips the client-side legality check)"""


def parse_flags(args):
    """Pull --why/--seed (either `--x val` or `--x=val`) out of argv; returns (positional, why, seed)."""
    pos, opts, i = [], {}, 0
    while i < len(args):
        a = args[i]
        name = next((n for n in ("why", "seed") if a == f"--{n}" or a.startswith(f"--{n}=")), None)
        if name is None:
            pos.append(a); i += 1
        elif "=" in a:
            opts[name] = a.split("=", 1)[1]; i += 1
        else:
            opts[name] = args[i + 1] if i + 1 < len(args) else ""; i += 2
    return pos, opts.get("why"), opts.get("seed")


def check_why(why):
    if why is None:
        return 'missing --why "...": every state-changing command needs a one-line rationale (it is recorded as training data)'
    if not why.strip():
        return "--why is empty: give a one-line rationale"
    if "\n" in why or "\r" in why:
        return "--why must be a single line"
    if len(why) > WHY_MAX:
        return f"--why is {len(why)} chars; keep it to {WHY_MAX} or fewer"
    return None


def build_action(cmd, rest, ints, d):
    """Map a CLI command to (type, params); exits with a message on malformed input."""
    n1 = ints[0] if ints else None
    if cmd == "start":
        deck = " ".join(x for x in rest if not x.isdigit()) or "Black Deck"
        if not deck.startswith("b_"):  # "Black Deck" / "black" -> "b_black" (the /legal domain lists back keys)
            deck = "b_" + re.sub(r"\s+deck$", "", deck.strip(), flags=re.I).lower().replace(" ", "_")
        return "START_RUN", {"deck": deck, "stake": n1 or 1}
    simple = {"blind": "SELECT_BLIND", "skip": "SKIP_BLIND", "rerollboss": "REROLL_BOSS", "cash": "CASH_OUT",
              "reroll": "SHOP_REROLL", "endshop": "SHOP_END", "skippack": "SKIP_PACK"}
    if cmd in simple:
        return simple[cmd], {}
    if cmd in ("play", "disc"):
        return ("PLAY_HAND" if cmd == "play" else "DISCARD"), {"card_indices": ints}
    if cmd == "sort":
        return "SORT_HAND", {"mode": rest[0] if rest else "rank"}
    slot = {"buy": "SHOP_BUY", "vouch": "SHOP_BUY_VOUCHER", "pack": "SHOP_BUY_BOOSTER"}
    if cmd in slot:
        return slot[cmd], {"slot": n1}
    if cmd == "sell":
        return "SELL_JOKER", {"index": n1}
    if cmd == "sellc":
        return "SELL_CONSUMABLE", {"index": n1}
    if cmd in ("use", "pick", "buyuse"):
        typ = {"use": "USE_CONSUMABLE", "pick": "SELECT_PACK_CARD", "buyuse": "SHOP_BUY_AND_USE"}[cmd]
        params = {("slot" if cmd == "buyuse" else "index"): n1}
        if len(ints) > 1:
            params["targets"] = ints[1:]
        return typ, params
    if cmd in ("order", "move"):
        area = AREAS.get(rest[0].lower()) if rest and not rest[0].isdigit() else None
        if cmd == "order":
            return "REORDER", {"area": area or "jokers", "order": ints}
        if not area or len(ints) != 2:
            print("usage: move hand|jokers|cons FROM TO"); sys.exit(1)
        n = len(lst(d.get(area)))
        src, dst = ints
        if not (1 <= src <= n and 1 <= dst <= n):
            print(f"move: positions must be 1..{n} for {area}"); sys.exit(1)
        order = list(range(1, n + 1))
        order.insert(dst - 1, order.pop(src - 1))
        return "REORDER", {"area": area, "order": order}
    print(f"unknown cmd {cmd}\n{USAGE}"); sys.exit(1)


def explain_illegal(l, typ, params, d):
    ents = legal_entries(l, typ)
    if not ents:
        print(f"NOT LEGAL NOW: {typ} is not available in {d.get('phase')}. Nothing was sent.")
    else:
        print(f"NOT LEGAL NOW: {typ} {json.dumps(params)} matches no legal form. Nothing was sent. Legal forms:")
        for a in ents:
            print("  " + fmt_entry(a))
    show_legal(l)


def pre_checks(cmd, typ, params, ints, d):
    """Advisory checks and warnings before sending (strategy hints; legality is decided by /legal)."""
    hand = lst(d.get("hand"))
    n_j = len(lst(d.get("jokers"))); slots_j = int(d.get("joker_slots") or 5)
    n_c = len(lst(d.get("consumables"))); slots_c = int(d.get("consumable_slots") or 2)
    shg = d.get("shop") or {}
    tg = sorted(params.get("targets") or [])
    if cmd == "pack":
        bst = next((b for b in lst(shg.get("boosters")) if b.get("index") == params["slot"]), None)
        if bst and "Buffoon" in str(bst.get("name")) and n_j >= slots_j:
            print(f"ABORTED: {bst.get('name')} offers only jokers and your joker slots are full ({n_j}/{slots_j}); the pack could only be skipped. `sell N` a joker first if you want it.")
            sys.exit(2)
    if cmd == "buy":
        itm = next((c for c in lst(shg.get("jokers")) if c.get("index") == params["slot"]), None)
        if itm and itm.get("set") in ("Planet", "Tarot", "Spectral") and n_c >= slots_c:
            print(f"ABORTED: consumable slots are full ({n_c}/{slots_c}); `buyuse {params['slot']}` uses {itm.get('name')} straight from the shop, or `use N`/`sellc N` a consumable first.")
            sys.exit(2)
        if itm and itm.get("set") == "Joker" and n_j >= slots_j:
            print(f"ABORTED: joker slots are full ({n_j}/{slots_j}); `sell N` your weakest joker first, then buy {itm.get('name')}.")
            sys.exit(2)
    name = None
    if cmd == "pick":
        cards = lst((d.get("pack") or {}).get("cards"))
        target = cards[params["index"] - 1] if 0 < params["index"] <= len(cards) else None
        name = (target or {}).get("name")
        SUIT_TAROT = {"The Star": "Diamonds", "The Moon": "Clubs", "The Sun": "Hearts", "The World": "Spades"}
        if name in SUIT_TAROT:
            boss_dp = (((d.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}).get("name")
            debuffs = {"The Goad": "Spades", "The Head": "Hearts", "The Club": "Clubs", "The Window": "Diamonds"}.get(boss_dp)
            print(f"{name} converts the selected cards TO {SUIT_TAROT[name]}." + (f" WARNING: the upcoming boss {boss_dp} debuffs {debuffs}." if debuffs == SUIT_TAROT[name] else ""))
        if (target or {}).get("set") == "Planet" or name in PLANET_FOR.values():
            hand_for = next((h for h, pl in PLANET_FOR.items() if pl == name), None)
            mh_p = main_hand(d)
            if hand_for:
                print(f"{name} levels {hand_for}" + (f" (NOT your main hand {mh_p}; a level elsewhere is mostly wasted)" if mh_p not in ("undecided", hand_for) else ""))
        if name in ("Wraith", "Judgement") and n_j >= slots_j:
            print(f"ABORTED: {name} creates a joker but your joker slots are full ({n_j}/{slots_j}); `sell N` a joker first (selling works while a pack is open), pick a different card, or `skippack`.")
            sys.exit(2)
        if name in ("The Fool", "The High Priestess", "The Emperor") and n_c >= slots_c:
            print(f"ABORTED: {name} creates a consumable but your consumable slots are full ({n_c}/{slots_c}); `use N` or `sellc N` one first, then `pick {params['index']}`.")
            sys.exit(2)
    if cmd == "use":
        name = (next((c for c in lst(d.get("consumables")) if c.get("index") == params["index"]), None) or {}).get("name")
    if cmd in ("use", "pick") and name == "Death" and len(tg) == 2:
        hc = _cards_by_idx(d, tg)
        if len(hc) == 2:
            print(f"Death: {card_str(hc[0])} (idx {tg[0]}) becomes a copy of {card_str(hc[1])} (idx {tg[1]}). The LEFT (lower index) card is overwritten.")
    if cmd == "play":
        b = d.get("blind") or {}
        if b.get("boss") and b.get("name") == "The Psychic" and len(ints) != 5:
            print(f"ABORTED: The Psychic requires exactly 5 cards; you selected {len(ints)}. Add non-scoring fillers.")
            sys.exit(2)
    if typ in ("USE_CONSUMABLE", "SELECT_PACK_CARD", "SHOP_BUY_AND_USE") and "targets" not in params:
        key = "slot" if typ == "SHOP_BUY_AND_USE" else "index"
        tdom = next(((a.get("params") or {}).get("targets") for a in legal_entries(LEGAL, typ)
                     if _domain_ok((a.get("params") or {}).get(key), params[key]) and (a.get("params") or {}).get("targets")), None)
        if tdom:
            print(f"ABORTED: {name or typ} needs target hand cards ({_fmt_domain(tdom)}): `{cmd} {params[key]} i [j ...]`. Hand: "
                  + " ".join(f"{c.get('index')}:{card_str(c)}" for c in hand))
            sys.exit(2)


def play_type_check(rest, ints, d):
    """`play TYPE i j ...`: compare TYPE with the game's own /preview reading; set _EST_CTX for est logging."""
    global _EST_CTX
    expected = HAND_WORDS[rest[0].upper()]
    pr = preview(ints)
    if not pr.get("ok"):
        print("PREVIEW FAILED (nothing sent):", pr.get("error")); sys.exit(1)
    pv = pr.get("hand")
    if pr.get("hidden") or pv is None:
        print("Preview hidden (face-down cards selected): type check skipped, playing as requested.")
        pv = None
    if pv == "Royal Flush" and expected == "Straight Flush":
        expected = "Royal Flush"
    if pv and pv != expected:
        print(f"ABORTED: you asked for {expected} but these cards form {pv}. Re-run `hands` and pick indices again.")
        sys.exit(2)
    scoring_idx = ints
    for hn, idxs, _e in _candidates(d):
        if hn == expected and set(idxs) <= set(ints):
            scoring_idx = idxs
            break
    if any(j.get("name") == "Splash" for j in lst(d.get("jokers"))):
        scoring_idx = ints
    else:
        stones = [c.get("index") for c in _cards_by_idx(d, ints) if "Stone" in _enh(c) and c.get("index") not in scoring_idx]
        scoring_idx = scoring_idx + stones  # Stone cards always score (+50 chips) even as fillers
    est, notes = estimate(expected, _cards_by_idx(d, scoring_idx), _held(d, ints), d, repeat=_repeat_flag(d, expected), played_n=len(ints))
    print(f"Playing {expected} with idx {ints} (scoring {scoring_idx}): est {est}" + (f" | notes: {'; '.join(notes)}" if notes else ""))
    _EST_CTX = (expected, scoring_idx, est, int(((d.get("blind") or {}).get("chips_scored")) or 0), d)


def show_preview(ints, d):
    pr = preview(ints)
    if not pr.get("ok"):
        print("PREVIEW FAILED:", pr.get("error")); return
    hn = pr.get("hand")
    print(f"Preview of {ints}: {hn} scoring {pr.get('scoring')} L{pr.get('level')} {pr.get('chips')}x{pr.get('mult')} (base, jokers not applied)"
          + (" | the blind debuffs this hand" if pr.get("blind_debuffed") else ""))
    if hn and pr.get("scoring"):
        est, notes = estimate(hn, _cards_by_idx(d, pr["scoring"]), _held(d, ints), d, repeat=_repeat_flag(d, hn), played_n=len(ints))
        print(f"  est with jokers {est}" + (f" | notes: {'; '.join(notes)}" if notes else ""))


def main():
    global LEGAL
    args, why, seed = parse_flags(sys.argv[1:])
    cmd, rest = (args[0], args[1:]) if args else ("s", [])
    ints = [int(re.sub(r"^[A-Za-z]+", "", x)) for x in rest if re.sub(r"^[A-Za-z]+", "", x).lstrip("-").isdigit() and re.sub(r"^[A-Za-z]+", "", x) != ""]
    if cmd == "help":
        print(USAGE); return
    if cmd not in FREE:
        err = check_why(why)
        if err:
            print(f"REFUSED (nothing sent): {err}.\n  e.g. b <port> {' '.join(args)} --why \"Two Pair est 412 clears the 300 needed\"")
            sys.exit(1)
    if cmd in ("buy", "buyuse", "vouch", "pack", "pick", "sell", "sellc", "use") and not ints:
        print(f"{cmd} needs a slot number (e.g. `{cmd} 2` or `{cmd} J2`)"); sys.exit(1)
    d = wait_settled()
    LEGAL = get("legal")
    if cmd in ("s", "state"):
        show(d); show_legal(LEGAL); return
    if cmd == "hands":
        show_hands(d); return
    if cmd == "advise":
        advise(d); return
    if cmd == "shopadvise":
        shop_advise(d); return
    if cmd == "legal":
        l = get("legal")
        print(f"[{l.get('phase')}] settled={l.get('settled')}")
        for a in lst(l.get("actions")):
            print("  " + fmt_entry(a))
        return
    if cmd == "raw":
        d.pop("hand_levels", None)
        print(json.dumps(d, indent=1)); return
    if cmd == "sel":
        show(d); show_preview(ints, d); return
    _META.update({"why": why.strip(), "agent": os.environ.get("BALATRO_AGENT_ID") or f"port-{PORT}", "client": _client_id()})
    if os.environ.get("BALATRO_AGENT_MODEL"):
        _META["model"] = os.environ["BALATRO_AGENT_MODEL"]
    if cmd == "do":
        typ, params = rest[0], json.loads(rest[1] if len(rest) > 1 else "{}")
    else:
        typ, params = build_action(cmd, rest, ints, d)
        if seed is not None:
            if typ != "START_RUN":
                print("--seed only applies to `start`"); sys.exit(1)
            params["seed"] = seed
        pre_checks(cmd, typ, params, ints, d)
        if not legal_match(LEGAL, typ, params):
            explain_illegal(LEGAL, typ, params, d); sys.exit(2)
        if cmd == "play" and rest and rest[0].upper() in HAND_WORDS:
            play_type_check(rest, ints, d)
    for attempt in range(4):
        r = act(typ, params)
        if r.get("ok") or not r.get("retry") or attempt == 3:
            break
        print(f"(bridge not settled: {r.get('error')}; waiting and retrying)")
        wait_settled()
    if r.get("ok"):
        print(f"ok: {typ}" + (f" (step {r['step']})" if r.get("step") is not None else "")
              + (f" -> recording {r['trajectory_path']}" if r.get("trajectory_path") else ""))
    else:
        print("ACTION REJECTED:", r.get("error"))
    d = wait_settled()
    LEGAL = get("legal")
    show(d)
    show_legal(LEGAL)
    if cmd == "play" and _EST_CTX and r.get("ok"):
        _log_est(d)
    if not r.get("ok"):
        sys.exit(2)


_EST_CTX = None


def _log_est(d):
    """Append est vs actual for the hand just played to docs/runs/est_log.tsv (for estimator calibration)."""
    try:
        expected, idxs, est, before, d0 = _EST_CTX
        after = (d.get("blind") or {}).get("chips_scored")
        if after is None:
            after = d.get("chips")  # blind is gone in ROUND_EVAL; `chips` still holds the round's score
        if after is None:
            return
        after = int(after)
        actual = after - before if after >= before else after
        cards = " ".join(card_str(c) for c in _cards_by_idx(d0, idxs))
        jokers = ",".join(str(j.get("name")) + ("(" + str(_joker_edition(j)) + ")" if _joker_edition(j) else "") for j in lst(d0.get("jokers")))
        boss = ((d0.get("blind") or {}).get("name") or "") if (d0.get("blind") or {}).get("boss") else "-"
        flag = "OK" if actual and abs(actual - est) <= 0.2 * max(actual, 1) else "MISS"
        line = f"{os.environ.get('BALATRO_RL_PORT', '7777')}\ta{d0.get('ante')}\t{boss}\t{expected}\t{cards}\t{jokers}\test={est}\tactual={actual}\t{flag}\n"
        with open(os.path.join(RUNS_DIR, "est_log.tsv"), "a", encoding="utf-8") as f:
            f.write(line)
        if flag == "MISS":
            print(f"(est {est} vs actual {actual}: logged for calibration)")
    except Exception as e:
        print(f"(est log skipped: {e})")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"BRIDGE OFFLINE: nothing is listening on port {PORT} (Connection refused). Not retryable: stop and report.")
        sys.exit(3)
