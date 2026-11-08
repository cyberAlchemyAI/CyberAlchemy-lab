import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync, spawnSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredPythonQueries, PYTHON_QUERY_VERSION} from '../../src/generation/configured-python-queries.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..'), pkg = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes = (file: string) => fs.readFileSync(file, 'utf8');
const sources = {configuration: bytes(path.join(pkg, 'configuration.json')), base: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  python: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')), query_contract: bytes(path.join(pkg, 'query-generation-contract.json')),
  field_contract: bytes(path.join(project, 'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'))};
const boundaryContract = bytes(path.join(project, 'development/reconciliation-v1/contracts/composition-boundary.json'));
const scalar = (name = 'String') => ({kind: 'scalar', name}), named = (name: string) => ({kind: 'named', selector: 'alpha:' + name});
const wrap = (kind: string, element: any) => ({kind, element});
const field = (name: string) => ({kind: 'field', name}), param = (name: string) => ({kind: 'parameter', name});
const cmp = (op: string, left: any, right: any) => ({op, left, right});
const projection = ['id', 'label', 'amount', 'active', 'money', 'customer', 'items', 'labels', 'state', 'choice', 'note', 'class'];
const spec: Record<string, any> = {
  all: {}, amount: {filter: {op: 'all', terms: [cmp('gte', field('amount'), param('min')), cmp('eq', field('active'), param('enabled'))]}, order_by: {field: 'amount', direction: 'asc'}, limit: 2},
  sorted: {order_by: {field: 'label', direction: 'asc'}, projection: ['id', 'label']}, descending: {order_by: {field: 'label', direction: 'desc'}, projection: ['id', 'label']},
  enabled: {order_by: {field: 'active', direction: 'desc'}, filter: cmp('gte', field('active'), param('enabled')), projection: ['id', 'active']},
  label: {filter: cmp('eq', field('label'), param('label')), projection: ['id']},
  predicate: {filter: {op: 'any', terms: [{op: 'all', terms: [cmp('lt', field('amount'), {kind: 'literal', type: 'UInt64', value: 10}), cmp('gt', field('amount'), {kind: 'literal', type: 'UInt64', value: 5}), cmp('lte', field('amount'), param('min'))]}, {op: 'not', term: cmp('eq', field('active'), {kind: 'literal', type: 'Bool', value: true})}]}, projection: ['id']},
  identity: {filter: cmp('eq', field('customer'), field('other_customer')), projection: ['id']},
  value: {filter: cmp('eq', field('money'), field('other_money')), projection: ['id']},
  optional: {filter: cmp('eq', field('note'), field('other_note')), projection: ['id', 'note']},
  list: {filter: cmp('eq', field('items'), field('other_items')), projection: ['id']},
  set: {filter: cmp('eq', field('labels'), field('other_labels')), projection: ['id']},
  sum: {filter: cmp('eq', field('choice'), field('other_choice')), projection: ['id']},
  enum: {filter: cmp('eq', field('state'), field('other_state')), projection: ['id']},
  literal: {filter: cmp('lt', field('label'), {kind: 'literal', type: 'String', value: '\ue000'}), projection: ['id']},
  empty: {inputs: [], projection: ['id', 'note']},
  'all-provider': {projection: ['id']},
};
function fixture(t: any, optional = false) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-query-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'); fs.cpSync(path.join(project, 'impl/cli/fixtures/input-roots/canonical-project'), source, {recursive: true});
  const write = (file: string, data: unknown) => {const full = path.join(source, file); fs.mkdirSync(path.dirname(full), {recursive: true}); fs.writeFileSync(full, JSON.stringify(data) + '\n');};
  const feature = JSON.parse(bytes(path.join(source, 'specs/alpha/feature.json'))), contracts: Record<string, any> = {};
  const node = (id: string, kind: string, body: any) => {feature.nodes.push(id); write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});};
  const record = (id: string, kind: string, fields: [string, any][]) => node(id, kind, {fields: fields.map(([n]) => n), ...(kind === 'Value Object' ? {invariant_refs: ['alpha:valid-read-value']} : {}), typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), properties: fields.map(([name, type]) => ({name, type, identity: name === 'id', cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: name, ontology_property: 'FIXTURE-' + id.toUpperCase() + '#' + name}))}});
  node('valid-read-value', 'Rule', {predicate: 'structured:domainspec.typed-rule/v1', typed_contract: {schema_version: 'domainspec.typed-rule/v1', ontology_rule: 'FIXTURE-VALID-READ-VALUE', parameters: [{name: 'amount', type: scalar('UInt64')}], expression: {op: 'eq', left: {op: 'literal', type: 'Bool', value: false}, right: {op: 'literal', type: 'Bool', value: true}}}});
  record('money', 'Value Object', [['amount', scalar('UInt64')], ['currency', scalar()]]);
  record('query-customer', 'Entity', [['id', scalar()], ['label', scalar()]]);
  const variants = [{name: 'Pending', ontology_variant: 'FIXTURE-STATUS#Pending', payload: null}, {name: 'Ready', ontology_variant: 'FIXTURE-STATUS#Ready', payload: null}];
  node('status', 'Enum', {values: variants.map(v => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-STATUS', variants}});
  const sum = {kind: 'sum', variants: [{name: 'None', ontology_variant: 'FIXTURE-CHOICE#None', payload: null}, {name: 'Amount', ontology_variant: 'FIXTURE-CHOICE#Amount', payload: scalar('UInt64')}, {name: 'Money', ontology_variant: 'FIXTURE-CHOICE#Money', payload: named('money')}]};
  const paired: [string, any][] = [['money', named('money')], ['customer', named('query-customer')], ['items', wrap('list', named('money'))], ['labels', wrap('set', scalar())], ['note', wrap('optional', scalar())], ['state', named('status')], ['choice', sum]];
  record('order', 'Entity', [['id', scalar()], ['label', scalar()], ['amount', scalar('UInt64')], ['active', scalar('Bool')], ['class', scalar()], ...paired.flatMap(([name, type]) => [[name, type], ['other_' + name, type]] as [string, any][])]);
  for (const [id, s] of Object.entries(spec)) {
    const name = 'read-' + id, edge = name + '-reads-order'; feature.edges.push(edge);
    const c = {schema_version: 'domainspec.typed-query/v1', ontology_query: 'FIXTURE-' + name.toUpperCase(), source: 'alpha:order', inputs: s.inputs ?? [{name: 'min', type: scalar('UInt64')}, {name: 'enabled', type: scalar('Bool')}, {name: 'label', type: scalar()}], filter: s.filter ?? null, projection: s.projection ?? projection, order_by: s.order_by ?? null, limit: s.limit ?? null}; contracts['alpha:' + name] = c;
    if (optional && id === 'amount') Object.assign(c, {schema_version:'domainspec.typed-query/v2',result_cardinality:'optional',limit:null});
    node(name, 'Query', {reads: ['alpha:order'], typed_contract: c});
    write('specs/alpha/edges/' + edge + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: edge, relationship: 'reads', source_node_id: name, target_node_id: 'order', scope: 'feature'});
  }
  write('specs/alpha/feature.json', feature);
  const compile = () => {
    const graph = loadCompiledProjectGraph(source), graph_sha256 = createCompiledProjectCertificate(graph).graph_sha256;
    const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256}, boundaryContract);
    const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256, roots: ['alpha:order'], bindings: []}, sources.field_contract);
    return {boundary, fields};
  };
  const {boundary, fields} = compile();
  const selection = {schema_version: PYTHON_QUERY_VERSION, language: 'python' as const, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, module_root: 'domain-app', roots: Object.keys(contracts)};
  return {temp, source, contracts, boundary, fields, selection, write, compile, plan: () => planConfiguredPythonQueries(boundary, fields, selection, sources)};
}
type Plan = ReturnType<typeof planConfiguredPythonQueries>;
function materialize(root: string, p: Plan) {for (const a of p.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}}
function payload(root: string, p: Plan, f: ReturnType<typeof fixture>) {return {root, modules: p.modules, files: p.artifacts.map(a => a.relative_path), contracts: f.contracts, model: f.fields.model, runtime_dir: path.posix.dirname(p.artifacts.find(a => a.relative_path.endsWith('/runtime/facts.py'))!.relative_path)};}
const observer = path.join(project, 'impl/cli/src/verification/python-query-observer.py');
const nativeScript = String.raw`
import copy, dataclasses, importlib, json, os, pathlib, sys, types, typing
data = json.load(sys.stdin); sys.path.insert(0, data['root']); f = {}
def thaw(value):
    if dataclasses.is_dataclass(value) and hasattr(value, 'entries'): return {k: thaw(v) for k, v in value.entries}
    if type(value) is tuple: return [thaw(v) for v in value]
    if hasattr(value, 'items'): return {k: thaw(v) for k, v in value.items()}
    return value
def members(shape):
    methods = typing.get_overloads(shape.__getitem__) or [shape.__getitem__]
    return {typing.get_args(typing.get_type_hints(method)['key'])[0]: typing.get_type_hints(method)['return'] for method in methods}
def union(parts):
    flat = []
    for part in parts: flat.extend(part['union'] if type(part) is dict and set(part) == {'union'} else [part])
    return flat[0] if len(flat) == 1 else {'union': sorted(flat,key=lambda p:json.dumps(p,sort_keys=True))}
def native_type(t):
    if t in (str,int,bool): return t.__name__
    if t is type(None): return 'None'
    origin,args = typing.get_origin(t),typing.get_args(t)
    if origin in (types.UnionType,typing.Union): return union([native_type(a) for a in args])
    if origin is typing.Literal: return {'literal':args[0]}
    if origin is tuple: return {'tuple':native_type(args[0])}
    assert getattr(t,'_is_protocol',False),t
    return {key:native_type(value) for key,value in members(t).items()}
declared={d['selector']:d for d in data['model']['declarations']}
def source_type(t):
    if t['kind']=='scalar': return {'String':'str','UInt64':'int','Bool':'bool'}[t['name']]
    if t['kind']=='named':
        d=declared[t['selector']]
        if d['kind']=='Enum': return source_type({'kind':'sum','variants':d['contract']['variants']})
        return {f['name']:source_type(f['type']) for f in d['contract']['properties']}
    if t['kind']=='sum': return union([{'variant':{'literal':v['name']},**({'payload':source_type(v['payload'])} if v['payload'] else {})} for v in t['variants']])
    if t['kind']=='optional': return union([source_type(t['element']),'None'])
    return {'tuple':source_type(t['element'])}
for m in data['modules']:
    module = importlib.import_module(m['import_name']); fn = getattr(module, m['callable']); f[m['selector'].split('read-', 1)[1]] = fn
    assert thaw(fn.descriptor) == m['descriptor']
    annotations = typing.get_type_hints(fn.__call__)
    assert typing.get_origin(annotations['return']) is tuple
    shape = typing.get_args(annotations['return'])[0]
    fields = members(shape)
    assert list(fields) == data['contracts'][m['selector']]['projection']
    for field in m['descriptor']['result_fields']:
        assert native_type(fields[field['name']]) == source_type(field['type']),field['name']
    params = typing.get_type_hints(annotations['parameters'])
    assert set(params) == {p['name'] for p in m['descriptor']['inputs']}
    for action in [lambda: setattr(fn, 'descriptor', {}), lambda: fn.descriptor.__setitem__('limit', 0), lambda: fn.descriptor['read_targets'][0].__setitem__('selector', 'foreign')]:
        try: action()
        except (TypeError, AttributeError): pass
        else: raise AssertionError('MUTABLE_BINDING')
params = {'min': 0, 'enabled': True, 'label': 'unused'}
money = lambda amount=4: {'amount': amount, 'currency': 'GBP'}
def row(id='a', amount=10, label='a'):
    m = money(); c = {'id': 'customer', 'label': 'first'}
    return {'id': id, 'amount': amount, 'label': label, 'active': True, 'class': 'premium', 'money': m, 'other_money': copy.deepcopy(m), 'customer': c, 'other_customer': {'id': 'customer', 'label': 'second'}, 'items': [money(1), money(1)], 'other_items': [money(1), money(1)], 'labels': ['z','a'], 'other_labels': ['a','z'], 'state': {'variant':'Ready'}, 'other_state': {'variant':'Ready'}, 'choice': {'variant':'Money','payload':money('18446744073709551615')}, 'other_choice': {'variant':'Money','payload':money('18446744073709551615')}}
def error(fn, rows, parameters=params):
    try: fn(rows, parameters)
    except TypeError as e: assert str(e) == 'QUERY_INPUT', str(e)
    else: raise AssertionError('QUERY_INPUT_MISSING')
events = []; armed = False
def audit(event, args):
    if armed and (event in ('open', 'exec', 'compile', 'import') or event.startswith(('os.', 'socket.', 'subprocess.'))): events.append(event)
sys.addaudithook(audit)
armed = True
a, b, c = row('same','18446744073709551615','z'), row('same','9007199254740992','a'), row('other',2,'b')
caller = [a,b,c]; before = copy.deepcopy(caller)
out = f['amount'](caller, {**params, 'min':'9007199254740992'})
assert type(out) is tuple and [v['amount'] for v in out] == [9007199254740992,18446744073709551615]
assert [v['id'] for v in out] == ['same','same']
assert out[1]['choice']['payload']['amount'] == 18446744073709551615
assert out[0]['note'] is None and out[0]['labels'] == ('a','z') and len(out[0]['items']) == 2
assert list(thaw(out[0])) == data['contracts']['alpha:read-all']['projection']
assert caller == before
a['money']['amount'] = 999; a['items'][0]['amount'] = 999
assert out[1]['money']['amount'] == 4 and out[1]['items'][0]['amount'] == 1
for value in [out[0], out[0]['money'], out[0]['choice']]:
    try: value.entries = ()
    except (TypeError, AttributeError): pass
    else: raise AssertionError('MUTABLE_READ_MODEL')
ties = [row('first',1),row('second',1),row('third',1)]
assert [v['id'] for v in f['amount'](ties,params)] == ['first','second']
assert f['all']([],params) == () and f['label']([row()],{**params,'label':'absent'}) == ()
unicode_rows = [row(str(i),1,x) for i,x in enumerate(['é','e\u0301','😀','\ue000'])]
assert [r['label'] for r in f['sorted'](unicode_rows,params)] == sorted([r['label'] for r in unicode_rows],key=lambda s:s.encode('utf-16-be','surrogatepass'))
assert [r['label'] for r in f['descending'](unicode_rows,params)] == sorted([r['label'] for r in unicode_rows],key=lambda s:s.encode('utf-16-be','surrogatepass'),reverse=True)
assert [r['id'] for r in f['literal']([row('astral',1,'😀'),row('bmp',1,'\ue000')],params)] == ['astral']
assert len(f['label']([row('pair',1,'\ud83d\ude00')],{**params,'label':'😀'})) == 1
truth = [row('true'),{**row('false'),'active':False}]
assert [r['id'] for r in f['enabled'](truth,{**params,'enabled':False})] == ['true','false']
predicates = [row(str(v),v) for v in [5,6,8,9,10]] + [{**row('inactive',0),'active':False}]
assert [r['id'] for r in f['predicate'](predicates,{**params,'min':8})] == ['6','8','inactive']
for name in ['identity','value','list','set','optional','sum','enum']: assert len(f[name]([row()],params)) == 1
changes = {'identity': ('other_customer', {'id':'other','label':'second'}), 'value':('other_money', {'amount':4,'currency':'USD'}), 'list':('other_items',[money(1)]), 'set':('other_labels',['a']), 'optional':('other_note','present'), 'sum':('other_choice',{'variant':'Amount','payload':4}), 'enum':('other_state',{'variant':'Pending'})}
for name,(key,value) in changes.items():
    changed = row(); changed[key] = value; assert f[name]([changed],params) == ()
changed = row(); changed['items']=[money(1),money(2)];changed['other_items']=[money(2),money(1)];assert f['list']([changed],params) == ()
assert len(f['all']([row()],params)) == 1  # Authored false VO invariant is not executed.
assert thaw(f['empty']([row()],{})) == [{'id':'a','note':None}]
for choice in [{'variant':'None'},{'variant':'Amount','payload':'18446744073709551615'},{'variant':'Money','payload':money(0)}]:
    assert f['all']([{**row(),'choice':choice}],params)[0]['choice']['variant'] == choice['variant']
for value in [True,1.0,-1,'01','+1','1\n','18446744073709551616',{},None]: error(f['all'],[row()],{**params,'min':value})
for value in [1,'true',None]: error(f['all'],[row()],{**params,'enabled':value})
error(f['all'],[],{**params,'label':1})
for value in [None,{},[],{**params,'extra':1},{'min':0,'enabled':True}]: error(f['all'],[row()],value)
bad = row(); bad['other_money']['amount'] = True
error(f['amount'],[row('valid'),{**bad,'amount':0}],{**params,'min':10})
for patch in [{'labels':['a','a']},{'state':{'variant':'Unknown'}},{'choice':{'variant':'None','payload':None}},{'note':3},{'extra':0}]: error(f['all'],[{**row(),**patch}])
bad = row(); del bad['other_money'];error(f['all'],[bad])
calls=[]
class ActiveList(list):
    def __iter__(self): calls.append('iterate'); return super().__iter__()
class ActiveDict(dict):
    def __getitem__(self,key): calls.append('get');return super().__getitem__(key)
class ActiveStr(str):
    def __eq__(self,other): calls.append('equal');return True
    def __hash__(self): return str.__hash__(self)
class ActiveInt(int):
    def __int__(self):calls.append('int');return 0
for rows in [ActiveList([row()]),[ActiveDict(row())],None,iter([row()])]:error(f['all'],rows)
for value in [ActiveInt(1),ActiveStr('1')]:error(f['all'],[row()],{**params,'min':value})
error(f['all'],[row()],ActiveDict(params))
assert calls == [], calls
hostile={ActiveStr('min'):0,'enabled':True,'label':'x'};calls.clear();error(f['all'],[row()],hostile);assert calls == []
result=thaw(f['all']([row()],params))
armed=False
assert events == [], events
for file in data['files']: compile(pathlib.Path(data['root'],file).read_bytes(),file,'exec')
print(json.dumps({'pid':os.getpid(),'result':result,'queries':len(f),'effects':events}))
`;

