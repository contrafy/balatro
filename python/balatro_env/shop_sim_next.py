"""Shop/pack option valuation by simulating the next blinds with the round solver.

`value_options(state, options=None, *, budget_s=4.0)` applies each option (a hypothetical edit of the run: buy a
joker, take a pack card, use a planet, add playing cards, sell jokers) to a copy of the state, then plays the next
`blinds` blinds (default 3: the ones still open this ante from `blind_select`, then the next ante's Small/Big/Boss
from the stake's base table, boss effect unknown) as fresh rounds dealt from the full deck composition
(`deck.cards`; uniformly random orders, never `hidden`). Each round is played by `solver.RoundSolver`'s greedy policy
and scored with cli.py's `estimate`, so joker effects match the in-round advisor.

Between rounds: perishable jokers expire (debuffed once their tally runs out), rentals cost $3, Gros Michel dies with
1/6 per round, Popcorn/Ice Cream/Ramen/Turtle Bean/Seltzer decay, Mr. Bones saves one failed blind scored at >= 25%
and is then destroyed. Hand size / discards / hands jokers (Juggler, Drunkard, Merry Andy, Troubadour, Stuntman,
Turtle Bean, Burglar) change the round parameters; boss effects The Needle, The Water and The Manacle do too, and the
solver applies the others it models (Psychic, Mouth, Eye, Hook, Serpent, suit/face debuffs, Flint, Arm via
estimate). Not modelled: joker growth across rounds (Hologram, Green Joker, Ride the Bus...), shop income/interest,
face-down bosses, Crimson Heart, Verdant Leaf (assumed handled by selling a joker), future shops.

Common random numbers: every option sees the same deals for the same (blind, sample), so deltas are much less noisy
than the absolute probabilities. Stdlib only; cli.py may load it by file path.
"""
from __future__ import annotations

import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter

LEVEL_UP = {"High Card": (10, 1), "Pair": (15, 1), "Two Pair": (20, 1), "Three of a Kind": (20, 2),
            "Straight": (30, 3), "Flush": (15, 2), "Full House": (25, 2), "Four of a Kind": (30, 3),
            "Straight Flush": (40, 4), "Five of a Kind": (35, 3), "Flush House": (40, 4), "Flush Five": (50, 3)}
PLANET_HAND = {"Pluto": "High Card", "Mercury": "Pair", "Uranus": "Two Pair", "Venus": "Three of a Kind",
               "Saturn": "Straight", "Jupiter": "Flush", "Earth": "Full House", "Mars": "Four of a Kind",
               "Neptune": "Straight Flush", "Planet X": "Five of a Kind", "Ceres": "Flush House", "Eris": "Flush Five"}
RENT = 3
TIE_P = 0.02  # p differences below this are sampling noise: ties rank by mean score ratio, then money
# Rent is money the next shops cannot spend. Gold shops convert ~$5 into a scorer worth ~+0.05..0.3 survival, so one
# rent dollar is charged DOLLAR_P of p (heuristic); a later shop entered with negative money buys nothing.
DOLLAR_P = 0.01
DEAD_SHOP_P = 0.05


def _lst(v):
    if isinstance(v, dict):
        return list(v.values())
    return v or []


def _solver():
    """The round solver module: the package one when the package is loaded, else solver.py by file path."""
    m = sys.modules.get("balatro_env.solver")
    if m is not None:
        return m
    if "balatro_env" in sys.modules:
        from balatro_env import solver as m
        return m
    m = sys.modules.get("_balatro_round_solver")
    if m is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solver.py")
        spec = importlib.util.spec_from_file_location("_balatro_round_solver", p)
        m = importlib.util.module_from_spec(spec)
        sys.modules["_balatro_round_solver"] = m
        spec.loader.exec_module(m)
    return m


# ---- blinds ---------------------------------------------------------------------------------------------------
def upcoming_blinds(state, n=3, blind_base=None):
    """The next n blinds to play: [{ante, kind, name, boss, chips}]. Open blinds of this ante come from
    blind_select (exact chips, known boss); later antes from blind_base (cli.BLIND_BASE) scaled like the current
    ante's Small Blind, with an unknown boss (no effect, 2x chips)."""
    ante = int(state.get("ante") or 1)
    ch = (state.get("blind_select") or {}).get("choices") or {}
    skip = {"Defeated", "Skipped"} | ({"Current"} if state.get("phase") == "ROUND_EVAL" else set())
    out = []
    for kind in ("Small", "Big", "Boss"):
        c = ch.get(kind) or {}
        if not c or (c.get("state") or "Upcoming") in skip or not c.get("chips"):
            continue
        out.append({"ante": ante, "kind": kind, "name": c.get("name") or kind, "boss": bool(c.get("boss")),
                    "chips": int(c.get("chips")), "dollars": int(c.get("dollars") or 0)})
    if blind_base:
        stake = int(state.get("stake") or 1)
        table = blind_base[3 if stake >= 6 else (2 if stake >= 3 else 1)]
        small = (ch.get("Small") or {}).get("chips")
        k = float(small) / table[ante - 1] if small and 1 <= ante <= len(table) else 1.0
        a = ante
        while len(out) < n and a < len(table):
            a += 1
            base = int(table[a - 1] * k)
            small_d = 0 if stake >= 2 else 3  # Red Stake and up: the Small Blind pays nothing
            out += [{"ante": a, "kind": "Small", "name": "Small Blind", "boss": False, "chips": base, "dollars": small_d},
                    {"ante": a, "kind": "Big", "name": "Big Blind", "boss": False, "chips": int(base * 1.5), "dollars": 4},
                    {"ante": a, "kind": "Boss", "name": "Boss (unknown)", "boss": False, "chips": base * 2, "dollars": 5}]
    return out[:n]


