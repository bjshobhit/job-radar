import requests
import logging
from typing import List
from models import Job

log = logging.getLogger("job-radar")
HEADERS = {"User-Agent": "job-radar/1.0"}


def http_get_json(url: str, params=None, timeout: int = 15):
    r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json()


def safe_fetch(name: str, fn) -> List[Job]:
    try:
        return fn()
    except Exception as e:  # isolation: one source never kills the run
        log.warning("source %s failed: %s", name, e)
        return []
