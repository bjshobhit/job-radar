import re
from typing import Dict
from models import Job


def _has_kw(text: str, keywords) -> bool:
    text = (text or "").lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False


def matches(job: Job, cfg: Dict) -> bool:
    title = job.title or ""
    if not _has_kw(title, cfg.get("include_keywords", [])):
        return False
    if _has_kw(title, cfg.get("exclude_keywords", [])):
        return False
    if cfg.get("strict_location"):
        return is_priority(job, cfg)
    return True


def is_priority(job: Job, cfg: Dict) -> bool:
    return _has_kw(job.location or "", cfg.get("priority_locations", []))
