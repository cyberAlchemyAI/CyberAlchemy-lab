import { execFile, spawnSync } from "node:child_process";
import { readdirSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { promisify } from "node:util";

import { deriveUnit, L1_CURRENT_PROJECTION, L1_PATHS, loadFinancialSettlementGraph } from "./derive.js";
import { assertExactRef, canonicalJson, digestValue, exactRef, readJson, repositoryRoot, writeStableJson } from "./exact-ref.js";
import type { SettlementDecisionInput } from "./standalone-settlement-decision.js";
import { loadStandaloneR4Decision, R4_STANDALONE_CONTRACT, R4_STANDALONE_SOURCE, type StandaloneR4Decision } from "./standalone-r4-runtime.js";
import { P4_CURRENT_ATTEMPT, replayStoredCurrentP4Receipt, type CurrentP4Receipt } from "./verify-p4-current.js";
import { fail, L1Error, R4_IDENTITY, type ExactRef, type GraphHandle, type L1ErrorCode, type L1Obligation } from "./types.js";

const EVF = "projects/domainspec-v2/development/evolvable-validation-framework";
export const R4_CURRENT_BINDING = `${EVF}/fixtures/SWU-GCP-003-R4/financial-settlement-r4-binding.v2.json`;
export const R4_CURRENT_VALIDATION = `${EVF}/work-pack/financial-settlement-r4-current-validation.v2.json`;
export const R4_CURRENT_ATTEMPT = `${EVF}/evidence/SWU-GCP-003-R4/attempt-002`;
const RECEIPT_SCHEMA = `${EVF}/contracts/financial-settlement-r4-terminal-receipt.v2.schema.json`;
const P4_RECEIPT = `${P4_CURRENT_ATTEMPT}/terminal-receipt.json`;
const CLAIM_CEILING = "candidate-local-r4-pure-decision-with-p4-prerequisite-not-application-equivalence-or-side-effects";
const BINDING_REF: ExactRef = { path: R4_CURRENT_BINDING,
  sha256: "c14a913cf4df623a37ce8a54a8389090db86cf96f2d4c1f36f5ae9d769c0a505", size_bytes: 2901 };
const VALIDATION_REF: ExactRef = { path: R4_CURRENT_VALIDATION,
  sha256: "4bfd1ca0e3a9a0997745f24842ddd6babbdf6ec9ebc042f7c3fbab638c6dd980", size_bytes: 4573 };
const RECEIPT_SCHEMA_REF: ExactRef = { path: RECEIPT_SCHEMA,
  sha256: "7b852b69622c4f4ddf64eacd898c611a013a133035e5a41f8878d734cad39c8b", size_bytes: 2843 };
const OUTPUT_FILES = ["derived-obligation.json", "observed-decision.json", "mutation-report.json",
  "test-process-result.json", "validation-result.json", "terminal-receipt.json"] as const;
const TEST_FILES = [
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-settlement-decision.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/current-projection.test.ts",
] as const;
const evidence = (name: string) => `${R4_CURRENT_ATTEMPT}/${name}`;

type Binding = Readonly<{
  schema_version: string; binding_id: string; unit_id: string; obligation_id: string; rule_id: string;
  edge_id: string; target_id: string; decision_field: string; semantic_ref: ExactRef;
  obligation_spec_ref: ExactRef; runtime_contract_ref: ExactRef; runtime_source_ref: ExactRef;
  runtime_loader_ref: ExactRef; fixture_ref: ExactRef; graph_ref: ExactRef;
  source_manifest_ref: ExactRef; p4_terminal_receipt_ref: ExactRef;
  authority_effect: string; release_admission: string; claim_ceiling: string;
}>;
type ValidationContract = Readonly<{
  schema_version: string; contract_id: string; unit_id: string;
  target_inventory: readonly Readonly<{ id: string; path: string }>[];
  target_denominator_scope: string;
  required_mutants: readonly Readonly<{ id: string; code: L1ErrorCode }>[];
  authority_effect: string; release_admission: string; claim_ceiling: string;
}>;
type Fixture = Readonly<{
  schema_version: string; fixture_id: string; expected_values_forbidden: boolean;
  cases: readonly Readonly<{ case_id: string; control_class: "truth-table" | "other-date" | "other-type";
    input: SettlementDecisionInput }>[];
}>;
type Observation = Readonly<{ case_id: string; control_class: Fixture["cases"][number]["control_class"];
  input_digest: string; actual: boolean; expected: boolean }>;
type Execution = Readonly<{
  schema_version: "evf.financial-settlement-r4-observed-decision/v2";
  execution_id: "evf.l1.financial-settlement.r4.execution.v2";
  fixture_ref: ExactRef; observations: readonly Observation[]; observations_digest: string;
  side_effect_observation: "none-pure-decision-only"; status: "pass";
  authority_effect: "none"; claim_ceiling: typeof CLAIM_CEILING;
}>;
type MutationResult = Readonly<{ mutant_id: string; required_code: L1ErrorCode;
  observed_code: L1ErrorCode; status: "killed" }>;
type TestProcess = Readonly<{
  schema_version: "evf.financial-settlement-r4-test-process/v2"; runner: "vitest";
  selected_test_refs: readonly ExactRef[]; total: 6; passed: 6; failed: 0; pending: 0; todo: 0;
  assertions: readonly Readonly<{ name: string; status: "passed" }>[];
  status: "pass"; authority_effect: "none"; claim_ceiling: typeof CLAIM_CEILING;
}>;

function schemaValidate(repoRoot: string, schemaPath: string, documentPath: string): void {
  const script = "import json,sys; from jsonschema import Draft202012Validator; " +
    "s=json.load(open(sys.argv[1])); d=json.load(open(sys.argv[2])); " +
    "Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(d)";
  const run = spawnSync("python3", ["-c", script, resolve(repoRoot, schemaPath), resolve(repoRoot, documentPath)],
    { cwd: repoRoot, encoding: "utf8", timeout: 30_000, maxBuffer: 1024 * 1024 });
  if (run.error || run.status !== 0) fail("TARGET_BASELINE_DRIFT", "admission",
    `schema validation failed for ${documentPath}: ${run.stderr || run.error}`);
}

function selectedSchemas(repoRoot: string): void {
  assertExactRef(repoRoot, RECEIPT_SCHEMA_REF, "BINDING_DIGEST_STALE");
  for (const [schema, document] of [
    [`${EVF}/contracts/financial-settlement-r4-runtime.v2.schema.json`, R4_STANDALONE_CONTRACT],
    [`${EVF}/contracts/financial-settlement-l1-obligations.v1.schema.json`, L1_PATHS.r4Obligation],
    [`${EVF}/fixtures/SWU-GCP-003-R4/financial-settlement-r4-input.v1.schema.json`, L1_PATHS.r4Fixture],
    [`${EVF}/fixtures/SWU-GCP-003-R4/financial-settlement-r4-binding.v2.schema.json`, R4_CURRENT_BINDING],
    [`${EVF}/work-pack/financial-settlement-r4-current-validation.v2.schema.json`, R4_CURRENT_VALIDATION],
  ] as const) schemaValidate(repoRoot, schema, document);
}

function sameRef(repoRoot: string, actual: ExactRef, expectedPath: string, code: L1ErrorCode): void {
  if (canonicalJson(actual) !== canonicalJson(exactRef(repoRoot, expectedPath)))
    fail(code, "binding", `selected exact ref differs: ${expectedPath}`);
  assertExactRef(repoRoot, actual, code);
}

export function loadCurrentR4Binding(repoRoot: string, ref: ExactRef = BINDING_REF): Binding {
  if (canonicalJson(ref) !== canonicalJson(BINDING_REF)) fail("BINDING_DIGEST_STALE", "binding", "R4 v2 binding selection changed");
  assertExactRef(repoRoot, ref, "BINDING_DIGEST_STALE");
  const binding = readJson<Binding>(repoRoot, ref.path);
  if (binding.schema_version !== "evf.financial-settlement-r4-binding/v2" ||
      binding.binding_id !== "evf.l1.financial-settlement.r4.binding.v2" ||
      binding.unit_id !== "SWU-GCP-003-R4" || binding.obligation_id !== R4_IDENTITY.obligation_id ||
      binding.rule_id !== R4_IDENTITY.rule_id || binding.edge_id !== R4_IDENTITY.edge_id ||
      binding.target_id !== "financial-settlement.GenerateSettlement" ||
      binding.decision_field !== "shouldCreateMakeupAppliedEvent" ||
      binding.authority_effect !== "none" || binding.release_admission !== "not-granted" ||
      binding.claim_ceiling !== CLAIM_CEILING) fail("BINDING_DIGEST_STALE", "binding", "R4 v2 identity or ceiling differs");
  for (const [ref, path, code] of [
    [binding.semantic_ref, L1_PATHS.r4Semantic, "PREDICATE_DIGEST_STALE"],
    [binding.obligation_spec_ref, L1_PATHS.r4Obligation, "BINDING_DIGEST_STALE"],
    [binding.runtime_contract_ref, R4_STANDALONE_CONTRACT, "BINDING_DIGEST_STALE"],
    [binding.runtime_source_ref, R4_STANDALONE_SOURCE, "BINDING_DIGEST_STALE"],
    [binding.runtime_loader_ref, "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-r4-runtime.ts", "BINDING_DIGEST_STALE"],
    [binding.fixture_ref, L1_PATHS.r4Fixture, "FIXTURE_DIGEST_STALE"],
    [binding.graph_ref, L1_CURRENT_PROJECTION.graph, "SOURCE_GRAPH_DIGEST_STALE"],
    [binding.source_manifest_ref, L1_CURRENT_PROJECTION.sourceManifest, "SOURCE_GRAPH_DIGEST_STALE"],
    [binding.p4_terminal_receipt_ref, P4_RECEIPT, "RECEIPT_TAMPERED"],
  ] as const) sameRef(repoRoot, ref, path, code);
  return binding;
}

function selectedContract(repoRoot: string): ValidationContract {
  assertExactRef(repoRoot, VALIDATION_REF, "BINDING_DIGEST_STALE");
  const contract = readJson<ValidationContract>(repoRoot, R4_CURRENT_VALIDATION);
  if (contract.schema_version !== "evf.financial-settlement-r4-current-validation/v2" ||
      contract.contract_id !== "evf.l1.financial-settlement.r4.current-validation.v2" ||
      contract.unit_id !== "SWU-GCP-003-R4" || contract.authority_effect !== "none" ||
      contract.release_admission !== "not-granted" || contract.claim_ceiling !== CLAIM_CEILING ||
      contract.target_denominator_scope !== "selected-nonrecursive-inputs" ||
      contract.target_inventory.length !== 19 || contract.required_mutants.length !== 15 ||
      new Set(contract.target_inventory.map(item => item.id)).size !== 19 ||
      new Set(contract.target_inventory.map(item => item.path)).size !== 19) {
    fail("VERIFIER_TARGET_OMITTED", "admission", "R4 current validation denominator differs");
  }
  return contract;
}

function targetInventory(repoRoot: string, contract: ValidationContract) {
  return contract.target_inventory.map(item => ({ id: item.id, ref: exactRef(repoRoot, item.path) }));
}

export function assertCurrentR4TargetInventory(
  actual: readonly Readonly<{ id: string; ref: ExactRef }>[], contract: ValidationContract,
): void {
  if (actual.length !== contract.target_inventory.length || actual.some((item, index) =>
    item.id !== contract.target_inventory[index]?.id || item.ref.path !== contract.target_inventory[index]?.path)) {
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "R4 current target inventory differs");
  }
}

