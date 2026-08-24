# feature5.py - Recommendations for missing skills

import logging
from llm_utils import call_llm_for_json

logger = logging.getLogger("skill_gap_analyzer")


def get_recommendations(gap_skills: list) -> list:
    """
    Get a short "why it matters + where to learn it free" recommendation for
    each of the user's top missing skills. Degrades gracefully to an empty
    list on failure rather than crashing the whole /analyze response - a
    missing recommendations panel is far better than a 500 error when the
    rest of the analysis (score, matched/gap skills) already succeeded.
    """
    if not gap_skills:
        return []

    top_gaps = gap_skills[:5]

    prompt = f"""For each skill in this list: {top_gaps}
Return a JSON array where each item has:
- skill: skill name
- why: one line on why this skill matters for getting hired
- learn_at: best free resource to learn it (a specific youtube channel, docs site, or course name)

Return ONLY the JSON array, nothing else, no markdown formatting.
Example: [{{"skill": "React", "why": "Most in-demand frontend framework", "learn_at": "react.dev official docs"}}]"""

    try:
        recommendations = call_llm_for_json(prompt)
    except (RuntimeError, ValueError) as e:
        logger.warning(f"Recommendation generation failed, returning empty list: {e}")
        return []

    if not isinstance(recommendations, list):
        return []

    return recommendations


# test
if __name__ == "__main__":
    print(get_recommendations(["Kubernetes", "GraphQL", "Terraform"]))
