#!/usr/bin/env bash
set -eu

readonly ENV_DIR="${1}"
readonly TEMPLATE_PATH="${2}"
readonly OUT_PATH="${3}"

if [ -z "${ENV_DIR}" ] || [ -z "${TEMPLATE_PATH}" ] || [ -z "${OUT_PATH}" ]; then
  printf 'Usage: %s <ENV_DIR> <TEMPLATE_PATH> <OUT_PATH>\n' "$0" >&2
  exit 1
fi

if [ -f "${ENV_DIR}/.env" ]; then
  set -a
  . "${ENV_DIR}/.env"
  set +a
else
  echo -e "Falta o arquivo .env em '${ENV_DIR}'\n" >&2
  exit 127
fi

: "${RMQ_HOST:?}"
: "${RMQ_PORT:?}"

export RMQ_HOST RMQ_PORT

envsubst '$RMQ_HOST $RMQ_PORT' < "${TEMPLATE_PATH}" > "${OUT_PATH}"
exit 0
