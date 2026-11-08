import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import type {CompiledProjectGraph} from '../input/project-model.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertReconciledRustProjectPlan, type ReconciledRustProjectPlan} from '../generation/reconciled-rust-project.js';
import {freezeRustProject as freeze} from '../generation/reconciled-rust-selection.js';
import {verifyReconciledProject} from '../generation/reconciled-output.js';
import {assertReconciledOutputLayout} from '../generation/reconciled-output-layout.js';
import type {OutputLayout} from '../generation/output-layout.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';

export interface RustVerificationOptions {readonly cargo_executable: string; readonly temporary_parent?: string; readonly target_root?: string; readonly output_layout?: OutputLayout;}
export const RUST_NATIVE_VERIFICATION_CONTRACT_SHA256 = 'de2cbae502d34b857d2389614deb8cd0654473ab6ac089ae75ada5467e77d280';
function fail(reason: string): never {throw new TypeError('DS_RUST_VERIFICATION:' + reason);}
export function validateRustVerificationOptions(value: unknown): RustVerificationOptions {
  assertInterfaceData(value); if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('options');
  const row = value as Record<string, unknown>, allowed = ['cargo_executable', 'temporary_parent', 'target_root', 'output_layout']; if (Object.keys(row).some(key => !allowed.includes(key)) || !Object.hasOwn(row, 'cargo_executable')) fail('closed options');
  const cargo = row.cargo_executable; if (typeof cargo !== 'string' || !path.isAbsolute(cargo) || !fs.existsSync(cargo) || !fs.statSync(cargo).isFile()) fail('cargo executable');
  const parent = row.temporary_parent; if (parent !== undefined && (typeof parent !== 'string' || !path.isAbsolute(parent) || !fs.existsSync(parent) || !fs.statSync(parent).isDirectory() || fs.realpathSync(parent) !== parent)) fail('temporary parent');
  const target = row.target_root; if (target !== undefined && (typeof target !== 'string' || !path.isAbsolute(target) || path.resolve(target) !== target)) fail('target root');
  assertReconciledOutputLayout(row.output_layout); if (row.output_layout !== undefined && target === undefined) fail('output layout requires target');
  return freeze({cargo_executable: cargo, ...(parent === undefined ? {} : {temporary_parent: parent}), ...(target === undefined ? {} : {target_root: target}), ...(row.output_layout === undefined ? {} : {output_layout: row.output_layout as OutputLayout})});
}
function run(command: string, args: readonly string[], cwd: string, target: string) {
  const result = spawnSync(command, [...args], {cwd, encoding: 'utf8', timeout: 120000, env: {...process.env, CARGO_TARGET_DIR: target}});
  if (result.error || result.status !== 0) fail(`Cargo rejected generated crate:${result.error?.message ?? (result.stderr || result.stdout || result.status)}`); return (result.stdout || result.stderr).trim();
}
function inspect(plan: ReconciledRustProjectPlan) {
  if (plan.metatype_accounting.length !== 13 || plan.metatype_accounting.some(row => row.count < 1) || plan.modules.length !== plan.node_selectors.length) fail('incomplete 13-of-13 accounting');
  const artifacts = new Map(plan.artifacts.map(row => [row.relative_path, row])); if (artifacts.size !== plan.artifacts.length) fail('duplicate artifact');
  for (const row of plan.artifacts) if (row.size_bytes !== Buffer.byteLength(row.content) || row.sha256 !== sha256(row.content)) fail('artifact digest:' + row.relative_path);
  for (const module of plan.modules) {const source = artifacts.get(module.relative_path)?.content; if (!source || !source.includes(JSON.stringify(module.selector))) fail('module selector binding:' + module.selector);}
  const rust = plan.artifacts.filter(row => row.relative_path.endsWith('.rs')); if (rust.some(row => /\bunsafe\b|todo!\s*\(|unimplemented!\s*\(|std::(?:fs|net|process)::/.test(row.content))) fail('forbidden Rust form');
  const roleMods = plan.artifacts.filter(row => row.relative_path.endsWith('/mod.rs'));
  for (const mod of roleMods) {
    const prefix = mod.relative_path.slice(0, -'mod.rs'.length), directFiles = plan.artifacts.filter(row => row.relative_path.startsWith(prefix) && row.relative_path.endsWith('.rs') && row.relative_path !== mod.relative_path && !row.relative_path.slice(prefix.length).includes('/')).map(row => path.basename(row.relative_path, '.rs'));
    const directDirectories = plan.artifacts.filter(row => row.relative_path.startsWith(prefix) && row.relative_path.endsWith('/mod.rs') && row.relative_path !== mod.relative_path && row.relative_path.slice(prefix.length).split('/').length === 2).map(row => row.relative_path.slice(prefix.length).split('/')[0]!);
    const expected = [...new Set([...directFiles, ...directDirectories])].sort().map(name => `pub mod ${name};`), declared = mod.content.trim().split('\n').filter(Boolean).sort(); if (canonicalJson(declared) !== canonicalJson(expected)) fail('module wiring:' + mod.relative_path);
  }
  const manifest = artifacts.get(plan.cargo.manifest_path)?.content; if (!manifest || /\[(?:dev-|build-)?dependencies\]/.test(manifest) || plan.cargo.dependency_count !== 0) fail('dependency-free manifest');
  return freeze({metatype_count: 13, node_count: plan.node_selectors.length, module_count: plan.modules.length, rust_source_count: rust.length, module_index_count: roleMods.length, dependency_count: 0});
}

export function executeReconciledRustVerification(graph: CompiledProjectGraph, plan: ReconciledRustProjectPlan, rawOptions: unknown) {
  assertReconciledRustProjectPlan(plan); const options = validateRustVerificationOptions(rawOptions);
  if (sha256(getReconciledSource('rust_native_verification')) !== RUST_NATIVE_VERIFICATION_CONTRACT_SHA256) fail('definition drift');
  if (canonicalJson(graph.source_manifest) !== canonicalJson(plan.semantic_sources)) fail('source identity changed');
  const shape = inspect(plan), output = options.target_root === undefined ? null : verifyReconciledProject(plan, options.target_root, null, options.output_layout);
  if (output?.result === 'fail') fail('published output differs');
  const parent = options.temporary_parent ?? os.tmpdir(), workspace = fs.mkdtempSync(path.join(parent, 'domainspec-rust-verify-')); let cleaned = false;
  try {
    for (const artifact of plan.artifacts) {const file = path.join(workspace, artifact.relative_path); if (!file.startsWith(workspace + path.sep)) fail('artifact escape'); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content, {flag: 'wx'});}
    const crate = path.join(workspace, path.dirname(plan.cargo.manifest_path)), target = path.join(workspace, '.cargo-target');
    const version = run(options.cargo_executable, ['--version'], crate, target), metadataText = run(options.cargo_executable, ['metadata', '--offline', '--locked', '--no-deps', '--format-version', '1'], crate, target), metadata = JSON.parse(metadataText);
    if (metadata.packages?.length !== 1 || metadata.packages[0]?.name !== plan.cargo.package_name || metadata.packages[0]?.dependencies?.length !== 0) fail('Cargo metadata mismatch');
    run(options.cargo_executable, ['check', '--offline', '--locked', '--quiet'], crate, target);
    fs.rmSync(workspace, {recursive: true, force: true}); cleaned = !fs.existsSync(workspace); if (!cleaned) fail('workspace cleanup');
    return freeze({schema_version: 'domainspec.rust-native-verification/v1-candidate' as const, result: 'pass' as const, project_id: plan.certificate.project_id, source_manifest_sha256: plan.semantic_sources.manifest_sha256, project_plan_sha256: plan.plan_sha256, contract_sha256: RUST_NATIVE_VERIFICATION_CONTRACT_SHA256, cargo_version: version, checks: [...(output === null ? [] : [{id: 'exact-output-currentness', result: 'pass' as const, evidence: {view_sha256: output.view_sha256}}]), {id: 'source-and-module-shape', result: 'pass' as const, evidence: shape}, {id: 'cargo-metadata', result: 'pass' as const, evidence: {package_count: 1, dependency_count: 0}}, {id: 'cargo-check', result: 'pass' as const, evidence: {offline: true, locked: true}}], temporary_workspace: 'removed' as const, authority_effect: 'none' as const});
  } finally {if (!cleaned && fs.existsSync(workspace)) fs.rmSync(workspace, {recursive: true, force: true});}
}
