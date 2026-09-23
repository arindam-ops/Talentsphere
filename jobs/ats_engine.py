import re
import os
import io
import math
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader


# Standard Comprehensive Skill Dictionary (Tech & Engineering)
SKILL_CATALOG = {
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "php", "ruby", "go",
    "rust", "kotlin", "swift", "r", "dart", "scala", "shell", "bash",
    
    # Web & Frontend
    "html", "html5", "css", "css3", "bootstrap", "tailwind", "sass", "react", "react.js",
    "vue", "vue.js", "angular", "next.js", "jquery", "redux", "ui/ux", "frontend",
    
    # Backend & Frameworks
    "django", "flask", "fastapi", "node.js", "nodejs", "express", "spring", "spring boot",
    "asp.net", "laravel", "backend", "rest api", "graphql", "microservices",
    
    # Databases
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "oracle", "nosql",
    "database management", "dbms",
    
    # Cloud, DevOps & Tools
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "gitlab", "linux",
    "ci/cd", "jenkins", "terraform", "nginx", "apache", "postman",
    
    # AI, ML & Data Science
    "machine learning", "deep learning", "nlp", "computer vision", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "data analysis", "data science",
    "power bi", "tableau", "statistics",
    
    # Software Engineering & Concepts
    "data structures", "algorithms", "oop", "object oriented programming", "system design",
    "unit testing", "selenium", "agile", "scrum", "sdlc", "debugging",
    
    # Soft Skills & Business
    "communication", "leadership", "problem solving", "teamwork", "time management", "critical thinking"
}


def extract_text_from_file(file_obj) -> str:
    """
    Extracts plain text from PDF, TXT, or DOCX resume files.
    """
    filename = getattr(file_obj, 'name', '').lower()
    text = ""

    try:
        if filename.endswith('.pdf'):
            # Using pypdf
            reader = PdfReader(file_obj)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif filename.endswith('.docx'):
            # Extract text from docx xml (zero extra dependencies)
            with zipfile.ZipFile(file_obj) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                text = " ".join([node.text for node in tree.iter() if node.text])
        else:
            # Fallback for plain text or unknown format
            content = file_obj.read()
            if isinstance(content, bytes):
                try:
                    text = content.decode('utf-8', errors='ignore')
                except Exception:
                    text = content.decode('latin-1', errors='ignore')
            else:
                text = str(content)
    except Exception as e:
        print(f"Resume text extraction error: {e}")
        text = ""

    # Reset stream pointer if seekable
    try:
        file_obj.seek(0)
    except Exception:
        pass

    return text.strip()


def normalize_text(text: str) -> str:
    """Clean and lower-case text for token comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^\w\s\+\#\.\-]', ' ', text)
    return text


def extract_skills(text: str) -> set:
    """Identifies skills from the skill catalog found within the text."""
    normalized = normalize_text(text)
    found_skills = set()

    for skill in SKILL_CATALOG:
        # Match as whole word/phrase
        pattern = r'(?:\b|(?<=\s))' + re.escape(skill) + r'(?:\b|(?=\s))'
        if re.search(pattern, normalized):
            found_skills.add(skill)

    return found_skills


def calculate_ats_score(resume_text: str, job_title: str, job_skills_str: str, job_description: str):
    """
    Calculates ATS Match Score (0 - 100%) and returns detailed match breakdown.
    
    Weights:
    1. Direct Required Skills Overlap: 50%
    2. Term Frequency & Description Keyword Overlap: 30%
    3. Experience & Education Signals: 20%
    """
    norm_resume = normalize_text(resume_text)
    
    # 1. Parse Required Skills from Job
    raw_required = [s.strip().lower() for s in job_skills_str.split(',') if s.strip()]
    if not raw_required:
        # Extract from description if empty
        raw_required = list(extract_skills(job_description + " " + job_title))

    required_skills_set = set(raw_required)

    # 2. Extract Candidate Skills
    candidate_skills = extract_skills(resume_text)

    # Calculate Matched & Missing Skills
    matched = []
    missing = []
    for req in required_skills_set:
        # Check direct or contained match
        pattern = r'(?:\b|(?<=\s))' + re.escape(req) + r'(?:\b|(?=\s))'
        if re.search(pattern, norm_resume) or req in candidate_skills:
            matched.append(req.title())
        else:
            missing.append(req.title())

    # Skill Match Component (0 to 50 pts)
    if required_skills_set:
        skill_coverage = len(matched) / len(required_skills_set)
    else:
        skill_coverage = 0.8  # Default baseline if no skills specified
    skill_score = skill_coverage * 50.0

    # 3. Term Frequency / Keyword Similarity (0 to 30 pts)
    job_words = set(re.findall(r'\b[a-z]{3,}\b', normalize_text(job_description + " " + job_title)))
    stop_words = {
        'the', 'and', 'for', 'with', 'you', 'will', 'this', 'that', 'from', 'have', 'are',
        'our', 'role', 'team', 'work', 'join', 'opportunity', 'company', 'looking', 'job',
        'years', 'experience', 'skills', 'must', 'should', 'responsibilities', 'requirements'
    }
    meaningful_job_words = job_words - stop_words
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', norm_resume))

    if meaningful_job_words:
        keyword_overlap = len(meaningful_job_words.intersection(resume_words)) / len(meaningful_job_words)
    else:
        keyword_overlap = 0.5
    keyword_score = min(keyword_overlap * 2.0, 1.0) * 30.0

    # 4. Education & Experience Signals (0 to 20 pts)
    signals_score = 0.0
    # Education keywords (up to 10 pts)
    edu_terms = ['btech', 'b.tech', 'be', 'b.e', 'bachelor', 'master', 'mtech', 'bca', 'mca', 'degree', 'computer science', 'engineering']
    if any(term in norm_resume for term in edu_terms):
        signals_score += 10.0
    else:
        signals_score += 4.0

    # Experience & Project keywords (up to 10 pts)
    exp_terms = ['experience', 'project', 'developed', 'implemented', 'intern', 'built', 'responsibilities', 'worked']
    matches_exp = sum(1 for term in exp_terms if term in norm_resume)
    signals_score += min(matches_exp * 2.5, 10.0)

    # Total Score calculation
    total_score = round(skill_score + keyword_score + signals_score)
    total_score = max(min(total_score, 98), 12)  # realistic bounds

    # Generate Actionable ATS Feedback
    feedback_points = []
    if missing:
        missing_preview = ", ".join(missing[:4])
        feedback_points.append(f"Skill Gap Identified: Consider emphasizing experience with {missing_preview}.")
    if skill_coverage >= 0.75:
        feedback_points.append("Excellent skill alignment! Your technical background strongly matches the core requirements.")
    elif skill_coverage >= 0.5:
        feedback_points.append("Moderate skill match. Highlighting specific projects using the required tech stack will improve shortlisting chances.")
    else:
        feedback_points.append("Low direct skill overlap. Tailor your resume summary and project bullet points toward the job description keywords.")

    if not any(term in norm_resume for term in ['project', 'developed', 'built']):
        feedback_points.append("Tip: Add measurable project outcomes (e.g. 'Built REST API using Django with MySQL').")

    feedback_text = " ".join(feedback_points)

    return {
        'score': total_score,
        'matched_skills': ", ".join(sorted(matched)),
        'missing_skills': ", ".join(sorted(missing)),
        'feedback': feedback_text,
    }

