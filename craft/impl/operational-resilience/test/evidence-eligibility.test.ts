import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  FOUNDATIONAL_CONTROL_IDS,
  type OperationalEvaluationBundle,
} from "../contracts/operational-evidence.js";
import type {
  EvidenceEligibilityResult,
  LegacyV1EligibilityReplayRequest,
} from "../contracts/evidence-eligibility.js";
import type { LegacyV1SourceInventory } from "../contracts/legacy-v1-adapter.js";
import { deriveFoundationalControlSet } from "../src/derive-foundational-controls.js";
import { evaluateLegacyV1EvidenceEligibility } from "../src/evaluate-evidence-eligibility.js";

type JsonRecord = Record<string, unknown>;
type Mutation = Readonly<{
  op: "replace" | "delete";
  path: string;
  value?: unknown;
}>;
type EligibilityHostileCase = Readonly<{
  schema_version: "domainspec.orodi.eligibility-hostile-case/v1";
  case_id: string;
  base_ref: string;
  mutations: readonly Mutation[];
  expected_code: string;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const implRoot = resolve(packageRoot, "..");
const goldenPath = resolve(packageRoot, "fixtures/eligibility/golden/replay-request.json");
const hostileRoot = resolve(packageRoot, "fixtures/eligibility/hostile");
const inventoryPath = resolve(packageRoot, "contracts/legacy-v1-source-inventory.json");
const resultSchemaPath = resolve(packageRoot, "contracts/evidence-eligibility-result.schema.json");

const readJson = <T>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const request = readJson<LegacyV1EligibilityReplayRequest>(goldenPath);
const inventory = readJson<LegacyV1SourceInventory>(inventoryPath);

const applyMutation = (target: JsonRecord, mutation: Mutation): void => {
  const segments = mutation.path.split("/").slice(1).map((segment) =>
    segment.replaceAll("~1", "/").replaceAll("~0", "~"));
  assert.ok(segments.length > 0, "mutation path must not target the document root");
  let parent: unknown = target;
  for (const segment of segments.slice(0, -1)) {
    assert.ok(parent !== null && typeof parent === "object", `invalid mutation path ${mutation.path}`);
    parent = Array.isArray(parent) ? parent[Number(segment)] : (parent as JsonRecord)[segment];
  }
  const leaf = segments.at(-1)!;
  assert.ok(parent !== null && typeof parent === "object", `invalid mutation parent ${mutation.path}`);
  if (Array.isArray(parent)) {
    const index = Number(leaf);
    assert.ok(Number.isInteger(index) && index >= 0 && index < parent.length, `invalid array index ${mutation.path}`);
    if (mutation.op === "delete") parent.splice(index, 1);
    else parent[index] = clone(mutation.value);
  } else if (mutation.op === "delete") {
    delete (parent as JsonRecord)[leaf];
  } else {
    (parent as JsonRecord)[leaf] = clone(mutation.value);
  }
};

const materialize = (casePath: string, hostile: EligibilityHostileCase): unknown => {
  const target = clone(readJson<JsonRecord>(resolve(dirname(casePath), hostile.base_ref)));
  hostile.mutations.forEach((mutation) => applyMutation(target, mutation));
  return target;
};

const runCli = (requestPath: string) => spawnSync(
  process.execPath,
  ["--import", "tsx", "operational-resilience/src/eligibility-replay-cli.ts", "evaluate", requestPath,
    "--inventory", "operational-resilience/contracts/legacy-v1-source-inventory.json"],
  { cwd: implRoot, encoding: "utf8" },
);

const validateSchema = (result: EvidenceEligibilityResult, scratch: string, stem: string): void => {
  const resultPath = join(scratch, `${stem}.json`);
  writeFileSync(resultPath, `${JSON.stringify(result, null, 2)}\n`);
  const check = spawnSync("python3", ["-m", "jsonschema", "-i", resultPath, resultSchemaPath], { encoding: "utf8" });
  assert.equal(check.status, 0, check.stdout + check.stderr);
};

test("golden legacy evidence is retained for replay but never admitted to runtime", () => {
  const result = evaluateLegacyV1EvidenceEligibility(request, inventory);
  assert.equal(result.decision, "replay-only");
  assert.equal(result.runtime_admission, "denied");
  assert.equal(result.replay_observations.length, 2);
  assert.deepEqual(result.runtime_admitted_observations, []);
  assert.equal(result.eligibility_receipts.length, 2);
  assert.deepEqual(result.findings, []);
  assert.equal(result.authority_effect, "none");
  for (const receipt of result.eligibility_receipts) {
    assert.equal(receipt.decision, "replay-only");
    assert.deepEqual(receipt.eligible_controls, []);
    assert.deepEqual(receipt.ineligible_controls, FOUNDATIONAL_CONTROL_IDS);
    assert.equal(receipt.authority_effect, "none");
  }
});

test("the existing evaluator sees exactly the empty admitted-set denominator", () => {
  const result = evaluateLegacyV1EvidenceEligibility(request, inventory);
  assert.ok(result.derived_result);
  assert.equal(result.derived_result.verdict, "reject");
  assert.equal(result.derived_result.comparison, "match");
  assert.deepEqual(
    result.derived_result.derived_controls.map(({ control_id, state, observation_refs }) =>
      ({ control_id, state, observation_refs })),
    [
      { control_id: "C01", state: "passed", observation_refs: [] },
      { control_id: "C05", state: "missing", observation_refs: [] },
      { control_id: "C11", state: "not-run", observation_refs: [] },
      { control_id: "C12", state: "not-run", observation_refs: [] },
      { control_id: "C14", state: "passed", observation_refs: [] },
      { control_id: "C15", state: "missing", observation_refs: [] },
    ],
  );
});

test("the gate closes the direct-assembly evidence-laundering path", () => {
  const directBundle: OperationalEvaluationBundle = {
    schema_version: "domainspec.orodi.evaluation-bundle/v1",
    evidence_lane: "candidate-local-prototype",
    binding: request.evaluation_context.binding,
    observations: request.normalizations.flatMap(({ normalized_observations }) => normalized_observations),
    controls: request.evaluation_context.controls,
    claim: { claim_id: "direct-assembly-counterexample", required_controls: FOUNDATIONAL_CONTROL_IDS },
    authority_effect: "none",
  };
  const direct = deriveFoundationalControlSet(directBundle, request.evaluated_at);
  assert.deepEqual(
    ["C05", "C11", "C15"].map((id) => direct.derived_controls.find(({ control_id }) => control_id === id)?.state),
    ["passed", "passed", "passed"],
    "the pre-gate evaluator would count raw legacy simulations",
  );
  const gated = evaluateLegacyV1EvidenceEligibility(request, inventory);
  assert.deepEqual(
    ["C05", "C11", "C15"].map((id) => gated.derived_result?.derived_controls.find(({ control_id }) => control_id === id)?.state),
    ["missing", "not-run", "missing"],
  );
});

test("eligibility evaluation is pure and byte-deterministic", () => {
  const mutable = clone(request);
  const before = JSON.stringify(mutable);
  const first = evaluateLegacyV1EvidenceEligibility(mutable, inventory);
  const second = evaluateLegacyV1EvidenceEligibility(mutable, inventory);
  assert.equal(JSON.stringify(mutable), before);
  assert.equal(JSON.stringify(first), JSON.stringify(second));
});

test("runtime-eligible is present only as a future vocabulary state and is never emitted", () => {
  const golden = evaluateLegacyV1EvidenceEligibility(request, inventory);
  assert.notEqual(golden.decision, "runtime-eligible");
  assert.ok(golden.eligibility_receipts.every(({ decision }) => decision !== "runtime-eligible"));
  for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
    const path = resolve(hostileRoot, filename);
    const hostile = readJson<EligibilityHostileCase>(path);
    const result = evaluateLegacyV1EvidenceEligibility(materialize(path, hostile), inventory);
    assert.notEqual(result.decision, "runtime-eligible", hostile.case_id);
  }
});

