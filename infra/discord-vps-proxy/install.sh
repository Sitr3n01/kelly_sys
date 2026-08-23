#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="discord-vps-proxy"
SERVICE_USER="discord-proxy"
INSTALL_DIR="/opt/discord-vps-proxy"
CONFIG_DIR="/etc/discord-vps-proxy"
STATE_DIR="/var/lib/discord-vps-proxy"
LOG_DIR="/var/log/discord-vps-proxy"
BIN_PATH="${INSTALL_DIR}/bin/sing-box"
CONFIG_PATH="${CONFIG_DIR}/config.json"
ENV_PATH="${CONFIG_DIR}/proxy.env"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
PORT="24080"
ADMIN_CIDR="${ADMIN_CIDR:-}"
ENABLE_UDP="${ENABLE_UDP:-0}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

log() {
  echo "==> $*"
}

require_root() {
  [ "$(id -u)" -eq 0 ] || die "run as root: sudo ./install.sh"
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --admin-cidr)
        [ "$#" -ge 2 ] || die "--admin-cidr requires a value"
        ADMIN_CIDR="$2"
        shift 2
        ;;
      --port)
        [ "$#" -ge 2 ] || die "--port requires a value"
        PORT="$2"
        shift 2
        ;;
      --enable-udp)
        ENABLE_UDP="1"
        shift
        ;;
      -h|--help)
        cat <<EOF
Usage: sudo ./install.sh [--admin-cidr A.B.C.D/32] [--port 24080] [--enable-udp]

Environment:
  ADMIN_CIDR=A.B.C.D/32   Same as --admin-cidr.
  ENABLE_UDP=1            Same as --enable-udp.
EOF
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
  done
}

detect_admin_cidr() {
  if [ -n "${ADMIN_CIDR}" ]; then
    return
  fi
  if [ -n "${SSH_CLIENT:-}" ]; then
    ADMIN_CIDR="$(printf '%s\n' "${SSH_CLIENT}" | awk '{print $1}')/32"
    return
  fi
  die "admin CIDR not detected. Re-run with: sudo ./install.sh --admin-cidr SEU.IP.PUBLICO/32"
}

validate_port() {
  case "${PORT}" in
    ''|*[!0-9]*) die "port must be numeric" ;;
  esac
  [ "${PORT}" -ge 1024 ] && [ "${PORT}" -le 65535 ] || die "port must be between 1024 and 65535"
}

validate_system() {
  [ "$(uname -s)" = "Linux" ] || die "Linux required"
  command -v systemctl >/dev/null 2>&1 || die "systemd/systemctl required"
  command -v curl >/dev/null 2>&1 || die "curl required"
  command -v tar >/dev/null 2>&1 || die "tar required"
  command -v ss >/dev/null 2>&1 || true
}

map_arch() {
  case "$(uname -m)" in
    x86_64|amd64) echo "amd64" ;;
    aarch64|arm64) echo "arm64" ;;
    i386|i686) echo "386" ;;
    *) die "unsupported architecture: $(uname -m)" ;;
  esac
}

random_safe() {
  local length="$1"
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 48 | tr -dc 'A-Za-z0-9_-' | head -c "${length}"
  else
    tr -dc 'A-Za-z0-9_-' </dev/urandom | head -c "${length}"
  fi
}

install_user_and_dirs() {
  local nologin
  nologin="/usr/sbin/nologin"
  [ -x "${nologin}" ] || nologin="/sbin/nologin"
  [ -x "${nologin}" ] || nologin="/bin/false"

  if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
    useradd --system --home-dir "${STATE_DIR}" --shell "${nologin}" "${SERVICE_USER}"
  fi

  install -d -o root -g root -m 0755 "${INSTALL_DIR}/bin"
  install -d -o root -g "${SERVICE_USER}" -m 0750 "${CONFIG_DIR}"
  install -d -o "${SERVICE_USER}" -g "${SERVICE_USER}" -m 0750 "${STATE_DIR}"
  install -d -o "${SERVICE_USER}" -g "${SERVICE_USER}" -m 0750 "${LOG_DIR}"
}

download_sing_box() {
  local arch version asset url tmp exe suffix
  arch="$(map_arch)"
  version="${SING_BOX_VERSION:-1.13.19}"

  log "Resolving official sing-box ${version} release for linux-${arch}"
  url=""
  asset=""
  for suffix in "" "-glibc" "-musl"; do
    asset="sing-box-${version}-linux-${arch}${suffix}.tar.gz"
    url="https://github.com/SagerNet/sing-box/releases/download/v${version}/${asset}"
    if curl -fsIL --retry 2 -H 'User-Agent: discord-vps-proxy-installer' "${url}" >/dev/null; then
      break
    fi
    url=""
    asset=""
  done
  [ -n "${url}" ] || die "could not find official asset for sing-box ${version} linux-${arch}"

  tmp="$(mktemp -d)"
  trap 'rm -rf "${tmp}"' RETURN
  log "Downloading ${asset}"
  curl -fL --retry 3 -H 'User-Agent: discord-vps-proxy-installer' -o "${tmp}/${asset}" "${url}"
  tar -xzf "${tmp}/${asset}" -C "${tmp}"
  exe="$(find "${tmp}" -type f -name sing-box -perm -u+x | head -n1)"
  [ -n "${exe}" ] || die "sing-box executable not found in archive"
  install -o root -g root -m 0755 "${exe}" "${BIN_PATH}"
  "${BIN_PATH}" version
}

