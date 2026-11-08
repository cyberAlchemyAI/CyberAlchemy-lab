import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test, {type TestContext} from 'node:test';
import {workflowValuesFixture, eventParameters, scalar} from '../helpers/workflow-values.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileOperationActionBindings} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {renderWorkflowMaterialization} from '../../src/generation/workflow-materialization-source.ts';
import {planPythonWorkflowMaterialization} from '../../src/generation/python-workflow-materialization.ts';
import {createWorkflowValueReference} from '../../src/verification/reconciled-workflow-value-reference.ts';
import {workflowVerificationDefinitions} from '../../src/verification/reconciled-workflow-controls.ts';

// Event-only Entity references intentionally have no selected field model.
// Runtime compiler/image qualification is separate from these source controls.
export function eventOnlyFixture(t: TestContext, identity: 'String'|'UInt64' = 'UInt64', mixed = false) {
  const f = workflowValuesFixture(t, {type: scalar(), events: true}), source = path.join(f.root, 'source');
  const edit = (id: string, change: (body: any) => void) => {
    const file = path.join(source, 'specs/commerce/nodes', id + '.json');
    const node = JSON.parse(fs.readFileSync(file, 'utf8')); change(node.body);
    fs.writeFileSync(file, JSON.stringify(node) + '\n');
  };
  edit('order', body => {body.typed_contract.properties.find((p: any) => p.identity).type.name = identity;});
  if (mixed) {
    edit('customer', body => {body.typed_contract.properties.find((p: any) => p.identity).type.name = 'String';});
    for (const id of ['posted', 'released']) edit(id, body => {
      body.payload.push({field_id: 'customer-id', type_ref: {kind: 'reference', selector: 'commerce:customer'}, required: false});
    });
  }
  const graph = loadCompiledProjectGraph(source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION,
    graph_sha256: certificate.graph_sha256, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256}, getReconciledSource('composition'));
  const actions = f.selection.operations.map((a: any) => compileOperationActionBindings(graph, boundary, null, a, getReconciledSource('operation_action')));
  const {recovery: _recovery, ...authored} = f.selection.workflows[0];
  const bindings = {...authored, schema_version: WORKFLOW_BINDINGS_VERSION,
    steps: authored.steps.map((s: any) => ({...s, action_sha256: actions[0]!.action_sha256})),
    compensations: authored.compensations.map((s: any) => ({...s, action_sha256: actions[1]!.action_sha256}))};
  const workflow = compileWorkflowBindings(graph, boundary, null, actions, bindings, getReconciledSource('workflow_binding'));
  return {graph, workflow, root: f.root};
}
const contract = () => getReconciledSource('workflow_materialization');
const render = (f: ReturnType<typeof eventOnlyFixture>) => renderWorkflowMaterialization(f.graph, f.workflow, null, contract());
const python = (f: ReturnType<typeof eventOnlyFixture>) => planPythonWorkflowMaterialization(f.graph, f.workflow, null, contract(), 'application');

test('Event-only UInt64 references use graph identity without selected fields in both materializers', t => {
  const f = eventOnlyFixture(t), ts = render(f).content, py = python(f);
  assert.match(ts, /eventUInt64\(p\["order-id"\]/);
  assert.match(ts, /EventRef<"commerce:order",bigint>/);
  assert.match(ts, /"order-id":bigint\|number\|string/);
  assert.ok(py.artifacts.some(a => a.relative_path.endsWith('/event_references/commerce/order.py') && a.content.includes(', int)')));
  assert.ok(py.artifacts.find(a => a.relative_path === py.relative_path)!.content.includes('_event_ref_uint64(p["order-id"])'));
});
test('String and mixed Event identity maps preserve matching brands and scalar modules', t => {
  const legacy = eventOnlyFixture(t, 'String'), ts = render(legacy).content, py = python(legacy);
  assert.match(ts, /EventRef<"commerce:order">/); assert.doesNotMatch(ts, /const eventUInt64/);
  assert.ok(py.artifacts.some(a => a.relative_path.endsWith('/event_references/commerce/order.py') && a.content.includes(', str)')));
  const mixed = eventOnlyFixture(t, 'UInt64', true), source = render(mixed).content;
  assert.match(source, /EventRef<"commerce:order",bigint>/); assert.match(source, /EventRef<"commerce:customer",string>/);
  assert.ok(python(mixed).artifacts.some(a => a.relative_path.endsWith('/event_references/commerce/customer.py') && a.content.includes(', str)')));
});
test('Materializers reject unregistered and different valid graph identities', t => {
  const f = eventOnlyFixture(t), other = eventOnlyFixture(t, 'String');
  for (const graph of [{...f.graph}, other.graph]) {
    assert.throws(() => renderWorkflowMaterialization(graph, f.workflow, null, contract()));
    assert.throws(() => planPythonWorkflowMaterialization(graph, f.workflow, null, contract(), 'application'));
  }
});
test('Independent Event numeric reference accepts exact carriers and rejects whole-string violations', t => {
  const f = eventOnlyFixture(t), ref = createWorkflowValueReference(f.graph, f.workflow, workflowVerificationDefinitions().values);
  const raw = () => ({amount: '3', ...eventParameters()});
  for (const value of [0n, 1, '18446744073709551615']) {
    const p = raw(); p.post.payload['order-id'] = value as any;
    assert.equal(ref.capture(p).post.payload['order-id'], BigInt(value));
  }
  for (const event of ['post', 'undo'] as const) for (const value of ['o', '', '01', '-1', '1\n', '1\r', '1\r\n', '1\u2028', '1\u2029', '18446744073709551616', '0'.repeat(21), 9007199254740992, true]) {
    const p = raw(); p[event].payload['order-id'] = value as any; assert.throws(() => ref.capture(p), TypeError);
  }
  for (const value of ['-9223372036854775808', '9223372036854775807']) {
    const p = raw(); p.post.payload.delta = value; assert.equal(ref.capture(p).post.payload.delta, BigInt(value));
  }
  for (const value of ['-1\n', '1\r\n', '-1\u2028', '0'.repeat(21), '-9223372036854775809', '9223372036854775808']) {
    const p = raw(); p.post.payload.delta = value; assert.throws(() => ref.capture(p), TypeError);
  }
  assert.equal(ref.capture(raw()).post.payload['order-id'], 1n);
});
