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
4. Incluir: arquivos a modificar/criar, critérios de aceite
5. **NÃO incluir blocos de código completos** — referenciar arquivos existentes

### Depois de cada sessão com Gemini
1. Revisar código produzido contra critérios de aceite
2. Verificar aderência aos padrões (naming, estrutura, imports)
3. **Testar funcionalidade** — acessar /admin/, verificar se dashboard renderiza, clicar nos links
4. Atualizar status no `PLAN.md`
5. Registrar decisões ou mudanças no `CLAUDE.md`
6. **Limpar GEMINI.md** — deletar instruções da tarefa concluída antes de adicionar novas

### Regras para GEMINI.md
- **NUNCA pode exceder 3KB** (~100 linhas)
- Sempre deletar instruções de tarefas concluídas antes de adicionar novas
- Nunca incluir blocos de código completos — referenciar caminhos de arquivos
- Manter apenas: convenções permanentes + tarefa atual + critérios de aceite

### Verificação obrigatória de libs terceiras
- Antes de usar qualquer chave de configuração de lib terceira, **conferir na documentação oficial**
- Unfold docs: https://unfoldadmin.com/docs/configuration/settings/
- Se a chave não existir na docs, NÃO usar — pode ser alucinação do agente

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
- Strings de UI no admin em **PT-BR** (fieldsets, actions, help_text)
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
  - Fieldsets organizados logicamente **em PT-BR**
  - Actions com descriptions **em PT-BR**
  - `help_text` **em PT-BR** para campos que confundem leigos
  - Inline admins onde faz sentido
- **Dashboard:** Usar `DASHBOARD_CALLBACK` (NÃO `INDEX_DASHBOARD`) no UNFOLD settings
  - Callback: função `dashboard_callback(request, context)` retorna context atualizado
  - Template: `templates/admin/index.html` (NÃO `dashboard.html`)
  - Sem CDN externo (Tailwind, fonts) — usar apenas classes Tailwind do Unfold

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
- [ ] Fieldsets organizados **e em PT-BR**?
- [ ] Actions úteis (publish, archive, export) **com descriptions em PT-BR**?
- [ ] Campos com `help_text` em PT-BR para leigos?

