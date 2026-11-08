import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import test from "node:test";
import { applyGatewayControl, initialGatewayState } from "../src/body-war-canary-gateway-state.js";
import { createBoundedUpstream, gatewayStartupConfigFromEnvironment, prepareGateway } from "../src/body-war-canary-gateway-entry.js";
import { GatewayMetrics } from "../src/body-war-canary-gateway-metrics.js";
import { handleConservedControlPlane, handleControlPlane, handleDataPlane } from "../src/body-war-canary-gateway-server.js";
import type { GatewayOperationalEvent } from "../src/body-war-canary-operational-event.js";

test("data plane forwards stable/candidate and injects faults only for candidate", async () => {
  const metrics = new GatewayMetrics();
  const initial = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  const installed = applyGatewayControl(initial, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z");
  assert.equal(installed.status, "applied"); if (installed.status !== "applied") return;
  const faulted = applyGatewayControl(installed.after, 1, { kind: "set-candidate-fault", active: true }, "2026-09-02T00:00:02Z");
  assert.equal(faulted.status, "applied"); if (faulted.status !== "applied") return;
  const upstream = async (target: string) => ({ status: 200, body: target, duration_seconds: 0.01 });
  const stable = await handleDataPlane(faulted.after, 1, "/api/status", metrics, upstream);
  const candidate = await handleDataPlane(faulted.after, 10, "/api/status", metrics, upstream);
  assert.deepEqual([stable.status, stable.cohort, candidate.status, candidate.cohort], [200, "stable", 503, "candidate"]);
  assert.equal(metrics.accountedRequests(), 2);
});

test("control plane authenticates token binding and generation", () => {
  const state = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  const token = "x".repeat(32);
  const binding = createHash("sha256").update(token).digest("hex");
  assert.equal(handleControlPlane(state, "wrong", binding, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z").status, 401);
  assert.equal(handleControlPlane(state, token, binding, 7, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z").status, 409);
  assert.equal(handleControlPlane(state, token, binding, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z").status, 200);
});

test("applied control transition is conserved before state can advance", async () => {
  const state = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  const token = "x".repeat(32);
  const binding = createHash("sha256").update(token).digest("hex");
  const recorded: GatewayOperationalEvent[] = [];
  const result = await handleConservedControlPlane(
    state,
    token,
    binding,
    0,
    { kind: "install-candidate", target: "http://candidate:3000" },
    "2026-09-02T00:00:01Z",
    { publish: async (event) => { recorded.push(event); } },
  );
  assert.equal(result.status, 200);
  assert.deepEqual(recorded, [{
    event_type: "install_candidate",
    phase: "control_transition",
    generation: 1,
    outcome: "applied",
    fault_state: "inactive",
    at: "2026-09-02T00:00:01Z",
  }]);
  await assert.rejects(
    handleConservedControlPlane(state, token, binding, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z", { publish: async () => { throw new Error("ORODI_OPERATIONAL_EVENT_UNAVAILABLE"); } }),
    /ORODI_OPERATIONAL_EVENT_UNAVAILABLE/,
  );
  assert.equal(state.generation, 0);
});

test("startup configuration fixes three internal listeners and one-second timeout", () => {
  const config = gatewayStartupConfigFromEnvironment({
    ORODI_STABLE_TARGET: "http://stable:5174",
    ORODI_UPSTREAM_TIMEOUT_MS: "1000",
  }, "x".repeat(48), "2026-09-02T00:00:00Z");
  assert.deepEqual({
    stable: config.stable_target,
    data: `${config.data_host}:${config.data_port}`,
    control: `${config.control_host}:${config.control_port}`,
    metrics: `${config.metrics_host}:${config.metrics_port}`,
    timeout: config.upstream_timeout_ms,
    run: config.run_id,
    otlp: config.otlp_logs_endpoint,
  }, {
    stable: "http://stable:5174",
    data: "0.0.0.0:18080",
    control: "0.0.0.0:18081",
    metrics: "0.0.0.0:9464",
    timeout: 1000,
    run: "orodi-local",
    otlp: "http://alloy:4318/v1/logs",
  });
  const prepared = prepareGateway(config, async () => ({ status: 200, body: "ok", duration_seconds: 0.01 }));
  assert.deepEqual(prepared.initialization_order, ["metrics", "data-listener", "control-listener"]);
  assert.equal(prepared.data.listening || prepared.control.listening || prepared.metricsServer.listening, false);
});

test("bounded upstream aborts without opening a listener", async () => {
  const neverFetch: typeof fetch = (_input, init) => new Promise<Response>((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => {
      const error = new Error("aborted");
      error.name = "AbortError";
      reject(error);
    }, { once: true });
  });
  const upstream = createBoundedUpstream(5, neverFetch);
  await assert.rejects(upstream("http://stable:5174", "/api/status"), (error: Error) => error.name === "AbortError");
  assert.throws(() => createBoundedUpstream(1001), /GATEWAY_UPSTREAM_TIMEOUT_INVALID/);
});
