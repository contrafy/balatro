"""Offline tests for the win end-state path of the replay verifier (balatro_env.data.replay) on a synthetic win.

A win's `end.final_obs` is captured the moment `G.GAME.won` flips (mid-transition, still ante 8 / boss Current);
the settled live state afterwards is already the next ante. The verifier must compare the original's final_obs
with the replay recording's own end line, never with the post-settle live state; steps stay strictly compared.
"""

import json
from pathlib import Path

from balatro_env.data.replay import ReplayResult, _compare_files, _run, finish_final
from balatro_env.data.trajectory import read_trajectory


def _obs(ante, blind_state, money, phase="SELECTING_HAND"):
    return {"phase": phase, "ante": ante, "money": money, "jokers": [{"index": 1, "id": 41, "key": "j_joker"}],
            "blind_select": {"choices": {"Boss": {"key": "bl_final_heart", "state": blind_state}}}}


WIN_FINAL = _obs(8, "Current", 39, phase="NEW_ROUND")
SETTLED_AFTER_WIN = _obs(9, "Defeated", 39, phase="WIN")  # what /state shows once the win overlay settles


def _write(path: Path, final_obs: dict | None, outcome: str = "win", ids=(41,)) -> Path:
    lines = [{"t": "header", "seed": "WIN00001", "deck_key": "b_black", "stake": 8, "port": 7807,
              "start_params": {"deck": "b_black", "stake": 8, "seed": "WIN00001"}, "start_meta": {"agent": "p"}}]
    for i, ident in enumerate(ids):
        obs = _obs(8, "Current", 30 + i)
        obs["jokers"][0]["id"] = ident
        lines.append({"t": "step", "i": i, "ts_ms": i, "obs": obs, "legal": {"settled": True, "actions": []},
                      "hidden": {"draw_order": []}, "refs": {},
                      "action": {"type": "PLAY_HAND", "params": {"card_indices": [1]}}, "meta": {"why": "x"},
                      "result": {"ok": True}})
    if final_obs is not None:
        lines.append({"t": "end", "outcome": outcome, "ante": 8, "round": 24, "steps": len(ids),
                      "final_obs": final_obs, "ts_ms": 99})
    path.write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in lines), encoding="utf-8")
    return path


class FakeBridge:
    """Live side: replays the recorded obs for every step, then settles at the post-win state."""

    def __init__(self, traj, replay_path: Path, final_state: dict):
        self.states = [s["obs"] for s in traj.steps]
        self.legal_ = [s["legal"] for s in traj.steps]
        self.k = 0
        self.replay_path = replay_path
        self.final_state = final_state
        self.settles = 0

    def act_settled(self, atype, params, meta):
        return {"ok": True, "trajectory_path": str(self.replay_path)}

    def health(self):
        return {}

    def wait_settled(self, timeout):
        self.settles += 1
        if self.k < len(self.states):
            return self.states[self.k], self.legal_[self.k]
        return self.final_state, {"settled": True, "actions": []}

    def action(self, atype, params, meta):
        self.k += 1
        return {"ok": True}


def _verify(tmp_path: Path, orig_final, replay_final, replay_ids=(41,), check_file=True, outcome="win"):
    orig = read_trajectory(_write(tmp_path / "WIN00001_7807_1.jsonl", orig_final, outcome))
    rep_path = _write(tmp_path / "WIN00001_7821_2.jsonl", replay_final, outcome, ids=replay_ids)
    res = ReplayResult(path=str(orig.path), steps_total=len(orig.steps))
    bridge = FakeBridge(orig, rep_path, SETTLED_AFTER_WIN)
    _run(orig, bridge, res, 5.0, True, lambda *a: None)
    if res.ok and check_file and res.replay_path:
        _compare_files(orig, res, lambda *a: None)
    finish_final(res)
    return res, bridge


def test_win_final_obs_compared_with_replay_end_line_not_settled_state(tmp_path):
    res, bridge = _verify(tmp_path, WIN_FINAL, WIN_FINAL)
    assert res.ok, res.report()
    assert res.steps_matched == 1 and not res.final_pending
    assert bridge.settles == 2  # one per step + the post-win settle (so the replay's end line is written)


def test_win_final_obs_ids_relabeled_like_steps(tmp_path):
    final = json.loads(json.dumps(WIN_FINAL))
    final["jokers"][0]["id"] = 77  # replay assigned other ids; consistent with its steps -> still equal
    res, _ = _verify(tmp_path, WIN_FINAL, final, replay_ids=(77,))
    assert res.ok, res.report()


def test_win_final_obs_difference_is_a_final_divergence(tmp_path):
    other = dict(WIN_FINAL, money=40)
    res, _ = _verify(tmp_path, WIN_FINAL, other)
    assert not res.ok and res.divergence_kind == "final"
    assert res.diff and res.diff[0][0] == ".money"


def test_win_without_replay_end_line_or_file_check_is_not_verified(tmp_path):
    res, _ = _verify(tmp_path, WIN_FINAL, None)
    assert not res.ok and res.divergence_kind == "final" and "no end line" in res.message
    res, _ = _verify(tmp_path, WIN_FINAL, WIN_FINAL, check_file=False)
    assert not res.ok and res.divergence_kind == "final" and "not verified" in res.message


def test_loss_still_compares_settled_live_state(tmp_path):
    # A loss settles at GAME_OVER and is compared live: here the live state differs from final_obs.
    res, _ = _verify(tmp_path, WIN_FINAL, WIN_FINAL, outcome="loss")
    assert not res.ok and res.divergence_kind == "final" and not res.final_pending
