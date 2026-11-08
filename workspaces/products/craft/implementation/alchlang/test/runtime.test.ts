import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CompilationRejected, MemoryActionAdapter, compileCarrier, evaluateRule, executeAction, parseDomainSource } from "../src/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const model = compileCarrier(parseDomainSource(readFileSync(path.join(root, "examples/customer-approval.md"), "utf8")).carrier).plan.model;
const facts = { customerId: "c-1", riskScore: 600, status: "approved", amount: 100 };

test("typed rules execute against runtime facts", () => {
  assert.equal(evaluateRule(model.rules.find((rule) => rule.id === "high-risk")!, { ...facts, riskScore: 472 }), true);
  assert.equal(evaluateRule(model.rules.find((rule) => rule.id === "high-risk")!, facts), false);
});

test("authorized action executes through an injected adapter", async () => {
  const adapter = new MemoryActionAdapter({ outcome: "released", emitted_events: ["credit-released"] });
  const result = await executeAction(model, { action_id: "ReleaseCredit", actor_ref: "CreditOperator", facts, authority_grants: ["credit-release-authority"] }, { ReleaseCredit: adapter });
  assert.equal(result.status, "executed"); assert.equal(result.outcome, "released"); assert.equal(adapter.records.length, 1);
});

test("rules, authority and adapters fail closed", async () => {
  const adapter = new MemoryActionAdapter();
  await assert.rejects(() => executeAction(model, { action_id: "ReleaseCredit", actor_ref: "CreditOperator", facts: { ...facts, status: "pending" }, authority_grants: ["credit-release-authority"] }, { ReleaseCredit: adapter }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "RULE_DENIED");
  await assert.rejects(() => executeAction(model, { action_id: "ReleaseCredit", actor_ref: "CreditOperator", facts, authority_grants: [] }, { ReleaseCredit: adapter }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "AUTHORITY_DENIED");
  await assert.rejects(() => executeAction(model, { action_id: "ReleaseCredit", actor_ref: "CreditOperator", facts, authority_grants: ["credit-release-authority"] }, {}), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "ADAPTER_NOT_BOUND");
});

test("legacy predicates execute only through an explicit registry", () => {
  const legacyRule = { id: "legacy", condition: { legacy_predicate: "risk-ok" }, owner: "owner", source_refs: [] };
  assert.throws(() => evaluateRule(legacyRule, facts), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "LEGACY_PREDICATE_UNBOUND");
  assert.equal(evaluateRule(legacyRule, facts, { "risk-ok": { operator: "gt", operands: [{ node: "fact_ref", ref: "riskScore" }, { node: "literal", value_type: "integer", value: 500 }] } }), true);
});
