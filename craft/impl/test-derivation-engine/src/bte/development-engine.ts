import { canonicalize } from "./contract-publication.js";
import { sha256 } from "./validation/validate-semantics.js";

export const DEVELOPMENT_PROFILE_ID =
  "feature-with-independent-node-and-edge-files@1-dev";

export const BACKEND_KINDS = [
  "Entity",
  "Value Object",
  "Enum",
  "Operation",
  "Query",
  "Calculation",
  "Rule",
  "Policy",
  "Workflow",
  "Interface",
  "Event",
  "Mapping",
  "State Machine",
] as const;

export type BackendKind = (typeof BACKEND_KINDS)[number];

export const BACKEND_RELATIONSHIPS = [
  "performs",
  "produces",
  "produces-for",
  "creates",
  "triggers-cross",
  "enforces",
  "calculates",
  "transitions",
  "exposes",
  "orchestrates",
  "applies",
  "maps",
  "contains",
  "reads",
  "emits",
  "owns",
  "belongs-to",
] as const;

export type BackendRelationship = (typeof BACKEND_RELATIONSHIPS)[number];

export type DevelopmentCoverageMode =
  | "complete-profile"
  | "declared-subset";

type JsonObject = Record<string, unknown>;

export type DevelopmentNode = {
  node_id: string;
  feature_id: string;
  kind: BackendKind;
  intent: string;
  body: JsonObject;
  source_anchor?: string;
};

export type DevelopmentEdge = {
  edge_id: string;
  family: BackendRelationship;
  from: string;
  to: string;
  ordinal?: number;
  source_anchor?: string;
};

export type DevelopmentProject = {
  schema_version: "bte-development-project/v1";
  project_id: string;
  profile_id: typeof DEVELOPMENT_PROFILE_ID;
  coverage_mode?: DevelopmentCoverageMode;
  nodes: DevelopmentNode[];
  edges: DevelopmentEdge[];
};

type RelationshipContract = {
  source: readonly BackendKind[];
  target: readonly BackendKind[];
  scopes: readonly ("same-feature" | "cross-feature")[];
  ordered?: boolean;
};

export const RELATIONSHIP_CONTRACTS: Readonly<
  Record<BackendRelationship, RelationshipContract>
> = {
  performs: { source: ["Entity"], target: ["Operation"], scopes: ["same-feature"] },
  produces: { source: ["Operation"], target: ["Event"], scopes: ["same-feature"] },
  "produces-for": {
    source: ["Operation"],
    target: ["Entity"],
    scopes: ["cross-feature"],
  },
  creates: {
    source: ["Operation"],
    target: ["Entity"],
    scopes: ["same-feature"],
  },
  "triggers-cross": {
    source: ["Event"],
    target: ["Operation"],
    scopes: ["cross-feature"],
  },
  enforces: {
    source: ["Rule"],
    target: ["Operation"],
    scopes: ["same-feature", "cross-feature"],
  },
  calculates: {
    source: ["Calculation"],
    target: ["Operation"],
    scopes: ["same-feature"],
  },
  transitions: {
    source: ["Event"],
    target: ["State Machine"],
    scopes: ["same-feature", "cross-feature"],
  },
  exposes: {
    source: ["Interface"],
    target: ["Operation", "Query"],
    scopes: ["same-feature", "cross-feature"],
  },
  orchestrates: {
    source: ["Workflow"],
    target: ["Operation"],
    scopes: ["same-feature", "cross-feature"],
    ordered: true,
  },
  applies: {
    source: ["Policy"],
    target: ["Operation", "Calculation"],
    scopes: ["same-feature"],
  },
  maps: {
    source: ["Mapping"],
    target: ["Entity", "Interface"],
    scopes: ["same-feature", "cross-feature"],
  },
  contains: {
    source: ["Entity"],
    target: ["Value Object"],
    scopes: ["same-feature"],
  },
  reads: {
    source: ["Query", "Operation"],
    target: ["Entity"],
    scopes: ["same-feature"],
  },
  emits: { source: ["Entity"], target: ["Event"], scopes: ["same-feature"] },
  owns: {
    source: ["Entity"],
    target: ["Entity"],
    scopes: ["same-feature", "cross-feature"],
  },
  "belongs-to": {
    source: ["Entity"],
    target: ["Entity"],
    scopes: ["same-feature", "cross-feature"],
  },
};

