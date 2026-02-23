from django.db import models
from apps.common.models import TimeStampedModel, SEOModel


class Department(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class JobPosting(TimeStampedModel, SEOModel):
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        INTERNSHIP = 'internship', 'Internship'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    requirements = models.TextField()
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    location = models.CharField(max_length=200, blank=True)
    salary_range = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'

    def __str__(self):
        return self.title


class Application(TimeStampedModel):
    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        REVIEWING = 'reviewing', 'Reviewing'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        INTERVIEW = 'interview', 'Interview'
        REJECTED = 'rejected', 'Rejected'
        ACCEPTED = 'accepted', 'Accepted'

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='hiring/resumes/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.job.title}'
