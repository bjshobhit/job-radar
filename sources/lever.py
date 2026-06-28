from typing import List
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_lever(company: str, data: List) -> List[Job]:
    out = []
    for j in data:
        loc = (j.get("categories") or {}).get("location", "")
        out.append(Job(source="lever", company=company,
                       title=j.get("text", ""), location=loc,
                       url=j.get("hostedUrl", "")))
    return out


def fetch(company: str) -> List[Job]:
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    return safe_fetch(f"lever:{company}",
                      lambda: parse_lever(company, http_get_json(url)))
