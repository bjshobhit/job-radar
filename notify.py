import requests
import logging
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



def send_telegram(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text,
                                     "parse_mode": "Markdown",
                                     "disable_web_page_preview": True}, timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        log.error("telegram send failed: %s", e)
        return False
