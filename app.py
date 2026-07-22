# app.py - FastAPI backend - connects all features together

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import json

from feature1 import extract_skills
from feature2 import search_jobs
from feature3 import extract_job_skills
from feature4 import find_gap
from feature5 import get_recommendations

load_dotenv()

app = FastAPI(title="Skill Gap Analyzer")

class ResumeInput(BaseModel):
    resume_text: str

@app.post("/analyze")
def analyze(input: ResumeInput):
    # step 1 - extract skills from resume
    user_skills = extract_skills(input.resume_text)

    # step 2 - search relevant jobs
    jobs = search_jobs(user_skills)

    # step 3 - extract skills market wants
    job_skills = extract_job_skills(jobs)

    # step 4 - find the gap
    gap_result = find_gap(user_skills, job_skills)

    # step 5 - get recommendations
    recommendations = get_recommendations(gap_result["gap_skills"])

    return {
        "user_skills": user_skills,
        "market_skills": list(set(job_skills)),
        "matched_skills": gap_result["matched_skills"],
        "gap_skills": gap_result["gap_skills"],
        "score": gap_result["score"],
        "recommendations": recommendations
    }

@app.get("/")
def home():
    return {"message": "Skill Gap Analyzer API is running"}
