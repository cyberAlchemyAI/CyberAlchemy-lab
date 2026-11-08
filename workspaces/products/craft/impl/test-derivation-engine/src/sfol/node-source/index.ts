import { createHash } from "node:crypto";

import type { NodeLogicModuleV1 } from "../language/ast.js";
import { canonicalJson } from "../language/contracts.js";
import {
  decodeNodeLogicModule,
  type SfolDecodeDiagnostic,
} from "../language/decoder.js";

export const NODE_PROOF_CONTEXT_VERSION =
  "domainspec-sfol-node-proof-context/v1" as const;
export const NODE_PROJECTION_ADMISSION_VERSION =
  "domainspec-sfol-node-projection-admission/v1" as const;
export const NODE_LOGIC_ENVELOPE_VERSION =
  "domainspec-sfol-node-logic-envelope/v1" as const;

export interface CanonicalNodeProofContextInput {
  readonly schema_version: typeof NODE_PROOF_CONTEXT_VERSION;
  readonly route: "canonical-minted-project-build";
  readonly graph_bytes: string;
  readonly source_manifest_bytes: string;
  readonly build_receipt_bytes: string;
}

export interface NodeProjectionAdmission {
  readonly schema_version: typeof NODE_PROJECTION_ADMISSION_VERSION;
  readonly profile_id: string;
  readonly profile_version: string;
  readonly logic_schema_versions: readonly string[];
  readonly admitted_node_ids: readonly string[];
}

export interface NodeLogicEnvelope {
  readonly schema_version: typeof NODE_LOGIC_ENVELOPE_VERSION;
  readonly proof_context: {
    readonly project_id: string;
    readonly profile_id: string;
    readonly profile_version: string;
    readonly profile_digest: string;
    readonly kinds_digest: string;
    readonly relationships_digest: string;
    readonly source_set_digest: string;
    readonly graph_digest: string;
    readonly manifest_digest: string;
    readonly build_receipt_digest: string;
    readonly generator_version: string;
  };
  readonly node: {
    readonly node_id: string;
    readonly feature_id: string;
    readonly kind: string;
    readonly source_path: string;
    readonly node_digest: string;
  };
  readonly module_id: string;
  readonly logic_digest: string;
  readonly logic: NodeLogicModuleV1;
}

export type NodeProjectionDiagnosticCode =
  | "SFOL_SOURCE_NONCANONICAL"
  | "SFOL_SOURCE_INVALID_JSON"
  | "SFOL_SOURCE_GRAPH_INVALID"
  | "SFOL_SOURCE_MANIFEST_INVALID"
  | "SFOL_SOURCE_BUILD_RECEIPT_INVALID"
  | "SFOL_SOURCE_STALE_GRAPH"
  | "SFOL_SOURCE_STALE_MANIFEST"
  | "SFOL_SOURCE_HANDLE_MISMATCH"
  | "SFOL_SOURCE_PROFILE_NOT_ADMITTED"
  | "SFOL_SOURCE_BIJECTION_MISMATCH"
  | "SFOL_SOURCE_DUPLICATE_ID"
  | "SFOL_SOURCE_LOGIC_INVALID"
  | "SFOL_SOURCE_OWNERSHIP_MISMATCH";

export interface NodeProjectionDiagnostic {
  readonly code: NodeProjectionDiagnosticCode;
  readonly stage: "node-source";
  readonly subject: string;
  readonly detail: string;
  readonly decode_diagnostics?: readonly SfolDecodeDiagnostic[];
}

export type NodeProjectionResult =
  | {
      readonly ok: true;
      readonly value: readonly NodeLogicEnvelope[];
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly NodeProjectionDiagnostic[];
    };

type WireNode = {
  readonly node_id: string;
  readonly feature_id: string;
  readonly kind: string;
  readonly intent: string;
  readonly body: Readonly<Record<string, unknown>>;
};

type WireGraph = {
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly language: {
    readonly profile_digest: string;
    readonly kinds_digest: string;
    readonly relationships_digest: string;
  };
  readonly nodes: readonly WireNode[];
  readonly edges: readonly {
    readonly edge_id: string;
    readonly type: string;
    readonly from: string;
    readonly to: string;
  }[];
};

