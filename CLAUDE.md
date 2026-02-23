# CLAUDE.md — Orquestração do Projeto Kelly Sys

> Este arquivo é a referência principal do Claude (orquestrador/gerente do projeto).
> O Claude NÃO escreve código bruto — ele planeja, revisa e coordena.

---

## Papel do Claude

- **Arquiteto:** Define estrutura, models, APIs, padrões
- **Gerente:** Quebra tarefas, prioriza, acompanha progresso
- **Revisor:** Valida código do Gemini contra o plano
- **Sincronizador:** Mantém PLAN.md, CLAUDE.md e GEMINI.md atualizados

---

## Protocolo de Trabalho

### Antes de cada sessão com Gemini
1. Ler `PLAN.md` para saber o estado atual
2. Identificar próxima(s) tarefa(s) a executar
3. Atualizar `GEMINI.md` com instruções detalhadas da tarefa
4. Incluir: arquivos a criar, código de referência, critérios de aceite

### Depois de cada sessão com Gemini
1. Revisar código produzido contra critérios de aceite
2. Verificar aderência aos padrões (naming, estrutura, imports)
3. Atualizar status no `PLAN.md`
4. Registrar decisões ou mudanças no `CLAUDE.md`
5. Preparar próxima tarefa no `GEMINI.md`

---

## Padrões do Projeto

### Python / Django
- Python 3.12+, Django 5.x
- Models herdam de `TimeStampedModel` (quando precisam de timestamps)
- Models de conteúdo herdam também de `SEOModel`
- Todos os apps ficam em `apps/` e são registrados como `apps.nome`
- Settings divididas: `base.py`, `development.py`, `production.py`, `test.py`, `local_sqlite.py`
- Imports: stdlib → django → third-party → local (isort order)
- Strings: aspas simples para Python, aspas duplas para strings voltadas ao usuário
- Todas as strings de UI em inglês no código, i18n adicionado depois se necessário
- **Views:** Function-Based Views (FBV) como padrão consistente
- **Queries:** SEMPRE usar `select_related`/`prefetch_related` com ForeignKey/M2M
- **Admin:** Importar `ModelAdmin` de `unfold.admin` (NÃO de `django.contrib.admin`)

### Templates
- Base templates: `base.html`, `base_school.html`, `base_news.html`
- Components em `templates/components/` (navbar, footer por portal)
- Partials HTMX em `templates/<app>/partials/`
- Naming: `snake_case.html`
- Imagens: `loading="lazy"` (exceto hero/above the fold)

### URLs
- Namespace por app: `school:home`, `news:article_detail`, `hiring:job_list`
- Slugs para URLs públicas: `/hiring/professor-matematica/`
- `<slug:slug>/` SEMPRE como última rota no urlpatterns

### Admin
- Usar Django Unfold para todas as customizações de admin
- Importar `ModelAdmin` de `unfold.admin`
- Registrar TODOS os models no admin com boas configurações:
  - `list_display`, `list_filter`, `search_fields`, `prepopulated_fields`
  - Fieldsets organizados logicamente
  - Inline admins onde faz sentido

---

## Checklist de Review (usar ao revisar código do Gemini)

### Models
- [ ] Herda de `TimeStampedModel`/`SEOModel` quando apropriado?
- [ ] Tem `__str__` definido?
- [ ] Tem `Meta.ordering` definido?
- [ ] `verbose_name`/`verbose_name_plural` quando necessário?
- [ ] ForeignKeys têm `on_delete` explícito?
- [ ] ForeignKeys têm `related_name`?
- [ ] Campos opcionais usam `blank=True` (e `null=True` só para non-string)?
- [ ] `upload_to` definido para FileField/ImageField?
- [ ] Tem `get_absolute_url()` para models com URLs públicas?

### Admin
- [ ] Model registrado no admin?
- [ ] Usa `unfold.admin.ModelAdmin` (não `django.contrib.admin.ModelAdmin`)?
- [ ] `list_display` configurado com campos úteis?
- [ ] `list_filter` e `search_fields` configurados?
- [ ] `prepopulated_fields` para slugs?
- [ ] Fieldsets organizados?
- [ ] Actions úteis (publish, archive, export)?

### Views
- [ ] Usa FBV (padrão do projeto)?
- [ ] Tem tratamento de 404 para objetos não encontrados?
- [ ] Formulários têm proteção CSRF?
- [ ] Queries otimizadas (select_related/prefetch_related)?
- [ ] Paginação para listagens?
- [ ] Suporte HTMX (verifica `request.htmx`)?
- [ ] Usa `F()` para updates atômicos (view_count etc.)?

### URLs
- [ ] Namespace definido?
- [ ] Patterns nomeados (para `reverse()`)?
- [ ] Slugs usados para URLs públicas?
- [ ] `<slug:slug>/` é a última rota?

### Templates
- [ ] Extende o base correto (base_school.html ou base_news.html)?
- [ ] Usa `{% block %}` adequadamente?
- [ ] Links usam `{% url %}` (nunca hardcoded)?
- [ ] Imagens usam `{{ image.url }}` (nunca paths hardcoded)?
- [ ] Imagens têm `loading="lazy"` (ou `eager` para hero)?
- [ ] Formulários usam `{% csrf_token %}`?
- [ ] Usa `{% include %}` para componentes reutilizáveis?
- [ ] SEO: Open Graph, Twitter Cards, JSON-LD quando aplicável?

---

## Decisões Registradas

| Data | Decisão | Justificativa |
|------|---------|---------------|
| 2026-02-21 | Django + PostgreSQL | ORM robusto, admin built-in, Sites framework |
| 2026-02-21 | HTMX + Alpine.js (sem SPA) | SEO nativo, sem build pipeline, Django-native |
| 2026-02-21 | Django Unfold para admin | UI moderna sem construir painel custom |
| 2026-02-21 | Path-based routing | Simplicidade, sem config DNS, upgrade fácil |
| 2026-02-21 | Docker Compose para dev | Consistência, PostgreSQL local fácil |
| 2026-02-23 | FBV como padrão | Consistência com código existente, sem migrar para CBV |
| 2026-02-23 | Busca com Django Q() | Sem biblioteca externa, volume escolar não justifica Elasticsearch |
| 2026-02-23 | Sidebar via utility function | Evita queries desnecessárias em páginas que não precisam |
| 2026-02-23 | Funcionalidade antes do design | Toda lógica implementada primeiro, design Stitch depois |
| 2026-02-23 | Context processor para nav | Categorias injetadas só em páginas `/news/` |
| 2026-02-23 | unique_together para NewsletterSubscription | `unique_together = [['email', 'site']]` — mesmo email pode assinar sites diferentes |
| 2026-02-23 | Admin agrupado por portal | Sidebar Unfold com grupos School Portal / News Portal / Sistema |
| 2026-02-23 | Dashboard customizado Unfold | Custom view com stats reais, sem biblioteca externa |
| 2026-02-23 | i18n no admin via LocaleMiddleware | PT-BR padrão, EN disponível via seletor na sidebar |

---

## Estado Atual

- **Fase:** 6 — Admin Enhancement (Painel Unificado Bilíngue)
- **Tarefa atual:** Fases 6A-6E no GEMINI.md
- **Próximo:** Gemini executa 6A-6E; Claude revisa; Google Stitch para Fase 7
- **Bloqueios:** Nenhum
- **Última atualização:** 2026-02-23
