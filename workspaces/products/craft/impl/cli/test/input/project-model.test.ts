import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { decodeBody, loadProjectNode, ProjectModelError, RELATIONSHIP_SIGNATURES } from "../../src/input/project-model.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");

function createRoot(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-project-model-"));
  fs.cpSync(fixtureRoot, root, { recursive: true });
  return root;
}

function removeRoot(root: string): void {
  assert.equal(root.startsWith(path.join(os.tmpdir(), "mtcli-project-model-")), true);
  fs.rmSync(root, { recursive: true, force: true });
}

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error) => error instanceof ProjectModelError && error.code === code);
}

function mutateJson(root: string, relativePath: string, mutate: (value: Record<string, unknown>) => void): void {
  const target = path.join(root, relativePath);
  const value = JSON.parse(fs.readFileSync(target, "utf8")) as Record<string, unknown>;
  mutate(value);
  fs.writeFileSync(target, `${JSON.stringify(value, null, 2)}\n`);
}

test("Entity input decodes from a read-only project with its exact relationship", () => {
  const root = createRoot();
  try {
    const before = fs.readFileSync(path.join(root, "specs/alpha/nodes/customer.json"), "utf8");
    const node = loadProjectNode(root, "alpha:customer");
    assert.equal(node.meta_type_id, "DS-D1.1");
    assert.equal(node.kind, "Entity");
    assert.equal(node.body.identity_field, "customer-id");
    assert.deepEqual((node.body.fields as readonly { field_id: string }[]).map(({ field_id }) => field_id), ["customer-id", "settlement-details", "preferred-method"]);
    assert.deepEqual(node.relationships.map(({ relationship }) => relationship), ["performs", "creates", "reads"]);
    assert.equal(fs.readFileSync(path.join(root, "specs/alpha/nodes/customer.json"), "utf8"), before);
  } finally {
    removeRoot(root);
  }
});

test("L1 typed roles remain structurally distinct and fail closed", () => {
  const primitive = (name: string) => ({ kind: "primitive", name });
  const field = (field_id: string, name = "string", required = true) => ({ field_id, type_ref: primitive(name), required });
  const entity = decodeBody("Entity", { description: "Account", identity_field: "account-id", fields: [field("account-id", "uuid"), field("name")] });
  assert.equal(entity.identity_field, "account-id");
  expectCode(() => decodeBody("Entity", { ...entity, identity_field: "missing" }), "MTCLI_ENTITY_IDENTITY");
  expectCode(() => decodeBody("Value Object", { description: "Money", fields: [field("amount", "decimal", false)], invariant_refs: ["money:positive"] }), "MTCLI_VALUE_OBJECT_COMPLETE");
  expectCode(() => decodeBody("Event", { description: "Occurred", event_type: "occurred", version: "v1", occurrence_id: field("occurrence-id", "uuid"), occurred_at_policy: "required", payload: [] }), "MTCLI_EVENT_VERSION");
  expectCode(() => decodeBody("Interface", { description: "API", boundary_kind: "mapping", version: "1", compatibility: "exact", operations: [] }), "MTCLI_INPUT_BODY");
  expectCode(() => decodeBody("Interface", { description: "API", boundary_kind: "external", version: "1", compatibility: "sideways", operations: [{ operation_id: "run", operation_ref: "api:run", request: [], result: [] }] }), "MTCLI_INTERFACE_COMPATIBILITY");
  expectCode(() => decodeBody("Entity", { description: "Account", identity_field: "account-id", fields: [{ field_id: "account-id", type_ref: primitive("bytes"), required: true }] }), "MTCLI_TYPE_REF");
});

test("all 13 bodies are closed and Operation and State Machine semantics are explicit", () => {
  assert.equal(RELATIONSHIP_SIGNATURES.length, 31);
  assert.equal(new Set(RELATIONSHIP_SIGNATURES.flatMap(({ validation_obligations }) => validation_obligations)).size, 45);
  const operation = decodeBody("Operation", {
    description: "Settle an account.",
    reads: ["account"],
    writes: ["account.status"],
    effects: ["SettlementCompleted"],
    guard: "can-settle",
    failure_continuation: "return-settlement-error",
  });
  assert.deepEqual(operation.writes, ["account.status"]);
  expectCode(() => decodeBody("Operation", { ...operation, undeclared: "effect" }), "MTCLI_INPUT_BODY");
  expectCode(() => decodeBody("Enum", { description: "Priority", values: [] }), "MTCLI_INPUT_BODY");
  expectCode(() => decodeBody("State Machine", { description: "Order", states: ["new"], initial: "missing", transitions: [] }), "MTCLI_INPUT_BODY");
  const stateMachine = decodeBody("State Machine", {
    description: "Order",
    states: ["new", "done"],
    initial: "new",
    transitions: [{ transition_id: "finish", source_state: "new", target_state: "done", guard_ref: "orders:can-finish", effect_event_ref: "orders:finished" }],
  });
  assert.deepEqual(stateMachine.transitions, [{ transition_id: "finish", source_state: "new", target_state: "done", guard_ref: "orders:can-finish", effect_event_ref: "orders:finished" }]);
  expectCode(() => decodeBody("State Machine", { ...stateMachine, transitions: [{ ...(stateMachine.transitions as readonly Record<string, unknown>[])[0], source_state: "missing" }] }), "MTCLI_STATE_MACHINE_STATE");
  expectCode(() => decodeBody("State Machine", { ...stateMachine, transitions: [...stateMachine.transitions as readonly Record<string, unknown>[], { ...(stateMachine.transitions as readonly Record<string, unknown>[])[0] }] }), "MTCLI_STATE_MACHINE_DUPLICATE_TRANSITION");
  expectCode(() => decodeBody("State Machine", { ...stateMachine, states: ["new", "not canonical"] }), "MTCLI_STATE_MACHINE_STATE");
});

