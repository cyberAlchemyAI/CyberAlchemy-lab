import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {inventoryPythonModule} from '../../src/generation/python-module-surface.ts';
import {resolvePythonModules, selectPythonModuleClosure} from '../../src/generation/resolved-python-modules.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {renderPythonValueSupport} from '../../src/generation/configured-python-value-source.ts';
import {renderPythonFactSupport} from '../../src/generation/configured-python-fact-source.ts';
import {renderPythonFactorySupport} from '../../src/generation/configured-python-factory-source.ts';
import {renderPythonEventValues} from '../../src/generation/configured-python-event-values.ts';
import {renderPythonReferenceSupport} from '../../src/generation/configured-python-reference-source.ts';
import {PYTHON_WORKFLOW_SETTLEMENT} from '../../src/generation/python-workflow-settlement-source.ts';

const artifact = (relative_path: string, content = '') => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});
function fixture(root = 'outer/package_root') {
  const files = [artifact(root + '/runtime/values.py', 'from __future__ import annotations\nfrom typing import TypeVar as _TypeVar\nT = _TypeVar("T")\nvalue = 7\n'),
    artifact(root + '/runtime/extra.py', 'unused = 1\n'),
    artifact(root + '/feature/api.py', 'from ..runtime import values as _values\nfrom ..runtime.values import value as imported\nasync def run() -> int:\n    return imported\n'),
    artifact(root + '/feature/wrapper.py', 'from .api import run as execute\n')];
  for (const a of [...files]) {const parts = a.relative_path.split('/'); for (let i = 1; i < parts.length; i++) {const p = parts.slice(0, i).join('/') + '/__init__.py'; if (!files.some(f => f.relative_path === p)) files.push(artifact(p));}}
  return files;
}

test('Python surface distinguishes module bindings and imports from literals, comments and nested definitions', () => {
  const source = 'from __future__ import annotations\nimport enum as _enum\nfrom .values import ValueProtocol as _Value, part\ntext = "from missing import hidden"\nraw = r"import fake"\nblock = """\nfrom other import fake\n"""\n# import ignored\nclass Value:\n    field: int\n    def method(self):\n        local = 1\nasync def run():\n    return text\n';
  const surface = inventoryPythonModule(source);
  assert.deepEqual(surface.bindings, ['Value', '_Value', '_enum', 'annotations', 'block', 'part', 'raw', 'run', 'text']);
  assert.deepEqual(surface.imports.map(i => i.specifier), ['__future__', 'enum', '.values']);
  assert.deepEqual(surface.imports[2]!.names, [{name: 'ValueProtocol', local: '_Value'}, {name: 'part', local: 'part'}]);
  assert.deepEqual(inventoryPythonModule('unbound: int\nother == 1\nbound: int = 2\n').bindings, ['bound']);
  assert.deepEqual(inventoryPythonModule('create_factory, ValueComponent = provider()\n').bindings, ['ValueComponent', 'create_factory']);
  for (const bad of ['def f():\n    import os\n', 'from x import *\n', 'from x import (y)\n', 'import x; import y\n', 'if True: import x\n', 'from x import y,\n', 'import x as\n', 'x = f"{__import__(\'os\')}"\n', 'x = __import__("os")\n', 'x = eval("1")\n', 'x = "unterminated\n', 'x = ([)]\n', 'x = (1\n']) assert.throws(() => inventoryPythonModule(bad), /DS_PYTHON_MODULE_SURFACE/, bad);
});

