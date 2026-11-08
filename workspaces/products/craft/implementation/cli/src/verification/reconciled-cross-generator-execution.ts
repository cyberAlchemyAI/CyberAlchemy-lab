import {assertCrossGeneratorOperationControls, crossGeneratorOperationProbe, checkCrossGeneratorOperationObservations, type CrossGeneratorOperationControls} from './reconciled-cross-generator-operation.js';
import {CROSS_GENERATOR_OPERATION_DEFINITION_SHA256} from './reconciled-cross-generator-operation-surface.js';
import {CROSS_GENERATOR_OPERATION_RUNNER} from './reconciled-cross-generator-operation-runner.js';
import {CROSS_GENERATOR_OPERATION_AUDIT_RUNNER} from './reconciled-cross-generator-operation-audit.js';
import {assertCrossGeneratorValueProducerSurface, type CrossGeneratorValueProducerSurface} from './reconciled-cross-generator-factory-surface.js';
import {crossGeneratorValueProducerProbe, checkCrossGeneratorValueProducerObservations, CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256} from './reconciled-cross-generator-value-producer.js';
import {CROSS_GENERATOR_VALUE_PRODUCER_RUNNER} from './reconciled-cross-generator-value-producer-runner.js';
import {CROSS_GENERATOR_VALUE_PRODUCER_AUDIT_RUNNER} from './reconciled-cross-generator-factory-audit.js';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertCrossGeneratorPolicyControls, crossGeneratorPolicyProbe, checkCrossGeneratorPolicyObservations, type CrossGeneratorPolicyControls} from './reconciled-cross-generator-policy.js';
import {CROSS_GENERATOR_POLICY_RUNNER} from './reconciled-cross-generator-policy-runner.js';
import {CROSS_GENERATOR_AUDIT_RUNNER, CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256, CROSS_GENERATOR_STATE_MACHINE_AUDIT_RUNNER} from './reconciled-cross-generator-audit.js';
import {assertCrossGeneratorStateMachineControls, crossGeneratorStateMachineProbe, checkCrossGeneratorStateMachineObservations, CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256, type CrossGeneratorStateMachineControls} from './reconciled-cross-generator-state-machine.js';
import {CROSS_GENERATOR_STATE_MACHINE_RUNNER} from './reconciled-cross-generator-state-machine-runner.js';
import {assertCrossGeneratorFactorySurface, CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256, type CrossGeneratorFactorySurface} from './reconciled-cross-generator-factory-surface.js';
import {crossGeneratorFactoryProbe, checkCrossGeneratorFactoryObservations} from './reconciled-cross-generator-factory.js';
import {CROSS_GENERATOR_FACTORY_RUNNER} from './reconciled-cross-generator-factory-runner.js';
import {CROSS_GENERATOR_FACTORY_AUDIT_RUNNER, CROSS_GENERATOR_OWNED_VALUES_AUDIT_RUNNER} from './reconciled-cross-generator-factory-audit.js';

import {assertCrossGeneratorOwnedValueSurface, CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256, type CrossGeneratorOwnedValueSurface} from './reconciled-cross-generator-factory-surface.js';
import {crossGeneratorOwnedValueProbe, checkCrossGeneratorOwnedValueObservations} from './reconciled-cross-generator-owned-values.js';
import {CROSS_GENERATOR_OWNED_VALUES_RUNNER} from './reconciled-cross-generator-owned-values-runner.js';

export interface CrossGeneratorExecutionOptions {workspace_parent: string; typescript_root: string;}
export class CrossGeneratorExecutionError extends Error {
  constructor(readonly phase: string, reason: string, readonly workspace?: string) {super('CROSS_GENERATOR_EXECUTION:' + phase + ':' + reason); this.name = 'CrossGeneratorExecutionError';}
}
const receipts = new WeakMap<object, () => void>();
function absolute(p: string) {
  if (typeof p !== 'string' || !path.isAbsolute(p) || path.resolve(p) !== p || fs.realpathSync(p) !== p) throw Error('normalized nonsymbolic absolute path required');
  return p;
}
function read(file: string, maximum = 268435456) {
  absolute(file); const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const st = fs.fstatSync(fd); if (!st.isFile() || st.size > maximum) throw Error('bounded regular file required');
    const bytes = Buffer.alloc(st.size + 1); let count = 0;
    while (count < bytes.length) {const n = fs.readSync(fd, bytes, count, bytes.length - count, null); if (!n) break; count += n;}
    if (count !== st.size) throw Error('file changed during read'); return bytes.subarray(0, count);
  } finally {fs.closeSync(fd);}
}
function tree(root: string) {
  absolute(root); const result = new Map<string, string>(); let total = 0, entries = 0;
  function walk(dir: string) {
    for (const entry of fs.readdirSync(dir, {withFileTypes: true}).sort((a, b) => a.name < b.name ? -1 : 1)) {
      if (++entries > 16384) throw Error('tree capacity');
      const file = path.join(dir, entry.name); absolute(file);
      if (entry.isSymbolicLink()) throw Error('symbolic tree entry');
      if (entry.isDirectory()) {result.set(file, 'directory'); walk(file);}
      else if (entry.isFile()) {const b = read(file); total += b.length; if (total > 536870912) throw Error('tree byte capacity'); result.set(file, sha256(b));}
      else throw Error('nonregular tree entry');
    }
  }
  walk(root); return Object.fromEntries(result);
}
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) throw Error(reason);};
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}

