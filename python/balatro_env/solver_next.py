"""Round solver for SELECTING_HAND: ranks the current play/discard by P(clear the blind this round).

`best_round_plan(state, estimate_fn)` enumerates first actions (the best play of every hand type, with and without
filler cards, "dig" plays of junk when no discard is left, and discards of card subsets pruned by an analytic draw
model), then scores each by Monte-Carlo rollouts over uniformly random orders of the PUBLIC draw-pile composition
(`deck.cards[*].remaining`; the observation's hidden draw order is never read). Later decisions inside a rollout use a
greedy policy: play a hand that clears, otherwise discard toward the keep set with the best analytic draw value
(flush/straight outs, rank improvements, made-hand floor), otherwise chip with the best hand or dig with junk.
Common random numbers (the same sampled orders for every candidate) and successive halving keep it within ~2 s.

Stdlib only and no package-relative imports, so cli.py can load it from a plain script path. estimate_fn is cli.py's
`estimate(hand_name, scoring, held, state, repeat=None, played_n=None)` (returns (score, notes)); any callable with the
first four arguments that returns a score or a (score, ...) tuple works.
"""
from __future__ import annotations

import inspect
import itertools
import math
import random
import time
from functools import lru_cache

SUITS = {"Spades": "S", "Hearts": "H", "Clubs": "C", "Diamonds": "D"}
RANKV = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 11, "Queen": 12,
         "King": 13, "Ace": 14}
SHORT = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"}
CHIPV = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 10, 12: 10, 13: 10, 14: 11}
SUIT_DEBUFF = {"The Club": "C", "The Goad": "S", "The Window": "D", "The Head": "H"}
HELD_JOKERS = {"Shoot the Moon", "Raised Fist", "Baron", "Blackboard"}  # estimate reads the held cards
HD_JOKERS = {"Dusk", "Acrobat", "Banner", "Mystic Summit", "Green Joker", "Ice Cream"}  # estimate reads hands/discards
GROWTH_JOKERS = {"Square Joker", "Runner", "Spare Trousers", "Ride the Bus", "Green Joker", "Supernova", "Hiker",
                 "Wee Joker"}
TIE_P = 0.015  # p_clear differences below this are Monte-Carlo noise: rank those options by secondary value
GROWTH_W = 0.5  # secondary value of one growth-joker trigger, in $ (an unused hand pays $1)
MIN_N = 64  # options within 0.3 of the best p get at least this many samples; fewer are flagged low_n
# Isotonic map of the model p to the realized clear rate of recorded Gold decisions WITH an active joker whose rest of
# the round still holds real decisions (solver_calib: 3452 decisions, 2026-10-14): (model p, realized) knots, linear in
# between. Players beat the greedy later-hand policy there. Jokerless rounds and actions after which the round is
# forced (final hand; a play at 2 hands with 0 discards: only the best final play remains) are calibrated as raw
# (h2/d0 plays: raw mid bins within 0.05, mapped 0.05-0.12 overconfident), so they stay raw.
CALIBRATION = ((0.0, 0.0), (0.0263, 0.1905), (0.1368, 0.3269), (0.2822, 0.4778), (0.4233, 0.5513), (0.5303, 0.6833),
               (0.5948, 0.7167), (0.6623, 0.7391), (0.7796, 0.8756), (0.8544, 0.9079), (0.884, 0.961),
               (0.9206, 0.973), (0.9947, 1.0), (1.0, 1.0))
PILLAR_W = 0.25  # $-equivalent cost per card played when The Pillar is this ante's boss (played cards get debuffed)
LEVEL_UP = {"High Card": (10, 1), "Pair": (15, 1), "Two Pair": (20, 1), "Three of a Kind": (20, 2),
            "Straight": (30, 3), "Flush": (15, 2), "Full House": (25, 2), "Four of a Kind": (30, 3),
            "Straight Flush": (40, 4), "Five of a Kind": (35, 3), "Flush House": (40, 4), "Flush Five": (50, 3)}
PLAY, DISCARD = "PLAY", "DISCARD"


@lru_cache(maxsize=None)
def _comb(n, k):
    return math.comb(n, k) if 0 <= k <= n else 0


@lru_cache(maxsize=None)
def p_none(P, a, n):
    """P(n cards drawn from a pile of P contain none of `a` specific cards)."""
    if n <= 0 or a <= 0:
        return 1.0
    if P - a < n:
        return 0.0
    return _comb(P - a, n) / _comb(P, n)


@lru_cache(maxsize=None)
def p_atleast(P, M, n, k):
    """P(n cards drawn from a pile of P with M successes contain at least k successes)."""
    if k <= 0:
        return 1.0
    n = min(n, P)
    if n < k or M < k:
        return 0.0
    return sum(_comb(M, x) * _comb(P - M, n - x) for x in range(k, min(n, M) + 1)) / _comb(P, n)


@lru_cache(maxsize=None)
def p_each(P, counts, n):
    """P(n draws contain at least one card of every group; counts = group sizes), by inclusion-exclusion."""
    tot = 0.0
    for r in range(len(counts) + 1):
        for sub in itertools.combinations(counts, r):
            tot += (-1) ** r * p_none(P, sum(sub), n)
    return max(0.0, tot)


class Card:
    __slots__ = ("id", "rank", "suit", "suits", "stone", "debuff", "face", "val", "d", "known", "bit")

    def __repr__(self):
        return self.label()

    def label(self):
        if not self.known:
            return "??"
        if self.stone:
            return "Stone"
        return f"{SHORT.get(self.rank, '?')}{self.suit or '?'}"


class _Pile:
    """Public composition of the unseen draw pile at a decision point (never its order)."""
    __slots__ = ("P", "rank_n", "suit_n", "by_rank", "by_suit")

    def __init__(self, cards, suit_keys, P=None):
        cs = sorted(cards, key=lambda c: c.id)
        self.P = len(cs) if P is None else P
        self.rank_n = {}
        self.by_rank = {}
        self.suit_n = dict.fromkeys(suit_keys, 0)
        self.by_suit = {k: [] for k in suit_keys}
        for c in cs:
            if c.rank:
                self.rank_n[c.rank] = self.rank_n.get(c.rank, 0) + 1
                self.by_rank.setdefault(c.rank, []).append(c)
            for k in c.suits:
                self.suit_n[k] += 1
                self.by_suit[k].append(c)


def _lst(v):
    if isinstance(v, dict):
        return list(v.values())
    return v or []


