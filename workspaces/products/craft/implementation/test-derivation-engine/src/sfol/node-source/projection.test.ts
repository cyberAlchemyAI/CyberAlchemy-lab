import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

import type {
  LogicClause,
  NodeLogicModuleV1,
} from "../language/ast.js";
import {
  NODE_LOGIC_ENVELOPE_VERSION,
  NODE_PROJECTION_ADMISSION_VERSION,
  NODE_PROOF_CONTEXT_VERSION,
  projectNodeLogic,
  type CanonicalNodeProofContextInput,
  type NodeProjectionAdmission,
} from "./index.js";

const A = "a".repeat(64);
const B = "b".repeat(64);
const C = "c".repeat(64);
const D = "d".repeat(64);
const E = "e".repeat(64);
const F = "f".repeat(64);

interface FixtureNode {
  node_id: string;
  feature_id: string;
  kind: string;
  intent: string;
  body: Record<string, unknown>;
}

interface FixtureGraph {
  schema_version: "minted-graph/v1";
  authority: "generated-semantic-read-model";
  project_id: string;
  language: {
    profile_digest: string;
    kinds_digest: string;
    relationships_digest: string;
  };
  source_set_digest: string;
  nodes: FixtureNode[];
  edges: Array<{
    edge_id: string;
    type: string;
    from: string;
    to: string;
  }>;
}

interface FixtureManifest {
  schema_version: "minted-source-manifest/v1";
  authority: "generated-provenance-read-model";
  project_id: string;
  source_set_digest: string;
  inputs: Array<{ path: string; digest: string }>;
  records: Array<{
    record_type: "node" | "edge";
    graph_id: string;
    source_path: string;
    source_digest: string;
  }>;
}

interface FixtureBuildReceipt {
  schema_version: "minted-build-receipt/v1";
  authority: "generated-verification-evidence";
  status: "pass";
  project_id: string;
  language: {
    profile_id: string;
    profile_version: string;
    profile_digest: string;
    kinds_digest: string;
    relationships_digest: string;
  };
  source_set_digest: string;
  artifacts: {
    graph_digest: string;
    source_manifest_digest: string;
    markdown_view_digest: string;
    markdown_content_digest: string;
  };
  generator_version: string;
}

function span(sourceId: string, path: string) {
  return {
    source_id: sourceId,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 8 },
  };
}

function logicFixture(
  nodeId: string,
  sourcePath: string,
  clauseId: string,
): NodeLogicModuleV1 {
  const clause: LogicClause = {
    clause_id: clauseId,
    kind: "invariant",
    status: "admitted",
    inputs: [],
    result_sort: { tag: "primitive", name: "boolean" },
    expression: {
      tag: "literal",
      value: { tag: "boolean", value: true },
      span: span(nodeId, "body.logic.clauses[0].expression"),
    },
    observation_sort: null,
    span: span(nodeId, "body.logic.clauses[0]"),
  };
  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: `${nodeId}-logic`,
    source: {
      feature_id: "framework",
      node_id: nodeId,
      source_id: nodeId,
      source_path: sourcePath,
    },
    declarations: [],
    clauses: [clause],
  };
}

function graphFixture(): FixtureGraph {
  return {
    schema_version: "minted-graph/v1",
    authority: "generated-semantic-read-model",
    project_id: "framework-proof",
    language: {
      profile_digest: A,
      kinds_digest: B,
      relationships_digest: C,
    },
    source_set_digest: D,
    nodes: [
      {
        node_id: "framework.RuleA",
        feature_id: "framework",
        kind: "Rule",
        intent: "Own the first framework rule.",
        body: {
          logic: logicFixture(
            "framework.RuleA",
            "specs/framework/nodes/rule-a.json",
            "framework.rule-a-holds",
          ),
        },
      },
      {
        node_id: "framework.RuleB",
        feature_id: "framework",
        kind: "Rule",
        intent: "Own the second framework rule.",
        body: {
          logic: logicFixture(
            "framework.RuleB",
            "specs/framework/nodes/rule-b.json",
            "framework.rule-b-holds",
          ),
        },
      },
    ],
    edges: [
      {
        edge_id: "framework.edge.rule-a-specializes-rule-b",
        type: "specializes",
        from: "framework.RuleA",
        to: "framework.RuleB",
      },
    ],
  };
}

