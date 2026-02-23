from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'avatar', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('role',)}),
    )
