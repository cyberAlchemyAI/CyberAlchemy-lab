import { execFile, spawnSync } from "node:child_process";
import { readdirSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { promisify } from "node:util";

import { deriveUnit, L1_CURRENT_PROJECTION, L1_PATHS, loadFinancialSettlementGraph } from "./derive.js";
import { assertExactRef, canonicalJson, digestValue, exactRef, readJson, repositoryRoot, writeStableJson } from "./exact-ref.js";
import type { StandalonePayout, StandalonePayoutPorts, StandalonePayoutPrestate } from "./standalone-payout-effects.js";
import { loadStandaloneP4Executor, P4_STANDALONE_CONTRACT, P4_STANDALONE_SOURCE, type StandaloneP4Executor } from "./standalone-p4-runtime.js";
import { fail, L1Error, P4_IDENTITY, type ExactRef, type GraphHandle, type L1ErrorCode } from "./types.js";

export const P4_CURRENT_BINDING =
  "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4/financial-settlement-p4-binding.v2.json";
export const P4_CURRENT_PRESTATE =
  "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4/financial-settlement-p4-prestate.v2.json";
export const P4_CURRENT_ATTEMPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-002-P4/attempt-006";
export const P4_CURRENT_VALIDATION =
  "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/financial-settlement-p4-current-validation.v2.json";
const VALIDATION_REF: ExactRef = {
  path: P4_CURRENT_VALIDATION,
  sha256: "c8eb47c9703cb2c6021c30201860c5e321554480a9e71cf99f75bb8b6077a1c4",
  size_bytes: 4403,
};
const RECEIPT_SCHEMA =
  "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-p4-terminal-receipt.v2.schema.json";
const RECEIPT_SCHEMA_REF: ExactRef = {
  path: RECEIPT_SCHEMA,
  sha256: "e6e70aaea96918c9e80ff71e2f4bf31587fb483f49efed9740bae9e30f3c14a0",
  size_bytes: 2640,
};
const BINDING_REF: ExactRef = {
  path: P4_CURRENT_BINDING,
  sha256: "77a377b6d14a0b6a60a43d6c375764a6fbc8be2c0e86e2c382017b27c4411eb1",
  size_bytes: 2788,
};
const CLAIM_CEILING = "candidate-local-p4-observed-rule-slice-not-application-equivalence";
const evidence = (name: string) => `${P4_CURRENT_ATTEMPT}/${name}`;
const OUTPUT_FILES = ["derived-obligation.json", "observed-execution.json", "mutation-report.json",
  "test-process-result.json", "validation-result.json", "terminal-receipt.json"] as const;
const P4_TEST_FILES = [
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-payout-effects.test.ts",
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/current-projection.test.ts",
] as const;

function schemaValidate(repoRoot: string, schemaPath: string, documentPath: string): void {
  const script = "import json,sys; from jsonschema import Draft202012Validator; " +
    "s=json.load(open(sys.argv[1])); d=json.load(open(sys.argv[2])); " +
    "Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(d)";
  const run = spawnSync("python3", ["-c", script, resolve(repoRoot, schemaPath), resolve(repoRoot, documentPath)],
    { cwd: repoRoot, encoding: "utf8", timeout: 30_000, maxBuffer: 1024 * 1024 });
  if (run.error || run.status !== 0) {
    fail("TARGET_BASELINE_DRIFT", "admission", `schema validation failed for ${documentPath}: ${run.stderr || run.error}`);
  }
}

function validateSelectedSchemas(repoRoot: string): void {
  assertExactRef(repoRoot, RECEIPT_SCHEMA_REF, "BINDING_DIGEST_STALE");
  const evf = "projects/domainspec-v2/development/evolvable-validation-framework";
  for (const [schema, document] of [
    [`${evf}/contracts/financial-settlement-p4-runtime.v2.schema.json`, P4_STANDALONE_CONTRACT],
    [`${evf}/fixtures/SWU-GCP-002-P4/financial-settlement-p4-prestate.v2.schema.json`, P4_CURRENT_PRESTATE],
    [`${evf}/fixtures/SWU-GCP-002-P4/financial-settlement-p4-binding.v2.schema.json`, P4_CURRENT_BINDING],
    [`${evf}/work-pack/financial-settlement-p4-current-validation.v2.schema.json`, P4_CURRENT_VALIDATION],
  ] as const) schemaValidate(repoRoot, schema, document);
}

type TestProcessResult = Readonly<{
  schema_version: "evf.financial-settlement-p4-test-process/v2";
  runner: "vitest";
  selected_test_refs: readonly ExactRef[];
  total: 10;
  passed: 10;
  failed: 0;
  pending: 0;
  todo: 0;
  assertions: readonly Readonly<{ name: string; status: "passed" }>[];
  status: "pass";
  authority_effect: "none";
  claim_ceiling: typeof CLAIM_CEILING;
}>;

async function runSelectedTestProcess(repoRoot: string): Promise<TestProcessResult> {
  const packageRoot = resolve(repoRoot, "projects/domainspec-v2/impl/test-derivation-engine");
  const selected = ["src/minted-project/l1/standalone-payout-effects.test.ts",
    "src/minted-project/l1/current-projection.test.ts"];
  let stdout: string;
  try {
    ({ stdout } = await promisify(execFile)("pnpm", ["exec", "vitest", "run", ...selected, "--reporter=json"],
      { cwd: packageRoot, encoding: "utf8", timeout: 120_000, maxBuffer: 4 * 1024 * 1024 }));
  } catch (error) {
    fail("TARGET_BASELINE_DRIFT", "execution", `selected P4 test process failed: ${error instanceof Error ? error.message : String(error)}`);
  }
  let report: Record<string, unknown>;
  try { report = JSON.parse(stdout) as Record<string, unknown>; }
  catch { fail("TARGET_BASELINE_DRIFT", "execution", "selected P4 test process returned non-JSON output"); }
  if (report.success !== true || report.numTotalTests !== 10 || report.numPassedTests !== 10 ||
      report.numFailedTests !== 0 || report.numPendingTests !== 0 || report.numTodoTests !== 0 ||
      !Array.isArray(report.testResults) || report.testResults.length !== 2) {
    fail("TARGET_BASELINE_DRIFT", "execution", "selected P4 test process denominator differs");
  }
  const assertions = (report.testResults as { name: string; status: string;
    assertionResults: readonly { fullName: string; status: string }[] }[])
    .flatMap(item => item.assertionResults.map(assertion => ({ name: assertion.fullName, status: assertion.status })));
  if (assertions.length !== 10 || assertions.some(item => item.status !== "passed") ||
      new Set(assertions.map(item => item.name)).size !== 10) {
    fail("TARGET_BASELINE_DRIFT", "execution", "selected P4 assertions are missing or duplicated");
  }
  const testPaths = (report.testResults as { name: string }[]).map(item => item.name);
  if (canonicalJson(testPaths.sort()) !== canonicalJson(P4_TEST_FILES.map(path => resolve(repoRoot, path)).sort())) {
    fail("TARGET_BASELINE_DRIFT", "execution", "selected P4 test files differ");
  }
  return {
    schema_version: "evf.financial-settlement-p4-test-process/v2", runner: "vitest",
    selected_test_refs: P4_TEST_FILES.map(path => exactRef(repoRoot, path)),
    total: 10, passed: 10, failed: 0, pending: 0, todo: 0,
    assertions: assertions.sort((left, right) => left.name.localeCompare(right.name)) as TestProcessResult["assertions"],
    status: "pass", authority_effect: "none", claim_ceiling: CLAIM_CEILING,
  };
}

function assertOutputSet(repoRoot: string): void {
  const actual = readdirSync(resolve(repoRoot, P4_CURRENT_ATTEMPT)).sort();
  if (canonicalJson(actual) !== canonicalJson([...OUTPUT_FILES].sort())) {
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "P4 current output file set differs");
  }
}

