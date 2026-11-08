import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonFactories, PYTHON_FACTORY_VERSION} from '../../src/generation/configured-python-factories.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), wp = 'development/reconciliation-v1/profile-compiler-reconciliation/';
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const sources = {configuration: read(wp + 'configuration.json'), base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'), python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  rule_contract: read(wp + 'string-order-rule-contract.json'), collection_contract: read(wp + 'rule-collection-value-contract.json'), predicate_contract: read(wp + 'rule-collection-predicate-contract.json'), numeric_contract: read(wp + 'rule-numeric-contract.json'), exact_contract: read(wp + 'rule-exact-contract.json'), literal_contract: read(wp + 'rule-exact-literal-contract.json'), structured_contract: read(wp + 'rule-structured-value-contract.json'),
  field_contract: read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json'), factory_contract: read(wp + 'factory-structured-rule-contract.json')};
const scalar = (name = 'String'): any => ({kind: 'scalar', name}), named = (id: string): any => ({kind: 'named', selector: 'commerce:' + id});
const wrap = (kind: string, element: any): any => ({kind, element});
const at = (root: string, ...properties: string[]): any => ({op: 'path', root, properties}), lit = (type: string, value: unknown): any => ({op: 'literal', type, value});
const eq = (left: any, right: any): any => ({op: 'eq', left, right});
const variant = (name: string, payload: any = null) => ({name, ontology_variant: 'FIXTURE-AUTH#' + name, payload});
const inline: any = {kind: 'sum', variants: [variant('None'), variant('Text', scalar())]};
const property = (owner: string, name: string, type: any, identity = false) => ({name, type, identity, cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: name, ontology_property: 'FIXTURE-' + owner + '#' + name});
function fixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-factories-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [];
  const write = (file: string, content: unknown) => {const p = path.join(source, file); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(content) + '\n');};
  const node = (id: string, kind: string, body: object) => {nodes.push(id); write(`specs/commerce/nodes/${id}.json`, {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const record = (id: string, kind: string, properties: any[], invariant_refs: string[] = []) => node(id, kind, {fields: properties.map(p => p.name), ...(kind === 'Value Object' ? {invariant_refs} : {}), typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), properties}});
  record('money', 'Value Object', [property('MONEY', 'amount', scalar('UInt64')), property('MONEY', 'currency', scalar()), property('MONEY', 'note', wrap('optional', scalar()))], ['commerce:valid-currency', 'commerce:positive']);
  record('customer', 'Entity', [property('CUSTOMER', 'id', scalar(), true), property('CUSTOMER', 'label', scalar())]);
  record('order', 'Entity', [property('ORDER', 'id', scalar(), true), property('ORDER', 'money', named('money')), property('ORDER', 'customer', named('customer')), property('ORDER', 'lines', wrap('list', named('money'))), property('ORDER', 'tags', wrap('set', scalar())), property('ORDER', 'status', named('status')), property('ORDER', 'authorization', named('authorization')), property('ORDER', 'choice', inline), property('ORDER', 'class', scalar())]);
  for (const [id, variants] of [['status', [variant('Draft'), variant('Ready')]], ['authorization', [variant('Denied'), variant('Approved', named('money'))]]] as const) node(id, 'Enum', {values: variants.map(v => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), variants}});
  const rule = (id: string, parameters: any[], expression: any) => node(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'RULE-' + id.toUpperCase(), parameters, expression}});
  const p = (name: string, type: any) => ({name, type});
  for (const id of ['valid-currency', 'valid-label', 'valid-id', 'valid-class']) rule(id, [p('value', scalar())], {op: 'not', term: eq(at('value'), lit('String', ''))});
  rule('positive', [p('value', scalar('UInt64'))], {op: 'lt', left: lit('UInt64', '0'), right: at('value')});
  rule('small', [p('value', scalar('UInt64'))], {op: 'lt', left: at('value'), right: lit('UInt64', '100')});
  rule('money-under-cap', [p('money', named('money'))], {op: 'lt', left: at('money', 'FIXTURE-MONEY#amount'), right: lit('UInt64', '100')});
  rule('ready', [p('status', named('status'))], eq(at('status'), {op: 'variant', selector: 'FIXTURE-AUTH#Ready'}));
  for (const [id, type] of Object.entries({'auth-shape': named('authorization'), 'choice-shape': inline, 'lines-shape': wrap('list', named('money'))})) rule(id, [p('value', type)], eq(at('value'), at('value')));
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-factories', features: ['commerce'], cross_feature_edges: []});
  write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges: []});
  const graph = loadCompiledProjectGraph(source);
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: createCompiledProjectCertificate(graph).graph_sha256, roots: ['commerce:order'], bindings: []}, sources.field_contract);
  const bind = (rule: string, field: string, parameter = 'value') => ({rule: 'commerce:' + rule, arguments: [{parameter, field}]});
  const selection = {schema_version: PYTHON_FACTORY_VERSION, language: 'python' as const, module_root: 'domain-app', field_compilation_sha256: fields.compilation_sha256, factories: [
    {selector: 'commerce:money', base_validators: [bind('valid-currency', 'currency'), bind('positive', 'amount')], extensions: [{id: 'small', validators: [bind('small', 'amount')]}]},
    {selector: 'commerce:customer', base_validators: [bind('valid-id', 'id'), bind('valid-label', 'label')], extensions: []},
    {selector: 'commerce:order', base_validators: [bind('valid-id', 'id'), bind('money-under-cap', 'money', 'money'), {rule: 'commerce:positive', arguments: [{parameter: 'value', path: ['money', 'amount']}]}, bind('auth-shape', 'authorization'), bind('choice-shape', 'choice'), bind('lines-shape', 'lines'), bind('valid-class', 'class')], extensions: [{id: 'ready', validators: [bind('ready', 'status', 'status')]}]},
  ]};
  return {temp, source, graph, fields, selection};
}

