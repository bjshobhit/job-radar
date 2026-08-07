from models import Job
from notify import (format_job, format_batch, chunk_messages, send_telegram,
                   format_job_with_ats)
import notify


def test_format_job_priority_star():
    j = Job(source="greenhouse", company="CRED", title="Backend Engineer",
            location="Gurugram", url="http://x", salary="2000000")
    msg = format_job(j, priority=True)
    assert "CRED" in msg and "Backend Engineer" in msg
    assert msg.startswith("\u2b50")  # star
    assert "http://x" in msg


def test_format_job_no_star_when_not_priority():
    j = Job("lever", "B", "Java Backend", "Noida", "http://2")
    msg = format_job(j, priority=False)
    assert not msg.startswith("\u2b50")


def test_format_job_unverified_tag_when_not_priority():
    # Non-star jobs that survive the filter are location-UNKNOWN -> tag them.
    j = Job("lever", "B", "Java Backend", "", "http://2")
    msg = format_job(j, priority=False)
    assert "unverified" in msg
    starred = format_job(j, priority=True)
    assert "unverified" not in starred


def test_format_job_with_ats_unverified_tag():
    j = Job("lever", "B", "Java Backend", "", "http://2")
    msg = format_job_with_ats(j, False, "exp ok", None)
    assert "unverified" in msg
    starred = format_job_with_ats(j, True, "exp ok", None)
    assert "unverified" not in starred


def test_format_batch_joins():
    j1 = Job("greenhouse", "A", "Backend", "Remote", "http://1")
    j2 = Job("lever", "B", "Java Backend", "Noida", "http://2")
    out = format_batch([(j1, True), (j2, False)])
    assert "http://1" in out and "http://2" in out


def test_chunk_messages_respects_limit():
    jobs = [(Job("s", f"C{i}", "Backend Engineer", "Remote", f"http://x/{i}"), False)
            for i in range(200)]
    msgs = chunk_messages(jobs, limit=3800)
    assert len(msgs) > 1
    assert all(len(m) <= 4096 for m in msgs)
    # every job url appears exactly once across all chunks
    joined = "\n".join(msgs)
    for i in range(200):
        assert f"http://x/{i}" in joined


def test_chunk_messages_single_when_small():
    jobs = [(Job("s", "A", "Backend", "Remote", "http://1"), True)]
    assert len(chunk_messages(jobs)) == 1


class _Resp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def test_send_telegram_retries_on_429_then_succeeds(monkeypatch):
    calls = {"n": 0}

    def fake_post(url, json=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return _Resp(429, {"parameters": {"retry_after": 1}})
        return _Resp(200)

    monkeypatch.setattr(notify.requests, "post", fake_post)
    monkeypatch.setattr(notify.time, "sleep", lambda s: None)
    assert send_telegram("tok", "chat", "hi") is True
    assert calls["n"] == 2


def test_send_telegram_gives_up_after_retries(monkeypatch):
    monkeypatch.setattr(notify.requests, "post",
                        lambda *a, **k: _Resp(429, {"parameters": {"retry_after": 1}}))
    monkeypatch.setattr(notify.time, "sleep", lambda s: None)
    assert send_telegram("tok", "chat", "hi", max_retries=3) is False


