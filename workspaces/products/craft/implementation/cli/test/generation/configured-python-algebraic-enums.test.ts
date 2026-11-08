import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, compiledFieldValueKey, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonAlgebraicEnums, PYTHON_ALGEBRAIC_ENUM_VERSION} from '../../src/generation/configured-python-algebraic-enums.ts';
import {renderPythonValueSupport} from '../../src/generation/configured-python-value-source.ts';
import {renderPythonEventValues} from '../../src/generation/configured-python-event-values.ts';

test('Python shared list/set and Event decimal reject active metaclasses without equality or conversion',()=>{
 const output=execFileSync('/usr/bin/python3',['-B','-c',`
import json,sys,types
sources=json.load(sys.stdin)
modules=[]
for name,source in sources.items():
    module=types.ModuleType(name)
    sys.modules[name]=module
    exec(compile(source,name,"exec"),module.__dict__)
    modules.append(module)
values,events=modules
for spoof in (False,True):
    effects=[]
    class ActiveMeta(type):
        def __eq__(cls,other):
            effects.append("equality")
            return spoof
    class Hostile(metaclass=ActiveMeta):
        def __iter__(self):
            effects.append("iteration")
            return iter(())
        def __float__(self):
            effects.append("conversion")
            return 1.0
    for normalize in (values.list_value(values.STRING).normalize,values.set_value(values.STRING).normalize,events.decimal):
        try:
            normalize(Hostile())
        except TypeError:
            pass
        else:
            raise AssertionError("ACTIVE_INPUT_ACCEPTED")
    assert not effects, "ACTIVE_METACLASS_EXECUTED:"+repr(effects)
assert values.list_value(values.UINT64).normalize(["2",1]) == (2,1)
assert values.set_value(values.UINT64).normalize(["2",1]) == (1,2)
assert events.decimal(2) == 2.0 and events.decimal(-0.0) == 0.0
try:
    events.decimal(True)
except TypeError:
    pass
else:
    raise AssertionError("BOOL_DECIMAL_COLLAPSE")
print("INERT_TYPES_OK")
`],{input:JSON.stringify({values:renderPythonValueSupport(),event_values:renderPythonEventValues()}),encoding:'utf8',stdio:['pipe','pipe','pipe']});
 assert.match(output,/INERT_TYPES_OK/);
});

const project = path.resolve(import.meta.dirname, '../../../..');
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const sources = {configuration: read('development/reconciliation-v1/profile-compiler-reconciliation/configuration.json'),
  base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
  field_contract: read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
function fixture(t: any, collision = false, record = false) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-sums-'));t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source');
  const write = (file: string, value: unknown) => {const target = path.join(source, file);fs.mkdirSync(path.dirname(target), {recursive: true});fs.writeFileSync(target, JSON.stringify(value) + '\n');};
  const scalar = (name: string): any => ({kind: 'scalar', name});
  const variant = (name: string, payload: any = null) => ({name, ontology_variant: 'FIXTURE-CASE#' + name, payload});
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-sums', features: ['commerce', 'audit'], cross_feature_edges: []});
  for (const feature_id of ['commerce', 'audit']) {
    const enums = [{id: 'currency', variants: [variant('USD'), variant('EUR')]},
      {id: 'answer', variants: [variant('None'), variant('Amount', scalar('UInt64')), variant('Maybe', {kind: 'optional', element: scalar('String')}),
        variant('Rows', {kind: 'list', element: scalar('UInt64')}), variant('Tags', {kind: 'set', element: scalar('String')}),
        variant('UniqueAmounts', {kind: 'set', element: scalar('UInt64')}), variant('Flag', scalar('Bool')),
        variant('Currency', {kind: 'named', selector: feature_id + ':currency'}),
        variant('Choice', {kind: 'sum', variants: [variant('Text', scalar('String')), variant('Count', scalar('UInt64'))]})]},
      {id: 'wrapper', variants: [variant('Absent'), variant('Nested', {kind: 'named', selector: feature_id + ':answer'}), variant('Rows', {kind: 'list', element: {kind: 'named', selector: feature_id + ':answer'}})]},
      ...(collision ? [{id: 'answer-sum', variants: [variant('Other')]}] : [])];
    write(`specs/${feature_id}/feature.json`, {schema_version: 'domainspec.feature/v1', feature_id, nodes: [...enums.map(e => e.id), ...(record ? ['order'] : [])], edges: []});
    if (record) write(`specs/${feature_id}/nodes/order.json`, {schema_version: 'domainspec.node/v1', feature_id, node_id: 'order', kind: 'Entity', body: {description: 'Needs validated factory', fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-ORDER', properties: [{name: 'id', ontology_property: 'FIXTURE-ORDER#id', type: scalar('String'), identity: true, cardinality: 'one', meaning: 'identity'}]}}});
    for (const e of enums) write(`specs/${feature_id}/nodes/${e.id}.json`, {schema_version: 'domainspec.node/v1', feature_id, node_id: e.id, kind: 'Enum', body: {description: 'Native sums', values: e.variants.map(v => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + feature_id.toUpperCase() + '-' + e.id.toUpperCase(), variants: e.variants}}});
  }
  const graph = loadCompiledProjectGraph(source);
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256,
    graph_sha256: createCompiledProjectCertificate(graph).graph_sha256, roots: ['commerce:wrapper', 'audit:wrapper', ...(collision ? ['commerce:answer-sum'] : []), ...(record ? ['commerce:order'] : [])], bindings: []}, sources.field_contract);
  const selection = {schema_version: PYTHON_ALGEBRAIC_ENUM_VERSION, language: 'python' as const, module_root: 'domain-app', field_compilation_sha256: fields.compilation_sha256};
  return {temp, source, graph, fields, selection};
}

