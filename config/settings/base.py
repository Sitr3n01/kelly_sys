import os
from pathlib import Path
import environ
from django.urls import reverse_lazy

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    # Unfold MUST come before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # Third-party
    'django_htmx',
    'imagekit',

    # Project apps
    'apps.common.apps.CommonConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.school.apps.SchoolConfig',
    'apps.hiring.apps.HiringConfig',
    'apps.contact.apps.ContactConfig',
    'apps.news.apps.NewsConfig',
    'apps.media_library.apps.MediaLibraryConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.site_context',
                'apps.common.context_processors.news_nav_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='kelly_sys'),
        'USER': env('DB_USER', default='kelly_user'),
        'PASSWORD': env('DB_PASSWORD', default='kelly_pass'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'

SITE_ID = 1

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
LANGUAGES = [
    ('pt-br', 'Português (BR)'),
    ('en', 'English'),
]
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
    'INDEX_DASHBOARD': 'apps.common.dashboard.AdminDashboardView',
}

# Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
