import json
import os
from sources.adzuna import parse_adzuna
from sources.remotive import parse_remotive

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_adzuna():
    data = json.load(open(os.path.join(FIX, "adzuna.json")))
    jobs = parse_adzuna(data)
    assert jobs[0].company == "Acme"
    assert jobs[0].location == "Noida, India"
    assert jobs[0].salary and "2000000" in jobs[0].salary
    assert jobs[0].source == "adzuna"


def test_adzuna_id_stable_across_rotating_redirect_url():
    # Adzuna's redirect_url carries a rotating tracking token that changes on
    # every API call. Dedup must rely on Adzuna's stable job id instead, so the
    # same posting yields the same id across runs (no repeat alerts).
    base = {"title": "Backend Engineer", "company": {"display_name": "Acme"},
            "location": {"display_name": "Noida"}, "id": "123456789"}
    a = parse_adzuna({"results": [dict(base, redirect_url="https://adzuna/x?token=AAA")]})
    b = parse_adzuna({"results": [dict(base, redirect_url="https://adzuna/x?token=BBB")]})
    assert a[0].id == b[0].id


def test_parse_remotive():
    data = json.load(open(os.path.join(FIX, "remotive.json")))
    jobs = parse_remotive(data)
    assert jobs[0].company == "Acme"
    assert jobs[0].location == "Remote"
    assert jobs[0].source == "remotive"