function selectedFixture(repoRoot: string, binding: Binding): Fixture {
  const fixture = readJson<Fixture>(repoRoot, binding.fixture_ref.path);
  const expectedIds = ["r4-zero-same-date", "r4-one-same-date", "r4-two-same-date",
    "r4-other-date-control", "r4-other-type-control"];
  if (fixture.schema_version !== "evf.financial-settlement-r4-input/v1" ||
      fixture.fixture_id !== "evf.l1.financial-settlement.r4.fixture.v1" ||
      fixture.expected_values_forbidden !== true || fixture.cases.length !== 5 ||
      canonicalJson(fixture.cases.map(item => item.case_id)) !== canonicalJson(expectedIds) ||
      fixture.cases.some(item => !Number.isSafeInteger(item.input.totalAppliedMakeup) ||
        item.input.totalAppliedMakeup <= 0 || typeof item.input.periodEnd !== "string")) {
    fail("FIXTURE_DIGEST_STALE", "binding", "R4 fixture identity, premise or denominator differs");
  }
  const [zero, one, two, otherDate, otherType] = fixture.cases;
  const sameDate = (item: Fixture["cases"][number]) => item.input.existingTransactions.filter(entry =>
    entry.type === "MAKEUP_APPLIED" && entry.date === item.input.periodEnd).length;
  if (canonicalJson(fixture.cases.map(item => item.control_class)) !==
      canonicalJson(["truth-table", "truth-table", "truth-table", "other-date", "other-type"]) ||
      canonicalJson(fixture.cases.map(sameDate)) !== canonicalJson([0, 1, 2, 0, 0]) ||
      zero!.input.existingTransactions.length !== 0 ||
      one!.input.existingTransactions.length !== 1 || two!.input.existingTransactions.length !== 2 ||
      otherDate!.input.existingTransactions.length !== 1 ||
      otherDate!.input.existingTransactions[0]!.type !== "MAKEUP_APPLIED" ||
      otherDate!.input.existingTransactions[0]!.date === otherDate!.input.periodEnd ||
      otherType!.input.existingTransactions.length !== 1 ||
      otherType!.input.existingTransactions[0]!.type === "MAKEUP_APPLIED" ||
      otherType!.input.existingTransactions[0]!.date !== otherType!.input.periodEnd) {
    fail("FIXTURE_DIGEST_STALE", "binding", "R4 fixture case/control-class/count/type/date join differs");
  }
  return fixture;
}

