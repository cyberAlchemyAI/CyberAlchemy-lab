import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { ConformanceError, observeTarget, observeTargetReceipt } from "../../src/conformance/observe-target.ts";
import { readInstantiationReceipt, ReceiptError } from "../../src/conformance/receipt.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";
import { publishInstantiation } from "../../src/generation/publish-instantiation.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";
import { canonicalJson } from "../../src/input/source-manifest.ts";
import { loadSystemIntegrationSelection, SystemIntegrationError } from "../../src/system-integration/compiler.ts";
import { testPlan } from "../helpers/plans.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const sourceFixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");
const authOperationSource = path.resolve(testDir, "../../../../../auth-foundation/implementation/operation-source");
const capacityOperationSource = path.resolve(testDir, "../fixtures/capacity-decision");

function targetFor(language: "typescript" | "python" | "rust" = "typescript", kind: "Operation" | "Workflow" | "State Machine" = "Operation"): { parent: string; target: string; artifact: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-observe-"));
  const target = path.join(parent, "target");
  const result = publishInstantiation(testPlan(kind, language), target);
  return { parent, target, artifact: path.join(target, result.receipt.artifacts[0]!.relative_path) };
}

function clean(parent: string): void {
  assert.equal(parent.startsWith(path.join(os.tmpdir(), "mtcli-observe-")), true);
  fs.rmSync(parent, { recursive: true, force: true });
}

function integrationTarget(language: "typescript" | "python" | "rust"): { parent: string; target: string; integrationArtifact: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-observe-"));
  const target = path.join(parent, "target");
  const node = loadProjectNode(sourceFixtureRoot, "alpha:settle");
  const selection = loadSystemIntegrationSelection(sourceFixtureRoot, "settle-runtime", "provider-neutral-v1", "alpha:settle", language);
  const result = publishInstantiation(planInstantiation(node, language, selection), target);
  return { parent, target, integrationArtifact: path.join(target, result.receipt.system_integration!.generated_relative_path) };
}

function typedAuthTarget(name = "target"): { parent: string; target: string; artifact: string; receiptPath: string; planSha256: string; receiptSha256: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-observe-"));
  const target = path.join(parent, name);
  const node = loadProjectNode(authOperationSource, "auth-exact-permission:authorize");
  const plan = planInstantiation(node, "rust");
  const result = publishInstantiation(plan, target);
  return {
    parent,
    target,
    artifact: path.join(target, result.receipt.artifacts[0]!.relative_path),
    receiptPath: path.join(target, result.receipt_path),
    planSha256: plan.plan_sha256,
    receiptSha256: result.receipt.receipt_sha256,
  };
}

function l1Target(selector: string, language: "typescript" | "python" | "rust" = "typescript"): { parent: string; target: string; artifact: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-observe-"));
  const target = path.join(parent, "target");
  const result = publishInstantiation(planInstantiation(loadProjectNode(sourceFixtureRoot, selector), language), target);
  return { parent, target, artifact: path.join(target, result.receipt.artifacts[0]!.relative_path) };
}

function typedCapacityTarget(name = "target"): { parent: string; target: string; artifact: string; receiptPath: string; planSha256: string; receiptSha256: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-observe-"));
  const target = path.join(parent, name);
  const node = loadProjectNode(capacityOperationSource, "capacity-decision:decide-capacity");
  const plan = planInstantiation(node, "rust");
  const result = publishInstantiation(plan, target);
  return {
    parent,
    target,
    artifact: path.join(target, result.receipt.artifacts[0]!.relative_path),
    receiptPath: path.join(target, result.receipt_path),
    planSha256: plan.plan_sha256,
    receiptSha256: result.receipt.receipt_sha256,
  };
}

function expectCode(target: string, code: string): void {
  assert.throws(() => observeTarget(target), (error) => error instanceof ConformanceError && error.code === code);
  const receipt = observeTargetReceipt(target);
  assert.equal(receipt.result, "fail");
  if (receipt.result === "fail") {
    assert.equal(receipt.schema_version, "domainspec.target-observation/v1");
    assert.equal(receipt.code, code);
    assert.equal(receipt.target_root, target);
    assert.equal(receipt.authority_effect, "none");
  }
}

