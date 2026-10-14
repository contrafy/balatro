"""Gold Stake (stake 8) run statistics from recorded trajectories.

Rerun: `cd python && python -m balatro_env.analysis.gold_stats [--data-dir ../data] [--out FILE] [--since-client SHA]`.
Prints Markdown tables (deaths, ante-start profile, economy, advisor versions, shop supply, decisions, score curve)
used by docs/GOLD_ANALYSIS.md. `--since-client SHA` adds a before/after split at the first step made with cli.py@SHA.
Read-only over `<data>/trajectories/**`.

Run filter: header stake 8, `start_meta.agent` not `test-*`/`replay`, no `replay_of`, seed not `FUZZ*`.
Runs without an `end` line are still being played (or crashed): they feed the supply/economy/score tables but
not the death tables.

Ante attribution: rounds (play, cash-out, rent) belong to the ante of their blind; shop/pack spending belongs to
`obs.ante` at the time (the shop after an ante-A boss already shows ante A+1: that money serves ante A+1).
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from balatro_env.data.trajectory import dataset_files, read_trajectory

RENT = 3  # G.GAME.rental_rate
GOLD_BASE = (300, 1000, 3200, 9000, 25000, 60000, 110000, 200000)  # get_blind_amount, scaling 3 (Green+ stakes)

# xMult jokers by how reliably they multiply a pair-family/flush hand.
XM_RELIABLE = {
    "j_cavendish", "j_card_sharp", "j_photograph", "j_triboulet", "j_baron", "j_ramen", "j_duo", "j_trio",
    "j_family", "j_order", "j_tribe",
}
XM_GROWTH = {
    "j_hologram", "j_constellation", "j_campfire", "j_lucky_cat", "j_vampire", "j_madness", "j_glass",
    "j_steel_joker", "j_obelisk", "j_yorick", "j_caino", "j_throwback", "j_hit_the_road",
}
XM_COND = {
    "j_acrobat", "j_idol", "j_bloodstone", "j_ancient", "j_flower_pot", "j_seeing_double", "j_drivers_license",
    "j_loyalty_card", "j_baseball", "j_stencil", "j_blackboard",
}
XM_ALL = XM_RELIABLE | XM_GROWTH | XM_COND
HAND_GATED = {"j_duo": "Pair", "j_trio": "Three of a Kind", "j_family": "Four of a Kind", "j_order": "Straight",
              "j_tribe": "Flush"}
CONTAINS = {  # hand -> hands it contains (for hand-gated xMults)
    "Pair": {"Pair"}, "Two Pair": {"Pair", "Two Pair"}, "Three of a Kind": {"Pair", "Three of a Kind"},
    "Full House": {"Pair", "Two Pair", "Three of a Kind", "Full House"},
    "Four of a Kind": {"Pair", "Two Pair", "Three of a Kind", "Four of a Kind"},
    "Straight": {"Straight"}, "Flush": {"Flush"}, "Straight Flush": {"Straight", "Flush", "Straight Flush"},
    "Five of a Kind": {"Pair", "Two Pair", "Three of a Kind", "Four of a Kind", "Five of a Kind"},
    "Flush House": {"Pair", "Two Pair", "Three of a Kind", "Full House", "Flush", "Flush House"},
    "Flush Five": {"Pair", "Two Pair", "Three of a Kind", "Four of a Kind", "Five of a Kind", "Flush", "Flush Five"},
    "High Card": set(),
}
PLANET_FOR = {"Pair": "c_mercury", "Two Pair": "c_uranus", "Three of a Kind": "c_venus", "Straight": "c_saturn",
              "Flush": "c_jupiter", "Full House": "c_earth", "Four of a Kind": "c_mars", "High Card": "c_pluto",
              "Straight Flush": "c_neptune", "Five of a Kind": "c_planet_x", "Flush House": "c_ceres",
              "Flush Five": "c_eris"}
PAIR_FAMILY = {"Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind", "Five of a Kind"}


def xm_class(key: str | None) -> str | None:
    if key in XM_RELIABLE:
        return "reliable"
    if key in XM_GROWTH:
        return "growth"
    if key in XM_COND:
        return "cond"
    return None


def stickers(item: dict) -> str:
    s = [n for n in ("eternal", "perishable", "rental") if item.get(n)]
    return "+".join(s) if s else "clean"


def main_hand(obs: dict) -> tuple[str | None, int]:
    """Most played hand (ties: higher level) and its level; (None, 0) before the first play."""
    levels = obs.get("hand_levels") or {}
    best = None
    for name, hl in levels.items():
        played = hl.get("played") or 0
        if played <= 0:
            continue
        cand = (played, hl.get("level") or 1, name)
        if best is None or cand > best:
            best = cand
    if best is None:
        return None, 0
    return best[2], int(best[1])


def hand_family(h: str | None) -> str:
    if h is None:
        return "none"
    if h in PAIR_FAMILY:
        return "pair-family"
    if "Flush" in h:
        return "flush"
    if h == "Straight":
        return "straight"
    return "high-card"


def xm_counts(obs: dict) -> dict[str, int]:
    """Active (not debuffed) xMult jokers by class; polychrome editions count as an extra reliable x1.5.
    Hand-gated xMults whose hand the main hand does not contain are counted as `cond`."""
    mh, _ = main_hand(obs)
    out = Counter()
    for j in obs.get("jokers") or []:
        if j.get("debuff") or j.get("facing") == "back":
            continue
        c = xm_class(j.get("key"))
        if c == "reliable" and j.get("key") in HAND_GATED and mh and HAND_GATED[j["key"]] not in CONTAINS.get(mh, set()):
            c = "cond"
        if c:
            out[c] += 1
        if j.get("edition") == "polychrome":
            out["reliable"] += 1
    return {"reliable": out["reliable"], "growth": out["growth"], "cond": out["cond"]}


def interest_of(obs: dict) -> int:
    m = obs.get("money") or 0
    if obs.get("no_interest") or m < 5:
        return 0
    cap = (obs.get("interest_cap") or 25) // 5
    return min(m // 5, cap) * (obs.get("interest_amount") or 1)


def blind_kind(key: str | None) -> str:
    return {"bl_small": "Small", "bl_big": "Big"}.get(key or "", "Boss")


@dataclass
class Round:
    ante: int
    rnd: int
    kind: str
    name: str
    needed: int
    dollars: int
    xm: dict
    jokers: int
    main: str | None
    main_level: int
    scores: list = field(default_factory=list)  # (hand type, score, hands_remaining_before)
    scored: int = 0
    cleared: bool | None = None


@dataclass
class Run:
    key: str
    seed: str
    port: Any
    model: str
    outcome: str
    finished: bool
    clients: Counter = field(default_factory=Counter)  # meta.client (cli.py@<sha>) -> steps
    started_ms: int = 0
    client_first_ms: dict = field(default_factory=dict)  # client -> first step ts_ms in this run
    rounds: list = field(default_factory=list)
    ante_start: dict = field(default_factory=dict)
    money: list = field(default_factory=list)  # (ante, category, amount)
    views: list = field(default_factory=list)
    packs: list = field(default_factory=list)
    jokers: dict = field(default_factory=dict)  # id -> acquisition record
    small_decisions: list = field(default_factory=list)  # (ante, 'play'|'skip', tag)
    skips: list = field(default_factory=list)  # (ante, on_deck, tag)
    cashouts: list = field(default_factory=list)  # (ante, money_before, interest, blind, hands, other)
    rerolls: list = field(default_factory=list)  # (ante, cost)

    @property
    def max_ante(self) -> int:
        return max([r.ante for r in self.rounds] or [1])

    @property
    def death(self) -> Round | None:
        if self.outcome == "loss" and self.rounds and self.rounds[-1].cleared is False:
            return self.rounds[-1]
        return None


def is_player_gold(traj) -> bool:
    sp, sm = traj.start_params, traj.start_meta
    agent = str(sm.get("agent") or "")
    return (sp.get("stake") == 8 and not agent.startswith(("test-", "replay")) and not sm.get("replay_of")
            and not str(sp.get("seed") or "").upper().startswith("FUZZ") and bool(traj.steps))


def item_at(obs: dict, area: str, idx: Any) -> dict:
    lst = ((obs.get("shop") or {}).get(area) or []) if area != "pack" else ((obs.get("pack") or {}).get("cards") or [])
    if isinstance(idx, int) and 1 <= idx <= len(lst):
        return lst[idx - 1]
    return {}


def analyse(traj) -> Run:
    steps = traj.steps
    models = Counter((s.get("meta") or {}).get("model") for s in steps if (s.get("meta") or {}).get("model"))
    run = Run(key=traj.key, seed=traj.start_params.get("seed"), port=(traj.header or {}).get("port"),
              model=(models.most_common(1)[0][0] if models else "?"), outcome=traj.outcome,
              finished=traj.end is not None,
              clients=Counter((s.get("meta") or {}).get("client") or "?" for s in steps),
              started_ms=int((traj.header or {}).get("started_at_ms") or 0))
    for s in steps:
        c = (s.get("meta") or {}).get("client") or "?"
        run.client_first_ms.setdefault(c, int(s.get("ts_ms") or 0))
    final_obs = (traj.end or {}).get("final_obs")
    cur: Round | None = None
    view = None
    pack = None
    owned: dict[int, dict] = {}
    for i, st in enumerate(steps):
        obs = st["obs"]
        nxt = steps[i + 1]["obs"] if i + 1 < len(steps) else final_obs
        act = st["action"]["type"]
        params = st["action"].get("params") or {}
        phase = obs.get("phase")
        ante = obs.get("ante") or 1
        prev_act = steps[i - 1]["action"]["type"] if i else None

        # --- joker ownership (acquisitions, rent, perish, exit)
        ids_now = {j["id"]: j for j in obs.get("jokers") or [] if j.get("id") is not None}
        for jid, j in ids_now.items():
            if jid not in owned:
                src = {"SHOP_BUY": "shop", "SELECT_PACK_CARD": "pack", "SELECT_BLIND": "created",
                       "USE_CONSUMABLE": "consumable"}.get(prev_act or "", "other")
                paid = 0
                if prev_act == "SHOP_BUY":
                    paid = -((obs.get("money") or 0) - (steps[i - 1]["obs"].get("money") or 0))
                owned[jid] = run.jokers[jid] = {
                    "key": j.get("key"), "name": j.get("name"), "sticker": stickers(j), "ante": ante, "src": src,
                    "paid": paid, "rounds": 0, "rent": 0, "perished": False, "exit": None, "edition": j.get("edition"),
                }
            rec = owned[jid]
            if j.get("perishable") and j.get("debuff") and (j.get("perish_tally") in (0, None)):
                rec["perished"] = True
        for jid in list(owned):
            if jid not in ids_now:
                owned[jid]["exit"] = prev_act
                del owned[jid]

        # --- ante start snapshot
        if phase == "BLIND_SELECT" and ante not in run.ante_start:
            mh, ml = main_hand(obs)
            xm = xm_counts(obs)
            run.ante_start[ante] = {
                "money": obs.get("money") or 0, "jokers": len(obs.get("jokers") or []), "xm": xm,
                "xm_rg": xm["reliable"] + xm["growth"], "xm_any": sum(xm.values()), "main": mh, "main_level": ml,
                "rentals": sum(1 for j in obs.get("jokers") or [] if j.get("rental")),
                "levels_total": sum((hl.get("level") or 1) - 1 for hl in (obs.get("hand_levels") or {}).values()),
            }

        # --- blind decisions
        if phase == "BLIND_SELECT" and act in ("SELECT_BLIND", "SKIP_BLIND"):
            bs = obs.get("blind_select") or {}
            od = bs.get("on_deck")
            tag = ((bs.get("choices") or {}).get(od) or {}).get("tag")
            if od == "Small":
                run.small_decisions.append((ante, "skip" if act == "SKIP_BLIND" else "play", tag))
            if act == "SKIP_BLIND":
                run.skips.append((ante, od, tag))

        # --- rounds and hand scores
        if phase == "SELECTING_HAND":
            b = obs.get("blind") or {}
            rk = (ante, obs.get("round"))
            if cur is None or (cur.ante, cur.rnd) != rk:
                mh, ml = main_hand(obs)
                cur = Round(ante=ante, rnd=obs.get("round"), kind=blind_kind(b.get("key")), name=b.get("name") or "?",
                            needed=b.get("chips_needed") or 0, dollars=b.get("dollars") or 0, xm=xm_counts(obs),
                            jokers=len(obs.get("jokers") or []), main=mh, main_level=ml)
                run.rounds.append(cur)
            if act == "PLAY_HAND" and nxt is not None:
                before = b.get("chips_scored") or 0
                if nxt.get("phase") == "SELECTING_HAND":
                    after = (nxt.get("blind") or {}).get("chips_scored") or 0
                elif nxt.get("phase") == "ROUND_EVAL":
                    after = nxt.get("chips") or 0
                else:
                    after = (nxt.get("blind") or {}).get("chips_scored")
                    if after is None:
                        after = nxt.get("chips") or before
                lv0 = obs.get("hand_levels") or {}
                lv1 = nxt.get("hand_levels") or {}
                htype = next((h for h in lv1 if (lv1[h].get("played") or 0) > ((lv0.get(h) or {}).get("played") or 0)), None)
                cur.scores.append((htype, max(0, after - before), obs.get("hands_remaining")))
                cur.scored = after
            if nxt is not None and nxt.get("phase") == "ROUND_EVAL":
                cur.cleared = True
                rentals = [j for j in obs.get("jokers") or [] if j.get("rental")]
                rent = RENT * len(rentals)
                for j in rentals:
                    if j.get("id") in owned:
                        owned[j["id"]]["rent"] += RENT
                for j in obs.get("jokers") or []:
                    if j.get("id") in owned:
                        owned[j["id"]]["rounds"] += 1
                delta = (nxt.get("money") or 0) - (obs.get("money") or 0)
                run.money.append((cur.ante, "rent", -rent))
                run.money.append((cur.ante, "in_round", delta + rent))
            elif nxt is not None and nxt.get("phase") == "GAME_OVER":
                cur.cleared = False
                cur.scored = max(cur.scored, (nxt.get("blind") or {}).get("chips_scored") or 0)
            elif nxt is not None:
                run.money.append((cur.ante, "in_round", (nxt.get("money") or 0) - (obs.get("money") or 0)))
            continue

        if nxt is None:
            continue
        delta = (nxt.get("money") or 0) - (obs.get("money") or 0)

        if act == "CASH_OUT":
            ra = cur.ante if cur else ante
            interest = interest_of(obs)
            blind_d = cur.dollars if cur else 0
            hands = obs.get("hands_remaining") or 0
            other = delta - interest - blind_d - hands
            run.cashouts.append((ra, obs.get("money") or 0, interest, blind_d, hands, other))
            run.money += [(ra, "blind_reward", blind_d), (ra, "interest", interest), (ra, "hands_left", hands),
                          (ra, "cashout_jokers_tags", other)]
            continue

        # --- shop views
        if phase == "SHOP":
            if view is None or prev_act in ("CASH_OUT", "SHOP_REROLL") or view["ante"] != ante or prev_act is None:
                mh, ml = main_hand(obs)
                sh = obs.get("shop") or {}
                items = sh.get("jokers") or []
                view = {
                    "ante": ante, "reroll": prev_act == "SHOP_REROLL", "money": obs.get("money") or 0, "main": mh,
                    "jokers": [{"key": it.get("key"), "cls": xm_class(it.get("key")), "cost": it.get("cost"),
                                "sticker": stickers(it), "edition": it.get("edition")}
                               for it in items if it.get("set") == "Joker"],
                    "cons": [it.get("key") for it in items if it.get("set") in ("Planet", "Tarot", "Spectral")],
                    "boosters": [b.get("kind") for b in sh.get("boosters") or []],
                    "xm_owned": sum(xm_counts(obs).values()), "bought": [],
                }
                run.views.append(view)
            if act in ("SHOP_BUY", "SHOP_BUY_AND_USE"):
                it = item_at(obs, "jokers", params.get("slot"))
                view["bought"].append(it.get("key"))

        # --- packs
        if phase == "PACK_OPENING":
            if prev_act != "SELECT_PACK_CARD" or pack is None:
                pk = obs.get("pack") or {}
                mh, _ = main_hand(obs)
                pack = {"ante": ante, "kind": pk.get("kind"), "from_shop": prev_act == "SHOP_BUY_BOOSTER",
                        "cards": [(c.get("key"), c.get("set"), stickers(c)) for c in pk.get("cards") or []],
                        "main": mh, "picked": []}
                run.packs.append(pack)
            if act == "SELECT_PACK_CARD":
                pack["picked"].append(item_at(obs, "pack", params.get("index")).get("key"))

        # --- money flows
        if act == "SHOP_BUY":
            it = item_at(obs, "jokers", params.get("slot"))
            cat = {"Joker": "joker", "Planet": "planet", "Tarot": "tarot", "Spectral": "spectral"}.get(it.get("set"), "card")
            run.money.append((ante, "buy_" + cat, delta))
        elif act == "SHOP_BUY_AND_USE":
            it = item_at(obs, "jokers", params.get("slot"))
            cost = it.get("cost") or 0
            cat = {"Planet": "planet", "Tarot": "tarot", "Spectral": "spectral"}.get(it.get("set"), "card")
            run.money += [(ante, "buy_" + cat, -cost), (ante, "consumable_effect", delta + cost)]
        elif act == "SHOP_BUY_BOOSTER":
            it = item_at(obs, "boosters", params.get("slot"))
            run.money.append((ante, "buy_pack", delta))
            run.money.append((ante, "pack_kind:" + str(it.get("kind")), delta))
        elif act == "SHOP_BUY_VOUCHER":
            run.money.append((ante, "buy_voucher", delta))
        elif act == "SHOP_REROLL":
            run.money.append((ante, "reroll", delta))
            run.rerolls.append((ante, -delta))
        elif act == "SELL_JOKER":
            run.money.append((ante, "sell_joker", delta))
        elif act == "SELL_CONSUMABLE":
            run.money.append((ante, "sell_consumable", delta))
        elif act in ("USE_CONSUMABLE", "SELECT_PACK_CARD", "SKIP_PACK"):
            run.money.append((ante, "consumable_effect", delta))
        elif act in ("SELECT_BLIND", "SKIP_BLIND"):
            run.money.append((ante, "tags_blind_select", delta))
        elif delta:
            run.money.append((ante, "other:" + act, delta))
    return run


def postmortem_model(repo: Path, port: Any, seed: str) -> str | None:
    """Model from the post-mortem title `# Run <seed> (port <port>, <model>) - ...` (steps carry no meta.model)."""
    path = repo / "docs" / "runs" / f"{port}_{seed}.md"
    try:
        first = path.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return None
    m = re.search(r"\(port \d+, ([^)]+)\)", first)
    return m.group(1) if m else None


def load_runs(root: Path) -> list[Run]:
    runs = []
    repo = root.resolve().parent
    for path in dataset_files(root):
        traj = read_trajectory(path)
        if traj.read_error or not is_player_gold(traj):
            continue
        run = analyse(traj)
        if run.model == "?":
            run.model = postmortem_model(repo, run.port, run.seed) or "?"
        runs.append(run)
    return runs


# ---------------------------------------------------------------- formatting helpers
def md(headers: list[str], rows: list[list[Any]]) -> str:
    def f(v):
        if isinstance(v, float):
            return f"{v:.2f}" if abs(v) < 10 else f"{v:.0f}"
        return "" if v is None else str(v)
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(f(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def pct(a, b):
    return f"{100 * a / b:.0f}% ({a}/{b})" if b else "-"


def kfmt(x):
    if x is None:
        return "-"
    return f"{x / 1000:.1f}k" if x >= 1000 else f"{x:.0f}"


# ---------------------------------------------------------------- report sections
def sec_runs(runs: list[Run]) -> str:
    rows = []
    for r in sorted(runs, key=lambda r: (-r.max_ante, r.key)):
        d = r.death
        last = r.ante_start.get(r.max_ante, {})
        rows.append([r.key.split("_")[1] + "_" + r.seed, r.model.replace("claude-", ""), r.outcome if r.finished else "live",
                     f"{d.ante} {d.kind}" if d else f"a{r.max_ante}",
                     f"{d.scored / d.needed:.2f}" if d and d.needed else "",
                     d.name if d else "", last.get("money"), last.get("jokers"), last.get("xm_any"),
                     f"{last.get('main')} L{last.get('main_level')}" if last.get("main") else "-",
                     len([s for s in r.small_decisions if s[1] == "skip"])])
    return md(["run", "model", "outcome", "death", "scored/needed", "blind", "$@last ante", "jokers", "xMult", "main hand",
               "small skips"], rows)


def sec_deaths(runs: list[Run]) -> str:
    fin = [r for r in runs if r.death]
    by_ante = Counter(r.death.ante for r in fin)
    by_kind = Counter((r.death.ante, r.death.kind) for r in fin)
    rows = []
    for a in sorted(by_ante):
        ds = [r.death for r in fin if r.death.ante == a]
        rows.append([a, by_ante[a], by_kind[(a, "Small")], by_kind[(a, "Big")], by_kind[(a, "Boss")],
                     f"{med([d.scored / d.needed for d in ds]):.2f}", f"{min(d.scored / d.needed for d in ds):.2f}",
                     f"{max(d.scored / d.needed for d in ds):.2f}",
                     ", ".join(sorted({d.name for d in ds if d.kind == 'Boss'}))])
    near = sum(1 for r in fin if r.death.scored / r.death.needed >= 0.85)
    t = md(["death ante", "runs", "Small", "Big", "Boss", "median scored/needed", "min", "max", "bosses"], rows)
    boss = defaultdict(lambda: [0, 0, []])
    for r in runs:
        for rd in r.rounds:
            if rd.kind == "Boss" and rd.cleared is not None:
                b = boss[rd.name]
                b[0] += 1
                if rd.cleared is False:
                    b[1] += 1
                    b[2].append(rd.scored / rd.needed if rd.needed else 0)
    brows = [[name, b[0], b[1], pct(b[1], b[0]), f"{med(b[2]):.2f}" if b[2] else ""]
             for name, b in sorted(boss.items(), key=lambda x: (-x[1][1], -x[1][0]))]
    rk = defaultdict(lambda: [0, 0])
    for r in runs:
        for rd in r.rounds:
            if rd.cleared is not None:
                rk[(rd.ante, rd.kind)][0] += 1
                rk[(rd.ante, rd.kind)][1] += rd.cleared is False
    krows = [[a, k, n, pct(d, n)] for (a, k), (n, d) in sorted(rk.items(), key=lambda x: (x[0][0], ["Small", "Big", "Boss"].index(x[0][1])))]
    return (t + f"\n\nFinished losses: {len(fin)}; near misses (>=85% of target): {near}; "
            f"blowouts (<50%): {sum(1 for r in fin if r.death.scored / r.death.needed < 0.5)}.\n\n"
            "Death rate per blind played:\n\n" + md(["ante", "blind", "played", "lost"], krows) +
            "\n\nBosses faced (all runs):\n\n" + md(["boss", "faced", "lost", "loss rate", "median scored/needed when lost"], brows))


def sec_first_xmult(runs: list[Run]) -> str:
    """Depth by the ante of the first reliable/growth xMult acquired (shop, pack or created)."""
    groups = defaultdict(list)
    for r in runs:
        if not r.finished or r.max_ante < 2:
            continue
        a = min([j["ante"] for j in r.jokers.values() if xm_class(j["key"]) in ("reliable", "growth")] or [99])
        groups["ante 1-2" if a <= 2 else "ante 3" if a == 3 else "ante 4+" if a < 99 else "never"].append(r)
    rows = []
    for lab in ("ante 1-2", "ante 3", "ante 4+", "never"):
        g = groups.get(lab, [])
        if g:
            rows.append([lab, len(g), mean([r.max_ante for r in g]), pct(sum(1 for r in g if r.max_ante >= 5), len(g)),
                         max(r.max_ante for r in g)])
    fill = defaultdict(list)
    for r in runs:
        if r.finished and 4 in r.ante_start:
            fill["6+ jokers at ante 4" if r.ante_start[4]["jokers"] >= 6 else "<6 jokers at ante 4"].append(r.max_ante)
    fl = "; ".join(f"{k}: n={len(v)}, mean final ante {mean(v):.1f}" for k, v in sorted(fill.items()))
    return md(["first reliable/growth xMult", "runs (reached ante 2)", "mean final ante", "reached ante 5", "best"], rows) + \
        f"\n\n{fl}."


def sec_ante_profile(runs: list[Run]) -> str:
    rows = []
    fin = [r for r in runs if r.finished]
    for a in range(1, 9):
        reach = [r for r in fin if a in r.ante_start]
        if not reach:
            continue
        died = [r for r in reach if r.death and r.death.ante == a]
        surv = [r for r in reach if r.max_ante > a or (r.death is None and r.outcome == "win")]
        for label, grp in (("died here", died), ("cleared", surv)):
            if not grp:
                continue
            s = [r.ante_start[a] for r in grp]
            rows.append([a, label, len(grp), med([x["money"] for x in s]), med([x["jokers"] for x in s]),
                         mean([x["xm_rg"] for x in s]), mean([x["xm_any"] for x in s]),
                         med([x["main_level"] for x in s]), med([x["levels_total"] for x in s]),
                         mean([x["rentals"] for x in s])])
    return md(["ante", "fate", "n", "median $", "median jokers", "mean xMult (reliable+growth)", "mean xMult (any)",
               "median main lvl", "median total levels", "mean rentals"], rows)


ECON_IN = ["blind_reward", "interest", "hands_left", "cashout_jokers_tags", "in_round", "sell_joker", "sell_consumable",
           "consumable_effect", "tags_blind_select"]
ECON_OUT = ["buy_joker", "buy_planet", "buy_tarot", "buy_spectral", "buy_card", "buy_pack", "buy_voucher", "reroll",
            "rent"]


def sec_economy(runs: list[Run]) -> str:
    per = defaultdict(lambda: defaultdict(float))  # ante -> cat -> sum
    run_antes = defaultdict(set)
    for r in runs:
        for a, cat, amt in r.money:
            per[a][cat] += amt
            run_antes[a].add(r.key)
    rows_in, rows_out = [], []
    for a in sorted(per):
        n = len(run_antes[a])
        rows_in.append([a, n] + [per[a][c] / n for c in ECON_IN] + [sum(per[a][c] for c in ECON_IN) / n])
        rows_out.append([a, n] + [-per[a][c] / n for c in ECON_OUT] + [-sum(per[a][c] for c in ECON_OUT) / n])
    tin = md(["ante", "runs", "blind", "interest", "hands left", "cash-out jokers/tags", "in-round (jokers/cards)",
              "sell jokers", "sell cons.", "consumable effects", "skip tags", "total in"], rows_in)
    tout = md(["ante", "runs", "jokers", "planets", "tarots", "spectrals", "cards", "packs", "vouchers", "rerolls",
               "rent", "total out"], rows_out)
    tot = defaultdict(float)
    for r in runs:
        for a, cat, amt in r.money:
            tot[cat] += amt
    income = sum(tot[c] for c in ECON_IN)
    spend = -sum(tot[c] for c in ECON_OUT)
    share = ", ".join(f"{c} {100 * tot[c] / income:.0f}%" for c in ECON_IN if tot[c] > 0)
    sshare = ", ".join(f"{c} {100 * -tot[c] / spend:.0f}%" for c in ECON_OUT if tot[c] < 0)
    packs = ", ".join(f"{c.split(':')[1]} ${-v:.0f}" for c, v in sorted(tot.items()) if c.startswith("pack_kind:"))
    return (f"Mean $ per run that played the ante.\n\n**Income**\n\n{tin}\n\n**Spending**\n\n{tout}\n\n"
            f"All runs: income ${income:.0f} ({share}).\n\nSpending ${spend:.0f} ({sshare}). Packs by kind: {packs}.")


def sec_interest(runs: list[Run]) -> str:
    rows = []
    by = defaultdict(list)
    for r in runs:
        for c in r.cashouts:
            by[c[0]].append(c)
    for a in sorted(by):
        cs = by[a]
        rows.append([a, len(cs), pct(sum(1 for c in cs if c[2] > 0), len(cs)), pct(sum(1 for c in cs if c[2] >= 5), len(cs)),
                     mean([c[2] for c in cs]), med([c[1] for c in cs])])
    allc = [c for cs in by.values() for c in cs]
    return md(["ante", "cash-outs", "interest > 0", "interest = $5 (cap)", "mean interest $", "median $ at cash-out"], rows) + \
        f"\n\nOverall: interest earned in {pct(sum(1 for c in allc if c[2] > 0), len(allc))} of cash-outs, capped in " \
        f"{pct(sum(1 for c in allc if c[2] >= 5), len(allc))}."


def sec_stickers(runs: list[Run]) -> str:
    rows = []
    recs = [(r, j) for r in runs for j in r.jokers.values() if j["src"] in ("shop", "pack")]
    for st in ("clean", "eternal", "perishable", "rental", "eternal+rental", "perishable+rental", "eternal+perishable"):
        g = [j for _, j in recs if j["sticker"] == st]
        if not g:
            continue
        xm = sum(1 for j in g if xm_class(j["key"]))
        rows.append([st, len(g), xm, mean([j["paid"] for j in g if j["src"] == "shop"]), mean([j["rounds"] for j in g]),
                     sum(j["rent"] for j in g), mean([j["rent"] for j in g]),
                     sum(1 for j in g if j["perished"]), sum(1 for j in g if j["exit"] == "SELL_JOKER")])
    rent_by_run = sorted(((sum(j["rent"] for j in r.jokers.values()), r) for r in runs), key=lambda x: -x[0])
    tot_rent = sum(x[0] for x in rent_by_run)
    n_rent = sum(1 for x in rent_by_run if x[0] > 0)
    worst = ", ".join(f"{r.seed} ${v} (a{r.max_ante})" for v, r in rent_by_run[:5] if v)
    return md(["sticker", "acquired", "of which xMult", "mean $ paid (shop)", "mean rounds held", "total rent $",
               "mean rent/joker $", "perished while held", "sold"], rows) + \
        f"\n\nRent: ${tot_rent} over {len(runs)} runs ({n_rent} runs paid any); top: {worst}."


def sec_supply(runs: list[Run]) -> str:
    rows = []
    by = defaultdict(list)
    for r in runs:
        for v in r.views:
            by[v["ante"]].append(v)
    allv = []
    for a in sorted(by):
        vs = by[a]
        allv += vs
        n = len(vs)
        any_x = [v for v in vs if any(j["cls"] for j in v["jokers"])]
        rg = [v for v in vs if any(j["cls"] in ("reliable", "growth") for j in v["jokers"])]
        rg_clean = [v for v in vs if any(j["cls"] in ("reliable", "growth") and j["sticker"] in ("clean", "eternal")
                                         for j in v["jokers"])]
        prices = [j["cost"] for v in vs for j in v["jokers"] if j["cls"] in ("reliable", "growth")]
        main_pl = [v for v in vs if v["main"] and PLANET_FOR.get(v["main"]) in v["cons"]]
        cel = [v for v in vs if "Celestial" in v["boosters"]]
        buf = [v for v in vs if "Buffoon" in v["boosters"]]
        just = [v for v in vs if "c_justice" in v["cons"]]
        p = len(rg) / n
        rows.append([a, n, pct(len(any_x), n), pct(len(rg), n), pct(len(rg_clean), n),
                     f"{(1 / p - 1):.1f}" if p else "inf", med(prices), pct(len(main_pl), n), pct(len(cel), n),
                     pct(len(buf), n), pct(len(just), n)])
    t = md(["ante", "shop views", "any xMult", "reliable/growth xMult", "...without rental/perishable",
            "E[rerolls] to see r/g xMult", "median r/g price", "main-hand planet", "Celestial pack", "Buffoon pack",
            "Justice"], rows)
    # which xMults appear, sticker rates
    offers = Counter()
    sticker = defaultdict(Counter)
    for v in allv:
        for j in v["jokers"]:
            if j["cls"]:
                offers[j["key"]] += 1
                sticker[j["key"]][j["sticker"]] += 1
    tops = ", ".join(f"{k[2:]} {n} ({100 * (n - sticker[k]['clean']) / n:.0f}% stickered)" for k, n in offers.most_common(14))
    njok = sum(len(v["jokers"]) for v in allv)
    st_all = Counter(j["sticker"] for v in allv for j in v["jokers"])
    st_line = ", ".join(f"{k} {100 * c / njok:.0f}%" for k, c in st_all.most_common())
    # packs
    prow = []
    pk_by = defaultdict(list)
    for r in runs:
        for p in r.packs:
            pk_by[p["kind"]].append(p)
    for kind, ps in sorted(pk_by.items(), key=lambda x: str(x[0])):
        n = len(ps)
        if kind == "Buffoon":
            hit = sum(1 for p in ps if any(xm_class(c[0]) in ("reliable", "growth") for c in p["cards"]))
            anyx = sum(1 for p in ps if any(xm_class(c[0]) for c in p["cards"]))
            took = sum(1 for p in ps if any(k for k in p["picked"]))
            prow.append([kind, n, f"r/g xMult in pack {pct(hit, n)}; any xMult {pct(anyx, n)}; took a joker {pct(took, n)}"])
        elif kind == "Celestial":
            hit = sum(1 for p in ps if p["main"] and any(c[0] == PLANET_FOR.get(p["main"]) for c in p["cards"]))
            took = sum(1 for p in ps if p["main"] and PLANET_FOR.get(p["main"]) in p["picked"])
            small = [p for p in ps if len(p["cards"]) <= 3]
            big = [p for p in ps if len(p["cards"]) > 3]
            hs = sum(1 for p in small if p["main"] and any(c[0] == PLANET_FOR.get(p["main"]) for c in p["cards"]))
            hb = sum(1 for p in big if p["main"] and any(c[0] == PLANET_FOR.get(p["main"]) for c in p["cards"]))
            prow.append([kind, n, f"main-hand planet offered {pct(hit, n)} (3-card {pct(hs, len(small))}, 5-card {pct(hb, len(big))}); "
                                  f"taken {pct(took, n)}"])
        elif kind == "Arcana":
            hit = sum(1 for p in ps if any(c[0] == "c_justice" for c in p["cards"]))
            prow.append([kind, n, f"Justice offered {pct(hit, n)}"])
        else:
            prow.append([kind, n, f"took something {pct(sum(1 for p in ps if p['picked']), n)}"])
    # $ per xMult sighting: a reroll buys one new view; a Buffoon pack buys one look at 2-4 jokers.
    rrv = [v for v in allv if v["reroll"]]
    rr_cost = mean([c for r in runs for _, c in r.rerolls if c > 0]) or 5
    bufs = [p for r in runs for p in r.packs if p["kind"] == "Buffoon" and p["from_shop"]]
    buf_cost = (-sum(a for r in runs for _, c, a in r.money if c == "pack_kind:Buffoon") / len(bufs)) if bufs else 5
    cost_rows = []
    for lab, test in (("reliable/growth xMult", lambda k: xm_class(k) in ("reliable", "growth")), ("any xMult", xm_class)):
        pr = sum(1 for v in rrv if any(test(j["key"]) for j in v["jokers"])) / len(rrv) if rrv else 0
        pb = sum(1 for p in bufs if any(test(c[0]) for c in p["cards"])) / len(bufs) if bufs else 0
        cost_rows.append([lab, f"{100 * pr:.0f}% of {len(rrv)}", f"${rr_cost / pr:.0f}" if pr else "inf",
                          f"{100 * pb:.0f}% of {len(bufs)}", f"${buf_cost / pb:.0f}" if pb else "inf"])
    ct = md(["target", "per reroll (all antes)", f"$ per sighting (reroll ~${rr_cost:.1f})", "per bought Buffoon pack",
             f"$ per sighting (pack ~${buf_cost:.1f})"], cost_rows)
    return (t + f"\n\nShop joker stickers (all offers, n={njok}): {st_line}.\n\nMost offered xMults: {tops}.\n\n"
            + md(["pack kind", "opened", "contents"], prow) + "\n\nCost of seeing an xMult:\n\n" + ct)


def sec_sightings(runs: list[Run]) -> str:
    """Every reliable/growth xMult a run saw (initial or rerolled shop view, any pack) and whether it was taken."""
    rows = []
    stats = Counter()
    for r in runs:
        for v in r.views:
            for j in v["jokers"]:
                if j["cls"] not in ("reliable", "growth"):
                    continue
                took = j["key"] in v["bought"]
                why = "bought" if took else ("unaffordable" if (j["cost"] or 0) > v["money"] else "passed")
                stats[why] += 1
                rows.append([r.seed, r.max_ante, v["ante"], "shop", j["key"][2:], j["cost"], j["sticker"], v["money"], why])
        for p in r.packs:
            for key, _, st in p["cards"]:
                if xm_class(key) in ("reliable", "growth"):
                    why = "bought" if key in p["picked"] else "passed"
                    stats[why] += 1
                    rows.append([r.seed, r.max_ante, p["ante"], f"{p['kind']} pack", key[2:], "", st, "", why])
    seen_by = defaultdict(set)
    for r in runs:
        for v in r.views:
            if any(j["cls"] in ("reliable", "growth") for j in v["jokers"]):
                seen_by[r.key].add(v["ante"])
        for p in r.packs:
            if any(xm_class(c[0]) in ("reliable", "growth") for c in p["cards"]):
                seen_by[r.key].add(p["ante"])
    deep = [r for r in runs if r.max_ante >= 4]
    saw = sum(1 for r in deep if any(a <= 3 for a in seen_by[r.key]))
    t = md(["run", "final ante", "ante", "where", "joker", "$", "sticker", "money", "outcome"],
           sorted(rows, key=lambda x: (x[8], -x[1])))
    return t + (f"\n\nOutcomes: {dict(stats)}. Runs reaching ante 4 that saw any reliable/growth xMult by ante 3 (shop or pack): "
                f"{pct(saw, len(deep))}.")


VERSION_COLS = ["runs", "finished", "models", "mean final ante", "reached ante 3", "reached ante 4", "reached ante 5",
                "wins", "median $ at ante 3 start", "median $ at ante 4 start", "rentals bought/run", "rent $/run",
                "reroll $/run", "Buffoon $/run", "interest $/run"]


def version_metrics(g: list[Run]) -> list[Any]:
    """Outcome and spending columns (VERSION_COLS) for a group of runs; outcome/spend over finished runs only."""
    fin = [r for r in g if r.finished]
    tot = [defaultdict(float, {c: sum(a for _, cc, a in r.money if cc == c) for c in
                               ("rent", "reroll", "pack_kind:Buffoon", "interest")}) for r in fin]
    return [len(g), len(fin), ", ".join(f"{m.replace('claude-', '')} {n}" for m, n in Counter(r.model for r in g).most_common()),
            mean([r.max_ante for r in fin])] + \
        [pct(sum(1 for r in fin if r.max_ante >= a), len(fin)) for a in (3, 4, 5)] + \
        [sum(1 for r in fin if r.outcome == "win"),
         med([r.ante_start[3]["money"] for r in fin if 3 in r.ante_start]),
         med([r.ante_start[4]["money"] for r in fin if 4 in r.ante_start]),
         mean([sum(1 for j in r.jokers.values() if "rental" in j["sticker"] and j["src"] in ("shop", "pack")) for r in fin]),
         mean([-t["rent"] for t in tot]), mean([-t["reroll"] for t in tot]),
         mean([-t["pack_kind:Buffoon"] for t in tot]), mean([t["interest"] for t in tot])]


def sec_by_client(runs: list[Run]) -> str:
    """Outcomes and spending behaviour per advisor version (`meta.client` = cli.py@<sha>, the run's majority client;
    the client usually changes mid-run as cli.py is updated). Versions are ordered by their first run's start time."""
    groups = defaultdict(list)
    for r in runs:
        groups[r.clients.most_common(1)[0][0] if r.clients else "?"].append(r)
    rows = []
    for client, g in sorted(groups.items(), key=lambda x: min(r.started_ms for r in x[1])):
        first = min(r.started_ms for r in g)
        when = datetime.fromtimestamp(first / 1000).strftime("%m-%d %H:%M") if first else "?"
        rows.append([client.replace("cli.py@", ""), when, sum(1 for r in g if len(r.clients) > 1)] + version_metrics(g))
    return md(["majority client (cli.py@)", "first run", "mixed-client runs"] + VERSION_COLS, rows) + \
        "\n\nOutcome/spend columns over finished runs; seeds and models differ between versions, so compare with care."


