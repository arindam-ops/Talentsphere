from django import forms
from django.contrib.auth.models import User
from .models import Job, Application, Company, UserProfile


class JobPostForm(forms.ModelForm):
    """
    Form for Employers to post and edit jobs.
    """
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'job_type', 'work_mode', 'location',
            'experience_level', 'salary_range', 'required_skills',
            'description', 'responsibilities', 'deadline', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Junior Python Developer'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Development'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote / Bangalore'}),
            'experience_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0-2 Years'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹6,00,000 - ₹9,00,000 / $70k'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, MySQL, Git, REST API'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the role, expectations, and day-to-day work...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key responsibilities and deliverables...'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JobApplyForm(forms.ModelForm):
    """
    Form for Candidates to apply to a Job with their Resume.
    """
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone', 'cover_letter', 'resume_file']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Briefly describe why you are a great fit...'}),
            'resume_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx,.txt'}),
        }


class CandidateRegisterForm(forms.ModelForm):
    """
    Registration form for Candidate / Job Seeker.
    """
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    headline = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aspiring Software Engineer | Python Enthusiast'}))
    skills = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, SQL, HTML, CSS, Git'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class EmployerRegisterForm(forms.ModelForm):
    """
    Registration form for an Employer + Company Tenant.
    """
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    # Company (Tenant) Info
    company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company / Organization Name'}))
    industry = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. IT, FinTech, E-Commerce'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore, India'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourcompany.com'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description of the company...'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose recruiter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HR First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HR Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'recruiter@company.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