const native = String.raw`
import ast
import copy
import gc
import importlib
import inspect
from dataclasses import FrozenInstanceError, is_dataclass
from pathlib import Path
import sys
import typing
root, prefix = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root))
def load(role, name):
    return importlib.import_module(prefix + ".features.commerce.src.domain." + role + "." + name)
m, c, o = load("value_objects", "money"), load("entities", "customer"), load("entities", "order")
status, auth = load("enums", "status"), load("enums", "authorization_sum")
runtime = importlib.import_module(prefix + ".runtime.factories")
mf, cf, of = m.create_money_factory(), c.create_customer_factory(), o.create_order_factory()
def success(result):
    assert result.ok is True, result
    assert result.failure_codes == ()
    assert result.trace.phases[-2:] == ("form", "freeze")
    return result.value
def failure(result, code):
    assert result.ok is False and result.value is None, "EXPECTED_FAILURE:" + code
    assert result.failure_codes == (code,), result
    assert "form" not in result.trace.phases and "freeze" not in result.trace.phases
def reject(call, code):
    try:
        call()
        raise AssertionError("ACCEPTED:" + code)
    except TypeError as error:
        assert code in str(error), str(error)
money = success(mf.create({"amount": "2", "currency": "GBP"}))
assert money.fields.amount == 2 and money.fields.note is None
assert money == success(mf.reconstruct({"amount": 2, "currency": "GBP", "note": None}))
assert money != success(mf.create({"amount": 3, "currency": "GBP"})), "COMPLETE_VALUE"
assert money != success(mf.create({"amount": 2, "currency": "USD"}))
assert money != success(mf.create({"amount": 2, "currency": "GBP", "note": ""}))
assert hash(money) == hash(success(mf.create({"amount": 2, "currency": "GBP"})))
before = len(runtime._snapshots)
failure(mf.create({"amount": 2, "currency": ""}), "RULE_FAIL:commerce:valid-currency")
failure(mf.reconstruct({"amount": 0, "currency": "GBP"}), "RULE_FAIL:commerce:positive")
assert len(runtime._snapshots) == before
for bad in (True, -1, "01", "1\n", 18446744073709551616, 1.0):
    failure(mf.create({"amount": bad, "currency": "GBP"}), "INVALID_FIELDS")
maximum = success(mf.create({"amount": "18446744073709551615", "currency": "GBP"}))
small = mf.extend("small")
assert mf.extensions == () and small.extensions == ("small",)
limited = small.create({"amount": 100, "currency": "GBP"})
failure(limited, "RULE_FAIL:commerce:small")
assert [(v.rule, v.outcome) for v in limited.trace.validators] == [("commerce:valid-currency", "pass"), ("commerce:positive", "pass"), ("commerce:small", "fail")]
assert money == success(small.create({"amount": 2, "currency": "GBP"}))
reject(lambda: small.extend("small"), "INVALID_EXTENSION")
reject(lambda: mf.extend("unknown"), "INVALID_EXTENSION")
customer = success(cf.create({"id": "a", "label": "First"}))
changed = success(cf.reconstruct({"id": "a", "label": "Changed"}))
assert customer == changed and hash(customer) == hash(changed), "ENTITY_IDENTITY_ONLY"
assert customer != success(cf.create({"id": "b", "label": "First"}))
assert customer.identity == ("a",)
transition = cf.transition(customer, {"id": "a", "label": "Later"})
later = success(transition)
assert later is not customer and later == customer and customer.fields.label == "First"
assert transition.trace.route == "transition" and transition.trace.phases == ("normalize", "resolve-identity", "form", "freeze")
failure(cf.transition(customer, {"id": "b", "label": "Later"}), "IDENTITY_CHANGED")
failure(cf.transition(customer, {"id": "a", "label": ""}), "RULE_FAIL:commerce:valid-label")
failure(cf.transition(money, {"id": "a", "label": "Later"}), "INVALID_PREVIOUS")
assert not hasattr(mf, "transition")
draft, ready = status.parse_status("Draft"), status.parse_status("Ready")
authorization = auth.create_authorization({"variant": "Approved", "payload": money})
raw = dict(id="order-1", money=money, customer=customer, lines=[money, money], tags=["b", "a"], status=draft, authorization=authorization, choice={"variant": "Text", "payload": "card"}, **{"class": "sale"})
order_result = of.create(raw)
order = success(order_result)
raw["lines"].append(maximum)
assert order.fields.lines == (money, money) and order.fields.tags == ("a", "b")
assert order.fields.customer is customer and order.fields.money is money
assert order.fields.authorization.payload is money
assert order.fields.choice.payload == "card" and order.fields.field__class == "sale"
assert all(v.outcome == "pass" for v in order_result.trace.validators)
assert all(len(v.closure_sha256) == 64 and len(v.artifact_sha256) == 64 for v in order_result.trace.validators)
failure(of.create({**raw, "money": maximum}), "RULE_FAIL:commerce:money-under-cap")
failure(of.create({**raw, "money": {"amount": 2, "currency": "GBP"}}), "INVALID_FIELDS")
failure(of.create({**raw, "status": "Draft"}), "INVALID_FIELDS")
failure(of.create({**raw, "authorization": {"variant": "Approved", "payload": money}}), "INVALID_FIELDS")
failure(of.create({**raw, "tags": ["a", "a"]}), "INVALID_FIELDS")
failure(of.extend("ready").create(raw), "RULE_FAIL:commerce:ready")
success(of.extend("ready").reconstruct({**raw, "status": ready}))
class Active(dict):
    def get(self, key):
        raise AssertionError("ACTIVE")
failure(mf.create(Active(amount=2, currency="GBP")), "INVALID_FIELDS")
failure(mf.create({"amount": 2, "currency": "GBP", "extra": 1}), "INVALID_FIELDS")
failure(mf.create({"amount": 2}), "INVALID_FIELDS")
for snapshot, component in ((money, m.MoneyValueComponent), (customer, c.CustomerValueComponent), (order, o.OrderValueComponent)):
    assert component.is_owned(snapshot)
    reject(lambda: type(snapshot)(), "SNAPSHOT_CONSTRUCTION_REQUIRES_FACTORY")
    for forged in (object.__new__(type(snapshot)), copy.copy(snapshot), copy.deepcopy(snapshot)):
        assert not component.is_owned(forged)
        reject(lambda: component.key(forged), "UNOWNED_SNAPSHOT")
        reject(lambda: hash(forged), "UNOWNED_SNAPSHOT")
    try:
        snapshot.fields = None
        raise AssertionError("MUTABLE_SNAPSHOT")
    except FrozenInstanceError:
        pass
try:
    money.fields.amount = 3
    raise AssertionError("MUTABLE_FIELDS")
except FrozenInstanceError:
    pass
assert is_dataclass(type(order)) and typing.get_type_hints(o.OrderFields)["field__class"] is str
assert str(inspect.signature(m.create_money_factory)) == "()"
try:
    m.create_money_factory((), ())
    raise AssertionError("VALIDATOR_INJECTION")
except TypeError:
    pass
for forged in (copy.copy(mf), object.__new__(type(mf))):
    reject(lambda: forged.create({"amount": 2, "currency": "GBP"}), "UNOWNED_FACTORY")
reject(lambda: type(mf)(), "FACTORY_CONSTRUCTION_REQUIRES_PROVIDER")
gc.collect()
count = len(runtime._snapshots)
temporary = success(mf.create({"amount": 11, "currency": "GBP"}))
assert len(runtime._snapshots) == count + 1
del temporary
gc.collect()
assert len(runtime._snapshots) == count
# Native fault injection exercises Rule-exception failure; not a reflection sandbox claim.
def explode(_):
    raise RuntimeError("injected")
m._rule0 = explode
failed = mf.create({"amount": 2, "currency": "GBP"})
assert failed.ok is False and failed.value is None and failed.failure_codes[0].startswith("RULE_EXCEPTION:")
tree = ast.parse(root.joinpath(*prefix.split("."), "features/commerce/src/domain/entities/order.py").read_text())
snapshot = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "OrderSnapshot")
decorator = next(n for n in snapshot.decorator_list if isinstance(n, ast.Call))
assert {k.arg: ast.literal_eval(k.value) for k in decorator.keywords} == dict(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)
assert any(isinstance(n, ast.ImportFrom) and any(a.name == "rule_money_under_cap" for a in n.names) for n in tree.body)
print("PYTHON_FACTORIES_OK:" + str(hash(customer)))
`;
function materialize(f: ReturnType<typeof fixture>, p: ReturnType<typeof planConfiguredPythonFactories>, name: string, transform = (file: string, source: string) => source) {
  const root = path.join(f.temp, name);
  for (const a of p.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, transform(a.relative_path, a.content), {flag: 'wx'});}
  const script = path.join(root, 'observe.py'); fs.writeFileSync(script, native);
  return () => execFileSync('/usr/bin/python3', ['-I', '-B', script, root, p.selection.module_root.replaceAll('-', '_').replaceAll('/', '.')], {encoding: 'utf8', stdio: 'pipe'}).trim();
}

