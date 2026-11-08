import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { projectTypeScriptEnum } from "../../adapter/enum/index.js";

type Constraint = Readonly<{
  constraint_id: string;
  constraint_kind: string;
  applies_to?: readonly string[];
  property_id: string;
  operator: string;
  expected?: unknown;
}>;
type Profile = Readonly<{ constraints: readonly Constraint[]; representation_overlays?: readonly Readonly<{ representation_constraints: readonly Constraint[] }>[] }>;
type FixtureCase = Readonly<{ case_id: string; source: string; mutation?: string; expected_findings: readonly string[] }>;

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixturesRoot = "projects/domainspec-v2/impl/architecture-conformance/typescript/fixtures/enum";
const loadJson = async <T>(path: string): Promise<T> =>
  JSON.parse(await readFile(resolve(repositoryRoot, path), "utf8")) as T;
const stable = (value: unknown): string => JSON.stringify(value, Object.keys(value as object).sort());
const setEquals = (actual: unknown, expected: unknown): boolean => {
  if (!Array.isArray(actual) || !Array.isArray(expected)) return false;
  const left = new Set(actual.map(stable));
  const right = new Set(expected.map(stable));
  return left.size === right.size && [...left].every((item) => right.has(item));
};
const evaluateOperator = (operator: string, actual: unknown, expected: unknown): boolean => {
  if (operator === "required") return actual !== undefined && actual !== null && actual !== "";
  if (operator === "equals") return actual === expected;
  if (operator === "set_equals") return setEquals(actual, expected);
  if (operator === "unique") return Array.isArray(actual) && new Set(actual.map(stable)).size === actual.length;
  if (operator === "non_empty") return (typeof actual === "string" || Array.isArray(actual)) && actual.length > 0;
  if (operator === "cardinality") {
    if (!Array.isArray(actual) || typeof expected !== "object" || expected === null) return false;
    const bounds = expected as { min?: number; max?: number; exact?: number };
    return (bounds.min === undefined || actual.length >= bounds.min)
      && (bounds.max === undefined || actual.length <= bounds.max)
      && (bounds.exact === undefined || actual.length === bounds.exact);
  }
  if (operator === "matches") return typeof actual === "string" && new RegExp(String(expected)).test(actual);
  if (operator === "one_of") return Array.isArray(expected) && expected.includes(actual);
  throw new Error(`unsupported fixture evaluator operator: ${operator}`);
};

const matrix = await loadJson<{ expected_values: readonly string[]; cases: readonly FixtureCase[] }>(`${fixturesRoot}/expected-results.json`);
const baseProfile = await loadJson<Profile>("projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json");
const typescriptProfile = await loadJson<Profile>("projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json");
const applicableTypes = new Set(["architecture.EnumImplementation", "architecture.DomainConceptImplementation", "architecture.ImplementationElement"]);
const constraints = [
  ...baseProfile.constraints,
  ...(typescriptProfile.representation_overlays?.flatMap(({ representation_constraints }) => representation_constraints) ?? []),
].filter(({ constraint_kind, applies_to }) =>
  constraint_kind === "node-property" && (applies_to ?? []).some((type) => applicableTypes.has(type))
);

const runCase = async (testCase: FixtureCase): Promise<readonly string[]> => {
  const projection = await projectTypeScriptEnum({
    repositoryRoot,
    sourcePath: `${fixturesRoot}/${testCase.source}`,
    exportName: "OrderStatus",
    subjectRef: "enum.order.status",
    conceptId: "domain.order.Status",
    expectedValues: matrix.expected_values,
    profilePath: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
    providerPath: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
    profileActivationReceiptPath: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/SWU-APE-ENUM-TS-001A.json",
  });
  if (projection.diagnostics.length > 0) {
    return projection.diagnostics.map(({ code }) => String(code)).sort();
  }
  const properties = Object.fromEntries(
    projection.facts.map(({ predicate_ref, value }) => [String(predicate_ref), value]),
  );
  if (testCase.mutation === "binding-current-false") properties["binding.current"] = false;
  return constraints
    .filter((constraint) => {
      const actual = properties[constraint.property_id];
      const expected = (
        typeof constraint.expected === "object"
        && constraint.expected !== null
        && (constraint.expected as { kind?: string }).kind === "property-ref"
      )
        ? properties[String((constraint.expected as { property_id: string }).property_id)]
        : constraint.expected;
      return !evaluateOperator(constraint.operator, actual, expected);
    })
    .map(({ constraint_id }) => constraint_id)
    .sort();
};

describe("TypeScript Enum discriminating fixture denominator", () => {
  it("accounts for every declared case with exact one-cause findings", async () => {
    const results = await Promise.all(
      matrix.cases.map(async (testCase) => ({
        case_id: testCase.case_id,
        actual: await runCase(testCase),
        expected: [...testCase.expected_findings].sort(),
      })),
    );
    expect(results).toHaveLength(13);
    expect(results).toEqual(
      results.map(({ case_id, expected }) => ({ case_id, actual: expected, expected })),
    );
    expect(results.filter(({ actual }) => actual.length === 0)).toHaveLength(1);
  });
});
