import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

import { BODY_CONTRACTS, decodeBody, loadProjectNode, type DecodedProjectNode } from "../../src/input/project-model.ts";
import { canonicalJson, sha256, type SourceManifestV1 } from "../../src/input/source-manifest.ts";
import { FROZEN_META_TYPE_CATALOG } from "../../src/meta-types/catalog.ts";
import { GENERATOR_REGISTRY, generatorIdFor } from "../../src/generation/generators.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const sourceFixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");

const sourceManifest = Object.freeze({
  schema_version: "domainspec.stable-foundation-cli.source-manifest/v1",
  project_id: "test-project",
  source_count: 1,
  total_size_bytes: 1,
  sources: [],
  aggregate_sha256: "0".repeat(64),
  authority_effect: "none",
  manifest_sha256: "1".repeat(64),
}) as unknown as SourceManifestV1;

const bodySamples: Readonly<Record<string, Record<string, unknown>>> = {
  Entity: { description: "Entity", identity_field: "entity-id", fields: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, { field_id: "value", type_ref: { kind: "primitive", name: "string" }, required: true }] },
  "Value Object": { description: "Value", fields: [{ field_id: "value", type_ref: { kind: "primitive", name: "string" }, required: true }], invariant_refs: ["feature:valid-value"] },
  Enum: { description: "Enum", values: ["one", "two"] },
  Operation: { description: "Operation", reads: ["entity"], writes: ["entity.state"], effects: ["Changed"], guard: "allowed", failure_continuation: "return-error" },
  Query: { description: "Query", reads: ["entity"] },
  Calculation: { description: "Calculation", inputs: ["left", "right"] },
  Rule: { description: "Rule", predicate: "candidate != null" },
  Policy: { description: "Policy", strategies: ["first"] },
  Workflow: { description: "Workflow", steps: ["operate"], compensations: ["undo"] },
  Interface: { description: "Interface", boundary_kind: "internal", version: "1", compatibility: "exact", operations: [{ operation_id: "operate", operation_ref: "feature:operate", request: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }], result: [{ field_id: "accepted", type_ref: { kind: "primitive", name: "boolean" }, required: true }] }] },
  Event: { description: "Event", event_type: "event", version: "1", occurrence_id: { field_id: "occurrence-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, occurred_at_policy: "required", payload: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }] },
  Mapping: { description: "Mapping", source: "Source", target: "Target" },
  "State Machine": { description: "Machine", states: ["new", "done"], initial: "new", transitions: [{ transition_id: "finish", source_state: "new", target_state: "done", guard_ref: null, effect_event_ref: null }] },
};

function node(kind: string, id: string): DecodedProjectNode {
  const type = FROZEN_META_TYPE_CATALOG.backend_meta_types.find(({ label }) => label === kind)!;
  const relationships = kind === "Workflow" ? Object.freeze([
    Object.freeze({
      edge_id: "workflow-operate",
      relationship: "orchestrates",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "feature", node_id: id, kind: "Workflow" }),
      target: Object.freeze({ feature_id: "feature", node_id: "operate", kind: "Operation" }),
    }),
    Object.freeze({
      edge_id: "workflow-undo",
      relationship: "orchestrates",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "feature", node_id: id, kind: "Workflow" }),
      target: Object.freeze({ feature_id: "feature", node_id: "undo", kind: "Operation" }),
    }),
  ]) : kind === "Interface" ? Object.freeze([
    Object.freeze({
      edge_id: "interface-operate",
      relationship: "exposes",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "feature", node_id: id, kind: "Interface" }),
      target: Object.freeze({ feature_id: "feature", node_id: "operate", kind: "Operation" }),
    }),
  ]) : Object.freeze([]);
  return Object.freeze({
    project_root: path.resolve("/tmp/test-project"),
    project_id: "test-project",
    feature_id: "feature",
    node_id: id,
    kind,
    meta_type_id: type.id,
    body: decodeBody(kind, bodySamples[kind]),
    relationships,
    source_manifest: sourceManifest,
  });
}

