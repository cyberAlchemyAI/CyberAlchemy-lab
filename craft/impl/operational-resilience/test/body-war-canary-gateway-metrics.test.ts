import assert from "node:assert/strict";
import test from "node:test";
import { initialGatewayState } from "../src/body-war-canary-gateway-state.js";
import { GATEWAY_INSTRUMENTS } from "../src/body-war-canary-gateway-instruments.js";
import { GatewayMetrics } from "../src/body-war-canary-gateway-metrics.js";

test("fixed instruments render bounded Prometheus labels and complete accounting", () => {
  const metrics = new GatewayMetrics();
  metrics.recordTerminal({ cohort: "stable", outcome: "good", status_class: "2xx" }, 0.01);
  metrics.recordTerminal({ cohort: "candidate", outcome: "bad", status_class: "5xx" }, 0);
  const text = metrics.renderPrometheus(initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z"));
  assert.equal(metrics.accountedRequests(), 2);
  const counterRows = text.split("\n").filter((line) => line.startsWith("orodi_gateway_requests_total{"));
  assert.equal(counterRows.length, 20);
  assert.match(text, /orodi_gateway_requests_total\{cohort="stable",outcome="good",status_class="2xx"\} 1/);
  assert.match(text, /orodi_gateway_requests_total\{cohort="candidate",outcome="bad",status_class="5xx"\} 1/);
  assert.match(text, /orodi_gateway_requests_total\{cohort="stable",outcome="bad",status_class="5xx"\} 0/);
  assert.match(text, /orodi_gateway_requests_total\{cohort="candidate",outcome="good",status_class="transport"\} 0/);
  for (const name of Object.values(GATEWAY_INSTRUMENTS)) assert.match(text, new RegExp(name));
  assert.doesNotMatch(text, /run_id|request_id|url=|host=|token=/);
  assert.throws(() => metrics.recordTerminal({ cohort: "stable", outcome: "good", status_class: "2xx", request_id: "x" } as never, 0.1), /CARDINALITY/);
});
