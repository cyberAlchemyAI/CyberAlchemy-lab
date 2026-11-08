import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import * as api from '../../src/index.ts';
import {migrateTypedPolicyV1} from '../../src/typed-backend/policy-compatibility.ts';
import {migrateLegacyStateMachine} from '../../src/typed-backend/state-machine-compatibility.ts';
import {planWorkflowOccurrenceMigration} from '../../src/input/workflow-migration.ts';
import {loadCommerceCorpus, commerceSourceRoot, domainSpecRoot} from '../helpers/reconciled-commerce-corpus.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';

const reconciliationRoot = path.join(domainSpecRoot, 'development/reconciliation-v1/profile-compiler-reconciliation');
const matrixPath = path.join(reconciliationRoot, 'R15-COMPATIBILITY-MATRIX.json');

test('R15 compatibility matrix is closed, exact and points only to present evidence files', () => {
  const matrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));
  assert.equal(matrix.authority_effect, 'none');
  assert.equal(matrix.status, 'specified-current');
  assert.equal(matrix.publication, false);
  assert.equal(matrix.admission, false);
  assert.equal('open_questions' in matrix, false);
  assert.deepEqual(matrix.dimensions.languages, ['typescript', 'python', 'rust']);
  assert.deepEqual(matrix.dimensions.selection_modes, ['legacy-omitted', 'reconciled-explicit']);
  assert.deepEqual(matrix.dimensions.output_views, ['legacy-default', 'reconciled-flat', 'domainspec.application-layout/v1']);
  assert.equal(matrix.cases.length, 15);
  assert.deepEqual(matrix.cases.map((row: any) => row.id), Array.from({length: 15}, (_, index) => `R15-C${String(index + 1).padStart(2, '0')}`));
  for (const row of matrix.cases) {
    assert.equal(row.expected, 'pass', row.id);
    assert.ok(row.evidence.length > 0, row.id);
    for (const reference of row.evidence) {
      const relative = reference.split('#')[0];
      assert.equal(fs.existsSync(path.join(domainSpecRoot, relative)), true, `${row.id}:${relative}`);
    }
  }
});

test('R15 explicit migrations are stable root APIs rather than internal-only helpers', () => {
  assert.equal(api.migrateTypedPolicyV1, migrateTypedPolicyV1);
  assert.equal(api.migrateLegacyStateMachine, migrateLegacyStateMachine);
  assert.equal(api.planWorkflowOccurrenceMigration, planWorkflowOccurrenceMigration);
});

test('R15 all selected languages remain explicit, fail closed, and leave authored source unchanged', () => {
  const before = loadCompiledProjectGraph(commerceSourceRoot).source_manifest.manifest_sha256;
  const corpus = loadCommerceCorpus();
  for (const language of ['typescript', 'python', 'rust'] as const) {
    const selection: any = corpus.selections[language];
    const decoded: any = api.decodeSelectedReconciledCompilation(selection);
    assert.equal(decoded.language, language);
    assert.equal(corpus.plans[language].selection.language, language);
    for (const invalid of [
      {...selection, schema_version: 'domainspec.reconciled-compilation/future'},
      {...selection, profile_id: 'domainspec.unknown-profile/v1'},
      {...selection, language: language === 'typescript' ? 'python' : 'typescript'},
      {...selection, layout_version: 'domainspec.unknown-layout/v1'},
    ]) {
      assert.throws(() => api.planSelectedReconciledProject('/source-must-not-be-read', invalid));
    }
  }
  const after = loadCompiledProjectGraph(commerceSourceRoot).source_manifest.manifest_sha256;
  assert.equal(after, before);
});

test('R15 qualification closes the compatibility denominator without default cutover', () => {
  const matrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));
  const qualification = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R15-QUALIFICATION.json'), 'utf8'));
  assert.equal(qualification.result, 'pass');
  assert.equal(qualification.authority_effect, 'none');
  assert.equal(qualification.default_cutover, false);
  assert.equal(qualification.source_rewrites, 0);
  assert.equal(qualification.publication, false);
  assert.equal(qualification.admission, false);
  assert.equal('open_questions' in qualification, false);
  assert.equal(qualification.denominators.cases, matrix.cases.length);
  assert.equal(qualification.denominators.cases_passed, matrix.cases.length);
  assert.deepEqual(qualification.dimensions, matrix.dimensions);
  assert.deepEqual(qualification.cases.map((row: any) => row.id), matrix.cases.map((row: any) => row.id));
  assert.equal(qualification.cases.every((row: any) => row.result === 'pass' && row.evidence.length > 0), true);
});
