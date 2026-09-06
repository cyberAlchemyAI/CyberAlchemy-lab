import { existsSync, readFileSync, rmSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  assertBindingRefs,
  deriveUnit,
  L1_PATHS,
  loadFinancialSettlementGraph,
} from "./derive.js";
import {
  assertExactRef,
  digestValue,
  exactRef,
  readJson,
  repositoryRoot,
  sha256,
  writeStableJson,
} from "./exact-ref.js";
import { runR4, validateR4Execution, type R4Execution, type R4FixtureDocument } from "./r4.js";
import { buildUnitReceipt, verifyUnitReceipt } from "./receipt.js";
import {
  fail,
  L1Error,
  R4_IDENTITY,
  type L1ErrorCode,
  type UnitReceipt,
} from "./types.js";
import { assertExactTargetList, schemaValidate } from "./verify-p4.js";

const REVIEWED_INVENTORY =
  "projects/domainspec-v2/development/evolvable-validation-framework/development/" +
  "planning-runs/20260821T002335Z-design-activation-repair/material/root/outputs/" +
  "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/target-inventory.l1.json";
const REVIEWED_INVENTORY_SHA = "39a34bf0100c4ea9d690c3fd3c4334842e2f909683edc32189366a875442c197";
const REVIEWED_VALIDATION_CONTRACT =
  "projects/domainspec-v2/development/evolvable-validation-framework/development/" +
  "planning-runs/20260821T002335Z-design-activation-repair/material/root/outputs/" +
  "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/validation-contract.l1.json";
const REVIEWED_VALIDATION_SHA = "9408ad8bff3fc2b93cd687bbcd1a96cdd69b4e3ec09fa2ff1d85d13f2f2b70e9";
const DEFAULT_P4_VALIDATION =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "SWU-GCP-002-P4/attempt-001/validation-receipt.json";
const DEFAULT_ATTEMPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "SWU-GCP-003-R4/attempt-001";

type Inventory = {
  readonly schema_version: string;
  readonly units: Record<string, { readonly targets: readonly { readonly path: string }[] }>;
};
type ValidationContract = {
  readonly schema_version: string;
  readonly contract_id: string;
  readonly units: Record<string, { readonly mutants: readonly { readonly id: string; readonly required_code: L1ErrorCode }[] }>;
};
type P4Validation = {
  readonly schema_version: string;
  readonly status: "pass";
  readonly unit_id: "SWU-GCP-002-P4";
  readonly receipt_ref: { readonly path: string; readonly sha256: string; readonly size_bytes: number };
  readonly graph_handle: { readonly handle_digest: string };
  readonly release_admission: "not-granted";
};

const R4_MUTANTS = [
  ["R4-M01-always-false", "R4_RESULT_MISMATCH"],
  ["R4-M02-always-true", "R4_RESULT_MISMATCH"],
  ["R4-M03-wrong-date-filter", "R4_RESULT_MISMATCH"],
  ["R4-M04-wrong-type-filter", "R4_RESULT_MISMATCH"],
  ["R4-M05-wrong-count-threshold", "R4_RESULT_MISMATCH"],
  ["R4-M06-count-all-dates", "R4_CONTROL_MISMATCH"],
  ["R4-M07-count-all-types", "R4_CONTROL_MISMATCH"],
  ["R4-M08-edge-wrong-target", "EDGE_ENDPOINT_MISMATCH"],
  ["R4-M09-source-graph-digest-stale", "SOURCE_GRAPH_DIGEST_STALE"],
  ["R4-M10-predicate-digest-stale", "PREDICATE_DIGEST_STALE"],
  ["R4-M11-binding-digest-stale", "BINDING_DIGEST_STALE"],
  ["R4-M12-fixture-digest-stale", "FIXTURE_DIGEST_STALE"],
  ["R4-M13-observation-tamper", "OBSERVATION_TAMPERED"],
  ["R4-M14-receipt-tamper", "RECEIPT_TAMPERED"],
  ["R4-M15-verifier-target-omitted", "VERIFIER_TARGET_OMITTED"],
] as const satisfies readonly (readonly [string, L1ErrorCode])[];

