from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse

from .models import Company, UserProfile, Job, Application
from .forms import JobPostForm, JobApplyForm, CandidateRegisterForm, EmployerRegisterForm
from .ats_engine import extract_text_from_file, calculate_ats_score
from .free_api import fetch_live_tech_jobs


def home(request):
    """
    Homepage and Global Job Search Engine.
    Candidates can browse and filter jobs across all companies (multi-tenant aggregation).
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    work_mode = request.GET.get('work_mode', '').strip()
    company_slug = request.GET.get('company', '').strip()

    jobs = Job.objects.filter(is_active=True).select_related('company')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(description__icontains=query) |
            Q(company__name__icontains=query) |
            Q(location__icontains=query)
        )

    if category:
        jobs = jobs.filter(category__iexact=category)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if work_mode:
        jobs = jobs.filter(work_mode=work_mode)

    if company_slug:
        jobs = jobs.filter(company__slug=company_slug)

    # Categories list for filter dropdown
    categories = Job.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    companies = Company.objects.annotate(job_cnt=Count('jobs')).filter(job_cnt__gt=0)

    # Simple fast pagination
    paginator = Paginator(jobs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    stats = {
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_companies': Company.objects.count(),
        'total_applications': Application.objects.count(),
    }

    context = {
        'jobs': page_obj,
        'query': query,
        'selected_category': category,
        'selected_type': job_type,
        'selected_mode': work_mode,
        'categories': categories,
        'companies': companies,
        'stats': stats,
    }
    return render(request, 'jobs/home.html', context)


def job_detail(request, pk):
    """
    Detailed Job View. Displays specifications, company info, and application form.
    """
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)
    
    # Check if user already applied
    already_applied = False
    user_application = None
    if request.user.is_authenticated:
        user_application = Application.objects.filter(job=job, candidate=request.user).first()
        if user_application:
            already_applied = True

    form = JobApplyForm(initial={
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip() if request.user.is_authenticated else "",
        'email': request.user.email if request.user.is_authenticated else ""
    })

    # Related jobs in the same company or category
    related_jobs = Job.objects.filter(is_active=True).filter(
        Q(category=job.category) | Q(company=job.company)
    ).exclude(pk=job.pk)[:3]

    context = {
        'job': job,
        'already_applied': already_applied,
        'user_application': user_application,
        'form': form,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_apply(request, pk):
    """
    Processes candidate application with resume upload.
    Runs the automated ATS scoring engine in real-time.
    """
    job = get_object_or_404(Job, pk=pk)

    # Check if already applied
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, "You have already applied for this position!")
        return redirect('jobs:job_detail', pk=pk)

    if request.method == 'POST':
        form = JobApplyForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user

            # Run ATS Evaluation
            resume_file = request.FILES.get('resume_file')
            if resume_file:
                # Extract text
                resume_text = extract_text_from_file(resume_file)
                # Compute score & match details
                ats_results = calculate_ats_score(
                    resume_text=resume_text,
                    job_title=job.title,
                    job_skills_str=job.required_skills,
                    job_description=job.description
                )
                application.ats_score = ats_results['score']
                application.matched_skills = ats_results['matched_skills']
                application.missing_skills = ats_results['missing_skills']
                application.ats_feedback = ats_results['feedback']

            application.save()
            messages.success(
                request,
                f"Application submitted successfully! Your ATS Match Score is {application.ats_score}%."
            )
            return redirect('jobs:candidate_dashboard')
        else:
            messages.error(request, "Please check the form fields and upload a valid resume.")
    
    return redirect('jobs:job_detail', pk=pk)


@login_required
def candidate_dashboard(request):
    """
    Candidate Dashboard: Displays all submitted applications and their ATS evaluations.
    """
    applications = Application.objects.filter(candidate=request.user).select_related('job', 'job__company')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/candidate_dashboard.html', context)


# ==========================================
# EMPLOYER / TENANT PORTAL
# ==========================================

def is_employer_check(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_employer and user.profile.company is not None


@login_required
def employer_dashboard(request):
    """
    Employer Dashboard: Isolated to the Recruiter's Company (Tenant Isolation).
    """
    if not is_employer_check(request.user):
        messages.error(request, "Access restricted to employer accounts.")
        return redirect('jobs:home')

    company = request.user.profile.company
    company_jobs = Job.objects.filter(company=company)
    company_applications = Application.objects.filter(job__company=company)

    # Key Tenant Metrics
    total_jobs = company_jobs.count()
    active_jobs = company_jobs.filter(is_active=True).count()
    total_applicants = company_applications.count()
    shortlisted_count = company_applications.filter(status__in=['SHORTLISTED', 'INTERVIEW', 'OFFERED']).count()
    avg_ats = company_applications.aggregate(avg=Avg('ats_score'))['avg'] or 0

    recent_applicants = company_applications.select_related('job', 'candidate')[:6]

    context = {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'shortlisted_count': shortlisted_count,
        'avg_ats': round(avg_ats, 1),
        'jobs': company_jobs[:8],
        'recent_applicants': recent_applicants,
    }
    return render(request, 'jobs/employer_dashboard.html', context)


@login_required
def job_create(request):
    """
    Recruiter creates a new Job. Automatically attached to the Recruiter's Company (Tenant).
    """
    if not is_employer_check(request.user):
        messages.error(request, "Only employers can post jobs.")
        return redirect('jobs:home')

    company = request.user.profile.company

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.posted_by = request.user
            job.save()
            messages.success(request, f"Job '{job.title}' posted successfully for {company.name}!")
            return redirect('jobs:employer_dashboard')
    else:
        form = JobPostForm()

    context = {
        'form': form,
        'company': company,
        'action_title': 'Post New Job'
    }
    return render(request, 'jobs/job_form.html', context)


@login_required
def job_edit(request, pk):
    """
    Edit an existing job, ensuring multi-tenant ownership check.
    """
    if not is_employer_check(request.user):
        return HttpResponseForbidden("Access denied.")

    company = request.user.profile.company
    job = get_object_or_404(Job, pk=pk, company=company)  # Tenant scoping!

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully.")
            return redirect('jobs:employer_dashboard')
    else:
        form = JobPostForm(instance=job)

    context = {
        'form': form,
        'company': company,
        'action_title': f"Edit Job: {job.title}"
    }
    return render(request, 'jobs/job_form.html', context)


@login_required
def job_delete(request, pk):
    """
    Toggle or delete job with tenant verification.
    """
    if not is_employer_check(request.user):
        return HttpResponseForbidden("Access denied.")

    company = request.user.profile.company
    job = get_object_or_404(Job, pk=pk, company=company)

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job listing removed.")
    return redirect('jobs:employer_dashboard')


@login_required
def employer_applicants(request, job_id=None):
    """
    ATS Applicant Tracking Pipeline:
    - View candidates for company jobs.
    - SORTS BY ATS SCORE (Highest to Lowest) to instantly bubble up top talent!
    - Filter by job and status.
    """
    if not is_employer_check(request.user):
        messages.error(request, "Access restricted to employers.")
        return redirect('jobs:home')

    company = request.user.profile.company
    company_jobs = Job.objects.filter(company=company)

    applicants = Application.objects.filter(job__company=company).select_related('job', 'candidate')

    selected_job_id = request.GET.get('job') or (str(job_id) if job_id else '')
    selected_status = request.GET.get('status', '')

    if selected_job_id:
        applicants = applicants.filter(job_id=selected_job_id)
    if selected_status:
        applicants = applicants.filter(status=selected_status)

    # Order by ATS score (highest first)
    applicants = applicants.order_by('-ats_score', '-applied_at')

    context = {
        'company': company,
        'jobs': company_jobs,
        'applicants': applicants,
        'selected_job_id': selected_job_id,
        'selected_status': selected_status,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'jobs/employer_applicants.html', context)


@login_required
def update_applicant_status(request, pk):
    """
    Recruiter updates candidate status (Applied -> Reviewing -> Shortlisted -> Interview -> Offered/Rejected).
    """
    if not is_employer_check(request.user):
        return HttpResponseForbidden("Access denied.")

    company = request.user.profile.company
    applicant = get_object_or_404(Application, pk=pk, job__company=company)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('recruiter_notes', '')

        if new_status in dict(Application.STATUS_CHOICES):
            applicant.status = new_status
            if notes:
                applicant.recruiter_notes = notes
            applicant.save()
            messages.success(request, f"Updated status for {applicant.full_name} to {applicant.get_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'jobs:employer_applicants'))


# ==========================================
# PUBLIC & FREE API VIEWS
# ==========================================

def live_api_jobs(request):
    """
    Fetches real-time live tech jobs using the 100% Free ArbeitNow API.
    Zero-cost, no credit card or paid keys required.
    """
    jobs = fetch_live_tech_jobs(limit=20)
    context = {
        'live_jobs': jobs,
    }
    return render(request, 'jobs/live_api_jobs.html', context)


def company_detail(request, slug):
    """
    Public showcase for a Company (Tenant).
    Displays company bio and active job postings.
    """
    company = get_object_or_404(Company, slug=slug)
    jobs = company.jobs.filter(is_active=True)

    context = {
        'company': company,
        'jobs': jobs,
    }
    return render(request, 'jobs/company_detail.html', context)


# ==========================================
# AUTHENTICATION & REGISTRATION
# ==========================================

def register_candidate(request):
    """
    Register as a Job Seeker / Candidate.
    """
    if request.user.is_authenticated:
        return redirect('jobs:dashboard_redirect')

    if request.method == 'POST':
        form = CandidateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            UserProfile.objects.create(
                user=user,
                role='CANDIDATE',
                headline=form.cleaned_data.get('headline', ''),
                skills=form.cleaned_data.get('skills', ''),
                phone=form.cleaned_data.get('phone', '')
            )

            login(request, user)
            messages.success(request, f"Welcome to the portal, {user.first_name or user.username}!")
            return redirect('jobs:candidate_dashboard')
    else:
        form = CandidateRegisterForm()

    return render(request, 'jobs/register_candidate.html', {'form': form})


def register_employer(request):
    """
    Register as an Employer and automatically create their Company Tenant.
    """
    if request.user.is_authenticated:
        return redirect('jobs:dashboard_redirect')

    if request.method == 'POST':
        form = EmployerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create Company (Tenant)
            company_name = form.cleaned_data['company_name']
            company, _ = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'industry': form.cleaned_data.get('industry', 'Technology'),
                    'location': form.cleaned_data.get('location', 'Remote'),
                    'website': form.cleaned_data.get('website', ''),
                    'description': form.cleaned_data.get('description', '')
                }
            )

            UserProfile.objects.create(
                user=user,
                role='EMPLOYER',
                company=company
            )

            login(request, user)
            messages.success(request, f"Company '{company.name}' registered successfully!")
            return redirect('jobs:employer_dashboard')
    else:
        form = EmployerRegisterForm()

    return render(request, 'jobs/register_employer.html', {'form': form})


def login_view(request):
    """
    Clean unified login view.
    """
    if request.user.is_authenticated:
        return redirect('jobs:dashboard_redirect')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in as {user.username}!")
            return redirect('jobs:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'jobs/login.html')


def logout_view(request):
    """
    Logout view.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('jobs:home')


