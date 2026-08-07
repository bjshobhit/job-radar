import re
from typing import Dict, Optional
from models import Job
from location import location_ok


def _has_kw(text: str, keywords) -> bool:
    text = (text or "").lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False


# Matches a YOE token like "5 years", "5+ yrs", "3-5 years", "3 to 5 years".
# Group 1 is the lower bound (the minimum the job actually requires).
_YEARS_RE = re.compile(
    r"(\d{1,2})\s*\+?\s*(?:(?:-|–|to)\s*\d{1,2}\s*\+?\s*)?(?:years?|yrs?)",
    re.IGNORECASE,
)


def _min_required_years(text: str) -> Optional[int]:
    """Return the smallest YOE requirement mentioned in an experience context.

    Only numbers followed shortly by the word "experience" count, so blurbs
    like "12 years of history" are ignored. Taking the minimum across matches
    avoids over-filtering on "preferred" (nice-to-have) higher bars.
    """
    text = (text or "").lower()
    mins = []
    for m in _YEARS_RE.finditer(text):
        window = text[m.end():m.end() + 40]
        if "experien" in window:
            mins.append(int(m.group(1)))
    return min(mins) if mins else None


def experience_ok(job: Job, cfg: Dict) -> bool:
    """True unless the job requires more YOE than the configured ceiling.

    Feature is off when ``max_years_experience`` is absent. Jobs with no
    detectable YOE requirement are kept (don't over-filter).
    """
    ceiling = cfg.get("max_years_experience")
    if ceiling is None:
        return True
    text = f"{job.title or ''} {job.description or ''}"
    required = _min_required_years(text)
    if required is None:
        return True
    return required <= ceiling


def matches(job: Job, cfg: Dict) -> bool:
    title = job.title or ""
    if not _has_kw(title, cfg.get("include_keywords", [])):
        return False
    if _has_kw(title, cfg.get("exclude_keywords", [])):
        return False
    if not experience_ok(job, cfg):
        return False
    if not location_ok(job, cfg):
        return False
    return True
