import assert from "node:assert/strict";
import test from "node:test";
import { buildOtlpLogPayload, createOperationalEventPublisher } from "../src/body-war-canary-operational-event.js";

const rollback = {
  event_type: "rollback" as const,
  phase: "control_transition" as const,
  generation: 3,
  outcome: "applied" as const,
  fault_state: "inactive" as const,
  at: "2026-09-02T12:00:00.000Z",
};

test("OTLP payload is bounded and excludes sensitive fields", () => {
  const text = JSON.stringify(buildOtlpLogPayload("orodi-test-1", rollback));
  for (const required of ["service.name", "service.namespace", "run.id", "event.type", "orodi.phase", "orodi.generation", "orodi.outcome", "orodi.fault_state"]) {
    assert.match(text, new RegExp(required.replace(".", "\\.")));
  }
  for (const forbidden of ["authorization", "control-token", "request.body", "user.email", "password", "secret"]) {
    assert.doesNotMatch(text.toLowerCase(), new RegExp(forbidden.replace(".", "\\.")));
  }
});

test("publisher uses only the fixed Alloy OTLP HTTP endpoint", async () => {
  let request: { input: string; init?: RequestInit } | undefined;
  const fetchImpl: typeof fetch = async (input, init) => {
    request = { input: String(input), init };
    return new Response(null, { status: 200 });
  };
  const publisher = createOperationalEventPublisher("http://alloy:4318/v1/logs", "orodi-test-1", fetchImpl);
  await publisher.publish(rollback);
  assert.equal(request?.input, "http://alloy:4318/v1/logs");
  assert.equal(request?.init?.method, "POST");
  assert.equal((request?.init?.headers as Record<string, string>)["content-type"], "application/json");
  assert.throws(() => createOperationalEventPublisher("http://127.0.0.1:4318/v1/logs", "orodi-test-1"), /ORODI_OTLP_LOGS_ENDPOINT_INVALID/);
  assert.throws(() => createOperationalEventPublisher("http://alloy:4318/v1/logs", "unbounded/value"), /ORODI_RUN_ID_INVALID/);
});

test("publisher fails closed when Alloy rejects the event", async () => {
  const publisher = createOperationalEventPublisher(
    "http://alloy:4318/v1/logs",
    "orodi-test-1",
    async () => new Response(null, { status: 503 }),
  );
  await assert.rejects(publisher.publish(rollback), /ORODI_OPERATIONAL_EVENT_REJECTED/);
});
