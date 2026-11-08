import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createPythonOwnedValueContext} from '../../src/verification/reconciled-python-value-context.ts';
import {createSumSemanticCases} from '../../src/verification/reconciled-sum-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function fixture(t: any, unsatisfied = false) {
  const f = pythonAllTypesFixture(t), feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  const scalar = (name: string): any => ({kind: 'scalar', name}), named = (id: string): any => ({kind: 'named', selector: 'alpha:' + id}), wrap = (kind: string, element: any): any => ({kind, element});
  const variants = (values: [string, any][]) => values.map(([name, payload]) => ({name, payload, ontology_variant: 'FIXTURE-SUM#' + name}));
  const sum = (id: string, values: [string, any][]) => {
    feature.nodes.push(id); f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Enum', body: {description: id, values: values.map(v => v[0]),
      typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), variants: variants(values)}}});
  };
  sum('detail', [['Text', scalar('String')], ['Flag', scalar('Bool')], ['Maybe', wrap('optional', scalar('String'))], ['List', wrap('list', scalar('UInt64'))], ['Set', wrap('set', scalar('UInt64'))],
    ['Inline', {kind: 'sum', variants: variants([['Absent', null], ['Present', wrap('optional', scalar('Bool'))]])}], ['None', null]]);
  sum('bundle', [['Order', named('order')], ['Money', named('money')], ['Amounts', wrap('list', named('answer'))], ['UniqueAmounts', wrap('set', named('answer'))],
    ['Maybe', wrap('optional', named('answer'))], ['Mode', named('mode')], ['Tags', wrap('set', scalar('String'))], ['None', null]]);
  f.write('specs/alpha/feature.json', feature);
  if (unsatisfied) {
    const node = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/id-valid.json'), 'utf8'));
    node.body.typed_contract.expression = {op: 'eq', left: {op: 'literal', type: 'String', value: 'a'}, right: {op: 'literal', type: 'String', value: 'b'}};
    f.write('specs/alpha/nodes/id-valid.json', node);
  }
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE,
    language: 'python', module_root: 'relocated/sum-app', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, plan};
}

