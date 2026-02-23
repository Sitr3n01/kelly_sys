from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import SiteExtension


@admin.register(SiteExtension)
class SiteExtensionAdmin(ModelAdmin):
    list_display = ['site', 'primary_email', 'phone_number']
    search_fields = ['site__name', 'primary_email']
    fieldsets = [
        ('Site', {
            'fields': ('site',),
        }),
        ('Branding', {
            'fields': ('tagline', 'logo', 'favicon'),
        }),
        ('Contact', {
            'fields': ('primary_email', 'phone_number', 'address'),
        }),
        ('Analytics & Social', {
            'fields': ('google_analytics_id', 'facebook_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
    ]
