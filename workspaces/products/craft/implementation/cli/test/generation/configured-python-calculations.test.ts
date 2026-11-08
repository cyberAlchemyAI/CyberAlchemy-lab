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
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredPythonCalculations, PYTHON_CALCULATION_VERSION} from '../../src/generation/configured-python-calculations.ts';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const pkg = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes = (file: string) => fs.readFileSync(file, 'utf8');
const sources = {configuration: bytes(path.join(pkg, 'configuration.json')),
  base: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  python: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')),
  calculation_contract: bytes(path.join(pkg, 'calculation-generation-contract.json')),
  exact_calculation_contract: bytes(path.join(pkg, 'calculation-v2-contract.json'))};
const boundaryContract = bytes(path.join(project, 'development/reconciliation-v1/contracts/composition-boundary.json'));
const input = (name: string) => ({op: 'input', name});
const literal = (value: string) => ({op: 'literal', value});
const binary = (op: string, left: any = input('left'), right: any = input('right')) => ({op, left, right});
const expressions = {
  add: binary('add'), subtract: binary('subtract'), multiply: binary('multiply'),
  floor: binary('divide'), ceil: binary('divide'), reject: binary('divide'), identity: input('left'),
  constant: literal('18446744073709551615'), literal: literal('9007199254740993'),
  'literal-sum': binary('add', literal('18446744073709551614'), literal('1')),
  intermediate: binary('subtract', binary('add'), input('right')),
  order: binary('add', binary('subtract', literal('0'), literal('1')), binary('divide', literal('1'), literal('0'))),
  repeated: binary('add', binary('add'), binary('add')),
  'add-provider': input('left'), keyword: input('class'), legacy: binary('add', input('left'), {op: 'literal', value: 1}),
};
function fixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-calculation-')); t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'); fs.cpSync(path.join(project, 'impl/cli/fixtures/input-roots/canonical-project'), source, {recursive: true});
  const write = (file: string, value: unknown) => {const full = path.join(source, file); fs.mkdirSync(path.dirname(full), {recursive: true}); fs.writeFileSync(full, JSON.stringify(value) + '\n');};
  const feature = JSON.parse(bytes(path.join(source, 'specs/alpha/feature.json'))), contracts: Record<string, any> = {};
  for (const [name, expression] of Object.entries(expressions)) {
    const id = 'compute-' + name, inputs = name === 'constant' || name === 'literal' ? [] : name === 'keyword' ? ['class'] : ['left', 'right', 'unused'];
    const contract = {schema_version: name === 'legacy' ? 'domainspec.typed-calculation/v1' : 'domainspec.typed-calculation/v2',
      ontology_calculation: 'FIXTURE-' + id.toUpperCase(), inputs: inputs.map(name => ({name, type: {kind: 'scalar', name: 'UInt64'}})),
      result: {kind: 'scalar', name: 'UInt64'}, division_rounding: name === 'floor' || name === 'ceil' ? name : 'reject', expression};
    contracts['alpha:' + id] = contract; feature.nodes.push(id);
    write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Calculation', body: {description: id, inputs, typed_contract: contract}});
  }
  feature.edges.push('compute-legacy-calculates-settle');
  write('specs/alpha/edges/compute-legacy-calculates-settle.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: 'compute-legacy-calculates-settle', relationship: 'calculates', source_node_id: 'compute-legacy', target_node_id: 'settle', scope: 'feature'});
  write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(source);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: createCompiledProjectCertificate(graph).graph_sha256}, boundaryContract);
  const selection = {schema_version: PYTHON_CALCULATION_VERSION, language: 'python' as const, boundary_sha256: boundary.boundary_sha256, module_root: 'domain-app', roots: Object.keys(contracts)};
  return {temp, source, boundary, contracts, selection, plan: () => planConfiguredPythonCalculations(boundary, selection, sources)};
}
type Plan = ReturnType<typeof planConfiguredPythonCalculations>;
function materialize(root: string, p: Plan) {
  for (const a of p.artifacts) {const f = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(f), {recursive: true}); fs.writeFileSync(f, a.content);}
}
const nativeScript = String.raw`
import ast, dataclasses, importlib, inspect, json, os, pathlib, sys, typing
data = json.load(sys.stdin)
sys.path.insert(0, data['root'])
def thaw(value):
    if isinstance(value, tuple): return [thaw(x) for x in value]
    if hasattr(value, 'items'): return {k: thaw(v) for k, v in value.items()}
    return value
f = {}
for m in data['modules']:
    module = importlib.import_module(m['import_name'])
    call = getattr(module, m['callable'])
    assert module.__all__ == [m['callable']]
    assert dataclasses.is_dataclass(call)
    assert thaw(call.descriptor) == m['descriptor']
    assert typing.get_type_hints(call.__call__)['return'] is int
    input_type = typing.get_type_hints(call.__call__)['input']
    assert typing.is_typeddict(input_type)
    assert input_type.__required_keys__ == frozenset(p['name'] for p in m['descriptor']['inputs'])
    assert all(t == int | str for t in typing.get_type_hints(input_type).values())
    for action in [lambda: setattr(call, 'descriptor', {}), lambda: setattr(call, 'replacement', 1), lambda: call.descriptor.__setitem__('selector', 'changed'), lambda: call.descriptor['result'].__setitem__('name', 'Bool')]:
        try: action()
        except (AttributeError, TypeError): pass
        else: raise AssertionError('MUTABLE_BINDING')
    f[m['selector'].split('compute-', 1)[1]] = call
maximum = 18446744073709551615
facts = lambda left, right=0, unused=0: {'left': left, 'right': right, 'unused': unused}
def error(fn, args, code):
    try: fn(args)
    except (TypeError, ValueError) as e: assert str(e) == code, str(e)
    else: raise AssertionError(code + '_MISSING')
for a in range(13):
    for b in range(13):
        assert type(f['add'](facts(a, b))) is int
        assert f['add'](facts(a, b)) == a + b
        assert f['multiply'](facts(a, b)) == a * b
        assert f['repeated'](facts(a, b)) == 2 * (a + b)
        if a >= b: assert f['subtract'](facts(a, b)) == a - b
        else: error(f['subtract'], facts(a, b), 'CALCULATION_UNDERFLOW')
        if b:
            assert f['floor'](facts(a, b)) == a // b
            assert f['ceil'](facts(a, b)) == (a + b - 1) // b
            if a % b: error(f['reject'], facts(a, b), 'CALCULATION_INEXACT')
            else: assert f['reject'](facts(a, b)) == a // b
assert f['constant']({}) == maximum
assert f['literal']({}) == 9007199254740993
assert f['literal-sum'](facts(0)) == maximum
assert f['legacy'](facts(maximum - 1)) == maximum
assert f['keyword']({'class': '7'}) == 7
assert f['add-provider'](facts(12)) == 12
assert f['ceil'](facts(maximum, 2)) == 9223372036854775808
assert f['floor'](facts(maximum, 2)) == 9223372036854775807
for value in [maximum, str(maximum), 9007199254740993, '9007199254740993', 0, '0']:
    assert f['identity'](facts(value)) == int(value)
for name in ['add', 'intermediate']: error(f[name], facts(maximum, 1), 'CALCULATION_OVERFLOW')
error(f['multiply'], facts(maximum, 2), 'CALCULATION_OVERFLOW')
error(f['order'], facts(0), 'CALCULATION_UNDERFLOW')
for name in ['floor', 'ceil', 'reject']: error(f[name], facts(0, 0), 'CALCULATION_DIVIDE_BY_ZERO')
for value in [True, False, 0.0, 1.0, 1.5, float('nan'), float('inf'), -1, maximum + 1, '', '01', '+1', '-0', '1\n', ' 1', '1.0', '١', '１', str(maximum + 1), '9' * 200, None, {}, []]:
    error(f['identity'], facts(value), 'CALCULATION_INPUT')
    error(f['identity'], facts(0, 0, value), 'CALCULATION_INPUT')
calls = []
class ActiveInt(int):
    def __int__(self): calls.append('int'); return 1
    def __lt__(self, other): calls.append('lt'); return False
class ActiveStr(str):
    def __eq__(self, other): calls.append('eq'); return True
    def __hash__(self): return str.__hash__(self)
class ActiveDict(dict):
    def __getitem__(self, key): calls.append('get'); return 1
for value in [ActiveInt(1), ActiveStr('1')]: error(f['identity'], facts(value), 'CALCULATION_INPUT')
for value in [None, [], {}, {'left': 1, 'right': 0}, {**facts(1), 'extra': 0}, ActiveDict(facts(1))]: error(f['identity'], value, 'CALCULATION_INPUT')
hostile_key = {ActiveStr('left'): 1, 'right': 0, 'unused': 0}
calls.clear()
error(f['identity'], hostile_key, 'CALCULATION_INPUT')
assert calls == [], calls
error(f['constant'], {'extra': 0}, 'CALCULATION_INPUT')
for artifact in data['files']:
    source = pathlib.Path(data['root'], artifact).read_bytes()
    compile(source, artifact, 'exec')
print(json.dumps({'pid': os.getpid(), 'maximum': str(f['constant']({})), 'modules': len(f)}))
`;
function payload(root: string, p: Plan, contracts: Record<string, unknown>) {
  return {root, modules: p.modules, files: p.artifacts.map(a => a.relative_path), contracts, support_path: p.artifacts.find(a => a.relative_path.endsWith('/runtime/calculations.py'))!.relative_path};
}
const observer = path.join(project, 'impl/cli/src/verification/python-calculation-observer.py');

