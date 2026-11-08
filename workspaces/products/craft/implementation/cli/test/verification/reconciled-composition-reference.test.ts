import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {compileDeclarativeFunction, type DeclarativeFunctionContract as Contract, type DeclarativeExpression as E} from '../../src/typed-backend/declarative-function.ts';
import {createCompositionReference, evaluateCompositionReference as reference, CompositionReferenceUnavailable, COMPOSITION_REFERENCE_DEFINITION_SHA256, type CompositionReferenceRequest as Request} from '../../src/verification/reconciled-composition-reference.ts';
import {fixture, authoredComposition} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planResolvedCompositionBindings} from '../../src/generation/resolved-composition-bindings.ts';
import {sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const definition = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/semantic-composition-reference-contract.json'), 'utf8');
const at = (...path: string[]): E => ({op: 'path', path});
const lit = (value: string | number | boolean | null): E => ({op: 'literal', value});
const call = (name: string, ...args: E[]): E => ({op: 'call', name, args});
const node = (id: string, kind: string, rest: object): any => ({id, kind, ontology: 'TEST-' + id.toUpperCase(), meaning: 'Reference witness for ' + id, ...rest});
const output = (fields: Record<string, E>, types: Record<string, string>, input: Record<string, string> = {}): Contract => ({
  schema_version: 'domainspec.declarative-function/v1', records: {Input: input, Output: types}, roots: {input: 'Input'}, calculations: {},
  nodes: [node('Result', 'Mapping', {target: 'Output', fields})], assertions: [], results: [{condition: lit(true), value: at('Result')}], output: 'Output'
});
const load = (source: string) => import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
function native(module: any, roots: any, api: any = {}, request: Request = {mode: 'execute'}) {
  const observations: any[] = [];
  try {
    const value = request.mode === 'validate-input' ? module.validateInput(roots, (e: any) => observations.push(e)) : module.execute(roots, api, (e: any) => observations.push(e), request.binding, request.phase);
    return {outcome: {kind: 'value', value}, observations};
  } catch (error: any) {
    const code = typeof error?.code === 'string' && /^[A-Z][A-Z0-9_]*$/.test(error.code) ? error.code : String(error?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'EVALUATION_FAILED';
    return {outcome: {kind: 'error', code}, observations};
  }
}
async function compare(c: Contract, cases: any[], request?: Request) {
  const module = await load(compileDeclarativeFunction(c).source);
  return cases.map(roots => {
    const expected = reference(c, roots, {}, request);
    assert.deepEqual(native(module, roots, {}, request), expected);
    return expected;
  });
}

test('definition pin, graph ownership, source-only snapshot reuse and structural bindings', t => {
  assert.equal(sha256(definition), COMPOSITION_REFERENCE_DEFINITION_SHA256);
  const f = fixture(t, {valueObject: true});
  const bound = createCompositionReference(f.graph, 'calculate', definition);
  const roots = {input: {id: 'request', qty: '10', rebate: '3'}};
  assert.deepEqual(bound.evaluate(roots).outcome, {kind: 'value', value: {net: '7', other: '13'}});
  assert.throws(() => createCompositionReference(structuredClone(f.graph), 'calculate', definition), /unvalidated or changed/);
  assert.throws(() => createCompositionReference(f.graph, 'unknown', definition), CompositionReferenceUnavailable);
  assert.throws(() => createCompositionReference(f.graph, 'calculate', definition + '\n'), /definition drift/);
  // Removing owned fixture source cannot make this registered source snapshot use a disk fallback.
  fs.rmSync(f.source, {recursive: true});
  assert.deepEqual(createCompositionReference(f.graph, 'calculate', definition).evaluate(roots), bound.evaluate(roots));
  assert.ok(Object.isFrozen(bound.evaluate(roots).observations));
  // Structural Value Object bindings deliberately do not execute factories or Rules.
  assert.ok(!bound.evaluate(roots).observations.some(e => e.node_kind === 'Rule'));
});

test('exact UInt64 conversions and decimal/format scales agree at boundaries', async () => {
  const c = output({value: call('text', call('uint64', at('input', 'value')))}, {value: 'String'}, {value: 'String'});
  const cases = ['0', '1', '9007199254740991', '9007199254740992', '9007199254740993', '18446744073709551615', '18446744073709551616', '-1', '+1', '01', '1.0', '', '1\n', '1\r\n', ' 1', '1 '];
  const results = await compare(c, cases.map(value => ({input: {value}})));
  assert.equal(results.filter(r => r.outcome.kind === 'value').length, 6);
  for (const scale of [0, 1, 2, 18]) {
    const c = output({value: call('format', call('decimal', at('input', 'value'), lit(scale)), lit(scale))}, {value: 'String'}, {value: 'String'});
    await compare(c, ['0', '1', '1.0', '1.25', '0.000000000000000001', '18.446744073709551615', '18.446744073709551616', '1.', '.1', '01', '-1', '1\n'].map(value => ({input: {value}})));
  }
  for (const type of ['Int', 'UInt64']) {
    const c = output({value: call('text', call('uint64', at('input', 'value')))}, {value: 'String'}, {value: type});
    await compare(c, (type === 'Int' ? [0, 1, -1, 9007199254740991, 9007199254740992, 1.5] : [0n, 9007199254740993n, 18446744073709551615n, -1n]).map(value => ({input: {value}})));
  }
});

test('optional absence, null, lazy coalescing and versioned lowercase preserve meanings', async () => {
  const c = output({value: call('coalesce', call('optional_uint64', at('input', 'value')), call('uint64', lit('invalid')))}, {value: 'UInt64'}, {value: 'String?'});
  const results = await compare(c, [{input: {value: '2'}}, {input: {value: null}}, {input: {}}, {input: {value: undefined}}]);
  assert.deepEqual(results.map(r => r.outcome.kind), ['value', 'error', 'error', 'error']);
  const lower = output({value: call('lower', at('input', 'value'))}, {value: 'String'}, {value: 'String'});
  const unicode = (await compare(lower, [{input: {value: 'ÄAZİ'}}]))[0]!;
  lower.portability = 'node-rust-v1';
  const portable = (await compare(lower, [{input: {value: 'ÄAZİ'}}]))[0]!;
  assert.notDeepEqual(unicode.outcome, portable.outcome);
});

test('strict comparisons, collection builtins and lazy Boolean operators match', async () => {
  const c = output({
    eq: call('eq', at('input', 'a'), at('input', 'b')), ne: call('ne', at('input', 'a'), at('input', 'b')),
    lt: call('lt', at('input', 'a'), at('input', 'b')), lte: call('lte', at('input', 'a'), at('input', 'b')),
    gt: call('gt', at('input', 'a'), at('input', 'b')), gte: call('gte', at('input', 'a'), at('input', 'b')),
    and: call('and', lit(false), call('eq', call('uint64', lit('bad')), call('uint64', lit('0')))),
    or: call('or', lit(true), call('eq', call('uint64', lit('bad')), call('uint64', lit('0')))),
    present: call('present', at('input', 'optional')), not: call('not', lit(false)),
    count: call('count', at('input', 'ids')), ids: call('sort', call('distinct', at('input', 'ids')))
  }, {eq: 'Bool', ne: 'Bool', lt: 'Bool', lte: 'Bool', gt: 'Bool', gte: 'Bool', and: 'Bool', or: 'Bool', present: 'Bool', not: 'Bool', count: 'Int', ids: 'String[]'}, {a: 'UInt64', b: 'UInt64', optional: 'String?', ids: 'String[]'});
  await compare(c, [[1n, 2n], [2n, 1n], [9007199254740993n, 9007199254740993n]].map(([a, b]) => ({input: {a, b, ids: ['z', 'a', 'z', 'ä'], optional: null}})));
  for (const name of ['one', 'first']) await compare(output({value: call(name, at('input', 'ids'))}, {value: 'String'}, {ids: 'String[]'}), [[], ['a'], ['a', 'b']].map(ids => ({input: {ids}})));
});

function queryFixture(): Contract {
  const c = output({ids: call('column', at('Selected'), lit('id')), again: call('column', at('Selected'), lit('id'))}, {ids: 'String[]', again: 'String[]'}, {rows: 'Row[]'});
  c.records.Row = {id: 'String', amount: 'UInt64'};
  c.nodes.unshift(node('Project', 'Mapping', {input: {name: 'row', type: 'Row'}, target: 'Row', fields: {id: call('lower', at('row', 'id')), amount: at('row', 'amount')}}));
  c.nodes.unshift(node('Selected', 'Query', {binding: 'row', source: at('input', 'rows'), where: call('gt', at('row', 'amount'), call('uint64', lit('0'))), select: call('Project', at('row'))}));
  return c;
}
test('Query filters before projection; zero-input declarations memoize per invocation', async () => {
  const c = queryFixture(), roots = {input: {rows: [{id: 'A', amount: 2n}, {id: 'B', amount: 0n}, {id: 'C', amount: 1n}]}};
  const [r] = await compare(c, [roots, roots]);
  assert.equal(r!.observations.filter(e => e.kind === 'node-start' && e.declaration === 'Selected').length, 1);
  let lastRow = -1;
  for(let i=r!.observations.length-1;i>=0;i--)if(r!.observations[i]!.kind==='query-row'){lastRow=i;break;}
  const firstProjection = r!.observations.findIndex(e => e.kind === 'node-start' && e.declaration === 'Project');
  assert.ok(lastRow < firstProjection);
  assert.equal(r!.observations.filter(e => e.kind === 'node-start' && e.declaration === 'Project').length, 2);
  assert.deepEqual(r!.outcome, {kind: 'value', value: {ids: ['a', 'c'], again: ['a', 'c']}});
});

test('quantifiers retain empty-list identities and their distinct short-circuit behavior', async () => {
  for (const op of ['exists', 'forall', 'exactly_one'] as const) {
    const c = output({value: {op, binding: 'row', collection: at('input', 'rows'), where: call('eq', call('uint64', at('row')), call('uint64', lit('1')))}}, {value: 'Bool'}, {rows: 'String[]'});
    const r = await compare(c, [[], ['1'], ['0'], ['1', 'bad'], ['0', 'bad'], ['1', '1']].map(rows => ({input: {rows}})));
    assert.deepEqual(r[0]!.outcome, {kind: 'value', value: {value: op === 'forall'}});
    assert.equal(r[3]!.outcome.kind, op === 'exists' ? 'value' : 'error');
    assert.equal(r[4]!.outcome.kind, op === 'forall' ? 'value' : 'error');
  }
});

function v2Fixture(): Contract {
  const c = output({first: call('text', at('Pair', 'left')), second: call('text', at('Pair', 'right'))}, {first: 'String', second: 'String'}, {a: 'String', b: 'String'});
  c.schema_version = 'domainspec.declarative-function/v2'; c.records.PairValue = {left: 'UInt64', right: 'UInt64'};
  c.nodes[0]!.inputs = [];
  c.nodes.unshift(node('Pair', 'Mapping', {inputs: [], target: 'PairValue', fields: {left: at('Built', 'left'), right: at('Built', 'right')}}));
  c.nodes.unshift(node('Built', 'Mapping', {inputs: [], target: 'PairValue', fields: {left: at('First', 'left'), right: at('First', 'right')}}));
  c.nodes.unshift(node('First', 'Mapping', {inputs: [], target: 'PairValue', fields: {left: at('input', 'a') as E, right: at('input', 'b') as E}}));
  c.nodes[0]!.fields = {left: call('uint64', at('input', 'a')), right: call('uint64', at('input', 'b'))};
  c.nodes.push(node('Combine', 'Mapping', {inputs: [{name: 'left', type: 'UInt64'}, {name: 'right', type: 'UInt64'}], target: 'PairValue', fields: {left: at('left'), right: at('right')}}));
  c.nodes.find(n => n.id === 'Built')!.fields = {left: call('uint64', at('input', 'a')), right: call('uint64', at('input', 'b'))};
  c.results[0]!.value = call('Present', call('Combine', at('First', 'left'), at('Built', 'right')));
  c.nodes.push(node('Present', 'Mapping', {inputs: [{name: 'pair', type: 'PairValue'}], target: 'Output', fields: {first: call('text', at('pair', 'left')), second: call('text', at('pair', 'right'))}}));
  return c;
}
test('v2 Mapping inputs evaluate once left-to-right and remain per-call, not memoized', async () => {
  const c = v2Fixture(), [r] = await compare(c, [{input: {a: '10', b: '3'}}, {input: {a: 'bad', b: 'also-bad'}}, {input: {a: '10', b: 'bad'}}]);
  assert.deepEqual(r!.observations.filter(e => e.kind === 'node-start').map(e => e.declaration), ['First', 'Built', 'Combine', 'Present']);
  assert.deepEqual(r!.outcome, {kind: 'value', value: {first: '10', second: '3'}});
  const repeated = structuredClone(c);
  repeated.records.Twice = {a: 'Output', b: 'Output'};
  repeated.nodes.push(node('Twice', 'Mapping', {inputs: [], target: 'Twice', fields: {a: c.results[0]!.value, b: c.results[0]!.value}}));
  repeated.results[0]!.value = at('Twice'); repeated.output = 'Twice';
  const [twice] = await compare(repeated, [{input: {a: '9007199254740993', b: '3'}}]);
  for (const name of ['Combine', 'Present']) assert.equal(twice!.observations.filter(e => e.kind === 'node-start' && e.declaration === name).length, 2);
  for (const name of ['First', 'Built']) assert.equal(twice!.observations.filter(e => e.kind === 'node-start' && e.declaration === name).length, 1);
});

test('assertion order, input-only phase, result cardinality and unused values stay distinct', async () => {
  const c = output({value: lit('ok')}, {value: 'String'}, {allowed: 'Bool'});
  c.nodes.unshift(node('Allowed', 'Rule', {expression: at('input', 'allowed')}));
  c.assertions = [{condition: at('input', 'allowed'), code: 'INPUT_DENIED'}, {condition: at('Allowed'), code: 'RULE_DENIED'}];
  const input = await compare(c, [{input: {allowed: true}}, {input: {allowed: false}}], {mode: 'validate-input'});
  assert.equal(input[0]!.observations.length, 1); assert.equal(input[0]!.observations[0]!.phase, 'input');
  await compare(c, [{input: {allowed: true}}, {input: {allowed: false}}]);
  c.assertions = [];
  c.nodes.push(node('Invalid', 'Mapping', {target: 'Output', fields: {value: call('text', call('uint64', lit('bad')))}}));
  c.results.push({condition: lit(false), value: at('Invalid')});
  assert.equal((await compare(c, [{input: {allowed: true}}]))[0]!.outcome.kind, 'value');
  c.results[1]!.condition = lit(true);
  assert.deepEqual((await compare(c, [{input: {allowed: true}}]))[0]!.outcome, {kind: 'error', code: 'DS_RESULT_CARDINALITY'});
  c.results.forEach(r => {r.condition = lit(false);});
  await compare(c, [{input: {allowed: false}}]);
});

test('declared binding guard/input phases and absent binding diagnostics are independent', async () => {
  const c = output({value: lit('ok')}, {value: 'String'}, {enabled: 'Bool'});
  c.records.Request = {enabled: 'Bool'}; c.records.Remote = {value: 'String'}; c.roots.remote = 'Remote';
  c.nodes.push(node('Request', 'Mapping', {target: 'Request', fields: {enabled: at('input', 'enabled')}}));
  c.bindings = [{name: 'remote', condition: at('input', 'enabled'), input: {mapping: 'Request', type: 'Request'}}];
  for (const binding of ['remote', 'missing']) for (const phase of ['guard', 'input'] as const) await compare(c, [{input: {enabled: true}}, {input: {enabled: false}}], {mode: 'execute', binding, phase});
  const empty = output({value: lit('ok')}, {value: 'String'}); empty.bindings = [];
  await compare(empty, [{input: {}}], {mode: 'execute', binding: 'ignored'});
});

test('reference capture rejects hostile/cyclic data without running accessors or coercion', () => {
  const c = output({value: lit('ok')}, {value: 'String'}); compileDeclarativeFunction(c);
  let calls = 0;
  const accessor = Object.defineProperty({}, 'input', {enumerable: true, get() {calls++; return {};}});
  const cyclic: any = {}; cyclic.input = cyclic;
  for (const roots of [accessor, cyclic, {input: {value: () => calls++}}, {input: new Date()}, {input: {v: NaN}}, {input: new Array(2)}, {input: {[Symbol('x')]: 1}}, Object.defineProperty({}, 'input', {value: {}})]) assert.throws(() => reference(c, roots), CompositionReferenceUnavailable);
  assert.equal(calls, 0);
  const shared = {value: 1}, roots = {input: {a: shared, b: shared}};
  assert.equal(reference(c, roots).outcome.kind, 'value');
  const plain = Object.create(null); plain.input = Object.create(null);
  assert.equal(reference(c, plain).outcome.kind, 'value');
  let deep: any = {}; for (let i = 0; i < 66; i++) deep = {child: deep};
  assert.throws(() => reference(c, {input: deep}), /capture capacity/);
});

test('unavailable whole reference capacity is not an expected domain error or partial success', () => {
  const c = output({value: {op: 'forall', binding: 'a', collection: at('input', 'rows'), where: {op: 'forall', binding: 'b', collection: at('input', 'rows'), where: call('eq', at('a'), at('b'))}}}, {value: 'Bool'}, {rows: 'Int[]'});
  compileDeclarativeFunction(c);
  assert.throws(() => reference(c, {input: {rows: Array(400).fill(1)}}), /evaluation capacity/);
  assert.throws(() => reference(c, {input: {rows: Array(4097).fill(1)}}), CompositionReferenceUnavailable);
  const text = output({value: at('input', 'value')}, {value: 'String'}, {value: 'String'});
  compileDeclarativeFunction(text);
  assert.throws(() => reference(text, {input: {value: 'é'.repeat(4194304)}}), /byte capacity/);
  // Source input fits; repeated detached observations and output must fit together too.
  assert.throws(() => reference(text, {input: {value: 'a'.repeat(4400000)}}), /byte capacity/);
});

test('compiling behavior mutants execute and disagree with independent results or traces', async () => {
  const c = queryFixture(), roots = {input: {rows: [{id: 'A', amount: 2n}, {id: 'B', amount: 1n}]}};
  const source = compileDeclarativeFunction(c).source, expected = reference(c, roots);
  const mutations: [string, string, string][] = [
    ['reverse source rows', 'rows.filter((row,index)', '[...rows].reverse().filter((row,index)'],
    ['drop accepted row', 'return accepted;', 'return false;'],
    ['projection case', '.toLowerCase()', '.toUpperCase()'],
    ['disable memo', 'if (!ready)', 'if (true)'],
    ['wrong observation', "kind:'selected-case',index:0", "kind:'selected-case',index:1"],
    ['query count drift', '{count:value.length}', '{count:value.length+1}'],
    ['discard selected result', 'return n_Result();', 'return {};'],
    ['omit result-case observation', "emit(observe,{kind:'result-case',index,passed});", ''],
    ['wrong query index', 'declaration,index,accepted,row', 'declaration,index:index+1,accepted,row']
  ];
  for (const [name, before, after] of mutations) {
    assert.ok(source.includes(before), name);
    const module = await load(source.replace(before, after));
    assert.notDeepEqual(native(module, roots), expected, name);
  }
  const numbers = output({value: call('text', call('uint64', at('input', 'value')))}, {value: 'String'}, {value: 'String'});
  const numericSource = compileDeclarativeFunction(numbers).source;
  const numericMutant = await load(numericSource.replace('const n=BigInt(value);', 'const n=BigInt(Number(value));'));
  const exactRoots = {input: {value: '9007199254740993'}};
  assert.notDeepEqual(native(numericMutant, exactRoots), reference(numbers, exactRoots));
  const v2 = v2Fixture(), v2Source = compileDeclarativeFunction(v2).source;
  const swapped = v2Source.replace('n_Combine(n_First()["left"],n_Built()["right"])', 'n_Combine(n_Built()["right"],n_First()["left"])');
  assert.notEqual(swapped, v2Source);
  assert.notDeepEqual(native(await load(swapped), {input: {a: '10', b: '3'}}), reference(v2, {input: {a: '10', b: '3'}}));
  const projectionFirst = source.replace(/return rows\.filter\(\(row,index\)=>\{const accepted=predicate\(row\);emit\(observe,\{kind:'query-row',declaration,index,accepted,row\}\);return accepted;\}\)\.map\(project\);/, "const out=[];rows.forEach((row,index)=>{const accepted=predicate(row);emit(observe,{kind:'query-row',declaration,index,accepted,row});if(accepted)out.push(project(row));});return out;");
  assert.notEqual(projectionFirst, source);
  assert.notDeepEqual(native(await load(projectionFirst), roots), expected);
  const lazy = output({value: call('and', lit(false), call('eq', call('uint64', lit('bad')), call('uint64', lit('0'))))}, {value: 'Bool'});
  const lazySource = compileDeclarativeFunction(lazy).source;
  const eager = lazySource.replace('(false && (uint64("bad") === uint64("0")))', 'Boolean(false & (uint64("bad") === uint64("0")))');
  assert.notEqual(eager, lazySource);
  assert.notDeepEqual(native(await load(eager), {input: {}}), reference(lazy, {input: {}}));
});

async function nativeFixture(f: ReturnType<typeof fixture>, graph = f.graph) {
  const resolved = f.resolved(graph), plan = planResolvedCompositionBindings(graph, resolved, fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/resolved-composition-bindings-contract.json'), 'utf8'));
  const bound = createCompositionReference(graph, 'calculate', definition), require = createRequire(import.meta.url);
  const types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))});
  const deps = path.dirname(path.dirname(path.dirname(types))), root = path.join(f.root, 'native'), compiled = path.join(f.root, 'compiled');
  fs.mkdirSync(root); fs.mkdirSync(compiled);
  const artifacts = [...resolved.artifacts, ...plan.artifacts];
  for (const a of artifacts) { const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content); }
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  execFileSync('docker', ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(),
    '--mount', 'type=bind,source=' + root + ',target=/input,readonly', '--mount', 'type=bind,source=' + compiled + ',target=/output', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', image,
    'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'commonjs', '--rootDir', '/input', '--outDir', '/output', ...artifacts.filter(a => a.relative_path.endsWith('.ts')).map(a => '/input/' + a.relative_path)], {encoding: 'utf8'});
  const api = require(path.join(compiled, 'compositions/calculate/core-api.js'));
  const behavior = await load(artifacts.find(a => a.relative_path === 'compositions/calculate/behavior.mjs')!.content);
  return {api, behavior, bound, compiled, require};
}
test('strict native selected Calculation adapter agrees with graph-bound reference and detects wrong binding', async t => {
  const f = fixture(t), {api, behavior, bound, compiled, require} = await nativeFixture(f);
  for (const [qty, rebate] of [['10', '3'], ['3', '10'], ['0', '0'], ['9007199254740993', '1'], ['18446744073709551615', '0'], ['18446744073709551615', '1'], ['bad', '0']]) {
    const roots = {input: {id: 'r', qty, rebate}};
    assert.deepEqual(native(behavior, roots, api), bound.evaluate(roots));
  }
  const direct = output({value: call('text', call('Net', at('input', 'qty'), at('input', 'rebate')))}, {value: 'String'}, {qty: 'UInt64', rebate: 'UInt64'});
  direct.calculations = {Net: ['qty', 'rebate']};
  const directModule = await load(compileDeclarativeFunction(direct).source);
  const calculations: any = {Net: {contract: f.graph.nodes.find(n => n.selector === 'alpha:compute')!.body.typed_contract, arguments: [{authored_name: 'qty', core_name: 'left'}, {authored_name: 'rebate', core_name: 'right'}]}};
  for (const qty of [10n, 10, '10', 9007199254740993n, '9007199254740993', '01', '1\n', -1n, 9007199254740992, '18446744073709551616', null, undefined, true]) {
    const roots = {input: {qty, rebate: 0n}}, expected = reference(direct, roots, calculations);
    assert.deepEqual(native(directModule, roots, api), expected);
    if (qty === null) assert.deepEqual(expected.outcome, {kind: 'error', code: 'EVALUATION_FAILED'});
  }
  const adapter = path.join(compiled, 'compositions/calculate/core-api.js'), original = fs.readFileSync(adapter, 'utf8');
  const changed = original.replace('case "Net":', 'case "Wrong":').replace('case "Other":', 'case "Net":');
  assert.notEqual(changed, original); fs.writeFileSync(adapter, changed); delete require.cache[require.resolve(adapter)];
  const mutant = require(adapter), roots = {input: {id: 'r', qty: '10', rebate: '3'}};
  assert.notDeepEqual(native(behavior, roots, mutant), bound.evaluate(roots));
});

