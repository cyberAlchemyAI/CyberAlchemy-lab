import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  decodeRuleExpression,
  decodeTypedOperationContract,
  decodeTypedRecordContract,
  decodeTypedRuleContract,
  decodeTypedSumContract,
  decodeTypedType,
  TypedContractError,
} from "../../src/typed-operation/contracts.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const authOperationSource = path.resolve(testDir, "../../../../../auth-foundation/implementation/operation-source");
const capacityOperationSource = path.resolve(testDir, "../fixtures/capacity-decision");

const scalar = (name: "String" | "Bool" | "UInt64") => ({ kind: "scalar", name });
const named = (selector: string) => ({ kind: "named", selector });
const valuePath = (root: string, ...properties: string[]) => ({ op: "path", root, properties });

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error) => error instanceof TypedContractError && error.code === code);
}

test("typed Auth-shaped record preserves property identity, type, cardinality, and meaning", () => {
  const record = decodeTypedRecordContract({
    schema_version: "domainspec.typed-record/v1",
    ontology_node: "AUTH-AUTHORIZATION-REQUEST",
    properties: [
      {
        ontology_property: "AUTH-AUTHORIZATION-REQUEST#request_id",
        name: "request_id",
        type: scalar("String"),
        cardinality: "one",
        identity: true,
        meaning: "Request identity.",
      },
      {
        ontology_property: "AUTH-AUTHORIZATION-REQUEST#required_permission",
        name: "required_permission",
        type: named("auth-exact-permission:permission"),
        cardinality: "one",
        identity: false,
        meaning: "Required exact permission.",
      },
    ],
  });
  assert.equal(record.properties[0]?.ontology_property, "AUTH-AUTHORIZATION-REQUEST#request_id");
  assert.deepEqual(record.properties[1]?.type, named("auth-exact-permission:permission"));
});

test("type algebra admits the bounded Auth constructors and rejects unsupported or incoherent forms", () => {
  const decision = decodeTypedType({
    kind: "sum",
    variants: [
      { ontology_variant: "AUTH-AUTHORIZATION-DECISION#Allow", name: "Allow", payload: null },
      { ontology_variant: "AUTH-AUTHORIZATION-DECISION#Deny", name: "Deny", payload: named("auth-exact-permission:deny-reason") },
    ],
  });
  assert.equal(decision.kind, "sum");
  const sum = decodeTypedSumContract({
    schema_version: "domainspec.typed-sum/v1",
    ontology_node: "AUTH-AUTHORIZATION-DECISION",
    variants: decision.kind === "sum" ? decision.variants : [],
  });
  assert.equal(sum.variants[1]?.payload?.kind, "named");
  assert.deepEqual(decodeTypedType({ kind: "list", element: named("auth-exact-permission:session") }), { kind: "list", element: named("auth-exact-permission:session") });
  expectCode(() => decodeTypedType({ kind: "scalar", name: "Float64" }), "MTCLI_TYPED_TYPE");
  expectCode(() => decodeTypedType({ kind: "optional", element: { kind: "optional", element: scalar("String") } }), "MTCLI_TYPED_TYPE");
  expectCode(() => decodeTypedRecordContract({
    schema_version: "domainspec.typed-record/v1",
    ontology_node: "AUTH-ROLE",
    properties: [{ ontology_property: "AUTH-ROLE#permissions", name: "permissions", type: { kind: "set", element: named("auth-exact-permission:permission") }, cardinality: "one", identity: false, meaning: "Grants." }],
  }), "MTCLI_TYPED_CARDINALITY");
  expectCode(() => decodeTypedRecordContract({
    schema_version: "domainspec.typed-record/v1",
    ontology_node: "AUTH-EVALUATION-CONTEXT",
    properties: [{ ontology_property: "AUTH-EVALUATION-CONTEXT#resolved_sessions", name: "resolved_sessions", type: { kind: "list", element: named("auth-exact-permission:session") }, cardinality: "many-unique", identity: false, meaning: "Resolution rows." }],
  }), "MTCLI_TYPED_CARDINALITY");
});

