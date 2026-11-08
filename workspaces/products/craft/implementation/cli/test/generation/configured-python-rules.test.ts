import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonRules, PYTHON_RULE_VERSION} from '../../src/generation/configured-python-rules.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const wp = 'development/reconciliation-v1/profile-compiler-reconciliation/';
const sources = {configuration: read(wp + 'configuration.json'),
  base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  rule_contract: read(wp + 'string-order-rule-contract.json'), collection_contract: read(wp + 'rule-collection-value-contract.json'),
  predicate_contract: read(wp + 'rule-collection-predicate-contract.json'), numeric_contract: read(wp + 'rule-numeric-contract.json'),
  exact_contract: read(wp + 'rule-exact-contract.json'), literal_contract: read(wp + 'rule-exact-literal-contract.json')};
const scalar = (name: string): any => ({kind: 'scalar', name});
const parameter = (name: string, type: any = scalar('String')) => ({name, type});
const value = (root: string): any => ({op: 'path', root, properties: []});
const literal = (type: string, value: unknown): any => ({op: 'literal', type, value});
const eq = (left: any, right: any): any => ({op: 'eq', left, right});
function fixture(t: any, structured = false) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-rules-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source');
  const write = (file: string, content: unknown) => {const target = path.join(source, file); fs.mkdirSync(path.dirname(target), {recursive: true}); fs.writeFileSync(target, JSON.stringify(content) + '\n');};
  const list = {kind: 'list', element: scalar('UInt64')}, set = {kind: 'set', element: scalar('UInt64')};
  const rules: Record<string, any> = {
    'audit:is-enabled': {parameters: [parameter('enabled', scalar('Bool'))], expression: eq(value('enabled'), literal('Bool', true))},
    'commerce:is-enabled': {parameters: [parameter('enabled', scalar('Bool'))], expression: {op: 'not', term: eq(value('enabled'), literal('Bool', true))}},
    'commerce:label': {parameters: [parameter('label')], expression: {op: 'not', term: eq(value('label'), literal('String', ''))}},
    'commerce:can-submit': {parameters: [parameter('enabled', scalar('Bool')), parameter('label')], expression: {op: 'all', terms: [
      {op: 'rule_ref', selector: 'audit:is-enabled', arguments: [{parameter: 'enabled', value: value('enabled')}]},
      {op: 'rule_ref', selector: 'commerce:label', arguments: [{parameter: 'label', value: value('label')}]}]}},
    'commerce:string-order': {parameters: [parameter('left'), parameter('right')], expression: {op: 'lt', left: value('left'), right: value('right')}},
    'commerce:maximum': {parameters: [parameter('amount', scalar('UInt64'))], expression: eq(value('amount'), literal('UInt64', '18446744073709551615')), version: 2},
    'commerce:numeric-order': {parameters: [parameter('left', scalar('UInt64')), parameter('right', scalar('UInt64'))], expression: {op: 'lt', left: value('left'), right: value('right')}},
    'commerce:same-rows': {parameters: [parameter('left', list), parameter('right', list)], expression: eq(value('left'), value('right'))},
    'commerce:same-set': {parameters: [parameter('left', set), parameter('right', set)], expression: {op: 'set_equal', left: value('left'), right: value('right')}},
    'commerce:project-set': {parameters: [parameter('rows', list), parameter('expected', set)], expression: {op: 'set_equal', left: {op: 'to_set', value: value('rows')}, right: value('expected')}},
    'commerce:contains': {parameters: [parameter('rows', list), parameter('wanted', scalar('UInt64'))], expression: {op: 'contains', left: value('rows'), right: value('wanted')}},
    'commerce:optional': {parameters: [parameter('left', {kind: 'optional', element: scalar('String')}), parameter('right', {kind: 'optional', element: scalar('String')})], expression: eq(value('left'), value('right'))},
    'commerce:any': {parameters: [parameter('a', scalar('Bool')), parameter('b', scalar('Bool'))], expression: {op: 'any', terms: [eq(value('a'), literal('Bool', true)), eq(value('b'), literal('Bool', true))]}},
  };
  if (structured) rules['commerce:record-rule'] = {parameters: [parameter('order', {kind: 'named', selector: 'commerce:order'})], expression: eq({op: 'path', root: 'order', properties: ['FIXTURE-ORDER#id']}, literal('String', 'order-1'))};
  for (const op of ['exists', 'exactly_one', 'unique']) rules['commerce:' + op.replaceAll('_', '-')] = {parameters: [parameter('rows', list)], expression: {op, binding: 'item', collection: value('rows'), where: eq(value('item'), op === 'unique' ? value('item') : literal('UInt64', 2))}};
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-rules', features: ['commerce', 'audit'], cross_feature_edges: []});
  for (const feature_id of ['commerce', 'audit']) write(`specs/${feature_id}/feature.json`, {schema_version: 'domainspec.feature/v1', feature_id, nodes: [...Object.keys(rules).filter(s => s.startsWith(feature_id + ':')).map(s => s.split(':')[1]), ...(structured && feature_id === 'commerce' ? ['order'] : [])], edges: []});
  if (structured) write('specs/commerce/nodes/order.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: 'order', kind: 'Entity', body: {description: 'Record requires validated factory', fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-ORDER', properties: [{name: 'id', ontology_property: 'FIXTURE-ORDER#id', type: scalar('String'), identity: true, cardinality: 'one', meaning: 'identity'}]}}});
  for (const [selector, rule] of Object.entries(rules)) {
    const [feature_id, node_id] = selector.split(':');
    write(`specs/${feature_id}/nodes/${node_id}.json`, {schema_version: 'domainspec.node/v1', feature_id, node_id, kind: 'Rule', body: {description: selector, predicate: 'structured:domainspec.typed-rule/v1', typed_contract: {schema_version: 'domainspec.typed-rule/v' + (rule.version ?? 1), ontology_rule: 'FIXTURE-' + node_id!.toUpperCase(), parameters: rule.parameters, expression: rule.expression}}});
  }
  const graph = loadCompiledProjectGraph(source);
  const selection = {schema_version: PYTHON_RULE_VERSION, language: 'python' as const, module_root: 'domain-app', roots: Object.keys(rules)};
  return {temp, source, graph, selection};
}
const native = String.raw`
import ast
import importlib
from pathlib import Path
import sys
root, prefix = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root))
def load(name, feature="commerce"):
    return importlib.import_module(prefix + ".features." + feature + ".src.domain.rules." + name)
def rule(name, **parameters):
    return getattr(load(name), "rule_" + name)(parameters)
def reject(call, code):
    try:
        call()
        raise AssertionError("accepted invalid value: " + code)
    except TypeError as error:
        assert code in str(error), str(error)
assert rule("can_submit", enabled=True, label="order") is True
assert rule("can_submit", enabled=False, label="order") is False
assert rule("can_submit", enabled=True, label="") is False
assert rule("is_enabled", enabled=True) is False
assert load("is_enabled", "audit").rule_is_enabled({"enabled": True}) is True
assert rule("maximum", amount="18446744073709551615") is True
assert rule("maximum", amount=18446744073709551615) is True
assert rule("maximum", amount=18446744073709551614) is False
for bad in (True, False, -1, 18446744073709551616, 1.0, "01", "1\n", "\u0661"):
    reject(lambda: rule("maximum", amount=bad), "INVALID_UINT64")
assert rule("numeric_order", left="9007199254740992", right="9007199254740993") is True
assert rule("numeric_order", left=2, right="1") is False
assert rule("string_order", left="\U00010000", right="\ue000") is True, "UTF16_ORDER"
assert rule("string_order", left="\ud800\udc00", right="\U00010000") is False
assert rule("string_order", left="a", right="aa") is True
assert rule("optional", left=None, right=None) is True
assert rule("optional", left=None, right="") is False
assert rule("optional", left="\U00010000", right="\ud800\udc00") is True
assert rule("optional", left="\u00e9", right="e\u0301") is False
assert rule("same_rows", left=[1, "2", 1], right=[1, 2, "1"]) is True
assert rule("same_rows", left=[1, 2], right=[2, 1]) is False, "LIST_ORDER"
assert rule("same_rows", left=[1, 1], right=[1]) is False
assert rule("same_set", left=[1, 2], right=[2, "1"]) is True
reject(lambda: rule("same_set", left=[1, "1"], right=[1]), "DUPLICATE_SET_VALUE")
assert rule("project_set", rows=[1, "1", 2], expected=[2, 1]) is True
assert rule("contains", rows=[1, 2, 1], wanted="2") is True
assert rule("contains", rows=[], wanted=2) is False
assert rule("exactly_one", rows=[1, 2]) is True
assert rule("exactly_one", rows=[2, "2"]) is False, "OCCURRENCE_COUNT"
assert rule("exists", rows=[2, 2]) is True
assert rule("exists", rows=[]) is False
assert rule("unique", rows=[]) is True
assert rule("unique", rows=[1, 2]) is True
assert rule("unique", rows=[1, "1"]) is False
for a in (False, True):
    for b in (False, True):
        assert rule("any", a=a, b=b) is (a or b)
reject(lambda: rule("can_submit", enabled=1, label="x"), "INVALID_BOOL")
reject(lambda: rule("label", label=1), "INVALID_STRING")
reject(lambda: rule("label"), "RULE_INPUT")
reject(lambda: rule("label", label="x", extra=True), "RULE_INPUT")
class Active(dict):
    def __iter__(self):
        raise AssertionError("ACTIVE_INPUT")
class ActiveList(list):
    def __iter__(self):
        raise AssertionError("ACTIVE_LIST")
reject(lambda: load("label").rule_label(Active(label="x")), "RULE_INPUT")
reject(lambda: rule("same_rows", left=ActiveList([1]), right=[1]), "INVALID_COLLECTION")
reject(lambda: rule("same_rows", left=iter([1]), right=[1]), "INVALID_COLLECTION")
# Observe syntax and direct qualified-leaf relationships independently of receipts.
source = root.joinpath(*prefix.split("."), "features/commerce/src/domain/rules/can_submit.py")
tree = ast.parse(source.read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "rule_can_submit")
assert ast.unparse(function.returns) == "bool"
imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and any(a.name.startswith("rule_") for a in n.names)]
assert {(n.level, n.module, n.names[0].name) for n in imports} == {(5, "audit.src.domain.rules.is_enabled", "rule_is_enabled"), (1, "label", "rule_label")}
assert {n.func.id for n in ast.walk(function) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.startswith("_dependency")} == {"_dependency0", "_dependency1"}
assert not any(isinstance(n, (ast.ClassDef, ast.AsyncFunctionDef)) for n in tree.body)
print("PYTHON_RULES_OK")
`;
function materialize(f: ReturnType<typeof fixture>, plan: ReturnType<typeof planConfiguredPythonRules>, name: string, transform = (file: string, content: string) => content) {
  const root = path.join(f.temp, name);
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, transform(a.relative_path, a.content), {flag: 'wx'});}
  const script = path.join(root, 'observe.py'); fs.writeFileSync(script, native);
  return () => execFileSync('/usr/bin/python3', ['-I', '-B', script, root, plan.selection.module_root.replaceAll('-', '_').replaceAll('/', '.')], {encoding: 'utf8', stdio: 'pipe'});
}

