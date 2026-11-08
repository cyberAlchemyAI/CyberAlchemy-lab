import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledRustProject} from '../../src/generation/reconciled-rust-project.ts';
import {RECONCILED_RUST_COMPILATION_VERSION, RECONCILED_RUST_PROFILE} from '../../src/generation/reconciled-rust-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {executeReconciledRustVerification, RUST_NATIVE_VERIFICATION_CONTRACT_SHA256, validateRustVerificationOptions} from '../../src/verification/reconciled-rust-native.ts';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
function fixture(t: any) {const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source), selection = {schema_version: RECONCILED_RUST_COMPILATION_VERSION, profile_id: RECONCILED_RUST_PROFILE, language: 'rust' as const, module_root: 'generated/domain', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: source.factories, operations: source.operations, workflows: source.workflows}, plan = planCompiledReconciledRustProject(graph, selection); return {...source, graph, selection, plan};}

test('Rust native verifier independently inspects and compiles the complete crate then removes its workspace', t => {
  const f = fixture(t), result = executeReconciledRustVerification(f.graph, f.plan, {cargo_executable: cargo, temporary_parent: f.temp}); assert.equal(result.result, 'pass'); assert.equal(result.contract_sha256, RUST_NATIVE_VERIFICATION_CONTRACT_SHA256); assert.equal(result.checks.length, 3); assert.equal(result.checks[0]!.evidence.metatype_count, 13); assert.equal(result.temporary_workspace, 'removed'); assert.deepEqual(fs.readdirSync(f.temp).filter(name => name.startsWith('domainspec-rust-verify-')), []);
});

test('Rust native verifier rejects forged plans, invalid options and source mismatch before accepting evidence', t => {
  const f = fixture(t); assert.throws(() => executeReconciledRustVerification(f.graph, structuredClone(f.plan) as any, {cargo_executable: cargo})); assert.throws(() => validateRustVerificationOptions({cargo_executable: 'cargo'})); assert.throws(() => validateRustVerificationOptions({cargo_executable: cargo, extra: true})); const other = structuredClone(f.graph); other.source_manifest.manifest_sha256 = '0'.repeat(64); assert.throws(() => executeReconciledRustVerification(other, f.plan, {cargo_executable: cargo}));
});

test('Rust native verifier cleans its private workspace when Cargo fails', t => {
  const f = fixture(t); assert.throws(() => executeReconciledRustVerification(f.graph, f.plan, {cargo_executable: '/usr/bin/false', temporary_parent: f.temp}), /Cargo rejected/); assert.deepEqual(fs.readdirSync(f.temp).filter(name => name.startsWith('domainspec-rust-verify-')), []);
});
