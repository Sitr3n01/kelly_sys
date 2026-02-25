import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import NewsletterSubscription

logger = logging.getLogger(__name__)


def get_newsletter_context(article, site=None, request=None):
    """
    Monta o contexto usado no template de newsletter.
    Reutilizado tanto no envio de email quanto no preview.

    Args:
        request: Se passado (preview no admin), usa request.get_host() para base_url,
                 tornando os links navegáveis no browser. Para envio real de email,
                 deixar None — usa site.domain configurado no banco.
    """
    site = site or article.site

    try:
        site_settings = site.extension
    except AttributeError:
        # SiteExtension não existe para este site (OneToOneField não encontrado)
        site_settings = None

    if request is not None:
        # Preview no admin: usa URL real do servidor para links clicáveis
        protocol = 'https' if request.is_secure() else 'http'
        base_url = f'{protocol}://{request.get_host()}'
    else:
        # Envio real de email: usa domínio configurado no banco (correto para inscritos)
        protocol = 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'
        base_url = f'{protocol}://{site.domain}'

    return {
        'article': article,
        'site': site,
        'site_settings': site_settings,
        'base_url': base_url,
        'article_url': f'{base_url}{article.get_absolute_url()}',
        'unsubscribe_url': f'{base_url}/news/account/?tab=settings',
    }


def get_from_email(site_settings):
    """
    Retorna o remetente da newsletter a partir das configurações do site.
    Formato: 'Nome <email>' ou apenas email.
    """
    if site_settings and site_settings.newsletter_from_email:
        email = site_settings.newsletter_from_email
        name = getattr(site_settings, 'newsletter_from_name', '')
        if name:
            return f'{name} <{email}>'
        return email
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')


def send_article_newsletter(article, site=None):
    """
    Envia email de newsletter para todos os inscritos ativos
    notificando sobre um novo artigo publicado.

    Args:
        article: instancia de Article (deve estar publicado)
        site: instancia de Site (opcional, usa o site do artigo)

    Returns:
        int: numero de emails enviados com sucesso
    """
    from .models import Article as ArticleModel

    if article.status != ArticleModel.Status.PUBLISHED:
        logger.warning(
            'Newsletter: artigo pk=%s não está publicado (status=%s) — envio cancelado',
            article.pk, article.status,
        )
        return 0

    site = site or article.site
    context = get_newsletter_context(article, site)

    subscribers = NewsletterSubscription.objects.filter(
        site=site,
        is_active=True,
    ).values_list('email', flat=True)

    if not subscribers:
        logger.info('Newsletter: nenhum inscrito ativo para o site %s', site.domain)
        return 0

    subject = f'{article.title} — {site.name}'
    html_content = render_to_string('news/email/newsletter_article.html', context)
    text_content = strip_tags(html_content)

    from_email = get_from_email(context.get('site_settings'))

    sent_count = 0
    failed_count = 0

    for email in subscribers:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send(fail_silently=False)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logger.error('Newsletter: falha ao enviar para %s: %s', email, e)

    logger.info(
        'Newsletter enviada: %d sucesso, %d falhas (artigo: %s)',
        sent_count, failed_count, article.title,
    )
    return sent_count
