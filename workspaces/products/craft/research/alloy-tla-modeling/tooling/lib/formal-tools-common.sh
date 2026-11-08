#!/usr/bin/env bash

formal_tools_repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

FORMAL_PROJECT_ROOT="${FORMAL_PROJECT_ROOT:-$(formal_tools_repo_root)}"
FORMAL_TOOLS_HOME="${FORMAL_TOOLS_HOME:-.formal-tools}"
JAVA_BIN="${JAVA_BIN:-${FORMAL_TOOLS_HOME}/jre/current/bin/java}"
TLA_TOOLS_JAR="${TLA_TOOLS_JAR:-${FORMAL_TOOLS_HOME}/tla/tla2tools-1.7.4.jar}"
ALLOY_JAR="${ALLOY_JAR:-${FORMAL_TOOLS_HOME}/alloy/org.alloytools.alloy.dist-6.2.0.jar}"
FORMAL_RUN_RESULTS_ROOT="${FORMAL_RUN_RESULTS_ROOT:-projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results}"

formal_abs() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$FORMAL_PROJECT_ROOT" "$1" ;;
  esac
}

formal_die() {
  printf 'formal-tools: %s\n' "$*" >&2
  exit 1
}

formal_require_file() {
  local path
  path="$(formal_abs "$1")"
  [[ -f "$path" ]] || formal_die "missing file: $1. Run tooling/install-formal-tools.sh or set the matching env override."
}

formal_require_executable() {
  local path
  path="$(formal_abs "$1")"
  [[ -x "$path" ]] || formal_die "missing executable: $1. Run tooling/install-formal-tools.sh or set JAVA_BIN."
}

formal_init_runtime() {
  JAVA_BIN_ABS="$(formal_abs "$JAVA_BIN")"
  TLA_TOOLS_JAR_ABS="$(formal_abs "$TLA_TOOLS_JAR")"
  ALLOY_JAR_ABS="$(formal_abs "$ALLOY_JAR")"
  FORMAL_RUN_RESULTS_ROOT_ABS="$(formal_abs "$FORMAL_RUN_RESULTS_ROOT")"
  formal_require_executable "$JAVA_BIN"
}

formal_require_tla() {
  formal_init_runtime
  formal_require_file "$TLA_TOOLS_JAR"
}

formal_require_alloy() {
  formal_init_runtime
  formal_require_file "$ALLOY_JAR"
}

formal_print_command() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
}

formal_run_with_receipt() {
  local receipt="$1"
  shift

  if [[ -z "$receipt" ]]; then
    formal_print_command "$@"
    "$@"
    return $?
  fi

  local receipt_abs
  receipt_abs="$(formal_abs "$receipt")"
  mkdir -p "$(dirname "$receipt_abs")"

  set +e
  {
    printf '# Formal Tool Receipt\n\n'
    printf 'Timestamp: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'Command:\n\n```bash\n'
    formal_print_command "$@"
    printf '```\n\nOutput:\n\n```text\n'
    "$@" 2>&1
    status=$?
    printf '```\n\nExit: %s\n' "$status"
    exit "$status"
  } | tee "$receipt_abs"
  status=${PIPESTATUS[0]}
  set -e
  return "$status"
}
