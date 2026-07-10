from models import Job
from filters import matches, is_priority, experience_ok

CFG = {
    "include_keywords": ["backend", "software engineer", "java", "python"],
    "exclude_keywords": ["staff", "frontend", "javascript", "golang"],
    "priority_locations": ["gurugram", "noida", "delhi", "ncr", "remote"],
}

# Config with the years-of-experience ceiling enabled.
CFG_YOE = dict(CFG, max_years_experience=3)


def _job(title, loc="Bengaluru", description=None):
    return Job(source="s", company="c", title=title, location=loc, url="u",
               description=description)


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


# --- Years-of-experience (YOE) filtering -----------------------------------

def test_experience_off_when_no_ceiling():
    # Feature disabled when max_years_experience is absent.
    job = _job("Backend Engineer", description="Requires 8+ years of experience")
    assert experience_ok(job, CFG)


def test_experience_keeps_when_no_yoe_detected():
    # No description, no number -> keep (don't over-filter).
    assert experience_ok(_job("Backend Engineer"), CFG_YOE)
    assert experience_ok(_job("Backend Engineer", description="Great team, fun work"), CFG_YOE)


def test_experience_excludes_above_ceiling():
    job = _job("Backend Engineer", description="You have 5+ years of experience in backend.")
    assert not experience_ok(job, CFG_YOE)


def test_experience_keeps_at_or_below_ceiling():
    job = _job("Backend Engineer", description="2+ years of professional experience required.")
    assert experience_ok(job, CFG_YOE)


def test_experience_range_uses_lower_bound():
    # "3-5 years" needs at least 3, which the 3-year ceiling satisfies.
    job = _job("Backend Engineer", description="3-5 years of experience with distributed systems.")
    assert experience_ok(job, CFG_YOE)


def test_experience_minimum_of_phrasing():
    job = _job("Backend Engineer", description="Minimum of 4 years of experience.")
    assert not experience_ok(job, CFG_YOE)


def test_experience_ignores_non_experience_numbers():
    # Company-history number must not be read as a requirement; real req is 2 years.
    desc = "We have 12 years of history. 2+ years of experience needed."
    assert experience_ok(_job("Backend Engineer", description=desc), CFG_YOE)


def test_experience_uses_min_across_multiple_reqs():
    # Preferred higher bar shouldn't disqualify when a lower requirement exists.
    desc = "3+ years of experience required; 8+ years of experience preferred."
    assert experience_ok(_job("Backend Engineer", description=desc), CFG_YOE)


def test_matches_applies_experience_filter():
    # Title passes keyword filter but description exceeds ceiling -> excluded.
    job = _job("Backend Engineer", description="Requires 6 years of experience.")
    assert not matches(job, CFG_YOE)
    ok = _job("Backend Engineer", description="1+ years of experience.")
    assert matches(ok, CFG_YOE)
