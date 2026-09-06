import {
  mkdirSync,
  readFileSync,
  realpathSync,
  writeFileSync,
} from "node:fs";
import { relative, resolve, sep } from "node:path";

import { loadBindings } from "../bindings/index.js";
import { emitHybridTests } from "../emit/tests.js";
import { parse } from "../grammar/index.js";
import { derive } from "../rules/index.js";
import {
  validateDevelopmentEdge,
  validateDevelopmentNode,
  type DevelopmentDiagnostic,
  type DevelopmentProject,
} from "./development-engine.js";
import {
  projectFeatureDirectory,
  type FeatureProjection,
} from "./feature-projector.js";
import {
  createDevelopmentSpecCatalogues,
  type DevelopmentObligation,
  type DevelopmentTestCase,
} from "./proof-engine.js";
import { sha256 } from "./validation/validate-semantics.js";

export const FINANCIAL_SETTLEMENT_STRUCTURAL_TOTAL = 52;
export const FINANCIAL_SETTLEMENT_EXPECTED_RED = {
  coverage_key:
    "edge-instance-conformance@1::financial-settlement.edge.007.maps",
  code: "BTE_DEV_EDGE_ENDPOINT_KIND",
} as const;

export type StructuralTestCase = DevelopmentTestCase & {
  source_anchor: string;
};

export type StructuralCaseResult = {
  coverage_key: string;
  source_anchor: string;
  status: "pass" | "fail";
  code:
    | "BTE_PROOF_PASS"
    | "BTE_PROOF_SUBJECT_MISSING"
    | "BTE_PROOF_SUBJECT_INVALID"
    | DevelopmentDiagnostic["code"];
  diagnostics: DevelopmentDiagnostic[];
};

export type FinancialSettlementStructuralReport = {
  schema_version: "bte-financial-settlement-structural-report/v1";
  project_id: "financial-settlement";
  result: "expected-red" | "unexpected";
  structural: {
    generated: number;
    passed: number;
    failed: number;
    todo: 0;
    skipped: 0;
    coverage_keys: string[];
    failed_cases: Array<{
      coverage_key: string;
      source_anchor: string;
      code: StructuralCaseResult["code"];
    }>;
  };
  expected_red: {
    coverage_key: typeof FINANCIAL_SETTLEMENT_EXPECTED_RED.coverage_key;
    code: typeof FINANCIAL_SETTLEMENT_EXPECTED_RED.code;
    observed: boolean;
  };
  behavioral: {
    total: number;
    assertions: number;
    properties: number;
    coverage_gaps: number;
  };
};

export type FinancialSettlementStructuralEmission = {
  projection: FeatureProjection;
  cases: StructuralTestCase[];
  results: StructuralCaseResult[];
  file: string;
  report: FinancialSettlementStructuralReport;
  reportBytes: string;
};

export type WrittenStructuralArtifacts = {
  testFile: string;
  reportFile: string;
  testSha256: string;
  reportSha256: string;
};

function sourceAnchor(
  project: DevelopmentProject,
  obligation: DevelopmentObligation,
): string {
  if (obligation.subject_type === "node") {
    return (
      project.nodes.find(({ node_id }) => node_id === obligation.subject_id)
        ?.source_anchor ?? `node:${obligation.subject_id}`
    );
  }
  if (obligation.subject_type === "edge") {
    return (
      project.edges.find(({ edge_id }) => edge_id === obligation.subject_id)
        ?.source_anchor ?? `edge:${obligation.subject_id}`
    );
  }
  if (obligation.subject_type === "kind") {
    return (
      project.nodes.find(({ kind }) => kind === obligation.subject_id)
        ?.source_anchor ?? `kind:${obligation.subject_id}`
    );
  }
  return (
    project.edges.find(({ family }) => family === obligation.subject_id)
      ?.source_anchor ?? `relationship:${obligation.subject_id}`
  );
}

