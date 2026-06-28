from models import Job, make_id


def test_make_id_stable_and_unique():
    a = make_id("greenhouse", "razorpay", "Backend Engineer", "http://x/1")
    b = make_id("greenhouse", "razorpay", "Backend Engineer", "http://x/1")
    c = make_id("greenhouse", "razorpay", "Backend Engineer", "http://x/2")
    assert a == b and a != c


def test_job_dataclass_defaults():
    j = Job(source="lever", company="cred", title="SDE", location="Bengaluru", url="http://x")
    assert j.posted_at is None and j.salary is None and j.id
