import { canonicalize } from "./contract-publication.js";
import {
  BACKEND_KINDS,
  BACKEND_RELATIONSHIPS,
  replayDevelopmentBuild,
  validateDevelopmentEdge,
  validateDevelopmentNode,
  type BackendKind,
  type BackendRelationship,
  type DevelopmentBuild,
  type DevelopmentDiagnostic,
  type DevelopmentGraph,
  type DevelopmentProject,
} from "./development-engine.js";
import { sha256 } from "./validation/validate-semantics.js";
import {
  createSelfAuthoredDevelopmentCatalogues,
  SELF_AUTHORED_EXPECTATION_ORACLE,
} from "./self-authored-expectations.js";

export const CATALOGUE_IDS = [
  "formation-criterion@1",
  "formation-structure@1",
  "node-kind-causality@1",
  "node-instance-conformance@1",
  "relationship-family-causality@1",
  "edge-instance-conformance@1",
] as const;

export type CatalogueId = (typeof CATALOGUE_IDS)[number];

export type DevelopmentObligation = {
  catalogue_id: CatalogueId;
  obligation_id: string;
  coverage_key: string;
  subject_type: "kind" | "node" | "relationship" | "edge";
  subject_id: string;
  expected_kind?: BackendKind;
  expected_relationship?: BackendRelationship;
  evaluator: "formation" | "node-causality" | "graph-conformance" | "relationship-causality";
};

export type DevelopmentCatalogue = {
  schema_version: "bte-development-catalogue/v1";
  catalogue_id: CatalogueId;
  oracle_id:
    | typeof SELF_AUTHORED_EXPECTATION_ORACLE
    | typeof BUILD_DERIVED_GENERATION_ORACLE;
  members: DevelopmentObligation[];
  membership_digest: string;
  authority: "development-fixture";
};

export type DevelopmentTestCase = {
  schema_version: "bte-development-test-case/v1";
  test_id: string;
  coverage_key: string;
  subject_type: DevelopmentObligation["subject_type"];
  subject_id: string;
  expected_result: "present-and-valid";
  mutation: {
    operation: "remove-subject";
    expected_code: "BTE_PROOF_SUBJECT_MISSING";
  };
};

export type DevelopmentExecutionResult = {
  schema_version: "bte-development-execution-result/v1";
  result_id: string;
  coverage_key: string;
  test_sha256: string;
  observed_result: "present-and-valid" | "missing-or-invalid";
  code: "BTE_PROOF_PASS" | "BTE_PROOF_SUBJECT_MISSING" | "BTE_PROOF_SUBJECT_INVALID";
  status: "pass" | "fail";
};

export type DevelopmentInstanceConformanceCase = {
  test: DevelopmentTestCase;
  execution: DevelopmentExecutionResult;
  diagnostics: DevelopmentDiagnostic[];
};

export type DevelopmentInstanceConformanceRun = {
  schema_version: "bte-development-instance-conformance-run/v1";
  project_id: string;
  cases: DevelopmentInstanceConformanceCase[];
  result: "pass" | "fail";
};

export type DevelopmentMutationResult = {
  schema_version: "bte-development-mutation-result/v1";
  mutation_id: string;
  coverage_key: string;
  operation: "remove-subject";
  observed_code: "BTE_PROOF_SUBJECT_MISSING" | "BTE_PROOF_MUTANT_SURVIVED";
  killed: boolean;
};

export type DevelopmentProofReceipt = {
  schema_version: "bte-development-proof-receipt/v1";
  receipt_id: string;
  catalogue_id: CatalogueId;
  build_receipt_sha256: string;
  required_coverage_digest: string;
  tests_digest: string;
  executions_digest: string;
  mutations_digest: string;
  coverage_count: number;
  result: "pass";
  admission: "development-only";
};

export type DevelopmentReplayResult = {
  schema_version: "bte-development-replay-result/v1";
  replay_id: string;
  catalogue_id: CatalogueId;
  proof_receipt_sha256: string;
  recomposed_coverage_digest: string;
  result: "pass";
};

export type DevelopmentCatalogueRun = {
  catalogue: DevelopmentCatalogue;
  generated: DevelopmentCatalogue;
  tests: DevelopmentTestCase[];
  executions: DevelopmentExecutionResult[];
  mutations: DevelopmentMutationResult[];
  proofReceipt: DevelopmentProofReceipt;
  replayResult: DevelopmentReplayResult;
};