function semanticRows(obligation: L1Obligation): readonly Readonly<{
  case_id: string; same_date_makeup_applied_count: number; expected: boolean }> [] {
  const semantic = obligation.semantic_contract as { truth_table?: readonly { case_id: string;
    same_date_makeup_applied_count: number; expected: boolean }[]; fixed_premise?: unknown; decision_field?: string };
  const rows = semantic.truth_table;
  if (obligation.contract_kind !== "pure-decision-truth-table" ||
      semantic.decision_field !== "shouldCreateMakeupAppliedEvent" ||
      canonicalJson(semantic.fixed_premise) !== canonicalJson({ totalAppliedMakeup: { operator: "gt", right: 0 } }) ||
      !rows || rows.length !== 5 || new Set(rows.map(item => item.case_id)).size !== 5 ||
      rows.some(item => typeof item.expected !== "boolean" || !Number.isSafeInteger(item.same_date_makeup_applied_count))) {
    fail("OBLIGATION_MISMATCH", "derivation", "R4 current O_spec truth table differs");
  }
  return rows;
}

function observeDecision(repoRoot: string, fixture: Fixture, obligation: L1Obligation, decide: StandaloneR4Decision): Execution {
  const rows = semanticRows(obligation);
  if (canonicalJson(fixture.cases.map(item => item.case_id)) !== canonicalJson(rows.map(item => item.case_id)))
    fail("OBLIGATION_MISMATCH", "derivation", "R4 fixture and obligation case IDs differ");
  const observations = fixture.cases.map((item, index): Observation => {
    const count = item.input.existingTransactions.filter(entry =>
      entry.type === "MAKEUP_APPLIED" && entry.date === item.input.periodEnd).length;
    if (count !== rows[index]!.same_date_makeup_applied_count)
      fail("FIXTURE_DIGEST_STALE", "binding", `R4 fixture count differs: ${item.case_id}`);
    return { case_id: item.case_id, control_class: item.control_class,
      input_digest: digestValue(item.input), actual: decide(item.input), expected: rows[index]!.expected };
  });
  return { schema_version: "evf.financial-settlement-r4-observed-decision/v2",
    execution_id: "evf.l1.financial-settlement.r4.execution.v2", fixture_ref: exactRef(repoRoot, L1_PATHS.r4Fixture),
    observations, observations_digest: digestValue(observations), side_effect_observation: "none-pure-decision-only",
    status: "pass", authority_effect: "none", claim_ceiling: CLAIM_CEILING };
}

