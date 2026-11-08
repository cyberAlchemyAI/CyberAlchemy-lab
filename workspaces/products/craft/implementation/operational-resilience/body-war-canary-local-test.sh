#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
runtime_dir="$repo_root/projects/domainspec-v2/impl/operational-resilience"
compose_file="$runtime_dir/body-war-canary.compose.yaml"
body_image="body-war-local:orodi-witness"
gateway_image="orodi-body-war-canary-gateway:local"
prom_image="prom/prometheus@sha256:1147c92841726a6fef55fe6124491d6f85480f8de204f7d420304ca5bbd0a8f7"
grafana_image="grafana/grafana@sha256:b0ae311af06228bcfd4a620504b653db80f5b91e94dc3dc2a5b7dab202bcde20"
loki_image="grafana/loki@sha256:70b9f699fc9bb868b62f1cfd4f787dfa50242f1fd92e6089787d5d7daea75fe8"
alloy_image="grafana/alloy@sha256:c958aef7294bc40c67caadb2bcecc93b95ab7961ff8afae3abee170d77426193"
reserved_project="orodi-bw-local-witness"
ports=(18080 18081 18101 18102 19090 13000 13100 14318)

fail() {
  printf 'LOCAL_TEST_READY=false\nERROR=%s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

image_field() {
  docker image inspect "$1" --format "$2" 2>/dev/null || fail "missing local image: $1"
}

preflight() {
  for command_name in docker curl python3 ss sha256sum; do require_command "$command_name"; done
  docker info >/dev/null 2>&1 || fail "Docker daemon unavailable"
  docker compose version >/dev/null 2>&1 || fail "Docker Compose unavailable"

  local body_id gateway_id image platform
  body_id="$(image_field "$body_image" '{{.Id}}')"
  gateway_id="$(image_field "$gateway_image" '{{.Id}}')"
  for image in "$body_image" "$gateway_image" "$prom_image" "$grafana_image" "$loki_image" "$alloy_image"; do
    platform="$(image_field "$image" '{{.Os}}/{{.Architecture}}')"
    [[ "$platform" == "linux/amd64" ]] || fail "image platform is $platform: $image"
  done

  local port
  for port in "${ports[@]}"; do
    if ss -H -ltn "sport = :$port" | grep -q .; then fail "loopback port already in use: $port"; fi
  done
  [[ -z "$(docker ps -aq --filter "label=com.docker.compose.project=$reserved_project")" ]] || fail "reserved ORODI containers already exist"
  [[ -z "$(docker network ls -q --filter "label=com.docker.compose.project=$reserved_project")" ]] || fail "reserved ORODI network already exists"

  ORODI_CONTROL_TOKEN_PATH=/tmp/orodi-preflight-token-placeholder \
  ORODI_BODY_WAR_IMAGE_ID="$body_id" \
  ORODI_RUN_ID=orodi-preflight \
    docker compose --file "$compose_file" config --quiet
  python3 "$runtime_dir/body-war-canary-validate-static.py" >/dev/null

  printf 'LOCAL_TEST_READY=true\n'
  printf 'RUNTIME_EXECUTED=false\n'
  printf 'BODY_WAR_IMAGE_ID=%s\n' "$body_id"
  printf 'GATEWAY_IMAGE_ID=%s\n' "$gateway_id"
  printf 'OBSERVABILITY_IMAGES=3 pinned\n'
  printf 'LOOPBACK_PORTS=free\n'
  printf 'AUTHORITY_EFFECT=none\n'
}

wait_url() {
  local url="$1" attempts=90
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --max-time 2 "$url" >/dev/null; then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "readiness timeout: $url"
}

emit_event() {
  local event_type="$1" phase_name="$2" generation="$3" outcome="$4" fault_state="$5" payload attempts=30
  payload="$(python3 - "$ORODI_RUN_ID" "$event_type" "$phase_name" "$generation" "$outcome" "$fault_state" <<'PY'
import json
import sys
import time

run_id, event_type, phase, generation, outcome, fault_state = sys.argv[1:]
now = str(time.time_ns())
def s(key, value): return {"key": key, "value": {"stringValue": value}}
payload = {
    "resourceLogs": [{
        "resource": {"attributes": [
            s("service.name", "orodi-runner"),
            s("service.namespace", "orodi"),
            s("deployment.environment.name", "local"),
        ]},
        "scopeLogs": [{
            "scope": {"name": "domainspec.orodi.operator-interface.runner", "version": "1"},
            "logRecords": [{
                "timeUnixNano": now,
                "observedTimeUnixNano": now,
                "severityNumber": 9,
                "severityText": "INFO",
                "body": {"stringValue": f"event_type={event_type} phase={phase} generation={generation} outcome={outcome} fault_state={fault_state}"},
                "attributes": [
                    s("run.id", run_id), s("event.type", event_type), s("orodi.phase", phase),
                    {"key": "orodi.generation", "value": {"intValue": generation}},
                    s("orodi.outcome", outcome), s("orodi.fault_state", fault_state),
                ],
            }],
        }],
    }],
}
print(json.dumps(payload, separators=(",", ":")))
PY
)"
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --max-time 2 --header 'Content-Type: application/json' --data-binary "$payload" http://127.0.0.1:14318/v1/logs >/dev/null; then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "operational event was not accepted: $event_type"
}

