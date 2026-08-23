#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="discord-vps-proxy"
SERVICE_USER="discord-proxy"
INSTALL_DIR="/opt/discord-vps-proxy"
CONFIG_DIR="/etc/discord-vps-proxy"
STATE_DIR="/var/lib/discord-vps-proxy"
LOG_DIR="/var/log/discord-vps-proxy"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
ENV_PATH="${CONFIG_DIR}/proxy.env"
PORT="24080"
ADMIN_CIDR=""

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_root() {
  [ "$(id -u)" -eq 0 ] || die "run as root: sudo ./uninstall.sh"
}

assert_path() {
  case "$1" in
    "${INSTALL_DIR}"|"${CONFIG_DIR}"|"${STATE_DIR}"|"${LOG_DIR}") ;;
    *) die "refusing to remove unexpected path: $1" ;;
  esac
}

load_env() {
  if [ -f "${ENV_PATH}" ]; then
    # shellcheck disable=SC1090
    . "${ENV_PATH}"
    PORT="${PROXY_PORT:-24080}"
    ADMIN_CIDR="${ADMIN_CIDR:-}"
  fi
}

remove_ufw_rules() {
  command -v ufw >/dev/null 2>&1 || return 0
  while ufw status numbered | grep -F "${SERVICE_NAME}" >/dev/null 2>&1; do
    local num
    num="$(ufw status numbered | grep -F "${SERVICE_NAME}" | sed -E 's/^\[[[:space:]]*([0-9]+)\].*/\1/' | tail -n1)"
    [ -n "${num}" ] || break
    yes | ufw delete "${num}" >/dev/null || break
  done
}

main() {
  require_root
  load_env
  systemctl disable --now "${SERVICE_NAME}.service" >/dev/null 2>&1 || true
  rm -f "${UNIT_PATH}"
  systemctl daemon-reload
  remove_ufw_rules

  for path in "${INSTALL_DIR}" "${CONFIG_DIR}" "${STATE_DIR}" "${LOG_DIR}"; do
    if [ -e "${path}" ]; then
      assert_path "${path}"
      rm -rf "${path}"
    fi
  done

  if id "${SERVICE_USER}" >/dev/null 2>&1; then
    userdel "${SERVICE_USER}" >/dev/null 2>&1 || true
  fi

  echo "Removed ${SERVICE_NAME}. news_portal paths were not touched."
}

main "$@"

