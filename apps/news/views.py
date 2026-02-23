from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import NewsletterSubscriptionForm
from .models import Article, Category, NewsletterSubscription, Tag
from .utils import get_sidebar_context

User = get_user_model()


def article_list(request):
    """Homepage do portal de noticias com artigo destaque + grid paginado."""
    articles = (
        Article.on_site
        .filter(status=Article.Status.PUBLISHED)
        .select_related('category', 'author')
        .prefetch_related('tags')
    )
    categories = Category.objects.all()

    # Featured: prioriza is_featured=True, senao o mais recente
    featured = articles.filter(is_featured=True).first() or articles.first()

    # Grid: demais artigos (excluindo featured)
    grid_articles = articles.exclude(pk=featured.pk) if featured else articles
    paginator = Paginator(grid_articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'news/article_list.html', {
        'featured': featured,
        'page_obj': page_obj,
        'categories': categories,
        **get_sidebar_context(),
    })


def article_detail(request, slug):
    """Detalhe do artigo com artigos relacionados."""
    article = get_object_or_404(
        Article.on_site.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status=Article.Status.PUBLISHED,
    )

    # Incrementar view_count atomicamente
    Article.on_site.filter(pk=article.pk).update(view_count=F('view_count') + 1)
    article.refresh_from_db(fields=['view_count'])

    # Artigos relacionados (mesma categoria, excluindo atual)
    related_articles = Article.objects.none()
    if article.category:
        related_articles = (
            Article.on_site
            .filter(status=Article.Status.PUBLISHED, category=article.category)
            .exclude(pk=article.pk)
            .select_related('category')
            .order_by('-published_at')[:3]
        )

    return render(request, 'news/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
        **get_sidebar_context(),
    })


def category_detail(request, slug):
    """Artigos de uma categoria especifica."""
    category = get_object_or_404(Category, slug=slug)
    articles = (
        Article.on_site
        .filter(category=category, status=Article.Status.PUBLISHED)
        .select_related('category', 'author')
        .prefetch_related('tags')
    )
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'news/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        **get_sidebar_context(),
    })


def tag_detail(request, slug):
    """Artigos filtrados por tag."""
    tag = get_object_or_404(Tag, slug=slug)
    articles = (
        Article.on_site
        .filter(tags=tag, status=Article.Status.PUBLISHED)
        .select_related('category', 'author')
        .prefetch_related('tags')
    )
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'news/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj,
        **get_sidebar_context(),
    })


def author_detail(request, username):
    """Perfil do autor com seus artigos publicados."""
    author = get_object_or_404(User, username=username)
    articles = (
        Article.on_site
        .filter(author=author, status=Article.Status.PUBLISHED)
        .select_related('category')
        .prefetch_related('tags')
    )
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'news/author_detail.html', {
        'author': author,
        'page_obj': page_obj,
        **get_sidebar_context(),
    })


def article_search(request):
    """Busca de artigos por titulo, excerpt, conteudo ou tags."""
    query = request.GET.get('q', '').strip()
    articles = Article.objects.none()

    if query:
        articles = (
            Article.on_site
            .filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query),
                status=Article.Status.PUBLISHED,
            )
            .distinct()
            .select_related('category', 'author')
        )

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.htmx:
        return render(request, 'news/partials/search_results.html', {
            'page_obj': page_obj,
            'query': query,
        })

    return render(request, 'news/search.html', {
        'page_obj': page_obj,
        'query': query,
        **get_sidebar_context(),
    })


def article_archive(request, year, month=None):
    """Arquivo de artigos por ano e mes opcional."""
    articles = (
        Article.on_site
        .filter(
            status=Article.Status.PUBLISHED,
            published_at__year=year,
        )
        .select_related('category', 'author')
    )
    if month:
        articles = articles.filter(published_at__month=month)

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'news/archive.html', {
        'page_obj': page_obj,
        'year': year,
        'month': month,
        **get_sidebar_context(),
    })


def article_list_page(request):
    """Endpoint HTMX para load-more na listagem principal."""
    if not request.htmx:
        return redirect('news:list')

    articles = (
        Article.on_site
        .filter(status=Article.Status.PUBLISHED)
        .select_related('category', 'author')
    )
    paginator = Paginator(articles, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'news/partials/article_grid.html', {'page_obj': page_obj})


@require_POST
def newsletter_subscribe(request):
    """Inscricao na newsletter (POST only, suporte HTMX)."""
    form = NewsletterSubscriptionForm(request.POST)
    if form.is_valid():
        site = get_current_site(request)
        obj, created = NewsletterSubscription.objects.get_or_create(
            email=form.cleaned_data['email'],
            site=site,
            defaults={'is_active': True},
        )
        if not created:
            obj.is_active = True
            obj.save(update_fields=['is_active'])
        if request.htmx:
            return render(request, 'news/partials/newsletter_success.html')
        messages.success(request, "Inscrição realizada com sucesso!")
        return redirect(request.META.get('HTTP_REFERER', 'news:list'))
    if request.htmx:
        return render(request, 'news/partials/newsletter_error.html', {'form': form})
    messages.error(request, "E-mail inválido. Tente novamente.")
    return redirect(request.META.get('HTTP_REFERER', 'news:list'))