wait_prom_value() {
  local query="$1" expected="$2" output="$3" attempts=30
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --get --data-urlencode "query=$query" http://127.0.0.1:19090/api/v1/query >"$output" && \
      python3 - "$output" "$expected" <<'PY'
import json
import math
import sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
expected = float(sys.argv[2])
results = doc.get("data", {}).get("result", [])
raise SystemExit(0 if results and math.isclose(float(results[0]["value"][1]), expected, rel_tol=0, abs_tol=1e-9) else 1)
PY
    then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "Prometheus value did not converge: $query = $expected"
}

wait_loki_event() {
  local event_type="$1" output="$2" attempts=30 query
  query="{service_namespace=\"orodi\"} |= \"event_type=$event_type\""
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --get --data-urlencode "query=$query" --data-urlencode 'limit=100' http://127.0.0.1:13100/loki/api/v1/query_range >"$output" && \
      python3 - "$output" <<'PY'
import json
import sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
count = sum(len(stream.get("values", [])) for stream in doc.get("data", {}).get("result", []))
raise SystemExit(0 if count else 1)
PY
    then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "Loki event missing: $event_type"
}

wait_grafana_rule_state() {
  local rule_uid="$1" expected="$2" output="$3" attempts=55
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --max-time 2 \
      http://127.0.0.1:13000/api/prometheus/grafana/api/v1/rules >"$output" && \
      python3 - "$output" "$rule_uid" "$expected" <<'PY'
import json
import sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
uid, expected = sys.argv[2:]
rules = [rule for group in doc.get("data", {}).get("groups", []) for rule in group.get("rules", [])]
matched = [rule for rule in rules if rule.get("uid") == uid]
raise SystemExit(0 if len(matched) == 1 and matched[0].get("state") == expected and matched[0].get("health") == "ok" else 1)
PY
    then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "Grafana rule state did not converge: $rule_uid = $expected"
}

wait_all_grafana_rules_inactive() {
  local output="$1" attempts=55
  while (( attempts > 0 )); do
    if curl --fail --silent --show-error --max-time 2 \
      http://127.0.0.1:13000/api/prometheus/grafana/api/v1/rules >"$output" && \
      python3 - "$output" <<'PY'
import json
import sys
expected = {
    "orodi-telemetry-unavailable",
    "orodi-unsafe-candidate-routing",
    "orodi-candidate-degradation",
    "orodi-stable-degradation",
    "orodi-rollback-incomplete",
}
doc = json.load(open(sys.argv[1], encoding="utf-8"))
rules = [rule for group in doc.get("data", {}).get("groups", []) for rule in group.get("rules", [])]
observed = {rule.get("uid") for rule in rules}
healthy = all(rule.get("state") == "inactive" and rule.get("health") == "ok" and rule.get("provenance") == "file" for rule in rules)
raise SystemExit(0 if observed == expected and healthy else 1)
PY
    then return 0; fi
    attempts=$((attempts - 1))
    sleep 1
  done
  fail "Grafana rules did not converge to five healthy inactive file-provisioned rules"
}

