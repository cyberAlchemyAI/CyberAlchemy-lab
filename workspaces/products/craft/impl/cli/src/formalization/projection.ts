import fs from "node:fs";
import path from "node:path";

import type { CompiledProjectGraph, DecodedRelationship, FieldSpec, InterfaceOperationSpec, StateTransitionSpec } from "../input/project-model.js";
import { FROZEN_META_TYPE_CATALOG } from "../meta-types/catalog.js";
import { FROZEN_RELATIONSHIP_AUTHORITY_V1 } from "../relationships/frozen-authority.generated.js";
import type { FrozenRelationshipSignature } from "../relationships/types.js";
import type { TypedRecordContract } from "../typed-operation/contracts.js";
import { canonicalJson } from "../input/source-manifest.js";
import {
  FORMALIZATION_LEAN_MODULE_FILENAMES,
  createFormalizationLeanModuleSet,
  formalizationLeanModuleSet,
  formalizationLeanModuleSources,
  type FormalizationLeanModuleSet,
  type FormalizationLeanModuleSources,
} from "./kernel.js";
import { createCompilerRefinementOutput, sha256, type GraphBoundCertificate, type TypeScriptProjectionPayload } from "./refinement.js";

const UI_META_TYPES = ["Page", "Layout", "Component", "View Model", "Hook", "Form", "Action", "Guard", "Binding", "Adapter", "State Indicator"] as const;
const LEAN_META_TYPE: Readonly<Record<string, string>> = Object.freeze({
  "Entity": "entity", "Value Object": "valueObject", "Enum": "enumType", "Operation": "operation", "Query": "query",
  "Calculation": "calculation", "Rule": "rule", "Policy": "policy", "Workflow": "workflow", "Interface": "interfaceType",
  "Event": "event", "Mapping": "mapping", "State Machine": "stateMachine", "Page": "page", "Layout": "layout",
  "Component": "component", "View Model": "viewModel", "Hook": "hook", "Form": "form", "Action": "action",
  "Guard": "guard", "Binding": "binding", "Adapter": "adapter", "State Indicator": "stateIndicator",
});
const LEAN_RELATION: Readonly<Record<string, string>> = Object.freeze({
  "performs": "performs", "produces": "produces", "produces-for": "producesFor", "creates": "creates",
  "triggers-cross": "triggersCross", "enforces": "enforces", "calculates": "calculates", "transitions": "transitions",
  "exposes": "exposes", "orchestrates": "orchestrates", "applies": "applies", "maps": "maps", "contains": "contains",
  "reads": "reads", "emits": "emits", "owns": "owns", "belongs-to": "belongsTo", "renders": "renders", "wraps": "wraps",
  "composes": "composes", "consumes": "consumes", "submits": "submits", "shapes": "shapes", "protects": "protects",
  "displays": "displays", "fetches": "fetches", "mutates": "mutates", "reflects": "reflects", "derives": "derives",
  "contracts": "contracts", "mirrors": "mirrors",
});
const LEAN_SCOPE: Readonly<Record<string, string>> = Object.freeze({ "same-feature": "sameFeature", "cross-feature": "crossFeature", "ui": "ui", "ui-backend": "uiBackend" });
const LEAN_MULTIPLICITY: Readonly<Record<string, string>> = Object.freeze({ "one_to_one": "oneToOne", "one_to_many": "oneToMany", "one_to_many_ordered": "oneToManyOrdered", "many_to_one": "manyToOne", "many_to_many": "manyToMany" });

export type ObligationFamily = "endpoint" | "scope" | "multiplicity" | "generated-projection" | "inverse-collapse" | "deprecation";
type StateTransitionProjection = Readonly<{ transition_id: string; source_state: string; target_state: string; guard_ref: string; effect_event_ref: string }>;
type ProjectNodeProjection = Readonly<{
  selector: string; feature_id: string; node_id: string; meta_type: string;
  generated_creation_targets: readonly string[]; authored_forbidden_projection_attributes: readonly string[];
  typed_field_ids: readonly string[]; typed_field_type_refs: readonly string[];
  entity_identity_field: string; value_object_structural_equality: boolean; enum_values: readonly string[];
  event_type: string; event_version: string; event_occurrence_field: string; event_occurred_at_policy: string;
  interface_boundary_kind: string; interface_version: string; interface_compatibility: string; interface_operation_refs: readonly string[];
  state_machine_states: readonly string[]; state_machine_initial: string; state_machine_transitions: readonly StateTransitionProjection[];
}>;
type ProjectEdgeProjection = Readonly<{
  edge_id: string; relation: string; scope: string; source_selector: string; target_selector: string;
  source_type: string; target_type: string; authored_relationship_id: string; source_generated_creation_targets: readonly string[];
  source_authored_generated_projection: boolean; obligation_ids: readonly string[];
}>;

type BaselineProjection = Readonly<{ id: string; digest: string; manifest_sha256: string }>;
type RelationshipAuthorityProjection = Readonly<{ path: string; sha256: string; signature_count: 31 }>;
type ProjectGraphProjection = Readonly<{
  project_id: string;
  source_manifest_sha256: string;
  source_bytes_sha256: string;
  graph_sha256: string;
  nodes: readonly ProjectNodeProjection[];
  edges: readonly ProjectEdgeProjection[];
}>;
type MetaTypeProjection = Readonly<{ label: string; lean_constructor: string; partition: "backend" | "ui-supporting-context" }>;
type RelationshipProjection = Readonly<{
  id: string; lean_constructor: string; source_types: readonly string[]; target_types: readonly string[]; scopes: readonly string[];
  multiplicity: string; inverse_kind: "none" | "generated_view"; obligation_ids: readonly string[];
}>;
type ObligationProjection = Readonly<{ obligation_id: string; lean_constructor: string; family: ObligationFamily; relationship_ids: readonly string[] }>;
type WitnessProjection = Readonly<{ witness_id: string; lean_constructor: string; edge_id: string; obligation_id: string }>;
type LeanModuleSetProjection = Readonly<{
  schema_version: "domainspec.formalization-lean-module-set-projection/v1-candidate";
  sha256: string;
  modules: readonly Readonly<{ filename: string; sha256: string }>[];
}>;

