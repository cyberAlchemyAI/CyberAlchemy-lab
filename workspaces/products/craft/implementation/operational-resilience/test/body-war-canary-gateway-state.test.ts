import assert from "node:assert/strict";
import test from "node:test";
import { applyGatewayControl, initialGatewayState } from "../src/body-war-canary-gateway-state.js";

test("generation-checked candidate, fault, and rollback transitions", () => {
  const initial = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  const installed = applyGatewayControl(initial, 0, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z");
  assert.equal(installed.status, "applied");
  if (installed.status !== "applied") return;
  assert.deepEqual([installed.after.stable_weight, installed.after.candidate_weight], [90, 10]);
  const faulted = applyGatewayControl(installed.after, 1, { kind: "set-candidate-fault", active: true }, "2026-09-02T00:00:02Z");
  assert.equal(faulted.status, "applied");
  if (faulted.status !== "applied") return;
  const rolledBack = applyGatewayControl(faulted.after, 2, { kind: "rollback" }, "2026-09-02T00:00:03Z");
  assert.equal(rolledBack.status, "applied");
  if (rolledBack.status !== "applied") return;
  assert.deepEqual({ target: rolledBack.after.candidate_target, weight: rolledBack.after.candidate_weight, stable: rolledBack.after.stable_weight, fault: rolledBack.after.candidate_fault_active, generation: rolledBack.after.generation }, { target: null, weight: 0, stable: 100, fault: false, generation: 3 });
});

test("stale generation and illegal transitions are non-mutating conflicts", () => {
  const initial = initialGatewayState("http://stable:3000", "2026-09-02T00:00:00Z");
  for (const result of [
    applyGatewayControl(initial, 1, { kind: "install-candidate", target: "http://candidate:3000" }, "2026-09-02T00:00:01Z"),
    applyGatewayControl(initial, 0, { kind: "set-candidate-fault", active: true }, "2026-09-02T00:00:01Z"),
    applyGatewayControl(initial, 0, { kind: "rollback" }, "2026-09-02T00:00:01Z"),
  ]) {
    assert.equal(result.status, "conflict");
    if (result.status === "conflict") assert.strictEqual(result.state, initial);
  }
});