const native = String.raw`
import ast
import copy
import gc
import importlib
import json
from pathlib import Path
import sys
import weakref
from dataclasses import FrozenInstanceError

root, prefix = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root))
def load(feature, name):
    return importlib.import_module(prefix + ".features." + feature + ".src.domain.enums." + name)
a, b = load("commerce", "answer_sum"), load("audit", "answer_sum")
w = load("commerce", "wrapper_sum")
currency, other_currency = load("commerce", "currency"), load("audit", "currency")
runtime = importlib.import_module(prefix + ".runtime.values")
create = a.create_answer
def case(variant, payload):
    return create({"variant": variant, "payload": payload})
def reject(call, code):
    try:
        call()
        raise AssertionError("accepted invalid value: " + code)
    except TypeError as error:
        assert code in str(error), str(error)

maximum = case("Amount", "18446744073709551615")
assert maximum.payload == 18446744073709551615 and type(maximum.payload) is int
assert maximum == case("Amount", 18446744073709551615)
assert hash(maximum) == hash(case("Amount", 18446744073709551615))
assert maximum != b.create_answer({"variant": "Amount", "payload": "18446744073709551615"})
for value in (True, False, -1, 18446744073709551616, 1.0, "01", "-0", "+1", "1.0", "1\n", "\u0661", "9" * 10000):
    reject(lambda value=value: case("Amount", value), "INVALID_UINT64")
assert case("Flag", True) != case("Flag", False)
for value in (0, 1, "true", None):
    reject(lambda value=value: case("Flag", value), "INVALID_BOOL")
rows = [1, "2", 1]
value = case("Rows", rows)
rows.append(9)
assert value.payload == (1, 2, 1)
assert value != case("Rows", [1, 1, 2])
assert value != case("Rows", [1, 2])
assert case("Tags", ["b", "a"]) == case("Tags", ["a", "b"])
reject(lambda: case("Tags", ["a", "a"]), "DUPLICATE_SET_VALUE")
reject(lambda: case("UniqueAmounts", [1, "1"]), "DUPLICATE_SET_VALUE")
assert case("Maybe", None) != create({"variant": "None"})
assert case("Maybe", None) != case("Maybe", "")
assert case("Maybe", "\U0001f600") == case("Maybe", "\ud83d\ude00")
assert case("Maybe", "\u00e9") != case("Maybe", "e\u0301")
reject(lambda: case("Tags", ["\U0001f600", "\ud83d\ude00"]), "DUPLICATE_SET_VALUE")
usd = currency.parse_currency("USD")
assert case("Currency", usd).payload is usd
reject(lambda: case("Currency", "USD"), "UNOWNED_ENUM_CASE")
reject(lambda: case("Currency", other_currency.parse_currency("USD")), "UNOWNED_ENUM_CASE")
choice = case("Choice", {"variant": "Count", "payload": "2"})
assert choice.payload.variant == "Count" and choice.payload.payload == 2
assert choice != case("Choice", {"variant": "Text", "payload": "2"})
wrapped = w.create_wrapper({"variant": "Nested", "payload": maximum})
assert wrapped.payload is maximum
assert w.create_wrapper({"variant": "Rows", "payload": [maximum, maximum]}).payload == (maximum, maximum)
reject(lambda: w.create_wrapper({"variant": "Nested", "payload": {"variant": "Amount", "payload": 1}}), "UNOWNED_COMPONENT")
reject(lambda: w.create_wrapper({"variant": "Nested", "payload": b.create_answer({"variant": "Amount", "payload": 1})}), "UNOWNED_COMPONENT")
for value in ({}, {"variant": "Unknown"}, {"variant": "Amount"}, {"variant": "None", "payload": None}, {"variant": "None", "extra": True}):
    reject(lambda value=value: create(value), "INVALID_SUM")
class Active(dict):
    def get(self, key):
        raise AssertionError("active get")
class ActiveList(list):
    def __iter__(self):
        raise AssertionError("active iteration")
reject(lambda: create(Active(variant="None")), "INVALID_SUM")
reject(lambda: case("Rows", ActiveList([1])), "INVALID_COLLECTION")
reject(lambda: case("Rows", {1, 2}), "INVALID_COLLECTION")
reject(lambda: a.AnswerVariantAmount(), "SUM_CONSTRUCTION_REQUIRES_COMPONENT")
for forged in (object.__new__(a.AnswerVariantAmount), copy.copy(maximum), copy.deepcopy(maximum)):
    assert not a.AnswerValueComponent.is_owned(forged)
    reject(lambda forged=forged: a.AnswerValueComponent.key(forged), "UNOWNED_SUM_CASE")
    reject(lambda forged=forged: hash(forged), "UNOWNED_SUM_CASE")
try:
    maximum.payload = 0
    raise AssertionError("mutable case")
except FrozenInstanceError:
    pass
try:
    choice.payload.payload = 0
    raise AssertionError("mutable nested case")
except FrozenInstanceError:
    pass
assert not hasattr(maximum, "__dict__")
temporary = case("Amount", 10)
reference = weakref.ref(temporary)
del temporary
gc.collect()
assert reference() is None
observed = []
for feature in ("audit", "commerce"):
    file = root.joinpath(*prefix.split("."), "features", feature, "src", "domain", "enums", "answer_sum.py")
    tree = ast.parse(file.read_text())
    compile(tree, str(file), "exec")
    definitions = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    wanted = {"Amount", "Choice", "Currency", "Flag", "Maybe", "None", "Rows", "Tags", "UniqueAmounts"}
    assert {name.removeprefix("AnswerVariant") for name in definitions if name.startswith("AnswerVariant")} == wanted
    for name in ("AnswerVariantAmount", "AnswerVariantRows"):
        d = definitions[name]
        settings = {k.arg: ast.literal_eval(k.value) for k in d.decorator_list[0].keywords}
        assert settings == {"frozen": True, "slots": True, "eq": False, "init": False, "weakref_slot": True}
        assert [ast.unparse(base) for base in d.bases] == ["_OwnedCase"]
    annotations = {n.target.id: ast.unparse(n.annotation) for n in definitions["AnswerVariantAmount"].body if isinstance(n, ast.AnnAssign)}
    assert annotations["payload"] == "int"
    observed.append(feature)
print(json.dumps({"status": "pass", "observed": observed, "python": sys.version.split()[0], "hash": str(hash(maximum))}))
`;
function materialize(root: string, artifacts: readonly {relative_path: string; content: string}[]) {
  for (const a of artifacts) {const file = path.join(root, a.relative_path);fs.mkdirSync(path.dirname(file), {recursive: true});fs.writeFileSync(file, a.content, {flag: 'wx'});}
  const script = path.join(root, 'observe.py');fs.writeFileSync(script, native);
  return (prefix: string) => JSON.parse(execFileSync('/usr/bin/python3', ['-I', '-B', script, root, prefix], {encoding: 'utf8', stdio: 'pipe'}));
}