run_commissioning() {
  local keep_live="$1"
  preflight >/dev/null
  local run_root project token_path evidence_dir body_id gateway_id token cleanup_complete=false phase="initialize"
  run_root="$(mktemp -d /tmp/orodi-bw-human.XXXXXX)"
  project="orodi-bw-human-$$"
  token_path="$run_root/control-token"
  evidence_dir="$run_root/evidence"
  mkdir -p "$evidence_dir"
  umask 077
  head -c 48 /dev/urandom | base64 > "$token_path"
  chmod 0600 "$token_path"
  body_id="$(image_field "$body_image" '{{.Id}}')"
  gateway_id="$(image_field "$gateway_image" '{{.Id}}')"
  token="$(tr -d '\r\n' < "$token_path")"
  export ORODI_CONTROL_TOKEN_PATH="$token_path"
  export ORODI_BODY_WAR_IMAGE_ID="$body_id"
  export ORODI_RUN_ID="orodi-bw-$$"

  write_run_result() {
    local exit_code="$1"
    python3 - "$evidence_dir/run-result.json" "$project" "$phase" "$exit_code" <<'PY'
import json
import sys
path, project, phase, exit_code = sys.argv[1:]
with open(path, "w", encoding="utf-8") as handle:
    json.dump({
        "schema_version": "orodi.local-operator-test-run-result/v1",
        "project": project,
        "phase": phase,
        "result": "pass" if exit_code == "0" else "fail",
        "exit_code": int(exit_code),
        "authority_effect": "none",
    }, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY
  }

  capture_runtime_diagnostics() {
    local exit_code="$1"
    docker compose --project-name "$project" --file "$compose_file" ps --all --format json >"$evidence_dir/compose-ps.json" 2>"$evidence_dir/compose-ps.stderr" || true
    docker compose --project-name "$project" --file "$compose_file" logs --no-color --timestamps >"$evidence_dir/compose.log" 2>&1 || true
    printf '%s\n' "$body_id" >"$evidence_dir/body-war-image-id.txt"
    printf '%s\n' "$gateway_id" >"$evidence_dir/gateway-image-id.txt"
    docker image inspect "$prom_image" "$grafana_image" "$loki_image" "$alloy_image" --format '{{.RepoDigests}} {{.Id}} {{.Os}}/{{.Architecture}}' >"$evidence_dir/observability-image-identities.txt"
    write_run_result "$exit_code"
  }

  cleanup() {
    local exit_code=$?
    if [[ "$cleanup_complete" != true ]]; then
      capture_runtime_diagnostics "$exit_code"
      if ! docker compose --project-name "$project" --file "$compose_file" down --volumes --remove-orphans >"$evidence_dir/cleanup.log" 2>&1; then
        exit_code=1
        phase="cleanup"
        write_run_result "$exit_code"
      fi
      cleanup_complete=true
    fi
    rm -f "$token_path"
    if [[ "$exit_code" -ne 0 ]]; then
      printf 'HUMAN_TEST=fail\nEVIDENCE_DIR=%s\nAUTHORITY_EFFECT=none\n' "$evidence_dir" >&2
    fi
    return "$exit_code"
  }
  trap cleanup EXIT INT TERM

  phase="start-observability"
  docker compose --project-name "$project" --file "$compose_file" up --detach prometheus loki alloy grafana
  phase="observability-readiness"
  wait_url http://127.0.0.1:19090/-/ready
  wait_url http://127.0.0.1:13100/ready
  wait_url http://127.0.0.1:13000/api/health
  emit_event commissioning_started commissioning 0 started not_applicable

  phase="start-stable-and-gateway"
  docker compose --project-name "$project" --file "$compose_file" up --detach stable gateway
  phase="stable-readiness"
  wait_url http://127.0.0.1:18101/api/status
  phase="gateway-data-readiness"
  wait_url http://127.0.0.1:18080/api/status
  phase="gateway-control-readiness"
  wait_url http://127.0.0.1:18081/ready
  phase="start-candidate"
  docker compose --project-name "$project" --file "$compose_file" up --detach candidate
  phase="candidate-readiness"
  wait_url http://127.0.0.1:18102/api/status

  phase="install-candidate"
  curl --fail --silent --show-error \
    --header "Authorization: Bearer $token" \
    --header 'Content-Type: application/json' \
    --data "{\"expected_generation\":0,\"action\":{\"kind\":\"install-candidate\",\"target\":\"http://candidate:5174\"},\"at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
    http://127.0.0.1:18081/control/action > "$evidence_dir/install-candidate.json"

  phase="baseline-routing"
  local baseline_candidate=0 baseline_stable=0 headers cohort
  for _request in $(seq 1 100); do
    headers="$(curl --fail --silent --show-error --dump-header - --output /dev/null http://127.0.0.1:18080/api/status)"
    cohort="$(printf '%s\n' "$headers" | awk -F': ' 'tolower($1)=="x-orodi-cohort" {gsub("\r", "", $2); print $2}')"
    if [[ "$cohort" == candidate ]]; then baseline_candidate=$((baseline_candidate + 1)); else baseline_stable=$((baseline_stable + 1)); fi
  done
  [[ "$baseline_candidate" -eq 10 && "$baseline_stable" -eq 90 ]] || fail "baseline split was $baseline_stable/$baseline_candidate"
  emit_event baseline_verified baseline 1 pass inactive
  wait_prom_value orodi_gateway_candidate_weight 0.1 "$evidence_dir/prometheus-query-baseline.json"

  phase="activate-candidate-fault"
  curl --fail --silent --show-error \
    --header "Authorization: Bearer $token" \
    --header 'Content-Type: application/json' \
    --data "{\"expected_generation\":1,\"action\":{\"kind\":\"set-candidate-fault\",\"active\":true},\"at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
    http://127.0.0.1:18081/control/action > "$evidence_dir/activate-fault.json"

  phase="fault-window"
  local fault_503=0 status
  for _request in $(seq 1 100); do
    status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' http://127.0.0.1:18080/api/status)"
    if [[ "$status" == 503 ]]; then fault_503=$((fault_503 + 1)); elif [[ "$status" != 200 ]]; then fail "unexpected gateway status during fault window: $status"; fi
  done
  [[ "$fault_503" -eq 10 ]] || fail "candidate-only fault count was $fault_503"
  emit_event fault_window_verified fault_window 2 pass active
  wait_prom_value orodi_gateway_candidate_fault_active 1 "$evidence_dir/prometheus-query-fault.json"

  phase="alert-firing"
  wait_grafana_rule_state orodi-unsafe-candidate-routing firing "$evidence_dir/grafana-alert-unsafe-candidate-firing.json"

  phase="rollback"
  curl --fail --silent --show-error \
    --header "Authorization: Bearer $token" \
    --header 'Content-Type: application/json' \
    --data "{\"expected_generation\":2,\"action\":{\"kind\":\"rollback\"},\"at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
    http://127.0.0.1:18081/control/action > "$evidence_dir/rollback.json"
  phase="rollback-restoration"
  for _request in $(seq 1 20); do curl --fail --silent --show-error http://127.0.0.1:18080/api/status >/dev/null; done
  for _request in $(seq 1 5); do curl --fail --silent --show-error http://127.0.0.1:18101/api/status >/dev/null; done
  curl --fail --silent --show-error http://127.0.0.1:18081/control/state > "$evidence_dir/final-state.json"
  python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); assert s["candidate_target"] is None and s["candidate_weight"] == 0 and s["stable_weight"] == 100 and not s["candidate_fault_active"]' "$evidence_dir/final-state.json"
  emit_event rollback_restored rollback_restoration 3 pass inactive
  wait_prom_value orodi_gateway_candidate_weight 0 "$evidence_dir/prometheus-query-rollback.json"
  wait_prom_value orodi_gateway_candidate_fault_active 0 "$evidence_dir/prometheus-query-rollback-fault.json"
  wait_prom_value orodi_gateway_candidate_reference_present 0 "$evidence_dir/prometheus-query-rollback-reference.json"
  wait_prom_value orodi_gateway_config_generation 3 "$evidence_dir/prometheus-query-generation.json"

  phase="alert-recovery"
  wait_grafana_rule_state orodi-unsafe-candidate-routing inactive "$evidence_dir/grafana-alert-unsafe-candidate-recovered.json"
  wait_all_grafana_rules_inactive "$evidence_dir/grafana-alert-rules-final.json"
  curl --fail --silent --show-error http://127.0.0.1:13000/api/alertmanager/grafana/api/v2/alerts > "$evidence_dir/grafana-active-alerts-final.json"
  python3 -c 'import json,sys; assert json.load(open(sys.argv[1], encoding="utf-8")) == []' "$evidence_dir/grafana-active-alerts-final.json"
  docker compose --project-name "$project" --file "$compose_file" logs --no-color grafana > "$evidence_dir/grafana-alerting.log" 2>&1
  if grep -Eiq 'notify attempt|failed to send notification|sending alert notification' "$evidence_dir/grafana-alerting.log"; then
    fail "Grafana attempted notification delivery"
  fi
  printf 'notification_delivery_attempts=0\nroute=always-muted\nsink=http://127.0.0.1:9/orodi-disabled\n' > "$evidence_dir/grafana-notification-audit.txt"

  phase="event-conservation"
  wait_loki_event install_candidate "$evidence_dir/loki-events-install-candidate.json"
  wait_loki_event candidate_fault_activated "$evidence_dir/loki-events-candidate-fault.json"
  wait_loki_event rollback "$evidence_dir/loki-events-rollback.json"
  wait_loki_event rollback_restored "$evidence_dir/loki-events-rollback-restored.json"
  emit_event machine_gates_passed machine_gates 3 pass inactive
  wait_loki_event machine_gates_passed "$evidence_dir/loki-events-machine-gates.json"
  curl --fail --silent --show-error --get --data-urlencode 'query={service_namespace="orodi"}' --data-urlencode 'limit=200' http://127.0.0.1:13100/loki/api/v1/query_range > "$evidence_dir/loki-events.json"
  python3 - "$evidence_dir/loki-events.json" <<'PY'
import json
import sys
text = json.dumps(json.load(open(sys.argv[1], encoding="utf-8"))).lower()
for forbidden in ("authorization", "control-token", "request.body", "user.email", "password", "secret"):
    assert forbidden not in text, forbidden
PY

  phase="dashboard-provisioning"
  curl --fail --silent --show-error http://127.0.0.1:13000/api/dashboards/uid/orodi-body-war-canary > "$evidence_dir/grafana-dashboard.json"
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["dashboard"]["uid"] == "orodi-body-war-canary" and len(d["dashboard"]["panels"]) == 10 and any(p.get("type") == "alertlist" for p in d["dashboard"]["panels"])' "$evidence_dir/grafana-dashboard.json"
  curl --fail --silent --show-error http://127.0.0.1:19090/-/ready > "$evidence_dir/prometheus-ready.txt"
  curl --fail --silent --show-error http://127.0.0.1:18080/api/status > "$evidence_dir/final-gateway-status.json"

  phase="postimage-evidence"
  sha256sum \
    "$runtime_dir/body-war-canary.compose.yaml" \
    "$runtime_dir/body-war-canary.prometheus.yml" \
    "$runtime_dir/body-war-canary-local-test.sh" \
    "$runtime_dir/body-war-canary-validate-static.py" \
    "$runtime_dir/body-war-canary.grafana-datasources.yml" \
    "$runtime_dir/body-war-canary.grafana-dashboard-provider.yml" \
    "$runtime_dir/body-war-canary.grafana-dashboard.json" \
    "$runtime_dir/body-war-canary.grafana-alerts.yml" \
    "$runtime_dir/body-war-canary.loki.yml" \
    "$runtime_dir/body-war-canary.alloy" \
    "$runtime_dir/BODY-WAR-CANARY-OPERATOR.md" \
    "$runtime_dir/src/body-war-canary-gateway-entry.ts" \
    "$runtime_dir/src/body-war-canary-gateway-server.ts" \
    "$runtime_dir/src/body-war-canary-gateway-metrics.ts" \
    "$runtime_dir/src/body-war-canary-operational-event.ts" \
    "$runtime_dir/test/body-war-canary-gateway-server.test.ts" \
    "$runtime_dir/test/body-war-canary-gateway-metrics.test.ts" \
    "$runtime_dir/test/body-war-canary-operational-event.test.ts" \
    > "$evidence_dir/implementation-postimages.sha256"
  printf '{"schema_version":"orodi.local-operator-test-summary/v1","project":"%s","run_id":"%s","body_war_image_id":"%s","baseline_stable":%d,"baseline_candidate":%d,"fault_503":%d,"rollback":"pass","metrics":"pass","events":"pass","alerts":"firing-and-recovery-pass","notification_delivery_attempts":0,"dashboard":"pass","authority_effect":"none"}\n' \
    "$project" "$ORODI_RUN_ID" "$body_id" "$baseline_stable" "$baseline_candidate" "$fault_503" > "$evidence_dir/summary.json"

  phase="completed"
  if [[ "$keep_live" == true ]]; then
    capture_runtime_diagnostics 0
    printf '#!/usr/bin/env bash\nset -euo pipefail\nORODI_CONTROL_TOKEN_PATH=%q ORODI_BODY_WAR_IMAGE_ID=%q ORODI_RUN_ID=%q docker compose --project-name %q --file %q down --volumes --remove-orphans\nrm -f %q\n' \
      "$token_path" "$body_id" "$ORODI_RUN_ID" "$project" "$compose_file" "$token_path" > "$run_root/cleanup.sh"
    chmod 0700 "$run_root/cleanup.sh"
    trap - EXIT INT TERM
    printf 'OPERATOR_TEST=machine-pass\nOPERATOR_INTERFACE_URL=http://127.0.0.1:13000/d/orodi-body-war-canary/orodi-body-war-canary\nEVIDENCE_DIR=%s\nCLEANUP_SCRIPT=%s\nPROJECT=%s\nAUTHORITY_EFFECT=none\n' "$evidence_dir" "$run_root/cleanup.sh" "$project"
    return 0
  fi

  cleanup
  trap - EXIT INT TERM
  [[ -z "$(docker ps -aq --filter "label=com.docker.compose.project=$project")" ]] || fail "project containers remain after cleanup"
  [[ -z "$(docker network ls -q --filter "label=com.docker.compose.project=$project")" ]] || fail "project network remains after cleanup"
  printf 'HUMAN_TEST=pass\nEVIDENCE_DIR=%s\nAUTHORITY_EFFECT=none\n' "$evidence_dir"
}

case "${1:-}" in
  --preflight) preflight ;;
  --human-test) run_commissioning false ;;
  --operator-test) run_commissioning true ;;
  *) fail "usage: $0 --preflight | --human-test | --operator-test" ;;
esac