export type DevelopmentCoreAggregate = {
  schema_version: "bte-development-core-aggregate/v1";
  aggregate_id: "bte-development-core";
  build_receipt_sha256: string;
  required_catalogues: CatalogueId[];
  replay_handles: Array<{
    catalogue_id: CatalogueId;
    sha256: string;
    coverage_count: number;
  }>;
  total_coverage_count: number;
  result: "pass";
  admission: "development-only";
};

export type DevelopmentCoreRun = {
  catalogueRuns: DevelopmentCatalogueRun[];
  aggregate: DevelopmentCoreAggregate;
  aggregateBytes: string;
};

export const PROOF_ENGINE_ERROR_CODES = [
  "BTE_PROOF_BUILD_INVALID",
  "BTE_EXPECTATION_NOT_INDEPENDENT",
  "BTE_PROOF_CATALOGUE_MISSING",
  "BTE_PROOF_CATALOGUE_EXTRA",
  "BTE_PROOF_CATALOGUE_DUPLICATE",
  "BTE_PROOF_SUBJECT_MISSING",
  "BTE_PROOF_SUBJECT_INVALID",
  "BTE_PROOF_MUTANT_SURVIVED",
  "BTE_PROOF_REPLAY_MISMATCH",
  "BTE_PROOF_CORE_INCOMPLETE",
] as const;

export type ProofEngineErrorCode = (typeof PROOF_ENGINE_ERROR_CODES)[number];

export class ProofEngineError extends Error {
  readonly code: ProofEngineErrorCode;
  readonly subject: string;

  constructor(code: ProofEngineErrorCode, subject: string, detail: string) {
    super(`${code}:${subject}:${detail}`);
    this.name = "ProofEngineError";
    this.code = code;
    this.subject = subject;
  }
}

const FORMATION_CRITERIA: Readonly<Record<BackendKind, readonly string[]>> = {
  Entity: ["identity", "typedness"],
  "Value Object": ["no-identity", "typedness", "equality"],
  Enum: ["closed-values"],
  Operation: ["writes-state"],
  Query: ["read-only"],
  Calculation: ["returns-value"],
  Rule: ["boolean-predicate"],
  Policy: ["selects-strategy"],
  Workflow: ["admitted-scope"],
  Interface: ["declares-boundary"],
  Event: ["past-tense"],
  Mapping: ["has-direction"],
  "State Machine": ["has-transitions"],
};

export const BUILD_DERIVED_GENERATION_ORACLE =
  "bte.build-derived.generator/v1" as const;

function bytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

function coverageKey(catalogueId: CatalogueId, obligationId: string): string {
  return `${catalogueId}::${obligationId}`;
}

function catalogue(
  catalogueId: CatalogueId,
  members: DevelopmentObligation[],
): DevelopmentCatalogue {
  const sorted = [...members].sort((left, right) =>
    left.coverage_key.localeCompare(right.coverage_key),
  );
  return {
    schema_version: "bte-development-catalogue/v1",
    catalogue_id: catalogueId,
    oracle_id: BUILD_DERIVED_GENERATION_ORACLE,
    members: sorted,
    membership_digest: sha256(canonicalize(sorted.map(({ coverage_key }) => coverage_key))),
    authority: "development-fixture",
  };
}

function formationCriterionMembers(
  kinds: readonly BackendKind[],
): DevelopmentObligation[] {
  return kinds.flatMap((kind) =>
    FORMATION_CRITERIA[kind].map((criterion) => {
      const obligationId = `${kind.toLowerCase().replaceAll(" ", "-")}/${criterion}`;
      return {
        catalogue_id: "formation-criterion@1" as const,
        obligation_id: obligationId,
        coverage_key: coverageKey("formation-criterion@1", obligationId),
        subject_type: "kind" as const,
        subject_id: kind,
        expected_kind: kind,
        evaluator: "formation" as const,
      };
    }),
  );
}

function formationStructureMembers(
  kinds: readonly BackendKind[],
): DevelopmentObligation[] {
  return kinds.map((kind) => {
    const obligationId = kind.toLowerCase().replaceAll(" ", "-");
    return {
      catalogue_id: "formation-structure@1",
      obligation_id: obligationId,
      coverage_key: coverageKey("formation-structure@1", obligationId),
      subject_type: "kind",
      subject_id: kind,
      expected_kind: kind,
      evaluator: "formation",
    };
  });
}

