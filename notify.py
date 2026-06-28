import requests
import logging
import time
from typing import List, Tuple
from models import Job

log = logging.getLogger("job-radar")


def format_job(job: Job, priority: bool) -> str:
    star = "\u2b50 " if priority else ""
    lines = [f"{star}*{job.company}* — {job.title}",
             f"\U0001F4CD {job.location or 'N/A'}  ·  _{job.source}_"]
    if job.salary:
        lines.append(f"\U0001F4B0 {job.salary}")
    lines.append(f"\U0001F517 {job.url}")
    return "\n".join(lines)


def format_batch(items: List[Tuple[Job, bool]]) -> str:
    blocks = [format_job(j, p) for j, p in items]
    header = f"\U0001F6A8 {len(items)} new backend job(s):\n\n"
    return header + "\n\n".join(blocks)


def chunk_messages(items: List[Tuple[Job, bool]], limit: int = 3800) -> List[str]:
    """Split jobs into Telegram-safe messages (<4096 chars each)."""
    messages: List[str] = []
    current: List[str] = []
    size = 0
    for job, priority in items:
        block = format_job(job, priority)
        add = len(block) + 2
        if current and size + add > limit:
            messages.append("\n\n".join(current))
            current, size = [], 0
        current.append(block)
        size += add
    if current:
        messages.append("\n\n".join(current))
    return messages



def send_telegram(token: str, chat_id: str, text: str, max_retries: int = 4) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text,
               "parse_mode": "Markdown",
               "disable_web_page_preview": True}
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 429:
                # Telegram rate limit: honor retry_after and try again.
                retry_after = 1
                try:
                    retry_after = int(r.json()["parameters"]["retry_after"])
                except Exception:
                    pass
                wait = retry_after + 1
                log.warning("telegram 429, retrying in %ss (attempt %d/%d)",
                            wait, attempt + 1, max_retries)
                time.sleep(wait)
                continue
            if r.status_code >= 400:
                # Surface Telegram's actual reason (e.g. "chat not found",
                # "can't parse entities") instead of a bare HTTP code.
                log.error("telegram %s: %s", r.status_code, r.text)
                return False
            return True
        except Exception as e:
            log.error("telegram send failed (attempt %d/%d): %s",
                      attempt + 1, max_retries, e)
            time.sleep(2 * (attempt + 1))
    return False

