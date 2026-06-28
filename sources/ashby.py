from typing import List, Dict
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_ashby(company: str, data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        out.append(Job(source="ashby", company=company,
                       title=j.get("title", ""),
                       location=j.get("location", ""),
                       url=j.get("jobUrl", "")))
    return out


def fetch(company: str) -> List[Job]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{company}"
    return safe_fetch(f"ashby:{company}",
                      lambda: parse_ashby(company, http_get_json(url)))