function nodeKindMembers(kinds: readonly BackendKind[]): DevelopmentObligation[] {
  return kinds.map((kind) => {
    const obligationId = kind.toLowerCase().replaceAll(" ", "-");
    return {
      catalogue_id: "node-kind-causality@1",
      obligation_id: obligationId,
      coverage_key: coverageKey("node-kind-causality@1", obligationId),
      subject_type: "kind",
      subject_id: kind,
      expected_kind: kind,
      evaluator: "node-causality",
    };
  });
}

function nodeInstanceMembers(
  nodes: DevelopmentGraph["nodes"],
): DevelopmentObligation[] {
  return nodes.map((node) => ({
    catalogue_id: "node-instance-conformance@1",
    obligation_id: node.node_id,
    coverage_key: coverageKey("node-instance-conformance@1", node.node_id),
    subject_type: "node",
    subject_id: node.node_id,
    expected_kind: node.kind,
    evaluator: "graph-conformance",
  }));
}

function relationshipFamilyMembers(
  relationships: readonly BackendRelationship[],
): DevelopmentObligation[] {
  return relationships.map((family) => ({
    catalogue_id: "relationship-family-causality@1",
    obligation_id: family,
    coverage_key: coverageKey("relationship-family-causality@1", family),
    subject_type: "relationship",
    subject_id: family,
    expected_relationship: family,
    evaluator: "relationship-causality",
  }));
}

function edgeInstanceMembers(
  edges: DevelopmentGraph["edges"],
): DevelopmentObligation[] {
  return edges.map((edge) => ({
    catalogue_id: "edge-instance-conformance@1",
    obligation_id: edge.edge_id,
    coverage_key: coverageKey("edge-instance-conformance@1", edge.edge_id),
    subject_type: "edge",
    subject_id: edge.edge_id,
    expected_relationship: edge.family,
    evaluator: "graph-conformance",
  }));
}

function buildCatalogues(graph: DevelopmentGraph): DevelopmentCatalogue[] {
  const kinds = [...new Set(graph.nodes.map(({ kind }) => kind))].sort();
  const relationships = [...new Set(graph.edges.map(({ family }) => family))].sort();
  return [
    catalogue("formation-criterion@1", formationCriterionMembers(kinds)),
    catalogue("formation-structure@1", formationStructureMembers(kinds)),
    catalogue("node-kind-causality@1", nodeKindMembers(kinds)),
    catalogue("node-instance-conformance@1", nodeInstanceMembers(graph.nodes)),
    catalogue(
      "relationship-family-causality@1",
      relationshipFamilyMembers(relationships),
    ),
    catalogue("edge-instance-conformance@1", edgeInstanceMembers(graph.edges)),
  ];
}

export function createDevelopmentSpecCatalogues(
  project: DevelopmentProject,
): DevelopmentCatalogue[] {
  return createSelfAuthoredDevelopmentCatalogues(project);
}

export function deriveDevelopmentCatalogues(
  build: DevelopmentBuild,
): DevelopmentCatalogue[] {
  return buildCatalogues(build.graph);
}

function duplicateKeys(catalogueValue: DevelopmentCatalogue): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const member of catalogueValue.members) {
    if (seen.has(member.coverage_key)) duplicates.add(member.coverage_key);
    seen.add(member.coverage_key);
  }
  return [...duplicates].sort();
}

export function compareDevelopmentCatalogues(
  expected: DevelopmentCatalogue,
  generated: DevelopmentCatalogue,
): {
  result: "pass" | "fail";
  diagnostic: "BTE_EXPECTATION_NOT_INDEPENDENT" | null;
  missing: string[];
  extra: string[];
  duplicate: string[];
} {
  const diagnostic =
    expected.oracle_id === SELF_AUTHORED_EXPECTATION_ORACLE &&
    generated.oracle_id === BUILD_DERIVED_GENERATION_ORACLE
      ? null
      : "BTE_EXPECTATION_NOT_INDEPENDENT";
  const expectedKeys = new Set(expected.members.map(({ coverage_key }) => coverage_key));
  const generatedKeys = new Set(generated.members.map(({ coverage_key }) => coverage_key));
  const missing = [...expectedKeys].filter((key) => !generatedKeys.has(key)).sort();
  const extra = [...generatedKeys].filter((key) => !expectedKeys.has(key)).sort();
  const duplicate = [
    ...new Set([...duplicateKeys(expected), ...duplicateKeys(generated)]),
  ].sort();
  return {
    result:
      diagnostic === null &&
      missing.length === 0 &&
      extra.length === 0 &&
      duplicate.length === 0
        ? "pass"
        : "fail",
    diagnostic,
    missing,
    extra,
    duplicate,
  };
}

