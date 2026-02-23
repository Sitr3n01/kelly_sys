from django.db import models
from django.contrib.sites.models import Site
from apps.common.models import TimeStampedModel


class ContactInquiry(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        READ = 'read', 'Read'
        REPLIED = 'replied', 'Replied'
        ARCHIVED = 'archived', 'Archived'

    class Subject(models.TextChoices):
        GENERAL = 'general', 'General'
        ADMISSIONS = 'admissions', 'Admissions'
        SUPPORT = 'support', 'Support'
        OTHER = 'other', 'Other'

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=50, choices=Subject.choices, default=Subject.GENERAL)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f'{self.name} - {self.subject}'
