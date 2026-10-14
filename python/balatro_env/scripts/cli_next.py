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
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", ".cli_cache")
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


def _digest(d):
    """What a decision depends on: phase, money, ids of hand/jokers/consumables/shop/pack cards, blind progress."""
    ids = lambda xs: [x.get("id", x.get("index")) for x in lst(xs)]
    sh = d.get("shop") or {}
    bs = d.get("blind_select") or {}
    return json.dumps([d.get("phase"), d.get("money"), ids(d.get("hand")), ids(d.get("jokers")), ids(d.get("consumables")),
                       ids(sh.get("jokers")), ids(sh.get("boosters")), ids(sh.get("vouchers")), ids((d.get("pack") or {}).get("cards")),
                       (d.get("blind") or {}).get("chips_scored"), d.get("hands_remaining"), d.get("discards_remaining"),
                       bs.get("on_deck"), [(k, (v or {}).get("state")) for k, v in sorted((bs.get("choices") or {}).items())],
                       sh.get("reroll_cost")], default=str)


def _last_action_file():
    return os.path.join(CACHE_DIR, f"{PORT}_last_action.json")


def _note_action(d, typ):
    """Before a state-changing action: remember the decision content it must change."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(_last_action_file(), "w", encoding="utf-8") as f:
            json.dump({"step_before": d.get("step"), "sig_before": _digest(d), "type": typ, "ts": time.time(), "confirmed": False}, f)
    except Exception:
        pass


def _await_action_effect(d, timeout=5.0):
    """7809: after `sell`, a separate `shopadvise` read the pre-sell state (two settled reads agreed: the sell lands
    later) and advised selling what by then was another joker. Until the last recorded action's effect is visible
    (decision content differs from before it), keep polling; returns the fresh state."""
    try:
        with open(_last_action_file(), encoding="utf-8") as f:
            la = json.load(f)
    except Exception:
        return d
    if la.get("confirmed") or time.time() - float(la.get("ts") or 0) > 120:
        return d
    t0 = time.time()
    while _digest(d) == la.get("sig_before") and time.time() - t0 < timeout:
        time.sleep(0.2)
        d = wait_settled()
    if _digest(d) == la.get("sig_before"):
        print(f"(warning: the last {la.get('type')} is not visible in the state after {timeout:.0f}s; re-run `s` before acting)")
    else:
        la["confirmed"] = True
        try:
            with open(_last_action_file(), "w", encoding="utf-8") as f:
                json.dump(la, f)
        except Exception:
            pass
    return d


def wait_settled(timeout=30.0):
    """Poll /state until the bridge reports a settled decision point AND two reads 150 ms apart agree on the decision
    content (7803: a read right after an action sometimes showed the PRE-action state with settled=true, i.e. before the
    action's events were queued); returns the last state seen."""
    t0 = time.time()
    d = get("state")
    prev = None
    while time.time() - t0 < timeout:
        if d.get("settled"):
            dg = _digest(d)
            if dg == prev:
                return d
            prev = dg
        else:
            prev = None
        time.sleep(0.15)
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


def _stk(c):
    """Stake stickers of a joker as {eternal, perishable, perish_tally, rental}. The bridge sends flat keys; older
    observations only carried them inside `ability` or a `stickers` list/dict."""
    src = dict(c.get("ability") or {})
    st = c.get("stickers")
    if isinstance(st, dict):
        src.update(st)
    elif isinstance(st, list):
        src.update({s: True for s in st})
    src.update({k: c[k] for k in ("eternal", "perishable", "perish_tally", "rental") if k in c})
    tally = src.get("perish_tally")
    return {"eternal": bool(src.get("eternal")), "perishable": bool(src.get("perishable")),
            "perish_tally": int(tally) if isinstance(tally, (int, float)) else None, "rental": bool(src.get("rental"))}


def stickers(c):
    """Stake stickers on a joker (owned, shop or pack): eternal (never sellable), perishable (debuffed after N rounds),
    rental (-$3 per round)."""
    s = _stk(c)
    out = []
    if s["eternal"]:
        out.append("ETERNAL")
    if s["perishable"]:
        out.append("PERISHED: scores nothing, sell it" if s["perish_tally"] == 0 else f"PERISHABLE({'?' if s['perish_tally'] is None else s['perish_tally']} rounds left)")
    if s["rental"]:
        out.append("RENTAL(-$3/round)")
    if c.get("debuff") and not (s["perishable"] and s["perish_tally"] == 0):
        out.insert(0, "DEBUFFED: does nothing now")
    return f"{{{','.join(out)}}}" if out else ""


def _dead_perishable(j):
    """A perishable joker whose tally ran out: debuffed for the rest of the run (scores nothing, still sellable)."""
    s = _stk(j)
    return s["perishable"] and s["perish_tally"] == 0


def _is_scoring_cls(cls):
    """jokers that reliably add to ordinary hands; suit-, growth- and rare-condition jokers do not count"""
    return (cls in ("PLUS", "PLUS(main hand)", "PLUS(common condition)", "PLUS(fires on any pair-family hand)", "PLUS(permanent growth)")
            or cls.startswith(("PLUS(retrigger", "PLUS(<=3 cards")) or (cls.startswith("XMULT") and "conditional" not in cls))


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
        idol = (d.get("run") or {}).get("idol_card") or {}
        idol_s = f" (this round: {idol.get('rank')} of {idol.get('suit')})" if isinstance(idol, dict) and idol.get("rank") else ""
        mail = (d.get("run") or {}).get("mail_card") or {}
        extra_s = {"The Idol": idol_s, "Mail-In Rebate": f" (this round: {mail.get('rank')})" if isinstance(mail, dict) and mail.get("rank") else ""}
        print(f"Jokers ({len(jk)}/{d.get('joker_slots')}) cons_slots {d.get('consumable_slots')} hand_size {d.get('hand_size')}: " + " | ".join(f"[{j.get('index', i + 1)}] {j.get('name')}{stickers(j)} ({JOKER_DESC.get(j.get('name'), 'effect not in table')}{extra_s.get(j.get('name'), '')}) sell${j.get('sell_cost')}"
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
        if (ch.get("Boss") or {}).get("name") == "The Mouth" and any(j.get("name") == "Burglar" for j in lst(d.get("jokers"))):
            print("WARNING: The Mouth locks the first played type for the round and Burglar removes ALL discards: you cannot rebuild a type. "
                  "Sell Burglar before the boss (or lock High Card / your most frequent type with the first hand).")
        # payout timing verified in tag.lua: 'immediate' / 'new_blind_choice' tags pay right after the skip (before the Big
        # Blind); 'store_joker_*' / 'shop_*' tags pay in the NEXT SHOP, which comes only after the Big Blind is beaten.
        NOW_TAGS = {"tag_buffoon": "a free MEGA Buffoon pack opens right now (take 2 of 4 jokers before the Big Blind)",
                    "tag_top_up": "up to two free Common jokers right now (only into free joker slots)",
                    "tag_charm": "a free Mega Arcana pack right now", "tag_meteor": "a free Mega Celestial pack right now (levels before the Big Blind)",
                    "tag_ethereal": "a free Spectral pack right now"}
        LATER_TAGS = {"tag_uncommon": "a free Uncommon joker in the NEXT SHOP (after the Big Blind)", "tag_rare": "a free Rare joker in the NEXT SHOP (after the Big Blind)",
                      "tag_negative": "the next shop's joker becomes Negative (paid AFTER the Big Blind)", "tag_foil": "the next shop's joker becomes Foil (paid AFTER the Big Blind)",
                      "tag_holo": "the next shop's joker becomes Holographic (paid AFTER the Big Blind)", "tag_polychrome": "the next shop's joker becomes Polychrome (paid AFTER the Big Blind)",
                      "tag_coupon": "the next shop's jokers and packs are free (paid AFTER the Big Blind)", "tag_investment": "$25 after the boss is beaten"}
        small = ch.get("Small") or {}
        stake_n = int(d.get("stake") or 1)
        ante_n = int(d.get("ante") or 1)
        tk = str(small.get("tag_key") or "")
        n_jk = len(lst(d.get("jokers"))); free_j = int(d.get("joker_slots") or 5) - n_jk
        scoring_j = sum(1 for j in lst(d.get("jokers")) if is_scorer(d, j, main_hand(d)))
        # cash / level tags pay right after the skip (tag.lua 'immediate'): value them in dollars against a $0 Small Blind
        run_c = d.get("run") or {}
        money_n = int(d.get("money") or 0)
        cash = {"tag_handy": int(run_c.get("hands_played_total") or 0), "tag_garbage": int(run_c.get("unused_discards") or 0),
                "tag_economy": min(max(money_n, 0), 40), "tag_skip": 5 * (int(run_c.get("skips") or 0) + 1)}
        if tk in cash and cash[tk] >= 5:  # Handy/Garbage/Economy/Skip pay right after the skip (3 reports of a refused Handy)
            NOW_TAGS[tk] = f"${cash[tk]} right now (the Small Blind pays $0 at this stake)"
        orb = small.get("orbital_hand")
        if tk == "tag_orbital" and orb in (main_hand(d), "Pair", "Two Pair", "Three of a Kind", "Full House"):
            NOW_TAGS[tk] = f"+3 levels to {orb} right now"
        boss_n = (ch.get("Boss") or {}).get("name")
        if tk == "tag_boss" and boss_n in ("The Wall", "Violet Vessel", "The Needle", "The Flint", "The Arm", "The Eye", "The Mouth", "The Psychic",
                                            "The Plant", "Crimson Heart", "Cerulean Bell", "Amber Acorn", "Verdant Leaf", "The Water", "The Manacle"):
            NOW_TAGS[tk] = f"rerolls {boss_n} right now (7807's win used a Boss Tag on The Wall)"
        # The Big Blind comes BEFORE any shop, so it must be beaten with what you own plus what the tag pays right now.
        # Stake 2-3 data (2026-08-30) and Gold data (2026-10-13: 328/450 and 448/450 with zero jokers after skipping for a
        # Rare/Polychrome tag) show a jokerless deck loses the ante-1 Big Blind; a shop-time tag cannot help it.
        if tk == "tag_buffoon":
            skip_ok = free_j >= 1
        elif tk == "tag_top_up":
            skip_ok = free_j >= 1
        elif (tk in NOW_TAGS or tk in LATER_TAGS) and ante_n >= 2:
            skip_ok = scoring_j >= 2  # ante 1: only joker-now tags (the two ante-1 Big losses skipped for Polychrome/Rare)
        else:
            skip_ok = False
        riff = any(j.get("name") in ("Riff-raff", "Riff-Raff") and not j.get("debuff") for j in lst(d.get("jokers"))) and free_j >= 1
        skip_ok = skip_ok and not riff  # Riff-raff makes 2 Common jokers when a blind is SELECTED: a skip forfeits them
        weak_hand = False
        n_rent = sum(1 for j in lst(d.get("jokers")) if _stk(j)["rental"])
        # Gold: the Small pays no blind reward (~$2-3 for unused hands); its round end charges every rental $3. With rent
        # due and a wallet that still could not buy a $4 joker afterwards, the shop visit is worth nothing (7801/7804/7807)
        money_b = int(d.get("money") or 0)
        # broke: after the Small's ~$3 (and its rent) the shop could not buy a $4 joker; skip if the Big is beatable as is
        # (7804/7807: "take the shop" at $<=3 or negative money)
        big_c = int((ch.get("Big") or {}).get("chips") or 0)
        big_ok = big_c > 0 and (deck_best_est(d) or typical_est(d, main_hand(d), best=True)) * int(d.get("hands_per_round") or 3) >= big_c
        poor = (money_b + 3 - 3 * n_rent < 4) and (n_rent >= 1 or (big_ok and ante_n >= 2))
        if poor and ante_n <= 4 and tk and not riff and bs.get("on_deck") == "Small":
            skip_ok = True
            NOW_TAGS.setdefault(tk, f"the {small.get('tag')} tag (the shop after this Small would find you broke: ${d.get('money')})")
        thr = any(j.get("name") == "Throwback" and not j.get("debuff") for j in lst(d.get("jokers")))
        # a skip has no round end, so perishables do not tick: with a key scorer at <= 2 rounds left, skipping keeps it
        # alive for the boss (Main 08:xx, ~6 runs lost a perishable carrier the round before the boss)
        perish_key = any(_stk(j)["perishable"] and (_stk(j)["perish_tally"] or 9) <= 2 and not _dead_perishable(j)
                         and joker_share(d, j, main_hand(d)) >= 0.2 for j in lst(d.get("jokers")))
        thr_ok = False
        if (thr or perish_key) and not riff:
            # WINNING LINE (7807, first Gold win): with Throwback, skip Small AND Big while your round beats this ante's
            # boss with margin: +x0.25 per skip forever, the tags pay now, one blind fought per ante
            boss_c_t = int((ch.get("Boss") or {}).get("chips") or 0)
            best_t = deck_best_est(d) or typical_est(d, main_hand(d), best=True)
            # handicap bosses (The House/Fish/Mark deal face-down, Psychic/Eye/Mouth restrict plays...) need more margin
            hard_b = (ch.get("Boss") or {}).get("name") in ("The House", "The Fish", "The Mark", "The Wheel", "The Psychic", "The Eye", "The Mouth",
                                                             "The Needle", "The Water", "The Pillar", "The Serpent", "The Manacle", "The Hook",
                                                             "Crimson Heart", "Cerulean Bell", "Amber Acorn", "Verdant Leaf", "Violet Vessel", "The Wall")
            thr_ok = boss_c_t > 0 and best_t * int(d.get("hands_per_round") or 3) >= (1.6 if hard_b else 1.3) * boss_c_t
            if thr_ok and bs.get("on_deck") == "Small" and tk:
                skip_ok = True
                NOW_TAGS.setdefault(tk, f"the {small.get('tag')} tag")
        if skip_ok and tk not in NOW_TAGS and not thr_ok and ante_n >= 2:
            # EMERGENCY (best hand < 0.35 x next boss/3: 84% died) - only a tag that pays a scorer NOW is worth the skip;
            # the Small's shop is the chance to buy a multiplier (7804 skipped for Ethereal at EMERGENCY 0.13)
            nxt_s = next_ante_targets(d)
            b_e = deck_best_est(d) or typical_est(d, main_hand(d), best=True)
            if nxt_s and nxt_s[3] and b_e < 0.35 * nxt_s[3] / 3:
                skip_ok = False
                weak_hand = True
        if skip_ok and 3 <= ante_n <= 4 and not thr_ok:
            # GOLD_ANALYSIS.md: ante 3-4 skippers died 40-46% vs players 25-33%: skip only if one hand reaches boss/2
            boss_c_s = int((ch.get("Boss") or {}).get("chips") or 0)
            best_s = deck_best_est(d) or typical_est(d, main_hand(d), best=True)
            weak_hand = boss_c_s > 0 and best_s < boss_c_s / 2
            skip_ok = not weak_hand
        pay = NOW_TAGS.get(tk) or LATER_TAGS.get(tk) or f"the {small.get('tag')} tag"
        if thr:
            pay += f"; Throwback gains x0.25 forever (x{1 + 0.25 * int((d.get('run') or {}).get('skips') or 0):g} -> x{1 + 0.25 * (int((d.get('run') or {}).get('skips') or 0) + 1):g})"
        if perish_key:
            pay += "; no round end, so your perishable carrier does not tick and stays alive for the boss"
        if stake_n >= 2 and bs.get("on_deck") == "Big" and thr_ok:
            big_t = (ch.get("Big") or {}).get("tag") or "Big Blind tag"
            print(f"ADVICE: b skip   ({'Throwback' if thr else 'Perishable-carrier'} skip plan: your rounds beat this ante's boss by 1.3x+, so skip the Big too: {pay.replace(str(small.get('tag')), str(big_t)) if small.get('tag') else big_t}; "
                  f"Boss Tag rerolls a Wall/Violet boss, Garbage/Skip/Economy pay money for the post-boss shop. The boss is never skipped.)")
        elif stake_n >= 2 and bs.get("on_deck") == "Small" and (ante_n <= 4 or thr_ok) and skip_ok:
            gold = f" Skipping also avoids one round-end ({sum(1 for j in lst(d.get('jokers')) if _stk(j)['rental'])} rental charge(s), one perishable tick)." if stake_n >= 8 and any(_stk(j)["rental"] or _stk(j)["perishable"] for j in lst(d.get("jokers"))) else ""
            print(f"ADVICE: b skip   (stake {stake_n}: the Small Blind pays $0, so skipping costs one shop visit; tag pays: {pay} ({small.get('tag')}). You own {scoring_j} scoring joker(s) for the Big Blind.{gold}"
                  + (" Skip plan: skip the Big too while your rounds beat the boss by 1.3x+; the boss is never skipped.)" if thr_ok else " Big and Boss blinds are never skipped.)"))
        elif stake_n >= 2 and bs.get("on_deck") == "Small" and tk:
            why_not = ("you own Riff-raff: playing the blind creates 2 Common jokers, a skip forfeits them" if riff else
                       "ante 5+: the shop after the Small Blind is worth more than a tag" if ante_n > 4 else
                       "no free joker slot for the tag's jokers" if tk in ("tag_top_up", "tag_buffoon") and free_j < 1 else
                       "ante 1: only a tag that gives jokers NOW (Buffoon, Top-up) is worth the skip" if ante_n == 1 and (tk in NOW_TAGS or tk in LATER_TAGS) else
                       "your typical hand is under half this ante's boss: skippers at ante 3-4 died far more often; take the shop" if weak_hand else
                       f"tag pays: {pay}; you own {scoring_j} scoring joker(s), the Big Blind must be beaten with them" + (" before the payout arrives" if tk in LATER_TAGS else " (this tag adds no joker)")
                       + ", and the shop after this Small Blind is your chance to add a scorer; skip for this tag only with 2+ scoring jokers" if (tk in NOW_TAGS or tk in LATER_TAGS) else
                       f"the {small.get('tag')} tag is not worth a shop visit")
            print(f"ADVICE: b blind   (do not skip: {why_not}. Big and Boss blinds are never skipped.)")
        else:
            print("ADVICE: b blind   (never skip the Big or Boss blind" + ("; at stake 1 never skip at all: income and a shop matter more than any tag)" if stake_n < 2 else ")"))

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
    "Flash Card": "+2 mult per shop reroll (growth)",
    "Riff-raff": "2 common jokers when a blind is selected", "Ceremonial Dagger": "destroys joker to right at blind start, gains double its value as mult",
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
    if a.get("to_do_poker_hand"):
        # To Do List: the live target is ability.to_do_poker_hand; extra.poker_hand is the card's static default ('High
        # Card'), which players read as the target (7804/7807)
        keep.pop("extra", None)
        keep["to_do"] = a["to_do_poker_hand"]
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
           "Superposition", "8 Ball", "Riff-raff", "Certificate", "DNA", "Faceless Joker", "Invisible Joker", "Brainstorm",
           "Blueprint", "Showman", "Mr. Bones", "Chicot", "Perkeo", "Yorick", "Canio", "Mail-In Rebate", "To Do List",
           "Matador", "Reserved Parking", "Trading Card", "Business Card", "Space Joker", "Dusk", "Sock and Buskin",
           "Hanging Chad", "Hack", "Mime", "Seltzer", "Loyalty Card", "Joker Stencil", "Driver's License", "Burnt Joker",
           "Diet Cola", "Midas Mask", "Cloud 9", "The Idol", "Baseball Card"}
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
    if "Wild" in _enh(c) and not c.get("debuff"):  # card.lua is_suit: a debuffed Wild card counts only as its printed suit
        return "WILD"
    return SMEAR.get(su, su) if "Smeared Joker" in jnames else su


def _suit_matches(c, wanted, jnames):
    su = SUIT.get(c.get("suit"), "?")
    if "Wild" in _enh(c) and not c.get("debuff"):
        return True
    if "Smeared Joker" in jnames:
        return SMEAR.get(su) == SMEAR.get(wanted)
    return su == wanted


def _suit_cover(scoring, jnames):
    """suits covered by a scoring hand the way Flower Pot/Seeing Double count them: each non-Wild card fills the
    first still-empty suit it matches (Smeared Joker lets a Heart fill Diamonds etc.), Wild cards fill leftovers."""
    scoring = [c for c in scoring if not c.get("debuff")]  # card.lua is_suit: a debuffed card has no suit for jokers
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
    # poker_hands is evaluated on the played cards: a Flush or Straight that holds a pair also "contains a Pair"
    # (7806: Sly Joker fired on Flush JD TS TD 5D 4D, est had skipped it)
    rc = Counter(_r(c) for c in scoring if c.get("rank") is not None)
    extra_types = set()
    if any(v >= 2 for v in rc.values()):
        extra_types.add("Pair")
    if sum(1 for v in rc.values() if v >= 2) >= 2:
        extra_types.add("Two Pair")
    if any(v >= 3 for v in rc.values()):
        extra_types.add("Three of a Kind")

    def contains(t):
        return hand_contains(hand_name, t) or t in extra_types
    hl = (state.get("hand_levels") or {}).get(hand_name) or {}
    chips = float(hl.get("chips") or 0)
    mult = float(hl.get("mult") or 1)
    bl_e = state.get("blind") or {}
    boss = (bl_e.get("name") or "") if bl_e.get("boss") and not bl_e.get("disabled") else ""
    if boss == "The Mouth" and bl_e.get("only_hand") and hand_name != bl_e["only_hand"]:
        return 0, [f"The Mouth: only {bl_e['only_hand']} scores this round; {hand_name} scores 0"]
    if boss == "The Eye" and hand_name in lst(bl_e.get("hands_used")):
        return 0, [f"The Eye: {hand_name} was already played this round and scores 0"]
    if boss == "The Flint":
        chips = float(int(chips // 2)); mult = float(int(mult // 2)) or 1.0
        notes.append("The Flint: base chips and mult halved")
    if boss == "The Arm" and int(hl.get("level") or 1) > 1:
        inc = {"High Card": (10, 1), "Pair": (15, 1), "Two Pair": (20, 1), "Three of a Kind": (20, 2), "Straight": (30, 3),
               "Flush": (15, 2), "Full House": (25, 2), "Four of a Kind": (30, 3), "Straight Flush": (40, 4)}.get(hand_name, (0, 0))
        chips -= inc[0]; mult -= inc[1]
        notes.append("The Arm: scored at one level lower (and the level is lost)")
    jokers = lst(state.get("jokers"))
    # Blueprint copies the joker to its right, Brainstorm copies the leftmost joker: score them as that joker.
    # A debuffed joker (Crimson Heart, perished, boss) does nothing, edition included; copying a debuffed joker gives nothing.
    resolved = []
    for i, j in enumerate(jokers):
        n0 = j.get("name")
        if j.get("debuff"):
            notes.append(f"{n0} is DEBUFFED: counts for nothing")
            continue
        if n0 == "Blueprint":
            k = i + 1
            while k < len(jokers) and jokers[k].get("name") in ("Blueprint", "Brainstorm"):
                k += 1
            tgt = jokers[k] if k < len(jokers) else None
            if tgt is not None and not tgt.get("debuff"):
                resolved.append(dict(tgt, edition=j.get("edition")))
            elif tgt is None:
                resolved.append(j)
        elif n0 == "Brainstorm":
            tgt = jokers[0] if jokers and jokers[0].get("name") not in ("Blueprint", "Brainstorm") else None
            if tgt is not None and not tgt.get("debuff"):
                resolved.append(dict(tgt, edition=j.get("edition")))
            elif tgt is None:
                resolved.append(j)
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
            times += 2 * jnames.count("Hanging Chad")  # Blueprint/Brainstorm copies of Chad retrigger again
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
    held_all = held
    held = [c for c in held if not c.get("debuff")]
    # held-card phase (state_events.lua): for each held card in HAND ORDER, its own effect (Steel x1.5) first, then each
    # joker's effect on that card left to right (Shoot the Moon +13 per Queen, Raised Fist on the lowest card, Baron x1.5
    # per King). A Steel Queen therefore gets x1.5 before its own +13 (7802: est was 3774 vs 2812 with Steel applied last).
    jn_h = [j.get("name") for j in jokers]
    fist_low = None
    if "Raised Fist" in jn_h:
        # card.lua: the lowest held card (debuffed ones included, Stone excluded, last one on ties); a debuffed one gives 0
        cand = [c for c in held_all if c.get("rank") is not None and "Stone" not in _enh(c)]
        if cand:
            fist_low = min(reversed(cand), key=lambda c: RANK_VAL.get(_r(c), 0))
    bl_e = state.get("blind") or {}
    mark = bl_e.get("name") == "The Mark" and not bl_e.get("disabled")
    for c in sorted(held_all, key=lambda c: c.get("index") or 0):
        if c.get("debuff"):
            continue
        if "Steel" in _enh(c):
            mult *= 1.5
        # The Mark deals every face card face-down: an unknown held card there is a J/Q/K, each about 1/3 likely
        # (7805: Shoot the Moon est ignored face-down Queens)
        fd_face = mark and c.get("rank") is None and c.get("facing") == "back"
        for n0 in jn_h:
            if n0 == "Shoot the Moon" and (_r(c) == "Q" if not fd_face else True):
                mult += 13 if not fd_face else 13 / 3
            elif n0 == "Raised Fist" and c is fist_low:
                lo = RANK_VAL.get(_r(c), 0)
                mult += 2 * (11 if lo == 14 else min(lo, 10))
            elif n0 == "Baron" and (_r(c) == "K" if not fd_face else True):
                mult *= 1.5 if not fd_face else 1 + 0.5 / 3
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
        elif n == "Joker Stencil":
            # card.lua: x(joker slots - jokers held + Stencils held); a Negative joker adds its own slot. Every other joker
            # you add costs Stencil x1 (and Blueprint/Brainstorm copies of Stencil the same) - 7805's x16 engine.
            raw_j = lst(state.get("jokers"))
            n_st = sum(1 for x in raw_j if x.get("name") == "Joker Stencil")
            slots_j = int(state.get("joker_slots") or 5)
            if slots_j - len(raw_j) > 0:  # card.lua 4328: no empty slot -> Stencil does not fire at all
                mult *= slots_j - len(raw_j) + n_st
        elif n == "Card Sharp":
            x = (ab.get("extra") or {}).get("Xmult", 3) if isinstance(ab.get("extra"), dict) else 3
            if repeat is True:
                mult *= x
            elif repeat is None:
                notes.append(f"Card Sharp x{x} only if the played type was already played this round")
        elif n in TYPE_X_JOKERS:
            t, x = TYPE_X_JOKERS[n]
            if contains(t):
                mult *= x
        elif n == "Abstract Joker":
            mult += 3 * len(lst(state.get("jokers")))  # counts debuffed/disabled jokers too (7807 verified 3x under Crimson Heart)
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
            # card.lua: rem = (every-1-hands_since_create) % (every+1) is recomputed DURING scoring and fires when it reaches
            # `every`; the stored value is the previous hand's, so it cycles ..., 1, 0, then fires on the next hand.
            rem = ab.get("loyalty_remaining")
            every = int((ab.get("extra") or {}).get("every", 5)) if isinstance(ab.get("extra"), dict) else 5
            if rem == 0:
                mult *= float((ab.get("extra") or {}).get("Xmult", 4) if isinstance(ab.get("extra"), dict) else 4)
                notes.append("Loyalty Card fires on THIS hand (x4)")
            elif rem == every:
                notes.append(f"Loyalty Card fired on the LAST hand: x4 again in {every + 1} hands")
            else:
                notes.append(f"Loyalty Card x4 in {rem + 1} hand(s) (this one counts)" if rem is not None else "Loyalty Card x4 every 6 hands: timing unknown")
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
        # these grow in the `before` step of the very hand that triggers them (card.lua), so the growth counts now
        elif n == "Square Joker":
            ex = ab.get("extra") if isinstance(ab.get("extra"), dict) else {}
            chips += float(ex.get("chips", 0)) + (float(ex.get("chip_mod", 4)) if played_n == 4 else 0)
        elif n == "Spare Trousers":
            mult += float(ab.get("mult") or 0) + (float(ab.get("extra") or 2) if not isinstance(ab.get("extra"), dict) and contains("Two Pair") else 0)
        elif n == "Runner":
            ex = ab.get("extra") if isinstance(ab.get("extra"), dict) else {}
            chips += float(ex.get("chips", 0)) + (float(ex.get("chip_mod", 15)) if hand_contains(hand_name, "Straight") else 0)
        elif n == "Obelisk":
            # state_events.lua bumps this hand's `played` before jokers run; card.lua then resets to x1 unless another
            # visible hand has been played at least as often, otherwise grows by `extra` (0.2) before scoring
            hl_o = state.get("hand_levels") or {}
            p_o = int((hl_o.get(hand_name) or {}).get("played") or 0) + 1
            other_more = any(k != hand_name and v.get("visible", True) and int(v.get("played") or 0) >= p_o for k, v in hl_o.items())
            if other_more:
                mult *= float(ab.get("x_mult") or 1) + float(ab.get("extra") or 0.2)
            else:
                notes.append("Obelisk resets to x1: this is your most played hand")
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
        elif n in ("Shoot the Moon", "Raised Fist", "Baron"):
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
        elif n == "Baseball Card":
            # x1.5 for each Uncommon joker owned (rarity 2); with none it is x1 (Fable 7801: ranked 89 with 0 Uncommons)
            mult *= 1.5 ** sum(1 for x in lst(state.get("jokers")) if int(x.get("rarity") or 0) == 2 and not x.get("debuff") and x is not j)
        elif n == "Flower Pot":
            if {"S", "H", "C", "D"} <= _suit_cover(scoring, jnames):
                mult *= 3
        elif n == "Seeing Double":
            # SMODS.seeing_double_check: one scoring card that is a Club (Wild counts) and ANOTHER that is a non-Club suit
            # (Wild counts too); 7802 est 24790 vs 49580 with a Wild as the club
            live = [c for c in scoring if not c.get("debuff")]
            club = [k for k, c in enumerate(live) if "Wild" in _enh(c) or _suit_matches(c, "C", jnames)]
            other = [k for k, c in enumerate(live) if "Wild" in _enh(c) or any(_suit_matches(c, s_, jnames) for s_ in ("H", "D", "S"))]
            if any(a != b for a in club for b in other):
                mult *= 2
        else:
            applied = False
            t_type = ab.get("type")
            if ab.get("t_mult") and t_type and contains(t_type):
                mult += float(ab["t_mult"]); applied = True
            if ab.get("t_chips") and t_type and contains(t_type):
                chips += float(ab["t_chips"]); applied = True
            if ab.get("mult"):
                mult += float(ab["mult"]); applied = True
            ex = ab.get("extra")
            if isinstance(ex, dict) and ex.get("Xmult") and ex.get("type") and contains(ex.get("type")):
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
    if "Misprint" in jnames:
        # Misprint rolls +0..23 mult; est uses 6. Show the roll-0 floor so a one-hand clear is judged on the worst case
        floor_m, _n = estimate(hand_name, scoring, held, dict(state, jokers=[x for x in lst(state.get("jokers")) if x.get("name") != "Misprint"]),
                               repeat=repeat, played_n=played_n)
        cur = int(chips * mult)
        notes.append(f"Misprint range: roll 0 -> {floor_m}, roll 23 -> ~{cur + int((cur - floor_m) * 17 / 6)}")
    return int(chips * mult), notes


def _cards_by_idx(d, idxs):
    hand = {c.get("index"): c for c in lst(d.get("hand"))}
    return [hand[i] for i in idxs if i in hand]


def _held(d, idxs):
    return [c for c in lst(d.get("hand")) if c.get("index") not in set(idxs)]

def _held_value(c, d):
    """1 when the card pays while HELD (Steel x1.5, Gold $3, Blue seal planet, Shoot the Moon Queen, Baron King): never a
    throwaway or filler (7803/7807 threw a held Steel)."""
    jn = {j.get("name") for j in lst(d.get("jokers")) if not j.get("debuff")}
    return int(any(e in _enh(c) for e in ("Steel", "Gold")) or c.get("seal") == "Blue"
               or ("Shoot the Moon" in jn and _r(c) == "Q") or ("Baron" in jn and _r(c) == "K"))

def _obelisk_resets(d, hand_name):
    """card.lua: Obelisk resets when the played type's count (after +1) is STRICTLY greater than every other visible
    type's count; ties keep it growing."""
    if not any(j.get("name") == "Obelisk" and not j.get("debuff") for j in lst(d.get("jokers"))):
        return False
    hl = d.get("hand_levels") or {}
    p = int((hl.get(hand_name) or {}).get("played") or 0) + 1
    return not any(k != hand_name and (v or {}).get("visible", True) and int((v or {}).get("played") or 0) >= p for k, v in hl.items())




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
    wilds = [c for c in hand if "Wild" in _enh(c) and not c.get("debuff")]
    for c in sorted(hand, key=lambda c: 1 if c.get("debuff") else 0):
        if c.get("rank") is None:
            continue  # face-down: rank and suit unknown, never assume them
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
            if len(cs) > 5:
                # pick the 5 by est, not by chips: Even Steven / Odd Todd / Scholar / Walkie Talkie care which ranks score
                # (7807: AD QD 8D 7D 6D 68425 over the 3-even AD QD 8D 6D 2D 76520)
                import itertools
                best = list(max(itertools.combinations(cs, 5), key=lambda cb: estimate("Flush", list(cb), [c for c in hand if c not in cb], d, played_n=5)[0]))
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
                # every distinct straight is a candidate (est decides): the A-5 wheel can beat a 6-high one with
                # Fibonacci / Scholar / Even Steven (Main 06:xx)
                out.append(f"STRAIGHT {hi}-high: idx {idx(run)} | {base('Straight')} + {card_chips(run)} card chips")
                found = True
        if found:
            break
    # a 1-card High Card is always a candidate: with Half Joker / Hanging Chad / Photograph it can beat a Pair (7803 at
    # The Water: High Card K est 2625 was never listed, Pair 7 est 484 was advised); est decides
    live_c = [c for c in hand if not c.get("debuff")] or hand
    # one High Card per distinct rank (Odd Todd / Even Steven / Scholar / Walkie make a lower card score more: 7806's
    # High 7S 2021 vs the listed KC 780); est ranks them
    seen_r = set()
    for c1 in sorted(live_c, key=lambda c: -CHIP_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0)):
        r1 = c1.get("rank")
        if r1 is None or r1 in seen_r:
            continue
        seen_r.add(r1)
        out.append(f"HIGH CARD {card_str(c1)}: idx {c1.get('index')} | {base('High Card')}")
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


ORDER_JOKERS = {"Hanging Chad", "Photograph"}  # retrigger / x2 on the FIRST scored (face) card: hand order matters
GROWTH_X = {"Throwback", "Hologram", "Constellation", "Lucky Cat", "Campfire", "Glass Joker", "Vampire", "Madness", "Obelisk",
            "Ramen", "Steel Joker", "Caino", "Canio", "Yorick", "Hit the Road", "Joker Stencil"}  # xMults that grow: never "flat rentals"


def _order_gain(d, hand_name, idxs):
    """Best est when one of the played cards is moved to the leftmost played slot (Hanging Chad retriggers the first
    scored card, Photograph x2 the first face): (est, card index to move) or (current est, None)."""
    cards = _cards_by_idx(d, idxs)
    held = _held(d, idxs)
    cur = estimate(hand_name, cards, held, d, played_n=len(idxs))[0]
    best = (cur, None)
    for k, c in enumerate(cards[1:], 1):
        # estimate scores cards in hand (index) order: give the moved card an index just left of the play
        lead_i = min(x.get("index") or 0 for x in cards) - 0.5
        e = estimate(hand_name, [dict(c, index=lead_i)] + cards[:k] + cards[k + 1:], held, d, played_n=len(idxs))[0]
        if e > best[0]:
            best = (e, c.get("index"))
    return best


TYPE_WORD = {v: k for k, v in HAND_WORDS.items()}


_SOLVER = None


def _round_solver():
    """python/balatro_env/solver.py loaded by path (the package __init__ imports torch)."""
    global _SOLVER
    if _SOLVER is None:
        import importlib.util
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "solver.py")
        spec = importlib.util.spec_from_file_location("round_solver", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SOLVER = mod
    return _SOLVER


def advise(d):
    """Rule-based advice, checked against DrawSolver's Monte-Carlo p_clear: the rule pick stands unless the solver's
    best first action clears the blind measurably more often (> 0.03). Special-case branches (non PLAY/DISCARD advice,
    Crimson Heart, Verdant Leaf, face-down cards) are kept as they are."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _advise_rules(d)
    lines = buf.getvalue().splitlines()
    adv_i = next((i for i, ln in enumerate(lines) if ln.startswith("ADVICE:")), None)
    adv = lines[adv_i] if adv_i is not None else ""
    m = re.match(r"ADVICE: (PLAY|DISCARD) -> b (play|disc)((?: [A-Z]+)?)((?: \d+)+)", adv)
    bname = (d.get("blind") or {}).get("name") or ""
    special = (not m or bname in ("Crimson Heart", "Verdant Leaf") or any(c.get("rank") is None for c in lst(d.get("hand")))
               or "(probe:" in adv)
    plan, mine = [], None
    if d.get("phase") == "SELECTING_HAND" and not special:
        try:
            rs = _round_solver()
            plan = rs.best_round_plan(d, estimate)
            if plan:
                mine = rs.evaluate_action(d, m.group(1), [int(x) for x in m.group(4).split()], estimate)
        except Exception as e:  # the rule advice stands on its own
            lines.insert(adv_i, f"  (solver unavailable: {type(e).__name__}: {e})")
            plan = []
    if plan:
        # solver.py ranks: full-sample options first (under-sampled leaders are topped up), p_model ties within 0.015
        # ordered by value = $ at cash-out + 0.5 x growth-joker triggers. p_clear is CALIBRATED (isotonic map on 2812
        # recorded Gold decisions, every bin within 0.05 of the realized clear rate); p_model is the raw model value.
        def _sl(r):
            p = r["p_clear"]
            ps = ">=0.99" if p >= 0.995 else f"{p:.2f}"
            return (f"p {ps} (calibrated, n={r.get('n')}{', low n' if r.get('low_n') else ''})"
                    + (f"  survive {r['p_survive']:.2f}" if r.get("p_survive") is not None and any(j.get("name") == "Mr. Bones" for j in lst(d.get("jokers"))) else "")
                    + f"  +${r.get('dollars', 0):.1f}" + (f" growth {r['growth']:.1f}" if r.get("growth") else "")
                    + f"  exp {int(r['exp_score'])}")
        sol = [f"  SOLVER {r['action']} {' '.join(map(str, r['cards']))}  {_sl(r)}  ({r['note']})" for r in plan[:3]]
        if all(r["p_clear"] < 0.01 for r in plan):
            bx = max(plan, key=lambda r: r["exp_score"])
            has_bones = any(j.get("name") == "Mr. Bones" for j in lst(d.get("jokers")))
            cons_n = [c.get("name") for c in lst(d.get("consumables"))]
            sol.append(f"  UNWINNABLE this round on the simulation: no line clears. Best expected score: {bx['action']} {' '.join(map(str, bx['cards']))} (exp {int(bx['exp_score'])})"
                       + ("; Mr. Bones saves the run at 25% of the blind" if has_bones else "")
                       + (f"; check consumables {cons_n} (Strength/Death/Justice/planets) before playing" if cons_n else ""))
        if mine:
            sol.append(f"  SOLVER on the rule pick ({m.group(2)}{m.group(4)}): {_sl(mine)}")
        top = plan[0]
        b_ = d.get("blind") or {}
        need_now = int(b_.get("chips_needed") or 0) - int(b_.get("chips_scored") or 0)
        m_est = re.search(r"est (\d+)", top.get("note") or "")
        clears_now = top["action"] == "PLAY" and m_est is not None and need_now > 0 and int(m_est.group(1)) >= need_now
        pm_top, pm_mine = top.get("p_model", top["p_clear"]), (mine or {}).get("p_model", (mine or {}).get("p_clear", 0))
        tied = mine and abs(pm_top - pm_mine) < 0.015
        # orchestrator 02:58: follow the solver when its calibrated p beats the rule pick by > 0.05; a PLAY that clears the
        # blind now also wins on a smaller model edge or, tied, on $1+ more value
        # an under-sampled option (low_n) never drives the switch
        better_p = mine and not top.get("low_n") and top["p_clear"] > mine["p_clear"] + 0.05
        better_c = mine and not top.get("low_n") and clears_now and (pm_top > pm_mine + 0.03 or (tied and top.get("value", 0) >= mine.get("value", 0) + 1.0))
        if mine and not (better_p or better_c):
            sol.append("  (rule pick kept: the solver's best does not beat it by more than 0.05 calibrated p)")
        if better_p or better_c:
            idxs = " ".join(map(str, top["cards"]))
            if top["action"] == "PLAY":
                word = TYPE_WORD.get(top.get("hand")) if top.get("hand") else None
                cmd = f"b play {word + ' ' if word else ''}{idxs}"
            else:
                cmd = f"b disc {idxs}"
            sol.append(f"  (rule advice was: {adv[8:]})")
            pt, pr_ = top["p_clear"], mine["p_clear"]
            dv = top.get("value", 0) - mine.get("value", 0)
            why = (f"clears {pt:.0%} vs {pr_:.0%} (calibrated) for the rule pick" if better_p else
                   "this play clears the blind now; " + (f"tied clear chance, +{dv:.1f} value ($ left / growth)" if tied else f"{pt:.0%} vs {pr_:.0%}"))
            adv = f"ADVICE: {top['action']} -> {cmd}   (solver: {why}; {top['note']})"
        lines = lines[:adv_i] + sol + [adv] + lines[adv_i + 1:]
    print("\n".join(lines))


def _advise_rules(d):
    _SHARE_MEMO.clear()
    if d.get("phase") != "SELECTING_HAND":
        print("advise only works while selecting a hand"); return
    b = d.get("blind") or {}
    need = (b.get("chips_needed") or 0) - (b.get("chips_scored") or 0)
    hands_left = int(d.get("hands_remaining") or 0)
    discards = int(d.get("discards_remaining") or 0)
    hand = lst(d.get("hand"))
    cands = _candidates(d)
    show_hands(d)
    if cands and any(j.get("name") in ORDER_JOKERS and not j.get("debuff") for j in lst(d.get("jokers"))):
        # 7805: an A-high Straight 2982 was advised over K-Q-J-T-9 with the King first (11704) under Photograph + Chad
        cur_best = max(c[2] for c in cands)
        reo = max(((_order_gain(d, h, ix), h, ix) for h, ix, _e in cands), key=lambda t: t[0][0])
        (e_r, mv), h_r, ix_r = reo
        if mv is not None and e_r >= 1.1 * cur_best:
            print(f"ADVICE: REORDER -> b move hand {mv} {min(ix_r)}   (Hanging Chad / Photograph act on the FIRST scored card: with card {mv} first, "
                  f"{h_r} {ix_r} scores ~{e_r} vs {cur_best} for the best play in this order; moving is free, then re-run advise)")
            return
    jc = d.get("_jokers_cached")
    if jc and cands:
        names = [str(j.get("name")) for j in lst(d.get("jokers"))]
        bc = max(cands, key=lambda t: t[2])
        sc_cards = _cards_by_idx(d, bc[1])
        held_c = _held(d, bc[1])
        ests = [estimate(bc[0], sc_cards, held_c, dict(d, jokers=[lst(d.get("jokers"))[i] for i in p]), played_n=len(bc[1]))[0]
                for p in _order_perms(names)]
        lo, hi = min(ests), max(ests)
        print(f"AMBER ACORN: jokers face-down and shuffled; est uses the jokers you last saw ({', '.join(names)})"
              + (" in the order inferred from your last hand" if jc.get("inferred") else "") + f". Best play {bc[0]} est range over joker orders {lo}..{hi}.")
        if not jc.get("inferred") and hi > 1.1 * lo and hands_left >= 2 and need > 0 and lo * (hands_left - 1) >= need and not _obelisk_resets(d, "High Card"):
            low = min((c for c in hand if c.get("rank") is not None and not c.get("debuff")), key=lambda c: (_held_value(c, d), CHIP_VAL.get(_r(c), 0)), default=None)
            if low is not None:
                print(f"ADVICE: PLAY -> b play HIGH {low.get('index')}   (probe: a 1-card High Card's score reveals the joker order (the CLI infers it after the play); "
                      f"then `b order` +mult jokers left of xMult before the big hands; {hands_left - 1} hands at >= {lo} still clear {need})")
                return
        if jc.get("inferred"):
            perms = _order_perms(names)
            k_best = max(range(len(perms)), key=lambda k: ests[k])
            cur = estimate(bc[0], sc_cards, held_c, d, played_n=len(bc[1]))[0]
            if ests[k_best] > 1.05 * cur:
                print(f"ADVICE: REORDER -> b order {' '.join(str(i + 1) for i in perms[k_best])}   (inferred order scores {bc[0]} {cur}; this order scores {ests[k_best]}; reordering is free)")
                return
    if not cands:
        fd_all = [c.get("index") for c in hand if c.get("rank") is None]
        bname = ((d.get("blind") or {}).get("name") or "") if (d.get("blind") or {}).get("boss") else ""
        if not fd_all:
            print("ADVICE: no hand found. Discard your lowest cards (`disc` up to 5) and re-run advise.")
        elif bname == "The Mark":
            print(f"ADVICE: PLAY -> b play {' '.join(map(str, fd_all[:4]))}   (The Mark: face-down cards are face cards; 4 of them contain at least a pair)")
        elif discards > 0:
            print(f"ADVICE: DISCARD -> b disc {' '.join(map(str, fd_all[:5]))}   ({bname or 'boss'}: these cards are face-down and unknown; never estimate hands from them. Discard them to draw visible cards, then re-run advise.)")
        elif hands_left >= 2:
            print(f"ADVICE: PLAY -> b play {fd_all[0]}   (no discards left and every card is face-down: a 1-card throwaway reveals new cards for the next hand; re-run advise after it)")
        else:
            print(f"ADVICE: PLAY -> b play {' '.join(map(str, fd_all[:5]))}   (last hand, every card face-down: play 5 for the best chance at a made hand)")
        return
    bl_now = d.get("blind") or {}
    boss_now = (bl_now.get("name") or "") if bl_now.get("boss") and not bl_now.get("disabled") else ""
    played_now = [k for k, v in (d.get("hand_levels") or {}).items() if int(v.get("played_this_round") or 0) > 0]
    if boss_now == "The Eye" and bl_now.get("hands_used") is not None:
        played_now = list(lst(bl_now.get("hands_used")))  # the blind's own record of used types
    if boss_now in ("The Mouth", "The Eye") and not any(c[0] == "High Card" for c in cands):
        vis = [c for c in hand if c.get("rank") is not None and not c.get("debuff")]
        if vis:
            top = max(vis, key=lambda c: (CHIP_VAL.get(_r(c), 0), RANK_VAL.get(_r(c), 0)))
            cands = cands + [("High Card", [top.get("index")], estimate("High Card", [top], _held(d, [top.get("index")]), d, played_n=1)[0])]
    if boss_now == "The Mouth":
        lock = bl_now.get("only_hand") or (played_now[0] if len(played_now) == 1 else None)
        played_now = [lock] if lock else []
        if not lock:
            mh_m = main_hand(d)
            PF = ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind")
            want = mh_m if mh_m in PF else "Pair"
            print(f"The Mouth: your FIRST played hand locks the type for all {hands_left} hands; every other type then scores 0. "
                  f"Lock a type you can repeat ({want}), unless one hand of another type clears the whole {need}."
                  + (" You have 0 discards: you cannot rebuild a type, so lock the one you can make most often." if discards == 0 else ""))
            if not any(c[2] >= need for c in cands):
                rep = [c for c in cands if c[0] == want] or [c for c in cands if c[0] in ("Pair", "Two Pair", "Three of a Kind")]
                if rep:
                    cands = rep
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
            elif hands_left >= 2:
                junk = [c.get("index") for c in hand if c.get("index") not in keep][:5] or [c.get("index") for c in hand][:1]
                print(f"ADVICE: PLAY -> b play {' '.join(map(str, junk))}   (The Mouth locked {locked} and none is makeable with no discards: a junk play scores 0 "
                      f"but draws {len(junk)} new cards for your last {hands_left - 1} hand(s); keeping {keep} toward {locked} (7807 found its 5th club this way and won))")
            else:
                print(f"ADVICE: NO VALID PLAY: you cannot form {locked} on the last hand. Any other hand scores 0. Play your closest cards to end the round.")
            return
        cands = matching
    if not cands:
        print("ADVICE: no legal scoring hand under this boss; discard toward a new type or play the least bad option manually.")
        return
    best = max(cands, key=lambda t: t[2])
    fds = [c.get("index") for c in hand if c.get("rank") is None]
    boss_name = ((d.get("blind") or {}).get("name") or "") if (d.get("blind") or {}).get("boss") else ""
    if boss_name == "Crimson Heart":
        off = [j for j in lst(d.get("jokers")) if j.get("debuff") and not _dead_perishable(j)]
        print("Crimson Heart: one random joker is disabled; it re-rolls after every PLAYED hand (discards do not re-roll it), "
              "and the next pick never repeats the joker disabled now.")
        if off and hands_left >= 2 and best[2] < need:
            j_off = off[0]
            d_full = dict(d, jokers=[dict(j, debuff=False) if j is j_off else j for j in lst(d.get("jokers"))])
            est_full, _n = estimate(best[0], _cards_by_idx(d, best[1]), _held(d, best[1]), d_full, repeat=_repeat_flag(d, best[0]))
            spare = [c for c in hand if c.get("index") not in best[1] and c.get("rank") is not None]
            # the throwaway costs one hand but returns the big joker for the rest: worth it whenever it multiplies the hand
            # by 1.5+ (7804 lost Crimson Heart discarding while its big xMult was the disabled one; discards never re-roll)
            # never a throwaway that resets Obelisk (7807 won at x3.6; a High Card throwaway would have reset it to x1)
            if spare and est_full >= int(1.5 * best[2]) and not _obelisk_resets(d, "High Card"):
                low = min(spare, key=lambda c: (_held_value(c, d), CHIP_VAL.get(_r(c), 0)))
                print(f"ADVICE: PLAY -> b play HIGH {low.get('index')}   (Crimson Heart disabled {j_off.get('name')}: your {best[0]} scores {best[2]} now vs ~{est_full} with it. "
                      f"A 1-card throwaway re-rolls the disabled joker (never {j_off.get('name')} again next), then play the {best[0]}; {hands_left - 1} hand(s) left after this. "
                      "The new pick is random and can hit another joker: re-run advise.)")
                return
    if fds and boss_name != "The Mark":
        print(f"Face-down cards {fds} are unknown random cards ({boss_name or 'no boss'}): do not count on them; prefer discarding them and playing visible hands.")
    if len(fds) >= 4 and boss_name == "The Mark":
        fake = [{"rank": "King", "suit": "Spades"}, {"rank": "King", "suit": "Hearts"}]
        est_fd, _n = estimate("Pair", fake, [c for c in hand if c.get("index") not in fds[:4]], d, repeat=_repeat_flag(d, "Pair"), played_n=4)
        print(f"Face-down cards {fds}: any 4 of them always contain a pair (3 same-suit face-downs are K,Q,J). A face pair here would score about {est_fd}.")
        # Half Joker (+20 at <= 3 cards): 3 face-downs pair 7 times in 9 (Main 06:xx: the 4-card play switched Half off)
        est3 = int(7 / 9 * estimate("Pair", fake, [c for c in hand if c.get("index") not in fds[:3]], d, repeat=_repeat_flag(d, "Pair"), played_n=3)[0])
        n_fd, e_fd = (3, est3) if est3 > est_fd else (4, est_fd)
        if e_fd >= best[2]:
            print(f"ADVICE: PLAY -> b play {' '.join(map(str, fds[:n_fd]))}   ({n_fd} face-down cards: " + ("guaranteed at least a pair of faces" if n_fd == 4 else "a pair of faces 7 times in 9, and Half Joker stays on")
                  + f", est ~{e_fd}; no TYPE given because the exact type is hidden)")
            return
    face_jokers = any(j.get("name") in ("Smiley Face", "Scary Face", "Photograph", "Triboulet", "Sock and Buskin") for j in lst(d.get("jokers")))
    all_idx = [c.get("index") for c in hand]

    jnames_all = [j.get("name") for j in lst(d.get("jokers")) if not j.get("debuff")]  # debuffed jokers do nothing this hand
    protect_ranks = set()
    if "Shoot the Moon" in jnames_all:
        protect_ranks.add("Q")
    if "Baron" in jnames_all:
        protect_ranks.add("K")
    # Raised Fist scores the LOWEST held card: play low cards away as fillers, keep high cards held (7809: fillers 6 7 8
    # left a 3 held, 324; fillers Q J 3 kept a 6 lowest, 432) - no rank protection, the filler sort already plays low first

    upcoming_boss = (((d.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}).get("name")
    pillar_ahead = upcoming_boss == "The Pillar" and not (d.get("blind") or {}).get("boss")
    if pillar_ahead:
        print("The Pillar is this ante's boss: every card you play now is debuffed at the boss. Playing WITHOUT fillers and with the fewest cards.")
    if boss_name == "The Serpent":
        print("The Serpent: every play or discard draws exactly 3 cards, so a 4-5 card discard shrinks your hand for the rest of the round. Discard at most 3 cards at a time and play made hands early.")
    sellable_v = [j for j in lst(d.get("jokers")) if not _stk(j)["eternal"]]
    if boss_name == "Verdant Leaf" and any(c.get("debuff") for c in hand) and sellable_v:
        weakest_v = min(sellable_v, key=lambda j: owned_value(d, j, main_hand(d)))
        print(f"ADVICE: SELL -> b sell {weakest_v.get('index')}   (Verdant Leaf debuffs every card until you sell ONE joker; {weakest_v.get('name')}{stickers(weakest_v)} is your least valuable sellable one (Eternal jokers cannot be sold). Do not discard before selling.)")
        return
    if boss_name == "The Tooth":
        pillar_ahead = True
        print("The Tooth: you lose $1 per card played. Playing WITHOUT fillers; if a 2-card pair clears the remaining need, play just the pair.")

    def fillers(idxs, hand_name):
        """_fillers0, padded to exactly 5 cards at The Psychic (any play under 5 cards is refused there)."""
        fl = _fillers0(idxs, hand_name)
        if psychic and len(idxs) + len(fl) < 5:
            rest = sorted((c for c in hand if c.get("index") not in idxs and c.get("index") not in fl),
                          key=lambda c: (c.get("rank") is not None and _r(c) in {_r(x) for x in _cards_by_idx(d, idxs)}, CHIP_VAL.get(_r(c), 0) if c.get("rank") is not None else 0))
            fl = fl + [c.get("index") for c in rest[:5 - len(idxs) - len(fl)]]
        return fl

    def _fillers0(idxs, hand_name):
        """non-scoring cards safe to add: no rank already in the hand, no face if face jokers, avoid making flush/straight."""
        cap = 5
        if "Half Joker" in jnames_all and len(idxs) <= 3 and not psychic:
            # Half Joker's +20 mult needs 3 or fewer cards played: plain fillers would cost more than they draw, but
            # with Splash a kicker scores, so fill up to 3 cards
            if "Splash" not in jnames_all:
                return []
            cap = 3
        if "Square Joker" in jnames_all and len(idxs) == 4 and not psychic:
            return []  # Square Joker grows only on exactly 4 played cards (7807: a 5th filler cost the growth)
        if pillar_ahead:
            return []
        # ranks held 2+ times outside the play are a pair for a later hand: never spend one as a filler (7801 x3)
        held_rank_n = Counter(_r(c) for c in hand if c.get("rank") is not None and c.get("index") not in idxs)
        held_pairs = {r for r, n in held_rank_n.items() if n >= 2} if hands_left > 1 else set()
        used_ranks = {_r(c) for c in _cards_by_idx(d, idxs)} | protect_ranks | held_pairs
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
            if "Steel" in _enh(c) or c.get("seal") == "Blue" or "Gold" in _enh(c):
                continue  # Steel x1.5 / Gold $3 / Blue seal planet pay while HELD: never a filler (7807 played a held Steel)
            if "Stone" in _enh(c):
                out.append((-100, i, None))
                continue
            if c.get("rank") is None:
                continue
            r = _r(c)
            splash = "Splash" in jnames_all
            if r in used_ranks or (face_jokers and r in FACES and not splash) or SUIT.get(c.get("suit")) in live_suit:
                continue
            if hand_name == "High Card" and RANK_VAL.get(r, 0) >= max((RANK_VAL.get(_r(x), 0) for x in _cards_by_idx(d, idxs)), default=0):
                continue  # the game scores the HIGHEST card: a higher filler steals the High Card (7806: AD over KS, 722 vs 3250)
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
        if "Blackboard" in jnames_all:
            # Blackboard x3 needs every HELD card to be a Spade or Club: play the red cards as fillers first
            out = [(k - 1000 if su in ("H", "D") else k, i, su) for k, i, su in out]
        out.sort()
        chosen = []
        chosen_ranks = set()
        if "Splash" in jnames_all and hand_name in ("Pair", "Two Pair", "Three of a Kind", "High Card"):
            # Splash: every played card scores, so pick each filler by the est it actually adds (as `sel` would)
            pool = list(out)
            while pool and len(idxs) + len(chosen) < cap:
                scored = []
                for _o, i, su in pool:
                    r_i = _r(_cards_by_idx(d, [i])[0])
                    if r_i in chosen_ranks or (used_suits + [x[1] for x in chosen] + [su]).count(su) >= 5:
                        continue
                    trial = idxs + [x[0] for x in chosen] + [i]
                    e_t, _n = estimate(hand_name, _cards_by_idx(d, trial), _held(d, trial), d, played_n=len(trial))
                    scored.append((e_t, i, su, r_i))
                if not scored:
                    break
                e_t, i, su, r_i = max(scored)
                chosen.append((i, su)); chosen_ranks.add(r_i)
                pool = [p for p in pool if p[1] != i]
            return [i for i, _ in chosen]
        for _, i, su in out:
            if len(idxs) + len(chosen) >= cap:
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
    if "Splash" in jnames_all and not psychic:
        # every played card scores: judge each candidate by its est WITH the fillers advise would add (7801: core 160 vs
        # 218 with fillers made advise discard a hand that cleared exactly)
        rescored = []
        for h_c, i_c, e_c in cands:
            fl_c = fillers(i_c, h_c) if len(i_c) < 5 else []
            if fl_c:
                all_c = i_c + fl_c
                e_c = max(e_c, estimate(h_c, _cards_by_idx(d, all_c), _held(d, all_c), d, repeat=_repeat_flag(d, h_c), played_n=len(all_c))[0])
            rescored.append((h_c, i_c, e_c))
        cands = rescored
        best = max(cands, key=lambda t: t[2])
    if best[2] >= need:
        # prefer the cheapest hand that still clears
        ok = [c for c in cands if c[2] >= need]
        mh_now = main_hand(d)
        PAIR_FAMILY = ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind")
        # any of these clears; prefer the hand we are building (main hand, then pair family) so levels and Supernova stay consolidated
        pick = max(ok, key=lambda t: (t[0] == mh_now, t[0] in PAIR_FAMILY, t[2], -len(t[1])))
        if pick[2] < 1.25 * need:
            # a thin margin is est risk (7810 The Eye last hand: Two Pair 5874 vs need 5350 over a Full House 10036): take the biggest
            pick = max(ok, key=lambda t: (t[2], -len(t[1])))
        why = "" if pick[2] == max(c[2] for c in ok) else f"; a bigger {max(ok, key=lambda t: t[2])[0]} also clears but {pick[0]} is the hand you are leveling"
        fl = fillers(pick[1], pick[0]) if len(pick[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(pick[0], 'HIGH')} {' '.join(map(str, pick[1] + fl))}   (est {pick[2]} >= need {need}{why}" + (f"; fillers {fl} just draw cards)" if fl else ")"))
        return
    summit = any(j.get("name") == "Mystic Summit" and not j.get("debuff") for j in lst(d.get("jokers")))
    if summit and discards > 0 and best[2] < need:
        est0 = estimate(best[0], _cards_by_idx(d, best[1]), _held(d, best[1]), dict(d, discards_remaining=0), repeat=_repeat_flag(d, best[0]), played_n=len(best[1]))[0]
        junk = sorted((c for c in hand if c.get("index") not in best[1]), key=lambda c: (_held_value(c, d), CHIP_VAL.get(_r(c), 0) if c.get("rank") else 0))
        if est0 >= need and junk:
            # Mystic Summit is +15 only at 0 discards left: burn them on junk, then the made hand clears (Main 06:xx: TT
            # discarded from a made pair that cleared with Summit on)
            burn = [c.get("index") for c in junk if not _held_value(c, d)][:5] or [junk[0].get("index")]
            print(f"ADVICE: DISCARD -> b disc {' '.join(map(str, burn))}   (Mystic Summit: {best[0]} {best[1]} scores {best[2]} now but {est0} at 0 discards left (need {need}); "
                  f"burn your {discards} discard(s) on junk (it also draws toward a bigger hand), keep {best[1]}, then play it)")
            return
    acro = next((j for j in lst(d.get("jokers")) if j.get("name") == "Acrobat" and not j.get("debuff")), None)
    if acro and hands_left >= 2 and not psychic and boss_name not in ("The Hook", "The Serpent", "The Eye", "The Mouth"):
        # Acrobat: x3 mult on the final hand of the round. Hold the best hand and burn the other hands with spare cards.
        burn = [c for c in cands if not set(c[1]) & set(best[1])]
        pick = max(burn, key=lambda t: t[2]) if burn else None
        if pick is None:
            spare = [c for c in hand if c.get("index") not in best[1] and c.get("rank") is not None]
            if spare:
                low = min(spare, key=lambda c: (_held_value(c, d), CHIP_VAL.get(_r(c), 0)))
                pick = ("High Card", [low.get("index")], 0)
        # the held hand's est AS the final hand: Acrobat x3, Dusk's retrigger and Summit (if the discards are gone) all
        # apply there (7803: Dusk was left out of the last-hand est)
        last_e = estimate(best[0], _cards_by_idx(d, best[1]), _held(d, best[1]), dict(d, hands_remaining=1), repeat=_repeat_flag(d, best[0]), played_n=len(best[1]))[0]
        if pick and last_e + pick[2] >= need and not _obelisk_resets(d, pick[0]):
            print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(pick[0], 'HIGH')} {' '.join(map(str, pick[1]))}   (Acrobat x3 fires on the FINAL hand: keep {best[0]} {best[1]} (est {best[2]} now, ~{last_e} as the last hand vs need {need}) and spend this hand on spare cards; {hands_left - 1} hand(s) left after this)")
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
    summit = "Mystic Summit" in jnames_all  # +15 mult only once discards are 0: spending discards early is free value
    if summit and discards > 0:
        print(f"Mystic Summit: +15 mult only with 0 discards left ({discards} now); use the discards early, the hands after them get +15.")
    # pace: banking a hand only makes sense when hands of this quality can clear (best x hands_left >= need); otherwise
    # use the discards first to dig for a hand that does (7810 lost a jokerless 300 with 3 x ~84 after banking Two Pair)
    # later hands count at PACE_LATER of the best hand (fresh cards come back; 7805 lost 192/300 when 60% made advise
    # discard twice from an on-pace Two Pair). Shown explicitly; DrawSolver's p_clear will replace this.
    PACE_LATER = 0.85
    pace_total = int(best[2] * (1 + PACE_LATER * max(0, hands_left - 1)))
    on_pace = pace_total >= need
    if not on_pace and discards > 0:
        print(f"PACE: {best[0]} est {best[2]} now + {max(0, hands_left - 1)} later hand(s) x {int(PACE_LATER * 100)}% = {pace_total} < need {need}: discard toward a bigger hand before playing.")
    used_disc = int((d.get("run") or {}).get("discards_used") or 0)
    if 0 < discards and (discards < hands_left or used_disc >= 1) and hands_left >= 2 and best[2] >= 0.6 * need / hands_left and feasible_after and not summit and on_pace:
        fl = fillers(best[1], best[0]) if len(best[1]) < 5 else []
        print(f"ADVICE: PLAY -> b play {TYPE_WORD.get(best[0], 'HIGH')} {' '.join(map(str, best[1] + fl))}   (est {best[2]}; {discards} discard(s) for {hands_left} hands: pacing, keep discards for later hands)")
        return
    if discards == 1 and hands_left >= 2 and best[2] >= 0.8 * need / hands_left and feasible_after and not summit and on_pace:
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
        # outs from the actual remaining draw pile when the bridge sends it (deck.cards[].remaining), else a fresh-deck guess
        deck_left = [c for c in lst((d.get("deck") or {}).get("cards")) if c.get("remaining")]
        deck_n = len(deck_left) or int(((d.get("deck") or {}).get("draw_pile")) or 40)
        draws = min(5, len(hand) - 4)

        def p_hit(outs):
            p_miss = 1.0
            for k in range(draws):
                p_miss *= max(0.0, (deck_n - outs - k) / max(1, deck_n - k))
            return 1 - p_miss
        BOSS_SUIT = {"The Head": "H", "The Club": "C", "The Goad": "S", "The Window": "D"}
        dead_suit = BOSS_SUIT.get(boss_name) if (d.get("blind") or {}).get("boss") and not (d.get("blind") or {}).get("disabled") else None
        if len(flush_draw[1]) == 4 and flush_draw[0] != dead_suit:  # a flush of the boss-debuffed suit scores no card chips
            fcards = _cards_by_idx(d, flush_draw[1])
            flush_est, _n = estimate("Flush", fcards + [fcards[0]], _held(d, flush_draw[1]), d)
            f_outs = sum(1 for c in deck_left if SUIT.get(c.get("suit")) == flush_draw[0]) if deck_left else max(0, 13 - len(flush_draw[1]) - 1)
            flush_ev = flush_est * p_hit(f_outs)
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
                four = [v for v in range(hi, hi - 5, -1) if vals.get(v) is not None]
                # ranks that complete 5 in a row with these four (gutshot: 1 rank, open-ended: 2)
                fill = {v for v in range(1, 15) if v not in four and any(set(range(lo, lo + 5)) == set(four) | {v} for lo in range(1, 11))}
                fill |= {14} if 1 in fill else set()
                fill |= {1} if 14 in fill else set()
                if deck_left:
                    s_outs = sum(1 for c in deck_left if RANK_VAL.get(RANK.get(str(c.get("rank")), str(c.get("rank"))), 0) in fill)
                else:
                    s_outs = 4 * len({min(v, 14) if v != 1 else 14 for v in fill})
                if st_est * p_hit(s_outs) > straight_ev:
                    straight_ev, straight_keep = st_est * p_hit(s_outs), have
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
        # with 2 or fewer discards (every Gold round) or on the final hand, never throw away the made floor: keep it and
        # draw to the chase around it (7805 discarded its only pair at The Head and missed the straight)
        # ... but only when the floor matters: a made hand under half the per-hand need is no floor (7802 kept a low pair vs 450)
        floor_needed = made and (discards <= 2 or hands_left == 1) and best_made >= 0.5 * need / max(1, hands_left)
        jokerless_ok = not jnames_all and proj >= 0.9 * need  # no joker: a missed chase strips the pair ranks that clear this blind
        if jokerless_ok and chase[2] and chase[0] > 1.25 * made_ev:
            print(f"No jokers: made pair-family hands project to {int(proj)} vs need {need}; sequencing them beats a {chase[1]} chase (EV {int(chase[0])}) that leaves nothing when it misses.")
        if chase[0] > 1.25 * made_ev and chase[0] > 0.3 * need and chase[2] and not floor_needed and not jokerless_ok:
            keep = chase[2]; why = f"drawing to a {chase[1]} (EV {int(chase[0])}) because made hands (best {best_made}) project to {int(proj)} {'<' if proj < need else '>='} need {need}"
        elif floor_needed and chase[2] and (discards == 1 or hands_left == 1 or chase[0] > 1.25 * made_ev):
            top = max(made, key=lambda t: t[2])
            keep = sorted(set(top[1]) | set(chase[2])); why = f"{'final hand' if hands_left == 1 else 'only ' + str(discards) + ' discard(s)'}: keeping the made {top[0]} as a floor while still drawing to the {chase[1]}"
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
        valuable = [c.get("index") for c in hand if not c.get("debuff") and c.get("index") not in keep
                    and (any(e in _enh(c) for e in ("Glass", "Steel", "Gold", "Mult", "Lucky")) or c.get("seal") == "Red" or c.get("edition"))]
        if valuable and len(keep) + len(valuable) < len(hand):
            keep = keep + valuable
            why += f"; keeping enhanced/sealed cards {valuable}"
        # held-card jokers: Shoot the Moon Queens / Baron Kings score while HELD (7805 discarded a held Queen twice)
        held_val = [c.get("index") for c in hand if not c.get("debuff") and c.get("index") not in keep and c.get("rank") is not None and _r(c) in protect_ranks]
        if held_val and len(keep) + len(held_val) < len(hand):
            keep = keep + held_val
            why += f"; keeping {', '.join(sorted({_r(c) for c in hand if c.get('index') in held_val}))} held for your held-card joker"
        if boss_name == "The Mark" and not (d.get("blind") or {}).get("disabled"):
            # The Mark deals every face card face-down: those cards are J/Q/K (pairs with each other ~78% of the time with 3),
            # never junk (7806 discarded all three)
            fd_m = [c.get("index") for c in lst(d.get("hand")) if c.get("rank") is None and c.get("index") not in keep]
            if fd_m and len(keep) + len(fd_m) < len(all_idx):
                keep = keep + fd_m
                why += f"; keeping face-down {fd_m}: under The Mark they are face cards"
        # a debuffed card still counts for the hand TYPE (and for flushes): keep it when it is part of what we keep
        # (7803: The Head, the discard list broke the pair it claimed to keep); discard the other debuffed cards first
        debuffed_idx = [c.get("index") for c in hand if c.get("debuff") and c.get("index") not in keep]
        if debuffed_idx:
            why += f"; debuffed cards {debuffed_idx} score nothing, discard them first"
        mail_r = ((d.get("run") or {}).get("mail_card") or {}).get("rank") if any(j.get("name") == "Mail-In Rebate" and not j.get("debuff") for j in lst(d.get("jokers"))) else None
        rest_d = [i for i in all_idx if i not in keep and i not in debuffed_idx]
        if boss_name != "The Mark":
            # The House/Fish/Wheel face-downs are unknown random cards: they go first (7805 kept a face-down and threw visible ones)
            fd_set = {c.get("index") for c in hand if c.get("rank") is None}
            rest_d = sorted(rest_d, key=lambda i: i not in fd_set)
        if mail_r:
            # Mail-In Rebate pays $5 per discarded card of this round's rank: discard those first (7805 missed ~$40)
            rest_d = sorted(rest_d, key=lambda i: str((_cards_by_idx(d, [i]) or [{}])[0].get("rank")) != str(mail_r))
            why += f"; Mail-In Rebate: {mail_r}s discarded first ($5 each)"
        disc = (debuffed_idx + rest_d)[:5]
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


GATE_WORDS = (("two pair", "Two Pair"), ("three of a kind", "Three of a Kind"), ("four of a kind", "Four of a Kind"),
              ("straight", "Straight"), ("flush", "Flush"), ("full house", "Full House"))


def _joker_gated_hand(d):
    """Hand type an owned hand-gated joker asks for (Clever/Mad -> Two Pair, Zany/Wily/The Trio -> Three of a Kind, ...);
    Pair-gated jokers (Jolly, Sly, The Duo) fire on every pair-family hand and decide nothing. None when no gate."""
    votes = Counter()
    for j in lst(d.get("jokers")):
        if j.get("debuff") or _dead_perishable(j):
            continue
        n = j.get("name")
        if n in TYPE_X_JOKERS and TYPE_X_JOKERS[n][0] != "Pair":
            votes[TYPE_X_JOKERS[n][0]] += 2  # an xMult gate outweighs a flat one
            continue
        desc = JOKER_DESC.get(n, "").lower()
        if " if " in desc:
            cond = desc.split(" if ", 1)[1]
            hit = next((t for w, t in GATE_WORDS if cond.startswith(w)), None)
            if hit:
                votes[hit] += 1
    return max(votes, key=lambda t: (votes[t], t in ("Two Pair", "Three of a Kind", "Full House"))) if votes else None


def main_hand(d):
    """_main_hand_raw with hysteresis (Fable 7801: the main hand flipped Pair/Two Pair across shops): outside the hard
    invariants, a new main hand replaces the remembered one (data/.cli_cache/<port>_mainhand.json, set by `b`) only
    after it was >= 20% better per hand in 2 consecutive shops."""
    raw = _main_hand_raw(d)
    h = d.get("_mh_hyst") or {}
    if h.get("run") != d.get("trajectory"):
        h = {}  # memory from another run on this port (7802 JB7Q6L46 inherited a stale Flush)
    prev = h.get("mh")
    if not prev or raw == prev or raw == "undecided" or d.get("_mh_forced") or prev not in SYN_HANDS:
        return raw
    hl = d.get("hand_levels") or {}
    pv, rv = hl.get(prev) or {}, hl.get(raw) or {}
    if int(pv.get("played") or 0) < int(rv.get("played") or 0) and int(pv.get("level") or 1) <= int(rv.get("level") or 1):
        return raw  # the remembered hand is now both less played and not higher level: nothing to stick to
    if h.get("pend") == raw and int(h.get("n") or 0) >= 2:
        return raw
    return prev


def _mh_hyst_update(d):
    """`b shopadvise`: advance the main-hand hysteresis state once per shop."""
    path = os.path.join(CACHE_DIR, f"{PORT}_mainhand.json")
    h = dict(d.get("_mh_hyst") or {})
    if h.get("run") != d.get("trajectory"):
        h = {}
    raw = _main_hand_raw(d)
    sig = json.dumps([d.get("ante"), d.get("round"), [x.get("id") for x in lst((d.get("shop") or {}).get("jokers"))]])
    prev = h.get("mh")
    if not prev or prev not in SYN_HANDS or d.get("_mh_forced") or raw == "undecided":
        h = {"mh": raw if raw != "undecided" else prev}
    elif raw == prev:
        h = {"mh": prev}
    elif typical_est(d, raw) >= 1.2 * typical_est(d, prev):
        if h.get("pend") == raw and h.get("sig") != sig:
            h["n"] = int(h.get("n") or 0) + 1
        elif h.get("pend") != raw:
            h.update(pend=raw, n=1)
        if int(h.get("n") or 0) >= 2:
            h = {"mh": raw}
    else:
        h = {"mh": prev}
    h["sig"] = sig
    h["run"] = d.get("trajectory")
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(h, f)
    except Exception:
        pass


def _mh_hyst_load():
    try:
        with open(os.path.join(CACHE_DIR, f"{PORT}_mainhand.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _main_hand_raw(d):
    hl = d.get("hand_levels") or {}
    # 1-card throwaways (Acrobat/Dusk final-hand holds, Crimson Heart re-rolls, Acorn probes) are logged as High Card plays:
    # they are not the hand you build (7803/7804 got Pluto picks from them)
    if any(j.get("name") in ("Acrobat", "Dusk") and not j.get("debuff") for j in lst(d.get("jokers"))) or \
            int((hl.get("High Card") or {}).get("played") or 0) < 0.6 * sum(int((v or {}).get("played") or 0) for v in hl.values()):
        hl = {k: v for k, v in hl.items() if k != "High Card"}
    best = None
    total = 0
    for name, v in hl.items():
        total += int(v.get("played") or 0)
        key = (int(v.get("played") or 0), int(v.get("played_this_round") or 0), int(v.get("level") or 1))  # plays, then recency
        if best is None or key > best[0]:
            best = (key, name)
    if not best or total < 3 or best[0][0] < 2:
        gate = _joker_gated_hand(d)
        return gate or "undecided"
    if int(d.get("ante") or 1) <= 2 and best[1] not in ("Pair", "Two Pair", "Three of a Kind", "Full House") and best[0][0] < 4:
        # a 2-3 hand Straight/Flush streak is dealt luck, not a plan; 4+ plays of one type are a plan (7809: six Flushes)
        return _joker_gated_hand(d) or "undecided"
    lead = best[1]
    # HARD INVARIANTS (Main 06:xx; 7809 read Flush with ~14 Pair plays at Pair L10): a type played >= 2x as often as
    # any other IS the main hand; otherwise a type leveled >= 3 above every other played type is
    pl = sorted(((int((v or {}).get("played") or 0), k) for k, v in hl.items()), reverse=True)
    if len(pl) == 1 or (pl[0][0] >= 3 and pl[0][0] >= 2 * pl[1][0]):
        d["_mh_forced"] = True
        return pl[0][1]
    lv = sorted(((int((v or {}).get("level") or 1), k) for k, v in hl.items() if int((v or {}).get("played") or 0) >= 2), reverse=True)
    if len(lv) >= 2 and lv[0][0] >= lv[1][0] + 3:
        d["_mh_forced"] = True
        return lv[0][1]
    if any(j.get("name") == "Card Sharp" and not j.get("debuff") for j in lst(d.get("jokers"))):
        # Card Sharp (x3 when the type was already played this round) wants the hand you can make 2-3 times a round:
        # the most played pair-family hand, Pair on ties; no re-anchor to a rarer, richer hand
        fam = [n for n in ("Pair", "Two Pair", "Three of a Kind", "Full House") if int((hl.get(n) or {}).get("played") or 0) > 0]
        if fam:
            return max(fam, key=lambda n: (int(hl[n].get("played") or 0), n == "Pair"))
        return lead
    # main hand = the type maximizing (typical est with current jokers and levels) x (how often you can make it, from this
    # run's plays). Containment: a Two Pair / Trips / Full House / Quads play shows you could have played a Pair, a Full
    # House shows Two Pair and Trips, but not the reverse. Replaces play-count thresholds that thrashed (7803 stuck on Two
    # Pair over 10 Pairs with Half Joker; 7809 read Pair with Clever owned and every big play Two Pair/Full House).
    plays = {k: int((v or {}).get("played") or 0) for k, v in hl.items()}
    CAPABLE = {"Pair": ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind"),
               "Two Pair": ("Two Pair", "Full House"), "Three of a Kind": ("Three of a Kind", "Full House", "Four of a Kind"),
               "Full House": ("Full House",), "Four of a Kind": ("Four of a Kind",), "Flush": ("Flush",), "Straight": ("Straight",),
               "High Card": ("High Card",)}
    value = {}
    for t, via in CAPABLE.items():
        freq = sum(plays.get(x, 0) for x in via)
        if freq >= 3 and t in SYN_HANDS:  # 1-2 lucky plays are not a plan: a type needs 3 plays to become the main hand
            value[t] = freq * typical_est(d, t)
    if not value:
        return lead
    # owned jokers that fire only on some types (Half Joker: <=3 cards, Clever: Two Pair, The Order: Straight...) anchor
    # the main hand to the types most of them fire on (7809 read Straight through ante 3 with Half Joker owned)
    owned = [j for j in lst(d.get("jokers")) if not j.get("debuff") and not _dead_perishable(j)]
    if len(value) > 1 and owned:
        fires = {t: sum(1 for j in owned if typical_est(d, t) > 1.05 * typical_est(d, t, [x for x in owned if x is not j])) for t in value}
        top_f = max(fires.values())
        if top_f > min(fires.values()):
            value = {t: v for t, v in value.items() if fires[t] == top_f}
    return max(value, key=lambda t: (value[t], t == lead))


AVOID_JOKERS = {"Madness": "destroys one of your jokers every blind", "Ceremonial Dagger": "destroys the joker to its right",
                "Ice Cream": "decays each hand", "Popcorn": "decays each round", "Turtle Bean": "decays",
                "Gros Michel": "1/6 to self-destruct", "Swashbuckler": "useless as the only joker",
                "Troubadour": "-1 hand per round: Black Deck has only 3",
                "Merry Andy": "-1 hand size"}


def classify_joker(name, cost, mh):
    desc = JOKER_DESC.get(name, "")
    dl = desc.lower()
    if name in TYPE_X_JOKERS and TYPE_X_JOKERS[name][0] != "Pair" and mh != "undecided" and not hand_contains(mh, TYPE_X_JOKERS[name][0]):
        return f"XMULT(conditional, other hand: needs {TYPE_X_JOKERS[name][0]}, your main hand is {mh})", 35
    if name in ("Bloodstone", "Ancient Joker", "Flower Pot", "Seeing Double") and mh not in ("Flush", "Straight Flush", "Flush House", "Flush Five"):
        # suit-gated: a 2-4 card pair-family hand rarely scores the right suit(s); fits Flush builds
        return "XMULT(conditional, suit: rarely fires outside a Flush build)", 35
    if name in AVOID_JOKERS:
        return "AVOID(" + AVOID_JOKERS[name] + ")", 5
    if name == "Acrobat":
        # x3 on the final hand of EVERY round (`advise` saves the best hand for it): the core xMult of the deepest Gold run
        return "XMULT(final hand: x3 every round)", 85
    if name == "Ramen":
        # x2 losing 0.01 per discarded card: at Gold (2 discards a round) still ~x1.5 after 5 rounds of full discards
        return "XMULT(decaying: x2, -0.01 per card discarded; discard less while it carries you)", 85
    if name == "Burnt Joker":
        return "LEVELS(first discarded hand type levels up every round: discard your main hand type first)", 95
    if name == "Astronomer":
        return "LEVELS(planets and Celestial packs free)", 85
    if name == "Space Joker":
        return "LEVELS(1/4 chance to level the played hand)", 65
    if name in ("Hiker", "Wee Joker", "Castle"):
        return "PLUS(permanent growth)", 60
    if name == "Mr. Bones":
        # survives one blind scored at >= 25% of its requirement, then destroys itself: a run-saver when under-scaled
        return "UTIL(run-saver: survive one blind at 25%, then destroyed)", 50
    if name == "Half Joker":
        # +20 mult on 3 or fewer played cards: every Pair/Trips/High Card play (Two Pair needs 4 cards)
        return ("PLUS(<=3 cards: fires on every Pair/Trips play)", 70) if mh in ("Pair", "Three of a Kind", "High Card", "undecided") else ("PLUS(<=3 cards: not your main hand)", 35)
    if name in ("Seltzer", "Hanging Chad", "Sock and Buskin", "Dusk", "Hack"):
        return f"PLUS(retrigger: {JOKER_DESC.get(name, '')})", 60
    if name in ("Walkie Talkie", "Square Joker", "Scary Face", "Smiley Face"):
        # rank/face-gated: fire only when specific ranks score; decent second joker, not a floor
        return ("PLUS(common condition)", 55) if name in ("Scary Face", "Smiley Face", "Walkie Talkie") else ("PLUS(rare condition)", 35)
    if name == "Ride the Bus":
        return "PLUS(growth: +1 mult per faceless hand, resets on a face)", 50
    if name == "Throwback":
        return "PLUS(x0.25 per skipped blind: useless, we never skip)", 15
    if name == "Hit the Road":
        return "PLUS(x0.5 per Jack discarded this round: rarely fires)", 30
    if name == "Obelisk":
        # 7807 WON with a foil Obelisk at x3.6: it grows x0.2 on every hand whose type is not STRICTLY your most played;
        # a flat chips/+mult build makes the type irrelevant, so rotate types and never feed the max type
        return "XMULT(growth: +x0.2 per hand of a type that is not strictly your most played)", 60
    if name in ("Blackboard", "Flower Pot", "Seeing Double", "Driver's License", "Joker Stencil", "Acrobat", "Loyalty Card", "Bloodstone", "Ancient Joker", "Baseball Card", "The Idol"):
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
        if ctype in ("Straight", "Flush"):
            # GOLD_ANALYSIS.md: 0 of 6 Flush/Straight-main runs reached ante 4 (17 of 28 pair-family did): never core
            return "PLUS(Flush/Straight-gated: non-core at Gold)", 35
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


# Ante base chips per game scaling (misc_functions.lua get_blind_amount): stake 1-2 scaling 1, stake 3-5 scaling 2,
# stake 6-8 scaling 3. Small = base, Big = 1.5x, Boss = 2x (The Wall 4x, Violet Vessel 6x).
BLIND_BASE = {1: (300, 800, 2000, 5000, 11000, 20000, 35000, 50000),
              2: (300, 900, 2600, 8000, 20000, 36000, 60000, 100000),
              3: (300, 1000, 3200, 9000, 25000, 60000, 110000, 200000)}


def _rounds_left(d):
    """Round-ends still ahead through the ante-8 boss (rent is charged and perishables tick at each one)."""
    ante = int(d.get("ante") or 1)
    ch = (d.get("blind_select") or {}).get("choices") or {}
    bl_left = sum(1 for k in ("Small", "Big", "Boss") if ((ch.get(k) or {}).get("state") or "Upcoming") not in ("Defeated", "Skipped"))
    return max(1, bl_left + 3 * max(0, 8 - ante))


def next_ante_targets(d):
    """(next ante, small, big, boss) from the base table, scaled by this ante's Small Blind chips from state (covers deck
    multipliers); None when unknown."""
    ante = int(d.get("ante") or 1); stake = int(d.get("stake") or 1)
    table = BLIND_BASE[3 if stake >= 6 else (2 if stake >= 3 else 1)]
    if not 1 <= ante < len(table):
        return None
    small_now = (((d.get("blind_select") or {}).get("choices") or {}).get("Small") or {}).get("chips")
    k = (float(small_now) / table[ante - 1]) if small_now else 1.0
    base = int(table[ante] * k)
    return ante + 1, base, int(base * 1.5), base * 2


SYN_HANDS = {"Pair": "KS KH", "Two Pair": "KS KH 9S 9D", "Three of a Kind": "KS KH KD", "Full House": "KS KH KD 9S 9D",
             "Four of a Kind": "KS KH KD KC", "Flush": "AH KH 9H 7H 4H", "Straight": "KS QH JD TC 9S", "High Card": "AS"}


def _syn_cards(spec, start=1):
    rk = {"A": "Ace", "K": "King", "Q": "Queen", "J": "Jack", "T": "10"}
    st = {"S": "Spades", "H": "Hearts", "D": "Diamonds", "C": "Clubs"}
    return [{"rank": rk.get(t[0], t[0]), "suit": st[t[1]], "index": start + i} for i, t in enumerate(spec.split())]


def typical_est(d, mh, jokers=None, best=False):
    """est of a synthetic main hand (Pair when undecided; KK-based, 3 neutral held cards) with the given jokers (default
    owned) and current levels: a stable 'what one hand scores' number for shop and skip decisions.
    best=True: the round's best hand with its always-on conditionals active (discards spent for Mystic Summit, final
    hand for Acrobat/Dusk, a repeat for Card Sharp): the 'ante's best hand' the survival thresholds were measured on."""
    hn = mh if mh in SYN_HANDS else "Pair"
    scoring = _syn_cards(SYN_HANDS[hn])
    held = _syn_cards("5C 6D 8S", start=len(scoring) + 1)
    state = dict(d, blind={}) if jokers is None else dict(d, blind={}, jokers=jokers)
    sharp = any(j.get("name") == "Card Sharp" and not j.get("debuff") for j in lst(state.get("jokers")))
    if best:
        state = dict(state, discards_remaining=0, hands_remaining=1)
    else:  # an ordinary hand early in the round (the shop obs carries last round's leftovers)
        state = dict(state, discards_remaining=int(d.get("discards_per_round") or 3), hands_remaining=int(d.get("hands_per_round") or 3))
    e = estimate(hn, scoring, held, state, played_n=len(scoring), repeat=True if sharp else None)[0]  # Card Sharp: repeats are the plan
    if not best and any(j.get("name") == "Mystic Summit" and not j.get("debuff") for j in lst(state.get("jokers"))):
        # Summit plan: discards burned before the first play, every hand +15 (PLAYBOOK; 7807 sold Summit for Ice Cream)
        e = max(e, estimate(hn, scoring, held, dict(state, discards_remaining=0), played_n=len(scoring), repeat=True if sharp else None)[0])
    return e


def round_est(d, mh, jokers=None):
    """est of a round: ordinary hands at the round start plus the final hand (Mystic Summit after the discards are spent,
    Acrobat/Dusk on the final hand) - the measure every joker's contribution is taken on."""
    h = int(d.get("hands_per_round") or 3)
    return typical_est(d, mh, jokers) * (h - 1) + typical_est(d, mh, jokers, best=True)


_SHARE_MEMO = {}


def joker_share(d, j, mh):
    """Fraction of a round's est this owned joker provides (1 - est without it / est with it), the larger of the KK
    synthetic round (round_est) and rounds dealt from your deck (deck_round_est: sees Half Joker on the 1-3 card plays you
    really make; 7803 was told to sell Half Joker, +20 of ~22 mult). Measures real contribution, not class."""
    if j.get("debuff"):
        return 0.0
    key = (id(d), id(j), mh)
    if key in _SHARE_MEMO:
        return _SHARE_MEMO[key]
    others = [x for x in lst(d.get("jokers")) if x is not j]
    with_j = round_est(d, mh)
    sh = max(0.0, 1 - round_est(d, mh, others) / with_j) if with_j > 0 else 0.0
    dw = deck_round_est(d)
    if dw:
        sh = max(sh, 1 - (deck_round_est(d, others) or 0) / dw)
    if len(_SHARE_MEMO) > 4096:
        _SHARE_MEMO.clear()
    _SHARE_MEMO[key] = sh
    return sh


def _deal_order(cards, state):
    """With Hanging Chad / Photograph the player reorders so the best card scores first: sampled deals do the same
    (faces, then high ranks first); otherwise the random deal order is kept (7805: SCORE CHECK 248-1560 vs real 8-12k)."""
    if any(j.get("name") in ORDER_JOKERS and not j.get("debuff") for j in lst(state.get("jokers"))):
        return sorted(cards, key=lambda c: (_r(c) not in FACES, -RANK_VAL.get(_r(c), 0)))
    return cards


def deck_round_est(d, jokers=None, samples=30, seed=11):
    """Median round total over deals from YOUR deck with the given jokers (default owned): best ordinary hand at the round
    start x (hands - 1) + best final hand (Summit/Acrobat/Dusk). Unlike the KK synthetic it sees rank/suit-gated jokers
    (Walkie Talkie, Even Steven, Scholar, Shoot the Moon...). None without deck data."""
    import random
    cards = [c for c in lst((d.get("deck") or {}).get("cards")) if c.get("rank") is not None]
    hs = int(d.get("hand_size") or 8)
    if len(cards) < hs:
        return None
    h = int(d.get("hands_per_round") or 3)
    base = dict(d, phase="SELECTING_HAND", blind={}, jokers=lst(d.get("jokers")) if jokers is None else jokers)
    st_ord = dict(base, hands_remaining=h, discards_remaining=int(d.get("discards_per_round") or 3))
    st_fin = dict(base, hands_remaining=1, discards_remaining=0)
    # Mystic Summit plan: burn the discards first, then every hand carries +15 (7807 sold Summit for a perishable Ice Cream)
    st_ord0 = dict(st_ord, discards_remaining=0) if any(j.get("name") == "Mystic Summit" for j in lst(base.get("jokers"))) else None
    rng = random.Random(seed)
    vals = []
    for _ in range(samples):
        deal = [dict(c, index=i + 1, facing="front", debuff=False, highlighted=False) for i, c in enumerate(_deal_order(rng.sample(cards, hs), base))]
        o = max((c[2] for st in (st_ord, st_ord0) if st is not None for c in _candidates(dict(st, hand=deal))), default=0)
        f = max((c[2] for c in _candidates(dict(st_fin, hand=deal))), default=0)
        vals.append(o * (h - 1) + f)
    vals.sort()
    return vals[len(vals) // 2]


def marginal_gain(d, mh, c, jokers=None):
    """Relative round-score gain from adding joker c: on deals from your deck when the deck is known, else on the KK
    synthetic round (round_est). The same measure ranks shop buys and pack picks."""
    own = lst(d.get("jokers")) if jokers is None else jokers
    # a Negative joker brings its own slot (Stencil sees no change); any other joker fills one (Stencil loses x1)
    d_c = dict(d, joker_slots=int(d.get("joker_slots") or 5) + 1) if _joker_edition(c) == "negative" else d
    b = deck_round_est(d, own)
    deck_g = deck_round_est(d_c, own + [c]) / b - 1 if b else None
    # the KK synthetic round on YOUR main hand sees hand-type-gated jokers (Mad Joker +10 on Two Pair) that the deck deals'
    # best hands often miss (7807 lost the ante-4 boss by 1304 with Mad Joker rated "adds ~0"); take the larger
    syn_g = round_est(d_c, mh, own + [c]) / (round_est(d, mh, own) or 1) - 1
    return syn_g if deck_g is None else max(deck_g, syn_g)


def is_scorer(d, j, mh):
    """ONE scorer test for blind select, shop and packs (7806: `s` said 1 scorer with 4 owned): a scoring class, a
    scoring edition, or 15%+ of a round's est."""
    if j.get("debuff") or _dead_perishable(j):
        return False
    return (_is_scoring_cls(classify_joker(j.get("name"), 0, mh)[0]) or _joker_edition(j) in ("holo", "foil", "polychrome")
            or joker_share(d, j, mh) >= 0.15)


def deck_best_est(d, samples=40, pct=0.75, seed=7):
    """SCORE CHECK from your real deck: deal `samples` random hands of your hand size from the full deck (ranks, suits,
    enhancements, editions), take each deal's best playable est (current jokers and levels, final-hand conditionals
    active) and return the pct quantile. Replaces the synthetic KK Pair, which ignored Odd Todd/Splash/Shoot the Moon
    held Queens (7804 2.4k shown vs ~5k real; 7802 495 vs 1540). None without deck data."""
    import random
    cards = [c for c in lst((d.get("deck") or {}).get("cards")) if c.get("rank") is not None]
    hs = int(d.get("hand_size") or 8)
    if len(cards) < hs:
        return None
    rng = random.Random(seed)
    base = dict(d, phase="SELECTING_HAND", blind={}, hands_remaining=1, discards_remaining=0,
                hands_per_round=d.get("hands_per_round") or 3)
    keep_disc = dict(base, discards_remaining=int(d.get("discards_per_round") or 3))  # Banner/Delayed Gratification
    vals = []
    for _ in range(samples):
        deal = [dict(c, index=i + 1, facing="front", debuff=False, highlighted=False) for i, c in enumerate(_deal_order(rng.sample(cards, hs), base))]
        vals.append(max((c[2] for st in (base, keep_disc) for c in _candidates(dict(st, hand=deal))), default=0))
    vals.sort()
    return vals[min(len(vals) - 1, int(pct * len(vals)))]


def _rg_x(cls):
    """reliable or growth xMult (GOLD_ANALYSIS.md: the jokers that carried deep runs); conditional/off-build ones excluded"""
    return cls == "XMULT" or cls.startswith(("XMULT(growth", "XMULT(decaying", "XMULT(Stencil", "XMULT(final hand"))

def _scores_now(cls):
    """the joker adds to ordinary hands today: any +chips/+mult joker or an xMult that is not still x1 (growth) or off-build"""
    if cls.startswith("PLUS"):
        return "adds ~0 now" not in cls and "useless" not in cls
    return cls.startswith("XMULT") and "growth" not in cls and "other hand" not in cls and "suit:" not in cls



def owned_value(d, j, mh):
    """keep value of an owned joker: its class score, raised by its real share of the main-hand est; a perished one is -100"""
    if _dead_perishable(j):
        return -100
    sc = classify_joker(j.get("name"), 0, mh)[1]
    share = joker_share(d, j, mh)
    return max(sc, min(140, 60 + int(100 * share))) if share >= 0.15 else sc


def sticker_adjust(c, cls, base_sc, score, ante, rounds_left, own_rentals, bridge, pack_free=None, core_hint=False):
    """Gold-stake value of a shop/pack joker's stickers. cls/base_sc: classify_joker result; score: shop score after
    situational bumps; rounds_left: round-ends still ahead (rent and perish ticks); own_rentals: rentals already held;
    bridge: ante 1-2 with fewer than two scorers (any scorer now beats a permanent one later).
    Returns (score, notes, may_replace): may_replace False = never sell an owned joker to make room for it."""
    s = _stk(c)
    pen, notes, may_replace = 0, [], True
    core = (_is_scoring_cls(cls) and base_sc >= 60) or cls.startswith(("LEVELS", "COPY", "COUNTER")) or core_hint
    growth = "growth" in cls
    # ante 1-2 with fewer than 2 scorers: surviving the next blinds beats any sticker cost on a joker that scores
    survive = bridge and ante <= 2 and _is_scoring_cls(cls) and not growth  # a growth xMult starts at x1: no survival help
    if survive and (s["eternal"] or s["rental"]):
        notes.append("NEEDED NOW: a scorer for the next blinds; survival beats the sticker cost at ante 1-2")
    in_pack = pack_free is not None  # a pack pick is already paid for: only future costs (slot, rent) count
    if s["eternal"] and not cls.startswith("AVOID"):
        if _joker_edition(c) == "negative":
            notes.append("ETERNAL but NEGATIVE: it brings its own slot, so it never blocks one")  # 7804: free negative eternal Zany
        elif in_pack and pack_free >= 2:
            notes.append(f"ETERNAL: harmless while you have {pack_free} free slots")
        elif core:
            notes.append("ETERNAL: fine, a core joker you would keep anyway")
        elif survive:
            pen += 10
        else:
            pen += 30 if cls == "ECON" else (20 if base_sc >= 50 else 35)
            may_replace = False
            notes.append("ETERNAL on a " + ("money joker you could never sell for a scorer later" if cls == "ECON" else "weak/conditional joker: it blocks a slot for the rest of the run"))
    if s["perishable"]:
        life = s["perish_tally"] if s["perish_tally"] is not None else 5
        if rounds_left <= life:
            notes.append(f"PERISHABLE({life}) outlasts the {rounds_left} round(s) left in the run: no cost")
        elif growth:
            pen += 40; may_replace = False
            notes.append(f"PERISHABLE growth joker: debuffed after {life} rounds, just when it has grown")
        elif cls.startswith("LEVELS"):
            pen += 10
            notes.append(f"PERISHABLE: works {life} rounds, but the levels it gives stay")
        else:
            pen += 5 if (in_pack or bridge) else 25; may_replace = in_pack
            notes.append(f"PERISHABLE: a short-term bridge, scores for {life} rounds (~{life / 3:.1f} antes) then is dead weight to sell")
    if s["rental"]:
        # a perishable rental is sold when it perishes, so its rent stops there
        life_r = (s["perish_tally"] if s["perish_tally"] is not None else 5) if s["perishable"] else None
        rent_rounds = min(rounds_left, life_r) if life_r is not None else rounds_left
        # data (GOLD_ANALYSIS.md): 41 rentals paid $393, mostly flat jokers held until the run died. Accept a rental only
        # for a reliable/growth xMult, or to survive ante 1-2 with fewer than 2 scorers.
        rg_x = _rg_x(cls)  # incl. Acrobat (final hand) and Stencil
        if s["eternal"] and not core_hint and ante < 7:
            pr = 60; may_replace = False  # unsellable rent for the rest of the run (7807: Raised Fist{ETERNAL,RENTAL} -$66 BUY)
        elif ante >= 7 or (survive and not own_rentals):
            pr = 5
        elif (rg_x or core_hint) and not s["eternal"]:
            pr = 10
        elif core_hint:
            pr = 20  # an eternal rental that adds 30%+ to every round (7805 holo Dusk $1 ranked 27, the blind was lost by 132)
        elif s["eternal"]:
            pr = 45; may_replace = False
        else:
            pr = 40; may_replace = False
        if in_pack and not (s["eternal"] and not core_hint):
            pr = min(pr, 5 if bridge else 20)  # no purchase price; only the rent remains, and a scorer you need beats it
        if life_r is not None and life_r < rounds_left:
            pr = min(pr, 10 + 2 * life_r)  # a perishable rental's rent stops when it perishes: at most ~$15
        pen += pr
        if cls == "ECON":
            pen += 45  # a money joker paying ~$3-4 a round minus $3 rent nets ~$0 and still takes a slot
            notes.append("RENTAL money joker: its income roughly equals the rent, net ~$0")
        if own_rentals and ante <= 4:
            # two permanent rentals = -$6/round, more than the blinds pay (drained 7808 to $0 by ante 2); a perishable one is
            # bounded; a joker that adds 30%+ to every round pays its rent (7803: Ramen x2 ranked 25 as a third rental)
            pen += 15 if (life_r is not None or core_hint) else 60
            may_replace = may_replace and (life_r is not None or core_hint)
        elif own_rentals and ante < 7:
            pen += 10 if life_r is not None else 25 * own_rentals
        until = "until it perishes, then sell it" if life_r is not None and life_r < rounds_left else ("if kept to the end" if not s["eternal"] else "for the rest of the run")
        notes.append(f"RENTAL: ${int(c.get('cost') or 0)} now, then -$3 x {rent_rounds} round(s) = -${3 * rent_rounds} {until} (~$9/ante + lost interest while held)"
                     + ("; ETERNAL too, so it can never be sold to stop the charge" if s["eternal"] else "; selling it ($1) stops the charge")
                     + ((f"; you already pay rent on {own_rentals} (this one's rent stops when it perishes)" if life_r is not None else
                         f"; you already pay rent on {own_rentals}: a second rental before ante 5 drains the run to $0") if own_rentals and ante <= 4
                        else (f"; you already pay rent on {own_rentals}" if own_rentals else "")))
    if in_pack and s["perishable"] and not growth:
        pen = min(pen, 20)  # already paid for and gone in ~5 rounds: its total future cost is bounded
    if s["eternal"] and s["rental"] and ante < 7:
        # unsellable rent for the rest of the run: never a buy before ante 7, not even NEEDED NOW (7807's winning run
        # passed Raised Fist{ETERNAL,RENTAL}: -$66)
        notes = [n for n in notes if not n.startswith("NEEDED NOW")] + ["ETERNAL on a RENTAL: -$3 every round for the rest of the run, never sellable"]
        return min(score - pen, 20), notes, False
    if any(n.startswith("NEEDED NOW") for n in notes):
        notes = [n for n in notes if n.startswith("NEEDED NOW")] + [n for n in notes if not n.startswith("NEEDED NOW")]
    return score - pen, notes, may_replace


def shop_advise(d):
    """Rule-based shop advice (_shop_rules). A perished joker is sold FIRST without hiding the ranking (Main 03:4x): its
    sell line is folded into the single ADVICE line."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _shop_rules(d)
    lines = buf.getvalue().splitlines()
    sf = next((ln for ln in lines if ln.startswith("  SELL FIRST: ")), None)
    if sf:
        cmd_sf = sf.split("SELL FIRST: ")[1].split("   ")[0]
        lines = [(f"ADVICE: SELL FIRST -> {cmd_sf}  then  {ln.split(' -> ', 1)[1] if ' -> ' in ln else ln[8:]}   (after the sell, joker indices right of it shift down by 1: re-run shopadvise)"
                  if ln.startswith("ADVICE:") else ln) for ln in lines]
    print("\n".join(lines))


_SHOP_SIM = None


def _shop_sim():
    """python/balatro_env/shop_sim.py loaded by path (DrawSolver's simulator of the next 3 blinds per shop option)."""
    global _SHOP_SIM
    if _SHOP_SIM is None:
        import importlib.util
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shop_sim.py")
        spec = importlib.util.spec_from_file_location("shop_sim", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SHOP_SIM = mod
    return _SHOP_SIM


def shop_advise_sim(d, budget_s=6.0):
    """`b shopadvise`: the rule advice plus a SIM section (shop_sim.value_options: each affordable buy played through the
    next 3 blinds). The SIM ranks by delta vs buying nothing (its absolute p is pessimistic: AUC 0.86 for ranking only);
    it breaks ties between buys the rules scored within 5 points and flags a disagreement > 0.05."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        shop_advise(d)
    lines = buf.getvalue().splitlines()
    adv_i = next((i for i, ln in enumerate(lines) if ln.startswith("ADVICE:")), None)
    if adv_i is None or d.get("phase") != "SHOP":
        print("\n".join(lines)); return
    try:
        ss = _shop_sim()
        opts = ss.options_from_state(d, packs=True)  # Buffoon/Celestial packs valued as their expected best pick
        sh_items = lst((d.get("shop") or {}).get("jokers"))
        for o in opts:
            item = o.get("add_joker") or (o.get("add_cards") or [None])[0]
            if item is None and o.get("levels"):
                nm = o.get("label", "").split(" $")[0].replace("buy ", "", 1)
                item = next((c for c in sh_items if c.get("name") == nm), None)
            if o.get("booster_index") is not None:
                o["_cmd"] = f"pack {o.get('booster_index')}"
                continue
            o["_cmd"] = f"buy {item.get('index')}" if item is not None and item.get("index") is not None else None
        res = ss.value_options(d, opts, budget_s=budget_s, estimate_fn=estimate, seed=0, min_samples=24)  # fixed seed; packs need the larger budget
    except Exception as e:
        lines.insert(adv_i, f"  (SIM unavailable: {type(e).__name__}: {e})")
        print("\n".join(lines)); return
    feas = [r for r in res if r.get("feasible") and r.get("label") != "baseline (no change)"]
    if not any(r["option"].get("_cmd") for r in feas):
        print("\n".join(lines)); return
    all_zero = all((r.get("p_next") or 0) < 0.05 for r in feas)
    # p_adj: p_next minus rent and dead-shop penalties (shop_sim, 09:xx); ranking and the ADVICE switch use it
    key = (lambda r: r.get("score_ratio") or 0) if all_zero else (lambda r: r.get("p_adj", r.get("p_next")) or 0)
    sim = (["  SIM: no option clears the next 3 blinds; ranking by expected score ratio"] if all_zero else []) + [
        f"  SIM: {r['label']}: " + (f"score ratio {r.get('score_ratio') or 0:.2f}" if all_zero else
                                    f"P(clear all next 3 blinds) {r.get('p_next') or 0:.2f}, rent-adjusted {key(r):.2f} ({r.get('delta_adj', r.get('delta')) or 0:+.2f} vs buying nothing)")
        + f" ${r.get('money_after')}" + (f" rent {r['rent_per_round']}/round" if r.get("rent_per_round") else "")
        + (f" | a later shop sees ${r['shop_money']}" if r.get("shop_money") is not None and r["shop_money"] < 5 else "")
        + (f" | ETERNAL RENTAL: -${3 * _rounds_left(d)} to the run's end, beyond the SIM's 3 blinds"
           if _stk(r["option"].get("add_joker") or {})["eternal"] and _stk(r["option"].get("add_joker") or {})["rental"] else "")
        for r in sorted(feas, key=key, reverse=True)[:6]]
    adv = lines[adv_i]
    out_all = "\n".join(lines)
    # SIM PRIMARY (orchestrator 06:4x: ~10 post-mortems where the rule score contradicted the SIM and the SIM was right).
    # Jokers/planets/playing cards are chosen by SIM delta (score ratio when every p < 0.05); the rule score only breaks
    # SIM ties within 0.03 and decides what the SIM cannot model (packs, vouchers, tarots, boss counters, sells first).
    # Hard money/sticker rules stay: no eternal rental before ante 7, no 2nd rental before ante 6, the $ floor unless
    # TIGHT/EMERGENCY.
    rank = {}
    for ln in lines:
        mm = re.match(r"^\s{1,4}(-?\d{1,3}) ((?:buy|pack) \d+)\s", ln)
        if mm:
            rank[mm.group(2)] = int(mm.group(1))
    mf = re.search(r"money floor \$(\d+)", out_all)
    floor_v = int(mf.group(1)) if mf else 0
    floor_off = "TIGHT:" in out_all or "EMERGENCY" in out_all
    m_sr = re.search(r"\(ratio (\d+\.\d+);", out_all)
    sc_ratio_s = float(m_sr.group(1)) if m_sr else 9.0
    ante_s = int(d.get("ante") or 1)
    own_rent = any(_stk(j)["rental"] for j in lst(d.get("jokers")))
    m0 = re.search(r"b (buy|buyuse|pack) (\d+)", adv)
    adv_cmd0 = f"{'pack' if m0.group(1) == 'pack' else 'buy'} {m0.group(2)}" if m0 else None
    base0 = next((r for r in feas if not r["option"].get("_cmd")), None)
    key0 = key(base0) if base0 else 0

    def allowed(r):
        aj = r["option"].get("add_joker") or {}
        st = _stk(aj)
        if st["eternal"] and st["rental"] and ante_s < 7:
            # exception (7806 lost the ante-4 Small by 79 after a $1 eternal-rental The Trio at SIM +0.23 was blocked):
            # an xMult while SCORE CHECK < 0.5 and the SIM gain is >= 0.15
            x_cls = classify_joker(aj.get("name"), 0, main_hand(d))[0].startswith("XMULT") or aj.get("name") in TYPE_X_JOKERS
            if not (x_cls and sc_ratio_s < 0.5 and key(r) - key0 >= 0.15):
                return False
        # a second PERMANENT rental before ante 6 drains the run; a perishable one is bounded, and a buy the rules already
        # advised passed their own rental checks (7809: The Duo perishable rental +0.40 was turned into LEAVE)
        if st["rental"] and not st["perishable"] and own_rent and ante_s < 6 and r["option"].get("_cmd") != adv_cmd0:
            return False
        # the $ floor binds unless TIGHT/EMERGENCY, the rules exempted this very buy, or the SIM gain is large (+0.15)
        if not floor_off and r.get("money_after") is not None and int(r.get("money_after") or 0) < floor_v and int(r["option"].get("cost") or 0) > 0 \
                and r["option"].get("_cmd") != adv_cmd0 and key(r) - key0 < 0.15:
            return False
        return True
    base = next((r for r in feas if not r["option"].get("_cmd")), None)
    cands_s = [r for r in feas if r["option"].get("_cmd") and allowed(r)]
    best = None
    if cands_s:
        top_k = max(key(r) for r in cands_s)
        tied = [r for r in cands_s if key(r) >= top_k - 0.03]
        best = max(tied, key=lambda r: (rank.get(r["option"]["_cmd"], -999), key(r)))
    gain = (key(best) - key(base)) if best and base else 0.0
    m = re.search(r"b (buy|buyuse|pack) (\d+)", adv)
    adv_cmd = f"{'pack' if m.group(1) == 'pack' else 'buy'} {m.group(2)}" if m else None
    sim_cmds = {r["option"].get("_cmd") for r in feas if r["option"].get("_cmd")}
    keep_rule = any(w in adv for w in ("COUNTER", "SELL FIRST", "USE first", "SELL first", "rerolls the boss", "MAIN SCALING")) or \
        (adv_cmd not in sim_cmds and adv.split("(")[0].strip() not in ("ADVICE: LEAVE -> b endshop", "ADVICE: REROLL -> b reroll") and gain < 0.05)
    if "MAIN SCALING" in adv and gain >= 0.05:
        keep_rule = False  # a main-hand planet levels forever (beyond the SIM's 3 blinds); only a clearly better buy replaces it
    if not keep_rule:
        if best is not None and gain > 0.02:
            new_cmd = best["option"]["_cmd"]
            sell_ix = best["option"].get("sell")
            sell_ix = sell_ix[0] if isinstance(sell_ix, list) and sell_ix else None
            new = (f"ADVICE: SELL then BUY -> b sell {sell_ix}  then  b {new_cmd}" if sell_ix else f"ADVICE: BUY -> b {new_cmd}") + \
                f"   (SIM: {best['label']} {'score ratio' if all_zero else 'p_next'} {key(best):.2f} vs {key(base):.2f} buying nothing" + \
                (f"; rule score {rank.get(new_cmd)}" if new_cmd in rank else "") + ")"
            if new.split("   ")[0] != adv.split("   ")[0]:
                sim.append(f"  (rule advice was: {adv[8:]})")
                adv = new
        elif adv_cmd in sim_cmds and int(next((r["option"].get("cost") or 0 for r in feas if r["option"].get("_cmd") == adv_cmd), 1)) > 0:
            # LEAVE only when the SIM says the rule pick HURTS (< -0.02); a neutral pick (Egg, Fortune Teller) stays with the
            # rules (money / long-term value), and a $0 item is never vetoed
            mine = next((r for r in feas if r["option"].get("_cmd") == adv_cmd), None)
            g_m = (key(mine) - key(base)) if mine and base else 0
            forced = "NEEDED NOW" in adv or "EMERGENCY" in adv  # a survival-forced buy must actually help survival (7810 Banner)
            if g_m < -0.02 or (forced and g_m <= 0.0):
                sim.append(f"  (rule advice was: {adv[8:]})")
                adv = f"ADVICE: LEAVE -> b endshop   (SIM: the rule pick changes P(clear all next 3 blinds) by {g_m:+.2f}; nothing on offer raises it by more than 0.02)"
            else:
                sim.append(f"  (SIM neutral on the rule pick ({g_m:+.2f}): the rules decide)")
    # INVARIANT: an affordable item with SIM gain >= 0.10 that passes the hard rules is never answered with LEAVE
    if adv.startswith("ADVICE: LEAVE") and best is not None and gain >= 0.10:
        sim.append(f"  (rule advice was: {adv[8:]})")
        sell_ix = best["option"].get("sell")
        sell_ix = sell_ix[0] if isinstance(sell_ix, list) and sell_ix else None
        adv = (f"ADVICE: SELL then BUY -> b sell {sell_ix}  then  b {best['option']['_cmd']}" if sell_ix else f"ADVICE: BUY -> b {best['option']['_cmd']}") + \
            f"   (SIM: {best['label']} +{gain:.2f} P(clear all next 3 blinds))"
    lines = lines[:adv_i] + sim + [adv] + lines[adv_i + 1:]
    print("\n".join(lines))


def pack_advise_sim(d, budget_s=3.5):
    """`b advise` in a pack: the rule pick plus SIM-primary choice among jokers/planets/cards (skip = baseline); hard
    sticker rules kept (no eternal rental before ante 7, no 2nd rental before ante 6). Spectral/Arcana picks (targets) stay
    with the rules."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        pack_advise(d)
    lines = buf.getvalue().splitlines()
    adv_i = next((i for i, ln in enumerate(lines) if ln.startswith("ADVICE:")), None)
    if adv_i is None or d.get("phase") != "PACK_OPENING":
        print("\n".join(lines)); return
    try:
        ss = _shop_sim()
        opts = ss.options_from_state(d)
        cards = lst((d.get("pack") or {}).get("cards"))
        for o in opts:
            item = o.get("add_joker") or (o.get("add_cards") or [None])[0]
            if item is None and o.get("levels"):
                nm = o.get("label", "").replace("take ", "", 1).split(" $")[0]
                item = next((c for c in cards if c.get("name") == nm), None)
            pos = next((i for i, c in enumerate(cards, 1) if c is item or (item is not None and c.get("id") == item.get("id") and c.get("name") == item.get("name"))), None)
            o["_cmd"] = f"pick {pos}" if pos else None
        res = ss.value_options(d, opts, budget_s=budget_s, estimate_fn=estimate, seed=0, min_samples=48)
    except Exception as e:
        lines.insert(adv_i, f"  (SIM unavailable: {type(e).__name__}: {e})")
        print("\n".join(lines)); return
    feas = [r for r in res if r.get("feasible") and r.get("label") != "baseline (no change)"]
    if not any(r["option"].get("_cmd") for r in feas):
        print("\n".join(lines)); return
    all_zero = all((r.get("p_next") or 0) < 0.05 for r in feas)
    key = (lambda r: r.get("score_ratio") or 0) if all_zero else (lambda r: r.get("p_adj", r.get("p_next")) or 0)
    ante_s = int(d.get("ante") or 1)
    own_rent = any(_stk(j)["rental"] for j in lst(d.get("jokers")))

    def allowed(r):
        aj = r["option"].get("add_joker") or {}
        st = _stk(aj)
        # packs are already paid: only an unsellable rental or a second PERMANENT rental is barred
        return not (st["eternal"] and st["rental"] and ante_s < 7) and not (st["rental"] and not st["perishable"] and own_rent and ante_s < 6)
    sim = (["  SIM: no option clears the next 3 blinds; ranking by expected score ratio"] if all_zero else []) + [
        f"  SIM: {r['label']}: " + (f"score ratio {r.get('score_ratio') or 0:.2f}" if all_zero else f"P(clear all next 3 blinds) {r.get('p_next') or 0:.2f} ({r.get('delta') or 0:+.2f} vs skipping)")
        for r in sorted(feas, key=key, reverse=True)[:6]]
    adv = lines[adv_i]
    base = next((r for r in feas if not r["option"].get("_cmd")), None)
    cands_s = [r for r in feas if r["option"].get("_cmd") and allowed(r)]
    if cands_s and base:
        top_k = max(key(r) for r in cands_s)
        rule_pick = (re.search(r"b (pick \d+)", adv) or [None, None])[1]
        tied = [r for r in cands_s if key(r) >= top_k - 0.03]
        best = next((r for r in tied if r["option"]["_cmd"] == rule_pick), None) or max(tied, key=key)
        if key(best) - key(base) > 0.02:
            sell_ix = best["option"].get("sell")
            sell_ix = sell_ix[0] if isinstance(sell_ix, list) and sell_ix else None
            new = (f"ADVICE: SELL then PICK -> b sell {sell_ix}  then  b {best['option']['_cmd']}" if sell_ix else f"ADVICE: PICK -> b {best['option']['_cmd']}") + \
                f"   (SIM: {best['label']} {key(best):.2f} vs {key(base):.2f} for skipping)"
            if new.split("   ")[0] != adv.split("   ")[0]:
                sim.append(f"  (rule advice was: {adv[8:]})")
                adv = new
        elif any(r["option"].get("_cmd") == rule_pick and r["option"].get("add_joker") for r in feas):
            # only a JOKER pick can be worse than skipping (stickers, a slot); a free planet/card never is
            sim.append(f"  (rule advice was: {adv[8:]})")
            adv = "ADVICE: SKIP -> b skippack   (SIM: no pick raises survival over the next 3 blinds by more than 0.02)"
    lines = lines[:adv_i] + sim + [adv] + lines[adv_i + 1:]
    print("\n".join(lines))


def _shop_rules(d):
    _SHARE_MEMO.clear()
    if d.get("phase") != "SHOP":
        print("shopadvise only works in the shop"); return
    money = int(d.get("money") or 0); ante = int(d.get("ante") or 1)
    jokers = lst(d.get("jokers")); slots = int(d.get("joker_slots") or 5)
    free = slots - len(jokers)
    mh = main_hand(d)
    sh = d.get("shop") or {}
    stake = int(d.get("stake") or 1)
    ch_now = (d.get("blind_select") or {}).get("choices") or {}
    bl_left = sum(1 for k in ("Small", "Big", "Boss") if ((ch_now.get(k) or {}).get("state") or "Upcoming") not in ("Defeated", "Skipped"))
    rounds_left = _rounds_left(d)
    # a perished joker still counts for Abstract Joker (+3 mult) and Swashbuckler: keep it while a slot is free (Main 07:xx)
    dead = [j for j in jokers if _dead_perishable(j)
            and not (free > 0 and any(x.get("name") in ("Abstract Joker", "Swashbuckler") and not x.get("debuff") for x in jokers))]
    if dead:
        j = dead[0]
        print(f"  SELL FIRST: b sell {j.get('index')}   ({j.get('name')} has perished: debuffed for the rest of the run, it scores nothing; selling returns ${j.get('sell_cost')} and frees the slot)")
        jokers = [x for x in jokers if x is not j]
        d = dict(d, jokers=jokers, money=int(d.get("money") or 0) + int(j.get("sell_cost") or 0))
        money = int(d.get("money") or 0)
        free = slots - len(jokers)
    rentals = [j for j in jokers if _stk(j)["rental"]]
    rent_due = 3 * len(rentals)  # charged at the next round end: a reroll never spends it (7809: $8 -> $3 with two rentals)
    if rentals:
        print(f"  Rentals owned: {', '.join(str(j.get('name')) for j in rentals)} = -${3 * len(rentals)} every round (~${9 * len(rentals)}/ante + lost interest) until sold; selling one returns $1 and stops its charge")
    # the game never lets you sell an Eternal joker; selling Credit Card in debt resets the debt limit, so the buy it funds
    # becomes impossible (Main 07:xx)
    sellable_j = [j for j in jokers if not _stk(j)["eternal"] and not (j.get("name") == "Credit Card" and money < 0)]

    def alive_next(j):
        """still scoring after the blinds left in this ante: perishables count only if their tally outlasts them"""
        s_a = _stk(j)
        return not s_a["perishable"] or s_a["perish_tally"] is None or s_a["perish_tally"] > bl_left
    expiring = [j for j in jokers if _stk(j)["perishable"] and _stk(j)["perish_tally"] is not None and _stk(j)["perish_tally"] <= 3]
    if expiring:
        print("  WARNING: perishing soon: " + ", ".join(f"{j.get('name')} ({_stk(j)['perish_tally']} round(s) left)" for j in expiring)
              + f"; {bl_left} blind(s) left this ante. Plan with the scorers that are still alive next ante (counted below) and buy a permanent replacement now; a perished joker scores nothing.")
    # GOLD_ANALYSIS.md: 8 of 20 missed reliable/growth xMults were unaffordable; every shop xMult bought by the ante-5+
    # runs was bought with $11-22. From ante 2 keep $8 after anything that is not an xMult, the main-hand planet or a
    # Buffoon pack (while owning <2 reliable/growth xMults); the floor is NOT suspended when under-scaled.
    floor = 0 if ante <= 1 else (8 if ante <= 4 else (10 if ante <= 6 else 0))
    def _fits_x(cls_x):
        return cls_x.startswith("XMULT") and "other hand" not in cls_x and "suit:" not in cls_x
    # card-trigger xMults (Photograph, Triboulet) fire while cards score, BEFORE joker-main +mult is added, so on a flat
    # +mult build they are worth ~+20%, not x2: they do not count toward the xMult targets
    n_x_now = sum(1 for j in jokers if alive_next(j) and j.get("name") not in CARD_TRIGGER_JOKERS and (_fits_x(classify_joker(j.get("name"), 0, mh)[0]) or _joker_edition(j) == "polychrome"))
    n_rg = sum(1 for j in jokers if alive_next(j) and j.get("name") not in CARD_TRIGGER_JOKERS and (_rg_x(classify_joker(j.get("name"), 0, mh)[0]) or _joker_edition(j) == "polychrome"))
    main_lvl = int(((d.get("hand_levels") or {}).get(mh) or {}).get("level") or 1) if mh != "undecided" else 1
    # SCORE CHECK (survival by the ante's best hand: < boss/3 died 15/15, boss/3..boss/2 died 8/10, >= boss/2 died 16/106)
    best_now = typical_est(d, mh)  # an ordinary hand: the base for marginal joker values
    best_hand = typical_est(d, mh, best=True)  # synthetic best hand of a round: base for marginal joker values
    deck_best = deck_best_est(d)  # survival measure: 75th pct best hand over 40 deals of YOUR deck
    nxt = next_ante_targets(d)
    boss_this = int((ch_now.get("Boss") or {}).get("chips") or 0) if (ch_now.get("Boss") or {}).get("state") != "Defeated" else 0
    boss_next = nxt[3] if nxt else 0
    # calibrated on 1120 recorded Gold shops (deck p75 best-hand est / (next boss / 3) vs died by the next ante; AUC 0.77,
    # synthetic KK hand 0.74): <0.35 died 84%, 0.35-0.7 65%, 0.7-1 38%, 1-1.5 31%, >=1.5 18%. EMERGENCY = lowest band.
    surv = deck_best if deck_best is not None else best_hand
    sc_ratio = surv / (boss_next / 3) if boss_next else 9
    emergency = ante >= 2 and boss_next and sc_ratio < 0.35
    if ante >= 2:
        band = "84%" if sc_ratio < 0.35 else "65%" if sc_ratio < 0.7 else "38%" if sc_ratio < 1 else "31%" if sc_ratio < 1.5 else "18%"
        print(f"  SCORE CHECK: " + (f"best hand of a deal from your deck (75th pct of 40 deals, current jokers/levels) ~{deck_best}" if deck_best is not None
                                    else f"best {mh if mh != 'undecided' else 'Pair'} of a round (KK, current jokers/levels) ~{best_hand}")
              + (f" vs boss/2 {boss_this // 2} this ante" if boss_this else "") + (f", boss/3 {boss_next // 3} next ante (ratio {sc_ratio:.2f}; recorded Gold runs at this ratio died {band} by the next ante)" if boss_next else "")
              + (": EMERGENCY: buy the cheapest multiplier, through the money floor (reliable/growth xMult > conditional xMult > Buffoon pack > main-hand planet)" if emergency else ""))
    # TIGHT: the next blind's projected round (ordinary hands + the final hand, scaled to your deck) under 1.2x its need
    # -> money floor off: interest is worth nothing if the run ends (7805 lost the ante-5 boss by 132 holding $12)
    nk = next((k for k in ("Small", "Big", "Boss") if ((ch_now.get(k) or {}).get("state") or "Upcoming") not in ("Defeated", "Skipped")), None)
    need_next = int((ch_now.get(nk) or {}).get("chips") or 0) if nk else 0
    proj = int(round_est(d, mh) * ((deck_best / best_hand) if deck_best and best_hand else 1))
    tight = bool(need_next) and proj < 1.2 * need_next
    if tight:
        floor = 0
        print(f"  TIGHT: next blind ({(ch_now.get(nk) or {}).get('name') or nk}) needs {need_next}; projected round ~{proj} ({proj / need_next:.2f}x < 1.2x): "
              f"recorded Gold shops at this ratio lost the next blind {'40' if proj < 0.5 * need_next else '32' if proj < 0.8 * need_next else '13'}% (>= 1.2x: 6% or less). "
              "Money floor OFF - spend on whatever adds main-hand score now (main-hand planet, Celestial/Arcana pack, scorer)")
    mh_lv = (d.get("hand_levels") or {}).get(mh) or {}
    mh_why = f" (L{mh_lv.get('level') or 1}, {mh_lv.get('played') or 0} plays" + ("; forced: 2x the plays or +3 levels" if d.get("_mh_forced") else "") + ")" if mh != "undecided" else ""
    print(f"Shop advisor: ante {ante}, ${money}, jokers {len(jokers)}/{slots}, main hand {mh}{mh_why}, money floor ${floor} (spend below it only for an xMult, your main-hand planet or a Buffoon pack)"
          + (f", {rounds_left} round-ends left (rent/perish ticks)" if stake >= 7 else ""))
    splash_owned = any(j.get("name") == "Splash" for j in jokers)
    if bl_left == 3 and all((ch_now.get(k) or {}).get("chips") for k in ("Small", "Big", "Boss")):
        # shop right after a boss: the ante counter already moved on, so the next blinds belong to THIS ante
        print(f"  Next blinds (ante {ante}, from state): Small {ch_now['Small']['chips']} / Big {ch_now['Big']['chips']} / Boss {ch_now['Boss']['chips']}")
    if nxt and stake >= 2:
        small_now = (ch_now.get("Small") or {}).get("chips")
        jump = f" (x{nxt[1] / float(small_now):.1f} this ante)" if small_now else ""
        print(f"  Plan for ante {nxt[0]}: Small {nxt[1]} / Big {nxt[2]} / Boss {nxt[3]}+{jump}. Buy what clears THOSE in {d.get('hands_per_round') or 3} hands"
              + (": the ante-2 -> 3 jump is the steepest at Gold, an xMult or main-hand levels before leaving ante 2 decide it." if stake >= 6 and ante == 2 else "."))
    rg_target = 1 if ante <= 2 else (2 if ante <= 5 else 3)
    if stake >= 6 and n_rg < rg_target:
        print(f"  GOLD CHECK: {n_rg} reliable/growth xMult alive next ante; target {rg_target} by the end of ante {2 if ante <= 2 else (5 if ante <= 5 else 7)}"
              + (" (incl. a growing one)" if rg_target == 3 else "") + ". Pair builds with 0 xMult top out ~10k/hand at ante 5 (16.7k needed).")
    if mh in ("Flush", "Straight") and stake >= 6:
        print(f"  BUILD: your main hand is {mh}; at Gold 0 of 6 Flush/Straight-main runs reached ante 4 (17 of 28 pair-family runs did). "
              "Shift to Pair/Two Pair/Trips: their jokers and planets are ranked above Flush/Straight ones.")
    # Joker order matters only between joker-main effects that touch MULT: a +mult joker (or holo edition) right of a
    # joker-main xMult loses the multiplication. +chips add to chips, so their position is irrelevant; card-trigger
    # jokers (Photograph, Triboulet, Smiley...) fire while cards score; xMult jokers among themselves commute.
    def _main_x(j):
        return (j.get("name") not in CARD_TRIGGER_JOKERS and classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT")) or _joker_edition(j) == "polychrome"

    def _main_plus(j):
        d_p = JOKER_DESC.get(j.get("name"), "").lower()
        return (j.get("name") not in CARD_TRIGGER_JOKERS and classify_joker(j.get("name"), 0, mh)[0].startswith("PLUS") and "mult" in d_p) or _joker_edition(j) == "holo"
    # a holo xMult (The Tribe holo) is an xMult: it goes with the xMults, never among the +mult jokers (7803 got Summit
    # placed right of a holo Tribe)
    pure_plus = [i for i, j in enumerate(jokers) if _main_plus(j) and not _main_x(j)]
    first_x = next((i for i, j in enumerate(jokers) if _main_x(j)), None)
    if first_x is not None and any(i > first_x for i in pure_plus):
        x_idx = [i for i, j in enumerate(jokers) if _main_x(j)]
        desired = [i + 1 for i in pure_plus] + [i + 1 for i in range(len(jokers)) if i not in pure_plus and i not in x_idx] + [i + 1 for i in x_idx]
        # verify with est on the whole order: Brainstorm copies the LEFTMOST joker and Blueprint the one to its right, so a
        # move can change what they copy (7805: the tip would have moved Brainstorm off its Stencil target)
        cands_o = [desired]
        if len(jokers) <= 5:
            import itertools
            cands_o += [[i + 1 for i in p] for p in itertools.permutations(range(len(jokers)))]
        cur_e = round_est(d, mh)
        best_o = max(cands_o, key=lambda o: round_est(d, mh, [jokers[i - 1] for i in o]))
        best_e = round_est(d, mh, [jokers[i - 1] for i in best_o])
        if best_e >= 1.03 * cur_e and best_o != list(range(1, len(jokers) + 1)):
            print(f"  ORDER FIRST (free): b order {' '.join(map(str, best_o))}   (left to right AFTER: {', '.join(str(jokers[i - 1].get('name')) for i in best_o)}; "
                  f"now: {', '.join(str(j.get('name')) for j in jokers)}; round est {cur_e} -> {best_e}, both orders measured); then follow the ADVICE below")
    _is_scoring = _is_scoring_cls
    # planning unit: scorers alive next ante; a holographic/foil edition makes any joker a flat scorer (+10 mult / +50 chips)
    # (suit jokers, Stencil, ... count when they carry 15%+ of a round: 7810 Gluttonous and 7807 Stencil were "0 scorers")
    scoring_now = sum(1 for j in jokers if alive_next(j) and is_scorer(d, j, mh))
    if expiring or any(not alive_next(j) for j in jokers):
        print(f"  Scorers still alive next ante: {scoring_now}")
    owns_mult = any(alive_next(j) and ("mult" in JOKER_DESC.get(j.get("name"), "").lower() or _joker_edition(j) in ("holo", "polychrome")) for j in jokers)
    ENGINE_KEEP = {"Splash", "Four Fingers", "Shortcut", "Smeared Joker", "Pareidolia", "Blueprint", "Brainstorm", "Sock and Buskin", "Hack", "Dusk", "Mime", "Seltzer", "Hanging Chad"}
    if sc_ratio < 1.0:
        ENGINE_KEEP.add("Mr. Bones")  # under-scaled (SCORE CHECK < 1.0): Bones is the run-saver, never the sell target (Main 06:xx)
    def keep_value(j):
        """how much selling this joker would hurt: class score, economy jokers cheap from ante 4, editions add value,
        a perishable that dies before the run ends and a rental's -$3/round lower it; a joker that carries a big share
        of the main hand's est is kept whatever its class (Gros Michel as the only mult source)"""
        cls_k, sc_k = classify_joker(j.get("name"), 0, mh)
        share = joker_share(d, j, mh)
        if share >= 0.15:
            sc_k = max(sc_k, min(140, 60 + int(100 * share)))
        if cls_k == "ECON" and ante >= 4:
            sc_k = 20
        ed_k = _joker_edition(j)
        sc_k += 40 if ed_k == "polychrome" else (15 if ed_k in ("holo", "foil") else 0)
        nm_k, ab_k = j.get("name"), (j.get("ability") or {})
        ex_k = ab_k.get("extra") if isinstance(ab_k.get("extra"), dict) else {}
        if splash_owned and (nm_k in SUIT_JOKERS or nm_k in CARD_TRIGGER_JOKERS):
            sc_k = max(sc_k, 70)  # Splash: every played card scores, so per-card and suit jokers fire on all 5 cards
        if nm_k == "Ice Cream":
            sc_k = max(sc_k, min(70, int(ex_k.get("chips") or 0) // 2))  # value by the chips it still gives, not its decay
        if nm_k == "Popcorn":
            sc_k = max(sc_k, min(70, 3 * int(ab_k.get("mult") or 0)))
        s_k = _stk(j)
        if s_k["perishable"] and s_k["perish_tally"] is not None and s_k["perish_tally"] < rounds_left:
            sc_k -= 35 if s_k["perish_tally"] <= 1 else (20 if s_k["perish_tally"] <= 3 else 10)  # tally 1: debuffed at the end of the next round
        if s_k["rental"] and ante <= 6:
            sc_k -= 15
        return sc_k
    # rental sells are folded into the ADVICE as SELL FIRST; the ranking below is computed as if it were sold (Main
    # 06:xx: no ranking was printed while a rental sell was pending)
    sold = None
    # never sell what this shop just bought (7805: bought Half Joker on SIM +0.15, next call said SELL FIRST)
    fresh = set(d.get("_bought_ids") or [])
    for j in [x for x in sellable_j if x.get("id") not in fresh]:
        cls_r = classify_joker(j.get("name"), 0, mh)[0]
        if (_stk(j)["rental"] and ante <= 6 and keep_value(j) <= 45 and j.get("name") not in ENGINE_KEEP and j.get("name") not in GROWTH_X
                and not _is_scoring(cls_r) and not cls_r.startswith("XMULT") and _joker_edition(j) not in ("holo", "foil", "polychrome")):
            print(f"  SELL FIRST: b sell {j.get('index')}   ({j.get('name')} [{cls_r}] is a RENTAL and not a core scorer: it costs $3 every round (~${3 * rounds_left} if kept to the end); selling returns $1 and stops the charge)")
            sold = j
            break
    non_rental_scorers = [j for j in jokers if not _stk(j)["rental"] and alive_next(j) and _is_scoring(classify_joker(j.get("name"), 0, mh)[0])]
    if sold is None and len(non_rental_scorers) >= 2 and ante <= 6:
        flat_r = [j for j in rentals if j.get("id") not in fresh and not _stk(j)["eternal"] and not classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") and j.get("name") not in TYPE_X_JOKERS
                  and j.get("name") not in GROWTH_X
                  and joker_share(d, j, mh) < 0.3 and j.get("name") != "Mr. Bones"]  # 7805: The Trio was called a "flat rental"
        if flat_r:
            sold = min(flat_r, key=keep_value)
            print(f"  SELL FIRST: b sell {sold.get('index')}   ({sold.get('name')}{stickers(sold)} is a flat RENTAL and {len(non_rental_scorers)} non-rental scorers carry your hands: "
                  f"its rent (-$3/round, ~${3 * rounds_left} to the end) buys more as an xMult later; 41 Gold rentals cost $393)")
    if sold is None and len(rentals) >= 2 and ante <= 6:
        # never the rental that carries the score (7801: Clever +80 chips on every Two Pair; 7807: Acrobat, the only xMult)
        # or the run-saver: sell the one whose rent buys the least
        sell_r = sorted([j for j in rentals if j.get("id") not in fresh and not _stk(j)["eternal"] and j.get("name") != "Mr. Bones" and joker_share(d, j, mh) < 0.25
                         and not (_rg_x(classify_joker(j.get("name"), 0, mh)[0]) and n_rg <= 1)], key=keep_value)
        if sell_r and keep_value(sell_r[0]) < 85 and not (scoring_now <= 1 and alive_next(sell_r[0]) and _is_scoring(classify_joker(sell_r[0].get("name"), 0, mh)[0])):
            sold = sell_r[0]
            print(f"  SELL FIRST: b sell {sold.get('index')}   ({len(rentals)} rentals cost ${3 * len(rentals)} every round, more than the blinds pay; {sold.get('name')}{stickers(sold)} is the weakest; selling returns $1 and stops its charge)")
    if sold is not None:
        jokers = [x for x in jokers if x is not sold]
        sellable_j = [x for x in sellable_j if x is not sold]
        rentals = [x for x in rentals if x is not sold]
        rent_due = 3 * len(rentals)
        money += int(sold.get("sell_cost") or 0)
        free += 1
        d = dict(d, jokers=jokers, money=money)
    options = []
    boss_c = ((d.get("blind_select") or {}).get("choices") or {}).get("Boss") or {}
    boss_ahead = boss_c.get("name") if boss_c.get("state") != "Defeated" else None
    BOSS_KILLS = {"The Plant": {"Smiley Face", "Scary Face", "Photograph", "Sock and Buskin", "Business Card", "Midas Touch", "Reserved Parking", "Triboulet"},
                  "The Head": {"Lusty Joker", "Bloodstone"}, "The Goad": {"Wrathful Joker", "Arrowhead"},
                  "The Club": {"Gluttonous Joker", "Onyx Agate"}, "The Window": {"Greedy Joker", "Rough Gem"},
                  "The Needle": {"Card Sharp"}, "The Eye": {"Card Sharp"}, "The Water": {"Banner"}}  # blind.lua: Eye no repeated type, Water 0 discards (Summit always on), Needle 1 hand
    crippled = [j.get("name") for j in jokers if j.get("name") in BOSS_KILLS.get(boss_ahead or "", set())]
    # BOSS PREP: the boss is known from the ante start. When it counters this build, buy a counter or keep money for one
    # (7802 reached ante 7 and died to The Eye with a Card Sharp repeat engine).
    owned_n = {j.get("name") for j in jokers if not j.get("debuff")}
    boss_chips = int(boss_c.get("chips") or 0) if boss_ahead else 0
    hands_r = int(d.get("hands_per_round") or 3)
    face_names = {"Smiley Face", "Scary Face", "Photograph", "Sock and Buskin", "Triboulet", "Business Card", "Pareidolia", "Midas Mask"}
    threat = None
    # blind.lua: The Eye refuses any hand type already played this round, so Card Sharp (x3 on a type already played this
    # round) never fires. The Mouth only locks the first type: repeating it is exactly what Card Sharp wants.
    sharp_engine = "Card Sharp" in owned_n and (joker_share(d, next(j for j in jokers if j.get("name") == "Card Sharp"), mh) >= 0.2 or
                                                 any(n in owned_n for n in ("Blueprint", "Brainstorm")))
    if boss_ahead in ("The Eye", "The Needle") and sharp_engine:
        threat = ("it refuses a repeated hand type in the round" if boss_ahead == "The Eye" else "it gives one hand, so no type repeats") + ": Card Sharp (and any copy of it) never fires"
    elif boss_ahead == "The Plant" and sum(joker_share(d, j, mh) for j in jokers if j.get("name") in face_names) >= 0.3:
        threat = "it debuffs every face card your face jokers need"
    elif boss_ahead == "The Psychic" and "Half Joker" in owned_n:
        threat = "it forces 5-card plays, so Half Joker never fires"
    elif boss_ahead in ("The Club", "The Goad", "The Head", "The Window") and mh == "Flush":
        threat = "it debuffs a suit and you build Flushes"
    elif boss_ahead in ("The Wall", "Violet Vessel", "The Needle", "The Flint", "The Arm") and boss_chips and \
            (surv if boss_ahead == "The Needle" else surv * hands_r) < boss_chips:
        threat = f"your best hand (~{surv}) x {1 if boss_ahead == 'The Needle' else hands_r} hand(s) is below its {boss_chips}"
    boss_counter = {"Luchador", "Chicot", "Mr. Bones"} if threat else set()
    if threat:
        dc_owned = "v_directors_cut" in lst(d.get("used_vouchers")) or "v_retcon" in lst(d.get("used_vouchers"))
        offered = [c.get("name") for c in lst(sh.get("jokers")) if c.get("name") in boss_counter] + [c.get("name") for c in lst(sh.get("vouchers")) if c.get("name") in ("Director's Cut", "Retcon")]
        print(f"  BOSS PREP: {boss_ahead} counters this build ({threat}). " +
              (f"Counter in this shop: {', '.join(offered)} (ranked first below). " if offered else "") +
              ("You own Director's Cut: keep $10 for `b rerollboss` at blind select." if dc_owned else
               "Counters to buy on sight: Luchador (sell it during the boss), Chicot, Mr. Bones, or the Director's Cut voucher ($10 boss reroll)."))
        if dc_owned:
            floor = max(floor, 10)
    FLOOR_CLS = ("PLUS", "PLUS(fires on any pair-family hand)", "PLUS(permanent growth)", "PLUS(common condition)", "PLUS(main hand)")
    has_floor = any(classify_joker(j.get("name"), 0, mh)[0] in FLOOR_CLS or _joker_edition(j) in ("holo", "foil") or joker_share(d, j, mh) >= 0.2 for j in jokers)
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
            if name == "Swashbuckler" and len(jokers) >= 2:
                cls, score = "PLUS(+mult = sell value of your other jokers)", 45
            if name == "Bull" and money - cost < 10:
                cls, score = "PLUS(weak/conditional)", 25  # +2 chips per $: worthless for a wallet that is about to be empty
            if name == "Burnt Joker" and ante <= 2 and scoring_now < 2:
                score = 40  # levels come second: with fewer than two scorers the $8 is the next floor joker
            if name in ("Blueprint", "Brainstorm"):
                cls, score = "COPY(copies the joker to its right / your leftmost joker: `order` it beside your best xMult or flat joker)", (80 if n_x_now >= 1 or scoring_now >= 2 else 30)
            base_sc = score
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
            if cls.startswith("XMULT(conditional") and "other hand" not in cls and "suit" not in cls and \
                    ((ante >= 4 and n_x_now < 2) or (ante >= 3 and n_rg == 0)):
                score = 85 if n_x_now == 0 else 78  # any xMult shows in 14-15% of ante 2-4 views, a reliable one in 2-8%
            if cls.startswith("XMULT(conditional") and ante <= 2 and scoring_now < 2:
                score = 25  # Loyalty Card/Acrobat/Flower Pot-style conditionals do not clear ante 1-2 blinds; a floor joker does
                print(f"  {name}: a conditional xMult beats none at ante {ante}; runs that reroll for a clean xMult usually never see one (1 in ~45 shops).")
            if name in ("Gros Michel", "Popcorn", "Ice Cream"):
                # value the decaying jokers by their marginal est on your main hand, not by class (Gros Michel was the only
                # mult source in 4 reported runs); Gros Michel's 1-in-6 destruction per round is a discount, not AVOID
                base_e = typical_est(d, mh) or 1
                gain = typical_est(d, mh, lst(d.get("jokers")) + [c]) / base_e - 1
                if gain >= 0.25:
                    cls = f"PLUS(bridge: +{int(100 * gain)}% on your {mh if mh != 'undecided' else 'Pair'} now; {'1-in-6 destroyed each round' if name == 'Gros Michel' else 'decays'})"
                    score = int(min(88, 45 + 30 * gain) * (5 / 6 if name == "Gros Michel" else 1))
            if name in ("Vampire", "Lucky Cat", "Glass Joker", "Steel Joker"):
                need_e = {"Vampire": None, "Lucky Cat": "Lucky", "Glass Joker": "Glass", "Steel Joker": "Steel"}[name]
                deck_c = lst((d.get("deck") or {}).get("cards"))
                fed = sum(1 for k in deck_c if (k.get("enhancement") and (need_e is None or need_e.lower() in str(k.get("enhancement")).lower())))
                if fed == 0:
                    score = min(score, 45)  # a growth xMult with nothing to feed it stays x1 (7801: Vampire ranked top with 0 enhanced cards)
                    print(f"  {name}: no {need_e or 'enhanced'} cards in your deck yet, so it starts and stays x1 until you add some")
            if name == "Mr. Bones" and (emergency or (ante >= 3 and scoring_now < 2)):
                score = max(score, 72)  # under-scaled: surviving one blind at 25% buys a shop to fix the build
            if name == "Throwback":
                skips_r = int((d.get("run") or {}).get("skips") or 0)
                x_tb = 1 + 0.25 * skips_r
                cls, score = (f"XMULT(growth: Throwback x{x_tb:g} now, +0.25 per blind skipped)", min(90, 35 + 20 * skips_r)) if skips_r >= 1 else (cls, score)
            elif cls.startswith("PLUS") and not cls.startswith("PLUS(bridge"):
                # every flat joker is valued by what it adds NOW on deals from your deck (7803: Erosion 85 "NEEDED NOW" at
                # +0 with a full deck; 7801 Bootstraps at $0-6; Ride the Bus 95 at ante 1; Supernova 98 at ante 1)
                if marginal_gain(d, mh, c) < 0.03:
                    cls, score = "PLUS(adds ~0 now: grows only with its condition)", min(score, 25)
            if c.get("edition") in ("foil", "holo", "polychrome") and scoring_now < 2 and not cls.startswith("AVOID"):
                score = max(score, 72)  # the edition scores on every hand even when the joker itself does not
            if name == "Riff-raff" and slots - len(jokers) - 1 >= 2 and ante <= 4:
                cls, score = "COPY(2 free Common jokers every blind while slots are free)", max(score, 70)  # 7806: free Riff-raff -15, it cleared the Wall
            if name == "Joker Stencil":
                # x1 per empty joker slot, counting itself: after buying it you hold len+1 of `slots`
                x_st = slots - len(jokers) + (1 if _joker_edition(c) == "negative" else 0)
                cls, score = (f"XMULT(Stencil: x{x_st} now, -1 for every joker you add later)", min(100, 40 + 12 * x_st)) if x_st >= 2 else ("AVOID(x1: no empty slots)", 5)
            if name == "Luchador" and (crippled or threat or boss_ahead in ("The Wall", "The Needle", "The Flint", "The Arm", "The Eye", "The Mouth", "The Psychic")):
                cls, score = "COUNTER", 92
                print(f"  Luchador in shop: buy and SELL it while the boss {boss_ahead} is active to disable the boss (`sell N` during the blind).")
            elif name in boss_counter:
                cls, score = "COUNTER", max(score, 90)  # BOSS PREP: Chicot disables every boss, Mr. Bones survives a 25% loss
            if name == "Driver's License":
                enh_n = sum(1 for k in lst((d.get("deck") or {}).get("cards")) if k.get("enhancement"))
                if enh_n < 12:
                    score = min(score, 30)  # x3 needs 16 enhanced cards; with few the joker is x1 for many antes
            if name == "Hologram":
                # x1 + 0.25 per card ADDED to the deck: worthless without a feed (Standard packs, DNA, Certificate, Marble);
                # 7802 sold Half Joker / Supernova at ante 7 for an unfed Hologram and lost the Big by 6k
                feed = any("Standard" in str(b_.get("name")) for b_ in lst(sh.get("boosters"))) or any(j.get("name") in ("DNA", "Certificate", "Marble Joker") for j in jokers)
                if not feed and ante >= 4:
                    cls, score = "XMULT(growth, UNFED: x1 until cards are added; no Standard pack/DNA/Certificate/Marble in sight)", min(score, 25)
            core_gain = False
            if name not in boss_counter and not cls.startswith(("AVOID", "COUNTER")):
                # value every joker by what it adds to your typical main hand NOW (7802: Gros Michel -46 and Seeing Double
                # -45 while each added ~68%): a big real gain makes it a core joker for the sticker math too
                # round total = ordinary hands + the best hand (Acrobat/Summit/Dusk fire there), with vs without the joker
                gain_c = marginal_gain(d, mh, c)
                if gain_c >= 0.2:
                    score = max(score, int(55 + min(40, 50 * gain_c)))
                    core_gain = gain_c >= 0.3
                elif gain_c <= -0.05:
                    # it LOWERS your rounds (fills a Joker Stencil slot: x1 less, x2 with a Brainstorm/Blueprint copy; 7805)
                    cls, score = f"AVOID(-{-gain_c:.0%} round est: it fills a slot your Stencil counts)" if any(j.get("name") == "Joker Stencil" for j in jokers) else f"AVOID(-{-gain_c:.0%} round est now)", min(score, 5)
                if name in CARD_TRIGGER_JOKERS and cls.startswith("XMULT") and gain_c < 0.3:
                    # card-phase xMult multiplies only the base mult (7807: Photograph{ETERNAL} 130 at ante 5 was ~+18%)
                    score = min(score, int(40 + 100 * gain_c))
                if cls.startswith("XMULT") and not any(w in cls for w in ("growth", "decaying", "Stencil")) and gain_c < 0.05 and (d.get("deck") or {}).get("cards"):
                    # an xMult that multiplies nothing on rounds from your deck is x1 now (Baseball Card with 0 Uncommons, a
                    # type xMult your deck rarely makes)
                    cls, score = f"{cls[:-1] if cls.endswith(')') else cls}, ~x1 on your deck now)" if cls.endswith(")") else f"XMULT(~x1 on your deck now)", min(score, 30)
            ed = c.get("edition")
            if ed in ("holo", "polychrome"):
                score += 30
            elif ed:
                score += 10
            dl_c = JOKER_DESC.get(name, "").lower()
            if cls.startswith("PLUS") and not owns_mult:
                if "chips" in dl_c and "mult" not in dl_c:
                    score -= 15  # chips on a base mult of 2-3 barely scale: the first scorers must add MULT
                elif "mult" in dl_c:
                    score += 8
            score, st_notes, may_replace = sticker_adjust(c, cls, base_sc, score, ante, rounds_left, len(rentals), (ante <= 3 and scoring_now < 2) or bool(emergency), core_hint=core_gain)
            if any("ETERNAL on a" in s_n for s_n in st_notes) and len(jokers) >= 3:
                score = min(score, 15)  # 3+ jokers owned: a weak Eternal takes one of the last slots meant for an xMult, forever
            FLOOR_OK = ("PLUS", "PLUS(main hand)", "PLUS(common condition)", "PLUS(fires on any pair-family hand)", "PLUS(one suit)", "XMULT")
            if ante <= 2 and scoring_now == 0 and cls in FLOOR_OK and ("mult" in dl_c or cls == "XMULT") and not _stk(c)["rental"] \
                    and not any("ETERNAL on a" in s_n for s_n in st_notes):
                score = max(score, 85)  # no scorer at all: a +mult joker that fires on most hands beats a Gold pack gamble (78)
            needed = next((n for n in st_notes if n.startswith("NEEDED NOW")), "")
            options.append((score, cls, f"buy {c['index']}", (needed + " -> " if needed else "") + f"{name}{stickers(c)} ${cost} [{cls}]{' ' + ed if ed else ''}: {JOKER_DESC.get(name, 'unknown effect')}" + (f" | {'; '.join(n for n in st_notes if n != needed)}" if st_notes else ""), cost,
                            may_replace and ((cls.startswith("XMULT") and not cls.startswith("XMULT(conditional")) or cls == "COUNTER" or core_gain or (_fits_x(cls) and cls.startswith("XMULT(conditional") and n_x_now < 2 and ante >= 4) or (name in ("Blueprint", "Brainstorm") and n_x_now >= 1)),
                            _joker_edition(c) != "negative"))  # a Negative joker brings its own slot
        elif typ == "Planet":
            good = name == PLANET_FOR.get(mh)
            sh2 = second_hand(d)
            if not good and sh2 and name == PLANET_FOR.get(sh2):
                options.append((66, "PLANET", f"buy {c['index']}", f"{name} ${cost} [planet for your second-most-played hand {sh2}: boss insurance]", cost, True, False))
                continue
            feeds = any(j.get("name") in ("Constellation", "Satellite", "Astronomer") for j in jokers)
            const = any(j.get("name") == "Constellation" and not j.get("debuff") for j in jokers)
            psc = (60 if mh in ("Flush", "Straight") else 88) if good else 15  # Flush/Straight mains do not reach ante 4 at Gold
            if good and main_lvl >= 6 and n_x_now < 2:
                psc = 52  # diminishing: L6+ adds ~12% per level while an xMult or Glass card adds 50-100%
            psc += 25 if feeds else 0
            if const and ante >= 4 and n_x_now <= 1:
                psc = max(psc, 82)  # Constellation: every planet used is +0.1x on every hand forever; $3 beats a $5+ reroll
            if ante <= 2 and scoring_now <= 1 and not const:
                psc = min(psc, 20)  # 0-1 scoring jokers at ante 1-2: a level on a jokerless hand is +10-20 points; buy a scorer
            # planets are used on purchase: `buyuse` needs no consumable slot and feeds Constellation immediately
            options.append((psc, "PLANET", f"{'buyuse' if feeds else 'buy'} {c['index']}", f"{name} ${cost} [{'MAIN SCALING: main-hand planet' if good else 'planet for other hand'}{' (already L' + str(main_lvl) + ': multiplication now beats another level)' if good and main_lvl >= 6 else ''}{'; feeds Constellation (+0.1x)' if const else ('; feeds ' + 'Satellite/Astronomer' if feeds else '')}]", cost, good or feeds, False))
        elif name == "Judgement":
            jsc = (75 if scoring_now < 2 else 62) if free > 0 else 5
            if any(j.get("name") == "Joker Stencil" for j in jokers):
                jsc = min(jsc, 15)  # the new joker fills a slot your Stencil counts (x1 less; Main 08:xx)
            options.append((jsc, "TAROT", f"buyuse {c['index']}", f"{name} ${cost} [creates a random joker now (`buyuse` it; needs a free joker slot{'' if free > 0 else ': slots FULL, worthless now'}); at Gold it can carry stickers]", cost, False, False))
        elif name == "The Hermit":
            options.append((45 if money - cost >= 10 else 5, "TAROT", f"buy {c['index']}", f"{name} ${cost} [doubles money up to +$20: only worth it with $10+ left after buying]", cost, False, False))
        elif name == "Temperance":
            gain_t = min(50, sum(int(j.get("sell_cost") or 0) for j in jokers)) - cost
            options.append((60 if gain_t >= 4 else 10, "TAROT", f"buyuse {c['index']}", f"{name} ${cost} [money: +${min(50, sum(int(j.get('sell_cost') or 0) for j in jokers))} (your jokers' sell values), net +${gain_t}]", cost, gain_t >= 4, False))
        elif name in ("Death", "Strength", "Justice") and ante >= 3:
            held_rescue = any(k.get("name") in ("Death", "Strength", "Justice") for k in lst(d.get("consumables")))
            # Glass x2 resolves in the card phase, before the joker row: on a flat +mult build it barely moves the score
            # (PLAYBOOK card-phase rule; Fable 7801: Justice 86 'rescue' on a +46 flat build)
            flat_build = name == "Justice" and n_x_now == 0 and sum(joker_share(d, j, mh) for j in jokers) >= 0.5
            options.append((30 if (held_rescue or flat_build) else 86, "TAROT", f"buy {c['index']}", f"{name} ${cost} [RESCUE tarot: hold it for a forced final hand; pack tarots must be used on the spot, only shop-bought ones can be banked"
                            + ("; Glass multiplies only the base mult on your flat +mult build" if flat_build else "") + "]", cost, not (held_rescue or flat_build), False))
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
            note = ("Telescope: your main planet is guaranteed" if telescope else
                    "no main hand yet: take the planet of the hand you play most (`advise` inside the pack picks it)" if mh == "undecided" else
                    f"take {PLANET_FOR.get(mh)}; if it is not offered, a fallback planet is worth little (skip the pack if you can buy your planet directly next shop)")
            if ante <= 2 and scoring_now <= 1 and not feeds:
                csc = min(csc, 15 - big)  # 0-1 scoring jokers at ante 1-2: levels on a jokerless hand barely move it (Main 08:xx)
            options.append((csc + big + (15 if feeds else 0), "PACK", f"pack {c['index']}", f"{name} ${cost} [hand level gamble: {note}{'; feeds Constellation' if feeds else ''}]", cost, ante >= 2 and (telescope or mh == "undecided") and not (ante <= 2 and scoring_now <= 1), False))
        elif "Buffoon" in name:
            n_x = sum(1 for j in jokers if (classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") or _joker_edition(j) == "polychrome"))
            bscore = 55 if free > 0 else 0
            if free > 0 and ante >= 3 and n_x == 0:
                bscore = 72
            if free > 0 and scoring_now == 0:
                bscore = 88  # no scorer at all: a joker choice beats every pack and beats leaving with cash
            st_pack = ""
            flat_slot = free > 0 or any(not _stk(j)["eternal"] and not _rg_x(classify_joker(j.get("name"), 0, mh)[0]) for j in jokers)
            buff_hunt = 2 <= ante <= 5 and n_rg < 2 and flat_slot  # a bought Buffoon shows a reliable/growth xMult 18% of the time (~$24 per sighting)
            if buff_hunt:
                bscore = max(bscore, 80)
            elif stake >= 4:
                bscore -= 10 if stake >= 8 else 5  # ~70% of pack jokers carry an Eternal/Perishable/Rental sticker at Gold; all-junk packs happen
                st_pack = "; at this stake pack jokers can be Eternal/Perishable/Rental: run `advise` inside the pack, it ranks them with stickers and says when to skip"
            options.append((bscore, "PACK", f"pack {c['index']}", f"{name} ${cost} [joker choice; prefer xMult, then +mult for {mh}{st_pack}]", cost, ante >= 3 and n_x == 0, True))
        elif "Arcana" in name:
            feeds = any(j.get("name") == "Vampire" for j in jokers)
            glass_plan = any(j.get("name") in ("Vampire", "Glass Joker") for j in jokers)
            arc = (70 if glass_plan else 45) if ante >= 3 else 15  # packs were 37% of all spending; Justice is in 29% of Arcana packs
            if ante >= 3 and mh != "undecided" and main_lvl < min(ante, 5):
                arc = min(arc, 45)  # level the main hand first
            options.append((arc + (25 if feeds else 0), "PACK", f"pack {c['index']}", f"{name} ${cost} [tarots: Justice=Glass x2 / Chariot=Steel x1.5 on your main-hand ranks (`pick N i` with the target card), Empress=+4 mult cards, Hermit=$; {'; enhancement tarots feed Vampire' if feeds else ''}]", cost, False, False))
        elif "Standard" in name:
            feeds = any(j.get("name") == "Hologram" for j in jokers)
            options.append((60 if feeds else 10, "PACK", f"pack {c['index']}", f"{name} ${cost} [playing cards{'; each card added feeds Hologram +0.25' if feeds else ''}]", cost, feeds, False))
        elif "Spectral" in name:
            options.append((45 if ante >= 3 else 20, "PACK", f"pack {c['index']}", f"{name} ${cost} [spectral: Aura = Foil/Holo/Polychrome on a target card (`pick N i` with a main-rank card), Cryptid = 2 copies of a target card (copy a Glass/Steel one), Talisman = Gold seal, Ectoplasm = Negative joker, Wraith = a random RARE joker (rares are often xMult; it sets money to $0 so take it when poor and a slot is free), Immolate = destroy 5 random hand cards for $20 (fine when broke); `advise` inside the pack picks]", cost, False, False))
        else:
            holo_feed = "Standard" in name and any(j.get("name") == "Hologram" and not j.get("debuff") for j in jokers)
            options.append((60 if holo_feed else 10, "PACK", f"pack {c['index']}", f"{name} ${cost}" + (" [feeds Hologram: +x0.25 per card added]" if holo_feed else ""), cost, holo_feed, False))
    for c in lst(sh.get("vouchers")):
        name, cost = c.get("name") or "", int(c.get("cost") or 0)
        sc = 45 if name in ("Overstock", "Clearance Sale", "Hone", "Telescope", "Grabber", "Wasteful", "Seed Money", "Money Tree") else 20
        if (ante >= 5 and money - cost < 15) or (ante >= 3 and money - cost < 8):
            sc = 15  # a voucher that empties the wallet costs the next joker/planet; late ones cannot pay back before the run ends
        strong_v = False
        if threat and name in ("Director's Cut", "Retcon"):
            sc, strong_v = 88, True  # BOSS PREP: rerolls the boss that counters this build
        options.append((sc, "VOUCHER", f"vouch {c['index']}", f"{name} ${cost} [voucher{': reroll the boss (BOSS PREP)' if strong_v else ''}]", cost, strong_v, False))
    # Coupon Tag / free items: a $0 pack or joker is never worse than leaving (except a sticker that costs a slot or rent forever)
    options = [(((max(o[0], 89),) + tuple(o[1:5]) + (True,) + tuple(o[6:])) if o[4] == 0 and not o[1].startswith("AVOID") and "ETERNAL on a" not in o[3] and "RENTAL:" not in o[3] else o) for o in options]
    refused = "drains the run to $0"
    buff_any_hunt = n_rg < 2  # a Buffoon pack may go below the money floor while owning <2 reliable/growth xMults
    if ante <= 2 and scoring_now < 2:
        # with 0-1 scorers at ante 1-2 any joker that adds to hands outranks every utility/money/level joker
        options = [((max(o[0], 65) if (o[2].startswith("buy") and _scores_now(o[1]) and "ETERNAL on a" not in o[3] and refused not in o[3])
                     else (min(o[0], 60) if o[2].startswith("buy") and o[1].startswith(("LEVELS", "ECON", "UTIL", "COPY", "UNKNOWN")) else o[0])),) + tuple(o[1:])
                   for o in options]
    if emergency:
        # cheapest multiplier first: reliable/growth xMult > conditional xMult > Buffoon pack > main-hand planet
        def _emerg(o):
            bump = 30 if (_rg_x(o[1]) and refused not in o[3]) else (20 if o[1].startswith("XMULT(conditional") and "other hand" not in o[1] and "suit" not in o[1]
                                                                    else (15 if "Buffoon" in o[3] else (10 if "MAIN SCALING" in o[3] else 0)))
            return (o[0] + bump,) + tuple(o[1:5]) + ((o[5] or bump > 0),) + tuple(o[6:])
        options = [_emerg(o) for o in options]
    if scoring_now == 0 and ante >= 3:
        # no scorer alive next ante: a scoring joker is the only thing that clears a blind; levels/packs/money come after
        options = [((max(o[0], 90) if _is_scoring(o[1]) and o[2].startswith("buy") and refused not in o[3] else (o[0] if "Buffoon" in o[3] else min(o[0], 45))),) + tuple(o[1:]) for o in options]
        print(f"  (no scorer alive next ante at ante {ante}: scoring jokers first, non-scorers capped at 45)")
    if scoring_now < 2:
        # few scorers alive next ante: a scorer may replace your weakest joker (e.g. one that is about to perish)
        options = [o[:5] + ((o[5] or (_is_scoring(o[1]) and o[2].startswith("buy") and refused not in o[3] and "ETERNAL on a" not in o[3])), o[6]) for o in options]
    need_joker = (len(jokers) < 2 and ante <= 3) or scoring_now == 0
    if need_joker:
        options = [(sc + (30 if (cls.startswith("PLUS") or cls == "XMULT") and refused not in label and "ETERNAL on a RENTAL" not in label else 0), cls, cmd, label, cost, strong, ns)
                   for sc, cls, cmd, label, cost, strong, ns in options]
        print("  (fewer than 2 jokers or no scorer alive next ante: scoring jokers weighted up)")
    if ante >= 6 and money >= 40:
        options = [(sc + (25 if cls.startswith("PLUS") else 0), cls, cmd, label, cost, True if cls.startswith("PLUS") else strong, ns)
                   for sc, cls, cmd, label, cost, strong, ns in options]
        print("  (ante 6+ with $40+: money is worth nothing unspent; flat +chips/+mult jokers weighted up, sell utility jokers to fit them)")
    # the printed ranking is the final one: the ADVICE below walks this exact list top-down (skips are printed)
    options.sort(key=lambda t: -t[0])
    for o in options:
        print(f"  {o[0]:>3} {o[2]:<9} {o[3]}")
    try:
        with open(os.path.join(RUNS_DIR, "shop_log.tsv"), "a", encoding="utf-8") as f:
            f.write(f"{os.environ.get('BALATRO_RL_PORT', '7777')}\ta{ante}\t${money}\tjokers={len(jokers)}/{slots}\txmult_owned={sum(1 for j in jokers if classify_joker(j.get('name'), 0, mh)[0] == 'XMULT')}\t" + " | ".join(f"{o[1]}:{o[3].split(' [')[0]}" for o in options) + "\n")
    except Exception:
        pass
    cons = lst(d.get("consumables"))
    cons_full = len(cons) >= int(d.get("consumable_slots") or 2)
    replaceable = free + sum(1 for j in sellable_j if not alive_next(j))  # open slots plus jokers that perish before next ante
    save_for_joker = (ante <= 2 and scoring_now < 2 or scoring_now == 0) and replaceable > 0
    if save_for_joker:
        print(f"  (ante {ante} with {scoring_now} scoring joker(s) alive next ante: keep at least $4 after any pack/planet/voucher so the next shop's $4-5 joker is affordable; a hand with no joker support cannot clear the next blinds)")
    # any affordable joker the ranking puts at 60+ counts as an offer: never reroll past it (7807: Ice Cream 88, ADVICE reroll)
    joker_offers = [o for o in options if o[2].startswith("buy") and (_is_scoring(o[1]) or _scores_now(o[1]) or (o[1].startswith("LEVELS") and scoring_now >= 1)
                                                                    or (o[0] >= 60 and not o[1].startswith("AVOID") and o[1] not in ("PLANET", "TAROT", "SPECTRAL"))) and o[4] <= money]
    reroll0 = int(sh.get("reroll_cost") or 5)
    cannot_reroll = money - reroll0 < 4
    if save_for_joker:
        main_planet_ok = ante >= 3 and any(o[1] == "PLANET" and "MAIN SCALING" in o[3] and o[4] <= money for o in options)
        if not joker_offers and not main_planet_ok and not any("Buffoon" in o[3] and o[4] <= money for o in options):
            passed = [o[3].split(" [")[0].split(" -> ")[-1] + ("" if o[4] <= money else f" (${o[4]}, unaffordable)") for o in options if o[0] >= 30 and not o[1].startswith("AVOID")]
            if passed and money - reroll0 - rent_due >= 3:
                print(f"  Ranked higher but passed over: {', '.join(passed)}: no scoring joker on offer, so the money goes to a reroll for one")
            if money - reroll0 - rent_due >= 4:
                print(f"ADVICE: REROLL -> b reroll   (no scoring joker in this shop and you own {scoring_now}: at ante {ante} a joker matters more than any pack; ${money - reroll0} left after)")
                return
            if scoring_now == 0 and money - reroll0 - rent_due >= 3:
                print(f"ADVICE: REROLL -> b reroll   (you own NO scoring joker and none is offered: a jokerless deck does not clear the next blind at this stake; ${money - reroll0} stays for a $3 Sly/Jolly if the reroll shows one)")
                return
            if scoring_now == 0 and money >= reroll0:
                print(f"  (no scorer offered and a reroll would leave under $3: rerolling to $0 has revealed $3 jokers it could no longer buy - keep the ${money} for the next shop)")
    skipped = []  # every option ranked above the ADVICE is listed with its reason: the ADVICE never silently contradicts the ranking

    def skip(lbl, why):
        skipped.append(f"{lbl.split(' [')[0].split(' -> ')[-1]}: {why}")

    def say_skipped():
        if skipped:
            print("  Ranked higher but passed over: " + "; ".join(skipped))
    # Credit Card: the game lets you spend down to -$20; only buys exempt from the money floor (strong/needed) use it
    credit = 20 if any(j.get("name") == "Credit Card" and not j.get("debuff") for j in jokers) else 0
    for score, cls, cmd, label, cost, strong, needs_slot in options:
        if score < 30:
            break
        if cost > money + credit and cmd.startswith("buy") and ((_fits_x(cls) and score >= 60 and ante >= 3) or (_is_scoring(cls) and scoring_now == 0 and jokers)):
            # an xMult (or, with no scorer at all, the first scoring joker) we cannot afford: sell the weakest non-xMult joker if that pays for it, otherwise keep the money
            sellable = [(int(j.get("sell_cost") or 0), j) for j in sellable_j if not classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") and not _is_scoring(classify_joker(j.get("name"), 0, mh)[0]) and j.get("name") not in ENGINE_KEEP and joker_share(d, j, mh) < 0.15]
            sellable.sort(key=lambda t: (owned_value(d, t[1], mh), -t[0]))
            if sellable and money + sellable[0][0] >= cost:
                say_skipped()
                print(f"ADVICE: SELL then BUY -> b sell {sellable[0][1].get('index')}  then  b {cmd}   ({label}; selling {sellable[0][1].get('name')} for ${sellable[0][0]} makes it affordable)")
                return
            print(f"  {label.split(' [')[0]} is an xMult you cannot afford (${money}): do not spend on packs this shop unless they clear the next blind; it is gone next shop, so only hold cash if a reroll/next shop is likely to show another")
        if cls.startswith("AVOID"):
            continue
        if cost > 0 and cost > money + credit:  # a $0 item (Coupon/tag) is always affordable, even at negative money (7807)
            skip(label, f"costs ${cost}, you have ${money}" + (" (+$20 Credit Card debt)" if credit else ""))
            continue
        if not tight and mh != "undecided" and main_lvl < min(ante, 5) and cls in ("PACK", "VOUCHER", "TAROT") and "Celestial" not in label and "Buffoon" not in label and not strong and money - cost < 4:
            skip(label, "keeps $4 for the main-hand planet (main hand behind the level curve)")
            continue
        if boss_ahead == "The Tooth" and not strong and money - cost < 6 and not emergency and not tight and scoring_now >= 2:
            skip(label, "The Tooth is this ante's boss (-$1 per card played): keeping $6")
            continue
        if not tight and save_for_joker and cls in ("PACK", "PLANET", "TAROT", "VOUCHER") and "Buffoon" not in label and money - cost < 4:
            if not (cls == "PLANET" and not joker_offers and cannot_reroll and strong):  # else: a cheap main-hand level beats idle cash
                skip(label, "keeps $4 for a scoring joker next shop")
                continue
        joker_buy = cmd.startswith("buy") and (cls.startswith(("PLUS", "XMULT")) or _is_scoring(cls))
        # behind (SCORE CHECK ratio < 0.7: 55-67% of such runs died by the next ante): a scoring joker may break the floor
        min_left = 0 if (strong or ante <= 1 or (need_joker and joker_buy) or (joker_buy and sc_ratio < 0.7)) else floor
        if "Buffoon" in label and buff_any_hunt:
            min_left = 0
        if tight and cls == "PACK" and ("Spectral" in label or "Standard" in label) and not strong:
            min_left = max(min_left, 8)  # TIGHT lifts the floor only for score now; Spectral/Standard packs are not that (7803)
        if cost > 0 and money - cost < (min_left or -credit):
            skip(label, f"would leave ${money - cost}, below the ${min_left} money floor")
            continue
        if cls in ("PLANET", "TAROT") and cons_full and not cmd.startswith("buyuse"):
            usable = [c for c in cons if c.get("index") in usable_cons()]
            if usable:
                say_skipped()
                print(f"ADVICE: USE first -> b use {usable[0].get('index')}   (consumable slots full; use {usable[0].get('name')} then re-run shopadvise to buy {label.split(' [')[0]})")
            else:
                RESCUE = {"Justice", "The Chariot", "The Empress", "The Hierophant", "The Magician", "The Devil", "The Tower", "The Lovers", "Strength", "Death", "The Hanged Man", "The Hermit", "Temperance", PLANET_FOR.get(mh)}
                if all(c.get("name") in RESCUE for c in cons):
                    skip(label, f"consumable slots hold only rescue/main-hand items {[c.get('name') for c in cons]}")
                    continue
                junk = sorted(cons, key=lambda c: (c.get("name") in RESCUE, c.get("set") == "Planet"))
                say_skipped()
                print(f"ADVICE: SELL first -> b sellc {junk[0].get('index')}   (consumable slots full; {junk[0].get('name')} is your least useful consumable, sell it then buy {label.split(' [')[0]})")
            return
        if needs_slot and free <= 0:
            weakest = None
            for j in sellable_j:  # never an Eternal: the game refuses to sell it
                if j.get("name") in ENGINE_KEEP:
                    continue
                s2 = keep_value(j)
                if weakest is None or s2 < weakest[0]:
                    weakest = (s2, j)
            if strong and weakest and weakest[0] < min(score, 100) and cmd.startswith("buy"):
                say_skipped()
                print(f"ADVICE: SELL then BUY -> b sell {weakest[1].get('index')}  then  b {cmd}   ({weakest[1].get('name')}{stickers(weakest[1])} is your weakest sellable joker; {label})")
                return
            skip(label, "no free joker slot and every owned joker is worth more" if strong else "no free joker slot (not strong enough to replace a joker)")
            continue
        say_skipped()
        print(f"ADVICE: BUY -> b {cmd}   ({label})")
        return
    say_skipped()
    # INVARIANT: in an EMERGENCY, or with <2 scorers at ante <= 3, never LEAVE while an affordable scorer is on offer
    if emergency or (ante <= 3 and scoring_now < 2):
        sc_o = [o for o in options if o[2].startswith("buy") and o[4] <= money and refused not in o[3] and not o[1].startswith("AVOID")
                and (_is_scoring(o[1]) or o[1].startswith("PLUS(bridge") or o[1] == "PLUS(one suit)" or (emergency and "Mr. Bones" in o[3])) and "growth" not in o[1]
                and "ETERNAL on a" not in o[3] and ("RENTAL:" not in o[3] or "NEEDED NOW" in o[3])]
        if sc_o:
            o = max(sc_o, key=lambda t: t[0])
            if free > 0:
                print(f"ADVICE: BUY -> b {o[2]}   ({'EMERGENCY' if emergency else f'{scoring_now} scorer(s) at ante {ante}'}: a scorer now beats leaving with cash; {o[3]})")
                return
            weak_j = min((j for j in sellable_j if j.get("name") not in ENGINE_KEEP), key=lambda j: owned_value(d, j, mh), default=None)
            if weak_j is not None and owned_value(d, weak_j, mh) < o[0]:
                print(f"ADVICE: SELL then BUY -> b sell {weak_j.get('index')}  then  b {o[2]}   ({weak_j.get('name')}{stickers(weak_j)} is your weakest; {o[3]})")
                return
    reroll = int(sh.get("reroll_cost") or 5)
    # GOLD_ANALYSIS.md: 6% of rerolls show a reliable/growth xMult (~$91 per sighting; 2 of 41 at ante 3-5). Hunt only
    # with $20+ left after the reroll, at most 2 rerolls per shop (cost rises $1 each), never over an affordable Buffoon.
    rerolls_done = max(0, reroll - 5)
    buff_ok = any("Buffoon" in o[3] and o[4] <= money for o in options)
    want_xmult = n_rg < rg_target
    if want_xmult and money - reroll - rent_due >= 20 and rerolls_done < 2 and not buff_ok:
        print(f"ADVICE: REROLL -> b reroll   (you own {n_rg} reliable/growth xMult (target {rg_target}): hunt for one; ${money - reroll} left after; only if an xMult appears, sell your weakest flat joker for it)")
        return
    scoring = scoring_now
    if (ante <= 2 and scoring < 2 or scoring == 0) and replaceable > 0 and money - reroll - rent_due >= 3:
        boss_need = f"; the {boss_c.get('name')} needs {boss_c.get('chips')} in {d.get('hands_per_round') or 3} hands" if boss_ahead and boss_c.get("chips") else ""
        print(f"ADVICE: REROLL -> b reroll   (ante {ante} with only {scoring} scoring joker(s) alive next ante: a reroll leaving ${money - reroll} for a $3-4 joker beats leaving{boss_need})")
        return
    if free > 0 and ante >= 2 and money - reroll - rent_due >= 20 and rerolls_done < 2 and not buff_ok:
        print(f"ADVICE: REROLL -> b reroll   (nothing worth buying, {free} free joker slot(s), ${money - reroll} left after)")
        return
    # before leaving: a strong item just out of reach can be funded by selling a joker that is about to die anyway
    # (perishable with <= 1 round left) or a flat rental (it costs $3 every round)
    want_o = [o for o in options if o[4] > money and o[0] >= 70 and (o[2].startswith("buy") or "Buffoon" in o[3]) and refused not in o[3]]
    rgx_wanted = any(_rg_x(o[1]) for o in want_o)  # a lasting r/g xMult $1-3 short: a perishable at <= 2 rounds may fund it
    fund = sorted([j for j in sellable_j if (_stk(j)["perishable"] and (_stk(j)["perish_tally"] or 0) <= (2 if rgx_wanted else 1))
                   or (_stk(j)["rental"] and not _rg_x(classify_joker(j.get("name"), 0, mh)[0]) and joker_share(d, j, mh) < 0.3)],
                  key=lambda j: owned_value(d, j, mh))
    if want_o and fund:
        o = max(want_o, key=lambda t: t[0])
        if money + sum(int(j.get("sell_cost") or 0) for j in fund) >= o[4]:
            j = fund[0]
            print(f"ADVICE: SELL -> b sell {j.get('index')}   (fund {o[3].split(' [')[0]} (${o[4]}, score {o[0]}): {j.get('name')}{stickers(j)} "
                  f"{'dies within a round' if _stk(j)['perishable'] else 'is a flat rental costing $3 a round'}; sell it (${j.get('sell_cost')}), then re-run shopadvise)")
            return
    print("ADVICE: LEAVE -> b endshop   (nothing worth buying at this money level)")
    bs = d.get("blind_select") or {}
    boss = ((bs.get("choices") or {}).get("Boss") or {}).get("name")
    if boss:
        print(f"Upcoming boss this ante: {boss}")


def pack_advise(d):
    """`advise` inside an open pack: ranks Buffoon jokers with their stake stickers, picks the main-hand planet."""
    _SHARE_MEMO.clear()
    pk = d.get("pack") or {}
    cards = lst(pk.get("cards"))
    mh = main_hand(d)
    ante = int(d.get("ante") or 1)
    jokers = lst(d.get("jokers")); slots = int(d.get("joker_slots") or 5)
    if any(c.get("set") == "Joker" for c in cards):
        bl_left = _rounds_left(d) - 3 * max(0, 8 - ante)
        alive = [j for j in jokers if not _dead_perishable(j) and not (_stk(j)["perishable"] and (_stk(j)["perish_tally"] or 0) <= bl_left)]
        scoring_now = sum(1 for j in alive if is_scorer(d, j, mh))
        own_rentals = sum(1 for j in jokers if _stk(j)["rental"])
        free_p = slots - len(jokers)
        under = (ante <= 2 and scoring_now < 2) or scoring_now < 2
        bridge = under
        ranked = []
        for i, c in enumerate(cards, 1):
            if c.get("set") != "Joker":
                continue
            cls, sc = classify_joker(c.get("name"), 0, mh)
            if c.get("name") == "Swashbuckler" and len(jokers) >= 2:
                cls, sc = "PLUS(+mult = sell value of your other jokers)", 45  # 7803: "useless as the only joker" with 5 owned
            base = sc
            gain = marginal_gain(d, mh, c, jokers)
            if cls.startswith("AVOID") and free_p > 0 and gain >= 0.1 and "decay" in cls:
                # a decaying joker into a FREE slot costs nothing: take its points now, sell it when it fades (7803 SKIP
                # over Popcorn at a TIGHT boss)
                cls, sc = "PLUS(decaying: free points now, sell when it fades)", 40
            elif cls.startswith("AVOID"):
                gain = 0.0
            if bridge and _is_scoring_cls(cls) and (gain >= 0.05 or not (d.get("deck") or {}).get("cards")):
                sc = max(sc, 90)  # a bridge must score NOW (7809: Erosion 90 on a full 52-card deck added 0)
            BRIDGES = {"Gros Michel": 64, "Popcorn": 62, "Ice Cream": 58}
            if scoring_now < 2 and c.get("name") in BRIDGES:
                cls, sc = "PLUS(decaying bridge: scores now, fades over ~5 rounds; sell when a real scorer arrives)", BRIDGES[c.get("name")]
            elif free_p > 0 and not cls.startswith("AVOID"):
                # the pack is already paid for: a joker into a free slot costs nothing now and can be sold later
                sc = max(sc, 55 if (under and cls.startswith(("PLUS", "XMULT"))) else 30)
            ed = c.get("edition")
            sc += 30 if ed in ("holo", "polychrome") else (10 if ed else 0)
            # same marginal valuation as the shop: what it adds to a round of your main hand NOW (7805: Eternal Scary
            # Face +60 chips vs Eternal Hanging Chad ~+10 both scored 90 and the slot order picked Chad; boss lost 534/600)
            if gain >= 0.2:
                sc = max(sc, int(55 + min(40, 50 * gain)))
            sc, notes, _ = sticker_adjust(c, cls, base, sc, ante, _rounds_left(d), own_rentals, bridge, pack_free=free_p, core_hint=gain >= 0.3)
            money_p = int(d.get("money") or 0)
            if _stk(c)["rental"] and money_p - 3 < 4 and gain < 0.3:
                sc -= 20  # 7807: rental Scholar NEEDED NOW at $<=5: its rent leaves no $4-5 for the next shop's joker
                notes.append(f"RENT: -$3 at round end leaves ${money_p - 3}, under a $4-5 joker in the next shop")
            if any("ETERNAL on a" in s_n for s_n in notes) and free_p <= 1:
                sc = min(sc, 15)
            if gain <= -0.05:
                sc = min(sc, 5)  # it lowers your rounds (fills a slot your Joker Stencil counts; 7805)
                notes.append(f"{gain:.0%} round est: fills a slot your Stencil counts" if any(j.get("name") == "Joker Stencil" for j in jokers) else f"{gain:.0%} round est")
            notes = [f"+{gain:.0%} round est now"] + notes if gain >= 0.01 else notes
            ranked.append((sc, i, c, cls, notes, gain))
        if ante <= 2 and scoring_now < 2:
            # 7805 lost the ante-1 Big 444/450 after Astronomer (75) outranked Walkie Talkie (45) with 0 scorers
            measured = bool((d.get("deck") or {}).get("cards"))
            ranked = [((max(sc, 65) if _scores_now(cls) and (g >= 0.05 or not measured) else min(sc, 60)), i, c, cls, notes, g) for sc, i, c, cls, notes, g in ranked]
        ranked.sort(key=lambda t: (-t[0], -t[5]))  # equal scores: the bigger real gain first, never slot order
        print(f"Pack advisor: {pk.get('kind') or 'joker pack'}, choose {pk.get('choices_remaining')}, jokers {len(jokers)}/{slots}, {scoring_now} scorer(s) alive next ante")
        for sc, i, c, cls, notes, _g in ranked:
            print(f"  {sc:>3} pick {i:<3} {c.get('name')}{stickers(c)} [{cls}]: {JOKER_DESC.get(c.get('name'), 'unknown effect')}" + (f" | {'; '.join(notes)}" if notes else ""))
        if not ranked:
            return
        sc, i, c, cls, _n, _g = ranked[0]
        if sc < 30:
            print(f"ADVICE: SKIP -> b skippack   (every joker here is weak or its stickers cost more than it gives; best is {c.get('name')} at {sc})")
            return
        if len(jokers) >= slots and _joker_edition(c) != "negative":
            sellable = [j for j in jokers if not _stk(j)["eternal"]]
            weak = min(sellable, key=lambda j: owned_value(d, j, mh), default=None)
            wsc = None if weak is None else owned_value(d, weak, mh)
            if weak is not None and sc >= 60 and sc > wsc + 20:
                print(f"ADVICE: SELL then PICK -> b sell {weak.get('index')}  then  b pick {i}   (joker slots are full; {c.get('name')} ({sc}) beats {weak.get('name')}{stickers(weak)}; selling works while the pack is open)")
            else:
                print("ADVICE: SKIP -> b skippack   (joker slots are full and nothing here beats your weakest sellable joker by enough)")
            return
        print(f"ADVICE: PICK -> b pick {i}   ({c.get('name')}{stickers(c)} [{cls}]" + ("; then re-run advise for the next choice" if (pk.get("choices_remaining") or 1) > 1 else "") + ")")
        return
    planets = [(i, c) for i, c in enumerate(cards, 1) if c.get("set") == "Planet"]
    if planets:
        hl_p = d.get("hand_levels") or {}
        most = max(hl_p, key=lambda k: int((hl_p[k] or {}).get("played") or 0), default=None) if hl_p else None
        PAIR_FAM = ("Pair", "Two Pair", "Three of a Kind", "Full House", "Four of a Kind")
        # undecided main hand: one lucky Straight/Flush is not a plan, only pair-family levels count (7801: Jupiter at ante 1)
        want = [PLANET_FOR.get(mh)] + [PLANET_FOR.get(h or "") for h in (most, second_hand(d)) if mh != "undecided" or h in PAIR_FAM]
        gate_x = next((TYPE_X_JOKERS[j.get("name")][0] for j in jokers if j.get("name") in TYPE_X_JOKERS and not j.get("debuff")
                       and (mh in ("undecided", "Flush", "Straight") or hand_contains(mh, TYPE_X_JOKERS[j.get("name")][0]))), None)
        want = [PLANET_FOR.get(gate_x or "")] + want  # an owned type xMult (The Trio...) decides which level pays most
        for w in want:
            hit = next(((i, c) for i, c in planets if w and c.get("name") == w), None)
            if hit:
                why_p = (f"levels {gate_x}, the type your owned xMult joker needs" if gate_x and w == PLANET_FOR.get(gate_x)
                         else f"levels {'your main hand ' + mh if w == PLANET_FOR.get(mh) else 'your most played / second hand'}")
                print(f"ADVICE: PICK -> b pick {hit[0]}   ({w} {why_p})")
                return
        PF_ORDER = ["Uranus", "Venus", "Earth", "Mercury", "Mars"]  # pair-family planets: the hands Gold runs live on
        i, c = min(planets, key=lambda t: PF_ORDER.index(t[1].get("name")) if t[1].get("name") in PF_ORDER else 99)
        print(f"ADVICE: PICK -> b pick {i}   (your main-hand planet is not here; {c.get('name')} levels a pair-family hand, the best fallback)")
        return
    spectrals = [(i, c) for i, c in enumerate(cards, 1) if c.get("set") == "Spectral"]
    if spectrals:
        hand = [c for c in lst(d.get("hand")) if c.get("rank") is not None and not c.get("debuff")]
        n_j = len(jokers)
        by_rank = Counter(_r(c) for c in hand)
        # target: the best card of your most common rank (it scores in your main pair-family hand), Glass/Steel for Cryptid
        tgt = max(hand, key=lambda c: (by_rank[_r(c)], CHIP_VAL.get(_r(c), 0)), default=None)
        glass = next((c for c in hand if any(e in _enh(c) for e in ("Glass", "Steel"))), None)
        strong_j = [j for j in jokers if classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT") or joker_share(d, j, mh) >= 0.4]
        money = int(d.get("money") or 0)
        SPEC = {"The Soul": (100 if n_j < slots else 5, None, "a Legendary joker"),
                "Black Hole": (90, None, "+1 level to every hand"),
                "Wraith": ((75 if n_j < slots and money <= 10 else (40 if n_j < slots else 5)) if not any(j.get("name") == "Joker Stencil" for j in jokers) else 15, None,
                           "a random Rare joker, money set to $0" + ("; it fills a slot your Joker Stencil counts" if any(j.get("name") == "Joker Stencil" for j in jokers) else "")),
                "Aura": (70, tgt, "Foil/Holo/Polychrome on the target card"),
                "Cryptid": (65 if glass else 45, glass or tgt, "2 copies of the target card"),
                "Deja Vu": (55, tgt, "Red Seal (retrigger) on the target card"),
                "Talisman": (45, tgt, "Gold Seal ($3 when played) on the target card"),
                "Hex": (55 if len(strong_j) == 1 and n_j <= 2 else 5, None, "Polychrome on a random joker, destroys the others"),
                "Immolate": (60 if money < 20 else 40, None, "destroys 5 random hand cards, +$20 (at Gold $20 is an xMult purchase; losing 5 random cards thins the deck)"),
                "Ectoplasm": (40, None, "Negative on a random joker (+1 slot), -1 hand size"),
                "Grim": (25, None, "destroys a random card, adds 2 Aces"), "Familiar": (25, None, "destroys a random card, adds 3 faces"),
                "Incantation": (25, None, "destroys a random card, adds 4 numbered cards"),
                "Medium": (20, tgt, "Purple Seal on the target card"), "Trance": (20, tgt, "Blue Seal on the target card"),
                "Ankh": (10, None, "copies a random joker, destroys the others"), "Sigil": (10, None, "all hand cards one random suit"),
                "Ouija": (10, None, "all hand cards one random rank, -1 hand size")}
        ranked = sorted(((SPEC.get(c.get("name"), (15, None, "unknown"))[0], i, c) for i, c in spectrals), key=lambda t: -t[0])
        print(f"Pack advisor: Spectral, choose {pk.get('choices_remaining')}, jokers {n_j}/{slots}")
        for sc, i, c in ranked:
            print(f"  {sc:>3} pick {i:<3} {c.get('name')}: {SPEC.get(c.get('name'), (0, None, '?'))[2]}")
        sc, i, c = ranked[0]
        if sc < 30:
            print(f"ADVICE: SKIP -> b skippack   (nothing here helps; best is {c.get('name')} at {sc})")
            return
        t = SPEC.get(c.get("name"), (0, None, ""))[1]
        print(f"ADVICE: PICK -> b pick {i}{' ' + str(t.get('index')) if t else ''}   ({c.get('name')}: {SPEC.get(c.get('name'), (0, None, ''))[2]}"
              + (f"; target {card_str(t)} (your most common rank)" if t else "") + ")")
        return
    tarots = [(i, c) for i, c in enumerate(cards, 1) if c.get("set") == "Tarot"]
    if tarots:
        # Arcana: card-phase enhancements multiply only the base mult (PLAYBOOK), so money and +mult/+chips cards on your
        # main-hand ranks come first; targets are your most common rank in hand
        hand = [c for c in lst(d.get("hand")) if c.get("rank") is not None and not c.get("debuff")]
        by_rank = Counter(_r(c) for c in hand)
        tgt_cards = sorted(hand, key=lambda c: (-by_rank[_r(c)], -CHIP_VAL.get(_r(c), 0)))
        money_a = int(d.get("money") or 0)
        sell_sum = min(50, sum(int(j.get("sell_cost") or 0) for j in jokers))
        n_x = sum(1 for j in jokers if classify_joker(j.get("name"), 0, mh)[0].startswith("XMULT"))
        TV = {"The Hermit": (70 if money_a >= 8 else 40, 0, f"+${min(20, max(money_a, 0))} (doubles money, max $20)"),
              "Temperance": (65 if sell_sum >= 6 else 20, 0, f"+${sell_sum} (your jokers' sell values)"),
              "The Empress": (55, 2, "+4 mult on 2 cards (Mult) - fires with your main-hand ranks"),
              "The Hierophant": (50, 2, "+30 chips on 2 cards (Bonus)"),
              "Strength": (45, 2, "+1 rank on 2 cards (completes pairs/straights)"),
              "Death": (45, 2, "left card becomes a copy of the right: duplicate your best rank"),
              "Justice": (55 if n_x >= 1 else 30, 1, "Glass x2 on 1 card (multiplies base mult only; strong with xMult jokers)"),
              "The Chariot": (45 if n_x >= 1 else 25, 1, "Steel x1.5 held (base mult only)"),
              "The Lovers": (35, 1, "Wild card (any suit)"), "The Devil": (40, 1, "Gold card: $3 when held at round end"),
              "The Tower": (30, 1, "Stone card +50 chips"), "The Magician": (25, 2, "Lucky cards"),
              "The Hanged Man": (40, 2, "destroy 2 cards (thin the deck)"), "The Fool": (35, 0, "copy of the last tarot/planet used"),
              "Wheel of Fortune": (20, 0, "1/4: edition on a random joker"), "Judgement": (45 if len(jokers) < slots else 5, 0, "a random joker"),
              "The Emperor": (30, 0, "2 random tarots"), "The High Priestess": (35, 0, "2 random planets"),
              "The Star": (25 if mh == "Flush" else 10, 3, "3 cards to Diamonds"), "The Moon": (25 if mh == "Flush" else 10, 3, "3 cards to Clubs"),
              "The Sun": (25 if mh == "Flush" else 10, 3, "3 cards to Hearts"), "The World": (25 if mh == "Flush" else 10, 3, "3 cards to Spades")}
        ranked_t = sorted(((TV.get(c.get("name"), (15, 0, "?"))[0], i, c) for i, c in tarots), key=lambda t: -t[0])
        print(f"Pack advisor: Arcana, choose {pk.get('choices_remaining')}")
        for sc, i, c in ranked_t:
            print(f"  {sc:>3} pick {i:<3} {c.get('name')}: {TV.get(c.get('name'), (0, 0, '?'))[2]}")
        sc, i, c = ranked_t[0]
        if sc < 25:
            print(f"ADVICE: SKIP -> b skippack   (nothing here helps; best is {c.get('name')} at {sc})")
            return
        n_t = TV.get(c.get("name"), (0, 0, ""))[1]
        tg = [str(x.get("index")) for x in tgt_cards[:n_t]] if n_t else []
        print(f"ADVICE: PICK -> b pick {i}{' ' + ' '.join(tg) if tg else ''}   ({c.get('name')}: {TV.get(c.get('name'), (0, 0, ''))[2]}"
              + (f"; targets {' '.join(card_str(x) for x in tgt_cards[:n_t])} (your most common ranks)" if tg else "") + ")")
        return
    print("No pack advice for this pack type: pick per PLAYBOOK section 5 (enhance main-hand ranks), or `skippack` if nothing fits.")


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
            print(f"Note: {bst.get('name')} offers jokers and your joker slots are full ({n_j}/{slots_j}): you can `sell N` while the pack is open to make room, or `skippack`.")
    if cmd == "sell":
        jk_s = next((j for j in lst(d.get("jokers")) if j.get("index") == params["index"]), None)
        if jk_s and _stk(jk_s)["eternal"]:
            print(f"ABORTED: {jk_s.get('name')} is ETERNAL: the game never lets you sell it (it keeps its slot for the rest of the run). Sell a different joker.")
            sys.exit(2)
    if cmd == "buy":
        itm = next((c for c in lst(shg.get("jokers")) if c.get("index") == params["slot"]), None)
        if itm and itm.get("set") in ("Planet", "Tarot", "Spectral") and n_c >= slots_c:
            print(f"Note: consumable slots are full ({n_c}/{slots_c}); `buyuse {params['slot']}` uses {itm.get('name')} straight from the shop. /legal decides.")
        if itm and itm.get("set") == "Joker" and n_j >= slots_j and _joker_edition(itm) != "negative":
            print(f"Note: joker slots are full ({n_j}/{slots_j}); if this is refused, `sell N` your weakest joker first, then buy {itm.get('name')}.")
        if itm and itm.get("set") == "Joker" and stickers(itm):
            print(f"Note: {itm.get('name')} carries {stickers(itm)}" + (": it can never be sold" if _stk(itm)["eternal"] else "")
                  + ("; rent -$3 at every round end until you sell it ($1)" if _stk(itm)["rental"] else "") + ".")
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
            print(f"Note: {name} creates a joker but your joker slots are full ({n_j}/{slots_j}): it creates nothing unless you `sell N` a joker first (selling works while a pack is open).")
        if name in ("The Fool", "The High Priestess", "The Emperor") and n_c >= slots_c:
            print(f"Note: {name} creates consumables but your consumable slots are full ({n_c}/{slots_c}): `use N` or `sellc N` one first.")
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
    if pv and pr.get("scoring"):
        scoring_idx = list(pr["scoring"])  # the game's own scoring set (Splash and Stone cards included by the bridge)
    else:
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
    if pr.get("blind_debuffed"):
        est = 0
        notes = [f"WARNING: the boss {(d.get('blind') or {}).get('name')} debuffs this {expected}: it scores 0 (only useful to cycle cards)"] + notes
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
    d_raw = _await_action_effect(wait_settled())
    d = _with_known_jokers(d_raw)
    LEGAL = get("legal")
    if cmd == "pick" and ints and d.get("phase") == "PACK_OPENING":
        # a typed index always means the CURRENT pack listing (Main 08:xx: remapping it through a cached listing sent the
        # wrong card); show what it is so a shifted index is visible before the next pick
        cur = lst((d.get("pack") or {}).get("cards"))
        if 1 <= ints[0] <= len(cur):
            print(f"(pick {ints[0]} = {cur[ints[0] - 1].get('name')} in the current pack listing)")
    if cmd in ("s", "state"):
        show(d); show_legal(LEGAL); return
    if cmd == "hands":
        show_hands(d); return
    if cmd == "advise":
        t0 = time.time()
        while d.get("phase") not in ("SELECTING_HAND", "PACK_OPENING") and time.time() - t0 < 12:
            time.sleep(0.3)  # right after `blind` / a pack pick the phase is still changing (7805)
            d = _with_known_jokers(wait_settled())
        if d.get("phase") == "PACK_OPENING":
            pack_advise_sim(d)
        else:
            advise(d)
        return
    if cmd == "shopadvise":
        _mh_hyst_update(d)
        d["_mh_hyst"] = _mh_hyst_load()
        shop_advise_sim(d); return
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
    _note_action(d_raw, typ)
    for attempt in range(4):
        r = act(typ, params)
        if r.get("ok") or not r.get("retry") or attempt == 3:
            break
        print(f"(bridge not settled: {r.get('error')}; waiting, then rebuilding the action from fresh state)")
        d_fresh = wait_settled()
        params2 = _remap_params(typ, params, d_raw, d_fresh)
        if params2 is None:
            print("REFUSED (nothing sent): the state changed under this command (a card/item it named is gone). Run `b s` and decide again.")
            sys.exit(2)
        params, d_raw = params2, d_fresh
    if r.get("ok"):
        print(f"ok: {typ}" + (f" (step {r['step']})" if r.get("step") is not None else "")
              + (f" -> recording {r['trajectory_path']}" if r.get("trajectory_path") else ""))
    else:
        print("ACTION REJECTED:", r.get("error"))
    d_pre = d
    d_raw = _await_action_effect(wait_settled()) if r.get("ok") else wait_settled()
    d = _with_known_jokers(d_raw)
    LEGAL = get("legal")
    show(d)
    show_legal(LEGAL)
    if r.get("ok") and typ in ("SHOP_BUY", "SHOP_BUY_AND_USE"):
        it = next((c for c in lst((d_pre.get("shop") or {}).get("jokers")) if c.get("index") == params.get("slot", params.get("index"))), None)
        if it is not None and it.get("set") == "Joker":
            bf = os.path.join(CACHE_DIR, f"{PORT}_bought.json")
            try:
                with open(bf, encoding="utf-8") as f:
                    bo = json.load(f)
            except Exception:
                bo = {}
            key_r = [d_pre.get("ante"), d_pre.get("round"), d_pre.get("trajectory")]
            ids = bo.get("ids", []) if bo.get("key") == key_r else []
            try:
                with open(bf, "w", encoding="utf-8") as f:
                    json.dump({"key": key_r, "ids": ids + [it.get("id")]}, f)
            except Exception:
                pass
    if r.get("ok") and typ == "REORDER" and params.get("area") == "jokers" and d_pre.get("_jokers_cached"):
        _cache_reorder([j.get("name") for j in lst(d_pre.get("jokers"))], params.get("order") or [])
    if cmd == "play" and _EST_CTX and r.get("ok"):
        _log_est(d)
        if d_pre.get("_jokers_cached") and not d_pre["_jokers_cached"].get("inferred"):
            _infer_joker_order(d)
    if not r.get("ok"):
        sys.exit(2)


def _cache_file():
    return os.path.join(CACHE_DIR, f"{PORT}_jokers.json")


def _cache_load():
    try:
        with open(_cache_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _cache_save(obj):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        tmp = _cache_file() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        os.replace(tmp, _cache_file())
    except Exception:
        pass


def _with_known_jokers(d):
    """Amber Acorn flips and shuffles the jokers face-down (blind.lua set_blind): the bridge rightly hides them, but the
    player saw them face-up a moment before. Face-up jokers are cached per port (data/.cli_cache/<port>_jokers.json);
    while they are face-down, est uses that multiset in the inferred order (after the first hand) or the last seen
    order, and d['_jokers_cached'] says so."""
    d = dict(d, _mh_hyst=_mh_hyst_load())  # main-hand hysteresis memory (per port)
    try:
        with open(os.path.join(CACHE_DIR, f"{PORT}_bought.json"), encoding="utf-8") as f:
            bo = json.load(f)
        if bo.get("key") == [d.get("ante"), d.get("round"), d.get("trajectory")]:
            d["_bought_ids"] = bo.get("ids") or []  # jokers bought in this shop: never a rental-sell target here
    except Exception:
        pass
    js = lst(d.get("jokers"))
    if not js:
        return d
    if not any(j.get("facing") == "back" or j.get("name") is None for j in js):
        _cache_save({"jokers": js, "order": None})
        return d
    c = _cache_load()
    if not c or len(lst(c.get("jokers"))) != len(js):
        print(f"(jokers face-down and no matching cached list for port {PORT}: est runs without them)")
        return d
    known = list(lst(c.get("jokers")))
    order = c.get("order")
    if order and sorted(order) == sorted(str(j.get("name")) for j in known):
        pool, arranged = list(known), []
        for nm in order:
            k = next(i for i, j in enumerate(pool) if str(j.get("name")) == nm)
            arranged.append(pool.pop(k))
        known = arranged
    new = [dict(k, index=i + 1, facing="front") for i, k in enumerate(known)]
    return dict(d, jokers=new, _jokers_cached={"inferred": bool(order)})


def _cache_reorder(names_now, new_order):
    """`order` on face-down jokers whose positions were inferred: keep the cached order in step."""
    c = _cache_load()
    if c and c.get("order") and len(new_order) == len(names_now):
        c["order"] = [names_now[p - 1] for p in new_order]
        _cache_save(c)


def _order_perms(names, cap=720):
    import itertools
    import random
    perms = list(itertools.islice(itertools.permutations(range(len(names))), cap)) if len(names) <= 6 else \
        [tuple(random.Random(k).sample(range(len(names)), len(names))) for k in range(cap)]
    return perms


def _infer_joker_order(d):
    """After a hand under Amber Acorn: the score delta tells which orders of the known jokers are possible."""
    try:
        expected, idxs, est, before, d0 = _EST_CTX
        after = (d.get("blind") or {}).get("chips_scored")
        after = int(after if after is not None else d.get("chips") or 0)
        actual = after - before if after >= before else after
        known = lst(d0.get("jokers"))
        scoring = _cards_by_idx(d0, idxs)
        held = _held(d0, [c.get("index") for c in scoring])
        fits = []
        for p in _order_perms(known):
            js = [known[i] for i in p]
            e = estimate(expected, scoring, held, dict(d0, jokers=js), played_n=len(scoring))[0]
            if abs(e - actual) <= max(2, 0.01 * actual):
                fits.append(tuple(str(j.get("name")) for j in js))
        fits = sorted(set(fits))
        if len(fits) == 1:
            _cache_save({"jokers": known, "order": list(fits[0])})
            print(f"JOKER ORDER INFERRED (scored {actual}): {' | '.join(fits[0])}. `advise` now uses it; reorder with `b order ...` (+mult left of xMult).")
        elif fits:
            print(f"(score {actual} fits {len(fits)} joker orders; play another cheap hand to narrow it, or reorder blind)")
        else:
            print(f"(score {actual} fits no order of the cached jokers: the cache may be stale)")
    except Exception as e:
        print(f"(joker order inference skipped: {e})")


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


def _remap_params(typ, params, d_old, d_new):
    """After retry:true: re-resolve every index in params by the entity ids of the state the command was built from
    (SwarmOps: a retry resent params built from stale state). None when an entity is gone."""
    sh_o, sh_n = d_old.get("shop") or {}, d_new.get("shop") or {}
    areas = {"card_indices": "hand", "targets": "hand"}
    idx_area = {"SELL_JOKER": "jokers", "SELL_CONSUMABLE": "consumables", "USE_CONSUMABLE": "consumables", "SELECT_PACK_CARD": "pack"}
    slot_area = {"SHOP_BUY": "shopj", "SHOP_BUY_AND_USE": "shopj", "SHOP_BUY_BOOSTER": "boosters", "SHOP_BUY_VOUCHER": "vouchers"}

    def items(d_, area, sh):
        if area == "pack":
            return lst((d_.get("pack") or {}).get("cards"))
        if area == "shopj":
            return lst(sh.get("jokers"))
        if area in ("boosters", "vouchers"):
            return lst(sh.get(area))
        return lst(d_.get(area))

    def remap(i, area):
        old = next((x for x in items(d_old, area, sh_o) if x.get("index") == i), None)
        if old is None or old.get("id") is None:
            return i
        new = next((x for x in items(d_new, area, sh_n) if x.get("id") == old.get("id")), None)
        return None if new is None else new.get("index")
    out = dict(params)
    for k, area in areas.items():
        if isinstance(out.get(k), list):
            m_ = [remap(i, area) for i in out[k]]
            if None in m_:
                return None
            out[k] = m_
    if typ in idx_area and "index" in out:
        out["index"] = remap(out["index"], idx_area[typ])
    if typ in slot_area and "slot" in out:
        out["slot"] = remap(out["slot"], slot_area[typ])
    if typ == "REORDER" and isinstance(out.get("order"), list):
        area = {"jokers": "jokers", "hand": "hand", "consumables": "consumables"}.get(out.get("area"), "jokers")
        ids_old = [x.get("id") for x in items(d_old, area, sh_o)]
        ids_new = [x.get("id") for x in items(d_new, area, sh_n)]
        if sorted(map(str, ids_old)) != sorted(map(str, ids_new)):
            return None
        want = [ids_old[p - 1] for p in out["order"]]
        out["order"] = [ids_new.index(w) + 1 for w in want]
    if out.get("index", 1) is None or out.get("slot", 1) is None:
        return None
    return out


class _PortLock:
    """One CLI command at a time per port, held across read -> decide -> act -> wait-settled (SwarmOps: overlapping b.sh
    calls on one port read pre-action state). Read-only commands wait for it too, so they never print mid-action state."""

    def __init__(self, timeout=90.0):
        self.timeout = timeout
        self.f = None

    def __enter__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.f = open(os.path.join(CACHE_DIR, f"{PORT}.lock"), "a+b")
        t0 = time.time()
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.f.seek(0)
                    msvcrt.locking(self.f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.time() - t0 > self.timeout:
                    print(f"(another command on port {PORT} still holds the CLI lock after {self.timeout:.0f}s; proceeding)")
                    return self
                time.sleep(0.1)

    def __exit__(self, *exc):
        try:
            if os.name == "nt":
                import msvcrt
                self.f.seek(0)
                msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.f.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        self.f.close()
        return False


if __name__ == "__main__":
    try:
        with _PortLock():
            main()
    except requests.exceptions.ConnectionError:
        print(f"BRIDGE OFFLINE: nothing is listening on port {PORT} (Connection refused). Not retryable: stop and report.")
        sys.exit(3)
