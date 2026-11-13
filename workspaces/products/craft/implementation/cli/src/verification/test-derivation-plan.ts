import { assertCompiledProjectSnapshot, type CompiledProjectGraph, type CompiledProjectGraphNode, type DecodedRelationship } from "../input/project-model.js";
import { canonicalJson, sha256, type SourceManifestEntry } from "../input/source-manifest.js";
import { FROZEN_META_TYPE_CATALOG } from "../meta-types/catalog.js";
import { FROZEN_RELATIONSHIP_AUTHORITY, RELATIONSHIP_SIGNATURES } from "../relationships/authority.js";

/** Source-bound construction obligations. Execution requires an independent target binding and oracle. */
export interface ConstructionTestCase {
  readonly case_id: string;
  readonly subject: string;
  readonly family: "meta-type-formation" | "meta-type-behavior" | "relationship-consequence";
  readonly definition_id: string;
  readonly source_path: string;
  readonly source_sha256: string;
  readonly clause: string;
  readonly observation: string;
  readonly expected: unknown;
  readonly disposition: "source-checked" | "needs-binding" | "needs-oracle";
}

export interface ConstructionTestPlan {
  readonly schema_version: "domainspec.construction-test-plan/v1-candidate";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly meta_type_baseline_digest: string;
  readonly relationship_authority_sha256: string;
  readonly catalog: Readonly<{
    readonly active_backend_meta_types: readonly string[];
    readonly backend_signatures: readonly string[];
    readonly ui_candidate_signatures: readonly string[];
  }>;
  readonly cases: readonly ConstructionTestCase[];
  readonly counts: Readonly<{ readonly nodes: number; readonly relationships: number; readonly source_checked: number; readonly needs_binding: number; readonly needs_oracle: number }>;
  readonly authority_effect: "none";
  readonly plan_sha256: string;
}

export class ConstructionTestPlanError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, message: string) { super(message); this.name = "ConstructionTestPlanError"; }
}

function source(graph: CompiledProjectGraph, path: string): SourceManifestEntry {
  const entry = graph.source_manifest.sources.find((candidate) => candidate.relative_path === path);
  if (!entry) throw new ConstructionTestPlanError("TDE_SOURCE_MISSING", `source manifest omits ${path}`);
  return entry;
}

function makeCase(input: Omit<ConstructionTestCase, "case_id">): ConstructionTestCase {
  return Object.freeze({ ...input, case_id: sha256(canonicalJson(input)) });
}

/* These are authored construction clauses, not answers copied from generated code. */
const BEHAVIOR_CLAUSES: Readonly<Record<string, readonly string[]>> = Object.freeze({
  Entity: ["identity_field", "fields"],
  "Value Object": ["fields", "invariant_refs"],
  Enum: ["values"],
  Operation: ["guard", "reads", "writes", "effects", "failure_continuation", "typed_contract"],
  Query: ["reads", "typed_contract"],
  Calculation: ["inputs", "semantics", "typed_contract"],
  Rule: ["predicate", "typed_contract"],
  Policy: ["strategies", "decisions", "default_strategy", "typed_contract"],
  Workflow: ["steps", "compensations", "compensation_dependencies"],
  Interface: ["operations"],
  Event: ["event_type", "payload", "occurred_at_policy"],
  Mapping: ["source", "target", "direction", "totality", "fields", "typed_contract"],
  "State Machine": ["states", "initial", "transitions"],
});

const RELATIONSHIP_OBSERVATIONS: Readonly<Record<string, string>> = Object.freeze({
  performs: "selected actor initiates the named operation under its declared conditions",
  produces: "successful operation emits the named event and declared payload",
  "produces-for": "cross-feature operation writes or projects the declared target data",
  creates: "successful operation creates a fresh target identity and matches its generated creation projection",
  "triggers-cross": "qualifying cross-feature event activates the named operation under an explicit delivery contract",
  enforces: "rule is checked before the operation mutates or emits an effect",
  calculates: "operation consumes the calculation result at its declared use point",
  transitions: "event drives a declared guarded state transition",
  exposes: "interface entry routes to the named operation or query with declared translation",
  orchestrates: "workflow invokes the named operation at its declared ordered step",
  applies: "operation or calculation uses the policy-selected strategy",
  maps: "target entity or interface receives the declared mapped values",
  contains: "entity embeds the value object while preserving separate identity and value equality",
  reads: "operation or query uses the named entity data in its declared result or decision",
  emits: "event records the named entity as its domain subject",
  owns: "target entity obeys the declared lifecycle, custody, or write-responsibility dimension",
  "belongs-to": "target entity obeys the declared membership, classification, or home-assignment kind",
  renders: "page renders the named component in its declared context",
  wraps: "layout places the named page in its declared slots",
  composes: "parent component includes the child with declared input and output",
  consumes: "component reflects the declared hook state and lifecycle",
  submits: "valid form input invokes the named action and invalid input follows its error path",
  shapes: "deferred Adapter requires resolution against Mapping before a distinct test family",
  protects: "guard allows or blocks page access with the declared fallback, without claiming authorization authority",
  displays: "component displays the declared view-model projection",
  fetches: "binding invokes the exact query with mapped parameters and declared cache behavior",
  mutates: "binding invokes the exact operation and applies declared result and invalidation mappings",
  reflects: "deferred State Indicator split requires resolution before a domain-state visual case",
  derives: "view-model fields follow their declared entity source without domain authority",
  contracts: "form payload and errors match the selected interface entry",
  mirrors: "client guard agrees with the authoritative rule on shared witnesses",
});

