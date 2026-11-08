import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync, spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicFixture, publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorPolicyControls, crossGeneratorPolicyProbe, checkCrossGeneratorPolicyObservations} from '../../src/verification/reconciled-cross-generator-policy.ts';
import {CROSS_GENERATOR_POLICY_RUNNER} from '../../src/verification/reconciled-cross-generator-policy-runner.ts';
import {createRecordRuleReference} from '../../src/verification/reconciled-rule-reference.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definition = fs.readFileSync(path.join(base, 'cross-generator-policy-contract.json'), 'utf8');
const boundaryDefinition = fs.readFileSync(path.join(base, 'cross-generator-verification-contract.json'), 'utf8');
const scalar = (name: string): any => ({kind: 'scalar', name});
const at = (root: string, properties: string[] = []): any => ({op: 'path', root, properties});
const lit = (type: string, value: unknown): any => ({op: 'literal', type, value});
const arg = (parameter: string, value: any) => ({parameter, value});
import {policyFixture as fixture} from '../helpers/cross-generator-policy.ts';
test('a Policy callee reached directly cannot cover its unvisited nested caller edge',t=>{
 const f=fixture(t),file=path.join(f.source,'specs/alpha/nodes/forward.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 const high=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/nodes/high.json'),'utf8'));
 raw.body.typed_contract.expression={op:'all',terms:[high.body.typed_contract.expression,{op:'any',terms:[
  {op:'eq',left:lit('Bool',true),right:lit('Bool',true)},raw.body.typed_contract.expression,
 ]}]};fs.writeFileSync(file,JSON.stringify(raw));
 const selected=path.join(f.source,'specs/alpha/nodes/choose.json'),policy=JSON.parse(fs.readFileSync(selected,'utf8'));
 policy.body.typed_contract.cases[1].rule={selector:'alpha:high',arguments:[arg('amount',at('other'))]};fs.writeFileSync(selected,JSON.stringify(policy));
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 const controls=createCrossGeneratorPolicyControls(graph,plan,boundary,definition),row=controls.rows.find(r=>r.selector==='alpha:choose')!;
 assert.equal(row.state,'not_evaluable');if(row.state==='not_evaluable')assert.match(row.reason,/unvisited.*edge/);
 assert.equal(crossGeneratorPolicyProbe(controls).rows.some(r=>r.selector==='alpha:choose'),false);
 assert.equal(controls.coverage.some(e=>e.policy_selectors.includes('alpha:choose')),false);
 assert.equal(controls.rows.find(r=>r.selector==='alpha:structured')!.state,'ready','unrelated family is retained');
});


