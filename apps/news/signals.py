import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def auto_send_newsletter_on_publish(sender, instance, **kwargs):
    """
    Envia newsletter automaticamente quando um artigo é publicado.

    Guards:
    - Só dispara se status == PUBLISHED (ignora rascunhos/arquivados)
    - Só dispara se newsletter_sent_at is None (idempotência: evita reenvio)
    - Usa .update() para marcar newsletter_sent_at sem disparar post_save novamente
    """
    if instance.status != Article.Status.PUBLISHED:
        return

    if instance.newsletter_sent_at is not None:
        return  # Já enviado — re-salvar artigo publicado não reenvia newsletter

    from .newsletter import send_article_newsletter

    try:
        sent = send_article_newsletter(instance)
        # Usar .update() para não disparar post_save novamente (evita loop infinito)
        Article.objects.filter(pk=instance.pk).update(
            newsletter_sent_at=timezone.now(),
        )
        logger.info(
            'Auto-newsletter: %d email(s) enviado(s) para artigo pk=%s ("%s")',
            sent, instance.pk, instance.title,
        )
    except Exception as e:
        logger.error(
            'Auto-newsletter: falha no envio para artigo pk=%s: %s',
            instance.pk, e,
        )
