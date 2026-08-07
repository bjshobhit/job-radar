import re
import logging
from typing import Optional, Tuple

log = logging.getLogger("job-radar")

# Patterns to extract experience requirements from job descriptions
EXPERIENCE_PATTERNS = [
    # "3-5 years", "3 - 5 years", "3 to 5 years", "3–5 years"
    r"(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)",
    # "5+ years", "5+ yrs"
    r"(\d+)\+\s*(?:years?|yrs?)",
    # "minimum 3 years", "min 3 years", "at least 3 years"
    r"(?:minimum|min|at\s+least)\s+(\d+)\s*(?:years?|yrs?)",
    # "3 years of experience", "3 yrs experience"
    r"(\d+)\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
    # "experience of 3 years", "experience: 3-5 years"
    r"experience\s*(?:of|:)?\s*(\d+)\s*[-–to]*\s*(\d*)\s*(?:years?|yrs?)",
]


def extract_experience(jd_text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract experience requirement from job description text.
    Returns (min_years, max_years). Either can be None.
    If no experience requirement found, returns (None, None).
    """
    if not jd_text:
        return (None, None)

    text = jd_text.lower()

    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2 and groups[1]:
                return (int(groups[0]), int(groups[1]))
            elif len(groups) >= 1:
                return (int(groups[0]), None)

    return (None, None)


def experience_matches(jd_text: str, my_years: int, max_target: int = 6) -> Tuple[bool, str]:
    """
    Check if job's experience requirement matches user's experience.

    Rules:
    - Job asks >= my_years (up to max_target): MATCH
    - Job asks < my_years (too junior): NO MATCH
    - Job asks > max_target (too senior): NO MATCH
    - No requirement mentioned: MATCH (benefit of doubt)

    Returns (matches: bool, reason: str)
    """
    min_yrs, max_yrs = extract_experience(jd_text)

    if min_yrs is None:
        return (True, "No experience requirement mentioned")

    # Job asks for less than my experience (too junior)
    if max_yrs and max_yrs < my_years:
        return (False, f"Too junior: Job asks {min_yrs}-{max_yrs} yrs (you have {my_years})")

    # Job's minimum is way above our target ceiling
    if min_yrs > max_target:
        return (False, f"Too senior: Job asks {min_yrs}+ yrs (your target max: {max_target})")

    # Job's minimum >= our experience level (good target)
    if min_yrs >= my_years or (max_yrs and max_yrs >= my_years):
        if max_yrs:
            return (True, f"Exp match: Job asks {min_yrs}-{max_yrs} yrs (you have {my_years})")
        return (True, f"Exp match: Job asks {min_yrs}+ yrs (you have {my_years})")

    # Job asks for minimum that's less than our years (we're overqualified but it's fine)
    if min_yrs >= my_years - 1:
        if max_yrs:
            return (True, f"Exp match: Job asks {min_yrs}-{max_yrs} yrs (you have {my_years})")
        return (True, f"Exp match: Job asks {min_yrs}+ yrs (you have {my_years})")

    # Default: too junior
    return (False, f"Too junior: Job asks {min_yrs} yrs max (you have {my_years})")
