import os
import sys
import time
import logging
import yaml
from typing import List, Tuple, Set
from models import Job
from filters import matches, is_priority
from dedup import load_seen, save_seen, partition_new
from notify import chunk_messages, send_telegram
from sources import greenhouse, lever, ashby, adzuna, remotive

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("job-radar")
HERE = os.path.dirname(os.path.abspath(__file__))


def collect(cfg) -> List[Job]:
    jobs: List[Job] = []
    watchlist = cfg.get("watchlist", {}) or {}
    for c in watchlist.get("greenhouse", []) or []:
        jobs += greenhouse.fetch(c)
    for c in watchlist.get("lever", []) or []:
        jobs += lever.fetch(c)
    for c in watchlist.get("ashby", []) or []:
        jobs += ashby.fetch(c)
    discovery = cfg.get("discovery", {}) or {}
    if discovery.get("enabled"):
        jobs += adzuna.fetch(os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY"),
                             discovery.get("queries", ["backend"]))
        jobs += remotive.fetch(discovery.get("remotive_search", "backend"))
    return jobs


def select_new(jobs: List[Job], cfg, seen: Set[str]) -> List[Tuple[Job, bool]]:
    fresh = partition_new([j for j in jobs if matches(j, cfg)], seen)
    return [(j, is_priority(j, cfg)) for j in fresh]


def main():
    dry = "--dry-run" in sys.argv
    seed = "--seed" in sys.argv
    with open(os.path.join(HERE, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    seen_path = os.path.join(HERE, "state", "seen.json")
    seen = load_seen(seen_path)
    jobs = collect(cfg)
    log.info("collected %d raw jobs", len(jobs))
    selected = select_new(jobs, cfg, seen)
    log.info("%d new matching jobs", len(selected))

    # Seed mode: mark everything currently open as seen WITHOUT alerting,
    # so future runs only notify on genuinely new postings.
    if seed:
        for j, _ in selected:
            seen.add(j.id)
        save_seen(seen_path, seen)
        log.info("seeded %d jobs as seen (no alerts sent)", len(selected))
        return

    if not selected:
        return

    messages = chunk_messages(selected)
    if dry:
        for m in messages:
            print(m)
            print("\n---\n")
        return

    token, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    header = f"\U0001F6A8 {len(selected)} new backend job(s):"
    all_sent = send_telegram(token, chat, header)
    for m in messages:
        time.sleep(1)  # stay under Telegram's per-chat send rate
        all_sent = send_telegram(token, chat, m) and all_sent
    # Only mark as seen if delivery succeeded, so failures retry next run.
    if all_sent:
        for j, _ in selected:
            seen.add(j.id)
        save_seen(seen_path, seen)



if __name__ == "__main__":
    main()
