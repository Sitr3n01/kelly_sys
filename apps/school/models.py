from django.db import models
from django.contrib.sites.models import Site
from apps.common.models import TimeStampedModel, SEOModel


class Page(TimeStampedModel, SEOModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True) # HTML Content
    featured_image = models.ImageField(upload_to='school/pages/', blank=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return f'{self.title} ({self.site.name})'


class TeamMember(TimeStampedModel):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='school/team/', blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return self.name


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=200, blank=True)
    quote = models.TextField()
    photo = models.ImageField(upload_to='school/testimonials/', blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return self.name