test("TypeScript Entity planning is pure and deterministic", () => {
  const input = node("Entity", "customer");
  const left = planInstantiation(input, "typescript");
  const right = planInstantiation(input, "typescript");
  assert.deepEqual(left, right);
  assert.equal(left.artifacts[0]?.relative_path, "src/domainspec/typescript/feature/customer.ts");
  assert.equal(left.artifacts[0]?.sha256, sha256(left.artifacts[0]?.content ?? ""));
  const { plan_sha256: ignored, ...body } = left;
  assert.equal(left.plan_sha256, sha256(canonicalJson(body)));
  assert.match(left.artifacts[0]?.content ?? "", /domainspec-meta:/);
  assert.match(left.artifacts[0]?.content ?? "", /export class Customer/);
});

test("generator coverage is exactly the frozen 13 by 3 matrix", () => {
  assert.equal(Object.keys(BODY_CONTRACTS).length, 13);
  assert.equal(GENERATOR_REGISTRY.length, 39);
  assert.equal(new Set(GENERATOR_REGISTRY.map((row) => `${row.meta_type_id}/${row.language}`)).size, 39);
  assert.equal(new Set(GENERATOR_REGISTRY.map((row) => row.generator_id)).size, 39);
  for (const metaType of FROZEN_META_TYPE_CATALOG.backend_meta_types) {
    for (const language of ["typescript", "python", "rust"] as const) {
      const plan = planInstantiation(node(metaType.label, metaType.label.toLowerCase().replaceAll(" ", "-")), language);
      assert.equal(plan.selected_realization.meta_type_id, metaType.id);
      assert.equal(plan.selected_realization.language, language);
      assert.equal(plan.generator_id, generatorIdFor(metaType.id, language));
      assert.equal(plan.artifacts.length, 1);
      assert.equal(plan.artifacts[0]?.content.endsWith("\n"), true);
    }
  }
});

test("all generated Workflow profiles expose Recovery Intent as the only intent term", () => {
  const workflow = node("Workflow", "recovery-workflow");
  const typescript = planInstantiation(workflow, "typescript").artifacts[0]?.content ?? "";
  const python = planInstantiation(workflow, "python").artifacts[0]?.content ?? "";
  const rust = planInstantiation(workflow, "rust").artifacts[0]?.content ?? "";
  assert.match(typescript, /RecoveryWorkflowRecoveryIntent/);
  assert.match(typescript, /recoveryIntent/);
  assert.match(python, /recovery_intent/);
  assert.match(rust, /RecoveryWorkflowRecoveryIntent/);
  assert.match(rust, /recovery_intent/);
  for (const content of [typescript, python, rust]) {
    assert.match(content, /not-required/);
    assert.match(content, /recovery-required/);
    assert.match(content, /semantic[_A-Za-z]*[Ss]tatus/);
    assert.match(content, /required/);
    assert.match(content, /durable[_A-Za-z]*[Tt]erminal[_A-Za-z]*[Dd]isposition/);
    assert.equal(content.includes("domainspec-compensation-states"), false);
    assert.equal(content.includes('"requested"'), false);
    assert.equal(content.includes('"running"'), false);
  }
  const supersededTokens = [
    ["Compensation", "Intent"].join(""),
    ["compensation", "Intent"].join(""),
    ["compensation", "intent"].join("_"),
    ["compensation", "intent"].join("-"),
  ];
  for (const content of [typescript, python, rust]) {
    for (const token of supersededTokens) assert.equal(content.includes(token), false);
  }
});

