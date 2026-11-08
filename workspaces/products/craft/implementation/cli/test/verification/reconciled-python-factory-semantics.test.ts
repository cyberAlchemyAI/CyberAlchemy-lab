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
import {createFactorySemanticCases} from '../../src/verification/reconciled-factory-controls.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function fixture(t: any, impossible = false, count = 2) {
  const f = pythonAllTypesFixture(t), read = (file: string) => JSON.parse(fs.readFileSync(path.join(f.source, file), 'utf8'));
  const feature = read('specs/alpha/feature.json'), order = read('specs/alpha/nodes/order.json');
  const scalar = (name: string): any => ({kind: 'scalar', name}), wrap = (kind: string, element: any): any => ({kind, element}), named = (id: string): any => ({kind: 'named', selector: 'alpha:' + id});
  const variant = (name: string, payload: any): any => ({name, payload, ontology_variant: 'FIXTURE-BRANCH#' + name});
  const types = {flag: scalar('Bool'), class: wrap('optional', scalar('String')), lines: wrap('list', named('money')), tags: wrap('set', scalar('String')), authorization: named('answer'),
    choice: {kind: 'sum', variants: [variant('Empty', null), variant('Text', scalar('String'))]}};
  order.node_id = 'customer'; order.body.typed_contract.ontology_node = 'FIXTURE-CUSTOMER';
  for (const p of order.body.typed_contract.properties) p.ontology_property = 'FIXTURE-CUSTOMER#' + p.name;
  for (const [name, type] of Object.entries(types) as [string, any][]) {
    order.body.fields.push(name); order.body.typed_contract.properties.push({name, type, identity: false,
      cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: name, ontology_property: 'FIXTURE-CUSTOMER#' + name});
  }
  f.write('specs/alpha/nodes/customer.json', order); feature.nodes.push('customer');
  const binding = {...structuredClone(f.factories.find(b => b.selector === 'alpha:order')!), selector: 'alpha:customer'} as any;
  f.factories.push(binding);
  binding.base_validators.push({rule: 'alpha:amount-valid', arguments: [{parameter: 'amount', path: ['money', 'amount']}]});
  for (let i = 0; i < count; i++) {
    const id = 'extension-' + String.fromCharCode(97 + i), type = scalar(i === 0 ? 'UInt64' : 'Bool');
    feature.nodes.push(id);
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Rule', body: {description: id,
      predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-' + id.toUpperCase(), parameters: [{name: 'value', type}],
        expression: impossible && i === 0 ? {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: false}}
          : i === 0 ? {op: 'lt', left: {op: 'path', root: 'value', properties: []}, right: {op: 'literal', type: 'UInt64', value: '100'}}
          : {op: 'eq', left: {op: 'path', root: 'value', properties: []}, right: {op: 'literal', type: 'Bool', value: true}}}}});
    binding.extensions.push({id, validators: [{rule: 'alpha:' + id, arguments: [{parameter: 'value', ...(i === 0 ? {path: ['money', 'amount']} : {field: 'flag'})}]}]});
  }
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION,
    profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/lifecycle', layout_version: RESOLVED_ARTIFACT_LAYOUT,
    field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, plan};
}

