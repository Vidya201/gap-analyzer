# app.py - FastAPI backend - connects all features together

import hashlib
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from feature1 import extract_skills
from feature2 import search_jobs
from feature3 import extract_job_skills
from feature4 import find_gap
from feature5 import get_recommendations

load_dotenv()

logger = logging.getLogger("skill_gap_analyzer")

app = FastAPI(title="Skill Gap Analyzer")

# Streamlit (port 8501) calls this API (port 8000) from the browser - without
# CORS enabled, those cross-origin requests would be silently blocked.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Very simple in-memory cache: same resume text -> skip re-running the whole
# LLM + job-search pipeline. Resets on server restart, which is fine for a
# demo/portfolio project (persistent caching is listed as a "next step").
_analysis_cache: dict[str, dict] = {}


class ResumeInput(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Resume text or comma-separated skill list")


@app.post("/analyze")
def analyze(input: ResumeInput):
    resume_text = input.resume_text.strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="resume_text cannot be empty")

    cache_key = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
    if cache_key in _analysis_cache:
        logger.info("Serving cached analysis result")
        return _analysis_cache[cache_key]

    try:
        # step 1 - extract skills from resume
        user_skills = extract_skills(resume_text)
        if not user_skills:
            raise HTTPException(
                status_code=422,
                detail="No technical skills could be identified in the given text.",
            )

        # step 2 - search relevant jobs
        jobs = search_jobs(user_skills)
        if not jobs:
            raise HTTPException(
                status_code=502,
                detail="Couldn't fetch job postings right now (job API may be unavailable). Try again shortly.",
            )

        # step 3 - extract skills market wants
        job_skills = extract_job_skills(jobs)
        if not job_skills:
            raise HTTPException(
                status_code=502,
                detail="Couldn't extract required skills from job postings. Try again shortly.",
            )

        # step 4 - find the gap
        gap_result = find_gap(user_skills, job_skills)

        # step 5 - get recommendations (best-effort; empty list on failure, not a hard error)
        recommendations = get_recommendations(gap_result["gap_skills"])

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Pipeline failure: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in /analyze")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {e}")

    result = {
        "user_skills": user_skills,
        "market_skills": sorted(set(job_skills), key=str.lower),
        "matched_skills": gap_result["matched_skills"],
        "gap_skills": gap_result["gap_skills"],
        "score": gap_result["score"],
        "jobs_analyzed": len(jobs),
        "recommendations": recommendations,
    }

    _analysis_cache[cache_key] = result
    return result


@app.get("/")
def home():
    return {"message": "Skill Gap Analyzer API is running"}


@app.get("/health")
def health():
    """Used by run.py to know when the backend is actually ready to take requests."""
    return {"status": "ok"}
