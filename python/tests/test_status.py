"""Offline tests for swarm status aggregation (balatro_env.data.status) and dataops helpers on synthetic runs."""

import gzip
import json
import os
import time
from pathlib import Path

import pytest

from balatro_env.data.dataops import (
    compress_trajectories,
    gui_candidates,
    gui_spot_check,
    headless_candidates,
    split_by_hash,
    superseded_files,
)
from balatro_env.data.manifest import ReplayVerdict, load_manifest, record_replays, write_manifest
from balatro_env.data.status import (
    BEGIN,
    END,
    PostMortemIndex,
    RunScanner,
    aggregate,
    render_markdown,
    write_status,
)

DAY = "trajectories/2026-10-13"


def _line(obj: dict) -> str:
    # The recorder writes sorted-key compact JSON; the scanner relies on it.
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def _header(seed, port, ms, deck="b_black", stake=1, agent="p1", **meta):
    return {"t": "header", "format_version": 1, "seed": seed, "port": port, "deck_key": deck, "stake": stake,
            "start_params": {"deck": deck, "stake": stake, "seed": seed},
            "start_meta": {"agent": agent, "why": "assigned seed", **meta}, "started_at_ms": ms,
            "unlocks": {"locked": 0, "undiscovered": 0}}


def _step(i, ante, model="m-a", agent="p1", why="because", phase="SELECTING_HAND", money=4, blind=None,
          jokers=(), ts=None, action="PLAY_HAND"):
    obs = {"phase": phase, "ante": ante, "round": ante * 3, "money": money, "hands_remaining": 3,
           "discards_remaining": 2, "jokers": [{"index": k + 1, "name": n, "key": "j_x"} for k, n in enumerate(jokers)]}
    if blind:
        obs["blind"] = blind
    return {"t": "step", "i": i, "ts_ms": ts or 1_000_000 + i, "obs": obs, "legal": {}, "hidden": {},
            "action": {"type": action, "params": {"card_indices": [1, 2]}}, "refs": {}, "result": {"ok": True},
            "meta": {"agent": agent, "model": model, "why": why}}


def _end(outcome, ante, blind=None, steps=0):
    return {"t": "end", "outcome": outcome, "ante": ante, "round": ante * 3, "steps": steps, "ts_ms": 2_000_000,
            "final_obs": {"phase": "GAME_OVER", "blind": blind} if blind else {"phase": "WIN"}}


def _write(root: Path, key: str, objs: list[dict], gz: bool, age_s: float | None = None) -> Path:
    d = root / DAY
    d.mkdir(parents=True, exist_ok=True)
    text = "".join(_line(o) for o in objs).encode("utf-8")
    path = d / (key + (".jsonl.gz" if gz else ".jsonl"))
    path.write_bytes(gzip.compress(text) if gz else text)
    if age_s is not None:
        t = time.time() - age_s
        os.utime(path, (t, t))
    return path


