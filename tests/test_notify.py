from models import Job
from notify import format_job, format_batch, chunk_messages


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

