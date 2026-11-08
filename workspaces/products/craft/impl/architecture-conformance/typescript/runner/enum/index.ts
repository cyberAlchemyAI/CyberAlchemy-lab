import { createHash } from "node:crypto";
import { readFile, readdir } from "node:fs/promises";
import { resolve } from "node:path";

import { projectTypeScriptEnum } from "../../adapter/enum/index.js";

type Json = null | boolean | number | string | readonly Json[] | { readonly [key: string]: Json };
type JsonRecord = Readonly<Record<string, Json>>;
type Constraint = Readonly<{
  constraint_id: string;
  constraint_kind: string;
  applies_to?: readonly string[];
  property_id: string;
  operator: string;
  expected?: unknown;
}>;
type Profile = Readonly<{
  constraints: readonly Constraint[];
  representation_overlays?: readonly Readonly<{ representation_constraints: readonly Constraint[] }>[];
}>;
type FixtureCase = Readonly<{
  case_id: string;
  source: string;
  mutation?: string;
  expected_findings: readonly string[];
}>;

const PATHS = {
  ontology: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json",
  baseProfile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json",
  typescriptProfile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
  observationSchema: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/contracts/observation-projection.schema.json",
  scenarioSchema: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/contracts/evaluation-scenario.schema.json",
  scenarioCases: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/scenarios/cases.json",
  scenarioExpected: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/scenarios/evaluations.expected.json",
  scenarioChecker: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/examples/enum/scenarios/check-evaluation-scenario.mjs",
  activationReceipt: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/SWU-APE-ENUM-TS-001A.json",
  fixtureReceipt: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/SWU-APE-ENUM-TS-003.json",
  provider: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
  adapter: "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/enum/index.ts",
  fixtureDirectory: "projects/domainspec-v2/impl/architecture-conformance/typescript/fixtures/enum",
  fixtureManifest: "projects/domainspec-v2/impl/architecture-conformance/typescript/fixtures/enum/expected-results.json",
  bteProvider: "projects/domainspec-v2/impl/test-derivation-engine/src/bte/proof-engine.ts",
  bteProviderTest: "projects/domainspec-v2/impl/test-derivation-engine/src/bte/proof-engine.test.ts",
  execution: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/typescript/EXECUTION.json",
  mutation: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/typescript/MUTATION.json",
  replay: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/typescript/REPLAY.json",
  scenarioReadiness: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/receipts/typescript/SCENARIO-READINESS.json",
  freeze: "projects/domainspec-v2/development/architecture-pattern-enforcement/instances/enum/contracts/FROZEN-OBSERVATION.json",
} as const;

export const TRUST_ARTIFACT_PATHS = {
  execution: PATHS.execution,
  mutation: PATHS.mutation,
  replay: PATHS.replay,
  scenarioReadiness: PATHS.scenarioReadiness,
  freeze: PATHS.freeze,
} as const;

export type TrustArtifacts = Readonly<Record<keyof typeof TRUST_ARTIFACT_PATHS, JsonRecord>>;

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

const sortJson = (value: unknown): Json => {
  if (value === null || ["boolean", "number", "string"].includes(typeof value)) return value as Json;
  if (Array.isArray(value)) return value.map(sortJson);
  if (typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, child]) => [key, sortJson(child)]),
    );
  }
  throw new Error(`non-JSON proof value: ${typeof value}`);
};

export const renderTrustArtifact = (value: JsonRecord): string =>
  `${JSON.stringify(sortJson(value), null, 2)}\n`;

const canonical = (value: unknown): string => JSON.stringify(sortJson(value));
const same = (left: unknown, right: unknown): boolean => canonical(left) === canonical(right);

const loadJson = async <T>(root: string, path: string): Promise<T> =>
  JSON.parse(await readFile(resolve(root, path), "utf8")) as T;

const exactRef = async (root: string, path: string): Promise<JsonRecord> => {
  const bytes = await readFile(resolve(root, path));
  return { path, sha256: sha256(bytes), size_bytes: bytes.byteLength };
};

const setEquals = (actual: unknown, expected: unknown): boolean => {
  if (!Array.isArray(actual) || !Array.isArray(expected)) return false;
  const left = new Set(actual.map(canonical));
  const right = new Set(expected.map(canonical));
  return left.size === right.size && [...left].every((item) => right.has(item));
};