@pytest.fixture
def swarm(tmp_path):
    root = tmp_path / "data"
    runs = tmp_path / "docs" / "runs"
    runs.mkdir(parents=True)
    _write(root, "AAAA1111_7801_1000", [
        _header("AAAA1111", 7801, 1000, stake=2),
        _step(0, 1), {"t": "reject", "i": 1, "ts_ms": 1_000_005, "phase": "SHOP", "error": "no",
                      "action": {"type": "SHOP_BUY", "params": {"slot": 9}}, "meta": {"agent": "p1"}},
        _step(1, 8), _end("win", 8, steps=2)], gz=True)
    _write(root, "BBBB2222_7802_1000", [
        _header("BBBB2222", 7802, 1000, stake=2, agent="p2"), _step(0, 3, agent="p2"),
        _end("loss", 3, {"name": "The Wall", "chips_scored": 900, "chips_needed": 2000}, 1)], gz=True)
    _write(root, "CCCC3333_7803_1000", [
        _header("CCCC3333", 7803, 1000, deck="b_red"), _step(0, 5, model="m-b"),
        _end("loss", 5, {"name": "The Hook", "chips_scored": 1, "chips_needed": 2}, 1)], gz=True)
    _write(root, "DDDD4444_7801_2000", [
        _header("DDDD4444", 7801, 2000), _step(0, 1),
        _step(1, 2, why="Pair est 320 > 300", money=7, jokers=("Joker", "Banner"),
              blind={"name": "Big Blind", "chips_scored": 120, "chips_needed": 300})], gz=False)
    _write(root, "EEEE5555_7804_500", [
        _header("EEEE5555", 7804, 500, deck="b_red"), _step(0, 2, model="m-b")], gz=False, age_s=7200)
    _write(root, "FUZZ0001_7805_1000", [_header("FUZZ0001", 7805, 1000, agent="fuzzer"), _step(0, 6, agent="fuzzer"),
                                         _end("loss", 6, {"name": "x"}, 1)], gz=True)
    _write(root, "TEST0001_7806_1000", [_header("TEST0001", 7806, 1000, agent="test-me"),
                                         _step(0, 7, agent="test-me"), _end("loss", 7, {"name": "x"}, 1)], gz=True)
    _write(root, "AAAA1111_7820_3000", [_header("AAAA1111", 7820, 3000, agent="replay", replay_of="AAAA1111_7801_1000"),
                                         _step(0, 8, agent="replay"), _end("win", 8, steps=1)], gz=True)
    (runs / "7802_BBBB2222.md").write_text("# Run BBBB2222 (port 7802, m-a) - LOSS at ante 3\nbody\n", "utf-8")
    (runs / "notes.md").write_text("# not a post-mortem\n", "utf-8")

    def row(key, **kw):
        base = {"run_key": key, "path": f"{DAY}/{key}.jsonl.gz", "seed": key[:8], "agent": "p1", "schema_ok": True,
                "replay_ok": None, "quarantined_reason": None, "replay_of": None, "bridge_hash": "h1"}
        return {**base, **kw}

    write_manifest(root, {r["run_key"]: r for r in [
        row("AAAA1111_7801_1000", replay_ok=True),
        row("BBBB2222_7802_1000", agent="p2"),
        row("CCCC3333_7803_1000", schema_ok=False, schema_error="x", quarantined_reason="schema: x"),
        row("FUZZ0001_7805_1000", agent="fuzzer"),
        row("TEST0001_7806_1000", agent="test-me"),
        row("AAAA1111_7820_3000", agent="replay", replay_of="AAAA1111_7801_1000"),
    ]})
    return root, runs


def _status(root, runs):
    from balatro_env.data.manifest import load_manifest

    return aggregate(RunScanner(root, persist=False).scan(), load_manifest(root), PostMortemIndex(runs).scan(),
                     now_s=time.time())


def test_results_live_and_filters(swarm):
    st = _status(*swarm)
    groups = {(g["model"], g["stake"], g["deck"]): g for g in st["results"]}
    assert set(groups) == {("m-a", 2, "b_black"), ("m-b", 1, "b_red")}  # no fuzz, test or replay runs
    a = groups[("m-a", 2, "b_black")]
    assert (a["runs"], a["wins"], a["losses"], a["mean_ante"], a["max_ante"]) == (2, 1, 1, 5.5, 8)
    b = groups[("m-b", 1, "b_red")]
    assert (b["runs"], b["losses"], b["unfinished"], b["mean_ante"], b["max_ante"]) == (2, 1, 1, 3.5, 5)
    # Only the newest, recently written open file of a port is live; the stale open run counts as unfinished.
    assert [i["run"].run_key for i in st["live"]] == ["DDDD4444_7801_2000"]
    snap = st["live"][0]["run"].last
    assert (snap["money"], snap["why"], snap["jokers"], snap["chips_scored"]) == (7, "Pair est 320 > 300",
                                                                                 ["Joker", "Banner"], 120)
    assert st["counts"] == {"player_runs": 5, "finished": 4, "live": 1, "files": 8}


def test_deepest_wins_histogram_postmortems(swarm):
    st = _status(*swarm)
    deep = [(i["run"].seed, i["run"].ante, i["run"].blind, i["postmortem"]) for i in st["deepest"]]
    assert deep == [("AAAA1111", 8, None, None), ("CCCC3333", 5, "The Hook 1/2", None),
                    ("BBBB2222", 3, "The Wall 900/2000", "7802_BBBB2222.md"), ("EEEE5555", 2, None, None)]
    assert [i["run"].seed for i in st["wins"]] == ["AAAA1111"]
    assert st["histogram"]["m-a"]["W"] == 1 and st["histogram"]["m-a"]["3"] == 1
    assert st["histogram"]["m-b"]["5"] == 1 and st["histogram"]["m-b"]["2"] == 1
    assert [p.name for p in st["postmortems"]] == ["7802_BBBB2222.md"]


