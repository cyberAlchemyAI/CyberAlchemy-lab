import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { loadProjectNode } from "../../src/input/project-model.ts";
import { renderTypedRustOperation, TypedRustError } from "../../src/typed-operation/rust.ts";
import type { TypedOperationClosureV1 } from "../../src/typed-operation/closure.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const authOperationSource = path.resolve(testDir, "../../../../../auth-foundation/implementation/operation-source");
const authTrustedInputSource = path.resolve(testDir, "../../../../../auth-foundation/implementation/trusted-input-source");
const capacityOperationSource = path.resolve(testDir, "../fixtures/capacity-decision");

function authClosure(): TypedOperationClosureV1 {
  return loadProjectNode(authOperationSource, "auth-exact-permission:authorize").typed_closure!;
}

function capacityClosure(): TypedOperationClosureV1 {
  return loadProjectNode(capacityOperationSource, "capacity-decision:decide-capacity").typed_closure!;
}

function authTrustedInputClosure(): TypedOperationClosureV1 {
  return loadProjectNode(authTrustedInputSource, "trusted-input-resolution:resolve-trusted-inputs").typed_closure!;
}

function mutableClosure(): any {
  return structuredClone(authClosure());
}

function guardContract(closure: any): any {
  return closure.nodes.find((node: any) => node.selector === closure.operation.guard).typed_contract;
}

function findExpression(expression: any, op: string): any | null {
  if (expression.op === op) return expression;
  if (expression.op === "all" || expression.op === "any") {
    for (const term of expression.terms) {
      const found = findExpression(term, op);
      if (found !== null) return found;
    }
  } else if (expression.op === "not") return findExpression(expression.term, op);
  else if (expression.op === "exactly_one" || expression.op === "unique" || expression.op === "exists") return findExpression(expression.where, op);
  return null;
}

function expectRustCode(action: () => unknown, code: string): void {
  assert.throws(action, (error) => error instanceof TypedRustError && error.code === code && error.exitCode === 22);
}

