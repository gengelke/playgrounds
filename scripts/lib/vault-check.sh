#!/usr/bin/env bash
# vault-check.sh - Ensure Vault is reachable, starting it if necessary.
#
# Usage (source or call from a Makefile recipe):
#   VAULT_ADDR=<addr> VAULT_DIR=<path> MODE=<mode> bash scripts/lib/vault-check.sh
#
# Required environment variables:
#   VAULT_ADDR  - Vault address, e.g. http://127.0.0.1:8200
#   VAULT_DIR   - Absolute path to the vault service directory
#   MODE        - docker or bare

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_DIR="${VAULT_DIR:?VAULT_DIR must be set}"
MODE="${MODE:-docker}"

http_code="$(curl -s -o /dev/null -w "%{http_code}" "${VAULT_ADDR}/v1/sys/health" 2>/dev/null || true)"

if [[ -n "$http_code" && "$http_code" != "000" ]]; then
    echo "Vault reachable at ${VAULT_ADDR} (HTTP ${http_code})"
else
    echo "Vault not reachable at ${VAULT_ADDR}; starting ${VAULT_DIR} (MODE=${MODE})"
    make -C "${VAULT_DIR}" up MODE="${MODE}"
fi