export interface FormalizationRenderPayload {
  readonly schema_version: "domainspec.meta-type-formalization-render-payload/v1-candidate";
  readonly baseline: BaselineProjection;
  readonly relationship_authority: RelationshipAuthorityProjection;
  readonly lean_module_set: LeanModuleSetProjection;
  readonly project_graph: ProjectGraphProjection;
  readonly meta_types: readonly MetaTypeProjection[];
  readonly relationships: readonly RelationshipProjection[];
  readonly obligation_catalog: readonly ObligationProjection[];
  readonly applicable_witnesses: readonly WitnessProjection[];
  readonly graph_certificate: GraphBoundCertificate;
  readonly typescript_projection: TypeScriptProjectionPayload;
}

export interface MetaTypeFormalizationProjection {
  readonly schema_version: "domainspec.meta-type-formalization-projection/v2-candidate";
  readonly authority_effect: "none";
  readonly claim_ceiling: "compiled-project-graph-projection-only-no-runtime-conformance-or-authority";
  readonly render_payload_sha256: string;
  readonly render_payload: FormalizationRenderPayload;
  /** Compatibility views. Rendering is exclusively controlled by render_payload. */
  readonly baseline: BaselineProjection;
  readonly relationship_authority: RelationshipAuthorityProjection;
  readonly project_graph: ProjectGraphProjection;
  readonly meta_types: readonly MetaTypeProjection[];
  readonly relationships: readonly RelationshipProjection[];
  readonly obligation_catalog: readonly ObligationProjection[];
  readonly applicable_witnesses: readonly WitnessProjection[];
}

export class FormalizationProjectionError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, message: string) { super(message); this.name = "FormalizationProjectionError"; }
}
function fail(code: string, message: string): never { throw new FormalizationProjectionError(code, message); }
function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}
function leanList(values: readonly string[]): string { return `[${values.map((value) => `.${value}`).join(", ")}]`; }
function leanStringList(values: readonly string[]): string { return `[${values.map((value) => JSON.stringify(value)).join(", ")}]`; }
function leanStateTransitionList(values: readonly StateTransitionProjection[]): string {
  return `[${values.map((value) => `⟨${JSON.stringify(value.transition_id)}, ${JSON.stringify(value.source_state)}, ${JSON.stringify(value.target_state)}, ${JSON.stringify(value.guard_ref)}, ${JSON.stringify(value.effect_event_ref)}⟩`).join(", ")}]`;
}
function leanIdentifier(value: string): string {
  const parts = value.split(/[^a-zA-Z0-9]+/).filter(Boolean);
  if (parts.length === 0) fail("MTCLI_FORMALIZE_IDENTIFIER", `cannot form Lean identifier:${value}`);
  const identifier = parts[0]!.toLowerCase() + parts.slice(1).map((part) => `${part[0]!.toUpperCase()}${part.slice(1)}`).join("");
  return /^[a-z][a-zA-Z0-9]*$/.test(identifier) ? identifier : fail("MTCLI_FORMALIZE_IDENTIFIER", `invalid Lean identifier:${value}`);
}
function obligationFamily(id: string): ObligationFamily {
  if (/^reject_non_.+_(?:source|target)$/.test(id)) return "endpoint";
  if (["admit_same_and_cross_feature_scope", "reject_cross_feature_scope", "reject_enforces_cross_label", "require_admitted_workflow_scope"].includes(id)) return "scope";
  if (["reject_multiple_sources_per_target", "reject_multiple_targets_per_source"].includes(id)) return "multiplicity";
  if (["reject_authored_generated_projection", "derive_creation_targets_from_edge"].includes(id)) return "generated-projection";
  if (id === "reject_inverse_collapse_with_owns") return "inverse-collapse";
  if (id === "reject_deprecated_queries_alias") return "deprecation";
  return fail("MTCLI_FORMALIZE_OBLIGATION", `unclassified DS-D8 obligation:${id}`);
}
function edgeScope(edge: DecodedRelationship, signature: FrozenRelationshipSignature): string {
  if (edge.scope === "project") return "crossFeature";
  if (signature.feature_scope.includes("same-feature")) return "sameFeature";
  if (signature.feature_scope.includes("ui")) return "ui";
  if (signature.feature_scope.includes("ui-backend")) return "uiBackend";
  return fail("MTCLI_FORMALIZE_SCOPE", `compiled feature edge has no admitted scope:${edge.edge_id}`);
}

