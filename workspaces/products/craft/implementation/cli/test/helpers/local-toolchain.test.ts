import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {alchToolchain, assertPinnedVersion, checkoutRoot, nodeExecutable, npmCli, repositoryToolchain, typeScriptToolchain} from './local-toolchain.ts';

test('host test tools resolve from this checkout and the pinned native Node installation', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(checkoutRoot, 'craft/toolchains/node-typescript/toolchain.json'), 'utf8'));
  assert.equal(nodeExecutable(), process.execPath);
  assert.equal(repositoryToolchain(), path.join(checkoutRoot, 'tools/toolchain/run'));
  assert.ok(alchToolchain().startsWith(checkoutRoot + path.sep));
  const typescript = typeScriptToolchain();
  assert.equal(execFileSync(nodeExecutable(), [typescript.compiler, '--version'], {encoding: 'utf8'}).trim(), `Version ${manifest.typescript}`);
  assert.equal(execFileSync(nodeExecutable(), [npmCli(), '--version'], {encoding: 'utf8'}).trim(), manifest.package_managers.npm);
  assert.ok(fs.existsSync(path.join(typescript.typeRoots, 'node/package.json')));
});

test('tool versions fail closed on drift rather than accepting another installed version', () => {
  assert.doesNotThrow(() => assertPinnedVersion('fixture', '7.0.2', '7.0.2'));
  assert.throws(() => assertPinnedVersion('fixture', '7.0.1', '7.0.2'), /DS_TEST_TOOL_VERSION_MISMATCH/);
});

test('missing checkout tools and installed packages reject without a PATH or historical-directory fallback', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-test-tools-missing-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  assert.throws(() => repositoryToolchain(root), /DS_TEST_TOOL_MISSING/);
  assert.throws(() => alchToolchain(root), /DS_TEST_TOOL_MISSING/);
  assert.throws(() => typeScriptToolchain(root), /Cannot find module/);
});

test('a wrong installed compiler package is rejected before its executable can run', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-test-tools-drift-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  const typescript = path.join(root, 'node_modules/typescript');
  fs.mkdirSync(typescript, {recursive: true});
  fs.writeFileSync(path.join(typescript, 'package.json'), JSON.stringify({name: 'typescript', version: '0.0.0', bin: {tsc: './must-not-run.js'}}));
  assert.throws(() => typeScriptToolchain(root), /DS_TEST_TOOL_VERSION_MISMATCH/);
});