def sec_since(runs: list[Run], sha: str) -> str:
    """Before/after split at the first step made with cli.py@<sha...>: a client counts as 'new' if it first appears at
    or after that moment; a run is 'after' when at least half its steps used new clients."""
    hits = [ms for r in runs for c, ms in r.client_first_ms.items() if c.replace("cli.py@", "").startswith(sha)]
    if not hits:
        return f"No step was made with cli.py@{sha} yet."
    cutoff = min(hits)
    first_seen = defaultdict(lambda: float("inf"))
    for r in runs:
        for c, ms in r.client_first_ms.items():
            first_seen[c] = min(first_seen[c], ms)
    groups = defaultdict(list)
    for r in runs:
        new = sum(n for c, n in r.clients.items() if first_seen[c] >= cutoff)
        share = new / max(1, sum(r.clients.values()))
        groups["after (all steps)" if share == 1 else "after (>=50% of steps)" if share >= 0.5 else
               "before (some steps after)" if share > 0 else "before (no steps after)"].append(r)
    order = ["before (no steps after)", "before (some steps after)", "after (>=50% of steps)", "after (all steps)"]
    rows = [[k] + version_metrics(groups[k]) for k in order if groups[k]]
    when = datetime.fromtimestamp(cutoff / 1000).strftime("%m-%d %H:%M")
    return (f"Cutoff: first step with cli.py@{sha} at {when}.\n\n" + md(["group"] + VERSION_COLS, rows) +
            "\n\nCaveat: young 'after' runs that already finished are mostly early deaths (survivorship); compare once "
            "the after-group has 10+ finished runs, and read the spend columns (behaviour) before the outcome columns.")


