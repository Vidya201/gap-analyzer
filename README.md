# 🎯 Skill Gap Analyzer

Find exactly what skills you're missing for the jobs you actually want — paste in a resume or a skill list, and get a data-backed gap report plus free resources to close it.

## What it does

1. **Extracts your skills** from pasted resume text or a comma-separated skill list (via an LLM call to Groq).
2. **Searches live job postings** relevant to your top skills (via the Remotive public jobs API).
3. **Extracts the skills those job postings ask for** (via Groq again, run in parallel across jobs).
4. **Compares the two sets** to compute a match score, your matched skills, and your skill gap — with light alias normalization (e.g. "JS" / "JavaScript" collapse to one skill) so near-duplicates don't inflate the gap.
5. **Recommends free resources** to learn the top missing skills.

## Tech stack

- **Backend:** FastAPI + Groq LLM API (`openai/gpt-oss-120b`) + Remotive Jobs API
- **Frontend:** Streamlit
- **Language:** Python 3.10+

## Project structure

```
skill-gap-analyzer/
├── app.py          # FastAPI backend — exposes POST /analyze, wires features together
├── ui.py           # Streamlit frontend — the UI users interact with
├── run.py          # Starts both servers together, waits for backend health check
├── llm_utils.py    # Shared Groq client + robust JSON parsing for LLM responses
├── feature1.py     # Extract skills from resume text (Groq)
├── feature2.py     # Search relevant job postings (Remotive API)
├── feature3.py     # Extract required skills from job descriptions (Groq, parallelized)
├── feature4.py     # Compare user skills vs market skills, compute gap + score
├── feature5.py     # Recommend free resources for missing skills (Groq)
├── requirements.txt
└── .env.example
```

## Setup

**1. Clone and enter the project folder**
```bash
git clone <your-repo-url>
cd skill-gap-analyzer
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**
- Get a free key from [console.groq.com](https://console.groq.com)
- Copy `.env.example` to `.env`
- Paste your key in:
```
GROQ_API_KEY=your_actual_key_here
```

**5. Run the app**
```bash
python run.py
```
This starts both servers, waiting for the backend to be ready before launching the UI:
- FastAPI backend → http://localhost:8000 (docs at `/docs`)
- Streamlit UI → http://localhost:8501

Open **http://localhost:8501** in your browser — that's the app.

> ⚠️ Don't run `streamlit run ui.py` directly — the UI depends on the FastAPI backend being up on port 8000. Always start with `python run.py` so both launch together, in the right order.

## How to use it

1. Paste your resume text, or just list your skills comma-separated (e.g. `python, pandas, streamlit, sql`).
2. Click **Analyze My Skills**.
3. You'll get:
   - Your extracted skills
   - What the current job market is asking for
   - Your match score
   - Exactly which skills you're missing
   - A free resource to learn each missing skill

## Design decisions & fixes worth knowing about

- **Robust LLM JSON parsing** (`llm_utils.py`): LLMs don't always return clean JSON even when told to — they wrap answers in markdown fences or add a stray sentence. `safe_json_parse` strips fences and falls back to regex-extracting the first JSON block before giving up, with retries on transient failures.
- **Graceful degradation, not crashes**: if job-recommendation generation fails, the app still returns the score and skill gap — it just skips that one section instead of a full 500 error.
- **Parallelized job-skill extraction** (`feature3.py`): each job posting's LLM call runs concurrently (`ThreadPoolExecutor`) instead of sequentially, and one failing job doesn't take down the batch.
- **Multi-skill job search fallback** (`feature2.py`): tries the top 3 user skills in order (not just the single strongest one) before falling back to a generic search, so a niche top skill doesn't return zero jobs.
- **Simple in-memory caching** (`app.py`): identical resume text skips re-running the full LLM + job-search pipeline within a server session.
- **CORS enabled**: the Streamlit frontend and FastAPI backend run on different ports, so cross-origin requests needed explicit `CORSMiddleware`.

## Known limitations

- The in-memory cache resets on server restart — no persistent cache yet.
- LLM skill extraction still isn't matched against a fixed skill taxonomy, so unusual naming can occasionally still slip through the alias list in `feature4.py`.
- No resume file upload yet — paste-only.

## Why I built this

Built as a hands-on project in AI-assisted development: I designed the architecture and prompts, used Claude to implement and debug the FastAPI + Streamlit + external API pipeline, and worked through real issues along the way — a mismatched frontend file, LLM responses that broke naive JSON parsing, a sequential loop that should have been parallel, and a startup race condition between the two servers. The goal was to practice directing and reviewing AI-generated code closely enough to explain every decision in it, not just accept what was generated.

## Possible next steps

- Deploy backend + frontend (e.g. Render/Railway for FastAPI, Streamlit Community Cloud for the UI) so it's usable without running locally
- Add resume file upload (PDF/DOCX) instead of paste-only
- Move the in-memory cache to something persistent (SQLite/Redis) across restarts
- Add unit tests (`feature4.py`'s gap-scoring logic and `llm_utils.py`'s JSON parsing are the highest-value targets, and are already exercised in testing during development)
