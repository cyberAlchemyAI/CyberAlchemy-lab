import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { CompilationRejected, compileCarrier, executeAction, parseDomainSource } from "../src/index.js";

const root = path.resolve(import.meta.dirname, "..");
const original = compileCarrier(parseDomainSource(readFileSync(path.join(root, "examples/customer-approval.md"), "utf8")).carrier).plan.model;
const request = { action_id: "ReleaseCredit", actor_ref: "CreditOperator", facts: { customerId: "c-1", riskScore: 600, status: "approved", amount: 100 }, authority_grants: ["credit-release-authority"] };

test("a permission for another declared action cannot authorize this action or call its adapter", async () => {
  const model = structuredClone(original);
  const action = model.actions.find(item => item.id === request.action_id)!;
  model.actions.push({ ...action, id: "InspectCredit" });
  const permission = model.permissions.find(item => action.permission_refs.includes(item.id))!;
  permission.action_refs = ["InspectCredit"];
  let calls = 0;
  const effects: string[] = [];
  await assert.rejects(() => executeAction(model, request, { ReleaseCredit: { async execute() { calls++; effects.push("released"); return { outcome: "released" }; } } }),
    (error: unknown) => error instanceof CompilationRejected && error.issues[0]?.code === "PERMISSION_ACTION_DENIED");
  assert.equal(calls, 0);
  assert.deepEqual(effects, []);
});

test("exact action permission executes once; actor, grant and false guards still prevent effects", async () => {
  for (const [patch, expected] of [
    [{ actor_ref: "UnrelatedActor" }, "ACTOR_DENIED"],
    [{ authority_grants: [] }, "AUTHORITY_DENIED"],
    [{ facts: { ...request.facts, status: "pending" } }, "RULE_DENIED"],
  ] as const) {
    let calls = 0;
    await assert.rejects(() => executeAction(original, { ...request, ...patch }, { ReleaseCredit: { async execute() { calls++; return { outcome: "released" }; } } }),
      (error: unknown) => error instanceof CompilationRejected && error.issues[0]?.code === expected);
    assert.equal(calls, 0);
  }
  let calls = 0;
  const result = await executeAction(original, request, { ReleaseCredit: { async execute() { calls++; return { outcome: "released", emitted_events: ["credit-released"] }; } } });
  assert.equal(calls, 1);
  assert.equal(result.status, "executed");
  assert.deepEqual(result.emitted_events, ["credit-released"]);
});

test("permission actor, exact boundary and condition remain separate pre-adapter checks", async () => {
  for (const [edit, expected] of [
    [(permission: typeof original.permissions[number]) => { permission.actor_refs = ["OtherActor"]; }, "ACTOR_DENIED"],
    [(permission: typeof original.permissions[number]) => { permission.authority_boundary_ref = "other-authority"; }, "AUTHORITY_BOUNDARY_MISMATCH"],
    [(permission: typeof original.permissions[number]) => { permission.condition = { operator: "eq", operands: [{ node: "literal", value_type: "integer", value: 0 }, { node: "literal", value_type: "integer", value: 1 }] }; }, "PERMISSION_DENIED"],
  ] as const) {
    const model = structuredClone(original);
    const action = model.actions.find(item => item.id === request.action_id)!;
    edit(model.permissions.find(item => action.permission_refs.includes(item.id))!);
    let calls = 0;
    await assert.rejects(() => executeAction(model, request, { ReleaseCredit: { async execute() { calls++; return { outcome: "released" }; } } }),
      (error: unknown) => error instanceof CompilationRejected && error.issues[0]?.code === expected);
    assert.equal(calls, 0);
  }
});
