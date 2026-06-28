from models import Job
from dedup import load_seen, save_seen, partition_new


def test_partition_new():
    seen = {"a", "b"}
    jobs = [Job("s", "c", "t1", "l", "u", id="a"), Job("s", "c", "t2", "l", "u", id="z")]
    new = partition_new(jobs, seen)
    assert [j.id for j in new] == ["z"]


def test_partition_dedups_within_batch():
    jobs = [Job("s", "c", "t", "l", "u", id="dup"), Job("s", "c", "t", "l", "u", id="dup")]
    assert len(partition_new(jobs, set())) == 1


def test_load_save_roundtrip(tmp_path):
    p = tmp_path / "seen.json"
    save_seen(str(p), {"x", "y"})
    assert load_seen(str(p)) == {"x", "y"}


def test_load_missing_returns_empty(tmp_path):
    assert load_seen(str(tmp_path / "none.json")) == set()
