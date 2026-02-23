from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Application, Department, JobPosting


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    list_display = ['title', 'department', 'employment_type', 'status', 'published_at', 'deadline']
    list_filter = ['status', 'employment_type', 'department']
    search_fields = ['title', 'description', 'requirements']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_at'
    fieldsets = [
        ('Job Details', {
            'fields': ('title', 'slug', 'department', 'employment_type', 'location', 'salary_range'),
        }),
        ('Description', {
            'fields': ('description', 'requirements'),
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'deadline'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    actions = ['open_postings', 'close_postings']

    @admin.action(description='Open selected job postings')
    def open_postings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='open', published_at=timezone.now())
        self.message_user(request, f'{updated} posting(s) opened.')

    @admin.action(description='Close selected job postings')
    def close_postings(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} posting(s) closed.')


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    list_display = ['first_name', 'last_name', 'job', 'status', 'created_at']
    list_filter = ['status', 'job', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['first_name', 'last_name', 'email', 'phone', 'cover_letter', 'resume', 'created_at', 'updated_at']
    fieldsets = [
        ('Applicant', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Application', {
            'fields': ('job', 'cover_letter', 'resume'),
        }),
        ('Review', {
            'fields': ('status', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    actions = ['mark_reviewing', 'mark_approved', 'mark_rejected']

    @admin.action(description='Mark as Under Review')
    def mark_reviewing(self, request, queryset):
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} application(s) marked as reviewing.')

    @admin.action(description='Mark as Approved')
    def mark_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} application(s) approved.')

    @admin.action(description='Mark as Rejected')
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} application(s) rejected.')