test("a malformed source inventory fails closed instead of throwing", () => {
  const malformed = clone(inventory) as unknown as { sources: unknown[] };
  malformed.sources[0] = null;
  const result = evaluateLegacyV1EvidenceEligibility(request, malformed);
  assert.equal(result.decision, "rejected");
  assert.equal(result.derived_result, null);
  assert.deepEqual(result.replay_observations, []);
  assert.ok(result.findings.some(({ code }) => code === "ORODI_ELIGIBILITY_INVENTORY_INVALID"));
});

for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
  test(`${filename} fails closed with its exact discriminator`, () => {
    const casePath = resolve(hostileRoot, filename);
    const hostile = readJson<EligibilityHostileCase>(casePath);
    assert.equal(hostile.schema_version, "domainspec.orodi.eligibility-hostile-case/v1");
    const input = materialize(casePath, hostile);
    const before = JSON.stringify(input);
    const result = evaluateLegacyV1EvidenceEligibility(input, inventory);
    assert.equal(result.decision, "rejected", hostile.case_id);
    assert.equal(result.runtime_admission, "denied", hostile.case_id);
    assert.deepEqual(result.replay_observations, [], hostile.case_id);
    assert.deepEqual(result.runtime_admitted_observations, [], hostile.case_id);
    assert.deepEqual(result.eligibility_receipts, [], hostile.case_id);
    assert.equal(result.derived_result, null, hostile.case_id);
    assert.ok(result.findings.some(({ code }) => code === hostile.expected_code),
      `${hostile.case_id}: expected ${hostile.expected_code}, observed ${result.findings.map(({ code }) => code).join(",")}`);
    assert.equal(JSON.stringify(input), before, `${hostile.case_id}: evaluator mutated input`);
    assert.equal(result.authority_effect, "none");
  });
}