function manifestFixture(): FixtureManifest {
  return {
    schema_version: "minted-source-manifest/v1",
    authority: "generated-provenance-read-model",
    project_id: "framework-proof",
    source_set_digest: D,
    inputs: [
      { path: "project.json", digest: A },
      { path: "specs/framework/feature.json", digest: B },
      { path: "specs/framework/nodes/rule-a.json", digest: E },
      { path: "specs/framework/nodes/rule-b.json", digest: F },
    ],
    records: [
      {
        record_type: "edge",
        graph_id: "framework.edge.rule-a-specializes-rule-b",
        source_path: "specs/framework/nodes/rule-a.json",
        source_digest: E,
      },
      {
        record_type: "node",
        graph_id: "framework.RuleA",
        source_path: "specs/framework/nodes/rule-a.json",
        source_digest: E,
      },
      {
        record_type: "node",
        graph_id: "framework.RuleB",
        source_path: "specs/framework/nodes/rule-b.json",
        source_digest: F,
      },
    ],
  };
}

function admissionFixture(): NodeProjectionAdmission {
  return {
    schema_version: NODE_PROJECTION_ADMISSION_VERSION,
    profile_id: "framework-node-logic",
    profile_version: "1",
    logic_schema_versions: ["domainspec-node-logic/v1"],
    admitted_node_ids: ["framework.RuleB", "framework.RuleA"],
  };
}

function materialize(
  graph = graphFixture(),
  manifest = manifestFixture(),
  admission = admissionFixture(),
) {
  const graphBytes = bytes(graph);
  const manifestBytes = bytes(manifest);
  const receipt: FixtureBuildReceipt = {
    schema_version: "minted-build-receipt/v1",
    authority: "generated-verification-evidence",
    status: "pass",
    project_id: graph.project_id,
    language: {
      profile_id: "framework-node-logic",
      profile_version: "1",
      profile_digest: graph.language.profile_digest,
      kinds_digest: graph.language.kinds_digest,
      relationships_digest: graph.language.relationships_digest,
    },
    source_set_digest: graph.source_set_digest,
    artifacts: {
      graph_digest: sha256(graphBytes),
      source_manifest_digest: sha256(manifestBytes),
      markdown_view_digest: A,
      markdown_content_digest: B,
    },
    generator_version: "minted-project-tools/v1",
  };
  const input: CanonicalNodeProofContextInput = {
    schema_version: NODE_PROOF_CONTEXT_VERSION,
    route: "canonical-minted-project-build",
    graph_bytes: graphBytes,
    source_manifest_bytes: manifestBytes,
    build_receipt_bytes: bytes(receipt),
  };
  return { graph, manifest, receipt, input, admission };
}

