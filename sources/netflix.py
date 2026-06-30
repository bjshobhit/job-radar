from typing import List, Dict
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_netflix(data: Dict) -> List[Job]:
    out = []
    for j in data.get("positions", []):
        locs = j.get("locations") or [j.get("location", "")]
        out.append(Job(source="netflix", company="Netflix",
                       title=j.get("name", ""),
                       location=", ".join(x for x in locs if x) or "N/A",
                       url=j.get("canonicalPositionUrl", ""),
                       posted_at=str(j.get("t_create", ""))))
    return out


def fetch(query: str = "backend", num: int = 100) -> List[Job]:
    url = "https://explore.jobs.netflix.net/api/apply/v2/jobs"
    params = {"domain": "netflix.com", "query": query, "start": 0, "num": num}
    return safe_fetch("netflix",
                      lambda: parse_netflix(http_get_json(url, params)))