export function materializeStructuralTestCases(
  project: DevelopmentProject,
): StructuralTestCase[] {
  return createDevelopmentSpecCatalogues(project).flatMap(({ members }) =>
    members.map((obligation) => ({
      schema_version: "bte-development-test-case/v1" as const,
      test_id: `test/${obligation.coverage_key}`,
      coverage_key: obligation.coverage_key,
      subject_type: obligation.subject_type,
      subject_id: obligation.subject_id,
      expected_result: "present-and-valid" as const,
      mutation: {
        operation: "remove-subject" as const,
        expected_code: "BTE_PROOF_SUBJECT_MISSING" as const,
      },
      source_anchor: sourceAnchor(project, obligation),
    })),
  );
}

function memberFor(
  project: DevelopmentProject,
  coverageKey: string,
): DevelopmentObligation | null {
  return (
    createDevelopmentSpecCatalogues(project)
      .flatMap(({ members }) => members)
      .find(({ coverage_key }) => coverage_key === coverageKey) ?? null
  );
}

export function evaluateStructuralCase(
  project: DevelopmentProject,
  coverageKey: string,
): StructuralCaseResult {
  const obligation = memberFor(project, coverageKey);
  if (!obligation) {
    return {
      coverage_key: coverageKey,
      source_anchor: `coverage:${coverageKey}`,
      status: "fail",
      code: "BTE_PROOF_SUBJECT_MISSING",
      diagnostics: [],
    };
  }
  const anchor = sourceAnchor(project, obligation);
  if (obligation.subject_type === "kind") {
    const nodes = project.nodes.filter(
      ({ kind }) => kind === obligation.subject_id,
    );
    const pass =
      nodes.length > 0 &&
      nodes.every(({ kind }) => kind === obligation.expected_kind);
    return {
      coverage_key: coverageKey,
      source_anchor: anchor,
      status: pass ? "pass" : "fail",
      code: pass ? "BTE_PROOF_PASS" : "BTE_PROOF_SUBJECT_INVALID",
      diagnostics: [],
    };
  }
  if (obligation.subject_type === "node") {
    const node = project.nodes.find(
      ({ node_id }) => node_id === obligation.subject_id,
    );
    if (!node) {
      return {
        coverage_key: coverageKey,
        source_anchor: anchor,
        status: "fail",
        code: "BTE_PROOF_SUBJECT_MISSING",
        diagnostics: [],
      };
    }
    const validation = validateDevelopmentNode(node);
    const pass =
      node.kind === obligation.expected_kind &&
      validation.result === "pass";
    return {
      coverage_key: coverageKey,
      source_anchor: anchor,
      status: pass ? "pass" : "fail",
      code: pass
        ? "BTE_PROOF_PASS"
        : (validation.diagnostics[0]?.code ?? "BTE_PROOF_SUBJECT_INVALID"),
      diagnostics: validation.diagnostics,
    };
  }
  if (obligation.subject_type === "relationship") {
    const edges = project.edges.filter(
      ({ family }) => family === obligation.subject_id,
    );
    const pass =
      edges.length > 0 &&
      edges.every(
        ({ family }) => family === obligation.expected_relationship,
      );
    return {
      coverage_key: coverageKey,
      source_anchor: anchor,
      status: pass ? "pass" : "fail",
      code: pass ? "BTE_PROOF_PASS" : "BTE_PROOF_SUBJECT_INVALID",
      diagnostics: [],
    };
  }
  const edge = project.edges.find(
    ({ edge_id }) => edge_id === obligation.subject_id,
  );
  if (!edge) {
    return {
      coverage_key: coverageKey,
      source_anchor: anchor,
      status: "fail",
      code: "BTE_PROOF_SUBJECT_MISSING",
      diagnostics: [],
    };
  }
  const validation = validateDevelopmentEdge(
    edge,
    project.nodes,
    project.edges,
  );
  const pass =
    edge.family === obligation.expected_relationship &&
    validation.result === "pass";
  return {
    coverage_key: coverageKey,
    source_anchor: anchor,
    status: pass ? "pass" : "fail",
    code: pass
      ? "BTE_PROOF_PASS"
      : (validation.diagnostics[0]?.code ?? "BTE_PROOF_SUBJECT_INVALID"),
    diagnostics: validation.diagnostics,
  };
}

