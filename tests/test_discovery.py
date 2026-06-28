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


def test_parse_remotive():
    data = json.load(open(os.path.join(FIX, "remotive.json")))
    jobs = parse_remotive(data)
    assert jobs[0].company == "Acme"
    assert jobs[0].location == "Remote"
    assert jobs[0].source == "remotive"
