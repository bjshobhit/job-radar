import json
import os
from sources.lever import parse_lever
from sources.ashby import parse_ashby

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_parse_lever():
    data = json.load(open(os.path.join(FIX, "lever.json")))
    jobs = parse_lever("acme", data)
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].location == "Gurugram"
    assert jobs[0].source == "lever"


def test_parse_ashby():
    data = json.load(open(os.path.join(FIX, "ashby.json")))
    jobs = parse_ashby("acme", data)
    assert jobs[0].title == "Software Engineer, Backend"
    assert jobs[0].location == "Remote - India"
    assert jobs[0].source == "ashby"