describe("DS-SFOL canonical node-logic projection", () => {
  it("projects one deterministic, bijective envelope set with every canonical handle", () => {
    const fixture = materialize();
    const left = projectNodeLogic(fixture.input, fixture.admission);
    const right = projectNodeLogic(fixture.input, fixture.admission);

    expect(left).toEqual(right);
    expect(left.ok && left.value.map((item) => item.node.node_id)).toEqual([
      "framework.RuleA",
      "framework.RuleB",
    ]);
    expect(left.ok && left.value[0]).toMatchObject({
      schema_version: NODE_LOGIC_ENVELOPE_VERSION,
      proof_context: {
        project_id: "framework-proof",
        profile_id: "framework-node-logic",
        profile_version: "1",
        profile_digest: A,
        kinds_digest: B,
        relationships_digest: C,
        source_set_digest: D,
        graph_digest: sha256(fixture.input.graph_bytes),
        manifest_digest: sha256(fixture.input.source_manifest_bytes),
        build_receipt_digest: sha256(fixture.input.build_receipt_bytes),
      },
      node: {
        node_id: "framework.RuleA",
        source_path: "specs/framework/nodes/rule-a.json",
        node_digest: E,
      },
    });
    expect(left.ok && Object.isFrozen(left.value[0]?.logic)).toBe(true);
  });

  it("rejects stale graph and source-manifest bytes", () => {
    const fixture = materialize();
    expect(
      projectNodeLogic(
        { ...fixture.input, graph_bytes: `${fixture.input.graph_bytes} ` },
        fixture.admission,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_STALE_GRAPH" }],
    });
    expect(
      projectNodeLogic(
        {
          ...fixture.input,
          source_manifest_bytes: `${fixture.input.source_manifest_bytes} `,
        },
        fixture.admission,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_STALE_MANIFEST" }],
    });
  });

  it("rejects incompatible project, source-set, or language handles", () => {
    const graph = graphFixture();
    graph.source_set_digest = C;
    expect(
      projectNodeLogic(
        materialize(graph).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_HANDLE_MISMATCH" }],
    });
  });

  it("rejects missing or extra graph/manifest/admission identities", () => {
    const missingRecord = manifestFixture();
    missingRecord.records.pop();
    expect(
      projectNodeLogic(
        materialize(graphFixture(), missingRecord).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_BIJECTION_MISMATCH" }],
    });

    const admission = admissionFixture();
    const oneNodeAdmission = {
      ...admission,
      admitted_node_ids: ["framework.RuleA"],
    };
    expect(
      projectNodeLogic(materialize().input, oneNodeAdmission),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_BIJECTION_MISMATCH" }],
    });
  });

  it("rejects duplicate graph and source-manifest identities", () => {
    const graph = graphFixture();
    graph.nodes.push(structuredClone(graph.nodes[0]!));
    expect(
      projectNodeLogic(
        materialize(graph).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_DUPLICATE_ID" }],
    });

    const manifest = manifestFixture();
    manifest.records.push(structuredClone(manifest.records[0]!));
    expect(
      projectNodeLogic(
        materialize(graphFixture(), manifest).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_DUPLICATE_ID" }],
    });
  });

  it("rejects unsupported or malformed node logic versions", () => {
    const graph = graphFixture();
    const logic = graph.nodes[0]!.body.logic as Record<string, unknown>;
    logic.schema_version = "domainspec-node-logic/v2";
    expect(
      projectNodeLogic(
        materialize(graph).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        {
          code: "SFOL_SOURCE_LOGIC_INVALID",
          decode_diagnostics: [
            { code: "SFOL_DECODE_UNKNOWN_SCHEMA_VERSION" },
          ],
        },
      ],
    });
  });

  it("rejects logic whose source ownership does not match the canonical node", () => {
    const graph = graphFixture();
    const logic = graph.nodes[0]!.body.logic as {
      source: { node_id: string };
    };
    logic.source.node_id = "framework.OtherRule";
    expect(
      projectNodeLogic(
        materialize(graph).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_OWNERSHIP_MISMATCH" }],
    });
  });

  it("rejects Markdown, direct-node input, and a second graph route", () => {
    const fixture = materialize();
    expect(
      projectNodeLogic("# Formal\ntrue", fixture.admission),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_NONCANONICAL" }],
    });
    expect(
      projectNodeLogic(
        { nodes: fixture.graph.nodes },
        fixture.admission,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_NONCANONICAL" }],
    });
    expect(
      projectNodeLogic(
        { ...fixture.input, second_graph: fixture.input.graph_bytes },
        fixture.admission,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_NONCANONICAL" }],
    });
  });

  it("keeps profile admission separate and rejects a nonmatching profile", () => {
    const fixture = materialize();
    expect(
      projectNodeLogic(fixture.input, {
        ...fixture.admission,
        profile_id: "minted-node",
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_PROFILE_NOT_ADMITTED" }],
    });
  });

  it("rejects a manifest record that does not match its source input digest", () => {
    const manifest = manifestFixture();
    manifest.records[1]!.source_digest = A;
    expect(
      projectNodeLogic(
        materialize(graphFixture(), manifest).input,
        admissionFixture(),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_SOURCE_HANDLE_MISMATCH" }],
    });
  });
});

function bytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}