### Dashboard / Unfold
- [ ] Chaves no `UNFOLD{}` existem na [docs oficial](https://unfoldadmin.com/docs/configuration/settings/)?
- [ ] Dashboard renderiza corretamente em `/admin/`?
- [ ] Template é `admin/index.html` (não `dashboard.html`)?
- [ ] `DASHBOARD_CALLBACK` aponta para função (não View class)?
- [ ] Sem CDN externo (Tailwind, Google Fonts) no template admin?

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
| 2026-02-23 | Context processor para nav | Categorias injetadas só em páginas `/news/` |
| 2026-02-23 | unique_together para NewsletterSubscription | `unique_together = [['email', 'site']]` — mesmo email pode assinar sites diferentes |
| 2026-02-23 | Admin agrupado por portal | Sidebar Unfold com grupos School Portal / News Portal / Sistema |
| 2026-02-23 | i18n no admin via LocaleMiddleware | PT-BR padrão, EN disponível via seletor na sidebar |
| 2026-02-23 | `?status=received` no link de candidaturas | `Application.Status.RECEIVED = 'received'`, não 'pending' |
| 2026-02-24 | ~~Workflow Stitch/Jules~~ → Design CSS puro | Stitch/Jules falhou — IA externa não entrega código integrável |
| 2026-02-24 | `DASHBOARD_CALLBACK` (não `INDEX_DASHBOARD`) | Chave correta do Unfold. Dashboard anterior nunca funcionou |
| 2026-02-24 | Template `admin/index.html` sem CDN externo | Unfold já compila Tailwind e carrega Material Symbols |
| 2026-02-24 | GEMINI.md max 3KB, sem código inline | Evitar alucinações do Gemini com contexto excessivo |
| 2026-02-24 | Admin inteiro em PT-BR | Fieldsets, actions, help_text — UX para leigos |
| 2026-02-24 | Portais independentes em dados, link apenas na navbar | Único crosslink: botão na navbar do news → escola |
| 2026-02-24 | Tailwind primary como shade scale (objeto com 50-900) | `"primary": "#hex"` flat não gera `text-primary-600`. Precisa de `{ DEFAULT, 50, 100, ..., 900 }` |
| 2026-02-24 | `max-w-[1400px]` padrão para listing pages do news | Dá ~200px extra de respiro vs 1200px, sem mudar aparência. article_detail mantém 960px |
| 2026-02-24 | Auto-set `published_at` no Article.save() | Previne artigos "publicados" sem data que somem das listagens (ordering by -published_at) |
| 2026-02-25 | `CurrentSiteManager` obrigatório em models com ForeignKey(Site) | Page.on_site para consistência com Article.on_site — sitemap/views devem usar `.on_site` |
| 2026-02-25 | CSP com `unsafe-inline`/`unsafe-eval` para Alpine.js + HTMX | Bloqueia scripts externos (vetor principal) sem quebrar funcionalidade reativa |
| 2026-02-25 | Constantes bleach centralizadas em `apps/common/sanitization.py` | Evita duplicação entre Article.save(), Page.save() e template filter |
| 2026-02-25 | Email unique=True no CustomUser (override do AbstractUser) | Constraint no banco > validação no form. Previne duplicatas via shell/admin/migration |
| 2026-02-25 | Mensagens genéricas para validação de existência (email, candidatura) | Previne user enumeration. Atacante não descobre quais emails existem no sistema |
| 2026-02-25 | PASSWORD_RESET_TIMEOUT = 3600 em produção | Token de 24h (default) é excessivo. 1h é suficiente e reduz janela de ataque |
| 2026-02-25 | `server_name _` no nginx para deploy por IP | Catch-all até domínio real ser configurado |

---

## Lições Aprendidas

| Data | Lição | Ação Preventiva |
|------|-------|-----------------|
| 2026-02-24 | Workflow Stitch → Jules falhou: IA externa não entrega código confiável | Nunca depender de ferramenta externa para gerar código de integração |
| 2026-02-24 | `INDEX_DASHBOARD` não existe no Unfold — Gemini alucinhou, Claude não verificou | Sempre conferir docs oficiais antes de usar chave de config de lib terceira |
| 2026-02-24 | GEMINI.md cresceu para 106KB → alucinações do Gemini | Limitar a 3KB, limpar após cada fase, sem blocos de código inline |
| 2026-02-24 | Tailwind flat color (`"primary": "#hex"`) não gera classes com sufixo numérico | Sempre definir cores como objeto com shade scale se partials usam `-100`, `-600` etc |
| 2026-02-24 | HTMX `hx-target` com ID inexistente falha silenciosamente | Sempre verificar que o ID alvo existe no HTML antes de configurar hx-target |
| 2026-02-24 | `Article.on_site` deve ser usado em TODOS os pontos (views, feeds, sitemaps) | Criar checklist: grep por `Article.objects` e validar se deveria ser `.on_site` |
| 2026-02-24 | Dashboard ficou órfã por semanas sem ninguém notar | Adicionar teste de renderização no checklist de review |
| 2026-02-24 | Tailwind CDN sobre Tailwind compilado = conflitos CSS | Nunca carregar CDN sobre framework que já compila Tailwind |
| 2026-02-25 | `\|safe` em help_text de Django forms é um risco oculto | Django validators geram HTML em help_text. Usar `\|striptags` em vez de `\|safe` |
| 2026-02-25 | Email do AbstractUser é `blank=True` sem `unique=True` por padrão | Sempre fazer override com `unique=True` se email é usado para login/reset |
| 2026-02-25 | Constantes de segurança (bleach tags) duplicadas divergem silenciosamente | Centralizar em módulo único. Nunca copiar listas de tags/attrs entre arquivos |
| 2026-02-25 | Sitemap sem filtro de site vaza URLs de outros portais | Todo model com ForeignKey(Site) precisa de CurrentSiteManager em sitemaps |
| 2026-02-25 | Mensagens de erro específicas são vetores de user enumeration | "Email já cadastrado" / "Já se candidatou" revelam dados. Usar mensagens genéricas |

---

## Estado Atual

- **Fase:** 8.6 concluída — Auditoria de Segurança Final (2ª rodada)
- **Tarefa ativa:** Nenhuma
- **Próximo:** 8.5 (responsividade mobile) ou Fase 9 (site da escola)
- **Pendente pós-implementação:** `makemigrations` + `migrate` (email unique + Page manager)
- **Bloqueios:** Nenhum
- **Última atualização:** 2026-02-25