# ---- options ----------------------------------------------------------------------------------------------------
def _is_joker(item):
    return item.get("set") == "Joker" or str(item.get("key") or "").startswith("j_")


def _is_playing_card(item):
    return item.get("rank") is not None and item.get("suit") is not None


def options_from_state(state, packs=False):
    """Standard options for the current SHOP or PACK_OPENING state: baseline, every affordable shop joker, shop
    planet, shop playing card, every pack joker/planet/playing card. Jokers that need a slot when the slots are full
    come with sell='weakest' (the owned non-eternal joker whose loss costs the least, found by simulation).
    packs=True (SHOP): also every affordable Buffoon / Celestial booster as {label, pack: {kind, size, choose}, cost,
    booster_index} (valued by value_options as the expected best pick; adds simulation work)."""
    ph = state.get("phase")
    money = int(state.get("money") or 0)
    full = len(_lst(state.get("jokers"))) >= int(state.get("joker_slots") or 5)
    opts = []
    if ph == "PACK_OPENING":
        opts.append({"label": "skip pack"})
        items = [(c, 0) for c in _lst((state.get("pack") or {}).get("cards"))]
        verb = "take"
    else:
        opts.append({"label": "baseline (buy nothing)"})
        items = [(c, int(c.get("cost") or 0)) for c in _lst((state.get("shop") or {}).get("jokers"))]
        verb = "buy"
    for c, cost in items:
        if cost > money:
            continue
        name = c.get("name") or c.get("key")
        tag = f"{verb} {name}" + (f" ${cost}" if cost else "")
        if _is_joker(c):
            o = {"label": tag, "add_joker": c, "cost": cost}
            if full and c.get("edition") != "negative":
                o["sell"] = "weakest"
            opts.append(o)
        elif c.get("set") == "Planet" and (name in PLANET_HAND or name == "Black Hole"):
            opts.append({"label": tag, "levels": ["*"] if name == "Black Hole" else [PLANET_HAND[name]], "cost": cost})
        elif c.get("set") == "Spectral" and name == "Black Hole":
            opts.append({"label": tag, "levels": ["*"], "cost": cost})
        elif _is_playing_card(c):
            opts.append({"label": tag, "add_cards": [c], "cost": cost})
    if packs and ph == "SHOP":
        for b in _lst((state.get("shop") or {}).get("boosters")):
            cost = int(b.get("cost") or 0)
            if b.get("kind") in ("Buffoon", "Celestial") and cost <= money:
                opts.append({"label": f"buy {b.get('name') or b.get('kind') + ' Pack'} ${cost}", "cost": cost,
                             "pack": {"kind": b.get("kind"), "size": b.get("size"), "choose": b.get("choose")},
                             "booster_index": b.get("index")})
    return opts


def _edition(j):
    e = j.get("edition")
    if isinstance(e, dict):
        return e.get("type")
    return e


def apply_option(state, opt):
    """Copy of state with the option applied; returns (state, error or None, notes)."""
    st = dict(state)
    notes = []
    jokers = [dict(j) for j in _lst(state.get("jokers"))]
    money = int(state.get("money") or 0) - int(opt.get("cost") or 0)
    sold = opt.get("sell") or []
    if sold == "weakest":
        return st, "unresolved sell", notes
    for ix in sold:
        j = next((x for x in jokers if x.get("index") == ix), None)
        if j is None:
            return st, f"no joker at index {ix}", notes
        if j.get("eternal") or (j.get("ability") or {}).get("eternal"):
            return st, f"{j.get('name')} is eternal", notes
        money += int(j.get("sell_cost") or 0)
        jokers.remove(j)
        notes.append(f"sell {j.get('name')} +${int(j.get('sell_cost') or 0)}")
    nj = opt.get("add_joker")
    if nj:
        if len(jokers) >= int(state.get("joker_slots") or 5) and _edition(nj) != "negative":
            return st, "no free joker slot", notes
        j = {k: nj.get(k) for k in ("key", "name", "rarity", "edition", "sell_cost", "eternal", "perishable",
                                    "perish_tally", "rental", "ability", "set")}
        j["ability"] = dict(nj.get("ability") or {})
        if j.get("perishable") and j.get("perish_tally") is None:
            j["perish_tally"] = j["ability"].get("perish_tally", 5)
        j["debuff"] = False
        j["index"] = len(jokers) + 1
        jokers.append(j)
    for i, j in enumerate(jokers):
        j["index"] = i + 1
    if money < 0:
        return st, f"not affordable (money {money})", notes
    st["jokers"] = jokers
    st["money"] = money
    if opt.get("levels"):
        hl = {k: dict(v) for k, v in (state.get("hand_levels") or {}).items()}
        for h in opt["levels"]:
            for name in (list(LEVEL_UP) if h == "*" else [h]):
                v = hl.setdefault(name, {"level": 1, "chips": 0, "mult": 1})
                c, m = LEVEL_UP.get(name, (0, 0))
                v["level"] = int(v.get("level") or 1) + 1
                v["chips"] = float(v.get("chips") or 0) + c
                v["mult"] = float(v.get("mult") or 1) + m
        st["hand_levels"] = hl
        planets = sum(1 for h in opt["levels"] if h != "*")  # Black Hole is a Spectral: Constellation ignores it
        if planets:
            for j in jokers:
                if j.get("name") == "Constellation" and not j.get("debuff"):
                    ab = dict(j.get("ability") or {})
                    ab["x_mult"] = max(1.0, float(ab.get("x_mult") or 1)) + 0.1 * planets
                    j["ability"] = ab
                    notes.append(f"Constellation +x{0.1 * planets:.1f}")
    if opt.get("add_cards") or opt.get("remove_cards") or opt.get("enhance"):
        dk = dict(state.get("deck") or {})
        cards = [dict(c) for c in _lst(dk.get("cards")) if c.get("id") not in set(opt.get("remove_cards") or [])]
        for c, enh in (opt.get("enhance") or {}).items():
            for x in cards:
                if x.get("id") == c:
                    x["enhancement"] = enh
        nid = max([int(c.get("id") or 0) for c in cards] + [0]) + 1000
        for c in opt.get("add_cards") or []:
            cards.append({"id": nid, "rank": c.get("rank"), "suit": c.get("suit"), "enhancement": c.get("enhancement"),
                          "edition": c.get("edition"), "seal": c.get("seal"), "perma_bonus": c.get("perma_bonus") or 0})
            nid += 1
        dk["cards"] = cards
        st["deck"] = dk
    return st, None, notes