test("golden and every hostile output satisfy the closed result schema", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-eligibility-schema-"));
  try {
    validateSchema(evaluateLegacyV1EvidenceEligibility(request, inventory), scratch, "golden");
    for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
      const casePath = resolve(hostileRoot, filename);
      const hostile = readJson<EligibilityHostileCase>(casePath);
      validateSchema(
        evaluateLegacyV1EvidenceEligibility(materialize(casePath, hostile), inventory),
        scratch,
        hostile.case_id,
      );
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the eligibility CLI matches the pure function and uses fail-closed exit codes", () => {
  const goldenRun = runCli("operational-resilience/fixtures/eligibility/golden/replay-request.json");
  assert.equal(goldenRun.status, 0, goldenRun.stdout + goldenRun.stderr);
  assert.deepEqual(JSON.parse(goldenRun.stdout), evaluateLegacyV1EvidenceEligibility(request, inventory));

  const hostilePath = resolve(hostileRoot, "forged-c05-pass.json");
  const hostile = readJson<EligibilityHostileCase>(hostilePath);
  const scratch = mkdtempSync(join(tmpdir(), "orodi-eligibility-cli-"));
  try {
    const requestPath = join(scratch, "forged.json");
    writeFileSync(requestPath, `${JSON.stringify(materialize(hostilePath, hostile), null, 2)}\n`);
    const hostileRun = runCli(requestPath);
    assert.equal(hostileRun.status, 1, hostileRun.stdout + hostileRun.stderr);
    const result = JSON.parse(hostileRun.stdout) as EvidenceEligibilityResult;
    assert.ok(result.findings.some(({ code }) => code === hostile.expected_code));
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the eligibility result schema has an absolute offline identity", () => {
  const schema = readJson<{ $id?: string }>(resultSchemaPath);
  assert.equal(schema.$id, "urn:domainspec:orodi:evidence-eligibility-result:v1");
  assert.doesNotThrow(() => new URL(schema.$id!));
  assert.equal(new URL(schema.$id!).protocol, "urn:");
});