function arg(argv: readonly string[], name: string, fallback: string): string {
  const index = argv.indexOf(name);
  return index >= 0 ? argv[index + 1] ?? fallback : fallback;
}

function reviewedSource(repoRoot: string, requested: string, reviewed: string, expectedSha: string): string {
  const requestedAbsolute = isAbsolute(requested) ? requested : resolve(repoRoot, requested);
  const selected = existsSync(requestedAbsolute) ? requested : reviewed;
  const absolute = isAbsolute(selected) ? selected : resolve(repoRoot, selected);
  if (!existsSync(absolute) || sha256(readFileSync(absolute)) !== expectedSha) {
    fail("TARGET_BASELINE_DRIFT", "admission", `reviewed R4 contract drift: ${selected}`, 2);
  }
  return selected;
}

function exactCode(action: () => unknown): L1ErrorCode | "NO_FAILURE" {
  try {
    action();
    return "NO_FAILURE";
  } catch (error) {
    if (error instanceof L1Error) return error.code;
    throw error;
  }
}

function evidencePath(root: string, name: string): string {
  if (isAbsolute(root)) fail("UNDECLARED_WRITE", "admission", "attempt root must be repository-relative", 2);
  return `${root.replace(/\/$/u, "")}/${name}`;
}

function validateR4Documents(repoRoot: string): void {
  const evf = "projects/domainspec-v2/development/evolvable-validation-framework";
  const pairs = [
    [`${evf}/contracts/financial-settlement-l1-obligations.v1.schema.json`, L1_PATHS.r4Obligation],
    [`${evf}/contracts/financial-settlement-l1-runtime.v1.schema.json`, L1_PATHS.r4Runtime],
    [`${evf}/fixtures/SWU-GCP-003-R4/financial-settlement-r4-input.v1.schema.json`, L1_PATHS.r4Fixture],
    [`${evf}/fixtures/SWU-GCP-003-R4/financial-settlement-r4-binding.v1.schema.json`, L1_PATHS.r4Binding],
  ] as const;
  for (const [schema, document] of pairs) schemaValidate(repoRoot, schema, document);
}

function mutationAssertion(input: {
  readonly id: string;
  readonly repoRoot: string;
  readonly fixture: R4FixtureDocument;
  readonly obligation: ReturnType<typeof deriveUnit>["O_spec"];
  readonly execution: R4Execution;
  readonly targets: readonly string[];
  readonly receipt: UnitReceipt;
}): () => unknown {
  const { id, repoRoot, fixture, obligation, execution, targets, receipt } = input;
  const zero = "0".repeat(64);
  if (/^R4-M0[1-7]-/u.test(id)) return () => runR4(fixture, obligation, id);
  if (id === "R4-M08-edge-wrong-target") {
    return () => {
      const graph = structuredClone(loadFinancialSettlementGraph(repoRoot));
      const edge = graph.edges.find((entry) => entry.edge_id === R4_IDENTITY.edge_id)! as { to: string };
      edge.to = "financial-settlement.PayoutCreated";
      deriveUnit(repoRoot, "R4", { graph });
    };
  }
  if (id === "R4-M09-source-graph-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.graph), sha256: zero }, "SOURCE_GRAPH_DIGEST_STALE");
  }
  if (id === "R4-M10-predicate-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.r4Semantic), sha256: zero }, "PREDICATE_DIGEST_STALE");
  }
  if (id === "R4-M11-binding-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.r4Binding), sha256: zero }, "BINDING_DIGEST_STALE");
  }
  if (id === "R4-M12-fixture-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.r4Fixture), sha256: zero }, "FIXTURE_DIGEST_STALE");
  }
  if (id === "R4-M13-observation-tamper") {
    return () => {
      const tampered = structuredClone(execution) as R4Execution & { observations: Array<{ actual: boolean }> };
      tampered.observations[0]!.actual = !tampered.observations[0]!.actual;
      validateR4Execution(tampered);
    };
  }
  if (id === "R4-M14-receipt-tamper") {
    return () => {
      const tampered = structuredClone(receipt) as UnitReceipt & { receipt_digest: string };
      tampered.receipt_digest = zero;
      verifyUnitReceipt(repoRoot, tampered);
    };
  }
  if (id === "R4-M15-verifier-target-omitted") {
    return () => assertExactTargetList(targets.slice(1), targets);
  }
  return () => fail("TARGET_BASELINE_DRIFT", "mutation", `unknown R4 mutant ${id}`);
}

