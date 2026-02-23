from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin

from .models import Article, Category, NewsletterSubscription, Tag


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    fieldsets = [
        (None, {'fields': ('name', 'slug', 'parent', 'order')}),
        ('Description', {'fields': ('description',)}),
    ]


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = [
        'title', 'category', 'author', 'site',
        'status', 'published_at', 'is_featured', 'view_count',
    ]
    list_filter = ['status', 'site', 'is_featured', 'category', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'tags']
    date_hierarchy = 'published_at'
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    fieldsets = [
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content'),
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_caption'),
        }),
        ('Classification', {
            'fields': ('category', 'tags'),
        }),
        ('Publication', {
            'fields': ('site', 'author', 'status', 'published_at', 'is_featured'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Stats', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    actions = ['publish_articles', 'archive_articles']

    @admin.action(description='Publish selected articles')
    def publish_articles(self, request, queryset):
        updated = queryset.filter(status=Article.Status.DRAFT).update(
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.message_user(request, f'{updated} article(s) published.')

    @admin.action(description='Archive selected articles')
    def archive_articles(self, request, queryset):
        updated = queryset.update(status=Article.Status.ARCHIVED)
        self.message_user(request, f'{updated} article(s) archived.')


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(ModelAdmin):
    list_display = ['email', 'site', 'is_active', 'created_at']
    list_filter = ['is_active', 'site', 'created_at']
    search_fields = ['email']
    actions = ['export_emails']

    @admin.action(description='Export selected emails as CSV')
    def export_emails(self, request, queryset):
        import csv

        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Site', 'Subscribed At'])
        for sub in queryset:
            writer.writerow([sub.email, sub.site.name, sub.created_at])
        return response
