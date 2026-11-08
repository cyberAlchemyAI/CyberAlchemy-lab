import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

test('native Enums execute every source member including keyword escapes alongside record-bearing sums', t => {
  const f = pythonAllTypesFixture(t);
  const feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  for (const [id, names] of [['none', ['True', 'False', 'None', 'VariantTrue', 'Ready']], ['singleton', ['Only']]] as const) {
    feature.nodes.push(id);
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Enum', body: {description: id, values: names,
      typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(),
        variants: names.map(name => ({name, ontology_variant: 'FIXTURE-' + id.toUpperCase() + '#' + name, payload: null}))}}});
  }
  f.write('specs/alpha/feature.json', feature);
  const sum = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/answer.json'), 'utf8'));
  sum.body.values.push('Order');
  sum.body.typed_contract.variants.push({name: 'Order', ontology_variant: 'FIXTURE-ANSWER#Order', payload: {kind: 'named', selector: 'alpha:order'}});
  f.write('specs/alpha/nodes/answer.json', sum);
  const graph = loadCompiledProjectGraph(f.source);
  const plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/python', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  const controls = createPythonSemanticControls(graph, plan);
  const enums = controls.rows.filter(r => r.kind === 'Enum' && r.state === 'ready' && (r as any).adapter === 'python-plain-enum');
  assert.equal(enums.length, 4);
  for (const row of enums) {
    if (row.state !== 'ready') throw new Error('ready required');
    const contract = graph.nodes.find(n => n.selector === row.selector)!.body.typed_contract as any;
    assert.deepEqual(row.cases.filter(c => c.mode === 'member').map(c => c.values[0]), contract.variants.map((v: any) => v.name).sort());
  }
  assert.equal(controls.rows.find(r => r.selector === 'alpha:answer')!.state, 'ready');
  assert.equal(controls.rows.find(r => r.selector === 'alpha:order')!.state, 'ready', 'factory lifecycle has its own executor');
  const before = fs.readdirSync(f.temp), report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 23, JSON.stringify(report.checks));
  assert.ok(report.semantic_rows!.filter(r => r.kind === 'Enum' && r.result === 'pass').every(r => r.binding_controls === 3 && r.compiling_substitutions === 2));
  assert.deepEqual(fs.readdirSync(f.temp), before);

  // One bounded interpreter probes compiling corruptions and false source
  // expectations. No copies per mutant and no altered emitted runtime retained.
  const root = path.join(f.temp, 'enum-mutations');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string) => name + "={'__name__':'observer'}\nexec(" + JSON.stringify(source) + ',' + name + ')\n';
  const script = load('observer', getReconciledSource('python_enum_observer')) + load('runner', getReconciledSource('python_enum_semantics')) + String.raw`
import ast, copy, hashlib, json, pathlib, sys
d=json.load(sys.stdin)
root=pathlib.Path(d['root'])
sys.path.insert(0,str(root))
row=next(r for r in d['controls']['rows'] if r['selector']=='alpha:none')
m=row['module']
source=(root/m['relative_path']).read_bytes()
observer['observe'](root,m,row['contract'])
mutations=['parse','emit','member-id','error-detail','error-code','alias','extra-effect','str-mixin']
for mutation in mutations:
    tree=ast.parse(source)
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    classes={n.name:n for n in tree.body if isinstance(n,ast.ClassDef)}
    if mutation in ('parse','emit','member-id'):
        name={'parse':'parse_none','emit':'emit_none','member-id':'none_member_id'}[mutation]
        next(n for n in ast.walk(functions[name]) if isinstance(n,ast.Return)).value=ast.Constant(value=None)
    elif mutation=='error-detail':
        fn=next(n for n in classes['_EnumWireError'].body if isinstance(n,ast.FunctionDef) and n.name=='as_dict')
        fn.body=[ast.Return(value=ast.Dict(keys=[],values=[]))]
    elif mutation=='error-code': classes['_EnumMemberError'].body[0].value=ast.Constant(value='WRONG')
    elif mutation=='alias': classes[m['symbol']].body[1].value=copy.deepcopy(classes[m['symbol']].body[0].value)
    elif mutation=='str-mixin': classes[m['symbol']].bases.insert(0,ast.Name(id='str',ctx=ast.Load()))
    else: tree.body.append(ast.Pass())
    ast.fix_missing_locations(tree)
    mutant=ast.unparse(tree).encode()
    compile(mutant,m['relative_path'],'exec',dont_inherit=True)
    try: observer['observe'](root,m,row['contract'],mutant)
    except ValueError as e: assert 'Enum semantics/effects' in str(e)
    else: raise AssertionError('survived:'+mutation)
def predecessor(value):
    return {'rows':[{'selector':r['selector'],'kind':r['kind'],'result':'not_evaluable','executed':False} for r in value['controls']['rows']],
            'toolchain_files':{},'controls_sha256':value['controls']['controls_sha256']}
changed=copy.deepcopy(d)
for r in changed['controls']['rows']:
    if r.get('adapter') in ('python-sum','python-factory'): r['state']='not_evaluable'
bad=next(r for r in changed['controls']['rows'] if r['selector']=='alpha:none')
bad['cases'][0]['expected']['value']='{}'
try: runner['run'](changed,predecessor,observer['observe'])
except ValueError as e: assert 'outcome:alpha:none:case-0' in str(e)
else: raise AssertionError('false expected outcome accepted')
print(json.dumps({'compiling_mutations_rejected':len(mutations),'false_outcome_rejected':True}))
`;
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', script], {input: JSON.stringify({root, controls}), encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024});
  assert.equal(result.status, 0, result.stderr); assert.deepEqual(JSON.parse(result.stdout), {compiling_mutations_rejected: 8, false_outcome_rejected: true});
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, executed: 23, enum_cases: enums.reduce((n, r) => n + (r.state === 'ready' ? r.cases.length : 0), 0), control_bytes: Buffer.byteLength(canonicalJson(controls))}));
});
