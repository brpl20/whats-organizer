#!/usr/bin/env bash
set -eu

readonly ENV_FILE="${1}"
readonly TEMPLATE_PATH="${2}"
readonly OUT_PATH="${3}"

if [ -z "${ENV_FILE}" ] || [ -z "${TEMPLATE_PATH}" ] || [ -z "${OUT_PATH}" ]; then
  printf 'Usage: %s <ENV_FILE> <TEMPLATE_PATH> <OUT_PATH>\n' "$0" >&2
  exit 1
fi

if [ -f "${ENV_FILE}/.env" ]; then
  set -a
  . "${ENV_FILE}/.env"
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
