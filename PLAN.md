# Kelly Sys - Plano Global do Projeto

## Visão Geral

Sistema web unificado que gerencia dois sites de um grupo educacional:
- **Site da Escola** — institucional com contratação e contato
- **Portal de Notícias** — portal público de notícias

Painel administrativo único (Django Unfold) para gerenciar ambos.

---

## Stack

- **Backend:** Python 3.12+ / Django 5.x
- **Database:** PostgreSQL 16
- **Frontend:** Django Templates + HTMX + Alpine.js
- **Admin:** Django Unfold
- **Static:** WhiteNoise
- **Dev:** Docker Compose (Django + PostgreSQL + Mailpit)

---

## Estrutura de Apps

| App | Responsabilidade |
|-----|-----------------|
| `apps.common` | Models abstratos, SiteExtension, utils, context processors |
| `apps.accounts` | CustomUser, roles, permissões (Groups) |
| `apps.school` | Páginas CMS, equipe, depoimentos |
| `apps.hiring` | Vagas, candidaturas, departamentos |
| `apps.contact` | Formulários de contato e inquiries |
| `apps.news` | Artigos, categorias, tags, RSS, newsletter |
| `apps.media_library` | Biblioteca de mídia compartilhada |

---

## Fases e Status

### Fase 1: Fundação ✅
| # | Tarefa | Status |
|---|--------|--------|
| 1 | Estrutura de diretórios e config Django | ✅ Concluído |
| 2 | `config/settings/base.py` completo | ✅ Concluído |
| 3 | `apps.accounts` com CustomUser | ✅ Concluído |
| 4 | `apps.common` com models abstratos | ✅ Concluído |
| 5 | Docker Compose dev | ✅ Concluído |
| 6 | Primeira migration + superuser | ✅ Concluído |
| 7 | Django Unfold configurado | ✅ Concluído |

### Fase 2: Apps de Conteúdo ✅
| # | Tarefa | Status |
|---|--------|--------|
| 8 | `apps.school` completo | ✅ Concluído |
| 9 | `apps.hiring` completo | ✅ Concluído |
| 10 | `apps.contact` completo | ✅ Concluído |
| 11 | `apps.news` básico (models, views, admin) | ✅ Concluído |
| 12 | `apps.media_library` completo | ✅ Concluído |

### Fase 3: Templates e Frontend (Básico) ✅
| # | Tarefa | Status |
|---|--------|--------|
| 13 | Base templates (base.html, base_school.html, base_news.html) | ✅ Concluído |
| 14 | Templates escola (home, page_detail, team_list) | ✅ Concluído |
| 15 | Templates notícias (article_list, article_detail, category_detail) | ✅ Concluído |
| 16 | Templates contratação (job_list, job_detail) | ✅ Concluído |
| 17 | Templates contato (contact_page) | ✅ Concluído |
| 18 | Integração HTMX (middleware configurado) | ✅ Concluído |
| 19 | Integração Alpine.js (menus, flash messages) | ✅ Concluído |

### Fase 4: Polimento e Deploy ✅
| # | Tarefa | Status |
|---|--------|--------|
| 20 | Data migrations iniciais | ✅ Concluído |
| 21 | Sitemaps (ArticleSitemap, PageSitemap) | ✅ Concluído |
| 22 | Testes (school, news, hiring, contact) | ✅ Concluído |
| 23 | Docker Compose produção + Nginx | ✅ Concluído |
| 24 | CI/CD GitHub Actions | ✅ Concluído |
| 25 | Documentação deploy (DEPLOY.md) | ✅ Concluído |

---

### Fase 5: Portal de Notícias — Funcionalidades Completas ✅
| # | Tarefa | Status |
|---|--------|--------|
| 5A | Correções backend: `get_absolute_url`, `F()` view_count, `select_related`, `utils.py` | ✅ Concluído |
| 5B | Model `NewsletterSubscription` + form + view + admin | ✅ Concluído |
| 5C | Novas views: tag, autor, busca, arquivo, load-more HTMX, relacionados | ✅ Concluído |
| 5D | RSS Feeds (`LatestArticlesFeed`, `CategoryFeed`) | ✅ Concluído |
| 5E | SEO: Open Graph, Twitter Cards, JSON-LD, canonical, RSS link | ✅ Concluído |
| 5F | Partials reutilizáveis: card, sidebar, grid, paginação, newsletter, like_button, comments_list | ✅ Concluído |
| 5G | Páginas novas: tag_detail, author_detail, search, archive | ✅ Concluído |
| 5H | Atualização templates existentes: list, detail, category, navbar | ✅ Concluído |
| 5I | Admin aprimorado: Unfold ModelAdmin, fieldsets, actions, Comment/Like/Bookmark | ✅ Concluído |
| 5J | Context processor: categorias na navegação | ✅ Concluído |
| 5K | Sistema de comentários e likes (add_comment, delete_comment, toggle_like) | ✅ Concluído |
| 5L | Autenticação e dashboard de usuário (login, register, bookmarks) | ✅ Concluído |
| 5M | Bug fixes revisão Claude: unique_per_site newsletter, sidebar filtro site, CategoryFeed 404 | ✅ Concluído |