const evaluateOperator = (operator: string, actual: unknown, expected: unknown): boolean => {
  if (operator === "required") return actual !== undefined && actual !== null && actual !== "";
  if (operator === "equals") return actual === expected;
  if (operator === "set_equals") return setEquals(actual, expected);
  if (operator === "unique") return Array.isArray(actual) && new Set(actual.map(canonical)).size === actual.length;
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
  throw new Error(`unsupported trust evaluator operator: ${operator}`);
};

const applicableConstraints = (base: Profile, typescript: Profile): readonly Constraint[] => {
  const applicableTypes = new Set([
    "architecture.EnumImplementation",
    "architecture.DomainConceptImplementation",
    "architecture.ImplementationElement",
  ]);
  return [
    ...base.constraints,
    ...(typescript.representation_overlays?.flatMap(({ representation_constraints }) => representation_constraints) ?? []),
  ].filter(({ constraint_kind, applies_to }) =>
    constraint_kind === "node-property" && (applies_to ?? []).some((type) => applicableTypes.has(type))
  );
};

const evaluateCase = async (
  root: string,
  fixture: FixtureCase,
  expectedValues: readonly string[],
  constraints: readonly Constraint[],
): Promise<JsonRecord> => {
  const sourcePath = `${PATHS.fixtureDirectory}/${fixture.source}`;
  const projection = await projectTypeScriptEnum({
    repositoryRoot: root,
    sourcePath,
    exportName: "OrderStatus",
    subjectRef: "enum.order.status",
    conceptId: "domain.order.Status",
    expectedValues,
    profilePath: PATHS.typescriptProfile,
    providerPath: PATHS.provider,
    profileActivationReceiptPath: PATHS.activationReceipt,
  });
  let findings: string[];
  if (projection.diagnostics.length > 0) {
    findings = projection.diagnostics.map(({ code }) => String(code)).sort();
  } else {
    const properties: Record<string, unknown> = Object.fromEntries(
      projection.facts.map(({ predicate_ref, value }) => [String(predicate_ref), value]),
    );
    if (fixture.mutation === "binding-current-false") properties["binding.current"] = false;
    findings = constraints
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
  }
  const expected = [...fixture.expected_findings].sort();
  return {
    case_id: fixture.case_id,
    source_ref: await exactRef(root, sourcePath),
    projection_sha256: sha256(canonical(projection)),
    expected_findings: expected,
    actual_findings: findings,
    exact_match: same(findings, expected),
    mutation_killed: fixture.case_id === "positive" ? null : findings.length > 0 && same(findings, expected),
  };
};

