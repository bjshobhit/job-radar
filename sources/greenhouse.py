from typing import List, Dict
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_greenhouse(company: str, data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        out.append(Job(source="greenhouse", company=company,
                       title=j.get("title", ""), location=loc,
                       url=j.get("absolute_url", ""),
                       posted_at=j.get("updated_at"),
                       description=j.get("content") or None))
    return out


def fetch(company: str) -> List[Job]:
    # content=true returns each posting's (HTML-escaped) body inline, at no
    # extra request cost, so we can read years-of-experience requirements.
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    return safe_fetch(f"greenhouse:{company}",
                      lambda: parse_greenhouse(company, http_get_json(url)))
