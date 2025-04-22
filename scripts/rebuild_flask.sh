#!/usr/bin/env sh

SCRIPT_DIR="${0%/*}"
. ${SCRIPT_DIR}/globals.sh

docker compose ${COMPOSE_FILES} up -d
docker compose ${COMPOSE_FILES} up flask --build ${@}
