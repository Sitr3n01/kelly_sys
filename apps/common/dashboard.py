from datetime import timedelta

from django.utils import timezone


def dashboard_callback(request, context):
    """Enriquece o contexto do admin index com stats dos portais."""
    from apps.contact.models import ContactInquiry
    from apps.hiring.models import Application, JobPosting
    from apps.news.models import Article, Comment, NewsletterSubscription

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (start_of_month - timedelta(days=1)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    last_draft = (
        Article.objects.filter(status=Article.Status.DRAFT)
        .order_by('-updated_at').first()
    )

    context.update({
        # ── Portal Escolar ──
        'open_jobs': JobPosting.objects.filter(status='open').count(),
        'pending_applications': Application.objects.filter(
            status=Application.Status.RECEIVED).count(),
        'unread_messages': ContactInquiry.objects.filter(status='new').count(),

        # ── Portal de Notícias ──
        'published_articles': Article.objects.filter(
            status=Article.Status.PUBLISHED).count(),
        'draft_articles': Article.objects.filter(
            status=Article.Status.DRAFT).count(),
        'newsletter_subscribers': NewsletterSubscription.objects.filter(
            is_active=True).count(),
        'pending_comments': Comment.objects.filter(is_active=False).count(),

        # ── Tendências ──
        'articles_this_month': Article.objects.filter(
            status=Article.Status.PUBLISHED,
            published_at__gte=start_of_month).count(),
        'articles_last_month': Article.objects.filter(
            status=Article.Status.PUBLISHED,
            published_at__gte=last_month_start,
            published_at__lt=start_of_month).count(),
        'newsletter_today': NewsletterSubscription.objects.filter(
            is_active=True, created_at__gte=start_of_today).count(),
        'last_draft_updated': last_draft.updated_at if last_draft else None,

        # ── Tabelas de atividade ──
        'recent_articles': (
            Article.objects.select_related('author', 'category')
            .order_by('-updated_at')[:5]
        ),
        'recent_applications': (
            Application.objects.select_related('job')
            .order_by('-created_at')[:5]
        ),
        'recent_messages': (
            ContactInquiry.objects.order_by('-created_at')[:5]
        ),
    })
    return context
