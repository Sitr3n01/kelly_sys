from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        SCHOOL_ADMIN = 'school_admin', 'School Admin'
        NEWS_EDITOR = 'news_editor', 'News Editor'
        HIRING_MANAGER = 'hiring_manager', 'Hiring Manager'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NEWS_EDITOR,
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        app_label = 'accounts'

    def __str__(self):
        return self.get_full_name() or self.username
