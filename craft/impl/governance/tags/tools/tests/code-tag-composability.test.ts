import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const thisDir = dirname(fileURLToPath(import.meta.url));
const frameworkRoot = resolve(thisDir, "../../../../");

const composabilityScript =
  "governance/tags/tools/check-code-tag-composability.ts";

function runTsxScript(args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", ...args], {
    cwd: frameworkRoot,
    encoding: "utf-8",
  });
}

function writeExtractionFixture(
  tempRoot: string,
  withRuleCall: boolean,
): string {
  const srcDir = join(tempRoot, "src");
  mkdirSync(srcDir, { recursive: true });

  writeFileSync(
    join(srcDir, "rules.ts"),
    [
      "export function maxAmountRule(amount: number, max: number): boolean {",
      "  return amount <= max;",
      "}",
      "",
    ].join("\n"),
    "utf-8",
  );

  const operationBody = withRuleCall
    ? [
        'import { maxAmountRule } from "./rules";',
        "",
        "export function processPayment(amount: number): { ok: true } {",
        "  if (!maxAmountRule(amount, 10000)) {",
        '    throw new Error("MAX_AMOUNT_EXCEEDED");',
        "  }",
        "  return { ok: true };",
        "}",
        "",
      ].join("\n")
    : [
        "export function processPayment(amount: number): { ok: true } {",
        "  if (amount <= 0) {",
        '    throw new Error("INVALID_AMOUNT");',
        "  }",
        "  return { ok: true };",
        "}",
        "",
      ].join("\n");

  writeFileSync(join(srcDir, "operations.ts"), operationBody, "utf-8");

  const extractionPath = join(tempRoot, "code-tags.json");
  writeFileSync(
    extractionPath,
    JSON.stringify(
      {
        meta: {
          generatedAt: new Date().toISOString(),
          mode: "strict",
          include: ["src"],
          root: tempRoot,
        },
        tags: [
          {
            file: "src/rules.ts",
            line: 1,
            symbol: "maxAmountRule",
            language: "ts",
            concept: {
              id: "payment.MaxAmountRule",
              type: "Rule",
            },
            edges: [
              {
                edge: "enforces",
                to: "payment.ProcessPayment",
              },
            ],
          },
          {
            file: "src/operations.ts",
            line: 3,
            symbol: "processPayment",
            language: "ts",
            concept: {
              id: "payment.ProcessPayment",
              type: "Operation",
            },
            edges: [],
          },
        ],
        issues: [],
        stats: {
          scannedFiles: 2,
          taggedSymbols: 2,
          issues: 0,
        },
      },
      null,
      2,
    ) + "\n",
    "utf-8",
  );

  return extractionPath;
}

function writeExposesFixture(
  tempRoot: string,
  withInterfaceCall: boolean,
): string {
  const srcDir = join(tempRoot, "src");
  mkdirSync(srcDir, { recursive: true });

  writeFileSync(
    join(srcDir, "operations.ts"),
    [
      "export async function createRecord(payload: unknown) {",
      "  return { ok: true, payload };",
      "}",
      "",
    ].join("\n"),
    "utf-8",
  );

  const interfaceBody = withInterfaceCall
    ? [
        'import { createRecord } from "./operations";',
        "",
        "export async function postRecordsController(payload: unknown) {",
        "  return createRecord(payload);",
        "}",
        "",
      ].join("\n")
    : [
        "export async function postRecordsController(payload: unknown) {",
        "  return { accepted: true, payload };",
        "}",
        "",
      ].join("\n");

  writeFileSync(join(srcDir, "interface.ts"), interfaceBody, "utf-8");

  const extractionPath = join(tempRoot, "code-tags-exposes.json");
  writeFileSync(
    extractionPath,
    JSON.stringify(
      {
        meta: {
          generatedAt: new Date().toISOString(),
          mode: "strict",
          include: ["src"],
          root: tempRoot,
        },
        tags: [
          {
            file: "src/interface.ts",
            line: 1,
            symbol: "postRecordsController",
            language: "ts",
            concept: {
              id: "catalog.RecordAPI",
              type: "Interface",
            },
            edges: [
              {
                edge: "exposes",
                to: "catalog.CreateRecord",
              },
            ],
          },
          {
            file: "src/operations.ts",
            line: 1,
            symbol: "createRecord",
            language: "ts",
            concept: {
              id: "catalog.CreateRecord",
              type: "Operation",
            },
            edges: [],
          },
        ],
        issues: [],
        stats: {
          scannedFiles: 2,
          taggedSymbols: 2,
          issues: 0,
        },
      },
      null,
      2,
    ) + "\n",
    "utf-8",
  );

  return extractionPath;
}

