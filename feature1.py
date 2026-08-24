# feature1.py - Extract skills from user resume using Groq LLM

import logging
from llm_utils import call_llm_for_json

logger = logging.getLogger("skill_gap_analyzer")


def extract_skills(resume_text: str) -> list:
    """
    Extract a clean, de-duplicated list of technical skills from resume text
    (or a plain comma-separated skill list - the prompt handles both).
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text is empty - nothing to extract skills from")

    prompt = f"""Extract all technical skills from this resume text.
Return ONLY a JSON array of skill names, nothing else, no markdown formatting.
Example: ["Python", "SQL", "React", "Git"]

Resume text:
{resume_text}"""

    try:
        skills = call_llm_for_json(prompt)
    except (RuntimeError, ValueError) as e:
        logger.error(f"Skill extraction failed: {e}")
        raise RuntimeError(
            "Couldn't extract skills from the resume text. This is usually a "
            "temporary issue with the AI provider - try again in a moment."
        ) from e

    if not isinstance(skills, list):
        raise RuntimeError("Skill extraction returned an unexpected format (not a list)")

    # clean + de-duplicate while preserving order and original casing of first occurrence
    seen = set()
    cleaned = []
    for skill in skills:
        if not isinstance(skill, str):
            continue
        skill = skill.strip()
        key = skill.lower()
        if skill and key not in seen:
            seen.add(key)
            cleaned.append(skill)

    logger.info(f"Extracted {len(cleaned)} user skills: {cleaned}")
    return cleaned


# test
if __name__ == "__main__":
    sample = "Python, FastAPI, SQL, React, Git, Docker"
    print("Extracted skills:", extract_skills(sample))
