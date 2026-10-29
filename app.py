# Smart Resume Screener - Stage 3 (Streamlit web app)
# Run with:  streamlit run app.py

import pandas as pd
import pdfplumber
import streamlit as st

# Reuse the functions we already built in main.py
from main import (
    calculate_match,
    clean_text,
    extract_skills,
    overall_score,
    skill_match_score,
    texts_too_similar,
    verdict,
)
from skills import MIN_JOB_SKILLS

st.set_page_config(page_title="Smart Resume Screener", page_icon="📄", layout="wide")


# Read text from an uploaded PDF or TXT file
def read_uploaded(uploaded_file):
    if uploaded_file.name.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text
    return uploaded_file.read().decode("utf-8", errors="ignore")


st.title("📄 Smart Resume Screener")
st.write("Upload a resume and a job description to see how well they match.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Resume")
    resume_file = st.file_uploader("Upload resume (PDF or TXT)", type=["pdf", "txt"], key="resume")

with col2:
    st.subheader("2. Job description")
    job_file = st.file_uploader("Upload job description (PDF or TXT)", type=["pdf", "txt"], key="job")
    job_pasted = st.text_area("...or paste it here", height=120)

if st.button("Analyze match", type="primary"):
    # Get the text from the inputs
    if resume_file is None:
        st.warning("Please upload a resume.")
        st.stop()

    if job_file is not None:
        job_raw = read_uploaded(job_file)
    elif job_pasted.strip():
        job_raw = job_pasted
    else:
        st.warning("Please upload or paste a job description.")
        st.stop()

    resume_raw = read_uploaded(resume_file)

    if not resume_raw.strip():
        st.error("Could not read any text from the resume. If it is a scanned PDF, it needs OCR.")
        st.stop()

    # Run the analysis
    resume = clean_text(resume_raw)
    job = clean_text(job_raw)

    similarity = calculate_match(resume, job)
    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)
    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)
    skill_score = skill_match_score(resume_skills, job_skills)
    combined = overall_score(similarity, skill_score, len(job_skills))
    level, message = verdict(similarity, skill_score, combined, len(job_skills))

    # Show the results
    st.divider()
    st.header("Results")

    if texts_too_similar(resume, job):
        st.warning(
            "Resume and job description look nearly identical. "
            "Make sure you did not upload/paste the same text into both sides."
        )

    if len(job_skills) < MIN_JOB_SKILLS:
        st.warning(
            f"Only **{len(job_skills)}** technical skill(s) found in the job description "
            f"(need {MIN_JOB_SKILLS}+). Soft skills like communication/teamwork are ignored "
            "for scoring because they inflate matches. Add more specific tech requirements."
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Text similarity", f"{similarity}%")
    m2.metric("Skill match", f"{skill_score}%")
    m3.metric("Overall score", f"{combined}%")
    m4.metric("Skills matched", f"{len(matched)} / {len(job_skills)}")

    st.progress(min(max(int(combined), 0), 100))

    if level == "strong":
        st.success(message)
    elif level == "moderate":
        st.info(message)
    elif level == "uncertain":
        st.warning(message)
    else:
        st.error(message)

    t1, t2 = st.columns(2)
    with t1:
        st.subheader("✅ Matched skills")
        if matched:
            st.dataframe(pd.DataFrame({"Skill": matched}), width="stretch", hide_index=True)
        else:
            st.write("No matching technical skills found.")
    with t2:
        st.subheader("❌ Missing skills")
        if missing:
            st.dataframe(pd.DataFrame({"Skill": missing}), width="stretch", hide_index=True)
        else:
            st.write("Nothing missing from the detected technical skills.")

    if not job_skills:
        st.caption(
            "No technical skills were found in the job description. "
            "Try a more specific JD, or add skills to skills.py."
        )
