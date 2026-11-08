import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonEnums, PYTHON_ENUM_SELECTION_VERSION, type PythonEnumSelection} from '../../src/generation/configured-python-enums.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const read = (file: string) => fs.readFileSync(path.join(project, file), 'utf8');
const sources = {configuration: read('development/reconciliation-v1/profile-compiler-reconciliation/configuration.json'),
  base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  python: read('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')};
const fieldContract = read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json');
function fixture(t: any, options: {payload?: boolean; record?: boolean; node?: string} = {}) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-enums-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), node = options.node ?? 'order-status';
  const names = ['Submitted', 'Draft', 'None', 'True', 'False', 'VariantTrue'];
  const write = (file: string, data: unknown) => {const target = path.join(source, file);fs.mkdirSync(path.dirname(target), {recursive: true});fs.writeFileSync(target, JSON.stringify(data) + '\n');};
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'python-enums', features: ['commerce', 'audit'], cross_feature_edges: []});
  for (const feature_id of ['commerce', 'audit']) {
    write(`specs/${feature_id}/feature.json`, {schema_version: 'domainspec.feature/v1', feature_id, nodes: [node, ...(options.record ? ['order'] : [])], edges: []});
    write(`specs/${feature_id}/nodes/${node}.json`, {schema_version: 'domainspec.node/v1', feature_id, node_id: node, kind: 'Enum', body: {description: 'Enum semantics', values: names,
      typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-' + feature_id.toUpperCase() + '-STATUS', variants: names.map(name => ({name, ontology_variant: 'FIXTURE-' + feature_id.toUpperCase() + '-STATUS#' + name, payload: options.payload ? {kind: 'scalar', name: 'String'} : null}))}}});
    if (options.record) write(`specs/${feature_id}/nodes/order.json`, {schema_version: 'domainspec.node/v1', feature_id, node_id: 'order', kind: 'Entity', body: {description: 'No silent filtering', fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + feature_id.toUpperCase() + '-ORDER', properties: [{name: 'id', ontology_property: 'FIXTURE-' + feature_id.toUpperCase() + '-ORDER#id', meaning: 'identity', type: {kind: 'scalar', name: 'String'}, cardinality: 'one', identity: true}]}}});
  }
  const graph = loadCompiledProjectGraph(source);
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256,
    graph_sha256: createCompiledProjectCertificate(graph).graph_sha256, roots: ['commerce:' + node, 'audit:' + node, ...(options.record ? ['commerce:order', 'audit:order'] : [])], bindings: []}, fieldContract);
  const selection: PythonEnumSelection = {schema_version: PYTHON_ENUM_SELECTION_VERSION, language: 'python', module_root: 'domain-app', field_compilation_sha256: fields.compilation_sha256};
  return {temp, source, fields, selection, names};
}