test('R10 Python Calculation plans bind native profiles, both source versions and deterministic snapshots', t => {
  const f = fixture(t), p = f.plan(); assert.equal(p.modules.length, 16); assert.deepEqual(f.plan(), p);
  assert.deepEqual(planConfiguredPythonCalculations(f.boundary, {...f.selection, roots: [...f.selection.roots].reverse()}, sources), p);
  const relocated = planConfiguredPythonCalculations(f.boundary, {...f.selection, module_root: 'alternate/nested'}, sources);
  assert.deepEqual(relocated.artifacts.filter(a => a.content).map(a => a.content), p.artifacts.filter(a => a.content).map(a => a.content));
  const subset = planConfiguredPythonCalculations(f.boundary, {...f.selection, roots: ['alpha:compute-add']}, sources);
  for (const a of subset.artifacts) assert.equal(a.content, p.artifacts.find(b => b.relative_path === a.relative_path)!.content);
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  assert.equal(p.authority_effect, 'none'); assert.ok(Object.isFrozen(p.modules[0]!.descriptor.inputs));
  for (const m of p.modules) {
    const {descriptor_sha256, ...d} = m.descriptor; assert.equal(descriptor_sha256, sha256(canonicalJson(d)));
    assert.equal(d.provider.sha256, p.artifacts.find(a => a.relative_path === m.provider_path)!.sha256);
    assert.equal(d.contract_sha256, sha256(canonicalJson(f.contracts[m.selector])));
  }
  fs.renameSync(f.source, path.join(f.temp, 'gone')); assert.deepEqual(f.plan(), p);
});

