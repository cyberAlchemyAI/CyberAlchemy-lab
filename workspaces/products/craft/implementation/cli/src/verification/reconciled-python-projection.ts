import {assertCompiledProjectSnapshot, validateCompiledProjectGraphObligations, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate, createCompiledSemanticGraph} from '../compilation/certificate.js';
import {createCompilerRefinementOutput, validateGraphBoundCertificate} from '../formalization/refinement.js';
import {assertReconciledPythonProjectPlan, selectReconciledPythonArtifacts, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {getReconciledSource, getReconciledSourceCapsule} from '../generation/reconciled-sources.js';
import {resolvePythonModules} from '../generation/resolved-python-modules.js';
import {pythonSnake} from '../generation/configured-python-owned-values.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezePythonProject as freeze} from '../generation/reconciled-python-selection.js';

export const PYTHON_VERIFICATION_PROJECTION_SHA256 = 'f8b486ae22e628150d0b6679a4244ad6a1b8eea1c58c85ef40cd4cd9b730e446';
const registered = new WeakSet<object>();
const fail = (message: string): never => {throw new TypeError('DS_PYTHON_VERIFICATION_PROJECTION:' + message);};
const same = (a: unknown, b: unknown, label: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(label);};

/** Closed verification input, not a native execution or assurance result. */
export function createReconciledPythonVerificationProjection(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph); assertReconciledPythonProjectPlan(plan);
  const definition = getReconciledSource('python_verification');
  if (sha256(definition) !== PYTHON_VERIFICATION_PROJECTION_SHA256) fail('definition drift');
  const certificate = createCompiledProjectCertificate(graph);
  same(certificate, plan.certificate, 'full compiled certificate mismatch');
  same(graph.source_manifest, plan.semantic_sources, 'source manifest mismatch');
  validateCompiledProjectGraphObligations(graph);
  const semantic = structuredClone(createCompiledSemanticGraph(graph));
  const finite = {nodes: semantic.nodes, edges: semantic.relationships};
  const refinement = createCompilerRefinementOutput(graph, finite);
  validateGraphBoundCertificate(graph, finite, refinement.certificate);

  const native = resolvePythonModules(plan.artifacts, plan.selection.module_root.split('/').map(pythonSnake).join('/'));
  same(native, plan.modules.map(({qualified_selectors, metatypes, ...module}) => module), 'native inventory mismatch');
  same([...new Set(plan.modules.flatMap(m => m.qualified_selectors))].sort(), graph.nodes.map(n => n.selector).sort(), 'node ownership coverage');
  const nodeViews = plan.node_selectors.map(selector => {
    const view = selectReconciledPythonArtifacts(plan, [selector]);
    return {selector, view_sha256: view.view_sha256, artifact_paths: view.artifacts.map(a => a.relative_path)};
  });
  const rows = graph.nodes.map(node => ({
    selector: node.selector, kind: node.kind, source_sha256: sha256(canonicalJson(node)),
    declaration_sha256: sha256(canonicalJson(node.body)),
    module_paths: plan.modules.filter(m => m.qualified_selectors.includes(node.selector)).map(m => m.relative_path),
    required_observations: ['native-form', 'positive-behavior', 'negative-behavior', 'compiling-substitution-controls'],
    state: 'not-executed' as const,
  }));
  const requirements = (JSON.parse(definition) as {required_execution: string[]}).required_execution;
  const body = {
    schema_version: 'domainspec.reconciled-python-verification-projection/v1-candidate' as const,
    definition_sha256: PYTHON_VERIFICATION_PROJECTION_SHA256,
    source_identity: refinement.certificate.source_identity,
    compiled_certificate: certificate, finite_projection_certificate: refinement.certificate,
    source_manifest: graph.source_manifest, semantic_graph: semantic,
    project_plan_sha256: plan.plan_sha256, source_capsule_sha256: plan.source_capsule_sha256,
    compilation_selection: plan.selection,
    native_projection: {
      language: 'python' as const, resolved_plan_sha256: plan.plan_sha256,
      boundary_sha256: plan.boundary_sha256, field_compilation_sha256: plan.field_compilation_sha256,
      requests: plan.requests, modules: plan.modules,
      artifacts: plan.artifacts.map(({content, ...artifact}) => artifact), node_views: nodeViews,
      source_references: getReconciledSourceCapsule().sources.map(({content, ...source}) => source),
    },
    semantic_obligations: rows,
    denominators: {node_count: graph.nodes.length, edge_count: graph.relationships.length,
      project_metatype_count: new Set(graph.nodes.map(n => n.kind)).size,
      applicability_count: graph.obligation_applicability.length, witness_count: graph.obligation_witnesses.length,
      artifact_count: plan.artifacts.length, python_module_count: native.length, node_view_count: nodeViews.length,
      semantic_obligation_count: rows.length, composition_count: graph.compositions?.length ?? 0},
    evidence_requirements: requirements.map(id => ({id, required: true as const, state: 'not-executed' as const})),
    claim_scope: 'verification-input-projection-only' as const, verification_status: 'not-executed' as const,
    native_compilation: 'not-performed' as const, semantic_observation: 'not-performed' as const,
    formal_verification: 'not-performed' as const, authority_effect: 'none' as const,
  };
  const result = freeze({...body, projection_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type ReconciledPythonVerificationProjection = ReturnType<typeof createReconciledPythonVerificationProjection>;
export function validateReconciledPythonVerificationProjection(value: unknown, graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertInterfaceData(value);
  const expected = createReconciledPythonVerificationProjection(graph, plan);
  same(value, expected, 'incomplete or changed verification inputs'); return expected;
}
export function renderReconciledPythonVerificationProjection(value: ReconciledPythonVerificationProjection): string {
  if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered projection required');
  return canonicalJson(value) + '\n';
}