function createMetaTypeFormalizationProjectionWithModuleSet(
  graph: CompiledProjectGraph,
  leanModuleSet: FormalizationLeanModuleSet,
): MetaTypeFormalizationProjection {
  if (graph.schema_version !== "domainspec.compiled-project-graph/v1-candidate" || graph.authority_effect !== "none") fail("MTCLI_FORMALIZE_GRAPH", "formalize requires the decoded, non-effectful project graph");
  const backend = FROZEN_META_TYPE_CATALOG.backend_meta_types.map(({ label }) => ({ label, lean_constructor: LEAN_META_TYPE[label] ?? fail("MTCLI_FORMALIZE_META_TYPE", `missing Lean constructor:${label}`), partition: "backend" as const }));
  const ui = UI_META_TYPES.map((label) => ({ label, lean_constructor: LEAN_META_TYPE[label] ?? fail("MTCLI_FORMALIZE_META_TYPE", `missing Lean constructor:${label}`), partition: "ui-supporting-context" as const }));
  const relationships = FROZEN_RELATIONSHIP_AUTHORITY_V1.signatures.map((signature) => ({
    id: signature.id,
    lean_constructor: LEAN_RELATION[signature.id] ?? fail("MTCLI_FORMALIZE_RELATIONSHIP", `missing Lean relation constructor:${signature.id}`),
    source_types: signature.source_types.map((label) => LEAN_META_TYPE[label] ?? fail("MTCLI_FORMALIZE_ENDPOINT", `missing Lean meta-type:${label}`)),
    target_types: signature.target_types.map((label) => LEAN_META_TYPE[label] ?? fail("MTCLI_FORMALIZE_ENDPOINT", `missing Lean meta-type:${label}`)),
    scopes: signature.feature_scope.map((scope) => LEAN_SCOPE[scope] ?? fail("MTCLI_FORMALIZE_SCOPE", `missing Lean scope:${scope}`)),
    multiplicity: LEAN_MULTIPLICITY[signature.multiplicity] ?? fail("MTCLI_FORMALIZE_MULTIPLICITY", `missing Lean multiplicity:${signature.multiplicity}`),
    inverse_kind: signature.inverse.kind,
    obligation_ids: Object.freeze([...signature.validation_obligations]),
  }));
  const obligationRelations = new Map<string, string[]>();
  for (const signature of FROZEN_RELATIONSHIP_AUTHORITY_V1.signatures) for (const id of signature.validation_obligations) {
    const relationIds = obligationRelations.get(id) ?? [];
    relationIds.push(signature.id);
    obligationRelations.set(id, relationIds);
  }
  const obligationCatalog = [...obligationRelations].map(([id, relationIds]) => Object.freeze({ obligation_id: id, lean_constructor: leanIdentifier(id), family: obligationFamily(id), relationship_ids: Object.freeze(relationIds.sort()) })).sort((a, b) => a.obligation_id.localeCompare(b.obligation_id));
  const graphNodes = graph.nodes.map((node): ProjectNodeProjection => {
    const transitions = node.kind === "State Machine" ? node.body.transitions as readonly StateTransitionSpec[] : [];
    const interfaceOperations = node.kind === "Interface" ? node.body.operations as readonly InterfaceOperationSpec[] : [];
    const typedRecord = (node.kind === "Entity" || node.kind === "Value Object") && (node.body.typed_contract as { schema_version?: unknown } | undefined)?.schema_version === "domainspec.typed-record/v1"
      ? node.body.typed_contract as unknown as TypedRecordContract
      : null;
    const fields: readonly FieldSpec[] = node.kind === "Entity" || node.kind === "Value Object"
      ? typedRecord === null ? node.body.fields as readonly FieldSpec[] : []
      : node.kind === "Event"
        ? [node.body.occurrence_id as FieldSpec, ...node.body.payload as readonly FieldSpec[]]
        : node.kind === "Interface"
          ? interfaceOperations.flatMap(({ request, result }) => [...request, ...result])
          : [];
    return Object.freeze({
      selector: node.selector, feature_id: node.feature_id, node_id: node.node_id,
      meta_type: LEAN_META_TYPE[node.kind] ?? fail("MTCLI_FORMALIZE_PROJECT_NODE", `missing Lean project meta-type:${node.kind}`),
      generated_creation_targets: Object.freeze([...(node.generated_relationship_projections.creation_targets ?? [])]),
      authored_forbidden_projection_attributes: Object.freeze([...node.authored_forbidden_projection_attributes]),
      typed_field_ids: Object.freeze(typedRecord === null ? fields.map(({ field_id }) => field_id) : typedRecord.properties.map(({ name }) => name)),
      typed_field_type_refs: Object.freeze(typedRecord === null ? fields.map(({ type_ref }) => type_ref.kind === "primitive" ? `primitive:${type_ref.name}` : `reference:${type_ref.selector}`) : typedRecord.properties.map(({ type }) => `typed:${canonicalJson(type)}`)),
      entity_identity_field: node.kind === "Entity" ? typedRecord?.properties.find(({ identity }) => identity)?.name ?? String(node.body.identity_field) : "",
      value_object_structural_equality: node.kind === "Value Object",
      enum_values: Object.freeze(node.kind === "Enum" ? [...node.body.values as readonly string[]] : []),
      event_type: node.kind === "Event" ? String(node.body.event_type) : "",
      event_version: node.kind === "Event" ? String(node.body.version) : "",
      event_occurrence_field: node.kind === "Event" ? (node.body.occurrence_id as FieldSpec).field_id : "",
      event_occurred_at_policy: node.kind === "Event" ? String(node.body.occurred_at_policy) : "",
      interface_boundary_kind: node.kind === "Interface" ? String(node.body.boundary_kind) : "",
      interface_version: node.kind === "Interface" ? String(node.body.version) : "",
      interface_compatibility: node.kind === "Interface" ? String(node.body.compatibility) : "",
      interface_operation_refs: Object.freeze(interfaceOperations.map(({ operation_ref }) => operation_ref)),
      state_machine_states: Object.freeze(node.kind === "State Machine" ? [...node.body.states as readonly string[]] : []),
      state_machine_initial: node.kind === "State Machine" ? String(node.body.initial) : "",
      state_machine_transitions: Object.freeze(transitions.map((transition) => Object.freeze({
        transition_id: transition.transition_id,
        source_state: transition.source_state,
        target_state: transition.target_state,
        guard_ref: transition.guard_ref ?? "",
        effect_event_ref: transition.effect_event_ref ?? "",
      }))),
    });
  });
  const nodeBySelector = new Map(graphNodes.map((node) => [node.selector, node]));
  const signatureById = new Map(FROZEN_RELATIONSHIP_AUTHORITY_V1.signatures.map((signature) => [signature.id, signature]));
  const graphEdges = graph.relationships.map((edge): ProjectEdgeProjection => {
    const signature = signatureById.get(edge.relationship) ?? fail("MTCLI_FORMALIZE_PROJECT_EDGE", `missing relationship signature:${edge.relationship}`);
    const sourceSelector = `${edge.source.feature_id}:${edge.source.node_id}`;
    return Object.freeze({
      edge_id: edge.edge_id, relation: LEAN_RELATION[edge.relationship] ?? fail("MTCLI_FORMALIZE_PROJECT_EDGE", `missing Lean relation:${edge.relationship}`),
      scope: edgeScope(edge, signature), source_selector: sourceSelector, target_selector: `${edge.target.feature_id}:${edge.target.node_id}`,
      source_type: LEAN_META_TYPE[edge.source.kind] ?? fail("MTCLI_FORMALIZE_PROJECT_EDGE", `missing Lean source type:${edge.source.kind}`),
      target_type: LEAN_META_TYPE[edge.target.kind] ?? fail("MTCLI_FORMALIZE_PROJECT_EDGE", `missing Lean target type:${edge.target.kind}`),
      authored_relationship_id: edge.relationship,
      source_generated_creation_targets: nodeBySelector.get(sourceSelector)?.generated_creation_targets ?? Object.freeze([]),
      source_authored_generated_projection: (nodeBySelector.get(sourceSelector)?.authored_forbidden_projection_attributes.length ?? 0) > 0,
      obligation_ids: Object.freeze([...signature.validation_obligations]),
    });
  });
  const applicableWitnesses = graphEdges.flatMap((edge) => edge.obligation_ids.map((obligationId) => {
    const witnessId = `${edge.edge_id}:${obligationId}`;
    return Object.freeze({ witness_id: witnessId, lean_constructor: leanIdentifier(witnessId), edge_id: edge.edge_id, obligation_id: obligationId });
  }));
  if (backend.length !== 13 || ui.length !== 11 || relationships.length !== 31 || obligationCatalog.length !== 45) fail("MTCLI_FORMALIZE_COVERAGE", "formalization source denominator drift");
  const graphIdentity = {
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    source_bytes_sha256: graph.source_manifest.aggregate_sha256,
    nodes: graphNodes,
    edges: graphEdges,
  };
  const refinement = createCompilerRefinementOutput(graph, { nodes: graphNodes, edges: graphEdges });
  const graphSha256 = refinement.certificate.graph_sha256;
  const renderPayload = deepFreeze<FormalizationRenderPayload>({
    schema_version: "domainspec.meta-type-formalization-render-payload/v1-candidate",
    baseline: { id: FROZEN_META_TYPE_CATALOG.baseline_id, digest: FROZEN_META_TYPE_CATALOG.baseline_digest, manifest_sha256: FROZEN_META_TYPE_CATALOG.manifest_sha256 },
    relationship_authority: { path: FROZEN_RELATIONSHIP_AUTHORITY_V1.source_path, sha256: FROZEN_RELATIONSHIP_AUTHORITY_V1.source_sha256, signature_count: 31 },
    lean_module_set: {
      schema_version: "domainspec.formalization-lean-module-set-projection/v1-candidate",
      sha256: leanModuleSet.sha256,
      modules: leanModuleSet.modules.map(({ filename, sha256: moduleSha256 }) => Object.freeze({ filename, sha256: moduleSha256 })),
    },
    project_graph: { ...graphIdentity, graph_sha256: graphSha256 },
    meta_types: [...backend, ...ui],
    relationships,
    obligation_catalog: obligationCatalog,
    applicable_witnesses: applicableWitnesses,
    graph_certificate: refinement.certificate,
    typescript_projection: refinement.typescript_projection,
  });
  const renderPayloadSha256 = sha256(JSON.stringify(renderPayload));
  return deepFreeze({
    schema_version: "domainspec.meta-type-formalization-projection/v2-candidate", authority_effect: "none",
    claim_ceiling: "compiled-project-graph-projection-only-no-runtime-conformance-or-authority",
    render_payload_sha256: renderPayloadSha256,
    render_payload: renderPayload,
    baseline: renderPayload.baseline,
    relationship_authority: renderPayload.relationship_authority,
    project_graph: renderPayload.project_graph,
    meta_types: renderPayload.meta_types,
    relationships: renderPayload.relationships,
    obligation_catalog: renderPayload.obligation_catalog,
    applicable_witnesses: renderPayload.applicable_witnesses,
  });
}

