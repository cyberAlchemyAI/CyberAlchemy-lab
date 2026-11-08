import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, named} from '../helpers/workflow-values.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {createPythonWorkflowControls} from '../../src/verification/reconciled-python-workflow-controls.ts';

for (const kind of ['scalar', 'constrained', 'no-compensations', 'owned-events']) test('Python Workflow executes all source cases, occurrence failures and cancellation: ' + kind, t => {
  const f = kind === 'owned-events' ? workflowValuesFixture(t, {type: named('customer'), events: true}) : workflowFixture(t,
    kind === 'constrained' ? {dependencies: [[], ['undo-first'], ['undo-second']]} : kind === 'no-compensations' ? {noCompensations: true} : {});
  const s = f.selection, plan = planCompiledReconciledPythonProject(f.graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION,
    profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/workflow-app', layout_version: s.layout_version,
    field_bindings: s.field_bindings, factories: s.factories, operations: s.operations, workflows: s.workflows});
  const controls = createPythonSemanticControls(f.graph, plan), row = controls.rows.find(r => r.kind === 'Workflow') as any;
  assert.equal(row.state, 'ready', row.reason); assert.equal(row.adapter, 'python-workflow');
  assert.equal(row.cases.filter((c: any) => c.mode === 'workflow').length, kind === 'owned-events' ? 408 : 133);
  for (const step of row.workflow.steps) for (const phase of ['begin', 'commit']) assert.ok(row.cases.some((c: any) => c.id === 'native-cancel-' + step.step_id + '-' + phase));
  assert.equal(canonicalJson(row).includes('"artifacts"'), false);
  const before = fs.readdirSync(f.root), report = execute(f.graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.root});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.deepEqual(report.semantic_rows!.find(r => r.kind === 'Workflow'), {selector: row.selector, kind: 'Workflow', result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.deepEqual(fs.readdirSync(f.root), before);
  t.diagnostic(JSON.stringify({kind, nodes: controls.rows.length, passed_nodes: report.semantic_rows!.filter(r => r.result === 'pass').length,
    workflow_cases: row.cases.length, cases: controls.case_count, controls_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python Workflow effects preserve read identity, ordered writes, clocks and mutation sensitivity', t => {
  const f = workflowValuesFixture(t, {type: named('customer'), events: true}), source = path.join(f.root, 'source');
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(source, p), 'utf8'));
  const write = (p: string, v: unknown) => fs.writeFileSync(path.join(source, p), JSON.stringify(v));
  const s: any = structuredClone(f.selection), feature = read('specs/commerce/feature.json');
  for (const op of s.operations) {
    const id = op.selector.split(':')[1], p = 'specs/commerce/nodes/' + id + '.json', n = read(p);
    n.body.reads = ['current']; n.body.writes = ['first-write', 'second-write']; write(p, n);
    const edge_id = id + '-reads-customer'; feature.edges.push(edge_id);
    write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship: 'reads', source_node_id: id, target_node_id: 'customer', scope: 'feature'});
    if (id === 'perform') {
      const creates_id = id + '-creates-customer'; feature.edges.push(creates_id);
      write('specs/commerce/edges/' + creates_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id: creates_id, relationship: 'creates', source_node_id: id, target_node_id: 'customer', scope: 'feature'});
    }
    op.reads = [{slot: 'current', target: 'commerce:customer', parameter: 'current', key: {op: 'path', root: 'amount', properties: ['TEST-CUSTOMER#id']}}];
    op.writes = [{slot: 'first-write', target: 'commerce:customer', mode: 'replace', value: {op: 'path', root: 'current', properties: []}},
      {slot: 'second-write', target: 'commerce:customer', mode: id === 'perform' ? 'create' : 'replace', value: {op: 'path', root: 'amount', properties: []}}];
    op.result.value = {op: 'path', root: 'current', properties: []};
  }
  const event = read('specs/commerce/nodes/posted.json'); event.body.occurred_at_policy = 'generated'; write('specs/commerce/nodes/posted.json', event);
  // Four effect-heavy occurrences exceed the existing aggregate control budget.
  // Use a separate complete two-step suite; four-step repetition/recovery is
  // retained in the independent fixtures above, never trimmed at runtime.
  const flow = read('specs/commerce/nodes/flow.json');
  flow.body.typed_contract.steps = flow.body.typed_contract.steps.filter((r: any) => ['first', 'last'].includes(r.step_id));
  flow.body.typed_contract.compensations = flow.body.typed_contract.compensations.filter((r: any) => r.for_step === 'first');
  write('specs/commerce/nodes/flow.json', flow);
  s.workflows[0].steps = s.workflows[0].steps.filter((r: any) => ['first', 'last'].includes(r.step_id));
  s.workflows[0].steps[1].arguments[0].value.step_id = 'first';
  s.workflows[0].compensations = s.workflows[0].compensations.filter((r: any) => r.compensation_id === 'undo-first');
  write('specs/commerce/feature.json', feature);
  const graph = loadCompiledProjectGraph(source), plan = planCompiledReconciledPythonProject(graph, {
    schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/effect-app',
    layout_version: s.layout_version, field_bindings: s.field_bindings, factories: s.factories, operations: s.operations, workflows: s.workflows});
  const controls = createPythonSemanticControls(graph, plan), row = controls.rows.find(r => r.kind === 'Workflow') as any;
  assert.equal(row.state, 'ready', row.reason);
  for (const step of row.workflow.steps) for (const phase of ['begin', 'read', 'commit', 'rollback']) assert.ok(row.cases.some((c: any) => c.id === 'native-cancel-' + step.step_id + '-' + phase));
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.root});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.semantic_rows!.find(r => r.kind === 'Workflow')!.result, 'pass'); assert.equal(report.residue, null);
  const root = path.join(f.root, 'sensitivity');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('owned', getReconciledSource('python_owned_semantics'))
    + load('facts', getReconciledSource('python_state_machine_semantics'), ", 'owned':types.SimpleNamespace(**owned)")
    + load('operations', getReconciledSource('python_operation_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts)")
    + load('runner', getReconciledSource('python_workflow_semantics'), ", 'owned':types.SimpleNamespace(**owned), 'facts':types.SimpleNamespace(**facts), 'operations':types.SimpleNamespace(**operations)") + String.raw`
import asyncio,copy,dataclasses,importlib,json,sys
d=json.load(sys.stdin);sys.path.insert(0,d['root']);row=d['row']
native=importlib.import_module(row['module']['import_name']);call=getattr(native,row['module']['callable']);original=native._execute
material=importlib.import_module(row['module']['material_path'][:-3].replace('/','.'))
Fact=importlib.import_module(d['runtime'].replace('/','.')+'.facts')._Fact
selected={row['coverage'][key] for key in ('baseline','capture','settlement/last/rejected')}
cases=[c for c in row['cases'] if c['id'] in selected]
async def main():
    rejected=[]
    for mutation in ('wrong-value','late-capture','write-order','duplicate-commit','recovery-arguments','false-settlement'):
        originals={cls:cls.arguments for cls in {type(c) for c in material.compensations.values()}}
        async def altered(parameters, identity, dependencies):
            if mutation=='late-capture': await asyncio.sleep(0)
            if mutation in ('write-order','duplicate-commit'):
                for dependency in dependencies.values():
                    begin=dependency['store'].begin
                    async def wrapped_begin(begin=begin):
                        tx=await begin();commit=tx.commit
                        async def wrapped_commit(batch):
                            if mutation=='write-order': batch=dataclasses.replace(batch,writes=tuple(reversed(batch.writes)))
                            result=await commit(batch)
                            if mutation=='duplicate-commit': await commit(batch)
                            return result
                        tx.commit=wrapped_commit;return tx
                    dependency['store'].begin=wrapped_begin
            value=await original(parameters,identity,dependencies)
            if mutation=='wrong-value' and value.status=='succeeded': return dataclasses.replace(value,value=None)
            return value
        native._execute=altered
        if mutation=='recovery-arguments':
            for cls in originals: cls.arguments=lambda *args: types.MappingProxyType({})
        found=False
        try:
            for case in cases:
                expected=json.loads(case['expected']['value'])
                if mutation=='false-settlement': expected['settled_while_pending']=True
                try: observed=await runner['observe_case'](call,case,row,Fact)
                except Exception: found=True;break
                if observed!=expected: found=True;break
        finally:
            native._execute=original
            for cls,value in originals.items(): cls.arguments=value
        assert found, 'SURVIVED:'+mutation
        rejected.append(mutation)
    return rejected
print(json.dumps(asyncio.run(main())))
`;
  const launcher = "import io,json,sys\nd=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(d['request']))\nexec(compile(d['program'],'<workflow-sensitivity>','exec'))\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, row, runtime: controls.runtime_dir}}), encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 6);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, passed_nodes: report.semantic_rows!.filter(r => r.result === 'pass').length,
    workflow_cases: row.cases.length, cases: controls.case_count, control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Python Workflow capacity remains wholly pending without a passing case prefix', t => {
  const f = workflowFixture(t, {noCompensations: true}), file = path.join(f.root, 'source/specs/commerce/nodes/flow.json');
  const n = JSON.parse(fs.readFileSync(file, 'utf8')), s: any = structuredClone(f.selection);
  const ids = Array.from({length: 128}, (_, i) => 'step-' + i);
  n.body.typed_contract.steps = ids.map(step_id => ({step_id, operation_ref: 'commerce:perform'})); fs.writeFileSync(file, JSON.stringify(n));
  s.workflows[0].steps = ids.map((step_id, i) => ({step_id, arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: ids[i - 1], properties: []} : {op: 'input', name: 'amount', properties: []}}], events: []}));
  s.workflows[0].result.value.step_id = ids.at(-1);
  const graph = loadCompiledProjectGraph(path.join(f.root, 'source')), plan = planCompiledReconciledPythonProject(graph, {
    schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'bounded',
    layout_version: s.layout_version, field_bindings: s.field_bindings, factories: s.factories, operations: s.operations, workflows: s.workflows});
  const row = createPythonWorkflowControls(graph.nodes.find(n => n.kind === 'Workflow')!, graph, plan);
  assert.equal(row.state, 'not_evaluable'); assert.equal(Object.hasOwn(row, 'cases'), false);
  if (row.state !== 'not_evaluable') throw new Error('capacity did not reject');
  assert.match(row.reason, /8 MiB|capacity/); assert.equal(plan.node_selectors.length, 3);
});
