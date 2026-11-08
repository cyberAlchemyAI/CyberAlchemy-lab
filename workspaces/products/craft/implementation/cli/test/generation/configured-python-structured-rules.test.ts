import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {compileSelectedProjectFields, compiledFieldValueKey, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {planConfiguredPythonRules, PYTHON_RULE_VERSION, PYTHON_STRUCTURED_RULE_VERSION} from '../../src/generation/configured-python-rules.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), wp = 'development/reconciliation-v1/profile-compiler-reconciliation/';
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const sources = {configuration: read(wp + 'configuration.json'), base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  rule_contract: read(wp + 'string-order-rule-contract.json'), collection_contract: read(wp + 'rule-collection-value-contract.json'), predicate_contract: read(wp + 'rule-collection-predicate-contract.json'),
  numeric_contract: read(wp + 'rule-numeric-contract.json'), exact_contract: read(wp + 'rule-exact-contract.json'), literal_contract: read(wp + 'rule-exact-literal-contract.json'),
  structured_contract: read(wp + 'rule-structured-value-contract.json'), field_contract: read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const scalar = (name = 'String'): any => ({kind: 'scalar', name});
const named = (id: string): any => ({kind: 'named', selector: 'commerce:' + id});
const wrap = (kind: string, element: any): any => ({kind, element});
const at = (root: string, ...properties: string[]): any => ({op: 'path', root, properties});
const lit = (type: string, value: unknown): any => ({op: 'literal', type, value});
const eq = (left: any, right: any): any => ({op: 'eq', left, right});
const variant = (name: string, payload: any = null) => ({name, ontology_variant: 'FIXTURE-RESULT#' + name, payload});
const sum: any = {kind: 'sum', variants: [variant('None'), variant('Amount', scalar('UInt64')), variant('Money', named('money')), variant('Maybe', wrap('optional', scalar()))]};
const property = (owner: string, name: string, type: any, identity = false) => ({name, type, identity, cardinality: type.kind === 'optional' ? 'optional' : type.kind === 'list' ? 'many' : type.kind === 'set' ? 'many-unique' : 'one', meaning: name, ontology_property: 'FIXTURE-' + owner + '#' + name});
function fixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-facts-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [], rules: string[] = [];
  const write = (file: string, content: unknown) => {const p = path.join(source, file); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(content) + '\n');};
  const node = (id: string, kind: string, body: object) => {nodes.push(id); write(`specs/commerce/nodes/${id}.json`, {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const record = (id: string, kind: string, properties: any[]) => node(id, kind, {fields: properties.map(p => p.name), ...(kind === 'Value Object' ? {invariant_refs: ['commerce:valid']} : {}), typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), properties}});
  record('money', 'Value Object', [property('MONEY', 'amount', scalar('UInt64')), property('MONEY', 'currency', scalar()), property('MONEY', 'note', wrap('optional', scalar()))]);
  record('customer', 'Entity', [property('CUSTOMER', 'id', scalar(), true), property('CUSTOMER', 'label', scalar()), property('CUSTOMER', 'balance', named('money'))]);
  for (const [id, variants] of [['status', [variant('Pending'), variant('Ready')]], ['result', sum.variants]] as const) node(id, 'Enum', {values: variants.map((v: any) => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), variants}});
  const rule = (id: string, parameters: any[], expression: any) => {rules.push('commerce:' + id); node(id, 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'RULE-' + id.toUpperCase(), parameters, expression}});};
  const p = (name: string, type: any) => ({name, type});
  rule('valid', [p('currency', scalar())], {op: 'not', term: eq(at('currency'), lit('String', ''))});
  for (const [id, type] of Object.entries({entity: named('customer'), value: named('money'), sum, status: named('status'), result: named('result'), nested: wrap('list', wrap('set', named('money')))})) rule('equal-' + id, [p('left', type), p('right', type)], eq(at('left'), at('right')));
  rule('ready', [p('status', named('status'))], eq(at('status'), {op: 'variant', selector: 'FIXTURE-RESULT#Ready'}));
  rule('balance', [p('customer', named('customer')), p('cap', scalar('UInt64'))], {op: 'lt', left: at('customer', 'FIXTURE-CUSTOMER#balance', 'FIXTURE-MONEY#amount'), right: at('cap')});
  rule('forward', [p('customer', named('customer')), p('cap', scalar('UInt64'))], {op: 'rule_ref', selector: 'commerce:balance', arguments: [{parameter: 'customer', value: at('customer')}, {parameter: 'cap', value: at('cap')}]});
  for (const kind of ['list', 'set']) {
    rule('project-' + kind, [p('customers', wrap(kind, named('customer'))), p('labels', wrap(kind, scalar()))], eq(at('customers', 'FIXTURE-CUSTOMER#label'), at('labels')));
    rule('contains-' + kind, [p('customers', wrap(kind, named('customer'))), p('customer', named('customer'))], {op: 'contains', left: at('customers'), right: at('customer')});
  }
  rule('unique', [p('customers', wrap('list', named('customer')))], {op: 'unique', binding: 'c', collection: at('customers'), where: eq(at('c', 'FIXTURE-CUSTOMER#balance'), at('c', 'FIXTURE-CUSTOMER#balance'))});
  rule('one', [p('customers', wrap('list', named('customer')))], {op: 'exactly_one', binding: 'c', collection: at('customers'), where: eq(at('c', 'FIXTURE-CUSTOMER#label'), lit('String', 'Alex'))});
  rule('exists', [p('customers', wrap('list', named('customer')))], {op: 'exists', binding: 'c', collection: at('customers'), where: {op: 'lt', left: at('c', 'FIXTURE-CUSTOMER#balance', 'FIXTURE-MONEY#amount'), right: lit('UInt64', '18446744073709551615')}});
  rule('image', [p('customers', wrap('list', named('customer'))), p('labels', wrap('set', scalar()))], {op: 'set_equal', left: {op: 'to_set', value: at('customers', 'FIXTURE-CUSTOMER#label')}, right: at('labels')});
  // Retaining the first duplicate Entity is observable through its non-identity state.
  rule('first-state', [p('customers', wrap('list', named('customer')))], {op: 'exists', binding: 'c', collection: {op: 'to_set', value: at('customers')}, where: eq(at('c', 'FIXTURE-CUSTOMER#label'), lit('String', 'First'))});
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-facts', features: ['commerce'], cross_feature_edges: []});
  write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges: []});
  const graph = loadCompiledProjectGraph(source), selection = {schema_version: PYTHON_STRUCTURED_RULE_VERSION, language: 'python' as const, module_root: 'domain-app', roots: rules};
  return {temp, source, graph, selection};
}

