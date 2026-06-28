from typing import List, Dict, Optional
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_themuse(data: Dict) -> List[Job]:
    out = []
    for j in data.get("results", []):
        locs = ", ".join(l.get("name", "") for l in (j.get("locations") or []))
        url = (j.get("refs") or {}).get("landing_page", "")
        out.append(Job(source="themuse",
                       company=(j.get("company") or {}).get("name", ""),
                       title=j.get("name", ""), location=locs, url=url,
                       posted_at=j.get("publication_date")))
    return out


def fetch(pages: int = 3, categories: Optional[List[str]] = None,
          locations: Optional[List[str]] = None) -> List[Job]:
    cats = categories or ["Software Engineering"]
    jobs: List[Job] = []
    for cat in cats:
        for p in range(1, pages + 1):
            params = {"category": cat, "page": p}
            if locations:
                params["location"] = locations  # requests repeats key per item
            jobs += safe_fetch(
                f"themuse:{cat}:{p}",
                lambda pr=params: parse_themuse(
                    http_get_json("https://www.themuse.com/api/public/jobs", pr)))
    return jobs