test('R10 Python Rules bind checked closure and frozen sources with stable qualified leaf artifacts', t => {
  const f = fixture(t), p = planConfiguredPythonRules(f.graph, f.selection, sources);
  assert.equal(p.modules.length, 16); assert.equal(p.authority_effect, 'none');
  assert.equal(p.artifacts.filter(a => a.relative_path.endsWith('/runtime/values.py')).length, 1);
  const {plan_sha256, ...body} = p; assert.equal(sha256(canonicalJson(body)), plan_sha256);
  assert.deepEqual(planConfiguredPythonRules(f.graph, {...f.selection, roots: [...f.selection.roots].reverse()}, sources), p);
  assert.ok(Object.isFrozen(p.modules[0]));
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  assert.deepEqual(fs.readdirSync(f.temp), ['source']);
  fs.rmSync(f.source, {recursive: true});
  assert.deepEqual(planConfiguredPythonRules(f.graph, f.selection, sources), p);
  const closure = planConfiguredPythonRules(f.graph, {...f.selection, roots: ['commerce:can-submit']}, sources);
  assert.deepEqual(closure.modules.map(m => m.selector), ['audit:is-enabled', 'commerce:can-submit', 'commerce:label']);
});

test('R10 Python Rule plans reject stale, forged, active and unsafe selection inputs', t => {
  const f = fixture(t);
  assert.throws(() => planConfiguredPythonRules({...f.graph}, f.selection, sources));
  for (const module_root of ['../escape', 'class', 'hashlib', 'typing', 'a\n', 'valid/a\n']) assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, module_root}, sources));
  for (const key of Object.keys(sources)) assert.throws(() => planConfiguredPythonRules(f.graph, f.selection, {...sources, [key]: sources[key as keyof typeof sources] + '\n'}), /source drift/);
  assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, extra: true} as any, sources), /closed/);
  assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, roots: []}, sources));
  assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, roots: ['commerce:label', 'commerce:label']}, sources), /duplicate/);
  const active = {...f.selection}; Object.defineProperty(active, 'module_root', {enumerable: true, get() {throw new Error('ACTIVE');}});
  assert.throws(() => planConfiguredPythonRules(f.graph, active, sources), /closed/);
  const roots: string[] = []; Object.defineProperty(roots, 0, {get() {throw new Error('ACTIVE');}});
  assert.throws(() => planConfiguredPythonRules(f.graph, {...f.selection, roots}, sources), /inert/);
  const record = fixture(t, true);
  assert.throws(() => planConfiguredPythonRules(record.graph, record.selection, sources), /structured dependency requires a Python fact adapter:commerce:order/);
  assert.throws(() => planConfiguredPythonRules(record.graph, {...record.selection, roots: ['commerce:order']}, sources), /selected root must be a typed Rule/);
});

