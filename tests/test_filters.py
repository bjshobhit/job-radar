from models import Job
from filters import matches, is_priority

CFG = {
    "include_keywords": ["backend", "software engineer", "java", "python"],
    "exclude_keywords": ["staff", "frontend", "javascript", "golang"],
    "priority_locations": ["gurugram", "noida", "delhi", "ncr", "remote"],
}


def _job(title, loc="Bengaluru"):
    return Job(source="s", company="c", title=title, location=loc, url="u")


def test_include_required():
    assert matches(_job("Backend Engineer"), CFG)
    assert not matches(_job("Product Manager"), CFG)


def test_exclude_blocks():
    assert not matches(_job("Staff Backend Engineer"), CFG)
    assert not matches(_job("Frontend Engineer"), CFG)


def test_word_boundary_java_not_javascript():
    assert matches(_job("Java Backend Engineer"), CFG)
    assert not matches(_job("JavaScript Engineer"), CFG)


def test_priority_location():
    assert is_priority(_job("Backend Engineer", "Gurugram"), CFG)
    assert is_priority(_job("Backend Engineer", "Remote - India"), CFG)
    assert not is_priority(_job("Backend Engineer", "Bengaluru"), CFG)


def test_strict_location_hard_filters():
    cfg = dict(CFG, strict_location=True)
    assert matches(_job("Backend Engineer", "Noida"), cfg)
    assert not matches(_job("Backend Engineer", "Bengaluru"), cfg)
