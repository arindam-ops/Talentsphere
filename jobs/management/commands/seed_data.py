import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings
from jobs.models import Company, UserProfile, Job, Application


class Command(BaseCommand):
    help = "Seeds database with demo companies, recruiters, candidates, jobs, and applications"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding multi-tenant job portal demo data..."))

        # 1. Superuser
        admin_user, created = User.objects.get_or_create(username="admin", defaults={
            "email": "admin@jobportal.com",
            "is_staff": True,
            "is_superuser": True
        })
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user, defaults={"role": "ADMIN"})
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / admin123"))

        # 2. Companies (Tenants)
        c1, _ = Company.objects.get_or_create(
            slug="technova-solutions",
            defaults={
                "name": "TechNova Solutions",
                "industry": "Enterprise Software & Cloud",
                "location": "Bangalore, India",
                "website": "https://technova.example.com",
                "description": "TechNova is a premier cloud innovation company building intelligent SaaS architectures for Fortune 500 enterprises.",
                "logo_color": "#2563eb"
            }
        )

        c2, _ = Company.objects.get_or_create(
            slug="cloudscale-systems",
            defaults={
                "name": "CloudScale Systems",
                "industry": "DevOps & Infrastructure",
                "location": "Hyderabad, India",
                "website": "https://cloudscale.example.com",
                "description": "Next-generation distributed infrastructure and cloud telemetry platforms helping millions scale seamlessly.",
                "logo_color": "#0d9488"
            }
        )

        c3, _ = Company.objects.get_or_create(
            slug="nexgen-healthtech",
            defaults={
                "name": "NexGen HealthTech",
                "industry": "Digital Healthcare & AI",
                "location": "Pune, India",
                "website": "https://nexgenhealth.example.com",
                "description": "Pioneering AI diagnostics, tele-medicine portals, and clinical data orchestration.",
                "logo_color": "#7c3aed"
            }
        )

        # 3. Recruiters / Employers (Tenant bound)
        r1_user, created = User.objects.get_or_create(username="technova_hr", defaults={
            "first_name": "Rohan", "last_name": "Sharma", "email": "rohan@technova.com"
        })
        if created:
            r1_user.set_password("password123")
            r1_user.save()
        UserProfile.objects.update_or_create(
            user=r1_user,
            defaults={"role": "EMPLOYER", "company": c1, "headline": "Talent Acquisition Lead at TechNova"}
        )

        r2_user, created = User.objects.get_or_create(username="cloudscale_hr", defaults={
            "first_name": "Ayesha", "last_name": "Khan", "email": "ayesha@cloudscale.com"
        })
        if created:
            r2_user.set_password("password123")
            r2_user.save()
        UserProfile.objects.update_or_create(
            user=r2_user,
            defaults={"role": "EMPLOYER", "company": c2, "headline": "HR Manager at CloudScale"}
        )

        # 4. Candidates (Job Seekers)
        cand1, created = User.objects.get_or_create(username="rahul_dev", defaults={
            "first_name": "Rahul", "last_name": "Verma", "email": "rahul.verma@example.com"
        })
        if created:
            cand1.set_password("password123")
            cand1.save()
        UserProfile.objects.update_or_create(
            user=cand1,
            defaults={
                "role": "CANDIDATE",
                "headline": "Backend Python Developer | Django & MySQL Enthusiast",
                "skills": "Python, Django, MySQL, REST API, Git, Docker",
                "phone": "+91 98765 43210"
            }
        )

        cand2, created = User.objects.get_or_create(username="priya_qa", defaults={
            "first_name": "Priya", "last_name": "Nair", "email": "priya.nair@example.com"
        })
        if created:
            cand2.set_password("password123")
            cand2.save()
        UserProfile.objects.update_or_create(
            user=cand2,
            defaults={
                "role": "CANDIDATE",
                "headline": "QA Engineer & Automation Tester",
                "skills": "Selenium, Python, Testing, Git, Agile, SQL",
                "phone": "+91 91234 56789"
            }
        )

        cand3, created = User.objects.get_or_create(username="ananya_ml", defaults={
            "first_name": "Ananya", "last_name": "Deshmukh", "email": "ananya.ml@example.com"
        })
        if created:
            cand3.set_password("password123")
            cand3.save()
        UserProfile.objects.update_or_create(
            user=cand3,
            defaults={
                "role": "CANDIDATE",
                "headline": "Data Science & Machine Learning Intern",
                "skills": "Python, Machine Learning, Pandas, NumPy, SQL, TensorFlow",
                "phone": "+91 99887 76655"
            }
        )

        # 5. Jobs across Companies
        job_defs = [
            {
                "company": c1,
                "posted_by": r1_user,
                "title": "Junior Python / Django Developer",
                "category": "Software Development",
                "job_type": "FULL_TIME",
                "work_mode": "REMOTE",
                "location": "Bangalore / Remote",
                "experience_level": "0-2 Years",
                "salary_range": "₹6,00,000 - ₹9,50,000 LPA",
                "required_skills": "Python, Django, MySQL, REST API, Git",
                "description": "We are seeking a proactive Junior Python & Django Developer to build robust backend microservices, clean RESTful endpoints, and relational database schemas.",
                "responsibilities": "- Develop server-side logic and database models using Django.\n- Collaborate with frontend team to integrate APIs.\n- Write unit tests and maintain high code quality."
            },
            {
                "company": c1,
                "posted_by": r1_user,
                "title": "Full Stack React & Node Engineer",
                "category": "Software Development",
                "job_type": "FULL_TIME",
                "work_mode": "HYBRID",
                "location": "Bangalore, India",
                "experience_level": "1-3 Years",
                "salary_range": "₹8,00,000 - ₹12,00,000 LPA",
                "required_skills": "React, Node.js, JavaScript, HTML, CSS, MongoDB, Git",
                "description": "Join our product squad to build high-performance web applications with modern React components and microservice backends.",
                "responsibilities": "- Build responsive, dynamic UI components using React.\n- Implement secure Node.js backend controllers.\n- Optimize rendering and state management."
            },
            {
                "company": c2,
                "posted_by": r2_user,
                "title": "DevOps & Cloud Associate",
                "category": "DevOps & Cloud",
                "job_type": "FULL_TIME",
                "work_mode": "REMOTE",
                "location": "Hyderabad / Remote",
                "experience_level": "1-3 Years",
                "salary_range": "₹7,50,000 - ₹11,00,000 LPA",
                "required_skills": "AWS, Docker, Linux, CI/CD, Git, Kubernetes",
                "description": "Looking for an energetic DevOps engineer to automate deployment pipelines, containerize microservices, and manage AWS infrastructure.",
                "responsibilities": "- Build automated CI/CD pipelines.\n- Manage Docker containers and monitoring dashboards.\n- Ensure cloud uptime and security best practices."
            },
            {
                "company": c2,
                "posted_by": r2_user,
                "title": "QA Automation Engineer",
                "category": "Quality Assurance",
                "job_type": "FULL_TIME",
                "work_mode": "ON_SITE",
                "location": "Hyderabad, India",
                "experience_level": "0-2 Years",
                "salary_range": "₹5,50,000 - ₹8,00,000 LPA",
                "required_skills": "Selenium, Python, SQL, Unit Testing, Agile, Git",
                "description": "Lead automated test suite development for our distributed cloud platforms to verify functional correctness and API speed.",
                "responsibilities": "- Author automated UI & API regression tests.\n- Report defects and work with developers on verification.\n- Participate in sprint planning and QA sign-offs."
            },
            {
                "company": c3,
                "posted_by": r1_user,
                "title": "Machine Learning & AI Intern",
                "category": "Data Science & AI",
                "job_type": "INTERNSHIP",
                "work_mode": "REMOTE",
                "location": "Pune / Remote",
                "experience_level": "Freshers / Students",
                "salary_range": "₹25,000 - ₹35,000 / month Stipend",
                "required_skills": "Python, Machine Learning, Pandas, NumPy, Data Analysis, SQL",
                "description": "Great opportunity for 2nd/3rd/4th-year students to train clinical NLP models, clean healthcare datasets, and prototype generative analytics.",
                "responsibilities": "- Perform exploratory data analysis and feature engineering.\n- Train and evaluate predictive classification models.\n- Prepare presentations on model metrics."
            },
        ]

        created_jobs = []
        for jd in job_defs:
            job, _ = Job.objects.get_or_create(
                company=jd["company"],
                title=jd["title"],
                defaults={
                    "posted_by": jd["posted_by"],
                    "category": jd["category"],
                    "job_type": jd["job_type"],
                    "work_mode": jd["work_mode"],
                    "location": jd["location"],
                    "experience_level": jd["experience_level"],
                    "salary_range": jd["salary_range"],
                    "required_skills": jd["required_skills"],
                    "description": jd["description"],
                    "responsibilities": jd["responsibilities"],
                    "deadline": date.today() + timedelta(days=30),
                    "is_active": True
                }
            )
            created_jobs.append(job)

        # 6. Applications with ATS Scores
        sample_resume_content = b"""
        Rahul Verma - Software Engineer
        Email: rahul.verma@example.com | Phone: +91 98765 43210 | Bangalore
        
        Education:
        B.Tech in Computer Science and Engineering (2022 - 2026)
        
        Technical Skills:
        Languages: Python, C++, SQL, JavaScript, HTML, CSS
        Frameworks & DBs: Django, REST API, MySQL, SQLite, Bootstrap
        Tools: Git, GitHub, Docker, Postman, Linux
        
        Projects:
        1. Multi-Tenant Job Search Web Application (Django & MySQL):
           Developed role-based multi-tenant job board with automated ATS resume parser.
        2. Student Management REST API:
           Designed relational database schemas with unit testing.
        
        Experience:
        Software Engineering Intern - Web Development
        Collaborated in Agile sprints, built backend APIs, and optimized query performance.
        """

        # Make sure media directory exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'resumes'), exist_ok=True)

        app1, _ = Application.objects.get_or_create(
            job=created_jobs[0],
            candidate=cand1,
            defaults={
                "full_name": "Rahul Verma",
                "email": "rahul.verma@example.com",
                "phone": "+91 98765 43210",
                "cover_letter": "I have solid hands-on experience building Django backends with MySQL and REST APIs. I would love to contribute to TechNova Solutions.",
                "ats_score": 92,
                "matched_skills": "Django, Git, MySQL, Python, REST API",
                "missing_skills": "",
                "ats_feedback": "Outstanding match! All required technical skills and education criteria are fully satisfied in the candidate resume.",
                "status": "SHORTLISTED",
                "recruiter_notes": "Very strong profile. Shortlisted for technical round 1 on Thursday."
            }
        )
        if not app1.resume_file:
            app1.resume_file.save("rahul_verma_resume.txt", ContentFile(sample_resume_content), save=True)

        app2, _ = Application.objects.get_or_create(
            job=created_jobs[3],
            candidate=cand2,
            defaults={
                "full_name": "Priya Nair",
                "email": "priya.nair@example.com",
                "phone": "+91 91234 56789",
                "cover_letter": "Passionate QA engineer with proven background in Selenium test automation and bug reporting.",
                "ats_score": 86,
                "matched_skills": "Agile, Git, Python, Selenium, SQL, Unit Testing",
                "missing_skills": "",
                "ats_feedback": "Great alignment with QA automation role. Strong project evidence present.",
                "status": "INTERVIEW",
                "recruiter_notes": "Passed initial screening. Panel interview scheduled."
            }
        )
        if not app2.resume_file:
            app2.resume_file.save("priya_nair_resume.txt", ContentFile(sample_resume_content), save=True)

        app3, _ = Application.objects.get_or_create(
            job=created_jobs[4],
            candidate=cand3,
            defaults={
                "full_name": "Ananya Deshmukh",
                "email": "ananya.ml@example.com",
                "phone": "+91 99887 76655",
                "cover_letter": "Enthusiastic about applying Machine Learning algorithms to healthcare challenges.",
                "ats_score": 78,
                "matched_skills": "Data Analysis, Machine Learning, NumPy, Pandas, Python, SQL",
                "missing_skills": "",
                "ats_feedback": "Strong foundational data science skills. Good fit for internship.",
                "status": "APPLIED"
            }
        )
        if not app3.resume_file:
            app3.resume_file.save("ananya_ml_resume.txt", ContentFile(sample_resume_content), save=True)

        self.stdout.write(self.style.SUCCESS("[OK] Successfully seeded demo companies, jobs, recruiters, candidates, and ATS applications!"))
