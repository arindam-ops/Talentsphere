# 🚀 TalentSphere — Multi-Tenant Job Portal with ATS Engine

A production-grade **multi-tenant job portal** built with **Django 6.0**, featuring an **automated Applicant Tracking System (ATS)** that scores resumes against job requirements in real-time.

## ✨ Features

- **Multi-Tenant Architecture** — Complete data isolation between company tenants (TechNova, CloudScale, NexGen)
- **Automated ATS Engine** — Real-time resume parsing & scoring (PDF/DOCX/TXT) with skill matching, keyword analysis, and actionable feedback
- **Employer Dashboard** — Post jobs, manage applicants, rank candidates by ATS score
- **Candidate Portal** — Browse all jobs, apply with resume, view live ATS score breakdown
- **Live API Integration** — Real-time global tech job listings from ArbeitNow API (free, no API key needed)
- **Company Public Pages** — Dedicated showcase pages per tenant at `/company/<slug>/`
- **1-Click Demo Login** — Quick autofill buttons on the login page for viva/presentations

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0, Python 3.x |
| Database | MySQL 8.0 (dev) / PostgreSQL (production) |
| ATS Engine | pypdf, regex-based NLP, custom skill taxonomy (150+ skills) |
| Frontend | Django Templates, Bootstrap, HTML5/CSS3 |
| External API | ArbeitNow Job Board API (free) |
| Deployment | Vercel (serverless) |

## 🔑 Demo Credentials

| Role | Username | Password |
|---|---|---|
| Employer (TechNova) | `technova_hr` | `password123` |
| Employer (CloudScale) | `cloudscale_hr` | `password123` |
| Candidate | `rahul_dev` | `password123` |
| Candidate | `priya_qa` | `password123` |
| Superadmin | `admin` | `admin123` |

## 🚀 Local Setup

```bash
# Clone the repo
git clone https://github.com/arindam-ops/TalentSphere.git
cd TalentSphere

# Create virtual environment
python -m venv myenv
myenv\Scripts\activate   # Windows
source myenv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up MySQL database (port 3304)
# Create database: multitenant_job_portal

# Run migrations & seed data
python manage.py migrate
python manage.py seed_data

# Start server
python manage.py runserver
```

Then visit: **http://127.0.0.1:8000/**

## 📊 ATS Scoring Algorithm

```
ATS Score = Skill Match (50%) + Keyword Similarity (30%) + Education & Experience Signals (20%)
```

The ATS engine automatically:
1. Extracts text from uploaded resumes (PDF/DOCX/TXT)
2. Matches candidate skills against job requirements from a catalog of 150+ IT skills
3. Analyzes keyword frequency and context similarity
4. Detects education and experience signals
5. Ranks all applicants from highest to lowest score

## 📄 License

This project was built as an academic project. All rights reserved.

