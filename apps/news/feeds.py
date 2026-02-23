from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Article, Category


class LatestArticlesFeed(Feed):
    title = 'Portal de Notícias - Últimas Notícias'
    description = 'As últimas notícias e eventos da nossa instituição.'

    def link(self):
        return reverse('news:list')

    def items(self):
        return (
            Article.objects
            .filter(status=Article.Status.PUBLISHED)
            .select_related('category', 'author')
            .order_by('-published_at')[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return item.author.get_full_name() if item.author else ''

    def item_categories(self, item):
        return [item.category.name] if item.category else []


class CategoryFeed(Feed):

    def get_object(self, request, slug):
        return Category.objects.get(slug=slug)

    def title(self, obj):
        return f'Portal de Notícias - {obj.name}'

    def link(self, obj):
        return reverse('news:category_detail', kwargs={'slug': obj.slug})

    def description(self, obj):
        return obj.description or f'Artigos da categoria {obj.name}'

    def items(self, obj):
        return (
            Article.objects
            .filter(category=obj, status=Article.Status.PUBLISHED)
            .select_related('author')
            .order_by('-published_at')[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_at
