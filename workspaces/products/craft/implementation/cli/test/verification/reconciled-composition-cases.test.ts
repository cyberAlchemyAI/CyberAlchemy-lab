import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {compileDeclarativeFunction, type DeclarativeFunctionContract as Contract, type DeclarativeExpression as E} from '../../src/typed-backend/declarative-function.ts';
import {createCompositionCases, createCompositionContractCases, assertCompositionCaseFamily, CompositionCasesUnavailable, COMPOSITION_CASES_DEFINITION_SHA256} from '../../src/verification/reconciled-composition-cases.ts';
import {encodeCompositionCaseValue as encode, decodeCompositionCaseValue as decode, CompositionCaseValueUnavailable} from '../../src/verification/reconciled-composition-case-values.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {publicFixture, publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
const base = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation');
const definitions = Object.fromEntries(['binding', 'reference', 'cases'].map(name => [name, fs.readFileSync(path.join(base, 'semantic-composition-' + name + '-contract.json'), 'utf8')])) as {binding: string; reference: string; cases: string};
const at = (...path: string[]): E => ({op: 'path', path});
const lit = (value: string | number | boolean | null): E => ({op: 'literal', value});
const call = (name: string, ...args: E[]): E => ({op: 'call', name, args});
const node = (id: string, kind: string, rest: object): any => ({id, kind, ontology: 'TEST-' + id.toUpperCase(), meaning: 'Finite source witness ' + id, ...rest});
const output = (fields: Record<string, E>, types: Record<string, string>, input: Record<string, string> = {}): Contract => ({schema_version: 'domainspec.declarative-function/v1', records: {Input: input, Output: types}, roots: {input: 'Input'}, calculations: {}, nodes: [node('Result', 'Mapping', {target: 'Output', fields})], assertions: [], results: [{condition: lit(true), value: at('Result')}], output: 'Output'});
const load = (source: string) => import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
function native(module: any, row: any, api = {}) {
  const observations: any[] = [], roots = decode(row.input), r = row.request;
  try {const value = r.mode === 'validate-input' ? module.validateInput(roots, (e: any) => observations.push(e)) : module.execute(roots, api, (e: any) => observations.push(e), r.binding, r.phase); return encode({outcome: {kind: 'value', value}, observations});}
  catch (error: any) {const code = typeof error?.code === 'string' && /^[A-Z][A-Z0-9_]*$/.test(error.code) ? error.code : String(error?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'EVALUATION_FAILED'; return encode({outcome: {kind: 'error', code}, observations});}
}
async function check(c: Contract) {
  const source = compileDeclarativeFunction(c).source, family = createCompositionContractCases(c, {}, definitions.cases), module = await load(source);
  for (const row of family.cases) assert.deepEqual(native(module, row), row.expected, row.id + ':' + row.group);
  return {family, source};
}

test('tagged wire retains inert exact values and rejects hostile data without execution', () => {
  const object = Object.create(null); Object.defineProperty(object, '__proto__', {value: 'data', enumerable: true}); object.a = undefined; object.b = [0n, 9007199254740993n, -0, null, false];
  const wire = encode(object), copy: any = decode(wire);
  assert.equal(copy.__proto__, 'data'); assert.ok(Object.hasOwn(copy, 'a')); assert.ok(!Object.hasOwn(copy, 'missing')); assert.ok(Object.is(copy.b[2], -0)); assert.equal(copy.b[1], 9007199254740993n); assert.deepEqual(encode(copy), wire);
  assert.ok(Object.isFrozen(wire)); assert.notEqual(decode(wire), copy);
  let calls = 0; const getter = Object.defineProperty({}, 'x', {enumerable: true, get() {calls++; return 1;}}), cyclic: any = {}; cyclic.x = cyclic;
  for (const value of [getter, cyclic, new Date(), new Array(1), NaN, Infinity, () => calls++, {[Symbol('x')]: 1}, {toJSON() {calls++;}}]) assert.throws(() => encode(value), CompositionCaseValueUnavailable);
  const malformed: any[] = [['number', '01'], ['bigint', '-0'], ['null', 1], ['record', [['x', ['null']], ['x', ['null']]]], ['record', [['2', ['null']], ['1', ['null']]]], ['unknown'], ['boolean', 'true']];
  for (const value of malformed) assert.throws(() => decode(value), CompositionCaseValueUnavailable);
  const wireGetter = Object.defineProperty(['string', 'x'], '1', {enumerable: true, get() {calls++; return 'x';}}); assert.throws(() => decode(wireGetter), /own enumerable/); assert.equal(calls, 0);
  let deep: any = null; for (let i = 0; i < 66; i++) deep = [deep]; assert.throws(() => encode(deep), /capacity/);
  assert.throws(() => encode('x'.repeat(8388609)), /capacity/); assert.throws(() => decode(['array', Array(4097).fill(['null'])]), /capacity/);
});

test('source-derived scalar, optional and collection families execute deterministically', async () => {
  const c = output({value: call('coalesce', call('optional_uint64', at('input', 'value')), call('uint64', lit('7'))), ids: call('sort', call('distinct', at('input', 'ids')))}, {value: 'UInt64', ids: 'String[]'}, {value: 'String?', ids: 'String[]'});
  const {family} = await check(c); assert.deepEqual(family, createCompositionContractCases(c, {}, definitions.cases));
  const roots: any[] = family.cases.map(row => decode(row.input));
  assert.ok(roots.some(r => !Object.hasOwn(r.input, 'value'))); assert.ok(roots.some(r => r.input.value === null)); assert.ok(roots.some(r => Object.hasOwn(r.input, 'value') && r.input.value === undefined));
  assert.ok(roots.some(r => r.input.ids.length === 0)); assert.ok(roots.some(r => r.input.ids.length === 2 && r.input.ids[0] === r.input.ids[1])); assert.ok(roots.some(r => r.input.ids.length === 2 && r.input.ids[0] !== r.input.ids[1]));
  assert.ok(family.cases.some(row => (decode(row.expected) as any).outcome.kind === 'error')); assert.ok(Object.isFrozen(family.cases));
  assert.equal(sha256(definitions.cases), COMPOSITION_CASES_DEFINITION_SHA256); assert.throws(() => createCompositionContractCases(c, {}, definitions.cases + '\n'), /definition drift/);
});

test('authored literals select both branches and inactive declarations stay explicit', async () => {
  for (const target of ['review_ready', 'another_literal']) {
    const c = output({value: lit('accepted')}, {value: 'String'}, {status: 'String'});
    c.nodes.push(node('Else', 'Mapping', {target: 'Output', fields: {value: lit('declined')}}));
    c.nodes.push(node('Dead', 'Mapping', {target: 'Output', fields: {value: call('text', call('uint64', lit('bad')))}}));
    c.results = [{condition: call('eq', at('input', 'status'), lit(target)), value: at('Result')}, {condition: call('ne', at('input', 'status'), lit(target)), value: at('Else')}, {condition: lit(false), value: at('Dead')}];
    const {family} = await check(c);
    assert.ok(family.cases.some(row => (decode(row.input) as any).input.status === target)); assert.deepEqual(family.coverage.results.map(r => r.required), [true, true, false]); assert.equal(family.coverage.declarations.find(r => r.id === 'Dead')!.required, false);
    assert.ok(family.coverage.witnessed.includes('result:0')); assert.ok(family.coverage.witnessed.includes('result:1'));
  }
});

test('exact numeric source literals drive UInt64 witnesses and optional array entries remain dense', async () => {
  const c = output({value: lit('ok')}, {value: 'String'}, {amount: 'UInt64'});
  c.assertions = [{condition: call('eq', at('input', 'amount'), call('uint64', lit('938271'))), code: 'MATCH'}];
  const {family} = await check(c); assert.ok(family.cases.some(row => (decode(row.input) as any).input.amount === 938271n));
  await check(output({value: call('count', at('input', 'values'))}, {value: 'Int'}, {values: 'String?[]'}));
});

function query(): Contract {
  const c = output({ids: call('column', at('Selected'), lit('id')), again: call('column', at('Selected'), lit('id'))}, {ids: 'String[]', again: 'String[]'}, {rows: 'Row[]'}); c.records.Row = {id: 'String', amount: 'UInt64'};
  c.nodes.unshift(node('Project', 'Mapping', {input: {name: 'row', type: 'Row'}, target: 'Row', fields: {id: call('lower', at('row', 'id')), amount: at('row', 'amount')}}));
  c.nodes.unshift(node('Selected', 'Query', {binding: 'row', source: at('input', 'rows'), where: call('gt', at('row', 'amount'), call('uint64', lit('0'))), select: call('Project', at('row'))})); return c;
}
test('Query witnesses include accepted projection and quantifiers preserve collection identities', async () => {
  const {family} = await check(query()); assert.ok(family.coverage.witnessed.includes('node:Project'));
  for (const op of ['exists', 'forall', 'exactly_one'] as const) await check(output({value: {op, binding: 'row', collection: at('input', 'rows'), where: call('eq', at('row'), lit('1'))}}, {value: 'Bool'}, {rows: 'String[]'}));
});

test('v2 multi-input Mappings and declared binding phases are independently covered', async () => {
  const c = output({value: call('lower', at('input', 'a'))}, {value: 'String'}, {a: 'String', b: 'String', enabled: 'Bool'});
  c.schema_version = 'domainspec.declarative-function/v2'; c.nodes[0]!.inputs = [];
  c.nodes.push(node('Pair', 'Mapping', {inputs: [{name: 'a', type: 'String?'}, {name: 'b', type: 'String'}], target: 'Output', fields: {value: call('coalesce', at('a'), at('b'))}}));
  c.results[0]!.value = call('Pair', at('input', 'a'), at('input', 'b'));
  c.roots.remote = 'Output'; c.bindings = [{name: 'remote', condition: at('input', 'enabled'), input: {mapping: 'Result', type: 'Output'}}];
  const {family} = await check(c); assert.ok(family.cases.some(row => row.request.phase === 'input')); assert.ok(family.cases.some(row => row.request.phase === 'guard')); assert.ok(family.cases.some(row => row.group === 'missing-binding'));
});

test('missing witnesses and finite family capacity never return a partial pass', () => {
  const c = output({value: lit('ok')}, {value: 'String'}, {a: 'String'}); c.assertions = [{condition: lit(false), code: 'NEVER'}]; compileDeclarativeFunction(c);
  assert.throws(() => createCompositionContractCases(c, {}, definitions.cases), (e: any) => e instanceof CompositionCasesUnavailable && e.missing.length > 0 && !Object.hasOwn(e, 'cases'));
  const impossible = output({value: lit('ok')}, {value: 'String'}); impossible.results.push({condition: lit(true), value: at('Result')}); compileDeclarativeFunction(impossible); assert.throws(() => createCompositionContractCases(impossible, {}, definitions.cases), /required witness/);
  const huge = output({value: lit('ok')}, {value: 'String'}, Object.fromEntries(Array.from({length: 513}, (_, i) => ['field' + i, 'Bool']))); compileDeclarativeFunction(huge); assert.throws(() => createCompositionContractCases(huge, {}, definitions.cases), /slot capacity/);
  const recursive = output({value: lit('ok')}, {value: 'String'}, {next: 'Input'}); compileDeclarativeFunction(recursive); assert.throws(() => createCompositionContractCases(recursive, {}, definitions.cases), /recursive type/);
});

test('nested optional and recursive collection seeds terminate and missing ancestors materialize', async () => {
  const c = output({value: call('count', at('input', 'rows'))}, {value: 'Int'}, {rows: 'Row[]', extra: 'Row?'}); c.records.Row = {id: 'String', children: 'Row[]'};
  const {family} = await check(c);
  assert.ok(family.cases.some(row => (decode(row.input) as any).input.rows.length > 0));
  assert.ok(family.cases.some(row => (decode(row.input) as any).input.extra === null));
  const forest = output({value: lit('ok')}, {value: 'String'}, {tree: 'Level0'});
  for (let i = 0; i < 20; i++) forest.records['Level' + i] = i === 19 ? {value: 'String'} : {left: 'Level' + (i + 1), right: 'Level' + (i + 1)};
  compileDeclarativeFunction(forest); assert.throws(() => createCompositionContractCases(forest, {}, definitions.cases), /type seed capacity/);
});

test('final case-family byte or count limits reject atomically after successful witnesses', () => {
  const c = output({value: lit('ok')}, {value: 'String'}, Object.fromEntries(Array.from({length: 110}, (_, i) => ['field' + i, 'String'])));
  compileDeclarativeFunction(c); assert.throws(() => createCompositionContractCases(c, {}, definitions.cases), (e: any) => e instanceof CompositionCasesUnavailable && /final family capacity/.test(e.message) && !Object.hasOwn(e, 'cases'));
});

test('generated behavior mutants execute and finite source cases detect disagreement', async () => {
  const {family, source} = await check(query());
  const mutations: [string, string][] = [['rows.filter((row,index)', '[...rows].reverse().filter((row,index)'], ['return accepted;', 'return false;'], ['.toLowerCase()', '.toUpperCase()'], ['if (!ready)', 'if (true)'], ['{count:value.length}', '{count:value.length+1}'], ['return n_Result();', 'return {};'], ["emit(observe,{kind:'result-case',index,passed});", ''], ['declaration,index,accepted,row', 'declaration,index:index+1,accepted,row']];
  for (const [before, after] of mutations) {assert.ok(source.includes(before), before); const module = await load(source.replace(before, after)); assert.ok(family.cases.some(row => JSON.stringify(native(module, row)) !== JSON.stringify(row.expected)), before);}
  const numeric = output({value: call('text', call('uint64', at('input', 'value')))}, {value: 'String'}, {value: 'String'}), n = await check(numeric);
  const module = await load(n.source.replace('const n=BigInt(value);', 'const n=BigInt(Number(value));')); assert.ok(n.family.cases.some(row => JSON.stringify(native(module, row)) !== JSON.stringify(row.expected)));
});

test('registered graph family executes strict-compiled selected Calculation adapters', async t => {
  const f = publicFixture(t), plan = planCompiledReconciledProject(f.graph, publicSelection()), family = createCompositionCases(f.graph, plan, 'calculate', definitions);
  assertCompositionCaseFamily(family); assert.throws(() => assertCompositionCaseFamily(structuredClone(family)), /registered/); assert.throws(() => createCompositionCases(structuredClone(f.graph), plan, 'calculate', definitions), /unvalidated or changed/);
  assert.equal(family.binding.contract_sha256, family.contract_sha256); assert.deepEqual(family, createCompositionCases(f.graph, plan, 'calculate', definitions));
  const root = path.join(f.root, 'native'), out = path.join(f.root, 'compiled'); fs.mkdirSync(root); fs.mkdirSync(out);
  const artifacts = [...plan.resolved.artifacts, ...plan.composition!.artifacts];
  for (const a of artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(a => a.endsWith('loader.mjs')).map(p => path.dirname(p))}), deps = path.dirname(path.dirname(path.dirname(types)));
  const image = nativeToolchainImage(); assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const compile = () => execFileSync('docker', ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + root + ',target=/input,readonly', '--mount', 'type=bind,source=' + out + ',target=/output', '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', image, 'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'commonjs', '--rootDir', '/input', '--outDir', '/output', ...family.binding.modules.filter(m => m.relative_path.endsWith('.ts')).map(m => '/input/' + m.relative_path)], {encoding: 'utf8', timeout: 60000});
  compile(); const adapterPath = path.join(out, family.binding.adapter_path.replace(/\.ts$/, '.js')), api = require(adapterPath), source = artifacts.find(a => a.relative_path === family.binding.behavior_path)!.content, module = await load(source);
  for (const row of family.cases) assert.deepEqual(native(module, row, api), row.expected, row.id);
  const adapterSource = path.join(root, family.binding.adapter_path), before = fs.readFileSync(adapterSource, 'utf8');
  const after = before.replace('calculation0(', 'calculation1('); assert.notEqual(after, before); fs.writeFileSync(adapterSource, after); compile(); delete require.cache[adapterPath]; const mutant = require(adapterPath);
  assert.ok(family.cases.some(row => JSON.stringify(native(module, row, mutant)) !== JSON.stringify(row.expected)));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
