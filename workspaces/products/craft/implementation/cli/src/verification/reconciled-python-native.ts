import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph, type CompiledProjectGraph} from '../input/project-model.js';
import {planCompiledReconciledPythonProject, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {createReconciledPythonVerificationProjection} from './reconciled-python-projection.js';
import {verifyReconciledProject} from '../generation/reconciled-output.js';
import {assertReconciledOutputLayout} from '../generation/reconciled-output-layout.js';
import type {OutputLayout} from '../generation/output-layout.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {freezePythonProject as freeze} from '../generation/reconciled-python-selection.js';
import {createPythonSemanticControls, PYTHON_SEMANTIC_VERIFICATION_SHA256, PYTHON_DATA_SEMANTIC_SHA256, PYTHON_DECISION_SEMANTIC_SHA256, PYTHON_ENUM_SEMANTIC_SHA256} from './reconciled-python-semantic-controls.js';
import {createReconciledFormalization} from '../formalization/reconciled.js';
import {SUBPROCESS_TIMEOUT_MS} from '../input/limits.js';

export const PYTHON_NATIVE_VERIFICATION_SHA256 = '90cfd1ecc4affc2599f6b7b61f9e425210fe6b87558a2d55934712ba4a9ad21a';
export const PYTHON_COMPLETE_VERIFICATION_SHA256 = '18bb7fc6d90db1bc4470fb4b46ee698d26210a0ea93198f7e33e61ba5dccd8d2';
const OBSERVER_SHA256 = '0ed0b5753472e5625daaef0b40d8049bd52761415241234f54464ffa0c981e43';
const fail = (message: string): never => {throw new TypeError('DS_PYTHON_NATIVE_VERIFICATION:' + message);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
export interface PythonNativeVerificationOptions {
  readonly python_executable: string;
  readonly temporary_parent: string;
  readonly target_root?: string;
  readonly output_layout?: OutputLayout;
}
export interface PythonVerificationOptions extends PythonNativeVerificationOptions {
  readonly target_root: string;
  readonly lean_executable: string;
}
function validateOptions(value: unknown, complete: boolean): PythonNativeVerificationOptions | PythonVerificationOptions {
  assertInterfaceData(value);
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('closed options required');
  const row = value as Record<string, unknown>;
  const allowed = ['python_executable', 'temporary_parent', 'target_root', 'output_layout', ...(complete ? ['lean_executable'] : [])];
  if (!Object.hasOwn(row, 'python_executable') || !Object.hasOwn(row, 'temporary_parent') || complete && (!Object.hasOwn(row, 'target_root') || !Object.hasOwn(row, 'lean_executable')) || Object.keys(row).some(k => !allowed.includes(k))) fail('closed options required');
  for (const [k, v] of Object.entries(row)) if (k !== 'output_layout' && (typeof v !== 'string' || !path.isAbsolute(v) || path.resolve(v) !== v)) fail('normalized absolute paths required');
  assertReconciledOutputLayout(row.output_layout);
  if (row.output_layout !== undefined && row.target_root === undefined) fail('output layout requires target');
  return freeze({...row}) as unknown as PythonNativeVerificationOptions | PythonVerificationOptions;
}
export function validatePythonNativeVerificationOptions(value: unknown): PythonNativeVerificationOptions {
  return validateOptions(value, false) as PythonNativeVerificationOptions;
}
export function validatePythonVerificationOptions(value: unknown): PythonVerificationOptions {
  return validateOptions(value, true) as PythonVerificationOptions;
}
function readRegular(file: string, limit: number): Buffer {
  if (fs.realpathSync(file) !== file) fail('symbolic file path');
  const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const st = fs.fstatSync(fd); if (!st.isFile() || st.size > limit) fail('bounded regular file required');
    const data = Buffer.alloc(st.size + 1); let offset = 0;
    while (offset < data.length) {const n = fs.readSync(fd, data, offset, data.length - offset, null); if (!n) break; offset += n;}
    if (offset !== st.size) fail('file changed during read'); return data.subarray(0, offset);
  } finally {fs.closeSync(fd);}
}
type Check = {id: string; required: true; executed: boolean; result: 'pass' | 'fail' | 'not_evaluable'; reason: string; blocked_by: string[]; evidence: Record<string, unknown>};
const registered = new WeakSet<object>();

/** Native stage only; pending semantic/formal obligations prevent a full pass. */
export function executeReconciledPythonNativeVerification(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan, value: PythonNativeVerificationOptions) {
  return executePythonVerification(graph, plan, value, 'native');
}
/** Explicit additive semantic stage; unsupported nodes/formal checks stay pending. */
export function executeReconciledPythonSemanticVerification(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan, value: PythonNativeVerificationOptions) {
  return executePythonVerification(graph, plan, value, 'semantic');
}
/** Complete selected-language verification. A full pass requires exact output,
 * all Python semantic rows, source/selection round-trip and Lean execution. */
export function executeReconciledPythonVerification(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan, value: PythonVerificationOptions) {
  return executePythonVerification(graph, plan, value, 'complete');
}
function executePythonVerification(graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan, value: PythonNativeVerificationOptions | PythonVerificationOptions, mode: 'native' | 'semantic' | 'complete') {
  const complete = mode === 'complete', semantics = mode !== 'native';
  const options = (complete ? validatePythonVerificationOptions(value) : validatePythonNativeVerificationOptions(value)), input = createReconciledPythonVerificationProjection(graph, plan);
  const controls = semantics ? createPythonSemanticControls(graph, plan) : null;
  const semanticRows: {selector: string; kind: string; result: 'pass' | 'not_evaluable'; executed: boolean; case_count?: number; native_form?: string; binding_controls?: number; compiling_substitutions?: number; blocked_by?: string[]}[] = controls?.rows.map(r => ({selector: r.selector, kind: r.kind, result: 'not_evaluable', executed: false})) ?? [];
  if (sha256(getReconciledSource('python_native')) !== PYTHON_NATIVE_VERIFICATION_SHA256) fail('definition drift');
  if (complete && sha256(getReconciledSource('python_complete_verification')) !== PYTHON_COMPLETE_VERIFICATION_SHA256) fail('complete definition drift');
  const observer = getReconciledSource('python_native_observer'); if (sha256(observer) !== OBSERVER_SHA256) fail('observer drift');
  const checks = new Map<string, Check>(input.evidence_requirements.map(r => [r.id, {id: r.id, required: true, executed: false, result: 'not_evaluable', reason: 'required executor not yet run', blocked_by: [], evidence: {}}]));
  const put = (id: string, result: Check['result'], reason: string, evidence: Record<string, unknown> = {}, executed = true, blocked_by: string[] = []) => checks.set(id, {id, required: true, result, reason, evidence, executed, blocked_by});
  const attempt = (id: string, action: () => Record<string, unknown>, dependencies: string[] = []) => {
    if (checks.get(id)?.result === 'fail') return false;
    const blocked = dependencies.filter(id => checks.get(id)?.result !== 'pass');
    if (blocked.length) {put(id, 'not_evaluable', 'prerequisite failed', {}, false, blocked); return false;}
    try {put(id, 'pass', 'observed check passed', action()); return true;} catch (e) {put(id, 'fail', String(e).slice(0, 4096)); return false;}
  };
  let workspace: string | null = null, inode: fs.Stats | null = null, executable = '', executableSha = '', leanExecutable = '', leanExecutableSha = '';
  const expected = new Map<string, string>();
  const sourceCurrent = () => {same(loadCompiledProjectGraph(graph.project_root).source_manifest, graph.source_manifest, 'source changed'); return {manifest_sha256: graph.source_manifest.manifest_sha256};};
  const write = (relative: string, content: Buffer | string) => {
    if (path.posix.normalize(relative) !== relative || relative.startsWith('/') || relative.includes('\\') || relative.split('/').some(p => !p || p === '.' || p === '..')) fail('unsafe run path');
    const file = path.join(workspace!, relative); fs.mkdirSync(path.dirname(file), {recursive: true, mode: 0o700}); fs.writeFileSync(file, content, {flag: 'wx', mode: 0o600}); expected.set(relative, sha256(content));
  };
  const workspaceCurrent = () => {
    if (!workspace || !inode) fail('no run workspace');
    const st = fs.lstatSync(workspace!); if (st.dev !== inode!.dev || st.ino !== inode!.ino || !st.isDirectory() || fs.realpathSync(workspace!) !== workspace) fail('workspace identity changed');
    const paths = new Set(expected.keys()); for (const f of expected.keys()) {let p = path.posix.dirname(f); while (p !== '.') {paths.add(p); p = path.posix.dirname(p);}}
    const seen = new Set<string>();
    const walk = (directory: string) => {for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
      const file = path.join(directory, entry.name), relative = path.relative(workspace!, file).split(path.sep).join('/');
      if (!paths.has(relative) || seen.has(relative)) fail('unexpected run path'); seen.add(relative);
      if (entry.isDirectory()) walk(file); else if (!entry.isFile() || sha256(readRegular(file, 64 * 1024 * 1024)) !== expected.get(relative)) fail('run file changed');
    }};
    walk(workspace!); if (seen.size !== paths.size) fail('run path missing'); return {files: expected.size};
  };
  const nativeIds = ['strict-native-compilation', 'independent-module-surface-observation', 'native-package-imports'];
  const prerequisites = ['source-currentness', 'compiled-graph-obligations', 'isolated-exact-source-replay', 'toolchain-currentness', 'verification-workspace-currentness', 'verification-workspace-cleanup'];
  put('compiled-graph-obligations', 'pass', 'checked graph and finite refinement validated', {projection_sha256: input.projection_sha256});
  try {
    const sourceOk = attempt('source-currentness', sourceCurrent);
    const toolOk = attempt('toolchain-currentness', () => {
      executable = fs.realpathSync(options.python_executable); fs.accessSync(executable, fs.constants.X_OK);
      executableSha = sha256(readRegular(executable, 128 * 1024 * 1024));
      if (complete) {
        leanExecutable = fs.realpathSync((options as PythonVerificationOptions).lean_executable); fs.accessSync(leanExecutable, fs.constants.X_OK);
        leanExecutableSha = sha256(readRegular(leanExecutable, 128 * 1024 * 1024));
      }
      const st = fs.lstatSync(options.temporary_parent); if (!st.isDirectory() || st.isSymbolicLink() || fs.realpathSync(options.temporary_parent) !== options.temporary_parent) fail('real temporary parent required');
      return {executable, executable_sha256: executableSha, ...(complete ? {lean_executable: leanExecutable, lean_executable_sha256: leanExecutableSha} : {})};
    });
    if (sourceOk && toolOk) {
      attempt('isolated-exact-source-replay', () => {
        const size = plan.artifacts.reduce((n, a) => n + a.size_bytes, graph.source_manifest.total_size_bytes);
        if (size > 64 * 1024 * 1024) fail('verification workspace exceeds 64MiB bound');
        workspace = fs.mkdtempSync(path.join(options.temporary_parent, 'domainspec-python-verify-')); inode = fs.lstatSync(workspace);
        for (const s of graph.source_manifest.sources) {const bytes = readRegular(path.join(graph.project_root, s.relative_path), s.size_bytes); if (bytes.length !== s.size_bytes || sha256(bytes) !== s.sha256) fail('source identity'); write('source/' + s.relative_path, bytes);}
        const replay = planCompiledReconciledPythonProject(loadCompiledProjectGraph(path.join(workspace, 'source')), plan.selection);
        same(replay, plan, 'isolated replay changed plan');
        for (const a of plan.artifacts) write('native/' + a.relative_path, a.content);
        workspaceCurrent(); return {plan_sha256: replay.plan_sha256, source_files: graph.source_manifest.source_count, generated_files: plan.artifacts.length, bytes: size};
      });
      const runOk = attempt('strict-native-compilation', () => {
        workspaceCurrent();
        const result = spawnSync(executable, ['-I', '-S', '-B', '-c', observer], {cwd: workspace!, env: {LANG: 'C.UTF-8', TZ: 'UTC'}, input: JSON.stringify({root: path.join(workspace!, 'native'), modules: plan.modules}), encoding: 'utf8', timeout: 30000, killSignal: 'SIGKILL', maxBuffer: 8 * 1024 * 1024});
        if (result.error || result.status !== 0) fail('native process rejected:' + (result.error?.message || result.stderr || 'exit ' + result.status).slice(0, 4096));
        const observed = JSON.parse(result.stdout) as {schema_version: string; compiled_paths: string[]; observed_paths: string[]; imported_paths: string[]; python_version: number[]; toolchain_files: Record<string, string>; domain_behavior: string};
        assertInterfaceData(observed);
        if (observed.schema_version !== 'domainspec.python-native-observation/v1-candidate' || observed.domain_behavior !== 'not-performed' || observed.python_version[0] !== 3) fail('native report identity');
        const paths = plan.modules.map(m => m.relative_path);
        for (const selected of [observed.compiled_paths, observed.observed_paths, observed.imported_paths]) same(selected, paths, 'incomplete native coverage');
        for (const [file, digest] of Object.entries(observed.toolchain_files)) if (sha256(readRegular(file, 128 * 1024 * 1024)) !== digest) fail('observed toolchain changed');
        if (!Object.keys(observed.toolchain_files).length) fail('toolchain observation missing');
        put('toolchain-currentness', 'pass', 'interpreter and observed native dependencies current', {executable, executable_sha256: executableSha, ...(complete ? {lean_executable: leanExecutable, lean_executable_sha256: leanExecutableSha} : {}), python_version: observed.python_version, files: observed.toolchain_files});
        const evidence = {observer_sha256: OBSERVER_SHA256, observation_sha256: sha256(canonicalJson(observed)), module_count: paths.length};
        put('independent-module-surface-observation', 'pass', 'native AST bindings and imports match', evidence);
        put('native-package-imports', 'pass', 'all selected modules imported from exact generated files', evidence);
        return evidence;
      }, ['isolated-exact-source-replay']);
      if (!runOk) for (const id of nativeIds.slice(1)) put(id, 'not_evaluable', 'native observation failed', {}, false, ['strict-native-compilation']);
      if (controls) {
        const passed = attempt('selected-generator-semantic-controls', () => {
          const astObserver = getReconciledSource('python_calculation_observer'), runner = getReconciledSource('python_calculation_semantics');
          if (sha256(astObserver) !== 'ff6f8cdd5359478bc5805c1febd60233c34695dfac3812a9199efefbc991bef4' || sha256(runner) !== 'f903372605c5670690f27f55218c263e48973e3d22e921e8f721ce67f950dc56') fail('semantic observer drift');
          workspaceCurrent();
          const query = getReconciledSource('python_query_observer'), mapping = getReconciledSource('python_mapping_observer'), dataRunner = getReconciledSource('python_data_semantics');
          if (sha256(query) !== '08c92082e288705a5b283a9222f87d6c26efed7ca7df4da3033b18ca50ba7f60' || sha256(mapping) !== 'ec95e86efa845e5d863c5ba34c303090707ec6053d7cb88b6a88a77b2e411d96' || sha256(dataRunner) !== 'e7a0f6f05afb23814263f006d4342418ac8408dbb3759c04bf6aa34ee959b60a') fail('data observer drift');
          const operation = getReconciledSource('python_operation_observer'), rule = getReconciledSource('python_rule_observer'), policy = getReconciledSource('python_policy_observer');
          if (sha256(operation) !== 'b1f5a8dd312d738b4963bed6b8fec5f335626cc5ebc65c5cc965fed82a778c74' || sha256(rule) !== 'fc7688a66073ecb88f3a2e4584825acd6b21622b96cdf05db3848dd3c10e6eaf' || sha256(policy) !== 'a26b64aad7fa8494559d9cac8fe46918070105a220c7e68865de6c0ed89506f3') fail('decision observer drift');
          const enumObserver = getReconciledSource('python_enum_observer'), enumRunner = getReconciledSource('python_enum_semantics');
          if (sha256(enumObserver) !== 'c31cdf7078453edc4c8593ebb9f85e98cd386242770a129cb1963965f0cb752d' || sha256(enumRunner) !== '3694e510d09db618f782d58ef4ae672aeb699cf570cc849b27934f76dcd6bb60') fail('Enum observer drift');
          const ownedObserver = getReconciledSource('python_owned_observer');
          if (sha256(ownedObserver) !== '5a325297c84353be413413cc52531c069ca7a052ee69cc9deb349a7036f4dace') fail('owned observer drift');
          const ownedRunner = getReconciledSource('python_owned_semantics');
          if (sha256(ownedRunner) !== 'e9baedf7f0e28702f367403dd894b806fdaa2ac4a68ee1befc5e85c2ab182fd3') fail('owned semantics drift');
          const factoryRunner = getReconciledSource('python_factory_semantics');
          if (sha256(factoryRunner) !== '340ae55383c1e59f0fe926abaff293b3ed45f805df86d7fd1509925e486dc30e') fail('factory semantics drift');
          const eventObserver = getReconciledSource('python_event_observer'), eventRunner = getReconciledSource('python_event_semantics');
          if (sha256(eventObserver) !== '6c8f1db9dc4629fa89aab1e4a7d8f64a828a56d150a6416dbc97b6f1c8ec17bb' || sha256(eventRunner) !== 'dc96099dd0465a99e4ca815d2612115ebe8592b61943c43387f8b9b62e60780f') fail('Event verifier drift');
          const stateMachineObserver = getReconciledSource('python_state_machine_observer'), stateMachineRunner = getReconciledSource('python_state_machine_semantics');
          if (sha256(stateMachineObserver) !== 'f33a24e929a19cfb78f20eafd85e68849f800e27d5a6028efd2bc3412d0470de' || sha256(stateMachineRunner) !== '7ff57e8ca7fdac79b06c3f915f7ea5bc59549c7ee92fffc17793442e55c72a9f') fail('State Machine verifier drift');
          const operationRunner = getReconciledSource('python_operation_semantics');
          if (sha256(operationRunner) !== 'e38224d2c4ae102227d66afa859d47657d46efe95624d9f4c60950363cf63a0e') fail('Operation verifier drift');
          const workflowObserver = getReconciledSource('python_workflow_observer'), materialObserver = getReconciledSource('python_workflow_materialization_observer'), workflowRunner = getReconciledSource('python_workflow_semantics');
          if (sha256(workflowObserver) !== 'c3c469ee45d3db75570f604a54b7956ea1cd1c3f53e53b9dfeb00c5ecdba91a7' || sha256(materialObserver) !== 'a52a21df5a9766b60c4c30e0ac62502a9bfdfbc558be6cc37007ea9e57ed5360' || sha256(workflowRunner) !== '1bee9cf6b9a6a461c43936e8869fc0d039eda9d99f2746d8b6380aee8a950717') fail('Workflow verifier drift:' + [sha256(workflowObserver), sha256(materialObserver), sha256(workflowRunner)].join(','));
          const load = (name: string, source: string, bindings = '') => name + " = {'__name__': 'observer'" + bindings + "}\nexec(" + JSON.stringify(source) + ', ' + name + ')\n';
          const interfaceObserver = getReconciledSource('python_interface_observer'), interfaceRunner = getReconciledSource('python_interface_semantics');
          const publicMappingObserver = getReconciledSource('python_public_mapping_observer'), publicMappingRunner = getReconciledSource('python_public_mapping_semantics');
          if (sha256(publicMappingObserver) !== 'a54c1c03e3cdd96c818cf082c550a2ccf409fc7571828fa0c78088f13c3e1380' || sha256(publicMappingRunner) !== '83e334a4fdca0bd2311086f5a47001202b1a2d7c38472cc7f6a250689536431f') fail('public Mapping verifier drift');
          if (sha256(interfaceObserver) !== '5b78e005a34053e114bb5e93b208b1defaba0394694ad5b37f4cce707e6a31ef' || sha256(interfaceRunner) !== '91a9b53149a599a587662a3c826f54b20b4b77738e456ce9394540438d6e9204') fail('Interface verifier drift');
          const script = 'import json, sys, types\n' + load('calculation', astObserver + '\n' + runner) + load('query', query) + load('mapping', mapping)
            + load('operation', operation) + load('rule', rule, ", 'helper': types.SimpleNamespace(**operation)") + load('policy', policy, ", 'observe_rule': rule['observe_rule']")
            + load('data', dataRunner) + load('enum_observer', enumObserver) + load('enum_runner', enumRunner)
            + load('owned_observer', ownedObserver) + load('owned_runner', ownedRunner)
            + load('factory_runner', factoryRunner, ", 'owned': types.SimpleNamespace(**owned_runner)")
            + load('event_observer', eventObserver) + load('event_runner', eventRunner, ", 'owned': types.SimpleNamespace(**owned_runner)")
            + load('state_machine_observer', stateMachineObserver, ", 'helper': types.SimpleNamespace(**operation)")
            + load('state_machine_runner', stateMachineRunner, ", 'owned': types.SimpleNamespace(**owned_runner)")
            + load('operation_runner', operationRunner, ", 'owned': types.SimpleNamespace(**owned_runner), 'facts': types.SimpleNamespace(**state_machine_runner)")
            + load('material_observer', materialObserver, ", 'base': types.SimpleNamespace(**operation)")
            + load('workflow_observer', workflowObserver, ", 'material': types.SimpleNamespace(**material_observer)")
            + load('workflow_runner', workflowRunner, ", 'owned': types.SimpleNamespace(**owned_runner), 'facts': types.SimpleNamespace(**state_machine_runner), 'operations': types.SimpleNamespace(**operation_runner)")
            + load('interface_observer', interfaceObserver, ", 'base': types.SimpleNamespace(**operation)")
            + load('interface_runner', interfaceRunner, ", 'owned': types.SimpleNamespace(**owned_runner), 'facts': types.SimpleNamespace(**state_machine_runner), 'operations': types.SimpleNamespace(**operation_runner)")
            + load('public_mapping_observer', publicMappingObserver, ", 'api': types.SimpleNamespace(**interface_observer)")
            + load('public_mapping_runner', publicMappingRunner, ", 'owned': types.SimpleNamespace(**owned_runner), 'facts': types.SimpleNamespace(**state_machine_runner), 'operations': types.SimpleNamespace(**operation_runner), 'interface': types.SimpleNamespace(**interface_observer)")
            + "def preceding(value): return data['run'](value, calculation['run_semantics'], query['observe'], mapping['observe'], rule['observe_rule'], policy['observe'])\n"
            + "def preceding_enums(value): return enum_runner['run'](value, preceding, enum_observer['observe'])\n"
            + "def preceding_sums(value): return owned_runner['run'](value, preceding_enums, owned_observer['observe'], enum_observer['observe'], rule['observe_rule'])\n"
            + "def preceding_factories(value): return factory_runner['run'](value, preceding_sums, owned_observer['observe'], enum_observer['observe'], rule['observe_rule'])\n"
            + "def preceding_events(value): return event_runner['run'](value, preceding_factories, event_observer['observe'])\n"
            + "def preceding_state_machines(value): return state_machine_runner['run'](value, preceding_events, state_machine_observer['observe'])\n"
            + "def preceding_operations(value): return operation_runner['run'](value, preceding_state_machines, operation['observe'], event_observer['observe'])\n"
            + "def preceding_workflows(value): return workflow_runner['run'](value, preceding_operations, workflow_observer['observe'], event_observer['observe'])\n"
            + "def preceding_interfaces(value): return interface_runner['run'](value, preceding_workflows, interface_observer['observe'])\n"
            + "request=json.load(sys.stdin)\nowned_surface=owned_observer['observe'](request, enum_observer['observe'], rule['observe_rule'])\n"
            + "print(json.dumps({**public_mapping_runner['run'](request, preceding_interfaces, public_mapping_observer['observe']), 'owned_surface': owned_surface}, sort_keys=True, separators=(',', ':')))\n";
          // Linux limits each argv entry independently of ARG_MAX. Keep the
          // pinned program and controls in bounded stdin, not one growing -c
          // argument or another temporary script file/workspace.
          const input = JSON.stringify({program: script, request: {root: path.join(workspace!, 'native'), controls}});
          if (Buffer.byteLength(input) > 10 * 1024 * 1024) fail('semantic transport capacity');
          const launcher = "import io,json,sys\nenvelope=json.load(sys.stdin)\nsys.stdin=io.StringIO(json.dumps(envelope['request']))\nexec(compile(envelope['program'], '<domainspec-semantic-verification>', 'exec'))\n";
          const result = spawnSync(executable, ['-I', '-S', '-B', '-c', launcher], {cwd: workspace!, env: {LANG: 'C.UTF-8', TZ: 'UTC'}, input, encoding: 'utf8', timeout: 30000, killSignal: 'SIGKILL', maxBuffer: 8 * 1024 * 1024});
          if (result.error || result.status !== 0) fail('semantic process rejected:' + (result.error?.message || result.stderr || 'exit ' + result.status).slice(0, 4096));
          const observation = JSON.parse(result.stdout) as {schema_version: string; controls_sha256: string; rows: typeof semanticRows; toolchain_files: Record<string, string>; owned_surface: {selectors: string[]; factories: number; sums: number; plain_enums: number; rules: number}};
          assertInterfaceData(observation);
          if (observation.schema_version !== 'domainspec.python-semantic-observation/v1-candidate' || observation.controls_sha256 !== controls.controls_sha256) fail('semantic report identity');
          const expectedRows = controls.rows.map(r => r.state === 'ready' ? {selector: r.selector, kind: r.kind, result: 'pass', executed: true, case_count: r.cases.length, native_form: 'pass', binding_controls: r.kind === 'Rule' ? 0 : 3, compiling_substitutions: 2} : {selector: r.selector, kind: r.kind, result: 'not_evaluable', executed: false});
          same(observation.rows, expectedRows, 'incomplete semantic coverage');
          const declarations = controls.data_model?.declarations ?? [];
          same(observation.owned_surface, {selectors: declarations.map(d => d.selector).sort(), factories: declarations.filter(d => d.kind !== 'Enum').length,
            sums: declarations.filter(d => d.kind === 'Enum' && d.contract.variants.some(v => v.payload !== null)).length,
            plain_enums: declarations.filter(d => d.kind === 'Enum' && d.contract.variants.every(v => v.payload === null)).length, rules: controls.rule_modules.length}, 'incomplete owned source observation');
          if (!Object.keys(observation.toolchain_files).length) fail('semantic toolchain observation missing');
          for (const [file, digest] of Object.entries(observation.toolchain_files)) if (sha256(readRegular(file, 128 * 1024 * 1024)) !== digest) fail('semantic toolchain changed');
          const toolEvidence = checks.get('toolchain-currentness')!.evidence;
          const nativeFiles = toolEvidence.files as Record<string, string>;
          for (const [file, digest] of Object.entries(observation.toolchain_files)) if (Object.hasOwn(nativeFiles, file) && nativeFiles[file] !== digest) fail('toolchain changed between native and semantic stages');
          toolEvidence.files = {...toolEvidence.files as Record<string, string>, ...observation.toolchain_files};
          semanticRows.splice(0, semanticRows.length, ...observation.rows);
          return {definition_sha256: PYTHON_SEMANTIC_VERIFICATION_SHA256, data_definition_sha256: PYTHON_DATA_SEMANTIC_SHA256, decision_definition_sha256: PYTHON_DECISION_SEMANTIC_SHA256, enum_definition_sha256: PYTHON_ENUM_SEMANTIC_SHA256, owned_observation_sha256: controls.owned_observation_sha256, sum_definition_sha256: controls.sum_definition_sha256, factory_definition_sha256: controls.factory_definition_sha256, event_definition_sha256: controls.event_definition_sha256, state_machine_definition_sha256: controls.state_machine_definition_sha256, operation_definition_sha256: controls.operation_definition_sha256, workflow_definition_sha256: controls.workflow_definition_sha256, interface_definition_sha256: controls.interface_definition_sha256, public_mapping_definition_sha256: controls.public_mapping_definition_sha256, owned_surface: observation.owned_surface, controls_sha256: controls.controls_sha256, observation_sha256: sha256(canonicalJson(observation)), node_count: semanticRows.length, passed_nodes: semanticRows.filter(r => r.result === 'pass').length, case_count: controls.case_count};
        }, nativeIds);
        if (passed && semanticRows.some(r => r.result !== 'pass')) put('selected-generator-semantic-controls', 'not_evaluable', 'remaining source nodes require semantic executors', checks.get('selected-generator-semantic-controls')!.evidence, true);
        if (complete && checks.get('selected-generator-semantic-controls')?.result === 'pass') {
          put('cross-generator-behavior', 'pass', 'Python native outcomes match the compiler-owned shared source cases', {
            scope: 'python-native-versus-shared-source-outcomes', controls_sha256: controls.controls_sha256,
            node_count: semanticRows.length, case_count: controls.case_count,
            outcomes_sha256: sha256(canonicalJson(semanticRows.map(({selector, kind, result, case_count}) => ({selector, kind, result, case_count})))),
          });
        }
      }
      if (complete && workspace) {
        const formal = createReconciledFormalization(graph, plan);
        const auditSuffix = '\n#print axioms DomainSpec.Reconciled.currentStructuralReferencesHold\n#eval IO.println (DomainSpec.Reconciled.toJson DomainSpec.Reconciled.sourceData)\n';
        write('Reconciled.lean', formal.artifact.content); write('Audit.lean', formal.artifact.content + auditSuffix);
        let observedMeaning: unknown;
        attempt('lean-structural-kernel', () => {
          workspaceCurrent();
          const version = spawnSync(leanExecutable, ['--version'], {cwd: workspace!, encoding: 'utf8', timeout: SUBPROCESS_TIMEOUT_MS, maxBuffer: 32 * 1024 * 1024});
          if (version.error || version.status !== 0 || !/^Lean \(version 4\.33\.1,/.test(version.stdout.trim())) fail('Lean 4.33.1 required');
          const result = spawnSync(leanExecutable, [path.join(workspace!, 'Audit.lean')], {cwd: workspace!, env: {LANG: 'C.UTF-8', TZ: 'UTC', LEAN_PATH: ''}, encoding: 'utf8', timeout: SUBPROCESS_TIMEOUT_MS, killSignal: 'SIGKILL', maxBuffer: 32 * 1024 * 1024});
          if (result.error || result.status !== 0) fail('Lean rejected formalization:' + (result.error?.message || result.stderr || 'exit ' + result.status).slice(0, 4096));
          const lines = result.stdout.trim().split('\n');
          if (lines.length !== 2 || lines[0] !== "'DomainSpec.Reconciled.currentStructuralReferencesHold' depends on axioms: [propext, Classical.choice, Quot.sound]") fail('unexpected Lean proof dependency or output');
          observedMeaning = JSON.parse(lines[1]!);
          return {version: version.stdout.trim(), proof_sha256: formal.artifact.sha256, audit_sha256: expected.get('Audit.lean'), axioms: ['propext', 'Classical.choice', 'Quot.sound'], scope: formal.claim_scope, checked_predicates: formal.checked_predicates};
        }, ['isolated-exact-source-replay', 'toolchain-currentness']);
        attempt('source-and-selection-preservation', () => {
          const expectedMeaning = {graph: input.semantic_graph, selection: input.compilation_selection};
          if (canonicalJson(observedMeaning) !== canonicalJson(expectedMeaning)) fail('Lean source/selection round trip mismatch');
          return {observation_sha256: sha256(canonicalJson(observedMeaning))};
        }, ['lean-structural-kernel']);
        attempt('successor-formalization-currentness', () => {
          if (readRegular(path.join(workspace!, 'Reconciled.lean'), 64 * 1024 * 1024).toString('utf8') !== formal.artifact.content || readRegular(path.join(workspace!, 'Audit.lean'), 64 * 1024 * 1024).toString('utf8') !== formal.artifact.content + auditSuffix) fail('formalization bytes changed');
          return {proof_sha256: formal.artifact.sha256, bundle_sha256: formal.bundle_sha256};
        }, ['lean-structural-kernel', 'source-and-selection-preservation']);
      }
    }
    attempt('source-currentness', sourceCurrent);
    attempt('toolchain-currentness', () => {
      if (!executable || fs.realpathSync(options.python_executable) !== executable || sha256(readRegular(executable, 128 * 1024 * 1024)) !== executableSha) fail('interpreter changed');
      if (complete && (!leanExecutable || fs.realpathSync((options as PythonVerificationOptions).lean_executable) !== leanExecutable || sha256(readRegular(leanExecutable, 128 * 1024 * 1024)) !== leanExecutableSha)) fail('Lean executable changed');
      for (const [file, digest] of Object.entries((checks.get('toolchain-currentness')!.evidence.files ?? {}) as Record<string, string>)) if (sha256(readRegular(file, 128 * 1024 * 1024)) !== digest) fail('observed toolchain changed after execution');
      return checks.get('toolchain-currentness')!.evidence;
    });
    if (workspace) attempt('verification-workspace-currentness', workspaceCurrent);
    if (options.target_root) attempt('exact-output-currentness', () => {
      const result = verifyReconciledProject(plan, options.target_root, null, options.output_layout); if (result.result !== 'pass') fail('published output differs'); return {view_sha256: result.view_sha256};
    }, ['source-currentness']);
  } finally {
    attempt('verification-workspace-cleanup', () => {
      if (workspace) {
        const st = fs.lstatSync(workspace); if (!inode || st.dev !== inode.dev || st.ino !== inode.ino || !st.isDirectory() || st.isSymbolicLink()) fail('refuse cleanup of replaced workspace');
        fs.rmSync(workspace, {recursive: true, force: false}); if (fs.existsSync(workspace)) fail('workspace remains');
      }
      return {created: workspace !== null, removed: workspace !== null};
    });
  }
  const blocked = prerequisites.filter(id => checks.get(id)?.result !== 'pass');
  if (blocked.length) for (const id of nativeIds) if (checks.get(id)?.result === 'pass') put(id, 'not_evaluable', 'final prerequisite failed', checks.get(id)!.evidence, true, blocked);
  if (controls && blocked.length) {
    for (const row of semanticRows) if (row.result === 'pass') {row.result = 'not_evaluable'; row.blocked_by = blocked;}
    if (checks.get('selected-generator-semantic-controls')?.result !== 'fail') put('selected-generator-semantic-controls', 'not_evaluable', 'final prerequisite failed', checks.get('selected-generator-semantic-controls')!.evidence, checks.get('selected-generator-semantic-controls')!.executed, blocked);
  }
  const rows = [...checks.values()];
  const body = {schema_version: complete ? 'domainspec.python-complete-verification/v1-candidate' as const : 'domainspec.python-native-verification/v1-candidate' as const,
    definition_sha256: complete ? PYTHON_COMPLETE_VERIFICATION_SHA256 : PYTHON_NATIVE_VERIFICATION_SHA256,
    ...(complete ? {native_definition_sha256: PYTHON_NATIVE_VERIFICATION_SHA256} : {}),
    projection_sha256: input.projection_sha256, project_plan_sha256: plan.plan_sha256, checks: rows,
    result: rows.some(c => c.result === 'fail') ? 'fail' as const : complete && rows.every(c => c.result === 'pass') ? 'pass' as const : 'not_evaluable' as const,
    native_stage_result: rows.some(c => c.result === 'fail') ? 'fail' as const : [...nativeIds, ...prerequisites].every(id => checks.get(id)?.result === 'pass') ? 'pass' as const : 'not_evaluable' as const,
    residue: checks.get('verification-workspace-cleanup')?.result === 'pass' ? null : {workspace_path: workspace, cleanup_required: true as const},
    claim_scope: complete ? 'selected-python-native-semantics-and-finite-structural-references' as const : 'native-compilation-import-and-module-structure-only' as const,
    ...(controls ? {semantic_definition_sha256: PYTHON_SEMANTIC_VERIFICATION_SHA256, semantic_rows: semanticRows} : {}),
    semantic_observation: controls ? 'bounded-per-node' as const : 'not-performed' as const, formal_verification: complete ? 'finite-structural-references' as const : 'not-performed' as const, authority_effect: 'none' as const};
  const report = freeze({...body, report_sha256: sha256(canonicalJson(body))}); registered.add(report); return report;
}
export type PythonNativeVerification = ReturnType<typeof executeReconciledPythonNativeVerification>;
export type PythonVerification = ReturnType<typeof executeReconciledPythonVerification>;
export function renderPythonNativeVerification(value: PythonNativeVerification): string {
  if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered report required'); return canonicalJson(value) + '\n';
}