test('R10 Python Query planning binds same-graph fields, profiles and stable source-only artifacts', t => {
  const f = fixture(t), p = f.plan(); assert.equal(p.modules.length, 17); assert.deepEqual(f.plan(), p);
  assert.deepEqual(planConfiguredPythonQueries(f.boundary, f.fields, {...f.selection, roots: [...f.selection.roots].reverse()}, sources), p);
  const alternate = planConfiguredPythonQueries(f.boundary, f.fields, {...f.selection, module_root: 'alternate/nested'}, sources);
  assert.deepEqual(alternate.artifacts.filter(a => a.content).map(a => a.content), p.artifacts.filter(a => a.content).map(a => a.content));
  const subset = planConfiguredPythonQueries(f.boundary, f.fields, {...f.selection, roots: ['alpha:read-all']}, sources);
  for (const a of subset.artifacts) assert.equal(a.content, p.artifacts.find(b => b.relative_path === a.relative_path)!.content);
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  for (const m of p.modules) {const {descriptor_sha256, ...d} = m.descriptor; assert.equal(descriptor_sha256, sha256(canonicalJson(d))); assert.equal(d.contract_sha256, sha256(canonicalJson(f.contracts[m.selector]))); assert.ok(Object.isFrozen(d.result_fields));}
  fs.renameSync(f.source, path.join(f.temp, 'gone')); assert.deepEqual(f.plan(), p);
});

