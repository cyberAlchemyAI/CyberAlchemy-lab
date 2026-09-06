import assert from "node:assert/strict";
import test from "node:test";
import { applyGatewayControl, initialGatewayState } from "../src/body-war-canary-gateway-state.js";
import { auditGatewaySequence, routeGatewayRequest } from "../src/body-war-canary-gateway-router.js";

const active = () => {
  const initial = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  const installed = applyGatewayControl(initial, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z");
  assert.equal(installed.status, "applied");
  if (installed.status !== "applied") throw new Error("install failed");
  return installed.after;
};

test("bounded sequence is exactly 90/10", () => {
  const audit = auditGatewaySequence(active(), 1, 100);
  assert.deepEqual({ stable: audit.stable_selected, candidate: audit.candidate_selected, stableFaults: audit.stable_injected_fault_count, accounting: audit.accounting_equal }, { stable: 90, candidate: 10, stableFaults: 0, accounting: true });
});

test("fault injection is candidate-only and pre-forward", () => {
  const state = active();
  const faulted = applyGatewayControl(state, 1, { kind: "set-candidate-fault", active: true }, "2026-09-02T00:00:02Z");
  assert.equal(faulted.status, "applied");
  if (faulted.status !== "applied") return;
  for (let sequence = 1; sequence <= 100; sequence += 1) {
    const decision = routeGatewayRequest(faulted.after, sequence);
    assert.equal(decision.action === "inject-503", decision.cohort === "candidate");
  }
  assert.deepEqual(auditGatewaySequence(faulted.after, 1, 100), {
    first_sequence: 1, last_sequence: 100, stable_selected: 90, candidate_selected: 10,
    stable_injected_fault_count: 0, candidate_injected_fault_count: 10,
    forwarded_stable: 90, forwarded_candidate: 0, accounting_equal: true,
  });
});

test("missing candidate and rollback are stable-only", () => {
  const initial = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  assert.equal(auditGatewaySequence(initial, 1, 100).candidate_selected, 0);
  assert.throws(() => routeGatewayRequest(initial, 0), /GATEWAY_SEQUENCE_INVALID/);
});
