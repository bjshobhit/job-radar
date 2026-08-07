import re
from typing import Dict
from models import Job

# Classification constants.
INDIA = "INDIA"
REMOTE_ELIGIBLE = "REMOTE_ELIGIBLE"
REMOTE_REGION_LOCKED = "REMOTE_REGION_LOCKED"
OTHER_COUNTRY = "OTHER_COUNTRY"
UNKNOWN = "UNKNOWN"


def _has_token(text: str, tokens) -> bool:
    """Word-boundary match so bare tokens like "us" hit "Remote - US" but not
    "status"/"focus". Multi-word tokens ("new york") work via escaped spaces."""
    text = (text or "").lower()
    for tok in tokens or []:
        pattern = r"\b" + re.escape(tok.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False


def classify_location(job: Job, cfg: Dict) -> str:
    loc_cfg = cfg.get("location", {})
    india = loc_cfg.get("india_tokens", [])
    remote = loc_cfg.get("remote_tokens", [])
    global_ = loc_cfg.get("global_tokens", [])
    blocked = loc_cfg.get("blocked_regions", [])

    loc = job.location or ""
    has_india = _has_token(loc, india)
    has_remote = _has_token(loc, remote)
    has_global = _has_token(loc, global_)
    has_blocked = _has_token(loc, blocked)

    if has_remote:
        if has_india or has_global:
            return REMOTE_ELIGIBLE
        if has_blocked:
            return REMOTE_REGION_LOCKED
        return UNKNOWN

    # Non-remote path. India always wins over a blocked region.
    if has_india:
        return INDIA
    if has_blocked:
        return OTHER_COUNTRY

    # Weak, keep-biased fallback: only ever upgrades to India from the JD.
    if _has_token(job.description or "", india):
        return INDIA
    return UNKNOWN


def location_ok(job: Job, cfg: Dict) -> bool:
    return classify_location(job, cfg) not in (REMOTE_REGION_LOCKED, OTHER_COUNTRY)


def is_india_star(cls: str) -> bool:
    return cls in (INDIA, REMOTE_ELIGIBLE)
