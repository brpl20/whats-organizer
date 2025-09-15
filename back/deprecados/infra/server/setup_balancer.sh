#!/usr/bin/env sh

# Generates multi processes based in FLASK_PORT_START and FLASK_PORT_END
UPSTREAM_SERVERS=""
for FLASK_PORT in $(seq -s ' ' ${FLASK_PORT_START} ${FLASK_PORT_END}); do
  UPSTREAM_SERVERS="${UPSTREAM_SERVERS}server ${NGINX_LOCALHOST}:${FLASK_PORT};\n"
done
export UPSTREAM_SERVERS