test("canonical State Machine resolves Rule guards and Event transition relationships", () => {
  const machine = loadProjectNode(fixtureRoot, "beta:settlement-status");
  assert.equal(machine.kind, "State Machine");
  assert.deepEqual(machine.relationships.map(({ relationship }) => relationship), ["transitions"]);
  assert.deepEqual((machine.body.transitions as readonly { transition_id: string }[]).map(({ transition_id }) => transition_id), ["complete-settlement", "fail-settlement"]);
});

test("L1 project references, occurrence identity, and Interface exposes closure fail causally", () => {
  const wrongType = createRoot();
  const wrongInvariant = createRoot();
  const wrongEvent = createRoot();
  const wrongOperation = createRoot();
  const missingExposes = createRoot();
  try {
    mutateJson(wrongType, "specs/alpha/nodes/customer.json", (node) => {
      const fields = (node.body as { fields: Array<{ type_ref: { selector?: string } }> }).fields;
      fields[1]!.type_ref.selector = "beta:can-complete-settlement";
    });
    expectCode(() => loadProjectNode(wrongType, "alpha:customer"), "MTCLI_TYPE_REFERENCE");

    mutateJson(wrongInvariant, "specs/beta/nodes/settlement-details.json", (node) => {
      (node.body as { invariant_refs: string[] }).invariant_refs = ["beta:settled"];
    });
    expectCode(() => loadProjectNode(wrongInvariant, "beta:settlement-details"), "MTCLI_VALUE_OBJECT_INVARIANT_REFERENCE");

    mutateJson(wrongEvent, "specs/beta/nodes/settlement-completed.json", (node) => {
      (node.body as { event_type: string }).event_type = "settlement-requested";
    });
    expectCode(() => loadProjectNode(wrongEvent, "beta:settlement-completed"), "MTCLI_EVENT_TYPE");

    mutateJson(wrongOperation, "specs/alpha/nodes/settlement-api.json", (node) => {
      (node.body as { operations: Array<{ operation_ref: string }> }).operations[0]!.operation_ref = "alpha:customer";
    });
    expectCode(() => loadProjectNode(wrongOperation, "alpha:settlement-api"), "MTCLI_INTERFACE_OPERATION_REFERENCE");

    mutateJson(missingExposes, "specs/alpha/feature.json", (feature) => {
      feature.edges = (feature.edges as string[]).filter((edge) => edge !== "settlement-api-exposes-settle");
    });
    fs.rmSync(path.join(missingExposes, "specs/alpha/edges/settlement-api-exposes-settle.json"));
    expectCode(() => loadProjectNode(missingExposes, "alpha:settlement-api"), "MTCLI_INTERFACE_EXPOSES_MISSING");
  } finally {
    removeRoot(wrongType);
    removeRoot(wrongInvariant);
    removeRoot(wrongEvent);
    removeRoot(wrongOperation);
    removeRoot(missingExposes);
  }
});

test("Workflow compensation dependencies are closed, Operation-shaped, and acyclic", () => {
  const workflow = decodeBody("Workflow", {
    description: "Settle an account.",
    steps: ["reserve", "charge"],
    compensations: ["release-reservation", "refund-payment"],
    compensation_dependencies: ["release-reservation:depends-on:refund-payment"],
  });
  assert.deepEqual(workflow.compensation_dependencies, ["release-reservation:depends-on:refund-payment"]);
  expectCode(() => decodeBody("Workflow", {
    ...workflow,
    compensation_dependencies: ["release-reservation->refund-payment"],
  }), "MTCLI_WORKFLOW_COMPENSATION_DEPENDENCY");
  expectCode(() => decodeBody("Workflow", {
    ...workflow,
    compensation_dependencies: [
      "release-reservation:depends-on:refund-payment",
      "refund-payment:depends-on:release-reservation",
    ],
  }), "MTCLI_WORKFLOW_COMPENSATION_DEPENDENCY_CYCLE");
});

test("unknown selected types and relationship endpoint mismatches fail closed", () => {
  const unknown = createRoot();
  const mismatch = createRoot();
  try {
    const nodePath = path.join(unknown, "specs/alpha/nodes/customer.json");
    const node = JSON.parse(fs.readFileSync(nodePath, "utf8"));
    node.kind = "Saga";
    fs.writeFileSync(nodePath, `${JSON.stringify(node, null, 2)}\n`);
    expectCode(() => loadProjectNode(unknown, "alpha:customer"), "MTCLI_RELATIONSHIP_ENDPOINT");

    const edgePath = path.join(mismatch, "specs/beta/edges/audit-owns-settled.json");
    const edge = JSON.parse(fs.readFileSync(edgePath, "utf8"));
    edge.relationship = "produces";
    fs.writeFileSync(edgePath, `${JSON.stringify(edge, null, 2)}\n`);
    expectCode(() => loadProjectNode(mismatch, "beta:audit"), "MTCLI_RELATIONSHIP_ENDPOINT");
  } finally {
    removeRoot(unknown);
    removeRoot(mismatch);
  }
});
