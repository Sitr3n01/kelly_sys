from django.contrib import admin
from .models import Department, JobPosting, Application


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'employment_type']
    list_filter = ['status', 'department', 'employment_type']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'job', 'status', 'created_at']
    list_filter = ['status', 'job']
    search_fields = ['first_name', 'last_name', 'email']
