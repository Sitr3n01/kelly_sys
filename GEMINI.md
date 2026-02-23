# GEMINI.md — Instruções de Código para o Projeto Kelly Sys

> Este arquivo contém as instruções que o Gemini deve seguir para escrever código.
> O Claude (orquestrador) atualiza este arquivo antes de cada sessão.
> **Leia SEMPRE a seção "Tarefa Atual" antes de começar a codar.**

---

## Visão Geral do Projeto

**Kelly Sys** é um sistema Django que gerencia dois sites:
1. **Site da Escola** — institucional com contratação e contato
2. **Portal de Notícias** — portal público do mesmo grupo

Ambos compartilham um banco de dados e um painel admin (Django Unfold).

---

## Stack e Versões

| Tecnologia | Versão | Notas |
|-----------|--------|-------|
| Python | 3.12+ | Usar type hints onde faz sentido |
| Django | 5.1+ | LTS preferido |
| PostgreSQL | 16 | Via Docker em dev |
| HTMX | 2.x | Incluir via CDN ou static |
| Alpine.js | 3.x | Incluir via CDN ou static |
| Django Unfold | 0.40+ | Tema admin Tailwind |
| WhiteNoise | 6.5+ | Servir statics |
| psycopg | 3.x | `psycopg[binary]` |
| Pillow | 10+ | Processamento de imagem |
| django-htmx | 1.17+ | Middleware HTMX |
| django-imagekit | 5+ | Thumbnails |
| django-environ | 0.11+ | Variáveis de ambiente |

---

## Convenções de Código

### Python
- **Imports:** stdlib → django → third-party → local apps (isort order)
- **Strings:** aspas simples `'texto'` para Python, aspas duplas `"texto"` para strings de UI
- **Models:** sempre definir `__str__`, `Meta.ordering`, `verbose_name` quando não óbvio
- **ForeignKey:** sempre `on_delete=` explícito e `related_name=`
- **Campos opcionais:** `blank=True` para todos; `null=True` apenas para non-string fields
- **Upload paths:** sempre definir `upload_to=` com subpastas organizadas

### Django Apps
- Todos os apps ficam dentro de `apps/`
- Registrados em INSTALLED_APPS como `'apps.nome_do_app'`
- Cada app tem `apps.py` com `name = 'apps.nome_do_app'`

### Admin
- Usar `@admin.register(Model)` (decorator, não `admin.site.register`)
- **Importar `ModelAdmin` de `unfold.admin`** (não de `django.contrib.admin`)
- Configurar: `list_display`, `list_filter`, `search_fields`, `prepopulated_fields`
- Organizar campos com `fieldsets`

### Templates
- Indentação: 2 espaços
- Naming: `snake_case.html`
- Usar `{% url 'namespace:name' %}` para links
- Usar `{% static 'path' %}` para statics
- Usar `{% csrf_token %}` em todo formulário POST
- Todas as imagens com `loading="lazy"` (exceto hero/above the fold que usa `loading="eager"`)

### URLs
- Cada app tem seu `urls.py` com `app_name`
- Patterns sempre nomeados: `path('', views.home, name='home')`
- Slugs para conteúdo público
- **IMPORTANTE:** `<slug:slug>/` deve ser sempre a ÚLTIMA rota para não capturar outras paths

### Views
- Usar Function-Based Views (FBV) — padrão do projeto
- SEMPRE usar `select_related()` e `prefetch_related()` em queries com ForeignKey/M2M
- Usar `Paginator` para listagens (12 items por página padrão)
- Suporte HTMX: verificar `request.htmx` para retornar partials

---

## Independência dos Portais (Escola vs Notícias)

O sistema "Kelly Sys" compartilha o mesmo banco de dados (e o mesmo Django Admin Unfold) para servir a **dois sites distintos** da mesma empresa: a Escola e o Portal de Notícias. O layout, paleta de cores e o modo de exibição de ambos devem ser completamente distintos e independentes para o usuário final, para que **não pareçam ser o mesmo portal**.

**Regras Essenciais de UI/UX para os Dois Portais:**

1. **Separação Visual:**
   - O projeto deve usar temas/paletas diferentes para o Portal de Notícias vs a Escola (ex: fontes institucionais vs fontes editoriais). Use templates customizados (`base_school.html` e `base_news.html`) que herdem lógicas distintas se necessário, ou injetem variáveis de cor diferentes no TailwindCSS.
   - Os domínios simulados ou *apps* atuam como silos de layout diferentes, compartilhando a mesma casca técnica mas não o estilo.

2. **Interligação Elegante na Navbar:**
   - Embora sejam sites com propostas diferentes, são da mesma empresa. Portanto, a `navbar` principal de ambos deve conter um "Link Útil" ou "Botão de Destaque" discreto que leve de um portal para o outro (Ex: na Escola há um botão "Ir para as Notícias", e nas Notícias há um botão "Conheça a nossa Escola").

3. **Arquitetura de Dados:**
   - Ambas as estruturas dividem os mesmos usuários e configs passados pelo painel `SiteExtension` ou podem ter dois modelos *Site* distintos configurados pelo Django `contrib.sites`.
   - Views de notícias não devem herdar o "Hero institucional" da escola, e Views da escola não devem herdar "Sidebar editorial" de notícias.

---

## Tarefa Atual

### 🎯 FASE 6: Admin Enhancement — Painel Unificado Bilíngue

**Objetivo:** Transformar o painel Django admin de uma interface técnica genérica em um painel profissional, simples e bilíngue (PT/EN), agrupado por portal, com dashboard de estatísticas e acessível para usuários sem conhecimento técnico.

**Execute TODAS as sub-fases abaixo (A até E) em sequência. Ao final, execute `manage.py check` e confirme zero erros.**

---

#### FASE 6A — Migrar Todos os admin.py para Unfold

**Arquivos a modificar:**
- `apps/school/admin.py`
- `apps/hiring/admin.py`
- `apps/contact/admin.py`
- `apps/accounts/admin.py`
- `apps/common/admin.py`

**Regra:** Em cada arquivo, substituir `from django.contrib import admin` e herança de `admin.ModelAdmin` por `unfold.admin.ModelAdmin`. Manter toda lógica existente intacta.

