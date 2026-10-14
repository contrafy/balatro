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
import os
import random
import sys
import time

LEVEL_UP = {"High Card": (10, 1), "Pair": (15, 1), "Two Pair": (20, 1), "Three of a Kind": (20, 2),
            "Straight": (30, 3), "Flush": (15, 2), "Full House": (25, 2), "Four of a Kind": (30, 3),
            "Straight Flush": (40, 4), "Five of a Kind": (35, 3), "Flush House": (40, 4), "Flush Five": (50, 3)}
PLANET_HAND = {"Pluto": "High Card", "Mercury": "Pair", "Uranus": "Two Pair", "Venus": "Three of a Kind",
               "Saturn": "Straight", "Jupiter": "Flush", "Earth": "Full House", "Mars": "Four of a Kind",
               "Neptune": "Straight Flush", "Planet X": "Five of a Kind", "Ceres": "Flush House", "Eris": "Flush Five"}
RENT = 3
TIE_P = 0.02  # p differences below this are sampling noise: ties rank by mean score ratio, then money


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
                    "chips": int(c.get("chips"))})
    if blind_base:
        stake = int(state.get("stake") or 1)
        table = blind_base[3 if stake >= 6 else (2 if stake >= 3 else 1)]
        small = (ch.get("Small") or {}).get("chips")
        k = float(small) / table[ante - 1] if small and 1 <= ante <= len(table) else 1.0
        a = ante
        while len(out) < n and a < len(table):
            a += 1
            base = int(table[a - 1] * k)
            out += [{"ante": a, "kind": "Small", "name": "Small Blind", "boss": False, "chips": base},
                    {"ante": a, "kind": "Big", "name": "Big Blind", "boss": False, "chips": int(base * 1.5)},
                    {"ante": a, "kind": "Boss", "name": "Boss (unknown)", "boss": False, "chips": base * 2}]
    return out[:n]


# ---- options ----------------------------------------------------------------------------------------------------
def _is_joker(item):
    return item.get("set") == "Joker" or str(item.get("key") or "").startswith("j_")


def _is_playing_card(item):
    return item.get("rank") is not None and item.get("suit") is not None


def options_from_state(state):
    """Standard options for the current SHOP or PACK_OPENING state: baseline, every affordable shop joker, shop
    planet, shop playing card, every pack joker/planet/playing card. Jokers that need a slot when the slots are full
    come with sell='weakest' (the owned non-eternal joker whose loss costs the least, found by simulation)."""
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


def _jokers_at(jokers, k, removed):
    """Jokers as they will be at blind k (k round-ends from now): perished ones debuffed, decayed values applied,
    removed ids (Gros Michel died, Mr. Bones used, Seltzer/Popcorn/Ice Cream used up) dropped."""
    out = []
    for i, j in enumerate(jokers):
        if i in removed:
            continue
        ab = dict(j.get("ability") or {})
        j = dict(j, ability=ab)
        n = j.get("name")
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


def _round_state(st, base, blind, k, removed):
    """Synthetic SELECTING_HAND state for a fresh round of `blind` played k round-ends from now."""
    jokers = _lst(st.get("jokers"))
    now = _jokers_at(jokers, k, removed)
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
    return dict(st, phase="SELECTING_HAND", hand=[], jokers=now, money=int(st.get("money") or 0) - RENT * rentals * k,
                hand_size=max(1, int(round(hs))), hands_remaining=max(1, int(hp)), discards_remaining=max(0, int(ds)),
                blind={"name": name, "boss": boss, "chips_needed": blind["chips"], "chips_scored": 0, "disabled": False},
                deck=dict(st.get("deck") or {}, cards=cards, draw_pile=len(cards)))