test("all three Operation realizations pass independent post-write observation", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const fixture = targetFor(language);
    try {
      const observation = observeTarget(fixture.target);
      assert.equal(observation.result, "pass");
      assert.equal(observation.observed_artifacts.length, 1);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("all three Workflow realizations bind composition-root compensation as intent only", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const fixture = targetFor(language, "Workflow");
    try {
      const observation = observeTarget(fixture.target);
      assert.equal(observation.result, "pass");
      assert.equal(observation.checks.includes("workflow-obligations-when-applicable"), true);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("all three State Machine realizations pass causal semantic observation", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const fixture = targetFor(language, "State Machine");
    try {
      const observation = observeTarget(fixture.target);
      assert.equal(observation.result, "pass");
      assert.equal(observation.checks.includes("state-machine-obligations-when-applicable"), true);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("all five L1 roles pass exact observation in TypeScript, Python, and Rust", () => {
  const selectors = ["alpha:customer", "beta:settlement-details", "beta:settlement-method", "beta:settlement-completed", "alpha:settlement-api"];
  for (const selector of selectors) for (const language of ["typescript", "python", "rust"] as const) {
    const fixture = l1Target(selector, language);
    try {
      const observation = observeTarget(fixture.target);
      assert.equal(observation.result, "pass");
      assert.equal(observation.checks.includes("l1-typed-role-obligations-when-applicable"), true);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("L1 role-confusion and compatibility marker drift fail causally", () => {
  const mutants: readonly [string, string, string, string][] = [
    ["alpha:customer", '// domainspec-entity-identity: "customer-id"', '// domainspec-entity-identity: "settlement-details"', "MTCLI_ENTITY_IDENTITY"],
    ["beta:settlement-details", "// domainspec-value-object-structural-equality: true", "// domainspec-value-object-structural-equality: false", "MTCLI_VALUE_EQUALITY"],
    ["beta:settlement-method", '// domainspec-enum-closed-values: ["card","bank-transfer"]', '// domainspec-enum-closed-values: ["card"]', "MTCLI_ENUM_CLOSED_VALUES"],
    ["beta:settlement-completed", '// domainspec-event-compatibility: {"event_type":"settlement-completed","version":"1"}', '// domainspec-event-compatibility: {"event_type":"settlement-requested","version":"1"}', "MTCLI_EVENT_COMPATIBILITY"],
    ["alpha:settlement-api", '// domainspec-interface-compatibility: {"direction":"backward","version":"2"}', '// domainspec-interface-compatibility: {"direction":"exact","version":"2"}', "MTCLI_INTERFACE_COMPATIBILITY"],
  ];
  for (const [selector, before, after, code] of mutants) {
    const fixture = l1Target(selector);
    try {
      const content = fs.readFileSync(fixture.artifact, "utf8");
      assert.equal(content.includes(before), true, `test fixture contains ${before}`);
      fs.writeFileSync(fixture.artifact, content.replace(before, after));
      expectCode(fixture.target, code);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("all three provider-neutral integration profiles pass exact post-write observation", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const fixture = integrationTarget(language);
    try {
      const observation = observeTarget(fixture.target);
      assert.equal(observation.result, "pass");
      assert.equal(observation.observed_artifacts.length, 2);
      assert.equal(observation.checks.includes("system-integration-profile-when-selected"), true);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("typed Auth Operation is deterministic, property-closed, observed, and compilable Rust", () => {
  const left = typedAuthTarget("left");
  const rightTarget = path.join(left.parent, "right");
  try {
    const node = loadProjectNode(authOperationSource, "auth-exact-permission:authorize");
    const rightPlan = planInstantiation(node, "rust");
    const right = publishInstantiation(rightPlan, rightTarget);
    const leftReceipt = readInstantiationReceipt(left.target);
    const rightReceipt = readInstantiationReceipt(rightTarget);
    const closure = leftReceipt.semantic_contract.typed_closure!;
    assert.equal(observeTarget(left.target).result, "pass");
    assert.equal(observeTarget(rightTarget).result, "pass");
    assert.equal(closure.properties.length, 22);
    assert.equal(closure.variants.length, 15);
    assert.equal(closure.rules.length, 8);
    assert.equal(left.planSha256, rightPlan.plan_sha256);
    assert.equal(left.receiptSha256, right.receipt.receipt_sha256);
    assert.equal(leftReceipt.artifacts[0]!.sha256, rightReceipt.artifacts[0]!.sha256);
    assert.equal(closure.closure_sha256, rightReceipt.semantic_contract.typed_closure!.closure_sha256);
    const generated = fs.readFileSync(left.artifact, "utf8");
    assert.equal(generated.includes("guard: bool"), false);
    const compiled = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", left.artifact, "-o", path.join(left.parent, "auth-operation.rlib")], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr);
    const cargoCheck = spawnSync("cargo", ["check"], { cwd: left.target, encoding: "utf8" });
    assert.equal(cargoCheck.status, 0, cargoCheck.stderr);
    const cargoTest = spawnSync("cargo", ["test"], { cwd: rightTarget, encoding: "utf8" });
    assert.equal(cargoTest.status, 0, cargoTest.stderr);
  } finally {
    clean(left.parent);
  }
});

test("a second non-Auth typed Operation is deterministic and exactly observed", () => {
  const left = typedCapacityTarget("left");
  const rightTarget = path.join(left.parent, "right");
  try {
    const node = loadProjectNode(capacityOperationSource, "capacity-decision:decide-capacity");
    const rightPlan = planInstantiation(node, "rust");
    const right = publishInstantiation(rightPlan, rightTarget);
    const leftReceipt = readInstantiationReceipt(left.target);
    const rightReceipt = readInstantiationReceipt(rightTarget);
    assert.equal(observeTarget(left.target).result, "pass");
    assert.equal(observeTarget(rightTarget).result, "pass");
    assert.equal(left.planSha256, rightPlan.plan_sha256);
    assert.equal(left.receiptSha256, right.receipt.receipt_sha256);
    assert.equal(leftReceipt.artifacts[0]!.sha256, rightReceipt.artifacts[0]!.sha256);
    assert.equal(leftReceipt.semantic_contract.typed_closure!.closure_sha256, rightReceipt.semantic_contract.typed_closure!.closure_sha256);
    assert.equal(fs.readFileSync(left.artifact, "utf8").toLowerCase().includes("auth"), false);
  } finally {
    clean(left.parent);
  }
});

test("typed closure marker and receipt closure tampering fail causally", () => {
  const markerFixture = typedAuthTarget();
  try {
    const content = fs.readFileSync(markerFixture.artifact, "utf8");
    fs.writeFileSync(markerFixture.artifact, content.replace("// domainspec-typed-closure-sha256: \"", "// domainspec-typed-closure-sha256: \"0"));
    expectCode(markerFixture.target, "MTCLI_TYPED_CLOSURE_DRIFT");
  } finally {
    clean(markerFixture.parent);
  }

  const receiptFixture = typedAuthTarget();
  try {
    const receipt = JSON.parse(fs.readFileSync(receiptFixture.receiptPath, "utf8"));
    receipt.semantic_contract.typed_closure.properties[0].domainspec_selector = "auth-exact-permission:permission#tampered";
    fs.writeFileSync(receiptFixture.receiptPath, `${canonicalJson(receipt)}\n`);
    assert.throws(() => readInstantiationReceipt(receiptFixture.target), (error) => error instanceof ReceiptError && error.code === "MTCLI_RECEIPT_TYPED_CLOSURE");
  } finally {
    clean(receiptFixture.parent);
  }
});

test("system-integration generated-contract drift fails causally", () => {
  const fixture = integrationTarget("typescript");
  try {
    const content = fs.readFileSync(fixture.integrationArtifact, "utf8");
    fs.writeFileSync(fixture.integrationArtifact, content.replace("provider-neutral-v1", "provider-neutral-v2"));
    assert.throws(() => observeTarget(fixture.target), (error) => error instanceof SystemIntegrationError && error.code === "SIC_GENERATED_PROFILE_DRIFT");
    const observation = observeTargetReceipt(fixture.target);
    assert.equal(observation.result, "fail");
    if (observation.result === "fail") assert.equal(observation.code, "SIC_GENERATED_PROFILE_DRIFT");
  } finally {
    clean(fixture.parent);
  }
});

test("causal mutants identify declared-set, guard, atomicity, continuation, and relationship drift", () => {
  const mutants: readonly [string, string, string][] = [
    ['// domainspec-operation-sets: {"effects":["AccountChanged"],"reads":["account"],"writes":["account.status"]}', '// domainspec-operation-sets: {"effects":[],"reads":["account"],"writes":["account.status"]}', "MTCLI_OPERATION_DECLARED_SETS"],
    ["if (!guard())", "if (guard())", "MTCLI_OPERATION_GUARD_ORDER"],
    ["const outbox", "const deferredOutbox", "MTCLI_OPERATION_ATOMICITY"],
    ["Contract.reads.map", "Contract.writes.map", "MTCLI_OPERATION_UNDECLARED_READ"],
    ["Contract.writes.reduce", "Contract.reads.reduce", "MTCLI_OPERATION_UNDECLARED_WRITE"],
    ["Contract.effects.map", 'Contract.effects.concat(["UndeclaredEffect"]).map', "MTCLI_OPERATION_UNDECLARED_EFFECT"],
    ['// domainspec-failure-continuation: "return-account-error"', '// domainspec-failure-continuation: "retry"', "MTCLI_OPERATION_CONTINUATION"],
    ['// domainspec-operation-instrumentation-owner: "outer-wrapper"', '// domainspec-operation-instrumentation-owner: "core"', "MTCLI_OPERATION_INSTRUMENTATION_BOUNDARY"],
    ['export const ChangeAccountContract = Object.freeze({"creation_targets":["accounts.account"]', 'export const ChangeAccountContract = Object.freeze({"creation_targets":[]', "MTCLI_OPERATION_CREATION_TARGETS"],
    ['// domainspec-relationships: [{"edge_id":"operation-creates-account"', '// domainspec-relationships: [{"edge_id":"changed-edge"', "MTCLI_OBSERVE_RELATIONSHIPS"],
  ];
  for (const [before, after, code] of mutants) {
    const fixture = targetFor();
    try {
      const content = fs.readFileSync(fixture.artifact, "utf8");
      assert.equal(content.includes(before), true, `test fixture contains ${before}`);
      fs.writeFileSync(fixture.artifact, content.replace(before, after));
      expectCode(fixture.target, code);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("Workflow compensation execution drift has a causal failure", () => {
  const fixture = targetFor("typescript", "Workflow");
  try {
    const content = fs.readFileSync(fixture.artifact, "utf8");
    const before = "void compensate;";
    assert.equal(content.includes(before), true);
    fs.writeFileSync(
      fixture.artifact,
      content.replace(before, `${before}\n  await compensate(recoveryIntent ?? "");`),
    );
    expectCode(fixture.target, "MTCLI_WORKFLOW_COMPENSATION_EXECUTION");
  } finally {
    clean(fixture.parent);
  }
});

test("Workflow compensation contract, state, order, executor, and Operation role drift fail causally", () => {
  const mutants: readonly [string, string, string][] = [
    ['// domainspec-compensation-contract: "forward-recovery-operation/v2"', '// domainspec-compensation-contract: "rollback/v1"', "MTCLI_WORKFLOW_COMPENSATION_CONTRACT"],
    ['// domainspec-recovery-intent-statuses: ["required","satisfied","unresolved"]', '// domainspec-recovery-intent-statuses: ["required","satisfied"]', "MTCLI_WORKFLOW_COMPENSATION_STATE"],
    ['// domainspec-compensation-order: "explicit-dependency-graph-with-reverse-completion-default"', '// domainspec-compensation-order: "forward-step-order"', "MTCLI_WORKFLOW_COMPENSATION_ORDER"],
    ['// domainspec-compensation-executor-owner: "external-runtime"', '// domainspec-compensation-executor-owner: "workflow"', "MTCLI_WORKFLOW_COMPENSATION_EXECUTOR"],
    ['// domainspec-compensation-operation-role: "Operation"', '// domainspec-compensation-operation-role: "callback"', "MTCLI_WORKFLOW_COMPENSATION_RELATIONSHIP"],
  ];
  for (const [before, after, code] of mutants) {
    const fixture = targetFor("typescript", "Workflow");
    try {
      const content = fs.readFileSync(fixture.artifact, "utf8");
      assert.equal(content.includes(before), true, `test fixture contains ${before}`);
      fs.writeFileSync(fixture.artifact, content.replace(before, after));
      expectCode(fixture.target, code);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("State Machine initial, table, guard, source, effect, and rejection drift fail causally", () => {
  const mutants: readonly [string, string, string][] = [
    ['// domainspec-state-machine-initial: "open"', '// domainspec-state-machine-initial: "changed"', "MTCLI_STATE_MACHINE_INITIAL"],
    ['// domainspec-state-machine-transitions: [{"effect_event_ref":"accounts:account-changed","guard_ref":null,"source_state":"open","target_state":"changed","transition_id":"record-change"}]', '// domainspec-state-machine-transitions: []', "MTCLI_STATE_MACHINE_TRANSITION_TABLE"],
    ['// domainspec-state-machine-event-intents-only: true', '// domainspec-state-machine-event-intents-only: false', "MTCLI_STATE_MACHINE_EFFECT_BOUNDARY"],
    ['// domainspec-state-machine-guard-contract: "rule-reference-callback/v1"', '// domainspec-state-machine-guard-contract: "inline-boolean/v1"', "MTCLI_STATE_MACHINE_GUARD_CONTRACT"],
    ['// domainspec-state-machine-guard-required: true', '// domainspec-state-machine-guard-required: false', "MTCLI_STATE_MACHINE_GUARD_CONTRACT"],
    ['// domainspec-state-machine-source-enforcement: true', '// domainspec-state-machine-source-enforcement: false', "MTCLI_STATE_MACHINE_SOURCE_ENFORCEMENT"],
    ['// domainspec-state-machine-causal-rejections: ["invalid-current-state","undeclared-transition","source-mismatch","guard-rejected"]', '// domainspec-state-machine-causal-rejections: ["guard-rejected"]', "MTCLI_STATE_MACHINE_REJECTION_CONTRACT"],
    ["transition.source_state !== current", "transition.source_state === current", "MTCLI_STATE_MACHINE_SOURCE_ENFORCEMENT"],
    ["effectEventRef: transition.effect_event_ref", "effectEventRef: null", "MTCLI_STATE_MACHINE_EFFECT_BOUNDARY"],
  ];
  for (const [before, after, code] of mutants) {
    const fixture = targetFor("typescript", "State Machine");
    try {
      const content = fs.readFileSync(fixture.artifact, "utf8");
      assert.equal(content.includes(before), true, `test fixture contains ${before}`);
      fs.writeFileSync(fixture.artifact, content.replace(before, after));
      expectCode(fixture.target, code);
    } finally {
      clean(fixture.parent);
    }
  }
});

test("undeclared effects and generic byte drift fail closed", () => {
  const undeclared = targetFor();
  const drift = targetFor();
  try {
    fs.writeFileSync(path.join(undeclared.target, "undeclared-effect.txt"), "effect");
    expectCode(undeclared.target, "MTCLI_OBSERVE_UNDECLARED_OUTPUT");
    fs.appendFileSync(drift.artifact, "// byte drift\n");
    expectCode(drift.target, "MTCLI_OBSERVE_EXACT_REALIZATION");
  } finally {
    clean(undeclared.parent);
    clean(drift.parent);
  }
});