test('R10 Python Query planner rejects active, stale, cross-graph and semantically incompatible inputs', t => {
  const f = fixture(t);
  for (const patch of [{schema_version:'future'},{language:'typescript'},{boundary_sha256:'stale'},{field_compilation_sha256:'stale'},{module_root:'../escape'},{module_root:'typing'},{roots:[]},{roots:['alpha:read-all','alpha:read-all']},{roots:['alpha:order']},{extra:true}]) assert.throws(() => planConfiguredPythonQueries(f.boundary,f.fields,{...f.selection,...patch} as any,sources));
  assert.throws(() => planConfiguredPythonQueries(structuredClone(f.boundary),f.fields,f.selection,sources));
  assert.throws(() => planConfiguredPythonQueries(f.boundary,structuredClone(f.fields),f.selection,sources));
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredPythonQueries(f.boundary,f.fields,f.selection,{...sources,[key]:sources[key as keyof typeof sources]+' '}),/source drift/);
  let reads=0;assert.throws(()=>planConfiguredPythonQueries(f.boundary,f.fields,{...f.selection,get roots(){reads++;return [];}},sources));assert.equal(reads,0);
  const file='specs/alpha/nodes/read-all.json',original=JSON.parse(bytes(path.join(f.source,file)));
  for(const patch of [{filter:cmp('eq',field('amount'),param('label'))},{order_by:{field:'note',direction:'asc'}}]){
    f.write(file,{...original,body:{...original.body,typed_contract:{...original.body.typed_contract,...patch}}});const next=f.compile();
    assert.throws(()=>planConfiguredPythonQueries(next.boundary,f.fields,{...f.selection,boundary_sha256:next.boundary.boundary_sha256},sources),/cross-graph/);
    assert.throws(()=>planConfiguredPythonQueries(next.boundary,next.fields,{...f.selection,boundary_sha256:next.boundary.boundary_sha256,field_compilation_sha256:next.fields.compilation_sha256},sources),/comparison type mismatch|ordering requires/);
  }
});

