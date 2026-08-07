from models import Job
from location import (classify_location, location_ok, is_india_star,
                     INDIA, REMOTE_ELIGIBLE, REMOTE_REGION_LOCKED,
                     OTHER_COUNTRY, UNKNOWN)

CFG = {
    "location": {
        "mode": "india_or_remote",
        "india_tokens": [
            "india", "bengaluru", "bangalore", "mumbai", "pune", "hyderabad",
            "chennai", "gurugram", "gurgaon", "noida", "delhi", "ncr",
            "kolkata", "ahmedabad", "jaipur",
        ],
        "remote_tokens": ["remote", "work from home", "wfh", "anywhere"],
        "global_tokens": ["worldwide", "global", "anywhere"],
        "blocked_regions": [
            "united states", "usa", "us", "emea", "europe",
            "uk", "united kingdom", "canada", "latam", "singapore", "dubai",
            "germany", "san francisco", "new york", "london",
        ],
    }
}


def _job(loc, description=None):
    return Job(source="s", company="c", title="Backend Engineer",
               location=loc, url="u", description=description)


# --- INDIA -----------------------------------------------------------------

def test_india_cities_classify_india():
    for city in ["Bengaluru", "Mumbai, India", "Pune", "Hyderabad, India",
                 "Gurugram", "Noida", "New Delhi", "NCR", "Chennai"]:
        assert classify_location(_job(city), CFG) == INDIA, city


def test_bare_india_token():
    assert classify_location(_job("India"), CFG) == INDIA


# --- REMOTE_ELIGIBLE -------------------------------------------------------

def test_remote_india_is_eligible():
    assert classify_location(_job("Remote - India"), CFG) == REMOTE_ELIGIBLE


def test_remote_worldwide_is_eligible():
    assert classify_location(_job("Remote (Worldwide)"), CFG) == REMOTE_ELIGIBLE
    assert classify_location(_job("Remote - Global"), CFG) == REMOTE_ELIGIBLE


def test_india_wins_over_blocked_region():
    # India appearing alongside a blocked region keeps the job.
    assert classify_location(_job("Remote - India/US"), CFG) == REMOTE_ELIGIBLE
    assert classify_location(_job("Bengaluru or London"), CFG) == INDIA


# --- REMOTE_REGION_LOCKED (drop) -------------------------------------------

def test_remote_us_locked_drops():
    assert classify_location(_job("Remote - US"), CFG) == REMOTE_REGION_LOCKED
    assert classify_location(_job("Remote (EMEA)"), CFG) == REMOTE_REGION_LOCKED
    assert classify_location(_job("Remote, United Kingdom"), CFG) == REMOTE_REGION_LOCKED


# --- OTHER_COUNTRY (drop) --------------------------------------------------

def test_other_country_drops():
    for loc in ["San Francisco, CA", "London, UK", "Berlin, Germany",
                "Singapore", "New York"]:
        assert classify_location(_job(loc), CFG) == OTHER_COUNTRY, loc


# --- UNKNOWN (keep, unverified) --------------------------------------------

def test_unknown_kept():
    assert classify_location(_job(""), CFG) == UNKNOWN
    assert classify_location(_job(None), CFG) == UNKNOWN
    assert classify_location(_job("Remote"), CFG) == UNKNOWN
    assert classify_location(_job("Multiple Locations"), CFG) == UNKNOWN


# --- location_ok -----------------------------------------------------------

def test_location_ok_keeps_india_remote_unknown():
    assert location_ok(_job("Bengaluru"), CFG)
    assert location_ok(_job("Remote - India"), CFG)
    assert location_ok(_job(""), CFG)


def test_location_ok_drops_blocked():
    assert not location_ok(_job("Remote - US"), CFG)
    assert not location_ok(_job("London, UK"), CFG)


# --- is_india_star ---------------------------------------------------------

def test_star_for_india_and_remote_eligible():
    assert is_india_star(INDIA)
    assert is_india_star(REMOTE_ELIGIBLE)
    assert not is_india_star(UNKNOWN)
    assert not is_india_star(REMOTE_REGION_LOCKED)


# --- description fallback ---------------------------------------------------

def test_description_fallback_for_india():
    # Empty location but JD mentions the office city -> still India.
    j = _job("", description="Join our Bengaluru office, hybrid 3 days/week.")
    assert classify_location(j, CFG) == INDIA