# ---- round parameters per blind ------------------------------------------------------------------------------
def _joker_round_effects(j):
    """(hand size, discards, hands) this joker adds while active."""
    n = j.get("name")
    ab = j.get("ability") or {}
    ex = ab.get("extra") if isinstance(ab.get("extra"), dict) else {}
    hs = float(ab.get("h_size") or 0)
    ds = float(ab.get("d_size") or 0)
    hp = 0
    if n == "Troubadour":
        hs += float(ex.get("h_size", 2))
        hp += int(ex.get("h_plays", -1))
    elif n == "Turtle Bean":
        hs += float(ex.get("h_size", 5))
    elif n == "Stuntman":
        hs -= float(ex.get("h_size", 2))
    return hs, ds, hp


def _active(j):
    return not j.get("debuff")


def _jokers_at(jokers, k, removed, growth=()):
    """Jokers as they will be at blind k (k round-ends from now): perished ones debuffed, decayed values applied,
    removed ids (Gros Michel died, Mr. Bones used, Seltzer/Popcorn/Ice Cream used up, destroyed by Madness or
    Ceremonial Dagger) dropped; growth = ((index, gain), ...) adds Dagger mult / Madness xMult gained so far."""
    grow = dict(growth)
    out = []
    for i, j in enumerate(jokers):
        if i in removed:
            continue
        ab = dict(j.get("ability") or {})
        j = dict(j, ability=ab)
        n = j.get("name")
        if i in grow:
            if n == "Ceremonial Dagger":
                ab["mult"] = float(ab.get("mult") or 0) + grow[i]
            elif n == "Madness":
                ab["x_mult"] = max(1.0, float(ab.get("x_mult") or 1)) + grow[i]
        tally = j.get("perish_tally", ab.get("perish_tally"))
        if (j.get("perishable") or ab.get("perishable")) and tally is not None and int(tally) - k <= 0:
            j["debuff"] = True
        if k:
            if n == "Popcorn":
                ab["mult"] = float(ab.get("mult") or 0) - 4 * k
                if ab["mult"] <= 0:
                    continue
            elif n == "Ice Cream" and isinstance(ab.get("extra"), dict):
                ab["extra"] = dict(ab["extra"], chips=float(ab["extra"].get("chips") or 0) - 10 * k)
                if ab["extra"]["chips"] <= 0:
                    continue
            elif n == "Ramen":
                ab["x_mult"] = max(1.0, float(ab.get("x_mult") or 2) - 0.08 * k)
            elif n == "Turtle Bean" and isinstance(ab.get("extra"), dict):
                ab["extra"] = dict(ab["extra"], h_size=float(ab["extra"].get("h_size", 5)) - k)
                if ab["extra"]["h_size"] <= 0:
                    continue
            elif n == "Seltzer":
                left = float(ab.get("extra") if not isinstance(ab.get("extra"), dict) else 10) - 2.5 * k
                if left <= 0:
                    continue
        out.append(j)
    return out


def _rounds_left(state):
    """Round-ends still ahead through the ante-8 boss (rent is charged at each)."""
    ante = int(state.get("ante") or 1)
    ch = (state.get("blind_select") or {}).get("choices") or {}
    open_ = sum(1 for k in ("Small", "Big", "Boss") if ((ch.get(k) or {}).get("state") or "Upcoming")
                not in ("Defeated", "Skipped"))
    return max(1, open_ + 3 * max(0, 8 - ante))