export function createMetaTypeFormalizationProjection(graph: CompiledProjectGraph): MetaTypeFormalizationProjection {
  return createMetaTypeFormalizationProjectionWithModuleSet(graph, formalizationLeanModuleSet());
}

/** Internal deterministic seam for module source-sensitivity tests; not exported by the package root. */
export function createMetaTypeFormalizationProjectionForModuleSources(
  graph: CompiledProjectGraph,
  sources: FormalizationLeanModuleSources,
): MetaTypeFormalizationProjection {
  return createMetaTypeFormalizationProjectionWithModuleSet(graph, createFormalizationLeanModuleSet(sources));
}

export function formalizationProjectionSha256(projection: MetaTypeFormalizationProjection): string { return sha256(JSON.stringify(projection)); }

export function renderLeanMetaTypeFormalization(projection: MetaTypeFormalizationProjection): string {
  const payload = projection.render_payload;
  if (sha256(JSON.stringify(payload)) !== projection.render_payload_sha256) {
    fail("MTCLI_FORMALIZE_PAYLOAD_DIGEST", "formalization render payload digest is stale");
  }
  const meta = payload.meta_types.map(({ lean_constructor }) => lean_constructor);
  const relations = payload.relationships;
  const obligations = payload.obligation_catalog;
  const signatureRows = relations.map((relation) => `  | .${relation.lean_constructor} => ⟨${leanList(relation.source_types)}, ${leanList(relation.target_types)}, ${leanList(relation.scopes)}, .${relation.multiplicity}, .${relation.inverse_kind === "generated_view" ? "generatedView" : "none"}, ${leanList(relation.obligation_ids.map(leanIdentifier))}⟩`);
  const familyRows = obligations.map((obligation) => `  | .${obligation.lean_constructor} => .${leanIdentifier(obligation.family)}`);
  const nodeRows = payload.project_graph.nodes.map((node) => `  ⟨${JSON.stringify(node.selector)}, ${JSON.stringify(node.feature_id)}, ${JSON.stringify(node.node_id)}, .${node.meta_type}, ${leanStringList(node.generated_creation_targets)}, ${leanStringList(node.authored_forbidden_projection_attributes)}, ${leanStringList(node.typed_field_ids)}, ${leanStringList(node.typed_field_type_refs)}, ${JSON.stringify(node.entity_identity_field)}, ${node.value_object_structural_equality}, ${leanStringList(node.enum_values)}, ${JSON.stringify(node.event_type)}, ${JSON.stringify(node.event_version)}, ${JSON.stringify(node.event_occurrence_field)}, ${JSON.stringify(node.event_occurred_at_policy)}, ${JSON.stringify(node.interface_boundary_kind)}, ${JSON.stringify(node.interface_version)}, ${JSON.stringify(node.interface_compatibility)}, ${leanStringList(node.interface_operation_refs)}, ${leanStringList(node.state_machine_states)}, ${JSON.stringify(node.state_machine_initial)}, ${leanStateTransitionList(node.state_machine_transitions)}⟩`);
  const edgeRows = payload.project_graph.edges.map((edge) => `  ⟨${JSON.stringify(edge.edge_id)}, .${edge.relation}, .${edge.scope}, ${JSON.stringify(edge.source_selector)}, ${JSON.stringify(edge.target_selector)}, .${edge.source_type}, .${edge.target_type}, ${JSON.stringify(edge.authored_relationship_id)}, ${leanStringList(edge.source_generated_creation_targets)}, ${edge.source_authored_generated_projection}⟩`);
  const witnessRows = payload.applicable_witnesses.map((witness) => `  ⟨${JSON.stringify(witness.witness_id)}, ${JSON.stringify(witness.edge_id)}, .${leanIdentifier(witness.obligation_id)}⟩`);
  return [
    "import DomainSpecMetaTypeTypeScriptProjectionRefinement", "",
    "/- Generated by domainspec-v2 formalize from one compiled project graph. Do not hand-edit.", `   Project: ${payload.project_graph.project_id}.`,
    `   Source manifest: ${payload.project_graph.source_manifest_sha256}.`, `   Source bytes: ${payload.project_graph.source_bytes_sha256}.`,
    `   Compiled graph: ${payload.project_graph.graph_sha256}.`, `   Reusable Lean module set: ${payload.lean_module_set.sha256}.`, `   Render payload: ${projection.render_payload_sha256}.`,
    `   Baseline: ${payload.baseline.id} (${payload.baseline.digest}).`, `   Relationship authority: ${payload.relationship_authority.path} (${payload.relationship_authority.sha256}). -/`,
    "namespace DomainSpec.CurrentGenerated", "", `def reusableLeanModuleSetSha256 : String := ${JSON.stringify(payload.lean_module_set.sha256)}`, "",
    `inductive MetaType | ${meta.join(" | ")} deriving DecidableEq, BEq, Repr`, `def allMetaTypes : List MetaType := ${leanList(meta)}`,
    "theorem allMetaTypes_count : allMetaTypes.length = 24 := by decide", "theorem allMetaTypes_complete : ∀ m : MetaType, allMetaTypes.contains m = true := by intro m; cases m <;> decide", "",
    `inductive Relation | ${relations.map(({ lean_constructor }) => lean_constructor).join(" | ")} deriving DecidableEq, BEq, Repr`,
    `def allRelations : List Relation := ${leanList(relations.map(({ lean_constructor }) => lean_constructor))}`, "theorem allRelations_count : allRelations.length = 31 := by decide",
    "theorem allRelations_complete : ∀ r : Relation, allRelations.contains r = true := by intro r; cases r <;> decide", "",
    `inductive ObligationId | ${obligations.map(({ lean_constructor }) => lean_constructor).join(" | ")} deriving DecidableEq, BEq, Repr`,
    `def allObligationIds : List ObligationId := ${leanList(obligations.map(({ lean_constructor }) => lean_constructor))}`,
    "theorem allObligationIds_count : allObligationIds.length = 45 := by decide", "theorem allObligationIds_complete : ∀ o : ObligationId, allObligationIds.contains o = true := by intro o; cases o <;> decide", "",
    "inductive ObligationFamily | endpoint | scope | multiplicity | generatedProjection | inverseCollapse | deprecation deriving DecidableEq, BEq, Repr", "def obligationFamily : ObligationId → ObligationFamily", ...familyRows, "",
    "inductive FeatureScope | sameFeature | crossFeature | ui | uiBackend deriving DecidableEq, BEq, Repr",
    "inductive Multiplicity | oneToOne | oneToMany | oneToManyOrdered | manyToOne | manyToMany deriving DecidableEq, BEq, Repr",
    "inductive InverseKind | none | generatedView deriving DecidableEq, BEq, Repr", "structure RelationshipSignature where", "  sourceTypes : List MetaType", "  targetTypes : List MetaType", "  scopes : List FeatureScope", "  multiplicity : Multiplicity", "  inverse : InverseKind", "  obligations : List ObligationId", "def signature : Relation → RelationshipSignature", ...signatureRows, "",
    "structure StateTransition where", "  transitionId : String", "  sourceState : String", "  targetState : String", "  guardRef : String", "  effectEventRef : String", "  deriving DecidableEq, BEq, Repr", "",
    "structure ProjectNode where", "  selector : String", "  featureId : String", "  nodeId : String", "  metaType : MetaType", "  generatedCreationTargets : List String", "  authoredForbiddenProjectionAttributes : List String", "  typedFieldIds : List String", "  typedFieldTypeRefs : List String", "  entityIdentityField : String", "  valueObjectStructuralEquality : Bool", "  enumValues : List String", "  eventType : String", "  eventVersion : String", "  eventOccurrenceField : String", "  eventOccurredAtPolicy : String", "  interfaceBoundaryKind : String", "  interfaceVersion : String", "  interfaceCompatibility : String", "  interfaceOperationRefs : List String", "  stateMachineStates : List String", "  stateMachineInitial : String", "  stateMachineTransitions : List StateTransition", "  deriving DecidableEq, BEq, Repr",
    `def projectNodes : List ProjectNode := [\n${nodeRows.join(",\n")}\n]`, "",
    "structure ProjectEdge where", "  edgeId : String", "  relation : Relation", "  scope : FeatureScope", "  sourceSelector : String", "  targetSelector : String", "  sourceType : MetaType", "  targetType : MetaType", "  authoredRelationshipId : String", "  sourceGeneratedCreationTargets : List String", "  sourceAuthoredGeneratedProjection : Bool", "  deriving DecidableEq, BEq, Repr",
    `def projectEdges : List ProjectEdge := [\n${edgeRows.join(",\n")}\n]`, "",
    "def endpointAllowed (edge : ProjectEdge) : Bool :=", "  (signature edge.relation).sourceTypes.contains edge.sourceType &&", "  (signature edge.relation).targetTypes.contains edge.targetType",
    "def scopeAllowed (edge : ProjectEdge) : Bool := (signature edge.relation).scopes.contains edge.scope",
    "def multiplicityAllowed (edges : List ProjectEdge) (edge : ProjectEdge) : Bool :=", "  if edge.relation == .creates then", "    (edges.filter (fun other => other.relation == .creates && other.sourceSelector == edge.sourceSelector)).length == 1 &&", "    (edges.filter (fun other => other.relation == .creates && other.targetSelector == edge.targetSelector)).length == 1", "  else true",
    "def generatedProjectionAllowed (edge : ProjectEdge) : Bool :=", "  if edge.relation == .creates then edge.sourceGeneratedCreationTargets.contains edge.targetSelector else true",
    "def authoredGeneratedProjectionAbsent (edge : ProjectEdge) : Bool := !edge.sourceAuthoredGeneratedProjection",
    "def inverseCollapseAllowed (edges : List ProjectEdge) (edge : ProjectEdge) : Bool :=", "  !(edge.relation == .belongsTo && edges.any (fun other =>", "    other.relation == .owns && other.sourceSelector == edge.targetSelector && other.targetSelector == edge.sourceSelector))",
    "def deprecatedQueriesAliasAbsent (edge : ProjectEdge) : Bool := edge.authoredRelationshipId != \"queries\"",
    "def enforcesCrossLabelAbsent (edge : ProjectEdge) : Bool := edge.authoredRelationshipId != \"enforces-cross\"", "",
    "def l1RoleHolds (node : ProjectNode) : Bool :=",
    "  match node.metaType with",
    "  | .entity => !node.typedFieldIds.isEmpty && node.typedFieldIds.length == node.typedFieldTypeRefs.length && node.entityIdentityField != \"\" && node.typedFieldIds.contains node.entityIdentityField",
    "  | .valueObject => !node.typedFieldIds.isEmpty && node.typedFieldIds.length == node.typedFieldTypeRefs.length && node.entityIdentityField == \"\" && node.valueObjectStructuralEquality",
    "  | .enumType => !node.enumValues.isEmpty && node.typedFieldIds.isEmpty",
    "  | .event => node.eventType == node.nodeId && node.eventVersion != \"\" && node.eventOccurrenceField != \"\" && node.typedFieldIds.contains node.eventOccurrenceField && (node.eventOccurredAtPolicy == \"required\" || node.eventOccurredAtPolicy == \"generated\")",
    "  | .interfaceType => (node.interfaceBoundaryKind == \"external\" || node.interfaceBoundaryKind == \"internal\") && node.interfaceVersion != \"\" && (node.interfaceCompatibility == \"exact\" || node.interfaceCompatibility == \"backward\") && !node.interfaceOperationRefs.isEmpty",
    "  | _ => true",
    "theorem allProjectL1RolesHold : ∀ node ∈ projectNodes, l1RoleHolds node = true := by decide", "",
    "def stateTransitionHolds (node : ProjectNode) (transition : StateTransition) : Bool :=",
    "  node.stateMachineStates.contains transition.sourceState &&",
    "  node.stateMachineStates.contains transition.targetState &&",
    "  (transition.guardRef == \"\" || projectNodes.any (fun candidate => candidate.selector == transition.guardRef && candidate.metaType == .rule)) &&",
    "  (transition.effectEventRef == \"\" ||",
    "    (projectNodes.any (fun candidate => candidate.selector == transition.effectEventRef && candidate.metaType == .event) &&",
    "     projectEdges.any (fun edge => edge.relation == .transitions && edge.sourceSelector == transition.effectEventRef && edge.targetSelector == node.selector)))",
    "def stateMachineHolds (node : ProjectNode) : Bool :=",
    "  if node.metaType == .stateMachine then",
    "    node.stateMachineStates.contains node.stateMachineInitial &&",
    "    !node.stateMachineTransitions.isEmpty &&",
    "    (node.stateMachineTransitions.map (fun transition => transition.transitionId)).eraseDups.length == node.stateMachineTransitions.length &&",
    "    node.stateMachineTransitions.all (stateTransitionHolds node)",
    "  else true",
    "theorem allProjectStateMachinesHold : ∀ node ∈ projectNodes, stateMachineHolds node = true := by decide", "",
    "def findStateTransition (node : ProjectNode) (transitionId : String) : Option StateTransition :=",
    "  node.stateMachineTransitions.find? (fun transition => transition.transitionId == transitionId)",
    "def stateTransitionAllowed (node : ProjectNode) (current transitionId : String) (guardAccepted : Bool) : Bool :=",
    "  if !node.stateMachineStates.contains current then false else",
    "  match findStateTransition node transitionId with",
    "  | none => false",
    "  | some transition => transition.sourceState == current && (transition.guardRef == \"\" || guardAccepted)",
    "theorem invalidCurrentStateRejected (node : ProjectNode) (current transitionId : String) (guardAccepted : Bool)",
    "    (h : node.stateMachineStates.contains current = false) : stateTransitionAllowed node current transitionId guardAccepted = false := by",
    "  unfold stateTransitionAllowed",
    "  rw [h]",
    "  rfl",
    "theorem undeclaredTransitionRejected (node : ProjectNode) (current transitionId : String) (guardAccepted : Bool)",
    "    (h : findStateTransition node transitionId = none) : stateTransitionAllowed node current transitionId guardAccepted = false := by",
    "  simp [stateTransitionAllowed, h]",
    "theorem sourceMismatchRejected (node : ProjectNode) (current transitionId : String) (guardAccepted : Bool) (transition : StateTransition)",
    "    (hfind : findStateTransition node transitionId = some transition) (hsource : (transition.sourceState == current) = false) : stateTransitionAllowed node current transitionId guardAccepted = false := by",
    "  unfold stateTransitionAllowed",
    "  split",
    "  · rfl",
    "  · rw [hfind]",
    "    simp [hsource]",
    "theorem guardFailureRejected (node : ProjectNode) (current transitionId : String) (transition : StateTransition)",
    "    (hfind : findStateTransition node transitionId = some transition) (hguard : (transition.guardRef == \"\") = false) : stateTransitionAllowed node current transitionId false = false := by",
    "  unfold stateTransitionAllowed",
    "  split",
    "  · rfl",
    "  · rw [hfind]",
    "    simp [hguard]", "",
    "def obligationHolds (edges : List ProjectEdge) (obligation : ObligationId) (edge : ProjectEdge) : Bool :=",
    "  if obligation == .rejectAuthoredGeneratedProjection then authoredGeneratedProjectionAbsent edge",
    "  else if obligation == .deriveCreationTargetsFromEdge then generatedProjectionAllowed edge",
    "  else if obligation == .rejectDeprecatedQueriesAlias then deprecatedQueriesAliasAbsent edge",
    "  else if obligation == .rejectEnforcesCrossLabel then enforcesCrossLabelAbsent edge && scopeAllowed edge",
    "  else match obligationFamily obligation with", "    | .endpoint => endpointAllowed edge", "    | .scope => scopeAllowed edge", "    | .multiplicity => multiplicityAllowed edges edge", "    | .generatedProjection => false", "    | .inverseCollapse => inverseCollapseAllowed edges edge", "    | .deprecation => false", "",
    "structure ApplicableObligationWitness where", "  witnessId : String", "  edgeId : String", "  obligation : ObligationId", "  deriving Repr",
    `def applicableWitnesses : List ApplicableObligationWitness := [\n${witnessRows.join(",\n")}\n]`, "def witnessHolds (witness : ApplicableObligationWitness) : Bool :=", "  match projectEdges.find? (fun edge => edge.edgeId == witness.edgeId) with", "  | some edge => (signature edge.relation).obligations.contains witness.obligation && obligationHolds projectEdges witness.obligation edge", "  | none => false",
    "theorem allApplicableWitnessesHold : ∀ witness ∈ applicableWitnesses, witnessHolds witness = true := by decide", "",
    "open DomainSpec.MetaTypeKernel",
    "open DomainSpec.MetaTypeCompilerRefinement",
    "open DomainSpec.MetaTypeTypeScriptProjectionRefinement", "",
    "structure RefinedProjectGraph where",
    "  nodes : List ProjectNode",
    "  edges : List ProjectEdge",
    "  deriving DecidableEq, BEq, Repr",
    "def refinedProjectGraph : RefinedProjectGraph := ⟨projectNodes, projectEdges⟩",
    "def refinedStaticConforms (graph : RefinedProjectGraph) : Bool :=",
    "  decide (graph = refinedProjectGraph)",
    "theorem refinedProjectGraphStaticConforms : refinedStaticConforms refinedProjectGraph = true := by decide", "",
    "theorem refinedStaticConformanceSound (graph : RefinedProjectGraph)",
    "    (checked : refinedStaticConforms graph = true) :",
    "    graph = refinedProjectGraph ∧",
    "    (∀ node ∈ graph.nodes, l1RoleHolds node = true) ∧",
    "    (∀ node ∈ graph.nodes, stateMachineHolds node = true) ∧",
    "    (∀ witness ∈ applicableWitnesses, witnessHolds witness = true) := by",
    "  have graphExact : graph = refinedProjectGraph := by",
    "    simpa [refinedStaticConforms] using checked",
    "  subst graph",
    "  exact ⟨rfl, by simpa [refinedProjectGraph] using allProjectL1RolesHold, by simpa [refinedProjectGraph] using allProjectStateMachinesHold, allApplicableWitnessesHold⟩", "",
    `def currentSourceIdentity : SourceIdentity := ⟨${JSON.stringify(payload.typescript_projection.project_id)}, ${JSON.stringify(payload.typescript_projection.source_manifest_sha256)}, ${JSON.stringify(payload.typescript_projection.source_bytes_sha256)}⟩`,
    "def unboundSourceIdentity : SourceIdentity := ⟨\"\", \"\", \"\"⟩",
    "def currentTheory : Theory RefinedProjectGraph := {",
    "  staticConforms := refinedStaticConforms",
    `  graphDigest := fun graph => if graph == refinedProjectGraph then ${JSON.stringify(payload.typescript_projection.graph_sha256)} else ""`,
    "  sourceIdentity := fun graph => if graph == refinedProjectGraph then currentSourceIdentity else unboundSourceIdentity",
    "}", "",
    "def currentTypeScriptProjection : TypeScriptProjectionPayload RefinedProjectGraph := {",
    "  graph := refinedProjectGraph",
    `  projectId := ${JSON.stringify(payload.typescript_projection.project_id)}`,
    `  sourceManifestSha256 := ${JSON.stringify(payload.typescript_projection.source_manifest_sha256)}`,
    `  sourceBytesSha256 := ${JSON.stringify(payload.typescript_projection.source_bytes_sha256)}`,
    `  graphSha256 := ${JSON.stringify(payload.typescript_projection.graph_sha256)}`,
    "}",
    "def currentCheckedProjectionInput : CheckedProjectionInput RefinedProjectGraph :=",
    "  lowerTypeScriptProjection currentTypeScriptProjection", "",
    "theorem typescriptProjectionRefinesCheckedInput :",
    "    currentCheckedProjectionInput.graph = currentTypeScriptProjection.graph ∧",
    "    currentCheckedProjectionInput.certificate.graphSha256 = currentTypeScriptProjection.graphSha256 ∧",
    "    currentCheckedProjectionInput.certificate.sourceIdentity.projectId = currentTypeScriptProjection.projectId ∧",
    "    currentCheckedProjectionInput.certificate.sourceIdentity.sourceManifestSha256 = currentTypeScriptProjection.sourceManifestSha256 ∧",
    "    currentCheckedProjectionInput.certificate.sourceIdentity.sourceBytesSha256 = currentTypeScriptProjection.sourceBytesSha256 :=",
    "  lowerTypeScriptProjection_refines_checked_input currentTypeScriptProjection", "",
    "theorem currentCertificateChecks :",
    "    checkCertificate currentTheory currentCheckedProjectionInput.graph currentCheckedProjectionInput.certificate = true := by decide",
    "theorem currentCompilerEmitsCertificate :",
    "    compileChecked currentTheory currentCheckedProjectionInput = some currentCheckedProjectionInput.certificate := by decide",
    "theorem currentCompileSuccessImpliesBoundStaticConformance :",
    "    GraphDigestBound currentTheory currentCheckedProjectionInput.graph currentCheckedProjectionInput.certificate ∧",
    "    SourceIdentityBound currentTheory currentCheckedProjectionInput.graph currentCheckedProjectionInput.certificate ∧",
    "    StaticConforms currentTheory currentCheckedProjectionInput.graph :=",
    "  compile_success_implies_static_conformance currentTheory currentCheckedProjectionInput currentCheckedProjectionInput.certificate currentCompilerEmitsCertificate", "",
    "theorem currentCompileSuccessCarriesGeneratedObligations :",
    "    (∀ node ∈ currentCheckedProjectionInput.graph.nodes, l1RoleHolds node = true) ∧",
    "    (∀ node ∈ currentCheckedProjectionInput.graph.nodes, stateMachineHolds node = true) ∧",
    "    (∀ witness ∈ applicableWitnesses, witnessHolds witness = true) :=",
    "  (refinedStaticConformanceSound currentCheckedProjectionInput.graph currentCompileSuccessImpliesBoundStaticConformance.2.2).2", "",
    "def forgedGraphDigestProjection : TypeScriptProjectionPayload RefinedProjectGraph :=",
    `  { currentTypeScriptProjection with graphSha256 := ${JSON.stringify("0".repeat(64))} }`,
    "theorem conformingGraphWithForgedDigestRejected :",
    "    checkCertificate currentTheory (lowerTypeScriptProjection forgedGraphDigestProjection).graph (lowerTypeScriptProjection forgedGraphDigestProjection).certificate = false := by decide", "",
    "def forgedSourceIdentityProjection : TypeScriptProjectionPayload RefinedProjectGraph :=",
    "  { currentTypeScriptProjection with projectId := \"forged-project\" }",
    "theorem conformingGraphWithForgedSourceIdentityRejected :",
    "    checkCertificate currentTheory (lowerTypeScriptProjection forgedSourceIdentityProjection).graph (lowerTypeScriptProjection forgedSourceIdentityProjection).certificate = false := by decide", "",
    "end DomainSpec.CurrentGenerated", "",
  ].join("\n");
}

