from typing import List, Dict
from models import Job, make_id
from sources.base import http_get_json, safe_fetch


def parse_smartrecruiters(company: str, data: Dict) -> List[Job]:
    out = []
    for j in data.get("content", []):
        loc = j.get("location") or {}
        locstr = loc.get("fullLocation") or ", ".join(
            x for x in [loc.get("city", ""), loc.get("country", "")] if x)
        jid = j.get("id", "")
        title = j.get("name", "")
        url = f"https://jobs.smartrecruiters.com/{company}/{jid}" if jid else ""
        job = Job(source="smartrecruiters",
                  company=(j.get("company") or {}).get("name", company),
                  title=title, location=locstr, url=url,
                  posted_at=j.get("releasedDate"))
        if jid:
            job.id = make_id("smartrecruiters", company, title, f"sr-id:{jid}")
        out.append(job)
    return out


def fetch(company: str) -> List[Job]:
    url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
    return safe_fetch(
        f"smartrecruiters:{company}",
        lambda: parse_smartrecruiters(company, http_get_json(url, {"limit": 100})))