def _round_state(st, base, blind, k, removed, growth=(), added=(), ob=None):
    """Synthetic SELECTING_HAND state for a fresh round of `blind` played k round-ends from now; `added` are jokers
    created since (Riff-raff); ob = (Obelisk x_mult, hand-type play counts) carried from the previous rounds."""
    jokers = _lst(st.get("jokers"))
    now = _jokers_at(jokers, k, removed, growth) + [dict(j, index=len(jokers) + i + 1) for i, j in enumerate(added)]
    hs = int(base.get("hand_size") or 8)
    ds = int(base.get("discards_per_round") or base.get("discards_remaining") or 0)
    hp = int(base.get("hands_per_round") or base.get("hands_remaining") or 1)
    for j in _lst(base.get("jokers")):  # the base state's round sizes already include its active jokers
        if _active(j):
            a, b, c = _joker_round_effects(j)
            hs, ds, hp = hs - a, ds - b, hp - c
    for j in now:
        if _active(j):
            a, b, c = _joker_round_effects(j)
            hs, ds, hp = hs + a, ds + b, hp + c
    if any(j.get("name") == "Burglar" and _active(j) for j in now):
        hp, ds = hp + 3, 0
    name = blind["name"]
    boss = blind["boss"] and name not in ("Verdant Leaf", "Crimson Heart", "Boss (unknown)")
    if boss and name == "The Needle":
        hp = 1
    if boss and name == "The Water":
        ds = 0
    if boss and name == "The Manacle":
        hs -= 1
    rentals = sum(1 for j in jokers if j.get("rental"))
    cards = [dict(c, remaining=True) for c in _lst((st.get("deck") or {}).get("cards"))]
    hl = st.get("hand_levels") or {}
    if ob is not None and hl:
        counts = dict(ob[1])
        hl = {h: dict(v, played=counts.get(h, int(v.get("played") or 0))) for h, v in hl.items()}
        now = [dict(j, ability=dict(j.get("ability") or {}, x_mult=ob[0])) if j.get("name") == "Obelisk" else j
               for j in now]
    elif k and hl:
        # growth over the k rounds already played, assuming ~2 plays of the most played type per round: Supernova
        # reads that type's play count; Spare Trousers gains +2 mult per Two Pair-family play
        main = max(hl, key=lambda h: int((hl[h] or {}).get("played") or 0))
        names = {j.get("name") for j in now if _active(j)}
        if "Supernova" in names:
            hl = dict(hl, **{main: dict(hl[main], played=int(hl[main].get("played") or 0) + 2 * k)})
    if k and hl and any(j.get("name") == "Spare Trousers" and _active(j) for j in now):
        main = max(hl, key=lambda h: int((hl[h] or {}).get("played") or 0))
        if main in ("Two Pair", "Full House", "Flush House"):
            now = [dict(j, ability=dict(j.get("ability") or {}, mult=float((j.get("ability") or {}).get("mult") or 0)
                                        + 4 * k)) if j.get("name") == "Spare Trousers" else j for j in now]
    return dict(st, phase="SELECTING_HAND", hand=[], jokers=now, money=int(st.get("money") or 0) - RENT * rentals * k,
                hand_size=max(1, int(round(hs))), hands_remaining=max(1, int(hp)), discards_remaining=max(0, int(ds)),
                blind={"name": name, "boss": boss, "chips_needed": blind["chips"], "chips_scored": 0, "disabled": False},
                deck=dict(st.get("deck") or {}, cards=cards, draw_pile=len(cards)), hand_levels=hl)


# ---- simulation ---------------------------------------------------------------------------------------------------
_COMMONS = None


def _commons():
    """Common jokers of the empirical Gold pool (pack_pool.json) without stickers: what Riff-raff creates."""
    global _COMMONS
    if _COMMONS is None:
        pool = load_pack_pool() or {}
        merged = {}
        for j in pool.get("jokers") or []:
            if int(j.get("rarity") or 0) != 1:
                continue
            key = (j.get("name"), j.get("edition"))
            if key in merged:
                merged[key]["count"] += j["count"]
            else:
                merged[key] = dict(j, eternal=False, perishable=False, rental=False, perish_tally=None, debuff=False)
        _COMMONS = list(merged.values())
    return _COMMONS


