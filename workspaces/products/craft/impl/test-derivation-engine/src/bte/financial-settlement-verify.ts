import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import {
  FINANCIAL_SETTLEMENT_EXPECTED_RED,
  deriveFinancialSettlementStructuralEmission,
  writeFinancialSettlementStructuralArtifacts,
} from "./structural-emitter.js";

type AssertionResult = {
  title?: string;
  fullName?: string;
  status?: string;
};

type VitestJson = {
  numTotalTests?: number;
  numPassedTests?: number;
  numFailedTests?: number;
  numPendingTests?: number;
  testResults?: Array<{ assertionResults?: AssertionResult[] }>;
};

function fail(message: string): never {
  throw new Error(`BTE_EXPECTED_RED_VERIFY:${message}`);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const implRoot = resolve(here, "../../..");
  const featureRoot = resolve(
    process.env.FSTG_FEATURE_ROOT ??
      resolve(
        implRoot,
        "../../../validation/poker-team/docs/features/financial-settlement",
      ),
  );
  const bindingsPath = resolve(
    implRoot,
    "test-derivation-engine/bindings/financial-settlement.json",
  );
  const allowedOutputRoot = resolve(implRoot, "generated-tests");
  const outputDir = resolve(allowedOutputRoot, "financial-settlement");

  const first = deriveFinancialSettlementStructuralEmission(
    featureRoot,
    bindingsPath,
  );
  const second = deriveFinancialSettlementStructuralEmission(
    featureRoot,
    bindingsPath,
  );
  if (first.file !== second.file || first.reportBytes !== second.reportBytes) {
    fail("generation is not byte-stable");
  }
  if (first.report.result !== "expected-red") {
    fail("derived report does not contain only the declared red");
  }
  const written = writeFinancialSettlementStructuralArtifacts(
    first,
    allowedOutputRoot,
    outputDir,
  );
  if (
    readFileSync(written.testFile, "utf8") !== first.file ||
    readFileSync(written.reportFile, "utf8") !== first.reportBytes
  ) {
    fail("written output differs from the derived bytes");
  }

  const vitestCli = resolve(implRoot, "node_modules/vitest/vitest.mjs");
  const raw = spawnSync(
    process.execPath,
    [vitestCli, "run", written.testFile, "--reporter=json"],
    {
      cwd: implRoot,
      encoding: "utf8",
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  if (raw.error) fail(raw.error.message);
  if (raw.status === 0) fail("raw Vitest unexpectedly passed");

  let report: VitestJson;
  try {
    report = JSON.parse(raw.stdout) as VitestJson;
  } catch {
    fail(`raw Vitest JSON could not be parsed: ${raw.stderr.trim()}`);
  }
  const failedAssertions = (report.testResults ?? [])
    .flatMap(({ assertionResults = [] }) => assertionResults)
    .filter(({ status }) => status === "failed");
  const failedNames = failedAssertions.map(
    ({ title, fullName }) => title ?? fullName ?? "",
  );
  const countsMatch =
    report.numTotalTests === 52 &&
    report.numPassedTests === 51 &&
    report.numFailedTests === 1 &&
    (report.numPendingTests ?? 0) === 0;
  const exactRed =
    failedNames.length === 1 &&
    failedNames[0] === FINANCIAL_SETTLEMENT_EXPECTED_RED.coverage_key;
  if (!countsMatch || !exactRed) {
    fail(
      JSON.stringify({
        expected: {
          total: 52,
          passed: 51,
          failed: 1,
          pending: 0,
          failedName: FINANCIAL_SETTLEMENT_EXPECTED_RED.coverage_key,
        },
        observed: {
          total: report.numTotalTests,
          passed: report.numPassedTests,
          failed: report.numFailedTests,
          pending: report.numPendingTests,
          failedNames,
        },
      }),
    );
  }
  console.log(
    JSON.stringify({
      schema_version: "bte-expected-red-verification/v1",
      result: "pass",
      generated: 52,
      passed: 51,
      expected_red: {
        ...FINANCIAL_SETTLEMENT_EXPECTED_RED,
        observed: true,
      },
      todo: 0,
      skipped: 0,
      behavioral: first.report.behavioral,
      outputs: written,
    }),
  );
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
