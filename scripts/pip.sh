#!/usr/bin/env sh

SCRIPT_DIR="${0%/*}"
. ${SCRIPT_DIR}/globals.sh

sh ${SCRIPT_DIR}/start.sh -d
docker compose ${COMPOSE_FILES} exec flask pip3 ${@}
