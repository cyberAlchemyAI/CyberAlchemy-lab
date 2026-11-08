import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {workflowFixture, workflowProject, stepIds} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, named} from '../helpers/workflow-values.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {createWorkflowEffectAudit, WORKFLOW_EFFECT_AUDIT_RUNNER, WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-effect-audit.ts';
import {createWorkflowCases, isWorkflowCasesCapacity} from '../../src/verification/reconciled-workflow-cases.ts';

const base = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definition = fs.readFileSync(path.join(base, 'semantic-workflow-effect-audit-contract.json'), 'utf8');
const bindingDefinition = fs.readFileSync(path.join(base, 'semantic-workflow-binding-contract.json'), 'utf8');
function selected(f: ReturnType<typeof workflowFixture>) {
  const plan = planCompiledReconciledProject(f.graph, f.selection);
  return {plan, profile: createWorkflowEffectAudit(f.graph, plan, bindingDefinition, definition)};
}
function plainEnum(t: Parameters<typeof workflowFixture>[0]) {
  const f = workflowValuesFixture(t, {type: named('choice')}), source = path.join(f.root, 'source'), p = path.join(source, 'specs/commerce/nodes/choice.json'), node = JSON.parse(fs.readFileSync(p, 'utf8'));
  node.body.typed_contract.variants.forEach((v: any) => v.payload = null); fs.writeFileSync(p, JSON.stringify(node));
  return {...f, graph: loadCompiledProjectGraph(source)};
}
function fixture(f: ReturnType<typeof workflowFixture>) {
  const {plan, profile} = selected(f), root = fs.mkdtempSync(path.join(f.root, 'effect-audit-'));
  for (const a of plan.resolved.artifacts) {const p = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, a.content);}
  const require = createRequire(import.meta.url), typeFile = require.resolve('@types/node/package.json', {paths: [path.join(workflowProject, 'impl'), ...process.execArgv.filter(p => p.endsWith('loader.mjs')).map(p => path.dirname(p))]}), deps = path.dirname(path.dirname(path.dirname(typeFile)));
  fs.writeFileSync(path.join(root, 'package.json'), '{"type":"module"}');
  const sourceConfig = path.join(root, 'tsconfig.source.json'), nativeConfig = path.join(root, 'tsconfig.native.json');
  fs.writeFileSync(sourceConfig, JSON.stringify({compilerOptions: {strict: true, skipLibCheck: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: ['node'], typeRoots: [path.join(deps, '@types')], rootDir: root, outDir: path.join(root, 'js')}, files: plan.resolved.artifacts.map(a => path.join(root, a.relative_path))}));
  fs.writeFileSync(nativeConfig, JSON.stringify({compilerOptions: {allowJs: true, checkJs: false, noEmit: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: []}, files: profile.module_paths.map(p => path.join(root, 'js', p.replace(/\.ts$/, '.js')))}));
  const chain = JSON.parse(fs.readFileSync(path.resolve(workflowProject, '../../toolchains/node-typescript/toolchain.json'), 'utf8'));
  const image = nativeToolchainImage(chain.container_image);
  assert.equal(image, NATIVE_TEST_IMAGE_ID);
  const docker = ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', process.getuid!() + ':' + process.getgid!(), '--mount', 'type=bind,source=' + root + ',target=' + root, '--mount', 'type=bind,source=' + deps + ',target=' + deps + ',readonly', '--workdir', root, image];
  const command = (args: string[]) => {
    try {return execFileSync('docker', [...docker, ...args], {encoding: 'utf8', stdio: 'pipe'});} catch (e) {const error = e as any; throw new Error([error.message, error.stdout, error.stderr].filter(Boolean).join('\n'));}
  };
  const compile = () => command(['tsc', '-p', sourceConfig, '--pretty', 'false']);
  const script = path.join(root, 'workflow-effects.mjs'); fs.writeFileSync(script, WORKFLOW_EFFECT_AUDIT_RUNNER);
  const input = (phase: 'source' | 'native'): any => ({phase, definition, module_root: phase === 'source' ? root : path.join(root, 'js'), module_paths: profile.module_paths.map(p => p.replace(/\.ts$/, phase === 'native' ? '.js' : '.ts')), workflow_modules: profile.workflow_modules, support_modules: profile.support_modules});
  const audit = (phase: 'source' | 'native', change?: (input: any) => void) => {
    const row = input(phase); change?.(row); const p = path.join(root, 'audit-' + phase + '.json'); fs.writeFileSync(p, JSON.stringify(row));
    return JSON.parse(command(['node', script, '/opt/node-toolchain/node_modules/typescript', phase === 'source' ? sourceConfig : nativeConfig, p]));
  };
  const freshProviderHashes = (row: any) => {row.workflow_modules = row.workflow_modules.map((m: any) => ({...m, source_sha256: sha256(fs.readFileSync(path.join(root, m.relative_path), 'utf8'))}));};
  return {root, plan, profile, input, audit, compile, freshProviderHashes};
}
const violations = (o: any) => o.modules.flatMap((m: any) => m.violations.map((v: any) => ({...v, module: m.relative_path})));