const buildOneRun = async (root: string): Promise<Readonly<{
  execution: JsonRecord;
  mutation: JsonRecord;
  scenarioReadiness: JsonRecord;
}>> => {
  const [matrix, base, typescript, scenarioSchema, scenarioCases, scenarioExpected] = await Promise.all([
    loadJson<{ expected_values: readonly string[]; cases: readonly FixtureCase[] }>(root, PATHS.fixtureManifest),
    loadJson<Profile>(root, PATHS.baseProfile),
    loadJson<Profile>(root, PATHS.typescriptProfile),
    loadJson<Record<string, unknown>>(root, PATHS.scenarioSchema),
    loadJson<{ cases: readonly unknown[]; authority_effect: string }>(root, PATHS.scenarioCases),
    loadJson<{ represented_bte_blockers: readonly string[]; total_join_enforced: boolean; authority_effect: string }>(root, PATHS.scenarioExpected),
  ]);
  const constraints = applicableConstraints(base, typescript);
  const cases = await Promise.all(
    matrix.cases.map((fixture) => evaluateCase(root, fixture, matrix.expected_values, constraints)),
  );
  const fixtureFiles = (await readdir(resolve(root, PATHS.fixtureDirectory)))
    .filter((name) => name.endsWith(".ts") || name.endsWith(".json"))
    .sort();
  const contractSources = await Promise.all([
    PATHS.ontology,
    PATHS.baseProfile,
    PATHS.typescriptProfile,
    PATHS.observationSchema,
    PATHS.activationReceipt,
    PATHS.fixtureReceipt,
    PATHS.provider,
    PATHS.adapter,
    PATHS.fixtureManifest,
    ...fixtureFiles.map((name) => `${PATHS.fixtureDirectory}/${name}`),
  ].map((path) => exactRef(root, path)));
  const allExact = cases.every(({ exact_match }) => exact_match === true);
  const execution: JsonRecord = {
    schema_version: "ape.typescript-enum-proof-execution/v1",
    proof_id: "ape.enum.typescript.trust/v1",
    protocol_id: "typescript.owned-const-object-enum/v1",
    projection_schema: "domainspec-observation-projection/v1",
    constraint_ids: constraints.map(({ constraint_id }) => constraint_id).sort(),
    property_ids: [...new Set(constraints.map(({ property_id }) => property_id))].sort(),
    raw_artifact_refs: contractSources,
    cases,
    declared_case_count: matrix.cases.length,
    accounted_case_count: cases.length,
    unaccounted_case_count: matrix.cases.length - cases.length,
    result: allExact && cases.length === matrix.cases.length ? "pass" : "block",
    authority_effect: "none",
  };
  const mutants = cases.filter(({ case_id }) => case_id !== "positive");
  const mutation: JsonRecord = {
    schema_version: "ape.typescript-enum-mutation-receipt/v1",
    proof_id: "ape.enum.typescript.trust/v1",
    mutants: mutants.map(({ case_id, source_ref, expected_findings, actual_findings, mutation_killed }) => ({
      case_id,
      source_ref,
      expected_findings,
      actual_findings,
      killed: mutation_killed,
    })),
    declared_mutant_count: mutants.length,
    killed_mutant_count: mutants.filter(({ mutation_killed }) => mutation_killed === true).length,
    survived_mutant_count: mutants.filter(({ mutation_killed }) => mutation_killed !== true).length,
    result: mutants.every(({ mutation_killed }) => mutation_killed === true) ? "pass" : "block",
    authority_effect: "none",
  };
  const blockers = [...scenarioExpected.represented_bte_blockers].sort();
  const scenarioReady = scenarioSchema.$id === "https://domainspec.local/contracts/evaluation-scenario.schema.json"
    && scenarioCases.cases.length === 4
    && scenarioCases.authority_effect === "none"
    && scenarioExpected.total_join_enforced === true
    && scenarioExpected.authority_effect === "none"
    && same(blockers, ["BTE_EXPECTATION_REWRITTEN", "BTE_RECOMPOSITION_MISSING", "BTE_RECOMPOSITION_OVERLAP"]);
  const scenarioReadiness: JsonRecord = {
    schema_version: "ape.bte-compatible-scenario-readiness/v1",
    contract_ref: await exactRef(root, PATHS.scenarioSchema),
    cases_ref: await exactRef(root, PATHS.scenarioCases),
    expected_ref: await exactRef(root, PATHS.scenarioExpected),
    checker_ref: await exactRef(root, PATHS.scenarioChecker),
    bte_provider_ref: await exactRef(root, PATHS.bteProvider),
    bte_provider_test_ref: await exactRef(root, PATHS.bteProviderTest),
    represented_bte_blockers: blockers,
    total_join_enforced: scenarioExpected.total_join_enforced,
    provider_adoption: "not-claimed-owner-gated",
    declared_external_gates: [
      "validate-evaluation-scenario-contract-readiness",
      "validate-bte-development-proof-provider-regression",
    ],
    result: scenarioReady ? "pass" : "block",
    authority_effect: "none",
  };
  return { execution, mutation, scenarioReadiness };
};

