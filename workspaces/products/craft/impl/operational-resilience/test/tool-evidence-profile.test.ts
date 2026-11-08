import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type { ToolEvidenceProfileValidationResult } from "../contracts/tool-evidence-profile.js";
import { validateToolEvidenceProfile } from "../src/validate-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
type Mutation = Readonly<{
  op: "add" | "remove" | "replace";
  path: string;
  value?: unknown;
  copy_from?: string;
}>;
type HostileCase = Readonly<{
  case_id: string;
  kind: "mutation" | "raw-descriptor" | "cli";
  base?: string;
  target?: "descriptor" | "inventory" | "policy" | "referents";
  mutations?: readonly Mutation[];
  raw_descriptor?: string;
  evaluated_at?: string;
  expected_code: string;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const goldenRoot = resolve(packageRoot, "fixtures/tool-evidence-profiles/golden");
const hostilePath = resolve(packageRoot, "fixtures/tool-evidence-profiles/hostile/cases.json");
const expectedPath = resolve(packageRoot, "fixtures/tool-evidence-profiles/expected-results.json");
const inventoryPath = resolve(packageRoot, "contracts/tool-evidence-profile-family-inventory.json");
const policyPath = resolve(packageRoot, "contracts/tool-evidence-profile-attribute-policy.json");
const referentsPath = resolve(packageRoot, "fixtures/tool-evidence-profiles/referents.json");
const resultSchemaPath = resolve(packageRoot, "contracts/tool-evidence-profile-validation-result.schema.json");
const evaluatedAt = "2026-08-26T12:37:54Z";
const families = [
  "telemetry", "health-failure", "workload", "fault", "canary-analysis",
  "deployment-observation", "rollback-observation",
] as const;

const readText = (path: string): string => readFileSync(path, "utf8");
const readJson = <T>(path: string): T => JSON.parse(readText(path)) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const inventoryText = readText(inventoryPath);
const policyText = readText(policyPath);
const referentsText = readText(referentsPath);
const hostile = readJson<{ cases: HostileCase[]; authority_effect: string }>(hostilePath);

function pointerSegments(path: string): string[] {
  return path.split("/").slice(1).map((segment) =>
    segment.replaceAll("~1", "/").replaceAll("~0", "~"));
}

function getPointer(target: unknown, path: string): unknown {
  let current = target;
  for (const segment of pointerSegments(path)) {
    assert.ok(current !== null && typeof current === "object", `invalid copy path ${path}`);
    current = Array.isArray(current) ? current[Number(segment)] : (current as JsonRecord)[segment];
  }
  return current;
}

function applyMutation(target: JsonRecord, mutation: Mutation): void {
  const segments = pointerSegments(mutation.path);
  assert.ok(segments.length > 0, "root mutation is forbidden");
  let parent: unknown = target;
  for (const segment of segments.slice(0, -1)) {
    assert.ok(parent !== null && typeof parent === "object", `invalid mutation path ${mutation.path}`);
    parent = Array.isArray(parent) ? parent[Number(segment)] : (parent as JsonRecord)[segment];
  }
  assert.ok(parent !== null && typeof parent === "object", `invalid mutation parent ${mutation.path}`);
  const leaf = segments.at(-1)!;
  const value = mutation.op === "remove"
    ? undefined
    : mutation.copy_from
      ? clone(getPointer(target, mutation.copy_from))
      : clone(mutation.value);
  if (Array.isArray(parent)) {
    if (mutation.op === "add" && leaf === "-") {
      parent.push(value);
      return;
    }
    const index = Number(leaf);
    assert.ok(Number.isInteger(index) && index >= 0 && index < parent.length, mutation.path);
    if (mutation.op === "remove") parent.splice(index, 1);
    else if (mutation.op === "add") parent.splice(index, 0, value);
    else parent[index] = value;
    return;
  }
  if (mutation.op === "remove") delete (parent as JsonRecord)[leaf];
  else (parent as JsonRecord)[leaf] = value;
}

function materialize(hostileCase: HostileCase): Readonly<{
  descriptor: string;
  inventory: string;
  policy: string;
  referents: string;
}> {
  const base = hostileCase.base ?? "telemetry";
  const inputs = {
    descriptor: readJson<JsonRecord>(resolve(goldenRoot, `${base}.json`)),
    inventory: readJson<JsonRecord>(inventoryPath),
    policy: readJson<JsonRecord>(policyPath),
    referents: readJson<JsonRecord>(referentsPath),
  };
  if (hostileCase.kind === "raw-descriptor") {
    return {
      descriptor: hostileCase.raw_descriptor!,
      inventory: JSON.stringify(inputs.inventory),
      policy: JSON.stringify(inputs.policy),
      referents: JSON.stringify(inputs.referents),
    };
  }
  const target = inputs[hostileCase.target ?? "descriptor"];
  for (const mutation of hostileCase.mutations ?? []) applyMutation(target, mutation);
  return {
    descriptor: JSON.stringify(inputs.descriptor),
    inventory: JSON.stringify(inputs.inventory),
    policy: JSON.stringify(inputs.policy),
    referents: JSON.stringify(inputs.referents),
  };
}

function evaluate(hostileCase: HostileCase): ToolEvidenceProfileValidationResult {
  const inputs = materialize(hostileCase);
  return validateToolEvidenceProfile({
    descriptor: inputs.descriptor,
    family_inventory: inputs.inventory,
    attribute_policy: inputs.policy,
    referent_inventory: inputs.referents,
    evaluated_at: hostileCase.evaluated_at ?? evaluatedAt,
  });
}

function assertAuthorityCeiling(result: ToolEvidenceProfileValidationResult): void {
  assert.equal(result.runtime_admission, "denied");
  assert.equal(result.referent_trust, "unverified");
  assert.equal(result.authority_effect, "none");
  const output = result as unknown as JsonRecord;
  for (const forbidden of ["normalized_output", "observations", "controls", "eligibility", "deployment_effect"]) {
    assert.equal(Object.hasOwn(output, forbidden), false, forbidden);
  }
}

for (const family of families) {
  test(`${family} golden profile validates without granting runtime authority`, () => {
    const descriptor = readText(resolve(goldenRoot, `${family}.json`));
    const result = validateToolEvidenceProfile({
      descriptor,
      family_inventory: inventoryText,
      attribute_policy: policyText,
      referent_inventory: referentsText,
      evaluated_at: evaluatedAt,
    });
    assert.equal(result.verdict, "pass", JSON.stringify(result.findings));
    assert.equal(result.profile_state, "structurally-valid");
    assert.deepEqual(result.findings, []);
    assert.equal(result.family_id, family);
    assertAuthorityCeiling(result);
  });
}

test("hostile case and expected-result inventories are complete and exact", () => {
  const expected = readJson<{ results: { case_id: string; expected_code: string }[] }>(expectedPath).results;
  assert.equal(new Set(hostile.cases.map(({ case_id }) => case_id)).size, hostile.cases.length);
  assert.deepEqual(
    hostile.cases.map(({ case_id, expected_code }) => ({ case_id, expected_code })),
    expected,
  );
  assert.equal(hostile.authority_effect, "none");
});

for (const hostileCase of hostile.cases.filter(({ kind }) => kind !== "cli")) {
  test(`${hostileCase.case_id} fails closed with its stable discriminator`, () => {
    const materialized = materialize(hostileCase);
    const before = JSON.stringify(materialized);
    const first = evaluate(hostileCase);
    const second = evaluate(hostileCase);
    assert.equal(first.verdict, "reject", hostileCase.case_id);
    assert.equal(first.profile_state, "rejected", hostileCase.case_id);
    assert.ok(first.findings.some(({ code }) => code === hostileCase.expected_code),
      `${hostileCase.case_id}: expected ${hostileCase.expected_code}; got ${first.findings.map(({ code }) => code).join(",")}`);
    assert.deepEqual(first, second, `${hostileCase.case_id}: validator is nondeterministic`);
    assert.equal(JSON.stringify(materialized), before, `${hostileCase.case_id}: input mutated`);
    assert.deepEqual(
      first.findings,
      [...first.findings].sort((left, right) => `${left.path}\u0000${left.code}\u0000${left.detail}`.localeCompare(`${right.path}\u0000${right.code}\u0000${right.detail}`)),
    );
    assertAuthorityCeiling(first);
  });
}

test("all golden and hostile results satisfy the closed validation-result schema", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-profile-result-schema-"));
  try {
    const results: ToolEvidenceProfileValidationResult[] = [];
    for (const family of families) {
      results.push(validateToolEvidenceProfile({
        descriptor: readText(resolve(goldenRoot, `${family}.json`)),
        family_inventory: inventoryText,
        attribute_policy: policyText,
        referent_inventory: referentsText,
        evaluated_at: evaluatedAt,
      }));
    }
    for (const hostileCase of hostile.cases.filter(({ kind }) => kind !== "cli")) results.push(evaluate(hostileCase));
    results.forEach((result, index) => {
      const resultPath = join(scratch, `${index}.json`);
      writeFileSync(resultPath, `${JSON.stringify(result, null, 2)}\n`);
      const check = spawnSync("python3", ["-m", "jsonschema", "-i", resultPath, resultSchemaPath], { encoding: "utf8" });
      assert.equal(check.status, 0, check.stdout + check.stderr);
    });
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("deferred profile families use the exact required discriminator", () => {
  for (const caseId of ["deferred-infrastructure-plan", "deferred-compatibility"]) {
    const hostileCase = hostile.cases.find((item) => item.case_id === caseId)!;
    const result = evaluate(hostileCase);
    assert.ok(result.findings.some(({ code }) => code === "PROFILE_FAMILY_DEFERRED_EXTENSION"));
  }
});
