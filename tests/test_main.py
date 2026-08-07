from models import Job
from main import select_new

LOC = {
    "mode": "india_or_remote",
    "india_tokens": ["india", "pune", "noida", "bengaluru"],
    "remote_tokens": ["remote", "wfh"],
    "global_tokens": ["worldwide", "global", "anywhere"],
    "blocked_regions": ["us", "usa", "europe", "uk"],
}


def test_select_new_filters_dedups_and_prioritizes():
    cfg = {"include_keywords": ["backend"], "exclude_keywords": ["staff"],
           "location": LOC}
    jobs = [Job("s", "A", "Backend Engineer", "Remote", "u1"),
            Job("s", "B", "Staff Backend", "Noida", "u2"),
            Job("s", "C", "Backend Engineer", "Pune", "u3")]
    seen = set()
    result = select_new(jobs, cfg, seen)
    titles = [j.title for j, _ in result]
    assert titles == ["Backend Engineer", "Backend Engineer"]
    assert result[0][1] is False  # bare Remote -> UNKNOWN -> unverified
    assert result[1][1] is True   # Pune -> INDIA -> star


def test_select_new_respects_seen():
    cfg = {"include_keywords": ["backend"], "exclude_keywords": [], "location": LOC}
    j = Job("s", "A", "Backend Engineer", "Remote", "u1")
    assert select_new([j], cfg, {j.id}) == []