test('audit closure is branded, deterministic, source-bound and independent of finite-case availability', t => {
  const f = workflowFixture(t), {plan, profile} = selected(f);
  assert.equal(sha256(definition), WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256);
  assert.deepEqual(profile.roots, ['commerce:flow']); assert.ok(Object.isFrozen(profile.workflow_modules));
  assert.equal(canonicalJson(createWorkflowEffectAudit(f.graph, plan, bindingDefinition, definition)), canonicalJson(profile));
  assert.ok(profile.module_paths.some(p => p.endsWith('/perform.provider.ts')));
  assert.ok(!profile.module_paths.some(p => p.endsWith('/undo.provider.ts')), 'compensation-only module is not a forward import');
  assert.throws(() => createWorkflowEffectAudit({...f.graph} as any, plan, bindingDefinition, definition));
  assert.throws(() => createWorkflowEffectAudit(f.graph, {...plan} as any, bindingDefinition, definition));
  assert.throws(() => createWorkflowEffectAudit(f.graph, plan, bindingDefinition + '\n', definition), /binding definition drift/);
  assert.throws(() => createWorkflowEffectAudit(f.graph, plan, bindingDefinition, definition + '\n'), /definition drift/);
  const other = workflowFixture(t, {noCompensations: true}); assert.throws(() => createWorkflowEffectAudit(other.graph, plan, bindingDefinition, definition), /cross-graph/);
  const source = path.join(f.root, 'source'), file = path.join(source, 'specs/commerce/nodes/flow.json'), flow = JSON.parse(fs.readFileSync(file, 'utf8')), selection: any = structuredClone(f.selection);
  const ids = [...stepIds, ...Array.from({length: 124}, (_, i) => 'step-' + i)];
  flow.body.typed_contract.steps = ids.map(step_id => ({step_id, operation_ref: 'commerce:perform'})); fs.writeFileSync(file, JSON.stringify(flow));
  selection.workflows[0].steps = ids.map((step_id, i) => ({step_id, arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: ids[i - 1], properties: []} : {op: 'input', name: 'amount', properties: []}}], events: []}));
  const graph = loadCompiledProjectGraph(source), large = selected({...f, graph, selection});
  const definitions: any = Object.fromEntries(Object.entries({execution: 'semantic-workflow-execution-contract.json', binding: 'semantic-workflow-binding-contract.json', values: 'semantic-workflow-values-contract.json', outcomes: 'semantic-workflow-controls-contract.json'}).map(([k, p]) => [k, fs.readFileSync(path.join(base, p), 'utf8')]));
  assert.throws(() => createWorkflowCases(graph.nodes.find(n => n.kind === 'Workflow')!, graph, large.plan, definitions, fs.readFileSync(path.join(base, 'semantic-workflow-cases-contract.json'), 'utf8')), isWorkflowCasesCapacity);
  assert.deepEqual(large.profile.roots, profile.roots); assert.deepEqual(large.profile.module_paths, profile.module_paths);
});

