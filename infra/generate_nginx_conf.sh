#!/usr/bin/env sh
set -eu

ENV_DIR=${ENV_DIR:-"$HOME"}
TEMPLATE_PATH=${TEMPLATE_PATH:-"infra/nginx.conf.tpl"}
OUT_PATH=${OUT_PATH:-"nginx.conf.rendered"}
NGINX_LOCALHOST=${NGINX_LOCALHOST:-"127.0.0.1"}

if [ ! -f "${ENV_DIR}/.env" ]; then
  printf 'missing .env\n' >&2
  exit 127
fi

get_var() {
  key="$1"
  grep -E "^${key}=" "${ENV_DIR}/.env" | tail -n1 | sed -e "s/^${key}=//" -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

FLASK_PORT_START=$(get_var FLASK_PORT_START)
FLASK_PORT_END=$(get_var FLASK_PORT_END)
PORT=$(get_var PORT)

: "${FLASK_PORT_START:?}"
: "${FLASK_PORT_END:?}"
: "${PORT:?}"

start=$(expr "${FLASK_PORT_START}" + 0)
end=$(expr "${FLASK_PORT_END}" + 0)
if [ "${start}" -gt "${end}" ]; then
  tmp=${start}; start=${end}; end=${tmp}
fi

UPSTREAM_SERVERS=""
p=${start}
while [ "${p}" -le "${end}" ]; do
  UPSTREAM_SERVERS=$(printf '%sserver %s:%s;\n' "${UPSTREAM_SERVERS}" "${NGINX_LOCALHOST}" "${p}")
  p=$((p + 1))
done

CF4=""
CF6=""
if command -v curl >/dev/null 2>&1; then
  CF4=$(curl -fsSL https://www.cloudflare.com/ips-v4 || true)
  CF6=$(curl -fsSL https://www.cloudflare.com/ips-v6 || true)
elif command -v wget >/dev/null 2>&1; then
  CF4=$(wget -qO- https://www.cloudflare.com/ips-v4 || true)
  CF6=$(wget -qO- https://www.cloudflare.com/ips-v6 || true)
fi

CLOUDFLARE_IPS_FIREWALL=""
for ip in $(printf '%s\n%s\n' "${CF4}" "${CF6}" | awk 'NF'); do
  CLOUDFLARE_IPS_FIREWALL=$(printf '%sallow %s;\n' "${CLOUDFLARE_IPS_FIREWALL}" "${ip}")
done
CLOUDFLARE_IPS_FIREWALL=$(printf '%sallow 127.0.0.1;\n' "${CLOUDFLARE_IPS_FIREWALL}")

CLOUDFLARE_REAL_IP=""
for ip in $(printf '%s\n%s\n' "${CF4}" "${CF6}" | awk 'NF'); do
  CLOUDFLARE_REAL_IP=$(printf '%sset_real_ip_from %s;\n' "${CLOUDFLARE_REAL_IP}" "${ip}")
done
CLOUDFLARE_REAL_IP=$(printf '%sreal_ip_header CF-Connecting-IP;\nreal_ip_recursive on;\n' "${CLOUDFLARE_REAL_IP}")

export FLASK_PORT_START FLASK_PORT_END PORT UPSTREAM_SERVERS CLOUDFLARE_IPS_FIREWALL CLOUDFLARE_REAL_IP NGINX_LOCALHOST

envsubst '$FLASK_PORT_START $FLASK_PORT_END $PORT $UPSTREAM_SERVERS $CLOUDFLARE_IPS_FIREWALL $CLOUDFLARE_REAL_IP $NGINX_LOCALHOST' < "${TEMPLATE_PATH}" > "${OUT_PATH}"
exit 0
