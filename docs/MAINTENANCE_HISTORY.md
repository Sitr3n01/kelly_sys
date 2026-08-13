# Histórico de Manutenção

> Este documento substitui os antigos roadmaps e cronogramas de desenvolvimento. Como o sistema encontra-se em produção, aqui devem ser registrados apenas os pacotes de manutenção, auditorias de segurança e grandes atualizações realizadas.

---

## [2026-08-12] Contenção do crescimento de disco, RAM e CPU na VPS

- **Sintoma**: depois da entrada do Wagtail e do sistema de backup, disco, RAM e CPU na VPS (1 vCPU / 4 GB) passaram a crescer de forma acelerada. O runbook `docs/technical/vps-optimization.md` já atacava a *limpeza*; este pacote ataca as *fontes*.

### Causas raiz confirmadas

1. **Dumps entrando na imagem Docker** — `docker/docker-compose.prod.yml` builda o `web` com `context: ..` (= `/opt/kelly_sys`); `scripts/deploy/kellysys-deploy` gravava o dump nesse diretório e buildava logo depois; `.dockerignore` não listava `backups/`; o `Dockerfile` faz `COPY . .`. Cada imagem carregava os dumps dos últimos 30 dias — a imagem nº N continha N dumps. Com o prune de 168h, uma semana dessas imagens coexistia: **crescimento quadrático**, além do vazamento de e-mails e hashes de senha para dentro de uma camada.
2. **Loop infinito de deploy** — `kellysys-deploy-approved` só gravava `last-approved-sha` depois do deploy inteiro passar, e o `kellysys-deploy` termina em oito healthchecks. Qualquer falha ali fazia o timer (`OnUnitActiveSec=1min`) repetir o deploy completo — `pg_dump` + `gzip -9`, build, migrate, collectstatic, recriação de containers — a cada minuto, indefinidamente.
3. **Cron dentro do cgroup do `web`** — três crons usavam `docker compose exec -T web`, e cada `manage.py` sobe um Django+Wagtail inteiro (~150–250 MB) dentro do container limitado a 1500M, junto dos workers do Gunicorn. Os dois `*/5` disparavam no mesmo instante.

### Correções

- **Deploy**: trava `.attempt` contra retry infinito; poller de 1min para 10min; `BACKUP_DIR` movido para `/var/backups/kellysys` (fora do build context); `backups/` no `.dockerignore` e no `.gitignore`; retenção de imagem/build cache de 168h para 48h; `gzip -9` para `-6`; verificação de integridade do dump (`gzip -t` + tamanho mínimo) abortando o deploy se falhar.
- **Runtime**: crons passam a `run --rm --no-deps` com `flock`, saída para o journald via `logger` (o `/var/log/social_sync.log` não tinha rotação); Gunicorn de 3×2 para 2×4 com `--preload`; HEALTHCHECK de 30s para 60s.
- **Aplicação**: `robots.txt` (não existia) barrando `/news/search/`; sitemap com `limit=1000`, `.only()`, `get_latest_lastmod` por aggregate e índice de sitemaps com `cache_page` de 6h; dedup de `view_count` sai da sessão para o cache; `card_image_url` em `fill-600x400` separado do `cover_image_url` em `max-1600x1600`; prefetch de renditions; busca com os termos de join em subquery; índice composto `(site, status, -published_at)`.
- **Crescimento contido**: `purge_revisions --days=30` e `clear_expired_verification_codes` agendados; `VACUUM (ANALYZE)` estendido a `django_cache` e `wagtailcore_revision`; `WAGTAILIMAGES_MAX_UPLOAD_SIZE`/`MAX_IMAGE_PIXELS`/`EXTENSIONS` definidos (o default do Wagtail eram 10 MB e 128 MP); `TASKS` declarado explicitamente.

### Bug corrigido de passagem

`/sitemap.xml` devolvia **500** sempre que existia uma página da escola publicada: `apps/school/models.Page` não define `get_absolute_url` e `PageSitemap` não sobrescrevia `location()`. Coberto por teste de regressão.

### Verificação

Suíte de 449 testes passando e `ruff check` limpo. 13 testes novos, incluindo a regressão do `/sitemap.xml`, a trava de que leitura anônima não cria mais linha em `django_session`, e o guarda contra divergência entre os dois tetos de upload de imagem.

> **Pendente de medição**: rodar o bloco de diagnóstico de `docs/technical/vps-optimization.md` antes e depois na VPS e registrar aqui os números de `docker system df`, `df -hT` e `pg_stat_user_tables`.

## [2026-06-11] Reestruturação da Documentação

- **Descrição**: Reestruturação completa da árvore de documentação do projeto.
- **Camadas Criadas**:
  - `docs/user/`: Documentação *User Friendly* com foco nos usuários finais não-técnicos (arquivos Markdown e HTML). Inclui manuais detalhados do admin, publicações, newsletter e redes sociais.
  - `docs/technical/`: Documentação técnica focada em engenharia de software, separada por assuntos (Segurança, Deploy, Guias e Arquitetura).
  - `docs/ai/`: Regras e visões sistêmicas estritas para o auxílio de IA no projeto.
- **Limpeza**: Remoção completa de arquivos de logs de conversas, `roadmap.md` e similares. Arquivos de instrução de agentes na raiz foram completamente limpos de acordo com as restrições atuais do sistema.