type WireManifest = {
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly inputs: readonly {
    readonly path: string;
    readonly digest: string;
  }[];
  readonly records: readonly {
    readonly record_type: "node" | "edge";
    readonly graph_id: string;
    readonly source_path: string;
    readonly source_digest: string;
  }[];
};

type WireBuildReceipt = {
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly language: {
    readonly profile_id: string;
    readonly profile_version: string;
    readonly profile_digest: string;
    readonly kinds_digest: string;
    readonly relationships_digest: string;
  };
  readonly artifacts: {
    readonly graph_digest: string;
    readonly source_manifest_digest: string;
    readonly markdown_view_digest: string;
    readonly markdown_content_digest: string;
  };
  readonly generator_version: string;
};

const SHA256 = /^[0-9a-f]{64}$/;

class ProjectionAbort extends Error {
  readonly diagnostic: NodeProjectionDiagnostic;

  constructor(diagnostic: NodeProjectionDiagnostic) {
    super(`${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`);
    this.name = "ProjectionAbort";
    this.diagnostic = diagnostic;
  }
}

export function projectNodeLogic(
  input: unknown,
  admissionInput: unknown,
): NodeProjectionResult {
  try {
    const canonicalInput = parseCanonicalInput(input);
    const admission = parseAdmission(admissionInput);
    const graph = parseGraph(canonicalInput.graph_bytes);
    const manifest = parseManifest(canonicalInput.source_manifest_bytes);
    const receipt = parseBuildReceipt(canonicalInput.build_receipt_bytes);
    validateArtifactHandles(canonicalInput, graph, manifest, receipt);
    validateAdmission(admission, receipt);
    const recordById = validateGraphManifestBijection(graph, manifest);
    const admittedIds = [...admission.admitted_node_ids].sort();
    const logicIds = graph.nodes
      .filter((node) => Object.hasOwn(node.body, "logic"))
      .map((node) => node.node_id)
      .sort();
    if (!equalStrings(admittedIds, logicIds)) {
      projectionFail(
        "SFOL_SOURCE_BIJECTION_MISMATCH",
        "admitted_node_ids",
        `admitted nodes [${admittedIds.join(",")}] do not equal graph logic nodes [${logicIds.join(",")}]`,
      );
    }

    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]));
    const moduleIds = new Set<string>();
    const clauseIds = new Set<string>();
    const proofContext = Object.freeze({
      project_id: graph.project_id,
      profile_id: receipt.language.profile_id,
      profile_version: receipt.language.profile_version,
      profile_digest: receipt.language.profile_digest,
      kinds_digest: receipt.language.kinds_digest,
      relationships_digest: receipt.language.relationships_digest,
      source_set_digest: receipt.source_set_digest,
      graph_digest: receipt.artifacts.graph_digest,
      manifest_digest: receipt.artifacts.source_manifest_digest,
      build_receipt_digest: sha256(canonicalInput.build_receipt_bytes),
      generator_version: receipt.generator_version,
    });

    const envelopes = admittedIds.map((nodeId): NodeLogicEnvelope => {
      const node = nodeById.get(nodeId);
      const record = recordById.get(nodeId);
      if (node === undefined || record === undefined) {
        projectionFail(
          "SFOL_SOURCE_BIJECTION_MISMATCH",
          nodeId,
          "admitted node is absent from graph or source manifest",
        );
      }
      const decoded = decodeNodeLogicModule(node.body.logic);
      if (!decoded.ok) {
        projectionFail(
          "SFOL_SOURCE_LOGIC_INVALID",
          nodeId,
          "body.logic is not a supported structured node logic module",
          decoded.diagnostics,
        );
      }
      const logic = decoded.value;
      if (
        !admission.logic_schema_versions.includes(logic.schema_version)
      ) {
        projectionFail(
          "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
          nodeId,
          `logic version ${logic.schema_version} is not admitted`,
        );
      }
      if (
        logic.source.node_id !== node.node_id ||
        logic.source.feature_id !== node.feature_id ||
        logic.source.source_id !== node.node_id ||
        logic.source.source_path !== record.source_path
      ) {
        projectionFail(
          "SFOL_SOURCE_OWNERSHIP_MISMATCH",
          nodeId,
          "logic source identity does not match its graph node and manifest record",
        );
      }
      if (moduleIds.has(logic.module_id)) {
        projectionFail(
          "SFOL_SOURCE_DUPLICATE_ID",
          logic.module_id,
          "module_id must be unique in one proof context",
        );
      }
      moduleIds.add(logic.module_id);
      for (const clause of logic.clauses) {
        if (clauseIds.has(clause.clause_id)) {
          projectionFail(
            "SFOL_SOURCE_DUPLICATE_ID",
            clause.clause_id,
            "clause_id must be unique in one proof context",
          );
        }
        clauseIds.add(clause.clause_id);
      }
      return deepFreeze({
        schema_version: NODE_LOGIC_ENVELOPE_VERSION,
        proof_context: proofContext,
        node: {
          node_id: node.node_id,
          feature_id: node.feature_id,
          kind: node.kind,
          source_path: record.source_path,
          node_digest: record.source_digest,
        },
        module_id: logic.module_id,
        logic_digest: sha256(canonicalJson(logic)),
        logic,
      });
    });

    return Object.freeze({
      ok: true,
      value: Object.freeze(envelopes),
    });
  } catch (error: unknown) {
    if (error instanceof ProjectionAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_SOURCE_NONCANONICAL",
          stage: "node-source",
          subject: "proof-context",
          detail: "node projection input is structurally invalid",
        }),
      ]),
    });
  }
}

