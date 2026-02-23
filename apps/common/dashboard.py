from django.contrib.admin import site as admin_site
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(login_required, name='dispatch')
class AdminDashboardView(View):
    """Custom admin dashboard with statistics per portal."""

    def get(self, request):
        from apps.contact.models import ContactInquiry
        from apps.hiring.models import Application, JobPosting
        from apps.news.models import Article, Comment, NewsletterSubscription

        context = {
            # Portal Escolar stats
            'open_jobs': JobPosting.objects.filter(status='open').count(),
            'pending_applications': Application.objects.filter(status='pending').count(),
            'unread_messages': ContactInquiry.objects.filter(status='new').count(),

            # Portal de Notícias stats
            'published_articles': Article.objects.filter(status=Article.Status.PUBLISHED).count(),
            'draft_articles': Article.objects.filter(status=Article.Status.DRAFT).count(),
            'newsletter_subscribers': NewsletterSubscription.objects.filter(is_active=True).count(),
            'pending_comments': Comment.objects.filter(is_active=False).count(),

            # Atividade recente
            'recent_articles': (
                Article.objects
                .filter(status=Article.Status.PUBLISHED)
                .select_related('author', 'category')
                .order_by('-published_at')[:5]
            ),
            'recent_applications': (
                Application.objects
                .select_related('job')
                .order_by('-created_at')[:5]
            ),

            # Admin site para manter o contexto correto do admin
            'title': 'Dashboard',
            'has_permission': True,
        }

        # Adicionar contexto padrão do admin
        context.update(admin_site.each_context(request))

        return render(request, 'admin/dashboard.html', context)
