import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const evidenceRoot = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/e03-evf-evidence-join";
const qualificationPath = path.join(repo, evidenceRoot, "qualification.v4-candidate.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const expectedBindings = [
  "join_implementation", "join_test", "cross_layer_test", "finalizer_implementation",
  "finalizer_test", "verification_test", "projection_test", "causal_schema",
  "provider_evidence_v1_schema", "theorem_evidence_schema", "evf_join_v1_schema",
  "provider_evidence_v2_schema", "evf_join_v2_schema", "finalized_request_schema",
  "provider_outcome_v2_schema", "mapping_document",
];

function exact(binding: { path: string; sha256: string }): void {
  assert.match(binding.sha256, /^[0-9a-f]{64}$/u);
  assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
}

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.e03-evf-evidence-join-qualification/v4-candidate");
  assert.equal(value.task, "E03");
  assert.equal(value.result, "scoped-pass");
  assert.equal(value.authority_effect, "none");
  assert.match(value.qualified_scope, /Fail-closed evidence joining/u);
  assert.equal(value.supersedes.path, `${evidenceRoot}/qualification.v3-candidate.json`);
  exact(value.supersedes);
  const predecessor = JSON.parse(fs.readFileSync(path.join(repo, value.supersedes.path), "utf8"));
  assert.equal(predecessor.schema_version, "alchlang.e03-evf-evidence-join-qualification/v3-candidate");
  const expected = structuredClone(predecessor);
  expected.schema_version = "alchlang.e03-evf-evidence-join-qualification/v4-candidate";
  expected.date = "2026-10-06";
  expected.supersedes = { path: `${evidenceRoot}/qualification.v3-candidate.json`,
    sha256: sha256(path.join(repo, value.supersedes.path)) };
  expected.current_bindings.finalizer_test.sha256 = sha256(path.join(repo, predecessor.current_bindings.finalizer_test.path));
  expected.freshness_delta = {
    changed_binding: "finalizer_test",
    previous_sha256: predecessor.current_bindings.finalizer_test.sha256,
    current_sha256: expected.current_bindings.finalizer_test.sha256,
    historical_test_preimage_available: false,
    interpretation: "Current selected tests passed 27/27; the original test preimage is unavailable for byte-diff attribution. No implementation or claim-ceiling promotion.",
  };
  assert.deepEqual(value, expected);
  assert.equal(value.freshness_delta.changed_binding, "finalizer_test");
  assert.equal(value.freshness_delta.previous_sha256, predecessor.current_bindings.finalizer_test.sha256);
  assert.equal(value.freshness_delta.current_sha256, value.current_bindings.finalizer_test.sha256);
  assert.equal(value.freshness_delta.historical_test_preimage_available, false);
  assert.deepEqual(Object.keys(value.current_bindings).sort(), Object.keys(predecessor.current_bindings).sort());
  for (const key of Object.keys(value.current_bindings).filter(key => key !== "finalizer_test")) {
    assert.deepEqual(value.current_bindings[key], predecessor.current_bindings[key], key);
  }
  assert.equal(value.inherited_boundary.result, "scoped-pass");
  exact(value.inherited_boundary);
  assert.equal(value.dag.node, "E03");
  exact(value.dag);
  assert.deepEqual(Object.keys(value.current_bindings).sort(), expectedBindings.slice().sort());
  for (const binding of Object.values(value.current_bindings) as Array<{ path: string; sha256: string }>) exact(binding);
  assert.deepEqual(value.route_outcome_accounting, {
    route_kinds: 2, causal_outcomes: 8, candidate_cells: 16,
    constructible_join_cells: 15, blocked_cells: ["execution-evidence/pass"],
    theorem_pass_join_constructible: true, execution_pass_join_constructible: false,
    synthetic_execution_pass_can_satisfy_obligation: false,
  });
  assert.deepEqual(value.validation.focused_evf_join, { tests: 9, passed: 9, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.selected_finalizer_verification_projection_join,
    { tests: 27, passed: 27, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.cross_layer, { tests: 7, passed: 7, failed: 0, skipped: 0 });
  assert.equal(value.validation.full_application_regression, "not-claimed");
  assert.match(value.claim_ceiling, /provider-native authentication are not demonstrated/u);
  assert.equal(value.open_questions.length, 2);
}

test("E03 successor binds current fail-closed join surfaces without promoting execution pass", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("E03 successor rejects stale sources, missing scope and synthetic-pass promotion", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.current_bindings.join_implementation.sha256 = "0".repeat(64); },
    (value: any) => { value.current_bindings.finalizer_test.path = value.current_bindings.join_test.path;
      value.current_bindings.finalizer_test.sha256 = value.current_bindings.join_test.sha256;
      value.freshness_delta.current_sha256 = value.current_bindings.join_test.sha256; },
    (value: any) => { value.freshness_delta.changed_binding = "join_implementation"; },
    (value: any) => { delete value.current_bindings.join_test; },
    (value: any) => { value.route_outcome_accounting.constructible_join_cells = 16; },
    (value: any) => { value.route_outcome_accounting.synthetic_execution_pass_can_satisfy_obligation = true; },
    (value: any) => { value.route_outcome_accounting.blocked_cells = []; },
    (value: any) => { value.validation.full_application_regression = "pass"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validate(changed));
  }
});
