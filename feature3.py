# feature3.py - Extract required skills from job descriptions using Groq LLM

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_utils import call_llm_for_json

logger = logging.getLogger("skill_gap_analyzer")

MAX_WORKERS = 4  # parallel LLM calls - keeps this fast without hammering the API


def _extract_one(job: dict) -> list:
    """Extract skills from a single job description. Returns [] on failure
    instead of raising, so one bad job doesn't take down the whole batch."""
    description = job.get("description", "")
    title = job.get("title", "unknown")

    if not description:
        return []

    prompt = f"""Extract all technical skills required from this job description.
Return ONLY a JSON array of skill names, nothing else, no markdown formatting.
Example: ["Python", "SQL", "React", "Git"]

Job description:
{description}"""

    try:
        skills = call_llm_for_json(prompt)
        if isinstance(skills, list):
            return [s.strip() for s in skills if isinstance(s, str) and s.strip()]
        return []
    except (RuntimeError, ValueError) as e:
        logger.warning(f"Skill extraction failed for job '{title}': {e}")
        return []


def extract_job_skills(jobs: list) -> list:
    """
    Extract required skills across all job postings. Runs the LLM calls in
    parallel (previously sequential - 8 jobs meant 8 blocking calls in a row)
    and tolerates individual failures instead of crashing the whole batch.
    """
    if not jobs:
        return []

    all_skills = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_extract_one, job): job for job in jobs}
        for future in as_completed(futures):
            all_skills.extend(future.result())

    logger.info(f"Extracted {len(all_skills)} total skill mentions across {len(jobs)} jobs")
    return all_skills


# test
if __name__ == "__main__":
    from feature1 import extract_skills
    from feature2 import search_jobs

    sample = "Python, FastAPI, SQL, React, Git"
    user_skills = extract_skills(sample)
    jobs = search_jobs(user_skills)
    job_skills = extract_job_skills(jobs)
    print("\nAll skills required by market:")
    print(job_skills)
