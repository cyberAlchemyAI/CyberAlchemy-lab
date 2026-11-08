import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getPythonStateMachineVerificationContext, planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createStateMachineSemanticCases} from '../../src/verification/reconciled-state-machine-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

const scalar = (name: string): any => ({kind: 'scalar', name});
const at = (root: string, ...properties: string[]): any => ({op: 'path', root, properties});
function fixture(t: any) {
  const f = pythonAllTypesFixture(t), feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  const read = (id: string) => JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/' + id + '.json'), 'utf8'));
  const node = (id: string, kind: string, body: any) => {
    if (!feature.nodes.includes(id)) feature.nodes.push(id);
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});
  };
  const edge = (id: string, from: string, to: string) => {
    feature.edges.push(id);
    f.write('specs/alpha/edges/' + id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: id, relationship: 'transitions', source_node_id: from, target_node_id: to, scope: 'feature'});
  };
  node('requested', 'Event', {...read('posted').body, event_type: 'requested', description: 'β😀 Unicode and lone surrogate \ud800'});
  const c = read('lifecycle').body.typed_contract;
  c.states.push('closed');
  c.transitions[0].output_intents = [{slot: 'primary', event_ref: 'alpha:requested'}, {slot: 'audit', event_ref: 'alpha:requested'}];
  c.transitions.push({transition_id: 'close', source_state: 'posted', target_state: 'closed', trigger_event_ref: 'alpha:requested', guard: null, output_intents: []},
    {transition_id: 'repeat', source_state: 'closed', target_state: 'closed', trigger_event_ref: 'alpha:posted', guard: null, output_intents: []});
  node('lifecycle', 'State Machine', {typed_contract: c}); edge('requested-transitions', 'requested', 'lifecycle');
  const guardless = {...c, ontology_state_machine: 'FIXTURE-GUARDLESS', inputs: [], transitions: c.transitions.map((r: any) => ({...r, guard: null}))};
  node('guardless', 'State Machine', {typed_contract: guardless});
  edge('requested-guardless', 'requested', 'guardless'); edge('posted-guardless', 'posted', 'guardless');
  const money = {kind: 'named', selector: 'alpha:money'};
  node('threshold', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {
    schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-THRESHOLD', parameters: [{name: 'current', type: money}],
    expression: {op: 'lt', left: {op: 'literal', type: 'UInt64', value: '9'}, right: at('current', 'FIXTURE-MONEY#amount')}}});
  node('forward', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {
    schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-FORWARD', parameters: [{name: 'current', type: money}],
    expression: {op: 'rule_ref', selector: 'alpha:threshold', arguments: [{parameter: 'current', value: at('current')}]}}});
  const structured = {...c, ontology_state_machine: 'FIXTURE-STRUCTURED', states: ['draft', 'posted'],
    inputs: [{name: 'money', type: money}, {name: 'note', type: {kind: 'optional', element: scalar('String')}},
      {name: 'history', type: {kind: 'list', element: scalar('UInt64')}}, {name: 'tags', type: {kind: 'set', element: scalar('String')}},
      {name: 'choice', type: {kind: 'named', selector: 'alpha:answer'}}],
    transitions: [{...c.transitions[0], guard: {selector: 'alpha:forward', arguments: [{parameter: 'current', value: at('money')}]}}]};
  node('structured', 'State Machine', {typed_contract: structured}); edge('posted-structured', 'posted', 'structured');
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION,
    profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/state-machine-app', layout_version: RESOLVED_ARTIFACT_LAYOUT,
    field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, plan};
}