const native = String.raw`
import ast
import importlib
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
root, prefix = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root))
def load(name):
    return importlib.import_module(prefix + ".features.commerce.src.domain.rules." + name)
def run(name, **parameters):
    return getattr(load(name), "rule_" + name)(parameters)
def money(amount=2, currency="GBP", **extra):
    return dict(amount=amount, currency=currency, **extra)
def customer(id="a", label="Alex", balance=None):
    return dict(id=id, label=label, balance=money() if balance is None else balance)
def reject(call, code="RULE_INPUT"):
    try:
        call()
        raise AssertionError("accepted invalid facts: " + code)
    except TypeError as error:
        assert code in str(error), str(error)
assert run("equal_entity", left=customer(), right=customer("a", "Changed", money(9))) is True, "ENTITY_IDENTITY_ONLY"
assert run("equal_entity", left=customer(), right=customer("b")) is False, "DISTINCT_ENTITY_IDENTITY"
assert run("equal_value", left=money(), right=money("2", note=None)) is True
assert run("equal_value", left=money(), right=money(3)) is False, "COMPLETE_VALUE"
assert run("equal_value", left=money(), right=money(2, "USD")) is False
assert run("equal_value", left=money(), right=money(note="")) is False
# Rule facts are not construction: invariants are not silently run.
assert run("equal_value", left=money(currency=""), right=money(currency="")) is True
assert run("valid", currency="") is False
assert run("equal_value", left=money("18446744073709551615"), right=money(18446744073709551615)) is True
reject(lambda: run("equal_entity", left=customer(), right=customer("a", balance=money(True))), "INVALID_UINT64")
for incomplete in ({"amount": 2}, {"currency": "GBP"}, {"amount": 2, "currency": "GBP", "extra": 1}):
    reject(lambda: run("equal_value", left=incomplete, right=money()))
assert run("equal_sum", left={"variant": "None"}, right={"variant": "Maybe", "payload": None}) is False
assert run("equal_sum", left={"variant": "Maybe", "payload": None}, right={"variant": "Maybe", "payload": ""}) is False
assert run("equal_sum", left={"variant": "Money", "payload": money()}, right={"variant": "Money", "payload": money("2")}) is True
assert run("equal_result", left={"variant": "Amount", "payload": "18446744073709551615"}, right={"variant": "Amount", "payload": 18446744073709551615}) is True
assert run("equal_status", left={"variant": "Ready"}, right={"variant": "Pending"}) is False
assert run("ready", status={"variant": "Ready"}) is True
assert run("ready", status={"variant": "Pending"}) is False
for malformed in ({"variant": "None", "payload": None}, {"variant": "Amount"}, {"variant": "Other"}, {"variant": "Amount", "payload": 2, "extra": 0}):
    reject(lambda: run("equal_sum", left=malformed, right={"variant": "None"}))
assert run("equal_nested", left=[[money(2), money(3)]], right=[[money("3"), money("2")]]) is True
reject(lambda: run("equal_nested", left=[[money(2), money("2")]], right=[]), "DUPLICATE_SET_VALUE")
assert run("balance", customer=customer(), cap=3) is True
assert run("balance", customer=customer(), cap=2) is False
assert run("forward", customer=customer(), cap=3) is True
assert run("forward", customer=customer(), cap=2) is False
assert run("project_list", customers=[customer(), customer("b")], labels=["Alex", "Alex"]) is True
assert run("project_list", customers=[customer(), customer("b")], labels=["Alex"]) is False
assert run("project_set", customers=[customer(), customer("b")], labels=["Alex"]) is True
reject(lambda: run("project_set", customers=[customer(), customer("a", "Changed")], labels=["Alex"]), "DUPLICATE_SET_VALUE")
assert run("contains_list", customers=[customer()], customer=customer("a", "Other")) is True
assert run("contains_set", customers=[customer()], customer=customer("b")) is False
assert run("unique", customers=[customer(), customer("b")]) is False
assert run("unique", customers=[customer(), customer("b", balance=money(3))]) is True
assert run("one", customers=[customer(), customer()]) is False
assert run("one", customers=[customer(), customer("b", "Other")]) is True
assert run("exists", customers=[customer()]) is True
assert run("exists", customers=[]) is False
assert run("image", customers=[customer(), customer("b")], labels=["Alex"]) is True
assert run("first_state", customers=[customer("a", "First"), customer("a", "Last")]) is True, "FIRST_OCCURRENCE"
assert run("first_state", customers=[customer("a", "Last"), customer("a", "First")]) is False
class Active(dict):
    def get(self, name):
        raise AssertionError("ACTIVE_FACT")
reject(lambda: run("equal_value", left=Active(money()), right=money()))
facts = importlib.import_module(prefix + ".runtime.facts")
v = importlib.import_module(prefix + ".runtime.values")
# Selected structured-Rule keys, independent of the provider component protocol.
assert facts.optional_fact(v.STRING).key(None) == "6:absent"
assert facts.optional_fact(v.STRING).key("a") == "7:present11:6:String1:a"
assert facts.sequence_fact(v.STRING, False).key(("a", "b")) == "4:list1:211:6:String1:a11:6:String1:b"
assert facts.sequence_fact(v.STRING, True).key(("a", "b")) == "3:set1:211:6:String1:a11:6:String1:b"
component = facts.record_fact("Value Object", "commerce:probe", (("rows", v.list_value(v.UINT64), False),), ("rows",))
rows = [1, "2"]
fact = component.normalize({"rows": rows})
rows.append(3)
assert fact["rows"] == (1, 2)
assert component.is_owned(fact) is False  # Never a validated domain object.
assert component.normalize(fact)["rows"] == (1, 2)
try:
    fact.entries = ()
    raise AssertionError("MUTABLE_FACT")
except FrozenInstanceError:
    pass
reject(lambda: component.normalize(facts._Fact((("rows", [1]), ("rows", [2])))))
tree = ast.parse(root.joinpath(*prefix.split("."), "features/commerce/src/domain/rules/balance.py").read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "rule_balance")
result = next(n for n in fn.body if isinstance(n, ast.Return))
assert ast.unparse(result.value) == "p0['balance']['amount'] < p1"
print("PYTHON_STRUCTURED_RULES_OK")
`;
function materialize(f: ReturnType<typeof fixture>, plan: ReturnType<typeof planConfiguredPythonRules>, name: string, transform = (file: string, content: string) => content) {
  const root = path.join(f.temp, name);
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, transform(a.relative_path, a.content), {flag: 'wx'});}
  const script = path.join(root, 'observe.py'); fs.writeFileSync(script, native);
  return () => execFileSync('/usr/bin/python3', ['-I', '-B', script, root, plan.selection.module_root.replaceAll('-', '_').replaceAll('/', '.')], {encoding: 'utf8', stdio: 'pipe'});
}