class _OptionSim:
    def __init__(self, sv, est, state, blinds, seed):
        self.sv, self.est, self.state, self.base, self.blinds, self.seed = sv, est, state, None, blinds, seed
        self.solvers = {}
        self.jokers = _lst(state.get("jokers"))
        self.gros = [i for i, j in enumerate(self.jokers) if j.get("name") == "Gros Michel" and _active(j)]
        self.bones = [i for i, j in enumerate(self.jokers) if j.get("name") == "Mr. Bones" and _active(j)]
        self.daggers = [i for i, j in enumerate(self.jokers) if j.get("name") == "Ceremonial Dagger" and _active(j)]
        self.madness = [i for i, j in enumerate(self.jokers) if j.get("name") == "Madness" and _active(j)]
        self.riffraff = [i for i, j in enumerate(self.jokers) if j.get("name") == "Riff-raff" and _active(j)]
        self.slots = int(state.get("joker_slots") or 5)
        self.stats = [[0, 0, 0.0, 0.0] for _ in blinds]  # per blind: n, survived, sum min(1, total/need), $ hands
        self.joint = 0
        self.n = 0
        self.bones_used = 0
        self.destroyed = 0
        self.created = 0

    def solver(self, k, removed, growth=(), added=(), ob=None):
        key = (k, removed, growth, added, ob)
        rs = self.solvers.get(key)
        if rs is None:
            jk = [_commons()[i] for i in added]
            rs = self.sv.RoundSolver(_round_state(self.state, self.base, self.blinds[k], k, removed, growth, jk, ob),
                                     self.est, seed=0)
            self.solvers[key] = rs
        return rs

    def _eternal(self, i):
        j = self.jokers[i]
        return bool(j.get("eternal") or (j.get("ability") or {}).get("eternal"))

    def _select_blind(self, blind, removed, growth, rng, added=None):
        """Blind-select joker effects: each Ceremonial Dagger destroys the joker to its right (gains 2x its sell
        value as mult); Madness (Small/Big only) destroys a random other joker and gains x0.5; Riff-raff creates 2
        Common jokers (drawn from the empirical Gold pool, no stickers) while slots are free."""
        for d in self.daggers:
            if d in removed:
                continue
            right = next((i for i in range(d + 1, len(self.jokers)) if i not in removed), None)
            if right is not None and not self._eternal(right):
                removed.add(right)
                growth[d] = growth.get(d, 0.0) + 2 * float(self.jokers[right].get("sell_cost") or 1)
                self.destroyed += 1
        if not blind["boss"]:
            for m in self.madness:
                if m in removed:
                    continue
                growth[m] = growth.get(m, 0.0) + 0.5
                victims = [i for i in range(len(self.jokers)) if i != m and i not in removed and not self._eternal(i)]
                if victims:
                    removed.add(rng.choice(victims))
                    self.destroyed += 1
        if added is not None:
            commons = _commons()
            for r in self.riffraff:
                if r in removed or not commons:
                    continue
                free = self.slots - (len(self.jokers) - len(removed)) - len(added)
                for _ in range(max(0, min(2, free))):
                    added.append(rng.choices(range(len(commons)), weights=[c["count"] for c in commons])[0])
                    self.created += 1

    def sample(self, s):
        removed = set()
        growth = {}
        added = []
        ob = None  # Obelisk x_mult and play counts carried from round to round
        grng = random.Random(f"{self.seed}:gros:{s}")
        all_ok = True
        for k, blind in enumerate(self.blinds):
            if k:
                for g in self.gros:
                    if g not in removed and grng.random() < 1 / 6:
                        removed.add(g)
            if self.daggers or self.madness or self.riffraff:
                self._select_blind(blind, removed, growth, grng, added)
            rs = self.solver(k, frozenset(removed), tuple(sorted(growth.items())), tuple(sorted(added)), ob)
            rng = random.Random(f"{self.seed}:{k}:{s}")
            pool = rs.pool
            perm = list(range(len(pool)))
            rng.shuffle(perm)
            cards = [pool[i] for i in perm]
            hand, order = cards[:rs.hand_size], cards[rs.hand_size:]
            kind, sel = rs.policy(hand, order, rs.h0, rs.d0, rs.need0, rs.ctx0)
            ids = {id(c) for c in sel}
            first = (kind, tuple(i for i, c in enumerate(hand) if id(c) in ids))
            ok, tot, hl, _du, _g = rs.rollout(first, hand, order, rng)[:5]
            if getattr(rs, "last_ob", None) is not None:
                ob = (round(rs.last_ob[0], 1), rs.last_ob[1])
            st = self.stats[k]
            st[0] += 1
            st[2] += min(1.0, tot / max(1.0, rs.need0))
            bones_left = [b for b in self.bones if b not in removed]
            if ok and tot < rs.need0:  # the round solver counted a Mr. Bones save
                if bones_left:
                    removed.add(bones_left[0])
                self.bones_used += 1
            elif ok:
                st[3] += hl
            elif bones_left and tot >= 0.25 * rs.need0:
                ok = True
                removed.add(bones_left[0])
                self.bones_used += 1
            st[1] += ok
            all_ok = all_ok and ok
        self.joint += all_ok
        self.n += 1


def _resolve_weakest(sv, est, state, blinds, budget_s, seed):
    """Index of the owned non-eternal joker whose sale lowers p_next the least (ties: higher sell value)."""
    cands = [j for j in _lst(state.get("jokers"))
             if not (j.get("eternal") or (j.get("ability") or {}).get("eternal"))]
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0].get("index")
    res = _run(sv, est, state, [{"label": f"sell {j.get('name')}", "sell": [j.get("index")]} for j in cands],
               blinds, budget_s, seed, min_samples=16)
    best = max(res, key=lambda r: (r["p_next"] or 0, r["score_ratio"] or 0, r["money_after"] or 0))
    return best["option"]["sell"][0]