test("structured Rule expressions admit the bounded operator set without executable language text", () => {
  const rule = decodeTypedRuleContract({
    schema_version: "domainspec.typed-rule/v1",
    ontology_rule: "AF-RULE-SESSION-CURRENT",
    parameters: [{ name: "context", type: named("auth-exact-permission:evaluation-context") }],
    expression: {
      op: "all",
      terms: [
        { op: "eq", left: valuePath("context", "AUTH-SESSION#status"), right: { op: "literal", type: "String", value: "Active" } },
        { op: "lt", left: valuePath("context", "AUTH-AUTHORIZATION-REQUEST#decision_time"), right: valuePath("context", "AUTH-SESSION#expires_at") },
      ],
    },
  });
  assert.equal(rule.expression.op, "all");
  expectCode(() => decodeRuleExpression({ op: "eval_rust", source: "true" }), "MTCLI_TYPED_RULE");
  expectCode(() => decodeRuleExpression({ op: "all", terms: [] }), "MTCLI_TYPED_RULE");
  expectCode(() => decodeRuleExpression({ op: "eq", left: { op: "literal", type: "UInt64", value: -1 }, right: { op: "literal", type: "UInt64", value: 0 } }), "MTCLI_TYPED_RULE");
  assert.deepEqual(
    decodeRuleExpression({
      op: "set_equal",
      left: valuePath("context", "AUTH-SESSION#active_role_ids"),
      right: { op: "to_set", value: valuePath("context", "AUTH-EVALUATION-CONTEXT#resolved_roles", "AUTH-ROLE#role_id") },
    }),
    {
      op: "set_equal",
      left: valuePath("context", "AUTH-SESSION#active_role_ids"),
      right: { op: "to_set", value: valuePath("context", "AUTH-EVALUATION-CONTEXT#resolved_roles", "AUTH-ROLE#role_id") },
    },
  );
  expectCode(() => decodeRuleExpression({
    op: "eq",
    left: { op: "to_set" },
    right: { op: "literal", type: "Bool", value: true },
  }), "MTCLI_TYPED_SCHEMA");
  assert.deepEqual(decodeRuleExpression({
    op: "rule_ref",
    selector: "auth-exact-permission:trusted-scope",
    arguments: [{ parameter: "context", value: { op: "path", root: "context", properties: [] } }],
  }), {
    op: "rule_ref",
    selector: "auth-exact-permission:trusted-scope",
    arguments: [{ parameter: "context", value: { op: "path", root: "context", properties: [] } }],
  });
  expectCode(() => decodeRuleExpression({ op: "rule_ref", selector: "auth-exact-permission:trusted-scope" }), "MTCLI_TYPED_SCHEMA");
});

test("typed Operation binds inputs, output, guard, and dependency selectors", () => {
  const operation = decodeTypedOperationContract({
    schema_version: "domainspec.typed-operation/v1",
    ontology_operation: "AUTH-OP-AUTHORIZE",
    inputs: [{ name: "context", type: named("auth-exact-permission:evaluation-context") }],
    output: named("auth-exact-permission:authorization-decision"),
    guard: "auth-exact-permission:authorization-invariant",
    reads: ["auth-exact-permission:session", "auth-exact-permission:role"],
    writes: [],
    effects: [],
    failure_continuation: "return-deny-without-state-change",
    success_result: { variant: "Allow", payload_variant: null },
    failure_result: { variant: "Deny", payload_variant: "NoExactActiveRoleGrant" },
  });
  assert.equal(operation.guard, "auth-exact-permission:authorization-invariant");
  assert.equal(operation.writes.length, 0);
  expectCode(() => decodeTypedOperationContract({ ...operation, reads: ["session"] }), "MTCLI_TYPED_NODE_SELECTOR");
  expectCode(() => decodeTypedOperationContract({ ...operation, inputs: [...operation.inputs, operation.inputs[0]] }), "MTCLI_TYPED_DUPLICATE");
});

test("typed result constructors admit strict value-expression payloads", () => {
  const operation = decodeTypedOperationContract({
    schema_version: "domainspec.typed-operation/v1",
    ontology_operation: "CAPACITY-QUERY-RESOLVE",
    inputs: [
      { name: "query", type: named("capacity-decision:capacity-query") },
      { name: "snapshot", type: named("capacity-decision:capacity-snapshot") },
    ],
    output: named("capacity-decision:capacity-resolution"),
    guard: "capacity-decision:query-valid",
    reads: ["capacity-decision:capacity-record"],
    writes: [],
    effects: [],
    failure_continuation: "return-deny",
    success_result: { variant: "Resolved", payload: { op: "path", root: "snapshot", properties: [] } },
    failure_result: { variant: "Deny", payload: null },
  });
  assert.deepEqual(operation.success_result, {
    variant: "Resolved",
    payload: { op: "path", root: "snapshot", properties: [] },
  });
  assert.deepEqual(operation.failure_result, { variant: "Deny", payload: null });
  expectCode(() => decodeTypedOperationContract({
    ...operation,
    success_result: { variant: "Resolved", payload: null, payload_variant: null },
  }), "MTCLI_TYPED_SCHEMA");
  expectCode(() => decodeTypedOperationContract({
    ...operation,
    success_result: { variant: "Resolved" },
  }), "MTCLI_TYPED_SCHEMA");
});