def sec_run_economy(runs: list[Run]) -> str:
    rows = []
    for r in sorted([r for r in runs if r.finished and r.max_ante >= 3], key=lambda r: -r.max_ante):
        tot = defaultdict(float)
        for _, c, a in r.money:
            tot[c] += a
        inc = sum(tot[c] for c in ECON_IN)
        rows.append([r.seed, r.max_ante, inc, tot["interest"], -tot["rent"], -tot["pack_kind:Celestial"],
                     -tot["pack_kind:Arcana"] - tot["pack_kind:Spectral"] - tot["pack_kind:Standard"],
                     -tot["pack_kind:Buffoon"], -tot["reroll"], -tot["buy_joker"], -tot["buy_planet"]])
    return md(["run", "final ante", "income", "interest", "rent", "Celestial", "Arcana/Spectral/Standard", "Buffoon",
               "rerolls", "jokers", "planets"], rows)


def sec_small_skip(runs: list[Run]) -> str:
    rows = []
    for a in range(1, 9):
        for choice in ("play", "skip"):
            ds = [(r, d) for r in runs if r.finished for d in r.small_decisions if d[0] == a and d[1] == choice]
            if not ds:
                continue
            died = sum(1 for r, _ in ds if r.death and r.death.ante == a)
            rows.append([a, choice, len(ds), pct(died, len(ds)), mean([r.max_ante for r, _ in ds]),
                         mean([r.ante_start.get(a + 1, {}).get("xm_any") for r, _ in ds])])
    t = md(["ante", "Small blind", "n", "died this ante", "mean final ante", "mean xMult at next ante"], rows)
    tags = Counter(s[2] for r in runs for s in r.skips)
    by_run = defaultdict(list)
    for r in runs:
        if r.finished and r.max_ante >= 3:
            by_run[min(3, sum(1 for d in r.small_decisions if d[1] == "skip" and d[0] <= 4))].append(r.max_ante)
    lines = ", ".join(f"{k}{'+' if k == 3 else ''} skips (ante 1-4): n={len(v)} mean final ante {mean(v):.1f}"
                      for k, v in sorted(by_run.items()))
    return t + f"\n\nTags taken: {dict(tags.most_common())}.\n\nRuns that reached ante 3, by Small skips at ante 1-4: {lines}."


