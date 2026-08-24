# ui.py - Streamlit frontend for the Skill Gap Analyzer
# Talks to the FastAPI backend (app.py) running on http://localhost:8000

import requests
import streamlit as st

API_URL = "http://localhost:8000/analyze"
HEALTH_URL = "http://localhost:8000/health"

st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🎯", layout="wide")

st.title("🎯 Skill Gap Analyzer")
st.markdown(
    "Paste your resume or list your skills, and see exactly what today's "
    "job market wants that you don't have yet — plus free resources to close the gap."
)

# ── input ──────────────────────────────────────────────────────────────
with st.form("analyze_form"):
    resume_text = st.text_area(
        "Paste your resume text, or a comma-separated skill list",
        height=220,
        placeholder="e.g. Python, FastAPI, SQL, React, Git, Docker\n\n...or paste your full resume text here.",
    )
    submitted = st.form_submit_button("🔍 Analyze My Skills", use_container_width=True)

if submitted:
    if not resume_text.strip():
        st.warning("Please paste your resume text or skills first.")
        st.stop()

    # quick check that the backend is actually up, so the error is clear
    # instead of a generic connection traceback
    try:
        requests.get(HEALTH_URL, timeout=3)
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Can't reach the backend API at http://localhost:8000. "
            "Make sure you started the app with `python run.py`, not "
            "`streamlit run ui.py` directly."
        )
        st.stop()

    with st.spinner("Extracting your skills, searching live job postings, and comparing against the market..."):
        try:
            response = requests.post(API_URL, json={"resume_text": resume_text}, timeout=90)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.Timeout:
            st.error("The analysis took too long and timed out. Please try again.")
            st.stop()
        except requests.exceptions.HTTPError:
            detail = response.json().get("detail", "Unknown error")
            st.error(f"⚠️ {detail}")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Couldn't reach the backend: {e}")
            st.stop()

    st.session_state["result"] = result

# ── results ────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Match Score", f"{result['score']}%")
    col2.metric("Matched Skills", len(result["matched_skills"]))
    col3.metric("Skills to Learn", len(result["gap_skills"]))

    st.progress(min(result["score"] / 100, 1.0))
    st.caption(f"Based on {result.get('jobs_analyzed', '?')} live job postings matching your top skills.")

    tab1, tab2, tab3 = st.tabs(["✅ What you have", "📈 What's missing", "📚 How to close the gap"])

    with tab1:
        st.subheader("Your extracted skills")
        st.write(", ".join(result["user_skills"]) or "None found")
        st.subheader("Skills that match the market")
        if result["matched_skills"]:
            st.write(", ".join(result["matched_skills"]))
        else:
            st.info("No overlap found between your skills and the sampled job postings.")

    with tab2:
        st.subheader("Skills the market wants that you don't have yet")
        if result["gap_skills"]:
            for skill in result["gap_skills"]:
                st.markdown(f"- {skill}")
        else:
            st.success("No gap found — your skills fully cover the sampled job postings! 🎉")

    with tab3:
        recs = result.get("recommendations", [])
        if not recs:
            st.info("No recommendations available for this run — try analyzing again.")
        else:
            for rec in recs:
                with st.container(border=True):
                    st.markdown(f"**{rec.get('skill', 'Unknown skill')}**")
                    st.write(rec.get("why", ""))
                    st.caption(f"📍 Learn at: {rec.get('learn_at', 'N/A')}")

    with st.expander("See all skills the sampled jobs asked for"):
        st.write(", ".join(result.get("market_skills", [])))
