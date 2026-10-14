"""Offline tests for balatro_env.data (validator, manifest, legality, seeds, diff) on fixture files."""

import gzip
import json
import random
import shutil
from pathlib import Path

import pytest

from balatro_env import vocab
from balatro_env.data import seeds
from balatro_env.data.diff import IdCanon, all_differences, normalize
from balatro_env.data.fuzz import classify, greedy_discard, greedy_play
from balatro_env.data.legality import (
    check_action,
    check_value,
    entry_is_satisfiable,
    illegal_probes,
    sample_params,
)
from balatro_env.data.manifest import build_manifest, load_manifest, update_replay_result
from balatro_env.data.trajectory import find_trajectories, read_trajectory, run_key
from balatro_env.data.validate import hidden_leaks, validate_trajectory
from balatro_env.schemas import GameState, LegalActions

FIXTURES = Path(__file__).parent / "fixtures" / "trajectories"


def fixture(name: str) -> Path:
    return FIXTURES / name


# ---------------------------------------------------------------------------------------------
# Validator


class TestValidator:
    def test_valid_trajectory(self):
        rep = validate_trajectory(fixture("valid.jsonl"))
        assert rep.ok, rep.errors
        assert rep.outcome == "loss"
        assert (rep.steps, rep.rejects) == (4, 1)
        assert rep.warnings == []

    def test_illegal_action_is_rejected(self):
        rep = validate_trajectory(fixture("illegal_action.jsonl"))
        assert not rep.ok
        assert any("step 3" in e and "illegal action" in e for e in rep.errors), rep.errors

    def test_hidden_field_leak(self):
        rep = validate_trajectory(fixture("hidden_leak.jsonl"))
        assert not rep.ok
        joined = "\n".join(rep.errors)
        assert "face-down entity exposes ['rank', 'suit']" in joined
        assert "run_id: hidden key in obs" in joined
        assert "contains the run seed" in joined

    def test_truncated_file(self):
        traj = read_trajectory(fixture("truncated.jsonl"))
        assert traj.truncated and traj.end is None
        rep = validate_trajectory(traj)
        assert not rep.ok
        assert rep.outcome == "abandoned"
        assert any("truncated" in e for e in rep.errors)

    def test_missing_end_line_is_abandoned_not_invalid(self, tmp_path):
        lines = fixture("valid.jsonl").read_text(encoding="utf-8").splitlines(keepends=True)
        path = tmp_path / "noend.jsonl"
        path.write_text("".join(lines[:-1]), encoding="utf-8")
        rep = validate_trajectory(path)
        assert rep.ok, rep.errors
        assert rep.outcome == "abandoned"
        assert rep.warnings

    def test_gzip_roundtrip_and_truncated_gzip(self, tmp_path):
        data = fixture("valid.jsonl").read_bytes()
        gz = tmp_path / "run.jsonl.gz"
        gz.write_bytes(gzip.compress(data))
        assert validate_trajectory(gz).ok
        cut = tmp_path / "cut.jsonl.gz"
        cut.write_bytes(gzip.compress(data)[:-40])
        rep = validate_trajectory(cut)
        assert not rep.ok and any("truncated" in e for e in rep.errors)

    @pytest.mark.parametrize("mutate, expected", [
        (lambda ls: ls[0]["unlocks"].update(locked=3), "unlocks.locked"),
        (lambda ls: ls[0].pop("game_version"), "game_version"),
        (lambda ls: ls[0].update(bridge_hash=""), "bridge_hash"),
        (lambda ls: ls[4].update(i=7), "does not follow"),
        (lambda ls: ls[2]["result"].update(ok=False), "result.ok"),
        (lambda ls: ls[2]["legal"].update(settled=False), "settled"),
        (lambda ls: ls[-1].update(steps=9), "end.steps"),
        (lambda ls: ls[1]["action"].update(params={"option": "boss"}), "illegal action"),
        (lambda ls: ls.append({"t": "step", "i": 4, "ts_ms": 1760000009000}), "after end"),
        (lambda ls: ls[-1].update(tainted=True), "tainted"),
        (lambda ls: ls.insert(2, {"t": "debug", "ts_ms": 1760000001500, "lua": "G.GAME.dollars = 99"}),
         "debug/eval"),
    ])
    def test_structural_errors(self, tmp_path, mutate, expected):
        lines = [json.loads(s) for s in fixture("valid.jsonl").read_text(encoding="utf-8").splitlines()]
        mutate(lines)
        path = tmp_path / "bad.jsonl"
        path.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
        rep = validate_trajectory(path)
        assert not rep.ok
        assert any(expected in e for e in rep.errors), rep.errors

    def test_hidden_leaks_allows_clean_face_down(self):
        obs = {"hand": [{"facing": "back", "area_index": 1}], "jokers": [{"facing": "front", "key": "j_joker"}]}
        assert hidden_leaks(obs, "K7QW3ZPA") == []
        obs["jokers"].append({"facing": "back", "id": 7})
        assert hidden_leaks(obs, None) == ["obs.jokers[1]: face-down entity exposes ['id']"]


