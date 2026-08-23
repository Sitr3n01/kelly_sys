#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="discord-vps-proxy"
CONFIG_DIR="/etc/discord-vps-proxy"
ENV_PATH="${CONFIG_DIR}/proxy.env"
PORT="24080"

if [ -f "${ENV_PATH}" ]; then
  # shellcheck disable=SC1090
  . "${ENV_PATH}"
  PORT="${PROXY_PORT:-24080}"
fi

echo "== systemd =="
systemctl --no-pager --full status "${SERVICE_NAME}.service" || true
echo

echo "== listen socket =="
if command -v ss >/dev/null 2>&1; then
  ss -lntup | grep -E "(:${PORT}[[:space:]])" || true
else
  echo "ss not found"
fi
echo

echo "== recent logs =="
journalctl -u "${SERVICE_NAME}.service" -n 100 --no-pager || true
echo

echo "== UFW =="
if command -v ufw >/dev/null 2>&1; then
  ufw status numbered || true
else
  echo "ufw not found"
fi
echo

echo "== news_portal compose health =="
if [ -d /opt/kelly_sys ] && command -v docker >/dev/null 2>&1; then
  (cd /opt/kelly_sys && docker compose -p kellysys -f docker/docker-compose.prod.yml ps) || true
else
  echo "/opt/kelly_sys or docker not available"
fi

