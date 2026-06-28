from typing import List, Dict
from models import Job, make_id
from sources.base import http_get_json, safe_fetch


def parse_himalayas(data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        locs = ", ".join(j.get("locationRestrictions") or []) or "Remote"
        job = Job(source="himalayas", company=j.get("companyName", ""),
                  title=j.get("title", ""), location=locs,
                  url=j.get("applicationLink", ""))
        guid = j.get("guid")
        if guid:
            job.id = make_id("himalayas", "", "", guid)
        out.append(job)
    return out


def fetch(limit: int = 50) -> List[Job]:
    return safe_fetch(
        "himalayas",
        lambda: parse_himalayas(http_get_json(
            "https://himalayas.app/jobs/api", {"limit": limit})))
