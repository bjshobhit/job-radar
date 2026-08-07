from typing import Dict, Set


def calculate_ats_score(resume_keywords: Set[str], jd_keywords: Set[str],
                        job_title: str, resume_title: str) -> Dict:
    """
    Calculate ATS compatibility score.

    Scoring:
    - Keyword Match (50%): JD keywords found in resume / total JD keywords
    - Skills Relevance (20%): overlap in skills section
    - Title Alignment (15%): job title words in resume summary/title
    - Format Score (10%): always 100% (we control the template)
    - Action Verbs (5%): always 90% (our bullets use strong verbs)

    Returns dict with score, matched, missing, breakdown.
    """
    if not jd_keywords:
        return {
            "score": 85,
            "matched": list(resume_keywords),
            "missing": [],
            "breakdown": {
                "keyword_match": 85,
                "skills_relevance": 85,
                "title_alignment": 85,
                "format_score": 100,
                "action_verbs": 90,
            }
        }

    matched = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords

    # Keyword match (50% weight)
    keyword_pct = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 85

    # Skills relevance (20% weight) — same as keyword for simplicity
    skills_pct = keyword_pct

    # Title alignment (15% weight)
    title_words = set(job_title.lower().split())
    resume_title_words = set(resume_title.lower().split())
    common_title = title_words & resume_title_words
    title_pct = (len(common_title) / len(title_words)) * 100 if title_words else 80

    # Format (10%) — always good since we generate it
    format_pct = 100

    # Action verbs (5%) — our template uses strong verbs
    verbs_pct = 90

    # Weighted final score
    score = (
        keyword_pct * 0.50 +
        skills_pct * 0.20 +
        title_pct * 0.15 +
        format_pct * 0.10 +
        verbs_pct * 0.05
    )

    return {
        "score": round(min(score, 100)),
        "matched": sorted(matched),
        "missing": sorted(missing),
        "breakdown": {
            "keyword_match": round(keyword_pct),
            "skills_relevance": round(skills_pct),
            "title_alignment": round(title_pct),
            "format_score": format_pct,
            "action_verbs": verbs_pct,
        }
    }
