import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  EVIDENCE_STATES,
  type EvidenceState,
  type OperationalEvaluationBundle,
} from "../contracts/operational-evidence.js";
import { validateOperationalEvidence } from "../src/validate-operational-evidence.js";

type JsonRecord = Record<string, unknown>;
type HostileCase = Readonly<{
  schema_version: "domainspec.orodi.hostile-case/v1";
  hostile_id: string;
  base_ref: string;
  mutation: Readonly<{ op: "replace" | "delete"; path: string; value?: unknown }>;
  expected_code: string;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const implRoot = resolve(packageRoot, "..");
const validPath = resolve(packageRoot, "fixtures/valid/c01-c16-pass.json");
const hostileRoot = resolve(packageRoot, "fixtures/hostile");
const evaluationAt = "2026-08-24T18:00:00Z";

const readJson = <T>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const applyMutation = (base: unknown, mutation: HostileCase["mutation"]): unknown => {
  const target = clone(base) as JsonRecord;
  const segments = mutation.path.split("/").slice(1).map((segment) => segment.replaceAll("~1", "/").replaceAll("~0", "~"));
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
  return target;
};

const runCli = (fixturePath: string) => spawnSync(
  process.execPath,
  ["--import", "tsx", "operational-resilience/src/cli.ts", "validate", fixturePath, "--at", evaluationAt],
  { cwd: implRoot, encoding: "utf8" },
);

test("the complete synthetic C01-C16 bundle passes with no authority effect", () => {
  const bundle = readJson<OperationalEvaluationBundle>(validPath);
  const result = validateOperationalEvidence(bundle, evaluationAt);
  assert.equal(result.verdict, "pass");
  assert.equal(result.claim_state, "passed");
  assert.equal(result.required_control_states.length, 16);
  assert.deepEqual(result.findings, []);
  assert.equal(result.evidence_lane, "candidate-local-prototype");
  assert.equal(result.authority_effect, "none");
});

test("identical input bytes and evaluation time yield identical JSON", () => {
  const bundle = readJson<unknown>(validPath);
  const first = JSON.stringify(validateOperationalEvidence(bundle, evaluationAt));
  const second = JSON.stringify(validateOperationalEvidence(bundle, evaluationAt));
  assert.equal(first, second);
});

test("all seven evidence states remain individually visible", () => {
  const base = readJson<OperationalEvaluationBundle>(validPath);
  for (const state of EVIDENCE_STATES) {
    const bundle = clone(base) as unknown as { controls: Array<{ state: EvidenceState }> };
    bundle.controls[0]!.state = state;
    const result = validateOperationalEvidence(bundle, evaluationAt);
    assert.equal(result.required_control_states[0]?.state, state);
    assert.equal(result.claim_state, state);
    assert.equal(result.verdict, state === "passed" ? "pass" : "reject");
  }
});

for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
  test(`${filename} is rejected with its exact discriminator`, () => {
    const hostilePath = resolve(hostileRoot, filename);
    const hostile = readJson<HostileCase>(hostilePath);
    assert.equal(hostile.schema_version, "domainspec.orodi.hostile-case/v1");
    const base = readJson<unknown>(resolve(dirname(hostilePath), hostile.base_ref));
    const result = validateOperationalEvidence(applyMutation(base, hostile.mutation), evaluationAt);
    assert.equal(result.verdict, "reject");
    assert.ok(result.findings.some(({ code }) => code === hostile.expected_code),
      `${hostile.hostile_id}: expected ${hostile.expected_code}, observed ${result.findings.map(({ code }) => code).join(",")}`);
    assert.equal(result.authority_effect, "none");
  });
}

test("the CLI passes the valid bundle and rejects every raw hostile descriptor", () => {
  const valid = runCli("operational-resilience/fixtures/valid/c01-c16-pass.json");
  assert.equal(valid.status, 0, valid.stdout + valid.stderr);
  const result = JSON.parse(valid.stdout) as { verdict: string; authority_effect: string };
  assert.equal(result.verdict, "pass");
  assert.equal(result.authority_effect, "none");
  for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
    const hostile = runCli(`operational-resilience/fixtures/hostile/${filename}`);
    assert.notEqual(hostile.status, 0, `${filename} unexpectedly passed\n${hostile.stdout}${hostile.stderr}`);
  }
});

test("the accepted bundle and emitted result satisfy their JSON Schemas", () => {
  const bundleSchema = resolve(packageRoot, "contracts/evaluation-bundle.schema.json");
  const resultSchema = resolve(packageRoot, "contracts/evaluation-result.schema.json");
  const bundleCheck = spawnSync("python3", ["-m", "jsonschema", "-i", validPath, bundleSchema], { encoding: "utf8" });
  assert.equal(bundleCheck.status, 0, bundleCheck.stdout + bundleCheck.stderr);

  const runRoot = mkdtempSync(join(tmpdir(), "orodi-result-"));
  try {
    const resultPath = join(runRoot, "result.json");
    writeFileSync(resultPath, `${JSON.stringify(validateOperationalEvidence(readJson(validPath), evaluationAt), null, 2)}\n`);
    const resultCheck = spawnSync("python3", ["-m", "jsonschema", "-i", resultPath, resultSchema], { encoding: "utf8" });
    assert.equal(resultCheck.status, 0, resultCheck.stdout + resultCheck.stderr);
  } finally {
    rmSync(runRoot, { recursive: true, force: true });
  }
});