def _run(sv, est, state, options, blinds, budget_s, seed, min_samples=24, max_samples=400):
    t0 = time.perf_counter()
    sims, res = [], []
    for opt in options:
        st, err, notes = apply_option(state, opt)
        r = {"label": opt.get("label") or "option", "option": opt, "feasible": err is None, "error": err,
             "notes": notes, "money_after": int(st.get("money") or 0) if err is None else None}
        if err is None:
            sim = _OptionSim(sv, est, st, blinds, seed)
            sim.base = state
            sims.append((r, sim))
            rentals = sum(1 for j in _lst(st.get("jokers")) if j.get("rental"))
            r["rent_per_round"] = RENT * rentals
            r["money_after_rent"] = r["money_after"] - RENT * rentals * len(blinds)
            # an eternal rental can never be sold: its rent runs to the end of the run
            stuck = [j for j in _lst(st.get("jokers")) if j.get("rental")
                     and (j.get("eternal") or (j.get("ability") or {}).get("eternal"))]
            r["rent_run"] = RENT * len(stuck) * _rounds_left(state)
            new = opt.get("add_joker")
            if new is not None and any(j.get("name") == new.get("name") for j in stuck):
                r["notes"].append(f"ETERNAL RENTAL: {new.get('name')} costs ${RENT} every round for the rest of the run "
                                  f"(~${RENT * _rounds_left(state)}) and can never be sold")
            for j in _lst(st.get("jokers")):
                tally = j.get("perish_tally", (j.get("ability") or {}).get("perish_tally"))
                if j.get("perishable") and tally is not None and int(tally) < len(blinds):
                    r["notes"].append(f"{j.get('name')} perishes after {int(tally)} more round(s)")
        res.append(r)
    s = 0
    while sims and s < max_samples:
        for _r, sim in sims:
            sim.sample(s)
        s += 1
        if s >= min_samples and time.perf_counter() - t0 > budget_s:
            break
    # the baseline (every delta's reference) always gets BASE_N samples, so repeated calls on the same shop agree (a
    # 3-blind product at n=24 swings by +-0.2); the 2 best options get TOP_N while the total stays under 2x the budget
    for r, sim in sims:
        if _is_base(r["option"]):
            while sim.n < BASE_N:
                sim.sample(sim.n)
    best = sorted((sim for r, sim in sims if not _is_base(r["option"]) and not r["label"].startswith("_pack ")),
                  key=lambda sm: -sm.joint / max(1, sm.n))[:2]
    for sim in best:
        while sim.n < TOP_N and time.perf_counter() - t0 < 2 * budget_s:
            sim.sample(sim.n)
    for r, sim in sims:
        n = max(1, sim.n)
        r["n"] = sim.n
        r["p_next_model"] = sim.joint / n
        r["p_blinds_model"] = [st[1] / max(1, st[0]) for st in sim.stats]
        # the solver's map from greedy-policy p to players' clear rate (jokerless rounds stay raw)
        r["p_blinds"] = [sv.calibrate(p, sim.solver(k, frozenset()).jokerless)
                         for k, p in enumerate(r["p_blinds_model"])]
        r["p_next"] = 1.0
        for p in r["p_blinds"]:
            r["p_next"] *= p
        r["score_ratio"] = sum(st[2] / max(1, st[0]) for st in sim.stats) / max(1, len(sim.stats))
        r["dollars"] = sum(st[3] / max(1, st[0]) for st in sim.stats)
        if sim.bones_used:
            r["notes"].append(f"Mr. Bones saved {sim.bones_used / n:.2f} blinds per run")
        if sim.destroyed:
            r["notes"].append(f"Madness/Ceremonial Dagger destroy {sim.destroyed / n:.1f} joker(s) over these blinds")
        if sim.created:
            r["notes"].append(f"Riff-raff creates {sim.created / n:.1f} Common joker(s) over these blinds")
        r["money_path"] = _money_path(state, sim.state, blinds, sim.stats, r["money_after"])
        r["shop_money"] = min(r["money_path"]) if r["money_path"] else r["money_after"]
        r["dead_shops"] = sum(1 for m in r["money_path"] if m < 0)
        r["rent_horizon"] = r["rent_per_round"] * len(blinds)
        if r["shop_money"] < 0:
            r["notes"].append(f"rent drives money to ${r['shop_money']} before a later shop: that shop is dead")
        elif r["rent_per_round"] >= 2 * RENT:
            r["notes"].append(f"{r['rent_per_round'] // RENT} rentals: -${r['rent_per_round']} every round")
    for r in res:
        r.setdefault("p_next", None)
    return res