test('R10 Python Queries execute complete structured semantics, immutable typed results and observed read-only bounds', t => {
  const f=fixture(t),results:any[]=[];
  for(const module_root of ['domain-app','relocated/nested']){
    const p=planConfiguredPythonQueries(f.boundary,f.fields,{...f.selection,module_root},sources),root=path.join(f.temp,module_root);materialize(root,p);const input=JSON.stringify(payload(root,p,f));
    results.push(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input,encoding:'utf8'})));
    assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B',observer],{input,encoding:'utf8'})),{observed:17});
  }
  assert.notEqual(results[0].pid,results[1].pid);assert.deepEqual(results[0].result,results[1].result);
});

test('optional Python Query preserves absent, one and too-many outcomes in its typed public binding', t => {
  const f=fixture(t,true),p=planConfiguredPythonQueries(f.boundary,f.fields,{...f.selection,roots:['alpha:read-amount']},sources);
  const root=path.join(f.temp,'optional');materialize(root,p);const module=p.modules[0]!;
  assert.equal(module.descriptor.protocol_id,'python.bound-query/v2-candidate');
  assert.deepEqual(module.descriptor.failures,['QUERY_INPUT','QUERY_CARDINALITY']);
  const script=String.raw`
import copy, importlib, json, sys, typing
d=json.load(sys.stdin);sys.path.insert(0,d['root']);module=importlib.import_module(d['module']);query=getattr(module,d['callable'])
def row(amount):
    money={'amount':4,'currency':'GBP'};customer={'id':'customer','label':'first'}
    r={'id':'order','label':'order','amount':amount,'active':True,'class':'premium'}
    values={'money':money,'customer':customer,'items':[money],'labels':['a'],'state':{'variant':'Ready'},'choice':{'variant':'Money','payload':money}}
    for name,value in values.items():r[name]=copy.deepcopy(value);r['other_'+name]=copy.deepcopy(value)
    return r
params={'min':2,'enabled':True,'label':'unused'}
assert query([],params) is None
assert query([row(1)],params) is None
rows=[row('18446744073709551615')];before=copy.deepcopy(rows);one=query(rows,params)
assert one['amount']==18446744073709551615 and rows==before
assert type(None) in typing.get_args(typing.get_type_hints(type(query).__call__)['return'])
try:one['amount']=1
except (TypeError,AttributeError):pass
else:raise AssertionError('mutable projection')
try:query(rows+rows,params)
except RuntimeError as e:assert str(e)=='QUERY_CARDINALITY'
else:raise AssertionError('cardinality lost')
try:query([row(-1)],params)
except TypeError as e:assert str(e)=='QUERY_INPUT'
else:raise AssertionError('invalid source accepted')
print('optional-ok')
`;
  assert.equal(execFileSync('/usr/bin/python3',['-I','-B','-c',script],{input:JSON.stringify({root,module:module.import_name,callable:module.callable}),encoding:'utf8'}).trim(),'optional-ok');
});

