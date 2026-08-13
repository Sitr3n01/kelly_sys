# VPS Optimization Runbook

Runbook para controlar crescimento de disco e CPU na VPS Hostinger em
producao. Execute comandos como `root`/`sudo` e nunca use `docker volume prune`,
`docker compose down -v` ou remocao manual em `/var/lib/docker/volumes`.

## Sintomas e causa provavel

Tres causas confirmadas ja foram corrigidas em codigo. Esta tabela existe para o
proximo incidente comecar por evidencia, nao por palpite.

| Sinal | Causa |
|---|---|
| `last-approved-sha` ausente/desatualizado e dezenas de "Deploying approved commit" por dia | Deploy em loop de retry. Corrigido pela trava `.attempt` em `kellysys-deploy-approved`; ver [secure-deploy.md](secure-deploy.md) §2.1 |
| Numero de dumps muito maior que o de deploys aprovados | O mesmo loop, visto pelo disco |
| Imagens `kellysys-web` cada uma maior que a anterior | Dumps entrando na imagem pelo build context. Corrigido movendo `BACKUP_DIR` para `/var/backups/kellysys` e adicionando `backups/` ao `.dockerignore` |
| OOM kill de gunicorn/python em `dmesg` | Cron rodando `manage.py` dentro do cgroup do `web` |
| `django_session` ou `wagtailcore_revision` no topo do `pg_stat_user_tables` | Sessao gravada por crawler anonimo / revisoes do Wagtail nunca purgadas |

## Diagnostico

```bash
cd /opt/kelly_sys

df -hT
sudo du -xhd1 / | sort -h
sudo du -xhd1 /var | sort -h
sudo du -xhd1 /var/lib/docker | sort -h
sudo du -sh /var/backups/kellysys /var/log 2>/dev/null || true

docker system df -v
docker compose -p kellysys -f docker/docker-compose.prod.yml ps
docker stats --no-stream

sudo find /var/lib/docker/containers -name '*-json.log' -printf '%s %p\n' | sort -nr | head -20
sudo journalctl --disk-usage

docker compose -p kellysys -f docker/docker-compose.prod.yml exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT relname, n_live_tup, n_dead_tup, pg_size_pretty(pg_total_relation_size(relid)) AS total FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 20;"'
```

Depois do bloco acima, o que ele nao cobre:

```bash
# A. O poller de deploy esta em loop de retry?
systemctl list-timers 'kellysys-*' --no-pager
journalctl -u kellysys-approved-deploy.service --since today --no-pager | grep -c 'Deploying approved commit'
cat /var/lib/kellysys-deploy/last-approved-sha 2>/dev/null || echo 'STATE FILE AUSENTE'
ls -la /var/lib/kellysys-deploy/

# B. Crescimento das imagens
ls -1 /var/backups/kellysys/postgres-*.sql.gz 2>/dev/null | wc -l
du -sh /var/backups/kellysys
docker images --format '{{.Repository}}:{{.Tag}}  {{.Size}}  {{.CreatedSince}}' | grep -i kellysys

# C. Pressao de memoria
free -m
dmesg -T 2>/dev/null | grep -iE 'oom|killed process' | tail -20
```

## Aplicacao

```bash
cd /opt/kelly_sys
git pull --ff-only origin master

sudo install -o root -g root -m 0755 scripts/deploy/kellysys-deploy /usr/local/sbin/kellysys-deploy
sudo install -o root -g root -m 0755 scripts/deploy/kellysys-deploy-approved /usr/local/sbin/kellysys-deploy-approved
sudo install -o root -g root -m 0755 scripts/deploy/kellysys-maintenance /usr/local/sbin/kellysys-maintenance

# Passo unico: move os dumps para fora do build context do Docker.
sudo install -d -m 0700 /var/backups/kellysys
sudo mv /opt/kelly_sys/backups/postgres-*.sql.gz /var/backups/kellysys/ 2>/dev/null || true
sudo rmdir /opt/kelly_sys/backups 2>/dev/null || true

# Passo unico: descarta as imagens que ja carregam dumps embutidos.
sudo docker image prune -af

sudo /usr/local/sbin/kellysys-deploy
sudo /usr/local/sbin/kellysys-maintenance

# Opcional, em janela curta: aplica a nova politica de log tambem ao Postgres.
sudo docker compose -p kellysys -f docker/docker-compose.prod.yml up -d --no-deps --force-recreate db
```

Se a cadencia do poller mudou em [secure-deploy.md](secure-deploy.md), reescreva o
timer com o bloco de la e recarregue:

```bash
sudo systemctl daemon-reload
sudo systemctl restart kellysys-approved-deploy.timer
systemctl list-timers 'kellysys-*' --no-pager
```

## Timer de manutencao

```bash
sudo tee /etc/systemd/system/kellysys-maintenance.service >/dev/null <<'EOF'
[Unit]
Description=KellySys safe daily maintenance
Wants=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/env bash /usr/local/sbin/kellysys-maintenance
EOF

sudo tee /etc/systemd/system/kellysys-maintenance.timer >/dev/null <<'EOF'
[Unit]
Description=Run KellySys safe daily maintenance

[Timer]
OnCalendar=*-*-* 03:20:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now kellysys-maintenance.timer
sudo systemctl start kellysys-maintenance.service
```

## Limpeza preservando os artigos publicados

Artigo publicado vive em dois lugares, e nenhum dos dois pode ser tocado:

- o volume `kellysys_postgres_data` (tabela `news_article`, `cms_media_image`, etc.);
- o volume `kellysys_media_volume` (os arquivos de imagem em si).

**Nunca execute**, em nenhuma circunstancia:

