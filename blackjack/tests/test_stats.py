import json

from bjtrainer.config import Settings
from bjtrainer.stats import Stats


def test_records_and_accuracy(tmp_path):
    s = Stats(path=tmp_path / "stats.json")
    s.record("hard 16 v T", False)
    s.record("hard 16 v T", True)
    s.record("hard 12 v 4", True)
    attempts, errors = s.section_accuracy("basic")
    assert (attempts, errors) == (3, 1)
    assert s.cells["hard 16 v T"].accuracy == 0.5


def test_weighting_prefers_unseen_then_missed(tmp_path):
    s = Stats(path=tmp_path / "stats.json")
    for _ in range(4):
        s.record("hard 16 v T", False)
    for _ in range(4):
        s.record("hard 20 v 2", True)
    assert s.weight("never seen") > s.weight("hard 20 v 2")
    assert s.weight("hard 16 v T") > s.weight("hard 20 v 2")


def test_round_trips_through_disk(tmp_path):
    path = tmp_path / "stats.json"
    s = Stats(path=path)
    s.record("hard 16 v 9", False, section="shoe")
    s.record_count_drill(True)
    s.save()
    again = Stats.load(path)
    assert again.cells["hard 16 v 9"].errors == 1
    assert again.section_accuracy("shoe") == (1, 1)
    assert again.count_drills["attempts"] == 1


def test_corrupt_stats_file_does_not_crash(tmp_path):
    path = tmp_path / "stats.json"
    path.write_text("{not json")
    assert Stats.load(path).cells == {}


def test_worst_cells_are_ranked_by_miss_rate(tmp_path):
    s = Stats(path=tmp_path / "stats.json")
    for _ in range(5):
        s.record("hard 16 v 9", False)
    s.record("hard 12 v 4", False)
    s.record("hard 12 v 4", True)
    s.record("hard 12 v 4", True)
    worst = s.worst_cells()
    assert worst[0][0] == "hard 16 v 9"


def test_settings_round_trip_and_rules(tmp_path):
    path = tmp_path / "config.json"
    s = Settings(decks=8, h17=True, surrender=False, system="KO")
    s.save(path)
    again = Settings.load(path)
    assert again.decks == 8 and again.h17 and not again.surrender
    assert again.rules.label == "8D H17 DAS NoSur 3:2"
    assert again.count_system.name == "KO"


def test_unknown_settings_keys_are_ignored(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"decks": 2, "from_the_future": True}))
    assert Settings.load(path).decks == 2