type Binding = Readonly<{
  schema_version: string;
  binding_id: string;
  unit_id: string;
  obligation_id: string;
  rule_id: string;
  edge_id: string;
  target_id: string;
  semantic_ref: ExactRef;
  obligation_spec_ref: ExactRef;
  runtime_contract_ref: ExactRef;
  runtime_source_ref: ExactRef;
  runtime_loader_ref: ExactRef;
  prestate_ref: ExactRef;
  fixture_ref: ExactRef;
  graph_ref: ExactRef;
  source_manifest_ref: ExactRef;
  authority_effect: string;
  release_admission: string;
  claim_ceiling: string;
}>;
type Prestate = Readonly<{
  schema_version: string;
  prestate_id: string;
  selection_kind: string;
  origin_fixture_ref: ExactRef;
  total_payout: number;
  existing_payout_count_for_end_date: number;
  end_date: string;
  expected_effect_values_forbidden: boolean;
  authority_effect: string;
  release_admission: string;
  claim_ceiling: string;
}>;
type Fixture = Readonly<{
  expected_values_forbidden: boolean;
  inputs: Readonly<{
    existing_transactions: readonly Readonly<{ type: string; date: string }>[];
    request: Readonly<{ end_date: string }>;
  }>;
}>;
type ValidationContract = Readonly<{
  schema_version: string;
  contract_id: string;
  unit_id: string;
  target_inventory: readonly Readonly<{ id: string; path: string }>[];
  required_mutants: readonly Readonly<{ id: string; code: L1ErrorCode }>[];
  authority_effect: string;
  release_admission: string;
  claim_ceiling: string;
}>;
export type ObservedEffect = Readonly<{
  sequence: number;
  kind: "write" | "event";
  name: "PAYOUT" | "PayoutCreated";
  amount: number;
  date: string;
}>;
export type CurrentP4Execution = Readonly<{
  schema_version: "evf.financial-settlement-p4-observed-execution/v2";
  execution_id: "evf.l1.financial-settlement.p4.execution.v2";
  prestate_ref: ExactRef;
  antecedent: StandalonePayoutPrestate;
  post: Readonly<{ payout_write_count: number; payout_event_count: number }>;
  effects: readonly ObservedEffect[];
  status: "pass";
  claim_ceiling: typeof CLAIM_CEILING;
  authority_effect: "none";
}>;
type Observed = Readonly<{
  effects: readonly ObservedEffect[];
  writes: readonly StandalonePayout[];
  events: readonly StandalonePayout[];
}>;