test('native Python factory lifecycle retains shared requests and executes all extension orders with nested values', t => {
  const f = fixture(t), controls = createPythonSemanticControls(f.graph, f.plan), rows = controls.rows.filter((r: any) => r.adapter === 'python-factory') as any[];
  assert.equal(rows.length, 3);
  for (const row of rows) {
    const context = createPythonOwnedValueContext(row.selector, f.graph, f.plan, true), shared = createFactorySemanticCases(context, probe => probe.trace.validators);
    assert.deepEqual(row.cases.map((c: any) => ({id: c.id, mode: c.mode, format: c.format, values: c.values})), shared.cases.map(({id, mode, format, values}) => ({id, mode, format, values})), 'every shared request retained');
    for (let i = 0; i < shared.cases.length; i++) {
      const original = shared.cases[i]!.expected, native = row.cases[i].expected;
      if (original.kind === 'error') {assert.deepEqual(native, original); continue;}
      const a = JSON.parse(original.value), b = JSON.parse(native.value);
      assert.deepEqual({ok: b.ok, codes: b.failure_codes, trace: {...b.trace, validators: b.trace.validators.map(({rule, outcome}: any) => ({rule, outcome}))}, snapshot: b.snapshot},
        {ok: a.ok, codes: a.failure_codes, trace: a.trace, snapshot: a.snapshot ? {view: a.snapshot.view, key: a.snapshot.key, equals_baseline: a.snapshot.equals_baseline} : null});
    }
  }
  const order = rows.find(r => r.selector === 'alpha:customer'), requests = order.cases.map((c: any) => JSON.parse(c.values[0]));
  assert.deepEqual([...new Set(requests.map((r: any) => r.chain.join(',')))].sort(), ['', 'extension-a', 'extension-a,extension-b', 'extension-b', 'extension-b,extension-a']);
  assert.deepEqual([...new Set(requests.map((r: any) => r.route))].sort(), ['create', 'extend', 'reconstruct', 'transition']);
  for (const code of ['INVALID_FIELDS', 'INVALID_PREVIOUS', 'IDENTITY_CHANGED', 'RULE_FAIL:alpha:id-valid', 'RULE_FAIL:alpha:extension-a', 'RULE_FAIL:alpha:extension-b'])
    assert.ok(order.cases.some((c: any) => c.expected.kind === 'value' && JSON.parse(c.expected.value).failure_codes.includes(code)), 'case required:' + code);
  const before = fs.readdirSync(f.temp), report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 24, JSON.stringify(report.checks));
  for (const row of rows) assert.deepEqual(report.semantic_rows!.find(r => r.selector === row.selector), {selector: row.selector, kind: row.kind, result: 'pass', executed: true,
    case_count: row.cases.length, native_form: 'pass', binding_controls: 3, compiling_substitutions: 2});
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const root = path.join(f.temp, 'sensitivity');
  for (const artifact of f.plan.artifacts) {const file = path.join(root, artifact.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}
  const load = (name: string, source: string, bindings = '') => name + "={'__name__':'observer'" + bindings + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const program = 'import types\n' + load('operation', getReconciledSource('python_operation_observer')) + load('rule', getReconciledSource('python_rule_observer'), ", 'helper':types.SimpleNamespace(**operation)")
    + load('enumeration', getReconciledSource('python_enum_observer')) + load('observer', getReconciledSource('python_owned_observer'))
    + load('owned', getReconciledSource('python_owned_semantics')) + load('runner', getReconciledSource('python_factory_semantics'), ", 'owned':types.SimpleNamespace(**owned)") + String.raw`
import copy, dataclasses, importlib, json, sys
d=json.load(sys.stdin);sys.path.insert(0,d['root'])
observer['observe'](d,enumeration['observe'],rule['observe_rule'])
def preceding(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']], 'toolchain_files':{}}
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:customer')
module=importlib.import_module(row['module']['relative_path'][:-3].replace('/','.'))
component=getattr(module,row['module']['symbol'])
factory_type=type(getattr(module,row['module']['callable'])())
methods={name:getattr(factory_type,name) for name in ('create','reconstruct','transition','extend')}
rejected=[]
for mutation in ('reconstruct-route','transition-alias','extension-drop','key-collapse','false-view','false-trace'):
    changed=copy.deepcopy(d)
    if mutation=='reconstruct-route': factory_type.reconstruct=methods['create']
    elif mutation=='transition-alias':
        def alias(self,previous,input):
            result=methods['transition'](self,previous,input)
            return dataclasses.replace(result,value=previous) if result.ok else result
        factory_type.transition=alias
    elif mutation=='extension-drop': factory_type.extend=lambda self,name:self
    elif mutation=='key-collapse': setattr(module,row['module']['symbol'],dataclasses.replace(component,key=lambda value:'one-key'))
    else:
        target=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:customer')
        case=next(c for c in target['cases'] if c['expected']['kind']=='value' and json.loads(c['expected']['value'])['ok'])
        value=json.loads(case['expected']['value'])
        if mutation=='false-view': value['snapshot']['view']={'kind':'false'}
        else: value['trace']['validators'][0]['outcome']='fail'
        case['expected']['value']=json.dumps(value)
    try: runner['run'](changed,preceding,observer['observe'],enumeration['observe'],rule['observe_rule'])
    except ValueError as error:
        assert 'factory outcome:' in str(error),str(error)
        rejected.append(mutation)
    else: raise AssertionError('survived:'+mutation)
    finally:
        setattr(module,row['module']['symbol'],component)
        for name,method in methods.items(): setattr(factory_type,name,method)
print(json.dumps(rejected))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).length, 6);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 24, cases: controls.case_count, factory_cases: rows.reduce((n, r) => n + r.cases.length, 0), control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});

test('unsatisfied extensions and exhaustive chain capacity retain whole Python factory rows as unevaluable', t => {
  for (const [impossible, count] of [[true, 2], [false, 7]] as const) {
    const f = fixture(t, impossible, count), controls = createPythonSemanticControls(f.graph, f.plan), row = controls.rows.find(r => r.selector === 'alpha:customer')!;
    assert.equal(row.state, 'not_evaluable'); assert.equal('cases' in row, false);
    assert.match((row as any).reason, /no satisfying base factory witness|bounded factory extension chain capacity/);
    assert.equal(controls.rows.find(r => r.selector === 'alpha:money')!.state, 'ready');
    if (impossible) {
      const report = execute(f.graph, f.plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
      assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks.filter(c => c.result === 'fail')));
      assert.equal(report.result, 'not_evaluable');
      assert.deepEqual(report.semantic_rows!.find(r => r.selector === 'alpha:customer'), {selector: 'alpha:customer', kind: 'Entity', result: 'not_evaluable', executed: false});
      assert.equal(report.semantic_rows!.find(r => r.selector === 'alpha:money')!.result, 'pass');
    }
  }
});