class RoundSolver:
    def __init__(self, state, estimate_fn, *, seed=0):
        self.state = state
        self.seed = seed
        self._est_fn = estimate_fn
        try:
            params = inspect.signature(estimate_fn).parameters
            self._kw = "repeat" in params and "played_n" in params
        except (TypeError, ValueError):
            self._kw = False
        b = state.get("blind") or {}
        self.boss = (b.get("name") or "") if b.get("boss") and not b.get("disabled") else ""
        jn = {j.get("name") for j in _lst(state.get("jokers")) if not j.get("debuff")}
        self.jn = jn
        self.F = 4 if "Four Fingers" in jn else 5
        self.gap = 2 if "Shortcut" in jn else 1
        self.splash = "Splash" in jn
        self.smeared = "Smeared Joker" in jn
        self.pareidolia = "Pareidolia" in jn
        self.card_sharp = "Card Sharp" in jn
        self.growth_j = jn & GROWTH_JOKERS
        active = [j.get("name") for j in _lst(state.get("jokers")) if not j.get("debuff")]
        self.n_misprint = active.count("Misprint")
        self.n_blood = active.count("Bloodstone")
        self.n_space = active.count("Space Joker")
        bs_ = ((state.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}
        self.pillar_ahead = not b.get("boss") and bs_.get("name") == "The Pillar"
        hl0 = state.get("hand_levels") or {}
        self.main_type = max(hl0, key=lambda k: int((hl0[k] or {}).get("played") or 0), default=None)
        self.suit_keys = ("SC", "HD") if self.smeared else ("S", "H", "C", "D")
        self.lim = int(state.get("highlight_limit") or 5)
        self.hand_size = int(state.get("hand_size") or 8)
        self.need0 = float((b.get("chips_needed") or 0) - (b.get("chips_scored") or 0))
        # Mr. Bones: a lost round still counts as survived when at least 25% of the blind was scored
        self.bones_at = 0.25 * float(b.get("chips_needed") or 0) - float(b.get("chips_scored") or 0) \
            if "Mr. Bones" in jn else None
        self.h0 = int(state.get("hands_remaining") or 0)
        self.d0 = int(state.get("discards_remaining") or 0)
        self.psychic = self.boss == "The Psychic"
        self.hook = self.boss == "The Hook"
        self.serpent = self.boss == "The Serpent"
        self.mark = self.boss == "The Mark"
        self.tooth = self.boss == "The Tooth"
        # Mouth/Eye are applied here (the lock and the used types change during a rollout), not inside estimate
        lock = b.get("only_hand") if self.boss == "The Mouth" else None
        used = frozenset(_lst(b.get("hands_used"))) if self.boss == "The Eye" else frozenset()
        rtypes = frozenset(k for k, v in (state.get("hand_levels") or {}).items() if int(v.get("played_this_round") or 0) > 0)
        if self.boss == "The Mouth" and lock is None and len(rtypes) == 1:
            lock = next(iter(rtypes))
        # Obelisk: its xMult and the played counts change with every hand in the round, so they live in ctx
        hl_s = state.get("hand_levels") or {}
        ob_j = next((j for j in _lst(state.get("jokers")) if j.get("name") == "Obelisk" and not j.get("debuff")), None)
        self._ob_extra = float((ob_j or {}).get("ability", {}).get("extra") or 0.2) if ob_j else 0.0
        self._ob_visible = frozenset(k for k, v in hl_s.items() if v.get("visible", True))
        ob0 = None if ob_j is None else (float((ob_j.get("ability") or {}).get("x_mult") or 1),
                                          tuple(sorted((k, int(v.get("played") or 0)) for k, v in hl_s.items())))
        self.ctx0 = (lock, used, rtypes, ob0)
        self._base = dict(state, blind=dict(b, only_hand=None, hands_used=[]))
        self._st = {}
        self._nb = 0  # each Card gets its own bit: card sets are keyed by int masks
        # hand: a Card per position; face-down cards are unknown placeholders resolved per sample
        self.slots = []
        self.slot_index = []
        self.forced = []
        for pos, cd in enumerate(_lst(state.get("hand"))):
            self.slot_index.append(cd.get("index", pos + 1))
            if cd.get("forced"):
                self.forced.append(pos)
            if cd.get("facing") == "back" or (cd.get("id") is None and cd.get("rank") is None):
                self.slots.append(None)
            else:
                self.slots.append(self._mk(cd, cd.get("index", pos + 1), from_deck=False))
        self.fd_pos = [i for i, c in enumerate(self.slots) if c is None]
        self.unknown = {}
        for p in self.fd_pos:
            u = Card()
            u.id, u.rank, u.suit, u.suits, u.stone, u.debuff, u.face, u.val, u.d, u.known = \
                -1 - p, 0, "", frozenset(), False, False, False, 0, {}, False
            u.bit = 1 << self._nb
            self._nb += 1
            self.unknown[p] = u
        # unseen pool: remaining-flagged deck cards = draw pile + face-down cards in hand
        dk = state.get("deck") or {}
        hand_ids = {c.id for c in self.slots if c is not None}
        self.pool = [self._mk(cd, 100 + int(cd.get("id") or 0), from_deck=True)
                     for cd in _lst(dk.get("cards")) if cd.get("remaining") and cd.get("id") not in hand_ids]
        dp = dk.get("draw_pile")
        n_pile = len(self.pool) - len(self.fd_pos)
        self.pile_n = max(0, min(n_pile, int(dp)) if dp is not None else n_pile)
        steel = any("steel" in str(c.d.get("enhancement") or "").lower() for c in self.pool + [c for c in self.slots if c])
        self.held_dep = bool(jn & HELD_JOKERS) or steel
        self.hd_dep = bool(jn & HD_JOKERS)
        self.final_dep = bool(jn & {"Dusk", "Acrobat"})  # final-hand jokers: holding a hand for the last play pays
        self.keep_discards = bool(jn & {"Banner", "Green Joker"})  # discards tax every later hand
        # scoring order matters (and the player can set it with `move hand`): first-card retrigger / first-face xMult,
        # or x-mult cards (Glass, polychrome) that should score after the additive ones
        xcards = any(self._xmult_card(c.d) for c in self.pool + [c for c in self.slots if c])
        self.order_dep = bool(jn & {"Hanging Chad", "Photograph"}) or xcards
        lucky = any("lucky" in str(c.d.get("enhancement") or "").lower() for c in self.pool + [c for c in self.slots if c])
        self.jokerless = not jn  # calibration segment: no active joker
        self.random_fx = bool(self.n_misprint or self.n_blood or self.n_space or lucky)
        # The Pillar: cards played earlier this ante are debuffed; obs flags them in hand but not in deck.cards, so
        # each sample debuffs a random share of the draw pile equal to the debuffed share of the visible hand
        self.pillar_frac = 0.0
        self.pool_deb = []
        if self.boss == "The Pillar":
            vis = [c for c in self.slots if c is not None]
            self.pillar_frac = sum(1 for c in vis if c.debuff) / max(1, len(vis))
            for c in self.pool:
                t = self._mk(c.d, c.d.get("index"), from_deck=False)
                t.debuff, t.val, t.d = True, c.val - 100, dict(c.d, debuff=True)
                t.suits = frozenset((self._group(c.suit),)) if c.suit else frozenset()
                self.pool_deb.append(t)
        self._score_memo = {}
        self._cls_memo = {}
        self._samples = []
        self._bp_memo = {}
        self._win_memo = {}

    # ---- cards ---------------------------------------------------------------------------------------------------
    def _group(self, s):
        if self.smeared:
            return "SC" if s in ("S", "C") else "HD" if s in ("H", "D") else ""
        return s

    def _mk(self, cd, index, from_deck):
        c = Card()
        c.known = True
        c.bit = 1 << self._nb
        self._nb += 1
        c.id = cd.get("id")
        enh = str(cd.get("enhancement") or "").lower()
        c.stone = "stone" in enh
        wild = "wild" in enh
        c.rank = 0 if c.stone else RANKV.get(str(cd.get("rank")), 0)
        c.suit = "" if c.stone else SUITS.get(cd.get("suit"), "")
        c.face = c.rank in (11, 12, 13) or (self.pareidolia and c.rank > 0)
        if from_deck:
            deb = self.boss == "Verdant Leaf"
            if self.boss in SUIT_DEBUFF and not c.stone:
                deb = wild or self._group(c.suit) == self._group(SUIT_DEBUFF[self.boss])
            if self.boss == "The Plant" and c.face:
                deb = True
        else:
            deb = bool(cd.get("debuff"))
        c.debuff = deb
        if c.stone:
            c.suits = frozenset()
        elif wild and not deb:
            c.suits = frozenset(self.suit_keys)
        else:
            g = self._group(c.suit)
            c.suits = frozenset((g,)) if g else frozenset()
        v = 50 if c.stone else CHIPV.get(c.rank, 0)
        v += float(cd.get("perma_bonus") or 0)
        v += 30 * ("bonus" in enh) + 25 * ("mult" in enh) + 60 * ("glass" in enh) + 40 * ("steel" in enh) \
            + 20 * ("lucky" in enh) + 15 * wild
        ed = cd.get("edition")
        v += {"foil": 50, "holo": 40, "polychrome": 70}.get(ed, 0) if isinstance(ed, str) else 0
        v += 15 if cd.get("seal") else 0
        c.val = v - (100 if deb else 0)
        c.d = dict(cd, index=index, debuff=deb)
        return c

    # ---- poker hand evaluation (vanilla evaluate_poker_hand order) ---------------------------------------------
    def _chain(self, ranked, need_len):
        """Highest run of distinct ranks (Ace high or low, Shortcut gaps) of length >= need_len; rank values."""
        present = {c.rank for c in ranked}
        if 14 in present:
            present.add(1)
        best, chain = None, []
        for v in sorted(present):
            if chain and v - chain[-1] <= self.gap:
                chain.append(v)
            else:
                if len(chain) >= need_len:
                    best = chain
                chain = [v]
        if len(chain) >= need_len:
            best = chain
        return best

    def classify(self, played):
        """(hand type, scoring cards) the game reads from these played cards."""
        key = 0
        for c in played:
            key |= c.bit
        r = self._cls_memo.get(key)
        if r is not None:
            return r
        ranked = [c for c in played if c.rank]
        F = self.F
        groups = {}
        for c in ranked:
            groups.setdefault(c.rank, []).append(c)
        flush = None
        straight = None
        if len(ranked) >= F:
            for k in self.suit_keys:
                fc = [c for c in ranked if k in c.suits]
                if len(fc) >= F:
                    flush = fc
                    break
            ch = self._chain(ranked, F)
            if ch:
                vs = {14 if v == 1 else v for v in ch}
                straight = [c for c in ranked if c.rank in vs]
        gs = sorted(groups.values(), key=lambda g: (-len(g), -g[0].rank))
        top = len(gs[0]) if gs else 0
        sec = len(gs[1]) if len(gs) > 1 else 0
        if top >= 5 and flush:
            t, sc = "Flush Five", gs[0]
        elif top == 3 and sec >= 2 and flush:
            t, sc = "Flush House", gs[0] + gs[1]
        elif top >= 5:
            t, sc = "Five of a Kind", gs[0]
        elif flush and straight:
            t, sc = "Straight Flush", list({id(c): c for c in flush + straight}.values())
        elif top == 4:
            t, sc = "Four of a Kind", gs[0]
        elif top == 3 and sec >= 2:
            t, sc = "Full House", gs[0] + gs[1]
        elif flush:
            t, sc = "Flush", flush
        elif straight:
            t, sc = "Straight", straight
        elif top == 3:
            t, sc = "Three of a Kind", gs[0]
        elif top == 2 and sec == 2:
            t, sc = "Two Pair", gs[0] + gs[1]
        elif top == 2:
            t, sc = "Pair", gs[0]
        else:
            t, sc = "High Card", ([max(ranked, key=lambda c: c.rank)] if ranked else [])
        if self.splash:
            sc = list(played)
        else:
            sc = sc + [c for c in played if c.stone and c not in sc]
        m = 0
        for c in sc:
            m |= c.bit
        r = (t, sc, m)
        self._cls_memo[key] = r
        return r

    # ---- scoring ------------------------------------------------------------------------------------------------
    def _state(self, h, d, ob=None):
        """State at hands_remaining=h, discards_remaining=d of this round: Green Joker has gained +1 mult per hand
        played and lost 1 per discard since the decision; Ice Cream has lost 5 chips per hand played; with an Obelisk
        state ob = (x_mult, played counts) the Obelisk and hand_levels.played are set from it."""
        st = self._st.get((h, d, ob))
        if st is None:
            st = dict(self._base, hands_remaining=h, discards_remaining=d)
            played, disc = self.h0 - h, self.d0 - d
            if ((played or disc) and self.jn & {"Green Joker", "Ice Cream"}) or ob is not None:
                js = []
                for j in _lst(self._base.get("jokers")):
                    ab = j.get("ability") or {}
                    if j.get("name") == "Green Joker" and not j.get("debuff"):
                        j = dict(j, ability=dict(ab, mult=max(0.0, float(ab.get("mult") or 0) + played - disc)))
                    elif j.get("name") == "Ice Cream" and isinstance(ab.get("extra"), dict) and not j.get("debuff"):
                        ex = ab["extra"]
                        j = dict(j, ability=dict(ab, extra=dict(ex, chips=max(0.0, float(ex.get("chips") or 0)
                                                                              - float(ex.get("chip_mod") or 5) * played))))
                    elif j.get("name") == "Obelisk" and ob is not None and not j.get("debuff"):
                        j = dict(j, ability=dict(ab, x_mult=ob[0]))
                    js.append(j)
                st["jokers"] = js
            if ob is not None:
                counts = dict(ob[1])
                st["hand_levels"] = {k: dict(v, played=counts.get(k, 0))
                                     for k, v in (self._base.get("hand_levels") or {}).items()}
            self._st[(h, d, ob)] = st
        return st

    def _obelisk_after(self, ob, t):
        """Obelisk state after playing type t (card.lua): reset to x1 when t is now strictly the most played visible
        type, otherwise +extra."""
        if ob is None:
            return None
        counts = dict(ob[1])
        p = counts.get(t, 0) + 1
        other_more = any(k != t and k in self._ob_visible and c >= p for k, c in counts.items())
        counts[t] = p
        return (ob[0] + self._ob_extra) if other_more else 1.0, tuple(sorted(counts.items()))

    def _est_raw(self, t, scd, hd, st, rep, n):
        if self._kw:
            r = self._est_fn(t, scd, hd, st, repeat=rep, played_n=n)
        else:
            r = self._est_fn(t, scd, hd, st)
        return float(r[0] if isinstance(r, tuple) else r)

    @staticmethod
    def _xmult_card(c):
        """A scoring card that multiplies mult (Glass, polychrome): scored after the additive cards."""
        return "glass" in str(c.get("enhancement") or "").lower() or c.get("edition") == "polychrome"

    def _orders(self, scd):
        """Scoring orders the player can set with `move hand`: each card in turn first (Hanging Chad retriggers it,
        Photograph doubles the first face), the rest additive cards first and x-mult cards last."""
        if not self.order_dep or len(scd) < 2:
            return [scd]
        slots = sorted(c.get("index") or 0 for c in scd)
        out = []
        for f in range(len(scd)):
            rest = sorted((c for i, c in enumerate(scd) if i != f), key=self._xmult_card)
            out.append([dict(c, index=ix) for c, ix in zip([scd[f]] + rest, slots)])
        return out

    def _est(self, t, scd, hd, st, rep, n):
        """estimate of the play in its best scoring order (estimate scores cards in index order)."""
        return max(self._est_raw(t, o, hd, st, rep, n) for o in self._orders(scd))

    def best_first(self, play, held=()):
        """Hand index of the card to move leftmost so the play scores its best (None when order does not matter)."""
        if not self.order_dep:
            return None
        t, sc, _m = self.classify(play)
        scd = [c.d for c in sc]
        st = self._state(self.h0, self.d0, self.ctx0[3])
        hd = [c.d for c in held if c.known]
        orders = self._orders(scd)
        vals = [self._est_raw(t, o, hd, st, None, len(play)) for o in orders]
        if max(vals) - min(vals) < 1:
            return None
        best = orders[vals.index(max(vals))][0]
        return next((c.d.get("index") for c in sc if c.d.get("id") == best.get("id")), None)

    def _first_for(self, cand):
        """best_first for a PLAY candidate of known cards (hand index), else None."""
        if cand["kind"] != PLAY or not self.order_dep:
            return None
        play = [self.slots[p] for p in cand["pos"]]
        if any(c is None for c in play):
            return None
        held = [c for c in self.slots if c is not None and c not in play]
        return self.best_first(play, held)

    def _components(self, t, sc, played, held, h, d, rep, ob=None):
        """Score of a play split into its random parts (estimate itself is deterministic):
        (base with every Misprint at 0, score per Misprint mult point, Misprint count, score per Lucky +20 hit,
        Lucky triggers, Bloodstone x1.5 chances, score of a Space Joker level-up, Space Joker count)."""
        st = self._state(h, d, ob)
        scd = [c.d for c in sc]
        hd = [c.d for c in held if c.known]
        n = max(5, len(played)) if self.psychic else len(played)  # The Psychic: every real play is 5 cards
        s6 = self._est(t, scd, hd, st, rep, n)  # estimate counts each Misprint as +6
        base, slope = s6, 0.0
        if self.n_misprint:
            st0 = dict(st, jokers=[dict(j, name="_misprint_zero") if j.get("name") == "Misprint" else j
                                   for j in _lst(st.get("jokers"))])
            base = self._est(t, scd, hd, st0, rep, n)
            slope = (s6 - base) / (6.0 * self.n_misprint)
        lucky = [c for c in sc if "lucky" in str(c.d.get("enhancement") or "").lower() and not c.debuff] \
            if "Vampire" not in self.jn else []
        lucky_inc = 0.0
        if lucky:
            first = lucky[0]
            scd2 = [dict(c.d, perma_mult=float(c.d.get("perma_mult") or 0) + 20) if c is first else c.d for c in sc]
            lucky_inc = self._est(t, scd2, hd, st, rep, n) - s6
        # Bloodstone: x1.5 in the card phase of each scoring Heart (1 in 2), not on the final score. estimate leaves it
        # out, so score k triggered Hearts by giving them a card-phase x1.5 (a polychrome edition) and keep the
        # ratios to the untriggered score
        blood = ()
        if self.n_blood and s6 > 0:
            hearts = [i for i, c in enumerate(sc) if not c.debuff and ("H" in c.suits or "HD" in c.suits)
                      and c.d.get("edition") != "polychrome"]
            ratios = [1.0]
            for k in range(1, len(hearts) + 1):
                trig = set(hearts[:k])
                scd_k = [dict(c.d, edition="polychrome") if i in trig else c.d for i, c in enumerate(sc)]
                ratios.append(self._est(t, scd_k, hd, st, rep, n) / s6)
            blood = tuple(ratios)
        space = 0.0
        if self.n_space:
            hl = dict(st.get("hand_levels") or {})
            v = dict(hl.get(t) or {})
            c_up, m_up = LEVEL_UP.get(t, (0, 0))
            v["chips"] = float(v.get("chips") or 0) + c_up
            v["mult"] = float(v.get("mult") or 1) + m_up
            v["level"] = int(v.get("level") or 1) + 1
            hl[t] = v
            space = self._est(t, scd, hd, dict(st, hand_levels=hl), rep, n) - s6
        return base, slope, self.n_misprint, lucky_inc, len(lucky), blood, space, self.n_space

    def score(self, played, held, h, d, ctx, rng=None):
        """(score, hand type) of playing `played` while `held` stays in hand. Without rng: the planning value with
        random jokers/cards at their expectation (Misprint +11.5, Lucky 1/5 x +20 mult, Bloodstone 1/2 x1.5 per
        Heart, Space Joker 1/4 level-up); with rng: one sampled outcome (how the hand actually scores)."""
        if not played:
            return 0.0, "High Card"
        t, sc, scm = self.classify(played)
        lock, used, rtypes, ob = ctx
        if (lock and t != lock) or t in used:
            return 0.0, t
        if self.psychic and len(played) < 5 and len(played) + len(held) >= 5:
            return 0.0, t
        rep = (t in rtypes) if self.card_sharp else None
        if self.held_dep:
            hm = 0
            for c in held:
                hm |= c.bit
        else:
            hm = 0
        key = (t, scm, len(played), hm, (h, d) if self.hd_dep else None, rep, ob)
        comp = self._score_memo.get(key)
        if comp is None:
            comp = self._components(t, sc, played, held, h, d, rep, ob)
            if not self.random_fx:
                comp = comp[0]
            self._score_memo[key] = comp
        if not self.random_fx:
            return comp, t
        base, slope, n_mis, lucky_inc, n_lucky, blood, space, n_space = comp
        q = 1.0 - 0.5 ** self.n_blood  # a Heart triggers at least one Bloodstone
        if rng is None:
            rb = 1.0
            if len(blood) > 1:
                hn = len(blood) - 1
                rb = sum(math.comb(hn, k) * q ** k * (1 - q) ** (hn - k) * r for k, r in enumerate(blood))
            return (base + slope * 11.5 * n_mis + 0.2 * n_lucky * lucky_inc + 0.25 * n_space * space) * rb, t
        m = sum(rng.randint(0, 23) for _ in range(n_mis))
        hits = sum(rng.random() < 0.2 for _ in range(n_lucky))
        k = sum(rng.random() < q for _ in range(len(blood) - 1)) if len(blood) > 1 else 0
        up = sum(rng.random() < 0.25 for _ in range(n_space))
        return (base + slope * m + hits * lucky_inc + up * space) * (blood[k] if blood else 1.0), t

    def _gen_plays(self, cards):
        """Candidate plays: every rank group and its 2..5 subsets, two pairs, full houses, the best flush per suit
        (and straight flush), the highest straight, the best single cards; Stone fillers; Psychic pads to 5."""
        ranked = [c for c in cards if c.rank]
        stones = [c for c in cards if c.stone]
        if not ranked and not stones:
            return []
        groups = {}
        for c in sorted(ranked, key=lambda c: -c.val):
            groups.setdefault(c.rank, []).append(c)
        plays = []
        lim = self.lim
        if ranked:
            hi = max(ranked, key=lambda c: (c.rank, c.val))
            plays.append([hi])
            hv = max(ranked, key=lambda c: c.val)
            if hv is not hi:
                plays.append([hv])
        multi = sorted((r for r, g in groups.items() if len(g) >= 2), reverse=True)
        for r in multi:
            g = groups[r]
            for n in range(2, min(len(g), lim) + 1):
                plays.append(g[:n])
        for a, b in itertools.combinations(multi[:4], 2):
            plays.append(groups[a][:2] + groups[b][:2])
        for t in multi:
            if len(groups[t]) >= 3:
                for p in multi:
                    if p != t:
                        plays.append(groups[t][:3] + groups[p][:2])
        for k in self.suit_keys:
            fc = sorted((c for c in ranked if k in c.suits), key=lambda c: -c.val)
            if len(fc) >= self.F:
                plays.append(fc[:lim])
                st = self._straight_pick(fc)
                if st:
                    plays.append(st)
        st = self._straight_pick(ranked)
        if st:
            plays.append(st)
        if stones and not self.tooth:
            stones.sort(key=lambda c: -c.val)
            plays = plays + [p + stones[:lim - len(p)] for p in plays if len(p) < lim]
            plays.append(stones[:lim])
        if self.psychic:
            plays = [self._pad(p, cards, 5) for p in plays]
        return plays

    def _straight_pick(self, ranked):
        ch = self._chain(ranked, self.F)
        if not ch:
            return None
        best = {}
        for c in ranked:
            if c.rank not in best or c.val > best[c.rank].val:
                best[c.rank] = c
        out = []
        for v in ch[-self.lim:]:
            c = best[14 if v == 1 else v]
            if c not in out:
                out.append(c)
        return out

    def _pad(self, play, cards, n, avoid=()):
        if len(play) >= n:
            return play
        ids = {id(c) for c in play}
        rest = sorted((c for c in cards if id(c) not in ids), key=lambda c: (id(c) in avoid, c.val))
        return play + rest[:n - len(play)]

    def best_play(self, cards, h, d, ctx):
        """(score, play cards, type) of the highest-scoring candidate play in `cards` (memoized on the card set)."""
        m = 0
        for c in cards:
            m |= c.bit
        mk = (m, h, d, ctx) if (self.hd_dep or self.psychic) else (m, ctx)
        r = self._bp_memo.get(mk)
        if r is not None:
            return r
        best = (-1.0, None, None)
        for p in self._gen_plays(cards):
            ids = {id(c) for c in p}
            s, t = self.score(p, [c for c in cards if id(c) not in ids], h, d, ctx)
            if s > best[0]:
                best = (s, p, t)
        if best[1] is None:
            p = sorted(cards, key=lambda c: c.val)[:1]
            best = (0.0, p, "High Card")
        self._bp_memo[mk] = best
        return best

    # ---- analytic draw model ------------------------------------------------------------------------------------
    def keep_value(self, keep, pile, need, h, d, ctx, n_draw):
        """Heuristic value of keeping `keep` and drawing n_draw cards: max over draw targets of
        p*min(target, need) + (1-p)*min(made, need). Returns (value, label)."""
        if keep:
            made, _mp, mt = self.best_play(keep, h, d, ctx)
        else:
            made, mt = 0.0, None
        base = min(made, need)
        best = (base, ("made", mt, int(made)) if mt else ("redraw",))
        n = min(n_draw, pile.P)
        if n <= 0:
            return best
        P = pile.P
        ranked = [c for c in keep if c.rank]
        F = self.F
        # flush
        cnt = {}
        rmask = 0
        for c in ranked:
            rmask |= 1 << c.rank
            for k in c.suits:
                cnt[k] = cnt.get(k, 0) + 1
        for k, m in cnt.items():
            miss = F - m
            if m >= 2 and 1 <= miss <= n:
                p = p_atleast(P, pile.suit_n[k], n, miss)
                if p > 0.005:
                    sc = sorted((c for c in ranked if k in c.suits), key=lambda c: -c.val)
                    v, _t = self.score(sc[:F] + pile.by_suit[k][:miss], [], h, d, ctx)
                    u = p * min(v, need) + (1 - p) * base
                    if u > best[0]:
                        best = (u, ("flush", m, F, p))
        # straight (Shortcut gaps are not modeled for draws; made Shortcut straights are)
        one_miss, multi = self._windows(rmask, min(n, 2))
        sp, slabel, srep = 0.0, None, ()
        if one_miss:
            a = sum(pile.rank_n.get(r, 0) for r in one_miss)
            sp = 1 - p_none(P, a, n)
            slabel = ("straight1", a, one_miss)
            srep = (max(one_miss, key=lambda r: pile.rank_n.get(r, 0)),)
        for miss in multi:
            p = p_each(P, tuple(sorted(pile.rank_n.get(r, 0) for r in miss)), n)
            if p > sp:
                sp, slabel, srep = p, ("straight2", miss), miss
        if sp > 0.005:
            reps = [pile.by_rank[r][0] for r in srep if pile.by_rank.get(r)]
            bestc = {}
            for c in ranked:
                if c.rank not in bestc or c.val > bestc[c.rank].val:
                    bestc[c.rank] = c
            cards = list(bestc.values()) + reps
            v = self.best_play(cards, h, d, ctx)[0]
            u = sp * min(v, need) + (1 - sp) * base
            if u > best[0]:
                best = (u, slabel + (sp,))
        # rank improvements
        groups = {}
        for c in ranked:
            groups.setdefault(c.rank, []).append(c)
        pairs = sorted((r for r, g in groups.items() if len(g) >= 2), key=lambda r: (-len(groups[r]), -r))
        singles = sorted((r for r, g in groups.items() if len(g) == 1), reverse=True)

        def consider(p, play, label):
            nonlocal best
            v, _t = self.score(play, [], h, d, ctx)
            u = p * min(v, need) + (1 - p) * base
            if u > best[0]:
                best = (u, label + (p,))

        if pairs:
            r = pairs[0]
            if pile.rank_n.get(r, 0):
                consider(1 - p_none(P, pile.rank_n[r], n), groups[r] + pile.by_rank[r][:1], ("set", r))
            if len(pairs) >= 2:
                r2 = pairs[1]
                a = pile.rank_n.get(r, 0) + pile.rank_n.get(r2, 0)
                if a:
                    rr = r if pile.rank_n.get(r, 0) else r2
                    consider(1 - p_none(P, a, n), groups[r][:2] + groups[r2][:2] + pile.by_rank[rr][:1], ("fh",))
            elif singles:
                s0 = next((s for s in singles if pile.rank_n.get(s, 0)), None)
                if s0:
                    a = sum(pile.rank_n.get(s, 0) for s in singles)
                    consider(1 - p_none(P, a, n), groups[r][:2] + groups[s0] + pile.by_rank[s0][:1], ("twopair",))
        elif singles:
            s0 = next((s for s in singles if pile.rank_n.get(s, 0)), None)
            if s0:
                a = sum(pile.rank_n.get(s, 0) for s in singles)
                consider(1 - p_none(P, a, n), groups[s0] + pile.by_rank[s0][:1], ("pair",))
        return best

    def _windows(self, rmask, max_miss):
        """Straight windows reachable from a rank bitmask (bit r = rank r held): (ranks completing a one-gap window,
        list of missing-rank tuples for windows missing 2..max_miss)."""
        key = (rmask, max_miss)
        r = self._win_memo.get(key)
        if r is not None:
            return r
        F = self.F
        present = {v for v in range(2, 15) if rmask >> v & 1}
        if 14 in present:
            present.add(1)
        one, multi = set(), []
        for lo in range(1, 16 - F):
            miss = tuple(14 if v == 1 else v for v in range(lo, lo + F) if v not in present)
            m = len(miss)
            if m == 0 or m > max_miss or F - m < 2:
                continue
            if m == 1:
                one.add(miss[0])
            else:
                multi.append(miss)
        r = self._win_memo[key] = (frozenset(one), multi)
        return r

    @staticmethod
    def label(lab):
        """Readable text of a keep_value label tuple."""
        k = lab[0]
        if k == "made":
            return f"made {lab[1]} {lab[2]}"
        if k == "redraw":
            return "full redraw"
        if k == "flush":
            return f"flush draw {lab[1]}/{lab[2]}, p={lab[3]:.2f}"
        if k == "straight1":
            return f"straight draw, {lab[1]} outs ({'/'.join(SHORT[r] for r in sorted(lab[2]))}), p={lab[3]:.2f}"
        if k == "straight2":
            return f"straight draw needs {'+'.join(SHORT[r] for r in lab[1])}, p={lab[2]:.2f}"
        if k == "set":
            return f"set draw {SHORT[lab[1]]}, p={lab[2]:.2f}"
        return {"fh": "full house draw", "twopair": "two pair draw", "pair": "pair draw"}[k] + f", p={lab[1]:.2f}"

    def _n_draw(self, n_keep, pile_P):
        n = 3 if self.serpent else self.hand_size - n_keep
        return max(0, min(n, pile_P))

    def _keep_sets(self, cards, bp):
        """Structural keep sets (frozensets of positions): best play, rank groups, each suit, straight windows (and
        open-ended pairs of windows), top cards, each also united with the best play; each throws 1..lim cards."""
        n = len(cards)
        ranked = [i for i in range(n) if cards[i].rank]
        bpi = {id(x) for x in (bp or ())}
        B = frozenset(i for i in range(n) if id(cards[i]) in bpi)
        raw = [B, frozenset()]
        groups = {}
        for i in ranked:
            groups.setdefault(cards[i].rank, []).append(i)
        pr = [g for g in groups.values() if len(g) >= 2]
        if pr:
            raw.append(frozenset(itertools.chain.from_iterable(pr)))
            raw.append(frozenset(max(pr, key=lambda g: (len(g), cards[g[0]].rank))))
        for k in self.suit_keys:
            sc = sorted((i for i in ranked if k in cards[i].suits), key=lambda i: -cards[i].val)
            if len(sc) >= 2:
                raw.append(frozenset(sc[:5]))
                raw.append(frozenset(sc[:5]) | B)
        best_by_rank = {}
        for i in ranked:
            r = cards[i].rank
            if r not in best_by_rank or cards[i].val > cards[best_by_rank[r]].val:
                best_by_rank[r] = i
        F = self.F
        for lo in range(1, 16 - F):
            win = [14 if r == 1 else r for r in range(lo, lo + F)]
            have = [best_by_rank[r] for r in win if r in best_by_rank]
            if len(have) >= max(2, F - 3):
                raw.append(frozenset(have))
                raw.append(frozenset(have) | B)
                if lo + F <= 14 and lo + F in best_by_rank:
                    raw.append(frozenset(have + [best_by_rank[lo + F]]))
        byr = sorted(ranked, key=lambda i: (-cards[i].rank, -cards[i].val))
        raw += [frozenset(byr[:1]), frozenset(byr[:2]), frozenset(byr[:3])]
        return self._normalize(cards, raw)

    def _normalize(self, cards, raw):
        n = len(cards)
        out = []
        seen = set()
        for K in raw:
            throw = [i for i in range(n) if i not in K]
            if not throw:
                continue
            if len(throw) > self.lim:
                throw = sorted(throw, key=lambda i: cards[i].val)[:self.lim]
                K = frozenset(i for i in range(n) if i not in throw)
            if K in seen:
                continue
            seen.add(K)
            out.append(K)
        return out

    # ---- rollout policy ---------------------------------------------------------------------------------------
    def _fillers(self, play, cards, keep, h, d, ctx, base_score):
        """Add up to lim-len(play) junk cards (outside keep) to a play when that does not lower its score."""
        room = self.lim - len(play)
        if room <= 0:
            return play
        pids = {id(c) for c in play}
        junk = sorted((c for i, c in enumerate(cards) if i not in keep and id(c) not in pids), key=lambda c: c.val)[:room]
        while junk:
            cand = play + junk
            cids = {id(c) for c in cand}
            s, _t = self.score(cand, [c for c in cards if id(c) not in cids], h, d, ctx)
            if s >= base_score:
                return cand
            junk = junk[:-1]
        return play

    def _hold(self, cards, h, d, ctx):
        """Hold line for final-hand jokers: (total = final-hand est + (h-1) single-card throwaways, best throwaway card,
        final est, final play, its type); None without a junk card."""
        fs, fp, ft = self.best_play(cards, 1, d, ctx)
        fids = {id(c) for c in fp}
        junk = [c for c in cards if id(c) not in fids]
        if not junk:
            return None
        best_j, best_s = None, -1.0
        for c in junk:
            s, _t = self.score([c], [x for x in cards if x is not c], h, d, ctx)
            if s > best_s:
                best_j, best_s = c, s
        return fs + best_s * (h - 1), best_j, fs, fp, ft

    def policy(self, cards, pile_cards, h, d, need, ctx):
        """Greedy later-hand policy; returns (kind, list of card objects)."""
        bs, bp, _bt = self.best_play(cards, h, d, ctx)
        if bs >= need or (h <= 1 and d <= 0) or not pile_cards:
            return PLAY, (self._pad(bp, cards, 5) if self.psychic else bp)
        if self.final_dep and h >= 2 and not self.psychic:
            # Acrobat/Dusk/...: hold a hand that clears as the final hand; burn the hands before it with 1 junk card
            hold = self._hold(cards, h, d, ctx)
            if hold and hold[0] >= need:
                return PLAY, [hold[1]]
        if self.keep_discards and d > 0 and h >= 2 and bs * h >= need:
            # Banner (+30 chips per remaining discard) / Green Joker (-1 mult per discard): every discard taxes all
            # later hands, so play the best hand while it keeps pace instead of digging
            if self.psychic:
                return PLAY, self._pad(bp, cards, 5)
            return PLAY, (bp if self.pillar_ahead else self._fillers(bp, cards, frozenset(), h, d, ctx, bs))
        pile = _Pile(pile_cards, self.suit_keys)
        scored = []
        for K in self._keep_sets(cards, bp):
            u, _l = self.keep_value([cards[i] for i in K], pile, need, h, d, ctx, self._n_draw(len(K), pile.P))
            scored.append((u, K))
        scored.sort(key=lambda t: -t[0])
        keep = scored[0][1] if scored else frozenset()
        if d > 0 and scored:
            return DISCARD, [c for i, c in enumerate(cards) if i not in keep]
        if self.psychic:
            if scored and bs * h < need and scored[0][0] > bs:
                return PLAY, self._pad([c for i, c in enumerate(cards) if i not in keep][:5], cards, 5)
            return PLAY, self._pad(bp, cards, 5, avoid={id(cards[i]) for i in keep})
        if self.pillar_ahead:  # every played card is debuffed at The Pillar: no fillers, no junk digs
            return PLAY, bp
        # no discard left, 2+ hands: choose the play maximizing score now + draw value of the cards that stay
        # (best hand + fillers, or the best hand among the cards outside each top keep set + junk fillers)
        plays = [self._fillers(bp, cards, keep, h, d, ctx, bs)]
        for _u, K in scored[:6]:
            rest = [c for i, c in enumerate(cards) if i not in K]
            if not rest:
                continue
            _s, p, _t = self.best_play(rest, h, d, ctx)
            if not p:
                continue
            pids = {id(c) for c in p}
            plays.append(p + sorted((c for c in rest if id(c) not in pids), key=lambda c: c.val)[:self.lim - len(p)])
        best, best_tot = plays[0], -1.0
        for p in plays:
            ids = {id(c) for c in p}
            held = [c for c in cards if id(c) not in ids]
            s, _t = self.score(p, held, h, d, ctx)
            if s >= need:
                return PLAY, p
            u2, _l = self.keep_value(held, pile, need - s, h - 1, d, ctx, self._n_draw(len(held), pile.P))
            if s + u2 > best_tot:
                best, best_tot = p, s + u2
        return PLAY, best

    def _growth(self, sel, t):
        """Growth-joker progress of one played hand: +1 per trigger of Square Joker (4 cards), Runner (Straight),
        Spare Trousers (Two Pair), Ride the Bus (no scoring face; a face resets it: -1), Green Joker (+1 per hand),
        Supernova (playing the most played type), Hiker (+1 per scoring card), Wee Joker (+1 per scoring 2)."""
        g = 0.0
        gj = self.growth_j
        if "Square Joker" in gj and len(sel) == 4:
            g += 1
        if "Runner" in gj and t in ("Straight", "Straight Flush"):
            g += 1
        if "Spare Trousers" in gj and t in ("Two Pair", "Full House", "Flush House"):
            g += 1
        if "Green Joker" in gj:
            g += 1
        if "Supernova" in gj and t == self.main_type:
            g += 1
        if gj & {"Ride the Bus", "Hiker", "Wee Joker"}:
            sc = [c for c in self.classify(sel)[1] if not c.debuff]
            if "Ride the Bus" in gj:
                g += -1 if any(c.face for c in sc) else 1
            if "Hiker" in gj:
                g += len(sc)
            if "Wee Joker" in gj:
                g += sum(1 for c in sc if c.rank == 2)
        return g

    def rollout(self, first, hand, order, rng):
        """Play the round from the current decision: first = (kind, positions) in `hand`; later decisions by policy.
        Each played hand's random jokers/cards are sampled from rng. Returns (cleared, total scored, hands left,
        discards used, growth-joker progress, cards played)."""
        h, d, need = self.h0, self.d0, self.need0
        lock, used, rtypes, ob = self.ctx0
        self.last_ob = ob  # Obelisk state at the end of this rollout (shop_sim carries it to the next round)
        total = 0.0
        growth = 0.0
        n_played = 0
        pos = 0
        kind, sel = first[0], [hand[i] for i in first[1]]
        cards = list(hand)
        while True:
            ids = {id(c) for c in sel}
            rest = [c for c in cards if id(c) not in ids]
            if kind == PLAY:
                s, t = self.score(sel, rest, h, d, (lock, used, rtypes, ob), rng)
                ob = self.last_ob = self._obelisk_after(ob, t)
                total += s
                need -= s
                h -= 1
                n_played += len(sel)
                if self.growth_j:
                    growth += self._growth(sel, t)
                if self.boss == "The Mouth" and lock is None:
                    lock = t
                if self.boss == "The Eye":
                    used = used | {t}
                if self.card_sharp:
                    rtypes = rtypes | {t}
                if need <= 0:
                    return True, total, h, self.d0 - d, growth, n_played
                if h <= 0:
                    return self.bones_at is not None and total >= self.bones_at, total, 0, self.d0 - d, growth, n_played
                if self.hook and rest:
                    for _ in range(min(2, len(rest))):
                        rest.pop(rng.randrange(len(rest)))
            else:
                d -= 1
                if "Green Joker" in self.growth_j:
                    growth -= 1
            n = 3 if self.serpent else max(0, self.hand_size - len(rest))
            rest.extend(order[pos:pos + n])
            pos += n
            cards = rest
            if not cards:
                return self.bones_at is not None and total >= self.bones_at, total, h, self.d0 - d, growth, n_played
            kind, sel = self.policy(cards, order[pos:], h, d, need, (lock, used, rtypes, ob))

    # ---- sampling ---------------------------------------------------------------------------------------------
    def _sample(self, s):
        while len(self._samples) <= s:
            k = len(self._samples)
            rng = random.Random(self.seed * 1_000_003 + k)
            perm = self.pool[:]
            rng.shuffle(perm)
            if self.pool_deb and self.pillar_frac > 0:  # The Pillar: a random share was played earlier this ante
                twin = {id(c): t for c, t in zip(self.pool, self.pool_deb)}
                deb = set(rng.sample(range(len(perm)), round(self.pillar_frac * len(perm))))
                perm = [twin[id(c)] if i in deb else c for i, c in enumerate(perm)]
            nfd = len(self.fd_pos)
            if nfd and self.mark:  # The Mark: face-down cards are face cards
                faces = [c for c in perm if c.face][:nfd]
                if len(faces) == nfd:
                    fset = {id(c) for c in faces}
                    perm = faces + [c for c in perm if id(c) not in fset]
            hand = list(self.slots)
            for j, p in enumerate(self.fd_pos):
                hand[p] = perm[j]
            self._samples.append((hand, perm[nfd:nfd + self.pile_n], rng.getstate()))
        return self._samples[s]

    def run(self, first, s):
        hand, order, rs = self._sample(s)
        rng = random.Random()
        rng.setstate(rs)
        return self.rollout(first, hand, order, rng)

    def run_with_order(self, first, hand, order, seed=0):
        """One rollout on an explicit resolved hand and draw order (offline evaluation of realized outcomes only)."""
        return self.rollout(first, hand, order, random.Random(seed))

    # ---- first-action candidates -----------------------------------------------------------------------------
    def candidates(self):
        """First actions: list of {kind, pos (hand positions), note}."""
        n = len(self.slots)
        known = [c if c is not None else self.unknown[i] for i, c in enumerate(self.slots)]
        ctx = self.ctx0
        h, d = self.h0, self.d0
        out, seen = [], set()

        def add(kind, pos, note):
            pos = tuple(sorted(set(pos) | set(self.forced)))
            if not pos or len(pos) > self.lim or (kind, pos) in seen:
                return
            seen.add((kind, pos))
            hand_type = None
            if kind == PLAY and all(known[i].known for i in pos):
                hand_type = self.classify([known[i] for i in pos])[0]
            out.append({"kind": kind, "pos": pos, "note": note, "hand": hand_type})

        vis = [c for c in known if c.known]
        idx_of = {id(c): i for i, c in enumerate(known)}
        bs, bp, _bt = self.best_play(vis, h, d, ctx) if vis else (0.0, [], None)
        pile_vis = _Pile(self.pool, self.suit_keys, P=max(1, self.pile_n))  # public composition (incl. face-down)
        keep_rank = {}
        for k in range(1, min(self.lim, n) + 1):
            for throw in itertools.combinations(range(n), k):
                K = frozenset(i for i in range(n) if i not in throw)
                keep_rank[K] = self.keep_value([known[i] for i in K], pile_vis, self.need0, h, d, ctx,
                                               self._n_draw(len(K), pile_vis.P))
        top_keeps = sorted(keep_rank.items(), key=lambda kv: -kv[1][0])
        # best play of each hand type, plain and with fillers
        by_type = {}
        for p in self._gen_plays(vis):
            ids = {id(c) for c in p}
            s, t = self.score(p, [c for c in known if id(c) not in ids], h, d, ctx)
            if t not in by_type or s > by_type[t][0]:
                by_type[t] = (s, p)
        for t, (s, p) in sorted(by_type.items(), key=lambda kv: -kv[1][0]):
            add(PLAY, [idx_of[id(c)] for c in p], f"{t} {' '.join(c.label() for c in p)} est {int(s)}")
            if self.psychic or self.pillar_ahead or len(p) >= self.lim:
                continue
            pids = {idx_of[id(c)] for c in p}
            for K, _v in top_keeps[:8]:
                fill = self._fillers(p, known, K | pids, h, d, ctx, s)
                if len(fill) > len(p):
                    fids = {id(c) for c in fill}
                    s2, t2 = self.score(fill, [c for c in known if id(c) not in fids], h, d, ctx)
                    sc2 = self.classify(fill)[1]  # label what the game reads (fillers can form a pair)
                    rest = [c for c in fill if c not in sc2]
                    add(PLAY, [idx_of[id(c)] for c in fill],
                        f"{t2} {' '.join(c.label() for c in sc2)} est {int(s2)}"
                        + (f" + filler(s) {' '.join(c.label() for c in rest)}" if rest else "")
                        + f" (draws {len(fill)} new cards)")
                    break
        if self.final_dep and h >= 2 and vis and not self.psychic:
            hold = self._hold(vis, h, d, ctx)
            if hold:
                tot, j, fs, fp, ft = hold
                add(PLAY, [idx_of[id(j)]], f"throwaway {j.label()}: hold {ft} {' '.join(c.label() for c in fp)} "
                                           f"for the final hand (est {int(fs)} then, ~{int(tot)} in total)")
        if d > 0:
            groups = {}
            for i, c in enumerate(known):
                if c.known and c.rank:
                    groups.setdefault(c.rank, []).append(i)
            made = [g for g in groups.values() if len(g) >= 2]
            chosen = [K for K, _v in top_keeps[:16]] + self._keep_sets(known, bp or [])
            for K in chosen:
                if K not in keep_rank:
                    continue
                _u, label = keep_rank[K]
                kept = " ".join(known[i].label() for i in sorted(K))
                broken = [g for g in made if any(i not in K for i in g)]
                warn = "; breaks " + ", ".join(SHORT[known[g[0]].rank] * len(g) for g in broken) if broken else ""
                add(DISCARD, [i for i in range(n) if i not in K], f"keep {kept or 'nothing'} ({self.label(label)}{warn})")
        elif h >= 2:
            # no discard left: playing junk is the only way to dig (keep pairs/draws, throw the rest as a hand)
            # The Pillar ahead: every played card is debuffed at the boss, so dig with single cards only
            digs = [kv for kv in top_keeps if n - len(kv[0]) == 1][:4] if self.pillar_ahead else top_keeps[:10]
            for K, (_u, label) in digs:
                throw = [i for i in range(n) if i not in K]
                if self.psychic and len(throw) < 5:
                    continue
                kept = " ".join(known[i].label() for i in sorted(K))
                add(PLAY, throw, f"dig: play {' '.join(known[i].label() for i in throw)}, keep {kept or 'nothing'} ({self.label(label)})")
        return out

    def forced_after(self, kind):
        """True when, after this first action, the rest of the round is forced (only the best final play is left):
        the final hand itself, or a play with 2 hands and 0 discards. Its p is exact under the model, so it is
        reported raw instead of through the calibration map."""
        return self.h0 <= 1 or (self.h0 == 2 and self.d0 == 0 and kind == PLAY)

    def evaluate(self, cands, samples=400, time_budget_s=2.0):
        """Successive halving on common sampled draw orders; returns ranked option dicts.
        Ranking: options whose p_clear is within TIE_P of the best full-sample option count as tied on p_clear and are
        ordered by secondary value = dollars from unused hands ($1 each) + GROWTH_W per growth-joker trigger
        - PILLAR_W per card played when The Pillar is this ante's boss, then fewer discards used, then exp_score;
        the rest follow by p_clear. A Mr. Bones save is a spent resource, not a clear: p_model counts only real clears
        and p_survive (Bones saves included) is the first tie-break."""
        t0 = time.perf_counter()
        # n, clears (no Bones), score, hands left, discards, growth, cards played, survivals (Bones saves included)
        stats = [[0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0] for _ in cands]
        pw = PILLAR_W if self.pillar_ahead else 0.0

        def step(i, upto):
            st = stats[i]
            first = (cands[i]["kind"], cands[i]["pos"])
            while st[0] < upto:
                ok, tot, hl, du, g, npl = self.run(first, st[0])
                st[0] += 1
                st[1] += ok and tot >= self.need0
                st[2] += tot
                st[3] += hl
                st[4] += du
                st[5] += g
                st[6] += npl
                st[7] += ok

        def key(i):
            st = stats[i]
            n = max(1, st[0])
            return (st[1] / n, st[7] / n, (st[3] + GROWTH_W * st[5] - pw * st[6]) / n, -st[4] / n, st[2] / n)

        alive = list(range(len(cands)))
        s1 = min(samples, 16)
        stages = [(s1, 10), (min(samples, 100), 4), (samples, len(cands))]
        for upto, keep in stages:
            for i in alive:
                step(i, upto)
                if upto > s1 and time.perf_counter() - t0 > time_budget_s:
                    break
            alive = sorted(alive, key=key, reverse=True)[:keep]
            if time.perf_counter() - t0 > time_budget_s:
                break
        # an under-sampled option that looks as good as the best full-sample one is noise until checked: top up the
        # best 3 such challengers to the full count (outside the budget) so no noisy p is shown above a measured one
        full = max(st[0] for st in stats) if stats else 0
        best_full = max((st[1] / st[0] for st in stats if st[0] == full and full), default=0.0)
        chal = sorted((i for i, st in enumerate(stats) if 0 < st[0] < full and st[1] / st[0] >= best_full - TIE_P),
                      key=key, reverse=True)[:3]
        for i in chal:
            step(i, full)
        # nothing within 0.3 of the best p is reported on fewer than MIN_N samples (n=16 estimates swing by +-0.25)
        best_p = max((st[1] / st[0] for st in stats if st[0]), default=0.0)
        near = sorted((i for i, st in enumerate(stats) if 0 < st[0] < MIN_N and st[1] / st[0] >= best_p - 0.3),
                      key=key, reverse=True)[:8]
        for i in near:
            step(i, min(MIN_N, samples))
        res = []
        for i, c in enumerate(cands):
            n, cl, tot, hl, du, g, npl, sv = stats[i]
            if not n:
                continue
            res.append({"action": c["kind"], "cards": [self.slot_index[p] for p in c["pos"]],
                        "p_clear": cl / n if self.forced_after(c["kind"]) else calibrate(cl / n, self.jokerless),
                        "p_model": cl / n, "p_survive": sv / n,
                        "exp_score": tot / n, "hands_left": hl / n, "dollars": hl / n, "growth": g / n,
                        "cards_played": npl / n, "value": (hl + GROWTH_W * g - pw * npl) / n,
                        "discards_used": du / n, "n": n, "low_n": n < min(MIN_N, samples), "note": c["note"],
                        "hand": c.get("hand"), "first_card": self._first_for(c)})
        # slices where p is less trustworthy: few samples, final-hand jokers (Acrobat/Dusk slice is mis-calibrated on
        # recorded data), face-down cards (their identity is sampled)
        shaky = self.final_dep or bool(self.fd_pos)
        for r in res:
            r["low_confidence"] = r["low_n"] or shaky
            if r["first_card"] is not None:
                lab = next(x.label() for x in self.slots if x is not None and x.d.get("index") == r["first_card"])
                r["note"] += f" [move {lab} leftmost: scores first]"
        top_n = max((r["n"] for r in res), default=0)
        full_n = min(top_n, 120)
        top_p = max((r["p_model"] for r in res if r["n"] >= full_n), default=0.0)

        def rank(r):
            tied = r["p_model"] >= top_p - TIE_P
            return (r["n"] >= full_n, tied, 1.0 if tied else r["p_model"], r["p_survive"], r["value"],
                    -r["discards_used"], r["exp_score"])

        res.sort(key=rank, reverse=True)
        return res


def calibrate(p, jokerless=False):
    """Map the model's p (P(clear) when the rest of the round follows the solver's greedy policy) to the observed
    clear rate of Gold players taking that action (CALIBRATION knots, linear interpolation). With jokers, players'
    later play beats the greedy policy in hard spots (consumables, chip-and-dig lines), so the raw p is too low in
    the 0.03-0.9 range; jokerless rounds are already calibrated raw and are returned unchanged.
    Refit with `python -m balatro_env.analysis.solver_calib`."""
    if jokerless:
        return p
    for (x0, y0), (x1, y1) in zip(CALIBRATION, CALIBRATION[1:]):
        if p <= x1:
            return y0 if x1 <= x0 else y0 + (y1 - y0) * (p - x0) / (x1 - x0)
    return CALIBRATION[-1][1]


def default_estimate():
    """cli.py's estimate (imported lazily: cli.py is a script that may itself load this module)."""
    try:
        from balatro_env.scripts.cli import estimate
    except Exception:  # noqa: BLE001 - package import unavailable (torch etc.): load the sibling script file
        import importlib.util
        import os
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "cli.py")
        spec = importlib.util.spec_from_file_location("_balatro_cli", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        estimate = mod.estimate
    return estimate


def best_round_plan(state, estimate_fn=None, *, samples=400, time_budget_s=2.0, seed=0):
    """Ranked options for the current SELECTING_HAND decision, best first:
    [{action: 'PLAY'|'DISCARD', cards: [hand indices], p_clear, exp_score, note, hand, hands_left, dollars, growth,
    value, discards_used, n}].
    p_clear = P(clear the blind within the remaining hands) taking this action and then the solver's greedy policy
    (Monte-Carlo over n sampled draw orders); exp_score = mean chips scored over the rest of the round; hand = the
    poker hand a PLAY makes (None for discards and plays with face-down cards); dollars = mean unused hands at the
    clear ($1 each at cash-out); growth = mean growth-joker triggers this round (Square Joker, Runner, Spare Trousers,
    Ride the Bus, Green Joker, Supernova, Hiker, Wee Joker); value = dollars + GROWTH_W * growth.
    Options that reached the full sample count rank first; options within TIE_P of the best p_clear are ordered by
    value, then fewer discards used, then exp_score. time_budget_s covers candidate generation too (every candidate
    still gets the first 16 samples)."""
    if state.get("phase") not in (None, "SELECTING_HAND") or not _lst(state.get("hand")):
        return []
    if int(state.get("hands_remaining") or 0) <= 0:
        return []
    t0 = time.perf_counter()
    rs = RoundSolver(state, estimate_fn or default_estimate(), seed=seed)
    cands = rs.candidates()
    return rs.evaluate(cands, samples=samples, time_budget_s=max(0.2, time_budget_s - (time.perf_counter() - t0)))


def evaluate_action(state, action, cards, estimate_fn=None, *, samples=400, seed=0):
    """p_clear / exp_score of one given first action (cards = hand indices) on the same sampled orders as
    best_round_plan with this seed."""
    rs = RoundSolver(state, estimate_fn or default_estimate(), seed=seed)
    want = set(cards)
    pos = tuple(i for i, ix in enumerate(rs.slot_index) if ix in want)
    r = rs.evaluate([{"kind": action, "pos": pos, "note": "given"}], samples=samples, time_budget_s=1e9)
    return r[0] if r else None
