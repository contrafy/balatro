"""Live legality fuzzer.

At every settled decision point: probe illegal actions (each must be rejected without changing state),
then sample a legal action from the full /legal domain (lightly biased so runs reach later antes and
shops) and require the bridge to accept it. Watches /health and the instance's Lovely log for crashes.
Seeds come from the FUZZ* range (disjoint from eval and swarm seeds).
"""

from __future__ import annotations

import itertools
import json
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from balatro_env.data.bridge import Bridge, BridgeError
from balatro_env.data.diff import all_differences, normalize
from balatro_env.data.legality import check_action, entry_is_satisfiable, illegal_probes, sample_params
from balatro_env.data.seeds import fuzz_seed

# Relative type weights (unlisted types weigh 1.0). Uniform within a type over entries and params.
TYPE_WEIGHTS = {
    "SELECT_BLIND": 6.0, "SKIP_BLIND": 1.0, "REROLL_BOSS": 1.0,
    "PLAY_HAND": 4.0, "DISCARD": 1.5, "REORDER": 0.4, "SORT_HAND": 0.4,
    "USE_CONSUMABLE": 1.5, "SELL_JOKER": 0.3, "SELL_CONSUMABLE": 0.3,
    "CASH_OUT": 4.0,
    "SHOP_BUY": 2.0, "SHOP_BUY_AND_USE": 1.0, "SHOP_BUY_VOUCHER": 1.0, "SHOP_BUY_BOOSTER": 1.5,
    "SHOP_REROLL": 0.7, "SHOP_END": 1.0,
    "SELECT_PACK_CARD": 3.0, "SKIP_PACK": 1.0,
}
GREEDY_PLAY_P = 0.85
LOW_STAKE_P = 0.5  # half the runs at the lowest legal stake so runs get deeper; the rest uniform
JOKER_BUY_P = 0.6  # in the shop, buy an affordable joker this often when one is legal
RUN_OVER_PHASES = {"GAME_OVER", "WIN"}

RANK_VALUE = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
              "Jack": 11, "Queen": 12, "King": 13, "Ace": 14}
HAND_BASE = {  # (chips, mult) at level 1
    "Straight Flush": (100, 8), "Four of a Kind": (60, 7), "Full House": (40, 4), "Flush": (35, 4),
    "Straight": (30, 4), "Three of a Kind": (30, 3), "Two Pair": (20, 2), "Pair": (10, 2),
    "High Card": (5, 1),
}


def _card_chips(rank: int) -> int:
    return 11 if rank == 14 else min(rank, 10)


def classify(cards: list[tuple[int, str]]) -> tuple[str, list[int]]:
    """Vanilla-ish poker hand of 1-5 (rank, suit) cards -> (hand, scoring positions within `cards`)."""
    ranks = [r for r, _ in cards]
    counts = Counter(ranks)
    by_count = sorted(counts.items(), key=lambda kv: (-kv[1], -kv[0]))
    flush = len(cards) == 5 and len({s for _, s in cards}) == 1
    uniq = sorted(set(ranks))
    straight = len(cards) == 5 and len(uniq) == 5 and (uniq[-1] - uniq[0] == 4 or uniq == [2, 3, 4, 5, 14])
    every = list(range(len(cards)))
    if straight and flush:
        return "Straight Flush", every
    if by_count[0][1] == 4:
        return "Four of a Kind", [i for i, r in enumerate(ranks) if r == by_count[0][0]]
    if by_count[0][1] == 3 and len(by_count) > 1 and by_count[1][1] == 2:
        return "Full House", every
    if flush:
        return "Flush", every
    if straight:
        return "Straight", every
    if by_count[0][1] == 3:
        return "Three of a Kind", [i for i, r in enumerate(ranks) if r == by_count[0][0]]
    if by_count[0][1] == 2 and len(by_count) > 1 and by_count[1][1] == 2:
        pair_ranks = {by_count[0][0], by_count[1][0]}
        return "Two Pair", [i for i, r in enumerate(ranks) if r in pair_ranks]
    if by_count[0][1] == 2:
        return "Pair", [i for i, r in enumerate(ranks) if r == by_count[0][0]]
    return "High Card", [ranks.index(max(ranks))]


def _subset_spec(entry: dict[str, Any]) -> dict[str, Any] | None:
    return ((entry.get("params") or {}).get("card_indices") or {}).get("subset")


