
import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python", "java", "c++", "javascript", "html", "css",
    "react", "node.js", "express", "flask", "django",
    "sql", "mysql", "mongodb", "machine learning",
    "deep learning", "artificial intelligence", "nlp",
    "data analysis", "pandas", "numpy", "scikit-learn",
    "git", "github", "rest api", "communication",
    "problem solving", "data structures", "algorithms",
    "excel", "power bi", "aws", "docker"
]


def extract_resume_text(file_path):
    """Extract text from PDF or DOCX files."""
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(file_path)
        pages = [
            page.extract_text() or ""
            for page in reader.pages
        ]
        return "\n".join(pages)

    if extension == ".docx":
        document = Document(file_path)
        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]
        return "\n".join(paragraphs)

    raise ValueError("Please upload a PDF or DOCX resume.")


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_skills(text):
    """Find known skills using whole-word or phrase matching."""
    normalized = normalize_text(text)
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(found)


def analyze_resume(resume_text, job_description):
    """Compare resume content against a job description."""
    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    if not resume_text:
        raise ValueError("No readable text was found in the resume.")

    if not job_description:
        raise ValueError("Please enter a job description.")

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(
        [resume_text, job_description]
    )

    similarity = cosine_similarity(
        vectors[0:1], vectors[1:2]
    )[0][0]

    resume_skills = set(find_skills(resume_text))
    required_skills = set(find_skills(job_description))

    matched_skills = sorted(resume_skills & required_skills)
    missing_skills = sorted(required_skills - resume_skills)

    if required_skills:
        skill_match = round(
            len(matched_skills) / len(required_skills) * 100
        )
    else:
        skill_match = 0

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Consider developing relevant skills: "
            + ", ".join(missing_skills)
            + ". Add them to your resume only if you genuinely have them."
        )

    if len(resume_text.split()) < 100:
        recommendations.append(
            "Your resume contains little text. If appropriate, "
            "include more detail about projects, education, and experience."
        )

    if not recommendations:
        recommendations.append(
            "Review your projects and achievements to ensure they "
            "clearly demonstrate the skills required for this role."
        )

    return {
        "similarity_score": round(similarity * 100),
        "skill_match": skill_match,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
    }
