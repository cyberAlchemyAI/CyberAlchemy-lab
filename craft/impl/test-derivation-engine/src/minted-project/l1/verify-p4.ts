import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, rmSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  assertBindingRefs,
  assertRelationshipSignature,
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
import {
  mutateP4Execution,
  runP4,
  validateP4Execution,
  type P4FixtureDocument,
} from "./p4.js";
import { buildUnitReceipt, verifyUnitReceipt } from "./receipt.js";
import {
  fail,
  L1Error,
  P4_IDENTITY,
  type ExactRef,
  type L1ErrorCode,
  type UnitReceipt,
} from "./types.js";

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
const DEFAULT_ATTEMPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/" +
  "SWU-GCP-002-P4/attempt-001";

type Inventory = {
  readonly schema_version: "evf.l1-target-inventory/v1";
  readonly units: Record<string, { readonly targets: readonly { readonly path: string }[] }>;
};
type ValidationContract = {
  readonly schema_version: "evf.l1-validation-contract/v1";
  readonly contract_id: "evf.l1.financial-settlement.p4-r4.v1";
  readonly units: Record<string, {
    readonly mutants: readonly { readonly id: string; readonly required_code: L1ErrorCode }[];
  }>;
};

const P4_MUTANTS = [
  ["P4-M01-missing-write", "P4_WRITE_MISSING"],
  ["P4-M02-missing-event", "P4_EVENT_MISSING"],
  ["P4-M03-wrong-write-amount", "P4_WRITE_AMOUNT_MISMATCH"],
  ["P4-M04-wrong-event-amount", "P4_EVENT_AMOUNT_MISMATCH"],
  ["P4-M05-wrong-write-date", "P4_WRITE_DATE_MISMATCH"],
  ["P4-M06-wrong-event-date", "P4_EVENT_DATE_MISMATCH"],
  ["P4-M07-event-before-write", "P4_EFFECT_ORDER_MISMATCH"],
  ["P4-M08-extra-effect", "P4_EFFECT_CARDINALITY_MISMATCH"],
  ["P4-M09-edge-wrong-target", "EDGE_ENDPOINT_MISMATCH"],
  ["P4-M10-signature-wrong", "RELATIONSHIP_SIGNATURE_MISMATCH"],
  ["P4-M11-source-graph-digest-stale", "SOURCE_GRAPH_DIGEST_STALE"],
  ["P4-M12-predicate-digest-stale", "PREDICATE_DIGEST_STALE"],
  ["P4-M13-binding-digest-stale", "BINDING_DIGEST_STALE"],
  ["P4-M14-fixture-digest-stale", "FIXTURE_DIGEST_STALE"],
  ["P4-M15-receipt-tamper", "RECEIPT_TAMPERED"],
  ["P4-M16-verifier-target-omitted", "VERIFIER_TARGET_OMITTED"],
] as const satisfies readonly (readonly [string, L1ErrorCode])[];

function arg(argv: readonly string[], name: string, fallback: string): string {
  const index = argv.indexOf(name);
  return index >= 0 ? argv[index + 1] ?? fallback : fallback;
}

function reviewedSource(
  repoRoot: string,
  requested: string,
  reviewed: string,
  expectedSha: string,
): string {
  const requestedAbsolute = isAbsolute(requested) ? requested : resolve(repoRoot, requested);
  const selected = existsSync(requestedAbsolute) ? requested : reviewed;
  const absolute = isAbsolute(selected) ? selected : resolve(repoRoot, selected);
  if (!existsSync(absolute) || sha256(readFileSync(absolute)) !== expectedSha) {
    fail("TARGET_BASELINE_DRIFT", "admission", `reviewed fast-lane contract drift: ${selected}`, 2);
  }
  return selected;
}

