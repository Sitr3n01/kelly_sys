from django import template
from django.utils.safestring import mark_safe

from apps.common.sanitization import sanitize_content

register = template.Library()


@register.filter(name='sanitize_html')
def sanitize_html(value):
    """Sanitiza HTML removendo tags/atributos perigosos, preservando formatação editorial."""
    if not value:
        return ''
    return mark_safe(sanitize_content(value))