test('R10 independent Python Query observation kills compiling predicate, ordering, projection and effect mutants', t => {
  const f=fixture(t),p=f.plan(),root=path.join(f.temp,'mutants');materialize(root,p);
  const m=p.modules.find(m=>m.selector==='alpha:read-amount')!,file=path.join(root,m.provider_path),original=bytes(file);
  const mutants=[original.replace('row["amount"] >= p0','row["amount"] < p0'),original.replace('reverse=False','reverse=True'),original.replace('selected[:2]','selected[:1]'),original.replace('("id", row["id"])','("id", row["label"])'),original.replace('return tuple(', 'globals()["write"] = 1\n        return tuple('),original.replace('return tuple(', 'rows.append(rows[0])\n        rows.pop()\n        return tuple('),original.replace('return tuple(', 'yield tuple(')];
  for(const mutant of mutants){
    assert.notEqual(mutant,original);fs.writeFileSync(file,mutant);execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
    const changed:any=structuredClone(m);changed.descriptor.provider.sha256=sha256(mutant);
    const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[changed]}),encoding:'utf8'});
    assert.notEqual(result.status,0);assert.match(result.stderr,/PYTHON_QUERY_OBSERVER:query semantics or effects/);
  }
  fs.writeFileSync(file,original);
  const facadeFile=path.join(root,m.relative_path),facade=bytes(facadeFile);
  for(const [mutant,reason] of [[facade.replace('frozen=True','frozen=False'),'frozen provider binding'],[facade.replace('"declared-read-only"','"state-changing"'),'descriptor binding']]){
    assert.notEqual(mutant,facade);fs.writeFileSync(facadeFile,mutant!);execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
    const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[m]}),encoding:'utf8'});
    assert.notEqual(result.status,0);assert.match(result.stderr,new RegExp(reason!));
  }
  fs.writeFileSync(facadeFile,facade);
  const data=payload(root,p,f),supportFile=path.join(root,data.runtime_dir,'values.py'),support=bytes(supportFile);
  const mutant=support.replace('if type(value) is not bool:', 'if type(value) not in (bool, int):');assert.notEqual(mutant,support);fs.writeFileSync(supportFile,mutant);
  execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
  const changed:any=structuredClone(m);changed.descriptor.runtime.find((r:any)=>r.id==='values.py').sha256=sha256(mutant);
  const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...data,modules:[changed]}),encoding:'utf8'});
  assert.notEqual(result.status,0);assert.match(result.stderr,/support perimeter/);
});