test('R10 structured Python Rule plans bind full checked facts without widening the scalar selection', t => {
  const f = fixture(t), p = planConfiguredPythonRules(f.graph, f.selection, sources);
  assert.equal(p.schema_version, 'domainspec.configured-python-rules-plan/v2-candidate'); assert.ok(p.field_model_sha256);
  assert.equal(p.modules.length, 19); assert.equal(p.authority_effect, 'none');
  assert.equal(p.artifacts.filter(a => a.relative_path.endsWith('/facts.py')).length, 1);
  assert.ok(Object.isFrozen(p.artifacts[0]));
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  assert.deepEqual(planConfiguredPythonRules(f.graph, {...f.selection, roots: [...f.selection.roots].reverse()}, sources), p);
  const {structured_contract, field_contract, ...old} = sources;
  assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, schema_version: PYTHON_RULE_VERSION}, old), /structured dependency/);
  for (const key of ['structured_contract', 'field_contract']) assert.throws(() => planConfiguredPythonRules(f.graph, f.selection, {...sources, [key]: sources[key as keyof typeof sources] + ' '}), /drift/);
  fs.rmSync(f.source, {recursive: true});
  assert.deepEqual(planConfiguredPythonRules(f.graph, f.selection, sources), p);
});

test('R10 native structured Python Rules preserve identity, complete value, sum, projection and occurrence semantics', t => {
  const f = fixture(t);
  for (const module_root of ['domain-app', 'relocated/nested']) assert.equal(materialize(f, planConfiguredPythonRules(f.graph, {...f.selection, module_root}, sources), module_root.replaceAll('/', '-'))().trim(), 'PYTHON_STRUCTURED_RULES_OK');
  // Independent source-side equality observations, not generator assertions.
  const fields = compileSelectedProjectFields(f.graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: createCompiledProjectCertificate(f.graph).graph_sha256, roots: ['commerce:customer'], bindings: []}, sources.field_contract);
  const customer = (id: string, label: string, amount = 2) => ({id, label, balance: {amount, currency: 'GBP'}});
  assert.equal(compiledFieldValueKey(fields, 'commerce:customer', customer('a', 'First')), compiledFieldValueKey(fields, 'commerce:customer', customer('a', 'Last', 9)));
  assert.notEqual(compiledFieldValueKey(fields, 'commerce:customer', customer('a', 'First')), compiledFieldValueKey(fields, 'commerce:customer', customer('b', 'First')));
});

test('R10 native counterexamples kill compiling identity, complete-value and first-occurrence mutations', t => {
  const f = fixture(t), p = planConfiguredPythonRules(f.graph, f.selection, sources);
  const mutants = [
    {name: 'identity', leaf: 'equal_entity.py', from: '("id",))', to: '("label",))', failure: /ENTITY_IDENTITY_ONLY/},
    {name: 'complete-value', leaf: 'equal_value.py', from: '("amount", "currency", "note",))', to: '("currency",))', failure: /COMPLETE_VALUE/},
    {name: 'last-occurrence', leaf: 'first_state.py', from: 'keyed.setdefault(element.key(item), item)', to: 'keyed[element.key(item)] = item', failure: /FIRST_OCCURRENCE/},
  ];
  for (const m of mutants) {
    let changes = 0;
    const observe = materialize(f, p, m.name, (file, source) => {if (file.endsWith('/' + m.leaf) && source.includes(m.from)) {changes++; return source.replace(m.from, m.to);} return source;});
    assert.equal(changes, 1, m.name);
    assert.throws(observe, (e: any) => e.status === 1 && m.failure.test(e.stderr), m.name);
  }
});