test("all generated TypeScript typechecks, all generated Python parses, and generated Rust Workflow is rustc-checked when available", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-language-validation-"));
  try {
    fs.writeFileSync(path.join(root, "package.json"), `${JSON.stringify({ type: "module" })}\n`);
    const pythonFiles: string[] = [];
    for (const metaType of FROZEN_META_TYPE_CATALOG.backend_meta_types) {
      const nodeId = metaType.label.toLowerCase().replaceAll(" ", "-");
      for (const language of ["typescript", "python"] as const) {
        const artifact = planInstantiation(node(metaType.label, nodeId), language).artifacts[0]!;
        const absolute = path.join(root, language, artifact.relative_path);
        fs.mkdirSync(path.dirname(absolute), { recursive: true });
        fs.writeFileSync(absolute, artifact.content);
        if (language === "python") pythonFiles.push(absolute);
      }
    }
    const configPath = path.join(root, "tsconfig.json");
    fs.writeFileSync(configPath, `${JSON.stringify({ compilerOptions: { strict: true, target: "ES2022", module: "NodeNext", moduleResolution: "NodeNext", skipLibCheck: true }, include: ["typescript/**/*.ts"] })}\n`);
    const localTsc = path.resolve(testDir, "../../node_modules/.bin/tsc");
    const workspaceTsc = path.resolve(testDir, "../../../node_modules/.bin/tsc");
    const tsc = spawnSync(fs.existsSync(localTsc) ? localTsc : workspaceTsc, ["--project", configPath, "--noEmit", "--pretty", "false"], { encoding: "utf8" });
    assert.equal(tsc.status, 0, `${tsc.stdout}\n${tsc.stderr}`);
    for (const pythonFile of pythonFiles) {
      const python = spawnSync("python3", ["-c", "import pathlib,sys; compile(pathlib.Path(sys.argv[1]).read_text(), sys.argv[1], 'exec')", pythonFile], { encoding: "utf8" });
      assert.equal(python.status, 0, `${pythonFile}\n${python.stdout}\n${python.stderr}`);
    }
    const rustArtifact = planInstantiation(node("Workflow", "recovery-workflow"), "rust").artifacts[0]!;
    const rustSource = path.join(root, rustArtifact.relative_path);
    fs.mkdirSync(path.dirname(rustSource), { recursive: true });
    fs.writeFileSync(rustSource, rustArtifact.content);
    const rust = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", rustSource, "--out-dir", root], { encoding: "utf8" });
    if ((rust.error as NodeJS.ErrnoException | undefined)?.code !== "ENOENT") assert.equal(rust.status, 0, `${rust.stdout}\n${rust.stderr}`);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("State Machine causal outcomes are equivalent in TypeScript, Python, and Rust", async (context) => {
  const machine = loadProjectNode(sourceFixtureRoot, "beta:settlement-status");
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-state-machine-runtime-"));
  const expected = [
    "applied|settled|beta:settlement-completed",
    "guard-rejected",
    "undeclared-transition",
    "source-mismatch",
    "invalid-current-state",
  ];
  try {
    const typescriptArtifact = planInstantiation(machine, "typescript").artifacts[0]!;
    const typescriptSource = path.join(root, "settlement-status.ts");
    fs.writeFileSync(typescriptSource, typescriptArtifact.content);
    const generated = await import(`${pathToFileURL(typescriptSource).href}?case=state-machine-runtime`);
    const typescriptResults = [
      generated.settlementStatusTransition("pending", "complete-settlement", () => true),
      generated.settlementStatusTransition("pending", "complete-settlement", () => false),
      generated.settlementStatusTransition("pending", "missing", () => true),
      generated.settlementStatusTransition("settled", "complete-settlement", () => true),
      generated.settlementStatusTransition("unknown", "complete-settlement", () => true),
    ].map((result: { ok: boolean; state: string; effectEventRef?: string | null; code?: string }) => result.ok ? `applied|${result.state}|${result.effectEventRef ?? ""}` : result.code);
    assert.deepEqual(typescriptResults, expected);

    const pythonArtifact = planInstantiation(machine, "python").artifacts[0]!;
    const pythonSource = path.join(root, "settlement_status.py");
    fs.writeFileSync(pythonSource, pythonArtifact.content);
    const pythonProgram = [
      "import importlib.util,sys",
      "spec=importlib.util.spec_from_file_location('machine',sys.argv[1])",
      "machine=importlib.util.module_from_spec(spec)",
      "spec.loader.exec_module(machine)",
      "cases=[machine.settlement_status_transition('pending','complete-settlement',lambda _ref: True),machine.settlement_status_transition('pending','complete-settlement',lambda _ref: False),machine.settlement_status_transition('pending','missing',lambda _ref: True),machine.settlement_status_transition('settled','complete-settlement',lambda _ref: True),machine.settlement_status_transition('unknown','complete-settlement',lambda _ref: True)]",
      "print('\\n'.join(('applied|'+str(value['state'])+'|'+str(value['effect_event_ref'] or '')) if value['ok'] else str(value['code']) for value in cases))",
    ].join(";");
    const python = spawnSync("python3", ["-c", pythonProgram, pythonSource], { encoding: "utf8" });
    assert.equal(python.status, 0, `${python.stdout}\n${python.stderr}`);
    assert.deepEqual(python.stdout.trim().split("\n"), expected);

    const rustArtifact = planInstantiation(machine, "rust").artifacts[0]!;
    const rustSource = path.join(root, "settlement_status.rs");
    const rustHarness = `
fn normalized(result: SettlementStatusTransitionResult) -> String {
    match result {
        SettlementStatusTransitionResult::Applied { state, effect_event_ref, .. } => format!("applied|{}|{}", state, effect_event_ref.unwrap_or_default()),
        SettlementStatusTransitionResult::Rejected { code, .. } => code.to_owned(),
    }
}
fn main() {
    let cases = [
        settlement_status_transition("pending", "complete-settlement", |_| true),
        settlement_status_transition("pending", "complete-settlement", |_| false),
        settlement_status_transition("pending", "missing", |_| true),
        settlement_status_transition("settled", "complete-settlement", |_| true),
        settlement_status_transition("unknown", "complete-settlement", |_| true),
    ];
    for result in cases { println!("{}", normalized(result)); }
}
`;
    fs.writeFileSync(rustSource, `${rustArtifact.content}${rustHarness}`);
    const rustBinary = path.join(root, "settlement-status");
    const rust = spawnSync("rustc", ["--edition", "2024", rustSource, "-o", rustBinary], { encoding: "utf8" });
    if ((rust.error as NodeJS.ErrnoException | undefined)?.code === "ENOENT") {
      context.skip("Rust provider is not installed");
      return;
    }
    assert.equal(rust.status, 0, `${rust.stdout}\n${rust.stderr}`);
    const executed = spawnSync(rustBinary, [], { encoding: "utf8" });
    assert.equal(executed.status, 0, `${executed.stdout}\n${executed.stderr}`);
    assert.deepEqual(executed.stdout.trim().split("\n"), expected);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("L1 identity, value, enum, event, and interface outcomes are equivalent across native runtimes", async (context) => {
  const selected = [
    loadProjectNode(sourceFixtureRoot, "alpha:customer"),
    loadProjectNode(sourceFixtureRoot, "beta:settlement-details"),
    loadProjectNode(sourceFixtureRoot, "beta:settlement-method"),
    loadProjectNode(sourceFixtureRoot, "beta:settlement-completed"),
    loadProjectNode(sourceFixtureRoot, "alpha:settlement-api"),
  ];
  const expected = ["entity|true|false", "value|true|false", "enum|card|bank-transfer", "event|true|false", "interface|true|true|false"];
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-l1-runtime-"));
  try {
    const tsModules: Record<string, Record<string, unknown>> = {};
    for (const node of selected) {
      const source = path.join(root, `${node.node_id}.ts`);
      fs.writeFileSync(source, planInstantiation(node, "typescript").artifacts[0]!.content);
      tsModules[node.node_id] = await import(`${pathToFileURL(source).href}?case=l1-runtime`);
    }
    const Customer = tsModules["customer"]!.Customer as new (fields: Record<string, unknown>) => { sameIdentity(other: unknown): boolean };
    const Details = tsModules["settlement-details"]!.SettlementDetails as new (fields: Record<string, unknown>) => { equals(other: unknown): boolean };
    const firstCustomer = new Customer({ customerId: "a", settlementDetails: "details" });
    const sameCustomer = new Customer({ customerId: "a", settlementDetails: "changed" });
    const otherCustomer = new Customer({ customerId: "b", settlementDetails: "details" });
    const firstDetails = new Details({ amount: 5, method: "card" });
    const sameDetails = new Details({ amount: 5, method: "card" });
    const otherDetails = new Details({ amount: 6, method: "card" });
    const enumType = tsModules["settlement-method"]!.SettlementMethod as Record<string, string>;
    const eventCompatible = tsModules["settlement-completed"]!.settlementCompletedCompatible as (candidate: { type: string; version: string }) => boolean;
    const interfaceCompatible = tsModules["settlement-api"]!.settlementApiAcceptsVersion as (version: string) => boolean;
    const typescriptResults = [
      `entity|${firstCustomer.sameIdentity(sameCustomer)}|${firstCustomer.sameIdentity(otherCustomer)}`,
      `value|${firstDetails.equals(sameDetails)}|${firstDetails.equals(otherDetails)}`,
      `enum|${enumType.Card}|${enumType.BankTransfer}`,
      `event|${eventCompatible({ type: "settlement-completed", version: "1" })}|${eventCompatible({ type: "settlement-completed", version: "2" })}`,
      `interface|${interfaceCompatible("1")}|${interfaceCompatible("2")}|${interfaceCompatible("3")}`,
    ];
    assert.deepEqual(typescriptResults, expected);

    const pythonSources: string[] = [];
    for (const node of selected) {
      const source = path.join(root, `${node.node_id.replaceAll("-", "_")}.py`);
      fs.writeFileSync(source, planInstantiation(node, "python").artifacts[0]!.content);
      pythonSources.push(source);
    }
    const pythonProgram = [
      "import importlib.util,sys",
      "mods=[]",
      "for i,p in enumerate(sys.argv[1:]):",
      "    spec=importlib.util.spec_from_file_location('m'+str(i),p)",
      "    m=importlib.util.module_from_spec(spec)",
      "    sys.modules[spec.name]=m",
      "    spec.loader.exec_module(m)",
      "    mods.append(m)",
      "c,d,e,ev,api=mods",
      "a=c.Customer('a','details')",
      "print('entity|'+str(a.same_identity(c.Customer('a','changed'))).lower()+'|'+str(a.same_identity(c.Customer('b','details'))).lower())",
      "v=d.SettlementDetails(5.0,'card')",
      "print('value|'+str(v.equals(d.SettlementDetails(5.0,'card'))).lower()+'|'+str(v.equals(d.SettlementDetails(6.0,'card'))).lower())",
      "print('enum|'+e.SettlementMethod.CARD.value+'|'+e.SettlementMethod.BANK_TRANSFER.value)",
      "print('event|'+str(ev.settlement_completed_compatible('settlement-completed','1')).lower()+'|'+str(ev.settlement_completed_compatible('settlement-completed','2')).lower())",
      "print('interface|'+'|'.join(str(api.settlement_api_accepts_version(x)).lower() for x in ('1','2','3')))",
    ].join("\n");
    const python = spawnSync("python3", ["-c", pythonProgram, ...pythonSources], { encoding: "utf8" });
    assert.equal(python.status, 0, `${python.stdout}\n${python.stderr}`);
    assert.deepEqual(python.stdout.trim().split("\n"), expected);

    const rustSource = path.join(root, "l1.rs");
    const rustContent = selected.map((value) => planInstantiation(value, "rust").artifacts[0]!.content).join("\n") + `
fn main() {
    let a = Customer { customer_id: "a".to_owned(), settlement_details: "details".to_owned(), preferred_method: None };
    println!("entity|{}|{}", a.same_identity(&Customer { customer_id: "a".to_owned(), settlement_details: "changed".to_owned(), preferred_method: None }), a.same_identity(&Customer { customer_id: "b".to_owned(), settlement_details: "details".to_owned(), preferred_method: None }));
    let value = SettlementDetails { amount: 5.0, method: "card".to_owned() };
    println!("value|{}|{}", value.equals(&SettlementDetails { amount: 5.0, method: "card".to_owned() }), value.equals(&SettlementDetails { amount: 6.0, method: "card".to_owned() }));
    println!("enum|card|bank-transfer");
    println!("event|{}|{}", settlement_completed_compatible("settlement-completed", "1"), settlement_completed_compatible("settlement-completed", "2"));
    println!("interface|{}|{}|{}", settlement_api_accepts_version("1"), settlement_api_accepts_version("2"), settlement_api_accepts_version("3"));
}
`;
    fs.writeFileSync(rustSource, rustContent);
    const rustBinary = path.join(root, "l1");
    const rust = spawnSync("rustc", ["--edition", "2024", rustSource, "-o", rustBinary], { encoding: "utf8" });
    if ((rust.error as NodeJS.ErrnoException | undefined)?.code === "ENOENT") {
      context.skip("Rust provider is not installed");
      return;
    }
    assert.equal(rust.status, 0, `${rust.stdout}\n${rust.stderr}`);
    const executed = spawnSync(rustBinary, [], { encoding: "utf8" });
    assert.equal(executed.status, 0, `${executed.stdout}\n${executed.stderr}`);
    assert.deepEqual(executed.stdout.trim().split("\n"), expected);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("generated TypeScript Workflow emits canonical Recovery Intent and preflights exact external Operation bindings", async () => {
  const type = FROZEN_META_TYPE_CATALOG.backend_meta_types.find(({ label }) => label === "Workflow")!;
  const workflowNode: DecodedProjectNode = Object.freeze({
    project_root: path.resolve("/tmp/test-project"),
    project_id: "test-project",
    feature_id: "feature",
    node_id: "recovery-workflow",
    kind: "Workflow",
    meta_type_id: type.id,
    body: decodeBody("Workflow", {
      description: "Recovery workflow",
      steps: ["operate", "publish"],
      compensations: ["undo", "none"],
      compensation_dependencies: [],
    }),
    relationships: Object.freeze([
      Object.freeze({ edge_id: "workflow-operate", relationship: "orchestrates", scope: "feature" as const, source: Object.freeze({ feature_id: "feature", node_id: "recovery-workflow", kind: "Workflow" }), target: Object.freeze({ feature_id: "feature", node_id: "operate", kind: "Operation" }) }),
      Object.freeze({ edge_id: "workflow-publish", relationship: "orchestrates", scope: "feature" as const, source: Object.freeze({ feature_id: "feature", node_id: "recovery-workflow", kind: "Workflow" }), target: Object.freeze({ feature_id: "feature", node_id: "publish", kind: "Operation" }) }),
      Object.freeze({ edge_id: "workflow-undo", relationship: "orchestrates", scope: "feature" as const, source: Object.freeze({ feature_id: "feature", node_id: "recovery-workflow", kind: "Workflow" }), target: Object.freeze({ feature_id: "feature", node_id: "undo", kind: "Operation" }) }),
    ]),
    source_manifest: sourceManifest,
  });
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-workflow-runtime-"));
  try {
    const artifact = planInstantiation(workflowNode, "typescript").artifacts[0]!;
    const source = path.join(root, "recovery-workflow.ts");
    fs.writeFileSync(source, artifact.content);
    const generated = await import(`${pathToFileURL(source).href}?case=runtime`);
    let directRecoveryCalls = 0;
    const digest = (material: string) => sha256(material);
    const outcome = await generated.recoveryWorkflow(
      async (step: string) => {
        if (step === "publish") throw new Error("publication-failed");
      },
      async () => {
        directRecoveryCalls += 1;
        throw new Error("Workflow must not execute recovery");
      },
      "workflow-run-1",
      "failure-1",
      digest,
    );
    assert.equal(outcome.compensationExecution, false);
    assert.equal(directRecoveryCalls, 0);
    assert.equal(outcome.workflowEvaluationResult, "recovery-required");
    assert.equal(outcome.recoveryIntent.semanticStatus, "required");
    assert.equal(outcome.recoveryIntent.workflowExecutionId, "workflow-run-1");
    assert.equal(outcome.recoveryIntent.failureOccurrenceId, "failure-1");
    assert.match(outcome.recoveryIntent.completedStepJournalDigest, /^[0-9a-f]{64}$/);
    assert.match(outcome.recoveryIntent.planDigest, /^[0-9a-f]{64}$/);
    assert.match(outcome.recoveryIntent.intentId, /^[0-9a-f]{64}$/);
    assert.deepEqual(outcome.recoveryIntent.plan.map(({ operationId }: { operationId: string }) => operationId), ["undo"]);
    assert.match(outcome.recoveryIntent.plan[0].invocationIdentity, /^[0-9a-f]{64}$/);

    const repeatedOutcome = await generated.recoveryWorkflow(
      async (step: string) => { if (step === "publish") throw new Error("publication-failed-again"); },
      async () => { directRecoveryCalls += 1; },
      "workflow-run-1",
      "failure-1",
      digest,
    );
    assert.equal(repeatedOutcome.recoveryIntent.intentId, outcome.recoveryIntent.intentId);
    assert.equal(repeatedOutcome.recoveryIntent.planDigest, outcome.recoveryIntent.planDigest);
    assert.equal(repeatedOutcome.recoveryIntent.plan[0].invocationIdentity, outcome.recoveryIntent.plan[0].invocationIdentity);
    assert.equal(directRecoveryCalls, 0);

    const noRecovery = await generated.recoveryWorkflow(
      async () => { throw new Error("first-step-failed"); },
      async () => { directRecoveryCalls += 1; },
      "workflow-run-2",
      "failure-2",
      digest,
    );
    assert.equal(noRecovery.workflowEvaluationResult, "not-required");
    assert.equal(noRecovery.recoveryIntent, null);
    assert.equal(directRecoveryCalls, 0);

    const calls: string[] = [];
    const validBinding = {
      workflowId: "recovery-workflow",
      operationId: "undo",
      failureContinuation: "escalate",
      invoke: async (invocationIdentity: string) => {
        calls.push(invocationIdentity);
        return { ok: true };
      },
    };
    await assert.rejects(
      generated.executeRecoveryWorkflowRecovery(outcome.recoveryIntent, [validBinding, {
        workflowId: "recovery-workflow",
        operationId: "publish",
        failureContinuation: "terminal-failure",
        invoke: async () => { calls.push("must-not-run"); return { ok: true }; },
      }], digest),
      /undeclared recovery binding:publish/,
    );
    assert.deepEqual(calls, []);
    await assert.rejects(
      generated.executeRecoveryWorkflowRecovery(outcome.recoveryIntent, [validBinding, {
        workflowId: "recovery-workflow",
        operationId: "rogue",
        failureContinuation: "terminal-failure",
        invoke: async () => { calls.push("must-not-run"); return { ok: true }; },
      }], digest),
      /binding is outside Workflow relation set:rogue/,
    );
    assert.deepEqual(calls, []);
    await assert.rejects(
      generated.executeRecoveryWorkflowRecovery({
        ...outcome.recoveryIntent,
        plan: [{ ...outcome.recoveryIntent.plan[0], operationId: "rogue" }],
      }, [validBinding], digest),
      /recovery target is outside Workflow relation set:rogue/,
    );
    assert.deepEqual(calls, []);
    await assert.rejects(
      generated.executeRecoveryWorkflowRecovery({
        ...outcome.recoveryIntent,
        intentId: "0".repeat(64),
      }, [validBinding], digest),
      /Recovery Intent identity mismatch/,
    );
    assert.deepEqual(calls, []);
    await assert.rejects(generated.executeRecoveryWorkflowRecovery(outcome.recoveryIntent, [], digest), /missing recovery Operation:undo/);
    assert.deepEqual(calls, []);

    const execution = await generated.executeRecoveryWorkflowRecovery(outcome.recoveryIntent, [validBinding], digest);
    assert.equal(execution.outcome, "succeeded");
    assert.equal(execution.recoveryIntentSemanticStatus, "required");
    assert.equal(execution.durableTerminalDisposition, null);
    assert.deepEqual(execution.executedPlanOccurrenceIds, [outcome.recoveryIntent.plan[0].planOccurrenceId]);
    assert.deepEqual(calls, [outcome.recoveryIntent.plan[0].invocationIdentity]);

    const failedExecution = await generated.executeRecoveryWorkflowRecovery(outcome.recoveryIntent, [{
      ...validBinding,
      invoke: async () => ({ ok: false, reason: "undo-failed" }),
    }], digest);
    assert.equal(failedExecution.outcome, "failed");
    assert.equal(failedExecution.failureContinuation, "escalate");
    assert.equal(failedExecution.recoveryIntentSemanticStatus, "required");
    assert.equal(failedExecution.durableTerminalDisposition, null);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
