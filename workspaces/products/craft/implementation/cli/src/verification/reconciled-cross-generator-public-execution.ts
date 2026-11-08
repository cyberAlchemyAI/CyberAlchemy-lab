import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {loadCompiledProjectGraph, type CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {crossGeneratorPreparationBindings, CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256, type CrossGeneratorPreparation, type CrossGeneratorFamily} from './reconciled-cross-generator-public.js';
import {getCrossGeneratorSource as source, CROSS_GENERATOR_SOURCE_CAPSULE_SHA256} from './cross-generator-sources.js';
import {
  executeCrossGeneratorPolicy, executeCrossGeneratorStateMachine, executeCrossGeneratorFactory,
  executeCrossGeneratorOwnedValues, executeCrossGeneratorValueProducer, executeCrossGeneratorOperation,
  assertCrossGeneratorExecutionCurrent, CrossGeneratorExecutionError, type CrossGeneratorExecution
} from './reconciled-cross-generator-execution.js';
import {executeCrossGeneratorWorkflow, assertCrossGeneratorWorkflowExecutionCurrent, WorkflowRetainedExecutionError, type CrossGeneratorWorkflowExecution} from './reconciled-cross-generator-workflow-execution.js';

export interface CrossGeneratorAggregateOptions {workspace_parent: string; typescript_root: string; node_types_root: string;}
export class CrossGeneratorAggregateError extends Error {
  constructor(readonly phase: string, reason: string, readonly workspace?: string) {
    super('CROSS_GENERATOR_AGGREGATE:' + phase + ':' + reason); this.name = 'CrossGeneratorAggregateError';
  }
}
type Receipt = CrossGeneratorExecution | CrossGeneratorWorkflowExecution;
type Issue = {scope: string; reason: string};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) throw Error(reason);};
const reason = (e: unknown) => (e instanceof Error ? e.message : String(e)).slice(0, 4096);
function freeze<T>(v: T): T {
  if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);}
  return v;
}
function absolute(p: string) {
  if (typeof p !== 'string' || !path.isAbsolute(p) || path.resolve(p) !== p || fs.realpathSync(p) !== p) throw Error('normalized nonsymbolic absolute path required');
  return p;
}
function read(file: string) {
  absolute(file);
  const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const st = fs.fstatSync(fd); if (!st.isFile() || st.size > 268435456) throw Error('bounded regular file required');
    const bytes = Buffer.alloc(st.size + 1); let count = 0;
    while (count < bytes.length) {const n = fs.readSync(fd, bytes, count, bytes.length - count, null); if (!n) break; count += n;}
    if (count !== st.size) throw Error('file changed during read');
    return bytes.subarray(0, count);
  } finally {fs.closeSync(fd);}
}
function tree(root: string) {
  absolute(root); const files: Record<string, string> = {}; let entries = 0, bytes = 0;
  const walk = (dir: string) => {
    for (const e of fs.readdirSync(dir, {withFileTypes: true}).sort((a, b) => a.name < b.name ? -1 : 1)) {
      if (++entries > 16384) throw Error('tool tree capacity');
      const file = absolute(path.join(dir, e.name));
      if (e.isDirectory()) {files[file] = 'directory'; walk(file);}
      else if (e.isFile()) {const content = read(file); bytes += content.length; if (bytes > 536870912) throw Error('tool tree byte capacity'); files[file] = sha256(content);}
      else throw Error('nonregular tool tree entry');
    }
  };
  walk(root); return files;
}
// Re-resolve every search location. Cached Node package resolution is not
// evidence that a newly shadowed dependency still selects the original bytes.
function packageLocation(origin: string, name: string) {
  let dir = origin;
  for (let depth = 0; depth < 64; depth++) {
    if (path.basename(dir) !== 'node_modules') {
      const candidate = path.join(dir, 'node_modules', name, 'package.json');
      let present = false;
      try {fs.lstatSync(candidate); present = true;} catch (e) {if ((e as NodeJS.ErrnoException).code !== 'ENOENT') throw e;}
      if (present) {const file = fs.realpathSync(candidate); read(file); return {selection_path: candidate, root: absolute(path.dirname(file))};}
    }
    const parent = path.dirname(dir); if (parent === dir) break; dir = parent;
  }
  throw Error('missing package dependency:' + name);
}
function captureTools(selected: CrossGeneratorAggregateOptions) {
  if (process.version !== 'v26.8.1') throw Error('Node 26.8.1 required');
  const tsPackage = path.join(selected.typescript_root, 'package.json'), ts = JSON.parse(read(tsPackage).toString());
  if (ts.name !== 'typescript' || ts.version !== '7.0.2') throw Error('TypeScript 7.0.2 required');
  const platformName = '@typescript/typescript-' + process.platform + '-' + process.arch;
  const platform = () => packageLocation(selected.typescript_root, platformName), platformRoot = platform().root;
  const pkg = JSON.parse(read(path.join(platformRoot, 'package.json')).toString());
  if (pkg.name !== platformName || pkg.version !== '7.0.2') throw Error('platform package identity');
  same(platformRoot, path.dirname(createRequire(tsPackage).resolve(platformName + '/package.json')), 'platform resolution mismatch');
  const nodePackage = path.join(selected.node_types_root, 'package.json'), node = JSON.parse(read(nodePackage).toString());
  if (node.name !== '@types/node' || node.version !== '26.4.0') throw Error('Node declarations 26.4.0 required');
  same(node.dependencies, {'undici-types': '~8.3.0'}, 'Node declaration dependency contract');
  const undici = () => packageLocation(selected.node_types_root, 'undici-types'), undiciRoot = undici().root;
  const undiciPkg = JSON.parse(read(path.join(undiciRoot, 'package.json')).toString());
  if (undiciPkg.name !== 'undici-types' || undiciPkg.version !== '8.3.0' || Object.keys(undiciPkg.dependencies ?? {}).length) throw Error('Undici declaration dependency contract');
  same(undiciRoot, path.dirname(createRequire(nodePackage).resolve('undici-types/package.json')), 'declaration resolution mismatch');
  const fingerprint = () => ({
    node: sha256(read(process.execPath)), typescript: tree(selected.typescript_root), platform_resolution: platform(), platform: tree(platformRoot),
    node_types: tree(selected.node_types_root), undici_resolution: undici(), undici: tree(undiciRoot)
  });
  const initial = fingerprint();
  return {initial, current: () => same(fingerprint(), initial, 'toolchain or dependency selection changed')};
}
function receiptCurrent(receipt: Receipt) {
  if (receipt.schema_version === 'domainspec.cross-generator-workflow-execution/v1-candidate') assertCrossGeneratorWorkflowExecutionCurrent(receipt);
  else assertCrossGeneratorExecutionCurrent(receipt);
}
type AggregateBinding = {
  inspect: () => Issue[];
  preparation: CrossGeneratorPreparation;
  graph: CompiledProjectGraph;
  plan: ReconciledProjectPlan;
  workflow: CrossGeneratorWorkflowExecution | null;
};
const registered = new WeakMap<object, AggregateBinding>();
const ready = <T>(binding: {state: 'prepared'; value: T} | {state: 'fail'; reason: string}): T => {
  if (binding.state !== 'prepared') throw Error(binding.reason); return binding.value;
};

