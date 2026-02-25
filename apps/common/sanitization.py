"""
Constantes e utilidades centralizadas de sanitização HTML (bleach).

Usado por:
- apps/news/models.py (Article.save)
- apps/school/models.py (Page.save)
- apps/common/templatetags/sanitize.py (template filter)
"""
import bleach

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
    'ul', 'ol', 'li',
    'a', 'abbr',
    'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'pre', 'code',
    'img', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'hr',
    'iframe',  # para embeds (YouTube etc.) — restrito por attrs
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'loading', 'class'],
    'iframe': ['src', 'width', 'height', 'frameborder', 'allow', 'allowfullscreen'],
    'div': ['class', 'style'],
    'span': ['class', 'style'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    'p': ['class'],
    'h2': ['class', 'id'],
    'h3': ['class', 'id'],
    'h4': ['class', 'id'],
    'pre': ['class'],
    'code': ['class'],
    'blockquote': ['class'],
    'figure': ['class'],
}


def sanitize_content(value):
    """Sanitiza HTML removendo tags/atributos perigosos, preservando formatação editorial."""
    if not value:
        return ''
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
