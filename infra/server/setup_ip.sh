#!/usr/bin/env sh

# Necessary workaround to make nginx see the IP as cloudflare's header IP

CF_IPV4_URL="https://www.cloudflare.com/ips-v4"
CF_IPV6_URL="https://www.cloudflare.com/ips-v6"

CLOUDFLARE_REAL_IP="$(wget -qO- ${CF_IPV4_URL})\n$(wget -qO- ${CF_IPV6_URL})"

export CLOUDFLARE_REAL_IP=$(printf "set_real_ip_from %s;\n" $CLOUDFLARE_REAL_IP)"\n\
real_ip_header CF-Connecting-IP;\n"