const observer = String.raw`
import ast
import enum
import importlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
prefix = sys.argv[2]
names = ["Draft", "False", "None", "Submitted", "True", "VariantTrue"]
native_names = ["Variant_" + n if n in ("False", "None", "True") else n for n in names]
loaded = []
for feature in ("audit", "commerce"):
    module_name = prefix + ".features." + feature + ".src.domain.enums.order_status"
    file = root.joinpath(*module_name.split(".")).with_suffix(".py")
    source = file.read_text()
    compile(source, str(file), "exec")
    tree = ast.parse(source)
    definitions = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "OrderStatus"]
    assert len(definitions) == 1
    definition = definitions[0]
    assert [ast.unparse(b) for b in definition.bases] == ["_enum.Enum"]
    assert [ast.unparse(d) for d in definition.decorator_list] == ["_enum.unique"]
    members = [(n.targets[0].id, ast.literal_eval(n.value)) for n in definition.body if isinstance(n, ast.Assign)]
    assert members == list(zip(native_names, names))
    functions = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert functions == ["parse_order_status", "emit_order_status", "order_status_member_id"]
    module = importlib.import_module(module_name)
    kind = module.OrderStatus
    assert issubclass(kind, enum.Enum) and not issubclass(kind, str)
    assert list(kind.__members__) == native_names and len(list(kind)) == len(names)
    assert module.ENUM_ID == feature + ":order-status"
    for name, native in zip(names, native_names):
        member = getattr(kind, native)
        assert module.parse_order_status(name) is member
        assert module.emit_order_status(member) == name
        assert module.order_status_member_id(member) == "FIXTURE-" + feature.upper() + "-STATUS#" + name
        assert member != name and name != member
        assert hash(member) == hash(member)
    class Active(str):
        def __eq__(self, other):
            raise AssertionError("active equality must not execute")
    class Object:
        def __repr__(self):
            raise AssertionError("active repr must not execute")
        def __eq__(self, other):
            raise AssertionError("active equality must not execute")
    for wrong in ("unknown", "draft", True, False, 1, None, {}, [], Active("Draft"), Object()):
        try:
            module.parse_order_status(wrong)
            raise AssertionError("wire accepted")
        except ValueError as error:
            assert error.code == "DOMAINSPEC_ENUM_UNKNOWN_WIRE"
            assert error.as_dict()["enum_id"] == feature + ":order-status"
    for wrong in ("Draft", True, 1, None, {}, Object()):
        for call in (module.emit_order_status, module.order_status_member_id):
            try:
                call(wrong)
                raise AssertionError("member accepted")
            except TypeError as error:
                assert error.code == "DOMAINSPEC_ENUM_MEMBER_INVALID"
    try:
        kind.Draft = kind.Submitted
        raise AssertionError("member reassigned")
    except AttributeError:
        pass
    try:
        kind.__members__["Alias"] = kind.Draft
        raise AssertionError("alias added")
    except TypeError:
        pass
    loaded.append(module)
left, right = loaded
assert left.OrderStatus.Draft != right.OrderStatus.Draft
assert len({left.OrderStatus.Draft, right.OrderStatus.Draft}) == 2
try:
    left.emit_order_status(right.OrderStatus.Draft)
    raise AssertionError("foreign enum accepted")
except TypeError as error:
    assert error.code == "DOMAINSPEC_ENUM_MEMBER_INVALID"
print(json.dumps({"status": "pass", "modules": len(loaded), "members_per_module": len(names), "python": sys.version.split()[0]}))
`;
function materialize(root: string, artifacts: readonly {relative_path: string; content: string}[]) {
  for (const a of artifacts) {const file = path.join(root, a.relative_path);fs.mkdirSync(path.dirname(file), {recursive: true});fs.writeFileSync(file, a.content, {flag: 'wx'});}
  const script = path.join(root, 'observe.py');fs.writeFileSync(script, observer);
  return (prefix = 'domain_app') => JSON.parse(execFileSync('/usr/bin/python3', ['-I', '-B', script, root, prefix], {encoding: 'utf8', stdio: 'pipe'}));
}

test('Python Enum plan binds exact fields and candidate profiles without writes or source reload', t => {
  const f = fixture(t), before = fs.readdirSync(f.temp), p = planConfiguredPythonEnums(f.fields, f.selection, sources);
  assert.deepEqual(fs.readdirSync(f.temp), before);assert.equal(p.modules.length, 2);
  assert.equal(p.modules[0]!.relative_path, 'domain_app/features/audit/src/domain/enums/order_status.py');
  assert.equal(p.modules[0]!.symbol, 'OrderStatus');assert.equal(p.output_effect, 'none');assert.equal(p.authority_effect, 'none');
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content));assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  const {plan_sha256, ...body} = p;assert.equal(plan_sha256, sha256(canonicalJson(body)));
  assert.ok(Object.isFrozen(p.modules[0]!.members));assert.ok(Object.isFrozen(p.artifacts));
  fs.renameSync(f.source, path.join(f.temp, 'moved-source'));
  assert.deepEqual(planConfiguredPythonEnums(f.fields, f.selection, sources), p);
  const relocated = planConfiguredPythonEnums(f.fields, {...f.selection, module_root: 'other-root/nested'}, sources);
  assert.deepEqual(relocated.artifacts.filter(a => a.content).map(a => a.content), p.artifacts.filter(a => a.content).map(a => a.content));
});

