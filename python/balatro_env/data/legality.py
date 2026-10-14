"""Legal-domain checks and sampling for the bridge's `GET /legal` shape (docs/DATA_CONTRACT.md).

`legal = {schema_version, phase, settled, actions: [entry, ...]}` with
`entry = {type, params: {name: domain}, info?: {...}}`. An action is legal iff it matches ANY entry of its
type: every listed param matches its domain (unless the domain is `optional` and the param is absent) and
no unlisted param is present. An empty `targets` list counts as absent. Domain kinds (exactly one key):

- `{"one_of": [v, ...]}`                                        scalar in the set
- `{"subset": {"of": [i...], "min": a, "max": b, "must_include": [i...]}}`  distinct ints from `of`
- `{"permutation": n}`                                          permutation of 1..n
- `{"seed": true}`                                              non-empty seed string
"""

from __future__ import annotations

import random
from typing import Any

DOMAIN_KINDS = ("one_of", "subset", "permutation", "seed")

# Every action type in the contract; used to build "wrong type" probes.
ALL_ACTION_TYPES = (
    "START_RUN", "SELECT_BLIND", "SKIP_BLIND", "REROLL_BOSS", "PLAY_HAND", "DISCARD", "REORDER",
    "SORT_HAND", "USE_CONSUMABLE", "SELL_JOKER", "SELL_CONSUMABLE", "CASH_OUT", "SHOP_BUY",
    "SHOP_BUY_AND_USE", "SHOP_BUY_VOUCHER", "SHOP_BUY_BOOSTER", "SHOP_REROLL", "SHOP_END",
    "SELECT_PACK_CARD", "SKIP_PACK",
)


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_absent(name: str, value: Any) -> bool:
    return value is None or (name == "targets" and isinstance(value, list) and len(value) == 0)


def _as_list(v: Any) -> Any:
    # Lua encodes empty tables as {}; treat that as an empty list.
    if isinstance(v, dict) and not v:
        return []
    return v


def domain_kind(domain: dict[str, Any]) -> str:
    kinds = [k for k in DOMAIN_KINDS if k in domain]
    if len(kinds) != 1:
        raise ValueError(f"domain must have exactly one of {DOMAIN_KINDS}: {domain!r}")
    return kinds[0]


def check_value(domain: dict[str, Any], value: Any) -> str | None:
    """Return None when `value` is inside `domain`, otherwise a reason string."""
    kind = domain_kind(domain)
    if kind == "one_of":
        options = _as_list(domain["one_of"])
        for opt in options:
            if type(opt) is type(value) and opt == value:
                return None
            if _is_int(opt) and _is_int(value) and opt == value:
                return None
        return f"{value!r} not in {options!r}"
    if kind == "subset":
        spec = domain["subset"]
        value = _as_list(value)
        if not isinstance(value, list) or not all(_is_int(v) for v in value):
            return f"{value!r} is not a list of ints"
        if len(set(value)) != len(value):
            return f"{value!r} has duplicates"
        of = set(_as_list(spec.get("of", [])))
        outside = [v for v in value if v not in of]
        if outside:
            return f"{outside!r} not in {sorted(of)!r}"
        lo, hi = spec.get("min", 0), spec.get("max", len(of))
        if not lo <= len(value) <= hi:
            return f"size {len(value)} not in [{lo}, {hi}]"
        missing = [v for v in _as_list(spec.get("must_include", [])) if v not in value]
        if missing:
            return f"must include {missing!r}"
        return None
    if kind == "permutation":
        n = domain["permutation"]
        value = _as_list(value)
        if not isinstance(value, list) or not all(_is_int(v) for v in value):
            return f"{value!r} is not a list of ints"
        if sorted(value) != list(range(1, n + 1)):
            return f"{value!r} is not a permutation of 1..{n}"
        return None
    # seed
    if not isinstance(value, str) or not value:
        return f"{value!r} is not a seed string"
    return None


def check_entry(entry: dict[str, Any], params: dict[str, Any]) -> str | None:
    """Return None when `params` match one legal entry, otherwise a reason string."""
    domains = entry.get("params") or {}
    for name, value in params.items():
        if name not in domains and not _is_absent(name, value):
            return f"param {name!r} not allowed"
    for name, domain in domains.items():
        value = params.get(name)
        if _is_absent(name, value):
            if domain.get("optional"):
                continue
            if name == "targets" and domain_kind(domain) == "subset" and domain["subset"].get("min", 0) == 0:
                continue
            return f"param {name!r} missing"
        reason = check_value(domain, value)
        if reason:
            return f"param {name!r}: {reason}"
    return None


def check_action(legal: dict[str, Any], action: dict[str, Any]) -> str | None:
    """Return None when `action` ({type, params}) is legal under `legal`, otherwise a reason string."""
    if legal.get("settled") is False:
        return "legal snapshot not settled"
    atype = action.get("type")
    params = action.get("params") or {}
    if not isinstance(params, dict):
        return f"params is not an object: {params!r}"
    entries = [e for e in _as_list(legal.get("actions") or []) if e.get("type") == atype]
    if not entries:
        return f"type {atype!r} not legal in phase {legal.get('phase')!r}"
    reasons = []
    for entry in entries:
        reason = check_entry(entry, params)
        if reason is None:
            return None
        reasons.append(reason)
    return f"{atype}: no entry matches ({'; '.join(reasons)})"


# --------------------------------------------------------------------------------------------------
# Sampling