interface FormalizationMaterializationHooks {
  readonly before_publish?: (stagingDirectory: string, targetDirectory: string) => void;
}

export interface FormalizationMaterializationResult {
  readonly projection_sha256: string;
  readonly render_payload_sha256: string;
  readonly project_graph_sha256: string;
  readonly lean_module_set_sha256: string;
  readonly proof_unit_sha256: string;
  readonly target_path: string;
  readonly module_paths: readonly string[];
}

interface FormalizationProofUnit {
  readonly projection: MetaTypeFormalizationProjection;
  readonly sources: readonly Readonly<{ filename: string; target: string; source: string }>[];
  readonly proof_unit_sha256: string;
}

function createFormalizationProofUnit(
  graph: CompiledProjectGraph,
  targetPath: string,
  moduleSources: FormalizationLeanModuleSources,
): FormalizationProofUnit {
  const directory = path.dirname(targetPath);
  const targetFilename = path.basename(targetPath);
  if (FORMALIZATION_LEAN_MODULE_FILENAMES.includes(targetFilename as typeof FORMALIZATION_LEAN_MODULE_FILENAMES[number])) {
    fail("MTCLI_FORMALIZE_TARGET", `generated module filename is reserved:${targetFilename}`);
  }
  const moduleSet = createFormalizationLeanModuleSet(moduleSources);
  const projection = createMetaTypeFormalizationProjectionWithModuleSet(graph, moduleSet);
  const sources = Object.freeze([
    ...moduleSet.modules.map(({ filename, source }) => Object.freeze({ filename, target: path.join(directory, filename), source })),
    Object.freeze({ filename: targetFilename, target: targetPath, source: renderLeanMetaTypeFormalization(projection) }),
  ]);
  return deepFreeze({
    projection,
    sources,
    proof_unit_sha256: sha256(JSON.stringify(sources.map(({ filename, source }) => ({ filename, source })))),
  });
}

