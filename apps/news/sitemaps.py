from django.contrib.sitemaps import Sitemap
from django.db.models import Max

from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    # Sem teto, o Django materializa ate 50.000 Article completos por request — e
    # Article carrega `content` (HTML inteiro) e `body` (StreamField JSON). Numa URL
    # publica que crawler bate sem parar, esse era o pico de RSS do worker. Com o
    # indice de sitemaps em config/urls.py, o excedente vira `?p=2`, `?p=3`...
    limit = 1000

    def items(self):
        # .only(): location() so precisa de `slug` (via get_absolute_url) e lastmod()
        # so de `updated_at`. order_by('pk') porque o `ordering` do Meta e
        # `-published_at`, que empata e embaralharia a paginacao entre requests.
        return (
            Article.on_site
            .filter(status=Article.Status.PUBLISHED)
            .only('slug', 'updated_at')
            .order_by('pk')
        )

    def lastmod(self, obj):
        return obj.updated_at

    def get_latest_lastmod(self):
        # A implementacao base faz max([self.lastmod(i) for i in self.items()]),
        # materializando o queryset inteiro so para montar o indice — desfazendo o
        # que o `limit` protege nas paginas. Um aggregate resolve em uma linha.
        return self.items().aggregate(Max('updated_at'))['updated_at__max']
