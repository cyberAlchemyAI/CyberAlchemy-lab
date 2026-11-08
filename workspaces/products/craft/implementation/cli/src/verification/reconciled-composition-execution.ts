import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertCompositionControls, type CompositionControls} from './reconciled-composition-controls.js';

export interface CompositionExecutionOptions {workspace_parent: string; typescript_root: string; node_type_root: string;}
export class CompositionExecutionError extends Error {
  constructor(readonly phase: string, reason: string, readonly workspace?: string) {super('COMPOSITION_EXECUTION:' + phase + ':' + reason); this.name = 'CompositionExecutionError';}
}
const receipts = new WeakMap<object, () => void>();
const absolute = (p: string) => {if (typeof p !== 'string' || !path.isAbsolute(p) || path.resolve(p) !== p || fs.realpathSync(p) !== p) throw Error('normalized nonsymbolic absolute path required'); return p;};
function read(file: string, maximum = 8388608): Buffer {
  absolute(file); const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const st = fs.fstatSync(fd); if (!st.isFile() || st.size > maximum) throw Error('bounded regular file required');
    const value = Buffer.alloc(st.size + 1); let offset = 0;
    while (offset < value.length) {const n = fs.readSync(fd, value, offset, value.length - offset, null); if (!n) break; offset += n;}
    if (offset !== st.size) throw Error('file changed during read'); return value.subarray(0, offset);
  } finally {fs.closeSync(fd);}
}
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;}
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) throw Error(reason);};