export function assertExactTargetList(actual: readonly string[], expected: readonly string[]): void {
  if (
    actual.length !== expected.length ||
    new Set(actual).size !== actual.length ||
    actual.some((path, index) => path !== expected[index])
  ) {
    fail("VERIFIER_TARGET_OMITTED", "aggregate", "verifier target denominator is not exact and ordered");
  }
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

export function schemaValidate(repoRoot: string, schemaPath: string, documentPath: string): void {
  const script = String.raw`
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
import json
import sys

from jsonschema import Draft202012Validator, RefResolver

schema_path = Path(sys.argv[1]).resolve()
document_path = Path(sys.argv[2]).resolve()
repository_root = Path(sys.argv[3]).resolve()
store = {}
seen = set()

def iter_refs(value):
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref
        for nested in value.values():
            yield from iter_refs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_refs(nested)

def within_repository(path):
    try:
        path.relative_to(repository_root)
        return True
    except ValueError:
        return False

def load_local(path, aliases=()):
    path = path.resolve()
    if not within_repository(path):
        raise RuntimeError(f"local schema reference escapes repository: {path}")
    schema = json.loads(path.read_text(encoding="utf-8"))
    base = schema.get("$id", path.as_uri())
    for uri in (path.as_uri(), base, *aliases):
        store[urldefrag(uri)[0]] = schema
    if path in seen:
        return schema
    seen.add(path)
    for ref in iter_refs(schema):
        target_ref, _ = urldefrag(ref)
        parsed = urlparse(target_ref)
        if target_ref and not parsed.scheme:
            target = (path.parent / target_ref).resolve()
            if target.is_file():
                alias = urldefrag(urljoin(base, ref))[0]
                load_local(target, (alias,))
    return schema

def reject_unregistered(uri):
    raise RuntimeError(f"unregistered schema retrieval forbidden: {uri}")

schema = load_local(schema_path)
document = json.loads(document_path.read_text(encoding="utf-8"))
resolver = RefResolver(
    base_uri=schema_path.as_uri(),
    referrer=schema,
    store=store,
    handlers={"http": reject_unregistered, "https": reject_unregistered, "file": reject_unregistered},
)
Draft202012Validator(schema, resolver=resolver).validate(document)
`;
  const child = spawnSync("python3", [
    "-c",
    script,
    resolve(repoRoot, schemaPath),
    resolve(repoRoot, documentPath),
    resolve(repoRoot),
  ], {
    cwd: repoRoot,
    encoding: "utf8",
    timeout: 120_000,
    maxBuffer: 4 * 1024 * 1024,
  });
  if (child.error || child.status !== 0) {
    fail("TARGET_BASELINE_DRIFT", "admission", `schema validation failed for ${documentPath}: ${child.stderr || child.stdout}`, 2);
  }
}

function validateP4Documents(repoRoot: string): void {
  const evf = "projects/domainspec-v2/development/evolvable-validation-framework";
  const pairs = [
    [`${evf}/semantic-source/financial-settlement-p4-rule.v1.schema.json`, L1_PATHS.p4Semantic],
    [`${evf}/semantic-source/financial-settlement-r4-predicate.v1.schema.json`, L1_PATHS.r4Semantic],
    [`${evf}/contracts/financial-settlement-l1-obligations.v1.schema.json`, L1_PATHS.p4Obligation],
    [`${evf}/contracts/financial-settlement-l1-runtime.v1.schema.json`, L1_PATHS.p4Runtime],
    [`${evf}/fixtures/SWU-GCP-002-P4/financial-settlement-p4-input.v1.schema.json`, L1_PATHS.p4Fixture],
    [`${evf}/fixtures/SWU-GCP-002-P4/financial-settlement-p4-binding.v1.schema.json`, L1_PATHS.p4Binding],
  ] as const;
  for (const [schema, document] of pairs) schemaValidate(repoRoot, schema, document);
}

function mutationAssertion(input: {
  readonly id: string;
  readonly repoRoot: string;
  readonly execution: Awaited<ReturnType<typeof runP4>>;
  readonly targets: readonly string[];
  readonly receipt: UnitReceipt;
}): () => unknown {
  const { id, repoRoot, execution, targets, receipt } = input;
  const zero = "0".repeat(64);
  if (id.startsWith("P4-M0") && Number.parseInt(id.slice(5, 7), 10) <= 8) {
    return () => validateP4Execution(mutateP4Execution(execution, id));
  }
  if (id === "P4-M09-edge-wrong-target") {
    return () => {
      const graph = structuredClone(loadFinancialSettlementGraph(repoRoot));
      const edge = graph.edges.find((entry) => entry.edge_id === P4_IDENTITY.edge_id)! as { to: string };
      edge.to = "financial-settlement.PayoutCreated";
      deriveUnit(repoRoot, "P4", { graph });
    };
  }
  if (id === "P4-M10-signature-wrong") {
    return () => assertRelationshipSignature({
      source_type: "Operation",
      target_type: "Rule",
      direction: "canonical",
      status: "active",
    });
  }
  if (id === "P4-M11-source-graph-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.graph), sha256: zero }, "SOURCE_GRAPH_DIGEST_STALE");
  }
  if (id === "P4-M12-predicate-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.p4Semantic), sha256: zero }, "PREDICATE_DIGEST_STALE");
  }
  if (id === "P4-M13-binding-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.p4Binding), sha256: zero }, "BINDING_DIGEST_STALE");
  }
  if (id === "P4-M14-fixture-digest-stale") {
    return () => assertExactRef(repoRoot, { ...exactRef(repoRoot, L1_PATHS.p4Fixture), sha256: zero }, "FIXTURE_DIGEST_STALE");
  }
  if (id === "P4-M15-receipt-tamper") {
    return () => {
      const tampered = structuredClone(receipt) as UnitReceipt & { acceptance_vector: Record<string, number> };
      tampered.acceptance_vector.mutants_killed = 15;
      verifyUnitReceipt(repoRoot, tampered);
    };
  }
  if (id === "P4-M16-verifier-target-omitted") {
    return () => assertExactTargetList(targets.slice(0, -1), targets);
  }
  return () => fail("TARGET_BASELINE_DRIFT", "mutation", `unknown P4 mutant ${id}`);
}

function evidencePath(root: string, name: string): string {
  if (isAbsolute(root)) fail("UNDECLARED_WRITE", "admission", "attempt root must be repository-relative", 2);
  return `${root.replace(/\/$/u, "")}/${name}`;
}

export async function runP4Verification(options: {
  readonly repoRoot?: string;
  readonly inventory?: string;
  readonly validationContract?: string;
  readonly attemptRoot?: string;
} = {}): Promise<Record<string, unknown>> {
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
  const attemptRoot = options.attemptRoot ?? DEFAULT_ATTEMPT;
  const created: string[] = [];
  try {
    const inventory = JSON.parse(readFileSync(resolve(repoRoot, inventoryPath), "utf8")) as Inventory;
    const contract = JSON.parse(readFileSync(resolve(repoRoot, validationPath), "utf8")) as ValidationContract;
    if (
      inventory.schema_version !== "evf.l1-target-inventory/v1" ||
      contract.schema_version !== "evf.l1-validation-contract/v1" ||
      contract.contract_id !== "evf.l1.financial-settlement.p4-r4.v1"
    ) {
      fail("TARGET_BASELINE_DRIFT", "admission", "reviewed P4 contract identity is invalid", 2);
    }
    const targets = inventory.units["SWU-GCP-002-P4"]?.targets.map((target) => target.path) ?? [];
    if (targets.length !== 44 || new Set(targets).size !== 44) {
      fail("VERIFIER_TARGET_OMITTED", "admission", "P4 target denominator is not exactly 44", 2);
    }
    const contractMutants = contract.units["SWU-GCP-002-P4"]?.mutants ?? [];
    assertExactTargetList(
      contractMutants.map((entry) => `${entry.id}:${entry.required_code}`),
      P4_MUTANTS.map(([id, code]) => `${id}:${code}`),
    );
    validateP4Documents(repoRoot);

    const derivation = deriveUnit(repoRoot, "P4");
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.p4Binding);
    assertBindingRefs(repoRoot, binding, "P4");
    const fixture = readJson<P4FixtureDocument>(repoRoot, L1_PATHS.p4Fixture);
    const execution = await runP4(fixture);

    const snapshotPath = evidencePath(attemptRoot, "source-graph-snapshot.json");
    const obligationPath = evidencePath(attemptRoot, "derived-obligation.json");
    const bindingPath = evidencePath(attemptRoot, "binding-envelope.json");
    const executionPath = evidencePath(attemptRoot, "execution-envelope.json");
    const mutationPath = evidencePath(attemptRoot, "mutation-report.json");
    const receiptPath = evidencePath(attemptRoot, "evolvable-validation-receipt.json");
    const validationReceiptPath = evidencePath(attemptRoot, "validation-receipt.json");
    const executorPath = evidencePath(attemptRoot, "executor-receipt.json");
    const targetInventoryPath = evidencePath(attemptRoot, "target-result-inventory.json");

    const snapshotRef = writeStableJson(repoRoot, snapshotPath, {
      schema_version: "evf.financial-settlement-source-graph-snapshot/v1",
      unit_id: "SWU-GCP-002-P4",
      graph_handle: derivation.graph_handle,
      distinct_rule_ids: [P4_IDENTITY.rule_id, "financial-settlement.NoDuplicateMakeupRule"],
      distinct_edge_ids: [P4_IDENTITY.edge_id, "financial-settlement.edge.no-duplicate-makeup-rule-enforces-generation"],
      status: "pass",
      authority_effect: "none",
      release_admission: "not-granted",
    }, created);
    const obligationRef = writeStableJson(repoRoot, obligationPath, {
      schema_version: "evf.financial-settlement-derived-obligation/v1",
      unit_id: "SWU-GCP-002-P4",
      O_spec: derivation.O_spec,
      O_gen: derivation.O_gen,
      comparison: derivation.comparison,
      O_spec_digest: digestValue(derivation.O_spec),
      O_gen_digest: digestValue(derivation.O_gen),
      authority_effect: "none",
    }, created);
    const bindingRef = writeStableJson(repoRoot, bindingPath, {
      schema_version: "evf.financial-settlement-binding-evidence/v1",
      unit_id: "SWU-GCP-002-P4",
      binding_ref: exactRef(repoRoot, L1_PATHS.p4Binding),
      exact_refs_verified: true,
      binding,
      authority_effect: "none",
    }, created);
    const executionRef = writeStableJson(repoRoot, executionPath, execution, created);

    const provisionalReceipt = buildUnitReceipt({
      unit: "P4",
      graphHandle: derivation.graph_handle,
      evidenceRefs: [
        snapshotRef,
        obligationRef,
        bindingRef,
        executionRef,
        exactRef(repoRoot, L1_PATHS.p4Semantic),
      ],
      acceptanceVector: { mutants_required: 16, mutants_killed: 16, writes: 1, events: 1 },
    });
    const mutantResults = P4_MUTANTS.map(([id, requiredCode]) => {
      const actualCode = exactCode(mutationAssertion({
        id,
        repoRoot,
        execution,
        targets,
        receipt: provisionalReceipt,
      }));
      if (actualCode !== requiredCode) {
        fail(
          requiredCode,
          "mutation",
          `${id} produced ${actualCode}; expected ${requiredCode}`,
        );
      }
      return { mutant_id: id, status: "killed" as const, stable_code: actualCode };
    });
    const mutationRef = writeStableJson(repoRoot, mutationPath, {
      schema_version: "evf.financial-settlement-p4-mutation-report/v1",
      unit_id: "SWU-GCP-002-P4",
      required: 16,
      killed: 16,
      survived: 0,
      results: mutantResults,
      status: "pass",
    }, created);

    const receipt = buildUnitReceipt({
      unit: "P4",
      graphHandle: derivation.graph_handle,
      evidenceRefs: [snapshotRef, obligationRef, bindingRef, executionRef, mutationRef],
      acceptanceVector: {
        rule_ids: 1,
        edge_ids: 1,
        obligations: 1,
        bindings: 1,
        eligible_execution_cases: 1,
        writes: 1,
        events: 1,
        mutants_required: 16,
        mutants_killed: 16,
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
      unit_id: "SWU-GCP-002-P4",
      status: "pass",
      mode: "candidate-local-fast-lane",
      handoff_notice: "HN-683467F8A6AD",
      actual_runtime_source_ref: exactRef(repoRoot, "validation/poker-team/backend/src/use-cases/financial-settlement/generate-settlement.ts"),
      observation_adapter_ref: exactRef(repoRoot, "validation/poker-team/backend/src/domain/__derived__/financial-settlement.sfol.adapter.ts"),
      network: "forbidden",
      authority_effect: "none",
      release_admission: "not-granted",
    }, created);
    const validationRef = writeStableJson(repoRoot, validationReceiptPath, {
      schema_version: "evf.financial-settlement-p4-candidate-validation/v1",
      unit_id: "SWU-GCP-002-P4",
      status: "pass",
      mode: "candidate-local-fast-lane",
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
        fail("VERIFIER_TARGET_OMITTED", "aggregate", `P4 target is absent: ${target}`);
      }
    }
    const inventoryResult = {
      schema_version: "evf.financial-settlement-target-result-inventory/v1",
      unit_id: "SWU-GCP-002-P4",
      target_count: targets.length,
      self: { path: targetInventoryPath, digest_policy: "self-path-recorded-self-digest-excluded" },
      targets: targets.filter((path) => path !== targetInventoryPath).map((path) => exactRef(repoRoot, path)),
      status: "pass",
      authority_effect: "none",
      release_admission: "not-granted",
    };
    writeStableJson(repoRoot, targetInventoryPath, inventoryResult, created);
    if (inventoryResult.targets.length !== 43) {
      fail("VERIFIER_TARGET_OMITTED", "aggregate", "P4 target-result inventory denominator is not 44");
    }

    return {
      status: "pass",
      unit_id: "SWU-GCP-002-P4",
      mode: "candidate-local-fast-lane",
      graph_handle_digest: derivation.graph_handle.handle_digest,
      mutant_kills: 16,
      receipt_ref: exactRef(repoRoot, receiptPath),
      validation_ref: validationRef,
      target_count: 44,
      authority_effect: "none",
      release_admission: "not-granted",
    };
  } catch (error) {
    for (const absolute of created.reverse()) {
      if (existsSync(absolute)) rmSync(absolute);
    }
    throw error;
  }
}

const invokedDirectly =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href;

if (invokedDirectly) {
  const argv = process.argv.slice(2);
  runP4Verification({
    inventory: arg(argv, "--inventory", "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/target-inventory.l1.json"),
    validationContract: arg(argv, "--validation-contract", "projects/domainspec-v2/development/evolvable-validation-framework/work-pack/validation-contract.l1.json"),
    attemptRoot: arg(argv, "--attempt-root", DEFAULT_ATTEMPT),
  }).then(
    (result) => process.stdout.write(`${JSON.stringify(result)}\n`),
    (error) => {
      const failure = error instanceof L1Error
        ? { status: "blocked-or-failed", code: error.code, phase: error.phase, message: error.message }
        : { status: "blocked-or-failed", code: "TARGET_BASELINE_DRIFT", phase: "aggregate", message: error instanceof Error ? error.message : String(error) };
      process.stderr.write(`${JSON.stringify(failure)}\n`);
      process.exitCode = error instanceof L1Error ? error.exitCode : 1;
    },
  );
}
