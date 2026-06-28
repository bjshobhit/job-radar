from typing import List, Dict, Optional
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_jobicy(data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        out.append(Job(source="jobicy", company=j.get("companyName", ""),
                       title=j.get("jobTitle", ""),
                       location=j.get("jobGeo", "") or "Remote",
                       url=j.get("url", ""), posted_at=j.get("pubDate")))
    return out


def fetch(tags: Optional[List[str]] = None) -> List[Job]:
    tags = tags or ["backend"]
    jobs: List[Job] = []
    for t in tags:
        jobs += safe_fetch(
            f"jobicy:{t}",
            lambda tt=t: parse_jobicy(http_get_json(
                "https://jobicy.com/api/v2/remote-jobs", {"count": 50, "tag": tt})))
    return jobs