export function validateCurrentR4Decision(execution: Execution): void {
  if (execution.observations_digest !== digestValue(execution.observations) ||
      execution.observations.length !== 5 || new Set(execution.observations.map(item => item.case_id)).size !== 5)
    fail("OBSERVATION_TAMPERED", "execution", "R4 observation digest or denominator differs");
  for (const item of execution.observations) if (item.actual !== item.expected)
    fail(item.control_class === "truth-table" ? "R4_RESULT_MISMATCH" : "R4_CONTROL_MISMATCH",
      "execution", `R4 decision mismatch: ${item.case_id}`);
  if (execution.side_effect_observation !== "none-pure-decision-only")
    fail("CLAIM_INFLATION", "execution", "R4 pure decision claims side effects");
}

function codeOf(action: () => unknown): L1ErrorCode | "NO_FAILURE" {
  try { action(); return "NO_FAILURE"; }
  catch (error) { if (error instanceof L1Error) return error.code; throw error; }
}

function negativeControls(repoRoot: string, fixture: Fixture, obligation: L1Obligation,
  binding: Binding, contract: ValidationContract,
  targets: readonly Readonly<{ id: string; ref: ExactRef }>[]): readonly MutationResult[] {
  const count = (input: SettlementDecisionInput) => input.existingTransactions.filter(item =>
    item.type === "MAKEUP_APPLIED" && item.date === input.periodEnd).length;
  const variants: readonly (readonly [string, L1ErrorCode, StandaloneR4Decision])[] = [
    ["R4-M01-always-false", "R4_RESULT_MISMATCH", () => false],
    ["R4-M02-always-true", "R4_RESULT_MISMATCH", () => true],
    ["R4-M03-wrong-date-filter", "R4_RESULT_MISMATCH", input => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(item => item.type === "MAKEUP_APPLIED" && item.date !== input.periodEnd)],
    ["R4-M04-wrong-type-filter", "R4_RESULT_MISMATCH", input => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(item => item.type !== "MAKEUP_APPLIED" && item.date === input.periodEnd)],
    ["R4-M05-wrong-count-threshold", "R4_RESULT_MISMATCH", input => input.totalAppliedMakeup > 0 && count(input) <= 1],
    ["R4-M06-count-all-dates", "R4_CONTROL_MISMATCH", input => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(item => item.type === "MAKEUP_APPLIED")],
    ["R4-M07-count-all-types", "R4_CONTROL_MISMATCH", input => input.totalAppliedMakeup > 0 && !input.existingTransactions.some(item => item.date === input.periodEnd)],
  ];
  const results: MutationResult[] = [];
  for (const [id, required, decide] of variants) {
    const actual = codeOf(() => validateCurrentR4Decision(observeDecision(repoRoot, fixture, obligation, decide)));
    if (actual !== required) fail(required, "mutation", `${id} produced ${actual}`);
    results.push({ mutant_id: id, required_code: required, observed_code: actual, status: "killed" });
  }
  const graph = structuredClone(loadFinancialSettlementGraph(repoRoot, L1_CURRENT_PROJECTION));
  const edge = graph.edges.find(item => item.edge_id === R4_IDENTITY.edge_id) as { to: string } | undefined;
  if (!edge) fail("EDGE_ENDPOINT_MISMATCH", "derivation", "R4 selected graph edge absent");
  edge.to = "financial-settlement.PayoutCreated";
  const zero = "0".repeat(64);
  const baseline = buildCurrentR4Receipt(deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION }).graph_handle,
    binding.p4_terminal_receipt_ref, { binding_ref: BINDING_REF, validation_contract_ref: VALIDATION_REF,
      derivation_ref: binding.semantic_ref, execution_ref: binding.runtime_source_ref,
      mutation_report_ref: binding.fixture_ref, test_result_ref: binding.graph_ref,
      validation_result_ref: binding.source_manifest_ref });
  const observed = observeDecision(repoRoot, fixture, obligation, () => true);
  const checks: readonly (readonly [string, L1ErrorCode, () => unknown])[] = [
    ["R4-M08-edge-wrong-target", "EDGE_ENDPOINT_MISMATCH", () => deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION, graph })],
    ["R4-M09-source-graph-digest-stale", "SOURCE_GRAPH_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.graph_ref, sha256: zero }, "SOURCE_GRAPH_DIGEST_STALE")],
    ["R4-M10-predicate-digest-stale", "PREDICATE_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.semantic_ref, sha256: zero }, "PREDICATE_DIGEST_STALE")],
    ["R4-M11-binding-digest-stale", "BINDING_DIGEST_STALE", () => loadCurrentR4Binding(repoRoot, { ...BINDING_REF, sha256: zero })],
    ["R4-M12-fixture-digest-stale", "FIXTURE_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.fixture_ref, sha256: zero }, "FIXTURE_DIGEST_STALE")],
    ["R4-M13-observation-tamper", "OBSERVATION_TAMPERED", () => validateCurrentR4Decision({ ...observed, observations_digest: zero })],
    ["R4-M14-receipt-tamper", "RECEIPT_TAMPERED", () => assertReceiptDigest({ ...baseline,
      acceptance_vector: { ...baseline.acceptance_vector, tests_passed: 5 } })],
    ["R4-M15-verifier-target-omitted", "VERIFIER_TARGET_OMITTED", () => assertCurrentR4TargetInventory(targets.slice(1), contract)],
  ];
  for (const [id, required, action] of checks) {
    const actual = codeOf(action);
    if (actual !== required) fail(required, "mutation", `${id} produced ${actual}`);
    results.push({ mutant_id: id, required_code: required, observed_code: actual, status: "killed" });
  }
  if (results.length !== 15 || results.some((item, index) =>
      item.mutant_id !== contract.required_mutants[index]?.id ||
      item.required_code !== contract.required_mutants[index]?.code))
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "R4 mutation denominator differs");
  return results;
}