export const DEVELOPMENT_ENGINE_ERROR_CODES = [
  "BTE_DEV_PROFILE_INVALID",
  "BTE_DEV_PROFILE_INCOMPLETE",
  "BTE_DEV_NODE_DUPLICATE",
  "BTE_DEV_EDGE_DUPLICATE",
  "BTE_DEV_FORMATION_INVALID",
  "BTE_DEV_EDGE_ENDPOINT_MISSING",
  "BTE_DEV_EDGE_ENDPOINT_KIND",
  "BTE_DEV_EDGE_SCOPE",
  "BTE_DEV_EDGE_ORDER",
  "BTE_DEV_BUILD_REPLAY_MISMATCH",
] as const;

export type DevelopmentEngineErrorCode =
  (typeof DEVELOPMENT_ENGINE_ERROR_CODES)[number];

export type DevelopmentDiagnostic = {
  code: DevelopmentEngineErrorCode;
  subject: string;
  criterion:
    | "project-envelope"
    | "node-envelope"
    | "node-identity"
    | "node-formation"
    | "kind-membership"
    | "edge-envelope"
    | "edge-identity"
    | "edge-endpoint"
    | "edge-contract"
    | "edge-scope"
    | "edge-order"
    | "relationship-membership";
  source_anchor: string;
  detail: string;
};

export type DevelopmentValidationResult = {
  result: "pass" | "fail";
  diagnostics: DevelopmentDiagnostic[];
};

export class DevelopmentEngineError extends Error {
  readonly code: DevelopmentEngineErrorCode;
  readonly subject: string;

  constructor(code: DevelopmentEngineErrorCode, subject: string, detail: string) {
    super(`${code}:${subject}:${detail}`);
    this.name = "DevelopmentEngineError";
    this.code = code;
    this.subject = subject;
  }
}

export type DevelopmentGraph = {
  schema_version: "bte-development-graph/v1";
  project_id: string;
  profile_id: typeof DEVELOPMENT_PROFILE_ID;
  coverage_mode: DevelopmentCoverageMode;
  nodes: DevelopmentNode[];
  edges: DevelopmentEdge[];
};

export type DevelopmentSourceManifest = {
  schema_version: "bte-development-source-manifest/v1";
  project_id: string;
  source_set_digest: string;
  records: Array<{
    record_type: "node" | "edge";
    record_id: string;
    source_digest: string;
  }>;
};

export type DevelopmentBuildReceipt = {
  schema_version: "bte-development-build-receipt/v1";
  receipt_kind: "build";
  project_id: string;
  profile_id: typeof DEVELOPMENT_PROFILE_ID;
  profile_digest: string;
  coverage_mode: DevelopmentCoverageMode;
  coverage_set_digest: string;
  source_set_digest: string;
  graph_sha256: string;
  source_manifest_sha256: string;
  kind_set: BackendKind[];
  relationship_set: BackendRelationship[];
  result: "pass";
  admission: "development-only";
};

export type DevelopmentBuild = {
  graph: DevelopmentGraph;
  sourceManifest: DevelopmentSourceManifest;
  receipt: DevelopmentBuildReceipt;
  graphBytes: string;
  sourceManifestBytes: string;
  receiptBytes: string;
};

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function nonemptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

function stringArray(value: unknown, minimum = 1): value is string[] {
  return (
    Array.isArray(value) &&
    value.length >= minimum &&
    value.every(nonemptyString) &&
    new Set(value).size === value.length
  );
}

function validFields(value: unknown): value is JsonObject[] {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    value.every(
      (field) =>
        isObject(field) &&
        nonemptyString(field.name) &&
        nonemptyString(field.type) &&
        typeof field.identity === "boolean",
    )
  );
}

function formationValid(node: DevelopmentNode): boolean {
  const body = node.body;
  switch (node.kind) {
    case "Entity":
      return validFields(body.fields) && body.fields.some((field) => field.identity === true);
    case "Value Object": {
      const fields = body.fields;
      return (
        validFields(fields) &&
        fields.every((field) => field.identity === false) &&
        isObject(body.equality) &&
        body.equality.strategy === "field-tuple" &&
        stringArray(body.equality.fields) &&
        body.equality.fields.every((field) =>
          fields.some((candidate) => candidate.name === field),
        )
      );
    }
    case "Enum":
      return stringArray(body.values);
    case "Operation":
      return body.state_change === "yes";
    case "Query":
      return body.state_change === "no";
    case "Calculation":
      return body.formal_return_type === "value";
    case "Rule":
      return body.formal_return_type === "boolean";
    case "Policy":
      return body.formal_return_type === "strategy";
    case "Workflow":
      return (
        (body.scope === "intra-feature" || body.scope === "cross-feature") &&
        stringArray(body.steps)
      );
    case "Interface":
      return body.interface_kind === "internal" || body.interface_kind === "external";
    case "Event":
      return body.temporal === "past";
    case "Mapping":
      return (
        body.direction === "inbound" ||
        body.direction === "outbound" ||
        body.direction === "bidirectional"
      );
    case "State Machine":
      return body.has_transitions === "yes" && stringArray(body.states, 2);
  }
}

