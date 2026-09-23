from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Global Job Portal & Candidate Routes
    path('', views.home, name='home'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    
    # Employer / Tenant Management Routes
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/job/post/', views.job_create, name='job_create'),
    path('employer/job/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('employer/job/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('employer/applicants/', views.employer_applicants, name='employer_applicants'),
    path('employer/applicants/job/<int:job_id>/', views.employer_applicants, name='employer_applicants_by_job'),
    path('employer/applicant/<int:pk>/status/', views.update_applicant_status, name='update_applicant_status'),

    # Company Showcase, ATS Scanner & Free API
    path('company/<slug:slug>/', views.company_detail, name='company_detail'),
    path('live-jobs/', views.live_api_jobs, name='live_api_jobs'),
    path('ats-scanner/', views.ats_scanner, name='ats_scanner'),

    # Auth & Routing
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('register/employer/', views.register_employer, name='register_employer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]

