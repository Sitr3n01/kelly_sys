from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models

from apps.common.models import SEOModel, TimeStampedModel


class Page(TimeStampedModel, SEOModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='school/pages/', blank=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Página'
        verbose_name_plural = 'Páginas'

    def __str__(self):
        return f'{self.title} ({self.site.name})'

    def save(self, *args, **kwargs):
        from apps.common.sanitization import sanitize_content
        if self.content:
            self.content = sanitize_content(self.content)
        super().save(*args, **kwargs)


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
        verbose_name = 'Membro da Equipe'
        verbose_name_plural = 'Membros da Equipe'

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
        verbose_name = 'Depoimento'
        verbose_name_plural = 'Depoimentos'

    def __str__(self):
        return self.name
