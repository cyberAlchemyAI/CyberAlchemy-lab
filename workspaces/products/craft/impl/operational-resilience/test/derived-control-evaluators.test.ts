import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  FOUNDATIONAL_CONTROL_IDS,
  type EvidenceState,
  type FoundationalControlId,
  type OperationalEvaluationBundle,
} from "../contracts/operational-evidence.js";
import {
  deriveOperationalControls,
  validateOperationalEvidence,
} from "../src/validate-operational-evidence.js";

type JsonRecord = Record<string, unknown>;
type Mutation = Readonly<{
  op: "replace" | "delete";
  path: string;
  value?: unknown;
}>;
type DerivedCase = Readonly<{
  schema_version: "domainspec.orodi.derived-hostile-case/v1";
  case_id: string;
  base_ref: string;
  mutations: readonly Mutation[];
  expected: Readonly<{
    control_id?: FoundationalControlId;
    state?: EvidenceState;
    comparison: "match" | "mismatch" | "unavailable";
    verdict: "pass" | "reject";
    code: string;
  }>;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const implRoot = resolve(packageRoot, "..");
const validPath = resolve(packageRoot, "fixtures/valid/c01-c16-pass.json");
const derivationRoot = resolve(packageRoot, "fixtures/derivation");
const evaluationAt = "2026-08-24T18:00:00Z";

const readJson = <T>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

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

const materialize = (casePath: string, derivedCase: DerivedCase): unknown => {
  const target = clone(readJson<JsonRecord>(resolve(dirname(casePath), derivedCase.base_ref)));
  derivedCase.mutations.forEach((mutation) => applyMutation(target, mutation));
  return target;
};

const observedCodes = (result: ReturnType<typeof deriveOperationalControls>): string[] => [
  ...result.findings.map(({ code }) => code),
  ...result.derived_controls.flatMap(({ findings }) => findings.map(({ code }) => code)),
  ...result.mismatches.map(({ code }) => code),
];

const runCli = (mode: "validate" | "derive", fixturePath: string) => spawnSync(
  process.execPath,
  ["--import", "tsx", "operational-resilience/src/cli.ts", mode, fixturePath, "--at", evaluationAt],
  { cwd: implRoot, encoding: "utf8" },
);

test("the accepted bundle derives the exact foundational denominator", () => {
  const result = deriveOperationalControls(readJson<unknown>(validPath), evaluationAt);
  assert.equal(result.verdict, "pass");
  assert.equal(result.comparison, "match");
  assert.deepEqual(result.derived_controls.map(({ control_id }) => control_id), FOUNDATIONAL_CONTROL_IDS);
  assert.deepEqual(result.derived_controls.map(({ state }) => state), FOUNDATIONAL_CONTROL_IDS.map(() => "passed"));
  assert.deepEqual(result.mismatches, []);
  assert.deepEqual(result.findings, []);
  assert.equal(result.authority_effect, "none");
});

test("derivation is pure and does not mutate its input", () => {
  const bundle = readJson<OperationalEvaluationBundle>(validPath);
  const before = JSON.stringify(bundle);
  deriveOperationalControls(bundle, evaluationAt);
  assert.equal(JSON.stringify(bundle), before);
});

test("identical facts and evaluation time emit byte-identical derived JSON", () => {
  const bundle = readJson<unknown>(validPath);
  assert.equal(
    JSON.stringify(deriveOperationalControls(bundle, evaluationAt)),
    JSON.stringify(deriveOperationalControls(bundle, evaluationAt)),
  );
});

for (const filename of readdirSync(derivationRoot).filter((name) => name.endsWith(".json")).sort()) {
  test(`${filename} derives its exact discriminator`, () => {
    const casePath = resolve(derivationRoot, filename);
    const derivedCase = readJson<DerivedCase>(casePath);
    assert.equal(derivedCase.schema_version, "domainspec.orodi.derived-hostile-case/v1");
    const result = deriveOperationalControls(materialize(casePath, derivedCase), evaluationAt);
    assert.equal(result.verdict, derivedCase.expected.verdict, derivedCase.case_id);
    assert.equal(result.comparison, derivedCase.expected.comparison, derivedCase.case_id);
    if (derivedCase.expected.control_id !== undefined) {
      const receipt = result.derived_controls.find(({ control_id }) =>
        control_id === derivedCase.expected.control_id);
      assert.ok(receipt, `${derivedCase.case_id}: missing derived receipt`);
      assert.equal(receipt.state, derivedCase.expected.state, derivedCase.case_id);
    }
    assert.ok(
      observedCodes(result).includes(derivedCase.expected.code),
      `${derivedCase.case_id}: expected ${derivedCase.expected.code}, observed ${observedCodes(result).join(",")}`,
    );
    assert.equal(result.authority_effect, "none");
  });
}

test("the derive CLI passes the accepted facts", () => {
  const run = runCli("derive", "operational-resilience/fixtures/valid/c01-c16-pass.json");
  assert.equal(run.status, 0, run.stdout + run.stderr);
  const result = JSON.parse(run.stdout) as { verdict: string; comparison: string; authority_effect: string };
  assert.equal(result.verdict, "pass");
  assert.equal(result.comparison, "match");
  assert.equal(result.authority_effect, "none");
});

test("the original validator and CLI reject a forged supplied state", () => {
  const casePath = resolve(derivationRoot, "claimed-state-forgery.json");
  const derivedCase = readJson<DerivedCase>(casePath);
  const forged = materialize(casePath, derivedCase);
  const result = validateOperationalEvidence(forged, evaluationAt);
  assert.equal(result.verdict, "reject");
  assert.ok(result.findings.some(({ code }) => code === "ORODI_DERIVED_CONTROL_STATE_MISMATCH"));

  const scratch = mkdtempSync(join(tmpdir(), "orodi-derived-forgery-"));
  try {
    const fixturePath = join(scratch, "forged.json");
    writeFileSync(fixturePath, `${JSON.stringify(forged, null, 2)}\n`);
    const run = runCli("validate", fixturePath);
    assert.equal(run.status, 1, run.stdout + run.stderr);
    const cliResult = JSON.parse(run.stdout) as { findings: Array<{ code: string }> };
    assert.ok(cliResult.findings.some(({ code }) => code === "ORODI_DERIVED_CONTROL_STATE_MISMATCH"));
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the emitted derived result satisfies its closed JSON Schema", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-derived-schema-"));
  try {
    const resultPath = join(scratch, "derived-result.json");
    const schemaPath = resolve(packageRoot, "contracts/derived-control-result.schema.json");
    writeFileSync(resultPath, `${JSON.stringify(deriveOperationalControls(readJson(validPath), evaluationAt), null, 2)}\n`);
    const check = spawnSync("python3", ["-m", "jsonschema", "-i", resultPath, schemaPath], { encoding: "utf8" });
    assert.equal(check.status, 0, check.stdout + check.stderr);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});