test('Python algebraic plan binds the complete Enum dependency closure and survives source removal', t => {
  const f = fixture(t), before = fs.readdirSync(f.temp), p = planConfiguredPythonAlgebraicEnums(f.graph, f.fields, f.selection, sources);
  assert.deepEqual(fs.readdirSync(f.temp), before);assert.equal(p.modules.length, 4);assert.equal(p.plain_modules.length, 2);
  assert.equal(p.artifacts.filter(a => a.relative_path.endsWith('/runtime/values.py')).length, 1);
  for (const m of p.modules) for (const d of m.dependencies) assert.ok(p.artifacts.some(a => a.relative_path === d.path));
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content));assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  const {plan_sha256, ...body} = p;assert.equal(plan_sha256, sha256(canonicalJson(body)));assert.ok(Object.isFrozen(p.modules));
  fs.renameSync(f.source, path.join(f.temp, 'moved'));
  assert.deepEqual(planConfiguredPythonAlgebraicEnums(f.graph, f.fields, f.selection, sources), p);
});

test('Python sum planning rejects forged bindings, source drift, native artifact collisions and active inputs', t => {
  const f = fixture(t);
  assert.throws(() => planConfiguredPythonAlgebraicEnums(structuredClone(f.graph), f.fields, f.selection, sources));
  assert.throws(() => planConfiguredPythonAlgebraicEnums(f.graph, structuredClone(f.fields), f.selection, sources));
  for (const change of [{language: 'rust'}, {schema_version: 'future'}, {field_compilation_sha256: '0'.repeat(64)}, {module_root: '../escape'}, {module_root: 'enum'}, {extra: true}])
    assert.throws(() => planConfiguredPythonAlgebraicEnums(f.graph, f.fields, {...f.selection, ...change} as any, sources));
  for (const key of Object.keys(sources) as (keyof typeof sources)[]) assert.throws(() => planConfiguredPythonAlgebraicEnums(f.graph, f.fields, f.selection, {...sources, [key]: sources[key] + ' '}));
  let reads = 0;const input = {...f.selection, get language() {reads++;return 'python';}};
  assert.throws(() => planConfiguredPythonAlgebraicEnums(f.graph, f.fields, input as any, sources));assert.equal(reads, 0);
  const collision = fixture(t, true);assert.throws(() => planConfiguredPythonAlgebraicEnums(collision.graph, collision.fields, collision.selection, sources), /conflicting artifact/);
  const record = fixture(t, false, true);assert.throws(() => planConfiguredPythonAlgebraicEnums(record.graph, record.fields, record.selection, sources), /record dependency requires a validated Python factory/);
});