# ---------------------------------------------------------------------------------------------
# Manifest


class TestManifest:
    def make_root(self, tmp_path: Path) -> Path:
        day = tmp_path / "trajectories" / "2026-10-13"
        day.mkdir(parents=True)
        shutil.copy(fixture("valid.jsonl"), day / "K7QW3ZPA_7779_1760000000000.jsonl")
        shutil.copy(fixture("illegal_action.jsonl"), day / "K7QW3ZPA_7779_1760000099999.jsonl")
        (day / "K7QW3ZPA_7779_1760000000000.jsonl.gz").write_bytes(
            gzip.compress(fixture("valid.jsonl").read_bytes()))
        return tmp_path

    def test_rows_and_quarantine(self, tmp_path):
        root = self.make_root(tmp_path)
        path, rows = build_manifest(root)
        assert path == root / "manifest.jsonl"
        by_key = {r["run_key"]: r for r in rows}
        assert len(by_key) == 2  # .jsonl twin of a .jsonl.gz is not double counted
        good = by_key["K7QW3ZPA_7779_1760000000000"]
        assert good["path"].endswith(".jsonl.gz")
        for col in ("path", "seed", "deck", "stake", "outcome", "steps", "bridge_hash", "schema_ok",
                    "replay_ok", "quarantined_reason"):
            assert col in good
        assert (good["seed"], good["deck"], good["stake"], good["outcome"], good["steps"]) == \
            ("K7QW3ZPA", "b_red", 1, "loss", 4)
        assert good["schema_ok"] is True and good["replay_ok"] is None and good["quarantined_reason"] is None
        bad = by_key["K7QW3ZPA_7779_1760000099999"]
        assert bad["schema_ok"] is False and bad["quarantined_reason"].startswith("schema:")

    def test_replay_results_survive_rebuild(self, tmp_path):
        root = self.make_root(tmp_path)
        build_manifest(root)
        traj = root / "trajectories" / "2026-10-13" / "K7QW3ZPA_7779_1760000000000.jsonl.gz"
        update_replay_result(root, traj, False, "obs divergence step 2", None, 1, 4)
        assert load_manifest(root)[run_key(traj)]["quarantined_reason"] == "replay: obs divergence step 2"
        update_replay_result(root, traj, True, None, "x.jsonl", 2, 4)
        build_manifest(root)
        row = load_manifest(root)[run_key(traj)]
        assert row["replay_ok"] is True and row["quarantined_reason"] is None
        # a verdict for fewer steps than the file now has (file grew while open) does not count
        update_replay_result(root, traj, True, None, "x.jsonl", 3, 3)
        row = load_manifest(root)[run_key(traj)]
        assert row["replay_ok"] is None and "replay again" in row["replay_detail"]

    def test_find_trajectories_skips_manifest(self, tmp_path):
        root = self.make_root(tmp_path)
        build_manifest(root)
        assert all(p.name != "manifest.jsonl" for p in find_trajectories(root))


# ---------------------------------------------------------------------------------------------
# Legality domains


LEGAL = {
    "schema_version": "1.1.0", "phase": "SELECTING_HAND", "settled": True,
    "actions": [
        {"type": "PLAY_HAND", "params": {"card_indices": {"subset": {"of": [1, 2, 3, 4, 5, 6, 7, 8], "min": 1,
                                                                     "max": 5, "must_include": [2]}}}},
        {"type": "USE_CONSUMABLE", "params": {"index": {"one_of": [1]},
                                              "targets": {"subset": {"of": [1, 2, 3], "min": 1, "max": 2}}}},
        {"type": "USE_CONSUMABLE", "params": {"index": {"one_of": [2]}}},
        {"type": "REORDER", "params": {"area": {"one_of": ["jokers"]}, "order": {"permutation": 3}}},
        {"type": "SORT_HAND", "params": {"mode": {"one_of": ["rank", "suit"]}}},
        {"type": "START_RUN", "params": {"deck": {"one_of": ["b_red"]}, "stake": {"one_of": [1, 2]},
                                         "seed": {"seed": True, "optional": True}}},
    ],
}