def test_validity_and_rejects(swarm):
    st = _status(*swarm)
    v = st["validity"]
    assert (v["files"], v["schema_ok"], v["schema_bad"], v["replay_ok"], v["awaiting_replay"]) == (3, 2, 1, 1, 1)
    assert v["quarantined"] == [("CCCC3333_7803_1000", "schema: x")]
    assert v["not_in_manifest"] == 2  # the two open runs
    assert st["validity_all"]["files"] == 5  # fuzz + replay rows counted, test-* row not
    rej = {x["agent"]: x for x in st["rejects"]}
    assert rej["p1"]["rejects"] == 1 and rej["p1"]["runs_with_rejects"] == 1
    assert rej["p2"]["rejects"] == 0 and "test-me" not in rej and "fuzzer" not in rej


def test_markdown_block_and_file_markers(swarm, tmp_path):
    st = _status(*swarm)
    md = render_markdown(st, "runs")
    assert "| 1 | AAAA1111 | m-a | 2 | Black | win | 8 |" in md
    assert "[7802_BBBB2222.md](runs/7802_BBBB2222.md)" in md
    assert "| 7801 | p1 | m-a | DDDD4444 |" in md
    assert "FUZZ0001" not in md and "TEST0001" not in md
    out = tmp_path / "docs" / "SWARM_STATUS.md"
    write_status(out, md)
    text = out.read_text("utf-8")
    assert "## Morning summary" in text and "## Orchestrator log" in text
    assert text.index(BEGIN) < text.index("AAAA1111") < text.index(END)
    out.write_text(text.replace("_Orchestrator: summarize the night here._", "All good.") + "- 23:00 note\n", "utf-8")
    write_status(out, "new block")
    text = out.read_text("utf-8")
    assert "All good." in text and text.endswith("- 23:00 note\n")
    assert f"{BEGIN}\nnew block\n{END}" in text and "AAAA1111" not in text


def test_scanner_incremental_open_file(swarm):
    root, _ = swarm
    scanner = RunScanner(root, persist=False)
    info = {r.run_key: r for r in scanner.scan()}["DDDD4444_7801_2000"]
    assert info.steps == 2 and not info.ended
    path = root / DAY / "DDDD4444_7801_2000.jsonl"
    with open(path, "a", encoding="utf-8", newline="") as fh:
        fh.write(_line(_step(2, 2, why="third")))
        fh.write('{"t":"step","i":3')  # partial line still being written
    info = {r.run_key: r for r in scanner.scan()}["DDDD4444_7801_2000"]
    assert info.steps == 3 and info.last["why"] == "third"
    with open(path, "a", encoding="utf-8", newline="") as fh:
        fh.write(',"x":1}\n' + _line(_end("loss", 2, {"name": "Big Blind"}, 4)))
    info = {r.run_key: r for r in scanner.scan()}["DDDD4444_7801_2000"]
    assert info.ended and info.outcome == "loss"


def test_scanner_disk_cache_roundtrip(swarm):
    root, _ = swarm
    first = {r.run_key: r for r in RunScanner(root).scan()}
    assert (root / ".status_cache.json").exists()
    second = {r.run_key: r for r in RunScanner(root).scan()}
    assert second["AAAA1111_7801_1000"] == first["AAAA1111_7801_1000"]
    assert second["BBBB2222_7802_1000"].blind == "The Wall 900/2000"


