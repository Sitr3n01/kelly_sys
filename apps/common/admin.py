from django.contrib import admin
from .models import SiteExtension


@admin.register(SiteExtension)
class SiteExtensionAdmin(admin.ModelAdmin):
    list_display = ['site', 'primary_email', 'phone_number']
    fieldsets = [
        ('Site', {'fields': ('site',)}),
        ('Branding', {'fields': ('tagline', 'logo', 'favicon')}),
        ('Contact', {'fields': ('primary_email', 'phone_number', 'address')}),
        ('Analytics', {'fields': ('google_analytics_id',)}),
        ('Social Media', {'fields': ('facebook_url', 'instagram_url', 'youtube_url')}),
    ]
