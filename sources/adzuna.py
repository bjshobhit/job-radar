from typing import List, Dict, Optional
from models import Job
from sources.base import http_get_json, safe_fetch


def parse_adzuna(data: Dict) -> List[Job]:
    out = []
    for j in data.get("results", []):
        smin = j.get("salary_min")
        salary = str(int(smin)) if smin else None
        out.append(Job(source="adzuna",
                       company=(j.get("company") or {}).get("display_name", ""),
                       title=j.get("title", ""),
                       location=(j.get("location") or {}).get("display_name", ""),
                       url=j.get("redirect_url", ""),
                       posted_at=j.get("created"), salary=salary))
    return out


def fetch(app_id: Optional[str], app_key: Optional[str], queries, country="in") -> List[Job]:
    if not app_id or not app_key:
        return []
    jobs: List[Job] = []
    for q in queries:
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {"app_id": app_id, "app_key": app_key, "what": q,
                  "results_per_page": 50, "max_days_old": 3, "sort_by": "date"}
        jobs += safe_fetch(f"adzuna:{q}",
                           lambda u=url, p=params: parse_adzuna(http_get_json(u, p)))
    return jobs
