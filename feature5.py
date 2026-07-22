# Feature 5 - Recommendations for missing skills

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("groq_key"))

def get_recommendations(gap_skills):
    if not gap_skills:
        return []

    # take top 5 missing skills only
    top_gaps = gap_skills[:5]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""For each skill in this list: {top_gaps}
                Return a JSON array where each item has:
                - skill: skill name
                - why: one line why this skill matters for getting hired
                - learn_at: best free resource to learn it (youtube channel or website name only)
                
                Return only JSON array. Nothing else.
                Example: [{{"skill": "React", "why": "Most in-demand frontend framework", "learn_at": "react.dev official docs"}}]"""
            }
        ]
    )

    result = response.choices[0].message.content
    recommendations = json.loads(result)
    return recommendations
