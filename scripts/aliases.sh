#!/usr/bin/env sh

SCRIPT_DIR="${0%/*}"
. ${SCRIPT_DIR}/globals.sh

alias pip="${SCRIPT_DIR}/pip.sh"
function pip() {
  case $* in
    freeze* )
        shift 1
        command ${SCRIPT_DIR}/pip_freeze.sh
    ;;
    * )
        command ${SCRIPT_DIR}/pip.sh
    ;;
  esac
}
alias pip3="pip"