def _money_path(base, st, blinds, stats, money):
    """Expected money entering the shop after each simulated blind (Gold cash-out order): rent of every rental is
    charged at round end, then the blind reward, $1 per unused hand (simulated mean) and interest ($1 per $5 held,
    capped; none below $0 or with no_interest)."""
    rentals = sum(1 for j in _lst(st.get("jokers")) if j.get("rental"))
    cap = int(base.get("interest_cap") or 25)
    amt = int(base.get("interest_amount") or 1)
    out = []
    m = float(money)
    for b, s in zip(blinds, stats):
        m -= RENT * rentals
        interest = 0 if base.get("no_interest") or m < 5 else amt * (min(m, cap) // 5)
        m += int(b.get("dollars") or 0) + s[3] / max(1, s[0]) + interest
        out.append(int(round(m)))
    return out


_POOL = None
BASE_N = 96  # guaranteed samples for the baseline option
TOP_N = 64  # guaranteed samples for the 2 best options
PACK_REPS = 8  # joker draws from the pool evaluated per Buffoon pack (distinct ones become simulated sub-options)
PACK_PLANETS = 4  # Celestial: planets of the 4 most played hands are simulated; others count as skipping
PACK_VIRTUAL = 2000  # virtual packs drawn from the evaluated cards for the expected value


def load_pack_pool():
    """Empirical Gold pools for pack options (pack_pool.json next to this file, built by
    `python -m balatro_env.analysis.pack_pool`); None when missing."""
    global _POOL
    if _POOL is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pack_pool.json")
        try:
            with open(p, encoding="utf-8") as f:
                _POOL = json.load(f)
        except OSError:
            _POOL = {}
    return _POOL or None


def _is_base(o):
    return not {k for k in o if not k.startswith("_")} - {"label", "cost"} and not o.get("cost")


def _expand_packs(state, options, seed):
    """Simulated sub-options for pack options: (sub-options, plan per pack option index)."""
    pool = load_pack_pool()
    rng = random.Random(f"{seed}:packs")
    subs, plans, reps = [], {}, {}
    full = len(_lst(state.get("jokers"))) >= int(state.get("joker_slots") or 5)
    owned = {j.get("name") for j in _lst(state.get("jokers"))}
    hl = state.get("hand_levels") or {}
    for oi, o in enumerate(options):
        pk = o.get("pack")
        if not pk:
            continue
        kind = pk.get("kind")
        if not pool or kind not in ("Buffoon", "Celestial"):
            plans[oi] = {"error": "no pack pool" if not pool else f"{kind} packs are not simulated"}
            continue
        if kind not in reps:
            if kind == "Buffoon":
                cands = [j for j in pool["jokers"] if j.get("name") not in owned]
                draws = rng.choices(cands, weights=[j["count"] for j in cands], k=PACK_REPS) if cands else []
                labels = []
                for j in draws:
                    lab = f"_pack Buffoon: {j.get('name')}" + "".join(
                        f" {{{s}}}" for s in ("eternal", "perishable", "rental") if j.get(s)) + (
                        f" ({j['edition']})" if j.get("edition") else "")
                    if lab not in {s["label"] for s in subs}:
                        so = {"label": lab, "add_joker": j, "cost": 0}
                        if full and j.get("edition") != "negative":
                            so["sell"] = "weakest"
                        subs.append(so)
                    labels.append(lab)
                reps[kind] = {"draws": labels}
            else:
                planets = pool["planets"]
                top = sorted(hl, key=lambda h: (-int((hl[h] or {}).get("played") or 0), -int((hl[h] or {}).get("level") or 1)))
                top = [h for h in top if h in PLANET_HAND.values() and int((hl[h] or {}).get("played") or 0) > 0]
                top = top[:PACK_PLANETS] or ["Pair"]  # unplayed hands' planets count as skipping
                names = [n for n in planets if n in PLANET_HAND]
                for n in names:
                    if PLANET_HAND[n] in top:
                        subs.append({"label": f"_pack Celestial: {n}", "levels": [PLANET_HAND[n]], "cost": 0})
                tele = "v_telescope" in [str(v.get("key") if isinstance(v, dict) else v)
                                         for v in _lst(state.get("used_vouchers"))]
                main = next((n for n, h in PLANET_HAND.items() if top and h == top[0]), None)
                reps[kind] = {"names": names, "weights": [planets[n] for n in names], "telescope": main if tele else None}
        plans[oi] = dict(reps[kind], kind=kind, size=int(pk.get("size") or 2), choose=int(pk.get("choose") or 1))
    return subs, plans


def _pack_result(o, plan, by_label, base, money, n_blinds, seed):
    """Expected outcome of opening the pack: best card (or skip) per virtual pack, averaged."""
    r = {"label": o.get("label") or "pack", "option": o, "feasible": True, "error": None, "notes": [],
         "money_after": money - int(o.get("cost") or 0)}
    if plan.get("error") or base is None or base.get("p_next") is None:
        return dict(r, feasible=False, error=plan.get("error") or "no baseline", p_next=None)
    if r["money_after"] < 0:
        return dict(r, feasible=False, error=f"not affordable (money {r['money_after']})", p_next=None)
    rng = random.Random(f"{seed}:virtual:{r['label']}")
    keys = ("p_next", "p_next_model", "score_ratio", "dollars", "rent_per_round", "rent_horizon", "rent_run", "shop_money")
    cost = int(o.get("cost") or 0)
    dead = 0.0
    acc = dict.fromkeys(keys, 0.0)
    acc_bl = [0.0] * len(base["p_blinds"])
    picks = Counter()
    for _ in range(PACK_VIRTUAL):
        if plan["kind"] == "Buffoon":
            cards = [by_label.get(lab) for lab in rng.sample(plan["draws"], min(plan["size"], len(plan["draws"])))]
        else:
            names = []
            if plan["telescope"]:
                names.append(plan["telescope"])
            while len(names) < min(plan["size"], len(plan["names"])):
                n = rng.choices(plan["names"], weights=plan["weights"])[0]
                if n not in names:
                    names.append(n)
            cards = [by_label.get(f"_pack Celestial: {n}") for n in names]
        cands = [c for c in cards if c is not None and c.get("p_next") is not None] + [base]
        best = max(cands, key=lambda c: (_p_adj(c) - DEAD_SHOP_P * sum(1 for m in c.get("money_path") or []
                                                                      if 0 <= m < cost), c["score_ratio"],
                                         c.get("money_after") or 0))
        dead += sum(1 for m in best.get("money_path") or [] if m - cost < 0)
        picks[best["label"]] += 1
        for k in keys:
            acc[k] += best.get(k) or 0.0
        for i, p in enumerate(best["p_blinds"]):
            acc_bl[i] += p
    for k in keys:
        r[k] = acc[k] / PACK_VIRTUAL
    r["p_blinds"] = [p / PACK_VIRTUAL for p in acc_bl]
    r["money_after_rent"] = r["money_after"] - r["rent_per_round"] * n_blinds
    r["shop_money"] -= cost  # sub-options were simulated with the pack's cost unpaid
    r["dead_shops"] = dead / PACK_VIRTUAL
    subs = [by_label[k] for k in by_label if k.startswith(f"_pack {plan['kind']}:")]
    r["n"] = min([s["n"] for s in subs if s.get("n")] + [base["n"]])
    top = ", ".join(f"{('skip' if lab == base['label'] else lab.split(': ', 1)[1])} {c / PACK_VIRTUAL:.0%}"
                    for lab, c in picks.most_common(4))
    r["notes"] = [f"expected value of the best pick over {PACK_VIRTUAL} virtual packs ({plan['size']} cards) drawn "
                  f"from {len(subs)} simulated {plan['kind']} cards (empirical Gold pool); picks: {top}"]
    if plan["choose"] > 1:
        r["notes"].append(f"choose {plan['choose']}: only the best single pick is counted (lower bound)")
    return r


def value_options(state, options=None, *, budget_s=4.0, blinds=3, estimate_fn=None, seed=0, min_samples=24):
    """Value shop/pack options by P(survive the next `blinds` blinds).

    options: list of dicts (default options_from_state(state)); each may contain
      label: str; cost: $ spent; add_joker: joker dict (shop/pack item); sell: [owned joker indices] or 'weakest';
      levels: [hand names] (+1 level each; '*' = every hand, Black Hole); add_cards: [playing card dicts];
      remove_cards: [deck card ids]; enhance: {deck card id: 'm_glass'...};
      pack: {kind: 'Buffoon'|'Celestial', size, choose} (unopened booster: expected value of its best pick, see
      options_from_state(packs=True)). Keys starting with '_' are the caller's and are ignored.
    A baseline option (no edits) is added first when missing.
    Returns options best first: {label, option, feasible, error, p_next (P(survive all simulated blinds): product
    of the per-blind p_blinds, each mapped by solver.calibrate to the clear rate Gold players achieve), p_next_model /
    p_blinds_model (raw rollout frequencies under the solver's greedy policy; p_next_model is the joint frequency),
    delta (p_next - baseline), score_ratio (mean min(1, scored/need) per blind), dollars (unused hands $ over the
    blinds), money_after, rent_per_round, rent_horizon (rent of every rental over the simulated blinds), rent_run
    (eternal rentals' rent to the end of the run), money_path (expected $ entering each later shop: rent charged,
    blind reward, unused hands, interest), shop_money (its minimum), p_adj (p_next - DOLLAR_P per rent $ -
    DEAD_SHOP_P per later shop entered below $0), delta_adj, n, notes, blinds}. Ranking: p_adj (options within TIE_P
    are tied), then score_ratio, then shop_money.
    Pack options cost extra simulation: up to PACK_REPS jokers per Buffoon and PACK_PLANETS planets per Celestial
    are simulated as hidden sub-options sharing the budget; their p is an upper-biased max over noisy estimates."""
    sv = _solver()
    est = estimate_fn or sv.default_estimate()
    cli = sys.modules.get(getattr(est, "__module__", "") or "")
    bl = upcoming_blinds(state, blinds, getattr(cli, "BLIND_BASE", None))
    if not bl:
        return []
    options = list(options_from_state(state) if options is None else options)
    if not any(_is_base(o) for o in options):
        options.insert(0, {"label": "baseline (no change)"})
    subs, plans = _expand_packs(state, options, seed)
    packs = [(i, o) for i, o in enumerate(options) if o.get("pack")]
    options = [o for o in options if not o.get("pack")] + subs
    t0 = time.perf_counter()
    if any(o.get("sell") == "weakest" for o in options):
        w = _resolve_weakest(sv, est, state, bl, budget_s * 0.25, seed)
        names = {j.get("index"): j.get("name") for j in _lst(state.get("jokers"))}
        options = [dict(o, sell=[w], label=f"{o.get('label')} (sell {names.get(w)})") if o.get("sell") == "weakest" and w
                   else o for o in options if not (o.get("sell") == "weakest" and not w)]
    res = _run(sv, est, state, options, bl, max(0.1, budget_s - (time.perf_counter() - t0)), seed, min_samples)
    base = next((r for r in res if r["feasible"] and _is_base(r["option"])), None)
    if packs:
        by_label = {r["label"].split(" (sell ")[0]: r for r in res if r["label"].startswith("_pack ")}
        res = [r for r in res if not r["label"].startswith("_pack ")]
        money = int(state.get("money") or 0)
        res += [_pack_result(o, plans[i], by_label, base, money, len(bl), seed) for i, o in packs]
    base = next((r for r in res if r["feasible"] and _is_base(r["option"])), None)
    bp = base["p_next"] if base else None
    for r in res:
        r["blinds"] = [f"a{b['ante']} {b['name']} {b['chips']}" for b in bl]
        r["delta"] = (r["p_next"] - bp) if (r.get("p_next") is not None and bp is not None) else None
        r["p_adj"] = _p_adj(r) if r.get("p_next") is not None else None
        r["delta_adj"] = (r["p_adj"] - _p_adj(base)) if (r["p_adj"] is not None and base) else None
    top = max((r["p_adj"] for r in res if r.get("p_adj") is not None), default=0.0)

    def rank(r):
        if r.get("p_adj") is None:
            return (0, 0, 0.0, 0.0, 0)
        tied = r["p_adj"] >= top - TIE_P
        return (1, tied, 1.0 if tied else r["p_adj"], r["score_ratio"], r.get("shop_money", r["money_after"]))

    res.sort(key=rank, reverse=True)
    return res


def _p_adj(r):
    """p_next charged for rent: DOLLAR_P per $ of rent over the horizon (all rentals) and, for eternal rentals,
    per $ of rent for the rest of the run; with a horizon money path that goes negative, the dead shops cost
    another DEAD_SHOP_P each."""
    rent = (r.get("rent_horizon") or 0) + (r.get("rent_run") or 0)
    dead = r["dead_shops"] if "dead_shops" in r else sum(1 for m in r.get("money_path") or [] if m < 0)
    return r["p_next"] - DOLLAR_P * rent - DEAD_SHOP_P * dead