export const buildTrustArtifacts = async (repositoryRoot: string): Promise<TrustArtifacts> => {
  const root = resolve(repositoryRoot);
  const first = await buildOneRun(root);
  const second = await buildOneRun(root);
  const executionBytes = renderTrustArtifact(first.execution);
  const replayBytes = renderTrustArtifact(second.execution);
  const byteIdentical = executionBytes === replayBytes
    && renderTrustArtifact(first.mutation) === renderTrustArtifact(second.mutation)
    && renderTrustArtifact(first.scenarioReadiness) === renderTrustArtifact(second.scenarioReadiness);
  const replay: JsonRecord = {
    schema_version: "ape.typescript-enum-replay-receipt/v1",
    proof_id: "ape.enum.typescript.trust/v1",
    first_execution_sha256: sha256(executionBytes),
    replay_execution_sha256: sha256(replayBytes),
    byte_identical: byteIdentical,
    independent_recomposition: true,
    result: byteIdentical ? "pass" : "block",
    authority_effect: "none",
  };
  const freezePayload: JsonRecord = {
    schema_version: "ape.frozen-observation-contract/v1",
    contract_id: "ape.enum.observation-contract/v1",
    frozen: true,
    protocol_id: "typescript.owned-const-object-enum/v1",
    projection_schema: "domainspec-observation-projection/v1",
    execution_sha256: sha256(executionBytes),
    mutation_sha256: sha256(renderTrustArtifact(first.mutation)),
    replay_sha256: sha256(renderTrustArtifact(replay)),
    scenario_readiness_sha256: sha256(renderTrustArtifact(first.scenarioReadiness)),
    ontology_ref: await exactRef(root, PATHS.ontology),
    base_profile_ref: await exactRef(root, PATHS.baseProfile),
    language_profile_ref: await exactRef(root, PATHS.typescriptProfile),
    observation_schema_ref: await exactRef(root, PATHS.observationSchema),
    fixture_manifest_ref: await exactRef(root, PATHS.fixtureManifest),
    fixture_receipt_ref: await exactRef(root, PATHS.fixtureReceipt),
    adapter_ref: await exactRef(root, PATHS.adapter),
    provider_ref: await exactRef(root, PATHS.provider),
    authority_effect: "none",
  };
  const freeze: JsonRecord = {
    ...freezePayload,
    frozen_contract_sha256: sha256(canonical(freezePayload)),
  };
  return { execution: first.execution, mutation: first.mutation, replay, scenarioReadiness: first.scenarioReadiness, freeze };
};

export const verifyTrustArtifacts = (artifacts: TrustArtifacts): readonly string[] => {
  const diagnostics: string[] = [];
  if (artifacts.execution.result !== "pass") diagnostics.push("APE_TS_PROOF_EXECUTION_BLOCKED");
  if (artifacts.mutation.result !== "pass") diagnostics.push("APE_TS_PROOF_MUTANT_SURVIVED");
  if (artifacts.replay.result !== "pass" || artifacts.replay.byte_identical !== true) diagnostics.push("APE_TS_PROOF_REPLAY_MISMATCH");
  if (artifacts.scenarioReadiness.result !== "pass") diagnostics.push("APE_TS_SCENARIO_NOT_READY");
  const { frozen_contract_sha256: declared, ...payload } = artifacts.freeze;
  if (artifacts.freeze.frozen !== true || declared !== sha256(canonical(payload))) diagnostics.push("APE_TS_FREEZE_DIGEST_MISMATCH");
  if (artifacts.freeze.execution_sha256 !== sha256(renderTrustArtifact(artifacts.execution))) diagnostics.push("APE_TS_FREEZE_EXECUTION_DRIFT");
  if (artifacts.freeze.mutation_sha256 !== sha256(renderTrustArtifact(artifacts.mutation))) diagnostics.push("APE_TS_FREEZE_MUTATION_DRIFT");
  if (artifacts.freeze.replay_sha256 !== sha256(renderTrustArtifact(artifacts.replay))) diagnostics.push("APE_TS_FREEZE_REPLAY_DRIFT");
  if (artifacts.freeze.scenario_readiness_sha256 !== sha256(renderTrustArtifact(artifacts.scenarioReadiness))) diagnostics.push("APE_TS_FREEZE_SCENARIO_DRIFT");
  return diagnostics.sort();
};

export const loadStoredTrustArtifacts = async (repositoryRoot: string): Promise<TrustArtifacts> => {
  const root = resolve(repositoryRoot);
  const entries = await Promise.all(
    Object.entries(TRUST_ARTIFACT_PATHS).map(async ([key, path]) => [key, await loadJson<JsonRecord>(root, path)] as const),
  );
  return Object.fromEntries(entries) as TrustArtifacts;
};
