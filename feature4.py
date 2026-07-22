# Feature 4 - Find skill gap between user skills and market skills

def find_gap(user_skills, job_skills):
    # convert both lists to lowercase sets for comparison
    user_set = set(skill.lower() for skill in user_skills)
    market_set = set(skill.lower() for skill in job_skills)

    # skills user already has
    matched = user_set.intersection(market_set)

    # skills user is missing
    gap = market_set.difference(user_set)

    # score = how many market skills user already has
    if len(market_set) == 0:
        score = 0
    else:
        score = round((len(matched) / len(market_set)) * 100, 2)

    return {
        "matched_skills": list(matched),
        "gap_skills": list(gap),
        "score": score,
        "total_market_skills": len(market_set),
        "total_user_skills": len(user_set)
    }
