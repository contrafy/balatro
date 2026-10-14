"""Headless engine tests. Need the user's Balatro.exe (game source is never committed) and lupa; skip otherwise."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import pytest

lupa = pytest.importorskip("lupa", reason="lupa not installed (pip install -e 'python[headless]')")

from balatro_env.data.trajectory import find_trajectories, read_trajectory  # noqa: E402
from balatro_env.data.validate import validate_trajectory  # noqa: E402
from balatro_env.headless.source import BRIDGE_DIR, find_exe  # noqa: E402

pytestmark = pytest.mark.skipif(find_exe() is None, reason="Balatro.exe not found (set BALATRO_EXE)")

LIVE_FIXTURES = Path(__file__).parent / "fixtures" / "live"


@pytest.fixture(scope="module", autouse=True)
def _quiet_faulthandler():
    """LuaJIT on Windows x64 raises Lua errors as SEH exceptions (code 0xE24C4A02) that its own pcall catches;
    pytest's faulthandler would print a 'Windows fatal exception' dump for each. They are not crashes."""
    import faulthandler

    was = faulthandler.is_enabled()
    faulthandler.disable()
    yield
    if was:
        faulthandler.enable()


@pytest.fixture(scope="module")
def env():
    from balatro_env.headless.env import HeadlessEnv

    return HeadlessEnv(agent="test-headless")


def _bridge_hash() -> str:
    return hashlib.sha256((BRIDGE_DIR / "main.lua").read_bytes() + (BRIDGE_DIR / "lovely.toml").read_bytes()).hexdigest()


def test_boot_reaches_unlocked_menu(env):
    h = env.engine.health()
    assert h["unlocked"] is True
    assert h["bridge_hash"] == _bridge_hash()
    assert h["game_version"].startswith("1.0.")
    ok, phase, _ = env.engine.status()
    assert ok and phase in ("MENU", "GAME_OVER", "WIN", "BLIND_SELECT", "SELECTING_HAND", "SHOP",
                            "ROUND_EVAL", "PACK_OPENING")


def test_reset_and_random_steps(env):
    from balatro_env.headless.env import random_legal_action

    obs, legal = env.reset("TESTHL01", "b_black", 2)
    assert obs["phase"] == "BLIND_SELECT" and obs["deck_key"] == "b_black" and obs["stake"] == 2
    assert legal["settled"] is True and legal["actions"]
    rng = random.Random(7)
    for _ in range(40):
        obs, legal, done, info = env.step(random_legal_action(legal, rng))
        assert info["ok"], info
        if done:
            break
        assert legal["settled"] is True


def test_illegal_action_rejected_without_state_change(env):
    obs, legal = env.reset("TESTHL02", "b_red", 1)
    obs2, legal2, done, info = env.step({"type": "PLAY_HAND", "params": {"card_indices": [1]}})
    assert not info["ok"] and info["error"]
    assert not done
    assert obs2 == obs and legal2 == legal


def test_same_seed_same_actions_same_observations():
    from balatro_env.headless.env import HeadlessEnv, random_legal_action

    def run(e):
        rng = random.Random(3)
        obs, legal = e.reset("TESTHL03", "b_plasma", 1)
        seen = [obs]
        for _ in range(25):
            obs, legal, done, _ = e.step(random_legal_action(legal, rng))
            seen.append(obs)
            if done:
                break
        return seen

    a = HeadlessEnv(agent="test-headless")
    first = run(a)
    assert run(a) == first  # same engine, second run
    assert run(HeadlessEnv(agent="test-headless")) == first  # fresh engine


def test_recording_is_valid_and_replays(tmp_path):
    from balatro_env.headless.env import HeadlessEnv, random_legal_action
    from balatro_env.headless.replay import replay

    env = HeadlessEnv(record_dir=tmp_path, agent="test-headless", port=1)
    rng = random.Random(11)
    obs, legal = env.reset("TESTHL04", "b_red", 1, meta={"why": "headless recording test"})
    done = False
    for _ in range(400):
        obs, legal, done, info = env.step(random_legal_action(legal, rng), meta={"why": "random"})
        if done:
            break
    assert done, "random policy should lose a run within 400 steps"
    files = find_trajectories(tmp_path)
    assert len(files) == 1 and files[0].name.endswith(".jsonl.gz")
    traj = read_trajectory(files[0])
    assert traj.header["host"] == "headless"
    assert traj.header["lovely_version"].startswith("headless-")
    assert traj.header["start_meta"]["agent"] == "test-headless"
    assert traj.end and traj.end["outcome"] in ("loss", "win")
    rep = validate_trajectory(traj)
    assert rep.ok, rep.errors
    res = replay(files[0], log=lambda *a: None)
    assert res.ok, res.report()


@pytest.mark.parametrize("path", sorted(LIVE_FIXTURES.glob("*.jsonl*")), ids=lambda p: p.name)
def test_live_recorded_fixture_replays(path):
    """A run recorded on a live GUI instance (includes a joker REORDER that Brainstorm's per-frame
    compatibility flag must reflect) reproduces exactly, including hidden draw order."""
    from balatro_env.headless.replay import replay

    res = replay(path, log=lambda *a: None)
    assert res.ok, res.report()
    assert res.steps_matched == res.steps_total > 0
