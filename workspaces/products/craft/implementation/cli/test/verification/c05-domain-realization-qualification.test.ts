import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {RECONCILED_SOURCE_CAPSULE_SHA256} from '../../src/generation/reconciled-sources.ts';

const cli = path.resolve(import.meta.dirname, '../..');
const project = path.resolve(cli, '../..');
const qualificationPath = path.join(project, 'development/authoring-to-runtime-v1/evidence/c05-domain-realization/qualification.json');
const historicalPath = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/evidence/r12-realization-matrix/qualification.json');

function readJson(file: string): any {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function sha256(file: string): string {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function validate(value: any): void {
  assert.equal(value.schema_version, 'alchlang.c05-domain-realization-qualification/v1-candidate');
  assert.equal(value.date, '2026-09-20');
  assert.equal(value.task, 'C05');
  assert.equal(value.result, 'pass');
  assert.equal(value.authority_effect, 'none');
  assert.deepEqual(value.denominators, {
    metatypes: 13,
    languages: 3,
    cells: 39,
    passed_cells: 39,
    failed_cells: 0,
    missing_cells: 0,
    skipped_cells: 0,
  });

  assert.equal(value.bindings.source_capsule_sha256, RECONCILED_SOURCE_CAPSULE_SHA256);
  assert.equal(
    sha256(path.join(project, value.bindings.configuration_path)),
    value.bindings.configuration_sha256,
  );
  assert.equal(
    sha256(path.join(project, value.bindings.matrix_definition_path)),
    value.bindings.matrix_definition_sha256,
  );
  assert.match(value.bindings.node_toolchain_image_sha256, /^sha256:[0-9a-f]{64}$/u);

  const historical = readJson(historicalPath);
  assert.deepEqual(value.cells, historical.cells, 'current C05 cells retain the reviewed 13 by 3 obligation map');
  assert.equal(value.cells.length, 39);
  assert.equal(new Set(value.cells.map((row: any) => row.cell)).size, 39);
  assert.equal(new Set(value.cells.map((row: any) => row.cell.split('/').at(-1))).size, 3);
  assert.equal(new Set(value.cells.map((row: any) => row.cell.slice(0, row.cell.lastIndexOf('/')))).size, 13);
  assert.ok(value.cells.every((row: any) => row.result === 'pass'));
  const testPaths = [...new Set(value.cells.flatMap((row: any) => row.tests))].sort();
  assert.equal(testPaths.length, 52);
  for (const testPath of testPaths) assert.equal(fs.statSync(path.join(project, testPath)).isFile(), true, testPath);

  assert.deepEqual(
    {
      test_files: value.exact_domain_run.test_files,
      tests: value.exact_domain_run.tests,
      passed: value.exact_domain_run.passed,
      failed: value.exact_domain_run.failed,
      cancelled: value.exact_domain_run.cancelled,
      skipped: value.exact_domain_run.skipped,
      todo: value.exact_domain_run.todo,
      tap_summary_validation: value.exact_domain_run.tap_summary_validation,
    },
    {test_files: 52, tests: 399, passed: 399, failed: 0, cancelled: 0, skipped: 0, todo: 0, tap_summary_validation: 'pass'},
  );
  assert.equal(value.exact_domain_run.tap_sha256, 'd1a314edb4955072466fd69d4ee5b544642751a7a270ee8f1a4a8965080189ff');
  assert.equal(value.exact_domain_run.wrapper_status_observed, 1);
  assert.equal(value.exact_domain_run.raw_tap_retained, false);
  assert.match(value.exact_domain_run.wrapper_observation, /not represented as a zero shell status/u);

  assert.deepEqual(value.focused_current_checks.realization_matrix, {
    path: 'impl/cli/test/verification/reconciled-realization-matrix.test.ts',
    tests: 3,
    passed: 3,
    failed: 0,
    skipped: 0,
    result: 'pass',
  });
  assert.deepEqual(
    {tests: value.focused_current_checks.rust_lane.tests, passed: value.focused_current_checks.rust_lane.passed, failed: value.focused_current_checks.rust_lane.failed, skipped: value.focused_current_checks.rust_lane.skipped, result: value.focused_current_checks.rust_lane.result},
    {tests: 68, passed: 68, failed: 0, skipped: 0, result: 'pass'},
  );

  const integrationPath = path.join(project, value.integration.qualification_path);
  assert.equal(sha256(integrationPath), value.integration.qualification_sha256);
  const integration = readJson(integrationPath);
  assert.deepEqual(
    {languages: value.integration.languages, passed: value.integration.passed, failed: value.integration.failed, skipped: value.integration.skipped},
    integration.denominators,
  );
  assert.equal(value.integration.normalized_semantic_sha256, integration.normalized_semantic_sha256);
  assert.equal(value.integration.byte_equality_required, false);
  assert.equal(integration.byte_equality_required, false);
  assert.deepEqual(value.integration.provider_observation_ceiling, integration.provider_observation_ceiling);
  for (const evidence of value.integration.runtime_evidence) {
    assert.equal(sha256(path.join(project, evidence.path)), evidence.sha256);
    const runtime = readJson(path.join(project, evidence.path));
    assert.equal(runtime.language, evidence.language);
    assert.equal(runtime.authority_effect, 'none');
  }

  assert.deepEqual(value.hard_stops, {
    missing_or_skipped_cell: false,
    byte_equality_used_as_semantic_proof: false,
    domain_parity_substituted_for_integration_parity: false,
  });
  assert.match(value.claim_ceiling, /does not prove durable PostgreSQL behavior/u);
  assert.ok(Array.isArray(value.open_questions) && value.open_questions.length > 0);
}

test('C05 qualification is current, complete across 39 cells and joined to three-target semantic parity', () => {
  validate(readJson(qualificationPath));
});

test('C05 qualification validator rejects missing cells, byte-equality substitution and stale integration evidence', () => {
  for (const mutate of [
    (value: any) => { value.cells.pop(); value.denominators.cells = 38; },
    (value: any) => { value.integration.byte_equality_required = true; },
    (value: any) => { value.integration.qualification_sha256 = '0'.repeat(64); },
  ]) {
    const changed = readJson(qualificationPath);
    mutate(changed);
    assert.throws(() => validate(changed));
  }
});
