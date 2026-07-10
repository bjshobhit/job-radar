from typing import List, Dict, Optional
from models import Job, make_id
from sources.base import http_get_json, safe_fetch


def parse_amazon(data: Dict) -> List[Job]:
    out = []
    for j in data.get("jobs", []):
        path = j.get("job_path", "")
        url = f"https://www.amazon.jobs{path}" if path else ""
        jid = j.get("id_icims", "")
        title = j.get("title", "")
        desc = j.get("basic_qualifications") or j.get("description") or None
        job = Job(source="amazon", company="Amazon", title=title,
                  location=j.get("location", "") or j.get("city", ""),
                  url=url, posted_at=j.get("posted_date"),
                  description=desc)
        if jid:
            job.id = make_id("amazon", "", title, f"amzn-id:{jid}")
        out.append(job)
    return out


def fetch(queries: Optional[List[str]] = None) -> List[Job]:
    queries = queries or ["backend engineer"]
    jobs: List[Job] = []
    for q in queries:
        params = {"base_query": q, "result_limit": 100, "sort": "recent"}
        jobs += safe_fetch(
            f"amazon:{q}",
            lambda p=params: parse_amazon(http_get_json(
                "https://www.amazon.jobs/en/search.json", p)))
    return jobs
