from django.contrib import admin
from .models import Company, UserProfile, Job, Application


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'location', 'website', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'industry', 'location')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company', 'headline', 'created_at')
    list_filter = ('role', 'company')
    search_fields = ('user__username', 'user__email', 'headline', 'skills')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'work_mode', 'location', 'is_active', 'created_at')
    list_filter = ('job_type', 'work_mode', 'is_active', 'company')
    search_fields = ('title', 'required_skills', 'description', 'company__name')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'ats_score', 'status', 'applied_at')
    list_filter = ('status', 'job__company', 'job')
    search_fields = ('full_name', 'email', 'matched_skills', 'job__title')
    ordering = ('-ats_score', '-applied_at')