### Fase 6: Admin Enhancement — Painel Unificado Bilíngue 🔄
| # | Tarefa | Status |
|---|--------|--------|
| 6A | Migrar todos os admin.py para `unfold.admin.ModelAdmin` (school, hiring, contact, accounts, common) | ⬜ Pendente |
| 6B | Configurar `UNFOLD` settings: branding, sidebar agrupada por portal, cores `#1152d4` | ⬜ Pendente |
| 6C | Dashboard customizado: cards de stats por portal, ações rápidas, atividade recente | ⬜ Pendente |
| 6D | i18n PT/BR: `LocaleMiddleware`, `LANGUAGES`, path `i18n/` | ⬜ Pendente |
| 6E | Melhorar admin models: fieldsets, actions, badges de role (school, hiring, contact, accounts) | ⬜ Pendente |

### Fase 7: Portal de Notícias — Design (Google Stitch) ⬜
| # | Tarefa | Status |
|---|--------|--------|
| 7.1 | Exportar template Google Stitch | ⬜ Pendente |
| 7.2 | Adaptar paleta de cores e tipografia | ⬜ Pendente |
| 7.3 | Implementar layout de componentes do Stitch | ⬜ Pendente |
| 7.4 | Responsividade mobile | ⬜ Pendente |

### Fase 8: Site da Escola — Funcionalidades e Design ⬜
| # | Tarefa | Status |
|---|--------|--------|
| 8.1 | (A definir após admin enhancement) | ⬜ Pendente |

---

## Decisões Arquiteturais

1. **Multi-site via Django Sites Framework** — roteamento por path inicialmente, subdomínios depois
2. **CustomUser antes da 1ª migration** — obrigatório pelo Django
3. **Django Unfold** para admin — sem construir painel customizado
4. **HTMX + Alpine.js** — SEO nativo, sem build pipeline JS
5. **WhiteNoise** — serve statics sem Nginx em dev e shared hosting
6. **Path-based routing** — escola em `/`, notícias em `/news/`
7. **Funcionalidade antes do design** — toda a lógica do portal de notícias implementada primeiro, design visual do Stitch aplicado depois como camada separada
8. **FBV (Function-Based Views)** — padrão consistente em todo o projeto, sem migrar para CBV
9. **Busca com Django Q()** — sem biblioteca externa (Elasticsearch desnecessário para volume escolar)
10. **`get_sidebar_context()` como utility** — evita queries desnecessárias em páginas que não precisam da sidebar

---

## Bugs Resolvidos (Revisão Claude — Fase 5M)

| Bug | Fix Aplicado |
|-----|-------------|
| `NewsletterSubscription.email` unique global | `unique_together = [['email', 'site']]` + migration 0005 |
| `get_sidebar_context()` sem filtro de site | `Article.on_site` em vez de `Article.objects` |
| `CategoryFeed` levantava 500 | `get_object_or_404(Category, slug=slug)` |
| Comments hardcoded no article_detail | Loop real `{% for comment in comments %}` + form autenticado |
| Like count "12" hardcoded | `{{ like_count }}` real + view `toggle_like` + partial `like_button.html` |
| Comment/Like/Bookmark sem admin | `CommentAdmin`, `ArticleLikeAdmin`, `ArticleBookmarkAdmin` registrados |
| Sem endpoint de post de comentário | View `add_comment` + URL + formulário no template |
| `user_dashboard` query ineficiente | `Article.objects.filter(bookmarks__user=user)` direto |
| `toggle_bookmark` usando HTTP_REFERER | Parâmetro `?source=dashboard` |

---

## Estado Atual

- **Fase:** 6 — Admin Enhancement (Painel Unificado Bilíngue)
- **Tarefa ativa:** Fases 6A-6E no GEMINI.md
- **Última atualização:** 2026-02-23
- **Próximo passo:** Gemini executa Fases 6A-6E; depois Google Stitch para design do portal
- **Bloqueios:** Nenhum