def sec_reroll_vs_planet(runs: list[Run]) -> str:
    rows = []
    fin = [r for r in runs if r.finished and r.max_ante >= 3]
    for r in sorted(fin, key=lambda r: -r.max_ante):
        rr = -sum(a for an, c, a in r.money if c == "reroll" and 3 <= an <= 5)
        pl = -sum(a for an, c, a in r.money if c == "buy_planet" and 3 <= an <= 5)
        cel = -sum(a for an, c, a in r.money if c == "pack_kind:Celestial" and 3 <= an <= 5)
        jk = -sum(a for an, c, a in r.money if c == "buy_joker" and 3 <= an <= 5)
        xm_bought = sum(1 for j in r.jokers.values() if 3 <= j["ante"] <= 5 and xm_class(j["key"]) and j["src"] in ("shop", "pack"))
        ml5 = r.ante_start.get(min(r.max_ante, 5), {}).get("main_level")
        rows.append([r.seed, r.max_ante, rr, pl + cel, jk, xm_bought, ml5])
    t = md(["run", "final ante", "reroll $ a3-5", "planet+Celestial $ a3-5", "joker $ a3-5", "xMult acquired a3-5",
            "main lvl at a5 (or last)"], rows)
    # reroll conversion: views after a reroll at ante 3-5 that showed / were bought from with a r/g xMult
    rv = [v for r in runs for v in r.views if v["reroll"] and 3 <= v["ante"] <= 5]
    seen = sum(1 for v in rv if any(j["cls"] in ("reliable", "growth") for j in v["jokers"]))
    seen_any = sum(1 for v in rv if any(j["cls"] for j in v["jokers"]))
    bought = sum(1 for v in rv if any(xm_class(k) for k in v["bought"]))
    rr_cost = mean([c for r in runs for a, c in r.rerolls if 3 <= a <= 5])
    hi = [x for x in rows if x[2] > x[3]]
    lo = [x for x in rows if x[2] <= x[3]]
    return t + (f"\n\nAnte 3-5 rerolls: {len(rv)} rerolled views, a reliable/growth xMult appeared in {pct(seen, len(rv))}, "
                f"any xMult in {pct(seen_any, len(rv))}, "
                f"an xMult was bought from {pct(bought, len(rv))}; mean reroll cost ${rr_cost:.1f}. Runs spending more on rerolls than planets: "
                f"n={len(hi)} mean final ante {mean([x[1] for x in hi]) or 0:.1f}; planets >= rerolls: n={len(lo)} mean final ante "
                f"{mean([x[1] for x in lo]) or 0:.1f}.")


