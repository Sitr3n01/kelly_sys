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
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Perfil', {'fields': ('role', 'avatar', 'bio')}),
    )
    add_fieldsets = (
        ('Credenciais', {
            'classes': ('wide',),
            'fields': ('username', 'usable_password', 'password1', 'password2'),
            'description': 'Defina o nome de usuário e a senha de acesso.',
        }),
        ('Perfil', {
            'fields': ('role',),
        }),
    )

    class Media:
        css = {
            'all': [],
        }

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['kb_password_fix'] = True
        return super().changeform_view(request, object_id, form_url, extra_context)