test('R10 Python factories bind complete owned data closure and declared Rules without effects', t => {
  const f = fixture(t), p = planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources);
  assert.equal(p.modules.length, 3); assert.equal(p.authority_effect, 'none');
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  assert.equal(p.artifacts.filter(a => a.relative_path.endsWith('/runtime/values.py')).length, 1);
  assert.equal(p.artifacts.filter(a => a.relative_path.endsWith('/runtime/factories.py')).length, 1);
  assert.deepEqual(planConfiguredPythonFactories(f.graph, f.fields, {...f.selection, factories: [...f.selection.factories].reverse()}, sources), p);
  assert.ok(Object.isFrozen(p.modules[0])); assert.deepEqual(fs.readdirSync(f.temp), ['source']);
  fs.rmSync(f.source, {recursive: true}); assert.deepEqual(planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources), p);
});

test('R10 native Python factories validate all routes and preserve ownership identity values and extensions', t => {
  const f = fixture(t), outputs: string[] = [];
  for (const module_root of ['domain-app', 'relocated/nested']) outputs.push(materialize(f, planConfiguredPythonFactories(f.graph, f.fields, {...f.selection, module_root}, sources), module_root.replaceAll('/', '-'))());
  assert.match(outputs[0]!, /^PYTHON_FACTORIES_OK:/); assert.equal(outputs[0], outputs[1]);
});