function sameRef(repoRoot: string, actual: ExactRef, expectedPath: string, code: L1ErrorCode): void {
  const expected = exactRef(repoRoot, expectedPath);
  if (canonicalJson(actual) !== canonicalJson(expected)) {
    fail(code, "binding", `selected exact ref differs: ${expectedPath}`);
  }
  assertExactRef(repoRoot, actual, code);
}

function selectedValidationContract(repoRoot: string): ValidationContract {
  assertExactRef(repoRoot, VALIDATION_REF, "BINDING_DIGEST_STALE");
  const contract = readJson<ValidationContract>(repoRoot, P4_CURRENT_VALIDATION);
  if (contract.schema_version !== "evf.financial-settlement-p4-current-validation/v2" ||
      contract.contract_id !== "evf.l1.financial-settlement.p4.current-validation.v2" ||
      contract.unit_id !== "SWU-GCP-002-P4" || contract.authority_effect !== "none" ||
      contract.release_admission !== "not-granted" || contract.claim_ceiling !== CLAIM_CEILING ||
      contract.target_inventory.length !== 18 || contract.required_mutants.length !== 16 ||
      new Set(contract.target_inventory.map(item => item.id)).size !== 18 ||
      new Set(contract.target_inventory.map(item => item.path)).size !== 18) {
    fail("VERIFIER_TARGET_OMITTED", "admission", "P4 current validation contract denominator differs");
  }
  return contract;
}

function exactTargetInventory(repoRoot: string, contract: ValidationContract): readonly Readonly<{ id: string; ref: ExactRef }>[] {
  return contract.target_inventory.map(item => ({ id: item.id, ref: exactRef(repoRoot, item.path) }));
}

export function assertCurrentP4TargetInventory(
  actual: readonly Readonly<{ id: string; ref: ExactRef }>[],
  contract: ValidationContract,
): void {
  if (actual.length !== contract.target_inventory.length ||
      actual.some((item, index) => item.id !== contract.target_inventory[index]?.id ||
        item.ref.path !== contract.target_inventory[index]?.path)) {
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "P4 current target inventory differs");
  }
}

export function loadCurrentP4Binding(repoRoot: string, ref: ExactRef = BINDING_REF): Binding {
  if (canonicalJson(ref) !== canonicalJson(BINDING_REF)) {
    fail("BINDING_DIGEST_STALE", "binding", "P4 v2 binding selection changed");
  }
  assertExactRef(repoRoot, ref, "BINDING_DIGEST_STALE");
  const binding = readJson<Binding>(repoRoot, ref.path);
  if (binding.schema_version !== "evf.financial-settlement-p4-binding/v2" ||
      binding.binding_id !== "evf.l1.financial-settlement.p4.binding.v2" ||
      binding.unit_id !== "SWU-GCP-002-P4" ||
      binding.obligation_id !== P4_IDENTITY.obligation_id ||
      binding.rule_id !== P4_IDENTITY.rule_id || binding.edge_id !== P4_IDENTITY.edge_id ||
      binding.target_id !== "financial-settlement.GenerateSettlement" ||
      binding.authority_effect !== "none" || binding.release_admission !== "not-granted" ||
      binding.claim_ceiling !== CLAIM_CEILING) {
    fail("BINDING_DIGEST_STALE", "binding", "P4 v2 binding identity or claim ceiling changed");
  }
  const selected = [
    [binding.semantic_ref, L1_PATHS.p4Semantic, "PREDICATE_DIGEST_STALE"],
    [binding.obligation_spec_ref, L1_PATHS.p4Obligation, "BINDING_DIGEST_STALE"],
    [binding.runtime_contract_ref, P4_STANDALONE_CONTRACT, "BINDING_DIGEST_STALE"],
    [binding.runtime_source_ref, P4_STANDALONE_SOURCE, "BINDING_DIGEST_STALE"],
    [binding.runtime_loader_ref, "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l1/standalone-p4-runtime.ts", "BINDING_DIGEST_STALE"],
    [binding.prestate_ref, P4_CURRENT_PRESTATE, "FIXTURE_DIGEST_STALE"],
    [binding.fixture_ref, L1_PATHS.p4Fixture, "FIXTURE_DIGEST_STALE"],
    [binding.graph_ref, L1_CURRENT_PROJECTION.graph, "SOURCE_GRAPH_DIGEST_STALE"],
    [binding.source_manifest_ref, L1_CURRENT_PROJECTION.sourceManifest, "SOURCE_GRAPH_DIGEST_STALE"],
  ] as const;
  for (const [actual, path, code] of selected) sameRef(repoRoot, actual, path, code);
  return binding;
}