test('native State Machines preserve complete source matrices, structured guards, nominal roles and ordered unexecuted intents', t => {
  const f = fixture(t), controls = createPythonSemanticControls(f.graph, f.plan), rows = controls.rows.filter((r: any) => r.adapter === 'python-state-machine') as any[];
  assert.equal(rows.length, 3, JSON.stringify(controls.rows.filter(r => r.kind === 'State Machine')));
  assert.equal(getPythonStateMachineVerificationContext(f.plan).length, 3);
  assert.throws(() => getPythonStateMachineVerificationContext(structuredClone(f.plan)), /registered/);
  assert.equal(canonicalJson(getPythonStateMachineVerificationContext(f.plan)).includes('"artifacts"'), false);
  for (const row of rows) {
    const shared = createStateMachineSemanticCases(f.graph.nodes.find(n => n.selector === row.selector)!, f.graph);
    assert.equal(shared.state, 'ready');
    assert.deepEqual(row.cases, (shared as any).cases, 'all source cases retained');
    assert.deepEqual(row.recipes, (shared as any).recipes, 'all source recipes retained');
  }
  const lifecycle = rows.find(r => r.selector === 'alpha:lifecycle');
  assert.equal(lifecycle.declared_pair_count, 6);
  assert.deepEqual(lifecycle.source_predicted_transitions, ['close', 'post', 'repeat']);
  const outcomes = lifecycle.cases.filter((c: any) => c.mode === 'state-machine' && c.expected.kind === 'value').map((c: any) => JSON.parse(c.expected.value));
  assert.ok(outcomes.some((o: any) => o.reason === 'guard')); assert.ok(outcomes.some((o: any) => o.reason === 'no-transition'));
  assert.ok(outcomes.some((o: any) => canonicalJson(o.output_intents) === canonicalJson([{slot: 'primary', event_ref: 'alpha:requested'}, {slot: 'audit', event_ref: 'alpha:requested'}])));
  const before = fs.readdirSync(f.temp), report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 26, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  for (const row of rows) assert.deepEqual(report.semantic_rows!.find(r => r.selector === row.selector), {selector: row.selector, kind: 'State Machine', result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const root = path.join(f.temp, 'sensitivity');
  for (const a of f.plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('helper', getReconciledSource('python_operation_observer'))
    + load('observer', getReconciledSource('python_state_machine_observer'), ", 'helper':types.SimpleNamespace(**helper)")
    + load('owned', getReconciledSource('python_owned_semantics'))
    + load('runner', getReconciledSource('python_state_machine_semantics'), ", 'owned':types.SimpleNamespace(**owned)") + String.raw`
import copy,dataclasses,importlib,json,sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
def forbidden(*args,**kwargs): raise AssertionError('EVENT_EXECUTED_BY_STATE_MACHINE')
for r in d['controls']['rows']:
    if r['kind']=='Event': importlib.import_module(r['module']['import_name'])._make=forbidden
runner['run'](d,preceding,observer['observe'])
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:lifecycle')
module=importlib.import_module(row['module']['import_name']);original=module._reduce
rejected=[]
for mutation in ('target','guard','intent-order','mutable-intents','input-mutation','false-outcome','false-event'):
    changed=copy.deepcopy(d)
    if mutation=='target':
        module._reduce=lambda s,t,p: dataclasses.replace(original(s,t,p),state=module.initial_state)
    elif mutation=='guard':
        module._reduce=lambda s,t,p: original(s,t,dict(p,value=True))
    elif mutation=='intent-order':
        module._reduce=lambda s,t,p: dataclasses.replace(original(s,t,p),output_intents=tuple(reversed(original(s,t,p).output_intents)))
    elif mutation=='mutable-intents':
        module._reduce=lambda s,t,p: dataclasses.replace(original(s,t,p),output_intents=list(original(s,t,p).output_intents))
    elif mutation=='input-mutation':
        def mutate(s,t,p):
            result=original(s,t,p);p['changed']=True;return result
        module._reduce=mutate
    elif mutation=='false-outcome':
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:lifecycle')
        target['cases'][0]['expected']['value']='closed'
    else:
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:lifecycle')
        target['events']['alpha:requested']['body']['description']='false'
    try: runner['run'](changed,preceding,observer['observe'])
    except ValueError as error:
        assert any(s in str(error) for s in ('outcome:','immutable output intents','input mutation/coercion','initial outcome','Event body binding')),str(error)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally: module._reduce=original
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 7);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 26, cases: controls.case_count, state_machine_cases: rows.reduce((n, r) => n + r.cases.length, 0), control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('State Machine case capacity remains a whole pending node', t => {
  const f = pythonAllTypesFixture(t), file = 'specs/alpha/nodes/lifecycle.json', source = JSON.parse(fs.readFileSync(path.join(f.source, file), 'utf8'));
  source.body.typed_contract.inputs.push(...Array.from({length: 127}, (_, i) => ({name: 'amount_' + i, type: scalar('UInt64')})));
  f.write(file, source);
  const graph = loadCompiledProjectGraph(f.source), row = createStateMachineSemanticCases(graph.nodes.find(n => n.selector === 'alpha:lifecycle')!, graph);
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false); assert.match((row as any).reason, /bounded State Machine/);
});