function nodeCases(graph: CompiledProjectGraph, node: CompiledProjectGraphNode): ConstructionTestCase[] {
  const entry = source(graph, `specs/${node.feature_id}/nodes/${node.node_id}.json`);
  const definition_id = node.meta_type_id;
  const subject = node.selector;
  const result: ConstructionTestCase[] = [makeCase({
    subject, family: "meta-type-formation", definition_id,
    source_path: entry.relative_path, source_sha256: entry.sha256,
    clause: "typed-node-formation", observation: "checked source satisfies the canonical meta-type criterion",
    expected: { kind: node.kind, meta_type_id: definition_id },
    disposition: "source-checked",
  })];
  const clauses = BEHAVIOR_CLAUSES[node.kind];
  if (!clauses) throw new ConstructionTestPlanError("TDE_TYPE_UNHANDLED", `no derivation family for ${node.kind}`);
  for (const clause of clauses) {
    const value = node.body[clause];
    if (value === undefined || value === null || (Array.isArray(value) && value.length === 0)) continue;
    const values = Array.isArray(value) ? value : [value];
    for (const [index, expected] of values.entries()) {
      result.push(makeCase({
        subject, family: "meta-type-behavior", definition_id,
        source_path: entry.relative_path, source_sha256: entry.sha256,
        clause: Array.isArray(value) ? `${clause}/${index}` : clause,
        observation: `bound target preserves the authored ${node.kind}.${clause} clause`, expected,
        disposition: clause === "values" || clause === "transitions" || clause === "fields" || clause === "operations"
          ? "needs-binding" : "needs-oracle",
      }));
    }
  }
  return result;
}

function edgeCases(graph: CompiledProjectGraph, edge: DecodedRelationship): ConstructionTestCase[] {
  const path = edge.scope === "feature"
    ? `specs/${edge.source.feature_id}/edges/${edge.edge_id}.json`
    : `edges/${edge.edge_id}.json`;
  const entry = source(graph, path);
  return [makeCase({
    subject: edge.edge_id, family: "relationship-consequence", definition_id: `DS-D8:${edge.relationship}`,
    source_path: entry.relative_path, source_sha256: entry.sha256,
    clause: edge.relationship,
    observation: RELATIONSHIP_OBSERVATIONS[edge.relationship] ?? "",
    expected: { source: `${edge.source.feature_id}:${edge.source.node_id}`, target: `${edge.target.feature_id}:${edge.target.node_id}`, scope: edge.scope },
    disposition: "needs-oracle",
  })];
}

export function deriveConstructionTestPlan(graph: CompiledProjectGraph): ConstructionTestPlan {
  assertCompiledProjectSnapshot(graph);
  const active = FROZEN_META_TYPE_CATALOG.backend_meta_types.map(({ label }) => label).sort();
  const handled = Object.keys(BEHAVIOR_CLAUSES).sort();
  if (canonicalJson(active) !== canonicalJson(handled)) throw new ConstructionTestPlanError("TDE_TYPE_COVERAGE", "13-type derivation inventory differs from the admitted catalog");
  const backend = RELATIONSHIP_SIGNATURES.filter((signature) => signature.source_types.every((type) => active.includes(type)) && signature.target_types.every((type) => active.includes(type)));
  const ui = RELATIONSHIP_SIGNATURES.filter((signature) => !backend.includes(signature));
  if (backend.length !== 17 || ui.length !== 14 || RELATIONSHIP_SIGNATURES.length !== 31) throw new ConstructionTestPlanError("TDE_EDGE_COVERAGE", "relationship derivation denominator drift");
  if (canonicalJson(Object.keys(RELATIONSHIP_OBSERVATIONS).sort()) !== canonicalJson(RELATIONSHIP_SIGNATURES.map(({ id }) => id).sort())) throw new ConstructionTestPlanError("TDE_EDGE_RULES", "relationship consequence rules differ from the admitted registry");
  const cases = [...graph.nodes.flatMap((node) => nodeCases(graph, node)), ...graph.relationships.flatMap((edge) => edgeCases(graph, edge))]
    .sort((left, right) => left.case_id.localeCompare(right.case_id));
  if (new Set(cases.map(({ case_id }) => case_id)).size !== cases.length) throw new ConstructionTestPlanError("TDE_CASE_COLLISION", "duplicate construction test case");
  const body = {
    schema_version: "domainspec.construction-test-plan/v1-candidate" as const,
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    meta_type_baseline_digest: FROZEN_META_TYPE_CATALOG.baseline_digest,
    relationship_authority_sha256: FROZEN_RELATIONSHIP_AUTHORITY.source_sha256,
    catalog: {
      active_backend_meta_types: FROZEN_META_TYPE_CATALOG.backend_meta_types.map(({ id }) => id).sort(),
      backend_signatures: backend.map(({ id }) => id).sort(),
      ui_candidate_signatures: ui.map(({ id }) => id).sort(),
    },
    cases,
    counts: {
      nodes: graph.nodes.length, relationships: graph.relationships.length,
      source_checked: cases.filter(({ disposition }) => disposition === "source-checked").length,
      needs_binding: cases.filter(({ disposition }) => disposition === "needs-binding").length,
      needs_oracle: cases.filter(({ disposition }) => disposition === "needs-oracle").length,
    },
    authority_effect: "none" as const,
  };
  return Object.freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
}