function selectedPrestate(repoRoot: string, binding: Binding): StandalonePayoutPrestate {
  const source = readJson<Prestate>(repoRoot, binding.prestate_ref.path);
  const fixture = readJson<Fixture>(repoRoot, binding.fixture_ref.path);
  if (source.schema_version !== "evf.financial-settlement-p4-rule-prestate/v2" ||
      source.prestate_id !== "evf.l1.financial-settlement.p4.rule-prestate.v2" ||
      source.selection_kind !== "candidate-explicit-rule-prestate-not-application-calculation" ||
      source.expected_effect_values_forbidden !== true || source.authority_effect !== "none" ||
      source.release_admission !== "not-granted" ||
      source.claim_ceiling !== "selected-rule-prestate-only-not-settlement-calculation" ||
      canonicalJson(source.origin_fixture_ref) !== canonicalJson(binding.fixture_ref) ||
      fixture.expected_values_forbidden !== true ||
      source.end_date !== fixture.inputs.request.end_date ||
      source.existing_payout_count_for_end_date !== fixture.inputs.existing_transactions.filter(
        item => item.type === "PAYOUT" && item.date === source.end_date).length ||
      !Number.isSafeInteger(source.total_payout) || source.total_payout <= 0) {
    fail("FIXTURE_DIGEST_STALE", "binding", "P4 selected rule prestate or fixture join is invalid");
  }
  return { totalPayout: source.total_payout,
    existingPayoutCountForEndDate: source.existing_payout_count_for_end_date,
    endDate: source.end_date };
}

export async function observeCurrentP4(
  executor: StandaloneP4Executor,
  prestate: StandalonePayoutPrestate,
): Promise<Observed> {
  const effects: ObservedEffect[] = [];
  const writes: StandalonePayout[] = [];
  const events: StandalonePayout[] = [];
  const ports: StandalonePayoutPorts = {
    async writePayout(payout) {
      const copy = { ...payout };
      writes.push(copy);
      effects.push({ sequence: effects.length, kind: "write", name: "PAYOUT", amount: copy.amount, date: copy.date });
    },
    async emitPayoutCreated(payout) {
      const copy = { ...payout };
      events.push(copy);
      effects.push({ sequence: effects.length, kind: "event", name: "PayoutCreated", amount: copy.amount, date: copy.date });
    },
  };
  await executor(prestate, ports);
  return { effects, writes, events };
}

export function validateCurrentP4Observation(observed: Observed, prestate: StandalonePayoutPrestate): void {
  const writes = observed.effects.filter(effect => effect.kind === "write");
  const events = observed.effects.filter(effect => effect.kind === "event");
  if (writes.length === 0) fail("P4_WRITE_MISSING", "execution", "P4 write not observed");
  if (events.length === 0) fail("P4_EVENT_MISSING", "execution", "P4 event not observed");
  if (writes.length !== 1 || events.length !== 1 || observed.effects.length !== 2 ||
      observed.writes.length !== 1 || observed.events.length !== 1) {
    fail("P4_EFFECT_CARDINALITY_MISMATCH", "execution", "P4 observed cardinality differs");
  }
  const write = writes[0]!;
  const event = events[0]!;
  if (observed.effects[0] !== write || observed.effects[1] !== event ||
      write.sequence !== 0 || event.sequence !== 1 ||
      write.name !== "PAYOUT" || event.name !== "PayoutCreated") {
    fail("P4_EFFECT_ORDER_MISMATCH", "execution", "P4 write and event were not called in order");
  }
  if (write.amount !== prestate.totalPayout) fail("P4_WRITE_AMOUNT_MISMATCH", "execution", "P4 write amount differs");
  if (event.amount !== prestate.totalPayout) fail("P4_EVENT_AMOUNT_MISMATCH", "execution", "P4 event amount differs");
  if (write.date !== prestate.endDate) fail("P4_WRITE_DATE_MISMATCH", "execution", "P4 write date differs");
  if (event.date !== prestate.endDate) fail("P4_EVENT_DATE_MISMATCH", "execution", "P4 event date differs");
  if (observed.writes[0]!.amount !== write.amount || observed.writes[0]!.date !== write.date ||
      observed.events[0]!.amount !== event.amount || observed.events[0]!.date !== event.date) {
    fail("OBSERVATION_TAMPERED", "execution", "P4 port stores and invocation trace differ");
  }
}

function errorCode(action: () => unknown): L1ErrorCode | "NO_FAILURE" {
  try { action(); return "NO_FAILURE"; }
  catch (error) { if (error instanceof L1Error) return error.code; throw error; }
}

type MutationResult = Readonly<{ mutant_id: string; required_code: L1ErrorCode;
  observed_code: L1ErrorCode; status: "killed" }>;

