# Skills used for matching. Soft skills are tracked separately and do not
# drive the skill-match score (they appear on almost every resume/JD).

TECHNICAL_SKILLS = [
    # Programming languages (avoid ultra-short tokens like "r" / "go")
    "python", "java", "c++", "c#", "javascript", "typescript", "golang",
    "sql", "r studio",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data visualization", "matplotlib", "seaborn",
    "opencv", "spacy", "nltk", "transformers", "llm",
    "retrieval augmented generation",
    # Web / APIs
    "flask", "django", "fastapi", "streamlit", "rest api", "html", "css",
    "react", "node js",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite",
    # Tools / DevOps
    "git", "github", "docker", "kubernetes", "linux", "aws", "azure", "gcp",
]

SOFT_SKILLS = [
    "communication", "teamwork", "problem solving", "leadership",
]

# Kept for any older imports
SKILLS = TECHNICAL_SKILLS + SOFT_SKILLS

# Skill match score needs at least this many technical skills in the JD
MIN_JOB_SKILLS = 3
