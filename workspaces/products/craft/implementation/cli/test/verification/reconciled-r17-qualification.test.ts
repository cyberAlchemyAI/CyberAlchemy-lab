import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {domainSpecRoot} from '../helpers/reconciled-commerce-corpus.ts';

const cliRoot = path.join(domainSpecRoot, 'impl/cli');
const reconciliationRoot = path.join(domainSpecRoot, 'development/reconciliation-v1/profile-compiler-reconciliation');
const qualification = JSON.parse(fs.readFileSync(path.join(reconciliationRoot, 'R17-QUALIFICATION.json'), 'utf8'));
const hash = (file: string) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

test('R17 qualification is exact, closed and non-authoritative', () => {
  assert.equal(qualification.result, 'pass');
  assert.equal(qualification.authority_effect, 'none');
  assert.equal(qualification.documentation.open_questions, 0);
  assert.equal(qualification.documentation.internal_development_links, 0);
  assert.equal(qualification.documentation.stale_selected_compiler_claims, 0);
  assert.deepEqual(qualification.denominators, {
    documentation_surfaces: 6,
    documentation_surfaces_passed: 6,
    languages: 3,
    languages_built: 3,
    languages_artifact_verified: 3,
    languages_natively_compiled: 3,
    languages_executed: 3,
    negative_controls: 1,
    negative_controls_killed: 1,
  });
  assert.deepEqual(qualification.example.languages.map((row: any) => row.id), ['typescript', 'python', 'rust']);
  assert.ok(qualification.example.languages.every((row: any) => row.build === 'pass' && row.verify === 'pass' && row.native_compile === 'pass'));
  for (const document of qualification.documentation.surfaces) assert.equal(hash(path.join(domainSpecRoot, document.path)), document.sha256, document.path);
  assert.equal(hash(path.join(cliRoot, 'examples/reconciled-commerce/scenarios.json')), qualification.example.scenarios_sha256);
  assert.equal(hash(path.join(cliRoot, 'examples/reconciled-commerce/values.json')), qualification.example.values_sha256);
  assert.equal(hash(path.join(reconciliationRoot, qualification.package.manifest)), qualification.package.manifest_sha256);
  assert.equal(qualification.publication, false);
  assert.equal(qualification.admission, false);
  assert.equal(qualification.release, false);
});
