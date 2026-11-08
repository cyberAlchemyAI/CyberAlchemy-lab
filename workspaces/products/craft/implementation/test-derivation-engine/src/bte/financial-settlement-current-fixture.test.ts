import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { copyFeatureFixture, projectFeatureDirectory } from "./feature-projector.js";
import {
  FIXTURE_ROOT,
  assessFixtureStructuralCases,
  deriveFixtureStructuralEmission,
  writeFixtureStructuralArtifacts,
} from "./financial-settlement-current-fixture.js";
import { evaluateStructuralCase } from "./structural-emitter.js";

describe("Financial Settlement local fixture structural verifier v2", () => {
  const emission = deriveFixtureStructuralEmission();

  it("binds 52 unique passing cases to the local fixture and keeps the report structural", () => {
    expect(emission.cases).toHaveLength(52);
    expect(new Set(emission.cases.map(({ coverage_key }) => coverage_key)).size).toBe(52);
    expect(emission.results.every(({ status }) => status === "pass")).toBe(true);
    expect(emission.report).toMatchObject({
      schema_version: "bte-financial-settlement-fixture-structural-report/v2",
      scope: "fixture-structural",
      behavioral_authority: false,
      result: "pass",
      structural: { generated: 52, passed: 52, failed: 0, todo: 0, skipped: 0 },
    });
    expect(emission.report.source_files.length).toBeGreaterThan(0);
    expect(emission.report.source_set_digest).toBe(
      createHash("sha256").update(JSON.stringify(emission.report.source_files)).digest("hex"),
    );
    expect(emission.file).toContain('../../test-derivation-engine/__fixtures__/financial-settlement');
    expect(emission.file).not.toContain("expected-red");
    expect((emission.file.match(/\bit\(/g) ?? [])).toHaveLength(52);
    expect(deriveFixtureStructuralEmission().reportBytes).toBe(emission.reportBytes);
  });

  it("rejects Mapping to Event with the original endpoint diagnostic", () => {
    const root = mkdtempSync(resolve(tmpdir(), "fstg-v2-map-event-"));
    copyFeatureFixture(FIXTURE_ROOT, root);
    const specPath = resolve(root, "SPEC.md");
    const source = readFileSync(specPath, "utf8");
    const mutated = source.replace(
      /(\|\s*financial-settlement\.SettlementRequestToInput\s*\|\s*maps\s*\|\s*)financial-settlement\.SettlementResult/u,
      "$1financial-settlement.PayoutCreated",
    );
    expect(mutated).not.toBe(source);
    writeFileSync(specPath, mutated);
    const project = projectFeatureDirectory(root).project;
    const failed = evaluateStructuralCase(project, "edge-instance-conformance@1::financial-settlement.edge.007.maps");
    expect(failed).toMatchObject({ status: "fail", code: "BTE_DEV_EDGE_ENDPOINT_KIND" });
    const cases = emission.cases;
    expect(() => assessFixtureStructuralCases(project, cases, cases.map(({ coverage_key }) => coverage_key))).toThrow("case-failed");
  });

  it("rejects missing and duplicate coverage and a failed result", () => {
    const project = projectFeatureDirectory(FIXTURE_ROOT).project;
    const keys = emission.cases.map(({ coverage_key }) => coverage_key);
    expect(() => assessFixtureStructuralCases(project, emission.cases.slice(1), keys)).toThrow("case-total");
    expect(() => assessFixtureStructuralCases(project, [...emission.cases.slice(1), emission.cases[1]!], keys)).toThrow("BTE_STRUCTURAL_COVERAGE_MISMATCH");
    expect(() => assessFixtureStructuralCases(project, emission.cases, keys, [
      { ...emission.results[0]!, status: "fail" }, ...emission.results.slice(1),
    ])).toThrow("case-failed");
  });

  it("confines output and preserves historical v1 bytes", () => {
    const root = mkdtempSync(resolve(tmpdir(), "fstg-v2-output-"));
    const historical = resolve(root, "financial-settlement.structural.report.json");
    writeFileSync(historical, "historical-v1\n");
    const outputDir = resolve(root, "financial-settlement-current-fixture");
    const written = writeFixtureStructuralArtifacts(emission, root, outputDir);
    expect(readFileSync(written.reportFile, "utf8")).toBe(emission.reportBytes);
    expect(readFileSync(historical, "utf8")).toBe("historical-v1\n");
    expect(() => writeFixtureStructuralArtifacts(emission, root, resolve(root, "..", "escape"))).toThrow("BTE_FIXTURE_OUTPUT_ESCAPE");
  });
});