/** Owns only a retained private experiment. Does not publish a whole-project pass. */
export function executeCrossGeneratorPolicy(plan: ReconciledProjectPlan, controls: CrossGeneratorPolicyControls, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'policy') as PolicyExecution;
}
export function executeCrossGeneratorStateMachine(plan: ReconciledProjectPlan, controls: CrossGeneratorStateMachineControls, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'state-machine') as StateMachineExecution;
}
export function executeCrossGeneratorFactory(plan: ReconciledProjectPlan, controls: CrossGeneratorFactorySurface, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'factory') as FactoryExecution;
}
export function executeCrossGeneratorOwnedValues(plan: ReconciledProjectPlan, controls: CrossGeneratorOwnedValueSurface, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'owned-values') as OwnedValuesExecution;
}
export function executeCrossGeneratorValueProducer(plan: ReconciledProjectPlan, controls: CrossGeneratorValueProducerSurface, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'value-producer') as ValueProducerExecution;
}
export function executeCrossGeneratorOperation(plan: ReconciledProjectPlan, controls: CrossGeneratorOperationControls, definition: string, options: CrossGeneratorExecutionOptions) {
  return execute(plan, controls, definition, options, 'operation') as OperationExecution;
}
type NativeModule = {relative_path: string; callable: string; sha256: string; value_exports?: readonly string[]; type_exports?: readonly string[]; imports: readonly {specifier: string; names: readonly string[]; target_path: string; type_only?: boolean; reexport?: boolean}[]; role?: string};
function execute(plan: ReconciledProjectPlan, controls: CrossGeneratorPolicyControls | CrossGeneratorStateMachineControls | CrossGeneratorFactorySurface | CrossGeneratorOwnedValueSurface | CrossGeneratorValueProducerSurface | CrossGeneratorOperationControls, definition: string, options: CrossGeneratorExecutionOptions, family: 'policy' | 'state-machine' | 'factory' | 'owned-values' | 'value-producer' | 'operation') {
  let phase = 'preflight', workspace: string | undefined;
  try {
    const assertControls = () => family === 'operation' ? assertCrossGeneratorOperationControls(controls) : family === 'policy' ? assertCrossGeneratorPolicyControls(controls) : family === 'state-machine' ? assertCrossGeneratorStateMachineControls(controls) : family === 'factory' ? assertCrossGeneratorFactorySurface(controls) : family === 'owned-values' ? assertCrossGeneratorOwnedValueSurface(controls) : assertCrossGeneratorValueProducerSurface(controls);
    const definitionHash = family === 'operation' ? CROSS_GENERATOR_OPERATION_DEFINITION_SHA256 : family === 'policy' ? CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256 : family === 'state-machine' ? CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256 : family === 'factory' ? CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256 : family === 'owned-values' ? CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256 : CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256;
    assertReconciledProjectPlan(plan); assertControls();
    if (typeof definition !== 'string' || sha256(definition) !== definitionHash) throw Error('definition drift');
    same(plan.plan_sha256, controls.project_plan_sha256, 'foreign plan');
    if (!options || ![Object.prototype, null].includes(Object.getPrototypeOf(options)) || Reflect.ownKeys(options).length !== 2 || ['workspace_parent', 'typescript_root'].some(k => {const d = Object.getOwnPropertyDescriptor(options, k); return !d || !d.enumerable || !Object.hasOwn(d, 'value') || typeof d.value !== 'string';})) throw Error('closed data tool options');
    const selected = {...options}; Object.values(selected).forEach(absolute);
    if (process.version !== 'v26.8.1') throw Error('Node 26.8.1 required');
    const packagePath = path.join(selected.typescript_root, 'package.json'), pkg = JSON.parse(read(packagePath).toString());
    if (pkg.name !== 'typescript' || pkg.version !== '7.0.2') throw Error('TypeScript 7.0.2 required');
    const platformName = '@typescript/typescript-' + process.platform + '-' + process.arch;
    const platformRoot = path.dirname(createRequire(packagePath).resolve(platformName + '/package.json'));
    if (JSON.parse(read(path.join(platformRoot, 'package.json')).toString()).name !== platformName) throw Error('platform package identity');
    const fingerprint = () => ({node: sha256(read(process.execPath)), typescript: tree(selected.typescript_root), platform: tree(platformRoot)});
    const tools = fingerprint(), probe = family === 'operation' ? crossGeneratorOperationProbe(controls as CrossGeneratorOperationControls) : family === 'policy' ? crossGeneratorPolicyProbe(controls as CrossGeneratorPolicyControls) : family === 'state-machine' ? crossGeneratorStateMachineProbe(controls as CrossGeneratorStateMachineControls) : family === 'factory' ? crossGeneratorFactoryProbe((controls as CrossGeneratorFactorySurface).behavior) : family === 'owned-values' ? crossGeneratorOwnedValueProbe((controls as CrossGeneratorOwnedValueSurface).behavior) : crossGeneratorValueProducerProbe((controls as CrossGeneratorValueProducerSurface).behavior);
    if (!probe.rows.length) throw Error('no ready interoperability families');
    const all: NativeModule[] = []; for (const r of controls.rows) if (r.state === 'ready') all.push(...r.modules);
    const modules = [...new Map(all.map(m => [m.relative_path, m])).values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1);
    if (modules.length > 8192) throw Error('module capacity');
    for (const m of all) same(m, modules.find(n => n.relative_path === m.relative_path), 'inconsistent shared module');
    const sources = modules.map(m => {const a = plan.resolved.artifacts.find(a => a.relative_path === m.relative_path); if (!a || sha256(a.content) !== m.sha256) throw Error('source artifact identity'); return {relative_path: m.relative_path, content: a.content};});
    workspace = fs.mkdtempSync(path.join(selected.workspace_parent, 'ds-cross-generator-run-')); absolute(workspace);
    const root = workspace, sourceRoot = path.join(root, 'source'), nativeRoot = path.join(root, 'native');
    fs.mkdirSync(sourceRoot); fs.mkdirSync(nativeRoot);
    const expected = new Map<string, string>([[sourceRoot, 'directory'], [nativeRoot, 'directory']]);
    const add = (relative: string, content: string) => {
      if (relative.includes('\\') || relative.includes('\0') || path.posix.isAbsolute(relative) || relative.split('/').some(p => !p || p === '.' || p === '..')) throw Error('unsafe run path');
      const file = path.join(root, relative); fs.mkdirSync(path.dirname(file), {recursive: true, mode: 0o700});
      let p = path.dirname(file); while (p !== root) {expected.set(p, 'directory'); p = path.dirname(p);}
      fs.writeFileSync(file, content, {flag: 'wx', mode: 0o600}); expected.set(file, sha256(content)); return file;
    };
    const current = () => {same(tree(root), Object.fromEntries(expected), 'run artifact changed or unexpected'); same(fingerprint(), tools, 'toolchain changed'); assertReconciledProjectPlan(plan); assertControls();};
    const run = (args: string[]) => {
      const r = spawnSync(process.execPath, args, {cwd: root, env: {LANG: 'C', TZ: 'UTC'}, encoding: 'utf8', timeout: 60000, maxBuffer: 16777216});
      if (r.error || r.status !== 0) throw Error((r.error?.message || r.stderr || r.stdout || 'exit ' + r.status).slice(0, 4096)); return r.stdout;
    };
    phase = 'source-materialization';
    sources.forEach(s => add('source/' + s.relative_path, s.content)); add('package.json', '{"type":"commonjs"}\n');
    const compilerOptions = {strict: true, skipLibCheck: true, types: [], target: 'ES2022', module: 'CommonJS', rootDir: sourceRoot, outDir: nativeRoot};
    const config = add('compiler.json', canonicalJson({compilerOptions, files: sources.map(s => path.join(sourceRoot, s.relative_path))}));
    const auditScript = add('audit.mjs', family === 'operation' ? CROSS_GENERATOR_OPERATION_AUDIT_RUNNER : family === 'policy' ? CROSS_GENERATOR_AUDIT_RUNNER : family === 'state-machine' ? CROSS_GENERATOR_STATE_MACHINE_AUDIT_RUNNER : family === 'factory' ? CROSS_GENERATOR_FACTORY_AUDIT_RUNNER : family === 'owned-values' ? CROSS_GENERATOR_OWNED_VALUES_AUDIT_RUNNER : CROSS_GENERATOR_VALUE_PRODUCER_AUDIT_RUNNER), runner = add('runner.mjs', family === 'operation' ? CROSS_GENERATOR_OPERATION_RUNNER : family === 'policy' ? CROSS_GENERATOR_POLICY_RUNNER : family === 'state-machine' ? CROSS_GENERATOR_STATE_MACHINE_RUNNER : family === 'factory' ? CROSS_GENERATOR_FACTORY_RUNNER : family === 'owned-values' ? CROSS_GENERATOR_OWNED_VALUES_RUNNER : CROSS_GENERATOR_VALUE_PRODUCER_RUNNER);
    const auditHashes: Record<string, string> = {};
    const audit = (stage: 'source' | 'native') => {
      phase = stage + '-module-audit'; const moduleRoot = stage === 'source' ? sourceRoot : nativeRoot;
      const paths = modules.map(m => stage === 'source' ? m.relative_path : m.relative_path.replace(/\.ts$/, '.js'));
      const auditConfig = add(stage + '-audit-config.json', canonicalJson({compilerOptions: {...compilerOptions, rootDir: moduleRoot, allowJs: true, checkJs: false, noEmit: true}, files: paths.map(p => path.join(moduleRoot, p))}));
      const input = add(stage + '-audit-input.json', canonicalJson({definition, phase: stage, module_root: moduleRoot, module_paths: paths, modules, ...(family === 'operation' ? {support_modules: modules.filter(m => m.role === 'enum-runtime').map(m => ({relative_path: m.relative_path, source_sha256: m.sha256}))} : {})}));
      current(); const text = run([auditScript, selected.typescript_root, auditConfig, input]); current();
      const wanted = {schema_version: 'domainspec.cross-generator-module-observation/v1-candidate', phase: stage, definition_sha256: definitionHash,
        modules: modules.map((m, i) => ({relative_path: paths[i], source_sha256: expected.get(path.join(moduleRoot, paths[i]!)), imports: m.imports.filter(i => stage === 'source' || !i.type_only).map(i => ({specifier: i.specifier, names: i.names, ...(stage === 'source' && i.type_only ? {type_only: true} : {}), ...(family === 'operation' && stage === 'source' && i.reexport ? {reexport: true} : {})})).sort((a, b) => a.specifier < b.specifier ? -1 : a.specifier > b.specifier ? 1 : 0), exports: [...(m.value_exports ?? [m.callable]), ...(stage === 'source' ? m.type_exports ?? [] : [])].sort(), violations: []}))};
      const observed = JSON.parse(text);
      same(observed, wanted, 'independent module audit mismatch:' + canonicalJson(observed.modules?.filter((m: any) => m.violations?.length).slice(0, 3)).slice(0, 4096));
      add(stage + '-audit-observation.json', text); auditHashes[stage] = sha256(text);
    };
    audit('source'); phase = 'strict-native-compilation'; current(); run([path.join(selected.typescript_root, 'bin/tsc'), '--project', config, '--pretty', 'false']);
    let nativeBytes = 0;
    const nativeModules = modules.map(m => {
      const relative_path = m.relative_path.replace(/\.ts$/, '.js'), file = path.join(nativeRoot, relative_path), bytes = read(file); nativeBytes += bytes.length;
      if (nativeBytes > 67108864) throw Error('native byte capacity');
      let p = path.dirname(file); while (p !== root) {expected.set(p, 'directory'); p = path.dirname(p);}
      const hash = sha256(bytes); expected.set(file, hash); return {relative_path, sha256: hash};
    });
    current(); audit('native');
    phase = 'native-behavior'; const inputText = canonicalJson(probe);
    if (Buffer.byteLength(inputText) > 16777216) throw Error('whole input capacity');
    const input = add('cases.json', inputText); current();
    const output = run(['--permission', '--allow-fs-read=' + root, '--disable-proto=throw', '--max-old-space-size=256', runner, input, nativeRoot]); current();
    const outcome = family === 'operation' ? checkCrossGeneratorOperationObservations(controls as CrossGeneratorOperationControls, JSON.parse(output)) : family === 'policy' ? checkCrossGeneratorPolicyObservations(controls as CrossGeneratorPolicyControls, JSON.parse(output)) : family === 'state-machine' ? checkCrossGeneratorStateMachineObservations(controls as CrossGeneratorStateMachineControls, JSON.parse(output)) : family === 'factory' ? checkCrossGeneratorFactoryObservations((controls as CrossGeneratorFactorySurface).behavior, JSON.parse(output)) : family === 'owned-values' ? checkCrossGeneratorOwnedValueObservations((controls as CrossGeneratorOwnedValueSurface).behavior, JSON.parse(output)) : checkCrossGeneratorValueProducerObservations((controls as CrossGeneratorValueProducerSurface).behavior, JSON.parse(output)); add('observations.json', output);
    phase = 'final-currentness'; current();
    const result = freeze({schema_version: 'domainspec.cross-generator-execution/v1-candidate' as const, result: 'pass' as const, definition_sha256: definitionHash,
      project_plan_sha256: plan.plan_sha256, controls_sha256: controls.controls_sha256, workspace: root, outcome, native_modules: nativeModules, audits: auditHashes,
      observation_sha256: sha256(output), files: Object.fromEntries(expected), tool_files: tools, authority_effect: 'none' as const,
      ...(['factory', 'owned-values', 'value-producer', 'operation'].includes(family) ? {surface_sha256: (controls as CrossGeneratorFactorySurface | CrossGeneratorOwnedValueSurface | CrossGeneratorValueProducerSurface | CrossGeneratorOperationControls).surface_sha256} : {}),
      ...(family === 'operation' ? {protocol_sha256: (controls as CrossGeneratorOperationControls).protocol_sha256} : {}),
      claim_scope: family === 'operation' ? 'finite-private-instrumented-operation-providers-not-whole-project' as const : family === 'policy' ? 'finite-private-instrumented-rule-policy-not-whole-project' as const : family === 'state-machine' ? 'finite-private-instrumented-rule-state-machine-not-whole-project' as const : family === 'factory' ? 'finite-private-instrumented-factory-rule-not-whole-project' as const : family === 'owned-values' ? 'finite-private-instrumented-factory-owned-values-not-whole-project' as const : 'finite-private-instrumented-value-producer-not-whole-project' as const});
    receipts.set(result, current); return result;
  } catch (e) {throw new CrossGeneratorExecutionError(phase, e instanceof Error ? e.message : String(e), workspace);}
}
type CommonExecution = ReturnType<typeof execute>;
type PolicyExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorPolicyObservations>; claim_scope: 'finite-private-instrumented-rule-policy-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256};
type StateMachineExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorStateMachineObservations>; claim_scope: 'finite-private-instrumented-rule-state-machine-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256};
type FactoryExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256' | 'surface_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorFactoryObservations>; claim_scope: 'finite-private-instrumented-factory-rule-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256; surface_sha256: string};
type OwnedValuesExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256' | 'surface_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorOwnedValueObservations>; claim_scope: 'finite-private-instrumented-factory-owned-values-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256; surface_sha256: string};
type ValueProducerExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256' | 'surface_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorValueProducerObservations>; claim_scope: 'finite-private-instrumented-value-producer-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256; surface_sha256: string};
type OperationExecution = Omit<CommonExecution, 'outcome' | 'claim_scope' | 'definition_sha256' | 'surface_sha256' | 'protocol_sha256'> & {outcome: ReturnType<typeof checkCrossGeneratorOperationObservations>; claim_scope: 'finite-private-instrumented-operation-providers-not-whole-project'; definition_sha256: typeof CROSS_GENERATOR_OPERATION_DEFINITION_SHA256; surface_sha256: string; protocol_sha256: string};
export type CrossGeneratorExecution = PolicyExecution | StateMachineExecution | FactoryExecution | OwnedValuesExecution | ValueProducerExecution | OperationExecution;
export function assertCrossGeneratorExecutionCurrent(value: unknown): asserts value is CrossGeneratorExecution {
  if (!value || typeof value !== 'object' || !receipts.has(value)) throw new CrossGeneratorExecutionError('receipt', 'registered execution required');
  try {receipts.get(value)!();} catch (e) {throw new CrossGeneratorExecutionError('currentness', e instanceof Error ? e.message : String(e));}
}
