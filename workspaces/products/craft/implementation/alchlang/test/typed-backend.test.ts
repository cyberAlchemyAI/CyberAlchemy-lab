import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CompilationRejected, compileCarrier, evaluateCalculation, evaluateMapping, evaluatePolicy, evaluateQuery, parseDomainSource } from "../src/index.js";
import type { NormalizedCalculation } from "../src/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(path.join(root, "examples/typed-backend.md"), "utf8");
const parsed = parseDomainSource(source);
const compiled = compileCarrier(parsed.carrier);

test("typed Query, Calculation, Mapping, and Policy parse and lower distinctly", () => {
  assert.equal(compiled.plan.model.logic_profile, "sfol-v1");
  assert.equal(compiled.plan.sfol_logic_model.formulas.length, compiled.plan.model.rules.length);
  assert.equal(compiled.plan.sfol_logic_model.terms.length, compiled.plan.calculation_contracts.length);
  assert.equal(compiled.plan.query_contracts[0].id, "OpenOrders");
  assert.equal(compiled.plan.calculation_contracts.length, 2);
  assert.equal(compiled.plan.mapping_contracts[0].id, "SummarizeOrder");
  assert.equal(compiled.plan.policy_contracts[0].id, "FeePolicy");
  for (const prefix of ["query_contract:", "calculation_contract:", "mapping_contract:", "policy_contract:"]) assert(compiled.plan.trace_ledger.some((entry) => entry.output_ref.startsWith(prefix)));
  assert("domain.typed-backend.ts" in compiled.files);
});

test("typed backend evaluates without mutation or implicit provider access", () => {
  const query = compiled.plan.query_contracts[0];
  const rows = [
    { order_id: "a", amount: 20, status: "open" },
    { order_id: "b", amount: 140, status: "open" },
    { order_id: "c", amount: 300, status: "closed" },
    { order_id: "d", amount: 80, status: "open" }
  ];
  assert.deepEqual(evaluateQuery(query, rows), [{ order_id: "b", amount: 140 }, { order_id: "d", amount: 80 }]);
  assert.deepEqual(rows[0], { order_id: "a", amount: 20, status: "open" });
  assert.equal(evaluateCalculation(compiled.plan.calculation_contracts[0], { amount: 140 }), 145n);
  assert.deepEqual(evaluateMapping(compiled.plan.mapping_contracts[0], { order_id: "b", amount: 140 }), { summary_id: "b", total: 140, risk_band: "standard" });
  assert.equal(evaluatePolicy(compiled.plan.policy_contracts[0], { amount: 140 }), "ApplyFee");
  assert.equal(evaluatePolicy(compiled.plan.policy_contracts[0], { amount: 40 }), "KeepAmount");
});

test("generated TypeScript module executes the same four contracts", async () => {
  const bytes = Buffer.from(compiled.files["domain.typed-backend.ts"]).toString("base64");
  const generated: any = await import(`data:text/javascript;base64,${bytes}`);
  assert.equal(generated.authorityEffect, "none");
  assert.equal(generated.evaluateCalculation("ApplyFee", { amount: 7 }), 12n);
  assert.deepEqual(generated.evaluateMapping("SummarizeOrder", { order_id: "x", amount: 9 }), { summary_id: "x", total: 9, risk_band: "standard" });
  assert.equal(generated.evaluatePolicy("FeePolicy", { amount: 101 }), "ApplyFee");
  assert.deepEqual(generated.evaluateQuery("OpenOrders", [{ order_id: "x", amount: 9, status: "open" }]), [{ order_id: "x", amount: 9 }]);
});

function rejectsCarrier(code: string, mutate: (carrier: any) => void): void {
  const carrier: any = structuredClone(parsed.carrier); mutate(carrier);
  assert.throws(() => compileCarrier(carrier), (error: unknown) => error instanceof CompilationRejected && error.issues.some((issue) => issue.code === code));
}

test("typed contracts fail closed during compilation", () => {
  rejectsCarrier("QUERY_LIMIT", (carrier) => { carrier.queries[0].limit = 0; });
  rejectsCarrier("UNKNOWN_CALCULATION_OPERATOR", (carrier) => { carrier.calculations[0].expression.operator = "power"; });
  rejectsCarrier("TYPE_MISMATCH", (carrier) => { carrier.mappings[0].clauses[0].source_field = "amount"; });
  rejectsCarrier("UNRESOLVED_REFERENCE", (carrier) => { carrier.policies[0].default_target_ref = "AmbientAction"; });
});

test("UInt64 runtime failures are causal and policy selection never executes targets", () => {
  const calculation = compiled.plan.calculation_contracts[0];
  assert.throws(() => evaluateCalculation(calculation, { amount: (1n << 64n) - 1n }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "CALCULATION_OVERFLOW");
  const divide: NormalizedCalculation = { ...calculation, expression: { operator: "divide", operands: [{ node: "input_ref", ref: "amount" }, { node: "uint64_literal", value: "2" }] } };
  assert.throws(() => evaluateCalculation(divide, { amount: 3 }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "CALCULATION_INEXACT");
  const zero: NormalizedCalculation = { ...divide, expression: { operator: "divide", operands: [{ node: "input_ref", ref: "amount" }, { node: "uint64_literal", value: "0" }] } };
  assert.throws(() => evaluateCalculation(zero, { amount: 3 }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "CALCULATION_DIVIDE_BY_ZERO");
  const subtract: NormalizedCalculation = { ...divide, expression: { operator: "subtract", operands: [{ node: "input_ref", ref: "amount" }, { node: "uint64_literal", value: "5" }] } };
  assert.throws(() => evaluateCalculation(subtract, { amount: 2 }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "CALCULATION_UNDERFLOW");
  assert.throws(() => evaluateQuery(compiled.plan.query_contracts[0], [{ order_id: "x", amount: 1 }]), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "MISSING_TYPED_VALUE");
  assert.throws(() => evaluatePolicy(compiled.plan.policy_contracts[0], {}), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "MISSING_TYPED_VALUE");
  let executed = false;
  const target = evaluatePolicy(compiled.plan.policy_contracts[0], new Proxy({ amount: 200 }, { get(target, key) { if (key === "execute") executed = true; return Reflect.get(target, key); } }));
  assert.equal(target, "ApplyFee"); assert.equal(executed, false);
});