async function runSelectedTests(repoRoot: string): Promise<TestProcess> {
  const packageRoot = resolve(repoRoot, "projects/domainspec-v2/impl/test-derivation-engine");
  let stdout: string;
  try {
    ({ stdout } = await promisify(execFile)("pnpm", ["exec", "vitest", "run",
      "src/minted-project/l1/standalone-settlement-decision.test.ts",
      "src/minted-project/l1/current-projection.test.ts", "--reporter=json"],
    { cwd: packageRoot, encoding: "utf8", timeout: 120_000, maxBuffer: 4 * 1024 * 1024 }));
  } catch (error) { fail("TARGET_BASELINE_DRIFT", "execution",
    `selected R4 test process failed: ${error instanceof Error ? error.message : String(error)}`); }
  let report: Record<string, unknown>;
  try { report = JSON.parse(stdout) as Record<string, unknown>; }
  catch { fail("TARGET_BASELINE_DRIFT", "execution", "selected R4 test process returned non-JSON output"); }
  if (report.success !== true || report.numTotalTests !== 6 || report.numPassedTests !== 6 ||
      report.numFailedTests !== 0 || report.numPendingTests !== 0 || report.numTodoTests !== 0 ||
      !Array.isArray(report.testResults) || report.testResults.length !== 2)
    fail("TARGET_BASELINE_DRIFT", "execution", "selected R4 test denominator differs");
  const files = report.testResults as { name: string; assertionResults: readonly { fullName: string; status: string }[] }[];
  if (canonicalJson(files.map(item => item.name).sort()) !==
      canonicalJson(TEST_FILES.map(path => resolve(repoRoot, path)).sort()))
    fail("TARGET_BASELINE_DRIFT", "execution", "selected R4 test files differ");
  const assertions = files.flatMap(item => item.assertionResults.map(value =>
    ({ name: value.fullName, status: value.status })));
  if (assertions.length !== 6 || assertions.some(item => item.status !== "passed") ||
      new Set(assertions.map(item => item.name)).size !== 6)
    fail("TARGET_BASELINE_DRIFT", "execution", "selected R4 assertions differ");
  return { schema_version: "evf.financial-settlement-r4-test-process/v2", runner: "vitest",
    selected_test_refs: TEST_FILES.map(path => exactRef(repoRoot, path)), total: 6, passed: 6,
    failed: 0, pending: 0, todo: 0,
    assertions: assertions.sort((a, b) => a.name.localeCompare(b.name)) as TestProcess["assertions"],
    status: "pass", authority_effect: "none", claim_ceiling: CLAIM_CEILING };
}

