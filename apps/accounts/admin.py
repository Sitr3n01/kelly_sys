from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    list_display = ['username', 'email', 'get_role_display', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('role', 'avatar', 'bio'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('role',),
        }),
    )
