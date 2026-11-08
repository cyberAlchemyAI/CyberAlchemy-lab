import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicFixture, publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {createCompositionBinding, COMPOSITION_BINDING_DEFINITION_SHA256} from '../../src/verification/reconciled-composition-binding.ts';
import {createCompositionEffectAudit, COMPOSITION_EFFECT_AUDIT_RUNNER, COMPOSITION_EFFECT_DEFINITION_SHA256} from '../../src/verification/reconciled-composition-effect-audit.ts';
const project = path.resolve(import.meta.dirname, '../../../..'), base = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const bindingDefinition = fs.readFileSync(path.join(base, 'semantic-composition-binding-contract.json'), 'utf8'), definition = fs.readFileSync(path.join(base, 'semantic-composition-effect-audit-contract.json'), 'utf8');
function selected(t: any, moduleRoot = 'domain', noCalculations = false) {
  const f = publicFixture(t);
  let graph = f.graph;
  if (noCalculations) {
    const source = structuredClone(f.composition), c = source.contract;
    c.calculations = {}; delete source.core_bindings.Net; delete source.core_bindings.Other;
    c.nodes.find((n: any) => n.id === 'Emit').fields = {net: {op: 'call', name: 'text', args: [{op: 'path', path: ['Parsed', 'qty']}]}, other: {op: 'call', name: 'text', args: [{op: 'path', path: ['Parsed', 'rebate']}]}};
    source.source_text = JSON.stringify(c, null, 2) + '\n'; const hash = sha256(source.source_text);
    source.ontology.source.sha256 = hash; source.ontology.composition_trace = compileDeclarativeFunction(c).trace as any;
    source.ontology.nodes = source.ontology.nodes.filter((n: any) => !['Net', 'Other'].includes(n.name));
    for (const n of source.ontology.nodes) {n.source.sha256 = hash; if (n.name === 'Emit') n.typed_contract = c.nodes.find((n: any) => n.id === 'Emit');}
    source.ontology.references = source.ontology.references.filter((r: any) => !['TEST-ALPHA', 'TEST-BETA'].includes(r.source) && !['TEST-ALPHA', 'TEST-BETA'].includes(r.target));
    source.ontology.references.forEach((r: any) => {r.evidence.sha256 = hash;});
    f.write('compositions/calculate.json', source); graph = loadCompiledProjectGraph(f.source);
  }
  const plan = planCompiledReconciledProject(graph, publicSelection(moduleRoot));
  const binding = createCompositionBinding(graph, plan, 'calculate', bindingDefinition);
  return {...f, graph, plan, binding, profile: createCompositionEffectAudit(binding, definition)};
}
function nativeFixture(t: any, moduleRoot?: string, noCalculations = false) {
  const f = selected(t, moduleRoot, noCalculations), root = path.join(f.root, 'audit'); fs.mkdirSync(root);
  const all = [...f.plan.resolved.artifacts, ...f.plan.composition!.artifacts];
  for (const a of all) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const require = createRequire(import.meta.url), types = require.resolve('@types/node/package.json', {paths: process.execArgv.filter(p => p.endsWith('loader.mjs')).map(p => path.dirname(p))});
  const deps = path.dirname(path.dirname(path.dirname(types))), out = path.join(root, 'js');
  fs.writeFileSync(path.join(root, 'package.json'), '{"type":"module"}');
  const sourceConfig = path.join(root, 'tsconfig.source.json'), nativeConfig = path.join(root, 'tsconfig.native.json');
  fs.writeFileSync(sourceConfig, JSON.stringify({compilerOptions: {strict: true, skipLibCheck: true, allowJs: true, checkJs: false, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: ['node'], typeRoots: [path.join(deps, '@types')], rootDir: root, outDir: out}, files: f.binding.modules.map(m => path.join(root, m.relative_path))}));
  fs.writeFileSync(nativeConfig, JSON.stringify({compilerOptions: {allowJs: true, checkJs: false, noEmit: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: []}, files: f.binding.modules.map(m => path.join(out, m.relative_path.replace(/\.ts$/, '.js')))}));
  const image = nativeToolchainImage();
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + root + ',target=' + root, '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--workdir', root, image];
  const command = (args: string[]) => {try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', timeout: 60000, stdio: 'pipe'});} catch (error: any) {throw Error([error.message, error.stdout, error.stderr].filter(Boolean).join('\n'));}};
  const script = path.join(root, 'effects.mjs'); fs.writeFileSync(script, COMPOSITION_EFFECT_AUDIT_RUNNER);
  const compile = () => command(['tsc', '-p', sourceConfig, '--pretty', 'false']);
  const input = (phase: 'source' | 'native'): any => ({...f.profile, definition, phase, module_root: phase === 'source' ? root : out, module_paths: f.binding.modules.map(m => m.relative_path.replace(/\.ts$/, phase === 'source' ? '.ts' : '.js'))});
  const audit = (phase: 'source' | 'native', change?: (input: any) => void) => {
    const row = structuredClone(input(phase)); change?.(row);
    const file = path.join(root, 'input-' + phase + '.json'); fs.writeFileSync(file, JSON.stringify(row));
    return JSON.parse(command(['node', script, '/opt/node-toolchain/node_modules/typescript', phase === 'source' ? sourceConfig : nativeConfig, file]));
  };
  // Mutation fixtures deliberately refresh only byte pins so AST rejection, not
  // the unchanged-source check, must expose the compiling code defect.
  const refresh = (row: any) => {
    row.binding.modules.forEach((m: any) => {m.source_sha256 = sha256(fs.readFileSync(path.join(root, m.relative_path)));});
    const {binding_sha256, ...body} = row.binding; row.binding.binding_sha256 = sha256(canonicalJson(body));
  };
  return {...f, root, out, input, audit, compile, refresh};
}
const violations = (o: any) => o.modules.flatMap((m: any) => m.violations.map((v: any) => ({...v, module: m.relative_path})));