@login_required
def dashboard_redirect(request):
    """
    Smart router redirecting user to appropriate dashboard based on their role.
    """
    if request.user.is_superuser:
        return redirect('/admin/')
    
    if hasattr(request.user, 'profile') and request.user.profile.is_employer:
        return redirect('jobs:employer_dashboard')

    return redirect('jobs:candidate_dashboard')


def ats_scanner(request):
    """
    Dedicated Interactive ATS Resume Scanner.
    Candidates or visitors can upload any resume or paste resume text,
    select a job posting (or enter custom job specs), and receive an instant
    beautiful visual ATS analysis report with match score, matched skills,
    missing skills, and tailored tips.
    """
    jobs = Job.objects.filter(is_active=True).select_related('company')
    selected_job_id = request.POST.get('job_id') or request.GET.get('job_id') or ''
    selected_job = None
    if selected_job_id:
        selected_job = Job.objects.filter(pk=selected_job_id, is_active=True).first()

    ats_result = None
    resume_text = ""
    job_title = ""
    required_skills = ""
    job_description = ""

    if request.method == 'POST':
        # Get job info either from selected job or custom inputs
        if selected_job:
            job_title = selected_job.title
            required_skills = selected_job.required_skills
            job_description = selected_job.description
        else:
            job_title = request.POST.get('custom_title', 'Software Engineer')
            required_skills = request.POST.get('custom_skills', 'Python, SQL, Django, Git')
            job_description = request.POST.get('custom_description', '')

        # Get resume text from file or text input
        resume_file = request.FILES.get('resume_file')
        pasted_text = request.POST.get('resume_text', '').strip()

        if resume_file:
            resume_text = extract_text_from_file(resume_file)
        elif pasted_text:
            resume_text = pasted_text

        if resume_text:
            ats_result = calculate_ats_score(
                resume_text=resume_text,
                job_title=job_title,
                job_skills_str=required_skills,
                job_description=job_description
            )
            ats_result['matched_skills_list'] = [s.strip() for s in ats_result['matched_skills'].split(',') if s.strip()]
            ats_result['missing_skills_list'] = [s.strip() for s in ats_result['missing_skills'].split(',') if s.strip()]
            ats_result['target_title'] = job_title
            ats_result['target_skills'] = required_skills
        else:
            messages.warning(request, "Please upload a resume file (.pdf, .docx, .txt) or paste your resume text.")

    context = {
        'jobs': jobs,
        'selected_job': selected_job,
        'selected_job_id': selected_job_id,
        'ats_result': ats_result,
        'resume_text': resume_text,
    }
    return render(request, 'jobs/ats_scanner.html', context)