function writeAuthorityCaseFixture(
  tempRoot: string,
  {
    edge,
    sourceType,
    targetType,
  }: { edge: string; sourceType: string; targetType: string },
): string {
  const srcDir = join(tempRoot, "src");
  mkdirSync(srcDir, { recursive: true });
  writeFileSync(
    join(srcDir, "concepts.ts"),
    [
      "export function sourceConcept() { return true; }",
      "export function targetConcept() { return true; }",
      "",
    ].join("\n"),
    "utf-8",
  );

  const extractionPath = join(tempRoot, `code-tags-${edge}.json`);
  writeFileSync(
    extractionPath,
    JSON.stringify(
      {
        meta: {
          generatedAt: new Date().toISOString(),
          mode: "strict",
          include: ["src"],
          root: tempRoot,
        },
        tags: [
          {
            file: "src/concepts.ts",
            line: 1,
            symbol: "sourceConcept",
            language: "ts",
            concept: {
              id: "authority.Source",
              type: sourceType,
            },
            edges: [
              {
                edge,
                to: "authority.Target",
              },
            ],
          },
          {
            file: "src/concepts.ts",
            line: 2,
            symbol: "targetConcept",
            language: "ts",
            concept: {
              id: "authority.Target",
              type: targetType,
            },
            edges: [],
          },
        ],
        issues: [],
        stats: {
          scannedFiles: 1,
          taggedSymbols: 2,
          issues: 0,
        },
      },
      null,
      2,
    ) + "\n",
    "utf-8",
  );

  return extractionPath;
}

function runAuthorityCase({
  edge,
  sourceType,
  targetType,
}: {
  edge: string;
  sourceType: string;
  targetType: string;
}) {
  const tempRoot = mkdtempSync(
    join(tmpdir(), "domainspec-composability-authority-test-"),
  );
  const extractionPath = writeAuthorityCaseFixture(tempRoot, {
    edge,
    sourceType,
    targetType,
  });
  const result = runTsxScript([
    composabilityScript,
    "--input",
    extractionPath,
    "--mode",
    "strict",
    "--json",
  ]);

  return {
    tempRoot,
    result,
    payload: JSON.parse(result.stdout),
  };
}