function developmentDiagnostic(
  code: DevelopmentEngineErrorCode,
  subject: string,
  criterion: DevelopmentDiagnostic["criterion"],
  sourceAnchor: string,
  detail: string,
): DevelopmentDiagnostic {
  return {
    code,
    subject,
    criterion,
    source_anchor: sourceAnchor,
    detail,
  };
}

function diagnosticOrder(left: DevelopmentDiagnostic, right: DevelopmentDiagnostic): number {
  return (
    DEVELOPMENT_ENGINE_ERROR_CODES.indexOf(left.code) -
      DEVELOPMENT_ENGINE_ERROR_CODES.indexOf(right.code) ||
    left.subject.localeCompare(right.subject) ||
    left.criterion.localeCompare(right.criterion) ||
    left.source_anchor.localeCompare(right.source_anchor) ||
    left.detail.localeCompare(right.detail)
  );
}

function validationResult(
  diagnostics: DevelopmentDiagnostic[],
): DevelopmentValidationResult {
  const ordered = [...diagnostics].sort(diagnosticOrder);
  return {
    result: ordered.length === 0 ? "pass" : "fail",
    diagnostics: ordered,
  };
}

function nodeAnchor(node: DevelopmentNode): string {
  return node.source_anchor ?? `node:${node.node_id || "unknown"}`;
}

function edgeAnchor(edge: DevelopmentEdge): string {
  return edge.source_anchor ?? `edge:${edge.edge_id || "unknown"}`;
}

export function validateDevelopmentNode(
  node: DevelopmentNode,
): DevelopmentValidationResult {
  const diagnostics: DevelopmentDiagnostic[] = [];
  const subject = nonemptyString(node.node_id) ? node.node_id : "node";
  const anchor = nodeAnchor(node);
  const kindValid = BACKEND_KINDS.includes(node.kind);

  if (
    !nonemptyString(node.node_id) ||
    !nonemptyString(node.feature_id) ||
    !nonemptyString(node.intent) ||
    !kindValid
  ) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_PROFILE_INVALID",
        subject,
        "node-envelope",
        anchor,
        "node id, feature id, intent, or backend kind is invalid",
      ),
    );
  }
  if (kindValid && !formationValid(node)) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_FORMATION_INVALID",
        subject,
        "node-formation",
        anchor,
        `${node.kind} body does not satisfy development formation v1`,
      ),
    );
  }
  return validationResult(diagnostics);
}

