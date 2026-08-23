# Discord VPS SOCKS5 Proxy

Kit para instalar um proxy SOCKS5 isolado na VPS, fora do Docker Compose `kellysys` e fora de `/opt/kelly_sys`.

## O Que Ele Faz

- Instala `sing-box` oficial em `/opt/discord-vps-proxy/bin/sing-box`.
- Cria usuario Linux sem shell: `discord-proxy`.
- Cria config local em `/etc/discord-vps-proxy/config.json`.
- Cria secrets locais em `/etc/discord-vps-proxy/proxy.env`.
- Cria servico systemd `discord-vps-proxy.service`.
- Aplica limites de cgroup: `MemoryHigh=128M`, `MemoryMax=256M`, `CPUWeight=20`, `CPUQuota=30%`, `TasksMax=128`.
- Libera firewall UFW somente para o CIDR informado.

Nao altera `/opt/kelly_sys`, Docker Compose `kellysys`, containers `web/db/nginx`, portas `80/443`, Nginx, Cloudflare ou deploy `kellysys-*`.

## Instalar Na VPS Via GitHub

```bash
cd /tmp
git clone https://github.com/Sitr3n01/news_portal.git news_portal-proxy
cd /tmp/news_portal-proxy/infra/discord-vps-proxy
chmod +x install.sh status.sh uninstall.sh
sudo ./install.sh --admin-cidr SEU.IP.PUBLICO/32
```

Se voce ja esta conectado por SSH a partir do IP que deve ser liberado, o instalador consegue detectar o IP cliente:

```bash
sudo ./install.sh
```

O instalador imprime os valores para o `.env` local do Windows:

```text
EU_PROXY_HOST=<IP_PUBLICO_DA_VPS>
EU_PROXY_PORT=24080
EU_PROXY_USERNAME=<usuario_gerado>
EU_PROXY_PASSWORD=<senha_gerada>
```

## Status Na VPS

```bash
sudo ./status.sh
```

Checks manuais:

```bash
systemctl status discord-vps-proxy --no-pager
journalctl -u discord-vps-proxy -n 100 --no-pager
ss -lntup | grep 24080
cd /opt/kelly_sys
docker compose -p kellysys -f docker/docker-compose.prod.yml ps
```

## Remover Da VPS

```bash
cd /tmp/news_portal-proxy/infra/discord-vps-proxy
sudo ./uninstall.sh
```

O uninstall para o servico, remove unit, binario, config, secrets, estado local e regras UFW marcadas com `discord-vps-proxy`. Nao toca no `news_portal`.

## Windows

Depois de preencher `outputs\discord-eu-proxy\.env`, rode PowerShell como Administrador:

```powershell
cd C:\Users\Sitr3n\Documents\Codex\2026-08-22\files-pasted-by-the-user-voc\outputs\discord-eu-proxy
.\scripts\start.ps1
.\scripts\test.ps1
.\scripts\status.ps1
```

Feche o Discord completamente e abra de novo.

## UDP / Voz Do Discord

SOCKS5 TCP deve funcionar para login/mensagens. Voz, video e screen share dependem de UDP. Se o teste local mostrar UDP `UNKNOWN` ou `UNSUPPORTED`, mantenha TCP e trate voz/video como limitacao do SOCKS5 nessa VPS.

