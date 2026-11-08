import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {domainSpecRoot} from '../helpers/reconciled-commerce-corpus.ts';

const reconciliationRoot = path.join(domainSpecRoot, 'development/reconciliation-v1/profile-compiler-reconciliation');
const evidenceRoot = path.join(reconciliationRoot, 'evidence/r16-installation-package');
const manifest = JSON.parse(fs.readFileSync(path.join(evidenceRoot, 'manifest.json'), 'utf8'));
const tarball = path.join(evidenceRoot, manifest.package.filename);

test('R16 retained installation archive matches its exact closed payload manifest', () => {
  const bytes = fs.readFileSync(tarball);
  assert.equal(bytes.length, manifest.package.size_bytes);
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), manifest.package.sha256);
  const entries = execFileSync('tar', ['-tzf', tarball], {encoding: 'utf8'}).trimEnd().split('\n');
  assert.equal(entries.length, manifest.package.entry_count);
  assert.equal(new Set(entries).size, entries.length);
  assert.equal(entries.every(entry => entry.startsWith('package/') && !entry.includes('/../') && !entry.startsWith('/')), true);
  for (const required of [
    'package/dist/index.js',
    'package/dist/index.d.ts',
    'package/dist/cli/main.js',
    'package/dist/generation/selected-reconciled-project.js',
    'package/dist/generation/reconciled-python-project.js',
    'package/dist/generation/reconciled-rust-project.js',
    'package/dist/typed-backend/policy-compatibility.js',
    'package/dist/typed-backend/state-machine-compatibility.js',
    'package/dist/input/workflow-migration.js',
    'package/USER-GUIDE.md',
    'package/examples/reconciled-commerce/source/project.json',
    'package/examples/reconciled-commerce/selections/typescript.json',
    'package/examples/reconciled-commerce/selections/python.json',
    'package/examples/reconciled-commerce/selections/rust.json',
    'package/lean/DomainSpecMetaTypeKernel.lean',
    'package/package.json',
  ]) assert.equal(entries.includes(required), true, required);
  assert.equal(entries.some(entry => entry.startsWith('package/src/') || entry.startsWith('package/test/')), false);
});

test('R16 qualification is current, non-authoritative and closes every package run', () => {
  const qualification = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R16-QUALIFICATION.json'), 'utf8'));
  assert.equal(qualification.result, 'pass');
  assert.equal(qualification.authority_effect, 'none');
  assert.equal(qualification.artifact.sha256, manifest.package.sha256);
  assert.equal(qualification.artifact.size_bytes, manifest.package.size_bytes);
  assert.equal(qualification.artifact.entry_count, manifest.package.entry_count);
  assert.equal(qualification.build.package_byte_equivalent, true);
  assert.equal(qualification.denominators.package_runs, qualification.denominators.package_runs_passed);
  assert.equal(qualification.denominators.clean_install_runs, qualification.denominators.clean_install_runs_passed);
  assert.equal(qualification.publication, false);
  assert.equal(qualification.admission, false);
  assert.equal(qualification.release, false);
  assert.equal('open_questions' in qualification, false);
});
