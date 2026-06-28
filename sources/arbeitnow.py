from typing import List, Dict
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_arbeitnow(data: Dict) -> List[Job]:
    out = []
    for j in data.get("data", []):
        loc = j.get("location", "")
        if j.get("remote"):
            loc = (loc + " (remote)").strip()
        out.append(Job(source="arbeitnow", company=j.get("company_name", ""),
                       title=j.get("title", ""), location=loc,
                       url=j.get("url", "")))
    return out


def fetch() -> List[Job]:
    return safe_fetch(
        "arbeitnow",
        lambda: parse_arbeitnow(http_get_json(
            "https://www.arbeitnow.com/api/job-board-api")))