async function runNegativeControls(
  repoRoot: string,
  prestate: StandalonePayoutPrestate,
  binding: Binding,
  validationContract: ValidationContract,
  targetInventory: readonly Readonly<{ id: string; ref: ExactRef }>[],
): Promise<readonly MutationResult[]> {
  const payout = { amount: prestate.totalPayout, date: prestate.endDate };
  const variants: readonly (readonly [string, L1ErrorCode, StandaloneP4Executor])[] = [
    ["P4-M01-missing-write", "P4_WRITE_MISSING", async (_pre, ports) => { await ports.emitPayoutCreated(payout); }],
    ["P4-M02-missing-event", "P4_EVENT_MISSING", async (_pre, ports) => { await ports.writePayout(payout); }],
    ["P4-M03-wrong-write-amount", "P4_WRITE_AMOUNT_MISMATCH", async (_pre, ports) => { await ports.writePayout({ ...payout, amount: payout.amount + 1 }); await ports.emitPayoutCreated(payout); }],
    ["P4-M04-wrong-event-amount", "P4_EVENT_AMOUNT_MISMATCH", async (_pre, ports) => { await ports.writePayout(payout); await ports.emitPayoutCreated({ ...payout, amount: payout.amount + 1 }); }],
    ["P4-M05-wrong-write-date", "P4_WRITE_DATE_MISMATCH", async (_pre, ports) => { await ports.writePayout({ ...payout, date: "2099-12-30" }); await ports.emitPayoutCreated(payout); }],
    ["P4-M06-wrong-event-date", "P4_EVENT_DATE_MISMATCH", async (_pre, ports) => { await ports.writePayout(payout); await ports.emitPayoutCreated({ ...payout, date: "2099-12-31" }); }],
    ["P4-M07-event-before-write", "P4_EFFECT_ORDER_MISMATCH", async (_pre, ports) => { await ports.emitPayoutCreated(payout); await ports.writePayout(payout); }],
    ["P4-M08-extra-effect", "P4_EFFECT_CARDINALITY_MISMATCH", async (_pre, ports) => { await ports.writePayout(payout); await ports.emitPayoutCreated(payout); await ports.emitPayoutCreated(payout); }],
  ];
  const results: MutationResult[] = [];
  for (const [id, required, variant] of variants) {
    const negative = await observeCurrentP4(variant, prestate);
    const actual = errorCode(() => validateCurrentP4Observation(negative, prestate));
    if (actual !== required) fail(required, "mutation", `${id} produced ${actual}`);
    results.push({ mutant_id: id, required_code: required, observed_code: actual, status: "killed" });
  }
  const zero = "0".repeat(64);
  const graph = structuredClone(loadFinancialSettlementGraph(repoRoot, L1_CURRENT_PROJECTION));
  const edge = graph.edges.find(item => item.edge_id === P4_IDENTITY.edge_id) as { to: string } | undefined;
  if (!edge) fail("EDGE_ENDPOINT_MISMATCH", "derivation", "P4 selected graph edge is missing");
  edge.to = "financial-settlement.PayoutCreated";
  const baselineReceipt = buildCurrentP4Receipt({
    graphHandle: deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION }).graph_handle,
    evidence: { binding_ref: BINDING_REF, validation_contract_ref: VALIDATION_REF,
      derivation_ref: binding.semantic_ref, execution_ref: binding.runtime_source_ref,
      mutation_report_ref: binding.prestate_ref, test_result_ref: binding.fixture_ref,
      validation_result_ref: binding.graph_ref },
  });
  const checks: readonly (readonly [string, L1ErrorCode, () => unknown])[] = [
    ["P4-M09-edge-wrong-target", "EDGE_ENDPOINT_MISMATCH", () => deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION, graph })],
    ["P4-M10-signature-wrong", "RELATIONSHIP_SIGNATURE_MISMATCH", () => deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION, signature: { source_type: "Operation", target_type: "Rule", direction: "canonical", status: "active" } })],
    ["P4-M11-source-graph-digest-stale", "SOURCE_GRAPH_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.graph_ref, sha256: zero }, "SOURCE_GRAPH_DIGEST_STALE")],
    ["P4-M12-predicate-digest-stale", "PREDICATE_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.semantic_ref, sha256: zero }, "PREDICATE_DIGEST_STALE")],
    ["P4-M13-binding-digest-stale", "BINDING_DIGEST_STALE", () => loadCurrentP4Binding(repoRoot, { ...BINDING_REF, sha256: zero })],
    ["P4-M14-fixture-digest-stale", "FIXTURE_DIGEST_STALE", () => assertExactRef(repoRoot, { ...binding.prestate_ref, sha256: zero }, "FIXTURE_DIGEST_STALE")],
    ["P4-M15-receipt-tamper", "RECEIPT_TAMPERED", () =>
      assertCurrentP4ReceiptDigest({ ...baselineReceipt,
        acceptance_vector: { ...baselineReceipt.acceptance_vector, events: 2 } })],
    ["P4-M16-verifier-target-omitted", "VERIFIER_TARGET_OMITTED", () => assertCurrentP4TargetInventory(targetInventory.slice(1), validationContract)],
  ];
  for (const [id, required, check] of checks) {
    const actual = errorCode(check);
    if (actual !== required) fail(required, "mutation", `${id} produced ${actual}`);
    results.push({ mutant_id: id, required_code: required, observed_code: actual, status: "killed" });
  }
  if (results.length !== 16 || results.some((item, index) =>
      item.mutant_id !== validationContract.required_mutants[index]?.id ||
      item.required_code !== validationContract.required_mutants[index]?.code)) {
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "P4 mutation denominator differs from selected validation contract");
  }
  return results;
}

