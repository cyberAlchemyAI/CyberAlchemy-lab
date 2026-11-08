import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import type {TestContext} from 'node:test';
import {workflowFixture, nativeWorkflow, workflowProject} from './workflow-verification.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';

export const scalar = (name = 'UInt64'): any => ({kind: 'scalar', name});
export const named = (name: string): any => ({kind: 'named', selector: 'commerce:' + name});
export const list = (element: any): any => ({kind: 'list', element});
export const set = (element: any): any => ({kind: 'set', element});
export const optional = (element: any): any => ({kind: 'optional', element});
export const money = (quantity: string | bigint = '3'): any => ({quantity});
export const order = (id = '1', label = 'one'): any => ({id, customer: {id: '2', name: 'customer'}, money: money(), choice: {variant: 'Some', payload: money('7')}, labels: [label, label], lines: [money(), money('9')]});
export const workflowValuesDefinitionPath = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation/semantic-workflow-values-contract.json');
export const workflowValuesDefinition = fs.readFileSync(workflowValuesDefinitionPath, 'utf8');

export function workflowValuesFixture(t: TestContext, options: {type?: any; events?: boolean; expression?: 'to_set' | 'projection' | 'literal' | 'variant'} = {}) {
  const base = workflowFixture(t), source = path.join(base.root, 'source');
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(source, p), 'utf8'));
  const write = (p: string, value: unknown) => {const f = path.join(source, p); fs.mkdirSync(path.dirname(f), {recursive: true}); fs.writeFileSync(f, JSON.stringify(value, null, 2) + '\n');};
  const manifest = read('specs/commerce/feature.json');
  const node = (id: string, kind: string, body: unknown) => {manifest.nodes.push(id); write('specs/commerce/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body});};
  const record = (id: string, kind: string, fields: [string, any][]) => node(id, kind, {description: id, fields: fields.map(([name]) => name), ...(kind === 'Value Object' ? {invariant_refs: ['commerce:positive']} : {}), typed_contract: {
    schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-' + id.toUpperCase(), properties: fields.map(([name, type]) => ({name, type, identity: kind === 'Entity' && name === 'id', cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'set' ? 'many-unique' : type.kind === 'list' ? 'many' : 'one', meaning: name, ontology_property: 'TEST-' + id.toUpperCase() + '#' + name}))
  }});
  record('money', 'Value Object', [['quantity', scalar()], ['note', optional(scalar('String'))]]);
  record('customer', 'Entity', [['id', scalar()], ['name', scalar('String')]]);
  node('choice', 'Enum', {description: 'Optional money choice.', values: ['None', 'Some'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'TEST-CHOICE',
    variants: [{name: 'None', ontology_variant: 'TEST-CHOICE#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-CHOICE#Some', payload: named('money')}]}});
  record('order', 'Entity', [['id', scalar()], ['customer', named('customer')], ['money', named('money')], ['choice', named('choice')], ['labels', list(scalar('String'))], ['lines', list(named('money'))]]);
  node('positive', 'Rule', {description: 'Explicit owned-value validation.', predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'TEST-POSITIVE',
    parameters: [{name: 'value', type: scalar()}], expression: {op: 'lt', left: {op: 'literal', type: 'UInt64', value: '0'}, right: {op: 'path', root: 'value', properties: []}}}});
  const type = options.type ?? named('order');
  const selection = structuredClone(base.selection);
  selection.factories = ['money', 'customer', 'order'].map(id => ({selector: 'commerce:' + id, base_validators: [{rule: 'commerce:positive', arguments: [{parameter: 'value', field: id === 'money' ? 'quantity' : 'id'}]}], extensions: []}));
  for (const op of selection.operations) {
    op.inputs = [{name: 'amount', type}]; op.result = {type, value: {op: 'path', root: 'amount', properties: []}};
    op.guards[0].arguments[0].value = {op: 'literal', type: 'UInt64', value: '1'};
  }
  const b = selection.workflows[0]; b.inputs = [{name: 'amount', type}]; b.result.type = type;
  if (options.expression) {
    let inputType: any = type, expr: any;
    if (options.expression === 'to_set') {inputType = list(type.element); expr = {op: 'to_set', value: {op: 'input', name: 'raw', properties: []}};}
    if (options.expression === 'projection') {inputType = list(named('order')); expr = {op: 'input', name: 'raw', properties: ['TEST-ORDER#id']};}
    if (options.expression === 'literal') expr = {op: 'literal', type: 'UInt64', value: '18446744073709551615'};
    if (options.expression === 'variant') expr = {op: 'variant', selector: 'TEST-CHOICE#None'};
    if (options.expression === 'to_set' || options.expression === 'projection') b.inputs.push({name: 'raw', type: inputType});
    b.steps[0].arguments[0].value = expr;
  }
  if (options.events) {
    for (const [id, generated] of [['posted', false], ['released', true]] as const) node(id, 'Event', {description: id, event_type: id, version: '1',
      occurrence_id: {field_id: 'event-id', type_ref: {kind: 'primitive', name: 'uuid'}, required: true}, occurred_at_policy: generated ? 'generated' : 'required',
      payload: [{field_id: 'order-id', type_ref: {kind: 'reference', selector: 'commerce:order'}, required: true},
        {field_id: 'delta', type_ref: {kind: 'primitive', name: 'integer'}, required: false}, {field_id: 'ratio', type_ref: {kind: 'primitive', name: 'decimal'}, required: false}]
    });
    for (const [i, op] of selection.operations.entries()) {
      const id = i ? 'undo' : 'perform', event = i ? 'released' : 'posted', n = read('specs/commerce/nodes/' + id + '.json');
      n.body.effects = ['notice']; write('specs/commerce/nodes/' + id + '.json', n);
      const edge_id = id + '-produces-' + event; manifest.edges.push(edge_id);
      write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship: 'produces', source_node_id: id, target_node_id: event, scope: 'feature'});
      op.events = [{slot: 'notice', target: 'commerce:' + event, parameter: 'notice_input'}];
    }
    b.event_inputs = [{name: 'post', event_ref: 'commerce:posted'}, {name: 'undo', event_ref: 'commerce:released'}];
    b.steps.forEach((s: any) => s.events = [{parameter: 'notice_input', input: 'post'}]);
    b.compensations.forEach((c: any) => c.events = [{parameter: 'notice_input', input: 'undo'}]);
  }
  write('specs/commerce/feature.json', manifest);
  const graph = loadCompiledProjectGraph(source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, graph_sha256: certificate.graph_sha256, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, graph_sha256: certificate.graph_sha256, contract_sha256: EXACT_FIELD_CONTRACT_SHA256,
    roots: ['commerce:choice', 'commerce:customer', 'commerce:money', 'commerce:order'], bindings: []}, getReconciledSource('field'));
  const actions = selection.operations.map((a: any) => compileOperationActionBindings(graph, boundary, fields, a, getReconciledSource('operation_action')));
  const {recovery, ...authored} = b;
  const bindings = {...authored, schema_version: WORKFLOW_BINDINGS_VERSION, steps: b.steps.map((s: any) => ({...s, action_sha256: actions[0]!.action_sha256})), compensations: b.compensations.map((s: any) => ({...s, action_sha256: actions[1]!.action_sha256}))};
  const workflow = compileWorkflowBindings(graph, boundary, fields, actions, bindings, getReconciledSource('workflow_binding'));
  const policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, ...recovery}, getReconciledSource('workflow_recovery'));
  return {...base, graph, workflow, policy, selection, nativePlan: () => selectReconciledArtifacts(planCompiledReconciledProject(graph, selection))};
}

export function nativeWorkflowValues(f: ReturnType<typeof workflowValuesFixture>, mutate?: (path: string, code: string) => string) {
  const native = nativeWorkflow(f, mutate), require = createRequire(import.meta.url);
  return {...native, material: require(path.join(native.root, 'js/domain/features/commerce/src/application/workflows/flow.material.js'))};
}

// Both Events reference the fixture's UInt64 order identity, not opaque text.
export const eventParameters = () => ({post: {occurrence: {'event-id': 'post-id'}, occurredAt: '2026-09-12', payload: {'order-id': '1', delta: '-9223372036854775808', ratio: 1.5}},
  undo: {occurrence: {'event-id': 'undo-id'}, payload: {'order-id': '1'}}});
