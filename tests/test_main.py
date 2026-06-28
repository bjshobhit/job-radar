from models import Job
from main import select_new


def test_select_new_filters_dedups_and_prioritizes():
    cfg = {"include_keywords": ["backend"], "exclude_keywords": ["staff"],
           "priority_locations": ["remote"]}
    jobs = [Job("s", "A", "Backend Engineer", "Remote", "u1"),
            Job("s", "B", "Staff Backend", "Noida", "u2"),
            Job("s", "C", "Backend Engineer", "Pune", "u3")]
    seen = set()
    result = select_new(jobs, cfg, seen)
    titles = [j.title for j, _ in result]
    assert titles == ["Backend Engineer", "Backend Engineer"]
    assert result[0][1] is True   # Remote -> priority
    assert result[1][1] is False  # Pune -> not priority


def test_select_new_respects_seen():
    cfg = {"include_keywords": ["backend"], "exclude_keywords": [], "priority_locations": []}
    j = Job("s", "A", "Backend Engineer", "Remote", "u1")
    assert select_new([j], cfg, {j.id}) == []