def sample_value(domain: dict[str, Any], rng: random.Random) -> Any:
    kind = domain_kind(domain)
    if kind == "one_of":
        return rng.choice(_as_list(domain["one_of"]))
    if kind == "subset":
        spec = domain["subset"]
        of = list(_as_list(spec.get("of", [])))
        must = list(_as_list(spec.get("must_include", [])))
        lo = max(spec.get("min", 0), len(must))
        hi = min(spec.get("max", len(of)), len(of))
        size = rng.randint(lo, hi)
        rest = [v for v in of if v not in must]
        return sorted(must + rng.sample(rest, size - len(must)))
    if kind == "permutation":
        order = list(range(1, domain["permutation"] + 1))
        rng.shuffle(order)
        return order
    raise ValueError("seed domains are filled by the caller")


def sample_params(entry: dict[str, Any], rng: random.Random, seed: str | None = None) -> dict[str, Any]:
    """Uniformly sample params inside `entry`'s domains. Optional params are included with p=0.5."""
    params: dict[str, Any] = {}
    for name, domain in (entry.get("params") or {}).items():
        if domain_kind(domain) == "seed":
            if seed is not None:
                params[name] = seed
            continue
        if domain.get("optional") and rng.random() < 0.5:
            continue
        value = sample_value(domain, rng)
        if name == "targets" and value == []:
            continue
        params[name] = value
    return params


def entry_is_satisfiable(entry: dict[str, Any]) -> bool:
    for domain in (entry.get("params") or {}).values():
        kind = domain_kind(domain)
        if kind == "one_of" and not _as_list(domain["one_of"]) and not domain.get("optional"):
            return False
        if kind == "subset":
            spec = domain["subset"]
            of = _as_list(spec.get("of", []))
            lo = max(spec.get("min", 0), len(_as_list(spec.get("must_include", []))))
            if lo > min(spec.get("max", len(of)), len(of)):
                return False
    return True


# --------------------------------------------------------------------------------------------------
# Illegal probes


def illegal_probes(legal: dict[str, Any], rng: random.Random) -> list[dict[str, Any]]:
    """Actions that must be rejected at this decision point (each verified illegal by `check_action`).

    START_RUN is never probed: mid-run it is accepted as an admin restart (closes the run as abandoned).
    """
    entries = [e for e in _as_list(legal.get("actions") or []) if e.get("type") and e["type"] != "START_RUN"]
    legal_types = {e["type"] for e in entries}
    candidates: list[dict[str, Any]] = [{"type": "NOT_AN_ACTION", "params": {}}]
    absent = [t for t in ALL_ACTION_TYPES if t not in legal_types and t != "START_RUN"]
    if absent:
        t = rng.choice(absent)
        candidates.append({"type": t, "params": _plausible_params(t)})
    for entry in entries:
        domains = entry.get("params") or {}
        base = sample_params(entry, rng) if entry_is_satisfiable(entry) else {}
        candidates.append({"type": entry["type"], "params": {**base, "bogus_param": 1}})
        for name, domain in domains.items():
            for bad in _bad_values(domain):
                candidates.append({"type": entry["type"], "params": {**base, name: bad}})
            if not domain.get("optional"):
                candidates.append({"type": entry["type"],
                                   "params": {k: v for k, v in base.items() if k != name}})
    probes, seen = [], set()
    for cand in candidates:
        key = repr((cand["type"], sorted(cand["params"].items(), key=lambda kv: kv[0])))
        if key in seen or check_action(legal, cand) is None:
            continue
        seen.add(key)
        probes.append(cand)
    return probes


def _plausible_params(atype: str) -> dict[str, Any]:
    if atype in ("PLAY_HAND", "DISCARD"):
        return {"card_indices": [1]}
    if atype in ("SHOP_BUY", "SHOP_BUY_VOUCHER", "SHOP_BUY_BOOSTER", "SHOP_BUY_AND_USE"):
        return {"slot": 1}
    if atype in ("USE_CONSUMABLE", "SELL_JOKER", "SELL_CONSUMABLE", "SELECT_PACK_CARD"):
        return {"index": 1}
    if atype == "SORT_HAND":
        return {"mode": "rank"}
    if atype == "REORDER":
        return {"area": "jokers", "order": [1]}
    if atype == "START_RUN":
        return {"deck": "b_red", "stake": 1, "seed": "FUZZPRB1"}
    return {}


def _bad_values(domain: dict[str, Any]) -> list[Any]:
    kind = domain_kind(domain)
    if kind == "one_of":
        opts = _as_list(domain["one_of"])
        ints = [o for o in opts if _is_int(o)]
        if ints:
            return [max(ints) + 1, 0, -1, str(ints[0])]
        return ["__bogus__", 1]
    if kind == "subset":
        spec = domain["subset"]
        of = list(_as_list(spec.get("of", [])))
        hi = spec.get("max", len(of))
        bad: list[Any] = [[max(of, default=0) + 1], [0], "1"]
        if of:
            bad.append([of[0], of[0]])
        if len(of) > hi:
            bad.append(of[: hi + 1])
        if spec.get("min", 0) >= 1:
            bad.append([])
        must = _as_list(spec.get("must_include", []))
        if must:
            rest = [v for v in of if v not in must]
            if rest:
                bad.append(rest[:1])
        return bad
    if kind == "permutation":
        n = domain["permutation"]
        bad = [list(range(1, n + 2)), [0] * max(n, 1)]
        if n >= 2:
            bad += [list(range(1, n)), [1] * n]
        return bad
    return [""]
