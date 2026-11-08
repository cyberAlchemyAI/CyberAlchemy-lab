import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {domainSpecRoot} from '../helpers/reconciled-commerce-corpus.ts';

const cliRoot = path.join(domainSpecRoot, 'impl/cli');
const reconciliationRoot = path.join(domainSpecRoot, 'development/reconciliation-v1/profile-compiler-reconciliation');
const review = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R18-CANDIDATE-REVIEW.json'), 'utf8'));
const hash = (file: string) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

test('R18 review pack binds one exact package and all R01-R17 completion evidence', () => {
  const plan = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'remaining-work-plan.json'), 'utf8'));
  const predecessors = plan.tasks.filter((row: any) => row.id !== 'R18');
  assert.equal(predecessors.length, 17);
  assert.ok(predecessors.every((row: any) => ['complete', 'completed'].includes(row.status)));
  assert.deepEqual(review.completion_evidence.map((row: any) => row.task), predecessors.map((row: any) => row.id));
  for (const row of review.completion_evidence) {
    const planned = predecessors.find((candidate: any) => candidate.id === row.task);
    assert.equal(row.path, planned.evidence_ref, row.task);
    assert.equal(hash(path.join(reconciliationRoot, row.path)), row.sha256, row.task);
  }

  const candidatePaths: Record<string, string> = {
    package_json_sha256: 'package.json',
    package_lock_sha256: 'package-lock.json',
    public_api_source_sha256: 'src/index.ts',
    cli_help_source_sha256: 'src/product/capabilities.ts',
    compiled_public_api_sha256: 'dist/index.js',
    compiled_cli_sha256: 'dist/cli/main.js',
    user_guide_sha256: 'USER-GUIDE.md',
  };
  for (const [field, relative] of Object.entries(candidatePaths)) assert.equal(hash(path.join(cliRoot, relative)), review.candidate[field], field);
  const archive = path.join(reconciliationRoot, review.candidate.archive);
  assert.equal(fs.statSync(archive).size, review.candidate.size_bytes);
  assert.equal(hash(archive), review.candidate.archive_sha256);
  const entries = execFileSync('tar', ['-tzf', archive], {encoding: 'utf8'}).trimEnd().split('\n');
  assert.equal(entries.length, review.candidate.entry_count);
  assert.equal(new Set(entries).size, entries.length);
  assert.ok(entries.every(entry => entry.startsWith('package/') && !entry.includes('/../') && !path.isAbsolute(entry)));
  const canonicalPaths = `${entries.slice().sort().join('\n')}\n`;
  assert.equal(crypto.createHash('sha256').update(canonicalPaths).digest('hex'), review.candidate.sorted_entry_paths_sha256);
});

test('R18 joined denominators are closed by current machine-readable qualifications', () => {
  for (const row of review.current_qualification_inputs) assert.equal(hash(path.join(reconciliationRoot, row.path)), row.sha256, row.path);
  for (const row of review.final_regression_inputs) assert.equal(hash(path.join(domainSpecRoot, row.path)), row.sha256, row.path);
  const r12 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'evidence/r12-realization-matrix/qualification.json'), 'utf8'));
  const r13 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R13-QUALIFICATION.json'), 'utf8'));
  const r14 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R14-QUALIFICATION.json'), 'utf8'));
  const r15 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R15-QUALIFICATION.json'), 'utf8'));
  const r16 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R16-QUALIFICATION.json'), 'utf8'));
  const r17 = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R17-QUALIFICATION.json'), 'utf8'));
  assert.deepEqual([r12, r13, r14, r15, r16, r17].map(row => row.result), Array(6).fill('pass'));
  assert.deepEqual(r12.denominators, {metatypes: 13, languages: 3, cells: 39, passed_cells: 39, missing_cells: 0, skipped_cells: 0});
  assert.deepEqual(r13.denominators, {scenarios: 22, passed: 22, failed: 0, missing: 0, languages: 3, metatypes: 13});
  assert.equal(r14.denominators.relationships, 17);
  assert.equal(r14.denominators.positive_witnesses_passed, 44);
  assert.equal(r14.denominators.semantic_mutants_killed, 44);
  assert.equal(r15.denominators.cases_passed, 15);
  assert.equal(r15.denominators.public_entry_points, 7);
  assert.equal(r15.denominators.migrations_passed, 3);
  assert.equal(r16.denominators.package_runs_passed, 2);
  assert.equal(r16.denominators.clean_install_runs_passed, 2);
  assert.equal(r17.denominators.languages_executed, 3);
  assert.equal(r17.denominators.negative_controls_killed, 1);
  assert.equal(review.joined_requirements.length, 13);
  assert.equal(review.final_focused_regression.tests, 20);
  assert.equal(review.final_focused_regression.passed, 20);
  assert.equal(review.final_focused_regression.failed, 0);
});

test('R18 preserves residuals and the authority boundary without an unresolved product decision', () => {
  assert.equal(review.result, 'pass');
  assert.equal(review.authority_effect, 'none');
  assert.equal(review.candidate_status, 'technically-prepared-for-separately-owned-review');
  assert.equal(review.review_status, 'not-performed');
  assert.deepEqual(review.important_decisions_required, []);
  assert.ok(review.residuals.length >= 5);
  assert.deepEqual(
    [review.default_cutover, review.publication, review.admission, review.release, review.deployment],
    [false, false, false, false, false],
  );
});