def greedy_play(state: dict[str, Any], entry: dict[str, Any]) -> tuple[list[int] | None, float]:
    """Best-scoring card subset inside a PLAY_HAND entry's subset domain (ignores jokers) and its score."""
    spec = _subset_spec(entry)
    hand = state.get("hand") or []
    if not spec or not isinstance(hand, list):
        return None, 0.0
    of = [i for i in spec.get("of", []) if 1 <= i <= len(hand)]
    must = list(spec.get("must_include") or [])
    lo, hi = max(spec.get("min", 1), len(must)), min(spec.get("max", 5), len(of))
    levels = state.get("hand_levels") or {}
    best, best_score = None, -1.0
    for size in range(lo, hi + 1):
        for combo in itertools.combinations(of, size):
            if any(m not in combo for m in must):
                continue
            cards = []
            for idx in combo:
                c = hand[idx - 1]
                cards.append((RANK_VALUE.get(str(c.get("rank")), 0), str(c.get("suit"))))
            name, scoring = classify(cards)
            lvl = levels.get(name) if isinstance(levels, dict) else None
            chips, mult = HAND_BASE[name]
            if isinstance(lvl, dict):
                chips, mult = lvl.get("chips") or chips, lvl.get("mult") or mult
            score = (chips + sum(_card_chips(cards[k][0]) for k in scoring)) * mult
            score -= 0.01 * size  # prefer keeping cards when equal
            if score > best_score:
                best, best_score = list(combo), score
    return best, best_score


def greedy_discard(state: dict[str, Any], entry: dict[str, Any]) -> list[int] | None:
    """Discard toward a flush (>=3 of a suit) or else keep pairs/high cards; respects the subset domain."""
    spec = _subset_spec(entry)
    hand = state.get("hand") or []
    if not spec or not isinstance(hand, list):
        return None
    of = [i for i in spec.get("of", []) if 1 <= i <= len(hand)]
    must = list(spec.get("must_include") or [])
    hi = spec.get("max", 5)
    ranks = {i: RANK_VALUE.get(str(hand[i - 1].get("rank")), 0) for i in of}
    suits = {i: str(hand[i - 1].get("suit")) for i in of}
    suit, n = Counter(suits.values()).most_common(1)[0] if suits else (None, 0)
    if n >= 3:
        keep = {i for i in of if suits[i] == suit}
    else:
        counts = Counter(ranks.values())
        keep = {i for i in of if counts[ranks[i]] >= 2}
    toss = sorted((i for i in of if i not in keep and i not in must), key=lambda i: ranks[i])
    pick = must + toss[: max(0, hi - len(must))]
    if len(pick) < max(spec.get("min", 1), 1):
        return None
    return sorted(pick)


@dataclass
class FuzzStats:
    port: int
    runs: int = 0
    steps: int = 0
    accepted: Counter = field(default_factory=Counter)
    sampled: Counter = field(default_factory=Counter)
    phases: Counter = field(default_factory=Counter)
    probes_sent: int = 0
    probes_rejected: int = 0
    legal_rejections: list[dict[str, Any]] = field(default_factory=list)
    probe_accepted: list[dict[str, Any]] = field(default_factory=list)
    probe_state_changed: list[dict[str, Any]] = field(default_factory=list)
    bridge_errors: list[dict[str, Any]] = field(default_factory=list)
    log_errors: list[str] = field(default_factory=list)
    crashes: list[dict[str, Any]] = field(default_factory=list)
    stuck: list[dict[str, Any]] = field(default_factory=list)
    run_summaries: list[dict[str, Any]] = field(default_factory=list)
    trajectories: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        out = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in self.__dict__.items()}
        out["acceptance_rate"] = (sum(self.accepted.values()) / self.steps) if self.steps else None
        return out


class LovelyLog:
    """Tails the newest Lovely log of one instance for ERROR lines."""

    def __init__(self, instance_dir: Path | None):
        self.dir = instance_dir / "Balatro" / "Mods" / "lovely" / "log" if instance_dir else None
        self.path: Path | None = None
        self.offset = 0
        self._latch()

    def _latch(self) -> None:
        if not self.dir or not self.dir.exists():
            return
        logs = sorted(self.dir.glob("*.log"), key=lambda p: p.stat().st_mtime)
        if logs and logs[-1] != self.path:
            self.path, self.offset = logs[-1], logs[-1].stat().st_size

    def new_errors(self) -> list[str]:
        if not self.path or not self.path.exists():
            self._latch()
            return []
        with open(self.path, "rb") as fh:
            fh.seek(self.offset)
            chunk = fh.read()
        self.offset += len(chunk)
        text = chunk.decode("utf-8", "replace")
        return [ln.strip() for ln in text.splitlines() if "ERROR" in ln]