```bash
docker volume prune            # apaga postgres_data e media_volume
docker compose down -v         # idem
rm -rf /var/lib/docker/volumes/kellysys_postgres_data
rm -rf /var/lib/docker/volumes/kellysys_media_volume
```

Medir antes, para saber o que de fato ocupa espaco:

```bash
cd /opt/kelly_sys
df -hT && docker system df
docker run --rm -v kellysys_media_volume:/m alpine:3.20 sh -c 'du -sh /m; du -sh /m/*'
docker compose -p kellysys -f docker/docker-compose.prod.yml exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid)) AS total FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 15;"'
```

### Nivel 1 — descartavel, risco zero

Nada aqui e dado da aplicacao.

```bash
sudo docker container prune -f
sudo docker image prune -af      # descarta tambem as imagens que carregavam dumps
sudo docker builder prune -af
sudo journalctl --vacuum-time=14d
sudo rm -f /var/log/social_sync.log   # substituido por journalctl -t kellysys-social
sudo apt-get clean
```

### Nivel 2 — dado derivado, regenera sozinho

Renditions sao recortes gerados a partir do original; apagar so obriga a
regerar sob demanda. Depois da mudanca para `fill-600x400` nos cards, as
renditions `max-1600x1600` geradas para card viraram peso morto.

```bash
C="docker compose -p kellysys -f /opt/kelly_sys/docker/docker-compose.prod.yml run --rm --no-deps web python manage.py"
$C wagtail_update_image_renditions --purge-only
$C clearsessions
$C clear_expired_verification_codes
```

Rode em janela de baixo trafego e aqueca em seguida, para nenhum visitante
pagar o custo do Pillow:

```bash
curl -s -o /dev/null https://kellyfarias.com.br/news/
curl -s -o /dev/null https://komuniki.com.br/
```

### Nivel 3 — historico, preserva a versao publicada

`purge_revisions` preserva `latest_revision`, publicacao agendada e revisao em
workflow. O corpo do artigo publicado vive em `news_article`, nao na revisao.

```bash
$C purge_revisions --days=30
```

### Nivel 4 — orfaos de midia, somente leitura

Varredura por chave estrangeira **nao basta** neste projeto: o HTML legado de
`Article.content` e o JSON de `Article.body` embutem `/media/...` sem nenhuma FK
que rastreie. O comando abaixo cobre os dois casos e **nunca apaga**.

```bash
$C scan_orphan_media
```

Ele separa o resultado em dois grupos:

- **RISCO ALTO** — qualquer coisa em `original_images/`, que e onde o Wagtail
  guarda o ORIGINAL. Apagar um que ainda esteja em uso destroi a regeneracao de
  todas as renditions daquela imagem. Sai sem linha `rm`, de proposito.
- **baixo risco** — sai com o `rm` pronto, para conferencia e execucao manual.

Confira antes de remover qualquer coisa. Um `_wVaw5BB` no fim do nome costuma
ser sobra de reenvio, mas o arquivo sem sufixo pode ser o que esta em uso.

### Recuperar espaco ja liberado no Postgres

`VACUUM (ANALYZE)` (que o `kellysys-maintenance` ja roda) marca espaco como
reutilizavel, mas nao devolve disco ao SO. `VACUUM FULL` devolve, e trava a
tabela enquanto roda — so em janela de manutencao, e so se o diagnostico
mostrar bloat relevante:

```bash
docker compose -p kellysys -f docker/docker-compose.prod.yml exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "VACUUM FULL wagtailcore_revision;"'
```

## Validacao

```bash
cd /opt/kelly_sys
docker compose -p kellysys -f docker/docker-compose.prod.yml ps
docker stats --no-stream
docker system df
df -hT
systemctl status kellysys-maintenance.timer --no-pager
journalctl -u kellysys-maintenance.service -n 80 --no-pager
curl -sI https://komuniki.com.br/ | head
curl -sI https://kellyfarias.com.br/news/ | head
```

O dump nao pode mais estar dentro da imagem:

```bash
docker run --rm --entrypoint sh kellysys-web -c 'ls /app/backups 2>&1'
```

Esperado: `No such file or directory`.

O poller nao pode mais repetir deploy:

```bash
systemctl list-timers 'kellysys-*' --no-pager
journalctl -u kellysys-approved-deploy.service --since today --no-pager | grep -c 'Deploying approved commit'
ls -la /var/lib/kellysys-deploy/
```

Esperado: uma linha de "Deploying" por commit aprovado — nao por minuto — e
`last-approved-sha.attempt` ausente depois de um deploy bem-sucedido.

O tamanho da imagem tem de ficar estavel entre deploys consecutivos:

```bash
docker images --format '{{.Repository}}  {{.Size}}  {{.CreatedSince}}' | grep -i kellysys
```

## Erro 203/EXEC no timer

`status=203/EXEC` significa que o systemd nao conseguiu executar o comando do
unit file. Reinstale o script e force LF antes de reiniciar o servico:

```bash
cd /opt/kelly_sys
sudo install -o root -g root -m 0755 scripts/deploy/kellysys-maintenance /usr/local/sbin/kellysys-maintenance
sudo sed -i 's/\r$//' /usr/local/sbin/kellysys-maintenance
sudo sed -i 's#^ExecStart=.*#ExecStart=/usr/bin/env bash /usr/local/sbin/kellysys-maintenance#' /etc/systemd/system/kellysys-maintenance.service
sudo systemctl daemon-reload
sudo systemctl reset-failed kellysys-maintenance.service
sudo systemctl start kellysys-maintenance.service
journalctl -u kellysys-maintenance.service -n 80 --no-pager
```
