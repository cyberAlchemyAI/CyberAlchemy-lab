import path from 'node:path';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {sha256} from '../input/source-manifest.js';
import {inventoryPythonModule, type PythonImport} from './python-module-surface.js';
import type {PlannedArtifact} from './contracts.js';

const standard = new Set(['__future__', 'enum', 'typing', 'types', 'dataclasses', 'collections', 'hashlib', 'weakref', 'codecs', 'math', 're', 'asyncio', 'json']);
const fail = (message: string): never => {throw new TypeError('DS_RESOLVED_PYTHON_MODULES:' + message);};
const name = (value: string) => /^[A-Za-z_][A-Za-z0-9_]*$/.test(value);
export interface ResolvedPythonImport {
  readonly specifier: string;
  readonly names: PythonImport['names'];
  readonly namespace: boolean;
  readonly target_path: string | null;
  readonly target_sha256: string | null;
  readonly dependency: 'python-standard-library' | 'generated-module' | 'generated-symbol' | 'package-initializer';
}

/** Resolve one exact generated package in memory. This inventories supplied
 * bytes; it does not admit arbitrary artifacts as registered generator output.
 * No filesystem probing, native process, source rewrite or implicit dependency.
 */
export function resolvePythonModules(artifacts: readonly PlannedArtifact[], moduleRoot: string) {
  assertInterfaceData(artifacts);
  if (typeof moduleRoot !== 'string' || !moduleRoot.split('/').every(name) || standard.has(moduleRoot.split('/')[0]!) || ['sys', 'builtins', 'encodings', 'concurrent', 'socket'].includes(moduleRoot.split('/')[0]!)) fail('package root');
  if (!Array.isArray(artifacts) || !artifacts.length || artifacts.length > 65536) fail('bounded artifact array');
  const parents = new Set(moduleRoot.split('/').map((_, i, parts) => parts.slice(0, i + 1).join('/') + '/__init__.py'));
  const files = new Map<string, PlannedArtifact>(), aliases = new Set<string>();
  for (const a of artifacts) {
    const p = a.relative_path;
    if (typeof p !== 'string' || !p.endsWith('.py') || !(p.startsWith(moduleRoot + '/') || parents.has(p)) || path.posix.normalize(p) !== p || p.includes('\\') || !p.slice(0, -3).split('/').every(name)) fail('unsafe native path');
    if (files.has(p) || aliases.has(p.toLowerCase())) fail('duplicate or case-fold path');
    if (typeof a.content !== 'string' || Buffer.byteLength(a.content) !== a.size_bytes || sha256(a.content) !== a.sha256) fail('artifact content binding');
    if (p.endsWith('/__init__.py') && a.content !== '') fail('nonempty initializer');
    files.set(p, a); aliases.add(p.toLowerCase());
  }
  const surfaces = new Map([...files].map(([p, a]) => [p, inventoryPythonModule(a.content)]));
  const initializerPaths = (p: string) => {
    const parts = path.posix.dirname(p).split('/');
    return parts.map((_, i) => parts.slice(0, i + 1).join('/') + '/__init__.py').filter(init => init !== p);
  };
  const target = (base: string) => {
    const candidates = [base + '.py', base + '/__init__.py'].filter(p => files.has(p));
    if (candidates.length > 1) fail('ambiguous module/package:' + base);
    return candidates[0] ?? null;
  };
  for (const p of files.keys()) if (!p.endsWith('/__init__.py')) target(p.slice(0, -3));
  const modules = [...files].sort(([a], [b]) => a < b ? -1 : 1).map(([p, artifact]) => {
    const surface = surfaces.get(p)!;
    const imports: ResolvedPythonImport[] = [];
    const add = (i: PythonImport, targetPath: string | null, dependency: ResolvedPythonImport['dependency']) => imports.push({...i, target_path: targetPath, target_sha256: targetPath === null ? null : files.get(targetPath)!.sha256, dependency});
    for (const init of initializerPaths(p)) {
      if (!files.has(init)) fail('missing initializer:' + init);
      add({specifier: '', names: [], namespace: false}, init, 'package-initializer');
    }
    for (const i of surface.imports) {
      if (!i.specifier.startsWith('.')) {
        if (!standard.has(i.specifier)) fail('unselected absolute import:' + i.specifier);
        add(i, null, 'python-standard-library'); continue;
      }
      const dots = /^\.+/.exec(i.specifier)![0].length;
      const directory = path.posix.dirname(p).split('/');
      if (dots > directory.length) fail('relative import escapes package');
      const base = [...directory.slice(0, directory.length - dots + 1), ...i.specifier.slice(dots).split('.').filter(Boolean)].join('/');
      if (!(base === moduleRoot || base.startsWith(moduleRoot + '/'))) fail('relative import escapes selected root');
      const resolved = target(base) ?? fail('unresolved relative module:' + p + ':' + i.specifier);
      for (const entry of i.names) {
        const imported = {...i, names: [entry]};
        if (surfaces.get(resolved)!.bindings.includes(entry.name)) add(imported, resolved, 'generated-symbol');
        else if (resolved.endsWith('/__init__.py')) {
          const child = target(base + '/' + entry.name) ?? fail('unresolved package member:' + p + ':' + entry.name);
          add(imported, child, 'generated-module');
        } else fail('unresolved symbol:' + resolved + ':' + entry.name);
      }
    }
    return {relative_path: p, sha256: artifact.sha256, bindings: surface.bindings, imports};
  });
  return modules;
}

/** Node projection uses import closure, including empty package initializers. */
export function selectPythonModuleClosure(modules: ReturnType<typeof resolvePythonModules>, roots: readonly string[]) {
  assertInterfaceData(modules); assertInterfaceData(roots);
  const byPath = new Map(modules.map(m => [m.relative_path, m]));
  if (!roots.length || new Set(roots).size !== roots.length || roots.some(p => !byPath.has(p))) fail('exact existing module roots required');
  const selected = new Set(roots), pending = [...roots];
  while (pending.length) for (const i of byPath.get(pending.pop()!)!.imports) if (i.target_path !== null && !selected.has(i.target_path)) {
    if (!byPath.has(i.target_path)) fail('unresolved closure');
    selected.add(i.target_path); pending.push(i.target_path);
  }
  return modules.filter(m => selected.has(m.relative_path));
}