test('R10 Python Calculation boundary rejects forged, stale, active and unsafe selections', t => {
  const f = fixture(t);
  assert.throws(() => planConfiguredPythonCalculations(structuredClone(f.boundary), f.selection, sources), /unvalidated boundary/);
  for (const patch of [{schema_version: 'future'}, {language: 'typescript'}, {boundary_sha256: 'stale'}, {module_root: '../escape'}, {module_root: 'domain//a'}, {module_root: 'types'}, {module_root: 'typing'}, {module_root: 'class'}, {roots: []}, {roots: ['alpha:compute-add', 'alpha:compute-add']}, {roots: ['alpha:settle']}, {roots: ['alpha:missing']}, {roots: ['alpha:compute-add:extra']}, {extra: true}])
    assert.throws(() => planConfiguredPythonCalculations(f.boundary, {...f.selection, ...patch} as any, sources));
  for (const key of Object.keys(sources)) assert.throws(() => planConfiguredPythonCalculations(f.boundary, f.selection, {...sources, [key]: sources[key as keyof typeof sources] + ' '}), /source drift/);
  let reads = 0;
  assert.throws(() => planConfiguredPythonCalculations(f.boundary, {...f.selection, get module_root() {reads++; return 'domain';}}, sources), /closed data/);
  const roots: any[] = []; Object.defineProperty(roots, '0', {enumerable: true, get() {reads++; return 'alpha:compute-add';}});
  assert.throws(() => planConfiguredPythonCalculations(f.boundary, {...f.selection, roots}, sources), /inert/);
  const sparse = new Array(2); sparse[1] = 'alpha:compute-add';
  assert.throws(() => planConfiguredPythonCalculations(f.boundary, {...f.selection, roots: sparse}, sources), /dense/);
  assert.equal(reads, 0);
});