function copiedAuthSource(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-typed-auth-"));
  fs.cpSync(authOperationSource, root, { recursive: true });
  return root;
}

function mutateNode(root: string, nodeId: string, mutate: (value: Record<string, any>) => void): void {
  const nodePath = path.join(root, "specs/auth-exact-permission/nodes", `${nodeId}.json`);
  const value = JSON.parse(fs.readFileSync(nodePath, "utf8"));
  mutate(value);
  fs.writeFileSync(nodePath, `${JSON.stringify(value, null, 2)}\n`);
}

test("selected Auth Operation compiles one deterministic property-and-rule closure", () => {
  const left = loadProjectNode(authOperationSource, "auth-exact-permission:authorize").typed_closure!;
  const right = loadProjectNode(authOperationSource, "auth-exact-permission:authorize").typed_closure!;
  assert.equal(left.nodes.length, 17);
  assert.equal(left.properties.length, 22);
  assert.equal(left.variants.length, 15);
  assert.equal(left.rules.length, 8);
  assert.equal(left.relationships.length, 10);
  assert.equal(left.closure_sha256, right.closure_sha256);
  assert.deepEqual(left, right);
  assert.equal(left.nodes.at(-1)?.selector, "auth-exact-permission:authorize");
});

test("a non-Auth Operation compiles through the same deterministic typed closure", () => {
  const left = loadProjectNode(capacityOperationSource, "capacity-decision:decide-capacity").typed_closure!;
  const right = loadProjectNode(capacityOperationSource, "capacity-decision:decide-capacity").typed_closure!;
  assert.equal(left.nodes.length, 4);
  assert.equal(left.properties.length, 3);
  assert.equal(left.variants.length, 2);
  assert.equal(left.rules.length, 1);
  assert.equal(left.relationships.length, 2);
  assert.equal(left.root_selector, "capacity-decision:decide-capacity");
  assert.equal(left.closure_sha256, right.closure_sha256);
  assert.deepEqual(left, right);
  assert.equal(left.nodes.some((node) => node.selector.startsWith("auth-")), false);
  assert.equal(left.properties.some((row) => row.ontology_property.startsWith("AUTH-")), false);
  assert.equal(left.variants.some((row) => row.ontology_variant.startsWith("AUTH-")), false);
  assert.equal(left.rules.some((row) => row.ontology_rule.startsWith("AF-RULE-")), false);
});

test("typed closure fails on missing dependencies, read-edge drift, and cycles", () => {
  const missing = copiedAuthSource();
  const reads = copiedAuthSource();
  const cycle = copiedAuthSource();
  try {
    mutateNode(missing, "authorization-request", (node) => {
      node.body.typed_contract.properties[2].type.selector = "auth-exact-permission:missing-permission";
    });
    expectCode(() => loadProjectNode(missing, "auth-exact-permission:authorize"), "MTCLI_TYPED_CLOSURE_MISSING");

    mutateNode(reads, "authorize", (node) => {
      node.body.typed_contract.reads = ["auth-exact-permission:session"];
    });
    expectCode(() => loadProjectNode(reads, "auth-exact-permission:authorize"), "MTCLI_TYPED_CLOSURE_READS");

    mutateNode(cycle, "unique-resolved-session", (node) => {
      node.body.typed_contract.expression = { op: "rule_ref", selector: "auth-exact-permission:default-deny", arguments: [{ parameter: "context", value: { op: "path", root: "context", properties: [] } }] };
    });
    mutateNode(cycle, "default-deny", (node) => {
      node.body.typed_contract.expression = { op: "rule_ref", selector: "auth-exact-permission:unique-resolved-session", arguments: [{ parameter: "context", value: { op: "path", root: "context", properties: [] } }] };
    });
    expectCode(() => loadProjectNode(cycle, "auth-exact-permission:authorize"), "MTCLI_TYPED_CLOSURE_CYCLE");
  } finally {
    fs.rmSync(missing, { recursive: true, force: true });
    fs.rmSync(reads, { recursive: true, force: true });
    fs.rmSync(cycle, { recursive: true, force: true });
  }
});