# ---- simulation ---------------------------------------------------------------------------------------------------
class _OptionSim:
    def __init__(self, sv, est, state, blinds, seed):
        self.sv, self.est, self.state, self.base, self.blinds, self.seed = sv, est, state, None, blinds, seed
        self.solvers = {}
        self.jokers = _lst(state.get("jokers"))
        self.gros = [i for i, j in enumerate(self.jokers) if j.get("name") == "Gros Michel" and _active(j)]
        self.bones = [i for i, j in enumerate(self.jokers) if j.get("name") == "Mr. Bones" and _active(j)]
        self.stats = [[0, 0, 0.0, 0.0] for _ in blinds]  # per blind: n, survived, sum min(1, total/need), $ hands
        self.joint = 0
        self.n = 0
        self.bones_used = 0

    def solver(self, k, removed):
        key = (k, removed)
        rs = self.solvers.get(key)
        if rs is None:
            rs = self.sv.RoundSolver(_round_state(self.state, self.base, self.blinds[k], k, removed), self.est, seed=0)
            self.solvers[key] = rs
        return rs

    def sample(self, s):
        removed = set()
        grng = random.Random(f"{self.seed}:gros:{s}")
        all_ok = True
        for k, blind in enumerate(self.blinds):
            if k:
                for g in self.gros:
                    if g not in removed and grng.random() < 1 / 6:
                        removed.add(g)
            rs = self.solver(k, frozenset(removed))
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
            st = self.stats[k]
            st[0] += 1
            st[2] += min(1.0, tot / max(1.0, rs.need0))
            if ok:
                st[3] += hl
            elif any(b not in removed for b in self.bones) and tot >= 0.25 * rs.need0:
                ok = True
                removed.add(next(b for b in self.bones if b not in removed))
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
    for r, sim in sims:
        n = max(1, sim.n)
        r["n"] = sim.n
        r["p_next"] = sim.joint / n
        r["p_blinds"] = [st[1] / max(1, st[0]) for st in sim.stats]
        r["score_ratio"] = sum(st[2] / max(1, st[0]) for st in sim.stats) / max(1, len(sim.stats))
        r["dollars"] = sum(st[3] / max(1, st[0]) for st in sim.stats)
        if sim.bones_used:
            r["notes"].append(f"Mr. Bones saved {sim.bones_used / n:.2f} blinds per run")
    for r in res:
        r.setdefault("p_next", None)
    return res


def value_options(state, options=None, *, budget_s=4.0, blinds=3, estimate_fn=None, seed=0, min_samples=24):
    """Value shop/pack options by P(survive the next `blinds` blinds).

    options: list of dicts (default options_from_state(state)); each may contain
      label: str; cost: $ spent; add_joker: joker dict (shop/pack item); sell: [owned joker indices] or 'weakest';
      levels: [hand names] (+1 level each; '*' = every hand, Black Hole); add_cards: [playing card dicts];
      remove_cards: [deck card ids]; enhance: {deck card id: 'm_glass'...}.
    A baseline option (no edits) is added first when missing.
    Returns options best first: {label, option, feasible, error, p_next (P(survive all simulated blinds)), p_blinds
    [per blind], delta (p_next - baseline), score_ratio (mean min(1, scored/need) per blind), dollars (unused hands $
    over the blinds), money_after, rent_per_round, money_after_rent, n, notes, blinds}. Ranking: p_next (options
    within TIE_P are tied), then score_ratio, then money_after."""
    sv = _solver()
    est = estimate_fn or sv.default_estimate()
    cli = sys.modules.get(getattr(est, "__module__", "") or "")
    bl = upcoming_blinds(state, blinds, getattr(cli, "BLIND_BASE", None))
    if not bl:
        return []
    options = list(options_from_state(state) if options is None else options)
    if not any(not (set(o) - {"label", "cost"}) and not o.get("cost") for o in options):
        options.insert(0, {"label": "baseline (no change)"})
    t0 = time.perf_counter()
    if any(o.get("sell") == "weakest" for o in options):
        w = _resolve_weakest(sv, est, state, bl, budget_s * 0.25, seed)
        names = {j.get("index"): j.get("name") for j in _lst(state.get("jokers"))}
        options = [dict(o, sell=[w], label=f"{o.get('label')} (sell {names.get(w)})") if o.get("sell") == "weakest" and w
                   else o for o in options if not (o.get("sell") == "weakest" and not w)]
    res = _run(sv, est, state, options, bl, max(0.1, budget_s - (time.perf_counter() - t0)), seed, min_samples)
    base = next((r for r in res if r["feasible"] and not (set(r["option"]) - {"label", "cost"})
                 and not r["option"].get("cost")), None)
    bp = base["p_next"] if base else None
    for r in res:
        r["blinds"] = [f"a{b['ante']} {b['name']} {b['chips']}" for b in bl]
        r["delta"] = (r["p_next"] - bp) if (r.get("p_next") is not None and bp is not None) else None
    top = max((r["p_next"] for r in res if r.get("p_next") is not None), default=0.0)

    def rank(r):
        if r.get("p_next") is None:
            return (0, 0, 0.0, 0.0, 0)
        tied = r["p_next"] >= top - TIE_P
        return (1, tied, 1.0 if tied else r["p_next"], r["score_ratio"], r["money_after"])

    res.sort(key=rank, reverse=True)
    return res
