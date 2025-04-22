#!/usr/bin/env sh

SCRIPT_DIR="${0%/*}"
. ${SCRIPT_DIR}/globals.sh

sh ${SCRIPT_DIR}/start.sh -d
"${SCRIPT_DIR}/pip.sh" freeze > "${ROOT_DIR}/requirements.txt"