test('source-derived binding distinguishes source identities, structural bridges and exact computation closure', t => {
  const f = selected(t);
  assert.equal(sha256(bindingDefinition), COMPOSITION_BINDING_DEFINITION_SHA256);
  assert.equal(sha256(definition), COMPOSITION_EFFECT_DEFINITION_SHA256);
  assert.deepEqual(f.binding, createCompositionBinding(f.graph, f.plan, 'calculate', bindingDefinition));
  assert.notEqual(f.binding.composition_source_sha256, f.binding.authored_text_sha256);
  assert.equal(f.binding.modules.length, 6);
  assert.deepEqual(f.binding.bridges.map(b => [b.name, b.role]), [['Net', 'calculation-call'], ['Other', 'calculation-call'], ['Values', 'structural-record']]);
  assert.equal(f.binding.bridges[2]!.native_target, null);
  assert.ok(f.binding.modules.every(m => !m.relative_path.includes('/operations/') && !m.relative_path.includes('/entities/')));
  assert.deepEqual(f.binding.modules.find(m => m.relative_path === f.binding.adapter_path)!.imports.map(i => [i.imported, i.local]), [['calculateCompute', 'calculation0'], ['calculateCompute', 'calculation1']]);
  assert.ok(Object.isFrozen(f.binding.modules[0]!.imports));
  assert.throws(() => createCompositionBinding(structuredClone(f.graph), f.plan, 'calculate', bindingDefinition), /unvalidated or changed/);
  assert.throws(() => createCompositionBinding(f.graph, structuredClone(f.plan), 'calculate', bindingDefinition), /registered|unchanged|plan/);
  assert.throws(() => createCompositionBinding(f.graph, f.plan, 'wrong', bindingDefinition), /source composition ID/);
  assert.throws(() => createCompositionBinding(f.graph, f.plan, 'calculate', bindingDefinition + '\n'), /definition drift/);
  assert.throws(() => createCompositionEffectAudit(structuredClone(f.binding), definition), /registered/);
  assert.throws(() => createCompositionEffectAudit(f.binding, definition + '\n'), /definition drift/);
  const other = selected(t, 'alternate');
  const file = 'specs/alpha/nodes/perform.json', changed = JSON.parse(fs.readFileSync(path.join(other.source, file), 'utf8'));
  changed.body.description += ' A distinct checked source.'; other.write(file, changed);
  assert.throws(() => createCompositionBinding(loadCompiledProjectGraph(other.source), f.plan, 'calculate', bindingDefinition), /cross-graph/);
});

test('clean source and strict-emitted native ESM match exact source-derived surfaces', t => {
  for (const [moduleRoot, noCalculations] of [['domain', false], ['alternate/deeper', false], ['domain', true]] as const) {
    const f = nativeFixture(t, moduleRoot, noCalculations); f.compile();
    assert.equal(f.binding.modules.length, noCalculations ? 2 : 6);
    for (const phase of ['source', 'native'] as const) {
      const observation = f.audit(phase);
      assert.deepEqual(violations(observation), []);
      assert.deepEqual(observation.modules.map((m: any) => m.relative_path), f.input(phase).module_paths);
      assert.equal(observation.definition_sha256, COMPOSITION_EFFECT_DEFINITION_SHA256);
      for (const m of observation.modules) assert.equal(m.source_sha256, sha256(fs.readFileSync(path.join(f.input(phase).module_root, m.relative_path))));
    }
  }
});

