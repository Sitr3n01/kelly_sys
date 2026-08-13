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
