import os

import yaml

from ats.keyword_extractor import (
    extract_keywords,
    get_resume_keywords,
    KEYWORD_BANK,
)
from ats.jd_parser import extract_experience, experience_matches
from ats.scorer import calculate_ats_score
from ats.optimizer import optimize_resume, _categorize_keyword

BASE_YAML = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resume",
    "base.yaml",
)

# Categories that must exist in resume/base.yaml (and be produced by the optimizer)
BASE_CATEGORIES = {
    "programming_languages",
    "frameworks",
    "databases",
    "distributed_systems",
    "tools",
    "methodologies",
}


def load_base():
    with open(BASE_YAML) as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------------------- #
# keyword_extractor
# --------------------------------------------------------------------------- #

def test_extract_keywords_empty():
    assert extract_keywords("") == set()
    assert extract_keywords(None) == set()


def test_extract_keywords_basic_backend():
    jd = (
        "We are looking for a backend engineer with strong Java and "
        "Spring Boot experience. Must know Kafka, PostgreSQL and Kubernetes."
    )
    kws = extract_keywords(jd)
    assert "java" in kws
    assert "spring boot" in kws
    assert "kafka" in kws
    assert "postgresql" in kws
    assert "kubernetes" in kws


def test_extract_keywords_short_token_word_boundary():
    # "go" must match as a standalone word...
    assert "go" in extract_keywords("Experience with Go and gRPC required.")
    # ...but must NOT match inside a larger word like "google" or "goods".
    assert "go" not in extract_keywords("We sell goods to google customers.")


def test_extract_keywords_short_token_aws_s3():
    jd = "Deep AWS experience: S3, EC2, and Lambda."
    kws = extract_keywords(jd)
    assert "aws" in kws
    assert "s3" in kws
    assert "ec2" in kws
    # 's3' should not be spuriously matched inside unrelated text
    assert "s3" not in extract_keywords("The bus3 route was delayed.")


def test_extract_keywords_case_insensitive():
    assert "kafka" in extract_keywords("KAFKA streaming pipeline")


def test_get_resume_keywords_from_base():
    resume = load_base()
    kws = get_resume_keywords(resume)
    # base.yaml clearly mentions these
    assert "java" in kws
    assert "spring boot" in kws
    assert "microservices" in kws
    assert kws.issubset(KEYWORD_BANK)


# --------------------------------------------------------------------------- #
# jd_parser
# --------------------------------------------------------------------------- #

def test_extract_experience_range():
    assert extract_experience("3-5 years of experience") == (3, 5)


def test_extract_experience_plus():
    assert extract_experience("5+ years required") == (5, None)


def test_extract_experience_minimum():
    assert extract_experience("minimum 3 years of experience") == (3, None)


def test_extract_experience_none():
    assert extract_experience("great team, fun culture") == (None, None)


def test_experience_matches_no_requirement():
    ok, reason = experience_matches("no years mentioned here", 2)
    assert ok is True
    assert "No experience requirement" in reason


def test_experience_matches_too_senior():
    # my_years=2, max_target=6 -> a 10+ job is too senior
    ok, reason = experience_matches("10+ years of experience", 2, max_target=6)
    assert ok is False
    assert "Too senior" in reason


def test_experience_matches_good_target():
    # 3-5 yrs with 2 yrs experience -> match (job min >= my_years)
    ok, reason = experience_matches("3-5 years of experience", 2, max_target=6)
    assert ok is True
    assert "Exp match" in reason


def test_experience_matches_too_junior():
    # Job caps at 1 year, I have 2 -> too junior
    ok, reason = experience_matches("1-1 years of experience", 2, max_target=6)
    assert ok is False
    assert "Too junior" in reason


# --------------------------------------------------------------------------- #
# scorer
# --------------------------------------------------------------------------- #

def test_score_empty_jd_defaults_to_85():
    result = calculate_ats_score({"java", "python"}, set(),
                                 "Backend Engineer", "Backend Software Engineer")
    assert result["score"] == 85
    assert result["missing"] == []


def test_score_full_match_high():
    jd = {"java", "spring boot", "kafka"}
    resume = {"java", "spring boot", "kafka"}
    result = calculate_ats_score(resume, jd,
                                 "Backend Engineer", "Backend Engineer")
    # keyword 50% + skills 20% at 100, title 15% at 100, format 10, verbs 5
    assert result["score"] >= 95
    assert set(result["matched"]) == jd
    assert result["missing"] == []


def test_score_partial_match_reports_missing():
    jd = {"java", "spring boot", "kafka", "redis"}
    resume = {"java", "spring boot"}
    result = calculate_ats_score(resume, jd,
                                 "Backend Engineer", "Backend Engineer")
    assert "kafka" in result["missing"]
    assert "redis" in result["missing"]
    assert 0 < result["score"] < 100


# --------------------------------------------------------------------------- #
# optimizer  (inject-all + categorization)
# --------------------------------------------------------------------------- #

def test_optimizer_injects_all_jd_keywords():
    base = load_base()
    jd_keywords = {"rust", "cassandra", "grpc", "terraform", "kanban"}
    optimized = optimize_resume(base, jd_keywords, "Backend Engineer")

    # Flatten all optimized skills (lowercased) and ensure every JD keyword landed
    all_skills = set()
    for skill_list in optimized["skills"].values():
        for s in skill_list:
            all_skills.add(s.lower())

    # gRPC -> "gRPC", Terraform -> "Terraform" etc.; compare by presence of the
    # keyword's canonical lowercase form somewhere in the skills.
    for kw in jd_keywords:
        assert any(kw in s or kw == s for s in all_skills), (
            f"JD keyword '{kw}' was not injected into optimized skills"
        )


def test_optimizer_does_not_mutate_base():
    base = load_base()
    original_langs = list(base["skills"]["programming_languages"])
    optimize_resume(base, {"rust", "scala"}, "Backend Engineer")
    assert base["skills"]["programming_languages"] == original_langs


def test_optimizer_categories_within_base_set():
    base = load_base()
    jd_keywords = {"rust", "cassandra", "grpc", "terraform", "kanban",
                   "unknown-tech-token"}
    optimized = optimize_resume(base, jd_keywords, "Backend Engineer")
    # optimizer must only ever produce the 6 known categories
    assert set(optimized["skills"].keys()).issubset(BASE_CATEGORIES)


def test_optimizer_summary_backend_wording():
    base = load_base()
    optimized = optimize_resume(base, {"java", "kafka"}, "Backend Engineer")
    assert optimized["summary"].startswith("Backend Software Engineer with 2+ years")


def test_categorize_keyword_buckets():
    assert _categorize_keyword("java") == "programming_languages"
    assert _categorize_keyword("spring boot") == "frameworks"
    assert _categorize_keyword("cassandra") == "databases"
    assert _categorize_keyword("kafka") == "distributed_systems"
    assert _categorize_keyword("terraform") == "tools"
    assert _categorize_keyword("agile") == "methodologies"
    # unknown token defaults to 'tools'
    assert _categorize_keyword("some-unknown-token") == "tools"