test('R10 Python Calculations execute full-width arithmetic, immutable native bindings and hostile-input controls', t => {
  const f = fixture(t), results: any[] = [];
  for (const module_root of ['domain-app', 'relocated/nested']) {
    const p = planConfiguredPythonCalculations(f.boundary, {...f.selection, module_root}, sources), root = path.join(f.temp, module_root);
    materialize(root, p); const input = JSON.stringify(payload(root, p, f.contracts));
    results.push(JSON.parse(execFileSync('/usr/bin/python3', ['-I', '-B', '-c', nativeScript], {input, encoding: 'utf8'})));
    assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3', ['-I', '-B', observer], {input, encoding: 'utf8'})), {observed: 16});
  }
  assert.notEqual(results[0].pid, results[1].pid); assert.equal(results[0].maximum, results[1].maximum);
});

test('R10 independent Python Calculation observer rejects compiling arithmetic, effects and binding mutants', t => {
  const f = fixture(t), p = f.plan(), root = path.join(f.temp, 'mutants'); materialize(root, p);
  const m = p.modules.find(m => m.selector === 'alpha:compute-add')!, file = path.join(root, m.provider_path), original = bytes(file);
  const mutants: [string, string][] = [
    [original.replace('_checked(p0 + p1)', '_checked(p0 - p1)'), 'authored arithmetic'],
    [original.replace('return v0', 'return p0'), 'complete value return'],
    [original.replace('return v0', 'return True'), 'operand'],
    [original.replace('return v0', 'import time\n    return time.time_ns()'), 'instruction order'],
    [original.replace('return v0', 'globals()["effect"] = 1\n    return v0'), 'instruction order'],
    [original.replace('return v0', 'yield v0'), 'complete value return'],
  ];
  for (const [mutant, reason] of mutants) {
    assert.notEqual(mutant, original); fs.writeFileSync(file, mutant);
    execFileSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys; compile(sys.stdin.read(), "mutant.py", "exec")'], {input: mutant});
    // Rebind advertised digests so semantic observation, not stale hashing, kills the mutant.
    const changed: any = structuredClone(m); changed.descriptor.provider.sha256 = sha256(mutant);
    const result = spawnSync('/usr/bin/python3', ['-I', '-B', observer], {input: JSON.stringify({...payload(root, p, f.contracts), modules: [changed]}), encoding: 'utf8'});
    assert.notEqual(result.status, 0); assert.match(result.stderr, new RegExp('PYTHON_CALCULATION_OBSERVER:' + reason));
  }
  fs.writeFileSync(file, original);
  const wrapper = path.join(root, m.relative_path), facade = bytes(wrapper);
  for (const [mutant, reason] of [[facade.replace('frozen=True', 'frozen=False'), 'frozen provider binding'], [facade.replace('"effect_contract": "none"', '"effect_contract": "writes"'), 'descriptor binding']] as const) {
    fs.writeFileSync(wrapper, mutant);
    execFileSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys; compile(sys.stdin.read(), "mutant.py", "exec")'], {input: mutant});
    const result = spawnSync('/usr/bin/python3', ['-I', '-B', observer], {input: JSON.stringify({...payload(root, p, f.contracts), modules: [m]}), encoding: 'utf8'});
    assert.notEqual(result.status, 0); assert.match(result.stderr, new RegExp(reason));
  }
  fs.writeFileSync(wrapper, facade);
  const data = payload(root, p, f.contracts), supportFile = path.join(root, data.support_path), support = bytes(supportFile);
  const changedSupport = support.replace('if type(value) is int:', 'if isinstance(value, int):');
  assert.notEqual(changedSupport, support); fs.writeFileSync(supportFile, changedSupport);
  execFileSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys; compile(sys.stdin.read(), "support.py", "exec")'], {input: changedSupport});
  const changed: any = structuredClone(m); changed.descriptor.runtime.sha256 = sha256(changedSupport);
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', observer], {input: JSON.stringify({...data, modules: [changed]}), encoding: 'utf8'});
  assert.notEqual(result.status, 0); assert.match(result.stderr, /support perimeter/);
});
