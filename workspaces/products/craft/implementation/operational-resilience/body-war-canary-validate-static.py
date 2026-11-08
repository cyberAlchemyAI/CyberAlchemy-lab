#!/usr/bin/env python3
"""No-effect hostile validator for the bound ORODI local operator interface."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NODE = "node:26.8.1-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3"
PROM = "prom/prometheus@sha256:1147c92841726a6fef55fe6124491d6f85480f8de204f7d420304ca5bbd0a8f7"
GRAFANA = "grafana/grafana@sha256:b0ae311af06228bcfd4a620504b653db80f5b91e94dc3dc2a5b7dab202bcde20"
LOKI = "grafana/loki@sha256:70b9f699fc9bb868b62f1cfd4f787dfa50242f1fd92e6089787d5d7daea75fe8"
ALLOY = "grafana/alloy@sha256:c958aef7294bc40c67caadb2bcecc93b95ab7961ff8afae3abee170d77426193"
PORTS = {
    "127.0.0.1:18080:18080", "127.0.0.1:18081:18081",
    "127.0.0.1:18101:5174", "127.0.0.1:18102:5174",
    "127.0.0.1:19090:9090", "127.0.0.1:13000:3000",
    "127.0.0.1:13100:3100", "127.0.0.1:14318:4318",
}


def validate(
    compose: str, app_dockerfile: str, gateway_dockerfile: str,
    prometheus: str, datasources: str, dashboard_provider: str,
    dashboard: str, alerts: str, loki: str, alloy: str, gateway_entry: str,
    gateway_server: str, gateway_metrics: str, gateway_metrics_test: str, event_source: str, event_test: str,
    runner: str, operator_guide: str,
) -> list[str]:
    errors: list[str] = []
    services: list[str] = []
    in_services = False
    for line in compose.splitlines():
        if line == "services:": in_services = True; continue
        if line == "networks:": in_services = False
        if in_services and line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            services.append(line.strip()[:-1])
    if services != ["stable", "candidate", "gateway", "prometheus", "loki", "alloy", "grafana"]: errors.append("services")
    if compose.count("networks: [experiment]") != 7: errors.append("network-membership")
    if compose.count("driver: bridge") != 1 or compose.count('com.docker.network.bridge.host_binding_ipv4: "127.0.0.1"') != 1: errors.append("loopback-bridge")
    if "\nvolumes:" in compose or "external: true" in compose: errors.append("persistent-or-external")
    observed_ports = set(re.findall(r'"(127\.0\.0\.1:\d+:\d+)"', compose))
    if observed_ports != PORTS: errors.append("ports")
    for token in ("read_only: true", "cap_drop: [ALL]", 'security_opt: ["no-new-privileges:true"]', "pids_limit: 128", "cpus: 0.50", "mem_limit: 256m", "pull_policy: never", "platform: linux/amd64"):
        if compose.count(token) != 7: errors.append(token)
    if compose.count("body-war-local:orodi-witness") != 2: errors.append("identical-app-image")
    for image in (PROM, GRAFANA, LOKI, ALLOY):
        if compose.count(image) != 1: errors.append(f"immutable-image:{image.split('@')[0]}")
    for token in (
        '/prometheus:size=128m,mode=0700,uid=65534,gid=65534',
        '/tmp:size=128m,mode=0700,uid=10001,gid=10001',
        '/var/lib/alloy-data:size=32m,mode=0700,uid=65534,gid=65534',
        '/var/lib/grafana:size=128m,mode=0750,uid=472,gid=0',
    ):
        if compose.count(token) != 1: errors.append(f"ephemeral-storage:{token.split(':')[0]}")
    forbidden = ("privileged:", "network_mode: host", "pid: host", "/var/run/docker.sock", "traefik", "postgres", "strava_token", "ssh://")
    if any(token in compose.lower() for token in forbidden): errors.append("forbidden-scope")
    if app_dockerfile.count(f"FROM {NODE}") != 2 or gateway_dockerfile.count(f"FROM {NODE}") != 2: errors.append("node-digest")
    if "mkdir -p /run/orodi" not in gateway_dockerfile or "USER node" not in gateway_dockerfile: errors.append("gateway-token-mountpoint")
    for token in ("projects/body-war/app", "projects/auth-user-management", "pnpm@10.34.5", 'CMD ["node", "dist/server.js"]', "EXPOSE 5174"):
        if token not in app_dockerfile: errors.append(f"app-build:{token}")
    if "projects/body-war/package.json" in app_dockerfile or "package-lock.json" in app_dockerfile or ".env" in app_dockerfile: errors.append("stale-or-secret-app-input")
    for token in ("BODY_WAR_HOST: 0.0.0.0", 'BODY_WAR_PORT: "5174"', "BODY_WAR_AUTH_BACKEND: memory", 'BODY_WAR_STRAVA_FAKE: "1"', 'BODY_WAR_SECURE_COOKIES: "0"'):
        if compose.count(token) != 2: errors.append(f"app-runtime:{token}")
    if compose.count("/workspace/projects/body-war/app/data:size=4m") != 2: errors.append("app-data-tmpfs")
    if "${ORODI_CONTROL_TOKEN_PATH:?set ORODI_CONTROL_TOKEN_PATH}:/run/orodi/control-token:ro" not in compose: errors.append("control-token-mount")
    if "/run/orodi:size=" in compose: errors.append("control-token-shadowed")
    if "ORODI_OTLP_LOGS_ENDPOINT: http://alloy:4318/v1/logs" not in compose or "ORODI_RUN_ID: ${ORODI_RUN_ID:?set ORODI_RUN_ID}" not in compose: errors.append("gateway-event-binding")
    observability = compose.partition("  prometheus:")[2]
    if any(token in observability.lower() for token in ("control-token", "control/action", "18081", "authorization")): errors.append("observer-actuation-path")

    if "scrape_interval: 2s" not in prometheus or 'targets: ["gateway:9464"]' not in prometheus: errors.append("prometheus-config")
    if "30m" not in compose or "64MB" not in compose or "/prometheus:size=128m" not in compose: errors.append("prometheus-limits")
    for token in ("uid: orodi-prometheus", "url: http://prometheus:9090", "uid: orodi-loki", "url: http://loki:3100", "editable: false"):
        if token not in datasources: errors.append(f"datasource:{token}")
    for token in ("allowUiUpdates: false", "disableDeletion: true", "/var/lib/grafana/dashboards"):
        if token not in dashboard_provider: errors.append(f"dashboard-provider:{token}")
    try:
        dashboard_doc = json.loads(dashboard)
    except json.JSONDecodeError:
        dashboard_doc = {}
        errors.append("dashboard-json")
    dashboard_text = json.dumps(dashboard_doc, sort_keys=True).lower()
    if dashboard_doc.get("uid") != "orodi-body-war-canary" or len(dashboard_doc.get("panels", [])) != 10: errors.append("dashboard-shape")
    for token in ("orodi_gateway_candidate_weight", "orodi_gateway_candidate_fault_active", "orodi_gateway_candidate_reference_present", "orodi_gateway_config_generation", "service_namespace"):
        if token not in dashboard_text: errors.append(f"dashboard-query:{token}")
    if any(token in dashboard_text for token in ("/control/action", "18081/control", "authorization: bearer")): errors.append("dashboard-actuation")
    if "body-war-canary.grafana-alerts.yml:/etc/grafana/provisioning/alerting/orodi.yml:ro" not in compose: errors.append("alert-provisioning-mount")
    required_alerts = {
        "orodi-telemetry-unavailable",
        "orodi-unsafe-candidate-routing",
        "orodi-candidate-degradation",
        "orodi-stable-degradation",
        "orodi-rollback-incomplete",
    }
    alert_rule_block = alerts.partition("muteTimes:")[0]
    observed_alerts = set(re.findall(r"^\s+- uid: (orodi-[a-z-]+)$", alert_rule_block, re.MULTILINE))
    if observed_alerts != required_alerts: errors.append("alert-rule-set")
    if alerts.count("noDataState: Alerting") != 5 or alerts.count("execErrState: Alerting") != 5:
        errors.append("alert-fail-closed-state")
    if alerts.count("notification_settings:") != 5 or alerts.count("mute_time_intervals: [orodi-local-evaluation-only]") != 5:
        errors.append("alert-delivery-not-muted")
    for token in ("muteTimes:", "name: orodi-local-evaluation-only", "start_time: '00:00'", "end_time: '24:00'", "weekdays: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']"):
        if alerts.count(token) != 1: errors.append(f"alert-mute-boundary:{token}")
    for token in (
        "datasourceUid: orodi-prometheus",
        "noDataState: Alerting",
        "execErrState: Alerting",
        "authority: evidence-only",
        "orodi_gateway_candidate_weight",
        "orodi_gateway_candidate_fault_active",
        "orodi_gateway_candidate_reference_present",
        "orodi_gateway_requests_total",
    ):
        if token not in alerts: errors.append(f"alerts:{token}")
    if alerts.count("receiver: ORODI disabled local sink") != 5:
        errors.append("alert-inert-receiver-binding")
    for token in ("contactPoints:", "name: ORODI disabled local sink", "uid: orodi-disabled-local-sink", "type: webhook", "url: http://127.0.0.1:9/orodi-disabled"):
        if alerts.count(token) != 1: errors.append(f"alert-inert-sink:{token}")
    for forbidden_alert_token in (
        "contactPoint:", "notificationPolicies:",
        "smtp", "slack", "pagerduty", "/control/action", "18081", "authorization",
        "https://", "0.0.0.0", "host.docker.internal",
    ):
        if forbidden_alert_token.lower() in alerts.lower(): errors.append(f"alert-external-effect:{forbidden_alert_token}")
    if dashboard_text.count('"type": "alertlist"') + dashboard_text.count('"type":"alertlist"') != 1:
        errors.append("dashboard-alert-list")
    for token in ("auth_enabled: false", "store: tsdb", "object_store: filesystem", "schema: v13", "allow_structured_metadata: true", "reporting_enabled: false"):
        if token not in loki: errors.append(f"loki:{token}")
    for token in ('otelcol.receiver.otlp "orodi"', 'endpoint = "0.0.0.0:4318"', 'otelcol.processor.batch "orodi"', 'otelcol.exporter.otlphttp "orodi_loki"', 'endpoint    = "http://loki:3100/otlp"'):
        if token not in alloy: errors.append(f"alloy:{token}")

    for token in ("createBoundedUpstream", "upstream_timeout_ms", "timeout > 1000", "ORODI_CONTROL_TOKEN_FILE", "GATEWAY_CONTROL_TOKEN_MODE_INVALID", "metrics_port: 9464", "startGateway", "ORODI_OTLP_LOGS_ENDPOINT", "ORODI_RUN_ID"):
        if token not in gateway_entry: errors.append(f"gateway-entry:{token}")
    for token in ('request.url === "/metrics"', '"/control/action"', 'request.url === "/control/state"', "getState", "handleConservedControlPlane", "await events.publish"):
        if token not in gateway_server: errors.append(f"gateway-server:{token}")
    for token in ('const COHORTS: readonly Cohort[] = ["stable", "candidate"]', 'const OUTCOMES: readonly Outcome[] = ["good", "bad"]', 'const STATUS_CLASSES: readonly StatusClass[] = ["2xx", "4xx", "5xx", "timeout", "transport"]', 'this.#requests.get(keyOf(attributes))?.count ?? 0'):
        if token not in gateway_metrics: errors.append(f"gateway-metrics-zero-series:{token}")
    for token in ("counterRows.length, 20", 'outcome="bad",status_class="5xx"\\} 0', 'outcome="good",status_class="transport"\\} 0'):
        if token not in gateway_metrics_test: errors.append(f"gateway-metrics-zero-test:{token}")
    for token in ("service.name", "service.namespace", "run.id", "event.type", "orodi.phase", "orodi.generation", "orodi.outcome", "orodi.fault_state", "ORODI_OTLP_LOGS_ENDPOINT_INVALID"):
        if token not in event_source: errors.append(f"event-source:{token}")
    for forbidden_field in ("authorization", "request.body", "user.email", "password", "secret"):
        if forbidden_field not in event_test.lower(): errors.append(f"event-privacy-test:{forbidden_field}")
    if "ORODI_OPERATIONAL_EVENT_REJECTED" not in event_test or "assert.rejects" not in event_test: errors.append("event-fail-closed-test")

    for mode in ("--preflight", "--human-test", "--operator-test"):
        if mode not in runner: errors.append(f"runner-mode:{mode}")
    if "down --volumes --remove-orphans" not in runner or "docker prune" in runner or "docker system prune" in runner: errors.append("runner-cleanup")
    if "chmod 0600" not in runner or "ORODI_CONTROL_TOKEN_PATH" not in runner: errors.append("runner-token")
    for token in ('ps --all --format json', 'logs --no-color --timestamps', 'run-result.json', 'capture_runtime_diagnostics "$exit_code"', "loki-events", "prometheus-query", "grafana-alert-unsafe-candidate-firing.json", "wait_all_grafana_rules_inactive", "notification_delivery_attempts=0", 'src/body-war-canary-gateway-metrics.ts', 'test/body-war-canary-gateway-metrics.test.ts', "OPERATOR_INTERFACE_URL"):
        if token not in runner: errors.append(f"runner-evidence:{token}")
    preflight = runner.partition("preflight() {")[2].partition("wait_url() {")[0]
    if not preflight or re.search(r"docker\s+(?:pull|build|create|run|start|stop|rm|compose\b.*\b(?:up|down))", preflight): errors.append("preflight-effect")
    for token in ("read-only", "loopback", "Grafana", "Prometheus", "Alloy", "Loki", "human visual"):
        if token.lower() not in operator_guide.lower(): errors.append(f"operator-guide:{token}")
    return sorted(set(errors))


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def main() -> int:
    values = {
        "compose": read("body-war-canary.compose.yaml"),
        "app_dockerfile": read("body-war-canary.Dockerfile"),
        "gateway_dockerfile": read("body-war-canary-gateway.Dockerfile"),
        "prometheus": read("body-war-canary.prometheus.yml"),
        "datasources": read("body-war-canary.grafana-datasources.yml"),
        "dashboard_provider": read("body-war-canary.grafana-dashboard-provider.yml"),
        "dashboard": read("body-war-canary.grafana-dashboard.json"),
        "alerts": read("body-war-canary.grafana-alerts.yml"),
        "loki": read("body-war-canary.loki.yml"),
        "alloy": read("body-war-canary.alloy"),
        "gateway_entry": read("src/body-war-canary-gateway-entry.ts"),
        "gateway_server": read("src/body-war-canary-gateway-server.ts"),
        "gateway_metrics": read("src/body-war-canary-gateway-metrics.ts"),
        "gateway_metrics_test": read("test/body-war-canary-gateway-metrics.test.ts"),
        "event_source": read("src/body-war-canary-operational-event.ts"),
        "event_test": read("test/body-war-canary-operational-event.test.ts"),
        "runner": read("body-war-canary-local-test.sh"),
        "operator_guide": read("BODY-WAR-CANARY-OPERATOR.md"),
    }
    errors = validate(**values)
    assert errors == [], errors
    hostile = {
        "public-bind": values["compose"].replace("127.0.0.1:18080", "0.0.0.0:18080", 1),
        "extra-service": values["compose"].replace("networks:\n", "  postgres:\n    image: postgres:latest\nnetworks:\n", 1),
        "external-network": values["compose"].replace("    driver: bridge\n", "    external: true\n"),
        "missing-limit": values["compose"].replace("    pids_limit: 128\n", "", 1),
        "named-volume": values["compose"] + "\nvolumes:\n  data:\n",
        "docker-socket": values["compose"].replace("    volumes:\n", "    volumes:\n      - /var/run/docker.sock:/var/run/docker.sock\n", 1),
        "unpinned-grafana": values["compose"].replace(GRAFANA, "grafana/grafana:latest"),
        "unpinned-loki": values["compose"].replace(LOKI, "grafana/loki:latest"),
        "unpinned-alloy": values["compose"].replace(ALLOY, "grafana/alloy:latest"),
        "observer-control-port": values["compose"].replace("  grafana:\n", "  grafana:\n    environment:\n      CONTROL_URL: http://gateway:18081/control/action\n", 1),
        "missing-event-binding": values["compose"].replace("      ORODI_OTLP_LOGS_ENDPOINT: http://alloy:4318/v1/logs\n", ""),
        "missing-grafana-limit": values["compose"].replace('    tmpfs: ["/var/lib/grafana:size=128m,mode=0750,uid=472,gid=0"]\n', ""),
    }
    for name, mutated in hostile.items():
        assert validate(**{**values, "compose": mutated}), f"hostile mutation accepted: {name}"
    assert validate(**{**values, "dashboard": values["dashboard"].replace("orodi_gateway_candidate_weight", "/control/action", 1)}), "hostile dashboard actuation accepted"
    assert validate(**{**values, "alerts": values["alerts"].replace("http://127.0.0.1:9/orodi-disabled", "https://example.invalid/orodi", 1)}), "hostile external alert delivery accepted"
    assert validate(**{**values, "alerts": values["alerts"].replace("noDataState: Alerting", "noDataState: OK", 1)}), "hostile alert no-data coercion accepted"
    assert validate(**{**values, "alerts": values["alerts"].replace("mute_time_intervals: [orodi-local-evaluation-only]", "mute_time_intervals: []", 1)}), "hostile unmuted alert accepted"
    assert validate(**{**values, "event_test": values["event_test"].replace("assert.rejects", "assert.doesNotReject", 1)}), "missing event failure check accepted"
    assert validate(**{**values, "gateway_metrics": values["gateway_metrics"].replace("this.#requests.get(keyOf(attributes))?.count ?? 0", "this.#requests.get(keyOf(attributes))?.count ?? 1", 1)}), "hostile zero-series forgery accepted"
    print("STATIC_TOPOLOGY=pass")
    print("SERVICES=7 NETWORKS=1 NAMED_VOLUMES=0")
    print("LOOPBACK_PORTS=8")
    print("ALERT_RULES=5 EXTERNAL_CONTACT_POINTS=0 DELIVERY=always-muted inert-loopback-sink")
    print("HOSTILE_MUTATIONS=18/18 rejected")
    print("RUNTIME_EXECUTED=false")
    print("AUTHORITY_EFFECT=none")
    return 0


if __name__ == "__main__": raise SystemExit(main())