def sec_packs_vs_singles(runs: list[Run]) -> str:
    rows = []
    shop_j = [j for r in runs for j in r.jokers.values() if j["src"] == "shop"]
    pack_j = [j for r in runs for j in r.jokers.values() if j["src"] == "pack"]
    buf = [p for r in runs for p in r.packs if p["kind"] == "Buffoon" and p["from_shop"]]
    buf_cost = -sum(a for r in runs for _, c, a in r.money if c == "pack_kind:Buffoon")
    buf_j = sum(1 for p in buf if any(p["picked"]))
    rows.append(["shop single", len(shop_j), sum(j["paid"] for j in shop_j), mean([j["paid"] for j in shop_j]),
                 pct(sum(1 for j in shop_j if xm_class(j["key"])), len(shop_j)),
                 pct(sum(1 for j in shop_j if j["sticker"] != "clean"), len(shop_j))])
    rows.append(["Buffoon pack (bought)", buf_j, buf_cost, buf_cost / buf_j if buf_j else None,
                 pct(sum(1 for j in pack_j if xm_class(j["key"])), len(pack_j)),
                 pct(sum(1 for j in pack_j if j["sticker"] != "clean"), len(pack_j))])
    t = md(["source", "jokers acquired", "$ spent", "$ per joker", "xMult share", "stickered share"], rows)
    cel = [p for r in runs for p in r.packs if p["kind"] == "Celestial" and p["from_shop"]]
    cel_cost = -sum(a for r in runs for _, c, a in r.money if c == "pack_kind:Celestial")
    cel_main = sum(1 for p in cel if p["main"] and PLANET_FOR.get(p["main"]) in p["picked"])
    pl_single = -sum(a for r in runs for _, c, a in r.money if c == "buy_planet")
    return t + (f"\n\nBuffoon packs bought: {len(buf)} (${buf_cost:.0f}), {buf_j} yielded a joker. Celestial packs bought: "
                f"{len(cel)} (${cel_cost:.0f}), main-hand planet taken from {cel_main} -> "
                f"${(cel_cost / cel_main) if cel_main else float('nan'):.1f} per main-hand level vs $3-4 for a shop planet "
                f"(${pl_single:.0f} spent on single planets).")