/** Actual finite native evidence. Public compilation and artifact checks remain a separate join. */
export function executePreparedCrossGeneratorVerification(preparation: CrossGeneratorPreparation, graph: CompiledProjectGraph, plan: ReconciledProjectPlan, options: CrossGeneratorAggregateOptions) {
  let workspace: string | undefined, phase = 'preflight';
  try {
    const state = crossGeneratorPreparationBindings(preparation, graph, plan);
    if (!options || ![Object.prototype, null].includes(Object.getPrototypeOf(options)) || Reflect.ownKeys(options).length !== 3 ||
      ['workspace_parent', 'typescript_root', 'node_types_root'].some(k => {const d = Object.getOwnPropertyDescriptor(options, k); return !d?.enumerable || !Object.hasOwn(d, 'value') || typeof d.value !== 'string';})) throw Error('closed data tool options');
    const selected = {...options};
    for (const value of Object.values(selected)) if (!fs.lstatSync(absolute(value)).isDirectory()) throw Error('directory option required');
    const within = (p: string, root: string) => p === root || p.startsWith(root + path.sep);
    if ([graph.project_root, selected.typescript_root, selected.node_types_root].some(root => within(selected.workspace_parent, root))) throw Error('workspace parent cannot be inside source or tool root');
    const sourceCurrent = () => {
      crossGeneratorPreparationBindings(preparation, graph, plan);
      if (sha256(source('public')) !== CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256) throw Error('public definition drift');
      same(loadCompiledProjectGraph(graph.project_root).source_manifest, graph.source_manifest, 'original source changed');
    };
    sourceCurrent();
    const hasReady = preparation.rows.some(r => r.state === 'ready');
    const tools = hasReady ? captureTools(selected) : null;
    const receipts = new Map<CrossGeneratorFamily, Receipt>(), failures = new Map<CrossGeneratorFamily, string>();
    const executed = new Set<CrossGeneratorFamily>(), stopped = new Set<CrossGeneratorFamily>(), issues: Issue[] = [];
    const directories = new Map<string, {dev: number; ino: number}>(), files = new Map<string, string>();
    let owned: fs.Stats | undefined;
    if (hasReady) {
      workspace = fs.mkdtempSync(path.join(selected.workspace_parent, 'ds-cross-generator-aggregate-'));
      owned = fs.lstatSync(absolute(workspace));
    }
    const add = (name: string, content: string) => {
      if (!workspace) throw Error('owned workspace required');
      const file = path.join(workspace, name); fs.writeFileSync(file, content, {flag: 'wx', mode: 0o600}); files.set(file, content);
    };
    if (workspace) add('preparation.json', canonicalJson({
      schema_version: 'domainspec.cross-generator-aggregate-input/v1-candidate',
      preparation_sha256: preparation.preparation_sha256, definition_sha256: CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256,
      contract_capsule_sha256: CROSS_GENERATOR_SOURCE_CAPSULE_SHA256, project_plan_sha256: plan.plan_sha256,
      source_manifest_sha256: preparation.source_manifest_sha256, families: preparation.families,
      tool_files_sha256: sha256(canonicalJson(tools!.initial)), authority_effect: 'none'
    }));
    const rootCurrent = () => {
      if (!workspace) return;
      const st = fs.lstatSync(absolute(workspace));
      if (!st.isDirectory() || st.dev !== owned!.dev || st.ino !== owned!.ino) throw Error('aggregate workspace identity changed');
      same(fs.readdirSync(workspace).sort(), [...files.keys(), ...directories.keys()].map(p => path.basename(p)).sort(), 'aggregate workspace entry set changed');
      for (const [file, content] of files) if (read(file).toString('utf8') !== content) throw Error('aggregate manifest changed');
      for (const [dir, identity] of directories) {
        const st = fs.lstatSync(absolute(dir));
        if (!st.isDirectory() || st.dev !== identity.dev || st.ino !== identity.ino) throw Error('retained family directory identity changed');
      }
    };
    const remember = (dir: string) => {
      if (!workspace || path.dirname(dir) !== workspace || directories.has(dir)) throw Error('family workspace ownership');
      const st = fs.lstatSync(absolute(dir)); if (!st.isDirectory()) throw Error('family workspace directory');
      directories.set(dir, {dev: st.dev, ino: st.ino});
    };
    const inspect = (): Issue[] => {
      const result: Issue[] = [];
      const check = (scope: string, action: () => void) => {try {action();} catch (e) {result.push({scope, reason: reason(e)});}};
      check('source', sourceCurrent); check('workspace', rootCurrent);
      if (tools) check('tools', tools.current);
      for (const [family, receipt] of receipts) check(family, () => receiptCurrent(receipt));
      return result;
    };
    const retain = (family: CrossGeneratorFamily, receipt: Receipt) => {
      if (receipt.project_plan_sha256 !== plan.plan_sha256 || receipt.controls_sha256 !== preparation.families.find(f => f.family === family)!.controls_sha256) throw Error('retained family input mismatch');
      const expected = receipt.schema_version === 'domainspec.cross-generator-workflow-execution/v1-candidate' ? tools!.initial :
        {node: tools!.initial.node, typescript: tools!.initial.typescript, platform: tools!.initial.platform};
      same(receipt.tool_files, expected, 'retained family tool epoch mismatch');
      receiptCurrent(receipt); remember(receipt.workspace); receipts.set(family, receipt);
    };
    const common = () => ({workspace_parent: workspace!, typescript_root: selected.typescript_root});
    const run: Record<CrossGeneratorFamily, () => Receipt> = {
      policy: () => executeCrossGeneratorPolicy(plan, ready(state.bindings.policy).controls, source('execution'), common()),
      'state-machine': () => executeCrossGeneratorStateMachine(plan, ready(state.bindings['state-machine']).controls, source('state_machine'), common()),
      'factory-rule': () => executeCrossGeneratorFactory(plan, ready(state.bindings['factory-rule']).surface, source('factory_execution'), common()),
      'owned-values': () => executeCrossGeneratorOwnedValues(plan, ready(state.bindings['owned-values']).surface, source('owned_values_execution'), common()),
      'value-producer': () => executeCrossGeneratorValueProducer(plan, ready(state.bindings['value-producer']).surface, source('value_producer'), common()),
      operation: () => executeCrossGeneratorOperation(plan, ready(state.bindings.operation).controls, source('operation'), common()),
      workflow: () => {
        const b = ready(state.bindings.workflow);
        return executeCrossGeneratorWorkflow(plan, b.controls, b.audit, source('workflow_execution'), source('workflow'), {...common(), node_types_root: selected.node_types_root});
      }
    };
    phase = 'family-execution';
    for (const family of preparation.families) {
      if (family.state === 'fail') {failures.set(family.family, family.reason!); continue;}
      if (!preparation.rows.some(r => r.family === family.family && r.state === 'ready')) continue;
      if (issues.length) {stopped.add(family.family); continue;}
      const before = inspect(); if (before.length) {issues.push(...before); stopped.add(family.family); continue;}
      executed.add(family.family);
      let receipt: Receipt | undefined;
      try {receipt = run[family.family](); retain(family.family, receipt);}
      catch (error) {
        failures.set(family.family, reason(error));
        const dir = receipt?.workspace ?? (error instanceof CrossGeneratorExecutionError || error instanceof WorkflowRetainedExecutionError ? error.workspace : undefined);
        if (dir && !directories.has(dir)) {try {remember(dir);} catch (e) {issues.push({scope: 'workspace', reason: reason(e)});}}
      }
      issues.push(...inspect());
    }
    phase = 'final-currentness';
    issues.push(...inspect());
    const uniqueIssues = [...new Map(issues.map(i => [canonicalJson(i), i])).values()];
    const projectOutcomes = () => {
      const rows = preparation.rows.map(row => {
        const observed = receipts.has(row.family), failed = failures.get(row.family);
        const stale = uniqueIssues.some(i => ['source', 'workspace', 'tools', row.family].includes(i.scope));
        const result = row.state === 'inapplicable' ? 'inapplicable' as const : row.state === 'fail' ? 'fail' as const : row.state === 'not_evaluable' ? 'not_evaluable' as const : failed ? 'fail' as const :
          !observed || stale ? 'not_evaluable' as const : 'pass' as const;
        return {...row, result, executed: row.state === 'ready' && executed.has(row.family),
          reason: row.state !== 'ready' ? row.reason : failed ?? (stale ? 'retained evidence is stale; see currentness issues' : stopped.has(row.family) ? 'execution stopped after a currentness failure' : row.reason)};
      });
      const rowByKey = new Map(rows.map(r => [r.family + ':' + r.selector, r]));
      const edges = preparation.edges.map(edge => {
        const observations = edge.witnesses.map(w => ({...w, result: rowByKey.get(w.family + ':' + w.selector)!.result}));
        const result = edge.category !== 'generated-runtime' ? 'separate-native-obligation' as const : observations.some(w => w.result === 'pass') ? 'pass' as const :
          observations.some(w => w.result === 'fail') ? 'fail' as const : 'not_evaluable' as const;
        return {...edge, observations, execution_status: result};
      });
      const families = preparation.families.map(family => {
        const selectedRows = rows.filter(r => r.family === family.family);
        const result = failures.has(family.family) || selectedRows.some(r => r.result === 'fail') ? 'fail' as const :
          selectedRows.some(r => r.result === 'not_evaluable') ? 'incomplete' as const : selectedRows.some(r => r.result === 'pass') ? 'pass' as const : 'inapplicable' as const;
        return {...family, result, executed: executed.has(family.family), reason: failures.get(family.family) ?? family.reason};
      });
      const applicable = rows.some(r => r.state !== 'inapplicable') || edges.some(e => e.behavior_required);
      const result = uniqueIssues.length || families.some(f => f.result === 'fail') ? 'fail' as const :
        families.some(f => f.result === 'incomplete') || edges.some(e => e.behavior_required && e.execution_status !== 'pass') ? 'incomplete' as const :
        applicable ? 'pass' as const : 'inapplicable' as const;
      return {rows, edges, families, result};
    };
    const retained = [...receipts].map(([family, receipt]) => ({
      family, workspace: receipt.workspace, definition_sha256: receipt.definition_sha256, controls_sha256: receipt.controls_sha256,
      observation_sha256: receipt.observation_sha256, file_count: Object.keys(receipt.files).length, files_sha256: sha256(canonicalJson(receipt.files)),
      native_module_count: receipt.native_modules.length, audits: receipt.audits, outcome: receipt.outcome, tool_files_sha256: sha256(canonicalJson(receipt.tool_files))
    }));
    if (workspace) add('outcomes.json', canonicalJson({preparation_sha256: preparation.preparation_sha256, ...projectOutcomes(), retained, currentness_issues: uniqueIssues}));
    // The final manifest itself participates in subsequent custody checks.
    const finalIssues = inspect();
    for (const i of finalIssues) if (!uniqueIssues.some(v => canonicalJson(v) === canonicalJson(i))) uniqueIssues.push(i);
    const {rows, edges, families, result} = projectOutcomes();
    const body = {
      schema_version: 'domainspec.cross-generator-aggregate-execution/v1-candidate' as const, definition_sha256: CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256,
      preparation_sha256: preparation.preparation_sha256, contract_capsule_sha256: CROSS_GENERATOR_SOURCE_CAPSULE_SHA256,
      project_plan_sha256: plan.plan_sha256, source_manifest_sha256: preparation.source_manifest_sha256, boundary_sha256: preparation.boundary_sha256,
      requests: preparation.requests, modules: preparation.modules, roots: preparation.roots, edges, rows, families, retained,
      result: uniqueIssues.length ? 'fail' as const : result, executed_family_count: executed.size, retained_family_count: retained.length,
      currentness_issues: uniqueIssues, workspace: workspace ?? null,
      aggregate_files: Object.fromEntries([...files].map(([p, content]) => [p, sha256(content)])),
      tool_files_sha256: tools ? sha256(canonicalJson(tools.initial)) : null,
      public_cross_generator_behavior: 'not_evaluable' as const, claim_scope: 'finite-retained-cross-generator-protocols-not-public-verification' as const,
      authority_effect: 'none' as const
    };
    const report = freeze({...body, report_sha256: sha256(canonicalJson(body))});
    const workflow = receipts.get('workflow');
    if (workflow && workflow.schema_version !== 'domainspec.cross-generator-workflow-execution/v1-candidate') throw Error('Workflow receipt kind');
    registered.set(report, {inspect, preparation, graph, plan, workflow: workflow ?? null});
    return report;
  } catch (error) {throw new CrossGeneratorAggregateError(phase, reason(error), workspace);}
}
export type CrossGeneratorAggregateExecution = ReturnType<typeof executePreparedCrossGeneratorVerification>;
/** Recheck before public aggregation and cleanup; this is not a post-cleanup live receipt. */
export function assertCrossGeneratorAggregateCurrent(value: unknown): asserts value is CrossGeneratorAggregateExecution {
  const binding = value && typeof value === 'object' ? registered.get(value) : undefined;
  if (!binding) throw new CrossGeneratorAggregateError('receipt', 'registered aggregate required');
  const issues = binding.inspect();
  if (issues.length) throw new CrossGeneratorAggregateError('currentness', canonicalJson(issues));
}

/** Internal custody bridge. Access is not public obligation fulfillment. */
export function retainedWorkflowExecutionBindings(value: unknown, preparation: CrossGeneratorPreparation, graph: CompiledProjectGraph, plan: ReconciledProjectPlan) {
  const binding = value && typeof value === 'object' ? registered.get(value) : undefined;
  if (!binding) throw new CrossGeneratorAggregateError('receipt', 'registered aggregate required');
  if (binding.preparation !== preparation || binding.graph !== graph || binding.plan !== plan) throw new CrossGeneratorAggregateError('receipt', 'foreign aggregate input');
  const state = crossGeneratorPreparationBindings(preparation, graph, plan);
  // Includes source, tools, original private receipts and aggregate ownership.
  // A different family's behavioral failure does not erase a Workflow receipt.
  assertCrossGeneratorAggregateCurrent(value);
  return freeze({binding: state.bindings.workflow, receipt: binding.workflow, rows: value.rows.filter(row => row.family === 'workflow')});
}
