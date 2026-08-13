# Histórico de Manutenção

> Este documento substitui os antigos roadmaps e cronogramas de desenvolvimento. Como o sistema encontra-se em produção, aqui devem ser registrados apenas os pacotes de manutenção, auditorias de segurança e grandes atualizações realizadas.

---

## [2026-08-12] Contenção do crescimento de disco, RAM e CPU na VPS

- **Sintoma**: depois da entrada do Wagtail e do sistema de backup, disco, RAM e CPU na VPS (1 vCPU / 4 GB) passaram a crescer de forma acelerada. O runbook `docs/technical/vps-optimization.md` já atacava a *limpeza*; este pacote ataca as *fontes*.

### Causas raiz confirmadas

1. **Dumps entrando na imagem Docker** — `docker/docker-compose.prod.yml` builda o `web` com `context: ..` (= `/opt/kelly_sys`); `scripts/deploy/kellysys-deploy` gravava o dump nesse diretório e buildava logo depois; `.dockerignore` não listava `backups/`; o `Dockerfile` faz `COPY . .`. Cada imagem carregava os dumps dos últimos 30 dias — a imagem nº N continha N dumps. Com o prune de 168h, uma semana dessas imagens coexistia: **crescimento quadrático**, além do vazamento de e-mails e hashes de senha para dentro de uma camada.
2. **Loop infinito de deploy** — `kellysys-deploy-approved` só gravava `last-approved-sha` depois do deploy inteiro passar, e o `kellysys-deploy` termina em oito healthchecks. Qualquer falha ali fazia o timer (`OnUnitActiveSec=1min`) repetir o deploy completo — `pg_dump` + `gzip -9`, build, migrate, collectstatic, recriação de containers — a cada minuto, indefinidamente.
3. **O gatilho: um healthcheck impossível** — `scripts/deploy/kellysys-deploy` exigia HTTP 200 em `https://www.komuniki.com.br/healthz/`, mas `docker/nginx/nginx.conf` tem um server block em 443 dedicado aos hosts `www.*` que faz `return 301` para o apex. A condição nunca poderia ser satisfeita. Todo deploy completava build, migrate, collectstatic e recriação de containers, e morria no oitavo e último healthcheck. Combinado com a causa 2, é o que de fato manteve o loop rodando: o `/var/lib/kellysys-deploy/last-approved-sha` estava parado em **11/06/2026** quando o diagnóstico começou, ou seja, dois meses sem um único deploy bem-sucedido.
4. **Cron dentro do cgroup do `web`** — três crons usavam `docker compose exec -T web`, e cada `manage.py` sobe um Django+Wagtail inteiro (~150–250 MB) dentro do container limitado a 1500M, junto dos workers do Gunicorn. Os dois `*/5` disparavam no mesmo instante.

### Correções

- **Deploy**: trava `.attempt` contra retry infinito; poller de 1min para 10min; `BACKUP_DIR` movido para `/var/backups/kellysys` (fora do build context); `backups/` no `.dockerignore` e no `.gitignore`; retenção de imagem/build cache de 168h para 48h; `gzip -9` para `-6`; verificação de integridade do dump (`gzip -t` + tamanho mínimo) abortando o deploy se falhar.
- **Runtime**: crons passam a `run --rm --no-deps` com `flock`, saída para o journald via `logger` (o `/var/log/social_sync.log` não tinha rotação); Gunicorn de 3×2 para 2×4 com `--preload`; HEALTHCHECK de 30s para 60s.
- **Aplicação**: `robots.txt` (não existia) barrando `/news/search/`; sitemap com `limit=1000`, `.only()`, `get_latest_lastmod` por aggregate e índice de sitemaps com `cache_page` de 6h; dedup de `view_count` sai da sessão para o cache; `card_image_url` em `fill-600x400` separado do `cover_image_url` em `max-1600x1600`; prefetch de renditions; busca com os termos de join em subquery; índice composto `(site, status, -published_at)`.
- **Crescimento contido**: `purge_revisions --days=30` e `clear_expired_verification_codes` agendados; `VACUUM (ANALYZE)` estendido a `django_cache` e `wagtailcore_revision`; `WAGTAILIMAGES_MAX_UPLOAD_SIZE`/`MAX_IMAGE_PIXELS`/`EXTENSIONS` definidos (o default do Wagtail eram 10 MB e 128 MP); `TASKS` declarado explicitamente.

### Achado de segurança durante o diagnóstico

O `git status` da VPS revelou `kellysys_deploy_ed25519` e o `.pub` soltos em `/opt/kelly_sys` — uma chave SSH **privada** dentro do build context, que o `COPY . .` do Dockerfile vinha assando em toda imagem construída. Mesma classe do problema dos dumps. Padrões de material de chave entraram no `.dockerignore` e no `.gitignore`. **A chave precisa ser rotacionada**: ela já esteve dentro de imagens.

### Bug corrigido de passagem

`/sitemap.xml` devolvia **500** sempre que existia uma página da escola publicada: `apps/school/models.Page` não define `get_absolute_url` e `PageSitemap` não sobrescrevia `location()`. Coberto por teste de regressão.

### Verificação

Suíte de 449 testes passando e `ruff check` limpo. 13 testes novos, incluindo a regressão do `/sitemap.xml`, a trava de que leitura anônima não cria mais linha em `django_session`, e o guarda contra divergência entre os dois tetos de upload de imagem.

### Resultado medido na VPS (13/08/2026)

| Métrica | Antes | Depois |
|---|---|---|
| Build cache do Docker | 23,95 GB | 442 MB |
| Disco (`/dev/sda1`, 48 G) | — | 12 G usados, 25% |
| Imagens Docker | — | 4, 1,338 GB |
| Volumes locais | — | 95,7 MB |
| RAM | — | 1.631 MB de 3.915, com 2.283 disponíveis |
| Swap | — | 81 MB de 2.047 |
| Último deploy bem-sucedido | 11/06/2026 | 13/08/2026 13:52 |
| Tick ocioso do poller | deploy completo (`pg_dump` + build + migrate + collectstatic) | early-exit em menos de 1 s |
| CPU de um deploy completo | — | 1,355 s |
| Órfãos em `media/` | — | 1 arquivo, 0,1 MB |

O deploy de 13/08 13:52 passou os oito healthchecks, incluindo o `https://www.komuniki.com.br/healthz/ -> 301` que era impossível antes, e gravou o state file. Os dois ticks seguintes do timer registraram `Approved commit already deployed` e encerraram — o comportamento que o pacote inteiro existia para restaurar.

A varredura de mídia praticamente não encontrou o que limpar: 0,1 MB de órfão em `original_images/`, deixado no lugar por não valer risco algum. O crescimento nunca esteve em mídia.

## [2026-06-11] Reestruturação da Documentação

- **Descrição**: Reestruturação completa da árvore de documentação do projeto.
- **Camadas Criadas**:
  - `docs/user/`: Documentação *User Friendly* com foco nos usuários finais não-técnicos (arquivos Markdown e HTML). Inclui manuais detalhados do admin, publicações, newsletter e redes sociais.
  - `docs/technical/`: Documentação técnica focada em engenharia de software, separada por assuntos (Segurança, Deploy, Guias e Arquitetura).
  - `docs/ai/`: Regras e visões sistêmicas estritas para o auxílio de IA no projeto.
- **Limpeza**: Remoção completa de arquivos de logs de conversas, `roadmap.md` e similares. Arquivos de instrução de agentes na raiz foram completamente limpos de acordo com as restrições atuais do sistema.