function materializeTest(obligation: DevelopmentObligation): DevelopmentTestCase {
  return {
    schema_version: "bte-development-test-case/v1",
    test_id: `test/${obligation.coverage_key}`,
    coverage_key: obligation.coverage_key,
    subject_type: obligation.subject_type,
    subject_id: obligation.subject_id,
    expected_result: "present-and-valid",
    mutation: {
      operation: "remove-subject",
      expected_code: "BTE_PROOF_SUBJECT_MISSING",
    },
  };
}

function evaluate(
  obligation: DevelopmentObligation,
  graph: DevelopmentGraph,
): "BTE_PROOF_PASS" | "BTE_PROOF_SUBJECT_MISSING" | "BTE_PROOF_SUBJECT_INVALID" {
  if (obligation.subject_type === "kind") {
    const nodes = graph.nodes.filter(({ kind }) => kind === obligation.subject_id);
    if (nodes.length === 0) return "BTE_PROOF_SUBJECT_MISSING";
    return nodes.every(({ kind }) => kind === obligation.expected_kind)
      ? "BTE_PROOF_PASS"
      : "BTE_PROOF_SUBJECT_INVALID";
  }
  if (obligation.subject_type === "node") {
    const node = graph.nodes.find(({ node_id }) => node_id === obligation.subject_id);
    if (!node) return "BTE_PROOF_SUBJECT_MISSING";
    return (
      node.kind === obligation.expected_kind &&
      validateDevelopmentNode(node).result === "pass"
    )
      ? "BTE_PROOF_PASS"
      : "BTE_PROOF_SUBJECT_INVALID";
  }
  if (obligation.subject_type === "relationship") {
    const edges = graph.edges.filter(({ family }) => family === obligation.subject_id);
    if (edges.length === 0) return "BTE_PROOF_SUBJECT_MISSING";
    return edges.every(({ family }) => family === obligation.expected_relationship)
      ? "BTE_PROOF_PASS"
      : "BTE_PROOF_SUBJECT_INVALID";
  }
  const edge = graph.edges.find(
    ({ edge_id }) => edge_id === obligation.subject_id,
  );
  if (!edge) return "BTE_PROOF_SUBJECT_MISSING";
  return (
    edge.family === obligation.expected_relationship &&
    validateDevelopmentEdge(edge, graph.nodes, graph.edges).result === "pass"
  )
    ? "BTE_PROOF_PASS"
    : "BTE_PROOF_SUBJECT_INVALID";
}

export function collectDevelopmentInstanceConformance(
  project: DevelopmentProject,
): DevelopmentInstanceConformanceRun {
  const graph: DevelopmentGraph = {
    schema_version: "bte-development-graph/v1",
    project_id: project.project_id,
    profile_id: project.profile_id,
    coverage_mode: project.coverage_mode ?? "complete-profile",
    nodes: [...project.nodes],
    edges: [...project.edges],
  };
  const members = buildCatalogues(graph).flatMap((catalogueValue) =>
    catalogueValue.catalogue_id === "node-instance-conformance@1" ||
    catalogueValue.catalogue_id === "edge-instance-conformance@1"
      ? catalogueValue.members
      : [],
  );
  const cases = members.map((obligation) => {
    const test = materializeTest(obligation);
    const code = evaluate(obligation, graph);
    const diagnostics =
      obligation.subject_type === "node"
        ? validateDevelopmentNode(
            graph.nodes.find(({ node_id }) => node_id === obligation.subject_id)!,
          ).diagnostics
        : validateDevelopmentEdge(
            graph.edges.find(({ edge_id }) => edge_id === obligation.subject_id)!,
            graph.nodes,
            graph.edges,
          ).diagnostics;
    const execution: DevelopmentExecutionResult = {
      schema_version: "bte-development-execution-result/v1",
      result_id: `result/${obligation.coverage_key}`,
      coverage_key: obligation.coverage_key,
      test_sha256: sha256(bytes(test)),
      observed_result:
        code === "BTE_PROOF_PASS"
          ? "present-and-valid"
          : "missing-or-invalid",
      code,
      status: code === "BTE_PROOF_PASS" ? "pass" : "fail",
    };
    return { test, execution, diagnostics };
  });
  return {
    schema_version: "bte-development-instance-conformance-run/v1",
    project_id: project.project_id,
    cases,
    result: cases.every(({ execution }) => execution.status === "pass")
      ? "pass"
      : "fail",
  };
}

