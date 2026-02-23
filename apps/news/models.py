import re

from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse

from apps.common.models import SEOModel, TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Article(TimeStampedModel, SEOModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/articles/', blank=True)
    featured_image_caption = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='articles')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimate reading time in minutes (average 200 wpm)."""
        word_count = len(re.findall(r'\w+', self.content))
        return max(1, round(word_count / 200))


class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='newsletter_subscriptions',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'

    def __str__(self):
        return self.email
