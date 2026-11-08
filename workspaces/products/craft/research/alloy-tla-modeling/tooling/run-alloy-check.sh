#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/formal-tools-common.sh
source "$SCRIPT_DIR/lib/formal-tools-common.sh"

usage() {
  cat <<'USAGE'
Usage:
  run-alloy-check.sh [--receipt PATH] [Alloy CLI args...]

Examples:
  run-alloy-check.sh help
  run-alloy-check.sh version
  run-alloy-check.sh commands projects/.../examples/OrderFulfillmentSaga.alloy
USAGE
}

receipt=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --receipt)
      [[ $# -ge 2 ]] || formal_die "--receipt requires a path"
      receipt="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  set -- help
fi

formal_require_alloy
formal_run_with_receipt "$receipt" "$JAVA_BIN_ABS" -jar "$ALLOY_JAR_ABS" "$@"
