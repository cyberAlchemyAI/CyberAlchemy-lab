import fs from 'node:fs';
import path from 'node:path';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getCrossGeneratorSource, CROSS_GENERATOR_SOURCE_CAPSULE_SHA256} from './cross-generator-sources.js';
import type {CrossGeneratorPreparation} from './reconciled-cross-generator-public.js';
import {retainedWorkflowExecutionBindings} from './reconciled-cross-generator-public-execution.js';
import type {CrossGeneratorWorkflowExecution} from './reconciled-cross-generator-workflow-execution.js';
import {assertReconciledSemanticControlsFor, type ReconciledSemanticControls} from './reconciled-semantic-controls.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {createWorkflowEffectAudit} from './reconciled-workflow-effect-audit.js';
import {createWorkflowOrchestrationAudit} from './reconciled-workflow-orchestration-audit.js';
import {createWorkflowBinding} from './reconciled-workflow-binding.js';

export const WORKFLOW_PUBLIC_EVIDENCE_DEFINITION_SHA256 = '570cecbca7c0a926ce24ec010ddf1a7499649e5edcba535efdb222da6ada0335';
const fail = (message: string): never => {throw new TypeError('WORKFLOW_PUBLIC_EVIDENCE:' + message);};
const same = (a: unknown, b: unknown, message: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(message);};
const unique = (paths: readonly string[]) => [...new Set(paths)].sort();
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}
const registered = new WeakMap<object, () => void>();

/** Read only a file already owned and hashed by the original live receipt. */
function readCaptured(receipt: CrossGeneratorWorkflowExecution, relative: string) {
  const file = path.join(receipt.workspace, relative), expected = receipt.files[file];
  if (!expected || expected === 'directory' || fs.realpathSync(file) !== file) return fail('uncaptured or symbolic artifact');
  const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile() || stat.size > 16777216) return fail('bounded regular audit artifact required');
    const bytes = Buffer.alloc(stat.size + 1); let size = 0;
    while (size < bytes.length) {const n = fs.readSync(fd, bytes, size, bytes.length - size, null); if (!n) break; size += n;}
    if (size !== stat.size) return fail('artifact changed during read');
    const content = bytes.subarray(0, size);
    if (sha256(content) !== expected) return fail('captured artifact changed');
    return {file, sha256: expected, value: JSON.parse(content.toString('utf8'))};
  } finally {fs.closeSync(fd);}
}

/** Retained lane only. The public executor must still check its own prerequisites,
 * preserve standalone failures and seal the result only after successful cleanup. */