test('Python payload sums preserve shared source cases and execute nested owned values plus every factory witness probe', t => {
  const f = fixture(t), controls = createPythonSemanticControls(f.graph, f.plan);
  const rows = controls.rows.filter((r: any) => r.adapter === 'python-sum') as any[];
  assert.equal(rows.length, 3);
  for (const row of rows) {
    const context = createPythonOwnedValueContext(row.selector, f.graph, f.plan), shared = createSumSemanticCases(context);
    const sumCases = row.cases.filter((c: any) => c.mode === 'sum');
    assert.deepEqual(sumCases.map(({native_error, ...c}: any) => c), shared.cases, 'all shared cases retained:' + row.selector);
    assert.deepEqual([...new Set(sumCases.filter((c: any) => c.expected.kind === 'value').map((c: any) => JSON.parse(c.values[0]).variant))].sort(), row.contract.variants.map((v: any) => v.name).sort());
    const probes = Object.values(context.dependencies).flatMap((d: any) => d.kind === 'Enum' ? [] : d.probes);
    assert.deepEqual(row.cases.filter((c: any) => c.mode === 'record-probe').map((c: any) => ({recipe: JSON.parse(c.values[0]), expected: JSON.parse(c.expected.value)})), probes);
  }
  const bundle = rows.find(r => r.selector === 'alpha:bundle');
  assert.ok(bundle.cases.some((c: any) => c.mode === 'record-probe' && !JSON.parse(c.expected.value).ok), 'Rule failure witness included');
  assert.ok(bundle.cases.some((c: any) => c.expected.kind === 'error' && c.native_error === 'UNOWNED_COMPONENT'));
  assert.ok(rows.some(r => r.cases.some((c: any) => c.native_error === 'INVALID_BOOL')));
  assert.ok(rows.some(r => r.cases.some((c: any) => c.native_error === 'INVALID_STRING')));
  const before = fs.readdirSync(f.temp), report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 23, JSON.stringify(report.checks));
  for (const row of rows) assert.deepEqual(report.semantic_rows!.find(r => r.selector === row.selector), {selector: row.selector, kind: 'Enum', result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.equal(report.semantic_rows!.find(r => r.selector === 'alpha:order')!.result, 'pass', 'factory lifecycle executed independently');
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const root = path.join(f.temp, 'sum-sensitivity');
  for (const a of f.plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, binding = '') => name + "={'__name__':'observer'" + binding + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const script = 'import types\n' + load('operation', getReconciledSource('python_operation_observer')) + load('rule', getReconciledSource('python_rule_observer'), ", 'helper':types.SimpleNamespace(**operation)")
    + load('enumeration', getReconciledSource('python_enum_observer')) + load('owned', getReconciledSource('python_owned_observer')) + load('runner', getReconciledSource('python_owned_semantics')) + String.raw`
import copy, dataclasses, importlib, json, sys
d=json.load(sys.stdin)
sys.path.insert(0,d['root'])
owned['observe'](d,enumeration['observe'],rule['observe_rule'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:detail')
module=importlib.import_module(row['module']['relative_path'][:-3].replace('/','.'))
original_component=getattr(module,row['module']['symbol'])
original_call=getattr(module,row['module']['callable'])
rejected=[]
for mutation in ('key-collapse','ownership','wrong-output','input-mutation','false-view','false-record-probe'):
    changed=copy.deepcopy(d)
    if mutation=='key-collapse': setattr(module,row['module']['symbol'],dataclasses.replace(original_component,key=lambda v:'one-key'))
    elif mutation=='ownership': setattr(module,row['module']['symbol'],dataclasses.replace(original_component,is_owned=lambda v:True))
    elif mutation=='wrong-output': setattr(module,row['module']['callable'],lambda v:None)
    elif mutation=='input-mutation':
        def changed_call(v):
            result=original_call(v)
            v['extra']=True
            return result
        setattr(module,row['module']['callable'],changed_call)
    elif mutation=='false-view':
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:detail')
        case=next(c for c in target['cases'] if c['expected']['kind']=='value')
        value=json.loads(case['expected']['value']);value['view']={'kind':'false'}
        case['expected']['value']=json.dumps(value)
    else:
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:bundle')
        case=next(c for c in target['cases'] if c['mode']=='record-probe')
        value=json.loads(case['expected']['value']);value['ok']=not value['ok']
        case['expected']['value']=json.dumps(value)
    try: runner['run'](changed,preceding,owned['observe'],enumeration['observe'],rule['observe_rule'])
    except ValueError as e:
        assert any(s in str(e) for s in ('outcome:','input mutation/coercion')),str(e)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally:
        setattr(module,row['module']['symbol'],original_component)
        setattr(module,row['module']['callable'],original_call)
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program: script, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 6);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 23, cases: controls.case_count, sum_cases: rows.reduce((n, r) => n + r.cases.filter((c: any) => c.mode === 'sum').length, 0),
    record_probes: rows.reduce((n, r) => n + r.cases.filter((c: any) => c.mode === 'record-probe').length, 0), control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('a sum with an unsatisfied record factory remains wholly unevaluable rather than passing its empty variant', t => {
  const f = fixture(t, true), controls = createPythonSemanticControls(f.graph, f.plan);
  const row = controls.rows.find(r => r.selector === 'alpha:bundle')!;
  assert.equal(row.state, 'not_evaluable'); assert.match((row as any).reason, /no satisfying base factory witness/);
  assert.equal('cases' in row, false);
  const report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable');
  assert.deepEqual(report.semantic_rows!.find(r => r.selector === 'alpha:bundle'), {selector: 'alpha:bundle', kind: 'Enum', result: 'not_evaluable', executed: false});
  assert.equal(report.semantic_rows!.find(r => r.selector === 'alpha:detail')!.result, 'pass', JSON.stringify(report.checks));
});
