import type {CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectSnapshot, validateCompiledProjectGraphObligations} from '../input/project-model.js';
import {createCompiledProjectCertificate, createCompiledSemanticGraph} from '../compilation/certificate.js';
import {createCompilerRefinementOutput, validateGraphBoundCertificate} from '../formalization/refinement.js';
import {assertReconciledRustProjectPlan, selectReconciledRustArtifacts, type ReconciledRustProjectPlan} from '../generation/reconciled-rust-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeRustProject as freeze} from '../generation/reconciled-rust-selection.js';

export const RUST_VERIFICATION_PROJECTION_VERSION = 'domainspec.reconciled-rust-verification-projection/v1-candidate' as const;
const registered = new WeakSet<object>();
const fail = (reason: string): never => {throw new TypeError('DS_RUST_VERIFICATION_PROJECTION:' + reason);};
const same = (left: unknown, right: unknown, reason: string) => {if (canonicalJson(left) !== canonicalJson(right)) fail(reason);};

/** Closed finite input shared by formalization and native Rust verification.
 * Construction performs no tool execution and writes no output. */
export function createReconciledRustVerificationProjection(graph: CompiledProjectGraph, plan: ReconciledRustProjectPlan) {
  assertCompiledProjectSnapshot(graph); assertReconciledRustProjectPlan(plan); validateCompiledProjectGraphObligations(graph);
  const certificate = createCompiledProjectCertificate(graph); same(certificate, plan.certificate, 'compiled certificate mismatch'); same(graph.source_manifest, plan.semantic_sources, 'source manifest mismatch');
  const semantic = structuredClone(createCompiledSemanticGraph(graph)), finite = {nodes: semantic.nodes, edges: semantic.relationships};
  const refinement = createCompilerRefinementOutput(graph, finite); validateGraphBoundCertificate(graph, finite, refinement.certificate);
  const nodeViews = plan.node_selectors.map(selector => {const view = selectReconciledRustArtifacts(plan, [selector]); return {selector, view_sha256: view.view_sha256, artifact_paths: view.artifacts.map(row => row.relative_path)};});
  const body = {
    schema_version: RUST_VERIFICATION_PROJECTION_VERSION,
    source_identity: refinement.certificate.source_identity,
    compiled_certificate: certificate,
    finite_projection_certificate: refinement.certificate,
    source_manifest: graph.source_manifest,
    semantic_graph: semantic,
    compilation_selection: plan.selection,
    project_plan_sha256: plan.plan_sha256,
    source_capsule_sha256: plan.source_capsule_sha256,
    native_projection: {language: 'rust' as const, checking_scope: plan.checking_scope, boundary_sha256: plan.boundary_sha256, field_compilation_sha256: plan.field_compilation_sha256, cargo: plan.cargo, modules: plan.modules, artifacts: plan.artifacts.map(({content, ...artifact}) => artifact), node_views: nodeViews},
    denominators: {node_count: graph.nodes.length, edge_count: graph.relationships.length, project_metatype_count: new Set(graph.nodes.map(node => node.kind)).size, applicability_count: graph.obligation_applicability.length, witness_count: graph.obligation_witnesses.length, artifact_count: plan.artifacts.length, rust_module_count: plan.modules.length, node_view_count: nodeViews.length},
    claim_scope: 'verification-input-projection-only' as const,
    verification_status: 'not-executed' as const,
    native_compilation: 'not-performed' as const,
    formal_verification: 'not-performed' as const,
    authority_effect: 'none' as const,
  };
  const result = freeze({...body, projection_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}

export type ReconciledRustVerificationProjection = ReturnType<typeof createReconciledRustVerificationProjection>;
export function renderReconciledRustVerificationProjection(value: ReconciledRustVerificationProjection): string {if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered projection required'); return canonicalJson(value) + '\n';}
