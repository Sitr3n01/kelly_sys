from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    fieldsets = [
        ('Dados de Contato', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
    ]
    actions = ['mark_resolved']

    @admin.action(description='Arquivar mensagens selecionadas')
    def mark_resolved(self, request, queryset):
        # Update to archived instead of resolved since valid choices are:
        # new, read, replied, archived
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} mensagem(ns) arquivada(s).')
