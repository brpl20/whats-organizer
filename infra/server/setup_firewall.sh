#!/usr/bin/env sh

# Necessary workaround to provide ssl in more than one port using free
# cloudflare plan this blocks all IPS outside cloudflare's network, it
# prevents deanonimization via SSL fingreprint (Censys, Shodan...)

CF_IPV4_URL="https://www.cloudflare.com/ips-v4"
CF_IPV6_URL="https://www.cloudflare.com/ips-v6"

CLOUDFLARE_IPS_FIREWALL="$(wget -qO- ${CF_IPV4_URL})\n$(wget -qO- ${CF_IPV6_URL})"

export CLOUDFLARE_IPS_FIREWALL=$(printf "allow %s;\n" $CLOUDFLARE_IPS_FIREWALL)"\n\
allow 127.0.0.1;\n\
# Docker's IP\n\
# allow 172.17.0.0/16;\n\
deny all;\n"