class Fuzzer:
    def __init__(self, port: int, seed_start: int = 0, rng_seed: int | None = None,
                 probes_per_step: int = 6, instance_dir: Path | None = None, log=print,
                 settle_timeout: float = 90.0):
        self.bridge = Bridge(port)
        self.port = port
        self.seed_index = seed_start
        self.rng = random.Random(rng_seed if rng_seed is not None else port * 1000003 + seed_start)
        self.probes_per_step = probes_per_step
        self.loglog = LovelyLog(instance_dir)
        self.log = log
        self.settle_timeout = settle_timeout
        self.stats = FuzzStats(port=port)
        self._shop_streak = 0
        self._start_entry: dict[str, Any] | None = None

    # ---- sampling -------------------------------------------------------------------------------

    def choose(self, state: dict[str, Any], legal: dict[str, Any]) -> dict[str, Any]:
        entries = [e for e in legal.get("actions") or [] if e.get("type") and entry_is_satisfiable(e)]
        entries = [e for e in entries if e["type"] != "START_RUN"]
        if not entries:
            raise BridgeError(f"no satisfiable legal entries in phase {legal.get('phase')}: {legal}")
        by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for e in entries:
            by_type[e["type"]].append(e)
        if "PLAY_HAND" in by_type and self.rng.random() < GREEDY_PLAY_P:
            pick, score = greedy_play(state, self.rng.choice(by_type["PLAY_HAND"]))
            blind = state.get("blind") or {}
            need = (blind.get("chips_needed") or 0) - (blind.get("chips_scored") or 0)
            hands_left = max(state.get("hands_remaining") or 1, 1)
            if "DISCARD" in by_type and score * 1.3 < need / hands_left:
                toss = greedy_discard(state, self.rng.choice(by_type["DISCARD"]))
                if toss:
                    return {"type": "DISCARD", "params": {"card_indices": toss}, "greedy": True}
            if pick:
                return {"type": "PLAY_HAND", "params": {"card_indices": pick}, "greedy": True}
        joker_buys = [e for e in by_type.get("SHOP_BUY", [])
                      if str((e.get("info") or {}).get("key", "")).startswith("j_")]
        if joker_buys and self.rng.random() < JOKER_BUY_P:
            return {"type": "SHOP_BUY", "params": sample_params(self.rng.choice(joker_buys), self.rng)}
        types = sorted(by_type)
        weights = []
        for t in types:
            w = TYPE_WEIGHTS.get(t, 1.0)
            if t == "SHOP_END":
                w += 0.5 * self._shop_streak
            weights.append(w)
        t = self.rng.choices(types, weights=weights)[0]
        entry = self.rng.choice(by_type[t])
        return {"type": t, "params": sample_params(entry, self.rng)}

    # ---- checks ---------------------------------------------------------------------------------

    def _crash_check(self, context: dict[str, Any]) -> bool:
        errors = self.loglog.new_errors()
        if errors:
            self.stats.log_errors.extend(errors)
            self.log(f"  LOVELY ERROR: {errors[:3]}")
        if not self.bridge.alive():
            time.sleep(5)
            if not self.bridge.alive():
                self.stats.crashes.append({**context, "log_errors": errors[-20:]})
                return True
        return False

    def _probe(self, state: dict[str, Any], legal: dict[str, Any], ctx: dict[str, Any]) -> bool:
        probes = illegal_probes(legal, self.rng)
        if len(probes) > self.probes_per_step:
            probes = probes[:2] + self.rng.sample(probes[2:], self.probes_per_step - 2)
        for probe in probes:
            self.stats.probes_sent += 1
            res = self.bridge.action(probe["type"], probe["params"],
                                     {"why": "fuzz illegal probe", "agent": "fuzzer"})
            if res.get("ok"):
                self.stats.probe_accepted.append({**ctx, "action": probe, "response": res})
                self.log(f"  BUG illegal action accepted: {probe}")
                return False  # state changed; re-read before continuing
            self.stats.probes_rejected += 1
        if probes:
            state2, legal2 = self.bridge.wait_settled(self.settle_timeout)
            d = all_differences(normalize(state), normalize(state2)) + \
                all_differences(normalize(legal), normalize(legal2), "legal")
            if d:
                self.stats.probe_state_changed.append({**ctx, "diff": d[:5], "probes": probes})
                self.log(f"  BUG rejected probes changed state: {d[:2]}")
                return False
        return True

    # ---- main loop ------------------------------------------------------------------------------

    def start_run(self, legal: dict[str, Any] | None) -> dict[str, Any]:
        seed = fuzz_seed(self.seed_index)
        self.seed_index += 1
        entry = next((e for e in (legal or {}).get("actions") or [] if e.get("type") == "START_RUN"), None)
        entry = entry or self._start_entry
        if entry:
            self._start_entry = entry
            params = sample_params(entry, self.rng, seed=seed)
            params.setdefault("seed", seed)
            for k in ("deck", "stake"):
                if k not in params and k in (entry.get("params") or {}):
                    params[k] = self.rng.choice(entry["params"][k]["one_of"])
            stakes = ((entry.get("params") or {}).get("stake") or {}).get("one_of") or []
            if stakes and self.rng.random() < LOW_STAKE_P:
                params["stake"] = min(stakes)
        else:  # mid-run admin restart before any START_RUN domain was seen
            params = {"deck": "b_red", "stake": 1, "seed": seed}
        res = self.bridge.act_settled("START_RUN", params, {"why": "fuzz run", "agent": "fuzzer"})
        if not res.get("ok"):
            raise BridgeError(f"START_RUN {params} rejected: {res}")
        path = res.get("trajectory_path") or self.bridge.health().get("trajectory_path")
        if path:
            self.stats.trajectories.append(path)
        self.stats.runs += 1
        self.log(f"run {self.stats.runs}: seed={seed} deck={params.get('deck')} stake={params.get('stake')} "
                 f"file={path}")
        return {"seed": seed, **params, "trajectory": path}

    def _settled(self, ctx: dict[str, Any], last_act: dict[str, Any] | None):
        """(state, legal) at the next decision point, or None when the game never settles (recorded)."""
        try:
            return self.bridge.wait_settled(self.settle_timeout)
        except BridgeError as exc:
            if not self.bridge.alive():
                raise
            legal = self.bridge.legal()
            self.stats.stuck.append({**ctx, "after_action": last_act, "error": str(exc),
                                     "phase": legal.get("phase"), "settle_reason": legal.get("settle_reason")})
            self.log(f"  STUCK after {last_act}: phase={legal.get('phase')} "
                     f"settle_reason={legal.get('settle_reason')!r}")
            return None

    def run(self, runs: int, steps_per_run: int, total_steps: int | None = None) -> FuzzStats:
        st = self.stats
        first = self._settled({"seed": None, "run_step": 0}, None)
        legal = first[1] if first else {}
        for _ in range(runs):
            if total_steps is not None and st.steps >= total_steps:
                break
            info = self.start_run(legal if legal.get("phase") in RUN_OVER_PHASES | {"MENU"} else None)
            run_steps, max_ante, outcome = 0, 0, "step_cap"
            self._shop_streak = 0
            skip_probe = False
            act: dict[str, Any] | None = None
            while run_steps < steps_per_run and (total_steps is None or st.steps < total_steps):
                ctx = {"seed": info["seed"], "run_step": run_steps, "trajectory": info.get("trajectory")}
                got = self._settled(ctx, act)
                if got is None:
                    outcome, legal = "stuck", {}
                    break
                state, legal = got
                phase = legal.get("phase")
                max_ante = max(max_ante, state.get("ante") or 0)
                if phase in RUN_OVER_PHASES:
                    outcome = "win" if phase == "WIN" else "loss"
                    break
                ctx["phase"] = phase
                if self.probes_per_step and not skip_probe and not self._probe(state, legal, ctx):
                    skip_probe = True  # probes misbehaved: act once from a fresh read before probing again
                    continue
                skip_probe = False
                act = self.choose(state, legal)
                act.pop("greedy", None)
                reason = check_action(legal, act)
                if reason:  # sampler bug, never send
                    raise AssertionError(f"sampler produced illegal action {act}: {reason}")
                before = self.bridge.health()
                res = self.bridge.action(act["type"], act["params"],
                                         {"why": "fuzz random legal action", "agent": "fuzzer"})
                st.steps += 1
                run_steps += 1
                st.sampled[act["type"]] += 1
                st.phases[phase] += 1
                self._shop_streak = self._shop_streak + 1 if phase == "SHOP" else 0
                if res.get("ok"):
                    st.accepted[act["type"]] += 1
                else:
                    entry = [e for e in legal.get("actions") or [] if e.get("type") == act["type"]]
                    st.legal_rejections.append({**ctx, "action": act, "response": res, "entries": entry})
                    self.log(f"  REJECTED legal action {act}: {res.get('error')!r} (retry={res.get('retry')})")
                after = self.bridge.health() if self.bridge.alive() else {}
                if after and after.get("error_count", 0) > before.get("error_count", 0):
                    st.bridge_errors.append({**ctx, "action": act, "last_error": after.get("last_error")})
                    self.log(f"  BRIDGE ERROR after {act}: {after.get('last_error')!r}")
                if self._crash_check({**ctx, "action": act}):
                    self.log(f"  CRASH after {act}")
                    st.run_summaries.append({**info, "steps": run_steps, "max_ante": max_ante,
                                             "outcome": "crash"})
                    return st
                if st.steps % 100 == 0:
                    self.log(f"  {st.steps} steps, ante {max_ante}, phase {phase}, "
                             f"rejections={len(st.legal_rejections)}")
            st.run_summaries.append({**info, "steps": run_steps, "max_ante": max_ante, "outcome": outcome})
            self.log(f"  run done: {outcome} after {run_steps} steps, max ante {max_ante}")
        return st


def write_report(stats: FuzzStats, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"fuzz_{stats.port}_{int(time.time() * 1000)}.json"
    path.write_text(json.dumps(stats.as_dict(), indent=1, default=str), encoding="utf-8")
    return path