test('clean TypeScript and strict-emitted ESM Workflow closures pass with exact module hashes', t => {
  for (const f of [workflowFixture(t), workflowValuesFixture(t, {type: named('choice'), events: true}), workflowFixture(t, {dependencies: [[], ['undo-first'], ['undo-second']]}), plainEnum(t)]) {
    const c = fixture(f); c.compile();
    for (const phase of ['source', 'native'] as const) {
      const o = c.audit(phase); assert.equal(o.schema_version, 'domainspec.workflow-effect-observation/v1-candidate'); assert.equal(o.phase, phase); assert.equal(o.definition_sha256, WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256);
      assert.deepEqual(violations(o), []); assert.deepEqual(o.modules.map((m: any) => m.relative_path), c.input(phase).module_paths);
      for (const m of o.modules) assert.equal(m.source_sha256, sha256(fs.readFileSync(path.join(c.input(phase).module_root, m.relative_path), 'utf8')));
    }
    t.diagnostic(JSON.stringify({modules: c.profile.module_paths.length, support: c.profile.support_modules.length}));
  }
});

test('strict-compiling metadata helper mutations are rejected in source and emitted ESM', t => {
  const c = fixture(workflowFixture(t)), p = path.join(c.root, c.profile.workflow_modules[0]!.relative_path), original = fs.readFileSync(p, 'utf8');
  const changes = [
    (s: string) => s.replace("createHash('sha256')", "createHash('sha1')"),
    (s: string) => s.replace(".digest('hex')", ".digest('base64')"),
    (s: string) => s.replace('.update(canonical(v))', '.update(JSON.stringify(v))'),
    (s: string) => s.replace('.update(canonical(v))', '.update(canonical(v), "utf8")'),
    (s: string) => s.replace('const digest=', 'let digest='),
    (s: string) => s.replace('const digest=(v:unknown):string=>', 'const digest:any=async(v:unknown)=>'),
    (s: string) => s.replace('import {createHash}', 'import {createHash as otherHash}').replace("createHash('sha256')", "otherHash('sha256')"),
    (s: string) => s + '\nconst escapeHash=createHash;\n',
    (s: string) => s + '\nexport {createHash};\n',
    (s: string) => s + '\nconst extraHash=()=>createHash("sha256").update("other").digest("hex");\n',
    (s: string) => s.replace("createHash('sha256')", "createHash?.('sha256')"),
    (s: string) => s.replace("createHash('sha256')", "createHash('sha256',{})"),
    (s: string) => s.replace('const digest=(v:unknown):string=>', 'const digest=(v:unknown="default"):string=>')
  ];
  for (const [i, mutate] of changes.entries()) {
    const next = mutate(original); assert.notEqual(next, original); fs.writeFileSync(p, next); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).some((v: any) => v.code.startsWith('crypto-')), phase + ' mutation ' + i);
  }
  t.diagnostic(JSON.stringify({compiling_mutations: changes.length, phase_comparisons: changes.length * 2}));
});

test('crypto cannot move to another module or expand into other external imports', t => {
  const c = fixture(workflowFixture(t)), provider = path.join(c.root, c.profile.workflow_modules[0]!.relative_path), op = path.join(c.root, c.profile.module_paths.find(p => p.endsWith('/perform.provider.ts'))!), original = fs.readFileSync(provider, 'utf8'), operation = fs.readFileSync(op, 'utf8');
  for (const [file, before, addition] of [[op, operation, 'import {createHash} from "node:crypto";\nconst unexpected=()=>createHash("sha256").digest("hex");'], [provider, original, 'import {randomUUID} from "node:crypto";\nconst unexpected=()=>randomUUID();'], [provider, original, 'import * as crypt from "node:crypto";\nconst unexpected=()=>crypt.createHash("sha256").digest("hex");'], [provider, original, 'import {readFileSync} from "node:fs";\nconst unexpected=()=>readFileSync("/unused");'], [provider, original, 'export {createHash as renamedHash} from "node:crypto";']] as const) {
    fs.writeFileSync(provider, original); fs.writeFileSync(op, operation); fs.writeFileSync(file, before + '\n' + addition); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).some((v: any) => ['crypto-binding', 'crypto-escape', 'external-import'].includes(v.code)));
  }
});