class TestLegality:
    @pytest.mark.parametrize("action", [
        {"type": "PLAY_HAND", "params": {"card_indices": [2]}},
        {"type": "PLAY_HAND", "params": {"card_indices": [8, 2, 1, 5, 6]}},
        {"type": "USE_CONSUMABLE", "params": {"index": 1, "targets": [3]}},
        {"type": "USE_CONSUMABLE", "params": {"index": 2}},
        {"type": "USE_CONSUMABLE", "params": {"index": 2, "targets": []}},
        {"type": "REORDER", "params": {"area": "jokers", "order": [3, 1, 2]}},
        {"type": "START_RUN", "params": {"deck": "b_red", "stake": 2}},
        {"type": "START_RUN", "params": {"deck": "b_red", "stake": 1, "seed": "ABCD1234"}},
    ])
    def test_legal(self, action):
        assert check_action(LEGAL, action) is None

    @pytest.mark.parametrize("action", [
        {"type": "PLAY_HAND", "params": {"card_indices": [1]}},           # misses forced card
        {"type": "PLAY_HAND", "params": {"card_indices": [2, 2]}},        # duplicate
        {"type": "PLAY_HAND", "params": {"card_indices": [1, 2, 3, 4, 5, 6]}},
        {"type": "PLAY_HAND", "params": {"card_indices": [2, 9]}},
        {"type": "PLAY_HAND", "params": {"card_indices": [2], "extra": 1}},
        {"type": "PLAY_HAND", "params": {}},
        {"type": "USE_CONSUMABLE", "params": {"index": 1}},               # targets required (min 1)
        {"type": "USE_CONSUMABLE", "params": {"index": 2, "targets": [1]}},
        {"type": "USE_CONSUMABLE", "params": {"index": True, "targets": [1]}},
        {"type": "REORDER", "params": {"area": "jokers", "order": [1, 2]}},
        {"type": "REORDER", "params": {"area": "hand", "order": [1, 2, 3]}},
        {"type": "SORT_HAND", "params": {"mode": "value"}},
        {"type": "START_RUN", "params": {"deck": "b_red", "stake": 3}},
        {"type": "DISCARD", "params": {"card_indices": [1]}},
        {"type": "SELECT_PACK_ITEM", "params": {"choice_index": 1}},
    ])
    def test_illegal(self, action):
        assert check_action(LEGAL, action) is not None

    def test_unsettled_snapshot_allows_nothing(self):
        assert check_action({**LEGAL, "settled": False}, {"type": "SORT_HAND", "params": {"mode": "rank"}})

    def test_samples_are_always_legal(self):
        rng = random.Random(1)
        for _ in range(500):
            entry = rng.choice(LEGAL["actions"])
            action = {"type": entry["type"], "params": sample_params(entry, rng, seed="FUZZ0001")}
            assert check_action(LEGAL, action) is None, action

    def test_probes_are_all_illegal_and_never_start_run(self):
        probes = illegal_probes(LEGAL, random.Random(3))
        assert len(probes) > 10
        for p in probes:
            assert p["type"] != "START_RUN"
            assert check_action(LEGAL, p) is not None, p

    def test_unsatisfiable_entry(self):
        entry = {"type": "PLAY_HAND", "params": {"card_indices": {"subset": {"of": [1], "min": 2, "max": 5}}}}
        assert not entry_is_satisfiable(entry)

    def test_lua_empty_table_lists(self):
        assert check_value({"subset": {"of": [1, 2], "min": 0, "max": 2, "must_include": {}}}, {}) is None

    def test_fixture_steps_pass_python_domain_check(self):
        for step in read_trajectory(fixture("valid.jsonl")).steps:
            assert check_action(step["legal"], step["action"]) is None


# ---------------------------------------------------------------------------------------------
# Seeds


class TestSeeds:
    def test_eval_file_matches_generator(self):
        listed = [s for s in seeds.EVAL_SEEDS_PATH.read_text(encoding="utf-8").splitlines()
                  if s and not s.startswith("#")]
        assert listed == seeds.generate_eval_seeds()
        assert len(set(listed)) == 500
        assert all(seeds.is_valid_seed(s) and not seeds.is_fuzz_seed(s) for s in listed)

    def test_ranges_are_disjoint(self):
        rng = random.Random(0)
        fresh = seeds.swarm_seeds(200, rng)
        assert all(seeds.reserved_reason(s) is None and seeds.is_valid_seed(s) for s in fresh)
        fz = [seeds.fuzz_seed(i) for i in range(50)]
        assert len(set(fz)) == 50
        assert all(seeds.is_valid_seed(s) and seeds.reserved_reason(s) == "fuzzer seed range" for s in fz)
        assert seeds.reserved_reason(seeds.generate_eval_seeds()[0]) == "held-out eval seed"


