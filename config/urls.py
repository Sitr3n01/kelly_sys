from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from apps.news.sitemaps import ArticleSitemap
from apps.school.sitemaps import PageSitemap

sitemaps = {
    'news': ArticleSitemap,
    'school': PageSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('hiring/', include('apps.hiring.urls', namespace='hiring')),
    path('contact/', include('apps.contact.urls', namespace='contact')),
    path('news/', include('apps.news.urls', namespace='news')),
    path('', include('apps.school.urls', namespace='school')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
