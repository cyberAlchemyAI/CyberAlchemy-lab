import type {
  BackendKind,
  BackendRelationship,
  DevelopmentProject,
} from "./development-engine.js";
import { canonicalize } from "./contract-publication.js";
import { sha256 } from "./validation/validate-semantics.js";
import type {
  CatalogueId,
  DevelopmentCatalogue,
  DevelopmentObligation,
} from "./proof-engine.js";

export const SELF_AUTHORED_EXPECTATION_ORACLE =
  "bte.validation-owner.self-authored/v1" as const;

// This table is deliberately owned by the validation side. It must not be
// imported from the build-derived catalogue path, otherwise the proof would
// compare one implementation with itself.
const EXPECTED_FORMATION_CRITERIA: Readonly<
  Record<BackendKind, readonly string[]>
> = {
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

function expectedCoverageKey(
  catalogueId: CatalogueId,
  obligationId: string,
): string {
  return `${catalogueId}::${obligationId}`;
}

function expectedCatalogue(
  catalogueId: CatalogueId,
  members: DevelopmentObligation[],
): DevelopmentCatalogue {
  const sorted = [...members].sort((left, right) =>
    left.coverage_key.localeCompare(right.coverage_key),
  );
  return {
    schema_version: "bte-development-catalogue/v1",
    catalogue_id: catalogueId,
    oracle_id: SELF_AUTHORED_EXPECTATION_ORACLE,
    members: sorted,
    membership_digest: sha256(
      canonicalize(sorted.map(({ coverage_key }) => coverage_key)),
    ),
    authority: "development-fixture",
  };
}

function expectedFormationCriterionMembers(
  kinds: readonly BackendKind[],
): DevelopmentObligation[] {
  return kinds.flatMap((kind) =>
    EXPECTED_FORMATION_CRITERIA[kind].map((criterion) => {
      const obligationId = `${kind.toLowerCase().replaceAll(" ", "-")}/${criterion}`;
      return {
        catalogue_id: "formation-criterion@1" as const,
        obligation_id: obligationId,
        coverage_key: expectedCoverageKey(
          "formation-criterion@1",
          obligationId,
        ),
        subject_type: "kind" as const,
        subject_id: kind,
        expected_kind: kind,
        evaluator: "formation" as const,
      };
    }),
  );
}

function expectedKindMembers(
  catalogueId: "formation-structure@1" | "node-kind-causality@1",
  kinds: readonly BackendKind[],
): DevelopmentObligation[] {
  return kinds.map((kind) => {
    const obligationId = kind.toLowerCase().replaceAll(" ", "-");
    return {
      catalogue_id: catalogueId,
      obligation_id: obligationId,
      coverage_key: expectedCoverageKey(catalogueId, obligationId),
      subject_type: "kind",
      subject_id: kind,
      expected_kind: kind,
      evaluator:
        catalogueId === "formation-structure@1"
          ? "formation"
          : "node-causality",
    };
  });
}

function expectedNodeMembers(
  nodes: DevelopmentProject["nodes"],
): DevelopmentObligation[] {
  return nodes.map((node) => ({
    catalogue_id: "node-instance-conformance@1",
    obligation_id: node.node_id,
    coverage_key: expectedCoverageKey(
      "node-instance-conformance@1",
      node.node_id,
    ),
    subject_type: "node",
    subject_id: node.node_id,
    expected_kind: node.kind,
    evaluator: "graph-conformance",
  }));
}

function expectedRelationshipMembers(
  relationships: readonly BackendRelationship[],
): DevelopmentObligation[] {
  return relationships.map((relationship) => ({
    catalogue_id: "relationship-family-causality@1",
    obligation_id: relationship,
    coverage_key: expectedCoverageKey(
      "relationship-family-causality@1",
      relationship,
    ),
    subject_type: "relationship",
    subject_id: relationship,
    expected_relationship: relationship,
    evaluator: "relationship-causality",
  }));
}

function expectedEdgeMembers(
  edges: DevelopmentProject["edges"],
): DevelopmentObligation[] {
  return edges.map((edge) => ({
    catalogue_id: "edge-instance-conformance@1",
    obligation_id: edge.edge_id,
    coverage_key: expectedCoverageKey(
      "edge-instance-conformance@1",
      edge.edge_id,
    ),
    subject_type: "edge",
    subject_id: edge.edge_id,
    expected_relationship: edge.family,
    evaluator: "graph-conformance",
  }));
}

export function createSelfAuthoredDevelopmentCatalogues(
  project: DevelopmentProject,
): DevelopmentCatalogue[] {
  const kinds = [...new Set(project.nodes.map(({ kind }) => kind))].sort();
  const relationships = [
    ...new Set(project.edges.map(({ family }) => family)),
  ].sort();
  return [
    expectedCatalogue(
      "formation-criterion@1",
      expectedFormationCriterionMembers(kinds),
    ),
    expectedCatalogue(
      "formation-structure@1",
      expectedKindMembers("formation-structure@1", kinds),
    ),
    expectedCatalogue(
      "node-kind-causality@1",
      expectedKindMembers("node-kind-causality@1", kinds),
    ),
    expectedCatalogue(
      "node-instance-conformance@1",
      expectedNodeMembers(project.nodes),
    ),
    expectedCatalogue(
      "relationship-family-causality@1",
      expectedRelationshipMembers(relationships),
    ),
    expectedCatalogue(
      "edge-instance-conformance@1",
      expectedEdgeMembers(project.edges),
    ),
  ];
}
