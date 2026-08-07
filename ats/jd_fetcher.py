"""
Fetches full job descriptions from ATS detail endpoints where available.
"""
import logging
import re
from typing import Optional
from models import Job
from sources.base import http_get_json, HEADERS
import requests

log = logging.getLogger("job-radar")

# Greenhouse detail API
GREENHOUSE_DETAIL = "https://boards-api.greenhouse.io/v1/boards/{}/jobs/{}"


def fetch_job_description(job: Job) -> Optional[str]:
    """
    Attempt to fetch the full job description text.
    Returns plain text (HTML stripped) or None if unavailable.
    """
    try:
        if job.source == "greenhouse":
            return _fetch_greenhouse_jd(job)
        elif job.source == "lever":
            return _fetch_lever_jd(job)
        elif job.source == "ashby":
            return _fetch_ashby_jd(job)
        else:
            # For discovery sources, try fetching the job URL page
            return _fetch_page_text(job.url)
    except Exception as e:
        log.debug("could not fetch JD for %s: %s", job.url, e)
        return None


def _fetch_greenhouse_jd(job: Job) -> Optional[str]:
    """Greenhouse has job detail endpoint with content field."""
    # Extract job ID from URL: .../jobs/12345 or .../jobs/12345?...
    match = re.search(r"/jobs/(\d+)", job.url)
    if not match:
        return None
    job_id = match.group(1)
    url = GREENHOUSE_DETAIL.format(job.company, job_id)
    data = http_get_json(url)
    content = data.get("content", "")
    return _strip_html(content)


def _fetch_lever_jd(job: Job) -> Optional[str]:
    """Lever job URLs are the detail page; fetch and extract."""
    return _fetch_page_text(job.url)


def _fetch_ashby_jd(job: Job) -> Optional[str]:
    """Ashby job URLs contain the description."""
    return _fetch_page_text(job.url)


def _fetch_page_text(url: str) -> Optional[str]:
    """Fetch a URL and extract visible text (basic HTML stripping)."""
    if not url:
        return None
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        return _strip_html(r.text)
    except Exception:
        return None


def _strip_html(html: str) -> str:
    """Remove HTML tags and return plain text."""
    if not html:
        return ""
    # Remove script and style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
