from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_remoteok(data) -> List[Job]:
    out = []
    for j in data:
        # The first array element is API legal metadata, not a job.
        if not isinstance(j, dict) or not j.get("position"):
            continue
        out.append(Job(source="remoteok", company=j.get("company", ""),
                       title=j.get("position", ""),
                       location=j.get("location", "") or "Remote",
                       url=j.get("url", ""), posted_at=j.get("date")))
    return out


def fetch() -> List[Job]:
    return safe_fetch("remoteok",
                      lambda: parse_remoteok(http_get_json("https://remoteok.com/api")))
