import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const root = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1";
const qualificationPath = path.join(repo, root, "evidence/e05-cross-layer-evidence/qualification.v4-candidate.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

function exact(binding: { path: string; sha256: string }): void {
  assert.match(binding.sha256, /^[0-9a-f]{64}$/u);
  assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
}

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.e05-cross-layer-evidence-qualification/v4-candidate");
  assert.equal(value.task, "E05");
  assert.equal(value.result, "blocked");
  assert.equal(value.authority_effect, "none");
  assert.equal(value.supersedes.path, `${root}/evidence/e05-cross-layer-evidence/qualification.v3-candidate.json`);
  exact(value.supersedes);
  const predecessor = JSON.parse(fs.readFileSync(path.join(repo, value.supersedes.path), "utf8"));
  const expected = structuredClone(predecessor);
  expected.schema_version = "alchlang.e05-cross-layer-evidence-qualification/v4-candidate";
  expected.date = "2026-10-06";
  expected.supersedes = { path: `${root}/evidence/e05-cross-layer-evidence/qualification.v3-candidate.json`,
    sha256: sha256(path.join(repo, value.supersedes.path)) };
  expected.inherited_boundaries.E03.path = `${root}/evidence/e03-evf-evidence-join/qualification.v4-candidate.json`;
  expected.inherited_boundaries.E03.sha256 = sha256(path.join(repo, expected.inherited_boundaries.E03.path));
  expected.inherited_boundaries.E04.path = `${root}/evidence/e04-runtime-observation-join/qualification.v4-candidate.json`;
  expected.inherited_boundaries.E04.sha256 = sha256(path.join(repo, expected.inherited_boundaries.E04.path));
  expected.bindings.obligation_matrix.path = `${root}/evidence/e05-cross-layer-evidence/obligation-matrix.v3-candidate.json`;
  expected.bindings.obligation_matrix.sha256 = sha256(path.join(repo, expected.bindings.obligation_matrix.path));
  expected.bindings.matrix_test.sha256 = sha256(path.join(repo, expected.bindings.matrix_test.path));
  expected.bindings.post_tde_finalizer_test.sha256 = sha256(path.join(repo, expected.bindings.post_tde_finalizer_test.path));
  expected.matrix_predecessor = predecessor.bindings.obligation_matrix;
  assert.deepEqual(value, expected);
  assert.deepEqual(value.coverage, predecessor.coverage);
  assert.deepEqual(value.validation, predecessor.validation);
  assert.equal(value.matrix_predecessor.path, `${root}/evidence/e05-cross-layer-evidence/obligation-matrix.v2-candidate.json`);
  exact(value.matrix_predecessor);
  assert.deepEqual(value.matrix_predecessor, predecessor.bindings.obligation_matrix);
  assert.deepEqual(Object.keys(value.inherited_boundaries), ["E01", "E02", "E03", "E04"]);
  assert.equal(value.inherited_boundaries.E03.path, `${root}/evidence/e03-evf-evidence-join/qualification.v4-candidate.json`);
  assert.equal(value.inherited_boundaries.E04.path, `${root}/evidence/e04-runtime-observation-join/qualification.v4-candidate.json`);
  for (const binding of Object.values(value.inherited_boundaries) as Array<{ path: string; sha256: string }>) exact(binding);
  assert.deepEqual(Object.keys(value.bindings).sort(), ["matrix_schema", "obligation_matrix", "cross_layer_test", "matrix_test", "post_tde_finalizer_test"].sort());
  for (const binding of Object.values(value.bindings) as Array<{ path: string; sha256: string }>) exact(binding);
  const matrix = JSON.parse(fs.readFileSync(path.join(repo, value.bindings.obligation_matrix.path), "utf8"));
  assert.deepEqual(matrix.current_boundaries, value.inherited_boundaries);
  assert.equal(matrix.result, "blocked");
  assert.deepEqual(matrix.coverage, { obligations: 32, by_task: { E01: 8, E02: 8, E03: 8, E04: 8 },
    satisfied: 28, blocked: 4, unexplained_gaps: 0, representation_only_substitutes: 0 });
  assert.deepEqual(value.coverage, { source_tasks: 4, inherited_obligations: 32, satisfied_original_predicates: 28,
    blocked_original_predicates: ["E03-O02", "E03-O03", "E03-O04", "E03-O05"],
    representation_only_substitutes: 0, unexplained_gaps: 0 });
  assert.deepEqual(value.validation.focused_cross_layer, { tests: 7, passed: 7, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.obligation_matrix, { tests: 2, passed: 2, failed: 0, skipped: 0 });
  assert.equal(value.validation.full_application_regression, "not-claimed");
  assert.match(value.claim_ceiling, /four original execution-pass-dependent E03 predicates remain blocked/u);
  assert.equal(value.open_questions.length, 2);
}

test("E05 successor binds 32 original predicates with four explicit blocked gaps", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("E05 successor rejects stale bindings and false completion claims", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.bindings.obligation_matrix.sha256 = "0".repeat(64); },
    (value: any) => { value.bindings.cross_layer_test.path = value.bindings.matrix_test.path;
      value.bindings.cross_layer_test.sha256 = value.bindings.matrix_test.sha256; },
    (value: any) => { value.inherited_boundaries.E03.sha256 = "0".repeat(64); },
    (value: any) => { value.coverage.blocked_original_predicates = []; },
    (value: any) => { value.result = "scoped-pass"; },
    (value: any) => { value.validation.full_application_regression = "pass"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validate(changed));
  }
});
