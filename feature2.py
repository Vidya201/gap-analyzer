# feature2.py - Search real jobs based on user skills using the Remotive API

import json
import logging
import requests

logger = logging.getLogger("skill_gap_analyzer")

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
REQUEST_TIMEOUT = 10


def _fetch(search_term: str) -> list:
    """One search request to Remotive. Returns [] on any failure instead of raising,
    so the caller can try the next skill in the fallback chain."""
    try:
        response = requests.get(
            REMOTIVE_URL,
            params={"category": "software-dev", "search": search_term, "limit": 20},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("jobs", [])
    except (requests.RequestException, json.JSONDecodeError) as e:
        logger.warning(f"Remotive search failed for '{search_term}': {e}")
        return []


def search_jobs(skills) -> list:
    """
    Search Remotive for jobs matching the user's skills. Tries the top 3 skills
    in order (instead of only the single strongest one) so a niche/rare top
    skill doesn't return zero jobs when a nearby skill would have worked -
    this directly addresses the "niche skills return few/no jobs" limitation.
    """
    if isinstance(skills, str):
        skills = json.loads(skills)

    if not skills:
        skills = ["software"]

    candidates = skills[:3]
    jobs = []
    used_term = None

    for term in candidates:
        logger.info(f"Searching Remotive for: {term}")
        jobs = _fetch(term)
        if jobs:
            used_term = term
            break

    if not jobs:
        logger.info("No jobs found for top 3 skills; falling back to generic 'software' search")
        jobs = _fetch("software")
        used_term = "software"

    # local relevance filter: keep jobs that actually mention at least one
    # of the user's top 5 skills in the title or description
    skill_terms = [s.lower() for s in skills[:5]]
    relevant_jobs = [
        job for job in jobs
        if any(
            term in (job.get("title", "") + " " + job.get("description", "")).lower()
            for term in skill_terms
        )
    ]

    final_jobs = relevant_jobs if relevant_jobs else jobs
    final_jobs = final_jobs[:8]

    logger.info(
        f"Found {len(final_jobs)} relevant jobs (from {len(jobs)} total, "
        f"search term: '{used_term}')"
    )
    return final_jobs


# test
if __name__ == "__main__":
    from feature1 import extract_skills
    sample = "Python, FastAPI, SQL, React, Git"
    skills = extract_skills(sample)
    jobs = search_jobs(skills)
    for job in jobs:
        print(job["title"], "-", job["company_name"])
