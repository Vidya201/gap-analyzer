# feature4.py - Find skill gap between user skills and market skills

import re

# Common aliases that would otherwise show up as separate "different" skills
# (e.g. market wants "JS" and "JavaScript" listed as two gaps instead of one).
# This is intentionally small and hand-picked rather than a full taxonomy -
# it targets the specific near-duplicate cases called out in the README's
# known limitations, not an exhaustive skill ontology.
ALIASES = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "py": "python",
    "postgres": "postgresql",
    "ml": "machine learning",
    "k8s": "kubernetes",
    "tf": "tensorflow",
}


def _normalize(skill: str) -> str:
    """Lowercase, strip punctuation/whitespace noise, and resolve known aliases
    so 'React.js' and 'ReactJS' collapse to the same key."""
    key = skill.strip().lower()
    key = re.sub(r"[^a-z0-9+.# ]", "", key)  # keep tokens like c++, c#, .net readable
    key = key.strip()
    return ALIASES.get(key, key)


def find_gap(user_skills: list, job_skills: list) -> dict:
    """
    Compare the user's skills against what the market is asking for.
    Returns matched skills, gap skills (with original casing preserved for
    display), a 0-100 match score, and counts.
    """
    # map normalized-key -> best display form (first one seen, title-cased)
    user_map = {}
    for skill in user_skills:
        user_map.setdefault(_normalize(skill), skill)

    market_map = {}
    for skill in job_skills:
        market_map.setdefault(_normalize(skill), skill)

    user_keys = set(user_map.keys())
    market_keys = set(market_map.keys())

    matched_keys = user_keys.intersection(market_keys)
    gap_keys = market_keys.difference(user_keys)

    matched = [market_map[k] for k in matched_keys]
    gap = [market_map[k] for k in gap_keys]

    score = round((len(matched_keys) / len(market_keys)) * 100, 2) if market_keys else 0

    return {
        "matched_skills": sorted(matched, key=str.lower),
        "gap_skills": sorted(gap, key=str.lower),
        "score": score,
        "total_market_skills": len(market_keys),
        "total_user_skills": len(user_keys),
    }


# test
if __name__ == "__main__":
    user = ["Python", "SQL", "React.js", "Git"]
    market = ["Python", "JS", "Docker", "Kubernetes", "SQL", "AWS"]
    print(find_gap(user, market))