def sec_score(runs: list[Run]) -> str:
    # Gold (scaling 3) ante base; Small = base, Big = 1.5x, Boss = 2x (The Wall 4x, Violet Vessel 6x).
    targets = {a + 1: {"Small": b, "Big": int(1.5 * b), "Boss": 2 * b} for a, b in enumerate(GOLD_BASE)}
    best = defaultdict(dict)  # run -> ante -> best hand score
    arche = defaultdict(lambda: defaultdict(list))
    for r in runs:
        for rd in r.rounds:
            for h, sc, hr in rd.scores:
                best[r.key][rd.ante] = max(best[r.key].get(rd.ante, 0), sc)
            if rd.scores:
                xm = rd.xm["reliable"] + rd.xm["growth"]
                lab = f"{hand_family(rd.main)}, xMult(r/g) {min(xm, 2)}{'+' if xm >= 2 else ''}"
                arche[lab][rd.ante].append(max(sc for _, sc, _ in rd.scores))
    rows = []
    prev_req = None
    for a in sorted(targets):
        boss = targets[a]["Boss"]
        req = boss / 3
        bs = [best[k][a] for k in best if a in best[k]]
        ok = sum(1 for x in bs if x >= req)
        ok2 = sum(1 for x in bs if x >= boss / 2)
        rows.append([a, kfmt(targets[a]["Small"]), kfmt(targets[a]["Big"]), kfmt(boss), kfmt(req),
                     f"x{req / prev_req:.1f}" if prev_req else "", len(bs), kfmt(med(bs)), kfmt(max(bs) if bs else None),
                     pct(ok, len(bs)), pct(ok2, len(bs))])
        prev_req = req
    t = md(["ante", "Small", "Big", "Boss", "boss/3 per hand", "growth vs prev ante", "runs", "median best hand",
            "max best hand", "best hand >= boss/3", "best hand >= boss/2"], rows)
    arows = []
    antes = sorted(targets)
    for lab in sorted(arche):
        arows.append([lab] + [f"{kfmt(med(arche[lab][a]))} (n{len(arche[lab][a])})" if arche[lab][a] else "" for a in antes])
    t2 = md(["archetype (at round start)"] + [f"a{a}" for a in antes], arows)
    # observed per-ante growth of each run's best hand
    gro = defaultdict(list)
    for k, d in best.items():
        for a in d:
            if a + 1 in d and d[a] > 0:
                gro[a + 1].append(d[a + 1] / d[a])
    g = ", ".join(f"a{a - 1}->a{a}: x{med(v):.1f} (n{len(v)})" for a, v in sorted(gro.items()))
    deep = []
    for r in runs:
        if r.max_ante >= 5:
            deep.append([r.seed, r.max_ante] + [kfmt(best[r.key].get(a)) for a in antes])
    t3 = md(["run", "final ante"] + [f"a{a}" for a in antes], sorted(deep, key=lambda x: -x[1]))
    # survival by the ante's best single hand relative to that ante's boss target (finished runs)
    thr = defaultdict(lambda: [0, 0])
    fam = defaultdict(list)
    for r in runs:
        if not r.finished:
            continue
        fam[hand_family(r.ante_start.get(r.max_ante, {}).get("main"))].append(r.max_ante)
        for a, b in best[r.key].items():
            boss = targets[a]["Boss"]
            cat = "< boss/3" if b < boss / 3 else ("boss/3 .. boss/2" if b < boss / 2 else ">= boss/2")
            thr[cat][0] += 1
            thr[cat][1] += bool(r.death and r.death.ante == a)
    t4 = md(["ante's best hand", "run-antes", "died in that ante"],
            [[c, thr[c][0], pct(thr[c][1], thr[c][0])] for c in ("< boss/3", "boss/3 .. boss/2", ">= boss/2") if thr[c][0]])
    t5 = md(["main hand family (at last ante start)", "finished runs", "reached ante 4", "mean final ante"],
            [[f, len(v), pct(sum(1 for x in v if x >= 4), len(v)), mean(v)] for f, v in sorted(fam.items())])
    return (t + "\n\nSurvival by the ante's best single hand vs that ante's boss target:\n\n" + t4 +
            "\n\n" + t5 + "\n\nMedian best single-hand score per round (round's best hand), by archetype:\n\n" + t2 +
            f"\n\nObserved median growth of a run's best hand per ante: {g}.\n\nBest hand per ante, runs reaching ante 5+:\n\n" + t3)


