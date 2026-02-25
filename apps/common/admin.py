from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import SiteExtension


@admin.register(SiteExtension)
class SiteExtensionAdmin(ModelAdmin):
    list_display = ['site', 'primary_email', 'newsletter_from_email']
    search_fields = ['site__name', 'primary_email']
    fieldsets = [
        ('Site', {
            'fields': ('site',),
        }),
        ('Identidade Visual', {
            'fields': ('tagline', 'logo', 'favicon'),
        }),
        ('Contato', {
            'fields': ('primary_email', 'phone_number', 'address'),
        }),
        ('Newsletter', {
            'fields': ('newsletter_from_email', 'newsletter_from_name'),
            'description': 'Configure o remetente das newsletters. Esse email aparecerá como "De:" quando os assinantes receberem a notificação de novos artigos.',
        }),
        ('Analytics e Redes Sociais', {
            'fields': ('google_analytics_id', 'facebook_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
    ]

