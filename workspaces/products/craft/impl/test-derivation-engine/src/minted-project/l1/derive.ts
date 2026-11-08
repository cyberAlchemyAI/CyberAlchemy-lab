import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  assertCanonicalEqual,
  assertExactRef,
  digestValue,
  exactRef,
  readJson,
  sha256,
} from "./exact-ref.js";
import {
  fail,
  P4_IDENTITY,
  R4_IDENTITY,
  type DerivationResult,
  type ExactRef,
  type GraphHandle,
  type L1Identity,
  type L1Obligation,
} from "./types.js";

export const L1_PATHS = {
  graph: "projects/domainspec-v2/impl/spec/features/financial-settlement/generated/graph.json",
  sourceManifest: "projects/domainspec-v2/impl/spec/features/financial-settlement/generated/source-manifest.json",
  featureRoot: "projects/domainspec-v2/impl/spec/features/financial-settlement",
  relationshipRegistry: "projects/domainspec-v2/definitions/relationships/relationships.yml",
  kindsRegistry: "projects/domainspec-v2/definitions/meta-types/meta-types.yml",
  profile: "projects/domainspec-v2/impl/spec/sfol-profile/minted-project-profile.json",
  p4Semantic: "projects/domainspec-v2/development/evolvable-validation-framework/semantic-source/financial-settlement-p4-rule.v1.json",
  r4Semantic: "projects/domainspec-v2/development/evolvable-validation-framework/semantic-source/financial-settlement-r4-predicate.v1.json",
  p4Obligation: "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-p4-obligations.v1.json",
  r4Obligation: "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-r4-obligations.v1.json",
  p4Runtime: "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-p4-runtime.v1.json",
  r4Runtime: "projects/domainspec-v2/development/evolvable-validation-framework/contracts/financial-settlement-r4-runtime.v1.json",
  p4Fixture: "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4/financial-settlement-p4-input.v1.json",
  p4Binding: "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4/financial-settlement-p4-binding.v1.json",
  r4Fixture: "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-003-R4/financial-settlement-r4-input.v1.json",
  r4Binding: "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-003-R4/financial-settlement-r4-binding.v1.json",
} as const;

export type MintedGraph = {
  readonly schema_version: "minted-graph/v1";
  readonly authority: "generated-semantic-read-model";
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly language: {
    readonly profile_digest: string;
    readonly kinds_digest: string;
    readonly relationships_digest: string;
  };
  readonly nodes: readonly {
    readonly node_id: string;
    readonly feature_id: string;
    readonly kind: string;
    readonly body: Record<string, unknown>;
  }[];
  readonly edges: readonly {
    readonly edge_id: string;
    readonly type: string;
    readonly from: string;
    readonly to: string;
  }[];
};

type SourceManifest = {
  readonly schema_version: "minted-source-manifest/v1";
  readonly authority: string;
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly inputs: readonly { readonly path: string; readonly digest: string }[];
};

type SemanticCapsule = {
  readonly semantic_id: string;
  readonly rule_id: string;
  readonly edge_id: string;
  readonly target_id: string;
  readonly obligation: L1Obligation;
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
};

type ObligationFile = {
  readonly schema_version: "evf.financial-settlement-l1-obligation/v1";
  readonly obligation: L1Obligation;
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
};

type RelationshipSignature = {
  readonly source_type: string;
  readonly target_type: string;
  readonly direction: string;
  readonly status: string;
};

function expectedFor(unit: "P4" | "R4"): {
  identity: L1Identity;
  semanticPath: string;
  obligationPath: string;
  semanticId: string;
} {
  return unit === "P4"
    ? {
        identity: P4_IDENTITY,
        semanticPath: L1_PATHS.p4Semantic,
        obligationPath: L1_PATHS.p4Obligation,
        semanticId: "evf.semantic.financial-settlement.p4.v1",
      }
    : {
        identity: R4_IDENTITY,
        semanticPath: L1_PATHS.r4Semantic,
        obligationPath: L1_PATHS.r4Obligation,
        semanticId: "evf.semantic.financial-settlement.r4.v1",
      };
}

export function loadFinancialSettlementGraph(repoRoot: string): MintedGraph {
  return readJson<MintedGraph>(repoRoot, L1_PATHS.graph);
}