export type CurrentR4Receipt = Readonly<{
  schema_version: "evf.financial-settlement-r4-terminal-receipt/v2";
  receipt_id: "evf.l1.financial-settlement.r4.receipt.v2"; unit_id: "SWU-GCP-003-R4";
  status: "pass"; graph_handle: GraphHandle; p4_terminal_receipt_ref: ExactRef;
  evidence: Readonly<{ binding_ref: ExactRef; validation_contract_ref: ExactRef;
    derivation_ref: ExactRef; execution_ref: ExactRef; mutation_report_ref: ExactRef;
    test_result_ref: ExactRef; validation_result_ref: ExactRef }>;
  acceptance_vector: Readonly<{ obligations: 1; bindings: 1; p4_prerequisite_replayed: 1;
    eligible_execution_cases: 5; mutants_required: 15; mutants_killed: 15;
    targets: 19; target_denominator_scope: "selected-nonrecursive-inputs";
    tests_passed: 6; writes_observed: 0; events_observed: 0 }>;
  claim_ceiling: typeof CLAIM_CEILING; authority_effect: "none";
  release_admission: "not-granted"; receipt_digest: string;
}>;

export function buildCurrentR4Receipt(graphHandle: GraphHandle, p4Ref: ExactRef,
  evidenceRefs: CurrentR4Receipt["evidence"]): CurrentR4Receipt {
  const unsigned = { schema_version: "evf.financial-settlement-r4-terminal-receipt/v2" as const,
    receipt_id: "evf.l1.financial-settlement.r4.receipt.v2" as const,
    unit_id: "SWU-GCP-003-R4" as const, status: "pass" as const,
    graph_handle: graphHandle, p4_terminal_receipt_ref: p4Ref, evidence: evidenceRefs,
    acceptance_vector: { obligations: 1 as const, bindings: 1 as const, p4_prerequisite_replayed: 1 as const,
      eligible_execution_cases: 5 as const, mutants_required: 15 as const, mutants_killed: 15 as const,
      targets: 19 as const, target_denominator_scope: "selected-nonrecursive-inputs" as const,
      tests_passed: 6 as const, writes_observed: 0 as const, events_observed: 0 as const },
    claim_ceiling: CLAIM_CEILING as typeof CLAIM_CEILING, authority_effect: "none" as const,
    release_admission: "not-granted" as const };
  return { ...unsigned, receipt_digest: digestValue(unsigned) };
}

function assertReceiptDigest<T extends { receipt_digest: string }>(receipt: T): void {
  const { receipt_digest, ...unsigned } = receipt;
  if (receipt_digest !== digestValue(unsigned)) fail("RECEIPT_TAMPERED", "receipt", "R4 receipt digest differs");
}

function assertOutputSet(repoRoot: string): void {
  if (canonicalJson(readdirSync(resolve(repoRoot, R4_CURRENT_ATTEMPT)).sort()) !==
      canonicalJson([...OUTPUT_FILES].sort()))
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "R4 current output set differs");
}

