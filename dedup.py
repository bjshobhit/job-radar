import json
import os
from typing import List, Set
from models import Job


def load_seen(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()


def save_seen(path: str, seen: Set[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(sorted(seen), f, indent=0)


def partition_new(jobs: List[Job], seen: Set[str]) -> List[Job]:
    out, ids = [], set()
    for j in jobs:
        if j.id not in seen and j.id not in ids:
            out.append(j)
            ids.add(j.id)
    return out