function mutate(
  obligation: DevelopmentObligation,
  graph: DevelopmentGraph,
): DevelopmentGraph {
  if (obligation.subject_type === "kind") {
    return {
      ...graph,
      nodes: graph.nodes.filter(({ kind }) => kind !== obligation.subject_id),
    };
  }
  if (obligation.subject_type === "node") {
    return {
      ...graph,
      nodes: graph.nodes.filter(({ node_id }) => node_id !== obligation.subject_id),
    };
  }
  if (obligation.subject_type === "relationship") {
    return {
      ...graph,
      edges: graph.edges.filter(({ family }) => family !== obligation.subject_id),
    };
  }
  return {
    ...graph,
    edges: graph.edges.filter(
      ({ edge_id }) => edge_id !== obligation.subject_id,
    ),
  };
}

function runCatalogue(
  expected: DevelopmentCatalogue,
  generated: DevelopmentCatalogue,
  build: DevelopmentBuild,
): DevelopmentCatalogueRun {
  const comparison = compareDevelopmentCatalogues(expected, generated);
  if (comparison.result !== "pass") {
    const code =
      comparison.diagnostic ??
      (comparison.missing.length > 0
        ? "BTE_PROOF_CATALOGUE_MISSING"
        : comparison.extra.length > 0
          ? "BTE_PROOF_CATALOGUE_EXTRA"
          : "BTE_PROOF_CATALOGUE_DUPLICATE");
    throw new ProofEngineError(
      code,
      expected.catalogue_id,
      canonicalize(comparison),
    );
  }
  const tests = generated.members.map(materializeTest);
  const executions = generated.members.map((obligation, index) => {
    const test = tests[index]!;
    const code = evaluate(obligation, build.graph);
    return {
      schema_version: "bte-development-execution-result/v1" as const,
      result_id: `result/${obligation.coverage_key}`,
      coverage_key: obligation.coverage_key,
      test_sha256: sha256(bytes(test)),
      observed_result:
        code === "BTE_PROOF_PASS"
          ? ("present-and-valid" as const)
          : ("missing-or-invalid" as const),
      code,
      status: code === "BTE_PROOF_PASS" ? ("pass" as const) : ("fail" as const),
    };
  });
  const failed = executions.find(({ status }) => status === "fail");
  if (failed) {
    throw new ProofEngineError(
      failed.code === "BTE_PROOF_SUBJECT_MISSING"
        ? "BTE_PROOF_SUBJECT_MISSING"
        : "BTE_PROOF_SUBJECT_INVALID",
      failed.coverage_key,
      failed.code,
    );
  }
  const mutations = generated.members.map((obligation) => {
    const code = evaluate(obligation, mutate(obligation, build.graph));
    const killed = code === "BTE_PROOF_SUBJECT_MISSING";
    return {
      schema_version: "bte-development-mutation-result/v1" as const,
      mutation_id: `mutation/${obligation.coverage_key}`,
      coverage_key: obligation.coverage_key,
      operation: "remove-subject" as const,
      observed_code: killed
        ? ("BTE_PROOF_SUBJECT_MISSING" as const)
        : ("BTE_PROOF_MUTANT_SURVIVED" as const),
      killed,
    };
  });
  const survivor = mutations.find(({ killed }) => !killed);
  if (survivor) {
    throw new ProofEngineError(
      "BTE_PROOF_MUTANT_SURVIVED",
      survivor.coverage_key,
      "removing the subject did not kill its proof",
    );
  }
  const proofReceipt: DevelopmentProofReceipt = {
    schema_version: "bte-development-proof-receipt/v1",
    receipt_id: `proof/${expected.catalogue_id}`,
    catalogue_id: expected.catalogue_id,
    build_receipt_sha256: sha256(build.receiptBytes),
    required_coverage_digest: expected.membership_digest,
    tests_digest: sha256(bytes(tests)),
    executions_digest: sha256(bytes(executions)),
    mutations_digest: sha256(bytes(mutations)),
    coverage_count: expected.members.length,
    result: "pass",
    admission: "development-only",
  };
  const replayResult: DevelopmentReplayResult = {
    schema_version: "bte-development-replay-result/v1",
    replay_id: `replay/${expected.catalogue_id}`,
    catalogue_id: expected.catalogue_id,
    proof_receipt_sha256: sha256(bytes(proofReceipt)),
    recomposed_coverage_digest: sha256(
      canonicalize(executions.map(({ coverage_key }) => coverage_key).sort()),
    ),
    result: "pass",
  };
  if (
    replayResult.recomposed_coverage_digest !==
    sha256(canonicalize(expected.members.map(({ coverage_key }) => coverage_key).sort()))
  ) {
    throw new ProofEngineError(
      "BTE_PROOF_REPLAY_MISMATCH",
      expected.catalogue_id,
      "execution coverage does not recompose",
    );
  }
  return {
    catalogue: expected,
    generated,
    tests,
    executions,
    mutations,
    proofReceipt,
    replayResult,
  };
}