def test_dataops_superseded_compress_and_candidates(swarm):
    root, _ = swarm
    files = sorted((root / DAY).iterdir())
    sup = superseded_files(files)
    assert sup == set()  # 7801's open file is its newest; 7804 has a single file
    _write(root, "FFFF6666_7804_900", [_header("FFFF6666", 7804, 900), _step(0, 1)], gz=False, age_s=5)
    sup = superseded_files(sorted((root / DAY).iterdir()))
    assert [p.name for p in sup] == ["EEEE5555_7804_500.jsonl"]
    assert compress_trajectories(root, include_superseded=True, log=lambda m: None) == 1
    assert (root / DAY / "EEEE5555_7804_500.jsonl.gz").exists()
    assert (root / DAY / "DDDD4444_7801_2000.jsonl").exists()  # live file untouched

    rows = list(load_manifest(root).values())
    # AAAA1111 has a legacy (gui) verdict; fuzz/test/replay rows never; CCCC3333 is schema-invalid.
    assert [r["run_key"] for r in headless_candidates(rows)] == ["BBBB2222_7802_1000"]
    assert [r["run_key"] for r in headless_candidates(rows, include_fuzz=True)] == \
        ["BBBB2222_7802_1000", "FUZZ0001_7805_1000"]
    assert split_by_hash(headless_candidates(rows), "other-hash") == ([], 1)
    # Without headless workers every unverified run is a live candidate; with them only the sample/divergences.
    assert [r["run_key"] for r in gui_candidates(rows, headless=False)] == ["BBBB2222_7802_1000"]
    assert gui_candidates(rows, every=0) == []
    assert [r["run_key"] for r in gui_candidates(rows, every=1)] == ["BBBB2222_7802_1000"]
    for r in rows:
        if r["run_key"] == "BBBB2222_7802_1000":
            r["headless_replay_ok"] = False
    assert [r["run_key"] for r in gui_candidates(rows, every=0)] == ["BBBB2222_7802_1000"]


def test_gui_spot_check_sample_is_stable_and_about_one_in_n():
    keys = [f"S{i:07d}_7801_{i}" for i in range(2000)]
    picked = [k for k in keys if gui_spot_check(k, 10)]
    assert 150 < len(picked) < 250 and picked == [k for k in keys if gui_spot_check(k, 10)]
    assert not any(gui_spot_check(k, 0) for k in keys)


def test_per_host_replay_verdicts(swarm):
    root, runs = swarm
    from balatro_env.data.manifest import build_manifest

    build_manifest(root)
    path = root / DAY / "BBBB2222_7802_1000.jsonl.gz"
    key = "BBBB2222_7802_1000"

    record_replays(root, [ReplayVerdict(path, "headless", True, None, 1, 10, "hX")])
    row = load_manifest(root)[key]
    assert (row["replay_ok"], row["replay_host"], row["replay_bridge_hash"]) == (True, "headless", "hX")
    assert row["headless_replay_ok"] is True and row.get("gui_replay_ok") is None

    # A live spot-check that disagrees: the live game is the reference, the disagreement is spelled out.
    record_replays(root, [ReplayVerdict(path, "gui", False, "obs divergence step 0", 1, 20, "hX", "r.jsonl")])
    row = load_manifest(root)[key]
    assert (row["replay_ok"], row["replay_host"], row["headless_replay_ok"]) == (False, "gui", True)
    assert row["replay_detail"].startswith("gui: obs divergence step 0; headless/gui disagree")
    assert row["quarantined_reason"].startswith("replay: gui: obs divergence")
    assert row["replayed_at_ms"] == 20 and row["replay_path"] == "r.jsonl"
    build_manifest(root)  # verdicts survive a rebuild
    assert load_manifest(root)[key]["gui_replay_ok"] is False

    record_replays(root, [ReplayVerdict(path, "gui", True, None, 1, 30, "hX")])
    row = load_manifest(root)[key]
    assert row["replay_ok"] is True and row["replay_detail"] is None and row["quarantined_reason"] is None

    # Legacy row (replay_ok without replay_host) + a headless verdict: the old verdict becomes the gui one.
    a = root / DAY / "AAAA1111_7801_1000.jsonl.gz"
    record_replays(root, [ReplayVerdict(a, "headless", True, None, 2, 40, "hX")])
    row = load_manifest(root)["AAAA1111_7801_1000"]
    assert (row["gui_replay_ok"], row["headless_replay_ok"], row["replay_host"]) == (True, True, "gui")

    st = _status(root, runs)
    v = st["validity"]
    assert (v["gui_ok"], v["headless_ok"], v["cross_checked"], v["disagree"]) == (2, 2, 2, 0)
    assert "headless ok 2 / failed 0; gui (live) ok 2 / failed 0" in render_markdown(st)
