// Test-only host prerequisite resolution. Open questions: C4-CLI-HARNESS-REPAIR.v1.md.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';

export const checkoutRoot = path.resolve(import.meta.dirname, '../../../../../../..');
const cliRoot = path.resolve(import.meta.dirname, '../..');
const manifest = JSON.parse(fs.readFileSync(path.join(checkoutRoot, 'craft/toolchains/node-typescript/toolchain.json'), 'utf8'));

export function assertPinnedVersion(tool: string, observed: string, expected: string): void {
  if (observed !== expected) throw new Error(`DS_TEST_TOOL_VERSION_MISMATCH: ${tool}: ${observed} != ${expected}`);
}

function requiredFile(file: string): string {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`DS_TEST_TOOL_MISSING: ${file}`);
  return file;
}

export function nodeExecutable(): string {
  assertPinnedVersion('node', process.versions.node, manifest.node.version);
  return requiredFile(process.execPath);
}

export function repositoryToolchain(root = checkoutRoot): string {
  const launcher = requiredFile(path.join(root, 'tools/toolchain/run'));
  fs.accessSync(launcher, fs.constants.X_OK);
  return launcher;
}

export function alchToolchain(root = checkoutRoot): string {
  return requiredFile(path.join(root, 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/run-toolchain.mjs'));
}

export function typeScriptToolchain(packageRoot = cliRoot): {compiler: string; typeRoots: string} {
  nodeExecutable();
  const require = createRequire(path.join(packageRoot, 'package.json'));
  const packageFile = require.resolve('typescript/package.json');
  const installed = JSON.parse(fs.readFileSync(packageFile, 'utf8'));
  if (installed.name !== 'typescript') throw new Error('DS_TEST_TOOL_PACKAGE_MISMATCH: typescript');
  assertPinnedVersion('typescript', installed.version, manifest.typescript);
  if (typeof installed.bin?.tsc !== 'string') throw new Error('DS_TEST_TOOL_BIN_MISSING: tsc');
  const compiler = requiredFile(path.resolve(path.dirname(packageFile), installed.bin.tsc));
  const nodeTypes = require.resolve('@types/node/package.json');
  return {compiler, typeRoots: path.dirname(path.dirname(requiredFile(nodeTypes)))};
}

export function npmCli(): string {
  const root = path.resolve(path.dirname(nodeExecutable()), '../lib/node_modules/npm');
  const installed = JSON.parse(fs.readFileSync(requiredFile(path.join(root, 'package.json')), 'utf8'));
  if (installed.name !== 'npm') throw new Error('DS_TEST_TOOL_PACKAGE_MISMATCH: npm');
  assertPinnedVersion('npm', installed.version, manifest.package_managers.npm);
  return requiredFile(path.join(root, 'bin/npm-cli.js'));
}
