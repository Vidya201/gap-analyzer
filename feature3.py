# feature3.py - Extract required skills from job descriptions using Groq LLM

import os
import json
from groq import Groq
from dotenv import load_dotenv
from feature1 import extract_skills
from feature2 import search_jobs

load_dotenv()

client = Groq(api_key=os.getenv("groq_key"))

def extract_job_skills(jobs):
    all_skills = []

    for job in jobs[:3]:
        job_description = job["description"]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract all technical skills required from this job description.
                    Return ONLY a JSON array of skills. Nothing else.
                    Example: ["Python", "SQL", "React", "Git"]
                    
                    Job description:
                    {job_description}"""
                }
            ]
        )

        result = response.choices[0].message.content
        skills = json.loads(result)
        all_skills.extend(skills)

    return all_skills


# test
if __name__ == "__main__":
    with open("VIDYA M.txt", "r", encoding="utf8") as f:
        resume_text = f.read()
    user_skills = extract_skills(resume_text)
    jobs = search_jobs(user_skills)
    job_skills = extract_job_skills(jobs)
    print("\nAll skills required by market:")
    print(job_skills)
