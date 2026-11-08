import { spawnSync } from "node:child_process";
import { existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

import type { DevelopmentProject } from "./development-engine.js";
import { projectFeatureDirectory } from "./feature-projector.js";
import {
  assertExactStructuralCoverage,
  evaluateStructuralCase,
  materializeStructuralTestCases,
  type StructuralCaseResult,
  type StructuralTestCase,
} from "./structural-emitter.js";
import { sha256 } from "./validation/validate-semantics.js";

const implRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
export const FIXTURE_ROOT = resolve(implRoot, "test-derivation-engine/__fixtures__/financial-settlement");
export const FIXTURE_OUTPUT_ROOT = resolve(implRoot, "generated-tests");
export const FIXTURE_OUTPUT_DIR = resolve(FIXTURE_OUTPUT_ROOT, "financial-settlement-current-fixture");
const TOTAL = 52;

export type FixtureStructuralReport = {
  schema_version: "bte-financial-settlement-fixture-structural-report/v2";
  project_id: "financial-settlement";
  source: "test-derivation-engine/__fixtures__/financial-settlement";
  source_files: Array<{ path: string; sha256: string }>;
  source_set_digest: string;
  scope: "fixture-structural";
  behavioral_authority: false;
  result: "pass";
  structural: {
    generated: 52;
    passed: 52;
    failed: 0;
    todo: 0;
    skipped: 0;
    coverage_keys: string[];
    failed_cases: [];
  };
  open_questions: ["Application behavior and production source conformance remain outside this fixture verifier."];
};

function requireFixture(condition: unknown, code: string): asserts condition {
  if (!condition) throw new Error(`BTE_FIXTURE_STRUCTURAL_INVALID:${code}`);
}

export function assessFixtureStructuralCases(
  project: DevelopmentProject,
  cases: readonly StructuralTestCase[],
  expectedKeys: readonly string[],
  results: readonly StructuralCaseResult[] = cases.map(({ coverage_key }) => evaluateStructuralCase(project, coverage_key)),
): void {
  requireFixture(cases.length === TOTAL && expectedKeys.length === TOTAL, "case-total");
  assertExactStructuralCoverage(expectedKeys, cases);
  requireFixture(new Set(expectedKeys).size === TOTAL, "expected-duplicate");
  requireFixture(results.length === TOTAL, "result-total");
  requireFixture(
    results.every((result, index) =>
      result.coverage_key === cases[index]?.coverage_key &&
      result.status === "pass" && result.code === "BTE_PROOF_PASS"),
    "case-failed",
  );
}

export function renderFixtureStructuralVitest(cases: readonly StructuralTestCase[]): string {
  const keys = cases.map(({ coverage_key }) => coverage_key);
  const rows = cases.flatMap(({ coverage_key, source_anchor }) => [
    `  // coverage_key: ${coverage_key.replace(/\r?\n/g, " ").replace(/\*\//g, "* /")}`,
    `  // source: ${source_anchor.replace(/\r?\n/g, " ").replace(/\*\//g, "* /")}`,
    `  it(${JSON.stringify(coverage_key)}, () => {`,
    `    const result = evaluateStructuralCase(projection.project, ${JSON.stringify(coverage_key)});`,
    '    expect(result.status).toBe("pass");',
    '    expect(result.code).toBe("BTE_PROOF_PASS");',
    "  });",
  ]);
  return [
    "// AUTO-GENERATED: local Financial Settlement fixture structural cases, v2.",
    'import { dirname, resolve } from "node:path";',
    'import { fileURLToPath } from "node:url";',
    'import { describe, expect, it } from "vitest";',
    'import { projectFeatureDirectory } from "../../test-derivation-engine/src/bte/feature-projector.js";',
    'import { assertExactStructuralCoverage, evaluateStructuralCase, materializeStructuralTestCases } from "../../test-derivation-engine/src/bte/structural-emitter.js";',
    "",
    'const fixtureRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../test-derivation-engine/__fixtures__/financial-settlement");',
    "const projection = projectFeatureDirectory(fixtureRoot);",
    'expect(projection.diagnostics).toEqual([]);',
    'expect(projection.conformance_diagnostics).toEqual([]);',
    `const expectedCoverageKeys = ${JSON.stringify(keys, null, 2)} as const;`,
    "assertExactStructuralCoverage(expectedCoverageKeys, materializeStructuralTestCases(projection.project));",
    "",
    'describe("Financial Settlement local fixture structural conformance", () => {',
    ...rows,
    "});",
    "",
  ].join("\n");
}

export function deriveFixtureStructuralEmission(featureRoot = FIXTURE_ROOT): {
  cases: StructuralTestCase[];
  results: StructuralCaseResult[];
  file: string;
  report: FixtureStructuralReport;
  reportBytes: string;
} {
  requireFixture(realpathSync(featureRoot) === realpathSync(FIXTURE_ROOT), "source-binding");
  const sourceEntries = readdirSync(featureRoot, { withFileTypes: true });
  requireFixture(sourceEntries.every((entry) => entry.isFile()), "source-entry-type");
  const sourceFiles = sourceEntries
    .map((entry) => ({ path: entry.name, sha256: sha256(readFileSync(resolve(featureRoot, entry.name))) }))
    .sort((left, right) => left.path.localeCompare(right.path));
  const projection = projectFeatureDirectory(featureRoot);
  requireFixture(projection.diagnostics.length === 0, "projection-diagnostics");
  requireFixture(projection.conformance_diagnostics.length === 0, "conformance-diagnostics");
  const cases = materializeStructuralTestCases(projection.project);
  const expectedKeys = cases.map(({ coverage_key }) => coverage_key);
  const results = cases.map(({ coverage_key }) => evaluateStructuralCase(projection.project, coverage_key));
  assessFixtureStructuralCases(projection.project, cases, expectedKeys, results);
  const report: FixtureStructuralReport = {
    schema_version: "bte-financial-settlement-fixture-structural-report/v2",
    project_id: "financial-settlement",
    source: "test-derivation-engine/__fixtures__/financial-settlement",
    source_files: sourceFiles,
    source_set_digest: sha256(JSON.stringify(sourceFiles)),
    scope: "fixture-structural",
    behavioral_authority: false,
    result: "pass",
    structural: {
      generated: TOTAL,
      passed: TOTAL,
      failed: 0,
      todo: 0,
      skipped: 0,
      coverage_keys: expectedKeys,
      failed_cases: [],
    },
    open_questions: ["Application behavior and production source conformance remain outside this fixture verifier."],
  };
  return { cases, results, file: renderFixtureStructuralVitest(cases), report, reportBytes: `${JSON.stringify(report, null, 2)}\n` };
}

function containedOutput(allowedRoot: string, outputDir: string): string {
  mkdirSync(allowedRoot, { recursive: true });
  const root = realpathSync(allowedRoot);
  const candidate = resolve(outputDir);
  const relation = relative(root, candidate);
  if (relation === ".." || relation.startsWith(`..${sep}`) || relation === "") {
    throw new Error(`BTE_FIXTURE_OUTPUT_ESCAPE:${outputDir}`);
  }
  mkdirSync(candidate, { recursive: true });
  const physical = realpathSync(candidate);
  const physicalRelation = relative(root, physical);
  if (physicalRelation === ".." || physicalRelation.startsWith(`..${sep}`) || physicalRelation === "") {
    throw new Error(`BTE_FIXTURE_OUTPUT_ESCAPE:${outputDir}`);
  }
  return physical;
}

export function writeFixtureStructuralArtifacts(
  emission: ReturnType<typeof deriveFixtureStructuralEmission>,
  allowedRoot = FIXTURE_OUTPUT_ROOT,
  outputDir = FIXTURE_OUTPUT_DIR,
): { testFile: string; reportFile: string; testSha256: string; reportSha256: string } {
  const directory = containedOutput(allowedRoot, outputDir);
  const testFile = resolve(directory, "financial-settlement.fixture-structural.test.ts");
  const reportFile = resolve(directory, "financial-settlement.fixture-structural.report.json");
  for (const path of [testFile, reportFile]) {
    if (existsSync(path) && !lstatSync(path).isFile()) throw new Error(`BTE_FIXTURE_OUTPUT_ESCAPE:${path}`);
  }
  writeFileSync(testFile, emission.file, "utf8");
  writeFileSync(reportFile, emission.reportBytes, "utf8");
  return { testFile, reportFile, testSha256: sha256(readFileSync(testFile)), reportSha256: sha256(readFileSync(reportFile)) };
}

type VitestJson = {
  numTotalTests?: number;
  numPassedTests?: number;
  numFailedTests?: number;
  numPendingTests?: number;
};

export function verifyFixtureStructural(): { report: FixtureStructuralReport; outputs: ReturnType<typeof writeFixtureStructuralArtifacts>; vitest: VitestJson } {
  const first = deriveFixtureStructuralEmission();
  const second = deriveFixtureStructuralEmission();
  requireFixture(first.file === second.file && first.reportBytes === second.reportBytes, "byte-stability");
  const outputs = writeFixtureStructuralArtifacts(first);
  requireFixture(readFileSync(outputs.testFile, "utf8") === first.file, "test-bytes");
  requireFixture(readFileSync(outputs.reportFile, "utf8") === first.reportBytes, "report-bytes");
  const cli = resolve(implRoot, "node_modules/vitest/vitest.mjs");
  const raw = spawnSync(process.execPath, [cli, "run", outputs.testFile, "--reporter=json"], {
    cwd: implRoot, encoding: "utf8", maxBuffer: 16 * 1024 * 1024,
  });
  requireFixture(!raw.error && raw.status === 0, `vitest-process:${raw.error?.message ?? raw.stderr.trim()}`);
  let vitest: VitestJson;
  try { vitest = JSON.parse(raw.stdout) as VitestJson; }
  catch { throw new Error(`BTE_FIXTURE_STRUCTURAL_INVALID:vitest-json:${raw.stdout.slice(0, 200)}`); }
  requireFixture(
    vitest.numTotalTests === TOTAL && vitest.numPassedTests === TOTAL &&
    vitest.numFailedTests === 0 && (vitest.numPendingTests ?? 0) === 0,
    "vitest-counts",
  );
  return { report: first.report, outputs, vitest };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const { report, outputs, vitest } = verifyFixtureStructural();
    process.stdout.write(`${JSON.stringify({ report, outputs, vitest: {
      total: vitest.numTotalTests, passed: vitest.numPassedTests,
      failed: vitest.numFailedTests, pending: vitest.numPendingTests ?? 0,
    } }, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
