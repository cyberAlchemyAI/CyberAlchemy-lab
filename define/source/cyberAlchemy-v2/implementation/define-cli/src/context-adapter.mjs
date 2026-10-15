import {readFileSync} from "node:fs";
import {join, resolve} from "node:path";

import {composeContextLifecycle} from "../../agent-reasoning-engine/packages/context-basis-runtime/index.mjs";
import {loadVerifiedDecisionProfile} from "../../agent-reasoning-engine/packages/request-decision-router/index.mjs";
import {canonicalize, digest} from "./canonical.mjs";

const DEFINITION_IDS = [
  "CAV2-DEFINE-CAND-001",
  "CAV2-DEFINE-PACK-CAND-001",
  "CAV2-DEFINE-SESSION-CAND-001",
];

const INITIAL_NODE_ID = "define-session-runtime.CliInterface";
const EDGE_IDS = [
  "define-session-runtime.edge.cli-exposes-create",
  "define-session-runtime.edge.cli-exposes-defer",
  "define-session-runtime.edge.cli-exposes-export",
  "define-session-runtime.edge.cli-exposes-open",
  "define-session-runtime.edge.cli-exposes-record",
  "define-session-runtime.edge.cli-exposes-validate",
  "define-session-runtime.edge.export-creates-pack",
  "define-session-runtime.edge.export-reads-session",
  "define-session-runtime.edge.validate-reads-pack",
  "define-session-runtime.edge.validate-reads-session",
];

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function definitionText(proposal) {
  return [
    `Term: ${proposal.term}`,
    `Normative: ${proposal.normative_voice}`,
    `Formal: ${proposal.formal_voice}`,
    `Plain language: ${proposal.plain_language_voice}`,
    `Domain context: ${proposal.domain_context_voice}`,
    `Boundary: ${proposal.boundary}`,
  ].join("\n");
}

function buildDefinitionCatalog(definitionsPath) {
  const source = readJson(definitionsPath);
  const byId = new Map(source.proposals.map((proposal) => [proposal.candidate_id, proposal]));
  const relationTargets = {
    "CAV2-DEFINE-CAND-001": ["CAV2-DEFINE-PACK-CAND-001", "CAV2-DEFINE-SESSION-CAND-001"],
    "CAV2-DEFINE-PACK-CAND-001": ["CAV2-DEFINE-SESSION-CAND-001"],
    "CAV2-DEFINE-SESSION-CAND-001": [],
  };
  const definitions = DEFINITION_IDS.map((definitionId) => {
    const proposal = byId.get(definitionId);
    if (!proposal) throw new Error(`define-context.missing-definition:${definitionId}`);
    const text = definitionText(proposal);
    return {
      definition_id: definitionId,
      version_or_revision: source.schema_version,
      digest: digest(canonicalize(proposal)),
      authority_posture: "candidate-not-canonical",
      source_ref: `cyberAlchemy-v2/define/definitions.json#${definitionId}`,
      aliases: proposal.aliases ?? [],
      definition_text: text,
      relations: relationTargets[definitionId].map((target) => ({
        relation_class: "requires",
        target_definition_id: target,
        required: true,
      })),
    };
  });
  return {
    catalog: {
      catalog_id: "cav2.define.cli.selected-definitions/v1",
      source_identity: "cyberAlchemy-v2/define/definitions.json",
      source_digest: digest(readFileSync(definitionsPath)),
      normative_relation_classes: ["requires"],
      definitions,
    },
    seed_definition_ids: ["CAV2-DEFINE-CAND-001"],
    universal_relation_classes: ["requires"],
    route_relation_classes_by_route: {"CA2-ROUTE-DEFINE": []},
  };
}

