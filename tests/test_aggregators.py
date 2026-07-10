from sources.remoteok import parse_remoteok
from sources.themuse import parse_themuse
from sources.jobicy import parse_jobicy
from sources.arbeitnow import parse_arbeitnow
from sources.himalayas import parse_himalayas
from sources.smartrecruiters import parse_smartrecruiters
from sources.amazon import parse_amazon
from sources.netflix import parse_netflix
from sources.greenhouse import parse_greenhouse
from sources.lever import parse_lever


def test_parse_remoteok_skips_metadata():
    data = [{"legal": "RemoteOK API notice"},  # first element is metadata
            {"position": "Backend Engineer", "company": "Acme",
             "location": "Remote", "url": "https://remoteok.com/x/1", "date": "2026-06-27"}]
    jobs = parse_remoteok(data)
    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].company == "Acme"
    assert jobs[0].source == "remoteok"


def test_parse_themuse():
    data = {"results": [{"name": "Software Engineer, Backend",
                         "company": {"name": "Acme"},
                         "locations": [{"name": "Bengaluru"}, {"name": "Remote"}],
                         "refs": {"landing_page": "https://themuse.com/jobs/acme/x"},
                         "publication_date": "2026-06-05T18:30:16Z"}]}
    jobs = parse_themuse(data)
    assert jobs[0].title == "Software Engineer, Backend"
    assert jobs[0].company == "Acme"
    assert "Bengaluru" in jobs[0].location
    assert jobs[0].source == "themuse"


def test_parse_jobicy():
    data = {"jobs": [{"jobTitle": "Java Backend Engineer", "companyName": "Binance",
                      "jobGeo": "APAC", "url": "https://jobicy.com/jobs/1-x",
                      "pubDate": "2026-06-27"}]}
    jobs = parse_jobicy(data)
    assert jobs[0].title == "Java Backend Engineer"
    assert jobs[0].company == "Binance"
    assert jobs[0].source == "jobicy"


def test_parse_arbeitnow_marks_remote():
    data = {"data": [{"title": "Backend Developer", "company_name": "Acme",
                      "location": "Berlin", "url": "https://arbeitnow.com/jobs/x-1",
                      "remote": True}]}
    jobs = parse_arbeitnow(data)
    assert jobs[0].title == "Backend Developer"
    assert "remote" in jobs[0].location.lower()
    assert jobs[0].source == "arbeitnow"


def test_parse_himalayas_uses_stable_guid():
    base = {"title": "Backend Engineer", "companyName": "Acme",
            "locationRestrictions": ["India"], "guid": "https://himalayas.app/c/acme/jobs/be"}
    a = parse_himalayas({"jobs": [dict(base, applicationLink="https://himalayas.app/apply?t=AAA")]})
    b = parse_himalayas({"jobs": [dict(base, applicationLink="https://himalayas.app/apply?t=BBB")]})
    assert a[0].id == b[0].id  # dedup keyed on stable guid, not volatile apply link
    assert a[0].source == "himalayas"


def test_parse_smartrecruiters_stable_id():
    data = {"content": [{"id": "744000134517094", "name": "Backend Engineer",
                         "company": {"name": "Wise"},
                         "location": {"fullLocation": "Bengaluru, India"}}]}
    jobs = parse_smartrecruiters("Wise", data)
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].company == "Wise"
    assert "744000134517094" in jobs[0].url
    assert jobs[0].source == "smartrecruiters"
    # stable id derived from sr job id, not the (rebuildable) url alone
    again = parse_smartrecruiters("Wise", data)
    assert jobs[0].id == again[0].id


def test_parse_amazon_builds_url_and_stable_id():
    data = {"jobs": [{"title": "SDE II, Backend", "company_name": "ADCI",
                      "location": "IN, KA, Bengaluru",
                      "job_path": "/en/jobs/10462700/sde-ii-backend",
                      "id_icims": "10462700", "posted_date": "June 30, 2026"}]}
    jobs = parse_amazon(data)
    assert jobs[0].title == "SDE II, Backend"
    assert jobs[0].company == "Amazon"
    assert jobs[0].url == "https://www.amazon.jobs/en/jobs/10462700/sde-ii-backend"
    assert jobs[0].source == "amazon"
    assert parse_amazon(data)[0].id == jobs[0].id  # stable across runs


def test_parse_netflix():
    data = {"positions": [{"name": "Software Engineer 5 - Backend",
                           "locations": ["USA - Remote"],
                           "canonicalPositionUrl": "https://explore.jobs.netflix.net/careers/job/790316090485",
                           "id": 790316090485, "t_create": 1779926400}]}
    jobs = parse_netflix(data)
    assert jobs[0].title == "Software Engineer 5 - Backend"
    assert jobs[0].company == "Netflix"
    assert "Remote" in jobs[0].location
    assert jobs[0].source == "netflix"


def test_parse_greenhouse_includes_description():
    data = {"jobs": [{"title": "Backend Engineer", "location": {"name": "Remote"},
                      "absolute_url": "https://x", "updated_at": "2026-06-30",
                      "content": "&lt;p&gt;You have 5+ years of experience&lt;/p&gt;"}]}
    jobs = parse_greenhouse("acme", data)
    assert "5+ years of experience" in (jobs[0].description or "")


def test_parse_lever_includes_description():
    data = [{"text": "Backend Engineer", "categories": {"location": "Remote"},
             "hostedUrl": "https://x",
             "descriptionPlain": "You bring 2+ years of experience."}]
    jobs = parse_lever("acme", data)
    assert "2+ years of experience" in (jobs[0].description or "")


def test_parse_amazon_includes_qualifications():
    data = {"jobs": [{"title": "SDE II, Backend", "company_name": "ADCI",
                      "location": "IN, KA, Bengaluru",
                      "job_path": "/en/jobs/1/sde-ii", "id_icims": "1",
                      "basic_qualifications":
                          "- 3+ years of non-internship professional software development experience"}]}
    jobs = parse_amazon(data)
    assert "3+ years" in (jobs[0].description or "")
