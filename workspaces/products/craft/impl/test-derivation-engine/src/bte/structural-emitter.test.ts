import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import ts from "typescript";
import { describe, expect, it } from "vitest";

import {
  FINANCIAL_SETTLEMENT_EXPECTED_RED,
  deriveFinancialSettlementStructuralEmission,
  writeFinancialSettlementStructuralArtifacts,
} from "./structural-emitter.js";

const here = dirname(fileURLToPath(import.meta.url));
const featureRoot = resolve(
  process.env.FSTG_FEATURE_ROOT ??
    resolve(
      here,
      "../../../../../../validation/poker-team/docs/features/financial-settlement",
    ),
);
const bindingsPath = resolve(
  here,
  "../../bindings/financial-settlement.json",
);

describe("Financial Settlement structural emitter", () => {
  const emission = deriveFinancialSettlementStructuralEmission(
    featureRoot,
    bindingsPath,
  );

  it("materializes the exact 52-case catalogue union and the one declared red", () => {
    expect(emission.projection.census).toEqual({
      nodes: 10,
      kinds: 9,
      edges: 7,
      families: 6,
    });
    expect(emission.cases).toHaveLength(52);
    expect(new Set(emission.cases.map(({ coverage_key }) => coverage_key)).size)
      .toBe(52);
    expect(emission.report.structural).toMatchObject({
      generated: 52,
      passed: 51,
      failed: 1,
      todo: 0,
      skipped: 0,
    });
    expect(emission.report.structural.failed_cases).toEqual([
      expect.objectContaining(FINANCIAL_SETTLEMENT_EXPECTED_RED),
    ]);
    expect(emission.report.result).toBe("expected-red");
  });

  it("keeps behavioral evidence separate and unchanged", () => {
    expect(emission.report.behavioral).toEqual({
      total: 79,
      assertions: 12,
      properties: 1,
      coverage_gaps: 67,
    });
  });

  it("renders 52 runnable, source-anchored cases with no todo or skip", () => {
    expect((emission.file.match(/\bit\(/g) ?? [])).toHaveLength(52);
    expect(emission.file).not.toContain("it.todo(");
    expect(emission.file).not.toContain("it.skip(");
    for (const testCase of emission.cases) {
      expect(testCase.source_anchor).not.toBe("");
      expect(emission.file).toContain(
        `// coverage_key: ${testCase.coverage_key}`,
      );
      expect(emission.file).toContain(`// source: ${testCase.source_anchor}`);
    }
    const transpiled = ts.transpileModule(emission.file, {
      compilerOptions: {
        module: ts.ModuleKind.ESNext,
        target: ts.ScriptTarget.ES2022,
      },
      reportDiagnostics: true,
    });
    expect(
      (transpiled.diagnostics ?? []).filter(
        ({ category }) => category === ts.DiagnosticCategory.Error,
      ),
    ).toEqual([]);
  });

  it("is byte-stable across repeated derivation", () => {
    const again = deriveFinancialSettlementStructuralEmission(
      featureRoot,
      bindingsPath,
    );
    expect(again.file).toBe(emission.file);
    expect(again.reportBytes).toBe(emission.reportBytes);
  });

  it("writes only below the declared generated-output root", () => {
    const allowedRoot = mkdtempSync(
      resolve(tmpdir(), "fstg-structural-allowed-"),
    );
    const outputDir = resolve(allowedRoot, "financial-settlement");
    const written = writeFinancialSettlementStructuralArtifacts(
      emission,
      allowedRoot,
      outputDir,
    );
    expect(readFileSync(written.testFile, "utf8")).toBe(emission.file);
    expect(readFileSync(written.reportFile, "utf8")).toBe(
      emission.reportBytes,
    );
    expect(() =>
      writeFinancialSettlementStructuralArtifacts(
        emission,
        allowedRoot,
        resolve(allowedRoot, "..", "escape"),
      ),
    ).toThrow("BTE_STRUCTURAL_OUTPUT_ESCAPE");
  });
});
