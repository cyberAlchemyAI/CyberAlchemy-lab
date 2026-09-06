#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/formal-tools-common.sh
source "$SCRIPT_DIR/lib/formal-tools-common.sh"

usage() {
  cat <<'USAGE'
Usage:
  run-tla-check.sh [--receipt PATH] --sany SPEC.tla
  run-tla-check.sh [--receipt PATH] --tlc SPEC.tla [TLC_ARGS...]

Defaults use .formal-tools/ from the repository root.
USAGE
}

receipt=""
mode=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --receipt)
      [[ $# -ge 2 ]] || formal_die "--receipt requires a path"
      receipt="$2"
      shift 2
      ;;
    --sany|--tlc)
      mode="${1#--}"
      shift
      break
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      formal_die "unknown option before mode: $1"
      ;;
  esac
done

[[ -n "$mode" ]] || { usage; exit 2; }
[[ $# -ge 1 ]] || formal_die "$mode requires a SPEC.tla path"

spec="$1"
shift
spec_abs="$(formal_abs "$spec")"
[[ -f "$spec_abs" ]] || formal_die "missing TLA spec: $spec"

formal_require_tla

case "$mode" in
  sany)
    formal_run_with_receipt "$receipt" "$JAVA_BIN_ABS" -cp "$TLA_TOOLS_JAR_ABS" tla2sany.SANY "$spec_abs"
    ;;
  tlc)
    formal_run_with_receipt "$receipt" "$JAVA_BIN_ABS" -cp "$TLA_TOOLS_JAR_ABS" tlc2.TLC "$@" "$spec_abs"
    ;;
esac
