#!/usr/bin/env sh

ROOT_DIR="$(dirname "$0")/../"
COMPOSE_FILES="-f ${ROOT_DIR}/docker-compose.yml -f ${ROOT_DIR}/docker-compose.dev.yml -f ${ROOT_DIR}/docker-compose.prod.yml"
