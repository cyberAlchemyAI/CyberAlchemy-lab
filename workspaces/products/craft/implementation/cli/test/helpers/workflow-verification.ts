import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import type {TestContext} from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileOperationActionBindings, OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {publicSelection} from './composition-project.ts';

export const workflowProject = path.resolve(import.meta.dirname, '../../../..');
export const workflowDefinitionPath = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation/semantic-workflow-controls-contract.json');
export const workflowDefinition = fs.readFileSync(workflowDefinitionPath, 'utf8');
export const stepIds = ['first', 'second', 'third', 'last'];
const scalar = {kind: 'scalar', name: 'UInt64'};
const input = {op: 'input', name: 'amount', properties: []};
export interface RecoveryFixtureOptions {
  dependencies?: string[][];
  declarationOrder?: number[];
  noCompensations?: boolean;
}

/** Minimal lawful graph: no Entity-shaped placeholder is needed for settlement metadata. */
export function workflowFixture(t: TestContext, options: RecoveryFixtureOptions = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-workflow-reference-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const source = path.join(root, 'source'), nodes: string[] = [], edges: string[] = [];
  const write = (p: string, value: unknown) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');};
  const node = (id: string, kind: string, body: unknown) => {nodes.push(id); write('specs/commerce/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body});};
  const edge = (from: string, relation: string, to: string) => {const id = from + '-' + relation + '-' + to; edges.push(id); write('specs/commerce/edges/' + id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id: id, source_node_id: from, target_node_id: to, relationship: relation, scope: 'feature'});};
  node('allowed', 'Rule', {description: 'Explicit fixture guard.', predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {
    schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{name: 'value', type: scalar}],
    expression: {op: 'eq', left: {op: 'path', root: 'value', properties: []}, right: {op: 'path', root: 'value', properties: []}}
  }});
  const operationIds = options.noCompensations ? ['perform'] : ['perform', 'undo'];
  const definitions = operationIds.map(id => {
    node(id, 'Operation', {description: 'Fixture ' + id, reads: [], writes: [], effects: [], guard: 'allowed', failure_continuation: 'return-' + id + '-error'});
    edge('allowed', 'enforces', id); edge('flow', 'orchestrates', id);
    return {schema_version: OPERATION_ACTION_BINDINGS_VERSION, selector: 'commerce:' + id, inputs: [{name: 'amount', type: scalar}],
      reads: [], writes: [], guards: [{selector: 'commerce:allowed', arguments: [{parameter: 'value', value: {op: 'path', root: 'amount', properties: []}}]}],
      events: [], result: {type: scalar, value: {op: 'path', root: 'amount', properties: []}}, atomicity: 'state-and-outbox', continuation: 'awaited-settlement'};
  });
  const comps = options.noCompensations ? [] : (options.declarationOrder ?? [0, 1, 2]).map(i => ({compensation_id: 'undo-' + stepIds[i],
    for_step: stepIds[i]!, operation_ref: 'commerce:undo', depends_on: options.dependencies?.[i] ?? []}));
  node('flow', 'Workflow', {description: 'Four ordered occurrences of one Operation.', typed_contract: {schema_version: 'domainspec.workflow-occurrences/v1',
    ontology_workflow: 'FIXTURE-FLOW', steps: stepIds.map(step_id => ({step_id, operation_ref: 'commerce:perform'})), compensations: comps}});
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'workflow-reference', features: ['commerce'], cross_feature_edges: []});
  write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges});
  const graph = loadCompiledProjectGraph(source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256,
    graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const actions = definitions.map(d => compileOperationActionBindings(graph, boundary, null, d, getReconciledSource('operation_action')));
  const bindings = {schema_version: WORKFLOW_BINDINGS_VERSION, selector: 'commerce:flow', inputs: [{name: 'amount', type: scalar}], event_inputs: [],
    steps: stepIds.map((step_id, i) => ({step_id, action_sha256: actions[0]!.action_sha256,
      arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: stepIds[i - 1], properties: []} : input}], events: []})),
    compensations: comps.map(c => ({compensation_id: c.compensation_id, action_sha256: actions[1]!.action_sha256,
      arguments: [{parameter: 'amount', value: {op: 'step-result', step_id: c.for_step, properties: []}}], events: []})),
    result: {type: scalar, value: {op: 'step-result', step_id: 'last', properties: []}}};
  const workflow = compileWorkflowBindings(graph, boundary, null, actions, bindings, getReconciledSource('workflow_binding'));
  const policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256,
    contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'}, getReconciledSource('workflow_recovery'));
  const strip = <T extends {action_sha256: string}>(c: T) => {const {action_sha256, ...rest} = c; return rest;};
  const {schema_version, ...authored} = bindings;
  const selection = {...publicSelection(), factories: [], operations: definitions, workflows: [{...authored, steps: bindings.steps.map(strip),
    compensations: bindings.compensations.map(strip), recovery: {dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'}}]};
  return {root, graph, workflow, policy, selection, nativePlan: () => selectReconciledArtifacts(planCompiledReconciledProject(graph, selection))};
}

export function nativeWorkflow(f: ReturnType<typeof workflowFixture>, mutate?: (path: string, content: string) => string) {
  const view = f.nativePlan(), root = fs.mkdtempSync(path.join(f.root, 'native-'));
  for (const a of view.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, mutate ? mutate(a.relative_path, a.content) : a.content);}
  const chain = JSON.parse(fs.readFileSync(path.resolve(workflowProject, '../../toolchains/node-typescript/toolchain.json'), 'utf8'));
  const image = nativeToolchainImage(chain.container_image);
  const require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: [path.join(workflowProject, 'impl'), ...process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))]});
  const deps = path.dirname(path.dirname(path.dirname(types)));
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + root + ',target=' + root,
    '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--workdir', root, image];
  try {
    execFileSync('docker', [...docker, 'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--declaration', '--types', 'node', '--typeRoots', path.join(deps, '@types'),
      '--target', 'ES2022', '--module', 'commonjs', '--rootDir', root, '--outDir', path.join(root, 'js'), ...view.artifacts.map(a => path.join(root, a.relative_path))], {encoding: 'utf8', stdio: 'pipe'});
  } catch (error) {const e = error as Error & {stdout?: string; stderr?: string}; throw new Error([e.message, e.stdout, e.stderr].filter(Boolean).join('\n'), {cause: e});}
  const run = require(path.join(root, 'js/domain/features/commerce/src/application/workflows/flow.js')).workflowFlow;
  return {run, root, view};
}

export function settlementProvider(failureIndex = -1, mode = 'reject') {
  let calls = 0;
  const commits: unknown[] = [], trace: string[] = [];
  const dependency = {store: {begin: async () => {
    const i = calls++; trace.push('begin:' + i);
    return {read: async () => {throw Error('undeclared read');}, rollback: async () => {trace.push('rollback:' + i);}, commit: async (batch: unknown) => {
      trace.push('commit:' + i);
      if (i === failureIndex && mode === 'reject') return {status: 'rejected'};
      if (i === failureIndex && mode === 'indeterminate') return {status: 'indeterminate'};
      if (i === failureIndex && mode === 'malformed') return {status: 'other'};
      if (i === failureIndex && mode === 'throw-before') throw Error('unknown');
      commits.push(batch);
      if (i === failureIndex && mode === 'throw-after') throw Error('lost acknowledgement');
      return {status: 'committed'};
    }};
  }}};
  return {dependency, commits, trace, count: () => calls};
}

import {nativeToolchainImage} from './native-toolchain-image.ts';