test('native AST independently confirms inventory for six generated runtime families', () => {
  const sources = [renderPythonValueSupport(), renderPythonFactSupport(), renderPythonFactorySupport(), renderPythonEventValues(), renderPythonReferenceSupport(), PYTHON_WORKFLOW_SETTLEMENT];
  const observed = sources.map(source => ({source, surface: inventoryPythonModule(source)}));
  const script = `import ast, json, sys
for row in json.load(sys.stdin):
    tree = ast.parse(row['source'])
    bindings, imports = set(), []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bindings.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                assert isinstance(target, ast.Name)
                bindings.add(target.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bindings.add(alias.asname or alias.name.split('.')[0])
            if isinstance(node, ast.ImportFrom):
                imports.append(dict(specifier='.' * node.level + (node.module or ''), namespace=False, names=[dict(name=a.name, local=a.asname or a.name) for a in node.names]))
            else:
                imports.extend(dict(specifier=a.name, namespace=True, names=[dict(name=a.name, local=a.asname or a.name.split('.')[0])]) for a in node.names)
    assert sorted(bindings) == row['surface']['bindings'], (sorted(bindings), row['surface']['bindings'])
    assert imports == row['surface']['imports']
print('native inventory pass')
`;
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', '-c', script], {encoding: 'utf8', input: JSON.stringify(observed)});
  assert.equal(result.status, 0, result.stdout + result.stderr);
});

test('Python resolution preserves module versus symbol imports, aliases and package initializer closure', t => {
  const files = fixture(), modules = resolvePythonModules(files, 'outer/package_root');
  assert.deepEqual(resolvePythonModules([...files].reverse(), 'outer/package_root'), modules);
  const api = modules.find(m => m.relative_path.endsWith('/feature/api.py'))!;
  const selected = api.imports.filter(i => i.specifier.startsWith('..'));
  assert.deepEqual(selected.map(i => i.dependency), ['generated-module', 'generated-symbol']);
  assert.equal(selected[0]!.target_path, selected[1]!.target_path);
  const closure = selectPythonModuleClosure(modules, ['outer/package_root/feature/wrapper.py']);
  assert.equal(closure.some(m => m.relative_path.endsWith('/extra.py')), false);
  assert.equal(closure.some(m => m.relative_path === 'outer/__init__.py'), true);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-module-native-')); t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  for (const module of closure) {const a = files.find(a => a.relative_path === module.relative_path)!; const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const code = 'import sys, importlib, asyncio\nsys.path.insert(0, sys.argv[1])\nm = importlib.import_module("outer.package_root.feature.wrapper")\nassert asyncio.run(m.execute()) == 7\n';
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', '-c', code, root], {encoding: 'utf8'}); assert.equal(result.status, 0, result.stderr);
});

test('Python resolution rejects stale bytes, missing symbols, external imports and ambiguous or escaping packages', () => {
  const root = 'outer/package_root', files = fixture(root);
  const replace = (suffix: string, content: string) => files.map(a => a.relative_path.endsWith(suffix) ? artifact(a.relative_path, content) : a);
  for (const [input, pattern] of [
    [[...files, files[0]!], /duplicate/],
    [files.map((a, i) => i ? a : {...a, sha256: '0'.repeat(64)}), /content binding/],
    [files.filter(a => a.relative_path !== 'outer/__init__.py'), /missing initializer/],
    [replace('/feature/api.py', 'from ..runtime.values import missing\n'), /unresolved symbol/],
    [replace('/feature/api.py', 'from ..runtime import missing\n'), /unresolved package member/],
    [replace('/feature/api.py', 'from ..absent import missing\n'), /unresolved relative module/],
    [replace('/feature/api.py', 'from ....other import value\n'), /escapes/],
    [replace('/feature/api.py', 'import requests\n'), /unselected absolute import/],
    [replace('/feature/__init__.py', 'state = 1\n'), /nonempty initializer/],
    [[...files, artifact(root + '/runtime/values/__init__.py')], /ambiguous/],
    [[...files, artifact(root + '/feature/../outside.py')], /unsafe native path/],
    [[...files, artifact(root + '/runtime/Values.py')], /case-fold/],
  ] as const) assert.throws(() => resolvePythonModules(input, root), pattern);
  for (const bad of ['../root', '/absolute', 'typing', 'asyncio', 'bad-name']) assert.throws(() => resolvePythonModules(files, bad), /package root/);
  let effects = 0; const active = {...files[0]!}; Object.defineProperty(active, 'content', {enumerable: true, get() {effects++; return '';} });
  assert.throws(() => resolvePythonModules([active], root)); assert.equal(effects, 0);
  assert.throws(() => selectPythonModuleClosure(resolvePythonModules(files, root), ['unknown']), /module roots/);
});