def report(runs: list[Run], since: str | None = None) -> str:
    fin = [r for r in runs if r.finished]
    head = (f"# Gold Stake statistics (generated by balatro_env.analysis.gold_stats)\n\n"
            f"Player Gold runs: {len(runs)} ({len(fin)} finished, {len(runs) - len(fin)} live/unfinished), "
            f"wins {sum(1 for r in fin if r.outcome == 'win')}, models {dict(Counter(r.model for r in runs))}.\n")
    secs = [("Runs", sec_runs), ("1. Deaths", sec_deaths), ("1b. Ante-start profile: died this ante vs cleared it", sec_ante_profile),
            ("1c. Depth by first reliable/growth xMult", sec_first_xmult),
            ("2. Economy per ante", sec_economy), ("2b. Interest", sec_interest), ("2c. Stickered jokers and rent", sec_stickers),
            ("2d. Money per run (runs reaching ante 3)", sec_run_economy),
            ("2e. By advisor version", sec_by_client),
            ("3. Shop and pack supply", sec_supply), ("3b. Every reliable/growth xMult seen", sec_sightings),
            ("4a. Small Blind: skip vs play", sec_small_skip),
            ("4b. Rerolls vs planets at ante 3-5", sec_reroll_vs_planet), ("4c. Packs vs singles", sec_packs_vs_singles),
            ("5. Score requirement vs achieved", sec_score)]
    if since:
        secs.insert(secs.index(("2e. By advisor version", sec_by_client)) + 1,
                    (f"2f. Before/after cli.py@{since}", lambda rs: sec_since(rs, since)))
    return head + "\n".join(f"\n## {name}\n\n{fn(runs)}\n" for name, fn in secs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_root = Path(__file__).resolve().parents[3] / "data"
    ap.add_argument("--data-dir", default=str(default_root))
    ap.add_argument("--out", help="also write the report to this file")
    ap.add_argument("--since-client", metavar="SHA", help="add a before/after split at the first step made with cli.py@SHA")
    args = ap.parse_args(argv)
    runs = load_runs(Path(args.data_dir))
    text = report(runs, args.since_client)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