test('Python Enum planner rejects stale, forged, active, unsafe and unsupported inputs', t => {
  const f = fixture(t);
  assert.throws(() => planConfiguredPythonEnums(structuredClone(f.fields), f.selection, sources), /UNCHECKED/);
  for (const change of [{language: 'typescript'}, {schema_version: 'future'}, {field_compilation_sha256: '0'.repeat(64)}, {extra: true}, ...['../escape', '/absolute', 'a\\b', 'con', 'x/class', 'Upper', 'caf\u00e9', 'cafe\u0301', 'enum', 'typing/x', 'a--b', 'module\n'].map(module_root => ({module_root}))])
    assert.throws(() => planConfiguredPythonEnums(f.fields, {...f.selection, ...change} as any, sources));
  for (const key of Object.keys(sources) as (keyof typeof sources)[]) assert.throws(() => planConfiguredPythonEnums(f.fields, f.selection, {...sources, [key]: sources[key] + ' '}), /source drift/);
  let calls = 0;const active = {...f.selection, get language() {calls++;return 'python';}};
  assert.throws(() => planConfiguredPythonEnums(f.fields, active as any, sources));assert.equal(calls, 0);
  assert.throws(() => planConfiguredPythonEnums(f.fields, {...f.selection, [Symbol('hidden')]: true}, sources));
  assert.throws(() => planConfiguredPythonEnums(f.fields, Object.assign(Object.create({hidden: true}), f.selection), sources));
  const reserved = fixture(t, {node: 'con'});assert.throws(() => planConfiguredPythonEnums(reserved.fields, reserved.selection, sources), /portable identifier/);
});

test('Python plain Enum adapter never erases payloads or filters records', t => {
  for (const options of [{payload: true}, {record: true}]) {
    const f = fixture(t, options);assert.throws(() => planConfiguredPythonEnums(f.fields, f.selection, sources), /payload-bearing sum|unsupported declaration kind/);
  }
});

test('native Python package imports preserve nominal values, explicit wire identity and hostile rejection in two roots', t => {
  const f = fixture(t);
  for (const module_root of ['domain-app', 'other-root/nested']) {
    const plan = planConfiguredPythonEnums(f.fields, {...f.selection, module_root}, sources);
    const observed = materialize(path.join(f.temp, module_root === 'domain-app' ? 'first' : 'second'), plan.artifacts)(module_root.replaceAll('-', '_').replaceAll('/', '.'));
    assert.deepEqual(observed, {status: 'pass', modules: 2, members_per_module: 6, python: '3.14.4'});
  }
});

test('independent native observer rejects compiling wire and representation mutations', t => {
  const f = fixture(t), plan = planConfiguredPythonEnums(f.fields, f.selection, sources);
  for (const [index, mutate] of [
    (source: string) => source.replace('class OrderStatus(_enum.Enum):', 'class OrderStatus(str, _enum.Enum):'),
    (source: string) => source.replace('return OrderStatus.Draft', 'return OrderStatus.Submitted'),
  ].entries()) {
    const root = path.join(f.temp, 'mutant-' + index), observe = materialize(root, plan.artifacts);
    const file = path.join(root, 'domain_app/features/commerce/src/domain/enums/order_status.py'), original = fs.readFileSync(file, 'utf8'), changed = mutate(original);
    assert.notEqual(changed, original);fs.writeFileSync(file, changed);
    execFileSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys;compile(open(sys.argv[1]).read(),sys.argv[1],"exec")', file]);
    assert.throws(() => observe(), (e: any) => e.status === 1 && String(e.stderr).includes('AssertionError'));
  }
});