function native(f: ReturnType<typeof fixture>) {
  const source = path.join(f.root, 'native-source'), output = path.join(f.root, 'native-js');
  fs.mkdirSync(source); fs.mkdirSync(output); fs.writeFileSync(path.join(output, 'package.json'), '{"type":"commonjs"}');
  const original = new Map(f.plan.resolved.artifacts.map(a => [a.relative_path, a.content]));
  for (const [p, content] of original) {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, content);}
  const require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(p => p.endsWith('loader.mjs')).map(p => path.dirname(p))});
  const deps = path.dirname(path.dirname(path.dirname(types)));
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + f.root + ',target=' + f.root, '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--workdir', f.root, image];
  const compile = () => {try {execFileSync('docker', [...docker, 'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.join(deps, '@types'), '--target', 'ES2022', '--module', 'commonjs', '--rootDir', source, '--outDir', output, ...[...original.keys()].map(p => path.join(source, p))], {encoding: 'utf8', timeout: 60000, stdio: 'pipe'});} catch (e: any) {throw Error([e.message, e.stdout, e.stderr].join('\n'));}};
  const runner = path.join(f.root, 'probe.mjs'), input = path.join(f.root, 'probe.json');
  fs.writeFileSync(runner, CROSS_GENERATOR_POLICY_RUNNER); fs.writeFileSync(input, JSON.stringify(crossGeneratorPolicyProbe(f.controls)));
  const run = () => {const r = spawnSync(process.execPath, ['--permission', '--allow-fs-read=' + f.root, runner, input, output], {cwd: f.root, encoding: 'utf8', timeout: 30000, maxBuffer: 16777216, env: {PATH: path.dirname(process.execPath), HOME: f.root, TMPDIR: f.root}}); assert.equal(r.status, 0, r.stderr); return JSON.parse(r.stdout);};
  const mutate = (relative: string, change: (old: string) => string) => {const old = original.get(relative)!; assert.equal(typeof old, 'string'); const next = change(old); assert.notEqual(next, old, 'mutation must be installed'); fs.writeFileSync(path.join(source, relative), next);};
  const restore = () => {for (const [p, content] of original) fs.writeFileSync(path.join(source, p), content);};
  return {compile, run, mutate, restore, source, output};
}

test('source-derived protocol binds every Policy and leaves incomplete families and unrelated edges explicit', t => {
  const f = fixture(t), c = f.controls;
  assert.equal(c.rows.length, 5); assert.equal(c.rows.filter(r => r.state === 'ready').length, 4);
  assert.equal(c.rows.find(r => r.selector === 'alpha:constant')!.state, 'not_evaluable');
  assert.deepEqual(c.coverage.map(e => e.edge_sha256), f.boundary.edges.map(e => e.edge_sha256));
  assert.ok(c.coverage.some(e => e.status === 'not_evaluable'));
  for (const row of c.rows) if (row.state === 'ready') {
    assert.ok(row.rule_edge_visits.length > 0);
    assert.ok(row.rule_edge_visits.every(e => e.calls > 0));
    assert.equal(row.rule_edge_visits.reduce((n, e) => n + e.calls, 0), row.cases.reduce((n, c) => n + c.expected.calls.length, 0));
    assert.deepEqual(row.rule_edge_visits.map(e => e.edge_sha256), f.boundary.edges.filter(e =>
      e.importer_path === row.relative_path.replace(/\.ts$/, '.provider.ts') || row.rules.some(r => r.relative_path === e.importer_path)
    ).map(e => e.edge_sha256));
  }
  const choose = c.rows.find(r => r.selector === 'alpha:choose')!; assert.equal(choose.state, 'ready');
  if (choose.state !== 'ready') throw Error('expected ready');
  assert.deepEqual(choose.rules.map(r => r.selector), ['alpha:enabled', 'alpha:forward', 'alpha:high']);
  assert.ok(choose.cases.some(c => c.expected.calls.some((x: any) => x.parent === 0 && x.selector === 'alpha:high')));
  assert.ok(choose.cases.some(c => c.expected.outcome.kind === 'error' && c.expected.calls.length === 0));
  const probe = crossGeneratorPolicyProbe(c);
  assert.equal(probe.rows.length, 4);
  for (const row of probe.rows) {assert.equal('rule_edge_visits' in row, false); assert.equal('source_predicted_targets' in row, false); for (const entry of row.cases) assert.equal('expected' in entry, false);}
  assert.throws(() => createCrossGeneratorPolicyControls(f.graph, f.plan, structuredClone(f.boundary), definition));
  assert.throws(() => createCrossGeneratorPolicyControls(f.graph, f.plan, f.boundary, definition + ' '), /definition drift/);
  assert.throws(() => crossGeneratorPolicyProbe(structuredClone(c)), /registered controls/);
  const other = fixture(t, 'different/root');
  assert.throws(() => createCrossGeneratorPolicyControls(f.graph, f.plan, other.boundary, definition), /foreign boundary/);
  assert.deepEqual(c.rows.filter(r => r.state === 'ready').map(r => r.cases), other.controls.rows.filter(r => r.state === 'ready').map(r => r.cases));
});

test('trace-only reference preserves existing selection and records source-order nested and repeated calls', t => {
  const f = fixture(t), ref = createRecordRuleReference(f.graph);
  for (const id of ['choose', 'repeated']) {
    const contract: any = f.graph.nodes.find(n => n.selector === 'alpha:' + id)!.body.typed_contract;
    for (const [total, active] of [[101n, true], [1n, true], [1n, false]] as const) {
      const values = {total, other: 2n, active}, scope = new Map(contract.inputs.map((p: any) => [p.name, {type: p.type, value: values[p.name as keyof typeof values]}]));
      const before = ref.select(contract, scope as any), trace = ref.tracePolicy(contract, scope as any);
      assert.deepEqual({target: trace.target, index: trace.index}, before); assert.deepEqual(ref.select(contract, scope as any), before);
      assert.deepEqual(trace.calls[0]!.input, {amount: total}); assert.equal(trace.calls[1]!.parent, 0);
      assert.equal(trace.calls[1]!.selector, 'alpha:high');
      assert.equal(trace.calls.length, total === 101n ? 2 : id === 'repeated' ? 5 : 3);
    }
  }
});

test('unvisited selected Rule keeps the whole Policy family incomplete despite distinct outcomes', t => {
  const f = fixture(t), manifest = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  manifest.nodes.push('unvisited'); f.write('specs/alpha/feature.json', manifest);
  f.write('specs/alpha/nodes/unvisited.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'unvisited', kind: 'Rule', body: {
    description: 'Selected but shadowed Rule.', predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'INTEROP-UNVISITED',
      parameters: [{name: 'value', type: scalar('Bool')}], expression: {op: 'eq', left: at('value'), right: lit('Bool', true)}}}});
  const policy = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/nodes/choose.json'), 'utf8'));
  policy.body.typed_contract.cases[1] = {target: 'alpha:perform', rule: {selector: 'alpha:enabled', arguments: [arg('value', lit('Bool', true))]}};
  policy.body.typed_contract.cases.push({target: 'alpha:compute', rule: {selector: 'alpha:unvisited', arguments: [arg('value', at('active'))]}});
  f.write('specs/alpha/nodes/choose.json', policy);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledProject(graph, f.selection);
  const boundary = createCrossGeneratorBoundary(graph, plan, boundaryDefinition), controls = createCrossGeneratorPolicyControls(graph, plan, boundary, definition);
  const row = controls.rows.find(r => r.selector === 'alpha:choose')!;
  assert.equal(row.state, 'not_evaluable'); assert.match((row as any).reason, /selected Rule unvisited/);
  assert.equal('cases' in row, false);
  assert.equal(crossGeneratorPolicyProbe(controls).rows.some(r => r.selector === row.selector), false);
  const edge = boundary.edges.find(e => e.importer_selectors.includes(row.selector) && e.target_selectors.includes('alpha:unvisited'))!;
  assert.equal(controls.coverage.find(e => e.edge_sha256 === edge.edge_sha256)!.status, 'not_evaluable');
});

