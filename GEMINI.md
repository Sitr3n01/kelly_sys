# GEMINI.md — Instruções Kelly Sys

> Leia **"Tarefa Atual"** antes de começar.

## Convenções

- isort, aspas simples (Python) / duplas (UI), FBV, `select_related`/`prefetch_related`
- Admin: `unfold.admin.ModelAdmin`, PT-BR, `DASHBOARD_CALLBACK`
- Templates: `{% url %}`, `{% csrf_token %}`, `loading="lazy"`, **NUNCA `|safe`** — usar `|sanitize_html` ou `|striptags`
- News: SEMPRE `Article.on_site` (nunca `.objects`) em views/feeds/sitemaps
- School: SEMPRE `Page.on_site` (nunca `.objects`) em views/sitemaps
- Paginator: 12 items. HTMX: `request.htmx` → partial
- Sanitização: importar de `apps.common.sanitization` (nunca duplicar listas de tags)
- Segurança: mensagens de erro genéricas (nunca revelar se email/username existe)

---

## Tarefa Atual — Newsletter + Conta do Usuário (Claude)

Sistema de newsletter implementado. Conta do usuário com configurações implementada.

**Concluído:**
- Newsletter: envio de email HTML por ação do admin, preview no navegador
- Conta: toggle newsletter, excluir conta com confirmação de senha
- Admin: campo `newsletter_from_email` e `newsletter_from_name` em SiteExtension
- Migration aplicada: `common` (newsletter_from_email + newsletter_from_name)

**Pendente pós-deploy:**
- `python manage.py makemigrations` (verificar se há pendentes)
- `python manage.py migrate`
- Verificar: `python manage.py check --deploy`
- Configurar SMTP real em `production.py`

**Próximas fases possíveis:**
- 8.5: Responsividade mobile (375px, 768px)
- 9: Site da Escola — construção completa

---

## Critérios de Aceite (genéricos)

1. `manage.py check` → 0 erros
2. Zero `|safe` em templates (usar `grep -r "|safe" templates/`)
3. Todo model com `ForeignKey(Site)` deve ter `on_site = CurrentSiteManager()`
4. Mensagens de validação nunca revelam se dado já existe no sistema
5. Conteúdo HTML sanitizado no `save()` do model (usar `sanitize_content()`)