test('compiling native binding and effect mutations reject in both parsed phases', t => {
  const f = nativeFixture(t), behavior = path.join(f.root, f.binding.behavior_path), adapter = path.join(f.root, f.binding.adapter_path);
  const original = fs.readFileSync(behavior, 'utf8'), originalAdapter = fs.readFileSync(adapter, 'utf8');
  f.compile(); for (const phase of ['source', 'native'] as const) assert.deepEqual(violations(f.audit(phase)), [], 'clean baseline before mutants');
  const mutations: [string, string, string][] = [
    ['extra export', behavior, original + '\nexport const Unexpected=1;'],
    ['ambient time', behavior, original + '\nconst unexpected=()=>Date.now();'],
    ['random', behavior, original + '\nconst unexpected=()=>Math.random();'],
    ['process alias', behavior, original + '\nconst unexpected=process;'],
    ['global computed escape', behavior, original + '\nconst unexpected=globalThis["process"];'],
    ['unicode ambient', behavior, original + '\nconst unexpected=proce\\u0073s;'],
    ['dynamic import', behavior, original + '\nconst unexpected=()=>import("node:fs");'],
    ['external import', behavior, original + '\nimport {readFileSync} from "node:fs";'],
    ['class', behavior, original + '\nclass Unexpected {}'],
    ['async', behavior, original + '\nconst unexpected=async()=>1;'],
    ['prototype escape', behavior, original + '\nconst unexpected=Object.prototype;'],
    ['mutation alias', behavior, original + '\nconst unexpected=Object.defineProperty;'],
    ['mutation destructuring', behavior, original + '\nconst {defineProperty:unexpected}=Object;'],
    ['computed constructor', behavior, original + '\nconst unexpected=(()=>{})["con"+"structor"];'],
    ['import alias drift', adapter, originalAdapter.replace('as calculation0', 'as changed').replace('return calculation0(', 'return changed(')],
    ['default export', behavior, original + '\nexport default 1;'],
    ['re-export', behavior, original + '\nexport {evaluateCalculation as Unexpected} from "./core-api.js";'],
    ['Reflect escape', behavior, original + '\nconst unexpected=Reflect.ownKeys;'],
    ['Reflect mutation', behavior, original + '\nconst unexpected=()=>Reflect.set({},"x",1);'],
    ['indirect prototype escape', behavior, original + '\nconst unexpected=Object.getPrototypeOf({});'],
    ['argument projection', adapter, originalAdapter.replace('d["qty"]!.value', 'd["rebate"]!.value')],
    ['wrong Calculation call', adapter, originalAdapter.replace('return calculation0(', 'return calculation1(')],
    ['argument declaration order', adapter, originalAdapter.replace('["qty","rebate"]', '["rebate","qty"]')],
    ['case identity', adapter, originalAdapter.replace('case "Net":', 'case "Wrong":')]
  ];
  for (const [name, file, content] of mutations) {
    fs.writeFileSync(behavior, original); fs.writeFileSync(adapter, originalAdapter); fs.writeFileSync(file, content); f.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(f.audit(phase, f.refresh)).length, name + ':' + phase);
  }
  t.diagnostic(JSON.stringify({strict_compiling_mutants: mutations.length, phase_observations: mutations.length * 2}));
});

test('audit input identity, phase, complete paths and current source bytes fail closed', t => {
  const f = nativeFixture(t); f.compile();
  for (const mutate of [(r: any) => r.phase = 'unknown', (r: any) => r.definition += '\n', (r: any) => r.module_paths.pop(), (r: any) => r.module_paths.push(r.module_paths[0]), (r: any) => r.module_paths[0] = '../escape.ts', (r: any) => r.binding.bridges[0].arguments.reverse()]) assert.throws(() => f.audit('source', mutate));
  const file = path.join(f.root, f.binding.behavior_path), original = fs.readFileSync(file);
  fs.appendFileSync(file, '\n// drift'); assert.throws(() => f.audit('source'), /source drift/);
  fs.writeFileSync(file, original);
  const backup = path.join(f.root, 'behavior-original.mjs'); fs.renameSync(file, backup); fs.symlinkSync(backup, file);
  assert.throws(() => f.audit('source'), /symbolic artifact/);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