export async function runCurrentP4Verification(repoRoot = repositoryRoot()): Promise<{
  readonly status: "pass";
  readonly receipt_ref: ExactRef;
  readonly graph_handle_digest: string;
  readonly mutation_count: 16;
}> {
  validateSelectedSchemas(repoRoot);
  const binding = loadCurrentP4Binding(repoRoot);
  const validationContract = selectedValidationContract(repoRoot);
  const targetInventory = exactTargetInventory(repoRoot, validationContract);
  assertCurrentP4TargetInventory(targetInventory, validationContract);
  const derivation = deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION });
  if (canonicalJson(derivation.graph_handle.graph_ref) !== canonicalJson(binding.graph_ref) ||
      canonicalJson(derivation.graph_handle.source_manifest_ref) !== canonicalJson(binding.source_manifest_ref)) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "binding", "P4 current graph handle differs from v2 binding");
  }
  const prestate = selectedPrestate(repoRoot, binding);
  const executor = await loadStandaloneP4Executor(repoRoot);
  const observed = await observeCurrentP4(executor, prestate);
  validateCurrentP4Observation(observed, prestate);
  const results = await runNegativeControls(repoRoot, prestate, binding, validationContract, targetInventory);
  const testProcess = await runSelectedTestProcess(repoRoot);

  const derivationRef = writeStableJson(repoRoot, evidence("derived-obligation.json"), {
    schema_version: "evf.financial-settlement-p4-derived-obligation/v2", unit_id: "SWU-GCP-002-P4",
    graph_handle: derivation.graph_handle, O_spec: derivation.O_spec, O_gen: derivation.O_gen,
    comparison: derivation.comparison, authority_effect: "none",
  });
  const executionRef = writeStableJson(repoRoot, evidence("observed-execution.json"), {
    schema_version: "evf.financial-settlement-p4-observed-execution/v2", execution_id: "evf.l1.financial-settlement.p4.execution.v2",
    prestate_ref: binding.prestate_ref, antecedent: prestate,
    post: { payout_write_count: observed.writes.length, payout_event_count: observed.events.length },
    effects: observed.effects, status: "pass", claim_ceiling: CLAIM_CEILING, authority_effect: "none",
  } satisfies CurrentP4Execution);
  const mutationRef = writeStableJson(repoRoot, evidence("mutation-report.json"), {
    schema_version: "evf.financial-settlement-p4-mutation-report/v2", unit_id: "SWU-GCP-002-P4",
    required: 16, killed: results.length, results, status: "pass", authority_effect: "none",
    claim_ceiling: CLAIM_CEILING as typeof CLAIM_CEILING,
  });
  const testResultRef = writeStableJson(repoRoot, evidence("test-process-result.json"), testProcess);
  const validationRef = writeStableJson(repoRoot, evidence("validation-result.json"), {
    schema_version: "evf.financial-settlement-p4-validation-result/v2", unit_id: "SWU-GCP-002-P4",
    status: "pass", selected_binding_ref: BINDING_REF, graph_handle_digest: derivation.graph_handle.handle_digest,
    observed_port_calls: 2, required_mutants: 16, killed_mutants: 16, passed_tests: 10,
    target_inventory: targetInventory, validation_contract_ref: VALIDATION_REF,
    test_result_ref: testResultRef, output_files: OUTPUT_FILES,
    authority_effect: "none", claim_ceiling: CLAIM_CEILING,
  });
  const receipt = buildCurrentP4Receipt({ graphHandle: derivation.graph_handle,
    evidence: { binding_ref: BINDING_REF, validation_contract_ref: VALIDATION_REF,
      derivation_ref: derivationRef, execution_ref: executionRef,
      mutation_report_ref: mutationRef, test_result_ref: testResultRef,
      validation_result_ref: validationRef } });
  const tamperCode = errorCode(() => assertCurrentP4ReceiptDigest({ ...receipt,
    acceptance_vector: { ...receipt.acceptance_vector, events: 2 } }));
  if (tamperCode !== "RECEIPT_TAMPERED") {
    fail("RECEIPT_TAMPERED", "mutation", "P4 full receipt tamper was not rejected");
  }
  await verifyCurrentP4Receipt(repoRoot, receipt);
  const receiptRef = writeStableJson(repoRoot, evidence("terminal-receipt.json"), receipt);
  schemaValidate(repoRoot, RECEIPT_SCHEMA, receiptRef.path);
  assertOutputSet(repoRoot);
  return { status: "pass", receipt_ref: receiptRef,
    graph_handle_digest: derivation.graph_handle.handle_digest, mutation_count: 16 };
}

export type CurrentP4Receipt = Readonly<{
  schema_version: "evf.financial-settlement-p4-terminal-receipt/v2";
  receipt_id: "evf.l1.financial-settlement.p4.receipt.v2";
  unit_id: "SWU-GCP-002-P4";
  status: "pass";
  graph_handle: GraphHandle;
  evidence: Readonly<{ binding_ref: ExactRef; validation_contract_ref: ExactRef;
    derivation_ref: ExactRef; execution_ref: ExactRef;
    mutation_report_ref: ExactRef; test_result_ref: ExactRef; validation_result_ref: ExactRef }>;
  acceptance_vector: Readonly<{ obligations: 1; bindings: 1; eligible_execution_cases: 1;
    writes: 1; events: 1; mutants_required: 16; mutants_killed: 16; targets: 18; tests_passed: 10 }>;
  claim_ceiling: typeof CLAIM_CEILING;
  authority_effect: "none";
  release_admission: "not-granted";
  receipt_digest: string;
}>;