export function runDevelopmentCore(
  project: DevelopmentProject,
  build: DevelopmentBuild,
): DevelopmentCoreRun {
  if (replayDevelopmentBuild(project, build).result !== "pass") {
    throw new ProofEngineError(
      "BTE_PROOF_BUILD_INVALID",
      project.project_id,
      "build replay must pass before proof",
    );
  }
  const expected = createDevelopmentSpecCatalogues(project);
  const generated = deriveDevelopmentCatalogues(build);
  const catalogueRuns = CATALOGUE_IDS.map((catalogueId) => {
    const expectedCatalogue = expected.find(
      (entry) => entry.catalogue_id === catalogueId,
    );
    const generatedCatalogue = generated.find(
      (entry) => entry.catalogue_id === catalogueId,
    );
    if (!expectedCatalogue || !generatedCatalogue) {
      throw new ProofEngineError(
        "BTE_PROOF_CATALOGUE_MISSING",
        catalogueId,
        "required catalogue is absent",
      );
    }
    return runCatalogue(expectedCatalogue, generatedCatalogue, build);
  });
  const replayHandles = catalogueRuns.map((run) => ({
    catalogue_id: run.catalogue.catalogue_id,
    sha256: sha256(bytes(run.replayResult)),
    coverage_count: run.catalogue.members.length,
  }));
  if (
    !CATALOGUE_IDS.every((catalogueId) =>
      replayHandles.some((handle) => handle.catalogue_id === catalogueId),
    ) ||
    new Set(replayHandles.map(({ catalogue_id }) => catalogue_id)).size !==
      CATALOGUE_IDS.length
  ) {
    throw new ProofEngineError(
      "BTE_PROOF_CORE_INCOMPLETE",
      project.project_id,
      "core does not contain exactly one replay for every catalogue",
    );
  }
  const aggregate: DevelopmentCoreAggregate = {
    schema_version: "bte-development-core-aggregate/v1",
    aggregate_id: "bte-development-core",
    build_receipt_sha256: sha256(build.receiptBytes),
    required_catalogues: [...CATALOGUE_IDS],
    replay_handles: replayHandles,
    total_coverage_count: replayHandles.reduce(
      (sum, handle) => sum + handle.coverage_count,
      0,
    ),
    result: "pass",
    admission: "development-only",
  };
  return {
    catalogueRuns,
    aggregate,
    aggregateBytes: bytes(aggregate),
  };
}

export function replayDevelopmentCore(
  project: DevelopmentProject,
  build: DevelopmentBuild,
  core: DevelopmentCoreRun,
): { result: "pass" | "fail"; codes: ProofEngineErrorCode[] } {
  try {
    const expected = runDevelopmentCore(project, build);
    if (
      core.aggregateBytes !== bytes(core.aggregate) ||
      core.aggregateBytes !== expected.aggregateBytes ||
      canonicalize(core.aggregate) !== canonicalize(expected.aggregate) ||
      canonicalize(core.catalogueRuns) !== canonicalize(expected.catalogueRuns)
    ) {
      return { result: "fail", codes: ["BTE_PROOF_REPLAY_MISMATCH"] };
    }
    return { result: "pass", codes: [] };
  } catch (error) {
    if (error instanceof ProofEngineError) {
      return { result: "fail", codes: [error.code] };
    }
    throw error;
  }
}