export function validateDevelopmentEdge(
  edge: DevelopmentEdge,
  nodes: readonly DevelopmentNode[],
  edges: readonly DevelopmentEdge[] = [edge],
): DevelopmentValidationResult {
  const diagnostics: DevelopmentDiagnostic[] = [];
  const subject = nonemptyString(edge.edge_id) ? edge.edge_id : "edge";
  const anchor = edgeAnchor(edge);
  const familyValid = BACKEND_RELATIONSHIPS.includes(edge.family);

  if (
    !nonemptyString(edge.edge_id) ||
    !nonemptyString(edge.from) ||
    !nonemptyString(edge.to) ||
    !familyValid
  ) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_PROFILE_INVALID",
        subject,
        "edge-envelope",
        anchor,
        "edge id, endpoints, or relationship family is invalid",
      ),
    );
  }
  if (edges.filter(({ edge_id }) => edge_id === edge.edge_id).length > 1) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_EDGE_DUPLICATE",
        subject,
        "edge-identity",
        anchor,
        "edge id occurs more than once",
      ),
    );
  }
  if (!familyValid) return validationResult(diagnostics);

  const nodeById = new Map(nodes.map((node) => [node.node_id, node]));
  const source = nodeById.get(edge.from);
  const target = nodeById.get(edge.to);
  if (!source || !target) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_EDGE_ENDPOINT_MISSING",
        subject,
        "edge-endpoint",
        anchor,
        `missing ${!source ? edge.from : edge.to}`,
      ),
    );
    return validationResult(diagnostics);
  }

  const contract = RELATIONSHIP_CONTRACTS[edge.family];
  if (!contract.source.includes(source.kind) || !contract.target.includes(target.kind)) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_EDGE_ENDPOINT_KIND",
        subject,
        "edge-contract",
        anchor,
        `${source.kind} -> ${target.kind} is invalid for ${edge.family}`,
      ),
    );
  }
  const scope = source.feature_id === target.feature_id ? "same-feature" : "cross-feature";
  if (!contract.scopes.includes(scope)) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_EDGE_SCOPE",
        subject,
        "edge-scope",
        anchor,
        `${edge.family} does not admit ${scope}`,
      ),
    );
  }
  if (contract.ordered) {
    if (!Number.isInteger(edge.ordinal) || (edge.ordinal ?? -1) < 0) {
      diagnostics.push(
        developmentDiagnostic(
          "BTE_DEV_EDGE_ORDER",
          subject,
          "edge-order",
          anchor,
          "ordered relationship requires a nonnegative ordinal",
        ),
      );
    } else {
      const slot = `${edge.from}/${edge.family}/${edge.ordinal}`;
      const slotCount = edges.filter(
        (candidate) =>
          `${candidate.from}/${candidate.family}/${candidate.ordinal}` === slot,
      ).length;
      if (slotCount > 1) {
        diagnostics.push(
          developmentDiagnostic(
            "BTE_DEV_EDGE_ORDER",
            subject,
            "edge-order",
            anchor,
            `duplicate ordered slot ${slot}`,
          ),
        );
      }
    }
  }
  return validationResult(diagnostics);
}

export function collectDevelopmentProjectDiagnostics(
  project: DevelopmentProject,
): DevelopmentValidationResult {
  const diagnostics: DevelopmentDiagnostic[] = [];
  const coverageMode = project.coverage_mode ?? "complete-profile";
  if (
    project.schema_version !== "bte-development-project/v1" ||
    project.profile_id !== DEVELOPMENT_PROFILE_ID ||
    !nonemptyString(project.project_id) ||
    (coverageMode !== "complete-profile" && coverageMode !== "declared-subset")
  ) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_PROFILE_INVALID",
        project.project_id || "project",
        "project-envelope",
        `project:${project.project_id || "unknown"}`,
        "development project envelope or profile is invalid",
      ),
    );
  }

  for (const node of project.nodes) {
    diagnostics.push(...validateDevelopmentNode(node).diagnostics);
  }
  for (const nodeId of new Set(project.nodes.map(({ node_id }) => node_id))) {
    if (project.nodes.filter(({ node_id }) => node_id === nodeId).length > 1) {
      diagnostics.push(
        developmentDiagnostic(
          "BTE_DEV_NODE_DUPLICATE",
          nodeId,
          "node-identity",
          `node:${nodeId}`,
          "node id occurs more than once",
        ),
      );
    }
  }

  const actualKinds = project.nodes.map(({ kind }) => kind);
  if (
    actualKinds.length === 0 ||
    (coverageMode === "complete-profile" &&
      !exactMembers(BACKEND_KINDS, actualKinds))
  ) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_PROFILE_INCOMPLETE",
        project.project_id,
        "kind-membership",
        `project:${project.project_id}`,
        "project must exercise every exact backend kind",
      ),
    );
  }

  for (const edge of project.edges) {
    diagnostics.push(
      ...validateDevelopmentEdge(edge, project.nodes, project.edges).diagnostics,
    );
  }
  const actualRelationships = project.edges.map(({ family }) => family);
  if (
    actualRelationships.length === 0 ||
    (coverageMode === "complete-profile" &&
      !exactMembers(BACKEND_RELATIONSHIPS, actualRelationships))
  ) {
    diagnostics.push(
      developmentDiagnostic(
        "BTE_DEV_PROFILE_INCOMPLETE",
        project.project_id,
        "relationship-membership",
        `project:${project.project_id}`,
        "project must exercise every exact backend relationship family",
      ),
    );
  }
  return validationResult(diagnostics);
}

function sortedUnique<T extends string>(values: readonly T[]): T[] {
  return [...new Set(values)].sort() as T[];
}

function exactMembers<T extends string>(
  expected: readonly T[],
  actual: readonly T[],
): boolean {
  return canonicalize(sortedUnique(expected)) === canonicalize(sortedUnique(actual));
}

