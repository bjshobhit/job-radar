import hashlib
from dataclasses import dataclass, field
from typing import Optional


def make_id(source: str, company: str, title: str, url: str) -> str:
    raw = f"{source}|{company}|{title}|{url}".lower()
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class Job:
    source: str
    company: str
    title: str
    location: str
    url: str
    posted_at: Optional[str] = None
    salary: Optional[str] = None
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = make_id(self.source, self.company, self.title, self.url)