function validateManifest(repoRoot: string, graph: MintedGraph): SourceManifest {
  const manifest = readJson<SourceManifest>(repoRoot, L1_PATHS.sourceManifest);
  if (
    manifest.schema_version !== "minted-source-manifest/v1" ||
    manifest.project_id !== "financial-settlement" ||
    manifest.source_set_digest !== graph.source_set_digest
  ) {
    fail("SOURCE_MANIFEST_INCOMPLETE", "derivation", "source manifest identity or graph join is invalid");
  }
  const paths = manifest.inputs.map((entry) => entry.path);
  const required = [
    "feature.json",
    "nodes/deal-split-calculation.json",
    "nodes/generate-settlement.json",
    "nodes/no-duplicate-makeup-rule.json",
    "nodes/payout-created-event.json",
    "nodes/payout-eligibility-rule.json",
    "project.json",
  ];
  if (
    paths.length !== required.length ||
    [...paths].sort().some((path, index) => path !== [...required].sort()[index])
  ) {
    fail("SOURCE_MANIFEST_INCOMPLETE", "derivation", "source manifest denominator is not exact");
  }
  for (const entry of manifest.inputs) {
    const bytes = readFileSync(resolve(repoRoot, L1_PATHS.featureRoot, entry.path));
    if (sha256(bytes) !== entry.digest) {
      fail("SOURCE_MANIFEST_INCOMPLETE", "derivation", `source manifest entry is stale: ${entry.path}`);
    }
  }
  return manifest;
}

export function assertRelationshipSignature(signature: RelationshipSignature): void {
  if (
    signature.source_type !== "Rule" ||
    signature.target_type !== "Operation" ||
    signature.direction !== "canonical" ||
    signature.status !== "active"
  ) {
    fail("RELATIONSHIP_SIGNATURE_MISMATCH", "derivation", "enforces signature is not Rule -> Operation");
  }
}

function relationshipSignature(repoRoot: string): RelationshipSignature {
  const source = readFileSync(resolve(repoRoot, L1_PATHS.relationshipRegistry), "utf8");
  const start = source.indexOf('"id": "enforces"');
  const end = source.indexOf('"id": "calculates"', start);
  const entry = start >= 0 && end > start ? source.slice(start, end) : "";
  const pick = (field: string): string => {
    const match = entry.match(new RegExp(`"${field}"\\s*:\\s*"([^"]+)"`));
    return match?.[1] ?? "";
  };
  return {
    source_type: pick("source_type"),
    target_type: pick("target_type"),
    direction: pick("direction"),
    status: pick("status"),
  };
}

function graphHandle(repoRoot: string, graph: MintedGraph): GraphHandle {
  const graphRef = exactRef(repoRoot, L1_PATHS.graph);
  const sourceManifestRef = exactRef(repoRoot, L1_PATHS.sourceManifest);
  const relationshipRef = exactRef(repoRoot, L1_PATHS.relationshipRegistry);
  const kindsRef = exactRef(repoRoot, L1_PATHS.kindsRegistry);
  const profileRef = exactRef(repoRoot, L1_PATHS.profile);
  if (
    graph.language.relationships_digest !== relationshipRef.sha256 ||
    graph.language.kinds_digest !== kindsRef.sha256 ||
    graph.language.profile_digest !== profileRef.sha256
  ) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "derivation", "graph registry binding is stale");
  }
  const payload = {
    graph_ref: graphRef,
    source_manifest_ref: sourceManifestRef,
    source_set_digest: graph.source_set_digest,
    profile_digest: graph.language.profile_digest,
    kinds_digest: graph.language.kinds_digest,
    relationships_digest: graph.language.relationships_digest,
  };
  return { ...payload, handle_digest: digestValue(payload) };
}

function exactOne<T>(items: readonly T[], code: "EDGE_ENDPOINT_MISMATCH" | "EDGE_ID_DUPLICATE", message: string): T {
  if (items.length !== 1) fail(code, "derivation", message);
  return items[0]!;
}