test("typed Rust guard lowering is deterministic, scoped, borrow-aware, and explicit about realized Rules", () => {
  const closure = authClosure();
  const first = renderTypedRustOperation(closure);
  const second = renderTypedRustOperation(closure);
  assert.equal(first, second);
  assert.match(first, /let __domainspec_rule_000 =/);
  assert.match(first, /__domainspec_rule_000 && \{/);
  assert.match(first, /\.filter\(\|session\| \{/);
  assert.match(first, /\.any\(\|role\| \{/);
  assert.match(first, /\.collect::<Vec<_>>\(\)\s+\.into_iter\(\)\s+\.collect::<BTreeSet<_>>\(\)/);
  assert.equal((first.match(/\.clone\(\)/g) ?? []).length, 1);
  assert.equal(first.includes(".to_owned()"), false);
  assert.equal(first.includes("DOMAINSPEC_RULE_BINDINGS"), false);
  assert.match(first, /pub const DOMAINSPEC_RULE_SELECTORS/);
  assert.match(first, /pub const DOMAINSPEC_RULE_IMPLEMENTATION_BINDINGS/);
  assert.match(first, /\("AF-RULE-ALLOW-IFF", "auth-exact-permission:allow-iff", "allow_iff"\)/);
  assert.equal(closure.rules.length, 8);
  assert.equal((first.match(/pub fn (?:allow_iff|authorization_admissible|complete_active_roles|default_deny|exact_active_role_grant|session_current|trusted_scope|unique_resolved_session)\(/g) ?? []).length, 8);
});

test("typed Rust lowering is capability-neutral for a second non-Auth Operation", () => {
  const closure = capacityClosure();
  const rendered = renderTypedRustOperation(closure);
  assert.equal(rendered, renderTypedRustOperation(capacityClosure()));
  assert.match(rendered, /pub struct CapacitySnapshot/);
  assert.match(rendered, /pub enum CapacityDecision/);
  assert.match(rendered, /pub fn within_capacity\(snapshot: &CapacitySnapshot\) -> bool/);
  assert.match(rendered, /snapshot\.requested_units < snapshot\.available_units/);
  assert.match(rendered, /pub fn decide_capacity\(snapshot: &CapacitySnapshot\) -> CapacityDecision/);
  assert.match(rendered, /CapacityDecision::Accept/);
  assert.match(rendered, /CapacityDecision::Reject/);
  assert.equal(rendered.includes("use std::collections::BTreeSet;"), false);
  assert.equal(rendered.toLowerCase().includes("auth"), false);
});

test("typed Rust Query returns an owned record payload and supplies only matching guard inputs", () => {
  const closure = authTrustedInputClosure();
  const rendered = renderTypedRustOperation(closure);
  assert.equal(closure.nodes.find((node) => node.selector === closure.root_selector)?.kind, "Query");
  assert.equal(rendered, renderTypedRustOperation(authTrustedInputClosure()));
  assert.match(rendered, /pub fn resolve_trusted_inputs\(query: &TrustedInputQuery, snapshot: &TrustedInputSnapshot\) -> TrustedInputResolution/);
  assert.match(rendered, /if trusted_input_query_valid\(query\)/);
  assert.match(rendered, /TrustedInputResolution::Resolved\(\(\*snapshot\)\.clone\(\)\)/);
  assert.match(rendered, /TrustedInputResolution::Deny/);

  const wrongType = structuredClone(closure) as any;
  wrongType.operation.success_result.payload = { op: "path", root: "query", properties: [] };
  expectRustCode(() => renderTypedRustOperation(wrongType), "MTCLI_TYPED_RUST_TYPE");
});

test("list projection remains a list until an authored to_set conversion", () => {
  const closure = mutableClosure();
  const completeRoles = closure.nodes.find((node: any) => node.selector === "auth-exact-permission:complete-active-roles").typed_contract;
  const setEquality = findExpression(completeRoles.expression, "set_equal");
  assert.equal(setEquality.right.op, "to_set");
  setEquality.right = setEquality.right.value;
  expectRustCode(() => renderTypedRustOperation(closure), "MTCLI_TYPED_RUST_TYPE");
});

test("all and any lower later terms behind their short-circuit operator", () => {
  const closure = mutableClosure();
  guardContract(closure).expression = {
    op: "any",
    terms: [
      { op: "eq", left: { op: "literal", type: "Bool", value: true }, right: { op: "literal", type: "Bool", value: true } },
      { op: "eq", left: { op: "literal", type: "Bool", value: false }, right: { op: "literal", type: "Bool", value: true } },
    ],
  };
  const rendered = renderTypedRustOperation(closure);
  assert.match(rendered, /let __domainspec_rule_001 = __domainspec_rule_000 \|\| \{/);
});

test("Rule references require exact named and typed arguments", () => {
  const missing = mutableClosure();
  const missingRef = findExpression(guardContract(missing).expression, "rule_ref");
  missingRef.arguments = [];
  expectRustCode(() => renderTypedRustOperation(missing), "MTCLI_TYPED_RUST_RULE");

  const wrongType = mutableClosure();
  const wrongTypeRef = findExpression(guardContract(wrongType).expression, "rule_ref");
  wrongTypeRef.arguments[0].value = { op: "literal", type: "Bool", value: true };
  expectRustCode(() => renderTypedRustOperation(wrongType), "MTCLI_TYPED_RUST_TYPE");
});

test("Rust lowering fails closed on normalized type-name collisions", () => {
  const closure = mutableClosure();
  const permission = closure.nodes.find((node: any) => node.selector === "auth-exact-permission:permission");
  closure.nodes.splice(closure.nodes.length - 1, 0, { ...structuredClone(permission), selector: "other-feature:permission" });
  expectRustCode(() => renderTypedRustOperation(closure), "MTCLI_TYPED_RUST_COLLISION");
});

test("Rust literals use Rust escapes and reject unpaired UTF-16 surrogates", () => {
  const closure = mutableClosure();
  guardContract(closure).expression = {
    op: "eq",
    left: { op: "path", root: "context", properties: ["AUTH-EVALUATION-CONTEXT#request", "AUTH-AUTHORIZATION-REQUEST#scope_evidence_ref"] },
    right: { op: "literal", type: "String", value: "line\n\u0001\"\\é" },
  };
  assert.match(renderTypedRustOperation(closure), /line\\n\\u\{1\}\\\"\\\\é/);
  guardContract(closure).expression.right.value = "\ud800";
  expectRustCode(() => renderTypedRustOperation(closure), "MTCLI_TYPED_RUST_LITERAL");
});