/** Internal deterministic seam for module source-sensitivity tests; not exported by the package root. */
export function createFormalizationProofUnitForModuleSources(
  graph: CompiledProjectGraph,
  targetPath: string,
  moduleSources: FormalizationLeanModuleSources,
): Readonly<{ projection: MetaTypeFormalizationProjection; proof_unit_sha256: string }> {
  const proofUnit = createFormalizationProofUnit(graph, targetPath, moduleSources);
  return deepFreeze({ projection: proofUnit.projection, proof_unit_sha256: proofUnit.proof_unit_sha256 });
}

function materializationResult(proofUnit: FormalizationProofUnit, targetPath: string): FormalizationMaterializationResult {
  return deepFreeze({
    projection_sha256: formalizationProjectionSha256(proofUnit.projection),
    render_payload_sha256: proofUnit.projection.render_payload_sha256,
    project_graph_sha256: proofUnit.projection.project_graph.graph_sha256,
    lean_module_set_sha256: proofUnit.projection.render_payload.lean_module_set.sha256,
    proof_unit_sha256: proofUnit.proof_unit_sha256,
    target_path: targetPath,
    module_paths: proofUnit.sources.slice(0, -1).map(({ target }) => target),
  });
}

function materializeLeanMetaTypeFormalizationWithHooks(
  graph: CompiledProjectGraph,
  targetPath: string,
  hooks: FormalizationMaterializationHooks = {},
): FormalizationMaterializationResult {
  if (!path.isAbsolute(targetPath)) fail("MTCLI_FORMALIZE_TARGET", "formalize target must be absolute");
  const proofUnit = createFormalizationProofUnit(graph, targetPath, formalizationLeanModuleSources());
  const targetDirectory = path.dirname(targetPath);
  const targetParent = path.dirname(targetDirectory);
  fs.mkdirSync(targetParent, { recursive: true });
  if (fs.existsSync(targetDirectory)) fail("MTCLI_FORMALIZE_TARGET_EXISTS", `formalization target directory already exists:${targetDirectory}`);
  const stagingDirectory = fs.mkdtempSync(path.join(targetParent, `.${path.basename(targetDirectory)}.formalize-`));
  try {
    for (const item of proofUnit.sources) {
      fs.writeFileSync(path.join(stagingDirectory, item.filename), item.source, { encoding: "utf8", flag: "wx" });
    }
    hooks.before_publish?.(stagingDirectory, targetDirectory);
    if (fs.existsSync(targetDirectory)) fail("MTCLI_FORMALIZE_TARGET_EXISTS", "a competing writer created the formalization target directory");
    fs.renameSync(stagingDirectory, targetDirectory);
  } catch (error) {
    if (fs.existsSync(stagingDirectory)) fs.rmSync(stagingDirectory, { recursive: true, force: true });
    if (["EEXIST", "ENOTEMPTY"].includes((error as NodeJS.ErrnoException).code ?? "")) {
      fail("MTCLI_FORMALIZE_TARGET_EXISTS", "a competing writer created the formalization target directory");
    }
    throw error;
  }
  return materializationResult(proofUnit, targetPath);
}