export async function runCurrentR4Verification(repoRoot = repositoryRoot()): Promise<{
  readonly status: "pass"; readonly receipt_ref: ExactRef;
  readonly graph_handle_digest: string; readonly mutation_count: 15;
}> {
  selectedSchemas(repoRoot);
  const binding = loadCurrentR4Binding(repoRoot);
  const contract = selectedContract(repoRoot);
  const targets = targetInventory(repoRoot, contract);
  assertCurrentR4TargetInventory(targets, contract);
  await replayStoredCurrentP4Receipt(repoRoot, binding.p4_terminal_receipt_ref);
  const p4 = readJson<CurrentP4Receipt>(repoRoot, binding.p4_terminal_receipt_ref.path);
  const derived = deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION });
  if (canonicalJson(derived.graph_handle) !== canonicalJson(p4.graph_handle) ||
      canonicalJson(derived.graph_handle.graph_ref) !== canonicalJson(binding.graph_ref) ||
      canonicalJson(derived.graph_handle.source_manifest_ref) !== canonicalJson(binding.source_manifest_ref))
    fail("SOURCE_GRAPH_DIGEST_STALE", "binding", "R4 and replayed P4 graph handles differ");
  const fixture = selectedFixture(repoRoot, binding);
  const execution = observeDecision(repoRoot, fixture, derived.O_spec, await loadStandaloneR4Decision(repoRoot));
  validateCurrentR4Decision(execution);
  const mutations = negativeControls(repoRoot, fixture, derived.O_spec, binding, contract, targets);
  const tests = await runSelectedTests(repoRoot);
  const derivationRef = writeStableJson(repoRoot, evidence("derived-obligation.json"), {
    schema_version: "evf.financial-settlement-r4-derived-obligation/v2", unit_id: "SWU-GCP-003-R4",
    graph_handle: derived.graph_handle, O_spec: derived.O_spec, O_gen: derived.O_gen,
    comparison: derived.comparison, authority_effect: "none" });
  const executionRef = writeStableJson(repoRoot, evidence("observed-decision.json"), execution);
  const mutationRef = writeStableJson(repoRoot, evidence("mutation-report.json"), {
    schema_version: "evf.financial-settlement-r4-mutation-report/v2", unit_id: "SWU-GCP-003-R4",
    required: 15, killed: mutations.length, results: mutations, status: "pass",
    authority_effect: "none", claim_ceiling: CLAIM_CEILING });
  const testRef = writeStableJson(repoRoot, evidence("test-process-result.json"), tests);
  const validationRef = writeStableJson(repoRoot, evidence("validation-result.json"), {
    schema_version: "evf.financial-settlement-r4-validation-result/v2", unit_id: "SWU-GCP-003-R4",
    status: "pass", selected_binding_ref: BINDING_REF, p4_terminal_receipt_ref: binding.p4_terminal_receipt_ref,
    graph_handle_digest: derived.graph_handle.handle_digest, decisions: 5,
    required_mutants: 15, killed_mutants: 15, passed_tests: 6,
    target_denominator_scope: "selected-nonrecursive-inputs", target_inventory: targets, validation_contract_ref: VALIDATION_REF,
    test_result_ref: testRef, output_files: OUTPUT_FILES,
    authority_effect: "none", claim_ceiling: CLAIM_CEILING });
  const receipt = buildCurrentR4Receipt(derived.graph_handle, binding.p4_terminal_receipt_ref, {
    binding_ref: BINDING_REF, validation_contract_ref: VALIDATION_REF,
    derivation_ref: derivationRef, execution_ref: executionRef,
    mutation_report_ref: mutationRef, test_result_ref: testRef, validation_result_ref: validationRef });
  await verifyCurrentR4Receipt(repoRoot, receipt);
  const receiptRef = writeStableJson(repoRoot, evidence("terminal-receipt.json"), receipt);
  schemaValidate(repoRoot, RECEIPT_SCHEMA, receiptRef.path);
  assertOutputSet(repoRoot);
  return { status: "pass", receipt_ref: receiptRef,
    graph_handle_digest: derived.graph_handle.handle_digest, mutation_count: 15 };
}

