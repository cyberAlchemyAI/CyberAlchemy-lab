import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import type {
  LegacyV1NormalizationResult,
  LegacyV1SourceInventory,
} from "../contracts/legacy-v1-adapter.js";
import { normalizeLegacyV1 } from "../src/normalize-legacy-v1.js";

type LegacyV1HostileCase = Readonly<{
  schema_version: "domainspec.orodi.legacy-v1-hostile-case/v1";
  case_id: string;
  input: unknown;
  replayed_at: string;
  expected_code: string;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const implRoot = resolve(packageRoot, "..");
const repositoryRoot = resolve(packageRoot, "../../../..");
const goldenRoot = resolve(packageRoot, "fixtures/legacy-v1/golden");
const hostileRoot = resolve(packageRoot, "fixtures/legacy-v1/hostile");
const inventoryPath = resolve(packageRoot, "contracts/legacy-v1-source-inventory.json");
const resultSchemaPath = resolve(packageRoot, "contracts/legacy-v1-normalization-result.schema.json");
const replayedAt = "2026-08-24T20:00:00Z";

const readJson = <T>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;
const inventory = readJson<LegacyV1SourceInventory>(inventoryPath);

const runCli = (inputPath: string, at = replayedAt) => spawnSync(
  process.execPath,
  ["--import", "tsx", "operational-resilience/src/legacy-v1-cli.ts", "normalize", inputPath,
    "--inventory", "operational-resilience/contracts/legacy-v1-source-inventory.json", "--at", at],
  { cwd: implRoot, encoding: "utf8" },
);

for (const stem of ["failure-map", "otel-metric"] as const) {
  test(`${stem} golden replay emits the exact generic observation`, () => {
    const input = readJson<unknown>(resolve(goldenRoot, `${stem}.input.json`));
    const expected = readJson<LegacyV1NormalizationResult>(resolve(goldenRoot, `${stem}.result.json`));
    const before = JSON.stringify(input);
    const result = normalizeLegacyV1(input, inventory, replayedAt);
    assert.deepEqual(result, expected);
    assert.equal(JSON.stringify(input), before, "normalizer mutated its input");
    assert.equal(JSON.stringify(normalizeLegacyV1(input, inventory, replayedAt)), JSON.stringify(result));
    assert.equal(result.authority_effect, "none");
    assert.equal(result.normalized_observations.length, 1);
    const observation = result.normalized_observations[0]!;
    assert.equal(observation.plane, "product");
    assert.equal(observation.mode, "simulation");
    assert.equal(observation.deployment_effect, false);
    assert.equal(observation.independently_observed, false);
    assert.deepEqual(observation.telemetry, {
      offered: 0, queued: 0, exported: 0, rejected: 0, dropped: 0, pending: 0, partial_success: 0,
    });
  });
}

for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
  test(`${filename} is rejected with its exact discriminator`, () => {
    const hostile = readJson<LegacyV1HostileCase>(resolve(hostileRoot, filename));
    assert.equal(hostile.schema_version, "domainspec.orodi.legacy-v1-hostile-case/v1");
    const before = JSON.stringify(hostile.input);
    const result = normalizeLegacyV1(hostile.input, inventory, hostile.replayed_at);
    assert.equal(result.verdict, "rejected", hostile.case_id);
    assert.deepEqual(result.normalized_observations, [], hostile.case_id);
    assert.ok(result.findings.some(({ code }) => code === hostile.expected_code),
      `${hostile.case_id}: expected ${hostile.expected_code}, observed ${result.findings.map(({ code }) => code).join(",")}`);
    assert.equal(JSON.stringify(hostile.input), before, `${hostile.case_id}: input mutated`);
    assert.equal(result.authority_effect, "none");
  });
}

test("all pinned source digests match the current repository bytes", () => {
  assert.equal(inventory.sources.length, 11);
  for (const source of inventory.sources) {
    const bytes = readFileSync(resolve(repositoryRoot, source.path));
    const digest = createHash("sha256").update(bytes).digest("hex");
    assert.equal(digest, source.sha256, source.path);
  }
});

test("every disposition is explicit and only two shapes are normalizable", () => {
  const normalizable = inventory.sources.filter(({ adapter_disposition }) =>
    adapter_disposition === "normalize-as-candidate-local-simulation");
  assert.deepEqual(normalizable.map(({ shape_id }) => shape_id), [
    "legacy-v1.failure-mapping-row/v1",
    "legacy-v1.otel-metric-declaration/v1",
  ]);
  assert.equal(inventory.sources.filter(({ shape_kind }) => shape_kind === "absent-family").length, 2);
  assert.equal(inventory.authority_effect, "none");
});

test("the result schema has an absolute offline identity for local fragment resolution", () => {
  const schema = readJson<{ $id?: string }>(resultSchemaPath);
  assert.equal(schema.$id, "urn:domainspec:orodi:legacy-v1-normalization-result:v1");
  assert.doesNotThrow(() => new URL(schema.$id!));
  assert.equal(new URL(schema.$id!).protocol, "urn:");
});

test("the CLI matches the golden library result and rejects hostile workflow telemetry", () => {
  const goldenRun = runCli("operational-resilience/fixtures/legacy-v1/golden/failure-map.input.json");
  assert.equal(goldenRun.status, 0, goldenRun.stdout + goldenRun.stderr);
  assert.deepEqual(JSON.parse(goldenRun.stdout), readJson(resolve(goldenRoot, "failure-map.result.json")));

  const hostile = readJson<LegacyV1HostileCase>(resolve(hostileRoot, "workflow-telemetry.json"));
  const scratch = mkdtempSync(join(tmpdir(), "orodi-v1-cli-"));
  try {
    const inputPath = join(scratch, "workflow-input.json");
    writeFileSync(inputPath, `${JSON.stringify(hostile.input, null, 2)}\n`);
    const hostileRun = runCli(inputPath);
    assert.equal(hostileRun.status, 1, hostileRun.stdout + hostileRun.stderr);
    const result = JSON.parse(hostileRun.stdout) as LegacyV1NormalizationResult;
    assert.ok(result.findings.some(({ code }) => code === hostile.expected_code));
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("all golden and hostile emitted results satisfy the closed result schema", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-v1-schema-"));
  try {
    const results: LegacyV1NormalizationResult[] = [];
    for (const stem of ["failure-map", "otel-metric"] as const) {
      results.push(normalizeLegacyV1(readJson(resolve(goldenRoot, `${stem}.input.json`)), inventory, replayedAt));
    }
    for (const filename of readdirSync(hostileRoot).filter((name) => name.endsWith(".json")).sort()) {
      const hostile = readJson<LegacyV1HostileCase>(resolve(hostileRoot, filename));
      results.push(normalizeLegacyV1(hostile.input, inventory, hostile.replayed_at));
    }
    results.forEach((result, index) => {
      const resultPath = join(scratch, `result-${index}.json`);
      writeFileSync(resultPath, `${JSON.stringify(result, null, 2)}\n`);
      const check = spawnSync("python3", ["-m", "jsonschema", "-i", resultPath, resultSchemaPath], { encoding: "utf8" });
      assert.equal(check.status, 0, check.stdout + check.stderr);
    });
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});