export function materializeLeanMetaTypeFormalization(
  graph: CompiledProjectGraph,
  targetPath: string,
): FormalizationMaterializationResult {
  return materializeLeanMetaTypeFormalizationWithHooks(graph, targetPath);
}

/** Internal hostile-race seam; not exported by the package root. */
export function materializeLeanMetaTypeFormalizationForTest(
  graph: CompiledProjectGraph,
  targetPath: string,
  hooks: FormalizationMaterializationHooks,
): FormalizationMaterializationResult {
  return materializeLeanMetaTypeFormalizationWithHooks(graph, targetPath, hooks);
}

export function checkLeanMetaTypeFormalization(graph: CompiledProjectGraph, targetPath: string): FormalizationMaterializationResult & Readonly<{ current: boolean }> {
  if (!path.isAbsolute(targetPath)) fail("MTCLI_FORMALIZE_TARGET", "formalize-check target must be absolute");
  const proofUnit = createFormalizationProofUnit(graph, targetPath, formalizationLeanModuleSources());
  const targetDirectory = path.dirname(targetPath);
  const expectedFilenames = proofUnit.sources.map(({ filename }) => filename).sort();
  const actualFilenames = fs.existsSync(targetDirectory) && fs.statSync(targetDirectory).isDirectory()
    ? fs.readdirSync(targetDirectory).sort()
    : [];
  const current = JSON.stringify(actualFilenames) === JSON.stringify(expectedFilenames)
    && proofUnit.sources.every(({ target, source }) => fs.readFileSync(target, "utf8") === source);
  return deepFreeze({ ...materializationResult(proofUnit, targetPath), current });
}