function assertCurrentP4ReceiptDigest<T extends { receipt_digest: string }>(receipt: T): void {
  const { receipt_digest, ...unsigned } = receipt;
  if (receipt_digest !== digestValue(unsigned)) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current receipt digest differs");
  }
}

export function buildCurrentP4Receipt(input: {
  graphHandle: GraphHandle;
  evidence: CurrentP4Receipt["evidence"];
}): CurrentP4Receipt {
  const unsigned = {
    schema_version: "evf.financial-settlement-p4-terminal-receipt/v2" as const,
    receipt_id: "evf.l1.financial-settlement.p4.receipt.v2" as const,
    unit_id: "SWU-GCP-002-P4" as const,
    status: "pass" as const,
    graph_handle: input.graphHandle,
    evidence: input.evidence,
    acceptance_vector: { obligations: 1 as const, bindings: 1 as const,
      eligible_execution_cases: 1 as const, writes: 1 as const, events: 1 as const,
      mutants_required: 16 as const, mutants_killed: 16 as const, targets: 18 as const,
      tests_passed: 10 as const },
    claim_ceiling: CLAIM_CEILING as typeof CLAIM_CEILING,
    authority_effect: "none" as const,
    release_admission: "not-granted" as const,
  };
  return { ...unsigned, receipt_digest: digestValue(unsigned) };
}