##### 6A.1 — apps/school/admin.py

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Page, TeamMember, Testimonial


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ['title', 'site', 'is_published', 'order', 'updated_at']
    list_filter = ['is_published', 'site']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Content', {
            'fields': ('title', 'slug', 'content', 'featured_image'),
        }),
        ('Publication', {
            'fields': ('site', 'is_published', 'order'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'title', 'bio']
    ordering = ['order', 'name']
    fieldsets = [
        (None, {'fields': ('name', 'title', 'photo', 'bio', 'email')}),
        ('Display', {'fields': ('is_active', 'order')}),
    ]


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['name', 'relationship', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['name', 'quote']
    actions = ['feature_selected', 'unfeature_selected']

    @admin.action(description='Feature selected testimonials')
    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonial(s) featured.')

    @admin.action(description='Unfeature selected testimonials')
    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} testimonial(s) unfeatured.')
```

##### 6A.2 — apps/hiring/admin.py

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Application, Department, JobPosting


@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    list_display = ['title', 'department', 'employment_type', 'status', 'published_at', 'deadline']
    list_filter = ['status', 'employment_type', 'department']
    search_fields = ['title', 'description', 'requirements']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_at'
    fieldsets = [
        ('Job Details', {
            'fields': ('title', 'slug', 'department', 'employment_type', 'location', 'salary_range'),
        }),
        ('Description', {
            'fields': ('description', 'requirements'),
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'deadline'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    actions = ['open_postings', 'close_postings']

    @admin.action(description='Open selected job postings')
    def open_postings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='open', published_at=timezone.now())
        self.message_user(request, f'{updated} posting(s) opened.')

    @admin.action(description='Close selected job postings')
    def close_postings(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} posting(s) closed.')


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    list_display = ['first_name', 'last_name', 'job', 'status', 'created_at']
    list_filter = ['status', 'job', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['first_name', 'last_name', 'email', 'phone', 'cover_letter', 'resume', 'created_at', 'updated_at']
    fieldsets = [
        ('Applicant', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Application', {
            'fields': ('job', 'cover_letter', 'resume'),
        }),
        ('Review', {
            'fields': ('status', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]
    actions = ['mark_reviewing', 'mark_approved', 'mark_rejected']

    @admin.action(description='Mark as Under Review')
    def mark_reviewing(self, request, queryset):
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} application(s) marked as reviewing.')

    @admin.action(description='Mark as Approved')
    def mark_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} application(s) approved.')

    @admin.action(description='Mark as Rejected')
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} application(s) rejected.')
```

##### 6A.3 — apps/contact/admin.py

Verificar como o model ContactInquiry está definido e adaptar:

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    fieldsets = [
        ('Contact Details', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
    ]
    actions = ['mark_resolved']

    @admin.action(description='Mark selected inquiries as resolved')
    def mark_resolved(self, request, queryset):
        # Verificar o valor correto do status 'resolved' no model
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} inquiry(ies) marked as resolved.')
```

**IMPORTANTE:** Verificar os valores de `status` choices no model `ContactInquiry` antes de usar `'resolved'` — adaptar conforme necessário.

##### 6A.4 — apps/accounts/admin.py

**Caso especial:** deve herdar de `ModelAdmin` (Unfold) E `UserAdmin` (Django). Ordem: `ModelAdmin` primeiro.

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    list_display = ['username', 'email', 'get_role_display', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('role', 'avatar', 'bio'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('role',),
        }),
    )
```

##### 6A.5 — apps/common/admin.py

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import SiteExtension


@admin.register(SiteExtension)
class SiteExtensionAdmin(ModelAdmin):
    list_display = ['site', 'primary_email', 'phone_number']
    search_fields = ['site__name', 'primary_email']
    fieldsets = [
        ('Site', {
            'fields': ('site',),
        }),
        ('Branding', {
            'fields': ('tagline', 'logo', 'favicon'),
        }),
        ('Contact', {
            'fields': ('primary_email', 'phone_number', 'address'),
        }),
        ('Analytics & Social', {
            'fields': ('google_analytics_id', 'facebook_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
    ]
```

---

#### FASE 6B — Configurar UNFOLD Settings

**Arquivo a modificar:** `config/settings/base.py`

Adicionar APÓS os imports (no topo) e ANTES de `INSTALLED_APPS`:

```python
from django.urls import reverse_lazy
```

Adicionar o bloco `UNFOLD` após `DEFAULT_AUTO_FIELD`:

```python
# ── Django Unfold Admin Configuration ──────────────────────────────────────
UNFOLD = {
    'SITE_TITLE': 'Kelly Sys',
    'SITE_HEADER': 'Painel de Administração',
    'SITE_URL': '/',
    'SITE_ICON': None,  # Deixar None ou apontar para um favicon estático
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'COLORS': {
        'primary': {
            '50': '239 246 255',
            '100': '219 234 254',
            '200': '191 219 254',
            '300': '147 197 253',
            '400': '96 165 250',
            '500': '59 130 246',
            '600': '17 82 212',   # #1152d4 — cor primária do projeto
            '700': '29 78 216',
            '800': '30 64 175',
            '900': '30 58 138',
            '950': '23 37 84',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Portal Escolar',
                'separator': True,
                'items': [
                    {
                        'title': 'Páginas',
                        'icon': 'article',
                        'link': reverse_lazy('admin:school_page_changelist'),
                        'permission': lambda request: request.user.has_perm('school.view_page'),
                    },
                    {
                        'title': 'Equipe',
                        'icon': 'group',
                        'link': reverse_lazy('admin:school_teammember_changelist'),
                        'permission': lambda request: request.user.has_perm('school.view_teammember'),
                    },
                    {
                        'title': 'Depoimentos',
                        'icon': 'format_quote',
                        'link': reverse_lazy('admin:school_testimonial_changelist'),
                        'permission': lambda request: request.user.has_perm('school.view_testimonial'),
                    },
                    {
                        'title': 'Vagas',
                        'icon': 'work',
                        'link': reverse_lazy('admin:hiring_jobposting_changelist'),
                        'permission': lambda request: request.user.has_perm('hiring.view_jobposting'),
                    },
                    {
                        'title': 'Departamentos',
                        'icon': 'business',
                        'link': reverse_lazy('admin:hiring_department_changelist'),
                        'permission': lambda request: request.user.has_perm('hiring.view_department'),
                    },
                    {
                        'title': 'Candidaturas',
                        'icon': 'description',
                        'link': reverse_lazy('admin:hiring_application_changelist'),
                        'permission': lambda request: request.user.has_perm('hiring.view_application'),
                    },
                    {
                        'title': 'Mensagens de Contato',
                        'icon': 'contact_mail',
                        'link': reverse_lazy('admin:contact_contactinquiry_changelist'),
                        'permission': lambda request: request.user.has_perm('contact.view_contactinquiry'),
                    },
                ],
            },
            {
                'title': 'Portal de Notícias',
                'separator': True,
                'items': [
                    {
                        'title': 'Artigos',
                        'icon': 'newspaper',
                        'link': reverse_lazy('admin:news_article_changelist'),
                        'permission': lambda request: request.user.has_perm('news.view_article'),
                    },
                    {
                        'title': 'Categorias',
                        'icon': 'category',
                        'link': reverse_lazy('admin:news_category_changelist'),
                        'permission': lambda request: request.user.has_perm('news.view_category'),
                    },
                    {
                        'title': 'Tags',
                        'icon': 'label',
                        'link': reverse_lazy('admin:news_tag_changelist'),
                        'permission': lambda request: request.user.has_perm('news.view_tag'),
                    },
                    {
                        'title': 'Comentários',
                        'icon': 'chat',
                        'link': reverse_lazy('admin:news_comment_changelist'),
                        'permission': lambda request: request.user.has_perm('news.view_comment'),
                    },
                    {
                        'title': 'Newsletter',
                        'icon': 'mail',
                        'link': reverse_lazy('admin:news_newslettersubscription_changelist'),
                        'permission': lambda request: request.user.has_perm('news.view_newslettersubscription'),
                    },
                ],
            },
            {
                'title': 'Sistema',
                'separator': True,
                'items': [
                    {
                        'title': 'Usuários',
                        'icon': 'manage_accounts',
                        'link': reverse_lazy('admin:accounts_customuser_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': 'Configurações do Site',
                        'icon': 'settings',
                        'link': reverse_lazy('admin:common_siteextension_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': 'Sites',
                        'icon': 'language',
                        'link': reverse_lazy('admin:sites_site_changelist'),
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
}
```

**IMPORTANTE:** `reverse_lazy` deve ser importado no topo do arquivo settings com `from django.urls import reverse_lazy`. Confirmar que este import existe antes de adicionar o bloco UNFOLD.

---

#### FASE 6C — Dashboard Customizado com Estatísticas

**Arquivo a criar:** `apps/common/dashboard.py`

Este arquivo implementa uma view customizada que substitui a home do admin com cards de estatísticas reais.

```python
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
```

**Arquivo a criar:** `templates/admin/dashboard.html`

```html
{% extends "admin/base_site.html" %}
{% load i18n %}

{% block content %}
<div class="py-8">

  <!-- Boas-vindas -->
  <div class="mb-8 p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {% blocktrans with name=request.user.get_full_name|default:request.user.username %}Bem-vindo, {{ name }}{% endblocktrans %}
      </h1>
      <p class="text-sm text-gray-500 mt-1">
        {% trans "Painel de controle — Kelly Sys" %}
      </p>
    </div>
    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
      {{ request.user.get_role_display|default:"Staff" }}
    </span>
  </div>

  <!-- Estatísticas em 2 colunas -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">

    <!-- Portal Escolar -->
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm p-6">
      <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4 flex items-center gap-2">
        <span class="material-symbols-outlined text-[18px]">school</span>
        {% trans "Portal Escolar" %}
      </h2>
      <div class="grid grid-cols-3 gap-4">
        <a href="{% url 'admin:hiring_jobposting_changelist' %}?status=open" class="flex flex-col items-center p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors">
          <span class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ open_jobs }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Vagas Abertas" %}</span>
        </a>
        <a href="{% url 'admin:hiring_application_changelist' %}?status=pending" class="flex flex-col items-center p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 hover:bg-amber-100 transition-colors">
          <span class="text-3xl font-bold text-amber-600 dark:text-amber-400">{{ pending_applications }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Candidaturas" %}</span>
        </a>
        <a href="{% url 'admin:contact_contactinquiry_changelist' %}?status=new" class="flex flex-col items-center p-4 rounded-lg bg-red-50 dark:bg-red-900/20 hover:bg-red-100 transition-colors">
          <span class="text-3xl font-bold text-red-600 dark:text-red-400">{{ unread_messages }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Mensagens" %}</span>
        </a>
      </div>
    </div>

    <!-- Portal de Notícias -->
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm p-6">
      <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4 flex items-center gap-2">
        <span class="material-symbols-outlined text-[18px]">newspaper</span>
        {% trans "Portal de Notícias" %}
      </h2>
      <div class="grid grid-cols-2 gap-4">
        <a href="{% url 'admin:news_article_changelist' %}?status=published" class="flex flex-col items-center p-4 rounded-lg bg-green-50 dark:bg-green-900/20 hover:bg-green-100 transition-colors">
          <span class="text-3xl font-bold text-green-600 dark:text-green-400">{{ published_articles }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Publicados" %}</span>
        </a>
        <a href="{% url 'admin:news_article_changelist' %}?status=draft" class="flex flex-col items-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 transition-colors">
          <span class="text-3xl font-bold text-gray-600 dark:text-gray-400">{{ draft_articles }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Rascunhos" %}</span>
        </a>
        <a href="{% url 'admin:news_newslettersubscription_changelist' %}?is_active=True" class="flex flex-col items-center p-4 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 transition-colors">
          <span class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{{ newsletter_subscribers }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Assinantes" %}</span>
        </a>
        <a href="{% url 'admin:news_comment_changelist' %}?is_active=False" class="flex flex-col items-center p-4 rounded-lg bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 transition-colors">
          <span class="text-3xl font-bold text-orange-600 dark:text-orange-400">{{ pending_comments }}</span>
          <span class="text-xs text-gray-500 mt-1 text-center">{% trans "Comentários para revisar" %}</span>
        </a>
      </div>
    </div>
  </div>

  <!-- Ações Rápidas -->
  <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm p-6 mb-8">
    <h2 class="text-sm font-bold uppercase tracking-widest text-gray-400 mb-4">{% trans "Ações Rápidas" %}</h2>
    <div class="flex flex-wrap gap-3">
      <a href="{% url 'admin:news_article_add' %}" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
        <span class="material-symbols-outlined text-[16px]">add</span>
        {% trans "Novo Artigo" %}
      </a>
      <a href="{% url 'admin:hiring_jobposting_add' %}" class="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <span class="material-symbols-outlined text-[16px]">work</span>
        {% trans "Nova Vaga" %}
      </a>
      <a href="{% url 'admin:hiring_application_changelist' %}" class="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <span class="material-symbols-outlined text-[16px]">description</span>
        {% trans "Ver Candidaturas" %}
      </a>
      <a href="{% url 'admin:contact_contactinquiry_changelist' %}" class="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <span class="material-symbols-outlined text-[16px]">contact_mail</span>
        {% trans "Mensagens" %}
      </a>
    </div>
  </div>

  <!-- Atividade Recente — 2 colunas -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

    <!-- Últimos Artigos -->
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-sm font-bold text-gray-700 dark:text-gray-300">{% trans "Últimos Artigos" %}</h2>
        <a href="{% url 'admin:news_article_changelist' %}" class="text-xs text-blue-600 hover:underline">{% trans "Ver todos" %}</a>
      </div>
      <table class="w-full text-sm">
        {% for article in recent_articles %}
        <tr class="border-b border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
          <td class="px-6 py-3">
            <a href="{% url 'admin:news_article_change' article.pk %}" class="font-medium text-gray-900 dark:text-white hover:text-blue-600 line-clamp-1">{{ article.title }}</a>
            <div class="text-xs text-gray-400 mt-0.5">{{ article.author.get_full_name|default:article.author.username }} · {{ article.published_at|date:"d/m/Y" }}</div>
          </td>
          <td class="px-6 py-3 text-right">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold
              {% if article.status == 'published' %}bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300
              {% elif article.status == 'draft' %}bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400
              {% else %}bg-orange-100 text-orange-700{% endif %}">
              {{ article.get_status_display }}
            </span>
          </td>
        </tr>
        {% empty %}
        <tr><td colspan="2" class="px-6 py-6 text-center text-gray-400 text-sm">{% trans "Nenhum artigo publicado ainda." %}</td></tr>
        {% endfor %}
      </table>
    </div>

    <!-- Últimas Candidaturas -->
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-sm font-bold text-gray-700 dark:text-gray-300">{% trans "Últimas Candidaturas" %}</h2>
        <a href="{% url 'admin:hiring_application_changelist' %}" class="text-xs text-blue-600 hover:underline">{% trans "Ver todas" %}</a>
      </div>
      <table class="w-full text-sm">
        {% for app in recent_applications %}
        <tr class="border-b border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
          <td class="px-6 py-3">
            <a href="{% url 'admin:hiring_application_change' app.pk %}" class="font-medium text-gray-900 dark:text-white hover:text-blue-600">{{ app.first_name }} {{ app.last_name }}</a>
            <div class="text-xs text-gray-400 mt-0.5">{{ app.job.title }} · {{ app.created_at|date:"d/m/Y" }}</div>
          </td>
          <td class="px-6 py-3 text-right">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold
              {% if app.status == 'pending' %}bg-yellow-100 text-yellow-800
              {% elif app.status == 'reviewing' %}bg-blue-100 text-blue-800
              {% elif app.status == 'approved' %}bg-green-100 text-green-800
              {% else %}bg-red-100 text-red-800{% endif %}">
              {{ app.get_status_display }}
            </span>
          </td>
        </tr>
        {% empty %}
        <tr><td colspan="2" class="px-6 py-6 text-center text-gray-400 text-sm">{% trans "Nenhuma candidatura ainda." %}</td></tr>
        {% endfor %}
      </table>
    </div>
  </div>

</div>
{% endblock %}
```

**Registrar o dashboard no settings e urls:**

Em `config/settings/base.py`, adicionar dentro do bloco `UNFOLD`:

```python
'INDEX_DASHBOARD': 'apps.common.dashboard.AdminDashboardView',
```

**IMPORTANTE:** A chave `INDEX_DASHBOARD` aponta para a classe view, não para uma URL.

---

#### FASE 6D — i18n PT/BR no Admin

**Arquivo a modificar:** `config/settings/base.py`

1. Adicionar `LANGUAGES` logo após `LANGUAGE_CODE`:

```python
LANGUAGE_CODE = 'pt-br'
LANGUAGES = [
    ('pt-br', 'Português (BR)'),
    ('en', 'English'),
]
```

2. Adicionar `LocaleMiddleware` no MIDDLEWARE entre `SessionMiddleware` e `CommonMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # ← ADICIONAR AQUI
    'django.middleware.common.CommonMiddleware',
    # ... resto igual
]
```

**Arquivo a modificar:** `config/urls.py`

Adicionar antes das urlpatterns existentes:

```python
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

# No urlpatterns, adicionar:
path('i18n/', include('django.conf.urls.i18n')),
```

A linha completa do urlpatterns ficará:

```python
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    # ... resto igual
]
```

---

#### FASE 6E — Validação Final

Após implementar todas as fases, executar:

```bash
python manage.py check
```

**Zero erros é obrigatório antes de concluir.**

Verificações manuais:
1. Abrir `/admin/` e confirmar que a sidebar mostra 3 grupos: "Portal Escolar", "Portal de Notícias", "Sistema"
2. Confirmar que a home do admin mostra cards de estatísticas (não a lista padrão de apps)
3. Confirmar que todos os admin.py usam `unfold.admin.ModelAdmin`:
   ```bash
   grep -r "from unfold.admin import ModelAdmin" apps/
   ```
4. Confirmar que o admin exibe textos em português por padrão
5. Confirmar que o link `/i18n/set_language/` funciona (seletor de idioma)

---

### Checklist de Aceite (marque antes de entregar)

- [ ] `manage.py check` → 0 erros
- [ ] Sidebar mostra Portal Escolar / Portal de Notícias / Sistema
- [ ] Dashboard home com cards de stats reais
- [ ] Todos os admin.py importam de `unfold.admin`
- [ ] Admin em português por padrão
- [ ] `LocaleMiddleware` adicionado ao MIDDLEWARE
- [ ] `LANGUAGES` configurado no settings
- [ ] `i18n/` path no urlpatterns
- [ ] Template `templates/admin/dashboard.html` criado

##### 5A.1 — Adicionar `get_absolute_url()` e `reading_time` ao model Article

Em `apps/news/models.py`, adicionar ao class `Article`:

```python
from django.urls import reverse
import re

# Dentro da class Article:

def get_absolute_url(self):
    return reverse('news:article_detail', kwargs={'slug': self.slug})

@property
def reading_time(self):
    """Estimate reading time in minutes (average 200 wpm)."""
    word_count = len(re.findall(r'\w+', self.content))
    return max(1, round(word_count / 200))
```

##### 5A.2 — Corrigir view_count com F() no article_detail

Em `apps/news/views.py`, o `article_detail` atual faz:
```python
article.view_count += 1
article.save(update_fields=['view_count'])
```

Substituir por (atômico, sem race condition):
```python
from django.db.models import F

# Dentro de article_detail, APÓS obter o article:
Article.on_site.filter(pk=article.pk).update(view_count=F('view_count') + 1)
article.refresh_from_db(fields=['view_count'])
```

##### 5A.3 — Adicionar select_related/prefetch_related em TODAS as views

Otimizar queries em `article_list`, `article_detail`, e `category_detail`:

```python
# article_list
articles = (
    Article.on_site
    .filter(status=Article.Status.PUBLISHED)
    .select_related('category', 'author')
    .prefetch_related('tags')
)

# article_detail
article = get_object_or_404(
    Article.on_site.select_related('category', 'author').prefetch_related('tags'),
    slug=slug,
    status=Article.Status.PUBLISHED,
)

# category_detail
articles = (
    Article.on_site
    .filter(category=category, status=Article.Status.PUBLISHED)
    .select_related('category', 'author')
    .prefetch_related('tags')
)
```

##### 5A.4 — Criar apps/news/utils.py

```python
from django.db.models import Count


def get_sidebar_context():
    """Return sidebar data: popular articles, top categories, top tags."""
    from .models import Article, Category, Tag

    popular_articles = (
        Article.objects
        .filter(status=Article.Status.PUBLISHED)
        .order_by('-view_count')[:5]
        .select_related('category')
    )
    top_categories = (
        Category.objects
        .annotate(article_count=Count('articles', filter=__import__('django.db.models').Q(articles__status='published')))
        .filter(article_count__gt=0)
        .order_by('-article_count')[:8]
    )
    top_tags = (
        Tag.objects
        .annotate(article_count=Count('articles', filter=__import__('django.db.models').Q(articles__status='published')))
        .filter(article_count__gt=0)
        .order_by('-article_count')[:20]
    )
    return {
        'popular_articles': popular_articles,
        'top_categories': top_categories,
        'top_tags': top_tags,
    }
```

**NOTA:** O import inline de Q acima é apenas para referência. Na prática, importe `Q` no topo do arquivo:
```python
from django.db.models import Count, Q
```

E use:
```python
top_categories = (
    Category.objects
    .annotate(article_count=Count('articles', filter=Q(articles__status='published')))
    .filter(article_count__gt=0)
    .order_by('-article_count')[:8]
)
```

**Critério de aceite 5A:**
- `python manage.py check` sem erros
- `Article.get_absolute_url()` retorna URL correta
- Sitemap em `/sitemap.xml` renderiza sem erro
- Views usam queries otimizadas

---

#### FASE 5B — Model Newsletter + Forms

**Arquivos a modificar:** `apps/news/models.py`, `apps/news/views.py`, `apps/news/admin.py`
**Arquivo a criar:** `apps/news/forms.py`
**Migration:** SIM — rodar `python manage.py makemigrations news && python manage.py migrate`

##### 5B.1 — Adicionar NewsletterSubscription ao models.py

Em `apps/news/models.py`, adicionar:

```python
class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='newsletter_subscriptions',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'

    def __str__(self):
        return self.email
```

##### 5B.2 — Criar apps/news/forms.py

```python
from django import forms

from .models import NewsletterSubscription


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Seu melhor e-mail',
                'class': 'flex-grow rounded-full border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 px-6 py-4',
            })
        }
```

##### 5B.3 — Adicionar view newsletter_subscribe

Em `apps/news/views.py`, adicionar:

```python
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscription


@require_POST
def newsletter_subscribe(request):
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
```

##### 5B.4 — Registrar NewsletterSubscriptionAdmin

Em `apps/news/admin.py`, adicionar:

```python
from .models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
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
```

**Critério de aceite 5B:**
- Migration criada e aplicada sem erro
- `NewsletterSubscription` aparece no admin
- Action de export CSV funciona

---

#### FASE 5C — Novas Views e URLs

**Arquivos a modificar:** `apps/news/views.py`, `apps/news/urls.py`
**Migration:** NÃO

##### 5C.1 — Reescrever apps/news/views.py completo

O arquivo final deve conter TODAS as views (existentes corrigidas + novas):

```python
import re

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import NewsletterSubscriptionForm
from .models import Article, Category, NewsletterSubscription, Tag
from .utils import get_sidebar_context


def article_list(request):
    """Homepage do portal de notícias com artigo destaque + grid paginado."""
    articles = (
        Article.on_site
        .filter(status=Article.Status.PUBLISHED)
        .select_related('category', 'author')
        .prefetch_related('tags')
    )
    categories = Category.objects.all()

    # Featured: primeiro artigo (ou is_featured=True se existir)
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
    """Artigos de uma categoria específica."""
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
    from django.contrib.auth import get_user_model
    User = get_user_model()
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
    """Busca de artigos por título, excerpt, conteúdo ou tags."""
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
    """Arquivo de artigos por ano e mês opcional."""
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
    """Inscrição na newsletter (POST only, suporte HTMX)."""
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
```

##### 5C.2 — Reescrever apps/news/urls.py completo

```python
from django.urls import path

from . import views
from .feeds import CategoryFeed, LatestArticlesFeed

app_name = 'news'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('search/', views.article_search, name='search'),
    path('feed/', LatestArticlesFeed(), name='feed'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:slug>/feed/', CategoryFeed(), name='category_feed'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('author/<str:username>/', views.author_detail, name='author_detail'),
    path('archive/<int:year>/', views.article_archive, name='archive_year'),
    path('archive/<int:year>/<int:month>/', views.article_archive, name='archive_month'),
    path('htmx/articles/', views.article_list_page, name='article_list_page'),
    # SLUG CATCH-ALL — deve ser SEMPRE a última rota
    path('<slug:slug>/', views.article_detail, name='article_detail'),
]
```

**IMPORTANTE:** A rota `<slug:slug>/` deve ser a ÚLTIMA, senão captura rotas como `search/`, `feed/`, etc.

**Critério de aceite 5C:**
- Todas as URLs resolvem sem erro (`reverse()` funciona)
- `/news/` mostra listagem com paginação
- `/news/search/?q=teste` retorna resultados
- `/news/tag/<slug>/` filtra por tag
- `/news/author/<username>/` mostra perfil do autor
- `/news/archive/2026/` mostra arquivo

---

#### FASE 5D — RSS Feeds

**Arquivo a reescrever:** `apps/news/feeds.py`
**Migration:** NÃO

```python
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
```

**Critério de aceite 5D:**
- `/news/feed/` retorna XML válido com artigos
- `/news/category/<slug>/feed/` retorna feed da categoria

---

#### FASE 5E — SEO e Metadados

**Arquivos a modificar:** `templates/base_news.html`, `templates/news/article_detail.html`
**Migration:** NÃO

##### 5E.1 — Adicionar blocks SEO no base_news.html

No `<head>`, DEPOIS da tag `<meta name="description">` existente, adicionar:

```html
<!-- Open Graph -->
{% block og_tags %}
<meta property="og:site_name" content="{{ current_site.name }}">
<meta property="og:type" content="website">
<meta property="og:title" content="{% block og_title %}{{ current_site.name }}{% endblock %}">
<meta property="og:description" content="{% block og_description %}{{ site_settings.tagline }}{% endblock %}">
<meta property="og:url" content="{{ request.build_absolute_uri }}">
{% block og_image %}{% endblock %}
{% endblock %}

<!-- Twitter Cards -->
{% block twitter_tags %}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block twitter_title %}{{ current_site.name }}{% endblock %}">
<meta name="twitter:description" content="{% block twitter_description %}{{ site_settings.tagline }}{% endblock %}">
{% block twitter_image %}{% endblock %}
{% endblock %}

<!-- Canonical & RSS -->
<link rel="canonical" href="{{ request.build_absolute_uri }}">
<link rel="alternate" type="application/rss+xml" title="{{ current_site.name }} RSS" href="{% url 'news:feed' %}">

{% block json_ld %}{% endblock %}
```

##### 5E.2 — Override SEO no article_detail.html

No início do template (após `{% extends %}`), adicionar TODOS os blocks de override:

```html
{% block og_title %}{{ article.meta_title|default:article.title }}{% endblock %}
{% block og_description %}{{ article.meta_description|default:article.excerpt }}{% endblock %}
{% block og_image %}
{% if article.featured_image %}
<meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}">
<meta property="og:image:alt" content="{{ article.title }}">
{% endif %}
{% endblock %}

{% block twitter_title %}{{ article.meta_title|default:article.title }}{% endblock %}
{% block twitter_description %}{{ article.meta_description|default:article.excerpt }}{% endblock %}
{% block twitter_image %}
{% if article.featured_image %}
<meta name="twitter:image" content="{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}">
{% endif %}
{% endblock %}

{% block json_ld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{{ article.title|escapejs }}",
  "description": "{{ article.excerpt|escapejs }}",
  "datePublished": "{{ article.published_at|date:'c' }}",
  "dateModified": "{{ article.updated_at|date:'c' }}",
  "url": "{{ request.build_absolute_uri }}",
  {% if article.featured_image %}
  "image": "{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}",
  {% endif %}
  {% if article.author %}
  "author": {
    "@type": "Person",
    "name": "{{ article.author.get_full_name|default:article.author.username|escapejs }}"
  },
  {% endif %}
  "publisher": {
    "@type": "Organization",
    "name": "{{ current_site.name|escapejs }}"
  }
}
</script>
{% endblock %}
```

**Critério de aceite 5E:**
- View source de um artigo contém tags `og:`, `twitter:`, e `application/ld+json`
- Tags Open Graph têm valores corretos do artigo

---

#### FASE 5F — Templates Partials Reutilizáveis

**Diretório a criar:** `templates/news/partials/`
**Arquivos a criar:** 7 partials
**Migration:** NÃO

##### 5F.1 — templates/news/partials/article_card.html

Card reutilizável para artigo (será usado em list, category, tag, author, search, archive):

```html
<a href="{% url 'news:article_detail' article.slug %}"
   class="flex flex-col bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 hover-lift group">
  <div class="aspect-[16/10] bg-gray-100 relative overflow-hidden">
    {% if article.featured_image %}
    <img src="{{ article.featured_image.url }}" alt="{{ article.title }}" loading="lazy"
         class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
    {% else %}
    <div class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center">
      <svg class="w-12 h-12 text-primary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
      </svg>
    </div>
    {% endif %}
    {% if article.category %}
    <div class="absolute top-4 left-4">
      <span class="bg-white/90 backdrop-blur text-gray-900 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
        {{ article.category.name }}
      </span>
    </div>
    {% endif %}
  </div>
  <div class="p-6 flex-grow flex flex-col">
    <div class="text-xs text-gray-500 mb-3 flex items-center gap-2 font-medium">
      <time datetime="{{ article.published_at|date:'c' }}">{{ article.published_at|date:"d M, Y" }}</time>
      <span class="text-gray-300">&bull;</span>
      <span>{{ article.reading_time }} min leitura</span>
    </div>
    <h3 class="text-xl font-bold font-display text-gray-900 mb-3 group-hover:text-primary-600 transition-colors line-clamp-2">
      {{ article.title }}
    </h3>
    <p class="text-gray-600 text-sm line-clamp-3 mb-6 flex-grow">
      {{ article.excerpt|default:article.content|striptags|truncatewords:30 }}
    </p>
    {% if article.author %}
    <div class="flex items-center gap-2 mb-4">
      {% if article.author.avatar %}
      <img src="{{ article.author.avatar.url }}" alt="{{ article.author.get_full_name }}" class="w-6 h-6 rounded-full object-cover">
      {% endif %}
      <span class="text-xs text-gray-500">{{ article.author.get_full_name|default:article.author.username }}</span>
    </div>
    {% endif %}
    <div class="mt-auto flex items-center text-primary-600 font-medium text-sm">
      Ler artigo
      <svg class="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
      </svg>
    </div>
  </div>
</a>
```

##### 5F.2 — templates/news/partials/sidebar.html

```html
<aside class="space-y-8">
  <!-- Mais Lidas -->
  <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
    <h3 class="font-display font-bold text-gray-900 text-lg mb-4 pb-3 border-b border-gray-100">Mais Lidas</h3>
    <div class="space-y-4">
      {% for item in popular_articles %}
      <a href="{% url 'news:article_detail' item.slug %}" class="flex gap-3 group">
        {% if item.featured_image %}
        <img src="{{ item.featured_image.url }}" alt="{{ item.title }}"
             class="w-16 h-16 rounded-xl object-cover flex-shrink-0" loading="lazy">
        {% else %}
        <div class="w-16 h-16 rounded-xl bg-primary-100 flex-shrink-0"></div>
        {% endif %}
        <div>
          <p class="text-sm font-semibold text-gray-800 group-hover:text-primary-600 transition-colors line-clamp-2">{{ item.title }}</p>
          <p class="text-xs text-gray-400 mt-1">{{ item.view_count }} leituras</p>
        </div>
      </a>
      {% endfor %}
    </div>
  </div>

  <!-- Categorias -->
  <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
    <h3 class="font-display font-bold text-gray-900 text-lg mb-4 pb-3 border-b border-gray-100">Categorias</h3>
    <ul class="space-y-2">
      {% for cat in top_categories %}
      <li>
        <a href="{% url 'news:category_detail' cat.slug %}"
           class="flex justify-between items-center text-gray-700 hover:text-primary-600 transition-colors py-1">
          <span class="font-medium">{{ cat.name }}</span>
          <span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{{ cat.article_count }}</span>
        </a>
      </li>
      {% endfor %}
    </ul>
  </div>

  <!-- Tag Cloud -->
  <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
    <h3 class="font-display font-bold text-gray-900 text-lg mb-4 pb-3 border-b border-gray-100">Tags</h3>
    <div class="flex flex-wrap gap-2">
      {% for t in top_tags %}
      <a href="{% url 'news:tag_detail' t.slug %}"
         class="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-lg hover:bg-primary-100 hover:text-primary-700 transition-colors">
        #{{ t.name }}
      </a>
      {% endfor %}
    </div>
  </div>

  <!-- RSS Feed -->
  <div class="bg-primary-900 rounded-2xl p-6 text-white">
    <h3 class="font-display font-bold text-lg mb-2">RSS Feed</h3>
    <p class="text-primary-200 text-sm mb-4">Assine nosso feed para receber todas as atualizações.</p>
    <a href="{% url 'news:feed' %}"
       class="inline-flex items-center gap-2 bg-white text-primary-900 px-4 py-2 rounded-xl font-bold text-sm hover:bg-primary-50 transition-colors">
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M6.18 15.64a2.18 2.18 0 0 1 2.18 2.18C8.36 19.01 7.38 20 6.18 20C4.98 20 4 19.01 4 17.82a2.18 2.18 0 0 1 2.18-2.18M4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44m0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1z"/>
      </svg>
      Assinar Feed
    </a>
  </div>
</aside>
```

##### 5F.3 — templates/news/partials/article_grid.html

Grid com botão load-more HTMX:

```html
{% for article in page_obj %}
  {% include 'news/partials/article_card.html' %}
{% endfor %}

{% if page_obj.has_next %}
<div class="col-span-full text-center mt-8" id="load-more-container">
  <button
    hx-get="{% url 'news:article_list_page' %}?page={{ page_obj.next_page_number }}"
    hx-target="#articles-grid"
    hx-swap="beforeend"
    class="bg-white border-2 border-primary-600 text-primary-600 px-8 py-3 rounded-full font-bold hover:bg-primary-600 hover:text-white transition-colors">
    Carregar mais artigos
  </button>
</div>
{% endif %}
```

##### 5F.4 — templates/news/partials/pagination.html

Paginação reutilizável:

```html
{% if page_obj.has_other_pages %}
<nav class="flex justify-center items-center gap-2 mt-12" aria-label="Paginação">
  {% if page_obj.has_previous %}
  <a href="?{% if query %}q={{ query }}&{% endif %}page={{ page_obj.previous_page_number }}"
     class="px-4 py-2 rounded-xl bg-white border border-gray-200 text-gray-700 hover:bg-primary-50 hover:border-primary-300 transition-colors font-medium text-sm">
    Anterior
  </a>
  {% endif %}

  {% for num in page_obj.paginator.page_range %}
    {% if page_obj.number == num %}
    <span class="px-4 py-2 rounded-xl bg-primary-600 text-white font-bold text-sm">{{ num }}</span>
    {% elif num > page_obj.number|add:"-3" and num < page_obj.number|add:"3" %}
    <a href="?{% if query %}q={{ query }}&{% endif %}page={{ num }}"
       class="px-4 py-2 rounded-xl bg-white border border-gray-200 text-gray-700 hover:bg-primary-50 transition-colors font-medium text-sm">{{ num }}</a>
    {% endif %}
  {% endfor %}

  {% if page_obj.has_next %}
  <a href="?{% if query %}q={{ query }}&{% endif %}page={{ page_obj.next_page_number }}"
     class="px-4 py-2 rounded-xl bg-white border border-gray-200 text-gray-700 hover:bg-primary-50 hover:border-primary-300 transition-colors font-medium text-sm">
    Próxima
  </a>
  {% endif %}
</nav>
{% endif %}
```

##### 5F.5 — templates/news/partials/newsletter_success.html

```html
<div class="text-center py-4">
  <svg class="w-12 h-12 text-green-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
  </svg>
  <p class="font-bold text-gray-900">Inscrição realizada!</p>
  <p class="text-gray-600 text-sm mt-1">Você receberá nossas novidades em breve.</p>
</div>
```

##### 5F.6 — templates/news/partials/newsletter_error.html

```html
<form hx-post="{% url 'news:newsletter_subscribe' %}" hx-target="this" hx-swap="outerHTML"
      class="flex flex-col sm:flex-row gap-3 max-w-lg mx-auto">
  {% csrf_token %}
  {{ form.email }}
  <button type="submit"
    class="bg-primary-600 text-white rounded-full px-8 py-4 font-bold hover:bg-primary-700 transition-colors shadow-lg hover:shadow-primary-500/30">
    Assinar
  </button>
  {% if form.email.errors %}
  <p class="text-red-500 text-sm w-full text-center sm:col-span-2">{{ form.email.errors|first }}</p>
  {% endif %}
</form>
```

##### 5F.7 — templates/news/partials/search_results.html

```html
{% if page_obj %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
  {% for article in page_obj %}
    {% include 'news/partials/article_card.html' %}
  {% endfor %}
</div>
{% include 'news/partials/pagination.html' %}
{% else %}
{% if query %}
<div class="text-center py-16 text-gray-500">
  <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
  </svg>
  <p class="text-lg">Nenhum resultado encontrado para <strong>"{{ query }}"</strong>.</p>
  <p class="text-sm mt-2">Tente outros termos de busca.</p>
</div>
{% endif %}
{% endif %}
```

**Critério de aceite 5F:**
- Todos os 7 arquivos criados em `templates/news/partials/`
- Templates renderizam sem erros de syntax

---

#### FASE 5G — Templates Páginas Novas

**Arquivos a criar:** 4 novos templates em `templates/news/`
**Migration:** NÃO

##### 5G.1 — templates/news/tag_detail.html

```html
{% extends 'base_news.html' %}

{% block title %}#{{ tag.name }} - Portal de Notícias{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Main Content -->
    <div class="flex-grow lg:w-2/3">
      <div class="mb-12">
        <a href="{% url 'news:list' %}"
           class="inline-flex items-center text-sm font-bold text-primary-600 uppercase tracking-widest hover:text-primary-800 mb-6 transition-colors">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Voltar para Notícias
        </a>
        <h1 class="text-5xl font-display font-bold text-gray-900 mb-4">#{{ tag.name }}</h1>
        <p class="text-xl text-gray-600">{{ page_obj.paginator.count }} artigo{{ page_obj.paginator.count|pluralize:"s" }} com esta tag.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {% for article in page_obj %}
          {% include 'news/partials/article_card.html' %}
        {% empty %}
        <div class="col-span-full text-center py-16 text-gray-500">
          Nenhum artigo encontrado com esta tag.
        </div>
        {% endfor %}
      </div>

      {% include 'news/partials/pagination.html' %}
    </div>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>
{% endblock %}
```

##### 5G.2 — templates/news/author_detail.html

```html
{% extends 'base_news.html' %}

{% block title %}{{ author.get_full_name|default:author.username }} - Portal de Notícias{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <!-- Author Header -->
  <div class="bg-white rounded-3xl p-8 md:p-12 mb-12 border border-gray-100 shadow-sm">
    <div class="flex flex-col md:flex-row items-center md:items-start gap-8">
      {% if author.avatar %}
      <img src="{{ author.avatar.url }}" alt="{{ author.get_full_name }}"
           class="w-32 h-32 rounded-full object-cover shadow-lg">
      {% else %}
      <div class="w-32 h-32 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-4xl font-display font-bold">
        {{ author.get_full_name|default:author.username|first|upper }}
      </div>
      {% endif %}
      <div class="text-center md:text-left">
        <h1 class="text-4xl font-display font-bold text-gray-900 mb-2">{{ author.get_full_name|default:author.username }}</h1>
        <p class="text-primary-600 font-medium mb-4">{{ author.get_role_display|default:"Redator" }}</p>
        {% if author.bio %}
        <p class="text-gray-600 max-w-2xl">{{ author.bio }}</p>
        {% endif %}
        <p class="text-sm text-gray-400 mt-4">{{ page_obj.paginator.count }} artigo{{ page_obj.paginator.count|pluralize:"s" }} publicado{{ page_obj.paginator.count|pluralize:"s" }}</p>
      </div>
    </div>
  </div>

  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Articles Grid -->
    <div class="flex-grow lg:w-2/3">
      <h2 class="text-2xl font-display font-bold text-gray-900 mb-8">Artigos publicados</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {% for article in page_obj %}
          {% include 'news/partials/article_card.html' %}
        {% empty %}
        <div class="col-span-full text-center py-16 text-gray-500">
          Este autor ainda não tem artigos publicados.
        </div>
        {% endfor %}
      </div>

      {% include 'news/partials/pagination.html' %}
    </div>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>
{% endblock %}
```

##### 5G.3 — templates/news/search.html

```html
{% extends 'base_news.html' %}

{% block title %}{% if query %}Busca: {{ query }}{% else %}Buscar{% endif %} - Portal de Notícias{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <!-- Search Header -->
  <div class="mb-12 text-center">
    <h1 class="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-8">Buscar Notícias</h1>
    <form action="{% url 'news:search' %}" method="get" class="max-w-2xl mx-auto">
      <div class="relative">
        <input type="text" name="q" value="{{ query }}"
               placeholder="Digite sua busca..."
               hx-get="{% url 'news:search' %}"
               hx-trigger="input changed delay:400ms, search"
               hx-target="#search-results"
               hx-push-url="true"
               hx-include="this"
               class="w-full rounded-full border-2 border-gray-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 pl-6 pr-14 py-5 text-lg font-sans"
               autocomplete="off">
        <button type="submit" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary-600 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </button>
      </div>
    </form>
    {% if query %}
    <p class="text-gray-500 mt-4">{{ page_obj.paginator.count }} resultado{{ page_obj.paginator.count|pluralize:"s" }} para "{{ query }}"</p>
    {% endif %}
  </div>

  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Results -->
    <div class="flex-grow lg:w-2/3" id="search-results">
      {% include 'news/partials/search_results.html' %}
    </div>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>
{% endblock %}
```

##### 5G.4 — templates/news/archive.html

```html
{% extends 'base_news.html' %}
{% load i18n %}

{% block title %}Arquivo {% if month %}{{ month }}/{% endif %}{{ year }} - Portal de Notícias{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Main Content -->
    <div class="flex-grow lg:w-2/3">
      <div class="mb-12">
        <a href="{% url 'news:list' %}"
           class="inline-flex items-center text-sm font-bold text-primary-600 uppercase tracking-widest hover:text-primary-800 mb-6 transition-colors">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Voltar para Notícias
        </a>
        <h1 class="text-5xl font-display font-bold text-gray-900 mb-4">
          Arquivo: {% if month %}{{ month }}/{% endif %}{{ year }}
        </h1>
        <p class="text-xl text-gray-600">{{ page_obj.paginator.count }} artigo{{ page_obj.paginator.count|pluralize:"s" }} encontrado{{ page_obj.paginator.count|pluralize:"s" }}.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {% for article in page_obj %}
          {% include 'news/partials/article_card.html' %}
        {% empty %}
        <div class="col-span-full text-center py-16 text-gray-500">
          Nenhum artigo encontrado neste período.
        </div>
        {% endfor %}
      </div>

      {% include 'news/partials/pagination.html' %}
    </div>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>
{% endblock %}
```

**Critério de aceite 5G:**
- 4 templates criados
- Cada página renderiza corretamente com dados de teste

---

#### FASE 5H — Atualização dos Templates Existentes

**Arquivos a modificar:** `templates/news/article_list.html`, `templates/news/article_detail.html`, `templates/news/category_detail.html`, `templates/components/navbar_news.html`
**Migration:** NÃO

##### 5H.1 — Reescrever templates/news/article_list.html

```html
{% extends 'base_news.html' %}

{% block title %}Portal de Notícias - {{ current_site.name }}{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <div class="flex flex-col md:flex-row justify-between items-end mb-12">
    <div>
      <h1 class="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-4">Últimas Notícias</h1>
      <p class="text-xl text-gray-600">Acompanhe as novidades e eventos da nossa instituição.</p>
    </div>

    <div class="flex items-center gap-4 mt-6 md:mt-0">
      <!-- Search Link -->
      <a href="{% url 'news:search' %}"
         class="bg-white border border-gray-200 text-gray-700 p-2.5 rounded-full hover:bg-gray-50 transition-colors shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </a>

      <!-- Category Filter -->
      <div x-data="{ open: false }" class="relative z-20">
        <button @click="open = !open" @click.away="open = false"
          class="bg-white border border-gray-200 text-gray-700 px-5 py-2.5 rounded-full font-medium inline-flex items-center hover:bg-gray-50 transition-colors shadow-sm">
          Categorias
          <svg class="w-5 h-5 ml-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <div x-show="open" x-cloak x-transition
             class="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 py-2">
          {% for cat in categories %}
          <a href="{% url 'news:category_detail' cat.slug %}"
             class="block px-4 py-2 text-gray-700 hover:bg-primary-50 hover:text-primary-700">{{ cat.name }}</a>
          {% endfor %}
        </div>
      </div>
    </div>
  </div>

  <!-- Featured Article Hero -->
  {% if featured %}
  <div class="mb-16">
    <a href="{% url 'news:article_detail' featured.slug %}"
       class="group block relative rounded-3xl overflow-hidden shadow-lg h-[500px]">
      {% if featured.featured_image %}
      <img src="{{ featured.featured_image.url }}" alt="{{ featured.title }}" loading="eager"
           class="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700">
      {% else %}
      <div class="absolute inset-0 w-full h-full bg-gray-900"></div>
      {% endif %}
      <div class="absolute inset-0 bg-gradient-to-t from-gray-900/90 via-gray-900/40 to-transparent"></div>

      <div class="absolute inset-x-0 bottom-0 p-8 md:p-12 text-white">
        {% if featured.category %}
        <span class="inline-block px-3 py-1 bg-primary-600 rounded-full text-xs font-bold uppercase tracking-wider mb-4">
          {{ featured.category.name }}
        </span>
        {% endif %}
        <h2 class="text-3xl md:text-5xl font-display font-bold mb-4 drop-shadow-lg group-hover:text-primary-200 transition-colors">
          {{ featured.title }}
        </h2>
        <p class="text-gray-200 line-clamp-2 text-lg mb-6 max-w-3xl">
          {{ featured.excerpt|default:featured.content|striptags|truncatewords:30 }}
        </p>
        <div class="flex items-center text-sm font-medium text-gray-300">
          <span>{{ featured.published_at|date:"d M, Y" }}</span>
          <span class="mx-2">&bull;</span>
          <span>{{ featured.reading_time }} min leitura</span>
          <span class="mx-2">&bull;</span>
          <span>{{ featured.view_count }} visualizações</span>
        </div>
      </div>
    </a>
  </div>
  {% endif %}

  <!-- Articles Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" id="articles-grid">
    {% for article in page_obj %}
      {% include 'news/partials/article_card.html' %}
    {% empty %}
    <div class="col-span-full text-center py-20 text-gray-500 bg-gray-50 rounded-3xl">
      Ainda não há notícias publicadas.
    </div>
    {% endfor %}
  </div>

  {% include 'news/partials/pagination.html' %}
</div>
{% endblock %}
```

##### 5H.2 — Reescrever templates/news/article_detail.html

```html
{% extends 'base_news.html' %}

{% block title %}{{ article.meta_title|default:article.title }} - {{ current_site.name }}{% endblock %}
{% block meta_description %}{{ article.meta_description|default:article.excerpt }}{% endblock %}

{% block og_title %}{{ article.meta_title|default:article.title }}{% endblock %}
{% block og_description %}{{ article.meta_description|default:article.excerpt }}{% endblock %}
{% block og_image %}
{% if article.featured_image %}
<meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}">
{% endif %}
{% endblock %}
{% block twitter_title %}{{ article.meta_title|default:article.title }}{% endblock %}
{% block twitter_description %}{{ article.meta_description|default:article.excerpt }}{% endblock %}
{% block twitter_image %}
{% if article.featured_image %}
<meta name="twitter:image" content="{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}">
{% endif %}
{% endblock %}

{% block json_ld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{{ article.title|escapejs }}",
  "description": "{{ article.excerpt|escapejs }}",
  "datePublished": "{{ article.published_at|date:'c' }}",
  "dateModified": "{{ article.updated_at|date:'c' }}",
  "url": "{{ request.build_absolute_uri }}"{% if article.featured_image %},
  "image": "{{ request.scheme }}://{{ request.get_host }}{{ article.featured_image.url }}"{% endif %}{% if article.author %},
  "author": {
    "@type": "Person",
    "name": "{{ article.author.get_full_name|default:article.author.username|escapejs }}"
  }{% endif %},
  "publisher": {
    "@type": "Organization",
    "name": "{{ current_site.name|escapejs }}"
  }
}
</script>
{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <!-- Breadcrumbs -->
  <nav class="mb-8 text-sm font-medium text-gray-500" aria-label="Breadcrumb">
    <ol class="flex items-center gap-2">
      <li><a href="{% url 'news:list' %}" class="hover:text-primary-600 transition-colors">Notícias</a></li>
      {% if article.category %}
      <li class="flex items-center gap-2">
        <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
        <a href="{% url 'news:category_detail' article.category.slug %}" class="hover:text-primary-600 transition-colors">{{ article.category.name }}</a>
      </li>
      {% endif %}
      <li class="flex items-center gap-2">
        <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
        <span class="text-gray-900 truncate max-w-[200px]">{{ article.title }}</span>
      </li>
    </ol>
  </nav>

  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Article Content -->
    <article class="flex-grow lg:w-2/3">
      <!-- Header -->
      <header class="mb-12 fade-in">
        {% if article.category %}
        <a href="{% url 'news:category_detail' article.category.slug %}"
           class="inline-block px-4 py-1.5 rounded-full bg-primary-100 text-primary-700 font-bold text-xs uppercase tracking-wider mb-6 hover:bg-primary-200 transition-colors">
          {{ article.category.name }}
        </a>
        {% endif %}

        <h1 class="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-6 leading-tight">{{ article.title }}</h1>

        {% if article.excerpt %}
        <p class="text-xl text-gray-600 italic mb-8">{{ article.excerpt }}</p>
        {% endif %}

        <div class="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-500">
          {% if article.author %}
          <a href="{% url 'news:author_detail' article.author.username %}" class="flex items-center gap-2 hover:text-primary-600 transition-colors">
            {% if article.author.avatar %}
            <img src="{{ article.author.avatar.url }}" alt="{{ article.author.get_full_name }}"
                 class="w-8 h-8 rounded-full object-cover">
            {% endif %}
            <span>{{ article.author.get_full_name|default:article.author.username }}</span>
          </a>
          <span>&bull;</span>
          {% endif %}
          <time datetime="{{ article.published_at|date:'c' }}">{{ article.published_at|date:"d de F, Y" }}</time>
          <span>&bull;</span>
          <span>{{ article.reading_time }} min de leitura</span>
          <span>&bull;</span>
          <span>{{ article.view_count }} leituras</span>
        </div>
      </header>

      <!-- Featured Image -->
      {% if article.featured_image %}
      <figure class="mb-16">
        <div class="rounded-[2rem] overflow-hidden shadow-2xl shadow-gray-200/50 relative aspect-video">
          <img src="{{ article.featured_image.url }}" alt="{{ article.title }}" class="w-full h-full object-cover" loading="eager">
        </div>
        {% if article.featured_image_caption %}
        <figcaption class="text-center text-sm text-gray-500 mt-4 italic">{{ article.featured_image_caption }}</figcaption>
        {% endif %}
      </figure>
      {% endif %}

      <!-- Content -->
      <div class="prose prose-lg prose-primary max-w-none prose-headings:font-display prose-headings:font-bold prose-a:text-primary-600 hover:prose-a:text-primary-800 prose-img:rounded-3xl prose-img:shadow-xl">
        {{ article.content|safe }}
      </div>

      <!-- Social Share -->
      <div class="flex items-center gap-4 mt-12 pt-8 border-t border-gray-100">
        <span class="text-sm font-bold text-gray-700 uppercase tracking-wider">Compartilhar:</span>
        <a href="https://twitter.com/intent/tweet?url={{ request.build_absolute_uri|urlencode }}&text={{ article.title|urlencode }}"
           target="_blank" rel="noopener noreferrer"
           class="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-xl text-sm font-medium hover:bg-gray-800 transition-colors">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.259 5.63L18.244 2.25z"/></svg>
          X
        </a>
        <a href="https://wa.me/?text={{ article.title|urlencode }}%20{{ request.build_absolute_uri|urlencode }}"
           target="_blank" rel="noopener noreferrer"
           class="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl text-sm font-medium hover:bg-green-600 transition-colors">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492l4.609-1.467A11.94 11.94 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75c-2.14 0-4.12-.67-5.75-1.812l-.413-.248-2.735.87.892-2.652-.273-.434A9.726 9.726 0 012.25 12C2.25 6.615 6.615 2.25 12 2.25S21.75 6.615 21.75 12 17.385 21.75 12 21.75z"/></svg>
          WhatsApp
        </a>
      </div>

      <!-- Tags -->
      {% if article.tags.exists %}
      <div class="mt-8 pt-8 border-t border-gray-100">
        <h4 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4">Tags</h4>
        <div class="flex flex-wrap gap-2">
          {% for tag in article.tags.all %}
          <a href="{% url 'news:tag_detail' tag.slug %}"
             class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-primary-100 hover:text-primary-700 transition-colors">
            #{{ tag.name }}
          </a>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <!-- Related Articles -->
      {% if related_articles %}
      <div class="mt-16 pt-12 border-t border-gray-100">
        <h3 class="text-2xl font-display font-bold text-gray-900 mb-8">Artigos Relacionados</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          {% for article in related_articles %}
            {% include 'news/partials/article_card.html' %}
          {% endfor %}
        </div>
      </div>
      {% endif %}
    </article>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>

<!-- Newsletter CTA -->
<div class="bg-primary-50 py-16 mt-24">
  <div class="max-w-4xl mx-auto px-4 text-center">
    <h3 class="text-3xl font-display font-bold text-gray-900 mb-4">Mantenha-se informado</h3>
    <p class="text-gray-600 mb-8 text-lg">Inscreva-se para receber as principais notícias e eventos diretamente no seu e-mail.</p>
    <form hx-post="{% url 'news:newsletter_subscribe' %}" hx-target="this" hx-swap="outerHTML"
          class="flex flex-col sm:flex-row gap-3 max-w-lg mx-auto">
      {% csrf_token %}
      <input type="email" name="email" placeholder="Seu melhor e-mail" required
             class="flex-grow rounded-full border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 px-6 py-4">
      <button type="submit"
        class="bg-primary-600 text-white rounded-full px-8 py-4 font-bold hover:bg-primary-700 transition-colors shadow-lg hover:shadow-primary-500/30">
        Assinar
      </button>
    </form>
  </div>
</div>
{% endblock %}
```

##### 5H.3 — Reescrever templates/news/category_detail.html

```html
{% extends 'base_news.html' %}

{% block title %}{{ category.name }} - Portal de Notícias - {{ current_site.name }}{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
  <div class="flex flex-col lg:flex-row gap-12">
    <!-- Main Content -->
    <div class="flex-grow lg:w-2/3">
      <div class="mb-12 border-b border-gray-200 pb-12">
        <a href="{% url 'news:list' %}"
           class="inline-flex items-center text-sm font-bold text-primary-600 uppercase tracking-widest hover:text-primary-800 mb-6 transition-colors">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Voltar para Notícias
        </a>
        <h1 class="text-5xl font-display font-bold text-gray-900 mb-4">{{ category.name }}</h1>
        {% if category.description %}
        <p class="text-xl text-gray-600 max-w-3xl">{{ category.description }}</p>
        {% endif %}
        <p class="text-sm text-gray-400 mt-4">{{ page_obj.paginator.count }} artigo{{ page_obj.paginator.count|pluralize:"s" }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {% for article in page_obj %}
          {% include 'news/partials/article_card.html' %}
        {% empty %}
        <div class="col-span-full py-24 text-center">
          <h3 class="text-2xl font-display font-bold text-gray-900 mb-2">Categoria Vazia</h3>
          <p class="text-gray-500">Ainda não há artigos publicados nesta categoria.</p>
        </div>
        {% endfor %}
      </div>

      {% include 'news/partials/pagination.html' %}
    </div>

    <!-- Sidebar -->
    <div class="lg:w-1/3">
      {% include 'news/partials/sidebar.html' %}
    </div>
  </div>
</div>
{% endblock %}
```

##### 5H.4 — Atualizar templates/components/navbar_news.html

Adicionar categorias no menu desktop e ícone de busca:

```html
<nav x-data="{ mobileMenuOpen: false }" class="fixed w-full top-0 z-50 glass-nav-news shadow-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-20 items-center">
      <!-- Logo -->
      <div class="flex-shrink-0 flex items-center">
        <a href="{% url 'news:list' %}" class="flex items-center gap-3 group">
          <div class="h-10 w-10 bg-primary-900 rounded-sm flex items-center justify-center text-white font-display font-bold text-2xl group-hover:bg-primary-700 transition-colors">
            K<span class="text-primary-300">.</span>
          </div>
          <span class="font-display font-black text-2xl tracking-tight text-gray-900 uppercase">Notícias</span>
        </a>
      </div>

      <!-- Desktop Menu -->
      <div class="hidden md:flex items-center gap-1">
        <a href="{% url 'news:list' %}"
           class="text-gray-700 hover:text-primary-700 font-bold font-sans uppercase tracking-widest text-sm px-3 py-2 transition-colors">Capa</a>

        {% for cat in nav_categories %}
        <a href="{% url 'news:category_detail' cat.slug %}"
           class="text-gray-600 hover:text-primary-700 font-sans text-sm px-3 py-2 transition-colors">{{ cat.name }}</a>
        {% endfor %}

        <span class="h-6 w-px bg-gray-300 mx-2"></span>

        <!-- Search -->
        <a href="{% url 'news:search' %}"
           class="text-gray-500 hover:text-primary-600 p-2 transition-colors" title="Buscar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </a>

        <span class="h-6 w-px bg-gray-300 mx-2"></span>

        <!-- Link para Escola -->
        <a href="{% url 'school:home' %}"
           class="text-sm font-sans font-medium text-primary-700 hover:text-primary-900 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Instituição
        </a>
      </div>

      <!-- Mobile menu button -->
      <div class="flex items-center md:hidden">
        <button @click="mobileMenuOpen = !mobileMenuOpen"
                class="text-gray-800 hover:text-primary-600 p-2 focus:outline-none">
          <svg class="h-6 w-6" x-show="!mobileMenuOpen" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <svg class="h-6 w-6" x-cloak x-show="mobileMenuOpen" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile Menu -->
  <div x-cloak x-show="mobileMenuOpen" x-transition
       class="md:hidden bg-white border-t border-gray-200 absolute w-full shadow-2xl">
    <div class="px-4 pt-2 pb-6 space-y-2 flex flex-col font-sans">
      <a href="{% url 'news:list' %}"
         class="block px-3 py-3 text-base font-bold text-gray-900 hover:text-primary-600 uppercase tracking-wider">Capa</a>

      {% for cat in nav_categories %}
      <a href="{% url 'news:category_detail' cat.slug %}"
         class="block px-3 py-3 text-base text-gray-700 hover:text-primary-600">{{ cat.name }}</a>
      {% endfor %}

      <a href="{% url 'news:search' %}"
         class="block px-3 py-3 text-base text-gray-700 hover:text-primary-600 flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        Buscar
      </a>

      <div class="my-2 border-t border-gray-100"></div>

      <a href="{% url 'school:home' %}"
         class="block px-3 py-3 text-center bg-gray-100 text-gray-600 font-medium hover:bg-gray-200 transition-colors">
        Voltar para a Instituição
      </a>
    </div>
  </div>
</nav>
```

**Critério de aceite 5H:**
- article_list usa partials (article_card.html) e tem paginação
- article_detail tem tags clicáveis, reading time, share buttons, artigos relacionados, breadcrumbs, newsletter HTMX
- category_detail tem sidebar e paginação
- navbar tem categorias e busca

---

#### FASE 5I — Admin Aprimorado

**Arquivo a reescrever:** `apps/news/admin.py`
**Migration:** NÃO

```python
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
    list_display = ['title', 'category', 'author', 'site', 'status', 'published_at', 'is_featured', 'view_count']
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
```

**IMPORTANTE:** Importar `ModelAdmin` de `unfold.admin`, NÃO de `django.contrib.admin`.

**Critério de aceite 5I:**
- Admin usa UI do Unfold
- Article tem fieldsets organizados, date_hierarchy, actions
- Newsletter admin tem export CSV

---

#### FASE 5J — Context Processor de Navegação

**Arquivos a modificar:** `apps/common/context_processors.py`, `config/settings/base.py`
**Migration:** NÃO

##### 5J.1 — Adicionar news_nav_context ao context_processors.py

Adicionar ao arquivo existente:

```python
def news_nav_context(request):
    """Inject top-level categories for news navigation."""
    if not request.path.startswith('/news/'):
        return {}
    from apps.news.models import Category
    return {
        'nav_categories': Category.objects.filter(parent__isnull=True).order_by('order', 'name')[:8]
    }
```

##### 5J.2 — Registrar no settings

Em `config/settings/base.py`, na lista de `context_processors`, adicionar:

```python
'apps.common.context_processors.news_nav_context',
```

Colocar APÓS `apps.common.context_processors.site_context`.

**Critério de aceite 5J:**
- `nav_categories` disponível em todas as páginas `/news/`
- Navbar mostra categorias automaticamente
- Páginas que NÃO são `/news/` NÃO fazem query desnecessária

---

## Validação Final (após todas as fases)

1. `python manage.py check` — sem erros
2. `python manage.py makemigrations --check` — sem migrations pendentes
3. `/news/` — listagem com featured, grid, paginação
4. `/news/<slug>/` — artigo com reading time, tags clicáveis, share buttons, relacionados, breadcrumbs, newsletter HTMX
5. `/news/category/<slug>/` — categoria com sidebar e paginação
6. `/news/tag/<slug>/` — tag com sidebar e paginação
7. `/news/author/<username>/` — perfil do autor
8. `/news/search/?q=teste` — busca funcional com HTMX
9. `/news/archive/2026/` — arquivo por ano
10. `/news/feed/` — RSS válido
11. `/news/newsletter/subscribe/` — POST funciona
12. `/admin/` — admin Unfold com todos os models
13. View source de artigo — contém Open Graph, Twitter Cards, JSON-LD
14. `pytest` — todos os testes passando

---

## Histórico de Tarefas

| Data | Tarefa | Status |
|------|--------|--------|
| 2026-02-21 | Fase 1-4: Fundação até Deploy | ✅ Concluído |
| 2026-02-23 | Fase 5A-5J: Portal de Notícias Completo | 🔄 Em andamento |

---

## Estado Atual

- **Tarefa ativa:** Fases 5A até 5J — Portal de Notícias Completo
- **Última atualização:** 2026-02-23
- **Notas:** Executar TODAS as sub-fases em sequência. Design visual será adaptado posteriormente com template Google Stitch.
