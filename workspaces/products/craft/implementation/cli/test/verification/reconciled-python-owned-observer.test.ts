import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledPythonProject, getPythonDataVerificationContext, getPythonDecisionVerificationContext, getPythonFactoryVerificationContext} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

test('owned observer covers nested types, references, validator paths and extensions and rejects independent compiling corruption', t => {
  const f = pythonAllTypesFixture(t), featureFile = 'specs/alpha/feature.json';
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(f.source, p), 'utf8'));
  const feature = read(featureFile);
  const scalar = (name = 'String'): any => ({kind: 'scalar', name}), named = (id: string): any => ({kind: 'named', selector: 'alpha:' + id});
  const wrap = (kind: string, element: any): any => ({kind, element});
  const variant = (name: string, payload: any = null): any => ({name, payload, ontology_variant: 'FIXTURE-OWNED#' + name});
  const choice: any = {kind: 'sum', variants: [variant('Text', wrap('list', {kind: 'sum', variants: [variant('Words', scalar()), variant('Flag', scalar('Bool'))]})), variant('Empty')]};
  const answer = read('specs/alpha/nodes/answer.json');
  answer.body.values.push('Money'); answer.body.typed_contract.variants.push(variant('Money', named('money')));
  f.write('specs/alpha/nodes/answer.json', answer);
  const order = read('specs/alpha/nodes/order.json');
  for (const [name, type] of Object.entries({lines: wrap('list', named('money')), tags: wrap('set', scalar()), modes: wrap('list', named('mode')), choice,
    authorization: named('answer'), class: wrap('optional', scalar()), peer: wrap('optional', scalar()), peers: wrap('list', scalar()), members: wrap('set', scalar()), copy_amount: scalar('UInt64'), flag: scalar('Bool')})) {
    order.body.fields.push(name);
    order.body.typed_contract.properties.push({name, type, identity: false, cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: 'Unicode β😀 and lone surrogate \ud800', ontology_property: 'FIXTURE-ORDER#' + name});
  }
  f.write('specs/alpha/nodes/order.json', order);
  const add = (id: string, kind: string, body: any) => {
    feature.nodes.push(id); f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});
  };
  const variants = [variant('Order', named('order')), variant('Orders', wrap('set', named('order'))), variant('Maybe', wrap('optional', named('answer'))), variant('Inline', choice), variant('Empty')];
  add('bundle', 'Enum', {values: variants.map(v => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-BUNDLE', variants}});
  const at = (root: string): any => ({op: 'path', root, properties: []});
  const orderBinding = f.factories.find(b => b.selector === 'alpha:order')! as any;
  for (const [id, field, type] of [['money-shape', 'money', named('money')], ['choice-shape', 'choice', choice], ['line-shape', 'lines', wrap('list', named('money'))], ['answer-shape', 'authorization', named('answer')], ['modes-shape', 'modes', wrap('list', named('mode'))]] as const) {
    add(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-' + id.toUpperCase(), parameters: [{name: 'value', type}], expression: {op: 'eq', left: at('value'), right: at('value')}}});
    orderBinding.base_validators.push({rule: 'alpha:' + id, arguments: [{parameter: 'value', field}]});
  }
  orderBinding.base_validators.push({rule: 'alpha:amount-valid', arguments: [{parameter: 'amount', path: ['money', 'amount']}]});
  for (const [id, expression, type] of [['small', {op: 'lt', left: at('value'), right: {op: 'literal', type: 'UInt64', value: '100'}}, scalar('UInt64')], ['flag-ok', {op: 'eq', left: at('value'), right: {op: 'literal', type: 'Bool', value: true}}, scalar('Bool')]] as const)
    add(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-' + id.toUpperCase(), parameters: [{name: 'value', type}], expression}});
  orderBinding.extensions.push({id: 'z-small', validators: [{rule: 'alpha:small', arguments: [{parameter: 'value', path: ['money', 'amount']}]}]}, {id: 'a-flag', validators: [{rule: 'alpha:flag-ok', arguments: [{parameter: 'value', field: 'flag'}]}]});
  f.write(featureFile, feature);
  const graph = loadCompiledProjectGraph(f.source);
  const field_bindings = ['peer', 'peers', 'members'].map(field => ({owner: 'alpha:order', field, kind: 'identity-reference', target: 'alpha:order', projection: ['id']}));
  field_bindings.push({owner: 'alpha:order', field: 'copy_amount', kind: 'field-projection', target: 'alpha:money', projection: ['amount']});
  const plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/owned', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings, factories: f.factories, operations: f.operations, workflows: f.workflows});
  const data = getPythonDataVerificationContext(plan), decisions = getPythonDecisionVerificationContext(plan);
  const controls = {data_model: data.model, runtime_dir: data.runtime_dir, factory_modules: getPythonFactoryVerificationContext(plan), factory_bindings: plan.selection.factories,
    rule_modules: decisions.rules, rule_contracts: Object.fromEntries(graph.nodes.filter(n => n.kind === 'Rule').map(n => [n.selector, n.body.typed_contract]))};
  const root = path.join(f.temp, 'observed');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const load = (name: string, source: string, binding = '') => name + "={'__name__':'observer'" + binding + '}\nexec(' + JSON.stringify(source) + ',' + name + ')\n';
  const script = 'import types\n' + load('operation', getReconciledSource('python_operation_observer'))
    + load('rule', getReconciledSource('python_rule_observer'), ", 'helper':types.SimpleNamespace(**operation)")
    + load('enumeration', getReconciledSource('python_enum_observer')) + load('owned', getReconciledSource('python_owned_observer')) + String.raw`
import ast, copy, hashlib, json, pathlib, sys
d=json.load(sys.stdin)
root=pathlib.Path(d['root'])
def observe(data=d, overrides=None): return owned['observe'](data,enumeration['observe'],rule['observe_rule'],overrides)
result=observe()
assert result['factories']==2 and result['sums']==2 and result['plain_enums']==2
order=next(m for m in d['controls']['factory_modules'] if m['selector']=='alpha:order')
file=order['relative_path']
source=(root/file).read_bytes()
mutations=['protocol','optional','identity','validator','extensions','reference','annotation','constructor','import','extra-effect']
for mutation in mutations:
    tree=ast.parse(source)
    provider=tree.body[-1].value
    classes={n.name:n for n in tree.body if isinstance(n,ast.ClassDef)}
    if mutation=='protocol': provider.args[2].elts[0].elts[2]=ast.Name(id='STRING',ctx=ast.Load())
    elif mutation=='optional': provider.args[2].elts[0].elts[3]=ast.Constant(value=True)
    elif mutation=='identity': provider.args[3].elts[0]=ast.Constant(value='amount')
    elif mutation=='validator': provider.args[6].elts[0].args[3].body=ast.Constant(value=True)
    elif mutation=='extensions': provider.args[7]=ast.Dict(keys=[],values=[])
    elif mutation=='reference':
        bindings=next(n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='OrderFieldBindings')
        bindings.elts[0].args[3]=ast.Constant(value='alpha:unexpected')
    elif mutation=='annotation': classes['OrderFields'].body[0].annotation=ast.Name(id='str',ctx=ast.Load())
    elif mutation=='constructor': next(n for n in classes['OrderSnapshot'].body if isinstance(n,ast.FunctionDef) and n.name=='__init__').body=[ast.Pass()]
    elif mutation=='import': next(n for n in tree.body if isinstance(n,ast.ImportFrom) and any(a.name=='MoneySnapshot' for a in n.names)).module='not_the_owner'
    else: tree.body.append(ast.Pass())
    ast.fix_missing_locations(tree)
    mutant=ast.unparse(tree).encode()
    compile(mutant,file,'exec',dont_inherit=True)
    try: observe(overrides={file:mutant})
    except ValueError as e: assert 'owned semantics/effects' in str(e), str(e)
    else: raise AssertionError('survived:'+mutation)
sum_file=file.replace('entities/order.py','enums/bundle_sum.py')
sum_source=(root/sum_file).read_bytes()
for mutation in ('sum-protocol','case-constructor','case-annotation','sum-return'):
    tree=ast.parse(sum_source)
    if mutation=='sum-protocol':
        component=next(n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='BundleValueComponent')
        component.args[1]=ast.Constant(value='alpha:another-owner')
    elif mutation=='sum-return': tree.body[-1].body[0].value=ast.Constant(value=None)
    else:
        case=next(n for n in tree.body if isinstance(n,ast.ClassDef) and any(isinstance(a,ast.AnnAssign) and a.target.id=='payload' for a in n.body))
        if mutation=='case-constructor': next(n for n in case.body if isinstance(n,ast.FunctionDef)).body=[ast.Pass()]
        else: next(n for n in case.body if isinstance(n,ast.AnnAssign) and n.target.id=='payload').annotation=ast.Name(id='object',ctx=ast.Load())
    ast.fix_missing_locations(tree)
    mutant=ast.unparse(tree).encode()
    compile(mutant,sum_file,'exec',dont_inherit=True)
    try: observe(overrides={sum_file:mutant})
    except ValueError as e: assert 'owned semantics/effects' in str(e)
    else: raise AssertionError('survived:'+mutation)
for suffix in ('values.py','factories.py','references.py'):
    file=d['controls']['runtime_dir']+'/'+suffix
    mutant=(root/file).read_bytes()+b'\npass\n'
    compile(mutant,file,'exec',dont_inherit=True)
    try: observe(overrides={file:mutant})
    except ValueError as e: assert 'owned support drift' in str(e)
    else: raise AssertionError('runtime drift survived')
rule_file=d['controls']['rule_modules'][0]['relative_path']
try: observe(overrides={rule_file:(root/rule_file).read_bytes()+b'\npass\n'})
except ValueError as e: assert 'Rule semantics/effects' in str(e)
else: raise AssertionError('Rule effect survived')
for mutation in ('missing-factory','binding','reference-metadata'):
    changed=copy.deepcopy(d)
    if mutation=='missing-factory': changed['controls']['factory_modules'].pop()
    elif mutation=='binding': next(b for b in changed['controls']['factory_bindings'] if b['selector']=='alpha:order')['extensions'].reverse()
    else: next(m for m in changed['controls']['factory_modules'] if m['selector']=='alpha:order')['field_bindings'][0]['target']='alpha:unexpected'
    # Source extension order is normalized by ID, not an execution sequence;
    # reversing this table must not manufacture a false drift error.
    if mutation=='binding':
        assert observe(changed)==result
        next(b for b in changed['controls']['factory_bindings'] if b['selector']=='alpha:order')['base_validators'].reverse()
    try: observe(changed)
    except ValueError: pass
    else: raise AssertionError('metadata drift survived:'+mutation)
print(json.dumps({**result,'compiling_mutations_rejected':18,'metadata_mutations_rejected':3}))
`;
  const launcher = "import io,json,sys\ne=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(e['request']))\nexec(e['program'])\n";
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', launcher], {input: JSON.stringify({program: script, request: {root, controls}}), encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr);
  const observed = JSON.parse(result.stdout);
  assert.deepEqual(observed.selectors, data.model!.declarations.map(d => d.selector).sort());
  assert.equal(observed.compiling_mutations_rejected, 18); assert.equal(observed.metadata_mutations_rejected, 3);
  t.diagnostic(JSON.stringify(observed));
});