test('original native Rules and Policies match exact source-derived traces in both module roots', t => {
  for (const root of ['domain', 'application/domain']) {
    const f = fixture(t, root), n = native(f); n.compile();
    const observation = n.run(), result = checkCrossGeneratorPolicyObservations(f.controls, observation);
    t.diagnostic('native-policy-evidence ' + JSON.stringify({module_root: root, ...result}));
    assert.equal(result.tested_policy_count, 4); assert.ok(result.tested_case_count > 100); assert.ok(result.tested_call_count > 100);
    assert.deepEqual(result.remaining.map(r => r.selector), ['alpha:constant']);
    assert.ok(result.uncovered_runtime_edge_count > 0); assert.equal(result.public_cross_generator_behavior, 'not_evaluable');
    // Policy targets are identifiers: native execution must not load their code.
    for (const m of f.plan.resolved.modules.filter(m => m.metatypes.some(k => k === 'Operation' || k === 'Calculation'))) fs.writeFileSync(path.join(n.output, m.relative_path.replace(/\.ts$/, '.js')), 'throw new Error("POLICY_TARGET_EXECUTED");');
    assert.deepEqual(n.run(), observation);
  }
});

test('native-compiling argument, predicate, order, duplicate and omitted-call mutations cannot pass', t => {
  const f = fixture(t), n = native(f), policy = 'domain/features/alpha/src/domain/policies/choose.provider.ts';
  const mutations: [string, string, (s: string) => string][] = [
    ['argument', policy, s => s.replace('["amount"]:p0', '["amount"]:p1')],
    ['predicate', 'domain/features/alpha/src/domain/rules/high.ts', s => s.replace('100n < p0', '101n < p0')],
    ['order', policy, s => {const lines = s.split('\n'), ids = lines.flatMap((l, i) => l.includes('if(condition') ? [i] : []); assert.equal(ids.length, 2); [lines[ids[0]!], lines[ids[1]!]] = [lines[ids[1]!], lines[ids[0]!]]; return lines.join('\n');}],
    ['duplicate', policy, s => s.replace('  if(condition', '  condition1({["amount"]:p0});\n  if(condition')],
    ['omitted', policy, s => s.replace('if(condition1({["amount"]:p0}))', 'if(p0 > 100n)')],
  ];
  for (const [id, file, mutation] of mutations) {
    n.restore(); n.mutate(file, mutation); n.compile();
    assert.throws(() => checkCrossGeneratorPolicyObservations(f.controls, n.run()), /native observation mismatch/, id);
  }
  n.restore(); n.compile(); checkCrossGeneratorPolicyObservations(f.controls, n.run());
});

test('complete observation accounting rejects omitted, extra, reordered and foreign cases or calls', t => {
  const f = fixture(t), n = native(f); n.compile(); const baseline = n.run();
  checkCrossGeneratorPolicyObservations(f.controls, baseline);
  const mutations: ((v: any) => void)[] = [
    v => v.rows.pop(), v => v.rows.push(v.rows[0]), v => v.rows.reverse(), v => v.rows[0].cases.pop(),
    v => v.rows[0].cases.push(v.rows[0].cases[0]), v => v.rows[0].cases.reverse(), v => {v.controls_sha256 = '0'.repeat(64);},
    v => {v.extra = true;}, v => {const c = v.rows.flatMap((r: any) => r.cases).find((c: any) => c.calls.length > 1); c.calls.pop();},
    v => {const c = v.rows.flatMap((r: any) => r.cases).find((c: any) => c.calls.length > 1); c.calls.reverse();},
    v => {v.rows[0].cases[0].getter_reads = 1;}, v => {v.rows[0].cases[0].input_changed = true;},
  ];
  for (const mutate of mutations) {const value = structuredClone(baseline); mutate(value); assert.throws(() => checkCrossGeneratorPolicyObservations(f.controls, value), /native observation mismatch/);}
  let reads = 0; const active: any = {}; Object.defineProperty(active, 'rows', {enumerable: true, get() {reads++; return [];} });
  assert.throws(() => checkCrossGeneratorPolicyObservations(f.controls, active)); assert.equal(reads, 0);
  assert.throws(() => checkCrossGeneratorPolicyObservations(structuredClone(f.controls), baseline), /registered controls/);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