function parseCanonicalInput(input: unknown): CanonicalNodeProofContextInput {
  const value = exactRecord(
    input,
    "proof-context",
    [
      "schema_version",
      "route",
      "graph_bytes",
      "source_manifest_bytes",
      "build_receipt_bytes",
    ],
    "SFOL_SOURCE_NONCANONICAL",
  );
  if (
    value.schema_version !== NODE_PROOF_CONTEXT_VERSION ||
    value.route !== "canonical-minted-project-build"
  ) {
    projectionFail(
      "SFOL_SOURCE_NONCANONICAL",
      "proof-context",
      "only the canonical minted-project build route is supported",
    );
  }
  return Object.freeze({
    schema_version: NODE_PROOF_CONTEXT_VERSION,
    route: "canonical-minted-project-build",
    graph_bytes: requiredString(
      value.graph_bytes,
      "proof-context.graph_bytes",
      "SFOL_SOURCE_NONCANONICAL",
    ),
    source_manifest_bytes: requiredString(
      value.source_manifest_bytes,
      "proof-context.source_manifest_bytes",
      "SFOL_SOURCE_NONCANONICAL",
    ),
    build_receipt_bytes: requiredString(
      value.build_receipt_bytes,
      "proof-context.build_receipt_bytes",
      "SFOL_SOURCE_NONCANONICAL",
    ),
  });
}

function parseAdmission(input: unknown): NodeProjectionAdmission {
  const value = exactRecord(
    input,
    "admission",
    [
      "schema_version",
      "profile_id",
      "profile_version",
      "logic_schema_versions",
      "admitted_node_ids",
    ],
    "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
  );
  if (value.schema_version !== NODE_PROJECTION_ADMISSION_VERSION) {
    projectionFail(
      "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
      "admission.schema_version",
      "unsupported node-projection admission version",
    );
  }
  const logicVersions = stringArray(
    value.logic_schema_versions,
    "admission.logic_schema_versions",
    "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
  );
  const admittedNodeIds = stringArray(
    value.admitted_node_ids,
    "admission.admitted_node_ids",
    "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
  );
  assertUnique(
    logicVersions,
    "admission.logic_schema_versions",
    "SFOL_SOURCE_DUPLICATE_ID",
  );
  assertUnique(
    admittedNodeIds,
    "admission.admitted_node_ids",
    "SFOL_SOURCE_DUPLICATE_ID",
  );
  return Object.freeze({
    schema_version: NODE_PROJECTION_ADMISSION_VERSION,
    profile_id: requiredString(
      value.profile_id,
      "admission.profile_id",
      "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
    ),
    profile_version: requiredString(
      value.profile_version,
      "admission.profile_version",
      "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
    ),
    logic_schema_versions: Object.freeze([...logicVersions].sort()),
    admitted_node_ids: Object.freeze([...admittedNodeIds].sort()),
  });
}