test('R10 Python factories reject missing invariants, mismatched arguments, active inputs and stale fields', t => {
  const f = fixture(t), run = (selection: any, selectedSources = sources) => planConfiguredPythonFactories(f.graph, f.fields, selection, selectedSources);
  assert.throws(() => planConfiguredPythonFactories({...f.graph}, f.fields, f.selection, sources));
  assert.throws(() => planConfiguredPythonFactories(f.graph, {...f.fields}, f.selection, sources));
  assert.throws(() => run({...f.selection, field_compilation_sha256: '0'.repeat(64)}), /current checked/);
  assert.throws(() => run({...f.selection, factories: []}), /binding list/);
  assert.throws(() => run({...f.selection, factories: f.selection.factories.slice(1)}), /coverage/);
  const changeMoney = (replace: (value: any) => any) => ({...f.selection, factories: f.selection.factories.map(b => b.selector === 'commerce:money' ? replace(structuredClone(b)) : b)});
  assert.throws(() => run(changeMoney(b => ({...b, base_validators: b.base_validators.slice(1)}))), /invariant coverage/);
  assert.throws(() => run(changeMoney(b => {b.base_validators[0].arguments[0].field = 'amount'; return b;})), /type mismatch/);
  assert.throws(() => run(changeMoney(b => {b.extensions[0].validators = [b.base_validators[0]]; return b;})), /duplicate/);
  assert.throws(() => run(changeMoney(b => {b.base_validators[0].arguments = []; return b;})), /parameter coverage/);
  assert.throws(() => run(changeMoney(b => {b.base_validators[1].arguments = [{parameter: 'value', path: ['note', 'extra']}]; return b;})), /must traverse required owned/);
  const referenceFields = compileSelectedProjectFields(f.graph, {...f.fields.selection, bindings: [{owner: 'commerce:order', field: 'class', kind: 'identity-reference', target: 'commerce:customer', projection: ['id']}]}, sources.field_contract);
  assert.throws(() => planConfiguredPythonFactories(f.graph, referenceFields, {...f.selection, field_compilation_sha256: referenceFields.compilation_sha256}, sources), /reference bindings require a Python reference adapter/);
  const active = {...f.selection}; Object.defineProperty(active, 'factories', {get() {throw new Error('ACTIVE');}, enumerable: true});
  assert.throws(() => run(active), /inert/);
  for (const key of Object.keys(sources)) assert.throws(() => run(f.selection, {...sources, [key]: sources[key as keyof typeof sources] + '\n'}), /drift/);
  assert.throws(() => run({...f.selection, module_root: 'domain\n'}), /unsafe/);
});

test('R10 native controls kill compiling validation-bypass identity and transition mutants', t => {
  const f = fixture(t), p = planConfiguredPythonFactories(f.graph, f.fields, f.selection, sources);
  const mutants = [
    {name: 'validators', leaf: '/runtime/factories.py', from: 'for validator in validators:', to: 'for validator in ():', failure: /EXPECTED_FAILURE:RULE_FAIL:commerce:valid-currency/},
    {name: 'identity', leaf: '/entities/customer.py', from: '("id",), "commerce:customer"', to: '("id", "label"), "commerce:customer"', failure: /ENTITY_IDENTITY_ONLY/},
    {name: 'transition', leaf: '/runtime/factories.py', from: 'if entity and previous is not None and', to: 'if False and', failure: /EXPECTED_FAILURE:IDENTITY_CHANGED/},
  ];
  for (const m of mutants) {
    let changes = 0;
    const observe = materialize(f, p, m.name, (file, source) => {if (file.endsWith(m.leaf) && source.includes(m.from)) {changes++; return source.replace(m.from, m.to);} return source;});
    assert.equal(changes, 1, m.name); assert.throws(observe, (e: any) => e.status === 1 && m.failure.test(e.stderr), m.name);
  }
});