export async function verifyCurrentP4Receipt(repoRoot: string, receipt: CurrentP4Receipt): Promise<void> {
  validateSelectedSchemas(repoRoot);
  assertCurrentP4ReceiptDigest(receipt);
  if (receipt.schema_version !== "evf.financial-settlement-p4-terminal-receipt/v2" ||
      receipt.receipt_id !== "evf.l1.financial-settlement.p4.receipt.v2" ||
      receipt.unit_id !== "SWU-GCP-002-P4" || receipt.status !== "pass" ||
      receipt.claim_ceiling !== CLAIM_CEILING || receipt.authority_effect !== "none" ||
      receipt.release_admission !== "not-granted" ||
      canonicalJson(receipt.acceptance_vector) !== canonicalJson({ obligations: 1, bindings: 1,
        eligible_execution_cases: 1, writes: 1, events: 1, mutants_required: 16, mutants_killed: 16,
        targets: 18, tests_passed: 10 })) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current receipt identity or acceptance differs");
  }
  const roles = ["binding_ref", "validation_contract_ref", "derivation_ref", "execution_ref",
    "mutation_report_ref", "test_result_ref", "validation_result_ref"];
  if (canonicalJson(Object.keys(receipt.evidence).sort()) !== canonicalJson([...roles].sort())) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current receipt evidence roles differ");
  }
  const expectedPaths = [P4_CURRENT_BINDING, P4_CURRENT_VALIDATION,
    evidence("derived-obligation.json"), evidence("observed-execution.json"),
    evidence("mutation-report.json"), evidence("test-process-result.json"),
    evidence("validation-result.json")];
  for (const [index, role] of roles.entries()) {
    sameRef(repoRoot, receipt.evidence[role as keyof CurrentP4Receipt["evidence"]], expectedPaths[index]!, "RECEIPT_TAMPERED");
  }
  const derived = deriveUnit(repoRoot, "P4", { projection: L1_CURRENT_PROJECTION });
  if (canonicalJson(receipt.graph_handle) !== canonicalJson(derived.graph_handle)) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "receipt", "P4 current graph handle changed");
  }
  const storedDerivation = readJson<Record<string, unknown>>(repoRoot, receipt.evidence.derivation_ref.path);
  const expectedDerivation = {
    schema_version: "evf.financial-settlement-p4-derived-obligation/v2", unit_id: "SWU-GCP-002-P4",
    graph_handle: derived.graph_handle, O_spec: derived.O_spec, O_gen: derived.O_gen,
    comparison: derived.comparison, authority_effect: "none",
  };
  if (canonicalJson(storedDerivation) !== canonicalJson(expectedDerivation)) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 derived obligation differs from current exact derivation");
  }
  const execution = readJson<CurrentP4Execution>(repoRoot, receipt.evidence.execution_ref.path);
  const binding = loadCurrentP4Binding(repoRoot);
  const contract = selectedValidationContract(repoRoot);
  if (canonicalJson(execution.prestate_ref) !== canonicalJson(binding.prestate_ref) ||
      canonicalJson(execution.antecedent) !== canonicalJson(selectedPrestate(repoRoot, binding)) ||
      execution.status !== "pass" || execution.claim_ceiling !== CLAIM_CEILING || execution.authority_effect !== "none") {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current execution scope differs");
  }
  const observed: Observed = {
    effects: execution.effects,
    writes: execution.effects.filter(item => item.kind === "write").map(item => ({ amount: item.amount, date: item.date })),
    events: execution.effects.filter(item => item.kind === "event").map(item => ({ amount: item.amount, date: item.date })),
  };
  validateCurrentP4Observation(observed, execution.antecedent);
  const actual = await observeCurrentP4(await loadStandaloneP4Executor(repoRoot), execution.antecedent);
  validateCurrentP4Observation(actual, execution.antecedent);
  const expectedExecution: CurrentP4Execution = {
    schema_version: "evf.financial-settlement-p4-observed-execution/v2",
    execution_id: "evf.l1.financial-settlement.p4.execution.v2",
    prestate_ref: binding.prestate_ref, antecedent: selectedPrestate(repoRoot, binding),
    post: { payout_write_count: actual.writes.length, payout_event_count: actual.events.length },
    effects: actual.effects, status: "pass", claim_ceiling: CLAIM_CEILING, authority_effect: "none",
  };
  if (canonicalJson(execution) !== canonicalJson(expectedExecution)) {
    fail("OBSERVATION_TAMPERED", "receipt", "P4 selected runtime replay differs from stored observation");
  }
  const mutations = readJson<{ schema_version: string; unit_id: string; status: string; authority_effect: string;
    claim_ceiling: string; required: number; killed: number;
    results: readonly { mutant_id: string; required_code: string; observed_code: string; status: string }[] }>(repoRoot, receipt.evidence.mutation_report_ref.path);
  if (mutations.schema_version !== "evf.financial-settlement-p4-mutation-report/v2" ||
      mutations.unit_id !== "SWU-GCP-002-P4" || mutations.status !== "pass" ||
      mutations.authority_effect !== "none" || mutations.claim_ceiling !== CLAIM_CEILING ||
      mutations.required !== 16 || mutations.killed !== 16 || mutations.results.length !== 16 ||
      mutations.results.some((item, index) => item.status !== "killed" || item.required_code !== item.observed_code ||
        item.mutant_id !== contract.required_mutants[index]?.id || item.required_code !== contract.required_mutants[index]?.code)) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current mutation report denominator differs");
  }
  const replayedMutations = await runNegativeControls(repoRoot, execution.antecedent, binding,
    contract, exactTargetInventory(repoRoot, contract));
  if (canonicalJson(mutations.results) !== canonicalJson(replayedMutations)) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 negative controls differ on replay");
  }
  const storedTests = readJson<TestProcessResult>(repoRoot, receipt.evidence.test_result_ref.path);
  if (canonicalJson(storedTests) !== canonicalJson(await runSelectedTestProcess(repoRoot))) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 selected test process result differs");
  }
  const validation = readJson<{ status: string; selected_binding_ref: ExactRef; validation_contract_ref: ExactRef;
    graph_handle_digest: string; observed_port_calls: number; required_mutants: number; killed_mutants: number;
    passed_tests: number; test_result_ref: ExactRef; output_files: readonly string[];
    authority_effect: string; claim_ceiling: string;
    target_inventory: readonly Readonly<{ id: string; ref: ExactRef }>[] }>(repoRoot, receipt.evidence.validation_result_ref.path);
  assertCurrentP4TargetInventory(validation.target_inventory, contract);
  for (const [index, item] of validation.target_inventory.entries()) {
    sameRef(repoRoot, item.ref, contract.target_inventory[index]!.path, "RECEIPT_TAMPERED");
  }
  if (validation.status !== "pass" || canonicalJson(validation.selected_binding_ref) !== canonicalJson(BINDING_REF) ||
      canonicalJson(validation.validation_contract_ref) !== canonicalJson(VALIDATION_REF) ||
      validation.graph_handle_digest !== receipt.graph_handle.handle_digest || validation.observed_port_calls !== 2 ||
      validation.required_mutants !== 16 || validation.killed_mutants !== 16 ||
      validation.passed_tests !== 10 ||
      canonicalJson(validation.output_files) !== canonicalJson(OUTPUT_FILES) ||
      canonicalJson(validation.test_result_ref) !== canonicalJson(receipt.evidence.test_result_ref) ||
      validation.authority_effect !== "none" || validation.claim_ceiling !== CLAIM_CEILING) {
    fail("RECEIPT_TAMPERED", "receipt", "P4 current validation result differs");
  }
  const tamperCode = errorCode(() => assertCurrentP4ReceiptDigest({ ...receipt,
    acceptance_vector: { ...receipt.acceptance_vector, events: 2 } }));
  if (tamperCode !== "RECEIPT_TAMPERED") {
    fail("RECEIPT_TAMPERED", "receipt", "P4 full receipt tamper was not rejected on replay");
  }
}

/** Replays a persisted terminal receipt and requires the exact six-file output set. */
export async function replayStoredCurrentP4Receipt(repoRoot: string, receiptRef: ExactRef): Promise<void> {
  sameRef(repoRoot, receiptRef, evidence("terminal-receipt.json"), "RECEIPT_TAMPERED");
  assertOutputSet(repoRoot);
  schemaValidate(repoRoot, RECEIPT_SCHEMA, receiptRef.path);
  await verifyCurrentP4Receipt(repoRoot, readJson<CurrentP4Receipt>(repoRoot, receiptRef.path));
}

const invokedDirectly = process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) {
  runCurrentP4Verification().then(
    value => process.stdout.write(`${JSON.stringify(value)}\n`),
    error => {
      process.stderr.write(`${JSON.stringify({ status: "blocked-or-failed",
        code: error instanceof L1Error ? error.code : "TARGET_BASELINE_DRIFT",
        message: error instanceof Error ? error.message : String(error) })}\n`);
      process.exitCode = 1;
    },
  );
}
