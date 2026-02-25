from django.contrib.sitemaps import Sitemap

from .models import Page


class PageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Page.on_site.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