function parseGraph(bytes: string): WireGraph {
  const value = parseJson(bytes, "graph");
  const graph = exactRecord(
    value,
    "graph",
    [
      "schema_version",
      "authority",
      "project_id",
      "language",
      "source_set_digest",
      "nodes",
      "edges",
    ],
    "SFOL_SOURCE_GRAPH_INVALID",
  );
  if (
    graph.schema_version !== "minted-graph/v1" ||
    graph.authority !== "generated-semantic-read-model"
  ) {
    projectionFail(
      "SFOL_SOURCE_GRAPH_INVALID",
      "graph",
      "unsupported graph schema or authority",
    );
  }
  const language = exactRecord(
    graph.language,
    "graph.language",
    ["profile_digest", "kinds_digest", "relationships_digest"],
    "SFOL_SOURCE_GRAPH_INVALID",
  );
  const nodes = arrayValue(
    graph.nodes,
    "graph.nodes",
    "SFOL_SOURCE_GRAPH_INVALID",
  ).map((item, index): WireNode => {
    const node = exactRecord(
      item,
      `graph.nodes[${index}]`,
      ["node_id", "feature_id", "kind", "intent", "body"],
      "SFOL_SOURCE_GRAPH_INVALID",
    );
    return {
      node_id: requiredString(
        node.node_id,
        `graph.nodes[${index}].node_id`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      feature_id: requiredString(
        node.feature_id,
        `graph.nodes[${index}].feature_id`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      kind: requiredString(
        node.kind,
        `graph.nodes[${index}].kind`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      intent: requiredString(
        node.intent,
        `graph.nodes[${index}].intent`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      body: exactRecord(
        node.body,
        `graph.nodes[${index}].body`,
        Object.keys(requireRecord(node.body, `graph.nodes[${index}].body`)),
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
    };
  });
  const edges = arrayValue(
    graph.edges,
    "graph.edges",
    "SFOL_SOURCE_GRAPH_INVALID",
  ).map((item, index) => {
    const edge = exactRecord(
      item,
      `graph.edges[${index}]`,
      ["edge_id", "type", "from", "to"],
      "SFOL_SOURCE_GRAPH_INVALID",
    );
    return {
      edge_id: requiredString(
        edge.edge_id,
        `graph.edges[${index}].edge_id`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      type: requiredString(
        edge.type,
        `graph.edges[${index}].type`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      from: requiredString(
        edge.from,
        `graph.edges[${index}].from`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      to: requiredString(
        edge.to,
        `graph.edges[${index}].to`,
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
    };
  });
  assertUnique(
    [...nodes.map((node) => node.node_id), ...edges.map((edge) => edge.edge_id)],
    "graph",
    "SFOL_SOURCE_DUPLICATE_ID",
  );
  return {
    project_id: requiredString(
      graph.project_id,
      "graph.project_id",
      "SFOL_SOURCE_GRAPH_INVALID",
    ),
    source_set_digest: requiredDigest(
      graph.source_set_digest,
      "graph.source_set_digest",
      "SFOL_SOURCE_GRAPH_INVALID",
    ),
    language: {
      profile_digest: requiredDigest(
        language.profile_digest,
        "graph.language.profile_digest",
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      kinds_digest: requiredDigest(
        language.kinds_digest,
        "graph.language.kinds_digest",
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
      relationships_digest: requiredDigest(
        language.relationships_digest,
        "graph.language.relationships_digest",
        "SFOL_SOURCE_GRAPH_INVALID",
      ),
    },
    nodes,
    edges,
  };
}

function parseManifest(bytes: string): WireManifest {
  const value = exactRecord(
    parseJson(bytes, "source-manifest"),
    "source-manifest",
    [
      "schema_version",
      "authority",
      "project_id",
      "source_set_digest",
      "inputs",
      "records",
    ],
    "SFOL_SOURCE_MANIFEST_INVALID",
  );
  if (
    value.schema_version !== "minted-source-manifest/v1" ||
    value.authority !== "generated-provenance-read-model"
  ) {
    projectionFail(
      "SFOL_SOURCE_MANIFEST_INVALID",
      "source-manifest",
      "unsupported manifest schema or authority",
    );
  }
  const inputs = arrayValue(
    value.inputs,
    "source-manifest.inputs",
    "SFOL_SOURCE_MANIFEST_INVALID",
  ).map((item, index) => {
    const input = exactRecord(
      item,
      `source-manifest.inputs[${index}]`,
      ["path", "digest"],
      "SFOL_SOURCE_MANIFEST_INVALID",
    );
    return {
      path: requiredPath(
        input.path,
        `source-manifest.inputs[${index}].path`,
      ),
      digest: requiredDigest(
        input.digest,
        `source-manifest.inputs[${index}].digest`,
        "SFOL_SOURCE_MANIFEST_INVALID",
      ),
    };
  });
  assertUnique(
    inputs.map((input) => input.path),
    "source-manifest.inputs",
    "SFOL_SOURCE_DUPLICATE_ID",
  );
  const records = arrayValue(
    value.records,
    "source-manifest.records",
    "SFOL_SOURCE_MANIFEST_INVALID",
  ).map((item, index): WireManifest["records"][number] => {
    const record = exactRecord(
      item,
      `source-manifest.records[${index}]`,
      ["record_type", "graph_id", "source_path", "source_digest"],
      "SFOL_SOURCE_MANIFEST_INVALID",
    );
    if (record.record_type !== "node" && record.record_type !== "edge") {
      projectionFail(
        "SFOL_SOURCE_MANIFEST_INVALID",
        `source-manifest.records[${index}].record_type`,
        "record_type must be node or edge",
      );
    }
    return {
      record_type: record.record_type,
      graph_id: requiredString(
        record.graph_id,
        `source-manifest.records[${index}].graph_id`,
        "SFOL_SOURCE_MANIFEST_INVALID",
      ),
      source_path: requiredPath(
        record.source_path,
        `source-manifest.records[${index}].source_path`,
      ),
      source_digest: requiredDigest(
        record.source_digest,
        `source-manifest.records[${index}].source_digest`,
        "SFOL_SOURCE_MANIFEST_INVALID",
      ),
    };
  });
  assertUnique(
    records.map((record) => record.graph_id),
    "source-manifest.records",
    "SFOL_SOURCE_DUPLICATE_ID",
  );
  return {
    project_id: requiredString(
      value.project_id,
      "source-manifest.project_id",
      "SFOL_SOURCE_MANIFEST_INVALID",
    ),
    source_set_digest: requiredDigest(
      value.source_set_digest,
      "source-manifest.source_set_digest",
      "SFOL_SOURCE_MANIFEST_INVALID",
    ),
    inputs,
    records,
  };
}

function parseBuildReceipt(bytes: string): WireBuildReceipt {
  const value = exactRecord(
    parseJson(bytes, "build-receipt"),
    "build-receipt",
    [
      "schema_version",
      "authority",
      "status",
      "project_id",
      "language",
      "source_set_digest",
      "artifacts",
      "generator_version",
    ],
    "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
  );
  if (
    value.schema_version !== "minted-build-receipt/v1" ||
    value.authority !== "generated-verification-evidence" ||
    value.status !== "pass"
  ) {
    projectionFail(
      "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      "build-receipt",
      "build receipt must be supported generated passing evidence",
    );
  }
  const language = exactRecord(
    value.language,
    "build-receipt.language",
    [
      "profile_id",
      "profile_version",
      "profile_digest",
      "kinds_digest",
      "relationships_digest",
    ],
    "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
  );
  const artifacts = exactRecord(
    value.artifacts,
    "build-receipt.artifacts",
    [
      "graph_digest",
      "source_manifest_digest",
      "markdown_view_digest",
      "markdown_content_digest",
    ],
    "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
  );
  return {
    project_id: requiredString(
      value.project_id,
      "build-receipt.project_id",
      "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
    ),
    source_set_digest: requiredDigest(
      value.source_set_digest,
      "build-receipt.source_set_digest",
      "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
    ),
    language: {
      profile_id: requiredString(
        language.profile_id,
        "build-receipt.language.profile_id",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      profile_version: requiredString(
        language.profile_version,
        "build-receipt.language.profile_version",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      profile_digest: requiredDigest(
        language.profile_digest,
        "build-receipt.language.profile_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      kinds_digest: requiredDigest(
        language.kinds_digest,
        "build-receipt.language.kinds_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      relationships_digest: requiredDigest(
        language.relationships_digest,
        "build-receipt.language.relationships_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
    },
    artifacts: {
      graph_digest: requiredDigest(
        artifacts.graph_digest,
        "build-receipt.artifacts.graph_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      source_manifest_digest: requiredDigest(
        artifacts.source_manifest_digest,
        "build-receipt.artifacts.source_manifest_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      markdown_view_digest: requiredDigest(
        artifacts.markdown_view_digest,
        "build-receipt.artifacts.markdown_view_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
      markdown_content_digest: requiredDigest(
        artifacts.markdown_content_digest,
        "build-receipt.artifacts.markdown_content_digest",
        "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
      ),
    },
    generator_version: requiredString(
      value.generator_version,
      "build-receipt.generator_version",
      "SFOL_SOURCE_BUILD_RECEIPT_INVALID",
    ),
  };
}

function validateArtifactHandles(
  input: CanonicalNodeProofContextInput,
  graph: WireGraph,
  manifest: WireManifest,
  receipt: WireBuildReceipt,
): void {
  if (sha256(input.graph_bytes) !== receipt.artifacts.graph_digest) {
    projectionFail(
      "SFOL_SOURCE_STALE_GRAPH",
      "graph",
      "graph bytes do not match the build receipt",
    );
  }
  if (
    sha256(input.source_manifest_bytes) !==
    receipt.artifacts.source_manifest_digest
  ) {
    projectionFail(
      "SFOL_SOURCE_STALE_MANIFEST",
      "source-manifest",
      "source-manifest bytes do not match the build receipt",
    );
  }
  if (
    graph.project_id !== manifest.project_id ||
    graph.project_id !== receipt.project_id ||
    graph.source_set_digest !== manifest.source_set_digest ||
    graph.source_set_digest !== receipt.source_set_digest ||
    graph.language.profile_digest !== receipt.language.profile_digest ||
    graph.language.kinds_digest !== receipt.language.kinds_digest ||
    graph.language.relationships_digest !==
      receipt.language.relationships_digest
  ) {
    projectionFail(
      "SFOL_SOURCE_HANDLE_MISMATCH",
      "proof-context",
      "project, source-set, or language handles disagree",
    );
  }
}

function validateAdmission(
  admission: NodeProjectionAdmission,
  receipt: WireBuildReceipt,
): void {
  if (
    admission.profile_id !== receipt.language.profile_id ||
    admission.profile_version !== receipt.language.profile_version
  ) {
    projectionFail(
      "SFOL_SOURCE_PROFILE_NOT_ADMITTED",
      "admission",
      "build profile does not match the separately supplied admission",
    );
  }
}

function validateGraphManifestBijection(
  graph: WireGraph,
  manifest: WireManifest,
): ReadonlyMap<string, WireManifest["records"][number]> {
  const graphIds = [
    ...graph.nodes.map((node) => node.node_id),
    ...graph.edges.map((edge) => edge.edge_id),
  ].sort();
  const manifestIds = manifest.records.map((record) => record.graph_id).sort();
  if (!equalStrings(graphIds, manifestIds)) {
    projectionFail(
      "SFOL_SOURCE_BIJECTION_MISMATCH",
      "graph-manifest",
      "graph identities do not equal source-manifest identities",
    );
  }
  const inputByPath = new Map(
    manifest.inputs.map((input) => [input.path, input.digest]),
  );
  for (const record of manifest.records) {
    if (inputByPath.get(record.source_path) !== record.source_digest) {
      projectionFail(
        "SFOL_SOURCE_HANDLE_MISMATCH",
        record.graph_id,
        "manifest record digest does not match its input digest",
      );
    }
  }
  return new Map(
    manifest.records.map((record) => [record.graph_id, record]),
  );
}

function parseJson(bytes: string, subject: string): unknown {
  try {
    return JSON.parse(bytes) as unknown;
  } catch {
    projectionFail(
      "SFOL_SOURCE_INVALID_JSON",
      subject,
      `${subject} bytes are not JSON`,
    );
  }
}

function exactRecord(
  input: unknown,
  subject: string,
  keys: readonly string[],
  code: NodeProjectionDiagnosticCode,
): Readonly<Record<string, unknown>> {
  const value = requireRecord(input, subject);
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  if (!equalStrings(actual, expected)) {
    projectionFail(
      code,
      subject,
      `expected keys ${expected.join(",")}; received ${actual.join(",")}`,
    );
  }
  return value;
}

function requireRecord(
  input: unknown,
  subject: string,
): Readonly<Record<string, unknown>> {
  if (
    typeof input !== "object" ||
    input === null ||
    Array.isArray(input)
  ) {
    projectionFail(
      "SFOL_SOURCE_NONCANONICAL",
      subject,
      "expected an object",
    );
  }
  return input as Readonly<Record<string, unknown>>;
}

function arrayValue(
  input: unknown,
  subject: string,
  code: NodeProjectionDiagnosticCode,
): readonly unknown[] {
  if (!Array.isArray(input)) {
    projectionFail(code, subject, "expected an array");
  }
  return input;
}

function stringArray(
  input: unknown,
  subject: string,
  code: NodeProjectionDiagnosticCode,
): readonly string[] {
  return arrayValue(input, subject, code).map((item, index) =>
    requiredString(item, `${subject}[${index}]`, code),
  );
}

function requiredString(
  input: unknown,
  subject: string,
  code: NodeProjectionDiagnosticCode,
): string {
  if (typeof input !== "string" || input.length === 0) {
    projectionFail(code, subject, "expected a non-empty string");
  }
  return input;
}

function requiredDigest(
  input: unknown,
  subject: string,
  code: NodeProjectionDiagnosticCode,
): string {
  const value = requiredString(input, subject, code);
  if (!SHA256.test(value)) {
    projectionFail(code, subject, "expected a lowercase SHA-256 digest");
  }
  return value;
}

function requiredPath(input: unknown, subject: string): string {
  const value = requiredString(
    input,
    subject,
    "SFOL_SOURCE_MANIFEST_INVALID",
  );
  if (
    value.startsWith("/") ||
    /^[A-Za-z]:[\\/]/.test(value) ||
    value.split(/[\\/]/).includes("..")
  ) {
    projectionFail(
      "SFOL_SOURCE_MANIFEST_INVALID",
      subject,
      "source path must be project-relative and contained",
    );
  }
  return value;
}

function assertUnique(
  values: readonly string[],
  subject: string,
  code: NodeProjectionDiagnosticCode,
): void {
  if (new Set(values).size !== values.length) {
    projectionFail(code, subject, "identities must be unique");
  }
}

function equalStrings(
  left: readonly string[],
  right: readonly string[],
): boolean {
  return (
    left.length === right.length &&
    left.every((value, index) => value === right[index])
  );
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function deepFreeze<T>(value: T): T {
  if (typeof value !== "object" || value === null || Object.isFrozen(value)) {
    return value;
  }
  Object.freeze(value);
  for (const item of Object.values(value)) {
    deepFreeze(item);
  }
  return value;
}

function projectionFail(
  code: NodeProjectionDiagnosticCode,
  subject: string,
  detail: string,
  decodeDiagnostics?: readonly SfolDecodeDiagnostic[],
): never {
  throw new ProjectionAbort(
    decodeDiagnostics === undefined
      ? { code, stage: "node-source", subject, detail }
      : {
          code,
          stage: "node-source",
          subject,
          detail,
          decode_diagnostics: Object.freeze([...decodeDiagnostics]),
        },
  );
}