/** Private computation executor. Parent public verification still owns whole-project replay. */
export function executeCompositionControls(control: CompositionControls, options: CompositionExecutionOptions) {
  let phase = 'preflight', workspace: string | undefined;
  try {
    assertCompositionControls(control);
    if (!options || ![Object.prototype, null].includes(Object.getPrototypeOf(options)) || Reflect.ownKeys(options).length !== 3 || ['workspace_parent', 'typescript_root', 'node_type_root'].some(k => {const d = Object.getOwnPropertyDescriptor(options, k); return !d || !d.enumerable || !Object.hasOwn(d, 'value') || typeof d.value !== 'string';})) throw Error('closed data tool options');
    const selected = {...options}; Object.values(selected).forEach(absolute);
    if (process.version !== 'v26.8.1') throw Error('Node 26.8.1 required');
    const tsc = path.join(selected.typescript_root, 'bin/tsc');
    const toolPaths = [process.execPath, path.join(selected.typescript_root, 'package.json'), tsc, path.join(selected.typescript_root, 'dist/api/sync/api.js'), path.join(selected.typescript_root, 'dist/ast/index.js'), path.join(selected.node_type_root, 'node/package.json')];
    const fingerprint = () => Object.fromEntries(toolPaths.map(p => [p, sha256(read(p, 268435456))]));
    const tools = fingerprint();
    if (JSON.parse(read(toolPaths[1]!).toString()).version !== '7.0.2' || JSON.parse(read(toolPaths[5]!).toString()).name !== '@types/node') throw Error('TypeScript 7.0.2 and explicit Node types required');
    workspace = fs.mkdtempSync(path.join(selected.workspace_parent, 'ds-composition-run-')); absolute(workspace);
    const root = workspace, sourceRoot = path.join(root, 'source'), nativeRoot = path.join(root, 'native');
    fs.mkdirSync(sourceRoot); fs.mkdirSync(nativeRoot);
    const expected = new Map<string, string>();
    function add(relative: string, content: string) {
      if (relative.includes('\\') || relative.includes('\0') || path.posix.isAbsolute(relative) || relative.split('/').some(p => !p || p === '.' || p === '..')) throw Error('unsafe run path');
      const file = path.join(root, relative); fs.mkdirSync(path.dirname(file), {recursive: true, mode: 0o700});
      fs.writeFileSync(file, content, {flag: 'wx', mode: 0o600}); expected.set(relative, sha256(content)); return file;
    }
    function inventory() {
      absolute(root); const names = new Set(['source', 'native']);
      for (const file of expected.keys()) {names.add(file); let parent = path.posix.dirname(file); while (parent !== '.') {names.add(parent); parent = path.posix.dirname(parent);}}
      const found = new Set<string>();
      function walk(dir: string) {for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
        const file = path.join(dir, entry.name), relative = path.relative(root, file).split(path.sep).join('/');
        if (!names.has(relative) || found.has(relative) || entry.isSymbolicLink()) throw Error('unexpected or symbolic run artifact:' + relative); found.add(relative);
        if (entry.isDirectory()) {if (expected.has(relative)) throw Error('artifact became directory'); walk(file);}
        else if (!entry.isFile() || !expected.has(relative)) throw Error('nonregular run artifact');
      }}
      walk(root); if (found.size !== names.size) throw Error('missing run artifact');
      for (const [relative, hash] of expected) if (sha256(read(path.join(root, relative), 33554432)) !== hash) throw Error('run artifact changed:' + relative);
    }
    const current = () => {inventory(); same(fingerprint(), tools, 'toolchain changed'); assertCompositionControls(control);};
    const run = (args: string[], restricted = false) => {
      const result = spawnSync(process.execPath, args, {cwd: root, env: {LANG: 'C', TZ: 'UTC'}, encoding: 'utf8', timeout: 60000, maxBuffer: 33554432});
      if (result.error || result.status !== 0) throw Error((restricted ? 'restricted runner rejected:' : 'native tool rejected:') + (result.error?.message || result.stderr || result.stdout || 'exit ' + result.status).slice(0, 4096));
      return result.stdout;
    };
    phase = 'source-materialization';
    for (const s of control.sources) add('source/' + s.relative_path, s.content);
    add('package.json', '{"type":"module"}\n');
    const b = control.family.binding, nativePath = (p: string) => p.replace(/\.ts$/, '.js');
    const compilerOptions = {strict: true, skipLibCheck: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: ['node'], typeRoots: [selected.node_type_root], rootDir: sourceRoot, outDir: nativeRoot};
    const config = add('compiler.json', canonicalJson({compilerOptions, files: b.modules.filter(m => m.relative_path.endsWith('.ts')).map(m => path.join(sourceRoot, m.relative_path))}) + '\n');
    const sourceAuditConfig = add('source-audit.json', canonicalJson({compilerOptions: {...compilerOptions, allowJs: true, checkJs: false, noEmit: true}, files: b.modules.map(m => path.join(sourceRoot, m.relative_path))}) + '\n');
    const auditScript = add('effects.mjs', control.audit_runner), runner = add('runner.mjs', control.runner);
    current(); phase = 'strict-native-compilation'; run([tsc, '--project', config, '--pretty', 'false']);
    // Native JavaScript is already emitted source. TypeScript would reformat it;
    // preserve its exact bytes and check syntax in the independent AST phase.
    for (const s of control.sources) if (s.relative_path.endsWith('.mjs')) add('native/' + s.relative_path, s.content);
    let total = 0;
    const nativeModules = b.modules.map(m => {
      const relative_path = nativePath(m.relative_path), bytes = read(path.join(nativeRoot, relative_path)); total += bytes.length;
      if (total > 67108864) throw Error('native closure capacity');
      const hash = sha256(bytes); if (m.relative_path.endsWith('.mjs') && hash !== m.source_sha256) throw Error('generated JavaScript changed during compilation');
      expected.set('native/' + relative_path, hash); return {relative_path, sha256: hash};
    });
    current();
    const auditHashes: Record<string, string> = {};
    for (const stage of ['source', 'native'] as const) {
      phase = stage + '-effect-audit';
      const paths = b.modules.map(m => stage === 'source' ? m.relative_path : nativePath(m.relative_path));
      const moduleRoot = stage === 'source' ? sourceRoot : nativeRoot;
      const auditConfig = stage === 'source' ? sourceAuditConfig : add('native-audit.json', canonicalJson({compilerOptions: {allowJs: true, checkJs: false, noEmit: true, skipLibCheck: true, target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', types: ['node'], typeRoots: [selected.node_type_root]}, files: paths.map(p => path.join(moduleRoot, p))}) + '\n');
      const input = add('effects-' + stage + '.json', canonicalJson({...control.effect, definition: control.definitions.effects, phase: stage, module_root: moduleRoot, module_paths: paths}) + '\n');
      current(); const observedText = run([auditScript, selected.typescript_root, auditConfig, input]); current();
      const observation = JSON.parse(observedText);
      const wanted = {schema_version: 'domainspec.composition-effect-observation/v1-candidate', phase: stage, definition_sha256: control.effect.definition_sha256,
        modules: b.modules.map((m, i) => ({relative_path: paths[i], source_sha256: stage === 'source' ? m.source_sha256 : nativeModules[i]!.sha256, imports: m.imports, exports: m.exports, violations: []}))};
      same(observation, wanted, 'independent ' + stage + ' audit mismatch');
      add('effects-' + stage + '-observation.json', observedText); auditHashes[stage] = sha256(observedText);
    }
    phase = 'native-behavior';
    const inputText = canonicalJson({schema_version: 'domainspec.composition-run-input/v1-candidate', control_sha256: control.control_sha256, binding_sha256: b.binding_sha256,
      behavior_path: b.behavior_path, adapter_path: nativePath(b.adapter_path), modules: nativeModules,
      cases: control.family.cases.map(c => ({id: c.id, request: c.request, input: c.input}))}) + '\n';
    if (Buffer.byteLength(inputText) > 16777216) throw Error('whole runner input capacity');
    const input = add('cases.json', inputText); current();
    const observedText = run(['--permission', '--allow-fs-read=' + root, '--disable-proto=throw', '--max-old-space-size=256', runner, input, nativeRoot, control.runner_sha256, sha256(inputText)], true);
    current();
    if (Buffer.byteLength(observedText) > 16777216) throw Error('whole observation capacity');
    const observed = JSON.parse(observedText), wanted = {
      schema_version: 'domainspec.composition-run-observation/v1-candidate', control_sha256: control.control_sha256, binding_sha256: b.binding_sha256,
      runner_sha256: control.runner_sha256, input_sha256: sha256(inputText), modules: nativeModules,
      cases: control.family.cases.map(c => ({id: c.id, observed: c.expected, input_changed: false}))};
    same(observed, wanted, 'native outcomes or ordered observations differ from source');
    add('observations.json', observedText); phase = 'final-currentness'; current();
    const result = freeze({schema_version: 'domainspec.composition-execution/v1-candidate' as const, result: 'pass' as const, control_sha256: control.control_sha256,
      binding_sha256: b.binding_sha256, workspace: root, cases: control.family.cases.length, modules: nativeModules, audits: auditHashes,
      observation_sha256: sha256(observedText), files: Object.fromEntries(expected), tool_files: tools, authority_effect: 'none' as const,
      claim_scope: 'finite-private-computation-controls-not-whole-project-verification' as const});
    receipts.set(result, current); return result;
  } catch (error) {throw new CompositionExecutionError(phase, error instanceof Error ? error.message : String(error), workspace);}
}
export type CompositionExecution = ReturnType<typeof executeCompositionControls>;
export function assertCompositionExecutionCurrent(value: unknown): asserts value is CompositionExecution {
  if (!value || typeof value !== 'object' || !receipts.has(value)) throw new CompositionExecutionError('receipt', 'registered execution required');
  try {receipts.get(value)!();} catch (error) {throw new CompositionExecutionError('currentness', error instanceof Error ? error.message : String(error));}
}