function buildOntologySnapshot(nodesPath, relationsPath) {
  const nodeSource = readJson(nodesPath);
  const relationSource = readJson(relationsPath);
  const relationById = new Map(relationSource.relations.map((edge) => [edge.relation_id, edge]));
  const selectedEdges = EDGE_IDS.map((edgeId) => {
    const edge = relationById.get(edgeId);
    if (!edge) throw new Error(`define-context.missing-ontology-edge:${edgeId}`);
    return edge;
  });
  const selectedNodeIds = new Set([INITIAL_NODE_ID]);
  for (const edge of selectedEdges) {
    selectedNodeIds.add(edge.from_node_id);
    selectedNodeIds.add(edge.to_node_id);
  }
  const nodeById = new Map(nodeSource.nodes.map((node) => [node.node_id, node]));
  const nodes = [...selectedNodeIds].sort().map((nodeId) => {
    const node = nodeById.get(nodeId);
    if (!node) throw new Error(`define-context.missing-ontology-node:${nodeId}`);
    return {
      node_id: nodeId,
      node_type: node.kind,
      source_digest: digest(canonicalize(node)),
      source_ref: `cyberAlchemy-v2/define/system-ontology/${node.source_path}`,
      content: {intent: node.intent, implementation_status: node.implementation_status, status: node.status},
      required_edge_ids: nodeId === INITIAL_NODE_ID ? EDGE_IDS : [],
    };
  });
  const edges = selectedEdges.map((edge) => ({
    edge_id: edge.relation_id,
    edge_type: edge.type,
    from_node_id: edge.from_node_id,
    to_node_id: edge.to_node_id,
    source_digest: digest(canonicalize(edge)),
    source_ref: `cyberAlchemy-v2/define/system-ontology/${edge.source_node_path}`,
    content: {status: edge.status, authority_effect: edge.authority_effect},
  }));
  const selected = canonicalize({nodes, edges});
  return {
    snapshot: {
      ontology_id: "cav2.define.system-ontology",
      source_identity: "cyberAlchemy-v2/define/system-ontology",
      snapshot_digest: digest(selected),
      nodes,
      edges,
    },
    initial_node_ids: [INITIAL_NODE_ID],
    required_edge_ids: [],
    omission_candidate_ids: [],
  };
}

export function composeDefineContext(input, repositoryRoot) {
  const root = resolve(repositoryRoot);
  const definitionsPath = join(root, "cyberAlchemy-v2/define/definitions.json");
  const nodesPath = join(root, "cyberAlchemy-v2/define/system-ontology/NODES.json");
  const relationsPath = join(root, "cyberAlchemy-v2/define/system-ontology/RELATIONS.json");
  const profilePath = join(root, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/request-decision-router/profiles/cyberalchemy-v1.json");
  const profile = loadVerifiedDecisionProfile(profilePath, root);
  if (!profile.ok) return {ok: false, stage: "decision-profile", reason_codes: profile.reason_codes, authority_effect: "none"};

  let definition;
  let ontology;
  try {
    definition = buildDefinitionCatalog(definitionsPath);
    ontology = buildOntologySnapshot(nodesPath, relationsPath);
  } catch (error) {
    return {ok: false, stage: "source-adapter", reason_codes: [error.message], authority_effect: "none"};
  }
  const sourceSnapshot = [
    {source_identity: definition.catalog.source_identity, source_digest: definition.catalog.source_digest},
    {source_identity: ontology.snapshot.source_identity, source_digest: ontology.snapshot.snapshot_digest},
  ];
  const requestMaterial = canonicalize({
    goal: input.goal,
    intent: input.intent,
    context: input.context,
    consumer: input.consumer,
  });
  const requestDigest = digest(requestMaterial);
  const sourceEpoch = digest(sourceSnapshot);
  const lifecycle = composeContextLifecycle({
    request_context: {
      schema_version: "are.request-context/v1",
      request_id: `define-request:${requestDigest}`,
      raw_request: "Define shared meaning for the supplied bounded request.",
      objective_kind: "define",
      requested_effects: [],
      target_refs: ["CA2-CAP-DEFINE-SHARED-MEANING"],
      constraints: ["non-effectful", "preserve-open-meaning"],
      evidence_refs: ["define-cli-user-input"],
      field_postures: {
        request_id: "inferred",
        raw_request: "explicit",
        objective_kind: "explicit",
        requested_effects: "explicit",
        target_refs: "inferred",
        constraints: "inferred",
        evidence_refs: "inferred"
      }
    },
    decision_profile: profile.value,
    definition,
    ontology,
    authority_posture: "candidate-context-only",
    effect_posture: "non-effectful",
    constraints: ["definition-pack-remains-candidate"],
    gaps: [],
    residue: [{kind: "known-gap", ref: "CAP-OBL-DEFINE-011-CLI-CHAT-CONTINUITY", posture: "out-of-scope-l0"}],
    view: {
      lane: "interaction-bound",
      consumer_ref: input.consumer,
      purpose: "define-shared-meaning",
      source_epoch: sourceEpoch,
      interaction_id: `define-session:${requestDigest}`,
      turn_id: "run:1",
    },
    current_sources: sourceSnapshot,
    projection_policy: {
      max_inline_bytes: 32 * 1024,
      claim_ceiling: "Candidate Define context only; no definition promotion, solution selection, implementation, or effect authority.",
    },
  });
  if (!lifecycle.ok) return lifecycle;
  return {
    ok: true,
    request_digest: requestDigest,
    source_epoch: sourceEpoch,
    route_decision: lifecycle.value.composition.value.route_decision,
    context_envelope: lifecycle.value.context_envelope.value,
    context_envelope_digest: lifecycle.value.context_envelope.digest,
    refresh_assessment: lifecycle.value.refresh_assessment.value,
    authority_effect: "none",
  };
}