export function assertExactStructuralCoverage(
  expectedKeys: readonly string[],
  actualCases: readonly StructuralTestCase[],
): void {
  const actualKeys = actualCases.map(({ coverage_key }) => coverage_key);
  const expected = new Set(expectedKeys);
  const actual = new Set(actualKeys);
  const duplicate = actualKeys.filter(
    (key, index) => actualKeys.indexOf(key) !== index,
  );
  const missing = expectedKeys.filter((key) => !actual.has(key));
  const extra = actualKeys.filter((key) => !expected.has(key));
  if (
    duplicate.length > 0 ||
    missing.length > 0 ||
    extra.length > 0 ||
    expectedKeys.length !== actualKeys.length
  ) {
    throw new Error(
      `BTE_STRUCTURAL_COVERAGE_MISMATCH:${JSON.stringify({
        duplicate: [...new Set(duplicate)].sort(),
        extra: [...new Set(extra)].sort(),
        missing: [...new Set(missing)].sort(),
      })}`,
    );
  }
}

function commentSafe(value: string): string {
  return value.replace(/\r?\n/g, " ").replace(/\*\//g, "* /");
}

export function renderStructuralVitest(
  cases: readonly StructuralTestCase[],
): string {
  const expectedKeys = cases.map(({ coverage_key }) => coverage_key);
  const renderedCases = cases.flatMap((testCase) => [
    `  // coverage_key: ${testCase.coverage_key}`,
    `  // source: ${commentSafe(testCase.source_anchor)}`,
    `  it(${JSON.stringify(testCase.coverage_key)}, () => {`,
    `    const result = evaluateStructuralCase(projection.project, ${JSON.stringify(testCase.coverage_key)});`,
    `    expect(result.status, ${JSON.stringify(testCase.source_anchor)}).toBe("pass");`,
    `  });`,
  ]);
  return [
    "// AUTO-GENERATED by the Financial Settlement BTE structural emitter.",
    "// Raw Vitest intentionally contains the declared source red; use the expected-red verifier.",
    'import { dirname, resolve } from "node:path";',
    'import { fileURLToPath } from "node:url";',
    'import { describe, expect, it } from "vitest";',
    "import {",
    "  assertExactStructuralCoverage,",
    "  evaluateStructuralCase,",
    "  materializeStructuralTestCases,",
    "  projectFeatureDirectory,",
    '} from "../../test-derivation-engine/src/bte/structural-emitter.js";',
    "",
    "const featureRoot = resolve(",
    "  process.env.FSTG_FEATURE_ROOT ??",
    "    resolve(",
    "      dirname(fileURLToPath(import.meta.url)),",
    '      "../../../../../validation/poker-team/docs/features/financial-settlement",',
    "    ),",
    ");",
    "const projection = projectFeatureDirectory(featureRoot);",
    `const expectedCoverageKeys = ${JSON.stringify(expectedKeys, null, 2)} as const;`,
    "assertExactStructuralCoverage(",
    "  expectedCoverageKeys,",
    "  materializeStructuralTestCases(projection.project),",
    ");",
    "",
    'describe("Financial Settlement structural conformance", () => {',
    ...renderedCases,
    "});",
    "",
  ].join("\n");
}

function expectedRedObserved(results: readonly StructuralCaseResult[]): boolean {
  const failed = results.filter(({ status }) => status === "fail");
  return (
    failed.length === 1 &&
    failed[0]?.coverage_key ===
      FINANCIAL_SETTLEMENT_EXPECTED_RED.coverage_key &&
    failed[0]?.code === FINANCIAL_SETTLEMENT_EXPECTED_RED.code
  );
}

export function deriveFinancialSettlementStructuralEmission(
  featureRoot: string,
  bindingsPath: string,
): FinancialSettlementStructuralEmission {
  const projection = projectFeatureDirectory(featureRoot);
  if (projection.diagnostics.length > 0) {
    throw new Error(
      `BTE_STRUCTURAL_PROJECTION_INVALID:${JSON.stringify(projection.diagnostics)}`,
    );
  }
  const cases = materializeStructuralTestCases(projection.project);
  if (cases.length !== FINANCIAL_SETTLEMENT_STRUCTURAL_TOTAL) {
    throw new Error(
      `BTE_STRUCTURAL_TOTAL_MISMATCH:expected=${FINANCIAL_SETTLEMENT_STRUCTURAL_TOTAL}:actual=${cases.length}`,
    );
  }
  assertExactStructuralCoverage(
    cases.map(({ coverage_key }) => coverage_key),
    cases,
  );
  const results = cases.map(({ coverage_key }) =>
    evaluateStructuralCase(projection.project, coverage_key),
  );
  const behavioralGraph = parse(featureRoot);
  if (behavioralGraph.violations.length > 0) {
    throw new Error(
      `BTE_STRUCTURAL_BEHAVIORAL_SOURCE_INVALID:${JSON.stringify(behavioralGraph.violations)}`,
    );
  }
  const behavioral = emitHybridTests(
    derive(behavioralGraph.graph),
    loadBindings(bindingsPath),
    behavioralGraph.graph,
  ).report;
  const failedCases = results
    .filter(({ status }) => status === "fail")
    .map(({ coverage_key, source_anchor, code }) => ({
      coverage_key,
      source_anchor,
      code,
    }));
  const observed = expectedRedObserved(results);
  const report: FinancialSettlementStructuralReport = {
    schema_version: "bte-financial-settlement-structural-report/v1",
    project_id: "financial-settlement",
    result: observed ? "expected-red" : "unexpected",
    structural: {
      generated: cases.length,
      passed: results.filter(({ status }) => status === "pass").length,
      failed: failedCases.length,
      todo: 0,
      skipped: 0,
      coverage_keys: cases.map(({ coverage_key }) => coverage_key),
      failed_cases: failedCases,
    },
    expected_red: {
      ...FINANCIAL_SETTLEMENT_EXPECTED_RED,
      observed,
    },
    behavioral: {
      total: behavioral.total,
      assertions: behavioral.assertions,
      properties: behavioral.properties,
      coverage_gaps: behavioral.coverageGaps,
    },
  };
  return {
    projection,
    cases,
    results,
    file: renderStructuralVitest(cases),
    report,
    reportBytes: `${JSON.stringify(report, null, 2)}\n`,
  };
}

function assertContained(allowedRoot: string, outputDir: string): string {
  mkdirSync(allowedRoot, { recursive: true });
  const allowedReal = realpathSync(allowedRoot);
  const candidate = resolve(outputDir);
  const lexical = relative(allowedReal, candidate);
  if (
    lexical === ".." ||
    lexical.startsWith(`..${sep}`) ||
    resolve(allowedReal, lexical) !== candidate
  ) {
    throw new Error(`BTE_STRUCTURAL_OUTPUT_ESCAPE:${outputDir}`);
  }
  mkdirSync(candidate, { recursive: true });
  const candidateReal = realpathSync(candidate);
  const physical = relative(allowedReal, candidateReal);
  if (physical === ".." || physical.startsWith(`..${sep}`)) {
    throw new Error(`BTE_STRUCTURAL_OUTPUT_ESCAPE:${outputDir}`);
  }
  return candidateReal;
}

export function writeFinancialSettlementStructuralArtifacts(
  emission: FinancialSettlementStructuralEmission,
  allowedOutputRoot: string,
  outputDir: string,
): WrittenStructuralArtifacts {
  const contained = assertContained(allowedOutputRoot, outputDir);
  const testFile = resolve(
    contained,
    "financial-settlement.structural.test.ts",
  );
  const reportFile = resolve(
    contained,
    "financial-settlement.structural.report.json",
  );
  writeFileSync(testFile, emission.file, "utf8");
  writeFileSync(reportFile, emission.reportBytes, "utf8");
  return {
    testFile,
    reportFile,
    testSha256: sha256(readFileSync(testFile, "utf8")),
    reportSha256: sha256(readFileSync(reportFile, "utf8")),
  };
}

export { projectFeatureDirectory };