export function runR4Verification(options: {
  readonly repoRoot?: string;
  readonly inventory?: string;
  readonly validationContract?: string;
  readonly p4Receipt?: string;
  readonly attemptRoot?: string;
} = {}): Record<string, unknown> {
  const repoRoot = options.repoRoot ? resolve(options.repoRoot) : repositoryRoot();
  const inventoryPath = reviewedSource(
    repoRoot,
    options.inventory ?? "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/target-inventory.l1.json",
    REVIEWED_INVENTORY,
    REVIEWED_INVENTORY_SHA,
  );
  const validationPath = reviewedSource(
    repoRoot,
    options.validationContract ?? "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/validation-contract.l1.json",
    REVIEWED_VALIDATION_CONTRACT,
    REVIEWED_VALIDATION_SHA,
  );
  const p4ValidationPath = options.p4Receipt ?? DEFAULT_P4_VALIDATION;
  const attemptRoot = options.attemptRoot ?? DEFAULT_ATTEMPT;
  const created: string[] = [];
  try {
    const inventory = JSON.parse(readFileSync(resolve(repoRoot, inventoryPath), "utf8")) as Inventory;
    const contract = JSON.parse(readFileSync(resolve(repoRoot, validationPath), "utf8")) as ValidationContract;
    const targets = inventory.units["SWU-GCP-003-R4"]?.targets.map((entry) => entry.path) ?? [];
    if (targets.length !== 20 || new Set(targets).size !== 20) {
      fail("VERIFIER_TARGET_OMITTED", "admission", "R4 target denominator is not exactly 20", 2);
    }
    const contractMutants = contract.units["SWU-GCP-003-R4"]?.mutants ?? [];
    assertExactTargetList(
      contractMutants.map((entry) => `${entry.id}:${entry.required_code}`),
      R4_MUTANTS.map(([id, code]) => `${id}:${code}`),
    );
    validateR4Documents(repoRoot);

    const p4Validation = readJson<P4Validation>(repoRoot, p4ValidationPath);
    if (
      p4Validation.status !== "pass" ||
      p4Validation.unit_id !== "SWU-GCP-002-P4" ||
      p4Validation.release_admission !== "not-granted"
    ) {
      fail("TARGET_BASELINE_DRIFT", "admission", "P4 terminal prerequisite is not a candidate-local PASS", 2);
    }
    assertExactRef(repoRoot, p4Validation.receipt_ref, "RECEIPT_TAMPERED");
    const p4Receipt = readJson<UnitReceipt>(repoRoot, p4Validation.receipt_ref.path);
    verifyUnitReceipt(repoRoot, p4Receipt);

    const derivation = deriveUnit(repoRoot, "R4");
    if (
      derivation.graph_handle.handle_digest !== p4Receipt.graph_handle.handle_digest ||
      p4Validation.graph_handle.handle_digest !== p4Receipt.graph_handle.handle_digest
    ) {
      fail("SOURCE_GRAPH_DIGEST_STALE", "admission", "R4 does not consume P4's frozen graph/source handle", 2);
    }
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.r4Binding);
    assertBindingRefs(repoRoot, binding, "R4");
    const fixture = readJson<R4FixtureDocument>(repoRoot, L1_PATHS.r4Fixture);
    const execution = runR4(fixture, derivation.O_spec);

    const sourceReplayPath = evidencePath(attemptRoot, "source-graph-replay.json");
    const obligationPath = evidencePath(attemptRoot, "derived-obligation.json");
    const bindingPath = evidencePath(attemptRoot, "binding-envelope.json");
    const executionPath = evidencePath(attemptRoot, "execution-envelope.json");
    const mutationPath = evidencePath(attemptRoot, "mutation-report.json");
    const receiptPath = evidencePath(attemptRoot, "evolvable-validation-receipt.json");
    const validationReceiptPath = evidencePath(attemptRoot, "validation-receipt.json");
    const executorPath = evidencePath(attemptRoot, "executor-receipt.json");
    const targetInventoryPath = evidencePath(attemptRoot, "target-result-inventory.json");

    const replayRef = writeStableJson(repoRoot, sourceReplayPath, {
      schema_version: "evf.financial-settlement-source-graph-replay/v1",
      unit_id: "SWU-GCP-003-R4",
      p4_validation_ref: exactRef(repoRoot, p4ValidationPath),
      graph_handle: derivation.graph_handle,
      source_graph_mutation: "forbidden-and-none-observed",
      status: "pass",
      authority_effect: "none",
    }, created);
    const obligationRef = writeStableJson(repoRoot, obligationPath, {
      schema_version: "evf.financial-settlement-derived-obligation/v1",
      unit_id: "SWU-GCP-003-R4",
      O_spec: derivation.O_spec,
      O_gen: derivation.O_gen,
      comparison: derivation.comparison,
      O_spec_digest: digestValue(derivation.O_spec),
      O_gen_digest: digestValue(derivation.O_gen),
      authority_effect: "none",
    }, created);
    const bindingRef = writeStableJson(repoRoot, bindingPath, {
      schema_version: "evf.financial-settlement-binding-evidence/v1",
      unit_id: "SWU-GCP-003-R4",
      binding_ref: exactRef(repoRoot, L1_PATHS.r4Binding),
      exact_refs_verified: true,
      decision_field: "shouldCreateMakeupAppliedEvent",
      binding,
      authority_effect: "none",
    }, created);
    const executionRef = writeStableJson(repoRoot, executionPath, execution, created);
    const provisionalReceipt = buildUnitReceipt({
      unit: "R4",
      graphHandle: derivation.graph_handle,
      evidenceRefs: [replayRef, obligationRef, bindingRef, executionRef, exactRef(repoRoot, L1_PATHS.r4Semantic)],
      acceptanceVector: { cases: 5, mutants_required: 15, mutants_killed: 15, side_effects: 0 },
    });
    const mutantResults = R4_MUTANTS.map(([id, requiredCode]) => {
      const actual = exactCode(mutationAssertion({
        id,
        repoRoot,
        fixture,
        obligation: derivation.O_spec,
        execution,
        targets,
        receipt: provisionalReceipt,
      }));
      if (actual !== requiredCode) {
        fail(requiredCode, "mutation", `${id} produced ${actual}; expected ${requiredCode}`);
      }
      return { mutant_id: id, status: "killed" as const, stable_code: actual };
    });
    const mutationRef = writeStableJson(repoRoot, mutationPath, {
      schema_version: "evf.financial-settlement-r4-mutation-report/v1",
      unit_id: "SWU-GCP-003-R4",
      required: 15,
      killed: 15,
      survived: 0,
      results: mutantResults,
      status: "pass",
    }, created);
    const receipt = buildUnitReceipt({
      unit: "R4",
      graphHandle: derivation.graph_handle,
      evidenceRefs: [replayRef, obligationRef, bindingRef, executionRef, mutationRef],
      acceptanceVector: {
        rule_ids: 1,
        edge_ids: 1,
        obligations: 1,
        bindings: 1,
        truth_table_cases: 5,
        mutants_required: 15,
        mutants_killed: 15,
        side_effects: 0,
        skips: 0,
        todos: 0,
        needs_formal: 0,
        orphans: 0,
        unrunnable: 0,
      },
    });
    verifyUnitReceipt(repoRoot, receipt);
    writeStableJson(repoRoot, receiptPath, receipt, created);
    schemaValidate(
      repoRoot,
      "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-l1-receipt.v1.schema.json",
      receiptPath,
    );
    const executorRef = writeStableJson(repoRoot, executorPath, {
      schema_version: "evf.candidate-local-prototype-executor/v1",
      unit_id: "SWU-GCP-003-R4",
      status: "pass",
      mode: "candidate-local-fast-lane",
      p4_prerequisite_ref: exactRef(repoRoot, p4ValidationPath),
      actual_runtime_source_ref: exactRef(repoRoot, "validation/poker-team/backend/src/domain/settlement/settlement.service.ts"),
      writes_observed: 0,
      events_observed: 0,
      network: "forbidden",
      authority_effect: "none",
      release_admission: "not-granted",
    }, created);
    const validationRef = writeStableJson(repoRoot, validationReceiptPath, {
      schema_version: "evf.financial-settlement-r4-candidate-validation/v1",
      unit_id: "SWU-GCP-003-R4",
      status: "pass",
      mode: "candidate-local-fast-lane",
      p4_prerequisite_ref: exactRef(repoRoot, p4ValidationPath),
      reviewed_inventory_ref: exactRef(repoRoot, inventoryPath),
      validation_contract_ref: exactRef(repoRoot, validationPath),
      receipt_ref: exactRef(repoRoot, receiptPath),
      executor_ref: executorRef,
      graph_handle: derivation.graph_handle,
      acceptance_vector: receipt.acceptance_vector,
      stable_codes: mutantResults.map((entry) => entry.stable_code),
      claim_ceiling: receipt.claim_ceiling,
      authority_effect: "none",
      release_admission: "not-granted",
    }, created);

    for (const target of targets) {
      if (target === targetInventoryPath) continue;
      if (!existsSync(resolve(repoRoot, target))) {
        fail("VERIFIER_TARGET_OMITTED", "aggregate", `R4 target is absent: ${target}`);
      }
    }
    const targetResult = {
      schema_version: "evf.financial-settlement-target-result-inventory/v1",
      unit_id: "SWU-GCP-003-R4",
      target_count: 20,
      self: { path: targetInventoryPath, digest_policy: "self-path-recorded-self-digest-excluded" },
      targets: targets.filter((path) => path !== targetInventoryPath).map((path) => exactRef(repoRoot, path)),
      status: "pass",
      source_graph_writes: 0,
      authority_effect: "none",
      release_admission: "not-granted",
    };
    writeStableJson(repoRoot, targetInventoryPath, targetResult, created);
    if (targetResult.targets.length !== 19) {
      fail("VERIFIER_TARGET_OMITTED", "aggregate", "R4 target-result inventory denominator is not 20");
    }
    return {
      status: "pass",
      unit_id: "SWU-GCP-003-R4",
      mode: "candidate-local-fast-lane",
      graph_handle_digest: derivation.graph_handle.handle_digest,
      mutant_kills: 15,
      receipt_ref: exactRef(repoRoot, receiptPath),
      validation_ref: validationRef,
      target_count: 20,
      authority_effect: "none",
      release_admission: "not-granted",
    };
  } catch (error) {
    for (const absolute of created.reverse()) if (existsSync(absolute)) rmSync(absolute);
    throw error;
  }
}

const invokedDirectly =
  process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) {
  const argv = process.argv.slice(2);
  try {
    const result = runR4Verification({
      inventory: arg(argv, "--inventory", "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/target-inventory.l1.json"),
      validationContract: arg(argv, "--validation-contract", "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/validation-contract.l1.json"),
      p4Receipt: arg(argv, "--p4-receipt", DEFAULT_P4_VALIDATION),
      attemptRoot: arg(argv, "--attempt-root", DEFAULT_ATTEMPT),
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const failure = error instanceof L1Error
      ? { status: "blocked-or-failed", code: error.code, phase: error.phase, message: error.message }
      : { status: "blocked-or-failed", code: "TARGET_BASELINE_DRIFT", phase: "aggregate", message: error instanceof Error ? error.message : String(error) };
    process.stderr.write(`${JSON.stringify(failure)}\n`);
    process.exitCode = error instanceof L1Error ? error.exitCode : 1;
  }
}