export function bindRetainedWorkflowPublicEvidence(graph: CompiledProjectGraph, plan: ReconciledProjectPlan,
  semantic: ReconciledSemanticControls, preparation: CrossGeneratorPreparation, aggregate: unknown) {
  assertReconciledSemanticControlsFor(semantic, graph, plan);
  if (sha256(getCrossGeneratorSource('workflow_public_evidence')) !== WORKFLOW_PUBLIC_EVIDENCE_DEFINITION_SHA256) fail('definition drift');
  const access = retainedWorkflowExecutionBindings(aggregate, preparation, graph, plan);
  const current = () => {
    assertReconciledSemanticControlsFor(semantic, graph, plan);
    const next = retainedWorkflowExecutionBindings(aggregate, preparation, graph, plan);
    if (next.receipt !== access.receipt || next.binding !== access.binding) fail('original receipt changed');
  };
  const definitions = workflowVerificationDefinitions();
  const effects = createWorkflowEffectAudit(graph, plan, definitions.binding, definitions.effects);
  const orchestration = createWorkflowOrchestrationAudit(graph, plan, definitions);
  const nodes = graph.nodes.filter(node => node.kind === 'Workflow');
  same(semantic.rows.map(r => [r.selector, r.kind]), graph.nodes.map(r => [r.selector, r.kind]), 'complete standalone source denominator');
  same(access.rows.map(r => r.selector), nodes.map(n => n.selector), 'complete retained source denominator');
  const prepared = access.binding.state === 'prepared' ? access.binding.value : null;
  const receipt = access.receipt;
  if (prepared) {
    same(prepared.audit.effects, effects, 'public effect profile mismatch');
    same(prepared.audit.orchestration, orchestration, 'public orchestration profile mismatch');
    same(prepared.audit.definitions, {effects: definitions.effects, orchestration: definitions.orchestration}, 'public audit definition mismatch');
    same(prepared.controls.rows.map(r => r.selector), nodes.map(n => n.selector), 'complete Workflow control denominator');
  }
  if (receipt) {
    if (!prepared) return fail('receipt without original preparation');
    same([receipt.project_plan_sha256, receipt.controls_sha256, receipt.surface_sha256, receipt.audit_sha256],
      [plan.plan_sha256, prepared.controls.controls_sha256, prepared.surface.surface_sha256, prepared.audit.audit_sha256], 'receipt binding mismatch');
    same(receipt.families.map(r => r.selector), prepared.controls.rows.filter(r => r.state === 'ready').map(r => r.selector), 'complete observed family denominator');
    same(Object.keys(receipt.audits).sort(), ['native:effects', 'native:module', 'native:orchestration', 'source:effects', 'source:module', 'source:orchestration'], 'six original audit facets required');
  }
  const rows = nodes.map(node => {
    const sourceBinding = createWorkflowBinding(node, graph, plan, definitions.binding);
    const selected = access.rows.find(r => r.selector === node.selector)!;
    const original = semantic.rows.find(r => r.selector === node.selector)!;
    const control = prepared?.controls.rows.find(r => r.selector === node.selector);
    const family = receipt?.families.find(r => r.selector === node.selector);
    if (control) same(control.modules.map(m => m.relative_path), sourceBinding.module_paths, 'source Workflow path denominator');
    const observed = selected.result === 'pass' && control?.state === 'ready' && !!receipt && !!family;
    if (observed) same([family.inputs.length, family.outputs.length], [control.batches.length, control.batches.length], 'complete batch observations required');
    return {
      selector: node.selector, kind: 'Workflow' as const,
      standalone: original.state === 'ready' ? {state: original.state, case_count: original.cases.length, contract_sha256: original.contract_sha256} : {state: original.state, reason: original.reason},
      retained_status: observed ? 'observed' as const : selected.result === 'fail' ? 'fail' as const : 'not_evaluable' as const,
      reason: observed ? null : selected.reason ?? (control?.state === 'not_evaluable' ? control.reason : 'complete retained Workflow observation unavailable'),
      required_source_paths: sourceBinding.module_paths,
      evidence: observed ? {
        origin: 'original-retained-workflow' as const, workspace: receipt.workspace, controls_sha256: receipt.controls_sha256,
        observation_sha256: receipt.observation_sha256, workflow_sha256: control.workflow_sha256, policy_sha256: control.policy_sha256,
        descriptor_sha256: sha256(canonicalJson(control.descriptor)), material_descriptor_sha256: sha256(canonicalJson(control.material_descriptor)),
        recipes_sha256: sha256(canonicalJson(control.recipes)), dimensions: control.dimensions, search: control.search,
        case_count: control.cases.length, case_ids_sha256: sha256(canonicalJson(control.cases.map(c => c.id))),
        semantic_commitments_sha256: sha256(canonicalJson(control.cases.map(c => ({id: c.id, semantic_sha256: c.expected.semantic_sha256})))),
        original_calls_sha256: sha256(canonicalJson(control.cases.map(c => ({id: c.id, calls: c.expected.calls})))),
        call_count: control.cases.reduce((n, c) => n + c.expected.calls.length, 0), batches: control.batches,
        batch_input_sha256s: family.inputs, batch_observation_sha256s: family.outputs,
        protocol_sha256: receipt.protocol_sha256, cases_definition_sha256: receipt.cases_definition_sha256
      } : null
    };
  });
  const readyPaths = unique(prepared?.controls.rows.flatMap(row => row.state === 'ready' ? row.modules.map(m => m.relative_path) : []) ?? []);
  const missingRoots = rows.filter(row => row.retained_status !== 'observed').map(row => row.selector);
  const facets = (['source', 'native'] as const).flatMap(stage => (['module', 'effects', 'orchestration'] as const).map(facet => {
    const required = facet === 'orchestration' ? orchestration.module_paths : effects.module_paths;
    const expectedPaths = required.filter(p => readyPaths.includes(p));
    const phasePath = (p: string) => stage === 'source' ? p : p.replace(/\.ts$/, '.js');
    const definition = facet === 'module' ? getCrossGeneratorSource('workflow') : definitions[facet];
    const observed: {source_path: string; source_sha256: string; artifact_path: string; artifact_sha256: string; origin: string}[] = [];
    let inputHash: string | null = null, observationHash: string | null = null;
    if (receipt) {
      const input = readCaptured(receipt, stage + '-' + facet + '-audit-input.json');
      const output = readCaptured(receipt, stage + '-' + facet + '-audit-observation.json');
      same(input.value.definition, definition, 'original audit definition');
      same(input.value.phase, stage, 'original audit phase');
      same(input.value.module_root, path.join(receipt.workspace, stage), 'original audit artifact origin');
      same(input.value.module_paths, expectedPaths.map(phasePath), 'original audit path denominator');
      same(output.value.modules.map((m: {relative_path: string}) => m.relative_path), expectedPaths.map(phasePath), 'observed audit path denominator');
      same([output.value.phase, output.value.definition_sha256], [stage, sha256(definition)], 'observed audit identity');
      same(output.sha256, receipt.audits[stage + ':' + facet], 'original audit observation commitment');
      inputHash = input.sha256; observationHash = output.sha256;
      for (const sourcePath of expectedPaths) {
        const artifact = plan.resolved.artifacts.find(a => a.relative_path === sourcePath) ?? fail('source audit artifact missing');
        const artifactPath = path.join(receipt.workspace, stage, phasePath(sourcePath));
        const module = output.value.modules.find((m: {relative_path: string}) => m.relative_path === phasePath(sourcePath));
        same(module.violations, [], 'audit violations');
        same(module.source_sha256, receipt.files[artifactPath], 'audited native/source byte identity');
        if (stage === 'source') same(module.source_sha256, sha256(artifact.content), 'original source byte identity');
        observed.push({source_path: sourcePath, source_sha256: sha256(artifact.content), artifact_path: artifactPath,
          artifact_sha256: module.source_sha256, origin: 'original-retained-workflow-' + stage});
      }
    }
    const missingPaths = required.filter(p => !observed.some(row => row.source_path === p));
    return {facet: stage + ':' + facet, definition_sha256: sha256(definition), required_source_paths: required,
      observed, missing_source_paths: missingPaths, missing_workflow_selectors: missingRoots,
      status: !nodes.length ? 'inapplicable' as const : !missingPaths.length && !missingRoots.length ? 'observed' as const : 'not_evaluable' as const,
      input_sha256: inputHash, observation_sha256: observationHash};
  }));
  current();
  const body = {schema_version: 'domainspec.workflow-public-evidence/v1-candidate' as const,
    definition_sha256: WORKFLOW_PUBLIC_EVIDENCE_DEFINITION_SHA256, contract_capsule_sha256: CROSS_GENERATOR_SOURCE_CAPSULE_SHA256,
    project_plan_sha256: plan.plan_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256,
    standalone_controls_sha256: semantic.controls_sha256, preparation_sha256: preparation.preparation_sha256,
    node_count: graph.nodes.length, workflow_count: nodes.length, rows, facets,
    retained_status: !nodes.length ? 'inapplicable' as const : rows.some(r => r.retained_status === 'fail') ? 'fail' as const :
      rows.every(r => r.retained_status === 'observed') && facets.every(f => f.status === 'observed') ? 'observed' as const : 'incomplete' as const,
    public_fulfillment: 'not_evaluable' as const, claim_scope: 'retained-workflow-lane-awaiting-public-prerequisites-and-cleanup' as const, authority_effect: 'none' as const};
  const result = freeze({...body, binding_sha256: sha256(canonicalJson(body))}); registered.set(result, current); return result;
}
export type WorkflowPublicEvidence = ReturnType<typeof bindRetainedWorkflowPublicEvidence>;
export function assertWorkflowPublicEvidenceCurrent(value: unknown): asserts value is WorkflowPublicEvidence {
  const current = value && typeof value === 'object' ? registered.get(value) : undefined;
  if (!current) return fail('registered evidence binding required');
  current();
}
