import { assertCompiledProjectSnapshot, validateCompiledProjectGraphObligations, type CompiledProjectGraph } from '../input/project-model.js';
import { createCompiledProjectCertificate, createCompiledSemanticGraph } from '../compilation/certificate.js';
import { createCompilerRefinementOutput, validateGraphBoundCertificate } from '../formalization/refinement.js';
import { assertReconciledProjectPlan, selectReconciledArtifacts, type ReconciledProjectPlan } from '../generation/reconciled-project.js';
import { assertInterfaceData } from '../typed-backend/interface.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import {createReconciledArtifactCoverage} from './reconciled-artifacts.js';

export const RECONCILED_VERIFICATION_PROJECTION_DEFINITION_SHA256 = 'd3ada0d819c8e1d2fbd0bd3b26dc330c5d756eb3454f098f4b092e3588896ed8';
export class ReconciledVerificationProjectionError extends Error {
  readonly exitCode = 22;
  readonly code = 'DS_RECONCILED_VERIFICATION_PROJECTION';
  constructor(readonly pointer: string, message: string) { super('DS_RECONCILED_VERIFICATION_PROJECTION:' + pointer + ':' + message); this.name = 'ReconciledVerificationProjectionError'; }
}
const registered = new WeakSet<object>();
function fail(pointer: string, message: string): never { throw new ReconciledVerificationProjectionError(pointer, message); }
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}

/** Verification inputs only: no native validator, formalizer or publisher runs here. */
export function createReconciledVerificationProjection(graph: CompiledProjectGraph, plan: ReconciledProjectPlan) {
  assertCompiledProjectSnapshot(graph);
  assertReconciledProjectPlan(plan);
  const coverage = createReconciledArtifactCoverage(plan);
  validateCompiledProjectGraphObligations(graph);
  const certificate = createCompiledProjectCertificate(graph);
  if (canonicalJson(certificate) !== canonicalJson(plan.resolved.certificate)) fail('/compiled-certificate', 'graph and plan certificates do not match');
  const semantic = structuredClone(createCompiledSemanticGraph(graph));
  const finiteGraph = { nodes: semantic.nodes, edges: semantic.relationships };
  const refinement = createCompilerRefinementOutput(graph, finiteGraph);
  validateGraphBoundCertificate(graph, finiteGraph, refinement.certificate);
  const nodeViews = plan.node_selectors.map(selector => {
    const view = selectReconciledArtifacts(plan, [selector]);
    return { selector, view_sha256: view.view_sha256, artifact_paths: view.artifacts.map(a => a.relative_path) };
  });
  const requirements = [
    ...plan.resolved.verification_obligations.map(id => ({ id, origin: 'shared-artifact-plan' as const, required: true as const })),
    ...['source-currentness', 'compiled-graph-obligations', 'source-and-selection-preservation', 'isolated-exact-source-replay', 'successor-formalization-currentness', 'exact-output-currentness'].map(id => ({ id, origin: 'project-verification' as const, required: true as const })),
  ];
  const body = {
    schema_version: 'domainspec.reconciled-verification-projection/v1-candidate' as const,
    definition_sha256: RECONCILED_VERIFICATION_PROJECTION_DEFINITION_SHA256,
    source_identity: refinement.certificate.source_identity,
    compiled_certificate: certificate,
    finite_projection_certificate: refinement.certificate,
    project_plan_sha256: plan.plan_sha256,
    source_capsule_sha256: plan.source_capsule_sha256,
    semantic_graph: semantic,
    compilation_selection: plan.selection,
    ...(plan.composition ? {composition_projection: plan.composition} : {}),
    native_projection: {
      resolved_plan_sha256: plan.resolved.plan_sha256,
      boundary_sha256: plan.resolved.boundary_sha256,
      requests: plan.resolved.requests,
      source_blobs: plan.resolved.source_blobs,
      modules: coverage.modules,
      artifacts: coverage.artifacts.map(({ content, ...artifact }) => artifact),
      artifact_coverage: {definition_sha256:coverage.definition_sha256,typescript_paths:coverage.typescript_paths,javascript_paths:coverage.javascript_paths,preserved_paths:coverage.preserved_paths},
      node_views: nodeViews,
    },
    denominators: {
      node_count: graph.nodes.length,
      edge_count: graph.relationships.length,
      project_metatype_count: new Set(graph.nodes.map(node => node.kind)).size,
      applicability_count: graph.obligation_applicability.length,
      witness_count: graph.obligation_witnesses.length,
      artifact_count: coverage.artifacts.length,
      composition_count: plan.composition?.compositions.length ?? 0,
      typescript_artifact_count: coverage.typescript_paths.length,
      javascript_artifact_count: coverage.javascript_paths.length,
      preserved_artifact_count: coverage.preserved_paths.length,
      node_view_count: nodeViews.length,
    },
    evidence_requirements: [...requirements,...(plan.composition ? plan.composition.verification_obligations.filter(id=>!requirements.some(r=>r.id===id)).map(id=>({id,origin:'composition-binding-plan' as const,required:true as const})) : []),...(coverage.javascript_paths.length ? [{id:'generated-javascript-syntax',origin:'artifact-coverage' as const,required:true as const}] : [])],
    claim_scope: 'verification-input-projection-only' as const,
    verification_status: 'not-executed' as const,
    native_compilation: 'not-performed' as const,
    semantic_observation: 'not-performed' as const,
    formal_verification: 'not-performed' as const,
    authority_effect: 'none' as const,
  };
  const result = freeze({ ...body, projection_sha256: sha256(canonicalJson(body)) });
  registered.add(result);
  return result;
}
export type ReconciledVerificationProjection = ReturnType<typeof createReconciledVerificationProjection>;

/** Caller hashes never replace reconstruction from checked source and compilation. */
export function validateReconciledVerificationProjection(value: unknown, graph: CompiledProjectGraph, plan: ReconciledProjectPlan): ReconciledVerificationProjection {
  assertInterfaceData(value);
  const expected = createReconciledVerificationProjection(graph, plan);
  if (canonicalJson(value) !== canonicalJson(expected)) fail('/projection', 'incomplete, changed or unbound verification inputs');
  return expected;
}

export function renderReconciledVerificationProjection(value: ReconciledVerificationProjection): string {
  if (!value || typeof value !== 'object' || !registered.has(value)) fail('/projection', 'registered verification projection required');
  return canonicalJson(value) + '\n';
}
