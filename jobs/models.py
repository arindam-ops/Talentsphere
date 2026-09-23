from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Company(models.Model):
    """
    Tenant Entity: Represents an organization / company.
    Enforces multi-tenancy where each company's recruiters manage their own jobs and applicants.
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    industry = models.CharField(max_length=100, default="Technology")
    location = models.CharField(max_length=150, default="Bangalore, India")
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    logo_color = models.CharField(max_length=20, default="#2563eb", help_text="Hex color for avatar branding")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def active_jobs_count(self):
        return self.jobs.filter(is_active=True).count()


class UserProfile(models.Model):
    """
    Extends Django's built-in User model.
    Role: CANDIDATE (Job Seeker) or EMPLOYER (Belongs to a Company Tenant).
    """
    ROLE_CHOICES = (
        ('CANDIDATE', 'Candidate / Job Seeker'),
        ('EMPLOYER', 'Employer / Recruiter'),
        ('ADMIN', 'Platform Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CANDIDATE')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recruiters',
        help_text="Tenant Company for Employers"
    )
    headline = models.CharField(max_length=200, blank=True, help_text="e.g. Full Stack Python Developer")
    phone = models.CharField(max_length=20, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills e.g. Python, Django, SQL")
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_employer(self):
        return self.role == 'EMPLOYER'

    @property
    def is_candidate(self):
        return self.role == 'CANDIDATE'


class Job(models.Model):
    """
    Job Posting Entity.
    Each Job belongs strictly to a Company (Tenant).
    """
    JOB_TYPE_CHOICES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('INTERNSHIP', 'Internship'),
        ('CONTRACT', 'Contract'),
    )

    WORK_MODE_CHOICES = (
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
        ('ON_SITE', 'On-site'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default="Software Development")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default='REMOTE')
    location = models.CharField(max_length=150, default="Remote")
    experience_level = models.CharField(max_length=50, default="0-2 Years")
    salary_range = models.CharField(max_length=100, blank=True, default="Competitive")
    required_skills = models.TextField(help_text="Comma-separated required skills e.g. Python, Django, MySQL, Git")
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    @property
    def skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    @property
    def applicant_count(self):
        return self.applications.count()


class Application(models.Model):
    """
    Applicant Tracking System (ATS) Record.
    Stores applicant data, extracted resume info, and automated ATS match score.
    """
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('REVIEWING', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('OFFERED', 'Job Offered'),
        ('REJECTED', 'Not Selected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cover_letter = models.TextField(blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    
    # Automated ATS Evaluation Fields
    ats_score = models.IntegerField(default=0, help_text="ATS match percentage score (0-100)")
    matched_skills = models.TextField(blank=True, help_text="Comma-separated list of matched skills")
    missing_skills = models.TextField(blank=True, help_text="Comma-separated list of missing skills")
    ats_feedback = models.TextField(blank=True, help_text="Automated ATS analysis & recommendations")
    
    # Recruiter Pipeline Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    recruiter_notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ats_score', '-applied_at']
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.full_name} -> {self.job.title} ({self.ats_score}% ATS)"

    @property
    def matched_skills_list(self):
        if not self.matched_skills:
            return []
        return [s.strip() for s in self.matched_skills.split(',') if s.strip()]

    @property
    def missing_skills_list(self):
        if not self.missing_skills:
            return []
        return [s.strip() for s in self.missing_skills.split(',') if s.strip()]

    @property
    def score_badge_class(self):
        if self.ats_score >= 75:
            return "bg-success text-white"
        elif self.ats_score >= 50:
            return "bg-warning text-dark"
        else:
            return "bg-danger text-white"

