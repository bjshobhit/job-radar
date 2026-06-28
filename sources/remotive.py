from typing import List, Dict
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_remotive(data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        out.append(Job(source="remotive", company=j.get("company_name", ""),
                       title=j.get("title", ""),
                       location=j.get("candidate_required_location", ""),
                       url=j.get("url", "")))
    return out


def fetch(search="backend") -> List[Job]:
    url = "https://remotive.com/api/remote-jobs"
    return safe_fetch("remotive",
                      lambda: parse_remotive(http_get_json(url, {"search": search})))
