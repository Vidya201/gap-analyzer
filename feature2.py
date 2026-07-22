# feature2.py - Search real jobs based on user skills using Remotive API

import os
import json
import requests
from dotenv import load_dotenv
from feature1 import extract_skills

load_dotenv()

def search_jobs(skills):
    # if skills came as JSON string, convert to list first
    if isinstance(skills, str):
        skills = json.loads(skills)

    # build search query from top 3 skills
    query = " ".join(skills[:3]) + " developer"
    print("Searching for:", query)

    try:
        response = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": query, "limit": 5},
            timeout=10
        )
        jobs = response.json()["jobs"]
        print(f"Found {len(jobs)} jobs")
        for job in jobs:
            print(job["title"], "-", job["company_name"])
        return jobs

    except Exception as e:
        print(f"Connection error: {e}")
        return []


# test
if __name__ == "__main__":
    with open("VIDYA M.txt", "r", encoding="utf8") as f:
        resume_text = f.read()
    skills = extract_skills(resume_text)
    jobs = search_jobs(skills)