function profileDigest(): string {
  return sha256(
    canonicalize({
      profile_id: DEVELOPMENT_PROFILE_ID,
      kinds: BACKEND_KINDS,
      relationships: BACKEND_RELATIONSHIPS,
      relationship_contracts: RELATIONSHIP_CONTRACTS,
      formation_version: "bte-development-formation/v1",
    }),
  );
}

function coverageSetDigest(
  coverageMode: DevelopmentCoverageMode,
  kinds: readonly BackendKind[],
  relationships: readonly BackendRelationship[],
): string {
  return sha256(
    canonicalize({
      coverage_mode: coverageMode,
      kinds: sortedUnique(kinds),
      relationships: sortedUnique(relationships),
    }),
  );
}

function canonicalBytes(value: unknown): string {
  return `${canonicalize(value)}\n`;
}

export function compileDevelopmentProject(
  project: DevelopmentProject,
): DevelopmentBuild {
  const coverageMode = project.coverage_mode ?? "complete-profile";
  const collected = collectDevelopmentProjectDiagnostics(project);
  if (collected.result === "fail") {
    const first = collected.diagnostics[0]!;
    throw new DevelopmentEngineError(first.code, first.subject, first.detail);
  }
  if (
    project.schema_version !== "bte-development-project/v1" ||
    project.profile_id !== DEVELOPMENT_PROFILE_ID ||
    !nonemptyString(project.project_id) ||
    (coverageMode !== "complete-profile" &&
      coverageMode !== "declared-subset")
  ) {
    throw new DevelopmentEngineError(
      "BTE_DEV_PROFILE_INVALID",
      project.project_id || "project",
      "development project envelope or profile is invalid",
    );
  }
  const nodeById = new Map<string, DevelopmentNode>();
  for (const node of project.nodes) {
    if (nodeById.has(node.node_id)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_NODE_DUPLICATE",
        node.node_id,
        "node id occurs more than once",
      );
    }
    if (
      !nonemptyString(node.node_id) ||
      !nonemptyString(node.feature_id) ||
      !nonemptyString(node.intent) ||
      !BACKEND_KINDS.includes(node.kind)
    ) {
      throw new DevelopmentEngineError(
        "BTE_DEV_PROFILE_INVALID",
        node.node_id,
        "node envelope is invalid",
      );
    }
    if (!formationValid(node)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_FORMATION_INVALID",
        node.node_id,
        `${node.kind} body does not satisfy development formation v1`,
      );
    }
    nodeById.set(node.node_id, node);
  }
  const actualKinds = project.nodes.map(({ kind }) => kind);
  if (
    actualKinds.length === 0 ||
    (coverageMode === "complete-profile" &&
      !exactMembers(BACKEND_KINDS, actualKinds))
  ) {
    throw new DevelopmentEngineError(
      "BTE_DEV_PROFILE_INCOMPLETE",
      project.project_id,
      "project must exercise every exact backend kind",
    );
  }

  const edgeIds = new Set<string>();
  const orderedSlots = new Set<string>();
  for (const edge of project.edges) {
    if (edgeIds.has(edge.edge_id)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_EDGE_DUPLICATE",
        edge.edge_id,
        "edge id occurs more than once",
      );
    }
    edgeIds.add(edge.edge_id);
    if (!BACKEND_RELATIONSHIPS.includes(edge.family)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_PROFILE_INVALID",
        edge.edge_id,
        "edge relationship family is outside the development profile",
      );
    }
    const source = nodeById.get(edge.from);
    const target = nodeById.get(edge.to);
    if (!source || !target) {
      throw new DevelopmentEngineError(
        "BTE_DEV_EDGE_ENDPOINT_MISSING",
        edge.edge_id,
        `missing ${!source ? edge.from : edge.to}`,
      );
    }
    const contract = RELATIONSHIP_CONTRACTS[edge.family];
    if (!contract.source.includes(source.kind) || !contract.target.includes(target.kind)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_EDGE_ENDPOINT_KIND",
        edge.edge_id,
        `${source.kind} -> ${target.kind} is invalid for ${edge.family}`,
      );
    }
    const scope = source.feature_id === target.feature_id ? "same-feature" : "cross-feature";
    if (!contract.scopes.includes(scope)) {
      throw new DevelopmentEngineError(
        "BTE_DEV_EDGE_SCOPE",
        edge.edge_id,
        `${edge.family} does not admit ${scope}`,
      );
    }
    if (contract.ordered) {
      if (!Number.isInteger(edge.ordinal) || (edge.ordinal ?? -1) < 0) {
        throw new DevelopmentEngineError(
          "BTE_DEV_EDGE_ORDER",
          edge.edge_id,
          "ordered relationship requires a nonnegative ordinal",
        );
      }
      const slot = `${edge.from}/${edge.family}/${edge.ordinal}`;
      if (orderedSlots.has(slot)) {
        throw new DevelopmentEngineError(
          "BTE_DEV_EDGE_ORDER",
          edge.edge_id,
          `duplicate ordered slot ${slot}`,
        );
      }
      orderedSlots.add(slot);
    }
  }
  const actualRelationships = project.edges.map(({ family }) => family);
  if (
    actualRelationships.length === 0 ||
    (coverageMode === "complete-profile" &&
      !exactMembers(BACKEND_RELATIONSHIPS, actualRelationships))
  ) {
    throw new DevelopmentEngineError(
      "BTE_DEV_PROFILE_INCOMPLETE",
      project.project_id,
      "project must exercise every exact backend relationship family",
    );
  }

  const nodes = [...project.nodes].sort((left, right) =>
    left.node_id.localeCompare(right.node_id),
  );
  const edges = [...project.edges].sort((left, right) =>
    left.edge_id.localeCompare(right.edge_id),
  );
  const records: DevelopmentSourceManifest["records"] = [
    ...nodes.map((node) => ({
      record_type: "node" as const,
      record_id: node.node_id,
      source_digest: sha256(canonicalize(node)),
    })),
    ...edges.map((edge) => ({
      record_type: "edge" as const,
      record_id: edge.edge_id,
      source_digest: sha256(canonicalize(edge)),
    })),
  ].sort((left, right) =>
    left.record_type.localeCompare(right.record_type) ||
    left.record_id.localeCompare(right.record_id),
  );
  const sourceSetDigest = sha256(canonicalize(records));
  const graph: DevelopmentGraph = {
    schema_version: "bte-development-graph/v1",
    project_id: project.project_id,
    profile_id: DEVELOPMENT_PROFILE_ID,
    coverage_mode: coverageMode,
    nodes,
    edges,
  };
  const sourceManifest: DevelopmentSourceManifest = {
    schema_version: "bte-development-source-manifest/v1",
    project_id: project.project_id,
    source_set_digest: sourceSetDigest,
    records,
  };
  const graphBytes = canonicalBytes(graph);
  const sourceManifestBytes = canonicalBytes(sourceManifest);
  const receipt: DevelopmentBuildReceipt = {
    schema_version: "bte-development-build-receipt/v1",
    receipt_kind: "build",
    project_id: project.project_id,
    profile_id: DEVELOPMENT_PROFILE_ID,
    profile_digest: profileDigest(),
    coverage_mode: coverageMode,
    coverage_set_digest: coverageSetDigest(
      coverageMode,
      actualKinds,
      actualRelationships,
    ),
    source_set_digest: sourceSetDigest,
    graph_sha256: sha256(graphBytes),
    source_manifest_sha256: sha256(sourceManifestBytes),
    kind_set: sortedUnique(actualKinds),
    relationship_set: sortedUnique(actualRelationships),
    result: "pass",
    admission: "development-only",
  };
  return {
    graph,
    sourceManifest,
    receipt,
    graphBytes,
    sourceManifestBytes,
    receiptBytes: canonicalBytes(receipt),
  };
}

export function replayDevelopmentBuild(
  project: DevelopmentProject,
  build: DevelopmentBuild,
): { result: "pass" | "fail"; codes: DevelopmentEngineErrorCode[] } {
  try {
    const expected = compileDevelopmentProject(project);
    if (
      build.graphBytes !== canonicalBytes(build.graph) ||
      build.sourceManifestBytes !== canonicalBytes(build.sourceManifest) ||
      build.receiptBytes !== canonicalBytes(build.receipt) ||
      build.graphBytes !== expected.graphBytes ||
      build.sourceManifestBytes !== expected.sourceManifestBytes ||
      build.receiptBytes !== expected.receiptBytes ||
      sha256(build.graphBytes) !== build.receipt.graph_sha256 ||
      sha256(build.sourceManifestBytes) !== build.receipt.source_manifest_sha256
    ) {
      return { result: "fail", codes: ["BTE_DEV_BUILD_REPLAY_MISMATCH"] };
    }
    return { result: "pass", codes: [] };
  } catch (error) {
    if (error instanceof DevelopmentEngineError) {
      return { result: "fail", codes: [error.code] };
    }
    throw error;
  }
}