# ---------------------------------------------------------------------------------------------
# Replay diff + fuzz helpers


class TestDiff:
    def test_ids_relabelled_and_volatile_dropped(self):
        a = {"timestamp_ms": 1, "hand": [{"id": 100, "rank": "Ace"}, {"id": 101, "rank": "2"}], "x": {}}
        b = {"timestamp_ms": 9, "hand": [{"id": 500, "rank": "Ace"}, {"id": 501, "rank": "2"}], "x": []}
        assert all_differences(normalize(a, IdCanon()), normalize(b, IdCanon())) == []

    def test_order_change_detected(self):
        a = {"hand": [{"id": 1, "rank": "Ace"}, {"id": 2, "rank": "2"}]}
        b = {"hand": [{"id": 2, "rank": "2"}, {"id": 1, "rank": "Ace"}]}
        diffs = all_differences(normalize(a, IdCanon()), normalize(b, IdCanon()))
        assert diffs and diffs[0][0] == ".hand[0].rank"

    def test_classify_and_greedy(self):
        assert classify([(13, "S"), (13, "H")])[0] == "Pair"
        assert classify([(2, "S"), (3, "S"), (4, "S"), (5, "S"), (14, "S")])[0] == "Straight Flush"
        state = {"hand": [{"rank": "King", "suit": "Spades"}, {"rank": "2", "suit": "Hearts"},
                          {"rank": "King", "suit": "Hearts"}, {"rank": "7", "suit": "Clubs"}]}
        entry = {"params": {"card_indices": {"subset": {"of": [1, 2, 3, 4], "min": 1, "max": 5}}}}
        assert greedy_play(state, entry)[0] == [1, 3]
        discard_entry = {"params": {"card_indices": {"subset": {"of": [1, 2, 3, 4], "min": 1, "max": 5,
                                                                "must_include": [4]}}}}
        assert greedy_discard(state, discard_entry) == [2, 4]


# ---------------------------------------------------------------------------------------------
# Python RL-side fixes


class TestRlSideFixes:
    def test_schema_keeps_bridge_fields(self):
        payload = {
            "schema_version": "1.1.0", "timestamp_ms": 1, "phase": "SELECTING_HAND", "settled": True,
            "won": False, "preview": {"hand": "Pair"}, "new_field": {"a": 1},
            "hand": [{"id": 1, "rank": "Ace", "perma_bonus": 10, "perma_mult": 2, "future": True},
                     {"facing": "back"}],
            "hand_levels": {"Pair": {"level": 2, "played": 3, "played_this_round": 1}},
        }
        state = GameState.model_validate(payload)
        dumped = state.model_dump()
        assert dumped["new_field"] == {"a": 1} and dumped["preview"] == {"hand": "Pair"}
        assert state.hand[0].perma_bonus == 10 and dumped["hand"][0]["future"] is True
        assert state.hand[1].id is None
        assert state.hand_levels["Pair"].played == 3 and state.settled is True

    def test_legal_actions_parse_new_shape(self):
        legal = LegalActions.model_validate(LEGAL)
        use = [a for a in legal.actions if a.type.value == "USE_CONSUMABLE"]
        assert use[0].options("index") == [1] and use[0].subset("targets")["max"] == 2
        assert use[1].to_request().params == {"index": 2}

    def test_stable_vocab_ids(self):
        assert vocab.JOKER_IDS["j_joker"] == 1 and len(vocab.JOKER_KEYS) == 150
        assert vocab.lookup(vocab.JOKER_IDS, None) == 0
        assert vocab.lookup(vocab.JOKER_IDS, "j_not_real") == 151
        assert vocab.ENHANCEMENT_IDS["m_glass"] == vocab.ENHANCEMENT_IDS["Glass Card"]
        assert len(set(vocab.CONSUMABLE_KEYS)) == 52

    def test_tokenizer_has_no_salted_hash(self):
        src = (Path(__file__).parents[1] / "balatro_env" / "obs_tokenizer.py").read_text(encoding="utf-8")
        assert "hash(" not in src