test('R10 native Python Rule functions preserve exact values, every selected operator and relocated imports', t => {
  const f = fixture(t);
  for (const module_root of ['domain-app', 'relocated/nested']) {
    const p = planConfiguredPythonRules(f.graph, {...f.selection, module_root}, sources);
    assert.equal(materialize(f, p, module_root.replaceAll('/', '-'))().trim(), 'PYTHON_RULES_OK');
  }
});

test('R10 independent native checks kill compiling Python Bool, Unicode-order and occurrence mutants', t => {
  const f = fixture(t), p = planConfiguredPythonRules(f.graph, f.selection, sources);
  const mutants = [
    {name: 'bool', pattern: 'if type(value) is int:', replacement: 'if isinstance(value, int):', failure: /accepted invalid value: INVALID_UINT64/},
    {name: 'order', pattern: 'p0.encode("utf-16-be", "surrogatepass") < p1.encode("utf-16-be", "surrogatepass")', replacement: 'p0 < p1', failure: /UTF16_ORDER/},
    {name: 'occurrence', pattern: 'sum(1 for q0 in p0 if', replacement: 'sum(1 for q0 in set(p0) if', failure: /OCCURRENCE_COUNT/},
  ];
  for (const mutant of mutants) {
    let changes = 0;
    const observe = materialize(f, p, mutant.name, (_file, content) => {if (content.includes(mutant.pattern)) {changes++; return content.replace(mutant.pattern, mutant.replacement);} return content;});
    assert.equal(changes, 1);
    assert.throws(observe, (error: any) => error.status === 1 && mutant.failure.test(error.stderr));
  }
});