test("check-code-tag-composability passes when operation calls enforcing rule", () => {
  const tempRoot = mkdtempSync(
    join(tmpdir(), "domainspec-composability-test-"),
  );

  try {
    const extractionPath = writeExtractionFixture(tempRoot, true);

    const result = runTsxScript([
      composabilityScript,
      "--input",
      extractionPath,
      "--mode",
      "strict",
      "--json",
    ]);

    assert.equal(result.status, 0, result.stderr || result.stdout);
    const payload = JSON.parse(result.stdout);
    assert.equal(payload.ok, true);
    assert.equal(payload.blockingIssues, 0);
    assert.equal(payload.checks, 1);
    assert.equal(payload.passedChecks, 1);
    assert.equal(
      payload.relationshipAuthority,
      "../definitions/relationships/relationships.yml",
    );
    assert.equal(payload.activeSignatureCount, 31);
    assert.equal(payload.generatedViewCount, 1);
    assert.equal(payload.deprecatedCount, 2);
    assert.equal(payload.deferredCount, 3);
    assert.equal(payload.dynamicRuleCount, 9);
    assert.equal(payload.unsupportedActiveSignatureCount, 26);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("check-code-tag-composability fails when operation does not call enforcing rule", () => {
  const tempRoot = mkdtempSync(
    join(tmpdir(), "domainspec-composability-test-"),
  );

  try {
    const extractionPath = writeExtractionFixture(tempRoot, false);

    const result = runTsxScript([
      composabilityScript,
      "--input",
      extractionPath,
      "--mode",
      "strict",
      "--json",
    ]);

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const payload = JSON.parse(result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.blockingIssues > 0, true);
    assert.equal(
      payload.report.some(
        (entry: { code: string }) => entry.code === "CT-COMP-001",
      ),
      true,
    );
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("check-code-tag-composability passes when interface exposes operation via call", () => {
  const tempRoot = mkdtempSync(
    join(tmpdir(), "domainspec-composability-test-"),
  );

  try {
    const extractionPath = writeExposesFixture(tempRoot, true);

    const result = runTsxScript([
      composabilityScript,
      "--input",
      extractionPath,
      "--mode",
      "strict",
      "--json",
    ]);

    assert.equal(result.status, 0, result.stderr || result.stdout);
    const payload = JSON.parse(result.stdout);
    assert.equal(payload.ok, true);
    assert.equal(payload.blockingIssues, 0);
    assert.equal(payload.checks, 1);
    assert.equal(payload.passedChecks, 1);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("check-code-tag-composability fails when interface does not call exposed operation", () => {
  const tempRoot = mkdtempSync(
    join(tmpdir(), "domainspec-composability-test-"),
  );

  try {
    const extractionPath = writeExposesFixture(tempRoot, false);

    const result = runTsxScript([
      composabilityScript,
      "--input",
      extractionPath,
      "--mode",
      "strict",
      "--json",
    ]);

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const payload = JSON.parse(result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.blockingIssues > 0, true);
    assert.equal(
      payload.report.some(
        (entry: { code: string }) => entry.code === "CT-COMP-004",
      ),
      true,
    );
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("generated owned-by is rejected as a noncanonical authored edge", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "owned-by",
    sourceType: "Entity",
    targetType: "Entity",
  });

  try {
    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.blockingIssues, 1);
    assert.equal(payload.report[0]?.code, "CT-COMP-020");
    assert.match(payload.report[0]?.message || "", /not a canonical authored edge/);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("deprecated enforces-cross is rejected with replacement guidance", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "enforces-cross",
    sourceType: "Rule",
    targetType: "Operation",
  });

  try {
    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.report[0]?.code, "CT-COMP-021");
    assert.match(payload.report[0]?.message || "", /use 'enforces'/);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("deprecated queries is rejected with reads replacement guidance", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "queries",
    sourceType: "Query",
    targetType: "Entity",
  });

  try {
    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.report[0]?.code, "CT-COMP-021");
    assert.match(payload.report[0]?.message || "", /use 'reads'/);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("deferred depends-on is rejected as non-active DS-D8 authority", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "depends-on",
    sourceType: "Entity",
    targetType: "Entity",
  });

  try {
    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.report[0]?.code, "CT-COMP-022");
    assert.match(payload.report[0]?.message || "", /not active DS-D8 authority/);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("active enforces with wrong endpoints is rejected as unconstructible", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "enforces",
    sourceType: "Operation",
    targetType: "Value Object",
  });

  try {
    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.equal(payload.ok, false);
    assert.equal(payload.report[0]?.code, "CT-COMP-023");
    assert.match(payload.report[0]?.message || "", /Unconstructible DS-D8 endpoint/);
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});

test("active performs without call semantics reports a non-blocking coverage gap", () => {
  const { tempRoot, result, payload } = runAuthorityCase({
    edge: "performs",
    sourceType: "Entity",
    targetType: "Operation",
  });

  try {
    assert.equal(result.status, 0, result.stderr || result.stdout);
    assert.equal(payload.ok, true);
    assert.equal(payload.blockingIssues, 0);
    assert.equal(payload.report[0]?.code, "CT-COMP-024");
    assert.match(payload.report[0]?.message || "", /coverage gap/);
    assert.equal(
      payload.unsupportedActiveSignatures.includes(
        "performs:entity->operation",
      ),
      true,
    );
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});
