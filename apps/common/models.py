from django.db import models
from django.contrib.sites.models import Site


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SEOModel(models.Model):
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class SiteExtension(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='extension')
    tagline = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='site_logos/', blank=True)
    favicon = models.ImageField(upload_to='site_favicons/', blank=True)
    primary_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    google_analytics_id = models.CharField(max_length=30, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return f'Settings for {self.site.name}'
