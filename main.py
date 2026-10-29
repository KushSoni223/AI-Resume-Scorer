# Smart Resume Screener - Stage 2
# Reads a resume (PDF or TXT) and a job description, then shows:
#   - overall match score
#   - matched skills
#   - missing skills
#
# Usage:
#   python main.py                                  (uses the sample files)
#   python main.py my_resume.pdf job_description.txt

import re
import sys

import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills import MIN_JOB_SKILLS, SOFT_SKILLS, TECHNICAL_SKILLS


# Step 1: Read text from a TXT or PDF file
def read_file(path):
    if path.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# Step 2: Clean the text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s+#]", " ", text)   # keep + and # for c++, c#
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _find_skills(clean, skill_list):
    found = set()
    for skill in skill_list:
        skill_clean = clean_text(skill)  # "scikit-learn" -> "scikit learn"
        # Require a real token boundary so short skills don't match inside words
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill_clean) + r"(?![a-z0-9+#])"
        if re.search(pattern, clean):
            found.add(skill)
    return found


# Step 3: Find which known skills appear in a text (technical only by default)
def extract_skills(clean, include_soft=False):
    found = _find_skills(clean, TECHNICAL_SKILLS)
    if include_soft:
        found |= _find_skills(clean, SOFT_SKILLS)
    return found


# Step 4: Overall similarity score (TF-IDF + cosine similarity)
def calculate_match(resume_text, job_text):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, job_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 2)


def texts_too_similar(resume_text, job_text, threshold=95.0):
    """True when resume and JD look like the same (or near-identical) document."""
    if not resume_text or not job_text:
        return False
    if resume_text == job_text:
        return True
    return calculate_match(resume_text, job_text) >= threshold


def skill_match_score(resume_skills, job_skills):
    if not job_skills:
        return 0.0
    matched = resume_skills & job_skills
    return round(len(matched) / len(job_skills) * 100, 2)


def overall_score(similarity, skill_score, job_skill_count):
    """Blend text + skill scores. Soften skill weight when the JD has few skills."""
    if job_skill_count < MIN_JOB_SKILLS:
        # Not enough technical skills in the JD to trust skill % alone
        return round(0.7 * similarity + 0.3 * skill_score, 2)
    return round(0.4 * similarity + 0.6 * skill_score, 2)


def verdict(similarity, skill_score, combined, job_skill_count):
    if job_skill_count < MIN_JOB_SKILLS:
        return (
            "uncertain",
            "Too few technical skills detected in the job description. "
            "Skill match alone is not reliable — add more specific requirements.",
        )
    if combined >= 70 and skill_score >= 50 and similarity >= 15:
        return "strong", "Strong match"
    if combined >= 40 and (skill_score >= 40 or similarity >= 20):
        return (
            "moderate",
            "Moderate match: consider adding the missing skills if you have them.",
        )
    return "weak", "Weak match: the resume needs tailoring for this job."


# Step 5: Compare skills and print the report
def main():
    resume_path = sys.argv[1] if len(sys.argv) > 1 else "sample_resume.txt"
    job_path = sys.argv[2] if len(sys.argv) > 2 else "sample_job.txt"

    resume = clean_text(read_file(resume_path))
    job = clean_text(read_file(job_path))

    similarity = calculate_match(resume, job)
    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)

    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)
    skill_score = skill_match_score(resume_skills, job_skills)
    combined = overall_score(similarity, skill_score, len(job_skills))
    level, message = verdict(similarity, skill_score, combined, len(job_skills))

    print("=" * 40)
    print(f"Text similarity score : {similarity}%")
    print(f"Skill match score     : {skill_score}%")
    print(f"Overall score         : {combined}%")
    print(f"Verdict               : {message}")
    print("=" * 40)
    print("Matched skills :", ", ".join(matched) if matched else "None")
    print("Missing skills :", ", ".join(missing) if missing else "None")
    print("=" * 40)

    if len(job_skills) < MIN_JOB_SKILLS:
        print(
            f"Warning: only {len(job_skills)} technical skill(s) found in the "
            f"job description (need {MIN_JOB_SKILLS}+ for a reliable skill score)."
        )
    if texts_too_similar(resume, job):
        print("Warning: resume and job description look nearly identical.")
    if missing:
        print("Tip: add these skills to your resume if you really have them.")


if __name__ == "__main__":
    main()