test('source-owned multiplication and all division rounding modes match native exact arithmetic', async t => {
  for (const [op, rounding] of [['multiply', 'reject'], ['divide', 'reject'], ['divide', 'floor'], ['divide', 'ceil']]) {
    const f = fixture(t), file = 'specs/alpha/nodes/compute.json';
    const calculation = JSON.parse(fs.readFileSync(path.join(f.source, file), 'utf8'));
    calculation.body.typed_contract.division_rounding = rounding;
    calculation.body.typed_contract.expression.op = op; f.write(file, calculation);
    const {compositions, ...bareManifest} = f.manifest;
    f.write('project.json', {...bareManifest, schema_version: 'domainspec.project/v1'});
    const bare = loadCompiledProjectGraph(f.source), authored = authoredComposition(bare);
    f.write('compositions/calculate.json', authored); f.write('project.json', {...f.manifest, compositions: ['calculate']});
    const graph = loadCompiledProjectGraph(f.source), {api, behavior, bound} = await nativeFixture(f, graph);
    for (const [qty, rebate] of [['10', '3'], ['9', '3'], ['0', '0'], ['1', '0'], ['9007199254740993', '2'], ['18446744073709551615', '2']]) {
      const roots = {input: {id: 'r', qty, rebate}};
      assert.deepEqual(native(behavior, roots, api), bound.evaluate(roots), op + ':' + rounding + ':' + qty + '/' + rebate);
    }
    const expected = bound.evaluate({input: {id: 'r', qty: '10', rebate: '3'}}).outcome;
    assert.deepEqual(expected, op === 'divide' && rounding === 'reject' ? {kind: 'error', code: 'CALCULATION_INEXACT'} : {kind: 'value', value: {net: op === 'multiply' ? '30' : rounding === 'ceil' ? '4' : '3', other: '13'}});
  }
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
