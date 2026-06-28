import json
import os
from sources.greenhouse import parse_greenhouse

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_greenhouse():
    data = json.load(open(os.path.join(FIX, "greenhouse.json")))
    jobs = parse_greenhouse("acme", data)
    assert len(jobs) == 1
    j = jobs[0]
    assert j.company == "acme" and j.title == "Backend Engineer"
    assert j.location == "Bengaluru, India"
    assert j.url.endswith("/jobs/1") and j.source == "greenhouse"