test('native Python sums preserve exact values, immutable composition and ownership in two module roots', t => {
  const f = fixture(t);
  const key = (value: unknown) => compiledFieldValueKey(f.fields, 'commerce:answer', value);
  assert.equal(key({variant: 'Amount', payload: 1n}), key({variant: 'Amount', payload: '1'}));
  assert.notEqual(key({variant: 'Rows', payload: [1n, 2n]}), key({variant: 'Rows', payload: [2n, 1n]}));
  assert.equal(key({variant: 'Tags', payload: ['b', 'a']}), key({variant: 'Tags', payload: ['a', 'b']}));
  assert.throws(() => key({variant: 'UniqueAmounts', payload: [1n, '1']}), /DUPLICATE/);
  let priorHash: string | undefined;
  for (const module_root of ['domain-app', 'relocated/nested']) {
    const p = planConfiguredPythonAlgebraicEnums(f.graph, f.fields, {...f.selection, module_root}, sources);
    const observed = materialize(path.join(f.temp, module_root === 'domain-app' ? 'first' : 'second'), p.artifacts)(module_root.replaceAll('-', '_').replaceAll('/', '.'));
    const {hash, ...rest} = observed;
    assert.deepEqual(rest, {status: 'pass', observed: ['audit', 'commerce'], python: '3.14.4'});
    assert.match(hash, /^-?[0-9]+$/);if (priorHash !== undefined) assert.equal(hash, priorHash);priorHash = hash;
  }
});

test('native behavioral controls detect compiling UInt64 and list-order mutations', t => {
  const f = fixture(t), p = planConfiguredPythonAlgebraicEnums(f.graph, f.fields, f.selection, sources);
  for (const [index, mutate] of [
    (s: string) => s.replace('if type(value) is int:', 'if isinstance(value, int):'),
    (s: string) => s.replace('return sequence_value(element, False)', 'return sequence_value(element, True)'),
  ].entries()) {
    const root = path.join(f.temp, 'mutant-' + index), observe = materialize(root, p.artifacts), file = path.join(root, 'domain_app/runtime/values.py');
    const original = fs.readFileSync(file, 'utf8'), changed = mutate(original);assert.notEqual(changed, original);fs.writeFileSync(file, changed);
    execFileSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys;compile(open(sys.argv[1]).read(),sys.argv[1],"exec")', file]);
    assert.throws(() => observe('domain_app'), (e: any) => e.status === 1 && String(e.stderr).includes(index === 0 ? 'accepted invalid value: INVALID_UINT64' : 'DUPLICATE_SET_VALUE'));
  }
});