test('inherited ambient, class, dynamic-import and Object mutation restrictions survive both phases', t => {
  const c = fixture(workflowFixture(t)), p = path.join(c.root, c.profile.workflow_modules[0]!.relative_path), original = fs.readFileSync(p, 'utf8');
  const changes = ['const forbidden=()=>Date.now();', 'class Forbidden {}', 'const forbidden=()=>Object.defineProperty({},"x",{value:1});', 'const forbidden=()=>Object.freeze(Object.prototype);', 'const forbidden=()=>import("node:crypto");', 'const forbidden=()=>Promise.resolve(1);', 'const forbidden=()=>globalThis;', 'const forbidden=()=>D\\u0061te.now();'];
  for (const addition of changes) {
    fs.writeFileSync(p, original + '\n' + addition); c.compile();
    for (const phase of ['source', 'native'] as const) assert.ok(violations(c.audit(phase, c.freshProviderHashes)).length > 0, phase + ' ' + addition);
  }
});

test('source pins, phases and exact exception metadata reject drift and malformed requests', t => {
  const c = fixture(workflowFixture(t)); c.compile();
  for (const change of [
    (v: any) => v.definition += '\n', (v: any) => v.phase = 'other', (v: any) => v.module_root = 'relative',
    (v: any) => v.module_paths.push(v.module_paths[0]), (v: any) => v.module_paths[0] = '../escape.ts',
    (v: any) => v.workflow_modules = [...v.workflow_modules, ...v.workflow_modules],
    (v: any) => v.workflow_modules = [{...v.workflow_modules[0], relative_path: 'other.ts'}],
    (v: any) => v.workflow_modules = [{...v.workflow_modules[0], source_sha256: v.workflow_modules[0].source_sha256 + '\n'}],
    (v: any) => v.workflow_modules = [{...v.workflow_modules[0], source_sha256: '0'.repeat(64)}],
    (v: any) => v.support_modules = v.workflow_modules
  ]) assert.throws(() => c.audit('source', change), /WORKFLOW_EFFECT_AUDIT:/);
  assert.ok(violations(c.audit('source', v => v.workflow_modules = [])).some((v: any) => v.code === 'crypto-binding'));
  const p = path.join(c.root, c.profile.workflow_modules[0]!.relative_path); fs.appendFileSync(p, '\n// drift\n');
  assert.throws(() => c.audit('source'), /Workflow source drift/);
});

test('pinned Enum support remains narrow in native code and cannot authorize application classes', t => {
  const c = fixture(plainEnum(t)); assert.equal(c.profile.support_modules.length, 1);
  const p = path.join(c.root, c.profile.support_modules[0]!.relative_path), original = fs.readFileSync(p, 'utf8');
  for (const addition of ['export class AddedClass {}', 'const mutate=()=>Object.defineProperty({},"x",{value:1});']) {
    fs.writeFileSync(p, original + '\n' + addition); c.compile();
    assert.throws(() => c.audit('source'), /support source drift/);
    assert.ok(violations(c.audit('native')).some((v: any) => ['impure-form', 'object-mutation'].includes(v.code)));
  }
});

test('native-only helper drift is observed even when source bytes and source audit remain clean', t => {
  const c = fixture(workflowFixture(t)); c.compile();
  const source = c.audit('source'); assert.deepEqual(violations(source), []);
  const nativePath = c.profile.workflow_modules[0]!.relative_path.replace(/\.ts$/, '.js'), p = path.join(c.root, 'js', nativePath), original = fs.readFileSync(p, 'utf8');
  const changed = original.replace(/createHash\(['"]sha256['"]\)/, 'createHash("sha1")'); assert.notEqual(changed, original); fs.writeFileSync(p, changed);
  assert.deepEqual(c.audit('source'), source);
  const native = c.audit('native'); assert.ok(violations(native).some((v: any) => v.code === 'crypto-helper'));
  assert.equal(native.modules.find((m: any) => m.relative_path === nativePath).source_sha256, sha256(changed));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
