import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getPythonEventVerificationContext, planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createEventSemanticCases} from '../../src/verification/reconciled-event-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t), feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  const field = (field_id: string, name: string, required = true) => ({field_id, type_ref: {kind: 'primitive', name}, required});
  const ref = (field_id: string, selector: string) => ({field_id, type_ref: {kind: 'reference', selector}, required: true});
  for (const [id, policy] of [['delivered', 'required'], ['clocked', 'generated'], ['empty', 'required']]) {
    feature.nodes.push(id);
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Event', body: {
      description: 'Occurrence β😀; lone surrogate \ud800', event_type: id, version: '2', occurred_at_policy: policy,
      occurrence_id: field('occurrence-id', id === 'empty' ? 'integer' : 'uuid'),
      payload: id === 'empty' ? [] : [field('amount', 'integer'), field('ratio', 'decimal'), field('enabled', 'boolean'), field('label', 'string'), field('at', 'timestamp'), field('uid', 'uuid'), field('class', 'string', false),
        ref('entity', 'alpha:order'), ref('value', 'alpha:money'), ref('mode', 'alpha:mode'), ref('previous', 'alpha:clocked')]}});
  }
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION,
    profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/event-app', layout_version: RESOLVED_ARTIFACT_LAYOUT,
    field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, plan};
}

test('native Events preserve all shared cases, explicit clocks, exact carriers, optional absence and shared reference types', t => {
  const f = fixture(t), controls = createPythonSemanticControls(f.graph, f.plan), rows = controls.rows.filter((r: any) => r.adapter === 'python-event') as any[];
  assert.equal(rows.length, 4);
  assert.equal(getPythonEventVerificationContext(f.plan).length, 4);
  assert.throws(() => getPythonEventVerificationContext(structuredClone(f.plan)), /registered/);
  assert.equal(canonicalJson(getPythonEventVerificationContext(f.plan)).includes('"artifacts"'), false);
  for (const row of rows) {
    const referenceScalars = new Map(row.module.reference_imports.map((reference: any) => [reference.selector, reference.identity.scalar]));
    const shared = createEventSemanticCases(f.graph.nodes.find(n => n.selector === row.selector)!, row.cases[0], referenceScalars);
    assert.equal(shared.state, 'ready');
    assert.deepEqual(row.cases.filter((c: any) => c.mode !== 'event-native-carrier'), (shared as any).cases, 'every source case retained:' + row.selector);
  }
  assert.equal(rows.reduce((n, r) => n + r.cases.filter((c: any) => c.mode === 'event-native-carrier').length, 0), 16);
  const before = fs.readdirSync(f.temp), report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 24, JSON.stringify(report.checks.filter(c => c.result === 'fail')));
  for (const row of rows) assert.deepEqual(report.semantic_rows!.find(r => r.selector === row.selector), {selector: row.selector, kind: 'Event', result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const root = path.join(f.temp, 'sensitivity');
  for (const a of f.plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('observer', getReconciledSource('python_event_observer')) + load('owned', getReconciledSource('python_owned_semantics'))
    + load('runner', getReconciledSource('python_event_semantics'), ", 'owned':types.SimpleNamespace(**owned)") + String.raw`
import copy, dataclasses, importlib, json, sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:clocked')
module=importlib.import_module(row['module']['import_name']);original=module._make
rejected=[]
for mutation in ('clock-twice','ignore-clock','mutable-fields','input-mutation','false-view','false-reference'):
    changed=copy.deepcopy(d)
    if mutation=='clock-twice':
        def twice(input,clock): clock(); return original(input,clock)
        module._make=twice
    elif mutation=='ignore-clock': module._make=lambda input,clock: original(input,lambda:'ignored')
    elif mutation=='mutable-fields':
        def mutable(input,clock):
            result=original(input,clock)
            return dataclasses.replace(result,payload=dict(result.payload))
        module._make=mutable
    elif mutation=='input-mutation':
        def mutated(input,clock):
            result=original(input,clock);input['__changed__']=True;return result
        module._make=mutated
    elif mutation=='false-view':
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:clocked')
        case=next(c for c in target['cases'] if c['mode']=='event')
        value=json.loads(case['expected']['value']);value['result']['values'][0]['version']='false'
        case['expected']['value']=json.dumps(value)
    else:
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:clocked')
        target['references']['alpha:clocked']['body']['description']='false'
    try: runner['run'](changed,preceding,observer['observe'])
    except ValueError as error:
        assert any(s in str(error) for s in ('outcome:','immutable Event fields','Event mutation/coercion/await','reference meaning')),str(error)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally: module._make=original
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 6);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 24, cases: controls.case_count, event_cases: rows.reduce((n, r) => n + r.cases.length, 0), control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('Event case capacity leaves a whole explicit pending row instead of retaining a passing prefix', () => {
  const field = (field_id: string) => ({field_id, required: true, type_ref: {kind: 'primitive', name: 'integer'}});
  const node: any = {selector: 'alpha:large', kind: 'Event', body: {event_type: 'large', version: '1', occurrence_id: field('id'), occurred_at_policy: 'generated', payload: Array.from({length: 100}, (_, i) => field('field-' + i))}};
  const row = createEventSemanticCases(node, {id: 'case-0', mode: 'event-descriptor', format: 'string', values: [], expected: {kind: 'value', value: '{}'}});
  assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false); assert.match((row as any).reason, /bounded Event .*capacity/);
});
