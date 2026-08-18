# ui.py - Streamlit frontend

import streamlit as st
import requests

st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🎯", layout="wide")

st.title("🎯 Skill Gap Analyzer")
st.subheader("Find exactly what skills you need to get hired")

resume_text = st.text_area(
    "Paste your resume or list your skills here",
    height=200,
    placeholder="Example: I know Python, SQL, built projects using Streamlit and FastAPI..."
)

if st.button("Analyze My Skills", type="primary"):
    if not resume_text.strip():
        st.error("Please paste your resume or skills first")
    else:
        with st.spinner("Analyzing your skills against real job market..."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json={"resume_text": resume_text}
                )
                data = response.json()

                # score section
                st.markdown("---")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Match Score", f"{data['score']}%")
                with col2:
                    st.metric("Skills You Have", len(data['matched_skills']))
                with col3:
                    st.metric("Skills You're Missing", len(data['gap_skills']))

                # matched skills
                st.markdown("---")
                st.subheader("✅ Skills You Already Have")
                if data['matched_skills']:
                    cols = st.columns(4)
                    for i, skill in enumerate(data['matched_skills']):
                        cols[i % 4].success(skill)
                else:
                    st.info("No matching skills found")

                # gap skills
                st.subheader("❌ Skills You're Missing")
                if data['gap_skills']:
                    cols = st.columns(4)
                    for i, skill in enumerate(data['gap_skills']):
                        cols[i % 4].error(skill)

                # recommendations
                st.markdown("---")
                st.subheader("📚 What to Learn Next")
                if data['recommendations']:
                    for rec in data['recommendations']:
                        with st.expander(f"🔵 {rec['skill']}"):
                            st.write(f"**Why it matters:** {rec['why']}")
                            st.write(f"**Learn at:** {rec['learn_at']}")

            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
                st.info("Make sure the FastAPI server is running with python run.py")