export async function verifyCurrentR4Receipt(repoRoot: string, receipt: CurrentR4Receipt): Promise<void> {
  selectedSchemas(repoRoot);
  assertReceiptDigest(receipt);
  if (receipt.schema_version !== "evf.financial-settlement-r4-terminal-receipt/v2" ||
      receipt.receipt_id !== "evf.l1.financial-settlement.r4.receipt.v2" ||
      receipt.unit_id !== "SWU-GCP-003-R4" || receipt.status !== "pass" ||
      receipt.authority_effect !== "none" || receipt.release_admission !== "not-granted" ||
      receipt.claim_ceiling !== CLAIM_CEILING ||
      canonicalJson(receipt.acceptance_vector) !== canonicalJson({ obligations: 1, bindings: 1,
        p4_prerequisite_replayed: 1, eligible_execution_cases: 5, mutants_required: 15,
        mutants_killed: 15, targets: 19, target_denominator_scope: "selected-nonrecursive-inputs",
        tests_passed: 6, writes_observed: 0, events_observed: 0 }))
    fail("RECEIPT_TAMPERED", "receipt", "R4 receipt identity or acceptance differs");
  const roles = ["binding_ref", "validation_contract_ref", "derivation_ref", "execution_ref",
    "mutation_report_ref", "test_result_ref", "validation_result_ref"] as const;
  if (canonicalJson(Object.keys(receipt.evidence).sort()) !== canonicalJson([...roles].sort()))
    fail("RECEIPT_TAMPERED", "receipt", "R4 receipt evidence roles differ");
  const paths = [R4_CURRENT_BINDING, R4_CURRENT_VALIDATION, evidence("derived-obligation.json"),
    evidence("observed-decision.json"), evidence("mutation-report.json"),
    evidence("test-process-result.json"), evidence("validation-result.json")];
  for (const [index, role] of roles.entries()) sameRef(repoRoot, receipt.evidence[role], paths[index]!, "RECEIPT_TAMPERED");
  const binding = loadCurrentR4Binding(repoRoot);
  const contract = selectedContract(repoRoot);
  const targets = targetInventory(repoRoot, contract);
  sameRef(repoRoot, receipt.p4_terminal_receipt_ref, P4_RECEIPT, "RECEIPT_TAMPERED");
  if (canonicalJson(receipt.p4_terminal_receipt_ref) !== canonicalJson(binding.p4_terminal_receipt_ref))
    fail("RECEIPT_TAMPERED", "receipt", "R4 receipt P4 prerequisite differs from binding");
  await replayStoredCurrentP4Receipt(repoRoot, receipt.p4_terminal_receipt_ref);
  const p4 = readJson<CurrentP4Receipt>(repoRoot, receipt.p4_terminal_receipt_ref.path);
  const derived = deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION });
  if (canonicalJson(receipt.graph_handle) !== canonicalJson(derived.graph_handle) ||
      canonicalJson(receipt.graph_handle) !== canonicalJson(p4.graph_handle))
    fail("SOURCE_GRAPH_DIGEST_STALE", "receipt", "R4/P4 full graph handle differs on replay");
  const expectedDerivation = { schema_version: "evf.financial-settlement-r4-derived-obligation/v2",
    unit_id: "SWU-GCP-003-R4", graph_handle: derived.graph_handle, O_spec: derived.O_spec,
    O_gen: derived.O_gen, comparison: derived.comparison, authority_effect: "none" };
  if (canonicalJson(readJson(repoRoot, receipt.evidence.derivation_ref.path)) !== canonicalJson(expectedDerivation))
    fail("RECEIPT_TAMPERED", "receipt", "R4 stored derivation differs from current exact derivation");
  const fixture = selectedFixture(repoRoot, binding);
  const expectedExecution = observeDecision(repoRoot, fixture, derived.O_spec, await loadStandaloneR4Decision(repoRoot));
  validateCurrentR4Decision(expectedExecution);
  if (canonicalJson(readJson(repoRoot, receipt.evidence.execution_ref.path)) !== canonicalJson(expectedExecution))
    fail("OBSERVATION_TAMPERED", "receipt", "R4 decision replay differs from stored execution");
  const expectedMutations = negativeControls(repoRoot, fixture, derived.O_spec, binding, contract, targets);
  const storedMutations = readJson(repoRoot, receipt.evidence.mutation_report_ref.path);
  if (canonicalJson(storedMutations) !== canonicalJson({ schema_version: "evf.financial-settlement-r4-mutation-report/v2",
    unit_id: "SWU-GCP-003-R4", required: 15, killed: 15, results: expectedMutations,
    status: "pass", authority_effect: "none", claim_ceiling: CLAIM_CEILING }))
    fail("RECEIPT_TAMPERED", "receipt", "R4 executed negative controls differ on replay");
  const testResult = await runSelectedTests(repoRoot);
  if (canonicalJson(readJson(repoRoot, receipt.evidence.test_result_ref.path)) !== canonicalJson(testResult))
    fail("RECEIPT_TAMPERED", "receipt", "R4 selected test process differs on replay");
  const expectedValidation = { schema_version: "evf.financial-settlement-r4-validation-result/v2",
    unit_id: "SWU-GCP-003-R4", status: "pass", selected_binding_ref: BINDING_REF,
    p4_terminal_receipt_ref: binding.p4_terminal_receipt_ref,
    graph_handle_digest: derived.graph_handle.handle_digest, decisions: 5,
    required_mutants: 15, killed_mutants: 15, passed_tests: 6,
    target_denominator_scope: "selected-nonrecursive-inputs", target_inventory: targets,
    validation_contract_ref: VALIDATION_REF, test_result_ref: receipt.evidence.test_result_ref,
    output_files: OUTPUT_FILES, authority_effect: "none", claim_ceiling: CLAIM_CEILING };
  if (canonicalJson(readJson(repoRoot, receipt.evidence.validation_result_ref.path)) !== canonicalJson(expectedValidation))
    fail("RECEIPT_TAMPERED", "receipt", "R4 current validation result differs on replay");
}

export async function replayStoredCurrentR4Receipt(repoRoot: string, receiptRef: ExactRef): Promise<void> {
  sameRef(repoRoot, receiptRef, evidence("terminal-receipt.json"), "RECEIPT_TAMPERED");
  assertOutputSet(repoRoot);
  schemaValidate(repoRoot, RECEIPT_SCHEMA, receiptRef.path);
  await verifyCurrentR4Receipt(repoRoot, readJson<CurrentR4Receipt>(repoRoot, receiptRef.path));
}

const invokedDirectly = process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) runCurrentR4Verification().then(
  result => process.stdout.write(`${JSON.stringify(result)}\n`),
  error => { process.stderr.write(`${JSON.stringify({ status: "blocked-or-failed",
    code: error instanceof L1Error ? error.code : "TARGET_BASELINE_DRIFT",
    message: error instanceof Error ? error.message : String(error) })}\n`); process.exitCode = 1; },
);
