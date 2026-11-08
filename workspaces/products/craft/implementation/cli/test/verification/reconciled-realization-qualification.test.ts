import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {
  CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256,
} from '../../src/verification/reconciled-realization-matrix.ts';
import {
  getReconciledSource,
  getReconciledSourceCapsule,
  RECONCILED_SOURCE_CAPSULE_SHA256,
} from '../../src/generation/reconciled-sources.ts';
import {sha256} from '../../src/input/source-manifest.ts';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../../');
const qualificationPath = path.join(
  projectRoot,
  'development/reconciliation-v1/profile-compiler-reconciliation/evidence/r12-realization-matrix/qualification.json',
);
const languages = ['typescript', 'python', 'rust'] as const;
const metatypes = [
  'Entity',
  'Value Object',
  'Enum',
  'Rule',
  'Calculation',
  'Query',
  'Mapping',
  'Policy',
  'Event',
  'Operation',
  'State Machine',
  'Workflow',
  'Interface',
] as const;
const observations = [
  'native-compile-or-import',
  'independent-native-surface',
  'normalized-positive-behavior',
  'normalized-hostile-behavior',
  'language-specific-negative-control',
] as const;

type Qualification = {
  schema_version: string;
  date: string;
  definition_sha256: string;
  source_capsule_sha256: string;
  denominators: {
    metatypes: number;
    languages: number;
    cells: number;
    passed_cells: number;
    missing_cells: number;
    skipped_cells: number;
  };
  fresh_runs: Array<{
    language: string;
    tests: number;
    passed: number;
    failed: number;
    skipped: number;
  }>;
  preserved_failures: Array<{run: string; tests: number; passed: number; failed: number; reason: string; resolution: string}>;
  required_evidence: string[];
  cells: Array<{cell: string; family: string; tests: string[]; result: string}>;
  normalization_guards: string[];
  result: string;
  claim_scope: string;
  authority_effect: string;
};

function loadQualification(): Qualification {
  return JSON.parse(fs.readFileSync(qualificationPath, 'utf8')) as Qualification;
}

test('R12 qualification is an exact 13 by 3 passed matrix bound to selected compiler sources', () => {
  const value = loadQualification();
  assert.deepEqual(Object.keys(value).sort(), [
    'authority_effect',
    'cells',
    'claim_scope',
    'date',
    'definition_sha256',
    'denominators',
    'fresh_runs',
    'normalization_guards',
    'preserved_failures',
    'required_evidence',
    'result',
    'schema_version',
    'source_capsule_sha256',
  ].sort());
  assert.equal(value.schema_version, 'domainspec.cross-language-realization-qualification/v1-candidate');
  assert.equal(value.definition_sha256, CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256);
  assert.equal(sha256(getReconciledSource('realization_matrix')), CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256);
  assert.equal(value.source_capsule_sha256, RECONCILED_SOURCE_CAPSULE_SHA256);
  assert.equal(getReconciledSourceCapsule().capsule_sha256, RECONCILED_SOURCE_CAPSULE_SHA256);
  assert.deepEqual(value.denominators, {
    metatypes: 13,
    languages: 3,
    cells: 39,
    passed_cells: 39,
    missing_cells: 0,
    skipped_cells: 0,
  });
  assert.deepEqual(value.required_evidence, observations);
  assert.equal(value.result, 'pass');
  assert.equal(value.authority_effect, 'none');
  assert.match(value.claim_scope, /R13 and R14/);

  const expectedCells = metatypes.flatMap(metatype => languages.map(language => `${metatype}/${language}`));
  assert.deepEqual(value.cells.map(row => row.cell).sort(), expectedCells.sort());
  assert.equal(new Set(value.cells.map(row => row.cell)).size, 39);
  for (const row of value.cells) {
    assert.deepEqual(Object.keys(row).sort(), ['cell', 'family', 'result', 'tests']);
    assert.equal(row.result, 'pass', row.cell);
    assert.match(row.family, /^[a-z0-9]+(?:-[a-z0-9]+)*$/, row.cell);
    assert.ok(row.tests.length > 0, row.cell);
    for (const reference of row.tests) {
      assert.ok(reference.startsWith('impl/cli/test/'), `${row.cell}: ${reference}`);
      assert.equal(reference, path.posix.normalize(reference), `${row.cell}: ${reference}`);
      const absolute = path.join(projectRoot, reference);
      assert.ok(fs.statSync(absolute).isFile(), `${row.cell}: ${reference}`);
      assert.match(fs.readFileSync(absolute, 'utf8'), /\btest\s*\(/, `${row.cell}: ${reference}`);
    }
  }
  for (const metatype of metatypes) {
    const rows = value.cells.filter(row => row.cell.startsWith(`${metatype}/`));
    assert.equal(rows.length, 3, metatype);
    assert.equal(new Set(rows.map(row => row.family)).size, 1, metatype);
  }
});

test('R12 run accounting has no silent failure or skip and preserves the repaired environment failure', () => {
  const value = loadQualification();
  assert.deepEqual(value.fresh_runs.map(run => run.language), languages);
  assert.deepEqual(value.fresh_runs.map(run => [run.tests, run.passed, run.failed, run.skipped]), [
    [276, 276, 0, 0],
    [140, 140, 0, 0],
    [62, 62, 0, 0],
  ]);
  for (const run of value.fresh_runs) {
    assert.equal(run.tests, run.passed + run.failed + run.skipped, run.language);
    assert.ok(run.tests > 0, run.language);
  }
  assert.equal(value.preserved_failures.length, 1);
  assert.deepEqual(
    [value.preserved_failures[0]?.run, value.preserved_failures[0]?.tests, value.preserved_failures[0]?.passed, value.preserved_failures[0]?.failed],
    ['python-initial', 140, 138, 2],
  );
  assert.match(value.preserved_failures[0]!.reason, /DOMAINSPEC_LEAN was absent/);
  assert.match(value.preserved_failures[0]!.resolution, /Reran the entire unchanged 140-test lane/);
  assert.ok(value.normalization_guards.some(guard => /Lists preserve order and duplicates/.test(guard)));
  assert.ok(value.normalization_guards.some(guard => /Entity identity and Value Object complete equality remain distinct/.test(guard)));
  assert.ok(value.normalization_guards.some(guard => /Workflow step occurrence and Operation identity remain distinct/.test(guard)));
});