write_secrets() {
  local username password
  if [ -f "${ENV_PATH}" ]; then
    # Preserve credentials across reinstalls, but update the operational knobs.
    # shellcheck disable=SC1090
    . "${ENV_PATH}"
    : "${PROXY_USERNAME:?missing PROXY_USERNAME in existing proxy.env}"
    : "${PROXY_PASSWORD:?missing PROXY_PASSWORD in existing proxy.env}"
    cat >"${ENV_PATH}" <<EOF
PROXY_USERNAME=${PROXY_USERNAME}
PROXY_PASSWORD=${PROXY_PASSWORD}
PROXY_PORT=${PORT}
ADMIN_CIDR=${ADMIN_CIDR}
EOF
    chown root:root "${ENV_PATH}"
    chmod 0600 "${ENV_PATH}"
    return
  fi
  username="discord_$(random_safe 8)"
  password="$(random_safe 40)"
  cat >"${ENV_PATH}" <<EOF
PROXY_USERNAME=${username}
PROXY_PASSWORD=${password}
PROXY_PORT=${PORT}
ADMIN_CIDR=${ADMIN_CIDR}
EOF
  chown root:root "${ENV_PATH}"
  chmod 0600 "${ENV_PATH}"
}

load_secrets() {
  # shellcheck disable=SC1090
  . "${ENV_PATH}"
  : "${PROXY_USERNAME:?missing PROXY_USERNAME}"
  : "${PROXY_PASSWORD:?missing PROXY_PASSWORD}"
}

write_config() {
  load_secrets
  cat >"${CONFIG_PATH}" <<EOF
{
  "log": {
    "level": "info",
    "timestamp": true,
    "output": "${LOG_DIR}/sing-box.log"
  },
  "inbounds": [
    {
      "type": "socks",
      "tag": "socks-in",
      "listen": "0.0.0.0",
      "listen_port": ${PORT},
      "users": [
        {
          "username": "${PROXY_USERNAME}",
          "password": "${PROXY_PASSWORD}"
        }
      ]
    }
  ],
  "outbounds": [
    {
      "type": "direct",
      "tag": "direct"
    }
  ],
  "route": {
    "final": "direct"
  }
}
EOF
  chown root:"${SERVICE_USER}" "${CONFIG_PATH}"
  chmod 0640 "${CONFIG_PATH}"
  "${BIN_PATH}" check -c "${CONFIG_PATH}"
}

write_unit() {
  cat >"${UNIT_PATH}" <<EOF
[Unit]
Description=Isolated SOCKS5 proxy for Discord split tunnel
Documentation=https://sing-box.sagernet.org/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
ExecStart=${BIN_PATH} run -c ${CONFIG_PATH}
WorkingDirectory=${STATE_DIR}
Restart=on-failure
RestartSec=3

MemoryHigh=128M
MemoryMax=256M
CPUWeight=20
CPUQuota=30%
TasksMax=128

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
ReadWritePaths=${LOG_DIR} ${STATE_DIR}

[Install]
WantedBy=multi-user.target
EOF
  chmod 0644 "${UNIT_PATH}"
}

configure_firewall() {
  if ! command -v ufw >/dev/null 2>&1; then
    log "ufw not found; skipping firewall rule. Manually allow ${ADMIN_CIDR} to tcp/${PORT}."
    return
  fi

  log "Adding UFW allow rule for ${ADMIN_CIDR} -> tcp/${PORT}"
  ufw allow from "${ADMIN_CIDR}" to any port "${PORT}" proto tcp comment "${SERVICE_NAME}" >/dev/null
  if [ "${ENABLE_UDP}" = "1" ]; then
    log "Adding UFW allow rule for ${ADMIN_CIDR} -> udp/${PORT}"
    ufw allow from "${ADMIN_CIDR}" to any port "${PORT}" proto udp comment "${SERVICE_NAME}" >/dev/null
  fi
  ufw status verbose || true
}

start_service() {
  systemctl daemon-reload
  systemctl enable --now "${SERVICE_NAME}.service"
  sleep 1
  systemctl --no-pager --full status "${SERVICE_NAME}.service" || true
  systemctl is-active --quiet "${SERVICE_NAME}.service" || die "${SERVICE_NAME}.service is not active"
}

print_client_env() {
  load_secrets
  local public_ip
  public_ip="$(curl -fsS --max-time 10 https://api.ipify.org || true)"
  echo
  echo "Windows .env values:"
  echo "EU_PROXY_HOST=${public_ip:-IP_PUBLICO_DA_VPS}"
  echo "EU_PROXY_PORT=${PORT}"
  echo "EU_PROXY_USERNAME=${PROXY_USERNAME}"
  echo "EU_PROXY_PASSWORD=${PROXY_PASSWORD}"
  echo
  echo "Next on Windows:"
  echo "  edit outputs\\discord-eu-proxy\\.env with the values above"
  echo "  run .\\scripts\\start.ps1 as Administrator"
}

main() {
  require_root
  parse_args "$@"
  detect_admin_cidr
  validate_port
  validate_system
  install_user_and_dirs
  download_sing_box
  write_secrets
  write_config
  write_unit
  configure_firewall
  start_service
  print_client_env
}

main "$@"