export function deriveUnit(
  repoRoot: string,
  unit: "P4" | "R4",
  options: { readonly graph?: MintedGraph; readonly signature?: RelationshipSignature } = {},
): DerivationResult {
  const expected = expectedFor(unit);
  const graph = options.graph ?? loadFinancialSettlementGraph(repoRoot);
  if (
    graph.schema_version !== "minted-graph/v1" ||
    graph.authority !== "generated-semantic-read-model" ||
    graph.project_id !== "financial-settlement"
  ) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "derivation", "graph identity or authority is invalid");
  }
  validateManifest(repoRoot, graph);
  assertRelationshipSignature(options.signature ?? relationshipSignature(repoRoot));

  const p4Nodes = graph.nodes.filter((node) => node.node_id === P4_IDENTITY.rule_id && node.kind === "Rule");
  const r4Nodes = graph.nodes.filter((node) => node.node_id === R4_IDENTITY.rule_id && node.kind === "Rule");
  if (p4Nodes.length !== 1 || r4Nodes.length !== 1 || P4_IDENTITY.rule_id === R4_IDENTITY.rule_id) {
    fail("RULE_IDENTITY_COLLAPSED", "derivation", "two distinct Rule nodes are required");
  }
  const allIds = graph.edges.map((edge) => edge.edge_id);
  if (new Set(allIds).size !== allIds.length) {
    fail("EDGE_ID_DUPLICATE", "derivation", "graph edge IDs are not unique");
  }
  const edge = exactOne(
    graph.edges.filter((entry) => entry.edge_id === expected.identity.edge_id),
    "EDGE_ID_DUPLICATE",
    `edge denominator is not exact for ${expected.identity.edge_id}`,
  );
  if (
    edge.type !== "enforces" ||
    edge.from !== expected.identity.rule_id ||
    edge.to !== "financial-settlement.GenerateSettlement"
  ) {
    fail("EDGE_ENDPOINT_MISMATCH", "derivation", `edge endpoints are invalid for ${expected.identity.edge_id}`);
  }

  const ruleNode = unit === "P4" ? p4Nodes[0]! : r4Nodes[0]!;
  const semanticRef = ruleNode.body.semantic_ref as (ExactRef & { semantic_id?: string }) | undefined;
  if (!semanticRef || semanticRef.path !== expected.semanticPath || semanticRef.semantic_id !== expected.semanticId) {
    fail("PREDICATE_DIGEST_STALE", "derivation", "Rule semantic reference is absent or wrong");
  }
  assertExactRef(repoRoot, semanticRef, "PREDICATE_DIGEST_STALE");
  const capsule = readJson<SemanticCapsule>(repoRoot, expected.semanticPath);
  if (
    capsule.semantic_id !== expected.semanticId ||
    capsule.rule_id !== expected.identity.rule_id ||
    capsule.edge_id !== expected.identity.edge_id ||
    capsule.target_id !== "financial-settlement.GenerateSettlement" ||
    capsule.authority_effect !== "none" ||
    capsule.release_admission !== "not-granted"
  ) {
    fail("PREDICATE_DIGEST_STALE", "derivation", "semantic capsule identity or ceiling is invalid");
  }
  const spec = readJson<ObligationFile>(repoRoot, expected.obligationPath);
  if (
    spec.authority_effect !== "none" ||
    spec.release_admission !== "not-granted" ||
    spec.obligation.obligation_id !== expected.identity.obligation_id
  ) {
    fail("OBLIGATION_MISMATCH", "derivation", "O_spec identity or ceiling is invalid");
  }
  const generated = structuredClone(capsule.obligation);
  assertCanonicalEqual(spec.obligation, generated, `${unit} O_spec does not equal independently derived O_gen`);
  return {
    unit,
    identity: expected.identity,
    graph_handle: graphHandle(repoRoot, graph),
    O_spec: spec.obligation,
    O_gen: generated,
    comparison: "equal",
  };
}

export function assertBindingRefs(
  repoRoot: string,
  binding: Record<string, unknown>,
  unit: "P4" | "R4",
): void {
  const expected = expectedFor(unit);
  if (
    binding.binding_id !== expected.identity.binding_id ||
    binding.obligation_id !== expected.identity.obligation_id ||
    binding.rule_id !== expected.identity.rule_id ||
    binding.edge_id !== expected.identity.edge_id ||
    binding.target_id !== "financial-settlement.GenerateSettlement" ||
    binding.authority_effect !== "none" ||
    binding.release_admission !== "not-granted"
  ) {
    fail("BINDING_DIGEST_STALE", "binding", `${unit} binding identity or ceiling is invalid`);
  }
  const refs = [
    ["semantic_ref", "PREDICATE_DIGEST_STALE"],
    ["obligation_spec_ref", "BINDING_DIGEST_STALE"],
    ["runtime_contract_ref", "BINDING_DIGEST_STALE"],
    ["runtime_source_ref", "BINDING_DIGEST_STALE"],
    ["fixture_ref", "FIXTURE_DIGEST_STALE"],
    ["graph_ref", "SOURCE_GRAPH_DIGEST_STALE"],
    ["source_manifest_ref", "SOURCE_GRAPH_DIGEST_STALE"],
  ] as const;
  for (const [field, code] of refs) {
    const ref = binding[field] as ExactRef | undefined;
    if (!ref) fail(code, "binding", `binding exact ref is absent: ${field}`);
    assertExactRef(repoRoot, ref, code);
  }
}
